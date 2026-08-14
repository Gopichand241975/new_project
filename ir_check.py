"""
ir_check.py

Decides, per frame, whether the pipeline should rely on normal-light face
recognition or fall back to IR-lit footage + gait recognition.

Logic:
    - Compute mean grayscale brightness of the frame.
    - If brightness >= DARKNESS_BRIGHTNESS_THRESHOLD -> "face" mode
      (normal color footage, face recognition is attempted first).
    - If brightness < DARKNESS_BRIGHTNESS_THRESHOLD -> "ir_gait" mode
      (assume the camera has switched to IR illumination; skip straight to
      gait recognition, since face recognition is unreliable under IR/low
      light without a model trained specifically for IR faces).

This module does not control the physical IR cut filter / illuminator on
the camera itself — most indoor security cameras switch to IR automatically
in low light. This module only decides which *software* path to run against
whatever footage is coming in.
"""

import cv2

from config import DARKNESS_BRIGHTNESS_THRESHOLD

FACE_MODE = "face"
IR_GAIT_MODE = "ir_gait"


def frame_brightness(frame):
    """Mean grayscale intensity of a frame, 0-255."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(gray.mean())


def decide_mode(frame, threshold=DARKNESS_BRIGHTNESS_THRESHOLD):
    """
    Returns FACE_MODE or IR_GAIT_MODE for the given frame.
    """
    brightness = frame_brightness(frame)
    if brightness < threshold:
        return IR_GAIT_MODE
    return FACE_MODE


class IRModeMonitor:
    """
    Optional smoothing wrapper so the pipeline doesn't flicker between
    modes on borderline-brightness frames (e.g. a light briefly passing
    over the camera). Requires N consecutive frames in the new mode
    before switching.
    """

    def __init__(self, threshold=DARKNESS_BRIGHTNESS_THRESHOLD, stability_frames=5):
        self.threshold = threshold
        self.stability_frames = stability_frames
        self.current_mode = FACE_MODE
        self._pending_mode = None
        self._pending_count = 0

    def update(self, frame):
        candidate = decide_mode(frame, self.threshold)
        if candidate == self.current_mode:
            self._pending_mode = None
            self._pending_count = 0
            return self.current_mode

        if candidate == self._pending_mode:
            self._pending_count += 1
        else:
            self._pending_mode = candidate
            self._pending_count = 1

        if self._pending_count >= self.stability_frames:
            self.current_mode = candidate
            self._pending_mode = None
            self._pending_count = 0

        return self.current_mode