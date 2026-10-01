---
title: "ADR-0007 — BCU SecurityAccess: derive offline freely, gate every live byte"
area: decisions
status: locked
version: 1.0
updated: 2026-10-01
summary: >
  The Valeo BCU seed→key may be reverse-engineered offline from clean (seed, key) pairs sniffed off a NanoCom; that derivation is pure maths and unrestricted, but sending any byte to the live BCU for unlock, EKA read or key programming stays behind an explicit confirmation gate and is not built into any default path.
---

# ADR-0007 — BCU SecurityAccess: derive offline freely, gate every live byte

- **Date:** 2026-10-01
- **Status:** accepted

## Context

The Valeo BCU gates its EKA read (`21 CC`) and output/key writes behind KWP2000
SecurityAccess (`27 01` seed → `27 02` key). The seed is two bytes and **rolls every
session** (`references/valeo_bcu_capabilities.md`), so a captured pair never unlocks a
fresh session, and the algorithm `key = f(seed)` is unknown. The earlier conclusion was
to **stop chasing EKA**: the only pairs we had were corrupt (the KKL tap loaded the bus
and flipped bit 7), and a correct key for a rolled seed can only come from a tool that
already knows `f`.

Two things change that. This is the owner's own vehicle (RDL 016), so recovering its
own emergency access is legitimate right-to-repair. And the NanoCom **is** a tool that
knows `f`: sniffing it unlock the BCU, with a high-impedance ESP32 tap that does not
corrupt the frames, yields many clean `(seed, key)` pairs — exactly the corpus that
reverse-engineering `f` needs. Deriving `f` from captured pairs is arithmetic on data
we already hold; it touches no vehicle.

## Decision

Split the work by whether a byte reaches the live BCU.

- **Offline derivation is unrestricted.** `src/d2diag/bcu/keygen.py` ingests captured
  `(seed, key)` pairs and fits a family of candidate transforms, reporting the one that
  reproduces every pair. It opens no port and is covered by hardware-free tests. A model
  is reported only when it fits all pairs **and** there is more evidence than the model
  has free parameters, so a transform is confirmed, not interpolated.
- **Every live SecurityAccess byte is gated.** Sending `27 01`/`27 02` to unlock, reading
  the EKA (`21 CC`), re-setting it (`3B CC …`) or key programming on the live BCU is a
  write/security action. It stays **documented only** and is not wired into any default
  code path, dashboard action or scan. It may be added later only behind an explicit,
  per-action confirmation gate, never automatic, and never as part of a passive capture.
- **Captured key material is never committed.** Raw `(seed, key)` pairs and any recovered
  EKA stay in the gitignored `logs/`/`captures/`. Only the derived algorithm — the fitted
  transform — is committed, never the pairs or a code.
- This ADR narrows, for the offline case, the earlier "stop chasing EKA" note in
  `references/valeo_bcu_capabilities.md`: derivation from clean NanoCom pairs is now in
  scope. The live unlock remains out of scope until it has its own gate.

## Consequences

- We can determine `f(seed)` the moment clean pairs exist, with no vehicle risk.
- The dangerous half (unlock, EKA, key programming) has one rule and one place it is
  allowed to live, so it cannot creep into a default path by accident.
- A locked BCU still carries a brick risk if written blindly; keeping writes gated and
  documented preserves the project's read-only-by-default posture (CONSTITUTION.md).

## Alternatives considered

- **Build the on-car unlock now.** Rejected for this pass: the offline keygen is the
  whole win with none of the risk, and the live path deserves its own deliberate gate.
- **Bench EEPROM read of the BCU (93C56/95xxx) to recover the EKA directly.** Kept as a
  documented invasive fallback only, if the algorithm resists derivation.
- **Brute force.** Inappropriate — a rolling seed plus a likely attempt counter/lockout.
