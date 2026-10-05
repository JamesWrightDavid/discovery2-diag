---
title: "Td5 LID cross-reference — our mappings vs five external repos"
area: references
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [td5-external-findings.md, td5-full-coverage-and-maf.md]
summary: >
  Per-LID comparison of our signal store against Ekaitza, SimonRafferty, BinOwl, hairyone/TD5Tester and td5opencom. Shows where the sources agree (so we don't re-derive), where they disagree (with the resolver test), and what we ported as candidate.
---

# Td5 LID cross-reference — ours vs five external repos

So we don't redo solved work: what each external Td5 repo maps, lined up against our
signal store (`src/d2diag/vehicles/lr_d2/signals/td5.json`). The research narrative is in
[td5-external-findings.md](td5-external-findings.md); this is the field-by-field table and
the authority for what we ported.

Sources: **Ours** (store, car-verified where `proven`) · **Ek** EA2EGA/Ekaitza_Itzali
(Python, real sniffs; `fuelling_to_json.py`) · **SR** SimonRafferty (MIT;
`TD5_PROTOCOL_REFERENCE.md`, big-endian corrected 2026-09) · **SR-App** SimonRafferty/
Td5-Diagnostic-App (MIT; `td5_provider.cpp` — the newest, most-corrected decode, mined
2026-10-01) · **BO** k0sci3j/BinOwl_Td5Gauge · **H1** hairyone/TD5Tester (Apache-2.0) ·
**TOC** td5opencom lineage (BennehBoy port).
Offsets are in the **data field** (after `61 <lid>`), i.e. what `read_local_identifier`
returns; external repos that count from the raw frame are shifted by their 3-byte header.

## Live data — agreement (already solved; no new work)

| Field | Ours | Ek | SR | BO | H1 | Verdict |
|---|---|---|---|---|---|---|
| rpm | `09`@0 u16 ×1 **proven** | ✓ | ✓ | ✓ | ✓ | all agree |
| speed | `0D`@0 u8 km/h **proven** | ✓ | ✓ (×0.621 → mph) | ✓ | ✓ | all agree |
| battery | `10`@0 u16 ×0.001 V **proven** | ✓ | ✓ | ✗ (BO decode wrong, rejected) | ✓ | ours/Ek/SR agree |
| coolant_temp | `1A`@0 u16 ×0.1 −273.2 **proven** | ✓ | ✓ | ✓ | ✓ ((raw−2732)/10) | all agree |
| air_temp | `1A`@4 **proven** | ✓ | ✓ | ✓ | ✓ | all agree |
| fuel_temp | `1A`@12 **proven** | ✓ | ✓ | ✓ | ✓ | all agree |
| manifold_press | `1C`@0 u16 ×0.0001 bar **proven** | ✓ | ✓ | ✓ (/100 kPa = same) | ✓ | all agree |
| injection_qty | `1D`@6 u16 ×0.01 mg/stroke **proven** | ✓ (1D "fuel-usage") | — | ✓ (@6 ×0.01) | — | ours/Ek/BO agree |
| rpm_error | `21`@0 s16 **proven** | ✓ | — | — | — | agree |
| ambient_press 1/2 | `23`@0/@2 u16 ×0.0001 bar **proven** | ✓ | ✓ (baro) | ✓ | — | agree |
| balance_1..5 | `40`@0..8 s16 **proven** | — | ✓ (5× s16 trim) | ✓ (5× s16) | — | agree |

**Takeaway:** our proven core is independently confirmed by 2–4 repos each. Nothing to port.

## Live data — disagreement or gap (ported as candidate / flagged)

| Field | Ours | External | Verdict → action | Resolver |
|---|---|---|---|---|
| **MAF (measured)** | `maf_sensor` `1C`@4 raw **cand** (faulted/0 on RDL016) | Ek: `1C`@4 = MAF raw · BO: `1C`@4 = MAF u16 ×0.1 kg/h | agree `1C`@4 is the physical sensor; BO adds the scale | **T-01** |
| **MAF (modelled)** | `maf` `1D`@4 u16 ×0.1 −515 **cand** | none name `1D`@4 as MAF | our own speed-density hypothesis; external MAF lives at `1C`@4 | **T-01** |
| **Wastegate** | `wastegate_modulator` `1D`@17 u8 ×(100/255) **cand** · **ported** `wastegate_pos` `38`@0 u16 ×0.01 % **cand** | SR md + **SR-App: `38` /100 %** · BO: `38` /1000 % | `0x38` native LID; **scale resolved /100** (two Simon sources; BO outlier). SR-App has NO EGR/wastegate in `1D` → conflicts with our `1D`@17 | **T-02** |
| **EGR** | `egr_modulator` `1D`@15 u8 ×(100/255) **cand** · **ported** `egr_pos` `37`@0 u16 ×0.01 % **cand** | SR md + **SR-App: `37` /100 %** | native `0x37` /100; SR-App has nothing in `1D` → conflicts with our `1D`@15 | **T-02** |
| **EGR inlet** | **ported** `egr_inlet` `45`@0 u16 ×0.01 % **cand** | SR-App: `0x45` EGR Inlet /100 % | **located** — replaces the abandoned `1D`@16 mis-map | **T-02** |
| **Battery (direct)** | **renamed** `reference_voltage`→`battery_direct` `10`@2 u16 ×0.001 V **cand** | SR md: "ref V"@2 · **SR-App: `10`@2 = 2nd battery ("Battery Direct")**; 5V ref is in `1B` | **correction** — `0x10`@2 is a battery reading, not a sensor ref | car read |
| **Driver demand** | **ported** `driver_demand` `1D`@0 u16 ×0.01 mg/stroke **cand** | BO: `1D`@0 fuel demand mg/stroke · **SR-App: `1D`@0 pedal % (i16/100)** | gap filled; **unit conflict** mg/stroke vs % | **T-03** |
| **Smoke / torque limit** | **ported** `smoke_limit` `1D`@10, `torque_limit` `1D`@12 (u16 ×0.01 mg) **cand** | SR-App: `1D` smoke@10, torque@12 | new fuelling fields | **T-03** |
| **Idle demand** | *not stored* (overlaps `egr_modulator`@15) | BO + SR-App: `1D`@14 idle demand | hypothesis — byte-15 overlap with our EGR candidate | **T-02/T-03** |
| **Sensor voltages** | **ported** `coolant_sensor_v` `1A`@2, `intake_sensor_v` `1A`@6, `fuel_sensor_v` `1A`@14 (u16 ×0.001 V) **cand** | SR-App: `1A` interleaves temp + sensor V | new; fill the `1A` gaps | car read |
| **Accel tracks** | `1B` 3 tracks + supply@6 (12-byte) **proven** | Ek: 4 tracks + supply@8 (14-byte) · BO: both forms, auto-detect · SR-App: ref V@8 (14-byte) | **variant difference** — RDL016 is the 12-byte form; ours right for this car | — |
| **Switch / relay bits** | `1E`/`36` captured, not decoded | **SR-App: `0x1E` = driver switches** (clutch `@0`b1, cruise `@0`b2-4, brake `@1`b7, A/C `@1`b3, transfer `@1`b6, ignition `@1`b1, security `@1`b5); **`0x36` = relay/output status** (rad fan, main relay, fuel pump, A/C clutch, MIL, glow) | concrete hypotheses — **not stored blind**; reframes `36` from "switches" to relays | **T-08** |

## Fault codes & security

| Item | Ours | External | Verdict |
|---|---|---|---|
| Fault block `21 3B` | `td5/faults.py` ~210 named bits (source of truth; `faultmap.json` generated) | Ek fault map (cross-validated); TOC DTC table | ours authoritative; others corroborate — no port |
| Seed→key | LFSR, taps 1/2/8/9 **proven** over all 65536 seeds (`td5/keygen.py`, ex pajacobson) | BO: bit-identical LFSR (3rd confirmation) · **SR: different** (byteswap, XOR `0x2E71`, +`0xCF`, rotate) | keep ours; **do not adopt SR's variant** (likely wrong/other ECU) |
| Outputs `30 xx` | `_OUTPUTS` A1/A2/A3/A4/B3/B7/BA/BD/BE (+PWM) **proven** | Ek captured bytes match exactly | agree — no port |
| Injector pulse | `31 C2 0n` **proven** | Ek / TOC same | agree |
| Injector classification codes | not located (Settings block) | Ek reads them; **format: 5 digits = start-offset (1-2, ±0.000127 s), end-offset (3-4), idle variance (5)** | **gap** — targeted Settings read (T-07) |
| DTC → P-code | `faults.py` `{byte,bit}` names, no P-codes | **SR-App `td5_dtc_table.h`: same `{byte,bit}=(X-1)*8+(Y-1)` + inferred OBD-II P-codes** | corroborates our indexing; P-codes a future enhancement |

## Notes
- **Big-endian:** SR's 2026-09 correction and SR-App agree with Ek, BO and our automap's BE
  preference. Treat any LE claim as stale.
- **Ported candidates** (`wastegate_pos`, `egr_pos`, `battery_direct`, `driver_demand`,
  `egr_inlet`, `smoke_limit`, `torque_limit`, `coolant_sensor_v`, `intake_sensor_v`,
  `fuel_sensor_v`) are `confidence: candidate` with their source in the store record; none
  is `proven` until a capture confirms it (CONSTITUTION.md).
- **The EGR/wastegate conflict is the headline open item:** SR-App places them ONLY at
  native `0x37`/`0x38` with nothing in `1D`, whereas our 4-drive data had `1D`@15/@17 move
  like EGR/wastegate. Both representations are stored as candidates; **T-02** decides which
  the car actually uses.
- All sources are **Td5-only**; none informs SLABS/BCU/airbag/ACE/EAT/cruise — see
  [td5-d2-ecosystem.md](td5-d2-ecosystem.md) for the vendor/RAVE docs that cover those.
