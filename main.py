"""
main.py

Two-camera outside forced-entry detection pipeline:

    Camera 1 (wide/normal) -> person detection -> tracking
                            -> door-zone dwell time + forced-entry motion flag

    Camera 2 (high fps)    -> weapon/tool-near-hand detection
                            -> matched to Camera 1's tracked person by bbox overlap

    Both signals -> scoring_engine -> alert if triggered

Camera 2 is read in its own thread since it may run at a different frame
rate than Camera 1, and we don't want it blocking the main detection loop.
"""

import argparse
import threading
import time

import cv2

from detection import PersonDetector
from tracker import PersonTracker
from weapon_detect import WeaponDetector
from scoring_engine import compute_suspicion_score
from alerts import send_alert, TamperMonitor
from config import CAMERA_1_SOURCE, CAMERA_2_SOURCE, CAMERA_2_TARGET_FPS