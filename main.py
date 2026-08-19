"""
main.py

Single-camera outside forced-entry pipeline:

    Camera 1 (door-facing) -> person detection -> tracking
                            -> door-zone dwell time + forced-entry motion
                            -> scoring_engine -> alert if triggered
"""

import argparse
import time

import cv2

from detection import PersonDetector
from tracker import PersonTracker
from scoring_engine import compute_suspicion_score
from alerts import send_alert, TamperMonitor
from config import CAMERA_1_SOURCE, FORCED_ENTRY_MOTION_DWELL_SECONDS
