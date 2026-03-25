

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

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

from   app.lib                         import BASE_STORAGE_DIR
from   app.swing_analysis_classes.main import Analyze
from   datetime                        import datetime, timedelta, timezone
from   fastapi                         import APIRouter, HTTPException, UploadFile, File, Form
from   fastapi.responses               import FileResponse
from   pathlib                         import Path
from   typing                          import Dict
from   uuid                            import uuid4

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
# An endpoint router for all analysis-related endpoints.
# ---------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   FUNCTION NAME: cleanup_expired_analyses
#
#   DESCRIPTION:
#       Removes the artifacts for the expired analyses based on a TTL
#       set by ANALYSIS_TTL and determined by the current time - TTL.
#
# ---------------------------------------------------------------------
def cleanup_expired_analyses() -> None:

    # -----------------------------------------------------------------
    # Grab the system's current time.
    # -----------------------------------------------------------------
    now = datetime.now( timezone.utc )

    # -----------------------------------------------------------------
    # Iterate through the cached analyses and identify any that have
    # expired based on the current time - the TTL.
    # -----------------------------------------------------------------
    expired_ids = [
        aid for aid, data in ANALYSIS_CACHE.items()
        if data[ "expires_at" ] < now
    ]

    # -----------------------------------------------------------------
    # For each expired analysis, grab the path to the directory holding
    # the artifacts and try removing it.
    # -----------------------------------------------------------------
    for aid in expired_ids:
        analysis_dir = Path( ANALYSIS_CACHE[ aid ][ "analysis_dir" ] )

        try:
            shutil.rmtree( analysis_dir )
        except Exception:
            pass
        
        # -------------------------------------------------------------
        # Remove the analysis ID from the cache.
        # -------------------------------------------------------------
        ANALYSIS_CACHE.pop( aid, None )


