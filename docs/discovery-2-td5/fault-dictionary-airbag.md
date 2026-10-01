---
title: "Airbag (SRS) fault dictionary"
area: docs
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Generated fault dictionary for the airbag module — every known code with its meaning, likely cause, severity and (inferred) P-code. Generated from src/d2diag/dtc/airbag.json; do not hand-edit.
---


# Airbag (SRS) fault dictionary

_Generated from the fault-meaning store (`src/d2diag/dtc/airbag.json`) — do not edit by hand; refine the store and re-run `tools/gen_fault_docs.py`._

| Code | Fault | P-code | Severity | Meaning | Likely cause |
|---|---|---|---|---|---|
| `004` | SRS fault 004 | — | logged | Airbag (TRW SPS) fault 004, seen on RDL016 with status 0x90 (open-circuit intermittent). | Circuit meaning not yet mapped — needs the RAVE SRS fault table or a labelled capture. Airbag is read-only; investigate, never actuate. |
| `022` | SRS fault 022 | — | logged | Airbag (TRW SPS) fault 022, seen on RDL016 with status 0x90 (open-circuit intermittent). | Circuit meaning not yet mapped — needs the RAVE SRS fault table or a labelled capture. Airbag is read-only; investigate, never actuate. |

