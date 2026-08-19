"""
main.py

Single-camera outside forced-entry pipeline:

    Camera 1 (door-facing) -> person detection -> tracking
                            -> door-zone dwell time + forced-entry motion
                            -> scoring_engine -> alert if triggered
"""