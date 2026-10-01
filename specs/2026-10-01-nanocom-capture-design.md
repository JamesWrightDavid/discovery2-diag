---
title: "NanoCom capture readiness + full system map — design"
area: specs
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [../decisions/adr-0005-nanocom-sniff-workflow.md, ../decisions/adr-0007-bcu-security-access.md]
summary: >
  Design for the tooling that makes a NanoCom rental pay off: all-bus module detection, a labelled-capture importer, a read-only address scan, and an offline BCU seed→key harness — plus the canonical system map. Candidate-only imports; every live write stays gated.
---

# NanoCom capture readiness + full system map — design

## Context

The owner will rent a NanoCom Evolution to learn every Discovery 2 module's protocol by
passively sniffing it (ADR-0005), and wants every system on the car mapped and reachable.
Today the tooling only detects Td5 and SLABS, nothing turns a labelled capture into
`automap` input, the asserted-only modules (cruise, HEVAC, IDM, instrument pack) are
unconfirmed, and the BCU seed→key is unknown. This design adds the pieces so one rental
session converts into candidate mappings across **all** supported modules, and sets up the
offline-only path to BCU full access. Nothing here sends a byte to the car.

## Approach

### 1. Module detection for every bus — `src/d2diag/sniff/modules.py`
One table both `capture.py` and `decoder.py` use (replacing their two-entry fast-init
dicts). Detects fast init (`0x13`/`0x29`), the airbag's addressed framing (`0x5B`), the
EAT `72` framing (XOR-closed request / `72 … 60` response), ACE bulk pairs, and the BCU
EKA identifier (`21`/`3B CC`). Unknown fast-init addresses become `unknown:0xNN`, never
dropped. A `ModuleTracker` applies an authority policy: real inits always switch the
active module; weaker content hints only seed an as-yet-unknown module, so a stray `0x72`
byte in a Td5 frame never flips the module to the gearbox.

### 2. Capture labelling — `tools/esp32_read.py` + the runbook
Structured markers the importer reads: `s <module>/<page>` → `screen …`, `v <name>=<text>`
→ `value …` (shorthand expands before logging). `references/nanocom_capture_protocol.md`
is the session runbook — passive tap wiring, per-module screen order and budget, hold each
screen ~10 s, change one input at a time, and the rule that every write/security/coding
frame is recorded but never replayed. It becomes **T-25** in the test plan.

### 3. Importer — `src/d2diag/sniff/importer.py` + `tools/nanocom_import.py`
Reads a labelled capture, anchors each `value` to the latest `61 <lid>` responses since
its `screen` marker, groups `(plaintext, raws-by-LID)` samples per named value, and runs
the existing `automap.solve` unchanged. Prints a markdown report; `--write` persists each
solved mapping as a **candidate** via `upsert_field`, the capture name as provenance. A
synthetic capture built from known Td5 LIDs reproduces the proven rpm/battery/coolant
mappings in tests.

### 4. Read-only address scan — `src/d2diag/modscan.py` + `tools/module_scan.py`
Walks fast-init and 5-baud addresses, records each responder's key bytes, and **sends only
init + StopCommunication**, releasing after every probe (CONSTITUTION.md). Confirms or
rules out cruise, HEVAC, instrument pack, IDM and the `0x18` responder before the rental.
Tested against `FakeKLineEcu`: detects a responder, tags unknown addresses, and emits no
read/write service byte. Becomes **T-26**.

### 5. BCU offline keygen — `src/d2diag/bcu/keygen.py`
Offline-only derivation harness: ingest clean `(seed, key)` pairs sniffed from the
NanoCom, fit a family of transforms (identity, XOR-mask, add-const, byte-swap-XOR, Td5
LFSR, rotate-XOR, affine), report the simplest that reproduces every pair — confirmed only
with more evidence than free parameters. Pure maths, no port. The on-car unlock/EKA/key
work stays **documented only** and gated (ADR-0007). Research in
`references/bcu_security_research.md`; new items **T-27** (capture pairs) and **T-28**
(verify a derived key on-car, gated).

### 6. Canonical system map — `docs/discovery-2-td5/system-map.md` + cruise stub
The single list of every module, address, what the NanoCom exposes and the access goal,
linking each module page. A `cruise-control.md` stub holds the unconfirmed Hella module.

## Scope decisions (confirmed)

- **BCU: offline keygen only.** No on-car unlock/EKA/key byte is built this pass.
- **All supported modules** in one pass: core four (Td5, SLABS, BCU, airbag) plus
  autobox, ACE and cruise.

## Verification

- `pytest -q`: module detection per bus, the importer (synthetic capture → right
  LID/offset/scale, decoy LID rejected, `--write` lands candidates), the scanner (only
  init + `82` sent), and the keygen (synthetic transforms recovered; unstructured pairs
  report no fit).
- `validate_frontmatter.py`, `check_links.py`, `build_index.py`; CI green.
- Dry run: `tools/nanocom_import.py` over `ui/e2e/sniff-demo.txt` (reports no labelled
  values, as expected) and a real capture once one exists.

## Changelog

- 2026-10-01 — Initial design (ADR-0005 implementation; ADR-0007 for BCU security).
