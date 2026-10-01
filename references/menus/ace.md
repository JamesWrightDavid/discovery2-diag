---
title: "Reference tool menus — ACE"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Reference tool ACE (Active Cornering Enhancement) menu: faults, inputs, outputs and utility functions in exact UI order.
---

# Reference tool menus — ACE

> Converted on 2026-10-01 from the former `reference_tool_master_menu.md` (a Word
> transcription of the reference tool's menus; see [overview.md](overview.md)). Menu order
> and UI spelling are preserved exactly. **Displayed values are screenshot examples,
> not protocol constants.** Empty request/response columns were dropped.

Status: Inputs, Outputs and Utility documented from reference tool screenshots; Faults still awaiting screenshots / captures.

#### Faults - Read

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Faults - Clear

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Inputs

| # | reference tool label / function |
|---|---|
| 1 | Engine Speed (rpm) |
| 2 | Road Speed (Km/h) |
| 3 | Battery Voltage (V) |
| 4 | DCV1 Current (AMP) |
| 5 | DCV2 Current (AMP) |
| 6 | PCV Current (AMP) |
| 7 | Pressure Sensor (bar) |
| 8 | Residual Pressure (bar) |
| 9 | System Pressure (bar) |
| 10 | Upper Lateral Acccelerometer |
| 11 | Lower Lateral Acccelerometer |
| 12 | Ignition Switch |
| 13 | Reverse Switch |
| 14 | Main Relay |
| 15 | Warning Lamp |

#### Outputs

| # | reference tool label / function | Displayed value / options |
|---|---|---|
| 1 | Main relay(Force ON) | ON / STOP |
| 2 | Main relay(Force OFF) | OFF / STOP |
| 3 | Warning Lamp | ON / OFF |
| 4 | Dir. Control Valve 1 | ON / OFF |
| 5 | Dir. Control Valve 2 | ON / OFF |

**Protocol-order note.** ACE Inputs and Outputs are recorded in the exact top-to-bottom order shown by reference tool. Preserve this sequence when correlating captures; the working hypothesis is that each menu may be read or controlled through a common command with fields returned or addressed in this order.

#### Utility

| # | reference tool label / function | Displayed value / options |
|---|---|---|
| 1 | Calib. Accelerometer 1 | CALIBRATE |
| 2 | Calib. Accelerometer 2 | CALIBRATE |
| 3 | Set Calibrated | SET |
| 4 | OIL BLEEDING STEP 1 | START / STOP |
| 5 | OIL BLEEDING STEP 2 | START / STOP |
| 6 | OIL BLEEDING STEP 3 | START / STOP |

**Protocol-order note.** Utility operations are kept in the exact reference tool menu order. Treat the three calibration operations and the three oil-bleeding steps as distinct commands until captures show otherwise. Bleeding functions are active procedures rather than passive reads, so capture the complete start/stop transaction and any periodic traffic generated while a step is running.
