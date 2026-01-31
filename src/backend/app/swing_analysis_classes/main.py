

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import os
import sys

# ---------------------------------------------------------------------
# Add the parent directory to the system path to allow for relative
# imports.
# ---------------------------------------------------------------------
PARENT_DIR = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
sys.path.append( PARENT_DIR )

# ---------------------------------------------------------------------
# TODO: Add imports for footage preprocessing modules here.
# ---------------------------------------------------------------------

from swing_analysis_classes.pose_estimation import PoseEstimation
from swing_analysis_classes.metrics         import MetricsCalculator
from swing_analysis_classes.prompt          import PromptBuilder
from services.gemini_endpoint               import Client

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: Analyze
#
#   DESCRIPTION:
#       Class for analyzing a swing video and providing a basic text
#       analysis as well as a video overlay with pose esitmation data.
#
# ---------------------------------------------------------------------
class Analyze():

    def __init__( 
            self, 
            face_on_path: str, 
            down_the_line_path: str,
            temp_dir_path: str,
            experience_level: str 
        ) -> None:

        # -------------------------------------------------------------
        # INPUTS
        # -------------------------------------------------------------
        # Path to the swing video we are analyzing. Include situational
        # context and swing metadata.
        # -------------------------------------------------------------
        self.face_on_video_path       = face_on_path
        self.down_the_line_video_path = down_the_line_path
        self.experience_level         = experience_level

        # -------------------------------------------------------------
        # OUTPUTS
        # -------------------------------------------------------------
        # Path to the outputted swing video with pose estimations
        # overlayed, and attribute for the final swing analysis.
        # -------------------------------------------------------------
        self.face_on_overlay_path       = None
        self.down_the_line_overlay_path = None
        self.temp_dir_path              = temp_dir_path
        self.analysis                   = ""

        # -------------------------------------------------------------
        # Run the pipeline.
        # -------------------------------------------------------------
        self._process_swing()

    # -----------------------------------------------------------------
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _process_swing
    #
    #   DESCRIPTION:
    #       Run the full swing analysis pipeline.
    #
    # -----------------------------------------------------------------
    def _process_swing( self ) -> None:

        # -------------------------------------------------------------
        # TODO: Preprocess the footage (e.g., stabilization, cropping).
        # -------------------------------------------------------------

        # -------------------------------------------------------------
        # Extract the pose data from the processed footage.
        # -------------------------------------------------------------
        pose_estimator = PoseEstimation(
            face_on_path = self.face_on_video_path,
            down_the_line_path = self.down_the_line_video_path,
            temp_dir_path = self.temp_dir_path
        )

        self.face_on_overlay_path       = pose_estimator.face_on_overlay_path
        self.down_the_line_overlay_path = pose_estimator.down_the_line_overlay_path

        # -------------------------------------------------------------
        # Perform metrics calculations based on the extracted pose data.
        # -------------------------------------------------------------
        # metrics_calculator = MetricsCalculator( pose_data=pose_estimator.pose_data )

        # -------------------------------------------------------------
        # Build the prompt for the AI model using the calculated
        # metrics.
        # -------------------------------------------------------------
        # prompt_builder = PromptBuilder(
        #     experience_level=self.experience_level,
        #     metrics=metrics_calculator.metrics
        # )
        
        # -------------------------------------------------------------
        # Send the prompt to the AI model and get the analysis.
        # -------------------------------------------------------------
        client = Client()
        self.analysis = client.generate_response( prompt=prompt_builder.prompt )

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------