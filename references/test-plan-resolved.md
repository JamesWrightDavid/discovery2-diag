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

- **2026-10-04 (afternoon) — `21 36` does not show forced outputs; fuel pump relay bit candidate.**
  Engine idling. The owner fired the Td5 output tests A/C clutch (`30 A3`), A/C fan (`A4`), MIL (`A2`),
  rev counter (`B7`) and temp gauge (`BA`); every one acknowledged `70 xx`. The MIL lit for ~1 s, and a
  `21 36` read 0.2 s into that window (and every read around the others) stayed `00 05`. So `36` is the
  ECU's own relay state, not the IOControl override: output tests cannot map it. Mapping must come
  from the ECU's own decisions (radiator fan when hot, A/C clutch on a warm day). From those: byte1
  bit2 = **fuel pump relay** (`00 01` engine off vs `00 05` running) -> `fuel_pump_relay`, then **proven** through the decoder: with the ignition on it read 1 during the
  prime and dropped to 0 at the moment the owner heard the pump stop;
  byte1 bit0 set whenever the ignition is on (Simon: main relay), not stored.
- **2026-10-04 (afternoon) — T-29: `21 42` bit2 is low range only; SLABS `21 48` is an analogue brake signal.**
  Engine idling, stationary, selector N. Transfer lever H -> N -> L -> N -> H: `42` = `83` / `83` /
  **`87`** / `83` / `83` (3 reads each; `83` = `82` + bit0 for selector N). Bit2 is set only in LOW;
  transfer NEUTRAL reads exactly like HIGH and nothing in `21 42/56/58` shows it. Decoder re-read
  L=1, H/N=0 -> `transfer_low` **proven**, states `0 = high or neutral`, `1 = low range`. The crawl
  part of T-29 is no longer needed. **`21 48`:** brake released `0x96xx-0xA6xx` (P or N), pressed
  firmly `0x3A3A-0x401F`, back at once on release; the selector alone does not move it -> new
  `brake_analog` (raw u16): re-read through the decoder after a restart (released 40519, pressed
  13155, released 42449) -> **proven** as a brake signal; physical meaning/scale open. This replaces the earlier "`48` wanders,
  analog, not a switch" reading, which had been taken with the brake held.
- **2026-10-04 (afternoon) — T-01/T-04: the measured MAF is `21 1C`@4; `1C`@6 is its voltage.**
  Engine idling, P, handbrake on, after the Td5 fault memory was cleared at 16:46 (dashboard). The
  long-dead sensor came alive: stationary holds idle / 1500 / 2600 rpm gave `1C`@4 = 478 / 1143 /
  2154 (repeat 2119-2147), proportional to rpm x MAP (ratio 0.61/0.67/0.64), and `1C`@6 = 1800 /
  2700 / 3440. `maf_sensor` rescaled to u16 x0.1 kg/h (BinOwl; 48/114/215 kg/h, plausible for 2.5 L)
  and re-read through the decoder after a restart (47.5 kg/h idle, 207-210 kg/h at 2560 rpm) ->
  `proven`. `maf_sensor_v` = `1C`@6 mV added as candidate (1.8/2.7/3.4 V hot-film curve; the old
  constant `0x009C` = 0.16 V was the faulted signal) — so `1C`@6 is not reserved. The modelled
  `maf` (`1D`@4, calibrated) agrees above idle (113/225 vs 114/215) but overstates idle (84 vs 48).
  The faults: only `25.5` (Current) came back after the clear; the logged `21.3`/`21.5` did not.
  **A/C at idle:** temperature LO, fan 1 on a cool day — no request (`1E` byte1 bit3 steady,
  `36` steady `00 05`); the climate unit is not calling for cooling. A Td5 A/C clutch output test
  (`30 A3 FF` -> `70 A3`) worked, but its pulse fell between `36` polls (2.8 s apart). Retry on a warm day.
