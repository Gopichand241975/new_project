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

def run(camera_source):
    cap = cv2.VideoCapture(camera_source)
    detector = PersonDetector()
    tracker = PersonTracker()
    tamper_monitor = TamperMonitor()

    alerted_tracks = set()

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        tamper_monitor.check(frame, camera_name="Camera 1 (Door)")

        detections = detector.detect(frame)
        tracks = tracker.update(detections, frame)

        for t in tracks:
            track_id = t["track_id"]
            forced_entry_motion = t["dwell_time"] >= FORCED_ENTRY_MOTION_DWELL_SECONDS

            result = compute_suspicion_score(
                dwell_time=t["dwell_time"],
                forced_entry_motion=forced_entry_motion,
            )

            if result["triggered"] and track_id not in alerted_tracks:
                snapshot_path = f"snapshot_{track_id}_{int(time.time())}.jpg"
                cv2.imwrite(snapshot_path, frame)
                reasons = ", ".join(result["reasons"])
                send_alert(
                    f"Possible break-in attempt detected. "
                    f"Score: {result['score']}. Reasons: {reasons}.",
                    snapshot_path,
                )
                alerted_tracks.add(track_id)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=CAMERA_1_SOURCE, help="Camera index or path")
    args = parser.parse_args()
    run(args.camera)