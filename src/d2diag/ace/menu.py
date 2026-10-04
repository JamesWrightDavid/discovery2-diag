"""ACE (Lucas active cornering) NanoCom menu — what exists; the catalog derives how far we are.

Data model: see :mod:`d2diag.td5.menu` (ADR-0008). ACE has not been sniffed yet (D2-JW has
it fitted but it needs a non-standard init), so inputs and outputs are hand ``sniff`` and the
utilities link planned/gated registry actions. Menu order is preserved exactly from the
reference tool (``references/menus/ace.md``); keep item ``name`` strings stable.

⚠️ The reference tool's ACE valve fault texts are unreliable (pressure-sensor faults show
as "control valve" faults). The DCV output tests can make the vehicle jerk violently from
side to side; calibration writes are gated ("Set Calibrated" reportedly locked up ECUs).
"""

ACE_MENU = [
    {"id": "faults", "page": "faults", "cat": "Fault codes", "nanocom": "ace/faults", "items": [
        {"id": "read-faults", "name": "Read faults (Faults - Read)", "status": "candidate",
         "ref": "dictionary 0001–0048; 04-02/04/05 + 06-01 seen RDL 016 via reference tool; raw not sniffed"},
        {"id": "clear-faults", "name": "Clear faults (Faults - Clear)", "status": "sniff",
         "ref": "sniff separately from Read"},
    ]},
    {"id": "inputs-live", "page": "inputs", "cat": "Inputs — live", "nanocom": "ace/inputs", "items": [
        {"id": "engine-speed", "name": "1. Engine Speed (rpm)", "status": "sniff", "ref": ""},
        {"id": "road-speed", "name": "2. Road Speed (km/h)", "status": "sniff", "ref": ""},
        {"id": "battery", "name": "3. Battery Voltage (V)", "status": "sniff", "ref": ""},
        {"id": "dcv1-current", "name": "4. DCV1 Current (A)", "status": "sniff", "ref": "direction valve 1"},
        {"id": "dcv2-current", "name": "5. DCV2 Current (A)", "status": "sniff", "ref": "direction valve 2"},
        {"id": "pcv-current", "name": "6. PCV Current (A)", "status": "sniff", "ref": "pressure control valve"},
        {"id": "pressure-sensor", "name": "7. Pressure Sensor (bar)", "status": "sniff",
         "ref": "key to the valve caveat; owners: 16–19 bar at idle"},
        {"id": "residual-pressure", "name": "8. Residual Pressure (bar)", "status": "sniff", "ref": "owners: 3–6 bar"},
        {"id": "system-pressure", "name": "9. System Pressure (bar)", "status": "sniff", "ref": ""},
        {"id": "upper-accel", "name": "10. Upper Lateral Accelerometer", "status": "sniff", "ref": ""},
        {"id": "lower-accel", "name": "11. Lower Lateral Accelerometer", "status": "sniff", "ref": ""},
        {"id": "ignition-switch", "name": "12. Ignition Switch", "status": "sniff", "ref": ""},
        {"id": "reverse-switch", "name": "13. Reverse Switch", "status": "sniff", "ref": ""},
        {"id": "main-relay", "name": "14. Main Relay", "status": "sniff", "ref": ""},
        {"id": "warning-lamp", "name": "15. Warning Lamp", "status": "sniff", "ref": ""},
    ]},
    {"id": "outputs-tester", "page": "outputs", "cat": "Outputs — tester ⚠️", "nanocom": "ace/outputs", "items": [
        {"id": "main-relay-on", "name": "1. Main relay (Force ON)", "status": "sniff", "ref": "ON / STOP"},
        {"id": "main-relay-off", "name": "2. Main relay (Force OFF)", "status": "sniff", "ref": "OFF / STOP"},
        {"id": "warning-lamp-test", "name": "3. Warning Lamp (ON/OFF)", "status": "sniff", "ref": ""},
        {"id": "dcv1-test", "name": "4. Dir. Control Valve 1 (ON/OFF)", "status": "sniff",
         "ref": "⚠️ activates valve — can jerk the vehicle"},
        {"id": "dcv2-test", "name": "5. Dir. Control Valve 2 (ON/OFF)", "status": "sniff",
         "ref": "⚠️ activates valve — can jerk the vehicle"},
    ]},
    {"id": "utilities-calibration", "page": "utilities", "cat": "Utility ⚠️ — Calibration",
     "nanocom": "ace/utility", "items": [
        {"id": "calibrate-accel-1", "name": "1. Calib. Accelerometer 1", "actions": ["ace_calibrate_1"],
         "ref": "⚠️ writes calibration — gated"},
        {"id": "calibrate-accel-2", "name": "2. Calib. Accelerometer 2", "actions": ["ace_calibrate_2"],
         "ref": "⚠️ writes calibration — gated"},
        {"id": "set-calibrated", "name": "3. Set Calibrated", "actions": ["ace_set_calibrated"],
         "ref": "⚠️ writes — reported to lock up ACE ECUs; gated"},
    ]},
    {"id": "utilities-bleed", "page": "utilities", "cat": "Utility ⚠️ — Oil bleed", "nanocom": "ace/utility",
     "items": [
        {"id": f"oil-bleed-{n}", "name": f"{3 + n}. Oil Bleeding Step {n}", "actions": ["ace_bleed"],
         "ref": "⚠️ active procedure (START / STOP)", "note": f"Step {n} of the 3-step oil bleed."}
        for n in (1, 2, 3)
    ]},
]