- **2026-10-04 (late) — A/C request inconclusive engine-off; handbrake and brake not in SLABS `40..5B`; cruise-group faults.**
  Engine off, ignition on. **A/C:** the car has automatic climate control (no A/C button), so the
  request was provoked by setting the temperature 23 -> LO, fan 1: `21 1E` byte1 bit3 never moved in
  5 reads over 12 s. Expected — the HEVAC likely withholds the request with the engine stopped (or on
  a cold night). Retry at idle. **Handbrake / brake on SLABS:** one-off wide reads of `21 40..5B`
  (16 LIDs answer) differenced handbrake on/off and brake pressed/released, then the movers re-read:
  `44` and `55` wander on their own (`55` byte3 `03`/`04` did not follow the handbrake), `40` drifts
  `87..8A`, `57` byte0 flips `05`/`06` at rest. Nothing tracks either input, so neither is in that
  range (the ABS may hold the brake signal outside it, or not report it). **Td5 faults:** the
  undecoded bits are now visible: `25.3` and `25.5` (Current) persist all night, and `21.5` / `21.3`
  (their Logged copies; `21.3` new after tonight's cruise presses/ignition cycles). Their named
  neighbours in bytes 21/25 are all cruise faults, so these are probably cruise-group faults —
  meaning open. The earlier clear had also wiped `14.4`, `15.5`, `15.6`, which have not returned.
  Not cleared.
- **2026-10-04 — T-16 BCU inputs are blanked without SecurityAccess (read-only boundary mapped).**
  Ignition off -> on, engine off. New `tools/bcu_scan.py` (logic `d2diag.bcu.scan`): 5-baud `0x40`
  -> `E5 8F` first try, then `21 D8`..`E9`, `2C`, `2D` (20 LIDs) twice each in shuffled order,
  keepalive `3E 01` between scans; no `27` and no `21 CC` (refused in code). Every LID answers a
  **positive, checksum-valid** `61 <lid> 00 00 00 00` — not `7F 21 33` — and the payload never
  moves: baseline (handbrake on, doors shut), driver door open, handbrake off all read identical
  zeros. With the ignition on, a real input block cannot be all-zero, so the BCU **masks its inputs
  with zeros until unlocked** (a silent gate, unlike an NRC). Conclusion: no free live body data
  from the BCU; handbrake, bonnet and door inputs stay unreachable on our side without the Valeo
  seed->key (T-27/T-28). Settings LIDs (`21 C6..EB`) were not read.
- **2026-10-04 — T-06 Td5 identity `1A` blocks decoded (layout; VIN digits kept out).**
  From the 2026-10-04 read (raw log gitignored). Text is ASCII and numbers are **packed BCD**, which
  matches the part-number form `NNN000120` in the factory tool's menu ([menus/td5.md](menus/td5.md)).
  Offsets are into the data after `5A <opt>`; frame checksums verify.
  - `1A 9A` (6 bytes): `4E 4E 4E` "NNN" + BCD `00 01 30` -> **ECU part number `NNN000130`** (RDL 016).
  - `1A 87` (46 bytes): @0-10 ASCII = first 11 VIN characters; @11-13 = 3 BCD bytes, most likely the
    6-digit VIN serial (**candidate** — check against the VIN plate before trusting); @14 `00`;
    @15-18 BCD `14 11 20 02` = **14/11/2002** (candidate: build or programming date, consistent with
    the VIN's model-year code for 2003); @19 `00`; @20-25 "NNW" + BCD `50 01 40` -> **`NNW500140`**
    (NNW = Td5 software/tune prefix; candidate meaning); @26-35 `00 00 00 00 41 90 00 58 00 40`
    unknown; @36-45 `00 00 00 00 FF FF FF FF FF FF` padding.
  - `1A 9B` -> `01`, `1A 9C` -> `01`: one byte each, meaning open.
  Still open: the bytes at `1A 87`@26-31, the `9B`/`9C` meaning, and where the factory tool's
  Config/Fuel Tune IDs and Homologation come from (not in these four blocks).
- **2026-10-04 — Td5 cruise switches mapped on `21 1E` byte0 (T-08 partial).**
  Key-on, engine off. Differential: master off `00` / on `04`; master + SET held `0C`; master +
  RESUME held `14`; 3-4 reads each, and every release returned to the prior state. So bit2 =
  `cruise_master`, bit3 = `cruise_set`, bit4 = `cruise_resume` (all active-high), confirming
  SimonRafferty's hypothesis. Re-read through the decoder after a dashboard restart
  (master/set/resume: SET held 1/1/0, RESUME held 1/0/1, master off 0/0/0, 3x each) -> `proven`.
  The first SET hold did not register (press not fully home), so a no-change on a momentary
  button is not a negative until repeated. `21 36` never moved. The checksum fix holds on the
  car (`1E` now returns 2 bytes, `00 82`).
- **2026-10-04 — `0x18` is a generic OBD-II (ISO 9141-2) responder, likely the EAT gearbox.**
  Key-on, engine off, read-only (`/home/admin/d2tools/probe18.py`; raw log gitignored). 5-baud
  `0x18` -> `55 08 08`, `~KW2` `F7` -> `~addr` `E7`. The EAT factory-tool frames (`72 05 04 00 73`
  faults, `72 05 0B 03 7F` inputs) got **no reply** after this init. OBD-II `68 6A F1 01 00` ->
  `48 6B 18 41 00 90 18 80 00 | 34` (checksum OK): supported PIDs `01 04 0C 0D 11` (status, load,
  rpm, speed, throttle). `01 01` -> `41 01 00 04 00 00` (MIL off, 0 DTCs). Mode `03` -> no reply.
  Identity **candidate**: the reply's source byte `0x18` is in SAE J1979's transmission range
  (`0x18`-`0x1F`; engines are `0x10`-`0x17`), the car is an automatic, the Td5 holds 2 faults where
  this reports 0, and `0x33` (generic engine OBD) was silent in the sweep. Not proven — the proprietary
  `72`-framed EAT session still needs its own init (not a standard 5-baud on `0x18`). Never sent:
  mode `04` (clear), mode `09` (VIN), EAT clear/adaptive reset/settings.
- **2026-10-04 — T-26 full address sweep: only the four known modules plus `0x18` answer.**
  Key-on, engine off, battery on a tender, unattended. `tools/module_scan.py auto` with fast init
  AND 5-baud init on every address `0x01`-`0xEF` (474 probes, init + release only, 2 s settle).
  Responders: fast `0x13` Td5 and `0x29` SLABS (`C1 57 8F`); 5-baud `0x13` Td5 (`57 8F` — the Td5
  also answers a slow init), `0x18` (`08 08`, ISO 9141-2, identity still open), `0x40` BCU
  (`E5 8F`), `0x5B` airbag (`E9 8F`). Every other address was silent on both inits. So no cruise,
  HEVAC, instrument pack or IDM answers a standard fast or 5-baud init on pin 7 on this car; stop
  guessing addresses for them. Caveat: a module needing a non-standard baud, tester address or a
  running engine would not show here. `0x18` is the only unexplained responder — probed the same night (entry above).
- **2026-10-04 — T-18 airbag read verified (no SecurityAccess needed); T-26 default scan; T-06 lengths.**
  Key-on, engine off, read-only. **Airbag:** 5-baud `0x5B` -> keybytes `E9 8F`, `10 81` -> `50 81`,
  `21 02` -> `61 02 90 04 90 00 00 00 00 00 00 00`, release `82` -> `C2`. The reference tool's
  SecurityAccess before the read is NOT required. Records as `[status][number]`: `90 04` = fault 004
  (warning lamp, matches the existing baseline); `90 00` (number 0) is unresolved, likely padding or
  a format detail, not a second fault. **Address scan** (`tools/module_scan.py`, defaults):
  `0x13`/`0x29` fast `C1 57 8F`; `0x40` `E5 8F`; `0x5B` `E9 8F`; **`0x18` responded with `08 08`**
  (ISO 9141-2 keybytes, not KWP2000; identity open); `0x5A` silent (ruled out for this car). The
  full 0x01-0xEF sweep followed later the same night (entry above). **Td5 `1A`:** `1A 87` -> 48 bytes
  (contains the VIN; raw kept only in the gitignored log), `1A 9A` -> 8 bytes, `1A 9B`/`9C` -> 3 bytes
  each; field layout not decoded yet (T-06 stays open).
- **2026-10-04 — SLABS reverse gear mapped; handbrake, bonnet and A/C not on the Td5/SLABS reads.**
  Automatic, engine off, ignition on. `21 42` byte0 bit3 = reverse (P `82 28` / R `8A 30`, 3x each
  across P-R-P-R-P-R); `reverse_gear` re-read through the decoder (R=1, P=0) -> `proven`. `42` "byte1" `28`<->`30` was the frame checksum (see the correction below). `21 58` did not move
  with P/R, `21 56` stayed `00` (door closed), and `21 48` wanders on its own (analog, not a
  switch). Door `56` re-confirmed (00 closed / 01 open). Handbrake: no polled Td5 LID responds
  (`21 36` flat; `21 1E` byte1 bit5 flickers by itself with the handbrake held, so it is not a
  switch). Bonnet switch: no change in `21 56/42/48/58` held vs released -> expect it on the BCU.
  Neutral added the same night: `21 42` byte0 bit0 = neutral (N `83 29`, seen in two separate
  periods with P between), `neutral_gear` re-read through the decoder (N=1, P=0) -> `proven`.
  Diff lock added: `21 42` byte0 bit4 (OFF `82 28` / ON `92 38`, OFF-ON-OFF-ON), `diff_lock`
  re-read through the decoder (engaged=1, disengaged=0) -> `proven`. The dash is frozen in diag mode,
  so engagement was never seen visually; identity rests on the diff lock control toggling the bit.
  **`42` "byte1" is the frame checksum, not data** (corrected later 2026-10-04): the frame is
  `03 61 42 <b0> <cs>`, so `cs = b0 + 0xA6` = the `byte0 - 0x5A` pattern seen in every sample. It
  leaked in before the kwp2000 trim fix; `21 42` returns ONE data byte.
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
