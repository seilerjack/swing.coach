

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

from lib                        import FullData
from typing                     import Any, Dict, List
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
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
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
        self.face_on_data: FullData       = { "metadata": {}, "frames": [ {} ] }
        self.down_the_line_data: FullData = { "metadata": {}, "frames": [ {} ] }

        self.face_on_overlay_path         = None
        self.down_the_line_overlay_path   = None

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
                self.face_on_data         = pose_data
                self.face_on_overlay_path = output_vid_path
            else:
                self.down_the_line_data         = pose_data
                self.down_the_line_overlay_path = output_vid_path
    
    
    # -----------------------------------------------------------------
    #                        PRIVATE METHODS
    # -----------------------------------------------------------------
    
    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: _estimate_poses
    #
    #   DESCRIPTION:
    #       Constructs the full dataset for a given video. This
    #       includes video metadata and frame by frame pose estimation
    #       data.
    #
    #       This method also overlays the pose estimation data ontop of
    #       the original video file and outputs it as an artifact.
    #
    # -----------------------------------------------------------------
    def _estimate_poses(
            self, 
            video_path: str, 
            output_vid_path: str
        ) -> FullData:
        
        # -------------------------------------------------------------
        # Initialize output structure to hold pose data for all frames.
        # Metatdata will contain:
        #   - video width, height, fps, total frames, rotation applied
        # Each frame will contain:
        #   - combined landmark data with image and world coordinates,
        #     visibility, presence, and validity
        # -------------------------------------------------------------
        metadata: Dict[ str, Any ]       = {}
        frames: List[ Dict[ str, Any ] ] = []
        full_data: FullData              = { "metadata": {}, "frames": [ {} ] }

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
        rotate = width > height
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

            # -----------------------------------------------------
            # Rotate the frame if necessary before processing with
            # MediaPipe. This ensures the pose estimation model
            # receives the correct orientation.
            # -----------------------------------------------------
            if rotate:
                frame = cv2.rotate( frame, cv2.ROTATE_90_CLOCKWISE )

            # ---------------------------------------------------------
            # Convert to an RGB color-scale (if not already) for 
            # MediaPipe.
            # ---------------------------------------------------------
            frame_corrected: Any = self.pose_obj.process(
                image=cv2.cvtColor( src=frame, code=cv2.COLOR_BGR2RGB )
            )

            # ---------------------------------------------------------
            # Initialize per-frame landmark container.
            # ---------------------------------------------------------
            landmarks: Dict[ str, Dict[ str, Any ] ] = {}

            # ---------------------------------------------------------
            # Populate landmarks if detected.
            # ---------------------------------------------------------
            if frame_corrected.pose_landmarks and frame_corrected.pose_world_landmarks:

                for name, enum in self.mp_pose.PoseLandmark.__members__.items():

                    lm_img   = frame_corrected.pose_landmarks.landmark[ enum ]
                    lm_world = frame_corrected.pose_world_landmarks.landmark[ enum ]

                    # -------------------------------------------------
                    # Landmark data must have at least a 60% visibility
                    # score for the frame to be considered valid.
                    # -------------------------------------------------
                    valid = lm_img.visibility > 0.6

                    # -------------------------------------------------
                    # Combined landmark data
                    # -------------------------------------------------
                    landmarks[ name ] = {
                        "image": {
                            "x": float( lm_img.x ),
                            "y": float( lm_img.y ),
                            "z": float( lm_img.z ),
                        },
                        "world": {
                            "x": float( lm_world.x ),
                            "y": float( lm_world.y ),
                            "z": float( lm_world.z ),
                        },
                        "visibility": float( lm_img.visibility ),
                        "presence": float( lm_img.presence ),
                        "valid": valid,
                    }

            # ---------------------------------------------------------
            # If no pose detected, mark all landmarks invalid.
            # ---------------------------------------------------------
            else:
                for name in self.mp_pose.PoseLandmark.__members__:
                    landmarks[ name ] = {
                        "image": {
                            "x": None, "y": None, "z": None,
                        },
                        "world": {
                            "x": None, "y": None, "z": None,
                        },
                        "visibility": 0.0,
                        "presence": 0.0,
                        "valid": False,
                    }

            # ---------------------------------------------------------
            # Append frame pose data.
            # ---------------------------------------------------------
            frames.append( {
                "frame_index": frame_idx,
                "landmarks": landmarks,
            } )

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
                # Overlay the Frame Number.
                # NOTE: THIS IS FOR DEBUGGING PURPOSES ONLY - REMOVE ON
                # PRODUCTION.
                # -----------------------------------------------------
                text      = f"Frame: { frame_idx }"
                font      = cv2.FONT_HERSHEY_SIMPLEX
                pos       = ( 50, 50 )
                scale     = 1.5
                thickness = 3
                cv2.putText( overlaid, text, pos, font, scale, ( 0, 0, 0 ), thickness + 2 )
                cv2.putText( overlaid, text, pos, font, scale, ( 255, 255, 255 ), thickness )
                
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
        # Construct the videos metadata.
        # -------------------------------------------------------------
        metadata = {
            "width": out_width,
            "height": out_height,
            "fps": fps,
            "num_frames": frame_idx,
            "rotation_applied": rotate
        }

        # -------------------------------------------------------------
        # Construct the full dataset with the video metadata and frame
        # structure containing the modeled pose data.
        # -------------------------------------------------------------
        full_data = {
            "metadata": metadata,
            "frames": frames
        }

        return full_data

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------
