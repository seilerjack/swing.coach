

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import textwrap

from   typing import Any, Dict
from   enum   import Enum

# -----------------------------------------------------------------------------
#                                  CONSTANTS
# -----------------------------------------------------------------------------

DELIMITER = textwrap.dedent( "-----" )

# -----------------------------------------------------------------------------
# Provides high-level instructions and framing for the LLM. This block explains
# the role (golf coach + biomechanics expertise) and overall analysis 
# objectives.
# -----------------------------------------------------------------------------
CONTEXT = textwrap.dedent( f"""\
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
TASKS = textwrap.dedent(f"""\
Task

IMPORTANT:
- Base your analysis ONLY on the provided metrics.
- Do not assume missing data.
- If a metric suggests uncertainty, acknowledge it briefly.

Tailor your explanation depth to the golfer's experience level.

1. Interpret what the metrics suggest about:
   - Posture and Setup
   - Backswing
   - Downswing
   - Impact Position
   - Follow-Through

2. Score each category from 0-100.
   - Provide a one-sentence justification for each score.
   - Then compute an overall swing score (0-100).

3. Provide 2-3 concise, actionable coaching recommendations.
   - One sentence each.
   - Prioritize the highest-impact improvement areas.

Be concise, structured, and practical.
{ DELIMITER }
""")


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

    def __init__( self, experience_level: str, metrics: Dict[ str, Any ] ) -> None:
        
        # -------------------------------------------------------------
        # Initialize the metrics, experience level, and camera angle
        # with the provided values.
        # -------------------------------------------------------------
        self.metrics          = metrics
        self.experience_level = experience_level

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
        return textwrap.dedent(f"""\
        Situation
        The golfer is at a { self.experience_level } experience level.
        The analysis includes both Face-On and Down-the-Line swing data when available.
        { DELIMITER }
        """)


    # -----------------------------------------------------------------
    #
    #   METHOD NAME: _build_metrics
    #
    #   DESCRIPTION:
    #       The metrics portion of the prompt should contain the
    #       formatted output from the metrics dictionary.
    #
    # -----------------------------------------------------------------
    def _build_metrics(self) -> str:

        # -------------------------------------------------------------
        # Initialize the section header. This primes the LLM to 
        # interpret the following values as structured numerical
        # inputs.
        # -------------------------------------------------------------
        lines = [ "Quantitative Swing Metrics" ]

        # -------------------------------------------------------------
        # Iterate through each camera view in the metrics dictionary.
        # Expected structure:
        # {
        #   "face_on": { "metrics": {...} },
        #   "down_the_line": { "metrics": {...} }
        # }
        # -------------------------------------------------------------
        for view_name, view_data in self.metrics.items():

            # ---------------------------------------------------------
            # Format the camera view name for readability in the 
            # prompt.
            # Example: "face_on" -> "Face On View:"
            # ---------------------------------------------------------
            lines.append( f"\n{ view_name.replace( '_', ' ' ).title() } View:" )

            # ---------------------------------------------------------
            # Safely extract the metric dictionary for this view.
            # Default to empty dict if key is missing.
            # ---------------------------------------------------------
            metric_dict = view_data.get( "metrics", {} )

            # ---------------------------------------------------------
            # If no metrics exist for this view, explicitly state it.
            # This prevents the LLM from assuming missing data.
            # ----------------------------------------------------------
            if not metric_dict:
                lines.append( "  (No metrics available)" )
                continue

            # ----------------------------------------------------------
            # Iterate through each metric in the current view.
            # Supports two formats:
            #
            # 1) Simple scalar:
            #    "shoulder_tilt": 12.4
            #
            # 2) Structured metric object:
            #    "shoulder_tilt": {
            #         "value": 12.4,
            #         "unit": "degrees"
            #     }
            #
            # This keeps the system future-proof without changing prompt
            # logic.
            # -------------------------------------------------------------
            for metric_name, metric_value in metric_dict.items():

                # ---------------------------------------------------------
                # Handle structured metric object
                # ---------------------------------------------------------
                if isinstance( metric_value, dict ):
                    value = metric_value.get( "value" )
                    unit  = metric_value.get( "unit", "" )
                else:
                    # -----------------------------------------------------
                    # Handle simple scalar metric
                    # -----------------------------------------------------
                    value = metric_value
                    unit  = ""

                # ---------------------------------------------------------
                # Format numerical values consistently.
                # Floats are rounded to 2 decimal places for readability.
                # Non-numeric values are converted directly to string.
                # ---------------------------------------------------------
                if isinstance( value, float ):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str( value )

                # ---------------------------------------------------------
                # Format metric name for readability:
                # "shoulder_rotation_range" -> "Shoulder Rotation Range"
                # ---------------------------------------------------------
                lines.append( f"  - { metric_name.replace( '_', ' ' ).title() }: { value_str } { unit }" )

        # -----------------------------------------------------------------
        # Append delimiter to clearly separate this section from the next
        # part of the prompt (e.g., task instructions).
        # -----------------------------------------------------------------
        lines.append( DELIMITER )

        # -----------------------------------------------------------------
        # Join all accumulated lines into a single formatted string.
        # -----------------------------------------------------------------
        return "\n".join( lines )


# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                  EXECUTION 
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # -------------------------------------------------------------
    # Example usage of the PromptBuilder class.
    # -------------------------------------------------------------
    example_metrics = {
        "face_on": {
            "metrics": {
                "swing_speed": { "value": 85.5, "unit": "mph" },
                "club_path_angle": { "value": -2.3, "unit": "degrees" }
            }
        },
        "down_the_line": {
            "metrics": {
                "attack_angle": { "value": 1.5, "unit": "degrees" },
                "face_to_path_angle": { "value": 0.5, "unit": "degrees" }
            }
        }
    }

    prompt_builder = PromptBuilder(
        experience_level="intermediate",
        metrics=example_metrics
    )

    print( prompt_builder.prompt )