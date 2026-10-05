---
title: "Td5 / Discovery 2 ecosystem — the map of every source"
area: references
status: stable
version: 1.1
updated: 2026-10-04
depends_on: [td5-cross-reference.md, td5-external-findings.md]
summary: >
  Catalogue of every known Td5/Discovery 2 information source — open-source projects, professional tools, vendor and factory docs, and community archives — with what each offers and whether we have mined it. So we stop re-discovering the same sources.
---

# Td5 / Discovery 2 ecosystem — the map of every source

The durable answer to "have I missed anything?". Everything known that bears on Discovery 2
Td5 diagnostics, with a **status**: 🟢 mined (folded into our repo) · 🟡 partial (some facts
used) · ⚪ catalogued (known, not yet mined) · 🔵 reference (read-only ground truth, not code).
Field-level comparisons live in [td5-cross-reference.md](td5-cross-reference.md); the
decision to port from any of these was taken per the owner (private use, permissions
obtained).

## Open-source projects

| Project | Lang / platform | License | What it offers | Status |
|---|---|---|---|---|
| [pajacobson/td5keygen](https://github.com/pajacobson/td5keygen) | C / Python | BSD-2 | Td5 SecurityAccess seed→key (ex-OffTrack disassembly) | 🟢 ported → `td5/keygen.py` |
| [EA2EGA/Ekaitza_Itzali](https://github.com/EA2EGA/Ekaitza_Itzali) | Python | none | real sniffs; LID map, fault map, outputs, settings; `fuelling_to_json.py` | 🟢 core corroborated |
| [SimonRafferty/Land-Rover-Td5-Arduino-Diagnostics](https://github.com/SimonRafferty/Land-Rover-Td5-Arduino-Diagnostics) | Arduino/ESP32 | MIT | `TD5_PROTOCOL_REFERENCE.md` LID table, big-endian correction | 🟢 folded |
| [SimonRafferty/Td5-Diagnostic-App](https://github.com/SimonRafferty/Td5-Diagnostic-App) | ESP32-S3 + Android | MIT | **newest, most-corrected decode** (`td5_provider.cpp`); ELM327-emulation; **DTC table w/ P-codes**; **PCB/gerbers/BOM/enclosure** | 🟢 mined 2026-10-01 |
| [hairyone/TD5Tester](https://github.com/hairyone/TD5Tester) | Android/Java | Apache-2.0 | 20+ param formulas; a 5th cross-check | 🟡 corroboration |
| [BennehBoy/td5opencomstm32](https://github.com/BennehBoy/td5opencomstm32) | STM32 C++ | none | td5opencom (Luca72) port; LID + DTC tables | 🟡 cross-check |
| td5opencom (Luca Veronesi / "Luca72") | Arduino | — | the common ancestor behind Ekaitza + BennehBoy | 🟡 via descendants |
| [k0sci3j/BinOwl_Td5Gauge](https://github.com/k0sci3j/BinOwl_Td5Gauge) | ESP32 | GPL-3.0 | LID offsets/scales; keygen confirmation | 🟡 facts only (GPL) |
| [hairyone/pyTD5Tester](https://github.com/hairyone/pyTD5Tester) | Python | none | init `81 13 F7 81 0C`, session `10 A0`, `27 01/02`, LIDs `09`/`0D`/`10` — all agree with ours (2026-10-04) | 🟡 corroboration |
| [Td5OpenDiag/Td5OpenDiag-android](https://github.com/Td5OpenDiag/Td5OpenDiag-android) | Android | Apache-2.0 | diagnostics + logging app | ⚪ not yet mined |
| [Luca72/Td5MapEditor](https://github.com/Luca72/Td5MapEditor) | C++/Qt | GPL-3.0 | Td5 **map-file** editor (base maps embedded); no ECU write path, no flash layout in the README | ⚪ tuning context only |
| [BennehBoy/LRDuinoTD5](https://github.com/BennehBoy/LRDuinoTD5) | STM32 | Beerware | gauge over L9637D K-line | ⚪ context |
| [JRogers83/TD5-Dash](https://github.com/JRogers83/TD5-Dash) | Pi | none | dashboard; its protocol doc claims `21 1A` = logged faults, which **conflicts** with our proven temperatures ([d2-tool-cross-reference.md](d2-tool-cross-reference.md)) | ⚠️ treat with care |
| [muki01/OBD2_K-line_Reader](https://registry.platformio.org/libraries/muki01/OBD2%20K-Line) | Arduino/ESP32 | MIT | fast-init timing, L9637D interface | 🟡 vendored ref |
| Leijoma/discovery2-diag | Python | — | our upstream (this repo is a fork) | 🟢 base |
| colinbourassa/libcomm14cux · memsgauge | C / C++ | — | Rover **V8 14CUX / MEMS 1.6** — not Td5 | ⚪ low reuse (wiring only) |
| Generic KWP2000 libs (argerus/ecu_diagnostics, aster94/Keyword-Protocol-2000, gkbus, ludwig-v/arduino-psa-diag) | various | various | protocol scaffolding, not Td5-specific | ⚪ reference |

**Conclusion:** a GitHub sweep (2026-10-01) found no other significant Td5-specific repo.
The open-source Td5 corpus above is complete, and all of it is **engine-only** — none covers
SLABS / BCU / airbag / EAT / ACE / cruise / HEVAC.

## Professional / commercial tools

| Tool | Maker | Notes | Use to us |
|---|---|---|---|
| **Nanocom Evolution** | Blackbox Solutions spin-off | the plan's capture source (ADR-0005); kits cover D2 Td5+V8, Defender, P38 | 🔵 capture oracle |
| **Faultmate MSV-2 / Lynx** | Blackbox Solutions | per-system software (6–9 modules); the `SM0xx` help pages document every D2 module functionally | 🔵 functional ref (weak modules) |
| **Hawkeye** | Blackbox Solutions | reverse-engineered Rovacom; consumer tool | ⚪ context |
| Rovacom / EASE / T4 / IID | various | older/pro LR tools | ⚪ context |
| **TD5Inside / "td5 Flasher"** | Performance Inside (Portugal), td5inside.pt | commercial remap service + closed paid PC tool (OBD cable): map/firmware read-write, dual maps, faults, I/O tests, injector codes, VIN coding, ECU "security code" learn; remap files locked to an ECU key + VIN. Proprietary, no licence published, so **not** a source to copy or decompile | ⚪ public facts only (below) |

### Td5 ECU variants and reflashing: what is public (2026-10-04)

- **MSB vs NNN.** Both give full live data and diagnostics over OBD.
  - NNN ECUs "have all functions enabled from the factory", including OBD map writing.
  - MSB ECUs need their internal memory changed (a chip soldered in) before OBD mapping.
    Early 1999–2001 MSB ECUs can't be read or written over OBD at all (TD5Inside product
    and service pages).
  - The NanoCom vendor guide says the same: MSB can't be programmed, NNN can.
- **Security.** The public keygen (`pajacobson/td5keygen`, which our `td5/keygen.py` is
  ported from) covers the **diagnostic** level `27 01/02` only. No open source documents a
  programming-level key.
- **The flash path is not public.** No open repository documents the Td5 programming
  sequence: RequestDownload `34`, TransferData `36`, RequestTransferExit `37`, a
  programming security level, or baud changes. The one library known to write maps
  (Luca72's original `td5opencom`) is not published. Commercial tools (NanoCom, TD5Inside
  Flasher, Rovacom, Faultmate) implement it, closed source.
- **Engine ECU ↔ immobiliser "security learn"** (fitting a replacement ECU) exists as a
  tool function on NanoCom and TD5Inside. Its bytes are unpublished. Our Td5 layer
  deliberately does not implement it.
- **Project stance:** reflashing stays research-only here. A failed write can brick the
  engine ECU, and every write needs its own ADR and confirmation gate (CONSTITUTION).

## Vendor & factory documentation (🔵 ground truth)

- **RAVE** — Land Rover's official workshop manual + **ETM** (Electronic Troubleshooting
  Manual): pinouts, wiring diagrams, the EKA entry procedure, and factory fault-code
  meanings. The authority for pinouts and fault semantics; we should cite it when promoting
  a fault or a pin, rather than inferring.
- **Nanocom module PDFs** — e.g. "Diagnostic Functions of the Valeo BCU" and "Wabco SLABS"
  (mirror: `cdbl.free.fr/Nanocom/...`, and `nanocom-diagnostics.com/uploads/downloads/`).
  Already the basis of `valeo_bcu_capabilities.md` / `wabco_slabs_capabilities.md`.
- **Blackbox "Faultmate" help** (`blackbox-solutions.com/help/SM016.html` = WABCO SLABS, and
  sibling `SM0xx` pages) — functional per-module reference, strongest for ACE/EAT/cruise/HEVAC
  which our repo barely covers. (Egress-blocked from here; read it in a browser.)
- **scribd**: "Discovery II Valeo BCU ECU Guide", "ABS-SLS SLABS Diagnostic Functions".

## Community archives (🔵 living knowledge)

- **AULRO** `electronic-diagnostic-systems` — the "reverse-engineering the Td5 ECU" thread is
  the canonical RE discussion (where OffTrack / Ekaitza / pajacobson collaborated).
- **Defender2.net**, **disco2.co.uk**, **4x4community.co.za**, **LandRoverForums** — injector
  coding, EKA lockout, MAF/EGR symptoms, tool comparisons.

## Concrete facts captured this pass
- **Injector-code format** (5 digits): digits 1-2 = start-of-injection offset (±0.000127 s),
  3-4 = end-of-injection offset, 5 = idle-performance variance. → test plan **T-07**.
- Td5 follows the **1997/8 draft** KWP2000, not the 1999 official — explains framing/timing
  quirks our K-line layer already tolerates.
- The Simon app's `td5_dtc_table.h` carries **OBD-II P-codes** on our exact `{byte,bit}`
  fault indexing — a future enhancement to `td5/faults.py` / `faultmap.json` (deferred: 211
  entries, wants its own verification pass).

## Fault dictionary (built 2026-10-01)
The "meaning of each error" is now a store: `src/d2diag/dtc/<module>.json` (loader
`d2diag.dtc`), seeded for Td5 (210 codes, meaning+cause+severity+inferred P-code), SLABS
(012–114 from rswsolutions) and airbag (sparse). It is served two ways: the generated
[fault dictionary](../docs/discovery-2-td5/fault-dictionary.md) (Docs tab, `tools/gen_fault_docs.py`)
and the web `/faults` endpoint (live meanings on the dashboard). The DTC→P-code
cross-reference above is folded in. Decoders stay the source of truth for bit→name; the
`dtc` store adds meaning.

## Not yet mined / next (the RAVE replacement, continued)
- **Wiring/technical diagram catalogue + connector/pinout library + viewer**, and **manual
  ingestion** (RAVE/ETM PDFs the owner supplies). Binaries live in the gitignored
  `manuals/`/`diagrams/` dirs; only the index + extracted text get committed. Deferred pass.
- The Faultmate `SM0xx` help and RAVE ETM for the **non-engine modules** (SLABS calibrations,
  ACE, EAT payloads, cruise, HEVAC) — the functional layer the NanoCom capture (ADR-0005) and
  `module_scan` will turn into protocol facts; also to enrich the airbag/EAT/BCU/ACE fault
  meanings (currently sparse).
