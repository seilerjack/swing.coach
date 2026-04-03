
# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import tempfile
import numpy        as     np
import numpy.typing as     npt
from   pathlib      import Path
from   typing       import Any, Dict, List, Tuple, TypedDict

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
# Reference to on disk runtime storage for analysis artifacts.
# ---------------------------------------------------------------------
BASE_STORAGE_DIR = Path( tempfile.gettempdir() ) / "swingcoach_storage"
BASE_STORAGE_DIR.mkdir( exist_ok=True )


# ---------------------------------------------------------------------
# Define reference axes for the mediapipe world coordinate system.
# ---------------------------------------------------------------------
VERTICAL_AXIS   = np.array( [ 0.0, 1.0, 0.0 ] )   # Up / down
HORIZONTAL_AXIS = np.array( [ 1.0, 0.0, 0.0 ] )   # Left / right
DEPTH_AXIS      = np.array( [ 0.0, 0.0, 1.0 ] )   # Toward / away camera

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------


# ---------------------------------------------------------
# 
#   PROCEDURE NAME: get_image_point
#
#   DESCRIPTION:
#       Grabs the coordinates of a given landmark in pixel
#       space for a given frame.
#
# ---------------------------------------------------------
def get_pixel_point(
        frame: Dict[ str, Any ],
        name: str,
        width: int,
        height: int
    ) -> Tuple[ int, int ] | None:

    # -----------------------------------------------------
    # Access landmark dictionary and convert to NumPy
    # array.
    # -----------------------------------------------------
    lm = frame[ "landmarks" ][ name ][ "image" ]

    # -----------------------------------------------------
    # If the landmark is marked as invalid, return None.
    # -----------------------------------------------------
    if frame[ "landmarks" ][ name ][ "valid" ] is False:
        return None

    # -----------------------------------------------------
    # Return pixel coordinates.
    # -----------------------------------------------------
    return (
        int( lm[ "x" ] * width ),
        int( lm[ "y" ] * height )
    )


# ---------------------------------------------------------
# 
#   PROCEDURE NAME: get_image_point
#
#   DESCRIPTION:
#       Grabs the coordinates of a given landmark in image
#       space for a given frame.
#
# ---------------------------------------------------------
def get_image_point(
        frame: Dict[ str, Any ],
        name: str
    ) -> npt.NDArray[ np.float64 ] | None:

    # -----------------------------------------------------
    # Access landmark dictionary and convert to NumPy
    # array.
    # -----------------------------------------------------
    lm = frame[ "landmarks" ][ name ][ "image" ]

    # -----------------------------------------------------
    # If the landmark is marked as invalid, return None.
    # -----------------------------------------------------
    if frame[ "landmarks" ][ name ][ "valid" ] is False:
        return None
    
    # -----------------------------------------------------
    # Return landmark coordinates in image space.
    # -----------------------------------------------------
    return np.array( [ lm[ "x" ], lm[ "y" ], lm[ "z" ] ], dtype = np.float64 )


