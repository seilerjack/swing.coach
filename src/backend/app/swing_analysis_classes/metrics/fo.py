
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
        angle = abs( np.degrees( np.arctan2( dy, dx ) ) )

        # ----------------------------------------------------------
        # Convert to smallest equivalent angle relative to horizontal
        # ----------------------------------------------------------
        if angle > 90:
            angle = 180 - angle

        return angle
    

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
    else:
        # ---------------------------------------------------------
        # Calculate the angle of the line connecting the hips
        # relative to the horiztonal axis.
        # ---------------------------------------------------------
        dx = r_h[ 0 ] - l_h[ 0 ]
        dy = r_h[ 1 ] - l_h[ 1 ]

        # ----------------------------------------------------------
        # Convert to degrees after taking the arctangent of the
        # slope. We take the absolute value since we don't care
        # about the direction, only the magnitude of the tilt.
        # ----------------------------------------------------------
        angle = abs( np.degrees( np.arctan2( dy, dx ) ) )

        # ----------------------------------------------------------
        # Convert to smallest equivalent angle relative to horizontal
        # ----------------------------------------------------------
        if angle > 90:
            angle = 180 - angle

        return angle


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
    # Retrieve ankle and hip landmarks.
    # -------------------------------------------------------------
    l_a = get_image_point( frame, "LEFT_ANKLE" )
    r_a = get_image_point( frame, "RIGHT_ANKLE" )
    l_s = get_image_point( frame, "LEFT_SHOULDER" )
    r_s = get_image_point( frame, "RIGHT_SHOULDER" )

    # -------------------------------------------------------------
    # If the ankle and shoulder landmarks are present and valid,
    # continue.
    # -------------------------------------------------------------
    if l_a is None or r_a is None or l_s is None or r_s is None:
        return None
    else:
        # ---------------------------------------------------------
        # Calculate the the horizontal seperation of the two ankle
        # x coordinates.
        # ---------------------------------------------------------
        dxa = abs( r_a[ 0 ] - l_a[ 0 ] )
        dxs = abs( r_s[ 0 ] - l_s[ 0 ] )

        # ---------------------------------------------------------
        # Divide the width of the ankles to the width of the
        # shoulders to normalize the stance width to the body size.
        # ---------------------------------------------------------
        stance_width_normalized = dxa / dxs

        return stance_width_normalized




# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
