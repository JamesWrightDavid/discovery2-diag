---
title: "Test backlog — the living plan for what to do next in the car"
area: references
status: stable
version: 1.1
updated: 2026-10-01
summary: >
  Living backlog of what to test next in the car or with a borrowed tool, each item with context tag, procedure and pre-written decision rule; Resolved log.
---

# Test backlog — the living plan for what to do next in the car

**This is the single reference for "what do we test next".** Before a session in the
car (or with a borrowed diagnostic tool), open this file and pick items by context tag.
After the session, route each result to its permanent home (table below), then move the
item down to **Resolved** with the date and the outcome. Nothing else in the repo is a
to-do list for car work — `TODO.md` covers code and infrastructure only.

Updated 2026-10-01.

## How to use it

1. **Pick by context.** Every test carries the conditions it needs:
   `[drive]` moving, `[idle]` stationary with the engine running, `[key-on]` ignition on
   engine off, `[lift]` a wheel safely off the ground, `[tool]` a borrowed reference tool
   (Nanocom), `[offline]` no car needed.
2. **Run it.** Each item states the exact command, what to watch, and — importantly —
   the **decision rule**: what result means what. A test without a decision rule in
   advance is how we end up measuring the clock (see the method lessons in `TODO.md`).
3. **Route the result.** Then update this file: outcome + date, and move it to Resolved.

### Where results go

| Result | Home |
| --- | --- |
| LID → field mapping, scaling, confidence | `src/d2diag/signals/*.json` via `upsert_field` — never hand-edited |
| Protocol facts (framing, init, services, timing) | `references/<module>_*.md` + the summary in `references/protocol_state_handoff.md` |
| Verdicts on external repos/claims | `references/td5-external-findings.md` |
| Fault codes and the car's actual condition | the sister project `../Discovery 2/` — **not** here |
| Raw captures | `logs/` (gitignored; scrub VIN/EKA before anything is published) |

### Standing rules

- K-line is a shared bus: **one module at a time**, always ending with `release()` (`82`).
- SLABS must be polled lightly — see `references/slabs/overview.md`.
- Airbag/SRS is **read-only**. No outputs, ever.
- macOS: `/dev/cu.*`, never `/dev/tty.*`.
- Anything that moves the car or actuates brakes: handbrake on, nobody underneath.

### Contributing a result from another car

Run a test and note the car (reg, variant, year), the raw values and how you confirmed
them. Then open a PR or issue that updates the item here and the matching module page in
`docs/`. A result from a *different* Td5 is especially valuable: it tells us what is
model-general and what is specific to RDL 016.

---

## Open tests

### P1 — Td5 air/boost mapping (the biggest open question)

#### T-01 `[idle]` `[drive]` — Is `21 1C`@4 the measured MAF?
**Question.** `1C`@4 sat in the store as the unscaled `maf_raw` candidate until commit
`bba77a9` moved `maf` to `1D`@4 with a provisional 2-point calibration.
BinOwl_Td5Gauge names `1C`@4 as MAF, u16/10 kg/h. In our logs `1C`@4 is zero in
502/503 samples (rare junk blips up to 51080) across idle, load and >2500 rpm — but
RDL 016 has `air flow circuit (Current)` live, so a dead sensor reading zero with
occasional garbage is exactly what we would expect. That would make `1D`@4 a
*modelled* air mass shown under a measured name. Background:
`references/td5-external-findings.md`.

**Setup.** Td5 session, CSV logging + raw log on. Read the **whole** `21 1C` block
(8 data bytes), not just @0 — and log `1D`@4 in the same cycle.

**Procedure.** Idle 30 s → hold ~2000 rpm 30 s → one full-load pull if driving.
Best case: do it on a Td5 with a healthy MAF, or after the air-flow fault is fixed.

**Decision rule.**
- `1C`@4 non-zero and roughly 55–65 kg/h at idle, ~185–200 at 2000 rpm →
  `1C`@4 = **MAF (proven)**; `1D`@4 gets renamed to a modelled air mass and its
  invented scale/bias dropped.
