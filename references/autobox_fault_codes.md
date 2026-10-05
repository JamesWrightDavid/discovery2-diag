---
title: "Discovery 2 auto gearbox (EAT) — fault codes"
area: references
status: draft
version: 1.0
updated: 2026-10-04
summary: >
  EAT gearbox fault codes keyed P-code plus the gearbox's internal fault number (1–39), compiled from a RAVE table posted on a Discovery 2 forum and cross-checked against tool screens; candidate; the 72-framed fault payload is not yet decoded.
---

# Discovery 2 auto gearbox (EAT) — fault codes

Fault codes for the EAT ECU (ZF 4HP22/24, Bosch control). They seed
`src/d2diag/dtc/autobox.json` through `tools/gen_dtc_seed.py`, which reads the table below.
They apply to both Td5 and V8 automatics. Every row is **candidate**.

## Key: P-code plus internal fault number

Several rows share one P-code (P1884 covers seven CAN-message faults). The ECU tells them
apart with an internal fault number (1–39), and the tools show it:
- Hawkeye shows `P1884-33` and `P0705 14`.
- NanoCom shows `P1884 19`.

So the store key is `Pxxxx-NN`, unique per row. The RAVE table gives two numbers for some
faults (for example P0705: 14 and 23), so each number gets its own key with the same text.
Number 36 does not appear.

## Raw encoding status

**Display codes documented; raw payload not decoded.** Read faults `72 05 04 00 73` returns
`72 09 60 01 00 00 00 00 1B` on RDL 016. The payload `01 00 00 00 00` is not interpreted.
The internal fault numbers above are the most likely thing the payload carries. That is a
hypothesis to test with a car that has a known EAT fault, not a mapping. See
[other-modules.md](../docs/discovery-2-td5/other-modules.md).

## Sources

- **RAVE table** (main source): the workshop manual's EAT fault table, posted in a 2002 D2
  Td5 auto thread. It was read first-hand and lists P-code, internal number, description,
  effect and lamp state:
  https://www.landyzone.co.uk/land-rover/2002-disco-td5-auto-auto-problem-oil.102675/page-2
- **Tool screens that agree with it**:
  - NanoCom on a 2001 Td5 showed P1884 (MD_IND invalid), P1843, P1842 and P0705, worded
    as in the table: https://www.landyzone.co.uk/land-rover/error-code-help.353225/
  - Hawkeye showed P1884-33, the engine-torque row:
    https://www.landyzone.co.uk/land-rover/auto-transmission-fault-code.343466/
  - NanoCom showed P1884 19 on a car with a coolant-temperature fault, the engine
    temperature row: https://www.landyzone.co.uk/land-rover/d2-autobox-p1884.397436/

Descriptions are our own wording of the manual's facts.

## Codes

The `Source` cell names which source each row comes from. In it, **RAVE table** means
https://www.landyzone.co.uk/land-rover/2002-disco-td5-auto-auto-problem-oil.102675/page-2

