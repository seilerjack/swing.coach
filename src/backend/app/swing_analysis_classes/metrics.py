

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import numpy as np
import os
import sys

# ---------------------------------------------------------------------
# Add the parent directory to the system path to allow for relative
# imports.
# ---------------------------------------------------------------------
PARENT_DIR = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
sys.path.append( PARENT_DIR )

from   swing_analysis_classes.segmentation import Segmentation
from   typing                              import Any, Dict, List

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   PROCEDURE NAME: rotation_helper
#
#   DESCRIPTION:
#       Helper for the rotational based metrics. This function computes
#       the angle between two keypoints in 2D screen space.
#
# ---------------------------------------------------------------------
def rotation_helper( frame: Dict[ str, Any ], left_key: str, right_key: str ) -> float:

    # -----------------------------------------------------------------
    # Initialize angle between the two keypoints to zero.
    # -----------------------------------------------------------------
    angle = 0.0

    # -----------------------------------------------------------------
    # Grab the landmarks from the passed frame.
    # -----------------------------------------------------------------
    landmarks = frame["landmarks"]

    # -----------------------------------------------------------------
    # If both keypoints are valid, calculate the angle between them.
    # -----------------------------------------------------------------
    if landmarks[ left_key ][ "valid" ] and landmarks[ right_key ][ "valid" ]:
        delta = np.array( [ 
            landmarks[ right_key ][ "x" ] - landmarks[ left_key ][ "x" ],
            landmarks[ right_key ][ "y" ] - landmarks[ left_key ][ "y" ]
            ] )
        angle = np.degrees( np.arctan2( delta[ 1 ], delta[ 0 ] ) )

    # -----------------------------------------------------------------
    # Return the calculated angle.
    # -----------------------------------------------------------------
    return angle


