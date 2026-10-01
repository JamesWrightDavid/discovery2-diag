---
title: "SLABS actuators, input LIDs and bleed frames — evidence"
area: references
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [references/slabs/overview.md]
summary: >
  Sniffed SLABS StartRoutine 31 xx actuator frames, the per-input LID sweep, byte-variance analysis, field identity from tool screens and the complete ABS bleed frames.
---

# SLABS actuators, input LIDs and bleed frames — evidence

Part of the [SLABS protocol evidence](overview.md). The canonical, curated SLABS page is [docs/discovery-2-td5/slabs.md](../../docs/discovery-2-td5/slabs.md).

## Actuators / tests — StartRoutine `31 xx` → response `71 xx 20`
**This is the write/control protocol.** All respond `71 <rid> 20`.
| Command | Function |
|---|---|
| `31 25 <p>` | **ABS pump relay** (`31 25 08 fa 5c`=on, `31 25 02 fa 56`) |
| `31 2F 28` | **SLS bleed valve** (exhaust valve) |
| `31 30 28` | **SLS compressor** |
| `31 31 0a` | **SLS buzzer** |
| `31 33 28` | **raise left** |
| `31 34 28` | **raise right** |
| `31 35 28` | **lower left** |
| `31 36 28` | **lower right** |
| `31 22 <sub> <p…>` | **ABS bleed + wheel tests** (12-byte param) |

**`31 22` subcommands** (the byte after `22` selects the circuit, then `<flags> c1 f4 …`):
| sub | function (from markers) |
|---|---|
| `04` | ABS power bleed (`31 22 04 00 49 c4 …`) |
| `11` | front left / module bleed step 1 (`31 22 11 0c c1 f4` = FL test; `…11 00 c0 7d 00 bb` = bleed) |
| `10` | front right (`31 22 10 03 c1 f4`) |
| `13` | rear left (`31 22 13 c0 c1 f4`) |
| `12` | rear right (`31 22 12 30 c1 f4`) |
| `14` | module bleed step 4 |
**The flag byte = a 2-bit mask per wheel (decoded 2026-08-07):** `03`=FR (bits 0–1),
`0c`=FL (bits 2–3), `30`=RR (bits 4–5), `c0`=RL (bits 6–7) — i.e. 2 bits (in/out valve)
per wheel in the order FR, FL, RR, RL. `sub` = `0x10 + wheel index` (FR=0…RL=3). `c1 f4`
constant (likely duration/timeout). Live data is also per-wheel: `21 43`=4
wheel speeds, `21 50`=4 sensor voltages → fits a wheel-oriented UI perfectly.

**NOTE — lamp tests missing cleanly:** the instrument-lamp tests (TC/ABS/HDC/brake/SLS lamps)
were only run in the FIRST session (baud clash → garbage). The bytes are unusable; the function
exists but must be **re-logged** (list the reference tool order at the same time, please).

## Input LIDs (sniffed 2026-08-08, full per-input sweep)
The reference tool polls a fixed LID set per screen; the operator stepped through
the entries. All input LIDs are now identified (offset/scale per entry still to be isolated
with targeted captures):

| Screen | LIDs | Entries |
|---|---|---|
| SLS inputs | `21 53`, `21 54`, `21 55` | L/R sensor value (**`21 54` b0/b1 decoded**), sensor supply, value (V), exhaust valve (V), compressor relay (V) |
| ABS inputs | `21 43`, `21 44`, `21 49`, `21 50`, `21 57` | wheel speed (`21 43`), ABS sensor V (`21 50`), inlet/outlet valves, pump relay/monitor, battery, ECU supply, ground ref, HDC brake, engine speed/torque/throttle (via CAN) |
| Switches | `21 42`, `21 48`, `21 56`, `21 58` | neutral, low range, diff lock, reverse, HDC, shuttle, **any-door (`21 56` byte0 bit0 — PROVEN: 00 closed/01 open)**, plip |
| Settings | `21 45`, `21 46`, `21 49`, `21 59` | **Stable raw bytes proven (RDL 016):** `45`=`7f`, `46`=`78 76`, `49`=`00 00 01`, `59`=`00 0f 0f 0f`. ⚠️ **LID→setting UNSOLVED** — two order-based labelings contradict each other (card order unstable). Solve with DIFFERENTIAL: change ONE setting → see which raw byte changes. |

