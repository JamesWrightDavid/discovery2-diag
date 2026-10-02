---
title: "NanoCom feature map — overview"
area: references
status: draft
version: 1.0
updated: 2026-10-02
summary: >
  Index to the NanoCom Evolution feature map for the Discovery 2 Td5, derived from the
  tool's online emulator. Links the generated menu tree and the per-module feature maps
  (function → data fields → current coverage → sniff priority → UI target → safety).
---

# NanoCom feature map — overview

What the NanoCom Evolution exposes for the Discovery 2 Td5, mapped so the project knows
**what to sniff**, **what to build in the dashboard**, and **what data becomes available**
once each function is reverse-engineered.

## Source & licensing

Derived from the NanoCom Evolution **online emulator** (Black Box Solutions). The raw
emulator export (`emulator.json` + page images) is that vendor's proprietary reference and
is **kept out of git** under `captures/nanocom/`; only our derived tree and transcriptions
are committed — the same practice behind [`../menus/`](../menus/overview.md). The emulator
proves a function *exists*; it is never evidence that our decode of it is correct (no
confidence tag is raised without car evidence — see [../test_plan.md](../test_plan.md)).

## Contents

- [`td5_menu_tree.md`](td5_menu_tree.md) — **generated** menu tree: every module and its
  faults/inputs/outputs/settings/utility functions, with each leaf's emulator page and
  screen image. Regenerate with `tools/parse_nanocom_emulator.py`; never hand-edit.
- [`feature_map.md`](feature_map.md) — **the cross-reference**: every function → data
  exposed → current coverage → sniff priority → dashboard tab → safety class. This is the
  answer to "what to sniff / what to build in the UI / what data becomes available".
- Per-module field lists live in [`../menus/`](../menus/overview.md) (BCU, SLABS, TD5, ACE,
  autobox, airbag, cruise) — the feature map links them rather than repeating them.

## Module coverage at a glance (emulator page counts)

| Module | Emulator functions | Pages | Current project coverage |
|--------|--------------------|-------|--------------------------|
| TD5 engine | faults, inputs (fuelling, switch), outputs, settings (info, injectors), utility | 23 | best-mapped (live + faults + outputs) |
| SLABS | faults, inputs (ABS, SLS, switch), outputs, settings, utility (bleed, height) | 29 | well-mapped (live + faults + actuators) |
| Valeo BCU | key programming, outputs (body, security), read inputs (body 1/2, instrument, power), settings (alarm/other, info, instrument pack, lights/win/seat, transm/lock/warn, write), utility | 54 | richest + least mapped (EKA offline only) |
| Auto gearbox (EAT) | faults, inputs (general, pressures), settings, utility | 16 | faults read; payload undecoded |
| Airbag / SRS | faults, settings | 7 | faults (experimental, read-only) |
| ACE | faults, inputs, outputs, utility | 9 | fault block isolated |
| Cruise (Hella) | faults, inputs, settings, utility | 9 | unconfirmed (shared with V8 variant) |

Cross-reference the decode status in [`../../docs/capability-inventory/overview.md`](../../docs/capability-inventory/overview.md)
and the coverage maps (`*_MENU` in `src/d2diag/*/menu.py`).

## How this feeds the project

- **Sniff backlog:** each OPEN function in the maps becomes a capture target (ordered in
  [../test_plan.md](../test_plan.md)); safe-write functions (fault clear) and forbidden
  ones (EKA/key programming, airbag outputs) are marked per the safety rules.
- **UI roadmap:** each function names the dashboard tab it belongs to (Faults, Inputs,
  Outputs, Settings, Utilities), so the viewer's screens are planned from the tool's own
  structure rather than guessed.
- **Available data:** the transcribed field lists are the candidate signals/outputs each
  function would yield; confirmed ones enter `signals/*.json` as `candidate` until car
  evidence proves them.
