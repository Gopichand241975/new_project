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

GAIT_BUFFER_LEN = 20

def run(camera_source):
    cap = cv2.VideoCapture(camera_source)
    detector = PersonDetector()
    tracker = PersonTracker()
    face_id = FaceIdentifier()
    gait_id = GaitIdentifier()
    ir_monitor = IRModeMonitor()
    tamper_monitor = TamperMonitor()

    alerted_tracks = set()
    silhouette_buffers = {}  # track_id -> list of silhouette frames for gait

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        tamper_monitor.check(frame, camera_name="Indoor Camera")
        mode = ir_monitor.update(frame)  # FACE_MODE or IR_GAIT_MODE

        detections = detector.detect(frame)
        tracks = tracker.update(detections, frame)

        for t in tracks:
            track_id = t["track_id"]
            bbox = t["bbox"]

            if mode == FACE_MODE:
                identity_name = face_id.identify(frame, bbox)
            else:
                # IR/low-light: accumulate a short silhouette buffer per
                # track and run gait recognition once we have enough frames.
                x1, y1, x2, y2 = bbox
                crop = frame[max(0, y1):y2, max(0, x1):x2]
                silhouette = _to_silhouette(crop)
                buf = silhouette_buffers.setdefault(track_id, [])
                buf.append(silhouette)
                if len(buf) > GAIT_BUFFER_LEN:
                    buf.pop(0)
                identity_name = gait_id.identify(buf) if len(buf) >= 5 else None

            result = compute_suspicion_score(
                identity_name=identity_name,
                identity_mode=mode,
                unusual_movement=t["unusual_movement"],
            )

            if result["triggered"] and track_id not in alerted_tracks:
                snapshot_path = f"snapshot_{track_id}_{int(time.time())}.jpg"
                cv2.imwrite(snapshot_path, frame)
                reasons = ", ".join(result["reasons"])
                send_alert(
                    f"Unrecognized person detected inside the house. "
                    f"Identity: {result['identity']}. Mode: {result['mode']}. "
                    f"Score: {result['score']}. Reasons: {reasons}.",
                    snapshot_path,
                )
                alerted_tracks.add(track_id)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def _to_silhouette(person_crop):
    """
    Very simple placeholder silhouette extraction: grayscale + threshold.
    Swap this for a proper background-subtraction or segmentation model
    (e.g. MediaPipe Selfie Segmentation) for real deployment — this is
    just enough to keep the gait pipeline runnable end-to-end.
    """
    gray = cv2.cvtColor(person_crop, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return mask

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0, help="Camera index or path")
    args = parser.parse_args()
    run(args.camera)