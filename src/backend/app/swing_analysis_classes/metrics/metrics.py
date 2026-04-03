
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
                                                     fo_hip_rotation_range,
                                                     fo_shoulder_rotation_range,
                                                     fo_head_displacement )
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

        # jack address 33
        frame  = self.face_on_data[ "frames" ][ 33 ]
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

        # -------------------------------------------------------------
        # REFERENCE FRAME SELECTION:
        # -------------------------------------------------------------
        # jack address 33, top 64
        # ryan address 122, top 323

        # -------------------------------------------------------------
        # Reference to address frame. Used to allow consistent angle
        # delta calculations against the current frame.
        # -------------------------------------------------------------
        addr_frame  = self.face_on_data[ "frames" ][ 33 ]
        width = self.face_on_data[ "metadata" ][ "width" ]
        height = self.face_on_data[ "metadata" ][ "height" ]
        
        # -------------------------------------------------------------
        # Down the line reference data used for calculating forward
        # bend. This is so we can tilt correct our rotational metrics.
        # -------------------------------------------------------------
        dtl_frame  = self.down_the_line_data[ "frames" ][ 57 ]
        dtl_width  = self.down_the_line_data[ "metadata" ][ "width" ]
        dtl_height = self.down_the_line_data[ "metadata" ][ "height" ]

        # -------------------------------------------------------------
        # Calculate the forward bend. Used as a correction factor.
        # -------------------------------------------------------------
        forward_bend = dtl_forward_bend( dtl_frame, dtl_width, dtl_height )
        forward_bend = forward_bend if forward_bend is not None else 0.0

        # -------------------------------------------------------------
        # Placeholder for hip and shoulder rotation angles across the
        # swing. 
        # -------------------------------------------------------------
        hip_rotation_angles        = []
        shoulder_rotation_angles   = []
        head_lateral_displacement  = []
        head_vertical_displacement = []

        # -------------------------------------------------------------
        # Iterate through the swing frames from address to the top of
        # the backswing and calculate the hip and shoulder rotation
        # angles.
        # -------------------------------------------------------------
        for frame in self.face_on_data[ "frames" ][ 33:65 ]:

            # ---------------------------------------------------------
            # Calculate the hip and shoulder rotation angles relative
            # to address and tilt corrected for forward bend.
            # ---------------------------------------------------------
            hip_rot_angle = fo_hip_rotation_range( addr_frame, frame, forward_bend )
            hip_rot_angle = hip_rot_angle if hip_rot_angle is not None else 0.0

            shld_rot_angle = fo_shoulder_rotation_range( addr_frame, frame, forward_bend )
            shld_rot_angle = shld_rot_angle if shld_rot_angle is not None else 0.0

            # ---------------------------------------------------------
            # Calculate the lateral and vertical head displacement
            # relative to address, normalized by shoulder width.
            # ---------------------------------------------------------
            head_disp = fo_head_displacement( addr_frame, frame, width, height )
            head_disp = head_disp if head_disp is not None else [ 0.0, 0.0 ]

            # ---------------------------------------------------------
            # Grab the angle delta between the current angle and the
            # angle from the previous frame.
            # ---------------------------------------------------------
            hip_delta      = hip_rot_angle - hip_rotation_angles[ -1 ] if hip_rotation_angles else 0.0
            shld_rot_delta = shld_rot_angle - shoulder_rotation_angles[ -1 ] if shoulder_rotation_angles else 0.0

            # ---------------------------------------------------------
            # If the delta exceeds 90 degrees, we likely have an angle
            # wraparound issue and should flip the angle to the correct
            # quadrant.
            # ---------------------------------------------------------
            if hip_delta > 90:
                hip_rot_angle = 180 - hip_rot_angle

            if shld_rot_delta > 90:
                shld_rot_angle = 180 - shld_rot_angle

            # ---------------------------------------------------------
            # Append the hip and shoulder rotation angles for the
            # current frame.
            # ---------------------------------------------------------
            hip_rotation_angles.append( hip_rot_angle )
            shoulder_rotation_angles.append( shld_rot_angle )

            # ---------------------------------------------------------
            # Append the head lateral and vertical displacement for the
            # current frame.
            # ---------------------------------------------------------
            head_lateral_displacement.append( head_disp[ 0 ] )
            head_vertical_displacement.append( head_disp[ 1 ] )


        return {

            # ---------------------------------------------------------
            # Max Hip Rotation
            # ---------------------------------------------------------
            "Max_Hip_Rotation": {
                "label": "Max Hip Rotation",
                "value": max( hip_rotation_angles ) if hip_rotation_angles else 0.0,
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Max Shoulder Rotation
            # ---------------------------------------------------------
            "Max_Shoulder_Rotation": {
                "label": "Max Shoulder Rotation",
                "value": max( shoulder_rotation_angles ) if shoulder_rotation_angles else 0.0,
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # X-Factor Range
            # ---------------------------------------------------------
            "X-Factor_Range": {
                "label": "X-Factor Range",
                "value": ( max( shoulder_rotation_angles ) - max( hip_rotation_angles ) ),
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Head Lateral Displacement
            # ---------------------------------------------------------
            "Head_Lateral_Displacement": {
                "label": "Head Lateral Displacement",
                "value": max( head_lateral_displacement ) - min( head_lateral_displacement ) if head_lateral_displacement else 0.0,
                "units": "shoulder widths",
            },

            # ---------------------------------------------------------
            # Head Vertical Displacement
            # ---------------------------------------------------------
            "Head_Vertical_Displacement": {
                "label": "Head Vertical Displacement",
                "value": max( head_vertical_displacement ) - min( head_vertical_displacement ) if head_vertical_displacement else 0.0,
                "units": "shoulder widths",
            }
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

        # jack address 57, top 90
        # ryan address 535, top 759
        frame  = self.down_the_line_data[ "frames" ][ 57 ]
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
        face_on_path = "H:\\GIT\\swing.coach\\test_swings\\j_fo_4.MOV",
        down_the_line_path = "H:\\GIT\\swing.coach\\test_swings\\j_dtl_4.MOV",
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
