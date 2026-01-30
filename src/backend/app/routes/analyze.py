

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import io
import os
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------
# Add the parent directory to the system path to allow for relative
# imports.
# ---------------------------------------------------------------------
PARENT_DIR = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
sys.path.append( PARENT_DIR )

from   app.swing_analysis_classes.main import Analyze
from   datetime                        import datetime, timedelta, timezone
from   email.mime.application          import MIMEApplication
from   email.mime.multipart            import MIMEMultipart
from   email.generator                 import BytesGenerator
from   fastapi                         import APIRouter, HTTPException, UploadFile, File, Form
from   fastapi.responses               import StreamingResponse
from   pathlib                         import Path
from   pydantic                        import BaseModel
from   typing                          import Dict
from   uuid                            import uuid4

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

router = APIRouter( prefix="/analysis", tags=[ "analysis" ] )

# ---------------------------------------------------------------------
# In-memory cache for storing analysis artifact paths OUTSIDE of the
# temporary directory.
# ---------------------------------------------------------------------
ANALYSIS_CACHE = {}

# ---------------------------------------------------------------------
# Time-to-live for analysis artifacts. Memory protection.
# ---------------------------------------------------------------------
ANALYSIS_TTL = timedelta( minutes=15 )

# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: 
#
#   DESCRIPTION:
#       Pydantic base model for the required swing analysis resources.
#
# ---------------------------------------------------------------------
class SwingAnalysis( BaseModel ):
    down_the_line: UploadFile = File( ... )     # Down-the-line swing video input
    face_on: UploadFile = File( ... )           # Face-on swing video input
    experience_level: str = Form( ... )         # User's experience level input


# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   ENDPOINT NAME: analyze
#
#   DESCRIPTION:
#       Endpoint that triggers the full swing analysis pipeline.
#
# ---------------------------------------------------------------------
@router.post("/")
async def analyze(
    swing: SwingAnalysis
) -> Dict:
    
    # -----------------------------------------------------------------
    # Create an analysis ID to uniquely identify this analysis session
    # and to help identify analysis artifacts.
    # -----------------------------------------------------------------
    analysis_id = str( uuid4())

    # -----------------------------------------------------------------
    # Create a unique temporary directory to store the input file and
    # any analysis artifacts.
    # -----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path( tmp_dir )

        # -------------------------------------------------------------
        # Create paths for the temporary versions of the input files.
        # -------------------------------------------------------------
        face_on_path       = tmp_dir_path / "face_on.mp4"
        down_the_line_path = tmp_dir_path / "down_the_line.mp4"

        # -------------------------------------------------------------
        # Write the uploaded files to the temporary location.
        # -------------------------------------------------------------
        for file, path in [ 
            ( swing.face_on, face_on_path ), 
            ( swing.down_the_line, down_the_line_path ) 
        ]:
            with path.open( "wb" ) as buffer:
                shutil.copyfileobj( file.file, buffer )

        # -------------------------------------------------------------
        # Pass input to the analysis classes and perform the analysis.
        # -------------------------------------------------------------
        output = Analyze(
            face_on_path=str( face_on_path ),
            down_the_line_path=str( down_the_line_path ),
            experience_level=swing.experience_level
        )

        # -------------------------------------------------------------
        # Store the analysis artifact paths in the in-memory cache.
        # -------------------------------------------------------------
        ANALYSIS_CACHE[ analysis_id ] = {
            "face_on_overlay": output.face_on_overlay_path,
            "down_the_line_overlay": output.down_the_line_overlay_path,
            "expires_at": datetime.now( timezone.utc ) + ANALYSIS_TTL
        }

        # -------------------------------------------------------------
        # Return the textual analysis and an analysis session ID for
        # retrieving analysis artifacts.
        # -------------------------------------------------------------
        return {
            "analysis_id": analysis_id,
            "swing_analysis": output.analysis
        }



# ---------------------------------------------------------------------
#
#   ENDPOINT NAME: get_overlays
#
#   DESCRIPTION:
#       Endpoint that allows the frontend to stream the pose-overlay
#       videos generated during swing analysis from a specific
#       analysis session.
#
# ---------------------------------------------------------------------
@router.get("/{analysis_id}/overlay")
async def get_overlays( analysis_id: str ) -> StreamingResponse:

    # -----------------------------------------------------------------
    # Retrieve the analysis ID from the cache. If id doesn't exist
    # throw a 404.
    # -----------------------------------------------------------------
    id = ANALYSIS_CACHE.get( analysis_id )
    if not id:
        raise HTTPException( status_code=404, detail="Analysis not found." )
    

    # -----------------------------------------------------------------
    #
    #   FUNCTION NAME: generate_streaming_response
    #
    #   DESCRIPTION:
    #       Streams both pose-overlay videos (face-on and down-the-
    #       line) as a single multipart MIME response, then cleans up
    #       all temporary artifacts associated with this analysis.
    #
    #       NOTE: This generator is intended to be used with FastAPI's
    #       StreamingResponse.
    #
    # -----------------------------------------------------------------
    def generate_streaming_response():

        # -------------------------------------------------------------
        # Create a multipart MIME container.
        # "mixed" allows multiple different file parts in one response.
        # -------------------------------------------------------------
        msg = MIMEMultipart( "mixed" )

        # -------------------------------------------------------------
        # Iterate over both overlay videos generated during analysis.
        # Each entry maps a logical name to a filesystem path.
        # -------------------------------------------------------------
        for name, path in [
            ( "face_on_overlay", id[ "face_on_overlay" ] ),
            ( "down_the_line_overlay", id[ "down_the_line_overlay" ] )
        ]:
            with open( path, "rb" ) as f:

                # -----------------------------------------------------
                # Wrap the raw MP4 bytes as a MIME application
                # -----------------------------------------------------
                part = MIMEApplication( f.read(), _subtype="mp4" )
                
                # -----------------------------------------------------
                # Add headers so the browser understands this as a file
                # attachment with a meaningful filename
                # -----------------------------------------------------
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=f"{ name }.mp4",
                )

                # -----------------------------------------------------
                # Attach this video part to the multipart response
                # -----------------------------------------------------
                msg.attach( part )

        # -------------------------------------------------------------
        # Serialize the multipart message into raw bytes
        # -------------------------------------------------------------
        buffer = io.BytesIO()
        BytesGenerator( buffer ).flatten( msg )
        buffer.seek( 0 )

        # -------------------------------------------------------------
        # Yield the entire multipart payload as the streaming response
        # body. (FastAPI will stream this to the client)
        # -------------------------------------------------------------
        yield buffer.read()

        # -------------------------------------------------------------
        # Remove all temporary files associated with this analysis
        # (both overlay videos)
        # -------------------------------------------------------------
        for path in id.values():
            if isinstance( path, str ) and Path( path ).exists():
                Path( path ).unlink()

        # -------------------------------------------------------------
        # Remove this analysis entry from the in-memory cache
        # so it does not persist beyond this request
        # -------------------------------------------------------------
        ANALYSIS_CACHE.pop( analysis_id, None )

    # -----------------------------------------------------------------
    # Return the streaming response with multipart/mixed media type to
    # the frontend.
    # -----------------------------------------------------------------
    return StreamingResponse(
        generate_streaming_response(),
        media_type="multipart/mixed",
    )

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
