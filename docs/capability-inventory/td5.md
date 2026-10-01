---
title: "Capability inventory — TD5 Engine ECU (Lucas)"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
depends_on: [docs/capability-inventory/overview.md]
summary: >
  Td5 capability inventory: fault codes, inputs, outputs, utilities and settings with established hex commands and open mapping.
---

# Capability inventory — TD5 Engine ECU (Lucas)

Part of the [capability inventory](overview.md). Status words (ESTABLISHED, STRONG CANDIDATE, OPEN, NOT ESTABLISHED) are defined there.

**ESTABLISHED** The base protocol, live data, most outputs, and security status are largely solved. Settings and switch bitfields are still only partially mapped.

## 3.1 Fault codes

| **Function**      | **Hex**                  | **Status**                    | **Explanation**                                                                                                                                             |
|-------------------|--------------------------|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Read fault block  | 21 3B                    | ESTABLISHED                   | 35-byte bit block. The working decoder uses bit index offset×8+bit; approximately 210 relevant bit positions have been mapped against the fault dictionary. |
| Clear faults      | 14/54 family             | ESTABLISHED at service level  | The exact TD5 clear sequence exists in code/logs; keep it separate from SLABS 14 FF FF.                                                                     |
| Current vs logged | Separate status memories | ESTABLISHED at function level | Active/current and logged states are distinct. Exact raw status encoding per fault is not fully documented here.                                            |

## 3.2 Inputs

Switch Inputs. The interface exposes the following 12 items in order. Traffic on this screen is dominated by LIDs 1E and 36. Byte 1 of LID 1E has been observed switching CA\<-\>EA (bit 0x20), but the exact switch\<-\>bit mapping is not yet complete.

| **\#** | UI label          | Known raw structure | **Status / notes**          |
|--------|-------------------|---------------------|-----------------------------|
| 1      | Brake Switch 1    | 21 1E / 21 36       | OPEN individual bit mapping |
| 2      | Brake Switch 2    | 21 1E / 21 36       | OPEN individual bit mapping |
| 3      | Clutch Switch     | 21 1E / 21 36       | OPEN individual bit mapping |
| 4      | Transfer Ratio    | 21 1E / 21 36       | OPEN individual bit mapping |
| 5      | Gear Box          | 21 1E / 21 36       | OPEN individual bit mapping |
| 6      | Cruise Control    | 21 1E / 21 36       | OPEN individual bit mapping |
| 7      | Cruise Resume     | 21 1E / 21 36       | OPEN individual bit mapping |
| 8      | Set Accelerate    | 21 1E / 21 36       | OPEN individual bit mapping |
| 9      | AC Clutch Request | 21 1E / 21 36       | OPEN individual bit mapping |
| 10     | AC Clutch Drive   | 21 1E / 21 36       | OPEN individual bit mapping |
| 11     | AC Fan Request    | 21 1E / 21 36       | OPEN individual bit mapping |
| 12     | AC Fan Drive      | 21 1E / 21 36       | OPEN individual bit mapping |

Fuelling / live engine data. Several LIDs and scalings are established here:

| Observed value                    | **LID**            | **Encoding**                                          | **Status**            |
|-----------------------------------|--------------------|-------------------------------------------------------|-----------------------|
| Engine Speed                      | 21 09              | u16 BE, rpm                                           | ESTABLISHED           |
| Idle Speed Error                  | 21 21              | s16 BE, rpm                                           | ESTABLISHED           |
| Road Speed                        | 21 0D              | 1 byte, km/h candidate; 0 when stationary             | HIGH                  |
| Battery                           | 21 10              | u16/1000 V                                            | ESTABLISHED           |
| Accel. Way 1–3 + Supply           | 21 1B              | 4 × u16 BE /1000 V                                    | ESTABLISHED           |
| Coolant/Fuel/Air inlet + ext temp | 21 1A              | temperature block, u16/10 − 273.2 for verified fields | ESTABLISHED/PARTIAL   |
| MAP / manifold                    | 21 1C              | MAP at offset 0 (u16 BE ×0.0001 bar) established; 1C@4 is NOT air mass (reads 0 while running) | ESTABLISHED (MAP)     |
| MAF (air mass)                    | 21 1D              | u16 BE @4; proven as the field (r=+0.95 vs rpm×MAP over a full WOT pull); kg/h scale is a CANDIDATE pending a reference | ESTABLISHED (field)   |
| Injection quantity                | 21 1D              | u16 BE @6, ×0.01 mg/stroke                            | ESTABLISHED           |
| Ambient + manifold pressure       | 21 23              | 2 × u16; displayed in kPa                             | ESTABLISHED structure |
| Cylinder 1–5 balances             | 21 40              | 5 × s16 BE                                            | ESTABLISHED           |
| EGR modulator                     | 21 1D              | u8 @15, ×100/255 % duty                               | STRONG CANDIDATE      |
| Wastegate modulator               | 21 1D              | u8 @17, ×100/255 % duty                               | STRONG CANDIDATE      |
| EGR/wastegate NOT at 21 37/38     | 21 37 / 21 38      | do not respond on this vehicle — dismissed            | NOT ESTABLISHED       |

