---
title: "Capture run-sheet — pipeline demo → BCU mapping session"
area: references
status: stable
version: 1.1
updated: 2026-10-05
summary: >
  Printable field run-sheet for on-car mapping. Part A proves the capture→automap→store
  pipeline with the KKL cable alone (no NanoCom) on Td5/SLABS switch inputs; Part B is the
  full BCU read-inputs session with the NanoCom as the oracle. Matches the Capture/Map tabs
  and the read-only safety rules.
---

# Capture run-sheet — pipeline demo → BCU mapping session

Two sessions, in order. **Part A** proves the whole mapping loop with just the KKL cable —
do this first. **Part B** is the full BCU session once the NanoCom is rented. The method is
the same both times: read a value, change one physical thing, read again, label what changed.

Background: the rig and session template are in
[nanocom_capture_protocol.md](nanocom_capture_protocol.md); the per-module plan and the
induce-a-known-fault trick are in [reference_tool_sniff_plan.md](reference_tool_sniff_plan.md);
the BCU field lists are in [menus/bcu-inputs.md](menus/bcu-inputs.md); priorities are in
[nanocom/feature_map.md](nanocom/feature_map.md).

## ⚠️ Safety — read before every session

- **Read-only.** Only ever *read* and *clear faults*. No settings writes, no output tests.
- **The sniffer stays RX-only.** Use the ESP32 tap (`esp32/kline_sniff`) — no TX wire — or a
  KKL cable in listen-only. Never let the tap transmit.
- **BCU: never** EKA / key programming / security outputs — these can **lock the car**, and a
  locked BCU cannot be unlocked by diagnostics.
- **Airbag: never** run outputs/actuator tests (pyrotechnics). Fault codes only.
- **SLABS: never** "store target heights"; never run brake-affecting bleeds except deliberately.
- Stationary, handbrake on, **ignition on / engine off** (SLABS drops comms once moving).
- Never interrupt a tool mid-write. If anything freezes, stop — don't spam buttons.

## Rig

| | Part A (demo) | Part B (BCU + NanoCom) |
|---|---|---|
| Cable | KKL on OBD **pin 7** (+ pin 4/5 gnd, pin 16 12V) | **Y-cable**: NanoCom one branch, ESP32 RX tap the other |
| Sniffer | optional (d2diag reads directly) | **ESP32 RX-only** on pin 7 (passive) |
| App | `PYTHONPATH=src python3 tools/dashboard.py --serial auto` → `/admin` | add `--sniff <esp32-port-or-feed>` ; `/admin` |
| Logging | `--raw-log` → `logs/raw-<module>-<time>.log` | same; one file per module |

**Validate the rig first (both parts):** connect the **Td5 engine**, Faults → Read. Confirm
the log shows `81 13 F7 81 …` → `C1 57 8F`. If that's there, the rig + annotation are proven.

---

## Part A — Pipeline demo (KKL only, NO NanoCom)

Goal: watch one real field go grey → yellow → green on the module's pages (Experimental mode, coverage bar), proving the
loop, before spending on the rental. Uses inputs d2diag can already read directly.

**Loop per field (differential):**
1. Connect the module (header module dropdown; the connection pill opens the connection sheet).
2. **Capture tab → "Read a LID directly"**: enter the LID, **Read** (baseline). Note the hex.
3. **Change one physical thing** (below). Read the same LID again.
4. The byte/bit that changed is that field. In the **label box** type what it is
   (e.g. `brake = ON`) → **Save capture** (appends to `logs/labeled_captures.jsonl`).
5. Repeat the toggle a couple more times (on/off/on) for a clean anchor.
6. **Map tab**: the field's live value shows; `automap` solves byte/offset/scale from your
   labels → **save to store** (candidate). The module's page (Experimental mode) now shows it decoded.

| Module | LID | Field to confirm | Change one thing | Expected |
|---|---|---|---|---|
| Td5 (motor) | `1E` | Brake switch | press/release brake pedal | one bit flips |
| Td5 (motor) | `36` | A/C request / handbrake | toggle A/C switch; set/release handbrake | a bit flips per toggle |
| SLABS | `56` | Any-door switch | open/close a door | a bit flips |
| SLABS | `42`/`48`/`58` | Neutral / diff-lock / reverse / HDC | select neutral; engage diff lock; reverse gear; HDC | a bit flips per action |

