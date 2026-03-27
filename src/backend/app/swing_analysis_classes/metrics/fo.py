
# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import numpy  as np

from   lib    import *
from   typing import Any, Dict

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------
#
#   PROCEDURE NAME: _shoulder_tilt
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
    l_sh = get_image_point( frame, "LEFT_SHOULDER", width, height )
    r_sh = get_image_point( frame, "RIGHT_SHOULDER", width, height )

    # -------------------------------------------------------------
    # If the should landmarks are present and valid, continue.
    # -------------------------------------------------------------
    if l_sh is None or r_sh is None:
        return None
    else:
        # ---------------------------------------------------------
        # Calculate the angle of the line connecting the shoulders
        # relative to the horiztonal axis.
        # ---------------------------------------------------------
        dx = r_sh[ 0 ] - l_sh[ 0 ]
        dy = r_sh[ 1 ] - l_sh[ 1 ]

        # ----------------------------------------------------------
        # Convert to degrees after taking the arctangent of the
        # slope. We take the absolute value since we don't care
        # about the direction, only the magnitude of the tilt.
        # ----------------------------------------------------------
        angle = np.degrees( np.arctan2( dy, dx ) )

        return abs( angle )




# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
