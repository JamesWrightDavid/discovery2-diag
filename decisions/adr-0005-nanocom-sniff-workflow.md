---
title: "ADR-0005 — NanoCom capture: passive sniff, label, candidate-only"
area: decisions
status: locked
version: 1.0
updated: 2026-09-30
summary: >
  Full-coverage mapping is done by passively sniffing a rented NanoCom with the ESP32 tap, labelling each capture against the tool's screen, and importing results as kandidat only; nothing sniffed is replayed as a write without its own ADR.
---

# ADR-0005 — NanoCom capture: passive sniff, label, candidate-only

- **Date:** 2026-09-30
- **Status:** accepted

## Context

Only Td5, SLABS and BCU connect are proven. ACE, EAT, airbag, BCU outputs and BCU
SecurityAccess are open. A reference tool that talks to every module is the fastest way
to get the request/response bytes. Its screen gives the plaintext values that
`sniff/automap.py` needs. Earlier borrowed-tool sessions showed that operator markers
land mid-stream and must be anchored by traffic regime.

## Decision

Sniff the rented NanoCom passively with the ESP32 RX-only tap on pin 7. Use the existing
`[ms] hh hh…` log with `>>> marker` lines.
- For every screen, record a marker and the plaintext values shown.
- Hold a steady state, and change one input at a time.
- Before the rental, extend module detection in `sniff/` to cover BCU, airbag, ACE and
  EAT.
- Add an importer that turns capture + labels into automap pairs. Results enter the
  signal store as `kandidat`, with the capture ID as provenance.
- Raw captures stay out of git (they may contain VIN or EKA data). Only derived facts
  are committed.
- Write, coding, security and actuator commands learned this way are documented but
  never sent by this tool without a dedicated ADR and a confirmation gate. Airbag stays
  read-only.

## Consequences

- Coverage grows quickly with honest confidence.
- The rental time is spent on a pre-written capture checklist
  (`references/test_plan.md`), not on exploration.
- BCU seed→key may still need several denied samples. This is acceptable.

## Alternatives considered

- Active LID sweeping without a tool. Rejected: slow, gives no plaintext oracle, and
  risks the SLABS session limits.
- Replaying the tool's traffic verbatim. Rejected: unsafe for write and security
  services.
