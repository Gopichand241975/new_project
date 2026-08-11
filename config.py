"""
Central configuration for the two-camera outside forced-entry detection system.

Camera 1: normal/wide feed — person detection, door-zone dwell time.
Camera 2: high frame-rate feed — dedicated to catching fast hand/tool
motion in detail, feeds weapon_detect.py.
"""

# Camera sources
CAMERA_1_SOURCE = 0          # wide/normal camera, door-facing
CAMERA_2_SOURCE = 1          # high-fps camera, same door area, tighter/detail framing
CAMERA_2_TARGET_FPS = 60     # request a high frame rate from camera 2 if the device supports it
