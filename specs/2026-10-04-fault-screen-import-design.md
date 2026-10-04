---
title: "Fault-screen import for NanoCom captures (T-30) — design"
area: specs
status: stable
version: 1.0
updated: 2026-10-04
depends_on: [../decisions/adr-0005-nanocom-sniff-workflow.md, 2026-10-04-dtc-coverage-design.md]
summary: >
  Extend the NanoCom capture importer so a labelled fault screen (s <module>/faults + v fault=<as shown>) is paired with the raw fault frame captured on the same screen, per module. It reports which fault-store entries the capture supports, proposes names for set-but-unnamed bits, keeps the raw ACE/EAT blocks for future decoding, and with --write promotes only exact matches from candidate to proven.
---

# Fault-screen import (T-30) — design

## Context

The fault stores (`src/d2diag/dtc/`) hold many `candidate` entries from forum lists. Only a
NanoCom screen read against the raw reply on this car can promote them (T-30). Today
`tools/nanocom_import.py` handles live-data `value` markers only. A fault screen would have
to be matched to its raw frame by hand. This design adds that pairing. The owner approved
the approach on 2026-10-04 ("agree, continue").

## Marker convention

- `s <module>/faults` when the fault screen is open (module = `td5`, `slabs`, `airbag`,
  `autobox` or `ace`).
- `v fault=<exactly as shown>`, one per displayed fault line, for example:
  - `v fault=(12,7) GLOWPLUG LAMP DRIVE OPEN LOAD, (CURRENT)`
  - `v fault=11-05 shuttle valve electrical fail 011 times`
  - `v fault=Code 008 - the drivers airbag measures open circuit (permanent)`
  - `v fault=04-02 DCV 2 Current out of range`
- `v fault=none` when the screen shows no faults. This confirms an empty raw block.

These markers use the existing `screen`/`value` grammar, so `esp32_read.py`'s `s`/`v`
shorthand works unchanged. The live-data importer skips the `fault` name.

## Raw evidence per module

The raw evidence is the latest matching reply seen since the screen marker.

| Module | Raw reply | Decoded with |
|---|---|---|
| td5 | `61 3B` + 35 bytes | set bits; display `(X,Y)`/`X-Y` → bit `(X-1).(Y-1)` |
| slabs | `61 11` (logged) / `61 47` (current) | set bits; the display's first number is a count, so match on text |
| airbag | addressed `… F7 5B 61 02 …` | `airbag.faults.decode_faults`; the display's number = record number |
| autobox | the `72 …` reply | not decoded: raw kept with the displayed codes |
| ace | the `67 …` block | not decoded: raw kept with the displayed codes |

## Verdict per displayed fault

- **Position.** Td5 and airbag: does the displayed code's bit or number appear in the raw
  reply? SLABS has no position in the display, so it uses the text only.
- **Text.** Does the displayed text agree with the store name? Comparison is normalised:
  case, punctuation, "glow plug" vs "glowplug", and the Logged/Current suffix.
- **Outcome:**
  - **Supported:** position and text agree.
  - **Name proposal:** the bit or number is set but has no store name.
  - **Text conflict:** the text disagrees with the store.
  - **Not in raw:** the displayed code's bit or number is absent from the raw reply.
- **Leftovers:** set bits or records with no displayed line are listed (for example the
  Td5 duplicate pairs, or SLABS when only one bit is unexplained).

## Writing (`--write`)

- **Airbag, autobox, ACE.** Their source of truth is the code table in
  `references/<module>_fault_codes.md`, which the seeder rebuilds the store from. So
  `--write` promotes a **supported** row there: Confidence `candidate` → `proven`, and the
  Source cell gets `; proven: nanocom:<capture> (T-30)`. The CLI then reruns the seeder and
  the fault-dictionary generator. Writing the JSON directly would be undone by the next
  seeder run.
- **Td5 and SLABS.** The decoders own the names and confidence (`td5/faults.py`,
  `slabs/faults.py`). The report gives the exact edit to make by hand.
- **Never written automatically:** name proposals and text conflicts. A person reviews them
  first, because NanoCom fault text has known errors (ACE, SLABS corners).
- **Read-only:** the importer reads a log and writes Markdown and JSON. It sends nothing to
  the car.

## Also in scope

`references/fault_capture_runsheet.md`, a one-page field sheet for T-30. It covers screen
order, what to type, the firmware version, the SLABS "times" line, the ACE screen vs TXT
export, and a physical SLABS corner check.

## Verification

Synthetic captures in `tests/test_fault_import.py`:
- a Td5 block with known bits;
- a SLABS anchor block;
- the RDL 016 airbag reply (`61 02 90 04 90 16`);
- an ACE raw block;
- a conflicting text;
- a set-but-unnamed bit;
- `--write` promoting only supported entries in a temporary store.

`pytest -q` must pass.

## Changelog

- 2026-10-04: v1.0.
