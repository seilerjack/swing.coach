

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import textwrap

from   typing import Any, Dict
from   enum   import Enum

# -----------------------------------------------------------------------------
#                                  CONSTANTS
# -----------------------------------------------------------------------------

DELIMITER = \
    textwrap.dedent( "-----" )

# -----------------------------------------------------------------------------
# Provides high-level instructions and framing for the LLM. This block explains
# the role (golf coach + biomechanics expertise) and overall analysis 
# objectives.
# -----------------------------------------------------------------------------
CONTEXT = \
    textwrap.dedent( f"""\
                     Context
                     You are an experienced golf coach with additional background in biomechanics.

                     You use your expertise and knowledge of human movement to provide insightful, actionable feedback to golfers aiming to improve their swing technique.

                     Analyze the following golf swing metrics and provide feedback on the player's movement and technique.
                    
                     Use a supportive tone and concise language, focusing on practical advice that the golfer can implement to enhance their performance.
                     { DELIMITER }
                     """ )

# -----------------------------------------------------------------------------
# Provides specific tasks the LLM should perform based on the provided data.
# -----------------------------------------------------------------------------
TASKS = \
    textwrap.dedent( f"""\
                     Task
                     IMPORTANT - Tailor your language and depth of explanation to the golfer's experience level: beginner, intermediate, or advanced.
                     1. Interpret what these values suggest about the golfer's swing mechanics.
                     2. Evaluate the gof swing using the following categories:
                        - Posture and Setup
                        - Backswing
                        - Downswing
                        - Impact Position
                        - Follow-Through
                        Assign each category a score from 0 - 100 and provide a one-sentence explanation.
                        Then compute an overall score from 0-100 reflecting the swing as a whole.
                     3. Offer 2-3 specific, actionable coaching tips for improvement.
                         - If the swing metrics and outcome indicate a successful shot, it is acceptable if fewer than 3 issues are noted.
                         - These coaching tips should be no more than one sentence each.
                     { DELIMITER }
                     """ )

# -----------------------------------------------------------------------------
#                                   CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: PromptBuilder
#
#   DESCRIPTION:
#       This class constructs the prompt used to query the LLM. It
#       requires data provided by the user, specifically: camera angle,
#       experience level, and metadata. This prompt is then used to 
#       generate the swing analysis via the Gemini API service.
#
# ---------------------------------------------------------------------
class PromptBuilder:

    def __init__( self, camera_angle: str, experience_level: str, metadata: str, metrics: Dict[ str, Any ] ) -> None:
        
        # -------------------------------------------------------------
        # Initialize the metrics, experience level, and camera angle
        # with the provided values.
        # -------------------------------------------------------------
        self.metrics          = metrics
        self.experience_level = experience_level
        self.camera_angle     = camera_angle
        self.metadata         = metadata

        # -------------------------------------------------------------
        # Build and store the prompt.
        # -------------------------------------------------------------
        self.prompt = self._build_prompt()


    # -----------------------------------------------------------------
    #
    #   METHOD NAME: _build_prompt
    #
    #   DESCRIPTION:
    #       Construct the full prompt by combining all parts. This 
    #       includes context, situation, metadata, metrics, tasks, and
    #       the expected output.
    #
    #   NOTE: The return is shifted left to align with the left margin.
    #
    # -----------------------------------------------------------------
    def _build_prompt( self ) -> str:
        return textwrap.dedent( f"""
{ CONTEXT }
{ self._build_situation() }
{ self._build_metadata() }
{ self._build_metrics() }
{ TASKS }
""" )


    # -----------------------------------------------------------------
    #
    #   METHOD NAME: _build_situation
    #
    #   DESCRIPTION:
    #       The situation portion of the prompt should contain the 
    #       player's experience level and the camera angle of the video
    #       taken.
    #
    # -----------------------------------------------------------------
    def _build_situation( self ) -> str:
        return textwrap.dedent( f"""\
                                Situation
                                The golfer is at an { self.experience_level } experience level.
                                The swing video was recorded from a { self.camera_angle } camera angle.
                                { DELIMITER }
                                """ )


    # -----------------------------------------------------------------
    #
    #   METHOD NAME: _build_metadata
    #
    #   DESCRIPTION:
    #       The metadata portion of the prompt should contain
    #       information relating to the outcome of the swing video
    #       uploaded. Things like "ball start right and faded 10 yards"
    #       would be most apporpriate here.
    #
    # -----------------------------------------------------------------
    def _build_metadata( self ) -> str:
        return textwrap.dedent( f"""\
                                Metadata
                                { self.metadata }
                                { DELIMITER }
                                """ )


    # -----------------------------------------------------------------
    #
    #   METHOD NAME: _build_metrics
    #
    #   DESCRIPTION:
    #       The metrics portion of the prompt should contain the
    #       formatted output from the metrics dictionary.
    #
    # -----------------------------------------------------------------
    def _build_metrics( self ) -> str:
        return textwrap.dedent( f"""\
                                Pose Metrics
                                - Shoulder rotation backswing : { self.metrics[ "shoulder_rotation_range_deg_backswing" ]:.2f}°
                                - Shoulder rotation range     : { self.metrics[ "shoulder_rotation_range_deg" ]:.2f}°
                                - Hip rotation backswing      : { self.metrics[ "hip_rotation_range_deg_backswing" ]:.2f}°
                                - Hip rotation range          : { self.metrics[ "hip_rotation_range_deg" ]:.2f}°
                                - Spine tilt (mean)           : { self.metrics[ "spine_tilt_mean_deg" ]:.2f}°
                                - Spine tilt (range)          : { self.metrics[ "spine_tilt_range_deg" ]:.2f}°
                                - Head movement (X)           : { self.metrics[ "head_movement_x" ]:.2f}% (lateral)
                                - Head movement (Y)           : { self.metrics[ "head_movement_y" ]:.2f}% (vertical)
                                { DELIMITER }
                                """ )


# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                  EXECUTION 
# -----------------------------------------------------------------------------
