"""Seed the fault-meaning store (src/d2diag/dtc/*.json) from the canonical fault data.

One-shot, **merge-preserving** seeder: it fills meanings that don't exist yet and leaves
any hand-refined entry alone (use ``--force`` to regenerate from scratch). Run it when the
decoders gain new fault bits.

    PYTHONPATH=src python3 tools/gen_dtc_seed.py          # add missing, keep edits
    PYTHONPATH=src python3 tools/gen_dtc_seed.py --force  # regenerate everything
    PYTHONPATH=src python3 tools/gen_dtc_seed.py --check   # CI: fail if anything is missing

Sources:
- **td5** — the 210 named bits in ``d2diag.td5.faults.FAULTS`` (key ``offset.bit``), with
  description/cause/severity/system templated from the name grammar, and OBD-II P-codes
  folded in from SimonRafferty/Td5-Diagnostic-App ``td5_dtc_table.h`` (same ``{byte,bit}``
  indexing; see references/td5-cross-reference.md). The Td5 is not OBD2, so a P-code is an
  *inferred* cross-reference, not a code the ECU emits.
- **slabs** — the numbered list in ``references/slabs_fault_codes.md`` (rswsolutions).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from d2diag import dtc  # noqa: E402
from d2diag.td5.faults import FAULTS  # noqa: E402

_ROOT = Path(__file__).resolve().parents[1]

# OBD-II P-codes per td5 "offset.bit", from SimonRafferty/Td5-Diagnostic-App td5_dtc_table.h
# (X,Y 1-based there → offset=X-1, bit=Y-1). Injectors handled by rule below.
_TD5_PCODES = {
    "0.0": "P0403", "0.1": "P0243", "0.2": "P0409", "0.4": "P0121", "0.5": "P0221",
    "0.6": "P0100", "0.7": "P0105",
    "1.0": "P0110", "1.1": "P0180", "1.2": "P0115", "1.3": "P0560", "1.4": "P0641",
    "1.5": "P0070", "1.6": "P0641", "1.7": "P2227",
    "2.0": "P0403", "2.1": "P0243", "2.2": "P0409", "2.4": "P0121", "2.5": "P0221",
    "2.6": "P0100", "2.7": "P0105",
    "3.0": "P0110", "3.1": "P0180", "3.2": "P0115", "3.3": "P0560", "3.4": "P0641",
    "3.5": "P0070", "3.6": "P0641", "3.7": "P2227",
    "4.0": "P0403", "4.1": "P0243", "4.2": "P0409", "4.4": "P0121", "4.5": "P0221",
    "4.6": "P0100", "4.7": "P0105",
    "5.0": "P0110", "5.1": "P0180", "5.2": "P0115", "5.3": "P0560", "5.4": "P0641",
    "5.6": "P0641", "5.7": "P2227",
    "6.2": "P0480", "6.4": "P0245", "6.5": "P0405", "6.6": "P0409",
    "7.1": "P0230", "7.6": "P0380", "7.7": "P0380",
    "8.2": "P0480", "8.4": "P0244", "8.5": "P0404", "8.6": "P0409",
    "9.1": "P0230", "9.6": "P0380", "9.7": "P0380",
    "10.2": "P0480", "10.4": "P0245", "10.5": "P0405", "10.6": "P0409",
    "11.1": "P0230", "11.6": "P0380", "11.7": "P0380",
    "12.2": "P0480", "12.4": "P0245", "12.5": "P0405", "12.6": "P0409",
    "13.1": "P0230", "13.6": "P0380", "13.7": "P0380",
    "14.1": "P0335", "15.1": "P0335", "16.1": "P0335",
    "18.1": "U0001", "18.2": "U0001", "18.5": "P0335", "18.7": "U0001",
    "19.0": "P0299", "19.1": "P0234", "19.3": "P0402", "19.4": "P0401",
    "20.3": "P0121", "20.4": "P0221", "20.5": "P0120", "20.6": "P2135", "20.7": "P1633",
    "21.0": "P0500",
    "22.0": "U0001", "22.1": "U0001", "22.2": "U0001", "22.3": "U0001", "22.4": "P0299",
    "22.5": "P0335",
    "23.0": "P0299", "23.1": "P0234", "23.2": "P0234", "23.3": "P0402", "23.4": "P0401",
    "23.6": "P0700",
    "24.3": "P0121", "24.4": "P0221", "24.5": "P0120", "24.6": "P2135", "24.7": "P1633",
    "25.0": "P0500",
}
_INJECTOR_OFFSETS = {26, 27, 28, 29, 30, 31, 32, 33, 34}  # bit 0..5 → cylinders 1..6


def _bit_of(mask: int) -> int:
    return mask.bit_length() - 1


def _pcode(off: int, bit: int) -> str:
    if off in _INJECTOR_OFFSETS and bit <= 5:
        return f"P020{bit + 1}"
    return _TD5_PCODES.get(f"{off}.{bit}", "")


def _system(name: str) -> str:
    n = name.lower()
    pairs = [
        (("egr", "turbo", "wastegate", "boost", "manifold", "air flow", "inlet air",
          "ambient"), "engine air & boost"),
        (("inj.", "injector", "fuel", "driver demand", "injection", "smoke", "torque"),
         "fuelling"),
        (("coolant", "temperature gauge", "temp. gauge", "radiator fan"), "cooling"),
        (("battery", "reference voltage", "glow", "mil"), "electrical"),
        (("can ", "can has", "can rx", "can tx", "remote can"), "comms (CAN)"),
        (("cruise",), "cruise control"),
        (("road speed", "crank", "noisy crank"), "engine sensors"),
        (("gear box", "gearbox", "abs"), "drivetrain"),
    ]
    for keys, system in pairs:
        if any(k in n for k in keys):
            return system
    return "engine"


def _describe_td5(name: str) -> "tuple[str, str, str]":
    """→ (description, cause, severity) templated from a Td5 fault name."""
    sev, base = "", name
    for suffix, s in (("(Current)", "current"), ("(Logged Low)", "logged (low/short)"),
                      ("(Logged High)", "logged (high/open)"), ("(Logged)", "logged")):
        if name.endswith(suffix):
            sev, base = s, name[: -len(suffix)].strip()
            break
    pretty = base[:1].upper() + base[1:]
    low = base.lower()

    if "diagnostics" in low:
        comp = pretty.replace(" diagnostics", "")
        hint = "short/low-side" if "low" in sev else "open/high-side" if "high" in sev else ""
        tail = f" ({hint} fault logged)" if hint else ""
        return (f"{comp}: actuator/feedback diagnostic fault{tail}.",
                f"Check the {comp.lower()} actuator, its vacuum/feedback and the wiring.", sev)
    if "circuit" in low and "short circuit" not in low and "open circuit" not in low:
        if "low" in sev:
            return (f"{pretty}: sensor-circuit fault, signal low.",
                    "Short to ground or low supply — check the sensor, wiring and connector.",
                    sev)
        if "high" in sev:
            return (f"{pretty}: sensor-circuit fault, signal high.",
                    "Open circuit or break — check the sensor, wiring and connector.", sev)
        return (f"{pretty}: sensor-circuit fault.",
                "Check the sensor, its wiring and connector.", sev)
    if "open load" in low:
        return (f"{pretty.replace(' open load', '')}: output driver sees no load (open).",
                "Open circuit — check the actuator and its wiring/connector.", sev)
    if "over temp" in low or "over temperature" in low:
        base2 = re.sub(r" over tempe?r?a?t?u?r?e?\.?$", "", pretty, flags=re.I)
        return (f"{base2}: output driver stage over-temperature (overload protection).",
                "Driver overloaded — check the circuit for a short or excessive current.", sev)
    if "partial short circuit" in low:
        return (f"{pretty}: injector partial short circuit.",
                "Check the injector and its harness; compare cylinder balance.", sev)
    if "short circuit" in low:
        return (f"{pretty}.", "Short in the actuator/injector or its harness — check wiring.",
                sev)
    if "open circuit" in low:
        return (f"{pretty}.", "Open circuit — check the actuator/injector and its wiring.", sev)
    if "peak charge" in low:
        return (f"{pretty}: injector peak-charge timing out of range.",
                "Suspect injector or harness — check resistance/connector, compare balance.",
                sev)
    if "boost" in low:
        return (f"{pretty}.",
                "Boost-control fault — check the turbo, wastegate modulator, hoses and MAP.",
                sev)
    if "egr valve stuck" in low:
        return (f"{pretty}.", "EGR valve/modulator stuck — check the valve, vacuum and soot.",
                sev)
    if "driver demand" in low:
        return (f"{pretty}.",
                "Accelerator pedal sensor — check the pedal tracks, supply and wiring.", sev)
    if low.startswith("can ") or "can " in low:
        return (f"{pretty}.", "CAN bus communication fault — check the bus wiring and the "
                "modules on it (SLABS/gearbox).", sev)
    if "cruise" in low:
        return (f"{pretty}.", "Cruise-control input/switch fault — check the stalk and brake/"
                "clutch switches.", sev)
    if "road speed" in low:
        return (f"{pretty}.", "Road-speed signal missing — check the source (SLABS/instruments).",
                sev)
    if "crank" in low:
        return (f"{pretty}.", "Crankshaft sensor signal issue — check the sensor and reluctor.",
                sev)
    if "injector trim" in low:
        return (f"{pretty}: stored injector classification codes are corrupt.",
                "Re-enter the injector codes with a capable tool.", sev)
    if "auto gear box" in low or "gear box" in low:
        return (f"{pretty}.", "Fault reported for the automatic gearbox — read the EAT module.",
                sev)
    return (f"{pretty}.", "See the workshop manual fault-finding for this circuit.", sev)


def build_td5() -> "list[dict]":
    out = []
    for f in FAULTS:
        bit = _bit_of(f.mask)
        key = f"{f.offset}.{bit}"
        desc, cause, sev = _describe_td5(f.name)
        rec = {"key": key, "name": f.name, "description": desc, "cause": cause,
               "severity": sev, "system": _system(f.name),
               "source": "td5/faults.py (Ekaitza + ref tool v1.12); templated meaning; "
                         "P-code ex SimonRafferty/Td5-Diagnostic-App"}
        pc = _pcode(f.offset, bit)
        if pc:
            rec["pcode"] = pc
        out.append({k: v for k, v in rec.items() if v != ""})
    return out


_SLABS_CAUSE = [
    ("open circuit", "Open circuit — check the component and its wiring/connector."),
    ("drive short to supply", "Driver short to +12V — suspect the ECU driver or a harness "
                              "short to supply."),
    ("short to supply", "Short to +12V — check the wiring for a short to supply."),
    ("short to gnd", "Short to ground — check the wiring for a short to chassis."),
    ("output low", "Wheel-speed signal low — check the sensor air gap, reluctor ring and wiring."),
    ("electric fail", "Wheel-speed sensor electrical failure — check the sensor and wiring."),
    ("bad output", "Wheel-speed signal implausible — check the sensor, reluctor ring and gap."),
    ("not running when on", "Pump commanded on but not running — check the pump, relay and supply."),
    ("running when not on", "Pump running when off — check the relay and pump drive."),
    ("sticking", "Mechanical sticking — inspect the valve/pump."),
    ("monitor line", "Pump monitor line fault — check the monitor wiring."),
    ("relay bad", "Internal valve relay fault — ECU suspect."),
]


def build_slabs() -> "list[dict]":
    text = (_ROOT / "references" / "slabs_fault_codes.md").read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^\|\s*(\d{3})\s*\|\s*(.+?)\s*\|\s*$", text, flags=re.M):
        code, name = m.group(1), m.group(2).strip()
        low = name.lower()
        cause = "See the workshop manual fault-finding for this circuit."
        for key, c in _SLABS_CAUSE:
            if key in low:
                cause = c
                break
        out.append({"key": code, "name": name,
                    "description": f"{name} (SLABS ABS/SLS fault {code}).",
                    "cause": cause, "system": "brakes & suspension (SLABS)",
                    "source": "references/slabs_fault_codes.md (rswsolutions)"})
    return out


_BUILDERS = {"td5": build_td5, "slabs": build_slabs}


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed the DTC meaning store")
    ap.add_argument("--force", action="store_true", help="overwrite existing entries")
    ap.add_argument("--check", action="store_true", help="CI: non-zero if any entry is missing")
    args = ap.parse_args()

    problems = 0
    for module, build in _BUILDERS.items():
        built = build()
        existing = {r["key"] for r in dtc.load_records(module)}
        missing = [r["key"] for r in built if r["key"] not in existing]
        if args.check:
            if missing:
                problems += len(missing)
                print(f"{module}: {len(missing)} fault meaning(s) missing from the store")
            continue
        rows = built if args.force else _merged_rows(module, built)
        _write(module, rows)
        print(f"{module}: wrote {len(rows)} meanings ({len(missing)} new)")
    if args.check:
        print("OK — DTC store covers every decoder fault." if not problems
              else f"\n{problems} missing meaning(s): run tools/gen_dtc_seed.py")
        return 1 if problems else 0
    return 0


def _merged_rows(module: str, built: "list[dict]") -> "list[dict]":
    existing = {r["key"]: r for r in dtc.load_records(module)}
    built_keys = [r["key"] for r in built]
    rows = [existing.get(r["key"], r) for r in built]          # keep edits, add missing
    rows += [r for k, r in existing.items() if k not in built_keys]  # keep hand-added extras
    return rows


def _write(module: str, rows: "list[dict]") -> None:
    path = Path(dtc.__file__).resolve().parent / f"{module}.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dtc._CACHE.pop(module, None)


if __name__ == "__main__":
    raise SystemExit(main())
