---
title: "Capability inventory — highest-priority open questions"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
depends_on: [docs/capability-inventory/overview.md]
summary: >
  The ranked list of open protocol questions across BCU, Td5, SLABS, ACE, auto gearbox and airbag, to drive the next sniff or car session.
---

# Capability inventory — highest-priority open questions

Part of the [capability inventory](overview.md). Each question that needs the car has a matching item in [references/test_plan.md](../../references/test_plan.md).

- BCU SecurityAccess: derive the seed→key algorithm from several complete seed/key pairs without brute force.

- BCU outputs: observation a non-zero write to bank 22/23/C1/C2, then map one output bit at a time.

- BCU settings: map C7/CA/CB/D3/EB/C6/CE/D4/D5/D6/D7 to exact configuration fields using single-change differential observations.

- TD5 settings: map 21 3D/20/0E/32/24 to the 21 feature fields and the injector/ID blocks.

- TD5 switch inputs: isolate the bits in 21 1E/21 36 by toggling one switch at a time.

- SLABS settings: map 45/46/49/59 to individual settings. Lamp-test routines are still missing.

- SLABS analog inputs: complete scaling/offset mapping in 53/55/44/50/57.

- ACE: leave parked until the system is actually repaired; the fault pattern may be an effect of ACE being disabled.

- Auto Gearbox: decode 0x72 framing and payload before naming field values.

- Airbag: collect more fault/status combinations to resolve status byte 0x90 and the relationship between 21 01 and 21 02.
