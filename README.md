## Overview

A single door-facing camera watches the door-lock area. If a person
lingers too long in that zone, or shows repetitive motion consistent with
someone working at the lock (jiggling, forcing, picking), the system sends
an alert to the homeowner. There's no identity check and no weapon
detection in the current design — the alert is based purely on dwell time
and motion pattern at the door.

## Pipeline

`alerts.py` also runs a separate tamper check (`TamperMonitor`) on every
frame, independent of the scoring pipeline above — if the feed goes dark
or is blocked for several seconds, it sends its own alert.

## Modules

| File | Purpose |
|---|---|
| `config.py` | Central settings: camera source, door-lock zone, dwell/motion thresholds, suspicion weights, Telegram credentials |
| `detection.py` | YOLOv8 person detection, restricted to the `person` class |
| `tracker.py` | DeepSORT tracking + dwell-time measurement in the door-lock zone |
| `scoring_engine.py` | Combines dwell time + forced-entry motion into a suspicion score; alert fires when the score crosses `SUSPICION_SCORE_THRESHOLD` |
| `alerts.py` | Sends Telegram alerts (with snapshot) and monitors for camera tampering |
| `main.py` | Wires the pipeline together and runs the main loop |
