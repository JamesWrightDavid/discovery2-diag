---
title: "Goals — the Ostler pack for Land Rover Discovery 2, and the platform in brief"
area: root
status: stable
version: 1.0
updated: 2026-10-06
depends_on: [SCOPE.md]
summary: >
  The Discovery 2 pack's goals in full (complete module coverage, a NanoCom-parity map, verified signals, the platform's reference pack and conformance fixture, upstream data contributions, safety) plus a condensed copy of the Ostler platform goals; the canonical platform GOALS.md lives in openostler/ostler.
---

# Goals

This file holds the **Discovery 2 pack's goals in full** and the **Ostler platform goals
in brief**. The canonical platform statement is
[openostler/ostler GOALS.md](https://github.com/openostler/ostler/blob/main/GOALS.md);
if the two disagree on a platform matter, that one wins.

## The Discovery 2 pack

**Mission:** be the most complete, honest and open diagnostic definition of the Land Rover
Discovery 2 Td5 over K-line, and the pack every other Ostler pack is measured against
([SCOPE.md](SCOPE.md)).

| # | Goal | What "done" looks like | Where it is tracked |
|---|---|---|---|
| 1 | **Full module coverage** | Td5, SLABS, BCU, airbag/SRS, ACE and EAT each have faults, live data, tests and procedures where the module offers them; the read-only address scan confirms or rules out every other asserted module | [capability inventory](docs/capability-inventory/overview.md), [TODO.md](TODO.md) (ACE, EAT, BCU decoding) |
| 2 | **NanoCom-parity map** | Every reference-tool menu item is mapped to its LID or routine with a status (verified, candidate, sniff, untranscribed), so the gap to a closed tool is visible at a glance | [reference tool menu map](references/reference_tool_menu_map.md), [menus](references/menus/overview.md) |
| 3 | **Verified signals** | Every field in `src/d2diag/signals/` is `proven` against the car or honestly `candidate`; open questions (e.g. Td5 MAF and boost mapping) are settled by the in-car backlog; proven coverage never regresses | [test_plan.md](references/test_plan.md), [protocol state](references/protocol_state_handoff.md) |
| 4 | **Reference pack and conformance fixture** | The `VehiclePack` contract, the generated capability manifest, the multi-system UI and the decode pipeline are all tested against this pack; platform CI fails if D2 coverage regresses | `tests/test_pack_contract.py`; platform ADR-0013 |
| 5 | **Open standards in the data** | Each signal carries a COVESA VSS `metric` path where one exists; fields are OBDb-expressible, with confidence, evidence and safety in an `x-ostler` block; proven fields gain fixtures from real, scrubbed captures | Platform UI spec, phases U0 and U7 |
| 6 | **Contributing upstream** | The D2 data, CC BY-SA 4.0, offered to OBDb (which has no D2/Td5 entry); findings shared with the Td5 community as a progress report; collaboration with Discovery 3/4 work (jlr-scanner) rather than duplication | [LICENSE-DATA](LICENSE-DATA), capability inventory |
| 7 | **One interpretation, two comms nodes** | The ESP32 K-line node's decode header is always generated from the signal store, never hand-copied | [esp32/](esp32/README.md), `tools/gen_signal_header.py --check` |
| 8 | **Safe by construction** | Reads first; airbag/SRS read-only; actuator tests confirmed and stationary; no EKA or key programming in any default path; BCU SecurityAccess research stays offline and gated (ADR-0007); no VIN, EKA or raw capture ever committed | [CONSTITUTION.md](CONSTITUTION.md), [decisions/](decisions/CLAUDE.md) |

**Not this pack's job:**

- Platform work (UI, logbook, server, integrations): it goes to
  [openostler/ostler](https://github.com/openostler/ostler).
- HEVAC control: a separate ESP32 project that Ostler only talks to; the HEVAC spec
  here is superseded by the platform direction.
- The car's own faults and maintenance history: those belong in the owner's sister
  project, not here.

**Open:** how the gated BCU security research (ADR-0007, test plan T-27/T-28) sits with
the platform's "no key programming" hard line is for the owner to settle.

## The Ostler platform, in brief

Ostler aims to be **the Home Assistant of the automotive world**: an open, local-first
vehicle platform on hardware you own. Full detail in the
[canonical GOALS.md](https://github.com/openostler/ostler/blob/main/GOALS.md).

- **Pillars:** diagnostics; a data logger with telemetry; a GPS tracker and a
  **notify-only** alarm on an always-on ESP32 guardian (own battery, IoT SIM); add-on
  devices on a private CAN bus (relay box, head-unit CAN/OBD emulator); cameras on our own
  infrastructure; MQTT/Home Assistant, OVMS and OwnTracks integration; a decode pipeline;
  community data.
- **Vehicles:** this D2 first, then other Land Rover and Rover, any OBD-II car
  (`generic_obd2`), modern CAN/UDS, and pre-OBD cars.
- **Displays are thin clients:** one head-unit-first PWA generated from capability
  manifests, with a garage for several vehicles; later an Ostler Android launcher.
- **Hardware:** a Pi 5 + CarPiHAT and an ESP32-S3 LTE/GNSS dev kit now; our own boards
  later.
- **Principles:** local-first and private by default; open standards (COVESA VSS
  canonical); safety travels with the action; honest confidence; core, add-on or moonshot,
  with the rule of two.
- **Hard lines:** nothing writes to a car without gates; no EKA or key programming; the
  VIN is never logged or uploaded; no cloud dependency; no vehicle maker's marks in our
  brand.
- **Business:** official hardware and a closed Ostler Cloud subscription; AGPL code plus
  a commercial licence; CC BY-SA vehicle data; a CLA.
- **Done:** `VehiclePack` decoupling, the platform/pack repo split, a dev server, a
  version tracker and the UI research. **Next:** UI seams and shell, then opt-in
  MQTT/Home Assistant, the guardian, `generic_obd2` and CAN add-ons.
