---
title: "Reply-length layouts (Td5 21 1B short vs long) — Design"
area: specs
status: stable
version: 1.0
updated: 2026-10-04
depends_on: [references/test_plan.md, references/td5-external-findings.md]
summary: >
  Let a signal-store record apply only to replies of one data length, so a LID whose layout
  differs between ECU variants (Td5 21 1B: 8 bytes on RDL 016, 10 bytes on D2-JW) decodes
  correctly on both cars. One optional `length` field, enforced in Signal.fits().
---

# Reply-length layouts — Design

## Problem

`21 1B` (accelerator pedal) has two layouts depending on the ECU variant (T-31, 2026-10-04):

| Data bytes | Car | @0 | @2 | @4 | @6 | @8 |
|---|---|---|---|---|---|---|
| 8 (short, "MSB") | RDL 016 | track 1 | track 2 | pedal % | supply | — |
| 10 (long, "NNN") | D2-JW | track 1 | track 2 | track 3 | pedal % | supply |

The store holds one offset per field, so whichever car it was mapped on decodes right and
the other decodes wrong: on D2-JW the old map showed a 0 V pedal supply. The store now
follows D2-JW, so RDL 016's short reply loses its supply and shows its pedal % as "track 3".

## Design

1. **Store:** an optional record field `length` = the exact data length (bytes after
   `61 <lid>`) the record applies to. Absent = any length (every existing record).
2. **`Signal.length: int | None = None`**, and `Signal.fits(data)` also requires
   `len(data) == length` when set. Every decoder already filters on `fits()` (`decode_lid`,
   the SLABS source, `sniff/decoder.py`), so they pick the right variant with no other change.
3. **Variants share a name.** A field may have one record per length (same `name`,
   different `offset`/`length`). `upsert_field` already keys on `(lid, offset, name)`, so both
   coexist. Fields with no counterpart in a layout simply have no record for it
   (`accel_way3` has no short-form record).
4. **Consumers that list fields** (`/fields`, `BY_NAME`, `LIMITS`) de-duplicate by name,
   first record wins (variants must share unit, limits and metadata — a store test enforces it).
5. **ESP32 header:** unchanged. It only uses track 1 (`@0`, same in both layouts); the
   generator skips `length`-restricted records and a test pins that.

## `21 1B` records after the change

| name | short (length 8) | long (length 10) |
|---|---|---|
| accel_way1 | @0 (no length — same in both) | |
| accel_way2 | @2 (no length) | |
| accel_way3 | — | @4 |
| accel_pedal_pct | @4 | @6 |
| accel_supply | @6 | @8 |

Confidence per record follows its own evidence: the long-form records are proven on D2-JW;
the short-form `accel_supply` keeps RDL 016's 2026-08 proof; the short-form `accel_pedal_pct`
is **candidate** (RDL 016's `0 -> 2.23 V` reading, reinterpreted, never re-read as %).

## Tests

- `fits()` honours `length`; `decode_lid` on RDL 016's recorded short frame
  (`02 86 11 1c 00 00 13 92`) gives supply 5.01 V and no `accel_way3`; on D2-JW's long frame
  (`02 ac 10 e3 12 19 00 00 13 72`) supply 4.98 V, way3 4.63 V, pedal 0 %.
- Variants of one name share unit/limits/label; `/fields` lists each name once.
- Header generator ignores `length` records.

## Out of scope

Any other LID. If another layout split turns up, it uses the same `length` field.
