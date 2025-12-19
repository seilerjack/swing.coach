

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import cv2
import os
import sys
import uuid

# ---------------------------------------------------------------------
# Add the parent directory to the system path to allow for relative
# imports.
# ---------------------------------------------------------------------
PARENT_DIR = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
sys.path.append( PARENT_DIR )

from lib                        import SHARED_DIR
from typing                     import Any, Dict, List, Optional  
from mediapipe.python.solutions import drawing_utils as mp_drawing_utils
from mediapipe.python.solutions import pose          as mp_pose_module


# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: PoseEstimation
#
#   DESCRIPTION:
#       Uses MediaPipe's Pose solution to estimate human poses in video
#       frames. Outputs structured pose data as a json dictionary and
#       can optionally generate a video with pose overlay.
#
# ---------------------------------------------------------------------
class PoseEstimation:
    
    def __init__( self, vid_in: str, overlay: Optional[ bool ] = False ) -> None:
        
        # -------------------------------------------------------------
        # Initialize the input and output video paths with the provided
        # and constant values.
        # -------------------------------------------------------------
        self.input_vid_path  = vid_in
        self.output_vid_path = os.path.join( SHARED_DIR, f"pose_overlay_{ uuid.uuid4().hex }.mp4" )
        self.overlay         = overlay

        # -------------------------------------------------------------
        # Initialize the mediapipe related resources.
        # -------------------------------------------------------------
        self.mp_drawing = mp_drawing_utils
        self.mp_pose    = mp_pose_module
        self.pose_obj   = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )

        # -------------------------------------------------------------
        # Calculate pose data and overlay esitmations, if specified.
        # -------------------------------------------------------------
        self.pose_data = self._estimate_poses()

    # -----------------------------------------------------------------
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------
    
    def _estimate_poses( self ) -> List[ Dict[ str, Any ] ]:
        
        # -------------------------------------------------------------
        # Initialize output structure to hold pose data.
        # -------------------------------------------------------------
        frames: List[ Dict[ str, Any ] ] = []

        # -------------------------------------------------------------
        # Instantiate a VideoCapture instance with the input video.
        # -------------------------------------------------------------
        cap = cv2.VideoCapture( self.input_vid_path )
        if not cap.isOpened():
            raise FileNotFoundError( f"Could not open video: { self.input_vid_path }" )
        
        # -------------------------------------------------------------
        # Grab video specific metadata. This will be used if the user
        # has specified for a pose overlay output.
        # -------------------------------------------------------------
        width  = int( cap.get( cv2.CAP_PROP_FRAME_WIDTH ) )
        height = int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT ) )
        fps    = cap.get( propId=cv2.CAP_PROP_FPS )
        
        # -------------------------------------------------------------
        # TODO (video-preprocessing):
        # Phone videos often store portrait footage as rotated landscape
        # buffers.
        # 
        # OpenCV ignores rotation metadata.
        # -------------------------------------------------------------
        rotate = True
        out_width, out_height = ( height, width ) if rotate else ( width, height )

        # -------------------------------------------------------------
        # Initialize overlay video writer if debug visualization is
        # enabled.
        #
        # NOTE: We must force the MSMY API for H264 encoding. This
        # allows for embedded browser streaming.
        # -------------------------------------------------------------
        if self.overlay and self.output_vid_path:
            fourcc = cv2.VideoWriter.fourcc( *"H264" )
            writer = cv2.VideoWriter(
                filename=self.output_vid_path,
                apiPreference=cv2.CAP_MSMF,
                fourcc=fourcc,
                fps=fps,
                frameSize=( out_width, out_height )
            )
        else: writer = None

        # -------------------------------------------------------------
        # Process each from in the video.
        # -------------------------------------------------------------
        frame_idx = 0
        while cap.isOpened():
            # ---------------------------------------------------------
            # Read video frame-by-frame. Exit if the read is 
            # unsuccessful for any frame.
            # ---------------------------------------------------------
            ret, frame = cap.read()
            if not ret:
                break

            # ---------------------------------------------------------
            # Convert to an RGB color-scale (if not already) for 
            # MediaPipe.
            # ---------------------------------------------------------
            frame_corrected: Any = self.pose_obj.process(
                image=cv2.cvtColor( src=frame, code=cv2.COLOR_BGR2RGB )
            )

            # ---------------------------------------------------------
            # Init structure to hold the landmarks for this frame.
            # ---------------------------------------------------------
            frame_landmarks: Dict[ str, Dict[ str, Any ] ] = {}

            # ---------------------------------------------------------
            # Map each MediaPipe landmark to an x, y coordinate and a
            # validity flag
            # ---------------------------------------------------------
            if frame_corrected.pose_landmarks:
                for landmark_name, landmark_enum in self.mp_pose.PoseLandmark.__members__.items():
                    landmark = frame_corrected.pose_landmarks.landmark[ landmark_enum ]
                    frame_landmarks[ landmark_name ] = {
                        "x": float( landmark.x ),
                        "y": float( landmark.y ),
                        "valid": landmark.visibility > 0.6,
                    }
                
            # ---------------------------------------------------------
            # If no landmarks are detected, mark all as invalid for
            # this frame.
            # ---------------------------------------------------------
            else:
                for landmark_name in self.mp_pose.PoseLandmark.__members__:
                    frame_landmarks[ landmark_name ] = { "x": None, "y": None, "valid": False }

            # ---------------------------------------------------------
            # Append any pose data and move on to the next frame.
            # ---------------------------------------------------------
            frames.append( { "frame_index": frame_idx, "landmarks": frame_landmarks } )
            frame_idx += 1

            # ---------------------------------------------------------
            # Optional: Overlay Pose Estimation on the input video.
            # ---------------------------------------------------------
            if self.overlay and writer:
                overlaid = frame.copy()

                # -----------------------------------------------------
                # Draw the landmarks on the new 'overlaid' frame.
                # -----------------------------------------------------
                if frame_corrected.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        image=overlaid,
                        landmark_list=frame_corrected.pose_landmarks,
                        connections=list( self.mp_pose.POSE_CONNECTIONS )
                    )
                
                # -----------------------------------------------------
                # TODO: Calculate whether the frames orientation needs
                # to be adjusted before writing.
                # -----------------------------------------------------
                if rotate:
                    overlaid = cv2.rotate( overlaid, cv2.ROTATE_90_CLOCKWISE )
                
                # -----------------------------------------------------
                # Write the adjusted, overlayed frames to output.
                # -----------------------------------------------------
                writer.write( overlaid )

        # -------------------------------------------------------------
        # Release the video and videowriter resources.
        # -------------------------------------------------------------
        cap.release()
        if writer:
            writer.release()

        # -------------------------------------------------------------
        # ...
        # -------------------------------------------------------------
            ### Interpolate Missing Pose Data Here ###

        # -------------------------------------------------------------
        # Return the frame structure containing the modeled pose data.
        # -------------------------------------------------------------
        return frames

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
