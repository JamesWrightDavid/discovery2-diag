---
title: "SLABS — fault codes and actuators"
area: docs
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [docs/discovery-2-td5/slabs.md]
summary: >
  SLABS fault-code reading and decoding (logged/current bit blocks, clear) and the StartRoutine 31 xx actuator tests, including ABS bleed.
---

# SLABS — fault codes and actuators

Part of the [SLABS page](slabs.md). The polling rule there applies: keep the bus load light.

## Fault codes

Fault memory is read as a **16-byte bit-per-fault block** (same technique as the
Td5's `21 3B`) via two identifiers, and cleared with one service:

| Operation | Command | Response | Confidence |
|---|---|---|---|
| Logged faults | `21 11` | 16-byte block | 🟢 Proven |
| Current faults | `21 47` | 16-byte block | 🟢 Proven |
| Clear faults | `14 FF FF` | `54` | 🟢 Proven |

A set bit at `(byte-offset, bit)` = one fault. `clear_faults()` uses a wider read
window (gap 0.5 s, overall 2.5 s) because SLABS writes EEPROM and only ACKs `54`
~300 ms later — the standard 60 ms window returned just the echo and looked like
"empty response" although the clear had succeeded. 🟢 Proven (session.log).

### Confirmed bit → fault anchors

Only two `(byte, bit) → number` anchors are confirmed, from the 2026-08-07 sniff
where `21 11` = `00 00 00 10 … 00 10 …` (bits at byte3.bit4 and byte10.bit4)
matched the car's two known baseline faults (`SLABS_FAULT_BITS` in
`src/d2diag/slabs/faults.py`):

| byte, bit | Number | Text | Confidence |
|---|---|---|---|
| (3, 4) | `020` | front right wheel-speed sensor — output too low | 🟢 Proven (anchor) |
| (10, 4) | `027` | shuttle valve switch — electrical failure | 🟢 Proven (anchor) |

Every other set bit decodes generically as `"unknown (byte i, bit b)"` until more
anchors are captured (via the "provoke a known fault" technique).

### ⚠️ Raw-index ↔ display-number mismatch

**The numbers `020`/`027` above are the factory tool's *display* numbers from the
sniffed session, matched to the two faults known to be on the car** — they are
**not** guaranteed to be the same as the numbers in a published fault list. The
number→text list in `references/slabs_fault_codes.md` (sourced from
rswsolutions.com, faults `012`–`114`) is a **display-number** table and even
disagrees on those two numbers (its `020` = "No Batt Supply Voltage", its `044`/
`046` = front-right/-left sensor "output low"). So the raw 16-byte bit positions,
the tool's display numbers, and any published list are **three separate
numbering spaces** that must be cross-validated bit-by-bit — do not assume a bit
index equals a display number. This mirrors the same caveat on the Td5 side.

## Actuators / StartRoutine (`31 xx`)

> ⚠️ **These touch hardware. Stationary, ignition on, at your own risk.** The
> bleed routines drive the brake system.

All routines answer `71 <rid> 20`. Commands below are 🟢 Proven from the
2026-08-07 sniff (the exact bytes were observed on the bus). Where noted "first
run from our code", the bytes are proven-from-sniff but our tool driving them has
not yet been round-tripped on the car.

| Routine | Command | Confidence |
|---|---|---|
| SLS exhaust valve | `31 2F 28` | 🟢 Proven (sniffed) |
| SLS compressor | `31 30 28` | 🟢 Proven |
| SLS buzzer | `31 31 0a` | 🟢 Proven (audible — good write-verification) |
| ABS pump relay | `31 25 08 fa` (on) / `31 25 02 fa` (off) | 🟢 Proven (on/off preliminary; trailing byte is checksum) |
| Raise left / right | `31 33 28` / `31 34 28` | 🟢 Proven |
| Lower left / right | `31 35 28` / `31 36 28` | 🟢 Proven |
| Per-wheel ABS valve test | `31 22 <sub> <mask> c1 f4` + 8×`00` | 🟢 Proven |

**Per-wheel valve test bit-mask** (`31 22`): `sub` = `0x10 + wheel index`, `mask` =
2 bits per wheel in order **FR, FL, RR, RL** — `03` = FR (bits 0–1), `0c` = FL
(2–3), `30` = RR (4–5), `c0` = RL (6–7); the two bits are in/out valve. `c1 f4`
constant (likely duration/timeout). In code: `Slabs._WHEEL` /
`Slabs.wheel_test(corner)`, corner ∈ {`fl`, `fr`, `rl`, `rr`}.

### ABS bleed routines

Two procedures under `RID_ABS_TEST` (`31 22`), distinct from the per-wheel valve
test. The **command frames are proven from the 2026-08-07 sniff**; our code
issues them as `Slabs.abs_power_bleed()` / `abs_module_bleed_step()` /
`abs_module_bleed()`, and the **first run from our own code** against the car has
not been logged yet — so treat the *frames* as 🟢 Proven and *our driving of
them* as 🟡 to be confirmed on the next car session.

| Routine | Data after `31 22` | Method |
|---|---|---|
| Power bleed — **start** | `04 00 49 c4` + 8×`00` | `abs_power_bleed(True)` |
| Power bleed — **stop** | `04 00 40 00` + 8×`00` | `abs_power_bleed(False)` |
| Module bleed step 1 | `11 00 c0 7d 00 bb` + 6×`00` | `abs_module_bleed_step(1)` |
| Module bleed step 2 | `12 00 c0 7d 00 bb` + 6×`00` | `abs_module_bleed_step(2)` |
| Module bleed step 3 | `13 00 c0 7d 00 bb` + 6×`00` | `abs_module_bleed_step(3)` |
| Module bleed step 4 | `14 00 c0 7d 00 bb` + 6×`00` | `abs_module_bleed_step(4)` |

- **Power bleed** runs the ABS pump to push fluid through the modulator.
- **Module bleed** cycles modulator circuits `0x11`→`0x14` in sequence.
  `abs_module_bleed()` runs all four steps with ~2.3 s between them (the factory
  tool's cadence). All answer `71 22 20`.

The web layer exposes these as actuator actions `bleed_power_on`,
`bleed_power_off`, `bleed_module` (`_SLABS_ACTUATORS` / `_slabs_do` in
`sources.py`).
