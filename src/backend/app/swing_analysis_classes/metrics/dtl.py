
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


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: dtl_shoulder_rotation_depth
#
#   DESCRIPTION:
#       Computes the magnitude of shoulder rotation from a
#       down-the-line perspective using the ratio of shoulder
#       widths between address and the current frame.
#
#       This method reintroduces depth information similarly to
#       the face-on hip rotation metric by assuming the true
#       shoulder width remains constant.
#
#       Optionally applies a correction for forward spine bend.
#
#   PARAMETERS:
#       addr_frame   : Frame at address position.
#       cur_frame    : Current frame.
#       forward_bend : Spine tilt angle (degrees). Optional.
#
#   RETURNS:
#       float | None : Corrected shoulder rotation angle in degrees.
#
# -----------------------------------------------------------------
def dtl_shoulder_rotation_depth(
        addr_frame: Dict[ str, Any ],
        cur_frame: Dict[ str, Any ],
        forward_bend: float | None = None
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve shoulder widths at address and current frame
    # -------------------------------------------------------------
    w0 = shoulder_width( addr_frame )
    w1 = shoulder_width( cur_frame )

    # -------------------------------------------------------------
    # Validate widths to avoid divide-by-zero errors
    # -------------------------------------------------------------
    if w0 is None or w1 is None or w0 < 1e-6:
        return None

    # -------------------------------------------------------------
    # Compute rotation angle from width ratio
    # -------------------------------------------------------------
    ratio = np.clip( w1 / w0, -1.0, 1.0 )
    angle = np.degrees( np.arccos( ratio ) )

    # -------------------------------------------------------------
    # Apply optional forward bend correction
    # -------------------------------------------------------------
    if forward_bend is not None:
        tilt_rad = np.radians( forward_bend )
        cos_tilt = np.cos( tilt_rad )

        # ---------------------------------------------------------
        # Avoid instability for extreme tilt values
        # ---------------------------------------------------------
        if abs( cos_tilt ) > 1e-3:
            angle = angle / cos_tilt

    return float( angle )


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: dtl_pelvis_depth
#
#   DESCRIPTION:
#       Computes pelvis depth from a down-the-line perspective
#       using the Z-coordinate of the hip midpoint in MediaPipe
#       world coordinates.
#
#       Intended for use in calculating Pelvis Depth Stability
#       (variance over time).
#
#   RETURNS:
#       float | None : Hip midpoint Z value, or None if insufficient
#       data is available.
#
# -----------------------------------------------------------------
def dtl_pelvis_depth(
        frame: Dict[ str, Any ]
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve world coordinates for both hips
    # -------------------------------------------------------------
    l_hip = get_world_point( frame, "LEFT_HIP" )
    r_hip = get_world_point( frame, "RIGHT_HIP" )

    # -------------------------------------------------------------
    # If the hip landmarks are present and valid, continue.
    # -------------------------------------------------------------
    if ( l_hip is None or r_hip is None ) \
    or ( not l_hip.all() or not r_hip.all() ):
        return None

    # -------------------------------------------------------------
    # Compute the midpoint of the hips.
    # NOTE: Not using midpoint from lib.py here because we want to
    # preserve the Z coordinate for depth.
    # -------------------------------------------------------------
    hip_mid_z = ( l_hip[ 2 ] + r_hip[ 2 ] ) / 2.0

    return float( hip_mid_z )


# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
