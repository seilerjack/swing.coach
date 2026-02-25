
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
| Max shoulder rotation      | Max-min shoulder rotation angle backswing           | Range             |
| Max hip rotation           | Max-min hip rotation angle backswing                | Range             |
| X-factor range             | (Shoulder - hip) max delta at top of backswing      | Range             |
| Shoulder rotation rate     | Peak angular velocity                               | Rate              |
| Hip rotation rate          | Peak angular velocity                               | Rate              |
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
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # 
    #   PROCEDURE NAME: _get_point
    #
    #   DESCRIPTION:
    #       Extracts a world-normalized landmark from a frame and
    #       returns it as a NumPy vector.
    #
    # -----------------------------------------------------------------
    def _get_point(
            self,
            frame: Dict[ str, Any ],
            name: str
        ) -> np.ndarray:

        # -------------------------------------------------------------
        # Access landmark dictionary and convert to NumPy array.
        # -------------------------------------------------------------
        lm = frame[ "landmarks" ][ name ][ "world_normalized" ]

        return np.array(
            [ lm[ "x" ], lm[ "y" ], lm[ "z" ] ],
            dtype = float
        )


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _angle_horizontal
    #
    #   DESCRIPTION:
    #       Computes the 2D angle (degrees) between two points in
    #       the XY plane relative to the horizontal axis.
    #
    # -----------------------------------------------------------------
    def _angle_horizontal(
            self, 
            p1: np.ndarray,
            p2: np.ndarray
        ) -> float:

        # -------------------------------------------------------------
        # Compute vector between points.
        # -------------------------------------------------------------
        vec = p2 - p1

        # -------------------------------------------------------------
        # Calculate angle relative to horizontal axis.
        # -------------------------------------------------------------
        angle_rad = np.arctan2( vec[ 1 ], vec[ 0 ] )

        return np.degrees( angle_rad )


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _angle_from_vertical
    #
    #   DESCRIPTION:
    #       Computes the angle (degrees) between a 2D vector and
    #       the vertical axis.
    #
    # -----------------------------------------------------------------
    def _angle_from_vertical(
            self,
            vec: np.ndarray
        ) -> float:

        # -------------------------------------------------------------
        # Define vertical reference vector.
        # -------------------------------------------------------------
        vertical = np.array( [ 0.0, 1.0 ] )

        # -------------------------------------------------------------
        # Normalize XY projection of vector.
        # -------------------------------------------------------------
        vec_2d = vec[ :2 ]
        vec_2d = vec_2d / np.linalg.norm( vec_2d )

        # -------------------------------------------------------------
        # Compute angular deviation from vertical.
        # -------------------------------------------------------------
        dot   = np.dot( vec_2d, vertical )
        angle = np.degrees( np.arccos( dot ) )

        return angle


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
    #   PROCEDURE NAME: _calculate_face_on_address_metrics
    #
    #   DESCRIPTION:
    #       Calculates static setup metrics from the predefined
    #       face-on address frame.
    #
    # -----------------------------------------------------------------
    def _calculate_face_on_address_metrics( self ) -> Dict[ str, Any ]:

        frame = self.face_on_pose_data[ FO_ADDRESS ]

        # -------------------------------------------------------------
        # Calculate static tilt and stance metrics.
        # -------------------------------------------------------------
        shoulder_tilt = self._shoulder_tilt( frame )
        hip_tilt      = self._hip_tilt( frame )
        spine_tilt    = self._spine_tilt( frame )
        stance_width  = self._stance_width( frame )

        return {
            "shoulder_tilt": {
                "value": float( shoulder_tilt ),
                "unit": "degrees"
            },
            "hip_tilt": {
                "value": float( hip_tilt ),
                "unit": "degrees"
            },
            "spine_tilt": {
                "value": float( spine_tilt ),
                "unit": "degrees"
            },
            "stance_width": {
                "value": float( stance_width ),
                "unit": "model_units"
            }
        }
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _shoulder_tilt
    #
    #   DESCRIPTION:
    #       Calculates shoulder tilt at a given frame using the
    #       angle between left and right shoulder landmarks.
    #
    # -----------------------------------------------------------------
    def _shoulder_tilt(
            self,
            frame: Dict[ str, Any ]
        ) -> float:

        # -------------------------------------------------------------
        # Retrieve shoulder landmarks.
        # -------------------------------------------------------------
        left  = self._get_point( frame, "LEFT_SHOULDER" )
        right = self._get_point( frame, "RIGHT_SHOULDER" )

        # -------------------------------------------------------------
        # Compute horizontal angle between shoulders.
        # -------------------------------------------------------------
        return self._angle_horizontal( left, right )
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _hip_tilt
    #
    #   DESCRIPTION:
    #       Calculates hip tilt at a given frame using the
    #       angle between left and right hip landmarks.
    #
    # -----------------------------------------------------------------
    def _hip_tilt(
            self,
            frame: Dict[ str, Any ]
        ) -> float:

        left  = self._get_point( frame, "LEFT_HIP" )
        right = self._get_point( frame, "RIGHT_HIP" )

        return self._angle_horizontal( left, right )
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _spine_tilt
    #
    #   DESCRIPTION:
    #       Calculates spine tilt relative to vertical using the
    #       midpoint between hips and shoulders.
    #
    # -----------------------------------------------------------------
    def _spine_tilt(
            self,
            frame: Dict[ str, Any ]
        ) -> float:

        # -------------------------------------------------------------
        # Retrieve shoulder and hip landmarks.
        # -------------------------------------------------------------
        left_sh   = self._get_point( frame, "LEFT_SHOULDER" )
        right_sh  = self._get_point( frame, "RIGHT_SHOULDER" )
        left_hip  = self._get_point( frame, "LEFT_HIP" )
        right_hip = self._get_point( frame, "RIGHT_HIP" )

        # -------------------------------------------------------------
        # Compute midpoints.
        # -------------------------------------------------------------
        mid_sh  = ( left_sh  + right_sh  ) / 2.0
        mid_hip = ( left_hip + right_hip ) / 2.0

        # -------------------------------------------------------------
        # Compute spine vector (hip → shoulder).
        # -------------------------------------------------------------
        spine_vec = mid_sh - mid_hip

        return self._angle_from_vertical( spine_vec )
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _stance_width
    #
    #   DESCRIPTION:
    #       Computes horizontal stance width using the X-axis
    #       separation between ankle landmarks.
    #
    # -----------------------------------------------------------------
    def _stance_width(
            self,
            frame: Dict[ str, Any ]
        ) -> float:

        # -------------------------------------------------------------
        # Retrieve ankle landmarks.
        # -------------------------------------------------------------
        left  = self._get_point( frame, "LEFT_ANKLE" )
        right = self._get_point( frame, "RIGHT_ANKLE" )

        # -------------------------------------------------------------
        # Compute horizontal separation (X-axis only).
        # -------------------------------------------------------------
        return abs( left[ 0 ] - right[ 0 ] )
    

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
        # Extract swing window frames.
        # -------------------------------------------------------------
        frames = self.face_on_pose_data[ FO_ADDRESS : FO_IMPACT + 1 ]

        # -------------------------------------------------------------
        # Placeholder motion metrics (to be implemented).
        # -------------------------------------------------------------
        return {
            "max_shoulder_rotation": {
                "value": 0.0,
                "unit": "degrees"
            },
            "max_hip_rotation": {
                "value": 0.0,
                "unit": "degrees"
            },
            "x_factor_range": {
                "value": 0.0,
                "unit": "degrees"
            },
            "shoulder_rotation_rate": {
                "value": 0.0,
                "unit": "deg_per_frame"
            },
            "hip_rotation_rate": {
                "value": 0.0,
                "unit": "deg_per_frame"
            },
            "head_lateral_displacement": {
                "value": 0.0,
                "unit": "normalized_units"
            },
            "head_vertical_displacement": {
                "value": 0.0,
                "unit": "normalized_units"
            },
            "trail_knee_flex_range": {
                "value": 0.0,
                "unit": "degrees"
            }
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
    #   PROCEDURE NAME: _calculate_dtl_address_metrics
    #
    #   DESCRIPTION:
    #       Calculates static setup metrics from the predefined
    #       down-the-line address frame.
    #
    # -----------------------------------------------------------------
    def _calculate_dtl_address_metrics( self ) -> Dict[ str, Any ]:

        frame = self.down_the_line_pose_data[ DTL_ADDRESS ]

        return {
            "spine_angle": {
                "value": 0.0,
                "unit": "degrees"
            },
            "arm_hang_angle": {
                "value": 0.0,
                "unit": "degrees"
            },
            "hand_depth": {
                "value": 0.0,
                "unit": "normalized_units"
            },
            "forward_bend": {
                "value": 0.0,
                "unit": "degrees"
            }
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

        frames = self.down_the_line_pose_data[ DTL_ADDRESS : DTL_IMPACT + 1 ]

        return {
            "hand_depth_range": {
                "value": 0.0,
                "unit": "normalized_units"
            },
            "hand_depth_rate": {
                "value": 0.0,
                "unit": "units_per_frame"
            },
            "peak_hand_speed": {
                "value": 0.0,
                "unit": "units_per_frame"
            },
            "shoulder_plane_stability": {
                "value": 0.0,
                "unit": "variance"
            },
            "trail_elbow_depth_range": {
                "value": 0.0,
                "unit": "normalized_units"
            },
            "pelvis_depth_stability": {
                "value": 0.0,
                "unit": "variance"
            }
        }


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
