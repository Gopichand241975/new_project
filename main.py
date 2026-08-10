"""
main.py

Post-entry indoor pipeline:

    indoor camera -> person detection -> tracking (movement flag)
                  -> ir_check decides face vs IR+gait mode
                  -> face_id (normal light) OR gait_id (IR / low light)
                  -> scoring_engine (identity + unusual movement)
                  -> alert if triggered

weapon_detect.py is intentionally NOT wired in here — it's optional/
secondary now that the system is post-entry rather than door-focused.
Import and call it inside the loop yourself if you want it back as an
extra signal.
"""
import argparse
import time

import cv2

from detection import PersonDetector
from tracker import PersonTracker
from face_id import FaceIdentifier
from gait_id import GaitIdentifier
from ir_check import IRModeMonitor, FACE_MODE, IR_GAIT_MODE
from scoring_engine import compute_suspicion_score
from alerts import send_alert, TamperMonitor
