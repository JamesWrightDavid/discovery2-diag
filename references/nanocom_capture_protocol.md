---
title: "NanoCom capture protocol — the sniffing-session runbook"
area: references
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [test_plan.md, menus/overview.md]
summary: >
  Step-by-step runbook for the NanoCom rental: passive ESP32 tap, structured markers (screen/value), per-module screen order and time budget, and the rule that every write/security/coding frame is recorded but never replayed. Feeds tools/nanocom_import.py.
---

# NanoCom capture protocol — the sniffing-session runbook

The one-session plan for the rented NanoCom (ADR-0005). The goal: come away with the
request/response bytes **and** the tool's plaintext for every module, labelled so
`tools/nanocom_import.py` can turn them into candidate signal-store mappings. Pick items
and decision rules from [test_plan.md](test_plan.md) (T-25); the menu order per module is
in [menus/](menus/overview.md).

## Wiring (passive, read-only)

Passive ESP32 tap on **OBD pin 7** (K-line), per `esp32/kline_sniff/kline_sniff.ino`:
OBD pin 7 → 220 kΩ → BC337 base; collector → GPIO16 + 10 kΩ to 3V3; emitter → GND; OBD
pin 4/5 → ESP32 GND. The tap has **no TX wire**, so it can never drive the bus. `hardware/`
has the full build and safety notes.

**Before capturing:** plug the NanoCom into the same OBD port and confirm it still
connects to the car with the tap in place. A passive tap should not disturb the bus —
prove it before trusting a capture. Car stationary, ignition on.

## Logging and markers

Run the reader and type markers as you drive the tool:

```
PYTHONPATH=src python3 tools/esp32_read.py auto logs/nanocom-YYYYMMDD.log
```

Two **structured markers** let the importer map automatically (shorthand expands):

| You type | Logged | Meaning |
|---|---|---|
| `s <module>/<page>` | `>>> screen <module>/<page>` | now on this screen |
| `v <name>=<text>`   | `>>> value <name>=<text>`   | the plaintext the tool shows right now |

`<module>` is the **store** name: `td5`, `slabs`, `bcu`, `airbag`, `autobox`, `ace`,
`cruise` (the UI alias `motor` = `td5`). Free text is logged as a note and still anchors
analysis.

**Method:** hold each screen ~10 s; change **one** physical input at a time and type a
fresh `v` after each change (two+ distinct readings lock a numeric scale and offset).
A `screen` marker resets the importer's LID snapshot, so always mark the screen before its
values.

## Per-module order and budget

Work the proven modules first (they validate the rig), then the rest. Suggested budget for
a single rental; expand from the menu files.

| Module | Screens to capture (menu order) | Budget |
|---|---|---|
| `td5` | Inputs/live (rpm, MAF, boost, temps), Settings/feature-config (T-09), injector codes (T-07), outputs (observe only) | 20 min |
| `slabs` | ABS Inputs, SLS Inputs (T-19 screen values), settings LIDs, lamp tests (observe) | 15 min |
| `bcu` | Inputs (doors, key-in, locking, indicators), Settings, **READ-SET EKA + key programming** (security session, see below) | 20 min |
| `airbag` | Faults read (verify decode, T-18) — **read-only, no clear, no outputs** | 5 min |
| `autobox` | Faults, inputs (pressures, general) — note payloads verbatim (T-17) | 10 min |
| `ace` | Faults, live inputs (one bulk block) — needs ACE enabled on the car | 10 min |
| `cruise` | Faults, any live data the tool shows (new module — confirm address/init first) | 5 min |

## The BCU security session (capture only)

For the offline seed→key work ([bcu_security_research.md](bcu_security_research.md),
ADR-0007): run the NanoCom's **READ-SET EKA** and **key programming** on the BCU several
times, so the rolling seed varies. Record every `27 01`/`27 02` exchange and the `21 CC`
read with the plaintext EKA the tool shows (`v eka=<code>`). This yields many clean
`(seed, key)` pairs for `tools/.../bcu/keygen.py` to fit offline.

## The one hard rule

Every **write, coding, security-unlock, key-programming or actuator** frame the NanoCom
sends is **recorded but never replayed** by our tools. The sniffer is RX-only; nothing
captured is sent to the car without its own ADR and confirmation gate (CONSTITUTION.md,
ADR-0005, ADR-0007). Airbag stays read-only, always.

## After the session

1. `PYTHONPATH=src python3 tools/nanocom_import.py logs/nanocom-YYYYMMDD.log` → review the
   report; re-run with `--write` to store the confirmed mappings as `candidate`.
2. Route protocol facts to `references/<module>_*.md` and the summary in
   `protocol_state_handoff.md`; mappings go to the signal store via the importer.
3. Raw logs stay in gitignored `logs/` (they carry VIN, EKA and seed/key material). Scrub
   before anything is published.
4. Close out the matching T-25…T-28 items in [test_plan.md](test_plan.md).
