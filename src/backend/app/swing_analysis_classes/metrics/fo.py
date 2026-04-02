
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


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: _hip_width
#
#   DESCRIPTION:
#       Returns the static hip width at a given frame.
#
#   NOTE: This is used as a reference measurement for reintroducing
#         hip rotation angle estimation using only world
#         coordinates.
#
# -----------------------------------------------------------------
def _hip_width( frame: Dict[ str, Any ] ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve hip landmarks.
    # -------------------------------------------------------------
    l_h = get_world_point( frame, "LEFT_HIP" )
    r_h = get_world_point( frame, "RIGHT_HIP" )

    # -------------------------------------------------------------
    # If the hip landmarks are present and valid, continue.
    # -------------------------------------------------------------
    if ( l_h is None or r_h is None ) \
    or ( not l_h.all() or not r_h.all() ):
        return None

    # -------------------------------------------------------------
    # Return the distance between the left and right hip x
    # coordinates.
    # -------------------------------------------------------------
    return abs( r_h[ 0 ] - l_h[ 0 ] )


# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------
#
#   PROCEDURE NAME: fo_shoulder_tilt
#
#   DESCRIPTION:
#       Calculates shoulder tilt at a given frame using the
#       angle between left and right shoulder landmarks relative to
#       the horizontal axis.
#
# -----------------------------------------------------------------
def fo_shoulder_tilt(
        frame: Dict[ str, Any ],
        width: int,
        height: int
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve shoulder landmarks.
    # -------------------------------------------------------------
    l_sh = get_pixel_point( frame, "LEFT_SHOULDER", width, height )
    r_sh = get_pixel_point( frame, "RIGHT_SHOULDER", width, height )

    # -------------------------------------------------------------
    # If the shoulder landmarks are present and valid, continue.
    # -------------------------------------------------------------
    if l_sh is None or r_sh is None:
        return None

    return _angle_to_horizontal( l_sh, r_sh )
    

# -----------------------------------------------------------------
#
#   PROCEDURE NAME: fo_hip_tilt
#
#   DESCRIPTION:
#       Calculates hip tilt at a given frame using the
#       angle between left and right hip landmarks relative to
#       the horizontal axis.
#
# -----------------------------------------------------------------
def fo_hip_tilt(
        frame: Dict[ str, Any ],
        width: int,
        height: int
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve hip landmarks.
    # -------------------------------------------------------------
    l_h = get_pixel_point( frame, "LEFT_HIP", width, height )
    r_h = get_pixel_point( frame, "RIGHT_HIP", width, height )

    # -------------------------------------------------------------
    # If the hip landmarks are present and valid, continue.
    # -------------------------------------------------------------
    if l_h is None or r_h is None:
        return None

    return _angle_to_horizontal( l_h, r_h )


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: fo_stance_width
#
#   DESCRIPTION:
#       Calculates the stance width as a ratio of horizontal
#       seperation between feet and shoulders.
#
# -----------------------------------------------------------------
def fo_stance_width(
        frame: Dict[ str, Any ],
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve ankle and shoulder landmarks.
    # -------------------------------------------------------------
    l_a = get_image_point( frame, "LEFT_ANKLE" )
    r_a = get_image_point( frame, "RIGHT_ANKLE" )
    l_s = get_image_point( frame, "LEFT_SHOULDER" )
    r_s = get_image_point( frame, "RIGHT_SHOULDER" )

    # -------------------------------------------------------------
    # If the ankle and shoulder landmarks are present and valid,
    # continue.
    # -------------------------------------------------------------
    if l_s is None or r_s is None or l_a is None or r_a is None:
        return None

    # -------------------------------------------------------------
    # Calculate the horizontal seperation of the two ankle x
    # coordinates.
    # -------------------------------------------------------------
    dxa = abs( r_a[ 0 ] - l_a[ 0 ] )
    dxs = abs( r_s[ 0 ] - l_s[ 0 ] )

    # -------------------------------------------------------------
    # Protect against divide by 0.
    # -------------------------------------------------------------
    if dxs == 0:
        return None

    # -------------------------------------------------------------
    # Divide the width of the ankles to the width of the shoulders
    # to normalize the stance width to the body size.
    # -------------------------------------------------------------
    stance_width_normalized = dxa / dxs

    return stance_width_normalized


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: fo_spine_tilt
#
#   DESCRIPTION:
#       Calculates the lateral spine tilt at a given frame using
#       the angle the between left and right hip and shoulder
#       landmarks relative to the vertical axis.
#
# -----------------------------------------------------------------
def fo_spine_tilt(
        frame: Dict[ str, Any ],
        width: int,
        height: int
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve shoulder and hip landmarks.
    # -------------------------------------------------------------
    l_s = get_pixel_point( frame, "LEFT_SHOULDER", width, height )
    r_s = get_pixel_point( frame, "RIGHT_SHOULDER", width, height )
    l_h = get_pixel_point( frame, "LEFT_HIP", width, height )
    r_h = get_pixel_point( frame, "RIGHT_HIP", width, height )

    # -------------------------------------------------------------
    # If the ankle and shoulder landmarks are present and valid,
    # continue.
    # -------------------------------------------------------------
    if l_s is None or r_s is None or l_h is None or r_h is None:
        return None
    
    # -------------------------------------------------------------
    # Calculate the midpoints for both the shoulders and the hips.
    # -------------------------------------------------------------
    mid_sh = _midpoint( l_s, r_s )
    mid_hp = _midpoint( l_h, r_h )

    # -------------------------------------------------------------
    # Calculate the spine vector.
    # -------------------------------------------------------------
    dx = mid_sh[ 0 ] - mid_hp[ 0 ]
    dy = mid_sh[ 1 ] - mid_hp[ 1 ]

    spine_vec = np.array( [ dx, dy ] )

    return _angle_to_vertical( spine_vec )


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: _fo_hip_rotation_angle_world
#
#   DESCRIPTION:
#       Computes hip rotation angle (face-on) using world coords.
#       Measures angle of hip line projected onto X-Z plane.
#
#   NOTE: This uses the hip width to reintroduce hip rotation using
#         only world coordinates.
#
# -----------------------------------------------------------------
def fo_hip_rotation_range(
        frames: list[ Dict[ str, Any ] ],
        address_idx: int,
        top_idx: int
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve the hip width at both address and top.
    # -------------------------------------------------------------
    w0 = _hip_width( frames[ address_idx ] )
    w1 = _hip_width( frames[ top_idx ] )

    # -------------------------------------------------------------
    # Ensure hip widths are valid and non zero to protect divide by
    # zero before continuing.
    # -------------------------------------------------------------
    if not w0 or not w1 or w0 < 1e-6:
        return None

    # -------------------------------------------------------------
    # Clamp for safety in case of numerical issues with very small
    # hip widths.
    # -------------------------------------------------------------
    ratio = np.clip( w1 / w0, -1.0, 1.0 )

    # -------------------------------------------------------------
    # Turn the ratio of hip widths into an angle using arccos. The
    # ratio of hip widths corresponds to the cosine of the hip
    # rotation angle, since as the hips rotate away from the
    # camera, the apparent width decreases. We take the arccosine 
    # to get the angle in radians, then convert to degrees.
    # -------------------------------------------------------------
    angle = np.degrees( np.arccos( ratio ) )

    return angle



# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
