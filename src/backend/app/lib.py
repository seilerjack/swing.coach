
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
