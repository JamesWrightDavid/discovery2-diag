"""BCU (Valeo body control unit) NanoCom menu — what exists; the catalog derives how far we are.

Data model: see :mod:`d2diag.td5.menu` (ADR-0008). Nothing here is mapped yet: the BCU
zero-masks its inputs until SecurityAccess (T-16), and every security function (EKA, key
programming) is gated by ADR-0007, so items are hand ``sniff`` (transcribed, not mapped)
and the security ones link only gated registry actions. Keep item ``name`` strings and
group titles stable: the admin Map tab keys saved readings on ``module|cat|name``.

Sources: ``references/menus/bcu-inputs.md``, ``bcu-settings.md`` and
``bcu-outputs-utilities.md`` (reference tool order, important for byte/bit mapping),
``references/valeo_bcu_capabilities.md`` and ``references/nanocom/td5_menu_tree.md``.
Sniff priority: EKA option, Market, Daytime run lights, immobiliser
(``references/bcu_sniff_plan.md``).
"""


def _slug(s: str) -> str:
    out = "".join(c if c.isalnum() else "-" for c in s.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def _sniff(prefix: str, rows: list, **extra) -> list:
    """Hand-``sniff`` items from ``(name, ref)`` rows; ids are ``<prefix>-<slug(name)>``."""
    return [{"id": f"{prefix}-{_slug(name)}", "name": name, "status": "sniff", "ref": ref, **extra}
            for name, ref in rows]


def _gated(prefix: str, rows: list) -> list:
    return _sniff(prefix, rows, safety="gated")


BCU_MENU = [
    # ---- Inputs (NanoCom "read inputs": body 1/2, instrument, power distribution) ----
    {"id": "inputs-lights", "page": "inputs", "cat": "DCU Read Inputs — LIGHTS",
     "nanocom": "valeo_bcu/read_inputs/body_1", "items": _sniff("in-lights", [
        ("Side lights", ""), ("Main beam", ""), ("Dipped", ""), ("Front fog light", ""),
        ("Rear fog light", ""), ("Left indicator", ""), ("Right indicator", ""), ("Hazard", ""),
        ("Daytime run light", "")])},
    {"id": "inputs-doors", "page": "inputs", "cat": "DCU Read Inputs — DOORS / BODY INPUTS",
     "nanocom": "valeo_bcu/read_inputs/body_1", "items": _sniff("in-doors", [
        ("Passenger door switch", ""), ("Driver door switch", ""), ("Bonnet", ""), ("Key lock", ""),
        ("Key unlock", ""), ("CDL Lock", ""), ("CDL unlock", ""),
        ("Inertia", "verify live vs latched vs polarity"), ("Ignition key inserted", ""),
        ("Transfer box neutral", "distinct from Transfer neutral switch"),
        ("Park/neutral", "distinct from Park neutral switch")])},
    {"id": "inputs-transmission", "page": "inputs", "cat": "DCU Read Inputs — TRANSMISSION",
     "nanocom": "valeo_bcu/read_inputs/body_2", "items": _sniff("in-trans", [
        ("Reverse idle", ""), ("Transfer neutral switch", ""), ("Autobox W switch", ""),
        ("Autobox X switch", ""), ("Autobox Y switch", ""), ("Autobox Z switch", ""),
        ("Park neutral switch", "")])},
    {"id": "inputs-windows", "page": "inputs", "cat": "DCU Read Inputs — WINDOWS",
     "nanocom": "valeo_bcu/read_inputs/body_2", "items": _sniff("in-windows", [
        ("Front LEFT down", ""), ("Front LEFT up", ""), ("Front RIGHT down", ""), ("Front RIGHT up", "")])},
    {"id": "inputs-wash-wipe", "page": "inputs", "cat": "DCU Read Inputs — WASH WIPE",
     "nanocom": "valeo_bcu/read_inputs/body_2", "items": _sniff("in-wash", [
        ("Front intermit", ""), ("Front wash", ""), ("Front wiper parked", ""),
        ("Front wiper speed", "numeric; likely multi-bit/byte"), ("Rear wiper", ""), ("Rear wash", "")])},
    {"id": "inputs-heated-engine", "page": "inputs", "cat": "DCU Read Inputs — HEATED SCREEN / ENGINE STATE",
     "nanocom": "valeo_bcu/read_inputs/body_2", "items": _sniff("in-heated", [
        ("Heated screen switch", ""), ("Ignition 2", ""), ("Engine speed signal", "")])},
    {"id": "inputs-instruments", "page": "inputs", "cat": "BCU Instruments — DISCRETE INPUTS / WARNING STATES",
     "nanocom": "valeo_bcu/read_inputs/instrument", "items": _sniff("in-instr", [
        ("LH DI", ""), ("RH DI", ""), ("LH Tailor DI", ""), ("RH Tailor DI", ""), ("Seat belt", ""),
        ("Diff lock", ""), ("Transfer neutral", ""), ("Autobox manual", ""), ("Autobox sport", ""),
        ("Offroad level", ""), ("ABS", "warning lamp, not switch"), ("Traction control", ""),
        ("SRS", "warning lamp"), ("HDC select", ""), ("Glow plug", ""), ("Brake", ""),
        ("Oil pressure", ""), ("Alternator", ""), ("Check engine", "warning lamp"), ("Fuel filter", ""),
        ("Transmission temp.", ""), ("Check ACE", "warning lamp"), ("Check HDC", "warning lamp"),
        ("Check SLS", "warning lamp")])},
    {"id": "inputs-mileage", "page": "inputs", "cat": "BCU Instruments — MILEAGE / TRIP",
     "nanocom": "valeo_bcu/read_inputs/instrument", "items": _sniff("in-mileage", [
        ("Instr. milage (km)", "instr-pack odometer reading; byte order/scale"),
        ("BCU milage (km)", "BCU-stored odometer reading; byte order/scale"), ("IP trip switch", "")])},
    {"id": "inputs-power", "page": "inputs", "cat": "BCU Power distribution — IGNITION / SUPPLY",
     "nanocom": "valeo_bcu/read_inputs/power_distibution", "items": _sniff("in-power", [
        ("BCU ignition pos. 1", "bitfield candidate (pos 1/2/3)"),
        ("BCU ignition pos. 2", "bitfield candidate (pos 1/2/3)"),
        ("BCU ignition pos. 3", "bitfield candidate (pos 1/2/3)"),
        ("IP ignition pos. 2", "instrument-pack report"), ("IDM ignition pos. 2", "IDM report"),
        ("IDM battery (V)", "voltage; scale TBD"), ("BCU switch power", "voltage; scale TBD"),
        ("BCU relay power", "voltage; scale TBD")])},
    # ---- Settings ----
    {"id": "settings-info", "page": "settings", "cat": "BCU INFO", "nanocom": "valeo_bcu/settings/info",
     "items": _sniff("info", [
        ("Serial No", "screenshot '0'"), ("Date", "screenshot '11/02/02'"),
        ("Hardware No", "screenshot '1.01'"), ("Software No", "screenshot '8.02'"),
        ("Alarm Type", "screenshot '10'"), ("VIN", "shown as 'SAL' + 14 characters; read only")])},
    {"id": "settings-lws", "page": "settings", "cat": "BCU Settings — LIGHTS-WINDOWS-SEATS",
     "nanocom": "valeo_bcu/settings/lights_win_seat", "items": _sniff("set-lws", [
        ("Front fog lamp", ""), ("Daytime run lights", "★ enum NONE/NO MAIN/NO HEADS"),
        ("Courtest head lamps", ""), ("Headlamp power wash", ""), ("Electric window front", ""),
        ("Rear windows sunroof", ""), ("Heated front screen", ""), ("Electric front seats", ""),
        ("Programmed wash wip", "enum, not boolean"), ("Seat belt warning", "enum (TIMED/…)"),
        ("Seat belt warning soun", ""), ("Autographics", "")])},
    {"id": "settings-tlw", "page": "settings", "cat": "BCU Settings — TRANSM-LOCK-WARN",
     "nanocom": "valeo_bcu/settings/transm_lock_warn", "items": _sniff("set-tlw", [
        ("Transmission", "enum (AUTO/…)"), ("Shift Interlock", ""), ("HDC", ""), ("Superlock", ""),
        ("Single point entry", ""), ("Speed lock option", ""), ("Mislock option", ""),
        ("Bathrobe lock option", ""), ("Odometer error warn", ""), ("Key warning", ""),
        ("Low battery warning", ""), ("Bulb failure", "")])},
    {"id": "settings-instrument-pack", "page": "settings", "cat": "BCU Settings — INSTRUMENT PACK",
     "nanocom": "valeo_bcu/settings/instrument_pack", "items": _sniff("set-ip", [
        ("Transmission", "vehicle config"), ("Engine", "enum (PETROL/…)"), ("ACE", "feature flag"),
        ("SLS", "feature flag"), ("Gulf", "feature flag"), ("Police", "feature flag"),
        ("HDC", "feature flag"), ("TRC", "feature flag")])},
    {"id": "settings-alarm-other", "page": "settings", "cat": "BCU Settings — ALARM-OTHER",
     "nanocom": "valeo_bcu/settings/alarm_other", "items": [
        *_sniff("set-alarm", [
            ("Alarm", ""), ("Alarm option", ""), ("Alarm disarm", "enum field"),
            ("Alarm sounder", "enum field"), ("Alarm tamper", ""), ("Engine immobil.", "★ enum (LED OFF/…)"),
            ("Passive immobil.", "★ en/dis"), ("Inertia switch", "enum (NO HAZARD/…)"),
            ("Hazard option", "enum field"), ("Volumetric sensor", ""),
            ("Market", "★ enum; market code not mapped (controls DRL etc.)"),
            ("EKA option", "★ en/dis; linked to the EKA code utility")]),
        {"id": "set-alarm-settings-ids", "name": "BCU settings IDs", "status": "candidate",
         "ref": "auto-extracted: 21 C6/C7/CA/CB/D3/D4-D7/EB (match against settings groups)"},
        *_sniff("set-alarm", [
            ("Cruise control", ""), ("Air conditioning", ""), ("Fuel burning heater", ""),
            ("Passive coil", ""), ("Transit mode", "")]),
    ]},
    {"id": "settings-write", "page": "settings", "cat": "BCU Settings — WRITE",
     "nanocom": "valeo_bcu/settings/write_settings", "items": _gated("set-write", [
        ("Write settings", "writes the BCU coding — never sent by this project")])},
    # ---- Outputs ----
    {"id": "outputs-body", "page": "outputs", "cat": "BCU Outputs — BODY", "nanocom": "valeo_bcu/outputs_body",
     "items": _sniff("out-body", [
        ("Front fog lights", ""), ("Rear fog lights", ""), ("Daytime running lights", ""),
        ("LH indicator enable", "seq 4; UI shows the label twice"),
        ("LH indicator enable (2)", "seq 5; may turn out to be RH"), ("Front left window up", ""),
        ("Front left window down", ""), ("Front right window up", ""),
        ("Front right window down", "UI-truncated label"), ("Rear windows enable", ""),
        ("Sunroof enable", ""), ("Front wiper enable", ""), ("Tail wiper enable", ""),
        ("Head lamp power wash", ""), ("Heated screen", ""), ("Heat. rear screen lamp", ""),
        ("Check engine lamp", "")])},
    # Immobiliser/alarm/locking outputs: forbidden (references/nanocom/feature_map.md).
    {"id": "outputs-security", "page": "outputs", "cat": "BCU Outputs — SECURITY/LOCKING",
     "nanocom": "valeo_bcu/outputs_security", "items": _gated("out-sec", [
        ("Horn", ""), ("BBUS ALL", ""), ("BBUS ST", ""), ("Fuel flap", ""), ("Alarm LED", ""),
        ("Ignition interlock", ""), ("Crank Enable", ""), ("Volumetric power", ""), ("Robust immo.", ""),
        ("Transponder Power", ""), ("Lock", ""), ("Unlock", ""), ("Superlock", ""),
        ("Single point entry", "")])},
    # ---- Utilities (all gated, ADR-0007) ----
    {"id": "utilities-eka", "page": "utilities", "cat": "BCU Utilities — EKA CODE", "nanocom": "valeo_bcu/utility",
     "items": [
        {"id": "eka-read", "name": "EKA code — READ", "actions": ["eka_read"],
         "ref": "21 CC behind SecurityAccess; without it the BCU returns the seed"},
        {"id": "eka-set", "name": "EKA code — SET", "actions": ["eka_set"], "ref": "3B CC <4B> — never sent"},
    ]},
    {"id": "utilities-keys", "page": "utilities", "cat": "BCU Utilities — KEY PROGRAMMING",
     "nanocom": "valeo_bcu/key_programming", "items": []},
    {"id": "utilities-key-codes", "page": "utilities", "parent": "utilities-keys", "cat": "Key codes / UPDATE",
     "nanocom": "valeo_bcu/key_programming", "items": [
        *_gated("key-code", [("Key Code 1", "SET"), ("Key Code 2", "SET"), ("Key Code 3", "SET"),
                             ("Key Code 4", "SET"), ("Susp", "SET")]),
        {"id": "key-code-update", "name": "UPDATE", "actions": ["key_program"], "ref": "never sent"},
    ]},
    {"id": "utilities-key-detect", "page": "utilities", "parent": "utilities-keys",
     "cat": "Key detection / synchronisation", "nanocom": "valeo_bcu/key_programming",
     "items": _gated("key-detect", [("Key 1", "SYNC"), ("Key 2", "SYNC"), ("Key 3", "SYNC"), ("Key 4", "SYNC"),
                                    ("SUSP", "SYNC"), ("KEY DETECT", "global key-detection button")])},
    {"id": "utilities-plip", "page": "utilities", "parent": "utilities-keys", "cat": "Suspension plip BAR CODE",
     "nanocom": "valeo_bcu/key_programming",
     "items": _gated("plip", [("BAR CODE", "screenshot value; verify against a capture"),
                              ("SET CODE 1", "button"), ("UPDATE", "")])},
]