# ---------------------------------------------------------------------
#
#   FUNCTION NAME: validate_analysis_cache
#
#   DESCRIPTION:
#       Validates that an analysis session exists and has not expired.
#       Returns the cached analysis dictionary if valid.
#
#       Raises:
#           404 -> If analysis ID does not exist
#           410 -> If analysis has expired
#
# ---------------------------------------------------------------------
def validate_analysis_cache(
    analysis_id: str,
) -> dict:

    # -----------------------------------------------------------------
    # Retrieve the analysis ID from the cache. If id doesn't exist
    # throw a 404.
    # -----------------------------------------------------------------
    id = ANALYSIS_CACHE.get( analysis_id )
    if not id:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    # -----------------------------------------------------------------
    # If the TTL has expired for this analysis ID, throw a 410.
    # -----------------------------------------------------------------
    if id[ "expires_at" ] < datetime.now( timezone.utc ):
        raise HTTPException(
            status_code=410,
            detail="Analysis expired.",
        )

    return id


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
    down_the_line: UploadFile = File( ... ),     # Down-the-line swing video input
    face_on: UploadFile = File( ... ),           # Face-on swing video input
    experience_level: str = Form( ... )          # User's experience level input
) -> Dict:
    
    # -----------------------------------------------------------------
    # Cleanup expired analyses on each new analysis request to manage 
    # memory.
    # -----------------------------------------------------------------
    cleanup_expired_analyses()

    # -----------------------------------------------------------------
    # Create an analysis ID to uniquely identify this analysis session
    # and to help identify analysis artifacts.
    # -----------------------------------------------------------------
    analysis_id = str( uuid4() )

    # -----------------------------------------------------------------
    # Create persistent runtime directory for this analysis.
    # -----------------------------------------------------------------
    analysis_dir = BASE_STORAGE_DIR / analysis_id
    analysis_dir.mkdir( parents=True, exist_ok=True )

    # -----------------------------------------------------------------
    # Create a unique temporary directory to store the input file and
    # any analysis artifacts.
    # -----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path( tmp_dir )

        # -------------------------------------------------------------
        # Create paths for the temporary versions of the input files.
        # This is so we can maintain a reference to the files on disk
        # while the analysis classes operate on them.
        # -------------------------------------------------------------
        face_on_path       = tmp_dir_path / "face_on.mp4"
        down_the_line_path = tmp_dir_path / "down_the_line.mp4"

        # -------------------------------------------------------------
        # Write the uploaded files to the temporary location.
        # -------------------------------------------------------------
        for file, path in [ 
            ( face_on, face_on_path ), 
            ( down_the_line, down_the_line_path ) 
        ]:
            with path.open( "wb" ) as buffer:
                shutil.copyfileobj( file.file, buffer )

        # -------------------------------------------------------------
        # Pass input to the analysis classes and perform the analysis.
        # -------------------------------------------------------------
        output = Analyze(
            face_on_path=str( face_on_path ),
            down_the_line_path=str( down_the_line_path ),
            temp_dir_path=str( tmp_dir_path ),
            experience_level=experience_level
        )

        # -------------------------------------------------------------
        # Move final overlays OUT of temp dir into persistent dir.
        # -------------------------------------------------------------
        final_face_on       = analysis_dir / "face_on_overlay.mp4"
        final_down_the_line = analysis_dir / "down_the_line_overlay.mp4"

        if output.face_on_overlay_path:
            shutil.move( output.face_on_overlay_path, final_face_on )

        if output.down_the_line_overlay_path:
            shutil.move( output.down_the_line_overlay_path, final_down_the_line )

        # -------------------------------------------------------------
        # Store the analysis artifact paths in the in-memory cache.
        # -------------------------------------------------------------
        ANALYSIS_CACHE[ analysis_id ] = {
            "face_on_overlay": str( final_face_on ),
            "down_the_line_overlay": str( final_down_the_line ),
            "analysis_dir": str( analysis_dir ),
            "expires_at": datetime.now( timezone.utc ) + ANALYSIS_TTL,
            "consumed": set()
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
#   ENDPOINT NAME: get_face_on_overlay
#
#   DESCRIPTION:
#       Streams the face-on pose-overlay video generated during swing
#       analysis for a specific analysis session. Cleans up artifacts
#       if both overlays have been retrieved.
#
# ---------------------------------------------------------------------
@router.get( "/{analysis_id}/overlay/face_on" )
async def get_face_on_overlay(
    analysis_id: str
) -> FileResponse:

    # -----------------------------------------------------------------
    # Validate the cache for this analysis ID.
    # -----------------------------------------------------------------
    id = validate_analysis_cache( analysis_id )

    video_path = Path( id[ "face_on_overlay" ] )
    if not video_path.exists():
        raise HTTPException( status_code=404, detail="Overlay not found." )

    # -----------------------------------------------------------------
    # Mark this overlay as consumed.
    # -----------------------------------------------------------------
    id[ "consumed" ].add( "face_on" )

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename="face_on_overlay.mp4",
    )


# ---------------------------------------------------------------------
#
#   ENDPOINT NAME: get_down_the_line_overlay
#
#   DESCRIPTION:
#       Streams the down-the-line pose-overlay video generated during
#       swing analysis for a specific analysis session. Cleans up
#       artifacts if both overlays have been retrieved.
#
# ---------------------------------------------------------------------
@router.get( "/{analysis_id}/overlay/down_the_line" )
async def get_down_the_line_overlay(
    analysis_id: str
) -> FileResponse:

    # -----------------------------------------------------------------
    # Validate the cache for this analysis ID.
    # -----------------------------------------------------------------
    id = validate_analysis_cache( analysis_id )

    video_path = Path( id[ "down_the_line_overlay" ] )
    if not video_path.exists():
        raise HTTPException( status_code=404, detail="Overlay not found." )

    # -----------------------------------------------------------------
    # Mark this overlay as consumed.
    # -----------------------------------------------------------------
    id[ "consumed" ].add( "down_the_line" )

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename="down_the_line_overlay.mp4",
    )


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