## Byte variance from session.log (`analyze_capture.py --variance`)
Which bytes **moved** during the capture = ready-made differential candidates. Narrows
down what should be correlated against reference tool values:

| LID | Byte structure (proven from variance) |
|---|---|
| `21 54` | **byte0 = left height, byte1 = right height** (both vary = live). Confirmed. |
| `21 50` | 4 bytes, **one ABS sensor voltage per wheel** (~`0x72`); byte1/2 varied (two wheels). |
| `21 43` | constant `7c 00 ×4` stationary = wheel-speed **baseline** (≠0). |
| `21 53` | byte0 ~`d1/d2` varies (supply candidate); byte1 const, byte2/3 = `0f 0f`. |
| `21 55` | byte3 varies (small value 00/02/03); the rest `00`. |
| `21 57` | byte0 varies (`05/06/08`); the rest `0f 0f 0f`. |
| `21 44` | **rich block** — offsets 2,3,4,6,8–13 vary (valves/pump/battery/supply). Requires labels. |
| `21 49` | constant `00 00 01`. |

**TD5 switches (session.log):** `21 1E` byte1 = switch bitfield (toggled `CA`→`EA`
= bit `0x20`; byte0 const); `21 36` constant `00 0D` (fixed switches). So we know
*which byte* but not *which switch* — requires an annotated toggle.

## Field identity from reference tool screen reading 2026-08 (structure proven, scale candidate)
Values read off the screen, correlated against old raw bytes (not the same
moment → scale = candidate). **Structure (which LID = which screen section) is proven** via
display order + value range:

| LID | Field | Candidate |
|---|---|---|
| `21 43` | **4× wheel speed** (2 bytes/wheel) | stationary `7c 00` = 1.7 km/h (baseline) |
| `21 50` | **4× ABS sensor voltage** (1 byte/wheel) | FR byte0 `0x72`=114 → 2.17 V (≈×0.019); FL blank in reference tool |
| `21 44` | **large analog block (14 bytes):** 8 valve voltages + pump relay/monitor + battery + ECU supply | valves `0x01–03`→ ×0.01 V (0.01–0.03); **byte12/13 = battery/ECU supply** (~`0xb3/b1`→ ×1/16 ≈ 11.3–11.5 V; VARIES = matches) |
| `21 53` | **L/R sensor supply** (byte0/1) | `0xd1`=209 → ~5 V (≈×0.024); byte2/3 `0f 0f` |
| `21 54` | **L/R height** (byte0=left, byte1=right) | **proven** (149/162) |
| `21 55` | compressor relay | byte3 `0x02` → 0.13 V (candidate) |
| `21 49`/`21 57` | CAN-derived: engine speed (noise 195–235 engine off), torque, throttle | throttle 0–86 on throttle application |

⚠️ **The exact byte↔valve order and scales require ONE fresh sniff capture** (raw +
reference tool value at the same moment) of the ABS/SLS inputs screens. Without it this is
the ceiling. Battery/ECU supply (21 44 byte12/13) is strongest — they vary and match.

**Next step for full decoding:** targeted differential captures — change ONE thing
(open a switch, lift a corner, measure a voltage) and compare the raw bytes before/after.
Run `analyze_capture.py --variance <log>` for the candidates directly.

### ABS bleed — complete frames (proven from the sniff 2026-08-07, coded)
Two procedures under `31 22`, distinct from the wheel-valve test (`31 22 <sub> <mask> c1 f4`):

| Command | Frame (data after `31 22`) | Code |
|---|---|---|
| Power bleed START | `04 00 49 c4` + 8×00 | `Slabs.abs_power_bleed(True)` |
| Power bleed STOP | `04 00 40 00` + 8×00 | `Slabs.abs_power_bleed(False)` |
| Module bleed step 1 | `11 00 c0 7d 00 bb` + 6×00 | `abs_module_bleed_step(1)` |
| Module bleed step 2 | `12 00 c0 7d 00 bb` + 6×00 | `abs_module_bleed_step(2)` |
| Module bleed step 3 | `13 00 c0 7d 00 bb` + 6×00 | `abs_module_bleed_step(3)` |
| Module bleed step 4 | `14 00 c0 7d 00 bb` + 6×00 | `abs_module_bleed_step(4)` |

`abs_module_bleed()` runs all four in sequence with ~2.3 s between (the reference tool's
cadence). All respond `71 22 20`. ⚠️ Brake system — stationary only, ignition on.
