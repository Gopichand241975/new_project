"""
scoring_engine.py

Two-camera outside forced-entry version. No identity/face/gait component —
this system runs before entry, so there's no known-person database to check
against. Suspicion score is built from:

    - long_dwell_time         (Camera 1: lingering in the door-lock zone)
    - forced_entry_motion     (Camera 1: repetitive motion in the zone,
                                e.g. jiggling/working at the lock)
    - weapon_or_tool_detected (Camera 2: tool/weapon detected near the hand)
"""
from config import SUSPICION_SCORE_THRESHOLD, WEIGHTS