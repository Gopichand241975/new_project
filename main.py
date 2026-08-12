"""
main.py

Two-camera outside forced-entry detection pipeline:

    Camera 1 (wide/normal) -> person detection -> tracking
                            -> door-zone dwell time + forced-entry motion flag

    Camera 2 (high fps)    -> weapon/tool-near-hand detection
                            -> matched to Camera 1's tracked person by bbox overlap

    Both signals -> scoring_engine -> alert if triggered

Camera 2 is read in its own thread since it may run at a different frame
rate than Camera 1, and we don't want it blocking the main detection loop.
"""