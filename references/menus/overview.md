---
title: "Reference tool menus — overview"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Index and provenance of the reference tool menu transcriptions (one file per module), the shared capture workflow and the capture-session template.
---

# Reference tool menus — overview

Transcriptions of the borrowed reference tool's module menus for the Discovery 2. The
source was the owner's Word document (an AI-assisted reading of the tool's online
emulator: a newer product with the same menu structure) and screenshots reviewed on
2026-08-08. These files drive the coverage maps (`*_MENU` in `src/d2diag/*/menu.py`)
and give decoding hints. The original one-cell-per-line paste is in git history before
2026-10-01.

| Module | File |
| ------ | ---- |
| DCU/BCU inputs, instruments, power | [bcu-inputs.md](bcu-inputs.md) |
| BCU settings and info | [bcu-settings.md](bcu-settings.md) |
| BCU outputs and utilities (EKA, keys) | [bcu-outputs-utilities.md](bcu-outputs-utilities.md) |
| ACE | [ace.md](ace.md) |
| Auto gearbox (EAT) | [autobox.md](autobox.md) |
| Airbag (SRS) | [airbag.md](airbag.md) |
| Td5 engine ECU | [td5.md](td5.md) |
| Hella cruise control (V8 branch) | [cruise.md](cruise.md) |

## Capture workflow

For each input, change one physical condition at a time while logging K-line traffic.
Record the reference tool request and the ECU response, then compare the captures to find
the byte, bit or encoded value that changes. Preserve the tool's menu order exactly: it may
map directly to byte or bit order in one returned block. The procedure for a sniffing
session is ADR-0005 and [../test_plan.md](../test_plan.md).

| Menu / function | Reverse-engineering note |
| --------------- | ------------------------ |
| Faults — Read | Read stored and current fault codes. Preserve the display order and all text and codes exactly. |
| Faults — Clear | Record the request/response separately from Faults — Read. |
| Inputs | Live input/status values, in the exact tool order. |
| Outputs | Actuator/output tests. Preserve the exact order and the group boundaries. |
| Utility | Module-specific service, programming and calibration functions. Document each separately. |

## Capture session template

| Field | Value |
| ----- | ----- |
| Date / time | |
| Vehicle / ECU variant | |
| Reference tool screen / function | |
| K-line interface / sniffer | |
| Baud / init method | |
| Raw log filename | |
| Comments | |
