---
title: "BCU SecurityAccess — research and the offline path to the seed→key"
area: references
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [valeo_bcu_capabilities.md]
summary: >
  How the Valeo BCU SecurityAccess works, why past pairs could not crack it, and the offline derivation path the NanoCom unblocks: sniff clean (seed, key) pairs, fit the transform with bcu/keygen.py, keep every live byte gated (ADR-0007).
---

# BCU SecurityAccess — research and the offline path to the seed→key

What is **proven** about the Valeo BCU's SecurityAccess, why we previously stopped, and
the one thing that changes it: a NanoCom that knows the algorithm. The protocol facts and
the "stop chasing EKA" history are in
[valeo_bcu_capabilities.md](valeo_bcu_capabilities.md); this page is the plan to get
`key = f(seed)` honestly. The rule for live bytes is fixed in
[../decisions/adr-0007-bcu-security-access.md](../decisions/adr-0007-bcu-security-access.md).

## The protocol (proven)

Standard KWP2000 SecurityAccess, gated in front of the EKA read:

| Step | Bytes | Note |
|---|---|---|
| Request seed | `27 01` → `67 01 <hi> <lo>` | 2-byte seed, **rolls per session** |
| Send key | `27 02 <hi> <lo>` → `67 02` (ok) / `7F 27 35` (invalidKey) | |
| Read EKA | `21 CC` (after unlock) | without unlock returns the current seed, not the code |

The seed being two bytes makes the key space 65536 — small enough that a **fixed
transform** (affine, rotate-and-XOR rounds, an LFSR as in the Td5, a byte swap, a small
lookup) is recoverable from a handful of correct pairs. The references for seed-key families:
the [Colorado State seed-key study](https://www.engr.colostate.edu/~jdaily/presentations/2017%20Seed%20Key%20Exchange.pdf)
and a [UDS seed-key write-up](https://medium.com/@mkklyci/uds-seed-key-algorithm-764d5067d90c).

## Why the old pairs could not crack it

1. **Rolling seed.** An old `(seed, key)` pair never unlocks a new session, so a single
   pair is worthless for live use — but it is still a data point for deriving `f`.
2. **No clean keys.** The key for a rolled seed can only be computed by something that
   already knows `f`. We could capture seeds all day but never the matching keys.
3. **Corrupt captures.** The cheap KKL cable, used as a passive tap, **loads the bus** and
   flips bit 7 on the BCU's response frames, so even the few pairs we sniffed were damaged
   (`EB CD → C0 10`, denied; `4A 8A` with no seed; `4B 5C` with a corrupt seed).

## What the NanoCom changes

The NanoCom computes the correct key for each rolled seed — it **is** the tool that knows
`f`. Sniffing it unlock the BCU gives many clean `(seed, key)` pairs in one session. Two
conditions make them usable, both already met by this project's rig:

- **High-impedance tap.** The ESP32 BC337 tap (220 kΩ into the transistor base) does not
  load the bus the way the KKL cable did, so the seed and key frames arrive intact.
  Validate every frame's checksum on import and discard any that fail — a corrupt pair
  poisons the fit.
- **Volume.** Capture the unlock several times so the seeds vary; the derivation needs
  more pairs than the transform has free parameters to confirm (not merely interpolate).

## The offline derivation

`src/d2diag/bcu/keygen.py` is the harness. Feed it the clean pairs; it tries, simplest
first: identity, XOR-mask, add-constant, byte-swap-plus-XOR, the Td5 LFSR, rotate-left-
plus-XOR, and affine (`key = a·seed + b mod 2¹⁶`, `a` odd). It reports the first family
that reproduces **every** pair, with its parameters, or says no family fits. A
hardware-free test pins each family by recovering it from synthetic pairs, and confirms
that unstructured pairs report no fit. This is pure maths on captured data — no port, no
car (ADR-0007).

If no family fits, widen the search (more rounds, a larger lookup) or fall back to the
documented invasive route: a bench EEPROM read of the BCU (93C56/95xxx) recovers the EKA
directly, offline.

## What stays gated

Deriving and testing `f` offline is free. Sending any byte to the **live** BCU — the
`27 01`/`27 02` unlock, the `21 CC` EKA read, the `3B CC` re-set, key programming — is a
security/write action, documented only, behind an explicit confirmation gate, never
automatic and never part of a passive capture (ADR-0007). Raw pairs and any recovered EKA
stay in the gitignored `logs/`/`captures/`; only the fitted algorithm is committed.

## Decision tree

1. Clean pairs captured (checksums valid, seeds vary)? → run `bcu/keygen.py`.
2. A family fits all pairs with evidence to spare? → commit the algorithm (not the pairs).
   On-car verification of the derived key is **T-28**, gated.
3. No family fits? → widen the search, or plan a bench EEPROM read.
