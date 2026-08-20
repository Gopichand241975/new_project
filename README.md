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
