---
title: "Cruise control — handled by the Td5 engine ECU, no separate module"
area: docs
status: draft
version: 1.1
updated: 2026-10-04
summary: >
  On the Discovery 2 Td5, cruise control is run by the engine ECU, not a separate Hella module (vendor documentation); the Hella unit with 41 faults is the petrol V8's. Cruise faults, switches and settings live in the Td5 fault block and live data. The read-only scan (T-26) can still confirm no extra module answers.
---

# Cruise control — handled by the Td5 engine ECU

🟡 **Resolved on vendor documentation (2026-10-04), not yet on the car.** The NanoCom
vendor's Discovery II page says the Td5's cruise control is run by the engine ECU and is
not a separate ECU: "Discovery II TD5 cruise control is managed by the engine-management
ECU; it is not a separate ECU" (https://www.blackbox-solutions.com/site/nanocom). The Hella
module, with its 41 fault codes, is listed for the **petrol V8 Discovery II only** (kit
NCOM04). That matches the NanoCom emulator showing cruise only under the V8 branch
([menus/cruise.md](../../references/menus/cruise.md)).

So on this car, cruise lives in the Td5 engine ECU:
- **Faults:** in the Td5 fault block, for example `21.6`/`21.7` "cruise control
  resume/set stuck closed" and `25.1` "cruise control system problem"
  ([fault-dictionary-td5.md](fault-dictionary-td5.md)).
- **Switches:** SET+, RES and Master, which the vendor's Td5 guide lists as engine-ECU
  pins and inputs.
- **Settings:** "cruise control enabled" and "cruise lamp" in the Td5 settings.

The page below is kept as the plan in case the scan finds anything unexpected.

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

Until then, treat cruise as part of the Td5 engine ECU, as the vendor documents it. See the
[system map](system-map.md) for where it sits among the modules.
