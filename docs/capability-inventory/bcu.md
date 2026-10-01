---
title: "Capability inventory — BCU / DCU (Valeo body system)"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
depends_on: [docs/capability-inventory/overview.md]
summary: >
  BCU/DCU capability inventory: inputs, output banks, EKA and key utilities, SecurityAccess and settings, with what is established versus open.
---

# Capability inventory — BCU / DCU (Valeo body system)

Part of the [capability inventory](overview.md). Status words (ESTABLISHED, STRONG CANDIDATE, OPEN, NOT ESTABLISHED) are defined there.

STRONG CANDIDATE The BCU function set is well documented. EKA read/write is solved. BCU output traffic shows four WriteLocalIdentifier banks and SecurityAccess, but individual output and settings bit mapping is not yet solved.

## 5.1 Fault codes

No conventional BCU Faults screen or DTC capability is established in the available material. The BCU should therefore not be given a speculative fault list until an actual function or raw traffic demonstrates it.

## 5.2 Inputs

| Group              | **Items**                                                                                                                                                                                                                                                                                                                                               | **Protocol status**                                                                                             |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| LIGHTS             | Side lights; Main beam; Dipped; Front fog light; Rear fog light; Left indicator; Right indicator; Hazard; Daytime run light                                                                                                                                                                                                                             | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |
| DOORS / BODY       | Passenger door switch; Driver door switch; Bonnet; Key lock; Key unlock; CDL Lock; CDL unlock; Inertia; Ignition key inserted; Transfer box neutral; Park/neutral                                                                                                                                                                                       | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |
| TRANSMISSION       | Reverse idle; Transfer neutral switch; Autobox W switch; Autobox X switch; Autobox Y switch; Autobox Z switch; Park neutral switch                                                                                                                                                                                                                      | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |
| WINDOWS            | Front LEFT down; Front LEFT up; Front RIGHT down; Front RIGHT up                                                                                                                                                                                                                                                                                        | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |
| WASH WIPE          | Front intermit; Front wash; Front wiper parked; Front wiper speed; Rear wiper; Rear wash                                                                                                                                                                                                                                                                | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |
| HEATED / ENGINE    | Heated screen switch; Ignition 2; Engine speed signal                                                                                                                                                                                                                                                                                                   | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |
| INSTRUMENTS        | LH DI; RH DI; LH Tailor DI; RH Tailor DI; Seat belt; Diff lock; Transfer neutral; Autobox manual; Autobox sport; Offroad level; ABS; Traction control; SRS; HDC select; Glow plug; Brake; Oil pressure; Alternator; Check engine; Fuel filter; Transmission temp.; Check ACE; Check HDC; Check SLS; Instr. milage (km); BCU milage (km); IP trip switch | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |
| POWER DISTRIBUTION | BCU ignition pos. 1; BCU ignition pos. 2; BCU ignition pos. 3; IP ignition pos. 2; IDM ignition pos. 2; IDM battery (V); BCU switch power; BCU relay power                                                                                                                                                                                              | Raw LID/bit mapping has not yet been systematically associated with every item. Preserve grouping and order. |

## 5.3 Outputs

The BCU exposes two ordered output blocks: BODY (17 items) and SECURITY/LOCKING (14 items). Observed traffic provides structural evidence for four 32-bit WriteLocalIdentifier banks:

3B 22 xx xx xx xx  
3B 23 xx xx xx xx  
3B C1 xx xx xx xx  
3B C2 xx xx xx xx

All observed payloads were 00 00 00 00. Therefore, no individual output may yet be assigned to a particular bit. The strongest hypothesis is that these are diagnostic output/control banks and that zero writes represent reset/inactive/housekeeping operations.

