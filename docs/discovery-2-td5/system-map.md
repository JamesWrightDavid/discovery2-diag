---
title: "Discovery 2 Td5 — system map (every module, address, access)"
area: docs
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  The single canonical list of every Discovery 2 Td5 K-line module: address, init, what the NanoCom exposes, what this project can read today and the access goal for each. Links each module's page.
---

# Discovery 2 Td5 — system map

The one place that lists **every** module on the Discovery 2 Td5 K-line, what a NanoCom
exposes for it, and how far this project can reach it. Each row links its detailed page.
Per-module status (🟢 proven · 🟡 assumed · 🔴 open) stays on those pages and in
[README.md](README.md); this is the map, not the detail.

The bus is a shared multi-drop K-line (pin 7, 10 400 baud, ISO 14230 KWP2000), not a
gateway — one module at a time, each released cleanly. Framing and init live in
[kline-protocol.md](kline-protocol.md).

## The modules

| System | ECU | Address / init | On K-line | NanoCom exposes | This project today | Access goal |
|---|---|---|---|---|---|---|
| Engine | Lucas Td5 | `0x13` fast | 🟢 proven | live, faults, outputs, injector codes, settings, security learn | ~20 live signals, faults, outputs, injector tests | finish switch bits (1E/36), settings block, injector codes (read-only) — [engine-td5.md](engine-td5.md) |
| Brakes / height | Wabco SLABS | `0x29` fast | 🟢 proven | faults, inputs, outputs, height calibration, bleed | heights, wheel speeds, faults, ABS bleed | analog scalings, settings LIDs, lamp tests, calibration (gated) — [slabs.md](slabs.md) |
| Body / immobiliser | Valeo BCU | `0x40` 5-baud | 🟢 proven | inputs, settings, outputs, EKA, key programming | connect, immobiliser status, identity | input/output/settings bits; **derive seed→key offline** (ADR-0007) — [bcu.md](bcu.md) |
| Airbag | TRW SPS | `0x5B` addressed | 🟢 proven | 37 faults, settings | fault read (addressed framing) | verify decode on the car; stays **read-only** — [other-modules.md](other-modules.md) |
| Gearbox | Bosch EAT (GS8.87) | `72`-framed | 🟢 proven | faults, limited live data | read/clear faults (payload unknown) | fault + payload decode, inputs — [other-modules.md](other-modules.md) |
| Active roll | Lucas ACE | unresolved | 🟡 asserted | faults, live data, outputs, bleed | fault block isolated | address/init, faults, inputs (needs ACE enabled) — [other-modules.md](other-modules.md) |
| Cruise | in the Td5 ECU (Hella is V8 only) | — | 🟢 no separate module: vendor doc + D2-JW address sweep (T-26) | via Td5 faults, inputs, settings | Td5 cruise faults decoded, cruise switches proven | decode the cruise-group bits `21.3/21.5/25.3/25.5` — [cruise-control.md](cruise-control.md) |
| HEVAC, instrument pack, IDM | — | asserted only | 🔴 unconfirmed | not in the Td5 kit | nothing | address scan (T-26) to confirm or rule out; else read via BCU inputs |
| Engine (petrol) | Bosch Motronic V8 | n/a on a Td5 | — | separate kit (NCOM04) | out of scope | roadmap — [rover-v8](../rover-v8/) |

## How coverage grows

The NanoCom rental is the lever: one passive-sniff session yields the request/response
bytes plus the tool's plaintext for every module it supports, which
[`tools/nanocom_import.py`](../../references/nanocom_capture_protocol.md) turns into
`candidate` signal-store mappings. The capture runbook is
[nanocom_capture_protocol.md](../../references/nanocom_capture_protocol.md); the open
items and decision rules are in [test_plan.md](../../references/test_plan.md) (T-25…T-28).

Addresses that are only community-asserted (cruise, HEVAC, instrument pack, IDM, the
`0x18` responder) are confirmed or ruled out before the rental by the read-only address
scan, `tools/module_scan.py` (T-26). BCU full access — the EKA via the seed→key — follows
the offline-only path in
[bcu_security_research.md](../../references/bcu_security_research.md) and ADR-0007.
