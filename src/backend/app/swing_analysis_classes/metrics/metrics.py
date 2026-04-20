

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import os
import statistics
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
                                                     dtl_arm_hang_angle,
                                                     dtl_shoulder_rotation_depth,
                                                     dtl_pelvis_depth )                 
from lib                                    import *
from typing                                 import Any, Dict
from scipy                                  import stats
from swing_analysis_classes.segmentation    import Segmentation

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

def frame_idx_to_array_idx( frames, target_frame_index ) -> int:
    """
    Maps a frame_index value to its corresponding position
    in the frames array.
    """
    for i, f in enumerate( frames ):
        if f[ "frame_index" ] == target_frame_index:
            return i
    return 0

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
        # Run segmentation to obtain swing phase indices
        # -------------------------------------------------------------
        self.segmentation = Segmentation(
            face_on_data       = self.face_on_data[ "frames" ],
            down_the_line_data = self.down_the_line_data[ "frames" ]
        )

        self.segments = self.segmentation.segments

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


    # ---------------------------------------------------------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_face_on_address_metrics
    #
    #   DESCRIPTION:
    #       Calculates static setup metrics from the predefined face-on address frame.
    #
    #       Face-On — Address / Setup (static window)
    #       | Metric Name                | Definition                                          | Signal Type       |
    #       | ---------------------------| --------------------------------------------------- | ----------------- |
    #       | Shoulder tilt              | Angle between shoulders and horizontal              | Scalar            |
    #       | Hip tilt                   | Angle between hips and horizontal                   | Scalar            |
    #       | Spine tilt                 | Angle between mid-hips → mid-shoulders and vertical | Scalar            |
    #       | Stance Width               | Ratio between ankle width and shoulder width        | Ratio             |
    #
    # ---------------------------------------------------------------------------------------------------------------
    def _calculate_face_on_address_metrics( self ) -> Dict[ str, Any ]:

        # -------------------------------------------------------------
        # REFERENCE FRAME SELECTION:
        # -------------------------------------------------------------
        frames = self.face_on_data[ "frames" ]

        addr_idx = frame_idx_to_array_idx(
            frames,
            self.segments[ "face_on" ][ "address" ]
        )

        frame = frames[ addr_idx ]
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
            # Spine Tilt
            # ---------------------------------------------------------
            "Spine_Tilt": {
                "label": "Spine Tilt",
                "value": fo_spine_tilt( frame, width, height ),
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Stance Width
            # ---------------------------------------------------------
            "Stance_Width": {
                "label": "Stance Width",
                "value": fo_stance_width( frame ),
                "units": "ratio",
            }
        }


    # ---------------------------------------------------------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_face_on_motion_metrics
    #
    #   DESCRIPTION:
    #       Calculates dynamic motion metrics across the entire face-on swing window.
    #
    #       Face-On — Motion (entire swing window)
    #       | Metric Name                | Definition                                          | Signal Type       |
    #       | -------------------------- | ----------------------------------------------------| ------------------|
    #       | Max hip rotation           | Max-min hip rotation angle backswing                | Range             |
    #       | Max shoulder rotation      | Max-min shoulder rotation angle backswing           | Range             |
    #       | X-factor range             | (Shoulder - hip) max delta at top of backswing      | Range             |
    #       | Head lateral displacement  | Max X - min X                                       | Range             |
    #       | Head vertical displacement | Max Y - min Y                                       | Range             |
    #
    # ---------------------------------------------------------------------------------------------------------------
    def _calculate_face_on_motion_metrics( self ) -> Dict[ str, Any ]:

        # -------------------------------------------------------------
        # REFERENCE FRAME SELECTION:
        # -------------------------------------------------------------
        frames = self.face_on_data[ "frames" ]

        addr_idx = frame_idx_to_array_idx(
            frames,
            self.segments[ "face_on" ][ "address" ]
        )

        top_idx = frame_idx_to_array_idx(
            frames,
            self.segments[ "face_on" ][ "top_of_backswing" ]
        )

        frame  = frames[ addr_idx ]
        width  = self.face_on_data[ "metadata" ][ "width" ]
        height = self.face_on_data[ "metadata" ][ "height" ]
        
        # -------------------------------------------------------------
        # Down the line reference data used for calculating forward
        # bend. This is so we can tilt correct our rotational metrics.
        # -------------------------------------------------------------
        dtl_frame  = self.down_the_line_data[ "frames" ][ 535 ]
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
        for frame in self.face_on_data[ "frames" ][ addr_idx:top_idx ]:

            # ---------------------------------------------------------
            # Calculate the hip and shoulder rotation angles relative
            # to address and tilt corrected for forward bend.
            # ---------------------------------------------------------
            hip_rot_angle = fo_hip_rotation_range( frame, frame, forward_bend )
            hip_rot_angle = hip_rot_angle if hip_rot_angle is not None else 0.0

            shld_rot_angle = fo_shoulder_rotation_range( frame, frame, forward_bend )
            shld_rot_angle = shld_rot_angle if shld_rot_angle is not None else 0.0

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
            # Calculate the lateral and vertical head displacement
            # relative to address, normalized by shoulder width.
            # ---------------------------------------------------------
            head_disp = fo_head_displacement( frame, frame, width, height )
            head_disp = head_disp if head_disp is not None else [ 0.0, 0.0 ]

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
                "value": ( max( shoulder_rotation_angles ) - max( hip_rotation_angles ) ) if shoulder_rotation_angles and hip_rotation_angles else 0.0,
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Head Lateral Displacement
            # ---------------------------------------------------------
            "Head_Lateral_Displacement": {
                "label": "Head Lateral Displacement",
                "value": ( max( head_lateral_displacement ) - min( head_lateral_displacement ) ) if head_lateral_displacement else 0.0,
                "units": "shoulder widths",
            },

            # ---------------------------------------------------------
            # Head Vertical Displacement
            # ---------------------------------------------------------
            "Head_Vertical_Displacement": {
                "label": "Head Vertical Displacement",
                "value": ( max( head_vertical_displacement ) - min( head_vertical_displacement ) ) if head_vertical_displacement else 0.0,
                "units": "shoulder widths",
            }
        }


    # ---------------------------------------------------------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_dtl_address_metrics
    #
    #   DESCRIPTION:
    #       Calculates static setup metrics from the predefined down-the-line address frame.
    #
    #       Down-the-Line — Address / Setup (static window)
    #       | Metric Name                | Definition                                          | Signal Type       |
    #       | ---------------------------| ----------------------------------------------------| ------------------|
    #       | Forward bend               | Hip → shoulder pitch                                | Scalar            |
    #       | Arm hang angle             | Shoulder → wrist angle                              | Scalar            |
    #
    # ---------------------------------------------------------------------------------------------------------------
    def _calculate_dtl_address_metrics( self ) -> Dict[ str, Any ]:

        # -------------------------------------------------------------
        # REFERENCE FRAME SELECTION:
        # -------------------------------------------------------------
        frames = self.down_the_line_data[ "frames" ]

        addr_idx = frame_idx_to_array_idx(
            frames,
            self.segments[ "down_the_line" ][ "address" ]
        )

        frame  = frames[ addr_idx ]
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


    # ---------------------------------------------------------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_dtl_motion_metrics
    #
    #   DESCRIPTION:
    #       Calculates dynamic motion metrics across the entire down-the-line swing window.
    #
    #       Down-the-Line — Motion (entire swing window)
    #       | Metric Name                | Definition                                          | Signal Type       |
    #       | ---------------------------| ----------------------------------------------------| ------------------|
    #       | Shoulder plane stability   | Std dev of shoulder rotation axis                   | Variance          |
    #       | Pelvis depth stability     | Std dev of hip Z                                    | Variance          |
    #
    # ---------------------------------------------------------------------------------------------------------------
    def _calculate_dtl_motion_metrics( self ) -> Dict[ str, Any ]:

        # -------------------------------------------------------------
        # REFERENCE FRAME SELECTION:
        # -------------------------------------------------------------
        frames = self.down_the_line_data[ "frames" ]

        addr_idx = frame_idx_to_array_idx(
            frames,
            self.segments[ "down_the_line" ][ "address" ]
        )

        top_idx = frame_idx_to_array_idx(
            frames,
            self.segments[ "down_the_line" ][ "top_of_backswing" ]
        )

        frame  = frames[ addr_idx ]
        width  = self.down_the_line_data[ "metadata" ][ "width" ]
        height = self.down_the_line_data[ "metadata" ][ "height" ]

        # -------------------------------------------------------------
        # Calculate the forward bend. Used as a correction factor.
        # -------------------------------------------------------------
        forward_bend = dtl_forward_bend( frame, width, height )
        forward_bend = forward_bend if forward_bend is not None else 0.0

        # -------------------------------------------------------------
        # Placeholder for hip and shoulder rotation angles across the
        # swing. 
        # -------------------------------------------------------------
        shoulder_plane_angles = []
        pelvis_depth_values   = []

        # -------------------------------------------------------------
        # Iterate through the swing frames from address to the top of
        # the backswing and calculate the hip and shoulder rotation
        # angles.
        # -------------------------------------------------------------
        for frame in self.down_the_line_data[ "frames" ][ addr_idx:top_idx ]:
            
            # ---------------------------------------------------------
            # Calculate the shoulder plane angle for the current frame.
            # ---------------------------------------------------------
            shld_plane_angle = dtl_shoulder_rotation_depth( frame, frame, forward_bend )
            shld_plane_angle = shld_plane_angle if shld_plane_angle is not None else 0.0

            # ---------------------------------------------------------
            # Grab the angle delta between the current angle and the
            # angle from the previous frame.
            # ---------------------------------------------------------
            shld_plane_delta = shld_plane_angle - shoulder_plane_angles[ -1 ] if shoulder_plane_angles else 0.0

            # ---------------------------------------------------------
            # If the delta exceeds 90 degrees, we likely have an angle
            # wraparound issue and should flip the angle to the correct
            # quadrant.
            # ---------------------------------------------------------
            if shld_plane_delta > 90:
                shld_plane_angle = 180 - shld_plane_angle

            # ---------------------------------------------------------
            # Append the shoulder plane angle for the current frame.
            # ---------------------------------------------------------
            shoulder_plane_angles.append( shld_plane_angle )

            # ---------------------------------------------------------
            # Calculate the pelvic depth value for the current frame,
            # and append to the list of values.
            # ---------------------------------------------------------
            depth = dtl_pelvis_depth( frame )

            if depth is not None:
                pelvis_depth_values.append( depth )

        return { 

            # ---------------------------------------------------------
            # Shoulder Plane Stability
            # ---------------------------------------------------------
            "Shoulder_Plane_Stability": {
                "label": "Shoulder Plane Stability",
                "value": stats.circstd( shoulder_plane_angles, high=180, low=-180 ) if shoulder_plane_angles else 0.0,
                "units": "degrees",
            },

            # ---------------------------------------------------------
            # Pelvis Depth Stability
            # ---------------------------------------------------------
            "Pelvis_Depth_Stability": {
                "label": "Pelvis Depth Stability",
                "value": statistics.stdev( pelvis_depth_values ) if len( pelvis_depth_values ) > 1 else 0.0,
                "units": "meters",
            }
        }


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    pass