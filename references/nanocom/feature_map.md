---
title: "NanoCom feature map — Discovery 2 Td5 (sniff / UI / data cross-reference)"
area: references
status: draft
version: 1.0
updated: 2026-10-02
summary: >
  The cross-reference the emulator was captured for: every NanoCom function per Discovery 2
  Td5 module mapped to what data it exposes, our current decode coverage, the sniff
  priority to close the gap, the dashboard tab it belongs in, and its safety class.
---

# NanoCom feature map — Discovery 2 Td5

One row per NanoCom function. **Data exposed** links the exact field list (already
transcribed in [`../menus/`](../menus/overview.md)); **coverage** is the decode status from
[`../../docs/capability-inventory/overview.md`](../../docs/capability-inventory/overview.md)
(ESTABLISHED / CANDIDATE / OPEN); **UI target** is the dashboard tab the function belongs
in (screens in `ui/src/screens/`); **safety** is read / safe-write (fault clear) /
write-coding / **forbidden**. The full function hierarchy is the generated
[`td5_menu_tree.md`](td5_menu_tree.md).

Legend — Sniff priority: **1** do next · **2** soon · **3** later · **✓** largely done.

## TD5 engine ECU (0x13 · 23 pages)

| Function | Type | Data exposed | Coverage | Sniff | UI tab | Safety |
|---|---|---|---|---|---|---|
| Faults read / clear | fault | DTC list (`dtc/td5.json`) | ESTABLISHED | ✓ | Faults | read + safe-write |
| Inputs — fuelling | live | rpm, MAF, boost, temps, fuel ([menus/td5](../menus/td5.md)) | ESTABLISHED | ✓ | Inputs/Drive | read |
| Inputs — switch | live | brake/clutch/A-C/handbrake bits (1E/36) | CANDIDATE | 2 | Inputs | read |
| Outputs | actuator | fuel pump, MIL, A/C, glow, rev-counter, wastegate, EGR, injectors | ESTABLISHED | ✓ | Outputs | write-coding |
| Settings — info | ident | part/tune IDs, homologation, feature config | CANDIDATE | 3 | **Settings (new)** | read |
| Settings — injectors | coding | injector codes, throttle | OPEN | 3 | **Settings (new)** | write-coding |
| Utility | service | security/service routines | OPEN | 3 | Utilities | write-coding |

## SLABS — ABS + air suspension (0x29 · 29 pages)

| Function | Type | Data exposed | Coverage | Sniff | UI tab | Safety |
|---|---|---|---|---|---|---|
| Faults read / clear | fault | DTC list (`dtc/slabs.json`) | ESTABLISHED | ✓ | Faults | read + safe-write |
| Inputs — ABS | live | wheel speeds, ABS sensor V ([menu map](../reference_tool_menu_map.md)) | ESTABLISHED | ✓ | Inputs | read |
| Inputs — SLS | live | corner heights, sensor supply/value | ESTABLISHED | ✓ | Inputs/Drive | read |
| Inputs — switch | live | neutral/low-range/diff/reverse/HDC/door, plip | CANDIDATE | 2 | Inputs | read |
| Outputs | actuator | inlet/outlet valves ×8, pump, compressor, buzzer, **lamps** | ESTABLISHED* | 1 | Outputs | write-coding |
| Settings | config | test status, ECU calibrated, transport mode, suspension type | CANDIDATE | 2 | **Settings (new)** | write-coding |
| Utility — bleed | service | ABS power/modulator bleed, wheel tests | ESTABLISHED | ✓ | Utilities | write-coding ⚠ brakes |
| Utility — height | service | raise/lower corners, store target heights | ESTABLISHED | ✓ | Utilities | write-coding (store = ⚠) |

\*Outputs: actuators proven; the **lamp tests** (T.C./ABS/HDC/Brake/SLS/Offroad) were not
captured cleanly — re-log Outputs in menu order (sniff **1**).

## Valeo BCU — body control (0x40 · 54 pages — richest)

| Function | Type | Data exposed | Coverage | Sniff | UI tab | Safety |
|---|---|---|---|---|---|---|
| Read inputs — body 1/2 | live | lights, indicators, doors, CDL, inertia, ignition, transmission, windows, wash/wipe, heated screen ([menus/bcu-inputs](../menus/bcu-inputs.md)) | OPEN (very extensive) | 2 | **Inputs (new BCU view)** | read |
| Read inputs — instrument | live | 24 warning/discrete states + mileage/trip | OPEN | 2 | Inputs | read |
| Read inputs — power distribution | live | ignition pos 1/2/3, IDM/BCU supply V | OPEN | 2 | Inputs | read |
| Outputs — body | actuator | 17 body outputs (lights, windows, wash/wipe, heated screen) ([bcu-outputs](../menus/bcu-outputs-utilities.md)) | OPEN (list known, bits open) | 3 | Outputs | write-coding |
| Outputs — security | actuator | horn, BBUS, fuel flap, alarm LED, interlock, crank, immo, transponder, lock/unlock/superlock | OPEN | — | Outputs | **forbidden** (immobiliser/alarm) |
| Settings | config | alarm/other, info (VIN), instrument pack, lights/win/seat, transm/lock/warn | OPEN (very extensive) | 3 | **Settings (new)** | write-coding |
| Utility — EKA code | security | read/set 4-part EKA | EKA solved (offline, ADR-0007) | — | Utilities | **forbidden** to write; read only |
| Utility — key programming | security | key codes 1–4, detect/sync, plip bar code | known (UI) | — | — | **forbidden** (can lock the car) |

