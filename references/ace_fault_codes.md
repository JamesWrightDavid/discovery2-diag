---
title: "Discovery 2 ACE — fault codes"
area: references
status: draft
version: 1.0
updated: 2026-10-04
summary: >
  ACE fault codes in two display schemes (NanoCom XX-YY and Hawkeye/Testbook DTC nn), compiled from first-hand forum pages as candidate; raw block offsets not yet mapped, and NanoCom ACE texts are known to mislead.
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

## Two display schemes, kept apart

- **NanoCom `XX-YY`**: group and sub-code. Stored with keys like `20-04`. Our repo writes
  the car's codes as `004-02`; that is the same code with a leading zero, and the store uses
  the two-digit form.
- **Hawkeye/Testbook `DTC nn`**: stored as `dtcNN` (for example `dtc33`).

In the newer NanoCom family, `XX` looks like the DTC number:
- NanoCom `33-06` and DTC 33 are both "direction control valve fault".
- NanoCom `18-04` and DTC 18 are both about closed-loop pressure control.

But `20-04` ("pressure control valve fault") and DTC 20 ("valve block characteristics")
differ. No source states the mapping, so the store does **not** link the schemes.

A second, low-numbered NanoCom family (`01-xx`, `03-xx`, `04-xx`, `06-xx`) also exists.
Our car showed codes from it. Its texts were only found in search-engine snippets of pages
that refuse automated fetches, so they are not stored (see the backlog).

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
| `04-05` | Electrical fault, directional control valve 1 | candidate | thread title, https://www.aulro.com/afvb/discovery-2-a/260641-need-assitance-fault-code-04-05-electrical-fault-directional-control-valve-1-a.html (page refuses fetch; seen on RDL 016 per other-modules.md) |
| `18-04` | Hydraulic or mechanical fault in pressure control system | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ ; https://www.landyzone.co.uk/land-rover/ace-fault-20-04.373528/ |
| `20-04` | Pressure control valve fault | candidate | https://www.landyzone.co.uk/land-rover/ace-fault-20-04.373528/ ; https://landyzone.co.uk/land-rover/ace-problem.396767/ |
| `22-04` | Hydraulic pressure too high | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `23-04` | Pressure signal out of range | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `33-06` | Direction control valve fault | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `42-07` | Hydraulic pressure too low | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `45-07` | Battery voltage too low | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `47-07` | Main relay test failed | candidate | https://www.landyzone.co.uk/land-rover/ace-red-warning-intermittent.377103/ |
| `dtc13` | No engine speed signal received | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc18` | Closed-loop pressure not under control | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc20` | Valve block characteristics out of specification | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc33` | Direction control valve fault | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ ; https://www.landyzone.co.uk/land-rover/discovery-2-ace-dtc-33-directional-control-valve-fault.387150/ |
| `dtc41` | System pressure stayed below threshold while pressure was demanded | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/5-ace-dtcs-logged-and-leaking-fluid-in-the-rear.368776/ |
| `dtc48` | Main relay fault | candidate | Hawkeye, https://www.landyzone.co.uk/land-rover/discovery-2-ace-dtc-33-directional-control-valve-fault.387150/ |

## Backlog (not stored, needs a first-hand source or the car)

- `04-02`, `04-04`, `06-01`: seen on RDL 016. Snippet-only texts are "direction control
  valve 2 current out of range" (`04-02`) and "hydraulic pressure too low" (`06-01`).
  Confirm on the reference tool's screen next session (T-25 capture).
- `01-05`, `03-01`, `03-04`, `03-05`: texts only in search snippets.
- The full DTC 1–48 list (the repo's register holds a compiled 0001–0048 dictionary that is
  not in this repository).
