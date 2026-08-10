"""
main.py

Post-entry indoor pipeline:

    indoor camera -> person detection -> tracking (movement flag)
                  -> ir_check decides face vs IR+gait mode
                  -> face_id (normal light) OR gait_id (IR / low light)
                  -> scoring_engine (identity + unusual movement)
                  -> alert if triggered

weapon_detect.py is intentionally NOT wired in here — it's optional/
secondary now that the system is post-entry rather than door-focused.
Import and call it inside the loop yourself if you want it back as an
extra signal.
"""