# ---------------------------------------------------------------------
#
#   PROCEDURE NAME: spine_tilt_helper
#
#   DESCRIPTION:
#       Helper for the spine tilt metrics. This function computes the 
#       angle of the spine tilt based on shoulder and hip keypoints.
#
# ---------------------------------------------------------------------
def spine_tilt_helper( frame: Dict[ str, Any ] ) -> float:

    # -----------------------------------------------------------------
    # Initialize spine tilt angle to zero.
    # -----------------------------------------------------------------
    angle = 0.0

    # -----------------------------------------------------------------
    # Grab the landmarks from the passed frame.
    # -----------------------------------------------------------------
    landmarks = frame["landmarks"]
    keys = [ "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_HIP", "RIGHT_HIP" ]
                
    # -----------------------------------------------------------------
    # Ensure all required landmarks are valid.
    # -----------------------------------------------------------------
    if all( landmarks[ k ][ "valid" ] for k in keys ):
        
        # -------------------------------------------------------------
        # Calculate midpoints for shoulders and hips.
        # -------------------------------------------------------------
        shoulder_mid = np.array( [ ( landmarks[ "LEFT_SHOULDER" ][ "x" ] + landmarks[ "RIGHT_SHOULDER" ][ "x" ] ) / 2,
                                   ( landmarks[ "LEFT_SHOULDER" ][ "y" ] + landmarks[ "RIGHT_SHOULDER" ][ "y" ] ) / 2 ] )
        hip_mid = np.array( [ ( landmarks[ "LEFT_HIP" ][ "x" ] + landmarks[ "RIGHT_HIP" ][ "x" ] ) / 2,
                              ( landmarks[ "LEFT_HIP" ][ "y" ] + landmarks[ "RIGHT_HIP" ][ "y" ] ) / 2 ] )
        
        # -------------------------------------------------------------
        # Calculate differences in x and y between shoulders and hips.
        # -------------------------------------------------------------
        dx = shoulder_mid[ 0 ] - hip_mid[ 0 ]
        dy = shoulder_mid[ 1 ] - hip_mid[ 1 ]
        
        # -------------------------------------------------------------
        # Calculate and store the spine tilt angle in degrees.
        # -------------------------------------------------------------
        angle = np.degrees( np.arctan2( dx, dy ) )

    # -----------------------------------------------------------------
    # Return the calculated angle.
    # -----------------------------------------------------------------
    return angle
    

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

    def __init__( self, pose_data: List[ Dict[ str, Any ] ] ) -> None:

        # -------------------------------------------------------------
        # Create a Segmentation object to identify key frames. This
        # will help with metric calculations.
        # -------------------------------------------------------------
        segments = Segmentation( pose_data )
        self.address_frame   = segments.address_frame
        self.backswing_frame = segments.backswing_frame
        self.impact_frame    = segments.impact_frame
        
        # -------------------------------------------------------------
        # Initialize the pose data with the fram data outputted by
        # pose_estimation.py.
        # -------------------------------------------------------------        
        self.pose_data = pose_data

        # -------------------------------------------------------------
        # Initialize the metrics dictionary.
        # -------------------------------------------------------------
        self.metrics = self._calculate_metrics()


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calculate_metrics
    #
    #   DESCRIPTION:
    #       Compiles all the calculated swing metrics and organizes
    #       them into the dictionary that will be the primary output of
    #       this class.
    #
    # -----------------------------------------------------------------
    def _calculate_metrics( self ) -> dict:

        # -------------------------------------------------------------
        # Dictionary of metrics to compute, be returned, and passed
        # through to the prompt generation.
        # -------------------------------------------------------------
        metrics = {
            "shoulder_rotation_range_deg_backswing" : self._calc_range_rotation_backswing( "LEFT_SHOULDER", "RIGHT_SHOULDER" ),
            "shoulder_rotation_range_deg"           : self._calc_range_rotation( "LEFT_SHOULDER", "RIGHT_SHOULDER" ),
            "hip_rotation_range_deg_backswing"      : self._calc_range_rotation_backswing( "LEFT_HIP", "RIGHT_HIP" ),
            "hip_rotation_range_deg"                : self._calc_range_rotation( "LEFT_HIP", "RIGHT_HIP" ),
            "spine_tilt_mean_deg"                   : self._calc_mean_spine_tilt(),
            "spine_tilt_range_deg"                  : self._calc_range_spine_tilt(),
            "head_movement_x"                       : self._calc_head_delta( axis=0 ),
            "head_movement_y"                       : self._calc_head_delta( axis=1 ),
        }
        return metrics
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calc_range_rotation_backswing
    #
    #   DESCRIPTION:
    #       Calculates the range of rotation from address to the top of
    #       the backswing. This is calculated for the specified key
    #       landmarks.
    #
    # -----------------------------------------------------------------
    def _calc_range_rotation_backswing( self, left: str, right: str ) -> float:
        
        # ---------------------------------------------------------------------
        # Empty list to hold the angles calculated between the left and right
        # landmarks.
        # ---------------------------------------------------------------------
        angles = []

        # ---------------------------------------------------------------------
        # Loop through all frames up to the top of the backswing.
        # ---------------------------------------------------------------------
        for i in range( self.address_frame, self.backswing_frame + 1 ):

            # -----------------------------------------------------------------
            # Extract the frame and the relevant landmarks
            # -----------------------------------------------------------------
            frame = self.pose_data[ i ]

            # -----------------------------------------------------------------
            # Computes the angle of the line segment between the two landmarks
            # in 2D screen space.
            # -----------------------------------------------------------------
            angle = rotation_helper( frame, left, right )
            angles.append( angle )
 
        # ---------------------------------------------------------------------
        # Return the mean angle computed across all frames up to impact. If no
        # angles were computed, return 0.0.
        # ---------------------------------------------------------------------
        return float( np.mean( angles ) ) if angles else 0.0
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calc_range_rotation
    #
    #   DESCRIPTION:
    #       Calculates the range of rotation from address to impact.
    #       This is calculated for the specified key landmarks.
    #
    # -----------------------------------------------------------------
    def _calc_range_rotation( self, left: str, right: str ) -> float:
        
        # ---------------------------------------------------------------------
        # Empty list to hold the angles calculated between the left and right
        # landmarks.
        # ---------------------------------------------------------------------
        angles = []

        # ---------------------------------------------------------------------
        # Loop through all frames up to impact.
        # ---------------------------------------------------------------------
        for i in range( self.address_frame, self.impact_frame + 1 ):

            # -----------------------------------------------------------------
            # Extract the frame and the relevant landmarks
            # -----------------------------------------------------------------
            frame = self.pose_data[ i ]

            # -----------------------------------------------------------------
            # Computes the angle of the line segment between the two landmarks
            # in 2D screen space.
            # -----------------------------------------------------------------
            angle = rotation_helper( frame, left, right )
            angles.append( angle )
 
        # ---------------------------------------------------------------------
        # Return the range of angles computed across all frames up to impact.
        # If no angles are calculated, return 0.0. Peak to peak (ptp) is just
        # max - min.
        # ---------------------------------------------------------------------
        return float( np.ptp( angles ) ) if angles else 0.0
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calc_mean_spine_tilt
    #
    #   DESCRIPTION:
    #       Calculates the average spine tilt angle from address to
    #       impact.
    #
    # -----------------------------------------------------------------
    def _calc_mean_spine_tilt( self ) -> float:
        
        # -------------------------------------------------------------
        # Empty list to hold the spine tilt angles.
        # -------------------------------------------------------------
        tilts = []
        
        # -------------------------------------------------------------
        # Loop through all frames up to impact.
        # -------------------------------------------------------------
        for i in range( self.address_frame, self.impact_frame + 1 ):
            
            # ---------------------------------------------------------
            # Extract the frame and the relevant landmarks
            # ---------------------------------------------------------
            frame = self.pose_data[ i ]

            # ---------------------------------------------------------
            # Calculate the spine tilt angle for the current frame.
            # ---------------------------------------------------------
            tilt = spine_tilt_helper( frame )
            tilts.append( tilt )

        # -------------------------------------------------------------
        # Return the mean spine tilt angle across all frames up to
        # impact. If no tilts were calculated, return 0.0.
        # -------------------------------------------------------------
        return float( np.mean( tilts ) ) if tilts else 0.0


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calc_range_spine_tilt
    #
    #   DESCRIPTION:
    #       Calculates the range of spine tilt angles from address to
    #       impact.
    #
    # -----------------------------------------------------------------
    def _calc_range_spine_tilt( self ) -> float:
        
        # -------------------------------------------------------------
        # Empty list to hold the spine tilt angles.
        # -------------------------------------------------------------
        tilts = []
        
        # -------------------------------------------------------------
        # Loop through all frames up to impact.
        # -------------------------------------------------------------
        for i in range( self.address_frame, self.impact_frame + 1 ):
            
            # ---------------------------------------------------------
            # Extract the frame and the relevant landmarks
            # ---------------------------------------------------------
            frame = self.pose_data[ i ]

            # ---------------------------------------------------------
            # Calculate the spine tilt angle for the current frame.
            # ---------------------------------------------------------
            tilt = spine_tilt_helper( frame )
            tilts.append( tilt )

        # -------------------------------------------------------------
        # Return the range of spine tilt angles across all frames up to
        # impact.
        # -------------------------------------------------------------
        return float( np.ptp( tilts ) ) if tilts else 0.0
    

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _calc_head_delta
    #
    #   DESCRIPTION:
    #       Calculates the delta of the head position along a specified
    #       axis from address to impact.
    #
    # -----------------------------------------------------------------
    def _calc_head_delta( self, axis: int ) -> float:
        
        # -------------------------------------------------------------
        # Empty list to hold the head positions.
        # -------------------------------------------------------------
        positions = []
        
        # -------------------------------------------------------------
        # Loop through all frames up to impact.
        # -------------------------------------------------------------
        for i in range( self.address_frame, self.impact_frame + 1 ):
            
            # ---------------------------------------------------------
            # Extract the frame and the relevant landmarks
            # ---------------------------------------------------------
            frame     = self.pose_data[ i ]
            landmarks = frame[ "landmarks" ]
            
            # ---------------------------------------------------------
            # Collect the head position along the specified axis.
            # ---------------------------------------------------------
            if landmarks[ "NOSE" ][ "valid" ]:
                positions.append( landmarks[ "NOSE" ][ "x" ] if axis == 0 else landmarks[ "NOSE" ][ "y" ] )
        
        # -------------------------------------------------------------
        # If no valid positions were found, return 0.0.
        # -------------------------------------------------------------
        if not positions:
            return 0.0
        
        # -------------------------------------------------------------
        # Return the delta between the first and last recorded head
        # positions.
        # -------------------------------------------------------------
        return float( positions[ -1 ] - positions[ 0 ] )


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
