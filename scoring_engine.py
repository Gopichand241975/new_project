"""
scoring_engine.py

Single-camera outside forced-entry version. No weapon/tool detection, no
identity check — suspicion score is built purely from door-zone behaviour:

    - long_dwell_time      (lingering in the door-lock zone)
    - forced_entry_motion  (repetitive motion in the zone, e.g.
                             jiggling/working at the lock)
"""

from config import SUSPICION_SCORE_THRESHOLD, WEIGHTS, DWELL_TIME_ALERT_SECONDS


def compute_suspicion_score(dwell_time, forced_entry_motion):
    score = 0
    reasons = []

    if forced_entry_motion:
        score += WEIGHTS["forced_entry_motion"]
        reasons.append("repetitive forced-entry motion")
    elif dwell_time >= DWELL_TIME_ALERT_SECONDS:
        score += WEIGHTS["long_dwell_time"]
        reasons.append(f"long dwell time ({dwell_time:.1f}s at lock)")

    triggered = score >= SUSPICION_SCORE_THRESHOLD

    return {
        "score": score,
        "triggered": triggered,
        "reasons": reasons,
    }