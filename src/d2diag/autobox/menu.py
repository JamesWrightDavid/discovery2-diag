"""Auto gearbox GS8.87.0 (Bosch, ZF4HP22-24) NanoCom menu — the catalog derives how far we are.

Data model: see :mod:`d2diag.td5.menu` (ADR-0008). **Own protocol (``72``-framed)**,
sniffed 2026-08-10: the reference tool said "unable to perform the function" but the ECU
responds with a data block. Function IDs proven; content interpretation awaits a session.
The fault list in the dictionary (39 RAVE P-codes) is official + forum-confirmed.

Sources: ``references/menus/autobox.md`` (exact UI order) and the emulator tree
``references/nanocom/td5_menu_tree.md`` (``d2_autogb``: faults, inputs general (5 pages) +
pressures (4 pages), settings (2 pages), utility (reset); **no outputs page**).
"""

AUTOBOX_MENU = [
    {"id": "faults", "page": "faults", "cat": "Fault codes", "nanocom": "d2_autogb/faults", "items": [
        {"id": "read-faults", "name": "Read faults (Faults - Read)", "status": "candidate",
         "ref": "cmd 72 05 04 00 73 proven (ECU responds 72 09 60 …); dictionary 39 P-codes; content TBD"},
        {"id": "clear-faults", "name": "Clear faults (Faults - Clear)", "status": "candidate",
         "ref": "cmd 72 04 05 73 proven"},
    ]},
    {"id": "inputs-general", "page": "inputs", "cat": "Inputs — general (26)", "nanocom": "d2_autogb/inputs/general",
     "items": [
        # read via 72 05 0B 00 (pressure) / 72 05 0B 03 (general); response 72 16 60 … (bulk)
        {"id": f"in-{n}", "name": name, "status": "sniff", "ref": ""}
        for n, name in enumerate([
            "1. Throttle position (%)", "2. Engine torque (%)", "3. Torque requested (%)",
            "4. Reduced torque (%)", "5. Friction torque (%)", "6. Torque reference (Nm)",
            "7. Gear switch W", "8. Gear switch X", "9. Gear switch Y", "10. Gear switch Z",
            "11. Program switch", "12. High/Low range switch", "13. Kick down", "14. Shift type",
            "15. Engine speed (rpm)", "16. Turbine speed (rpm)", "17. Output speed (rpm)",
            "18. Battery (V)", "19. Solenoid valve 1", "20. Solenoid valve 2", "21. Solenoid valve 3",
            "22. Modulator pressure", "23. Engine temperature (°C)", "24. Adaptive program 1",
            "25. Adaptive program 2", "26. Adaptive program 3"], start=1)
    ]},
    {"id": "inputs-pressures", "page": "inputs", "cat": "Inputs — pressures",
     "nanocom": "d2_autogb/inputs/pressures", "items": [
        {"id": "pressures", "name": "Pressures (not transcribed)", "untranscribed": True, "pages": 4,
         "ref": "72 05 0B 00; vendor guide: adaptive pressures for upshifts 1-2/2-3/3-4 in three speed ranges"},
    ]},
    {"id": "settings", "page": "settings", "cat": "Settings", "nanocom": "d2_autogb/settings", "items": [
        {"id": "settings", "name": "Settings (not transcribed)", "untranscribed": True, "pages": 2,
         "ref": "read request + identification"},
    ]},
    {"id": "utilities", "page": "utilities", "cat": "Utility", "nanocom": "d2_autogb/utility", "items": [
        {"id": "reset-adaptives", "name": "Reset adaptive values", "actions": ["autobox_reset_adaptives"],
         "ref": "72 06 83 FF 07 08 FF (undecoded) ⚠️ writes"},
    ]},
]
