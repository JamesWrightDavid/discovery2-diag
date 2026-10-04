---
title: "Discovery 2 airbag (TRW SPS 2A) — fault codes"
area: references
status: draft
version: 1.0
updated: 2026-10-04
summary: >
  Airbag/SRS display codes (3-digit numbers, which the decoder already yields from the raw 21 02 records), compiled from this car's baseline read and first-hand Discovery 2 forum pages as candidate; read-only module.
---

# Discovery 2 airbag (TRW SPS 2A) — fault codes

Display codes for the airbag ECU. They seed `src/d2diag/dtc/airbag.json` through
`tools/gen_dtc_seed.py`, which reads the table below. **Read-only module**: this project
never clears, actuates or writes to it (CONSTITUTION, Safety).

## Raw encoding status

**Fault number decoded; number→circuit text mostly undocumented.** Unlike the other
modules, the raw format is proven: `21 02` returns 2-byte `[status][number]` records, and the
number *is* the tool's display code (`90 04` = 004, `90 16` = 022). See
`src/d2diag/airbag/faults.py`. So a stored key resolves directly against a live read. What
is missing is the text for most numbers, and the meaning of the status bits (only `0x90` has
been observed).

The tools show a state word after the text:
- "permanent" seems to mean present now;
- "intermittent" seems to mean seen before, not present now.

On one Discovery 2, replacing the rotary coupler turned 008 from permanent to intermittent.
That is one observation, not a decoded status bit.

## Codes

| Code | Fault | Confidence | Source |
|---|---|---|---|
| `004` | Airbag warning lamp circuit, open circuit | candidate | RDL 016 baseline read 2026-08-07 (docs/discovery-2-td5/fault-codes.md) showed "warning lamp open circuit" and "LH pretensioner open circuit"; raw re-read 2026-08-10 gave 004 + 022. Pairing by elimination, since 022 is the LH pretensioner. A P38 thread shows 004 with no circuit named: https://www.landyzone.co.uk/land-rover/srs-error-004-open-circuit.383085/ |
| `008` | Driver's airbag circuit, open circuit | candidate | NanoCom, 2003 Discovery 2: https://www.landyzone.co.uk/land-rover/srs-light.385858/ |
| `022` | Left-hand seat-belt pretensioner circuit, open circuit | candidate | thread title, Discovery 2 forum: https://www.aulro.com/afvb/discovery-2-a/260850-code-022-left-hand-pretensioner-measures-open-circuit-permanent.html ; also the RDL 016 baseline read |
| `023` | Right-hand seat-belt pretensioner circuit, short to ground | candidate | Discovery 2: https://www.landyzone.co.uk/land-rover/seat-belt-pretensioner-gone-off.294442/ |

`004` and `022` are this car's own faults. They stay `candidate` until one session
photographs the tool screen (number + text) while the raw `61 02` frame is captured. That
promotes both to `proven` (test plan T-25).

## Backlog (not stored)

- Every other number, up to the 1–65 range the register's string dump covers. That
  register is not in this repository.
- `032`: "right-hand pretensioner open circuit", found only in a search snippet.
- `018`: a P38 page, wording doubtful.
- P38-only codes: the P38 also uses a TRW module and 008 reads the same on both, but no
  source says the tables are identical.
