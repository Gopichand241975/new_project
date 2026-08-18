"""
scoring_engine.py

Single-camera outside forced-entry version. No weapon/tool detection, no
identity check — suspicion score is built purely from door-zone behaviour:

    - long_dwell_time      (lingering in the door-lock zone)
    - forced_entry_motion  (repetitive motion in the zone, e.g.
                             jiggling/working at the lock)
"""