---
title: "Discovery 2 cross-reference against NanoCom, Hawkeye and public sources"
area: references
status: stable
version: 1.0
updated: 2026-10-04
summary: >
  Our protocol, live-data and fault facts checked against the NanoCom vendor ECU guides, owners' NanoCom/Hawkeye screens and open-source Td5 code: what agrees, what was corrected (SLABS height band, overboost, glow-plug lamp names, cruise), known tool quirks, and claims that conflict with our proven data.
---

# Discovery 2 cross-reference: tools and public sources

What a research pass on 2026-10-04 found when it checked this project against outside
sources. It lists where they agree and what we changed. Only content read on a fetched
page counts here; search-engine summaries were not used.

## Sources

- **NanoCom vendor ECU guides** (Blackbox Solutions), one PDF per module from
  https://www.blackbox-solutions.com/site/support:
  - Td5 `download?id=23`
  - SLABS `id=18`
  - ACE `id=17`
  - EAT `id=19`
  - airbag `id=16`
  - BCU `id=32`

  Kit contents are at https://www.blackbox-solutions.com/site/nanocom. They are functional
  guides with no protocol bytes. Facts are restated here in our own words, with short quotes.
- **Owners' NanoCom and Hawkeye screens** on landyzone.co.uk, defender2.net and
  rangerovers.pub (URL per row).
- **Open-source Td5 code:** td5opencom (`td5comm.cpp`), Ekaitza_Itzali and TD5-Dash. No
  open-source code was found for any Discovery 2 module other than the engine.

## Fault totals (vendor guides)

| Module | Faults the ECU can report | Our store |
|---|---|---|
| Td5 | "over 200", in two memories (current and logged) | 211 bits named of 280 |
| SLABS | "up to 47" | 2 proven + rsw list |
| ACE | "up to 45"; some are "MASKED FAULT" (hidden by Testbook) | 22 |
| EAT | "up to 39" | 38 |
| Airbag | "up to 37" | 4 |
| Hella cruise | 41, **petrol V8 Discovery II only** | n/a on the Td5 |

## Corrections made from this pass

| What | Was | Now | Evidence |
|---|---|---|---|
| Td5 `11.6`, `13.6` | "glow plug relay drive open load (Current)", the source list's repeat | "glowplug lamp drive open load (Current)", candidate | NanoCom screens `(12,7)` and `(14,7)` read GLOWPLUG LAMP ([td5_fault_codes.md](td5_fault_codes.md)) |
| SLABS display number | `020`/`027` treated as fault numbers | occurrence counts; faults keyed by raw bit | vendor guide: faults listed "together with the number of times" ([slabs_fault_codes.md](slabs_fault_codes.md)) |
| SLABS ride-height band | 110–135, L≈R | 135–165, L and R may differ | RDL 016 read 149/162; owners 138–157; vendor: ≈1.4 mm per count, calibration-dependent |
| Td5 overboost cut | fixed > 2.42 bar | ≈ ambient + 142 kPa | defender2.net/forum/topic65863.html |
| Td5 cylinder balance | +6…+15 = weak cylinder | worth checking, not proof | owners ran double figures for years (landyzone 386655) |
| Cruise | separate Hella module, unconfirmed | run by the Td5 engine ECU | vendor: "it is not a separate ECU" ([cruise-control.md](../docs/discovery-2-td5/cruise-control.md)) |

## Agrees with us

**Td5 protocol** (td5opencom source and the Ekaitza README):
- 10400 baud;
- `81 13 F7 81` fast init, so tester address `F7`;
- session `10 A0`;
- seed/key `27 01`/`27 02`;
- faults `21 3B`, read as a 35-byte bit block;
- clear with `31 DD` padded with zeros.