## 3.3 Outputs

| Output                   | **Hex command**       | **Status / notes**              |
|--------------------------|-----------------------|---------------------------------|
| A/C CLUTCH               | 30 A3 FF              | ESTABLISHED                     |
| A/C FAN                  | 30 A4 FF              | ESTABLISHED                     |
| MIL LAMP                 | 30 A2 FF              | ESTABLISHED                     |
| FUEL PUMP                | 30 A1 FF              | ESTABLISHED                     |
| GLOW PLUGS               | 30 B3 FF              | ESTABLISHED                     |
| PULSE REV COUNTER        | 30 B7 FF              | ESTABLISHED                     |
| WASTEGATE MODUL.         | 30 BE FF + PWM        | ESTABLISHED; parameter/PWM used |
| TEMP GAUGE               | 30 BA FF              | ESTABLISHED                     |
| EGR THROTTLE / modulator | 30 BD FF + PWM        | ESTABLISHED                     |
| INJECTOR 1–5             | 31 C2 01 ... 31 C2 05 | ESTABLISHED                     |

## 3.4 Utilities

| **Function**        | **Hex**                  | **Status / notes**                                                                             |
|---------------------|--------------------------|------------------------------------------------------------------------------------------------|
| LEARN SECURITY CODE | 31 C0-related routine    | Function exists; the full write sequence should be kept separate from status reading.          |
| GET SECURITY STATUS | 31 C0 ; 33 C0 → 73 C0 03 | ESTABLISHED. Status 03 matched “ECU not immobilized” and is a strong candidate for this state. |

## 3.5 Settings

Settings contain several data types and should not be treated as one homogeneous block. In the observations, settings are retrieved through several one-shot LIDs, including 21 3D, 21 20, 21 0E, 21 32, and 21 24. Exact LID→field mapping is not yet complete.

| **Group**      | Fields                                                                                                                                                                                                                                                                                                    | **Known protocol**                      | **Status**                                                                          |
|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|-------------------------------------------------------------------------------------|
| Injector codes | Injector 1–5 (5 characters each), INJ. TYPE                                                                                                                                                                                                                                                               | Bulk/read-write not fully isolated      | UI + baseline established; write format open                                  |
| Read-only ID   | Config Tune ID; Fuel Tune ID; ECU Part Number; Homologation; GET VIN                                                                                                                                                                                                                                      | Part of settings/ID reads               | Function/field established; exact requests per field partially open                             |
| Feature config | Temperature Gauge; Tachometer; SLABS; Road Speed; Radiator Fan; MIL Lamp; Fuel Used; Fuel Temperature; EGR Modulator; EGR Inlet; Cruise Lamp; Cruise Control; Clutch Switch; CAN Bus; Auxiliary Fan; Auto Gearbox; Air Conditioning; Active Engine mount; Ambient Sensor; Wastegate Modulator; ECU Status | 21 3D / 20 / 0E / 32 / 24 occur in bulk | UI order established; individual byte/bit mapping requires differential observation |

Baseline structure (vehicle-identifying values redacted): Config Tune ID, Fuel Tune ID, ECU Part Number, and Homologation are read as read-only ID fields here. Feature-config values are booleans (ENABLED/DISABLED) plus an ECU Status enum — e.g. Temperature Gauge, Tachometer, SLABS, Road Speed, Radiator Fan, MIL, Fuel Used, Fuel Temperature, EGR Modulator, EGR Inlet, Cruise Control, ECU Status. The specific per-field values are not published here.
