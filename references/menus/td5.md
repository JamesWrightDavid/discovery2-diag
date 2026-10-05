---
title: "Reference tool menus — Td5 engine ECU"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Complete reference tool Td5 menu (settings, inputs, outputs, utilities) in exact UI order; drives src/d2diag/vehicles/lr_d2/td5/menu.py. Values are screenshot baselines, not RDL 016 readings.
---

# TD5 Engine ECU (Lucas) — complete reference tool menu

Source: `reference tool_protocol_Discovery2_Master_TD5_Complete.docx` (register
repo, transcribed 2026-08-08). Menu order preserved exactly. Drives the TD5 map
(`src/d2diag/vehicles/lr_d2/td5/menu.py`). Our raw mapping: `td5/identifiers.py` (live) +
`td5/faults.py` (`21 3B`).

> ⚠️ **The display values below (ABNFE, svtnp006, ENABLED/DISABLED, ROBUST, 12.6 V …)
> are the transcription's screenshot baseline — NOT read off RDL 016.**
> Faults/Inputs for TD5 had NO screenshots in the .docx;
> our fault decoding comes instead from Ekaitza + reference tool v1.12 (confirmed).

## Settings

**Injector codes / type** (6): Injector 1–5 = five-character classification code
(baseline `ABNFE`), + `INJ. TYPE` (UI action). *Change only one field at a time
during any coding capture.*

**Read-only identification** (5):

| # | Field | Baseline (screenshot) |
|---|---|---|
| 1 | Config Tune ID | `svtnp006` |
| 2 | Fuel Tune ID | `svdhg003` |
| 3 | ECU Part Number | `NNN000120` |
| 4 | Homologation | `4213` |
| 5 | GET VIN | (UI action, separate service) |

**Feature / ECU configuration** (21, packed-block hypothesis): Temperature Gauge,
Tachometer, SLABS, Road Speed, Radiator Fan, MIL Lamp, Fuel Used, Fuel
Temperature, EGR Modulator, EGR Inlet, Cruise Lamp, Cruise Control, Clutch Switch,
CAN Bus, Auxiliary Fan, Auto Gearbox, Air Conditioning, Active Engine mount,
Ambient Sensor, Wastegate Modulator (ENABLED/DISABLED flags) + **ECU Status**
(enum, baseline `ROBUST`). *Toggle one at a time and re-read during a differential capture.*

## Inputs — switches (12)
Brake Switch 1, Brake Switch 2, Clutch Switch, Transfer Ratio, Gear Box,
Cruise Control, Cruise Resume, Set Accelerate, AC Clutch Request, AC Clutch Drive,
AC Fan Request, AC Fan Drive. *Brake 1/2 are logged together (complementary
contacts); AC Request vs Drive is compared as request-against-output.*

## Inputs — Fuelling / live (22)
Engine Speed (rpm), Idle Speed Error (rpm), Road Speed (km/h), Battery (V),
Accel. Way 1/2/3 (V), Accel. Supply (V), Coolant Temp (°C), Fuel Temp (°C),
Air Inlet Temp (°C), Air Flow (gr/hr), Ambient Pressure (kPa), Manifold Turbo
Pressure (kPa), EGR Modulator (%), EGR Inlet (%), Wastegate Modulator (%),
Cylinder 1–5 (balance). *We already decode most of these (see the map); note that
the reference tool shows **three** accelerator voltage tracks while our `21 1B`
decoding gives track1/track2 + demand% — verify Way 3.*

## Outputs — active tests (14, pulse)
A/C Clutch, A/C Fan, MIL Lamp, Fuel Pump, Glow Plugs, Pulse Rev Counter,
Wastegate Modul., Temp Gauge, EGR Throttle, Injector 1–5. *The sequence is
independently confirmed by the reference tool's TD5 documentation. Not implemented
on our side (requires a transmitting cable).*

## Utilities (2) — security 🔴
`GET SECURITY STATUS` (read immobiliser status — start here, read-only) and
`LEARN SECURITY CODE` (can change immobiliser state — **never run** during protocol
testing until the normal state and its recovery are understood).
