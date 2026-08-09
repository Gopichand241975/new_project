"""
scoring_engine.py

Post-entry version. Suspicion score is now built from:
    - face_unrecognized   (face mode ran, and the person wasn't matched)
    - gait_unrecognized   (gait/IR mode ran, and the person wasn't matched)
    - unusual_movement    (behaviour flag: erratic path, lingering near
                            valuables, repeated backtracking, etc.)

"Unknown alone is not enough" is enforced here: identity weights only push
the score up partway. SUSPICION_SCORE_THRESHOLD (in config.py) should be
set so that identity mismatch alone never crosses it — only identity +
unusual movement together should trigger an alert.
"""

from config import SUSPICION_SCORE_THRESHOLD, WEIGHTS


def compute_suspicion_score(
    identity_name,
    identity_mode,
    unusual_movement,
):
    """
    identity_name: matched name string, or None if unrecognized.
    identity_mode: "face" or "ir_gait" — which recognizer produced the result,
                   from ir_check.decide_mode / IRModeMonitor.
    unusual_movement: bool, from behaviour analysis (e.g. tracker.py).
    """
    score = 0
    reasons = []
    is_unknown = identity_name is None

    if is_unknown and identity_mode == "face":
        score += WEIGHTS["face_unrecognized"]
        reasons.append("face not recognized")
    elif is_unknown and identity_mode == "ir_gait":
        score += WEIGHTS["gait_unrecognized"]
        reasons.append("gait not recognized (IR mode)")

    if unusual_movement:
        score += WEIGHTS["unusual_movement"]
        reasons.append("unusual movement pattern")

    triggered = score >= SUSPICION_SCORE_THRESHOLD

    return {
        "score": score,
        "triggered": triggered,
        "reasons": reasons,
        "identity": identity_name if identity_name else "Unknown",
        "mode": identity_mode,
    }