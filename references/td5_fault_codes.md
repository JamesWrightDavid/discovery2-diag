---
title: "Discovery 2 TD5 (Lucas engine ECU) — fault codes"
area: references
status: stable
version: 1.1
updated: 2026-10-04
summary: >
  Td5 engine ECU fault memory: raw-mapped, 208 proven + 3 candidate named fault bits (13.6 renamed from a NanoCom screen); the forum X-Y to offset.bit mapping verified 210/210; 69 bits still unnamed (backlog).
---

# Discovery 2 TD5 (Lucas engine ECU) — fault codes

The engine ECU's fault memory. **Unlike the other modules, TD5 is already
raw-mapped** — we read the faults directly on K-line and decode them bit-by-bit in code.

- **Raw decoder (code):** `src/d2diag/td5/faults.py` — 208 proven + 3 candidate named fault bits
- **Reference (display codes + causes):** the fault-code dictionary (register repo),
  the TD5 section incl. Kelvin's complete forum list (`X-Y` format)
- **Live signals:** `src/d2diag/td5/identifiers.py` (LIDs `21 xx`)

## Raw encoding (PROVEN)
Td5 does **not** read standard DTCs. The fault memory is fetched as a **status block** via
ReadDataByLocalIdentifier `21 3B` (bytes after positive `61 3B`), and cleared via
StartRoutine `0xDD` with 18 zero bytes.

- The block is **35 bytes** (offset 0–34) and **bit-coded**: each bit = one fault.
- **Fault index = offset·8 + bit** (bit 0 = mask `0x01` … bit 7 = `0x80`).
- Set bits without known text are reported generically as `byte<off>.bit<n>` so
  no fault disappears silently.

The map is **proven** from the reference tool Ekaitza_Itzali *and* cross-validated against
**reference tool v1.12** — both give the same name for the same offset/bit (no code copied,
see `THIRD_PARTY_LICENSES.md`).

## Status encoding (offset bands)
The reference tool distinguishes more finely than Ekaitza's coarse Logged/Current. The pattern in the block:

| Offset band | Meaning |
|---|---|
| 0–1 | **Logged Low** — stored, signal low (short circuit/low voltage) |
| 2–3 | **Logged High** — stored, broken circuit (high) |
| 4–5 | **Current** — sensor-circuit faults active right now |
| 6–13 | Driver stage (over-temp / open-load / short), Logged and Current respectively |
| 14–25 | Crankshaft, CAN, boost, driver demand, speed, cruise |
| 26–34 | Injectors 1–6 (peak long/short, open/short/partial) + topside switch |

## Forum X-Y ↔ offset.bit: verified (2026-10-04)

Forum and NanoCom codes are written `X-Y` (or `(X,Y)`), 1-indexed: **`X-Y` = offset `X-1`,
bit `Y-1`**. Three independent checks support this:

1. **Full-list diff.** The TD5SPY list (https://www.td5spy.co.za/td5_faults, 211 rows; the
   same upstream as Ekaitza, down to the typos "peck", "inlett" and "crack") was diffed
   mechanically against all 210 bits in `faults.py`. **210/210 match on both text and the
   L/C marker** under `(X-1).(Y-1)`. The shifted alternatives score 0–2 name hits:

   | Mapping tried | Name hits |
   |---|---|
   | `(X-1).(Y-1)` | 210 |
   | `X.Y` | 0 |
   | `(X-1).Y` | 0 |
   | `X.(Y-1)` | 2 |
   | `(X-2).(Y-1)` | 2 |

   Examples: `1-1` egr inlet throttle (L) → `0.0`; `4-1` inlet air temp (L) → `3.0`
   (Logged High band); `17-2` high speed crank (C) → `16.1`; `28-7` topside switch pre
   injection (L) → `27.6`.
