---
title: "Test backlog — resolved items"
area: references
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [references/test_plan.md]
summary: >
  Append-only log of settled car and tool tests, newest first, with the date and what
  settled each one (inconclusive outcomes included) so nothing is re-run blind.
---

# Test backlog — resolved items

Companion to [test_plan.md](test_plan.md). When an open test is settled, move it here
with the date and the outcome. Newest first.

- **2026-10-04 — T-18 airbag read verified (no SecurityAccess needed); T-26 default scan; T-06 lengths.**
  Key-on, engine off, read-only. **Airbag:** 5-baud `0x5B` -> keybytes `E9 8F`, `10 81` -> `50 81`,
  `21 02` -> `61 02 90 04 90 00 00 00 00 00 00 00`, release `82` -> `C2`. The reference tool's
  SecurityAccess before the read is NOT required. Records as `[status][number]`: `90 04` = fault 004
  (warning lamp, matches the existing baseline); `90 00` (number 0) is unresolved, likely padding or
  a format detail, not a second fault. **Address scan** (`tools/module_scan.py`, defaults):
  `0x13`/`0x29` fast `C1 57 8F`; `0x40` `E5 8F`; `0x5B` `E9 8F`; **`0x18` responded with `08 08`**
  (ISO 9141-2 keybytes, not KWP2000; identity open); `0x5A` silent (ruled out for this car). The
  full 0x01-0xEF sweep for cruise/HEVAC/IP/IDM was not run. **Td5 `1A`:** `1A 87` -> 48 bytes
  (contains the VIN; raw kept only in the gitignored log), `1A 9A` -> 8 bytes, `1A 9B`/`9C` -> 3 bytes
  each; field layout not decoded yet (T-06 stays open).
- **2026-10-04 — SLABS reverse gear mapped; handbrake, bonnet and A/C not on the Td5/SLABS reads.**
  Automatic, engine off, ignition on. `21 42` byte0 bit3 = reverse (P `82 28` / R `8A 30`, 3x each
  across P-R-P-R-P-R); `reverse_gear` re-read through the decoder (R=1, P=0) -> `proven`. `42`
  byte1 shifts `28`<->`30` in step with the gear (unidentified, not stored). `21 58` did not move
  with P/R, `21 56` stayed `00` (door closed), and `21 48` wanders on its own (analog, not a
  switch). Door `56` re-confirmed (00 closed / 01 open). Handbrake: no polled Td5 LID responds
  (`21 36` flat; `21 1E` byte1 bit5 flickers by itself with the handbrake held, so it is not a
  switch). Bonnet switch: no change in `21 56/42/48/58` held vs released -> expect it on the BCU.
  Neutral added the same night: `21 42` byte0 bit0 = neutral (N `83 29`, seen in two separate
  periods with P between), `neutral_gear` re-read through the decoder (N=1, P=0) -> `proven`.
  Diff lock added: `21 42` byte0 bit4 (OFF `82 28` / ON `92 38`, OFF-ON-OFF-ON), `diff_lock`
  re-read through the decoder (engaged=1, disengaged=0) -> `proven`. The dash is frozen in diag mode,
  so engagement was never seen visually; identity rests on the diff lock control toggling the bit.
  **`42` byte1 is a check byte, not a field:** `byte0 - byte1 = 0x5A` in every sample (P `82 28`,
  N `83 29`, R `8A 30`, diff lock `92 38`, lever `86 2C`). Only byte0 carries information.
  **Lever on byte0 bit2:** an earlier lever movement set `42` byte0 bit2 (`86 2C`, reproducible).
  The user confirmed it was low range; end-of-travel HIGH reads `82 28`, LOW `86 2C`. Staged as
  candidate `transfer_low` (neutral still unconfirmed, see test_plan T-29). Not done: HDC (`21 42/48/58`), A/C request (`21 1E` byte1 bit3).
- **2026-10-03 — T-08 partial: brake switches mapped (first on-car run of the Part A pipeline).**
  Rig validated on the Pi (Linux, FTDI KKL, `send_break`): `81 13 F7 81` -> `C1 57 8F`, session
  and SecurityAccess OK. Differential on `21 1E` (3x released `00 82`, 2x pressed `01 02`):
  byte1 bit7 = brake main (active-low), byte0 bit0 = second brake switch (active-high). Saved via
  capture -> automap -> `upsert_field`, then re-read through the decoder (held 0/1, released
  1/0) -> `proven`. `21 36` unchanged. T-08 stays open for the other switches.
- **2026-10-01 — Merged the Td5 verification backlog** (`docs/discovery-2-td5/verification-todo.md`,
  now removed) into this file. Its items map as follows: fuel consumption → resolved 2026-08-21
  (`injection_qty`, plus the derived `fuel_rate`/`economy`); MAF scale → T-01; EGR/wastegate
  `21 37/38` → T-02; switch bits `21 1E/36` → T-08; VIN/ECU identity → T-06; remaining
  fuelling bytes → T-03/T-05; wastegate modulator `30 BE` → T-23.
- **2026-08-29 — SLABS diagnostics are STANDSTILL-ONLY (does it really die at speed?).** The ESP
  node sampled SLABS while driving 0–71 km/h, logging whether `81 29 F7 81` got a reply. SLABS
  answered `C1` at a standstill right after an ignition cycle, then went **silent the instant the
  car moved** (StartComm only echoed — no `C1`, no `7F 81 10`) and **did not recover when stopped**
  — dead until the next ignition cycle. So it's SLABS suspending diagnostics while the ABS is
  active, not our polling. Live ABS-sensor data while driving is therefore **unreachable over
  K-line** (analog tap needed). The node's SLABS excursion is now gated to `speed < 5 km/h`. See
  `references/slabs/overview.md`.
- **2026-08-23 — ESP32 K-line node talks to the Td5.** Wiring proven: L9637D VS on pin 7,
  pull-up 510 Ω–1 k is critical, common ground required.
- **2026-08-21 — `accel_way3` moves (0 → 2.23 V).** Pedal track 3 is live; `1B` mapping
  confirmed against the car. (Note: BinOwl's frame-length heuristic labels our 12-byte
  `1B` the "MSB" variant, which disagrees with the Euro-3/NNN reading — harmless for us,
  unresolved in general. See `references/td5-external-findings.md`.)
- **2026-08-21/22 — `1D`@15 EGR modulator and `1D`@17 wastegate modulator** confirmed
  across four drives as behaviour (not scale). `1D`@16 is a constant-0 dead byte.
  Scale still `candidate` → T-02.
- **2026-08-21 — `1D`@6 = injection quantity (mg/stroke), `proven`,** via deliberate
  overrun lifts: idle 11.1 → load 23.9 → overrun 4.7 (below idle = fuel cut).
- **2026-08-20 — `21 21` = idle-governor error (s16),** ≈0 at idle, grows with engine
  speed. Not a fault.
- **2026-08-19 — SLABS init pulse corrected** (TiniH was ~32 ms instead of 25 ± 1); both
  modules connect reliably. Follow-up on repeatability → T-10.
- **2026-08-18 — the communication link outlives the process.** A run that only talks to
  SLABS is still rejected if a previous run died with the link open — hence the
  best-effort `82` before every init attempt.
- **2026-08-03 — `1A` temperatures and `1C`@0 boost** verified against the car
  (coolant 59.2 °C; boost 1.0 → 1.2 bar). `1A`@8 "ext_temp" is a phantom: the sensor is
  not fitted, so it reads a constant 150.0 °C.