| Code | Fault | Confidence | Source | Effect |
|---|---|---|---|---|
| `P1613-1` | Solenoid-valve supply relay stuck open | candidate | RAVE table | Limp-home in high and low range |
| `P1612-2` | Solenoid-valve supply relay stuck closed or open circuit | candidate | RAVE table | Limp-home in high and low range |
| `P1606-3` | ECU EEPROM fault | candidate | RAVE table | No obvious effect |
| `P1601-4` | ECU EEPROM checksum fault | candidate | RAVE table | Limp-home in high and low range |
| `P0741-5` | Torque-converter lock-up clutch fault | candidate | RAVE table | May affect driveability |
| `P1606-6` | ECU watchdog fault | candidate | RAVE table | No obvious effect |
| `P0743-7` | Lock-up solenoid (MV3) open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P0753-8` | Shift solenoid MV1 open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P0758-9` | Shift solenoid MV2 open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P0748-10` | Pressure-regulating solenoid (MV4) open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P1884-11` | CAN message invalid: engine friction torque | candidate | RAVE table | No obvious effect |
| `P1810-12` | Sport/Manual warning-lamp circuit fault | candidate | RAVE table | Lamp fails bulb check or stays lit |
| `P1810-13` | Sport/Manual warning-lamp circuit fault | candidate | RAVE table | Lamp fails bulb check or stays lit |
| `P0705-14` | Gear position (XYZ) switch, implausible outputs | candidate | RAVE table; NanoCom and Hawkeye screens agree | Holds gear in low range, limp-home in high range |
| `P1842-15` | CAN level monitoring | candidate | RAVE table; NanoCom screen agrees | Holds gear in low range, limp-home in high range |
| `P1841-16` | CAN bus fault | candidate | RAVE table | Holds gear in low range, limp-home in high range |
| `P1843-17` | CAN time-out monitoring | candidate | RAVE table; NanoCom screen agrees | Holds gear in low range, limp-home in high range |
| `P1884-18` | CAN message invalid: throttle position | candidate | RAVE table | Economy mode only, no kick-down |
| `P1884-19` | CAN message invalid: engine temperature | candidate | RAVE table; NanoCom P1884 19 with a coolant-temp fault | Substitute temperature used |
| `P1884-20` | CAN message invalid: road speed | candidate | RAVE table | No obvious effect |
| `P0721-21` | Downshift blocked by the over-speed safety monitor | candidate | RAVE table | Holds gear in low range, limp-home |
| `P0722-22` | Torque converter slipping | candidate | RAVE table | Holds gear in low range, limp-home |
| `P0705-23` | Gear position (XYZ) switch, implausible outputs | candidate | RAVE table | Holds gear in low range, limp-home in high range |
| `P1562-24` | Battery supply below 9 V with the engine running | candidate | RAVE table | Holds gear in low range |
| `P0743-25` | Lock-up solenoid (MV3) open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P0753-26` | Shift solenoid MV1 open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P0758-27` | Shift solenoid MV2 open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P0748-28` | Pressure-regulating solenoid (MV4) open or short circuit | candidate | RAVE table | Limp-home in high and low range |
| `P0731-29` | Implausible 1st-gear ratio | candidate | RAVE table | No obvious effect |
| `P0732-30` | Implausible 2nd-gear ratio | candidate | RAVE table | No obvious effect |
| `P0733-31` | Implausible 3rd-gear ratio | candidate | RAVE table | No obvious effect |
| `P0734-32` | Implausible 4th-gear ratio | candidate | RAVE table | No obvious effect |
| `P1884-33` | CAN message invalid: engine torque | candidate | RAVE table; Hawkeye screen agrees | Substitute torque used, shift quality may suffer |
| `P1884-34` | CAN message invalid: engine torque | candidate | RAVE table | Substitute torque used, shift quality may suffer |
| `P1884-35` | CAN message invalid: engine speed | candidate | RAVE table | Holds gear in low range, limp-home in high range |
| `P1884-37` | CAN message invalid: intake air temperature | candidate | RAVE table | No obvious effect |
| `P1844-38` | Altitude shift-control signal invalid | candidate | RAVE table | No torque-reduction compensation |
| `P1705-39` | High/low range input implausible | candidate | RAVE table | No obvious effect |

## Backlog

- Internal number 36: absent from the table. Whether it is unused or missing is unknown.
- NanoCom's P1884 sub-texts use German signal names. Only `MD_IND` (engine torque) and
  `WFPDK (DKI)` (throttle) were seen first-hand. Matching them to rows 33/34 and 18 is
  probable, not sourced.
- More screens (third pass), consistent with the table but not stored separately:
  - Hawkeye shows `P1884-33` as "Torque NOT in expected range"
    (https://www.landyzone.co.uk/land-rover/auto-transmission-fault-code.343466/page-2);
  - an owner quotes "CAN message throttle angle invalid", which fits row 18
    (https://www.landyzone.co.uk/land-rover/p1884-code-any-ideas.348483/, tool not named);
  - a 2000 D2 V8 owner quotes "V3 road speed invalid", which fits row 20 and supports
    `V3` = road speed
    (https://discoweb.org/index.php?threads/code-p1884-and-loss-of-power.28226/, tool
    unclear).
- Decoding the `72` read-faults payload against a car with a known EAT fault.
