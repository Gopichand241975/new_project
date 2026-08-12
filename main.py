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

class Camera2Reader:
    """Continuously reads the high-fps camera in a background thread and
    keeps only the latest frame, so the main loop never blocks on it."""

    def __init__(self, source, target_fps):
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FPS, target_fps)
        self.latest_frame = None
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self):
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                continue
            with self.lock:
                self.latest_frame = frame

    def read(self):
        with self.lock:
            return None if self.latest_frame is None else self.latest_frame.copy()

    def release(self):
        self.running = False
        self.thread.join(timeout=1)
        self.cap.release()