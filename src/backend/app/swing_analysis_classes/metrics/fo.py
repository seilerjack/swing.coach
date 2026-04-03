
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

from   lib                                import *
from   typing                             import Any, Dict

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

    return angle_to_horizontal( l_sh, r_sh )
    

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

    return angle_to_horizontal( l_h, r_h )


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
    # If the hip and shoulder landmarks are present and valid,
    # continue.
    # -------------------------------------------------------------
    if l_s is None or r_s is None or l_h is None or r_h is None:
        return None
    
    # -------------------------------------------------------------
    # Calculate the midpoints for both the shoulders and the hips.
    # -------------------------------------------------------------
    mid_sh = midpoint( l_s, r_s )
    mid_hp = midpoint( l_h, r_h )

    # -------------------------------------------------------------
    # Calculate the spine vector.
    # -------------------------------------------------------------
    dx = mid_sh[ 0 ] - mid_hp[ 0 ]
    dy = mid_sh[ 1 ] - mid_hp[ 1 ]

    spine_vec = np.array( [ dx, dy ] )

    return angle_to_vertical( spine_vec )


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: fo_hip_rotation_range
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
        addr_frame: Dict[ str, Any ],
        cur_frame: Dict[ str, Any ],
        forward_bend: float
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve the hip width at both address and top.
    # -------------------------------------------------------------
    w0 = hip_width( addr_frame )
    w1 = hip_width( cur_frame )

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

    # -------------------------------------------------------------
    # Catch bad spine vector and return uncorrected angle if so.
    # -------------------------------------------------------------
    if forward_bend is None:
        return angle

    # -------------------------------------------------------------
    # Convert to radians for correction.
    # -------------------------------------------------------------
    tilt_rad = np.radians( forward_bend )

    # -------------------------------------------------------------
    # Protect against extreme tilt.
    # -------------------------------------------------------------
    cos_tilt = np.cos( tilt_rad )

    # -------------------------------------------------------------
    # Avoid angle explosion...
    # -------------------------------------------------------------
    if abs( cos_tilt ) < 1e-3:
        return angle

    # -------------------------------------------------------------
    # Correct and return the hip rotation angle by dividing by the
    # cosine of the spine tilt.
    # -------------------------------------------------------------
    corrected = angle / cos_tilt

    return corrected


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: fo_shoulder_rotation_range
#
#   DESCRIPTION:
#       Computes shoulder rotation angle (face-on) using world
#       coords. Measures angle of shoulder line projected onto
#       X-Z plane.
#
#   NOTE: This uses the shoulder width to reintroduce shoulder
#         rotation using only world coordinates.
#
# -----------------------------------------------------------------
def fo_shoulder_rotation_range(
        addr_frame: Dict[ str, Any ],
        cur_frame: Dict[ str, Any ],
        forward_bend: float
    ) -> float | None:

    # -------------------------------------------------------------
    # Retrieve the shoulder width at both address and top.
    # -------------------------------------------------------------
    w0 = shoulder_width( addr_frame )
    w1 = shoulder_width( cur_frame )

    # -------------------------------------------------------------
    # Ensure shoulder widths are valid and non zero to protect
    # divide by zero before continuing.
    # -------------------------------------------------------------
    if not w0 or not w1 or w0 < 1e-6:
        return None

    # -------------------------------------------------------------
    # Clamp for safety in case of numerical issues with very small
    # hip widths.
    # -------------------------------------------------------------
    ratio = np.clip( w1 / w0, -1.0, 1.0 )

    # -------------------------------------------------------------
    # Turn the ratio of shoulder widths into an angle using arccos.
    # The ratio of shoulder widths corresponds to the cosine of the
    # shoulder rotation angle, since as the shoulders rotate away
    # from the camera, the apparent width decreases. We take the
    # arccosine to get the angle in radians, then convert to
    # degrees.
    # -------------------------------------------------------------
    angle = np.degrees( np.arccos( ratio ) )

    # -------------------------------------------------------------
    # Catch bad spine vector and return uncorrected angle if so.
    # -------------------------------------------------------------
    if forward_bend is None:
        return angle

    # -------------------------------------------------------------
    # Convert to radians for correction.
    # -------------------------------------------------------------
    tilt_rad = np.radians( forward_bend )

    # -------------------------------------------------------------
    # Protect against extreme tilt.
    # -------------------------------------------------------------
    cos_tilt = np.cos( tilt_rad )

    # -------------------------------------------------------------
    # Avoid angle explosion...
    # -------------------------------------------------------------
    if abs( cos_tilt ) < 1e-3:
        return angle

    # -------------------------------------------------------------
    # Correct and return the hip rotation angle by dividing by the
    # cosine of the spine tilt.
    # -------------------------------------------------------------
    corrected = angle / cos_tilt

    return corrected


# -----------------------------------------------------------------
#
#   PROCEDURE NAME: fo_head_displacement
#
#   DESCRIPTION:
#       Computes the lateral (horizontal) and vertical head
#       displacement from address to the current frame using the
#       NOSE landmark.
#
#       Lateral (x):
#           + → right (trail side for RH)
#           - → left  (lead side for RH)
#
#       Vertical (y):
#           + → down
#           - → up
#
#       Output is normalized by shoulder width at address to ensure
#       scale invariance across different video resolutions.
#
# -----------------------------------------------------------------
def fo_head_displacement(
        addr_frame: Dict[ str, Any ],
        cur_frame: Dict[ str, Any ],
        width: int,
        height: int
    ) -> Tuple[ float, float ] | None:

    # -------------------------------------------------------------
    # Retrieve reference head position at address
    # -------------------------------------------------------------
    ref = get_pixel_point( addr_frame, "NOSE", width, height )

    if not ref:
        return None

    # -------------------------------------------------------------
    # Retrieve shoulder landmarks at address
    # -------------------------------------------------------------
    l_sh = get_pixel_point( addr_frame, "LEFT_SHOULDER", width, height )
    r_sh = get_pixel_point( addr_frame, "RIGHT_SHOULDER", width, height )

    if not l_sh or not r_sh:
        return None

    # -------------------------------------------------------------
    # Compute shoulder width (normalization factor)
    # -------------------------------------------------------------
    shoulder_width = np.linalg.norm(
        np.array( [ r_sh[ 0 ] - l_sh[ 0 ], r_sh[ 1 ] - l_sh[ 1 ] ] )
    )

    if shoulder_width < 1e-6:
        return None

    # -------------------------------------------------------------
    # Retrieve current head position
    # -------------------------------------------------------------
    pt = get_pixel_point( cur_frame, "NOSE", width, height )

    if not pt:
        return None

    # -------------------------------------------------------------
    # Compute signed displacement
    # -------------------------------------------------------------
    dx = pt[ 0 ] - ref[ 0 ]
    dy = pt[ 1 ] - ref[ 1 ]

    # -------------------------------------------------------------
    # Normalize by shoulder width
    # -------------------------------------------------------------
    norm_dx = dx / shoulder_width
    norm_dy = dy / shoulder_width

    return ( float( norm_dx ), float( norm_dy ) )


# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