## Auto gearbox — EAT ZF4HP22/24 (72-framed · 16 pages)

| Function | Type | Data exposed | Coverage | Sniff | UI tab | Safety |
|---|---|---|---|---|---|---|
| Faults read / clear | fault | DTC list | ESTABLISHED (read/clear) | ✓ | Faults | read + safe-write |
| Inputs — general | live | gear, oil temp, engine/turbine/output speed ([menus/autobox](../menus/autobox.md)) | CANDIDATE (GENERAL complete) | 1 | Inputs | read |
| Inputs — pressures | live | pressure group | OPEN | 1 | Inputs | read |
| Settings | ident | read request + UI identification | CANDIDATE (decode open) | 3 | **Settings (new)** | read |
| Utility | service | reset adaptive values | ESTABLISHED | 3 | Utilities | write-coding |

## ACE — active cornering (9 pages)

| Function | Type | Data exposed | Coverage | Sniff | UI tab | Safety |
|---|---|---|---|---|---|---|
| Faults read / clear | fault | fault block (bits open) | CANDIDATE | 2 | Faults | read + safe-write |
| Inputs | live | 15 items — pressures/valves ([menus/ace](../menus/ace.md)) | OPEN (bulk offsets open) | 2 | Inputs | read |
| Outputs | actuator | 5 items | OPEN | 3 | Outputs | write-coding |
| Utility | service | 3 calibration + 3 oil-bleed steps | ESTABLISHED | 3 | Utilities | write-coding ⚠ |

## Airbag / SRS (0x5B addressed · 7 pages)

| Function | Type | Data exposed | Coverage | Sniff | UI tab | Safety |
|---|---|---|---|---|---|---|
| Faults read / clear | fault | 37-type record (`dtc/airbag.json`) | ESTABLISHED | ✓ | Faults | read + safe-write |
| Settings | ident | 16 identification/config fields ([menus/airbag](../menus/airbag.md)) | ESTABLISHED (fields) | 2 | **Settings (new)** | read |
| (Outputs / actuator tests) | — | — | — | — | — | **forbidden** (pyrotechnics) |

## Cruise — Hella (ECCU · 9 pages, V8 branch)

| Function | Type | Data exposed | Coverage | Sniff | UI tab | Safety |
|---|---|---|---|---|---|---|
| Faults read / clear | fault | DTC list | OPEN | 3 | Faults | read + safe-write |
| Inputs | live | cruise status, set/resume/brake switches, road/target speed ([menus/cruise](../menus/cruise.md)) | OPEN | 3 | Inputs | read |
| Settings | coding | ident + PID tuning (P/D amp, hysteresis, pulse, accel), vehicle tune | OPEN | — | **Settings (new)** | write-coding |
| Utility | service | one page (to transcribe) | OPEN | 3 | Utilities | write-coding |

> **Cruise caveat:** the emulator exposes Hella cruise only under the V8/motronic branch; a
> separate addressable Td5 cruise module did **not** answer the full T-26 sweep (2026-10-04:
> fast + 5-baud, `0x01`-`0xEF`; see [test-plan-resolved](../test-plan-resolved.md)).

## What this tells us

- **Sniff next (priority 1):** SLABS lamp outputs (re-log in order) and the EAT gearbox
  inputs (general + pressures) — both are close and high value. Then (priority 2) the BCU
  read-inputs blocks (huge, all OPEN), SLABS/Td5 switch inputs, ACE faults+inputs, airbag
  settings.
- **UI gap — a Settings screen.** Every module has a Settings function, but the dashboard
  has no Settings tab. BCU read-inputs also wants its own rich Inputs view. These are the
  clear next dashboard additions (`ui/src/screens/`).
- **Data that becomes available:** the BCU alone unlocks a whole body-state layer (doors,
  lights, windows, ignition, transmission switches, mileage, supply voltages) the project
  doesn't surface today — directly useful to the GPS/alarm and HEVAC integration specs.
- **Forbidden, by the safety rules:** BCU security outputs, EKA/key programming (can lock
  the car), and airbag actuator tests (pyrotechnics). Read-only, always.
