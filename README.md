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

## Not currently used

These modules were built for earlier versions of the project (an indoor
identity-based stage, and a two-camera weapon-detection stage) and are not
wired into `main.py` in the current design. Left in the repo in case
identity or weapon detection gets added back later:

- `face_id.py`
- `gait_id.py`
- `ir_check.py`

`weapon_detect.py` has been removed entirely.


## Setup

1. Install dependencies (see `requirements.txt`).
2. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `config.py`.
3. Adjust `DOOR_LOCK_ZONE` in `config.py` to match your camera's framing of the door/lock area.
4. Run the system:
```bash
   python main.py --camera 0
```

## Setup

1. Install dependencies (see `requirements.txt`).
2. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `config.py`.
3. Adjust `DOOR_LOCK_ZONE` in `config.py` to match your camera's framing of the door/lock area.
4. Run the system:
```bash
   python main.py --camera 0
```

## Known limitations

- A person who lingers near the door briefly (e.g. checking their phone, waiting for someone) may occasionally cross the dwell-time threshold and cause a false alert.
- Detection is restricted to humans only (pets/vehicles ignored).
- No identity check — the system can't distinguish a family member fumbling with keys from a stranger; it only reacts to behaviour at the door.

## References

See `Research_Papers_Download_Links.pdf` for the research backing the detection and tracking components used in this project.

Suggested commit:

bash
git add README.md
git commit -m "docs: update README for single-camera outside forced-entry design (drop weapon/identity references)"
git push

That closes out the "still out of sync" list. Remaining open items are weapon_detect.py deletion (command given last turn), the unused identity files (your call whether to keep or remove), and the newer additions — requirements.txt, tests/, and the report PDF update. Want any of those next?S