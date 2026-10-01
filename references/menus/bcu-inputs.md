---
title: "Reference tool menus — DCU/BCU inputs, instruments and power"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Reference tool DCU Read Inputs, BCU Instruments and BCU Power Distribution menus in exact UI order, with screenshot values and capture notes.
---

# Reference tool menus — DCU/BCU inputs, instruments and power

> Converted on 2026-10-01 from the former `reference_tool_master_menu.md` (a Word
> transcription of the reference tool's menus; see [overview.md](overview.md)). Menu order
> and UI spelling are preserved exactly. **Displayed values are screenshot examples,
> not protocol constants.** Empty request/response columns were dropped.

## DCU — Read Inputs

**Purpose.** Working document for reverse-engineering reference tool communication with the Discovery 2 DCU. The menu labels below are transcribed exactly from the supplied reference tool screenshots. The “Screenshot value” column records only the state visible in those screenshots; it is not assumed to be the only possible value.

**Capture workflow.** For each input, change one physical condition at a time while logging K-line traffic. Record the reference tool request and ECU response, then compare captures to identify the byte/bit or encoded value that changes.

### LIGHTS

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Side lights | OFF |
| 2 | Main beam | OFF |
| 3 | Dipped | OFF |
| 4 | Front fog light | OFF |
| 5 | Rear fog light | OFF |
| 6 | Left indicator | OFF |
| 7 | Right indicator | OFF |
| 8 | Hazard | OFF |
| 9 | Daytime run light | DISABLED |

### DOORS / BODY INPUTS

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Passenger door switch | CLOSE |
| 2 | Driver door switch | CLOSE |
| 3 | Bonnet | CLOSE |
| 4 | Key lock | IDLE |
| 5 | Key unlock | IDLE |
| 6 | CDL Lock | IDLE |
| 7 | CDL unlock | IDLE |
| 8 | Inertia | TRIGGER |
| 9 | Ignition key inserted | OUT |
| 10 | Transfer box neutral | OFF |
| 11 | Park/neutral | OFF |

### TRANSMISSION

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Reverse idle | OFF |
| 2 | Transfer neutral switch | OFF |
| 3 | Autobox W switch | OFF |
| 4 | Autobox X switch | OFF |
| 5 | Autobox Y switch | OFF |
| 6 | Autobox Z switch | OFF |
| 7 | Park neutral switch | OFF |

### WINDOWS

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Front LEFT down | OFF |
| 2 | Front LEFT up | OFF |
| 3 | Front RIGHT down | OFF |
| 4 | Front RIGHT up | OFF |

### WASH WIPE

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Front intermit | OFF |
| 2 | Front wash | OFF |
| 3 | Front wiper parked | OFF |
| 4 | Front wiper speed | 6 |
| 5 | Rear wiper | OFF |
| 6 | Rear wash | OFF |

### HEATED SCREEN / ENGINE STATE

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Heated screen switch | OFF |
| 2 | Ignition 2 | ON |
| 3 | Engine speed signal | ACTIVE |

#### Notes for protocol analysis

Keep “Transfer box neutral” and “Transfer neutral switch” as separate reference tool items until captures prove that they map to the same underlying signal.

Keep “Park/neutral” and “Park neutral switch” separate for the same reason.

The screenshot shows “Inertia = TRIGGER”. Verify whether this is a live state, a latched state, or reference tool wording for the input polarity before assigning protocol semantics.

“Front wiper speed” is numeric (6 in the screenshot), unlike the surrounding Boolean-style inputs. Treat it as a likely multi-bit or byte value until captures show otherwise.

Record full frames including initialization/session traffic where possible. Repeated requests are useful for identifying polling cadence and response length.



## BCU — Instruments

**Purpose.** Menu labels and displayed values transcribed from the supplied reference tool BCU → Instruments screenshots. As with the DCU section, the displayed values are capture examples only; they should not be treated as protocol constants.

### BCU INSTRUMENTS — DISCRETE INPUTS / WARNING STATES

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | LH DI | OFF |
| 2 | RH DI | OFF |
| 3 | LH Tailor DI | OFF |
| 4 | RH Tailor DI | OFF |
| 5 | Seat belt | OFF |
| 6 | Diff lock | OFF |
| 7 | Transfer neutral | OFF |
| 8 | Autobox manual | OFF |
| 9 | Autobox sport | OFF |
| 10 | Offroad level | OFF |
| 11 | ABS | ON |
| 12 | Traction control | OFF |
| 13 | SRS | ON |
| 14 | HDC select | OFF |
| 15 | Glow plug | OFF |
| 16 | Brake | ON |
| 17 | Oil pressure | OFF |
| 18 | Alternator | OFF |
| 19 | Check engine | ON |
| 20 | Fuel filter | OFF |
| 21 | Transmission temp. | OFF |
| 22 | Check ACE | ON |
| 23 | Check HDC | ON |
| 24 | Check SLS | ON |

### BCU INSTRUMENTS — MILEAGE / TRIP INPUT

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Instr. milage (km) | 00468502 |
| 2 | BCU milage (km) | 00480000 |
| 3 | IP trip switch | OFF |

#### Notes for BCU protocol analysis

Preserve reference tool spelling exactly during reverse engineering. The screenshots show “LH Tailor DI”, “RH Tailor DI” and “milage”; these may be UI typos rather than protocol terminology.

The two mileage values are especially useful for determining whether reference tool requests instrument-pack mileage and BCU-stored mileage separately, and for identifying byte order and scaling.

Several displayed ON states are warning-lamp/status outputs rather than obvious switch inputs (for example ABS, SRS, Check engine, Check ACE, Check HDC and Check SLS). Treat the menu as an “instrument states” view rather than assuming every item is a direct BCU input.

For Boolean items, capture repeated frames while toggling only one physical condition at a time. For warning states that cannot be safely toggled, compare ignition-off, ignition-on/engine-off and engine-running captures.



## BCU — Power distribution

**Purpose.** Menu labels and displayed values transcribed from the supplied reference tool BCU → Power Distribution screenshots. Displayed values are capture examples only and should not be treated as protocol constants.

### BCU POWER DISTRIBUTION — IGNITION / SUPPLY STATES

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | BCU ignition pos. 1 | ON |
| 2 | BCU ignition pos. 2 | ON |
| 3 | BCU ignition pos. 3 | OFF |
| 4 | IP ignition pos. 2 | ON |
| 5 | IDM ignition pos. 2 | ON |
| 6 | IDM battery (V) | 12.7 |
| 7 | BCU switch power | 12.6 |
| 8 | BCU relay power | 12.6 |

#### Notes for BCU power-distribution protocol analysis

The three BCU ignition-position states are good candidates for a compact bit field. Capture frames at key removed, accessory/position 1, ignition on/position 2 and crank/position 3 if practical.

**IP ignition pos.** 2 and IDM ignition pos. 2 may be separate status reports from the instrument pack (IP) and Intelligent Driver Module (IDM), even though both follow the same ignition condition.

The three voltage values are especially useful for determining numeric encoding and scaling. Record several known battery voltages with a multimeter and compare the raw response bytes.

Because IDM battery, BCU switch power and BCU relay power are close but not identical, do not assume reference tool derives them from one measurement until the response data confirms it.
