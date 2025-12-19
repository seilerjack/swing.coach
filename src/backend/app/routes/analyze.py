

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

from   app.swing_analysis_classes.main import Analyze
from   fastapi                         import APIRouter, UploadFile, File, Form
from   pathlib                         import Path
from   typing                          import Dict

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

router = APIRouter( prefix="/analysis", tags=[ "analysis" ] )

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   EDNPOINT NAME: analyze
#
#   DESCRIPTION:
#       [description].
#
# ---------------------------------------------------------------------
@router.post("/")
async def analyze(
    video: UploadFile = File(...),
    experience_level: str = Form(...),
    camera_angle: str = Form(...),
    metadata: str = Form(...)
) -> Dict:
    
    # -----------------------------------------------------------------
    # Create a unique temporary directory to store the input file and
    # any analysis artifacts.
    # -----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path( tmp_dir )

        # -------------------------------------------------------------
        # Save the uploaded video.
        # -------------------------------------------------------------
        if video.filename is None:
            video.filename = "tmp_swing.mp4"
            
        video_path = tmp_dir_path / video.filename
        with video_path.open( "wb" ) as buffer:
            shutil.copyfileobj( video.file, buffer )

        # -------------------------------------------------------------
        # Run the full analysis pipeline.
        # -------------------------------------------------------------
        output = Analyze(
            video_path=str( video_path ),
            camera_angle=camera_angle,
            experience_level=experience_level,
            metadata=metadata
        )

        # -------------------------------------------------------------
        # Grab the filename from the returned video overlay so it can
        # be resolved in the static folder shared directory.
        # -------------------------------------------------------------
        pose_overlay_path = Path( output.video_overlay_path ).name if output.video_overlay_path else None

        # -------------------------------------------------------------
        # Return the JSON response including the full swing analysis
        # and a path to the pose overlayed swing video.
        # -------------------------------------------------------------
        return {
            "swing_analysis": output.analysis,
            "pose_overlay": f"/shared/{ pose_overlay_path }"
        }

# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
