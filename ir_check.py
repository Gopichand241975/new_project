"""
tracker.py

Two-camera outside forced-entry version. Tracks people in Camera 1's
(wide/normal) frame and measures dwell time inside the door-lock zone —
this is the core "lingering / working at the lock" signal that feeds
scoring_engine.py, alongside forced_entry_motion.
"""