2. **A NanoCom screen posted by an owner** (https://www.landyzone.co.uk/land-rover/error-code-help.353225/)
   shows the tool's own `(X,Y)` numbers with text:
   - `(3,5)` driver demand problem 1 (Logged High) → our `2.4`;
   - `(20,2)` turbocharger overboosting (Logged) → `19.1`;
   - `(22,1)` road speed missing (Logged) → `21.0`.

   All three match. More NanoCom screens posted later agree too:
   - `(15,2)` high speed crank (Logged) → `14.1`
     (https://www.defender2.net/forum/topic79738.html);
   - `17.2` high speed crank (current) → `16.1`
     (https://www.landyzone.co.uk/land-rover/nanocom-fault-code-17-2.338410/);
   - `(25,8)` injector trim data corrupted (Current) → `24.7`
     (https://www.defender2.net/forum/post967555.html).
3. **RDL 016 (the original author's car).**
   - The 2026-08-07 baseline read showed `001-07` and `004-01` on the reference tool, and
     the 2026-08-08 raw sniff decoded bits `0.6` (air flow, Logged Low) and `3.0` (IAT,
     Logged High). Those are exactly `(1-1).(7-1)` and `(4-1).(1-1)`.
   - The text transcribed for `001-07` in the baseline table ("EGR vacuum module, short
     circuit") does *not* fit its number, which is air flow. Treat that transcription as
     suspect. Re-check the screen next session.

**One bit gained:** TD5SPY `21-8` "injector trim data corrupted (L)" → `20.7`. Its Current
twin `25-8` is already our proven `24.7`, and SimonRafferty's DTC table also gives `20.7`
(P1633). It is added as **candidate**: `Fault(..., "candidate")` in `faults.py`, listed
under `candidate` in `faultmap.json`, with `confidence: candidate` in `dtc/td5.json`.

## A NanoCom screen corrects one name (2026-10-04)

A NanoCom engine screen (`TD5ENG.APP`) posted by a Td5 owner shows seven faults with the
tool's own numbers (https://www.defender2.net/forum/post594365.html):

| NanoCom line | Our bit | Our name | Verdict |
|---|---|---|---|
| `(3,5) DRIVER DEMAND PROBLEM 1, (LOGGED HIGH)` | `2.4` | driver demand problem 1 (Logged High) | matches |
| `(10,4) GEARBOX / ABS DRIVE OPEN LOAD, (LOGGED)` | `9.3` | gearbox/abs drive open load (Logged) | matches |
| `(14,4) GEARBOX / ABS DRIVE OPEN LOAD, (CURRENT)` | `13.3` | gearbox/abs drive open load (Current) | matches |
| `(20,2) TURBOCHARGER OVERBOOSTING, (LOGGED)` | `19.1` | turbocharger over boosting (Logged) | matches |
| `(14,6) MIL LAMP DRIVE OPEN LOAD, (CURRENT)` | `13.5` | mil lamp drive open load (Current) | matches |
| `(14,7) GLOWPLUG LAMP DRIVE OPEN LOAD, (CURRENT)` | `13.6` | ~~glow plug relay drive open load (Current)~~ | **corrected** |
| `(10,3) TACHOMETER DRIVE OPEN LOAD, (CURRENT)` | `9.2` | tachometer open load (Logged) | state word differs |

**`13.6` is renamed** "glowplug lamp drive open load (Current)", now **candidate**. Three
things point the same way:
- the tool's own screen says lamp;
- the source list repeats "relay" at `13.6` and `13.7`, a visible copy error;
- the logged twin `9.6` is "glow plug lamp drive open load".

**`11.6` is renamed too.** It shows the same repeat ("relay" at `11.6` and `11.7`), and a
full NanoCom dump shows `(12,7) GLOWPLUG LAMP DRIVE OPEN LOAD, (CURRENT)`
(https://www.defender2.net/forum/post840727.html). Now **candidate**, P-code dropped.

**`(10,3)` tachometer** shows "(CURRENT)" in a row whose other entry on the same screen
reads "(LOGGED)". This is one screen and may be a NanoCom quirk, so `9.2` is unchanged and
the bit goes on T-30.

The P-code P0380 (glow-plug circuit) was removed from `13.6`, because a lamp driver is not
the plug circuit.

### The duplicate names are real, not a transcription error

Bytes 10/12 and 11/13 carry identical names in the source list. For example, `11.0` and
`13.0` are both "air conditioning fan drive open load (Current)". A hit-count across every
NanoCom screen we could fetch (2026-10-04) shows the tool itself prints them that way:

| Slots (tool / ours) | What NanoCom prints | Hits | Verdict |
|---|---|---|---|
| `(12,1–8)` / `11.0–11.7` | the row-10 drivers, OPEN LOAD, (CURRENT) | 1 full dump (post840727) | same text as row 14: genuine duplicate |
| `(14,1–8)` / `13.0–13.7` | the same eight texts, (CURRENT) | 1–3 per slot (post840727, post594365, landyzone 285327, defender2 topic43605) | genuine duplicate |
| `(12,7)`, `(14,7)` / `11.6`, `13.6` | GLOWPLUG **LAMP** DRIVE OPEN LOAD | 1 and 2 | source's "relay" was wrong; renamed |
| `(8,7)`, `(8,8)` / `7.6`, `7.7` | GLOWPLUG RELAY / GLOWPLUG LAMP DRIVE OVER TEMPERATURE (LOGGED) | 1 | matches our map |
| `(10,7)`, `(10,8)` / `9.6`, `9.7` | GLOWPLUG LAMP / GLOWPLUG RELAY DRIVE OPEN LOAD (LOGGED) | 1 | matches our map |
| `(13,6)` / `12.5` | EGR INLET THROTTLE SHORT CIRCUIT, (CURRENT) | 1 | matches; weak support that 10/12 also duplicate |
| `(10,3)` / `9.2` | TACHOMETER DRIVE OPEN LOAD, **(CURRENT)** | 3 cars | the tool's own label; see below |

**Conclusion:** both copies of each duplicate pair exist in the tool, and probably in the
ECU (two "current" memories). So the decoder cannot say which of the two bits a name
refers to, and a name lookup resolves to one of them. The bit key (`11.0` vs `13.0`) is
always correct.

**`(10,3)` tachometer** reads "(CURRENT)" on three different cars, while the rest of row 10
reads "(LOGGED)". The tool's state word comes from a fixed per-slot text table, not from the
row. Our `9.2` "(Logged)" follows the band and is unchanged. Don't infer logged/current
from NanoCom's word alone.

## Unnamed bits — backlog for on-car / NanoCom confirmation

69 of 280 bits have no name in any source we can read. The decoder reports them as
`byte<off>.bit<n>`, which is correct: do not invent names.

| Offset | Unnamed bits |
|---|---|
| 5 | 5 (the Current band's "ambient air temp" slot; no list names it) |
| 14, 15, 16 | 0, 2–7 |
| 17 | all (0–7) |
| 18 | 0, 3, 4, 6 |
| 19 | 2, 5, 6, 7 |
| 20 | 0, 1, 2 |
| 21 | 1, 3, 4, 5 |
| 22 | 6, 7 |
| 23 | 5, 7 |
| 24 | 0, 1, 2 |
| 25 | 3, 4, 5 |
| 26–29 | 7 (after the topside-switch bit) |
| 30–34 | 6, 7 |

Seen set with no name. Two cars; keep their evidence apart (see `docs/README.md`):
- **D2-JW** (this fork's car, 2026-10-04): `25.3` and `25.5` (Current) persist across power
  cycles, with their Logged copies `21.3` and `21.5`. Their named neighbours in bytes 21/25
  are all cruise faults, so these are probably cruise-group faults. The forum `X-Y` codes
  are `(22,4)`, `(22,6)`, `(26,4)` and `(26,6)`. `14.4`, `15.5` and `15.6` were set before
  the 16:46 fault clear and have not returned
  ([test-plan-resolved.md](test-plan-resolved.md)).
- **RDL 016:** `18.6` (raw sniff 2026-08-08, below).
- `15.7` was named in the owner's brief for this work, but no session note records it. It may
  have been one of D2-JW's pre-clear bits; check before relying on it.

A second research pass (2026-10-04) searched for each gap separately and found no name for
any of them. Ekaitza's own table marks every one of these slots `fault_code_void`
("Unknown"), and SimonRafferty's `td5_dtc_table.h` (generated from the same TD5SPY list) has
no entry for them. Names guessed by copying across the Logged/Current byte pairs were
rejected: that is a pattern, not a source.

To name a bit, photograph the NanoCom fault screen while capturing the raw `61 3B` block,
then match the displayed `X-Y` against the set bit.

## Display code ↔ raw (reference-tool cross-check)
The reference tool shows `X-Y` (e.g. `28-7` topside switch). Our raw mapping gives
`offset.bit`, related as verified above. A sniff of the reference tool reading Td5 faults
(raw block and displayed code captured together) would settle the remaining unnamed bits,
the same method as for SLABS.
The reference table in the dictionary holds the display codes; this file + `faults.py` hold
the raw encoding.

> 🔴 **`28-7` / `topside switch failed pre-injection`** (offset 27 bit 6, Logged;
> offset 29 bit 6, Current): the forum's strongest clue for *the engine stalling completely /
> the reference tool not getting in* — the topside switch is a solenoid **inside the ECU** that
> fails (especially after moisture). See the dictionary for the whole reasoning. Not seen on
> RDL 016.

## Seen on RDL 016 — raw-sniffed 2026-08-08 (proven)
`21 3B` read during warm idle; our decoder gave: **air flow circuit** (Current +
Logged Low), **inlet air temp** (Logged High), **can tx/rx error** (Logged),
**driver demand** (problem Current + inconsistencies Logged), plus two suspicious ones:
**inj. 6 peak charge long** (Current — but the engine is 5-cyl) and an unknown `byte18.bit6`.
Raw block + full table: see the dictionary, section "Seen on RDL 016 — raw-sniffed".

The same session also proved: SecurityAccess seed `d3 e6` → key `ad 87` (our keygen
is correct), immobiliser status `03` = not immobilised, fast init `0x13`, session `0xA0`.

## New protocols sniffed (beyond faults)
- **Output tests:** IOControl `30 <id> ff` (fuel pump A1, MIL A2, A/C clutch A3,
  A/C fan A4, glow B3, rev-counter B7, temp-gauge BA; wastegate BE / EGR BD with PWM
  parameters). **Injector click:** StartRoutine `31 C2 0<n>` (cyl 1–5).
- **Security:** `31 C0` + `33 C0` → status byte. Implemented in `td5/td5.py`
  (`output_test`, `injector_pulse`, `security_status`); `LEARN SECURITY CODE`
  deliberately not implemented (state-changing).

## reference tool live-data screens → our LIDs (reference 2026-08-19)

External description of the reference tool's Td5 screens, cross-run against our sniffed LIDs.
Confirms mappings and names fields we don't read yet.

| reference tool field | Our LID | Status |
|---|---|---|
| Engine Speed | `21 09` rpm | proven |
| Road Speed | `21 0D` speed | proven |
| Coolant Temp | `21 1A@0` | proven (normal 86–95 °C, thermostat 88, >105 danger) |
| **Turbo Pressure** | `21 1C@0` manifold_press | proven — = boost pressure. Idle ~1.0 bar, full load 2.0–2.2, overboost cut >2.42 |
| Battery Volt | `21 10` | proven (13.8–14.4 V while charging) |
| Ambient Pressure | `21 23` | proven (~1.0 bar sea level) |
| **Air Flow (MAF)** | `21 1C@4` maf_raw | **CANDIDATE — reclassified.** The earlier "no MAF" was wrong; the reference tool shows it. Idle 55–65 kg/hr. Our only reading=0 (engine off). Scale unknown → requires a capture with the engine running |
| Air Inlet Temp | `21 1A@4` air_temp | proven |
| Fuel Temp | `21 1A@12` | proven (~70–80 °C warm, 10–15 below coolant) |
| Cylinder 1–5 balance | `21 40@0..8` | proven (±4 idle; +6…+15 = weak cylinder) |
| Accel Track 1 | `21 1B@0` | proven (0.3→4.7 V) |
| Accel Track 2 | `21 1B@2` | proven (INVERTED 4.7→0.3 V) |
| Accel Track 3 | `21 1B@4` | candidate — **Euro 3 (NNN) only**; 0 on Euro 2 |
| Accel Supply | `21 1B@6` | proven (5.0 V ±0.1) |
| Idle Speed Error | `21 21` rpm_error | proven |

### Still UNMAPPED live fields (reference tool screen 5) — next capture goal
- **EGR Inlet**, **EGR Modulator** (PWM), **Wastegate** (electronically controlled on the D2).
  Probably live in one of the not-yet-interpreted LIDs `0E, 11, 20, 24, 32, 37, 3D`.
  Requires labeled captures (reference tool value + raw bytes) to be mapped.
- **`21 1C@2`**: a second pressure-like u16 (~1.007 bar) next to the manifold — unidentified.
- Switch inputs `21 1E / 21 36 / 21 38` (bitfields) — documented in the handoff, not in the store.

## reference tool SLABS screens → our LIDs

| reference tool field | Our LID | Status |
|---|---|---|
| L/R Height Sensor | `21 54@0/1` | proven (normal ~110–135, calibration-dependent; L≈R on level ground) |
| Wheel speeds FL/FR/RL/RR | `21 43` (4×) | candidate — only FR mapped; raw value ~124 baseline ≠ km/h |
| Door switches | `21 56@0 bit0` any_door | proven — SLABS does NOT adjust the suspension with a door open |
| Valve/target supply V | `21 44@12/13` | candidate — ~12.5–14 V, scale not cross-validated |
| **Shuttle Valve Switches** | `21 42/48/58`? | unmapped — our fault code **027** = classic WABCO circuit-board fault |
| Brake switch, SLS off-road switch | switch LIDs | unmapped (`21 42/48/56/58` bitfields) |