- `1C`@4 still zero-with-blips while `1D`@4 tracks load → consistent with the dead
  sensor; **inconclusive**, both stay `candidate`. Do not "fix" it by rescaling.
- `1C`@4 moves but nowhere near kg/h → it is something else. Record the range and
  stop guessing at a scale.
- Fastest possible answer: **T-19** — one MAF reading off a reference tool screen
  settles it without any of the above.

#### T-02 `[drive]` — Pin the wastegate/EGR LID and settle the scale
**Question.** We now carry **two representations** of each, both `candidate` in the store:
the `1D` duty bytes (`wastegate_modulator` `1D`@17, `egr_modulator` `1D`@15, u8 ×100/255)
and the **native LIDs** ported 2026-10-01 (`wastegate_pos` `0x38`, `egr_pos` `0x37`, u16).
**Two Simon sources (the `.md` and the newer Td5-Diagnostic-App) both scale `0x37`/`0x38`
at `/100`**, the app explicitly "not /1000"; BinOwl's `/1000` is the outlier. The real open
question is now **where the signal lives**: the Simon app puts EGR/wastegate ONLY at native
`0x37`/`0x38` and has nothing at `1D`@15/@17, yet our four 2026-08 drives saw `1D`@15 fall
under load (EGR-like) and `1D`@17 rise with boost. Both can't be the live source.
`0x37`/`0x38` respond on RDL016 but read 0 at idle, so idle can't discriminate. (EGR inlet
is separately at `0x45` → `egr_inlet`.)

**Procedure.** Same drive as T-01. Read `21 37`, `21 38`, `21 45`, `21 1D` together and log a
boost pull: steady cruise → full-load pull to ~3500 rpm → overrun.

**Decision rule.**
- **Which LID:** whichever of the native `0x38`/`0x37` or the `1D`@17/@15 bytes actually
  moves with boost/load across the pull is the live source → promote it to `proven`, demote
  the other (record it as not-that-signal). If both move identically, keep the natively
  scaled `0x38`/`0x37` as preferred.
- **Scale:** confirm `/100` puts the mover in the published band (0% idle, 20–40% boost,
  max ~40%); if not, correct it. Same logic sets `egr_inlet` (`0x45`).

#### T-03 `[drive]` — Name the `21 1D` fuelling fields
**Question.** The `1D` block carries several fuelling fields. Stored as candidates:
`driver_demand`@0, `injection_qty`@6 (proven), `smoke_limit`@10, `torque_limit`@12 (the last
two from the Simon app). **Unit conflict on @0:** BinOwl reads it as fuel demand mg/stroke,
the Simon app as pedal position % (i16/100). **Not stored:** `1D`@14 = idle demand (BinOwl +
Simon app) because it overlaps our `egr_modulator`@15 candidate — part of the T-02 conflict.

**Procedure.** In the same log: idle (no pedal) → steady pedal → **overrun** (lift off in
gear) → idle again.

**Decision rule.**
- `driver_demand`@0 should follow the pedal and drop to ~0 on overrun. Its **unit** is set
  by whether the full-throttle value reads like a percentage (~100) or a fuelling mass
  (tens of mg/stroke); fix the store unit/scale accordingly.
- `smoke_limit`@10 / `torque_limit`@12 should sit at or above `injection_qty` and cap it
  under load; confirm they behave as ceilings, else demote.
- `1D`@14 vs `egr_modulator`@15: if @14 behaves as an idle-only demand AND the EGR signal is
  shown by T-02 to live at native `0x37` (not `1D`@15), store `idle_demand`@14 and drop
  `egr_modulator`@15. Resolve jointly with T-02 — do not map both over byte 15.

#### T-04 `[idle]` — What is `21 1C`@6?
Constant `0x009C` (156) in every capture we have. Watch it across cold start, warm idle,
load. If it never moves it is a reserved byte — record that and stop looking.

