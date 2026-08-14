"""
tracker.py

Two-camera outside forced-entry version. Tracks people in Camera 1's
(wide/normal) frame and measures dwell time inside the door-lock zone —
this is the core "lingering / working at the lock" signal that feeds
scoring_engine.py, alongside forced_entry_motion.
"""

import time

from deep_sort_realtime.deepsort_tracker import DeepSort
from config import DOOR_LOCK_ZONE


def _in_zone(bbox, zone):
    x1, y1, x2, y2 = bbox
    zx1, zy1, zx2, zy2 = zone
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    return zx1 <= cx <= zx2 and zy1 <= cy <= zy2


class PersonTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=30)
        self.zone_entry_time = {}

    def update(self, detections, frame):
        ds_input = [
            (
                [d["bbox"][0], d["bbox"][1],
                 d["bbox"][2] - d["bbox"][0], d["bbox"][3] - d["bbox"][1]],
                d["conf"], "person",
            )
            for d in detections
        ]
        tracks = self.tracker.update_tracks(ds_input, frame=frame)
        results = []
        now = time.time()

        for t in tracks:
            if not t.is_confirmed():
                continue
            track_id = t.track_id
            bbox = tuple(map(int, t.to_ltrb()))

            dwell_time = 0.0
            if _in_zone(bbox, DOOR_LOCK_ZONE):
                self.zone_entry_time.setdefault(track_id, now)
                dwell_time = now - self.zone_entry_time[track_id]
            else:
                self.zone_entry_time.pop(track_id, None)

            results.append({
                "track_id": track_id,
                "bbox": bbox,
                "dwell_time": dwell_time,
            })

        return results