# ---------------------------------------------------------
# 
#   PROCEDURE NAME: get_world_point
#
#   DESCRIPTION:
#       Grabs the coordinates of a given landmark in world
#       space for a given frame.
#
# ---------------------------------------------------------
def get_world_point(
        frame: Dict[ str, Any ],
        name: str
    ) -> npt.NDArray[ np.float64 ] | None:

    # -----------------------------------------------------
    # Access landmark dictionary and convert to NumPy
    # array.
    # -----------------------------------------------------
    lm = frame[ "landmarks" ][ name ][ "world" ]

    # -----------------------------------------------------
    # If the landmark is marked as invalid, return None.
    # -----------------------------------------------------
    if frame[ "landmarks" ][ name ][ "valid" ] is False:
        return None
    
    # -----------------------------------------------------
    # Return landmark coordinates in world space.
    # -----------------------------------------------------
    return np.array( [ lm[ "x" ], lm[ "y" ], lm[ "z" ] ], dtype = np.float64 )


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: angle_to_horizontal
#
#   DESCRIPTION:
#       Returns the smallest angle (degrees) between a line defined
#       by two points and the horizontal axis.
#
# -----------------------------------------------------------------
def angle_to_horizontal( p1, p2 ) -> float:

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
#   PROCEDURE NAME: angle_to_vertical
#
#   DESCRIPTION:
#       Returns the smallest angle (degrees) between a vector and
#       the vertical axis.
#
# -----------------------------------------------------------------
def angle_to_vertical( vec ) -> float:

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
#   PROCEDURE NAME: get_spine_vector
#
#   DESCRIPTION:
#       Computes the spine vector using best available landmarks.
#       Returns a 2D vector in pixel space.
#
# -----------------------------------------------------------------
def get_spine_vector(
        frame: Dict[ str, Any ],
        width: int,
        height: int
    ) -> np.ndarray | None:

    # -------------------------------------------------------------
    # Retrieve shoulder and hip landmarks.
    # -------------------------------------------------------------
    l_s = get_pixel_point( frame, "LEFT_SHOULDER", width, height )
    r_s = get_pixel_point( frame, "RIGHT_SHOULDER", width, height )
    l_h = get_pixel_point( frame, "LEFT_HIP", width, height )
    r_h = get_pixel_point( frame, "RIGHT_HIP", width, height )

    # -------------------------------------------------------------
    # Best case: midpoints
    # -------------------------------------------------------------
    if l_s and r_s and l_h and r_h:
        mid_sh = midpoint( l_s, r_s )
        mid_hp = midpoint( l_h, r_h )

        return np.array( [
            mid_sh[ 0 ] - mid_hp[ 0 ],
            mid_sh[ 1 ] - mid_hp[ 1 ]
        ] )

    # -------------------------------------------------------------
    # Prefer right side (DTL usually shows trail side better)
    # -------------------------------------------------------------
    elif r_s and r_h:
        return np.array( [
            r_s[ 0 ] - r_h[ 0 ],
            r_s[ 1 ] - r_h[ 1 ]
        ] )

    # -------------------------------------------------------------
    # Fall back to left side
    # -------------------------------------------------------------
    elif l_s and l_h:
        return np.array( [
            l_s[ 0 ] - l_h[ 0 ],
            l_s[ 1 ] - l_h[ 1 ]
        ] )

    return None


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: midpoint
#
#   DESCRIPTION:
#       Returns midpoint between two points.
#
# -----------------------------------------------------------------
def midpoint( p1, p2 ):

    return (
        ( p1[ 0 ] + p2[ 0 ] ) / 2,
        ( p1[ 1 ] + p2[ 1 ] ) / 2
    )


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: hip_width
#
#   DESCRIPTION:
#       Returns the static hip width at a given frame.
#
#   NOTE: This is used as a reference measurement for reintroducing
#         hip rotation angle estimation using only world
#         coordinates.
#
# -----------------------------------------------------------------
def hip_width( frame: Dict[ str, Any ] ) -> float | None:

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


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: shoulder_width
#
#   DESCRIPTION:
#       Returns the static shoulder width at a given frame.
#
#   NOTE: This is used as a reference measurement for reintroducing
#         shoulder rotation angle estimation using only world
#         coordinates.
#
# -----------------------------------------------------------------
def shoulder_width( frame: Dict[ str, Any ] ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve shoulder landmarks.
    # -------------------------------------------------------------
    l_s = get_world_point( frame, "LEFT_SHOULDER" )
    r_s = get_world_point( frame, "RIGHT_SHOULDER" )

    # -------------------------------------------------------------
    # If the shoulder landmarks are present and valid, continue.
    # -------------------------------------------------------------
    if ( l_s is None or r_s is None ) \
    or ( not l_s.all() or not r_s.all() ):
        return None

    # -------------------------------------------------------------
    # Return the distance between the left and right shoulder x
    # coordinates.
    # -------------------------------------------------------------
    return abs( r_s[ 0 ] - l_s[ 0 ] )


# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: FullData
#
#   DESCRIPTION:
#       The overall data structure for holding video metadata and
#       frame by frame pose estimation data.
#
# ---------------------------------------------------------------------
class FullData( TypedDict ):
    metadata: Dict[ str, Any ]
    frames: List[ Dict[ str, Any ] ]


# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    pass
