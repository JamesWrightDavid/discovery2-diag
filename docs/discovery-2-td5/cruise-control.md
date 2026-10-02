---
title: "Cruise control (Hella) — unconfirmed module"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
summary: >
  Hella cruise-control module stub: community-asserted on the K-line, nothing proven yet. Address and init to be confirmed by the read-only scan (T-26); faults to be decoded from a NanoCom capture (T-25).
---

# Cruise control (Hella) — unconfirmed module

🔴 **Unconfirmed.** The Discovery 2's cruise control is a Hella module that the
community places on the shared K-line, and the NanoCom lists up to 41 cruise fault codes
for it. This project has **no** proven address, init or traffic for it yet — this page is
a stub to fill once the rental and scan produce evidence.

## What we expect

- A diagnostic address answering either fast init or a 5-baud wake, like the other
  non-engine modules. The read-only scan (`tools/module_scan.py`, T-26) walks the
  candidate addresses and records who answers with which key bytes, to confirm or rule
  out cruise before the rental spends time on it.
- Faults in the usual KWP shape (`18`/`21` read, `14` clear) if it is a KWP module.

## How this page gets filled

1. **T-26 (scan).** Run `tools/module_scan.py` and note any address that responds and is
   not already a known module — a candidate for cruise.
2. **T-25 (capture).** On the NanoCom, open the cruise **Faults** screen and any live
   data, marking `screen cruise/...` and `value ...` (see
   [nanocom_capture_protocol.md](../../references/nanocom_capture_protocol.md)). Import
   with `tools/nanocom_import.py`.
3. Record the confirmed address/init in [kline-protocol.md](kline-protocol.md) and the
   per-module summary; promote this page from draft once there is car evidence.

Until then, treat cruise as **not present/decoded**. See the
[system map](system-map.md) for where it sits among the modules.
