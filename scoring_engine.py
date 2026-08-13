"""
scoring_engine.py

Two-camera outside forced-entry version. No identity/face/gait component —
this system runs before entry, so there's no known-person database to check
against. Suspicion score is built from:

    - long_dwell_time         (Camera 1: lingering in the door-lock zone)
    - forced_entry_motion     (Camera 1: repetitive motion in the zone,
                                e.g. jiggling/working at the lock)
    - weapon_or_tool_detected (Camera 2: tool/weapon detected near the hand)
"""

from config import SUSPICION_SCORE_THRESHOLD, WEIGHTS


def compute_suspicion_score(dwell_time, forced_entry_motion, weapon_detected):
    score = 0
    reasons = []

    if dwell_time >= 0 and forced_entry_motion is False and dwell_time >= _dwell_alert_seconds():
        score += WEIGHTS["long_dwell_time"]
        reasons.append(f"long dwell time ({dwell_time:.1f}s at lock)")

    if forced_entry_motion:
        score += WEIGHTS["forced_entry_motion"]
        reasons.append("repetitive forced-entry motion")

    if weapon_detected:
        score += WEIGHTS["weapon_or_tool_detected"]
        reasons.append("tool/weapon detected near hand")

    triggered = score >= SUSPICION_SCORE_THRESHOLD

    return {
        "score": score,
        "triggered": triggered,
        "reasons": reasons,
    }


def _dwell_alert_seconds():
    from config import DWELL_TIME_ALERT_SECONDS
    return DWELL_TIME_ALERT_SECONDS