#### T-05 — EGR Inlet %, still unlocated
`1D`@15 = EGR modulator is a solid candidate; `1D`@16 is a constant-0 dead byte, so the
Nanocom page order misleads here. `1D`@14 is now claimed as idle fuel demand (T-03), so
the remaining unknown bytes in `1D` need a differential drive. Low priority until T-01/02
are settled.

#### T-23 `[key-on]` — Confirm the wastegate modulator output `30 BE`
We have the EGR modulator output (`30 BD`) proven. The wastegate modulator
(`30 BE FF 00 0A 13 88`) comes from Ekaitza captures and has never been run from our code.

**Procedure.** Engine off, behind the explicit actuator confirmation. Run `30 BE` and
listen/observe at the wastegate actuator.

**Decision rule.** An audible/visible actuation that stops when the routine ends
promotes it to proven in `engine-td5.md`. No movement, with `30 BD` still working as a
control in the same session, means the frame is wrong for this ECU: record it and stop.

### P2 — Td5 read-only additions (cheap, no risk)

#### T-06 `[key-on]` — ECU identification `1A xx`
We never read `1A`. Ekaitza gives `1A 87` = VIN, `1A 9A` = ECU type, `1A 9B/9C` = further
IDs. Read all four once, note the framing and lengths.
⚠️ **The response contains the VIN** — the raw log must be scrubbed before it goes
anywhere public (`references/hex-PII` rule: hex-encoded VIN survives text scans).

#### T-07 `[key-on]` — Injector classification codes
Five-digit code per injector, in a Settings/identifier block the dashboard never polls, so
they are in **no** raw log we have. Needs a targeted read. Useful for the car register
(injector matching), not for live data.

**Format (community-documented, 2026-10-01):** the 5 digits are — digits **1-2** = start-of-
injection offset from nominal (range ±0.000127 s), **3-4** = the same for end-of-injection,
**5** = a measured idle-performance variance. Baseline on RDL016 noted as `ABNFE` in
`references/menus/td5.md`. When read, record the raw Settings bytes AND the tool's displayed
5-digit codes so the byte↔digit encoding can be mapped (as with the EKA code).

#### T-08 `[key-on]` — `21 1E` driver switches / `21 36` relay-output status
**Reframe (Simon app, 2026-10-01):** `0x1E` is the **driver switch** bitfield and `0x36` is
the **relay / output status** bitfield (NOT "both switch fields" as previously assumed).
`1E` toggles `00 CA`↔`00 EA` (bit `0x20` = byte0 bit5); `36` sat constant `00 0D`.
Differential procedure: connect, then actuate **one at a time**, annotating the log.

**`0x1E` hypotheses** (SimonRafferty, `.md` + Td5-Diagnostic-App; two marked *confirmed* —
[td5-cross-reference.md](td5-cross-reference.md)); candidates to confirm, not facts:
- byte0 (DB1): bit1 = clutch (0 = pressed), bits2/3/4 = cruise master/set/resume.
- byte1 (DB2): bit7 = brake-main (0 = pressed), bit3 = A/C request, bit6 = transfer box
  (1 = LOW), bit1 = ignition, bit5 = security link.
- ⚠️ the one bit WE have seen move is byte0 **bit5**, NOT in Simon's map — resolve by actuation.
- Actuate: brake → clutch → cruise on/set/resume → A/C request → transfer high/low.

