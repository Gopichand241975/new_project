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

# Door zone (in Camera 1's frame coordinates)
DOOR_LOCK_ZONE = (400, 300, 700, 850)
DWELL_TIME_ALERT_SECONDS = 8
FORCED_ENTRY_MOTION_DWELL_SECONDS = 5   # dwell time in-zone that counts as "repetitive motion"



# Suspicion scoring
SUSPICION_SCORE_THRESHOLD = 70
WEIGHTS = {
    "long_dwell_time": 30,
    "forced_entry_motion": 30,
    "weapon_or_tool_detected": 40,
}

# Telegram alert credentials
TELEGRAM_BOT_TOKEN = "SET_ME"
TELEGRAM_CHAT_ID = "SET_ME"

# Weapon/tool detection model
WEAPON_MODEL_PATH = "weapon_yolov8.pt"
WEAPON_CONF_THRESHOLD = 0.5