

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
                     **Context**
                     You are an experienced golf coach with additional background in biomechanics.

                     You use your expertise and knowledge of human movement to provide insightful, actionable feedback to golfers aiming to improve their swing technique.

                     Analyze the following golf swing metrics and provide feedback on the player's movement and technique.
                     { DELIMITER }
                     """ )

# -----------------------------------------------------------------------------
# Provides specific tasks the LLM should perform based on the provided data.
# -----------------------------------------------------------------------------
TASKS = \
    textwrap.dedent( f"""\
                     **Task**
                     1. Interpret what these values suggest about the golfer's swing mechanics.
                     2. Identify potential issues or inefficiencies.
                     3. Offer 2-3 specific, actionable coaching tips for improvement.
                         - If the swing metrics and outcome indicate a successful shot, it is acceptable if fewer than 3 issues are noted.  
                     4. Keep the tone supportive, concise, and practical.
                     5. Tailor your language and depth of explanation to the golfer's experience level: beginner, intermediate, or advanced.
                     { DELIMITER }
                     6. Give a letter grade (A+ -> F) for the swing based on the metrics and overall analysis.
                     """ )

# -----------------------------------------------------------------------------
# Defines the exact structure the LLM should return. This strongly improves
# determinism and consistency in model-generated analysis.
# -----------------------------------------------------------------------------
EXPECTED_OUTPUT = \
    textwrap.dedent( """\
                     Return your feedback in this format:

                     { 
                        "swingAnalysis" : (summary paragraph),
                        "keyObservations" : [
                            (bullet 1),
                            (bullet 2),
                            ...
                            ],
                        "coachingTips" : [
                            (tip 1),
                            (tip 2),
                            ...
                            ],
                        "LetterGrade" : (letter grade)
                    }

                     """ )

# -----------------------------------------------------------------------------
#                                   CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: ExperienceLevel
#
#   DESCRIPTION:
#       This value is injected into the Task portion of the prompt so
#       the LLM tailors tone, depth, and terminology to the golfer's
#       skill level.
#
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# TODO: Add frontend ability to allow user to select their own
# experience level from a list of these options. This should then be
# passed to the backend and fed into the PromptBuilder. For now the
# value is hardcoded.
# --------------------------------------------------------------------- 
class ExperienceLevel( Enum ):
    BEGINNER     = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED     = "advanced"


# ---------------------------------------------------------------------
#
#   CLASS NAME: CameraAngle
#
#   DESCRIPTION:
#       This value is injected into the Metadata portion of the prompt
#       so the LLM can garner additional context about the pose data.
#
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# TODO: Add frontend ability to allow user to select their own camera
# angle from a list of these options. This should then be passed to the
# backend and fed into the PromptBuilder. For now the value is
# hardcoded.
# --------------------------------------------------------------------- 
class CameraAngle( Enum ):
    DOWN_THE_LINE = "down the line"
    FACE_ON       = "face on"


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
{ EXPECTED_OUTPUT }
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
                                **Situation**
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
                                **Metadata**
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
                                **Pose Metrics**
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
