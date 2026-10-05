---
title: "SRS (airbag) fault dictionary"
area: docs
status: stable
version: 1.0
updated: 2026-10-04
summary: >
  Generated fault dictionary for the airbag module — every known code with its meaning, likely cause, severity and (inferred) P-code. Generated from src/d2diag/dtc/airbag.json; do not hand-edit.
---


# SRS (airbag) fault dictionary

_Generated from the fault-meaning store (`src/d2diag/dtc/airbag.json`) — do not edit by hand; refine the store and re-run `tools/gen_fault_docs.py`._

| Code | Fault | Confidence | P-code | Severity | Meaning | Likely cause |
|---|---|---|---|---|---|---|
| `004` | Airbag warning lamp circuit, open circuit | candidate | — | — | SRS (airbag, TRW SPS) fault 004: Airbag warning lamp circuit, open circuit. | Read-only module: investigate the named circuit (connectors, rotary coupler, under-seat plugs); never actuate. |
| `008` | Driver's airbag circuit, open circuit | candidate | — | — | SRS (airbag, TRW SPS) fault 008: Driver's airbag circuit, open circuit. | Read-only module: investigate the named circuit (connectors, rotary coupler, under-seat plugs); never actuate. |
| `022` | Left-hand seat-belt pretensioner circuit, open circuit | candidate | — | — | SRS (airbag, TRW SPS) fault 022: Left-hand seat-belt pretensioner circuit, open circuit. | Read-only module: investigate the named circuit (connectors, rotary coupler, under-seat plugs); never actuate. |
| `023` | Right-hand seat-belt pretensioner circuit, short to ground | candidate | — | — | SRS (airbag, TRW SPS) fault 023: Right-hand seat-belt pretensioner circuit, short to ground. | Read-only module: investigate the named circuit (connectors, rotary coupler, under-seat plugs); never actuate. |

