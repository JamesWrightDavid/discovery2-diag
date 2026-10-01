---
title: "Wabco SLABS — K-line protocol evidence (sniffed from a reference tool)"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Distilled evidence from passive sniffs of a reference tool talking to the Wabco SLABS: basics (address, init, keepalive, standstill-only), identification, faults, live data, with links to the timing and services detail pages.
---

# Wabco SLABS — K-line protocol evidence (sniffed from a reference tool)

The canonical, curated SLABS page is [docs/discovery-2-td5/slabs.md](../../docs/discovery-2-td5/slabs.md). This folder keeps the dated evidence it is built on.

Captured 2026-08-07 via a passive ESP32 tap (RX-only, GPIO16) on pin 7, while a borrowed
**reference tool 1** ran the full function set. Raw log + markers:
`logs/session.log` (decoded with `tools/decode_session.py`). This is **proven from
real traffic**, not guessed.

> The raw capture files (`slabs_session_20260807` etc.) are kept **local-only** —
> gitignored under the `captures/` / `*.log` policy, since a full session may carry
> VIN/EKA. This document is the distilled, redacted evidence; the protocol facts below
> are what the captures showed.

## Basics
- **Address `0x29`, FAST init:** `81 29 F7 81 22` → response `C1 57 8F` (KWP2000, KW2=8F).
  ✅ **Init works since 2026-08-19** — see "The init pulse" in [init-timing.md](init-timing.md). That it previously
  took many attempts was OUR fault (TiniH ~32 ms instead of 25), not the module's.
- **Session:** unaddressed, length-prefixed frames `<len> <SID> <data…> <cs>`
  (checksum = byte sum & 0xFF), same style as the Td5 session.
- **Keepalive:** `01 3E` → `7E` (TesterPresent), ~1 s. **NOTE: bare `3E` without
  sub-byte** (frame `01 3e 3f`). `3E 01` gets no response and tears down the session.
- Requires **ignition ON** (ignition-fed module). Comms die >8–20 km/h.
- **⭐ Diagnostics are STANDSTILL-ONLY — proven RDL016 2026-08-29.** The ESP node sampled SLABS
  every ~30 s while driving 0–71 km/h and logged whether `81 29 F7 81` got a reply: SLABS answered
  (`C1`) at a **standstill right after an ignition cycle**, then went **silent the moment the car
  moved** (StartComm just echoes back — `sb=81 29 F7 81 22`, no `C1`, no `7F 81 10`) and **did not
  recover when stopped** — it stays dead until the next **ignition cycle**. So the "8–20 km/h"
  figure is really "once you move at all". This is SLABS deliberately suspending diagnostics while
  the ABS is active, not our polling or a stale link. **Consequence:** live ABS-sensor data *while
  driving* is unreachable over K-line — only an analog tap on the sensor wires can get that. The
  node's SLABS excursion is therefore gated to `speed < 5 km/h`.

### ⚠️ SLABS must be polled LIGHTLY (proven 2026-08-07)
The reference tool ran ~**1 Hz keepalive + occasional reads** — not continuous
block polling. Our driver must do the same:
- **Read few LIDs, rarely.** The dashboard's `SlabsDataSource.poll` reads only
  heights (`21 54`). An earlier store-driven block read of 5 LIDs + fault codes on
  **every** 0.5 s cycle (~7× the bus traffic) connected but **killed the session
  after ~15 s**.
- **The RATE matters as much as the number of LIDs (the car 2026-08-18).** Just reading
  `21 54` wasn't enough: with the server's 0.5 s cycle it became `3E` + `21 54` = **4
  frames/s**, whereas the reference tool ran ~1 Hz (keepalive `01 3e 3f` was every ~1048 ms
  in the sniff). The session died after 21 s (connected 20:54:28, dead 20:54:49).
  Traffic is therefore throttled on the **clock, not the poll cycle**: `_SLABS_BUS_PERIOD =
  1.0 s` and fault codes on their own cadence `_SLABS_FAULT_PERIOD = 30 s`. Extra polls
  return cached values without touching the bus.

## ReadEcuIdentification — `1A xx`
| Req | Response | Content |
|---|---|---|
| `1A 8A` | 28 bytes `00 37 44 60 44 03 10 ff 31 90 10 86 40 ff 06 29 …` | hardware/config ID |
| `1A 8B` | ASCII | **software modules:** `KRTE49B0 HDTE16A0 EBTE87A0 CDTE91A0 KWTP11A0` |
| `1A 8D` | ASCII | **VIN:** `SALLXXXXXXXXXXXXX` ✅ (confirms the decoding) |

## Fault codes
- **`21 11`** → 16-byte block = **LOGGED faults** (bit-per-fault). Before clear: bits set
  in byte 3 (`0x10`) + byte 10 (`0x10`) = **two faults = baseline's `020` RF sensor +
  `027` shuttle valve**. After clear: all `00`. ⇒ `21 11` IS the logged-fault block.
- **`21 47`** → 16-byte block = **CURRENT faults** (was `00` = none current now).
- **`14 FF FF`** → `54` = **ClearFaults** (safe write; reset `21 11`).
- Byte↔number mapping: 2 bits (byte3.bit4, byte10.bit4) = faults 020+027. More
  anchor points come from the "induce a known fault" technique.

## Live data — ReadDataByLocalIdentifier `21 xx`
Grouped by reference tool screen (values = examples):
- **SLS inputs:** `21 53`=`d2 d2 0f 0f` · `21 54`=`91 9c 0f 0f` (heights, changed live) ·
  `21 55`=`00 00 00 02` · `21 45`=`7f` · `21 46`=`78 76` · `21 49`=`00 00 01` ·
  `21 59`=`00 0f 0f 0f`
- **ABS inputs:** `21 43`=`7c 00 7c 00 7c 00 7c 00` (**4 wheel speeds**) ·
  `21 44`=`00 80 01 02 01 01 02 01 02 02 03 04 …` · `21 50`=`72 73 73 72`
  (**sensor voltages?**) · `21 57`=`06 0f 0f 0f` · `21 49`=`00 00 01`
- **ABS-SLS switch:** `21 42`=`82` · `21 48`=`94 61` · `21 56`=`01 0f 0f 0f` ·
  `21 58`=`32 0f 0f 0f`

## To build in d2diag (all the material exists now)
`Slabs(KWP2000(KLine(...)))`: establish() via fast init 0x29 → C1 57 8F; keepalive 3E;
`read_faults()` = `21 11`/`21 47` (bit-per-fault, map in `slabs_fault_codes.md`);
`clear_faults()` = `14 FF FF`; live via `21 xx`; actuators via `31 xx`. Reuse
the Td5 layer's tolerant read + the same session pattern.

## Detail pages

| Topic | Page |
| ----- | ---- |
| Init timing, silent period, init pulse, addressing trial | [init-timing.md](init-timing.md) |
| Actuators, input LIDs, byte variance, field identity, bleed frames | [services-and-lids.md](services-and-lids.md) |
