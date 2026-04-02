
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
| Stance Width               | Ratio between ankle width and shoulder width        | Ratio             |

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
# Add the parent and grandparent directories to the system path to
# allow for relative imports.
# ---------------------------------------------------------------------
PARENT_DIR       = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
GRAND_PARENT_DIR = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
sys.path.append( PARENT_DIR )
sys.path.append( GRAND_PARENT_DIR )

from swing_analysis_classes.metrics.fo      import ( fo_shoulder_tilt,
                                                     fo_hip_tilt,
                                                     fo_stance_width,
                                                     fo_spine_tilt,
                                                     fo_hip_rotation_range )
from swing_analysis_classes.metrics.dtl     import ( dtl_forward_bend,
                                                     dtl_arm_hang_angle )                 
from lib                                    import *
from typing                                 import Any, Dict
from swing_analysis_classes.pose_estimation import PoseEstimation

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# NOTE: CAN EVENTUALLY BE USED TO EASE DICTIONARY LOADING. CAN ALSO BE EDITED
# TO SUPPORT GRADING BANDS.
# -----------------------------------------------------------------------------
def _metric( label, value, units, valid_range, ideal_range ):
    return {
        "label": label,
        "value": value,
        "units": units,
        "valid_range": valid_range,
        "ideal_range": ideal_range
    }

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
            face_on_data: FullData,
            down_the_line_data: FullData
        ) -> None:

        # -------------------------------------------------------------
        # Initialize the pose data with the frame data outputted by
        # pose_estimation.py.
        # -------------------------------------------------------------        
        self.face_on_data       = face_on_data
        self.down_the_line_data = down_the_line_data

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

        # jack 169
        # ryan 94
        frame  = self.face_on_data[ "frames" ][ 169 ]
        width  = self.face_on_data[ "metadata" ][ "width" ]
        height = self.face_on_data[ "metadata" ][ "height" ]

        return {

            # ---------------------------------------------------------
            # Shoulder Tilt
            # ---------------------------------------------------------
            "Shoulder_Tilt": {
                "label": "Shoulder Tilt",
                "value": fo_shoulder_tilt( frame, width, height ),
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Hip Tilt
            # ---------------------------------------------------------
            "Hip_Tilt": {
                "label": "Hip Tilt",
                "value": fo_hip_tilt( frame, width, height ),
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Stance Width
            # ---------------------------------------------------------
            "Stance_Width": {
                "label": "Stance Width",
                "value": fo_stance_width( frame ),
                "units": "ratio",
            },

            # ---------------------------------------------------------
            # Spine Tilt
            # ---------------------------------------------------------
            "Spine_Tilt": {
                "label": "Spine Tilt",
                "value": fo_spine_tilt( frame, width, height ),
                "units": "degrees",
            }
        }


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

        # jack address 169, top 203
        # ryan 524
        frame  = self.face_on_data[ "frames" ][ 169 ]
        width  = self.face_on_data[ "metadata" ][ "width" ]
        height = self.face_on_data[ "metadata" ][ "height" ]

        return {

            # ---------------------------------------------------------
            # Forward Bend
            # ---------------------------------------------------------
            "Max_Hip_Rotation": {
                "label": "Max Hip Rotation",
                "value": fo_hip_rotation_range( self.face_on_data[ "frames" ], 169, 203 ),
                "units": "degrees",
            },
        }


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

        # jack 9
        # ryan 524
        frame  = self.down_the_line_data[ "frames" ][ 9 ]
        width  = self.down_the_line_data[ "metadata" ][ "width" ]
        height = self.down_the_line_data[ "metadata" ][ "height" ]

        return {

            # ---------------------------------------------------------
            # Forward Bend
            # ---------------------------------------------------------
            "Forward_Bend": {
                "label": "Forward Bend",
                "value": dtl_forward_bend( frame, width, height ),
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Arm Hang Angle
            # ---------------------------------------------------------
            "Arm_Hang": {
                "label": "Arm Hang Angle",
                "value": dtl_arm_hang_angle( frame, width, height ),
                "units": "degrees",
            },
        }


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
    
    # -------------------------------------------------------------
    # Extract the pose data from the processed footage.
    # -------------------------------------------------------------
    pose_estimator = PoseEstimation(
        face_on_path = "H:\\GIT\\swing.coach\\test_swings\\j_fo_2.MOV",
        down_the_line_path = "H:\\GIT\\swing.coach\\test_swings\\test_swing_raw.mp4",
        temp_dir_path = "H:\\GIT\\swing.coach\\test_swings"
    )

    # -------------------------------------------------------------
    # Perform metrics calculations based on the extracted pose data.
    # -------------------------------------------------------------
    metrics_calculator = MetricsCalculator(
        face_on_data = pose_estimator.face_on_data,
        down_the_line_data = pose_estimator.down_the_line_data
    )

    print( metrics_calculator.metrics )