**`0x36` hypotheses** (Simon app — these are OUTPUTS/relays, observe don't actuate): byte0
bit1 = rad-fan drive; byte1 bit0 = main relay, bit2 = fuel pump, bit3 = A/C clutch,
bit4 = MIL (active-high), bit5 = glow-plug light, bit6 = glow-plug relay.

**Decision rule.** A `1E` bit that flips with exactly one actuation, matching a hypothesis,
is that switch → store `candidate` (then `proven` after a second, independent confirmation).
For `0x36`, correlate each bit against a known output state (glow light on cold start, fuel
pump prime, rad fan, MIL) rather than a driver action. A bit that flips with two different
actions is unidentified — repeat. Ekaitza's ECU-pin map is background, not a byte.bit claim.

#### T-09 `[tool]` — `21 3D` feature/config block
14-byte status block, read in bulk with `21 3D 20 0E 32 24`. To decode it we need the
reference tool's **Settings → Feature/config** screen: all 21 ENABLED/DISABLED flags in
displayed order plus ECU Status. Read them off the screen; no sniff needed.

### P3 — SLABS

#### T-10 `[idle]` — Confirm session reliability across occasions
The init-pulse fix has only been tested over one afternoon. Run on cold start, after a
long standstill, and in the cold:
```
PYTHONPATH=src python3 tools/slabs_probe.py --quiet 5 --hold 30 --no-td5
```
**Decision rule.** ≥50 % hit rate per attempt and the dashboard connecting on the first
attempt = reliable, close the item. Anything worse: keep the raw logs, do not tune blind.

#### T-11 `[idle]` — Lower `retry_sleep`
SLABS `establish` waits 28 s between attempts, a legacy from the broken-timing era. Try
3–5 s and measure the hit rate over ~10 attempts. **Rule:** keep the shorter wait only if
the hit rate is statistically indistinguishable — and mix the order, do not run the two
settings as separate time blocks.

#### T-12 `[idle]` — Decide W5 and P4
Both implemented, disabled, unproven: `--init-idle 1000` and `--write-gaps 0,5`. The P4
measurement predates the exact wait, so it measured the wrong thing. Re-measure or delete
the flags — do not leave them as dead options.

#### T-13 `[idle]` — Scale the remaining SLABS analog LIDs
Open per `references/slabs/services-and-lids.md`: `21 53/55` (supplies), `44/49/57`
(valves/voltages), `50` (ABS-sensor V). Read within the 1 Hz budget. For the settings
LIDs where LID→function is unsolved, the only method is differential: change **one**
setting, see which raw byte moves.

#### T-14 `[lift]` — Prove the wheel order
`wheel_speed_fl/fr/rl/rr` is a **hypothesis**. Jack up ONE wheel safely (axle stands,
handbrake, engine running, SLABS connected), spin it by hand, see which field moves.
Repeat for a second wheel → then the byte order is proven. Without jacking, it stays a
candidate — do not promote it on plausibility.

#### T-15 `[idle]` — ABS bleed commands, first live run
⚠️ **Brake system. Only during an actual brake bleed.** `abs_power_bleed(True/False)` and
`abs_module_bleed()` are proven from the sniff but have never been run from our code.
Verify each replies `71 22 20`. If only verifying without bleeding: pulse power_bleed
on→off, confirm the ack, and do **not** run the full module sequence.

### P4 — Other modules

#### T-16 `[key-on]` — BCU: map the read-only auth boundary
**Question.** How much of the BCU is legible **without** SecurityAccess? First contact,
address `0x40`, keybytes `E5 8F`, EKA-behind-SA and the rolling seed are all already
settled (see Resolved and `references/valeo_bcu_capabilities.md`) — the seed→key is
unknown and we have stopped chasing EKA. What we have **never** tested is whether the
BCU's live inputs (doors, key-in, locking, indicators, `21 D8..E9/2C/2D`) and settings
(`21 C6..EB`) actually *require* auth, or whether only EKA does. The reference tool did
SA before every read out of habit, so the 2026-08-09 sniff cannot answer it. If the
inputs read unauthenticated, we get live BCU body data for the dashboard for free.

**Setup.** Read only — no writes, no key, no actuators. Ignition cycle (off → fob key →
on) to put the BCU in diagnostic mode. New tool:
```
PYTHONPATH=src python3 tools/bcu_scan.py --serial auto
PYTHONPATH=src python3 tools/bcu_scan.py --serial auto --stimulus "open the driver door"
PYTHONPATH=src python3 tools/bcu_scan.py --serial auto --full     # optional: sweep 21 00..FF
```
It sweeps each LID **twice in shuffled order**, fetches a seed up front to flag the
`21 CC` decoy, and classifies every response: **DATA** (positive, plausibly real),
**SEED-DECOY** (positive but just the current seed), **DENIED** (`7F..33`
securityAccessDenied), **NRC** (other negative, e.g. `31` = no such LID), **NO-RESPONSE**,
or **INCONSISTENT** (disagreed between passes = comms-flaky, not gating). `--stimulus`
does a baseline → change one input → re-read and prints which LIDs' bytes **moved**.

**Decision rule.**
- A LID in **DATA**, stable across both passes, whose bytes **move** under `--stimulus`
  = real live data readable without auth → add it to the BCU source (`web/sources.py`)
  and map the field as `candidate`. This is the win condition.
- **DATA** but constant even under stimulus = a static/placeholder positive; record the
  bytes, do not map a live field yet.
- **DENIED** = genuinely auth-gated; note it and move on (we cannot unlock).
- **NRC 0x31** = LID not supported on this module (expected for most of a `--full` sweep).
- **INCONSISTENT / NO-RESPONSE on both passes** = do not conclude; the BCU init is flaky
  (~1 in 4). Re-run before calling anything gated. **Mix the order, never read a block
  as one time-ordered sweep** — the tool shuffles for exactly this reason.

**Route results** to `references/valeo_bcu_capabilities.md` (the auth-boundary table) and,
for any live field found, the signal store + a BCU `DataSource`. Never the EKA code.

> **Update (2026-10-01, ADR-0007).** The "stopped chasing EKA" note above still holds for
> *our* old pairs (rolling seed, no clean keys). A rented NanoCom changes it: it computes
> the correct key per rolled seed, giving clean pairs for an **offline** seed→key
> derivation (`bcu/keygen.py`). See T-27/T-28 and
> [bcu_security_research.md](bcu_security_research.md). Live unlock stays gated.

#### T-17 `[idle]` — Autobox (EAT) read faults
The one module we have never got fault codes out of. Engine **running**, selector in
**P/N**. Framing is solved (`72 <len> <data> <XOR-cs>`) and `72 05 04 00 73` →
`72 09 60 01 00 00 00 00 1B` is confirmed — but the response's meaning is unknown, so do
not interpret it as a fault count yet. Note verbatim what comes back.

#### T-18 — Airbag live verification
Implemented, addressed framing at `0x5B`, read-only by construction, **never verified
against the car**. A single successful establish + read-faults is all that is needed.
⚠️ Read only. No outputs.

### P5 — Needs a borrowed reference tool `[tool]`

#### T-19 — Screen values to correlate against raw bytes
We already have the raw bytes for most blocks; what we lack is the tool's plain-text
values. Highest value, no sniffing required — write down **all** values in **displayed
order**:
- SLABS → ABS Inputs (wheel speeds, ABS sensor V, valves, pump monitor/relay, battery,
  ECU supply, ground ref, HDC brake, engine speed/torque/throttle) → vs `21 43/44/49/50/57`
- SLABS → SLS Inputs (L/R height, sensor supply, L/R volts, exhaust valve, compressor
  relay) → vs `21 53/54/55`
- TD5 → Settings → Feature/config → solves T-09
- TD5 → the MAF/air-flow live value → **settles T-01 directly**

#### T-20 — Fault read across all modules
Per-module checklist with the exact wording to note down:
`references/fault_read_checklist.md`. Codes go to the sister project.

#### T-24 `[key-on]` `[idle]` — React dashboard parity in the car
Run the new app (`/`) next to `/legacy/v2` on TD5 then SLABS. **Decision rule:** if every
Drive/Inputs value, fault, output and capture matches, delete the legacy pages; any gap
becomes an issue first (`specs/2026-10-01-web-ui-design.md`).

### P6 — Offline `[offline]`

#### T-21 — Decode `21 0E` / `21 32` (homologation / map variant)
We already hold the bytes: `61 0e 73 73 75 75 74 74 64 64 70 70 30 30 30 30 38 38` —
ASCII with every character doubled ("ssuuttddpp00008 8"). Work out the field split and
what the variant string means; no car needed.

#### T-22 — Distinguish comms glitches from real sensor faults
Signals sharing a LID are read in one request, so a bad read corrupts them together.
Whole-LID corrupt = comms glitch (~1 % baseline); one signal bad while its LID-mates are
valid = a real sensor/circuit fault, corroborated by the ECU's own DTC. Tag CSV/snapshot
rows with a `comms_glitch` marker and classify in the analysis. Detail in `TODO.md`.

### P7 — NanoCom rental readiness `[tool]` `[offline]`

The rental plan and tooling are specced in
[`specs/2026-10-01-nanocom-capture-design.md`](../specs/2026-10-01-nanocom-capture-design.md)
and ADR-0005. The session runbook is
[nanocom_capture_protocol.md](nanocom_capture_protocol.md).

#### T-25 `[tool]` — Capture every module against the NanoCom screen
Passive ESP32 tap; log with `tools/esp32_read.py` and the structured markers
(`s <module>/<page>`, `v <name>=<text>`). Work the per-module screen order and budget in
[nanocom_capture_protocol.md](nanocom_capture_protocol.md): hold each screen ~10 s, change
one input at a time, and record (never replay) every write/security/coding frame.
**Decision rule.** After the session, `tools/nanocom_import.py --write` must reproduce the
already-proven Td5 mappings (rpm/coolant/battery) from the labelled capture before any new
mapping is trusted; a new mapping enters the store as `candidate` with the capture as
provenance, promoted only by a later on-car confirmation.

#### T-26 `[key-on]` — Read-only address scan to confirm/rule out the asserted modules
Run `tools/module_scan.py auto` (ignition on, stationary). It walks fast-init and 5-baud
addresses and records who answers, sending only init + StopCommunication.
**Decision rule.** An address that responds and is not an already-known module is a
candidate — tag it by key bytes and plan a capture (e.g. cruise). An address silent across
the scan is ruled out for this car; note it and stop guessing. The `0x18` responder: record
its key bytes to characterise it. Route results to the module pages and the system map.

#### T-27 `[tool]` — Capture clean BCU `(seed, key)` pairs
During the BCU security session (NanoCom READ-SET EKA + key programming, run several
times), record every `27 01`/`27 02` exchange with valid checksums. The high-impedance tap
must not corrupt the frames (unlike the old KKL tap — see
[valeo_bcu_capabilities.md](valeo_bcu_capabilities.md)).
**Decision rule.** Feed the clean pairs to `src/d2diag/bcu/keygen.py`. A family that fits
every pair with evidence to spare → commit the **algorithm** (never the pairs or any EKA).
No fit → widen the search or plan a bench EEPROM read
([bcu_security_research.md](bcu_security_research.md)). Offline only; no live byte here.

#### T-28 `[key-on]` — Verify a derived BCU key on-car (GATED)
⚠️ **Security/write action — behind ADR-0007 and an explicit confirmation gate, never
automatic, never part of a default path.** Only after T-27 yields a confirmed algorithm:
our own `27 01` → compute key → `27 02`, expecting `67 02`.
**Decision rule.** A positive `67 02` proves the derived keygen; record that the algorithm
is verified (not the key). An `invalidKey` (`7F 27 35`) means the derivation is wrong —
back to T-27 with more pairs. Do not retry blindly (likely attempt counter/lockout).

---

## Resolved and appendices

Settled items (dated, inconclusive ones included) live in
[test-plan-resolved.md](test-plan-resolved.md). Step-by-step appendices this backlog
indexes: `car-test-slabs-bcu.md` (SLABS signals, ABS bleed, BCU probe),
`fault_read_checklist.md` (per-module fault reading), `final_session_plan.md` and
`reference_tool_sniff_plan.md` (reference-tool sessions), `bcu_sniff_plan.md` (BCU).
