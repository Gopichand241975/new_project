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