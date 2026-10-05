"""TD5 (Lucas engine ECU) NanoCom menu — what exists; the catalog derives how far we are.

Data model (ADR-0008, specs/2026-10-05-ui-overhaul-design.md): each group has an ``id``,
a ``page`` (session | faults | inputs | outputs | settings | utilities), a display ``cat``
and the NanoCom emulator path ``nanocom``. Each item has a unique slug ``id`` and links
either a signal-store field (``sig``, plus ``at="LID@offset"`` where length variants share
a name) or registry actions (``actions``, see :mod:`openostler.commands`). Only unlinked items
carry a hand ``status`` (verified | candidate | sniff | untranscribed). Status is derived
in :mod:`openostler.catalog`, never copied here. Keep item ``name`` strings stable: the admin
Map tab keys saved readings on them.

Source: ``references/menus/td5.md`` (the reference tool .docx transcription, exact UI
order) and ``references/nanocom/td5_menu_tree.md``. Display values in the .docx (ABNFE,
svtnp006, ENABLED/DISABLED, ROBUST …) are the transcription's screenshot baseline, NOT
read off a car.
"""

_FEATURE_FLAGS = [
    "Temperature Gauge", "Tachometer", "SLABS", "Road Speed", "Radiator Fan", "MIL Lamp",
    "Fuel Used", "Fuel Temperature", "EGR Modulator", "EGR Inlet", "Cruise Lamp",
    "Cruise Control", "Clutch Switch", "CAN Bus", "Auxiliary Fan", "Auto Gearbox",
    "Air Conditioning", "Active Engine mount", "Ambient Sensor", "Wastegate Modulator",
]


def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-").replace("--", "-")


