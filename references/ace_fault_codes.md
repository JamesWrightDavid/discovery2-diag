---
title: "Discovery 2 ACE — fault codes"
area: references
status: draft
version: 1.2
updated: 2026-10-04
summary: >
  ACE fault codes in three display schemes (NanoCom component-grouped XX-YY as on this car, NanoCom flat list keyed flat-XX-YY, Hawkeye/Testbook DTC nn), compiled from first-hand forum pages as candidate; raw block offsets not yet mapped, and NanoCom ACE texts are known to mislead.
---

# Discovery 2 ACE — fault codes

Display codes for the ACE (Active Cornering Enhancement) ECU, compiled from public forum
pages. They seed `src/d2diag/dtc/ace.json` through `tools/gen_dtc_seed.py`, which reads the
table below. Every row is **candidate**: no row has been confirmed on RDL 016 against a raw
capture.

## Raw encoding status

**Display codes documented; raw block offsets not yet mapped.** A one-shot fault block was
captured (`67 67 11 e0 e0 f0 f0 00 00 00 1a 00 00 08 09 80 92 00 00`) while the reference
tool showed `04-02`, `04-04`, `04-05` and `06-01` on this car. See
[other-modules.md](../docs/discovery-2-td5/other-modules.md). The byte-doubling question has
to be settled before any offset is trusted, so no bit is mapped here.

## Three display schemes, kept apart

NanoCom shows ACE codes in two different families. One owner saw both at once:
- the NanoCom screen showed "Fault 18-04";
- the saved TXT file of the same read said "Fault 04-02" (DCV2 current out of range).

Source: https://www.landyzone.co.uk/land-rover/fault-04-02-dcv2-current-out-of-range-and-red-light.373132/

So the families may be the screen and the export of one tool, rather than two firmwares.
That one report does not give the screen's text, so it cannot link any code pair.

- **Component-grouped `XX-YY`** (stored as plain `XX-YY`): `01` accelerometers, `03` pressure
  control valve, `04` direction control valves, `06` hydraulic pressure. **This is what this
  car's NanoCom showed** (`04-02`, `04-04`, `04-05`, `06-01`), so it owns the plain keys. Our
  repo writes these as `004-02`; the store uses the two-digit form.
- **Flat list `XX-YY`** (stored as `flat-XX-YY`, for example `flat-20-04`). In it, `XX` looks
  like the Hawkeye DTC number:
  - `33-06` and DTC 33 are both "direction control valve fault";
  - `18-04` and DTC 18 are both about closed-loop pressure control.

  But `20-04` ("pressure control valve fault") and DTC 20 ("valve block characteristics")
  differ. The same text also turns up under both NanoCom families:
  - "hydraulic pressure too low" is `06-01` and `flat-42-07`;
  - "pressure control valve fault" is `03-04` and `flat-20-04`.

  That is why the families must not share keys.
- **Hawkeye/Testbook `DTC nn`** (stored as `dtcNN`, for example `dtc33`).

No source states how any of the three relate, so the store links none of them. The
"(fault 29)" and "(fault 31)" notes next to `04-05` and `04-07` on one page may be internal
numbers, but they are not linked to anything either.

> ⚠️ **NanoCom ACE texts are unreliable.** A first-hand landyzone thread reports two
> mislabels:
> - an out-of-range pressure sensor read as "control valve 2 circuit fault";
> - an unplugged pressure sensor read as "control valve 1 circuit failure".
>
> Several owners recommend Hawkeye/Testbook for ACE. Treat valve-circuit codes as "check
> the pressure transducer first", and confirm with live pressure and valve currents.

## Codes

| Code | Fault | Confidence | Source |
|---|---|---|---|
| `01-03` | Lower accelerometer signal not changing | candidate | https://www.landyzone.co.uk/land-rover/discovery-ii-nanocom-errors.321133/ |
| `03-04` | Pressure control valve fault | candidate | https://www.landyzone.co.uk/land-rover/ace-fault-03-04-pressure-control-valve-fault.326555/ ; https://www.landyzone.co.uk/land-rover/ace-issue-any-ideas.325758/page-3 (a member notes the NanoCom code is "most probably wrong") |
| `04-02` | Direction control valve 2 current out of range | candidate | https://landyzone.co.uk/land-rover/ace-woes.372902/ ; https://www.landyzone.co.uk/land-rover/ace-fault-04-02.299089/ (seen on RDL 016) |
| `04-05` | Electrical fault, direction control valve 1 circuit | candidate | https://landyzone.co.uk/land-rover/ace-woes.372902/ ("fault 29"); thread title https://www.aulro.com/afvb/discovery-2-a/260641-need-assitance-fault-code-04-05-electrical-fault-directional-control-valve-1-a.html (seen on RDL 016) |
| `04-07` | Electrical fault, direction control valve 1 circuit | candidate | https://landyzone.co.uk/land-rover/ace-woes.372902/ ("fault 31") |
| `06-01` | Hydraulic pressure too low | candidate | https://landyzone.co.uk/land-rover/ace-woes.372902/ ; https://www.landyzone.co.uk/land-rover/another-ace-question-ear-defenders-on-already.233095/ (seen on RDL 016) |
| `06-05` | Pressure control valve current too low | candidate | https://www.landyzone.co.uk/land-rover/another-ace-question-ear-defenders-on-already.233095/ |
| `flat-18-04` | Hydraulic or mechanical fault in pressure control system | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ ; https://www.landyzone.co.uk/land-rover/ace-fault-20-04.373528/ |
| `flat-20-04` | Pressure control valve fault | candidate | https://www.landyzone.co.uk/land-rover/ace-fault-20-04.373528/ ; https://landyzone.co.uk/land-rover/ace-problem.396767/ |
| `flat-22-04` | Hydraulic pressure too high | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `flat-23-04` | Pressure signal out of range | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `flat-33-06` | Direction control valve fault | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `flat-41-07` | Sensor supply voltage out of range | candidate | https://www.landyzone.co.uk/land-rover/ace-fault-41-07.370993/ |
| `flat-42-07` | Hydraulic pressure too low | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `flat-45-07` | Battery voltage too low | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `flat-47-07` | Main relay test failed | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `dtc13` | No engine speed signal received | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc18` | Closed-loop pressure not under control | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc20` | Valve block characteristics out of specification | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc33` | Direction control valve fault | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ ; https://www.landyzone.co.uk/land-rover/discovery-2-ace-dtc-33-directional-control-valve-fault.387150/ |
| `dtc41` | System pressure stayed below threshold while pressure was demanded | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc48` | Main relay fault | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/discovery-2-ace-dtc-33-directional-control-valve-fault.387150/ |

## Backlog (not stored, needs a first-hand source or the car)

- `04-04`: seen on RDL 016, no text anywhere. Read it off the screen next session (T-29).
- `01-05`, `03-01`, `03-05`, `02-02`: texts only in search snippets.
- Hawkeye DTC 22, 23 and 42: texts only in snippets. Hawkeye texts seen with no number
  (landyzone 383549): "the latest page of data was corrupt at the last power up" and
  "pressure signal stuck at a value". Some Hawkeye texts are known with no
  number: "invalid pressure signal received", "hit current direction valve 1/2 not achieved",
  "direction valve hold current not achieved", "upper/lower lateral accelerometer difference
  too high while stationary".
- The full DTC 1–48 list (the repo's register holds a compiled 0001–0048 dictionary that is
  not in this repository).
- **Never send** NanoCom's ACE "set calibrated" or "set tested". A first-hand report says
  they locked up two ACE ECUs (landyzone 132815).
