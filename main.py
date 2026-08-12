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


def run(camera_1_source, camera_2_source):
    cap1 = cv2.VideoCapture(camera_1_source)
    cam2 = Camera2Reader(camera_2_source, CAMERA_2_TARGET_FPS)

    detector = PersonDetector()
    tracker = PersonTracker()
    weapon_detector = WeaponDetector()
    tamper_monitor = TamperMonitor()

    alerted_tracks = set()

    while True:
        ok, frame1 = cap1.read()
        if not ok:
            break

        tamper_monitor.check(frame1, camera_name="Camera 1 (Door)")

        detections = detector.detect(frame1)
        tracks = tracker.update(detections, frame1)

        frame2 = cam2.read()  # latest available high-fps frame, may be None early on

        for t in tracks:
            track_id = t["track_id"]
            bbox = t["bbox"]

            weapon = None
            if frame2 is not None:
                weapon = weapon_detector.detect_in_hand(frame2, bbox)

            forced_entry_motion = t["dwell_time"] >= 5

            result = compute_suspicion_score(
                dwell_time=t["dwell_time"],
                forced_entry_motion=forced_entry_motion,
                weapon_detected=bool(weapon),
            )

            if result["triggered"] and track_id not in alerted_tracks:
                snapshot_path = f"snapshot_{track_id}_{int(time.time())}.jpg"
                cv2.imwrite(snapshot_path, frame1)
                reasons = ", ".join(result["reasons"])
                send_alert(
                    f"Possible break-in attempt detected. "
                    f"Score: {result['score']}. Reasons: {reasons}.",
                    snapshot_path,
                )
                alerted_tracks.add(track_id)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap1.release()
    cam2.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera1", type=int, default=CAMERA_1_SOURCE, help="Camera 1 (wide) index or path")
    parser.add_argument("--camera2", type=int, default=CAMERA_2_SOURCE, help="Camera 2 (high-fps) index or path")
    args = parser.parse_args()
    run(args.camera1, args.camera2)