TD5_MENU = [
    {"id": "session", "page": "session", "cat": "Connection (requires unlock)", "items": [
        {"id": "fast-init", "name": "Fast init (StartCommunication)", "status": "verified",
         "ref": "tolerant, searches for C1"},
        {"id": "start-session", "name": "StartDiagnosticSession", "status": "verified", "ref": "0xA0"},
        {"id": "security-access", "name": "SecurityAccess (seed→key)", "status": "verified",
         "ref": "keygen; Ekaitza-confirmed"},
    ]},
    {"id": "faults", "page": "faults", "cat": "Fault codes", "nanocom": "td5_engine/faults", "items": [
        {"id": "read-faults", "name": "Read faults (211 bits raw-mapped, 3 candidate)", "status": "verified",
         "ref": "21 3B, byte*8+bit; PROVEN Ekaitza + reference tool v1.12"},
        {"id": "clear-faults", "name": "Clear faults", "status": "verified", "ref": "StartRoutine 0xDD + 18×00"},
        {"id": "fault-reference", "name": "Reference (display codes + causes)", "status": "verified",
         "ref": "the dictionary TD5 + Kelvin list"},
    ]},
    {"id": "inputs-fuelling", "page": "inputs", "cat": "Inputs — Fuelling / live (22)",
     "nanocom": "td5_engine/inputs_fuelling", "items": [
        {"id": "engine-speed", "name": "1. Engine Speed (rpm)", "ref": "21 09", "lid": "09", "sig": "rpm"},
        {"id": "idle-speed-error", "name": "2. Idle Speed Error (rpm)", "ref": "21 21 (s16)", "lid": "21",
         "sig": "rpm_error"},
        {"id": "road-speed", "name": "3. Road Speed (km/h)", "ref": "21 0D", "lid": "0d", "sig": "speed"},
        {"id": "battery", "name": "4. Battery (V)", "ref": "21 10 (u16/1000)", "lid": "10", "sig": "battery"},
        {"id": "accel-way-1", "name": "5. Accel. Way 1 (V)", "ref": "21 1B@0", "lid": "1b", "sig": "accel_way1"},
        {"id": "accel-way-2", "name": "6. Accel. Way 2 (V)", "ref": "21 1B@2", "lid": "1b", "sig": "accel_way2"},
        {"id": "accel-way-3", "name": "7. Accel. Way 3 (V)", "ref": "21 1B@4 (long 10-byte form; Euro 3)",
         "lid": "1b", "sig": "accel_way3"},
        {"id": "accel-supply", "name": "8. Accel. Supply (V)",
         "ref": "21 1B@8 long form (D2-JW); @6 in the short 8-byte form", "lid": "1b",
         "sig": "accel_supply", "at": "1B@8"},
        {"id": "coolant-temp", "name": "9. Coolant Temp (°C)", "ref": "21 1A@0", "lid": "1a", "sig": "coolant_temp"},
        {"id": "fuel-temp", "name": "10. Fuel Temp (°C)", "ref": "21 1A@12", "lid": "1a", "sig": "fuel_temp"},
        {"id": "air-inlet-temp", "name": "11. Air Inlet Temp (°C)", "ref": "21 1A@4", "lid": "1a", "sig": "air_temp"},
        {"id": "air-flow", "name": "12. Air Flow (kg/hr)", "ref": "21 1C@4 ×0.1 kg/h (physical MAF sensor)",
         "lid": "1c", "sig": "maf_sensor", "at": "1C@4"},
        {"id": "ambient-pressure", "name": "13. Ambient Pressure (kPa)", "ref": "21 23@0", "lid": "23",
         "sig": "ambient_press_1"},
        {"id": "manifold-pressure", "name": "14. Manifold Turbo Pressure (kPa)", "ref": "21 1C@0",
         "lid": "1c", "sig": "manifold_press"},
        {"id": "egr-modulator", "name": "15. EGR Modulator (%)", "ref": "21 1D@15 u8 (native 21 37 is the alternative, T-02)",
         "lid": "1d", "sig": "egr_modulator"},
        {"id": "egr-inlet", "name": "16. EGR Inlet (%)", "ref": "21 45@0 ×0.01 % (1D@16 was a dead byte)",
         "lid": "45", "sig": "egr_inlet"},
        {"id": "wastegate-modulator", "name": "17. Wastegate Modulator (%)",
         "ref": "21 1D@17 u8 (native 21 38 is the alternative, T-02)", "lid": "1d", "sig": "wastegate_modulator"},
        {"id": "cylinder-1", "name": "18. Cylinder 1 (balance)", "ref": "21 40@0 (s16)", "lid": "40", "sig": "balance_1"},
        {"id": "cylinder-2", "name": "19. Cylinder 2 (balance)", "ref": "21 40@2", "lid": "40", "sig": "balance_2"},
        {"id": "cylinder-3", "name": "20. Cylinder 3 (balance)", "ref": "21 40@4", "lid": "40", "sig": "balance_3"},
        {"id": "cylinder-4", "name": "21. Cylinder 4 (balance)", "ref": "21 40@6", "lid": "40", "sig": "balance_4"},
        {"id": "cylinder-5", "name": "22. Cylinder 5 (balance)", "ref": "21 40@8", "lid": "40", "sig": "balance_5"},
    ]},
    {"id": "inputs-switches", "page": "inputs", "cat": "Inputs — switches (12)",
     "nanocom": "td5_engine/inputs_switch", "items": [
        {"id": "brake-switch-1", "name": "1. Brake Switch 1", "ref": "21 1E byte1 bit7 (active-low)",
         "lid": "1e", "sig": "brake_main", "note": "Main brake switch; Brake 1 ↔ main is by inference."},
        {"id": "brake-switch-2", "name": "2. Brake Switch 2", "ref": "21 1E byte0 bit0 (complementary to Brake 1)",
         "lid": "1e", "sig": "brake_switch_2"},
        {"id": "clutch-switch", "name": "3. Clutch Switch", "status": "sniff",
         "ref": "SR-App hint: 21 1E@0 bit1 (not stored)", "lid": "1e"},
        {"id": "transfer-ratio", "name": "4. Transfer Ratio (HIGH/LOW)", "status": "sniff",
         "ref": "SR-App hint: 21 1E@1 bit6 (not stored)", "lid": "1e"},
        {"id": "gear-box", "name": "5. Gear Box (P/N…)", "status": "sniff", "ref": "", "lid": "1e 36"},
        {"id": "cruise-control", "name": "6. Cruise Control", "ref": "21 1E byte0 bit2 (master)", "lid": "1e",
         "sig": "cruise_master"},
        {"id": "cruise-resume", "name": "7. Cruise Resume", "ref": "21 1E byte0 bit4", "lid": "1e",
         "sig": "cruise_resume"},
        {"id": "set-accelerate", "name": "8. Set Accelerate", "ref": "21 1E byte0 bit3 (SET)", "lid": "1e",
         "sig": "cruise_set"},
        {"id": "ac-clutch-request", "name": "9. AC Clutch Request", "status": "sniff",
         "ref": "SR-App hint: 21 1E@1 bit3 (not stored)", "lid": "1e"},
        {"id": "ac-clutch-drive", "name": "10. AC Clutch Drive", "status": "sniff",
         "ref": "SR-App hint: 21 36 relay block (not stored)", "lid": "36"},
        {"id": "ac-fan-request", "name": "11. AC Fan Request", "status": "sniff", "ref": "", "lid": "1e 36"},
        {"id": "ac-fan-drive", "name": "12. AC Fan Drive", "status": "sniff", "ref": "", "lid": "1e 36"},
    ]},
    # Fields this project decodes that the NanoCom does not show (store signals; sources in the store).
    {"id": "inputs-extra", "page": "inputs", "cat": "Inputs — extra live data (not on the NanoCom)", "items": [
        {"id": "accel-pedal-pct", "name": "Accelerator pedal (%)", "ref": "21 1B@6 ×0.01 % (long form); @4 short form",
         "lid": "1b", "sig": "accel_pedal_pct", "at": "1B@6"},
        {"id": "air-mass-modelled", "name": "Air mass (modelled)", "ref": "21 1D@4 — likely the ECU's model, T-01",
         "lid": "1d", "sig": "maf"},
        {"id": "maf-sensor-v", "name": "Air flow sensor voltage (V)", "ref": "21 1C@6", "lid": "1c",
         "sig": "maf_sensor_v"},
        {"id": "coolant-sensor-v", "name": "Coolant sensor voltage (V)", "ref": "21 1A@2", "lid": "1a",
         "sig": "coolant_sensor_v"},
        {"id": "intake-sensor-v", "name": "Intake air sensor voltage (V)", "ref": "21 1A@6", "lid": "1a",
         "sig": "intake_sensor_v"},
        {"id": "fuel-sensor-v", "name": "Fuel temp sensor voltage (V)", "ref": "21 1A@14", "lid": "1a",
         "sig": "fuel_sensor_v"},
        {"id": "ambient-pressure-2", "name": "Ambient pressure 2 (kPa)", "ref": "21 23@2", "lid": "23",
         "sig": "ambient_press_2"},
        {"id": "battery-direct", "name": "Battery direct (V)", "ref": "21 10@2", "lid": "10", "sig": "battery_direct"},
        {"id": "injection-qty", "name": "Injection quantity", "ref": "21 1D@6", "lid": "1d", "sig": "injection_qty"},
        {"id": "driver-demand", "name": "Driver demand", "ref": "21 1D@0 (T-03)", "lid": "1d", "sig": "driver_demand"},
        {"id": "smoke-limit", "name": "Smoke limit", "ref": "21 1D@10", "lid": "1d", "sig": "smoke_limit"},
        {"id": "torque-limit", "name": "Torque limit", "ref": "21 1D@12", "lid": "1d", "sig": "torque_limit"},
        {"id": "egr-pos-native", "name": "EGR modulator (native 0x37, %)", "ref": "21 37@0 (T-02)", "lid": "37",
         "sig": "egr_pos"},
        {"id": "wastegate-pos-native", "name": "Wastegate modulator (native 0x38, %)", "ref": "21 38@0 (T-02)",
         "lid": "38", "sig": "wastegate_pos"},
        {"id": "fuel-pump-relay", "name": "Fuel pump relay", "ref": "21 36 byte1 bit2", "lid": "36",
         "sig": "fuel_pump_relay"},
    ]},
    {"id": "settings-injectors", "page": "settings", "cat": "Settings — injector codes (6)",
     "nanocom": "td5_engine/settings/injectors", "items": [
        {"id": "injector-codes", "name": "Injector 1–5 (5-character code)", "status": "sniff",
         "ref": "docx baseline 'ABNFE' (not RDL 016)"},
        {"id": "injector-type", "name": "INJ. TYPE (read/identify)", "status": "sniff",
         "ref": "UI action, separate from the code fields"},
    ]},
    {"id": "settings-identity", "page": "settings", "cat": "Settings — read-only ID (5)",
     "nanocom": "td5_engine/settings/info", "items": [
        {"id": "config-tune-id", "name": "Config Tune ID", "status": "sniff",
         "ref": "docx: 'svtnp006'; not in the 1A 87/9A/9B/9C blocks"},
        {"id": "fuel-tune-id", "name": "Fuel Tune ID", "status": "sniff",
         "ref": "docx: 'svdhg003'; not in the 1A blocks"},
        {"id": "ecu-part-number", "name": "ECU Part Number", "actions": ["read_identity"],
         "ref": "1A 9A: 'NNN' + BCD (D2-JW NNN000130); 1A 87 adds VIN, date, NNW software no.",
         "note": "Read ECU identity reads all 1A blocks; the VIN is masked and never logged."},
        {"id": "homologation", "name": "Homologation", "status": "sniff", "ref": "docx: '4213'; not in the 1A blocks"},
        {"id": "get-vin", "name": "GET VIN", "status": "sniff",
         "ref": "1A 87@0-10 ASCII (first 11 VIN chars) + BCD serial; returned masked by Read ECU identity"},
    ]},
    {"id": "settings-features", "page": "settings", "cat": "Settings — feature/config (21)",
     "nanocom": "td5_engine/settings/info", "items": [
        *[{"id": f"feature-{_slug(f)}", "name": f, "status": "sniff", "ref": "ENABLED/DISABLED flag"}
          for f in _FEATURE_FLAGS],
        {"id": "feature-ecu-status", "name": "ECU Status", "status": "sniff", "ref": "enum, docx baseline 'ROBUST'"},
    ]},
    {"id": "outputs-tests", "page": "outputs", "cat": "Outputs — tests ⚠️ (14)",
     "nanocom": "td5_engine/outputs", "items": [
        {"id": "ac-clutch", "name": "1. A/C Clutch (pulse)", "actions": ["output_ac_clutch"], "ref": "30 A3 FF"},
        {"id": "ac-fan", "name": "2. A/C Fan (pulse)", "actions": ["output_ac_fan"], "ref": "30 A4 FF"},
        {"id": "mil-lamp", "name": "3. MIL Lamp (pulse)", "actions": ["output_mil_lamp"], "ref": "30 A2 FF"},
        {"id": "fuel-pump", "name": "4. Fuel Pump (pulse)", "actions": ["output_fuel_pump"], "ref": "30 A1 FF"},
        {"id": "glow-plugs", "name": "5. Glow Plugs (pulse)", "actions": ["output_glow_plugs"], "ref": "30 B3 FF"},
        {"id": "rev-counter", "name": "6. Pulse Rev Counter", "actions": ["output_rev_counter"],
         "ref": "30 B7 FF (tacho needle)"},
        {"id": "wastegate-test", "name": "7. Wastegate Modul. (pulse)", "actions": ["output_wastegate"],
         "ref": "30 BE FF 00 0A 13 88 (PWM)"},
        {"id": "temp-gauge", "name": "8. Temp Gauge (pulse)", "actions": ["output_temp_gauge"], "ref": "30 BA FF"},
        {"id": "egr-throttle", "name": "9. EGR Throttle (pulse)", "actions": ["output_egr_throttle"],
         "ref": "30 BD FF 00 FA 13 88 (PWM)"},
        *[{"id": f"injector-{n}", "name": f"{9 + n}. Injector {n} (single pulse)", "actions": [f"injector_{n}"],
           "ref": f"31 C2 0{n}"} for n in range(1, 6)],
    ]},
    {"id": "utilities-security", "page": "utilities", "cat": "Utilities — security ⚠️ (2)",
     "nanocom": "td5_engine/utility", "items": [
        {"id": "security-status", "name": "GET SECURITY STATUS", "actions": ["security_status"],
         "ref": "31 C0 + 33 C0 → 03 = not immobilised (read-only)"},
        {"id": "learn-security-code", "name": "LEARN SECURITY CODE", "actions": ["learn_security_code"],
         "ref": "🔴 can change immobiliser state — never sent"},
    ]},
]
