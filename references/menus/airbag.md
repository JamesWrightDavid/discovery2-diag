---
title: "Reference tool menus — airbag (SRS)"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Reference tool TRW airbag menu: faults, settings/identification (VIN is the only programmable item), outputs and utility. This tool stays read-only.
---

# Reference tool menus — airbag (SRS)

> Converted on 2026-10-01 from the former `reference_tool_master_menu.md` (a Word
> transcription of the reference tool's menus; see [overview.md](overview.md)). Menu order
> and UI spelling are preserved exactly. **Displayed values are screenshot examples,
> not protocol constants.** Empty request/response columns were dropped.

> This project never writes to the airbag ECU (CONSTITUTION).

Status: Settings documented from reference tool screenshots; Faults still awaiting screenshots / captures. This ECU is limited compared with the other Discovery 2 modules.

#### Faults - Read

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Faults - Clear

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Settings

| # | reference tool label / function |
|---|---|
| 1 | Manufacturer |
| 2 | Model |
| 3 | Software version |
| 4 | Hardware version |
| 5 | Serial number |
| 6 | Date of build |
| 7 | Part reference |
| 8 | Part number |
| 9 | VIN |
| 10 | Driver's airbag |
| 11 | Passenger's airbag |
| 12 | Right hand Pretensioner |
| 13 | Left hand Pretensioner |
| 14 | Driver's side airbag |
| 15 | Passenger's side airbag |
| 16 | Rolamites |

#### Outputs

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

#### Utility

_No entries captured yet. Columns: reference tool label / function, Displayed value / options, Request frame, Response frame, Byte / bit / notes._

**Airbag Settings.** The TRW SPS Type 2A ECU exposes identification/configuration data and only VIN is documented as programmable. Keep read-settings traffic separate from any VIN write operation. The settings order above is preserved as the working protocol order.

**Airbag capability note.** Unlike BCU/ACE, the Discovery 2 TRW SPS Type 2A is documented primarily for Read/Clear Faults and Settings; no separate live Inputs or Outputs page is assumed here unless a reference tool screen/capture demonstrates one.
