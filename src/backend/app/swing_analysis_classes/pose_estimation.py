

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

from zipfile import Path
import cv2
import os
import sys
import uuid
import tempfile

# ---------------------------------------------------------------------
# Add the parent directory to the system path to allow for relative
# imports.
# ---------------------------------------------------------------------
PARENT_DIR = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
sys.path.append( PARENT_DIR )

from lib                        import SHARED_DIR
from pathlib                    import Path
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
    
    def __init__( 
            self, 
            face_on_path: str, 
            down_the_line_path: str,
            temp_dir_path: str
            ) -> None:
        
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
        # INPUTS
        # -------------------------------------------------------------
        # Path to the swing video we are analyzing. Include situational
        # context and swing metadata.
        # -------------------------------------------------------------
        self.face_on_video_path       = face_on_path
        self.down_the_line_video_path = down_the_line_path
        
        # -------------------------------------------------------------
        # OUTPUT
        # -------------------------------------------------------------
        # Initialize structures to hold the pose data and overlay
        # paths for each video.
        # -------------------------------------------------------------
        self.face_on_pose_data: List[ Dict[ str, Any ] ]       = []
        self.down_the_line_pose_data: List[ Dict[ str, Any ] ] = []

        self.face_on_overlay_path       = None
        self.down_the_line_overlay_path = None

        # -------------------------------------------------------------
        # Apply the pose estimation model and generate the overlays.
        # -------------------------------------------------------------
        for video in [
            self.face_on_video_path,
            self.down_the_line_video_path
        ] :
            # ---------------------------------------------------------
            # Generate a unique temporary path for the output video
            # overlay.
            # ---------------------------------------------------------
            output_vid_path = os.path.join(
                temp_dir_path,
                f"{ uuid.uuid4().hex }_overlay.mp4"
            )

            # ---------------------------------------------------------
            # Estimate poses and generate overlay video.
            # ---------------------------------------------------------
            pose_data = self._estimate_poses(
                video_path=video,
                output_vid_path=output_vid_path
            )

            # ---------------------------------------------------------
            # Store the results in the appropriate attributes.
            # ---------------------------------------------------------
            if video == self.face_on_video_path:
                self.face_on_pose_data    = pose_data
                self.face_on_overlay_path = output_vid_path
            else:
                self.down_the_line_pose_data    = pose_data
                self.down_the_line_overlay_path = output_vid_path
    
    
    # -----------------------------------------------------------------
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------
    
    def _estimate_poses(
            self, 
            video_path: str, 
            output_vid_path: str 
        ) -> List[ Dict[ str, Any ] ]:
        
        # -------------------------------------------------------------
        # Initialize output structure to hold pose data.
        # -------------------------------------------------------------
        frames: List[ Dict[ str, Any ] ] = []

        # -------------------------------------------------------------
        # Instantiate a VideoCapture instance with the input video.
        # -------------------------------------------------------------
        cap = cv2.VideoCapture( video_path )
        if not cap.isOpened():
            raise FileNotFoundError( f"Could not open video: { video_path }" )
        
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
        # Initialize overlay video writer.
        #
        # NOTE: We must force the MSMY API for H264 encoding. This
        # allows for embedded browser streaming.
        # -------------------------------------------------------------
        if output_vid_path:
            fourcc = cv2.VideoWriter.fourcc( *"H264" )
            writer = cv2.VideoWriter(
                filename=output_vid_path,
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
            if writer:
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
        # TODO
        # -------------------------------------------------------------
            ### Interpolate Missing Pose Data Here ###

        # -------------------------------------------------------------
        # Return the frame structure containing the modeled pose data.
        # -------------------------------------------------------------
        return frames

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
