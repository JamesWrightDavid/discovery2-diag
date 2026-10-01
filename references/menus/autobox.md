---
title: "Reference tool menus — auto gearbox (EAT)"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Reference tool auto gearbox (EAT, Bosch GS8.87.0) menu: faults, the 26 ordered GENERAL inputs, outputs and utility, in exact UI order.
---

# Reference tool menus — auto gearbox (EAT)

> Converted on 2026-10-01 from the former `reference_tool_master_menu.md` (a Word
> transcription of the reference tool's menus; see [overview.md](overview.md)). Menu order
> and UI spelling are preserved exactly. **Displayed values are screenshot examples,
> not protocol constants.** Empty request/response columns were dropped.

Status: General Inputs documented from reference tool screenshots; Faults, Settings/other input groups, Outputs and Utility still awaiting screenshots / captures.

#### Faults - Read

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Faults - Clear

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Inputs

| # | reference tool label / function |
|---|---|
| 1 | Throttle position (%) |
| 2 | Engine torque (%) |
| 3 | Torque requested (%) |
| 4 | Reduced torque (%) |
| 5 | Friction torque (%) |
| 6 | Torque reference (Nm) |
| 7 | Gear switch W |
| 8 | Gear switch X |
| 9 | Gear switch Y |
| 10 | Gear switch Z |
| 11 | Program switch |
| 12 | High/Low range switch |
| 13 | Kick down |
| 14 | Shift type |
| 15 | Engine speed (RPM) |
| 16 | Turbine speed (RPM) |
| 17 | Output speed (RPM) |
| 18 | Battery (V) |
| 19 | Solenoid valve 1 |
| 20 | Solenoid valve 2 |
| 21 | Solenoid valve 3 |
| 22 | Modulator pressure |
| 23 | Engine temperature (°C) |
| 24 | Adaptive program 1 |
| 25 | Adaptive program 2 |
| 26 | Adaptive program 3 |

#### Outputs

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Utility

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

**Auto Gearbox Inputs.** The 26 GENERAL input items are kept in the supplied reference tool top-to-bottom sequence. Do not reorder them when correlating K-line captures. Treat the whole page as a possible single polling block until traffic proves otherwise.