**Td5 live data** (owners' NanoCom and Hawkeye logs):

| Value | Ours | Owners |
|---|---|---|
| MAF at idle | 55–65 kg/hr | 55–60, logged 63.9; a faulty MAF reads 14–16 |
| Boost at full load | 2.0–2.2 bar | 215–220 kPa |
| Coolant | 86–95 °C | 90 ± 2 |
| Accelerator tracks | 0.3→4.7 V / 4.7→0.3 V, 5.0 V supply | the same |

**ACE live data** (owners' logs):
- residual pressure 3–6 bar;
- DCV current about 0.001 A, pressure-control valve current 0–0.012 A;
- coil resistance: DCV 2.7 Ω, pressure-control solenoid 5.7 Ω.

**Vendor guides**:
- **SLABS:** faults current/intermittent with a count; heights 0–255; L/R calibration only;
  wheel speeds can't be read below 1.8 km/h.
- **ACE:** accelerometers 1 and 2 calibration, a 3-step bleed, 15 inputs, and 5 outputs
  (main relay on/off, warning lamp, DCV1, DCV2).
- **BCU:** EKA read/set and two key-programming methods.
- **Airbag:** VIN is the only programmable setting.

## New facts worth knowing

**SLABS**
- It stops communicating once all four wheels pass about **8 km/h**, by design, and this
  "cannot be overridden". Live SLABS data only works stationary or creeping, which matches
  our "poll lightly, standstill" rule.
- Stored target heights can't be read back.
- Settings include ECU calibrated, test status, transport mode and suspension type (air
  or coil).

**ACE**
- The guide warns the DCV output tests can make the vehicle "jerk violently from side to
  side".
- "Set Calibrated" only sets a flag "and it doesn't have any effect on the system". An
  owner nevertheless reports it locked up two ECUs (landyzone 132815). We never send it.
- A new ECU won't energise its main relay until it has passed its response tests.
- Owners' readings: the pressure sensor shows 16–19 bar at idle, and 0–0.4 bar means
  failure. The accelerometers sit near 0.01 g at rest.

**Td5**
- Where air-conditioning or cruise isn't fitted, the ECU can report the unused inputs and
  outputs as faults, without the MIL. That explains owners' "spurious" A/C and gearbox codes
  (defender2 post474378).
- A Hawkeye screen also shows the raw sensor voltages: MAF 1.63 V, coolant 1.09 V at 66 °C.

**EAT**
- Live data includes adaptive pressure values for upshifts 1-2, 2-3 and 3-4 in three speed
  ranges.
- The ECU is on CAN as well as the K-line.

**BCU**
- "A locked BCU cannot be unlocked by diagnostic methods", and when it is locked the VIN
  can't be written. This backs ADR-0007's gate.
- Instrument mileage and the instrument-pack trip switch are readable through the BCU
  inputs.

**HEVAC and instrument pack**
- Not in the NanoCom's Discovery II module list, so they are probably not diagnosable on
  the K-line. T-26 can confirm.

## Tool quirks (treat the oracle with care)

- **ACE:** NanoCom ACE fault texts are unreliable. A pressure-sensor fault shows as a
  "control valve circuit" fault. One owner saw `18-04` on screen but `04-02` in the saved
  TXT file for the same read ([ace_fault_codes.md](ace_fault_codes.md)).
- **SLABS (P38 report, not D2):** on the Range Rover P38's Wabco ABS, NanoCom's live
  wheel-sensor voltages are put on the wrong corners, with only front-right correct
  (rangerovers.pub topic 3583). Fault codes are said to be right. Not shown for the
  Discovery 2, but **when mapping SLABS wheel channels during T-25, verify each corner
  physically** (unplug one sensor), not by NanoCom's label.
- **Td5:** NanoCom's LOGGED/CURRENT word comes from a per-slot text table. `(10,3)` reads
  CURRENT in a logged row on three cars. Map faults by bit position.
- **All modules:** record the NanoCom firmware version in every capture's metadata. No
  public changelog shows D2 fixes.

## Claims that conflict with our proven data (not adopted)

- **TD5-Dash** (`documentation/TD5-ECU-Protocol-Technical-Reference.md`) lists local ID
  `0x1A` as "logged/historic faults" and `0x20` as current faults. Our `21 1A` is **proven**
  as coolant, air and fuel temperatures, so this is not adopted. It may describe something
  else; it needs checking before any use.
- TD5-Dash also gives keybytes `57 8F` for the Td5 fast init and a bare `3E` keepalive
  variant. These are plausible (SLABS returns `C1 57 8F`) but not recorded for the Td5 here
  yet. Check them on the next capture.
