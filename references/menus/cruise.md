---
title: "Reference tool menus — Hella cruise control (ECCU)"
area: references
status: stable
version: 1.0
updated: 2026-10-02
summary: >
  NanoCom emulator menus for the Hella cruise control module (faults, inputs, settings,
  utility), transcribed in exact UI order. The emulator exposes it only under the V8
  (motronic) Discovery branch, so whether the Td5 has a separate addressable cruise module
  is still open — see docs/discovery-2-td5/cruise-control.md.
---

# Reference tool menus — Hella cruise control (ECCU)

Transcribed 2026-10-02 from the NanoCom Evolution online emulator
(`discovery/motronic/hella_cc`, screen images). Menu order and UI spelling are preserved
exactly. **Displayed values are screenshot examples, not protocol constants** (most input
fields were blank in the emulator). See [overview.md](overview.md) for provenance and the
capture workflow.

> **Scope caveat (data honesty).** The emulator lists this Hella cruise module only under
> the **V8/motronic** Discovery (its Settings "Vehicle tune" reads `4.6 ENGINE`). The Td5
> Discovery 2's cruise may be handled differently (integrated with the EDC/BCU) — treat a
> separate Td5 cruise module as **unconfirmed** until an address scan or sniff proves it
> (see [docs/discovery-2-td5/cruise-control.md](../../docs/discovery-2-td5/cruise-control.md)
> and T-26 in [../test_plan.md](../test_plan.md)).

Top menu: **Faults · Settings · Inputs · Utility**.

## Faults

Read and Clear (the shared fault-read/clear cycle — capture both services, cf. the other
modules in [reference_tool_sniff_plan.md](../reference_tool_sniff_plan.md)).

## Inputs

| # | reference tool label | Screenshot value |
|---|---|---|
| 1 | Cruise status | (blank) |
| 2 | Brake/clutch switch | (blank) |
| 3 | Brake light | (blank) |
| 4 | Set switch | (blank) |
| 5 | Resume switch | (blank) |
| 6 | Speed input | (blank) |
| 7 | Minimum threshold | (blank) |
| 8 | Road Speed (Kmh) | (blank) |
| 9 | Road speed (mph) | (blank) |
| 10 | Target speed (Kmh) | (blank) |
| 11 | Target speed (mph) | (blank) |

## Settings

Identification (read-only) then tuning parameters, ending in a **WRITE SETTINGS** action.

| # | reference tool label | Screenshot value | Note |
|---|---|---|---|
| 1 | Part Number | (blank) | identification |
| 2 | Software name | (blank) | identification |
| 3 | Manufacturer | (blank) | identification |
| 4 | Diagnostic index | (blank) | identification |
| 5 | Coding index | (blank) | identification |
| 6 | Date | (blank) | identification |
| 7 | P amplification | (blank) | control tuning |
| 8 | D amplification | (blank) | control tuning |
| 9 | Hysteresis pump | (blank) | control tuning |
| 10 | Hysteresis value | (blank) | control tuning |
| 11 | Set pulse offset | (blank) | control tuning |
| 12 | Set pulse gradient | (blank) | control tuning |
| 13 | Initial acceleration | (blank) | control tuning |
| 14 | Initial acceleration grad. | (blank) | control tuning |
| 15 | Vehicle tune | `4.6 ENGINE` | selectable (V8 branch) |
| — | WRITE SETTINGS | (button) | ⚠️ write/coding — never sniff by writing |

## Utility

One utility page (module-specific service). Contents to be transcribed from
`utility.jpg` when cruise becomes a capture target.

## Reverse-engineering notes

- The two **Road Speed** and two **Target speed** pairs (Kmh/mph) are the same underlying
  value in different units — a good anchor for scaling once captured.
- The control-tuning block (P/D amplification, hysteresis, pulse offset/gradient, initial
  acceleration) are **write/coding** parameters; capture READs only, never a WRITE.
- Confirm the module's address/init first (unconfirmed; address scan T-26) before trusting
  any of this against the Td5 car.
