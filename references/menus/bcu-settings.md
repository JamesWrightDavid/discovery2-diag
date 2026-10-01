---
title: "Reference tool menus — BCU settings and info"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Reference tool BCU Settings pages (lights/windows/seats, transmission/lock/warn, instrument pack, alarm/other) and BCU INFO identity fields, in exact UI order.
---

# Reference tool menus — BCU settings and info

> Converted on 2026-10-01 from the former `reference_tool_master_menu.md` (a Word
> transcription of the reference tool's menus; see [overview.md](overview.md)). Menu order
> and UI spelling are preserved exactly. **Displayed values are screenshot examples,
> not protocol constants.** Empty request/response columns were dropped.

## BCU — Settings

**Purpose.** Configuration items transcribed from the supplied reference tool BCU → Settings screenshots. The values shown are the settings visible in this capture only. During protocol analysis, distinguish a read-settings request from any write/commit operation; do not assume that cycling a reference tool option immediately writes to the BCU.

### BCU SETTINGS — LIGHTS WINDOWS-SEATS

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Front fog lamp | NONE |
| 2 | Daytime run lights | NONE |
| 3 | Courtest head lamps | DISABLED |
| 4 | Headlamp power wash | NOT FITTED |
| 5 | Electric window front | DRV CANCE |
| 6 | Rear windows sunroof | DRV CANCE |
| 7 | Heated front screen | NOT FITTED |
| 8 | Electric front seats | NOT FITTED |
| 9 | Programmed wash wip | NORMAL |
| 10 | Seat belt warning | TIMED |
| 11 | Seat belt warning soun | TIMED |
| 12 | Autographics | ALWAYS |

### BCU SETTINGS — TRANSM-LOCK-WARN

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Transmission | AUTO |
| 2 | Shift Interlock | NONE |
| 3 | HDC | NOT FITTED |
| 4 | Superlock | DISABLE |
| 5 | Single point entry | NOT SPE |
| 6 | Speed lock option | DISABLED |
| 7 | Mislock option | DISABLED |
| 8 | Bathrobe lock option | DISABLED |
| 9 | Odometer error warn | NOT FITTED |
| 10 | Key warning | DISABLED |
| 11 | Low battery warning | DISABLED |
| 12 | Bulb failure | DISABLED |

### BCU SETTINGS — INSTRUMENT PACK

Configuration items transcribed from the supplied reference tool BCU → Settings → Instrument Pack screenshots. One screenshot repeats the Gulf/Police/HDC/TRC page, so duplicate entries are listed only once.

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Transmission | MANUAL |
| 2 | Engine | PETROL |
| 3 | ACE | YES |
| 4 | SLS | YES |
| 5 | Gulf | YES |
| 6 | Police | YES |
| 7 | HDC | YES |
| 8 | TRC | YES |

Instrument Pack has several feature-presence flags (ACE, SLS, HDC, TRC, Gulf, Police) plus enumerated vehicle configuration such as Transmission and Engine. These are strong candidates for a packed configuration block; change only one setting at a time when mapping bytes/bits.

#### Notes for BCU settings protocol analysis

Preserve the displayed reference tool text exactly while mapping the protocol. Several labels/values are visibly abbreviated or appear misspelled in the UI (for example “Courtest head lamps”, “DRV CANCE”, “Seat belt warning soun” and “NOT SPE”). Do not expand these until the actual option semantics have been verified.

Settings are particularly useful for differential captures: read the same menu, change exactly one option in reference tool, read again, and compare the raw request/response frames. If possible, capture the traffic both when cycling the displayed value and when leaving/saving the menu.

Treat enumerated settings such as Transmission=AUTO, Programmed wash wip=NORMAL and Seat belt warning=TIMED as likely multi-valued fields rather than Boolean flags.

Before intentionally writing configuration, make a complete baseline capture of every settings page and record the original values so the BCU can be restored if needed.

### BCU SETTINGS — ALARM-OTHER

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Alarm | NOT FITTED |
| 2 | Alarm option | DISABLED |
| 3 | Alarm disarm | ALWAYS |
| 4 | Alarm sounder | ALARM |
| 5 | Alarm tamper | DISABLED |
| 6 | Engine immobil. | LED OFF |
| 7 | Passive immobil. | DISABLED |
| 8 | Inertia switch | NO HAZARD |
| 9 | Hazard option | DISABLED |
| 10 | Volumetric sensor | NOT FITTED |
| 11 | Market | UNKNOWN |
| 12 | EKA option | DISABLED |
| 13 | Cruise control | DISABLED |
| 14 | Air conditioning | NOT FITTED |
| 15 | Fuel burning heater | UNKNOWN |
| 16 | Passive coil | NOT FITTED |
| 17 | Transit mode | NOT SET |

**Protocol note.** ALARM-OTHER contains a useful mixture of Boolean flags and enumerated fields (for example Alarm disarm, Alarm sounder, Inertia switch, Hazard option and Market). This makes the page especially useful for distinguishing packed bit fields from one-byte enumerations. In this captured screen Market is displayed as UNKNOWN; do not assign a market code until the raw response is mapped.

### BCU INFO

| # | reference tool label | Captured value |
|---|---|---|
| 1 | Serial No | 0 |
| 2 | Date | 11/02/02 |
| 3 | Hardware No | 1.01 |
| 4 | Software No | 8.02 |
| 5 | Alarm Type | 10 |
| 6 | VIN | SAL + LTGA877A654321 |

UI shows prefix “SAL” separately from “LTGA877A654321”; concatenated form is SALLTGA877A654321.

**Protocol note.** The INFO page exposes six identity/version fields: Serial No, Date, Hardware No, Software No, Alarm Type and VIN. The values in the table are transcribed from the supplied screenshots. The VIN is displayed by reference tool in two adjacent fields (“SAL” and “LTGA877A654321”), which together form SALLTGA877A654321.

**Reference cross-check.** Menu labels were cross-checked against the official reference tool Valeo BCU (Discovery II) ECU guide; screenshot spellings remain the primary reference for reverse engineering.
