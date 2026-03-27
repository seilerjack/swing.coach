
# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import tempfile
from   pathlib   import Path
from   typing    import Any, Dict, List, Tuple, TypedDict

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
# Reference to on disk runtime storage for analysis artifacts.
# ---------------------------------------------------------------------
BASE_STORAGE_DIR = Path( tempfile.gettempdir() ) / "swingcoach_storage"
BASE_STORAGE_DIR.mkdir( exist_ok=True )

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
def get_image_point(
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
    # Return pixel coordinates in image space.
    # -----------------------------------------------------
    return (
        int( lm[ "x" ] * width ),
        int( lm[ "y" ] * height )
    )

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
