

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

    def __init__( self, video_path: str, camera_angle: str, experience_level: str, metadata: str ) -> None:

        # -------------------------------------------------------------
        # Path to the swing video we are analyzing.
        # -------------------------------------------------------------
        self.video_path = video_path

        # -------------------------------------------------------------
        # Include situational context and swing metadata.
        # -------------------------------------------------------------
        self.camera_angle     = camera_angle
        self.experience_level = experience_level
        self.metadata         = metadata

        # -------------------------------------------------------------
        # Path to the outputted swing video with pose estimations
        # overlayed.
        # -------------------------------------------------------------
        self.video_overlay_path = None

        # -------------------------------------------------------------
        # Attribute for holding the final swing analysis.
        # -------------------------------------------------------------
        self.analysis = ""

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
            vid_in=self.video_path,
            overlay=True
        )
        self.video_overlay_path = pose_estimator.output_vid_path

        # -------------------------------------------------------------
        # Perform metrics calculations based on the extracted pose data.
        # -------------------------------------------------------------
        metrics_calculator = MetricsCalculator( pose_data=pose_estimator.pose_data )

        # -------------------------------------------------------------
        # Build the prompt for the AI model using the calculated
        # metrics.
        # -------------------------------------------------------------
        prompt_builder = PromptBuilder(
            camera_angle=self.camera_angle,
            experience_level=self.experience_level,
            metadata=self.metadata,
            metrics=metrics_calculator.metrics
        )
        
        # -------------------------------------------------------------
        # Send the prompt to the AI model and get the analysis.
        # -------------------------------------------------------------
        client = Client()
        self.analysis = client.generate_response( prompt=prompt_builder.prompt )

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
