

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import numpy        as np
import numpy.typing as npt

from   typing       import Any, Dict, List

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
#   CLASS NAME: Segmentation
#
#   DESCRIPTION:
#       Handles the segmentation of a golf swing into its key phases
#       address, backswing, and impact using pose estimation data.
#
# ---------------------------------------------------------------------
class Segmentation:
    
    def __init__( self, pose_data: List[ Dict[ str, Any ] ] ) -> None:

        # -------------------------------------------------------------
        # Initialize the pose data with the frame data outputted by
        # pose_estimation.py.
        # -------------------------------------------------------------        
        self.pose_data = pose_data
        
        # -------------------------------------------------------------
        # Initialize the frame indices for key swing segements.
        # Specifically, we are tracking address, top of the backswing,
        # and impact frames.
        # -------------------------------------------------------------
        self.address_frame   = self._detect_address_frame()
        self.backswing_frame = self._detect_backswing_frame()
        self.impact_frame    = self._detect_impact_frame()

    # -----------------------------------------------------------------
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _detect_address_frame
    #
    #   DESCRIPTION:
    #       Detects the frame index corresponding to the address
    #       position. 
    # 
    #       In order to prevent misidentification due to movement
    #       pre-address, we search for a "window of stability" using N
    #       consecutive frames with movement below a certain threshold.
    #       This indicates that the golfer has settled into the address
    #       position, and we can safely assign a frame index.
    #
    # -----------------------------------------------------------------
    def _detect_address_frame( self ) -> int:

        # -------------------------------------------------------------
        # Define local constants related to movement thresholding.
        # -------------------------------------------------------------
        MOVEMENT_THRESHOLD = 0.003
        STABILITY_WINDOW   = 3

        # -------------------------------------------------------------
        # Initialize return index.
        # -------------------------------------------------------------
        address_frame_idx = -1

        # -------------------------------------------------------------
        #
        #   PROCEDURE NAME: __get_pose_vector
        #
        #   DESCRIPTION:
        #       Collect a pose vector from the given landmarks. We care
        #       about the shoulders and hips for this calculation.
        #
        # -------------------------------------------------------------
        def __get_pose_vector( landmark ) -> npt.NDArray:
            # ---------------------------------------------------------
            # Initialize pose vector.
            # ---------------------------------------------------------
            vector_positions = []
            # ---------------------------------------------------------
            # Loop through the key landmarks.
            # ---------------------------------------------------------
            for key in [ "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_HIP", "RIGHT_HIP" ]:
                # -----------------------------------------------------
                # If the landmark is valid, add its x and y to the pose
                # vector. If not, return an empty array.
                # -----------------------------------------------------
                if landmark[ key ][ "valid" ]:
                    vector_positions.extend( [ landmark[ key ][ "x" ], landmark[ key ][ "y" ] ] )
                else: return np.array( [] )
            # ---------------------------------------------------------
            # Return the pose vector as a numpy array.
            # ---------------------------------------------------------
            return np.array( vector_positions )
        
        # -------------------------------------------------------------
        # Initialize pose vector.
        # -------------------------------------------------------------
        pose_vectors = []

        # -------------------------------------------------------------
        # Loop through each frame and collect pose vectors.
        # -------------------------------------------------------------
        for frame in self.pose_data:
            vector = __get_pose_vector( frame[ "landmarks" ] )
            pose_vectors.append( vector )

        # -------------------------------------------------------------
        # Compute movement between consecutive pose vectors.
        # -------------------------------------------------------------
        movements: List[ Any ] = [ None ]  
        
        # -------------------------------------------------------------
        # Loop through the pose vectores, skipping the first frame bc
        # it has no previous frame to compare to.
        # -------------------------------------------------------------
        for i in range( 1, len( pose_vectors ) ):
            
            # ---------------------------------------------------------
            # Calculate movement only if both current and previous pose
            # vectors are valid.
            # ---------------------------------------------------------
            if pose_vectors[ i ] is None or pose_vectors[ i - 1 ] is None:
                movements.append( None )
                continue
            
            delta = np.linalg.norm( pose_vectors[ i ] - pose_vectors[ i - 1 ] )
            movements.append( delta )

        # -------------------------------------------------------------
        # Loop through the movements beteween frames to find a stable
        # window.
        # -------------------------------------------------------------
        stable_frame_count = 0
        for i, movement in enumerate( movements ):
            # ---------------------------------------------------------
            # If there was movement and it is below the threshold,
            # increment.
            # ---------------------------------------------------------
            if movement is not None and movement < MOVEMENT_THRESHOLD:
                stable_frame_count += 1
            else:
                stable_frame_count = 0
            
            # ---------------------------------------------------------
            # If we have a window of consequtive stable frames, mark
            # the index and set the address frame.
            # ---------------------------------------------------------
            if stable_frame_count >= STABILITY_WINDOW:
                address_frame_idx = i - ( STABILITY_WINDOW - 1 )
                break

        # -------------------------------------------------------------
        # Return the index of the address frame.
        # -------------------------------------------------------------
        return address_frame_idx

    
    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _detect_backswing_frame
    #
    #   DESCRIPTION:
    #       Detects the frame index corresponding to the top of the
    #       backswing. By analyzing the y-positions of the wrists
    #       across frames, it identifies the frame where the average
    #       y-position of both wrists is at its maximum, indicating the
    #       highest point of the backswing.
    #
    # -----------------------------------------------------------------
    def _detect_backswing_frame( self ) -> int:

        # -------------------------------------------------------------
        # Initialize return index.
        # -------------------------------------------------------------
        top_of_backswing_frame_idx = -1

        # -------------------------------------------------------------
        # Initialize list to hold y-positions of hands, specifically,
        # the wrists.
        # -------------------------------------------------------------
        hands_y_positions = []

        # -------------------------------------------------------------
        # Loop through each frame in the pose data.
        # -------------------------------------------------------------
        for frame in self.pose_data:
            
            # ---------------------------------------------------------
            # Extract landmarks from the frame.
            # ---------------------------------------------------------
            landmarks = frame[ "landmarks" ]

            # ---------------------------------------------------------
            # Check if position data for both wrists is valid. If so,
            # compute average y position.
            # ---------------------------------------------------------
            if landmarks["LEFT_WRIST"][ "valid" ] and landmarks["RIGHT_WRIST"][ "valid" ]:
                hands_y_positions.append( ( landmarks["LEFT_WRIST"][ "y" ] + landmarks["RIGHT_WRIST"][ "y" ] ) / 2.0 )
            
            # ---------------------------------------------------------
            # If not valid, append negative infinity to indicate
            # invalid data.
            # ---------------------------------------------------------
            else:
                hands_y_positions.append( float( "-inf" ) )

        # -------------------------------------------------------------
        # Identify valid indices where hand y-positions are valid.
        # -------------------------------------------------------------
        valid_idxes = [ idx for idx, y in enumerate( hands_y_positions ) if y is not float( "-inf" ) ]
        
        # -------------------------------------------------------------
        # If there are valid indices, find the index with the maximum
        # y-position ( top of backswing ).
        # -------------------------------------------------------------
        if valid_idxes:
            top_of_backswing_frame_idx = max( valid_idxes, key=lambda idx: hands_y_positions[ idx ] )

        # -------------------------------------------------------------
        # Return the index of the top of backswing frame.
        # -------------------------------------------------------------
        return top_of_backswing_frame_idx

    
    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _detect_impact_frame
    #
    #   DESCRIPTION:
    #       Detects the frame index corresponding to the moment of
    #       impact. At a very basic level, using the pose data, this
    #       can be inferred by the hands position closest to the point
    #       of address (after the downswing has been initiated).
    #
    # -----------------------------------------------------------------
    def _detect_impact_frame( self ) -> int:

        # -------------------------------------------------------------
        # Initialize impact frame index.
        # -------------------------------------------------------------
        impact_frame_idx = -1

        # -------------------------------------------------------------
        #
        #   PROCEDURE NAME: __get_hands_position
        #
        #   DESCRIPTION:
        #       Grab the position of the hands at address. Because our
        #       data is only represented in 2D space (x,y), we can
        #       calculate the position by taking the x,y coordinates of
        #       both wrists and calculating the vector norm. This is
        #       what we will compare against for the rest of the
        #       frames.
        #
        # -------------------------------------------------------------
        def __get_hands_position( landmark ) -> np.floating[ Any ]:
            # ---------------------------------------------------------
            # Initialize list to hold wrist positions.
            # ---------------------------------------------------------
            positions = []
            # ---------------------------------------------------------
            # Loop through both wrists.
            # ---------------------------------------------------------
            for key in [ "LEFT_WRIST", "RIGHT_WRIST" ]:
                # -----------------------------------------------------
                # calculate the landmark's vector norm and add to the
                # positions list.
                # -----------------------------------------------------
                pos = np.linalg.norm( [ landmark[ key ][ "x" ], landmark[ key ][ "y" ] ] )
                positions.append( pos )
            # ---------------------------------------------------------
            # Return the average position of both wrists.
            # ---------------------------------------------------------
            return np.mean( positions )

        # -------------------------------------------------------------
        # Assign a position for the hands at address.
        # -------------------------------------------------------------
        address_landmark  = self.pose_data[ self.address_frame ][ "landmarks" ]
        hands_address_pos = __get_hands_position( address_landmark )

        # -------------------------------------------------------------
        # Loop through all the frames starting from the top of the
        # backswing to the end of the swing.
        # -------------------------------------------------------------
        min_hands_delta = float( "inf" )
        for i in range( self.backswing_frame, len( self.pose_data ) ):
           
            # --------------------------------------------------------
            # Get the hands position at the current frame.
            # --------------------------------------------------------
            landmarks = self.pose_data[ i ][ "landmarks" ]
            hands_impact_pos = __get_hands_position( landmarks )

            # ---------------------------------------------------------
            # Update the minimum distance and impact frame if needed.
            # The minimum distance is that between the wrists at
            # address and the wrists at impact (frame == i)
            # ---------------------------------------------------------
            if abs( hands_impact_pos - hands_address_pos ) < min_hands_delta:
                min_hands_delta = abs( hands_impact_pos - hands_address_pos )
                impact_frame_idx = i

        # -------------------------------------------------------------
        # If no valid frames are found, set impact frame to the address
        # frame. (Best effort)
        # -------------------------------------------------------------
        if impact_frame_idx is None:
            impact_frame_idx = self.address_frame

        return impact_frame_idx


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
