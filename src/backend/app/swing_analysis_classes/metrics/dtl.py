
# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import os
import sys
import numpy  as np

# ---------------------------------------------------------------------
# Add the parent and grandparent directories to the system path to
# allow for relative imports.
# ---------------------------------------------------------------------
PARENT_DIR       = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
GRAND_PARENT_DIR = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
sys.path.append( PARENT_DIR )
sys.path.append( GRAND_PARENT_DIR )

from   lib    import *
from   typing import Any, Dict

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 HELPERS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------
#
#   PROCEDURE NAME: dtl_forward_bend
#
#   DESCRIPTION:
#       Calculates forward bend (posture) from a down-the-line
#       view. Measures the angle between the spine vector and the
#       vertical axis.
#
#       Uses midpoints if both sides are available. Falls back to a
#       single side if occlusion is present.
#
# -----------------------------------------------------------------
def dtl_forward_bend(
        frame: Dict[ str, Any ],
        width: int,
        height: int
    ) -> float | None:

    # -------------------------------------------------------------
    # Determine best available spine representation.
    # -------------------------------------------------------------
    spine_vec = get_spine_vector( frame, width, height )
    
    # -------------------------------------------------------------
    # Catch bad spine vector due to missing landmarks or bad
    # geometry.
    # -------------------------------------------------------------
    if spine_vec is None:
        return None

    # -------------------------------------------------------------
    # Compute angle relative to vertical.
    # -------------------------------------------------------------
    return angle_to_vertical( spine_vec )


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: dtl_arm_hang_angle
#
#   DESCRIPTION:
#       Calculates the arm hang angle from a down-the-line view.
#       This is the angle between the arm vector (shoulder → wrist)
#       and the vertical axis.
#
#       Uses left side by default, falls back to right side if needed.
#
# -----------------------------------------------------------------
def dtl_arm_hang_angle(
        frame: Dict[ str, Any ],
        width: int,
        height: int
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve landmarks
    # -------------------------------------------------------------
    l_s = get_pixel_point( frame, "LEFT_SHOULDER", width, height )
    l_e = get_pixel_point( frame, "LEFT_ELBOW", width, height )

    r_s = get_pixel_point( frame, "RIGHT_SHOULDER", width, height )
    r_e = get_pixel_point( frame, "RIGHT_ELBOW", width, height )

    arm_vec = None

    # -------------------------------------------------------------
    # Prefer right side (DTL usually shows trail side better)
    # -------------------------------------------------------------
    if r_s and r_e:

        dx = r_e[ 0 ] - r_s[ 0 ]
        dy = r_e[ 1 ] - r_s[ 1 ]

        arm_vec = np.array( [ dx, dy ] )

    # -------------------------------------------------------------
    # Fall back to left side
    # -------------------------------------------------------------
    elif l_s and l_e:

        dx = l_e[ 0 ] - l_s[ 0 ]
        dy = l_e[ 1 ] - l_s[ 1 ]

        arm_vec = np.array( [ dx, dy ] )

    else:
        return None

    # -------------------------------------------------------------
    # Guard against degenerate vectors
    # -------------------------------------------------------------
    if np.linalg.norm( arm_vec ) < 1e-6:
        return None

    # -------------------------------------------------------------
    # Compute angle relative to vertical
    # -------------------------------------------------------------
    return angle_to_vertical( arm_vec )


# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
