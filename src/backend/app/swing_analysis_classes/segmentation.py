

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import numpy        as np
import numpy.typing as npt

from   typing       import Any, Dict, List, Tuple
from   scipy.signal import savgol_filter


# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: Segmentation
#
#   DESCRIPTION:
#       Handles the segmentation of a golf swing into its key phases:
#           - Address
#           - Top of the backswing
#           - Impact
#
#       This class operates on pose landmark data extracted from both
#       face-on and down-the-line camera angles. Segmentation is
#       deterministic, pose-only, and designed to be stable across runs.
#
#       The segmentation pipeline:
#           1. Extract wrist-based signal (with fallback logic)
#           2. Normalize time via downsampling
#           3. Smooth signal
#           4. Detect phases using derivative sign changes
#           5. Map detected indices back to original frame indices
#
# ---------------------------------------------------------------------
class Segmentation:
    
    def __init__(
        self,
        face_on_data: List[ Dict[ str, Any ] ],
        down_the_line_data: List[ Dict[ str, Any ] ]
    ) -> None:

        # -------------------------------------------------------------
        # Store pose data for each camera angle.
        # -------------------------------------------------------------        
        self.pose_data = {
            "face_on": face_on_data,
            "down_the_line": down_the_line_data,
        }

        # -------------------------------------------------------------
        # Segment each view independently and store results.
        # -------------------------------------------------------------
        self.segments: Dict[ str, Dict[ str, int ] ] = {}

        for view, data in self.pose_data.items():
            self.segments[ view ] = self._segment_view( data )


    # -----------------------------------------------------------------
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _segment_view
    #
    #   DESCRIPTION:
    #       Runs the full segmentation pipeline for a single camera
    #       view and returns detected swing phase frame indices.
    #
    # -----------------------------------------------------------------
    def _segment_view(
        self,
        pose_data: List[ Dict[ str, Any ] ],
        target_length: int = 100
    ) -> Dict[ str, int ]:

        # -------------------------------------------------------------
        # Step 1: Extract wrist signal from pose data.
        # -------------------------------------------------------------
        frames, signal = self._extract_wrist_signal( pose_data )

        # -------------------------------------------------------------
        # Guard: insufficient data
        # -------------------------------------------------------------
        if len( signal ) < 10:
            return {
                "address": int( frames[ 0 ] ) if len( frames ) else 0,
                "top_of_backswing": int( frames[ 0 ] ) if len( frames ) else 0,
                "impact": int( frames[ 0 ] ) if len( frames ) else 0,
            }

        # -------------------------------------------------------------
        # Step 2: Normalize time via downsampling.
        # -------------------------------------------------------------
        signal_ds, ds_indices = self._downsample_signal(
            signal,
            target_length
        )

        # -------------------------------------------------------------
        # Step 3: Apply light smoothing.
        # -------------------------------------------------------------
        signal_smooth = self._smooth_signal( signal_ds )

        # -------------------------------------------------------------
        # Step 4: Detect phases on compressed signal.
        # -------------------------------------------------------------
        address_r, top_r, impact_r = self._detect_phases( signal_smooth )

        # -------------------------------------------------------------
        # Step 5: Map detected indices back to original frames.
        # -------------------------------------------------------------
        address_idx = ds_indices[ address_r ]
        top_idx     = ds_indices[ top_r ]
        impact_idx  = ds_indices[ impact_r ]

        return {
            "address": int( frames[ address_idx ] ),
            "top_of_backswing": int( frames[ top_idx ] ),
            "impact": int( frames[ impact_idx ] ),
        }


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _extract_wrist_signal
    #
    #   DESCRIPTION:
    #       Extracts a wrist-based signal from pose data using a
    #       priority schema:
    #
    #           - If both wrists are available → use midpoint
    #           - If one wrist is available  → use that wrist
    #           - If no wrists are available → skip frame
    #
    #       Returns:
    #           frame_indices : array of frame indices
    #           y_signal      : corresponding wrist Y-values
    #
    # -----------------------------------------------------------------
    def _extract_wrist_signal(
        self,
        pose_data: List[ Dict[ str, Any ] ]
    ) -> Tuple[ npt.NDArray, npt.NDArray ]:

        y_signal      = []
        frame_indices = []

        for frame in pose_data:

            lm = frame[ "landmarks" ]
            wrists = []

            # ---------------------------------------------------------
            # Attempt to extract LEFT_WRIST
            # ---------------------------------------------------------
            if "LEFT_WRIST" in lm:
                try:
                    wrists.append( lm[ "LEFT_WRIST" ][ "image" ][ "y" ] )
                except KeyError:
                    pass

            # ---------------------------------------------------------
            # Attempt to extract RIGHT_WRIST
            # ---------------------------------------------------------
            if "RIGHT_WRIST" in lm:
                try:
                    wrists.append( lm[ "RIGHT_WRIST" ][ "image" ][ "y" ] )
                except KeyError:
                    pass

            # ---------------------------------------------------------
            # Skip frame if no wrist data is available
            # ---------------------------------------------------------
            if len( wrists ) == 0:
                continue

            # ---------------------------------------------------------
            # Use mean of available wrists (1 or 2)
            # ---------------------------------------------------------
            y_signal.append( np.mean( wrists ) )
            frame_indices.append( frame[ "frame_index" ] )

        return np.array( frame_indices ), np.array( y_signal )


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _downsample_signal
    #
    #   DESCRIPTION:
    #       Compresses the signal to a fixed length using index-based
    #       sampling. This provides time normalization across swings
    #       with different frame counts.
    #
    # -----------------------------------------------------------------
    def _downsample_signal(
        self,
        signal: npt.NDArray,
        target_length: int
    ) -> Tuple[ npt.NDArray, npt.NDArray ]:

        idx = np.linspace( 0, len( signal ) - 1, target_length ).astype( int )
        return signal[ idx ], idx


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _smooth_signal
    #
    #   DESCRIPTION:
    #       Applies light Savitzky-Golay smoothing to stabilize the
    #       signal while preserving overall shape.
    #
    # -----------------------------------------------------------------
    def _smooth_signal(
        self,
        signal: npt.NDArray,
        window: int = 7,
        poly: int = 2
    ) -> npt.NDArray:

        if window % 2 == 0:
            window += 1

        window = min( window, len( signal ) - 1 )

        return savgol_filter( signal, window_length=window, polyorder=poly )


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _detect_phases
    #
    #   DESCRIPTION:
    #       Detects key swing phases using derivative sign changes:
    #
    #           - Address: last local maximum before initial descent
    #           - Top:     first local minimum after address
    #           - Impact:  first local maximum after top
    #
    #       Operates on the downsampled and smoothed signal.
    #
    # -----------------------------------------------------------------
    def _detect_phases(
        self,
        signal: npt.NDArray
    ) -> Tuple[ int, int, int ]:

        dy = np.gradient( signal )

        # -------------------------------------------------------------
        # Smooth derivative to reduce noise in sign changes
        # -------------------------------------------------------------
        dy = savgol_filter( dy, 7, 2 )

        # ---------------- ADDRESS ----------------
        address_idx = None
        for i in range( 1, len( dy ) ):
            if dy[ i ] < 0 and dy[ i - 1 ] >= 0:
                address_idx = i - 1
                break

        if address_idx is None:
            address_idx = np.argmax( signal[ :len( signal ) // 3 ] ) 

        # ---------------- TOP ----------------
        top_idx = None
        for i in range( address_idx + 1, len( dy ) - 1 ):
            if dy[ i - 1 ] < 0 and dy[ i ] >= 0:
                top_idx = i
                break

        if top_idx is None:
            top_idx = address_idx + np.argmin( signal[ address_idx: ] )

        # ---------------- IMPACT ----------------
        impact_idx = None
        for i in range( top_idx + 1, len( dy ) ):
            if dy[ i - 1 ] > 0 and dy[ i ] <= 0:
                impact_idx = i
                break

        if impact_idx is None:
            impact_idx = top_idx + np.argmax( signal[ top_idx: ] )

        return ( int( address_idx ), int( top_idx ), int( impact_idx ) )