| **Block**          | Items                                                                                                                                                                                                                                                                                                                                 | **Status**                                     |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| BODY               | Front fog lights; Rear fog lights; Daytime running lights; LH indicator enable; LH indicator enable (UI duplicate); Front left window up/down; Front right window up/down; Rear windows enable; Sunroof enable; Front wiper enable; Tail wiper enable; Head lamp power wash; Heated screen; Heat. rear screen lamp; Check engine lamp | UI complete. Individual bank/bit mapping OPEN. |
| SECURITY / LOCKING | Horn; BBUS ALL; BBUS ST; Fuel flap; Alarm LED; Ignition interlock; Crank Enable; Volumetric power; Robust immo.; Transponder Power; Lock; Unlock; Superlock; Single point entry                                                                                                                                                       | UI complete. Individual bank/bit mapping OPEN. |

## 5.4 Utilities

| **Utility**                  | **Known traffic**                       | **Status / explanation**                                                                                                         |
|------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| EKA CODE READ                | 21 CC                                   | ESTABLISHED                                                                                                                      |
| EKA CODE SET                 | 3B CC d1 d2 d3 d4                       | ESTABLISHED. Write format is 3B CC \<d1\> \<d2\> \<d3\> \<d4\>. No vehicle-specific EKA value or credential example is included. |
| Key Code 1–4 + Susp / UPDATE | Function set documented                           | Protocol not mapped; six-hex-digit credential fields exist.                                                                    |
| KEY DETECT / SYNC            | Key 1–4 + SUSP, SYNC; global KEY DETECT | Function set documented; protocol open.                                                                                                    |
| Suspension plip BAR CODE     | BAR CODE; SET CODE 1; UPDATE            | Function set documented; protocol open.                                                                                                    |

## 5.5 SecurityAccess / auth

BCU write/output sessions use classic KWP SecurityAccess (SID 0x27). We have at least one clean seed/key observation and additional key observations:

| **Step**             | **Hex**       | **Status / notes**                                                                          |
|----------------------|---------------|---------------------------------------------------------------------------------------------|
| Request seed         | 27 01           | ESTABLISHED                                                       |
| Seed response        | 67 01 \<seed\>  | ESTABLISHED structure; concrete seed bytes redacted              |
| Key attempt          | 27 02 \<key\>   | ESTABLISHED structure; a mismatched key returns 7F 27 83         |

What is missing is the vendor-specific seed→key algorithm itself. **Concrete seed/key values are deliberately excluded from this public document** — they are immobiliser SecurityAccess material and are dual-use. Brute force should be avoided because SecurityAccess may use an attempt counter or lockout. A safer approach is to collect/recover several complete seed/key pairs (kept private) and then derive the algorithm.

## 5.6 Settings

| Group                | **Items**                                                                                                                                                                                                                                                  | **Known protocol status**                                                |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| LIGHTS WINDOWS-SEATS | Front fog lamp; Daytime run lights; Courtest head lamps; Headlamp power wash; Electric window front; Rear windows sunroof; Heated front screen; Electric front seats; Programmed wash wip; Seat belt warning; Seat belt warning soun; Autographics         | Settings LIDs occur, but individual LID/bit mapping is not resolved.     |
| TRANSM-LOCK-WARN     | Transmission; Shift Interlock; HDC; Superlock; Single point entry; Speed lock option; Mislock option; Bathrobe lock option; Odometer error warn; Key warning; Low battery warning; Bulb failure                                                            | UI exactly documented.                                                   |
| INSTRUMENT PACK      | Transmission; Engine; ACE; SLS; Gulf; Police; HDC; TRC                                                                                                                                                                                                     | Likely packed config block; individual mapping open.                     |
| ALARM-OTHER          | Alarm; Alarm option; Alarm disarm; Alarm sounder; Alarm tamper; Engine immobil.; Passive immobil.; Inertia switch; Hazard option; Volumetric sensor; Market; EKA option; Cruise control; Air conditioning; Fuel burning heater; Passive coil; Transit mode | Mixture of Boolean + enum fields; good differential target.              |
| INFO                 | Serial No; Date; Hardware No; Software No; Alarm Type; VIN                                                                                                                                                                                                 | Read-only identification rather than live input. Fields and example values verified. |

Observed BCU settings IDs include C7, CA, CB, D3, EB, C6, CE, D4, D5, D6, and D7. They should be treated as identified LID candidates, not as fully named fields.
