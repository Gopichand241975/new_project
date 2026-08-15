"""
Central configuration for the outside forced-entry detection system.

Single camera, door-facing. Detects a person lingering or repeatedly
working at the door lock and sends an alert based on dwell time and
motion pattern alone.
"""

# Camera source
CAMERA_1_SOURCE = 0
# Door zone (in Camera 1's frame coordinates)
DOOR_LOCK_ZONE = (400, 300, 700, 850)
DWELL_TIME_ALERT_SECONDS = 8
FORCED_ENTRY_MOTION_DWELL_SECONDS = 5   # dwell time in-zone that counts as "repetitive motion"

# Suspicion scoring
SUSPICION_SCORE_THRESHOLD = 50
WEIGHTS = {
    "long_dwell_time": 50,
    "forced_entry_motion": 50,
}
