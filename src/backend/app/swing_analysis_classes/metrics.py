
"""
Docstring for backend.app.swing_analysis_classes.metrics

FACE-ON METRICS

Primary role: symmetry, tilt, rotation, lateral motion

Face-On — Address / Setup (static window)
| Metric Name                | Definition                                          | Signal Type       |
| ---------------------------| --------------------------------------------------- | ----------------- |
| Shoulder tilt              | Angle between shoulders and horizontal              | Scalar            |
| Hip tilt                   | Angle between hips and horizontal                   | Scalar            |
| Spine tilt                 | Angle between mid-hips → mid-shoulders and vertical | Scalar            |
| Stance width               | Distance between ankles / shoulder width            | Normalized scalar |

Face-On — Motion (entire swing window)
| Metric Name                | Definition                                          | Signal Type       |
| -------------------------- | ----------------------------------------------------| ------------------|
| Max shoulder rotation      | Max-min shoulder rotation angle                     | Range             |
| Max hip rotation           | Max-min hip rotation angle                          | Range             |
| X-factor range             | (Shoulder - hip) max delta                          | Range             |
| Shoulder rotation rate     | Peak angular velocity                               | Rate              |
| Hip rotation rate          | Peak angular velocity                               | Rate              |
| Head lateral displacement  | Max X - min X                                       | Range             |
| Head vertical displacement | Max Y - min Y                                       | Range             |
| Trail knee flex range      | Max - min knee angle                                | Range             |


DOWN-THE-LINE METRICS

Primary role: depth, posture, delivery proxies

Down-the-Line — Address / Setup (static window)
| Metric Name                | Definition                                          | Signal Type       |
| ---------------------------| ----------------------------------------------------| ------------------|
| Spine angle                | Spine vs vertical                                   | Scalar            |
| Arm hang angle             | Shoulder → wrist angle                              | Scalar            |
| Hand depth                 | Avg Z of wrists                                     | Scalar            |
| Forward bend               | Hip → shoulder pitch                                | Scalar            |

Down-the-Line — Motion (entire swing window)
| Metric Name                | Definition                                          | Signal Type       |
| ---------------------------| ----------------------------------------------------| ------------------|
| Hand depth range           | Max Z - min Z                                       | Range             |
| Hand depth rate            | Max                                                 | dZ/dt             |
| Peak hand speed            | Max wrist velocity magnitude                        | Peak              |
| Shoulder plane stability   | Std dev of shoulder rotation axis                   | Variance          |
| Trail elbow depth range    | Max Z - min Z                                       | Range             |
| Pelvis depth stability     | Std dev of hip Z                                    | Variance          |


"""

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import numpy  as np
from   typing import Any, Dict, List

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
#   CLASS NAME: MetricsCalculator
#
#   DESCRIPTION:
#       Handles the calculation and organization of various swing
#       metrics generated from the extrapolated pose data.
#
# ---------------------------------------------------------------------
class MetricsCalculator:

    def __init__( 
            self,
            face_on_pose_data: List[ Dict[ str, Any ] ],
            down_the_line_pose_data: List[ Dict[ str, Any ] ]
        ) -> None:

        # -------------------------------------------------------------
        # Initialize the pose data with the frame data outputted by
        # pose_estimation.py.
        # -------------------------------------------------------------        
        self.face_on_pose_data       = face_on_pose_data
        self.down_the_line_pose_data = down_the_line_pose_data

        # -------------------------------------------------------------
        # Initialize the metrics dictionary.
        # -------------------------------------------------------------
        self.metrics = self._build_metrics_output()


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _build_metrics_output
    #
    #   DESCRIPTION:
    #       Structures the public facing metric data.
    #
    # -----------------------------------------------------------------
    def _build_metrics_output( self ) -> Dict[ str, Any ]:

        return {
            "face_on": {
                "metrics": self._calculate_face_on_metrics()
            },
            "down_the_line": {
                "metrics": self._calculate_down_the_line_metrics()
            }
        }

    
    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_face_on_metrics
    #
    #   DESCRIPTION:
    #       Calculates all the face-on swing metrics.
    #
    # -----------------------------------------------------------------
    def _calculate_face_on_metrics( self ) -> dict:
        return {
            "shoulder_tilt_at_impact": {
                "value": 12.4,
                "unit": "degrees"
            },
            "hip_sway_at_top": {
                "value": 1.5,
                "unit": "inches"
            },
            "shaft_lean_at_impact": {
                "value": 8.5,
                "unit": "degrees"
            },
            "head_vertical_movement": {
                "value": -1.2,
                "unit": "inches"
            },
            "wrist_hinge_angle_max": {
                "value": 82.0,
                "unit": "degrees"
            }
        }


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_down_the_line_metrics
    #
    #   DESCRIPTION:
    #       Calculates all the down-the-line swing metrics.
    #
    # -----------------------------------------------------------------
    def _calculate_down_the_line_metrics( self ) -> dict:
        return {
            "shaft_plane_angle": {
                "value": 45.0,
                "unit": "degrees"
            },
            "shoulder_alignment_at_address": {
                "value": 0.0,
                "unit": "degrees"
            },
            "hand_depth_at_top": {
                "value": 15.2,
                "unit": "inches"
            },
            "club_path_angle": {
                "value": 2.5,
                "unit": "degrees"
            },
            "spine_angle_retention": {
                "value": -2.1,
                "unit": "degrees"
            }
        }


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
