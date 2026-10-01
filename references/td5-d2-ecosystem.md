---
title: "Td5 / Discovery 2 ecosystem — the map of every source"
area: references
status: stable
version: 1.0
updated: 2026-10-01
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

## Not yet mined / next
- The Faultmate `SM0xx` help and RAVE ETM for the **non-engine modules** (SLABS calibrations,
  ACE, EAT payloads, cruise, HEVAC) — the functional layer the NanoCom capture (ADR-0005) and
  `module_scan` will turn into protocol facts.
- DTC → P-code cross-reference (above).
