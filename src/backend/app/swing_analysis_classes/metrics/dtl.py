
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

# -----------------------------------------------------------------
#
#   PROCEDURE NAME: _angle_to_horizontal
#
#   DESCRIPTION:
#       Returns the smallest angle (degrees) between a line defined
#       by two points and the horizontal axis.
#
# -----------------------------------------------------------------
def _angle_to_horizontal( p1, p2 ) -> float:

    # -------------------------------------------------------------
    # Extract the x and y components of the slope.
    # -------------------------------------------------------------
    dx = p2[ 0 ] - p1[ 0 ]
    dy = p2[ 1 ] - p1[ 1 ]

    # -------------------------------------------------------------
    # Convert to degrees after taking the arctangent of the
    # slope. We take the absolute value since we don't care
    # about the direction, only the magnitude.
    # -------------------------------------------------------------
    angle = abs( np.degrees( np.arctan2( dy, dx ) ) )

    # -------------------------------------------------------------
    # Convert to the smallest equivalent angle relative to
    # vertical. This ensures the result is always in [0, 90]
    # degrees, since we only care about magnitude of tilt, not
    # direction.
    # -------------------------------------------------------------
    if angle > 90:
        angle = 180 - angle

    return angle


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: _angle_to_vertical
#
#   DESCRIPTION:
#       Returns the smallest angle (degrees) between a vector and
#       the vertical axis.
#
# -----------------------------------------------------------------
def _angle_to_vertical( vec ) -> float:

    # -------------------------------------------------------------
    # Normalize the input vector to unit length. This ensures that
    # the magnitude of the vector does not affect the angle
    # calculation, only its direction.
    # -------------------------------------------------------------
    vec = vec / np.linalg.norm( vec )

    # -------------------------------------------------------------
    # Define the vertical axis in image space.
    # NOTE: In OpenCV/image coordinates, the origin is top-left and
    # the Y-axis increases downward. Therefore, "up" is (0, -1).
    # -------------------------------------------------------------
    vertical = np.array( [ 0.0, -1.0 ] )

    # -------------------------------------------------------------
    # Compute the dot product between the normalized vector and the
    # vertical axis. This gives the cosine of the angle between
    # them. Clamp the result to [-1, 1] to avoid numerical issues
    # with arccos due to floating point precision.
    # -------------------------------------------------------------
    dot = np.clip( np.dot( vec, vertical ), -1.0, 1.0 )

    # -------------------------------------------------------------
    # Convert the arccosine of the dot product into degrees.
    # This gives the angle between the vector and vertical axis.
    # -------------------------------------------------------------
    angle = np.degrees( np.arccos( dot ) )

    # -------------------------------------------------------------
    # Convert to the smallest equivalent angle relative to
    # vertical. This ensures the result is always in [0, 90]
    # degrees, since we only care about magnitude of tilt, not
    # direction.
    # -------------------------------------------------------------
    if angle > 90:
        angle = 180 - angle

    return angle


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: _midpoint
#
#   DESCRIPTION:
#       Returns midpoint between two points.
#
# -----------------------------------------------------------------
def _midpoint( p1, p2 ):

    return (
        ( p1[ 0 ] + p2[ 0 ] ) / 2,
        ( p1[ 1 ] + p2[ 1 ] ) / 2
    )

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
    # Retrieve landmarks
    # -------------------------------------------------------------
    l_s = get_pixel_point( frame, "LEFT_SHOULDER", width, height )
    r_s = get_pixel_point( frame, "RIGHT_SHOULDER", width, height )
    l_h = get_pixel_point( frame, "LEFT_HIP", width, height )
    r_h = get_pixel_point( frame, "RIGHT_HIP", width, height )

    # -------------------------------------------------------------
    # Determine best available spine representation
    # -------------------------------------------------------------
    spine_vec = None

    # -------------------------------------------------------------
    # Case 1: Both sides available → use midpoints (best)
    # -------------------------------------------------------------
    if l_s and r_s and l_h and r_h:

        mid_sh = _midpoint( l_s, r_s )
        mid_hp = _midpoint( l_h, r_h )

        dx = mid_sh[ 0 ] - mid_hp[ 0 ]
        dy = mid_sh[ 1 ] - mid_hp[ 1 ]

        spine_vec = np.array( [ dx, dy ] )

    # -------------------------------------------------------------
    # Case 2: Right side only (Righties) 
    # NOTE: More common so we prioritize this over left side only.
    # -------------------------------------------------------------
    elif r_s and r_h:

        dx = r_s[ 0 ] - r_h[ 0 ]
        dy = r_s[ 1 ] - r_h[ 1 ]

        spine_vec = np.array( [ dx, dy ] )

    # -------------------------------------------------------------
    # Case 3: Left side only (Lefties)
    # -------------------------------------------------------------
    elif l_s and l_h:

        dx = l_s[ 0 ] - l_h[ 0 ]
        dy = l_s[ 1 ] - l_h[ 1 ]

        spine_vec = np.array( [ dx, dy ] )

    # -------------------------------------------------------------
    # No usable data
    # -------------------------------------------------------------
    else:
        return None

    # -------------------------------------------------------------
    # Compute angle relative to vertical
    # -------------------------------------------------------------
    return _angle_to_vertical( spine_vec )


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
    return _angle_to_vertical( arm_vec )


# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
