
"""
NOTE: The longterm solution for the swing segmentation problem will likely
be a trained model that can classify each frame into swing phases.
"""
# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import numpy        as np
import numpy.typing as npt

from   typing       import Any, Dict, List, Optional

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
#       Handles the segmentation of a golf swing into its key phases:
#           - Address
#           - Top of the backswing
#           - Start of the downswing
#           - Impact
#
#       This class operates on pose landmark data extracted from both
#       face-on and down-the-line camera angles. Segmentation is
#       deterministic, pose-only, and designed to be stable across runs.
#
# ---------------------------------------------------------------------
class Segmentation:
    
    def __init__(
        self,
        face_on_pose_data: List[ Dict[ str, Any ] ],
        down_the_line_pose_data: List[ Dict[ str, Any ] ],
    ) -> None:

        # -------------------------------------------------------------
        # Store pose data for each camera angle.
        # -------------------------------------------------------------        
        self.pose_data = {
            "face_on": face_on_pose_data,
            "down_the_line": down_the_line_pose_data,
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
    def _segment_view( self, pose_data: List[ Dict[ str, Any ] ] ) -> Dict[ str, int ]:

        address = self._detect_address( pose_data )
        top     = self._detect_top_of_backswing( pose_data )
        impact  = self._detect_impact( pose_data )

        return {
            "address": address,
            "top_of_backswing": top,
            "impact": impact,
        }


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _detect_address
    #
    #   DESCRIPTION:
    #       Detects address as first stable posture window using
    #       hips and shoulders.
    #
    # -----------------------------------------------------------------
    def _detect_address(
        self,
        pose_data: List[ Dict[ str, Any ] ],
    ) -> int:
        
        return 0


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _detect_top_of_backswing
    #
    #   DESCRIPTION:
    #       Finds frame where hands are farthest from address.
    #
    # -----------------------------------------------------------------
    def _detect_top_of_backswing(     
        self,
        pose_data: List[ Dict[ str, Any ] ],
    ) -> int:

        return 0


    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _detect_impact
    #
    #   DESCRIPTION:
    #       Detects impact frame based on minimum distance of hands
    #       to address position after downswing starts
    #
    # -----------------------------------------------------------------
    def _detect_impact( 
        self,
        pose_data: List[ Dict[ str, Any ] ],
    ) -> int:

        return 0


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
