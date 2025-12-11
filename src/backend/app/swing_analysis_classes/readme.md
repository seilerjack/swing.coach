

#
#  NOTE: For more information on the Pose Estimation model, see: 

# https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/pose.md


### static_image_mode - Treat the input images as a video stream.

### model_complexity - Complexity of the pose landmark model. Landmark accuracy as well as interfernce latency generally go up with model complexity.

### smooth_landmarks - Filter pose landmarks across different input images to reduce jitter.

### enable_segmentation - Additionally produce a segmentation mask?

### min_detection_confidence - Minimum confidence value from the person-detection model for the detection to be considered successful.

### min_tracking_confidence - Minimum confidence value for the landmark-tracking model for the pose landmarks to be considered successful.
