
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

Face-On — Motion (entire swing window)
| Metric Name                | Definition                                          | Signal Type       |
| -------------------------- | ----------------------------------------------------| ------------------|
| Max shoulder rotation      | Max-min shoulder rotation angle backswing           | Range             |
| Max hip rotation           | Max-min hip rotation angle backswing                | Range             |
| X-factor range             | (Shoulder - hip) max delta at top of backswing      | Range             |
| Head lateral displacement  | Max X - min X                                       | Range             |
| Head vertical displacement | Max Y - min Y                                       | Range             |
| Trail knee flex range      | Max - min knee angle between address and backswing  | Range             |


DOWN-THE-LINE METRICS

Primary role: depth, posture, delivery proxies

Down-the-Line — Address / Setup (static window)
| Metric Name                | Definition                                          | Signal Type       |
| ---------------------------| ----------------------------------------------------| ------------------|
| Spine angle                | Spine vs vertical                                   | Scalar            |
| Arm hang angle             | Shoulder → wrist angle                              | Scalar            |
| Forward bend               | Hip → shoulder pitch                                | Scalar            |

Down-the-Line — Motion (entire swing window)
| Metric Name                | Definition                                          | Signal Type       |
| ---------------------------| ----------------------------------------------------| ------------------|
| Shoulder plane stability   | Std dev of shoulder rotation axis                   | Variance          |
| Trail elbow depth range    | Max Z - min Z                                       | Range             |
| Pelvis depth stability     | Std dev of hip Z                                    | Variance          |

"""

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

from lib                                    import *
from typing                                 import Any, Dict, List

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
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------

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
    #       Parent procedure for all face-on metrics. Splits address
    #       (static window) and motion (entire swing window) metrics.
    #
    # -----------------------------------------------------------------
    def _calculate_face_on_metrics( self ) -> Dict[ str, Any ]:

        return {
            "address": self._calculate_face_on_address_metrics(),
            "motion" : self._calculate_face_on_motion_metrics()
        }
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_down_the_line_metrics
    #
    #   DESCRIPTION:
    #       Parent procedure for all down-the-line metrics.
    #       Splits address and motion metrics.
    #
    # -----------------------------------------------------------------
    def _calculate_down_the_line_metrics( self ) -> Dict[ str, Any ]:

        return {
            "address": self._calculate_dtl_address_metrics(),
            "motion" : self._calculate_dtl_motion_metrics()
        }


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_face_on_address_metrics
    #
    #   DESCRIPTION:
    #       Calculates static setup metrics from the predefined
    #       face-on address frame.
    #
    # -----------------------------------------------------------------
    def _calculate_face_on_address_metrics( self ) -> Dict[ str, Any ]:

        return { }


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_face_on_motion_metrics
    #
    #   DESCRIPTION:
    #       Calculates dynamic motion metrics across the entire
    #       face-on swing window.
    #
    # -----------------------------------------------------------------
    def _calculate_face_on_motion_metrics( self ) -> Dict[ str, Any ]:

        return { }


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_dtl_address_metrics
    #
    #   DESCRIPTION:
    #       Calculates static setup metrics from the predefined
    #       down-the-line address frame.
    #
    # -----------------------------------------------------------------
    def _calculate_dtl_address_metrics( self ) -> Dict[ str, Any ]:

        return { }


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_dtl_motion_metrics
    #
    #   DESCRIPTION:
    #       Calculates dynamic motion metrics across the entire
    #       down-the-line swing window.
    #
    # -----------------------------------------------------------------
    def _calculate_dtl_motion_metrics( self ) -> Dict[ str, Any ]:

        return { }


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    pass