---
title: "DTC coverage — every documented fault code in the store, honestly — design"
area: specs
status: stable
version: 1.2
updated: 2026-10-04
depends_on: [../CONSTITUTION.md, ../decisions/adr-0006-english-confidence-vocabulary.md]
summary: >
  Design for filling the fault-meaning store (src/d2diag/dtc/) from public forum lists: a confidence field on every meaning, one forum-named Td5 bit (20.7) after verifying the forum X-Y to offset.bit mapping, new airbag/autobox/ace stores keyed by display code, and re-keying the rswsolutions SLABS list because its numbering contradicts both car-proven anchors.
---

# DTC coverage — design

## Context

The owner asked for every documented fault code to be in the app, with the rule that a
wrong label is worse than an honest unknown. Before this work the store held: Td5 210 bits
(of 280), SLABS 63 (rswsolutions list), airbag 2 (unnamed), autobox 0, ACE 0. The approach
was set by the owner's brief; this spec records the decisions made while doing it.

## Decisions

### 1. A `confidence` field on every meaning

`FaultMeaning` gains `confidence`: `proven` (the code→meaning pairing was seen on this car
or on the reference tool's screen against a raw capture) or `candidate` (from a forum or
vendor list, not car-confirmed). It is optional in the JSON (blank = unspecified) so old
records still load. Everything added from forums is `candidate`. Nothing is promoted to
`proven` without a car result (CONSTITUTION, confidence is honest). The `Fault` record in
`td5/faults.py` gets the same field (default `proven`, matching its docstring), and
`td5/faultmap.json` lists any candidate bits under a `candidate` key.

### 2. Td5: verify the X-Y mapping, then fill only what a source names

Forum lists use 1-indexed `X-Y` (byte, bit). Our key is `offset.bit`, 0-indexed. The
mapping `X-Y → (X-1).(Y-1)` is accepted only after a mechanical diff against all 210
existing named bits, comparing both the text and the Logged/Current marker. A bit is added
only if a list names it explicitly. Bits no list names (including `15.7`, seen set on the
car) stay unnamed, so the decoder keeps reporting `byte<off>.bit<n>`. They are recorded as
the backlog in `references/td5_fault_codes.md`.

### 3. New stores for airbag, autobox (EAT) and ACE, keyed by display code

These modules have no raw block offsets yet, so the store is keyed by what the tools
display:

- **airbag**: 3-digit number (`008`). Our decoder already yields this number (proven).
- **autobox**: P-code plus the gearbox's internal fault number (`P1884-33`).
  - One P-code covers several faults (P1884 has seven CAN messages). The internal number
    (1–39) tells them apart, and the tools display it (Hawkeye `P1884-33`, NanoCom
    `P1884 19`).
  - A plain P-code key would merge different faults.
- **ace**: three display schemes exist and must not be merged:
  - NanoCom's component-grouped `XX-YY` (the family this car's tool shows) owns the plain
    keys (`04-02`);
  - NanoCom's flat-list family is keyed `flat-XX-YY`;
  - Hawkeye/Testbook DTCs are keyed `dtcNN`.

  The same text appears under different numbers across the families, so no scheme is
  mapped onto another.

Only pairings read first-hand on a fetched page are stored. Search-engine summaries are
not used, because one misattributed a Td5 code during this work. Vehicles other than the
Discovery 2 are excluded. The files are named after the UI module ids (`autobox`, `ace`),
and `/faults` accepts `eat`/`gearbox` as aliases.

### 4. SLABS: re-key the rswsolutions list

Both car-proven anchors contradict the rswsolutions numbering:

| Reference tool (car) | rswsolutions number for that same fault |
|---|---|
| `020` right front wheel-speed sensor, output too low | `044` (and rsw `020` = no battery supply) |
| `027` shuttle valve switch, electrical failure | `114` (and rsw has no `027`) |

So the rsw numbers are a different numbering scheme. Keyed as display numbers, they put
the wrong meaning on this car's real fault `020`. The rsw records move to `rsw-NNN` keys
(fault-type knowledge kept, no collision with tool numbers) as `candidate`. The two
anchors get `proven` records under their real tool numbers. The SLABS decoder is unchanged.

### 5. Surfaces

The seeder (`tools/gen_dtc_seed.py`) gains builders for the new modules, reading tables
from the per-module reference docs, so the docs stay the single place where sources are
listed. The generated fault dictionary pages, `/faults`, the UI fixtures and the tests
follow.

## Out of scope

Anything that writes to the car. Decoding the EAT `72`-framed payload or the ACE bulk block.
UI changes beyond the response shape (the UI's Zod schema ignores the new field until a
badge is designed).

## Verification

`pytest -q` passes. A test checks that every record in each store has a `confidence`
value, that no forum-sourced record is `proven`, that the airbag `004`/`022` keys and the
SLABS anchors resolve, and that `/faults?module=autobox|ace|eat` serves the new stores.

## Changelog

- 2026-10-04: v1.0, written alongside the implementation from the owner's brief.
- 2026-10-04: v1.1. A second research pass (one agent per gap) found this car's ACE
  NanoCom family, so plain ACE keys now mean that family and the earlier flat-list codes
  move to `flat-XX-YY`. The fault dictionary index gains a total-per-module column.
- 2026-10-04: v1.2. A third pass with exact-phrase queries built from known tool wording.
  A NanoCom screen corrects the Td5 decoder name at `13.6` (glow-plug lamp, not a second
  "relay"); `13.6` and the identical `11.6` become candidate. The NanoCom SLABS first field
  is shown to be an occurrence count. ACE gains `flat-41-07`.
