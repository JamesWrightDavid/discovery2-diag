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
signal store (`src/d2diag/signals/td5.json`). The research narrative is in
[td5-external-findings.md](td5-external-findings.md); this is the field-by-field table and
the authority for what we ported.

Sources: **Ours** (store, car-verified where `proven`) · **Ek** EA2EGA/Ekaitza_Itzali
(Python, real sniffs; `fuelling_to_json.py`) · **SR** SimonRafferty (MIT;
`TD5_PROTOCOL_REFERENCE.md`, big-endian corrected 2026-09) · **BO** k0sci3j/BinOwl_Td5Gauge ·
**H1** hairyone/TD5Tester (Apache-2.0) · **TOC** td5opencom lineage (BennehBoy port).
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
| **Wastegate** | `wastegate_modulator` `1D`@17 u8 ×(100/255) **cand** · **ported** `wastegate_pos` `38`@0 u16 ×0.01 % **cand** | SR: `38` raw/100 % · BO: `38` raw/1000 % | `0x38` is the native LID (SR+BO agree on the LID); **scale disputed /100 vs /1000** | **T-02** |
| **EGR** | `egr_modulator` `1D`@15 u8 ×(100/255) **cand** · **ported** `egr_pos` `37`@0 u16 ×0.01 % **cand** | SR: `37` raw/100 % | native LID `0x37` (SR only; `0x37` responds on RDL016) | **T-02** |
| **Reference voltage** | **ported** `reference_voltage` `10`@2 u16 ×0.001 V **cand** | SR: `10` = battery@0 + ref V@2 | gap filled from SR | car/NanoCom read |
| **Driver demand** | **ported** `driver_demand` `1D`@0 u16 ×0.01 mg/stroke **cand** | BO: `1D`@0 driver fuel demand | gap filled from BO | **T-03** |
| **Idle demand** | *not stored* (would overlap `egr_modulator`@15) | BO: `1D`@14 idle fuel demand | hypothesis only — byte-15 overlap | **T-03** |
| **Accel tracks** | `1B` 3 tracks + supply@6 (12-byte) **proven** | Ek: 4 tracks + supply@8 (14-byte) · BO: both forms, auto-detect | **variant difference** — RDL016 is the 12-byte form; ours right for this car | — |
| **Switch bits** | `1E` captured, not decoded | SR: DB1 `@0` bit1=clutch(0=pressed, *confirmed*), bits0/2/3/4=brake2/cruise×3; DB2 `@1` bit2/3=A/C, bit6=transfer(1=LOW), bit7=brake-main(0=pressed, *confirmed*) · Ek: ECU-pin map | concrete bit hypotheses — **not stored blind** (our one observed moving bit was `@0` bit5, not in SR's map) | **T-08** |

## Fault codes & security

| Item | Ours | External | Verdict |
|---|---|---|---|
| Fault block `21 3B` | `td5/faults.py` ~210 named bits (source of truth; `faultmap.json` generated) | Ek fault map (cross-validated); TOC DTC table | ours authoritative; others corroborate — no port |
| Seed→key | LFSR, taps 1/2/8/9 **proven** over all 65536 seeds (`td5/keygen.py`, ex pajacobson) | BO: bit-identical LFSR (3rd confirmation) · **SR: different** (byteswap, XOR `0x2E71`, +`0xCF`, rotate) | keep ours; **do not adopt SR's variant** (likely wrong/other ECU) |
| Outputs `30 xx` | `_OUTPUTS` A1/A2/A3/A4/B3/B7/BA/BD/BE (+PWM) **proven** | Ek captured bytes match exactly | agree — no port |
| Injector pulse | `31 C2 0n` **proven** | Ek / TOC same | agree |
| Injector classification codes | not located (Settings block) | Ek reads them | **gap** — needs a targeted Settings read (T-07) |

## Notes
- **Big-endian:** SR's 2026-09 correction ("all multi-byte values are big-endian, no
  exceptions") agrees with Ek, BO and our automap's BE preference. Treat any LE claim as
  stale.
- **Ported candidates** (`wastegate_pos`, `egr_pos`, `reference_voltage`, `driver_demand`)
  are `confidence: candidate` with their source in the store record; none is `proven`
  until a capture confirms it (CONSTITUTION.md).
- All five repos are **Td5-only**; none informs SLABS/BCU/airbag/ACE/EAT/cruise.