Notes: LIDs are the known switch blocks ([reference_tool_menu_map.md](reference_tool_menu_map.md));
treat the exact bit as **candidate** until the toggle proves it. `read_block` is read-only.

**Demo success = at least one field saved to the store and shown decoded on its page.**
That's the "we have a working mapping pipeline" milestone → then order the NanoCom.

---

## Part B — BCU read-inputs session (with the NanoCom)

The NanoCom is the **oracle**: it shows what each byte means while you sniff. You do not
control it — a human presses its menus; d2diag/you handle the capture + solving.

**Connect:** let the NanoCom attach to the BCU (it needs the ignition cycle: off → key → on
→ key). Your tap records the **5-baud slow init** at address `0x40`, keybytes `E5 8F`, and
the session header — the part we can't guess (see
[docs/discovery-2-td5/kline/physical-and-init.md](../docs/discovery-2-td5/kline/physical-and-init.md)).

**Capture loop per field (Capture tab → "From the reference-tool sniff"):**
1. **⬤ New capture** (arm) → on the NanoCom press **READ** for the input group.
2. The dashboard lists every LID that polled; **change one physical thing**, re-READ.
3. Label each LID with exactly what the NanoCom shows, in displayed order → **Save batch**.
4. Note the **time + action** for each step (or drop a capture marker) so bytes pair up.

Work the groups in [menus/bcu-inputs.md](menus/bcu-inputs.md) order. For each, the "change"
column is how you make the value move so the diff is unambiguous:

| Group | Representative fields | How to change it |
|---|---|---|
| LIGHTS | side/main/dipped/fog, indicators, hazard | operate each light + indicator stalk |
| DOORS / BODY | passenger/driver door, bonnet, key lock/unlock, CDL, inertia, ignition key inserted | open each door; open bonnet; lock/unlock with key + plip; insert/remove key |
| TRANSMISSION | reverse idle, transfer neutral, autobox W/X/Y/Z, park-neutral | select reverse; neutral; move auto selector through gears |
| WINDOWS | front L/R up/down | operate each window switch |
| WASH WIPE | front intermit/wash/parked/speed, rear wiper/wash | each wiper + washer; note "speed" is **numeric** |
| HEATED SCREEN / ENGINE | heated screen, ignition 2, engine speed signal | heated-screen switch; ignition pos; crank/run (engine signal) |
| INSTRUMENT states (×24) | ABS/SRS/brake/check-engine/diff-lock/HDC/ACE/SLS… | compare ignition-off vs on vs engine-running (many are warning lamps) |
| MILEAGE / TRIP | instr. mileage, BCU mileage, IP trip switch | read once; press trip switch; the two mileages anchor byte order/scale |
| POWER DISTRIBUTION | ignition pos 1/2/3, IDM/BCU supply V | step key through positions; **multimeter** the battery for the voltage fields |

**Faults:** Read fault codes → Clear → Read again. Capture all three (read + the *safe* clear
service + the empty response). Optionally induce a known harmless fault (unplug one wheel-speed
sensor on SLABS) to anchor raw↔fault-number — never on airbag.

**Do NOT capture** (forbidden, above): BCU Settings writes, Outputs (body/security), EKA, key
programming. Read inputs + faults only.

---

## Pipeline & confirm (both parts)

```
label in the UI ─▶ logs/labeled_captures.jsonl ─▶ tools/nanocom_import.py (sniff/importer.py)
                                                └▶ sniff/automap.py  ─▶ signals/<module>.json (candidate)
raw bus log  ─────────────────────────────────▶ logs/raw-<module>-<time>.log  (kept, gitignored)
```

- Offline alternative: hand the raw log to the mapping step and it emits candidates without
  the live UI.
- **Confidence stays `candidate`** until re-read on the car confirms it; only then green.
- After a session: route findings to `references/` + the signal store **in the same commit**
  as any code change, and close out the matching item in [test_plan.md](test_plan.md).

## Quick reference

- Start: `PYTHONPATH=src python3 tools/dashboard.py --serial auto --raw-log` (add `--sniff` for Part B).
- Admin UI: open `/admin` (Capture + Map tabs).
- Priorities after the demo: SLABS lamp outputs re-log, EAT gearbox inputs, then the BCU
  read-inputs sweep — see [nanocom/feature_map.md](nanocom/feature_map.md).
