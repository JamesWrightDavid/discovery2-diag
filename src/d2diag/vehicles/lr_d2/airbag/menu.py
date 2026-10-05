"""Airbag (TRW SPS Type 2A) NanoCom menu — the catalog derives how far we are.

Data model: see :mod:`d2diag.td5.menu` (ADR-0008). The ECU is limited: Read/Clear Faults +
Settings (ID/config); the NanoCom has **no** live Inputs, Outputs or Utility page
(``references/nanocom/td5_menu_tree.md``, ``d2_airbag``).

🔴 SAFETY: SRS is pyrotechnics. **Read only by construction** (CONSTITUTION): no
registry actions at all, every item is ``read`` or ``gated``. Never activate any output or
firing circuit. Only clear faults once the fault is fixed.
"""

_SETTINGS = [
    ("1. Manufacturer", ""), ("2. Model", ""), ("3. Software version", ""), ("4. Hardware version", ""),
    ("5. Serial number", ""), ("6. Date of build", ""), ("7. Part reference", ""), ("8. Part number", ""),
    ("9. VIN", "the only documented writable one — read only here"),
    ("10. Driver's airbag (present)", ""), ("11. Passenger's airbag (present)", ""),
    ("12. Right hand Pretensioner", ""), ("13. Left hand Pretensioner", ""),
    ("14. Driver's side airbag", ""), ("15. Passenger's side airbag", ""), ("16. Rolamites", "crash sensors"),
]

AIRBAG_MENU = [
    {"id": "faults", "page": "faults", "cat": "Fault codes", "nanocom": "d2_airbag/faults", "items": [
        {"id": "read-faults", "name": "Read faults (Faults - Read)", "status": "candidate",
         "ref": "dictionary: position=display code solved (1–65); 004 + 022 seen RDL 016 via reference tool; raw not sniffed"},
        {"id": "clear-faults", "name": "Clear faults (Faults - Clear)", "status": "sniff",
         "ref": "⚠️ only after repair; sniff separately from Read"},
    ]},
    {"id": "settings", "page": "settings", "cat": "Settings — ID/config (read)", "nanocom": "d2_airbag/settings",
     "items": [{"id": f"setting-{name.split('.')[0]}", "name": name, "status": "sniff", "ref": ref}
               for name, ref in _SETTINGS]},
    {"id": "outputs-none", "page": "outputs", "cat": "Outputs / Utility", "items": [
        {"id": "none-by-design", "name": "No output/utility page 🔴", "status": "sniff", "safety": "gated",
         "ref": "TRW SPS 2A has no output tests — never activate a firing circuit",
         "note": "None by design: airbag outputs are gated (pyrotechnics)."},
    ]},
]
