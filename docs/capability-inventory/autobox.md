---
title: "Capability inventory — Auto Gearbox — Bosch GS8.87.0"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
depends_on: [docs/capability-inventory/overview.md]
summary: >
  Auto gearbox (EAT) capability inventory: fault read/clear confirmed, GENERAL inputs, reset-adaptive utility, 0x72 framing open.
---

# Capability inventory — Auto Gearbox — Bosch GS8.87.0

Part of the [capability inventory](overview.md). Status words (ESTABLISHED, STRONG CANDIDATE, OPEN, NOT ESTABLISHED) are defined there.

PARTIAL The ECU responds deterministically using its own 0x72-framed protocol, even when the diagnostic interface reports that the function could not be performed. Function requests are well identified, but data contents and frame semantics are not yet fully decoded.

## 7.1 Fault codes

| **Function** | **Request**    | **Response**               | **Status / notes**                                                                                                  |
|--------------|----------------|----------------------------|---------------------------------------------------------------------------------------------------------------------|
| Read faults  | 72 05 04 00 73 | 72 09 60 01 00 00 00 00 1B | CONFIRMED/reproduced in a separate final session. Do not yet interpret 01 00 00 00 00 as a fault count or DTC list. |
| Clear faults | 72 04 05 73    | 72 04 60 99 FF             | CONFIRMED/reproduced. 60/99 FF appears to be a generic acknowledgement/session structure; semantics open.           |

## 7.2 Inputs

The GENERAL screen has 26 items in exact observed UI order:

| **\#** | UI label                | **Known request**                     |
|--------|-------------------------|---------------------------------------|
| 1      | Throttle position (%)   | 72 05 0B 03 7F (entire GENERAL block) |
| 2      | Engine torque (%)       | 72 05 0B 03 7F (entire GENERAL block) |
| 3      | Torque requested (%)    | 72 05 0B 03 7F (entire GENERAL block) |
| 4      | Reduced torque (%)      | 72 05 0B 03 7F (entire GENERAL block) |
| 5      | Friction torque (%)     | 72 05 0B 03 7F (entire GENERAL block) |
| 6      | Torque reference (Nm)   | 72 05 0B 03 7F (entire GENERAL block) |
| 7      | Gear switch W           | 72 05 0B 03 7F (entire GENERAL block) |
| 8      | Gear switch X           | 72 05 0B 03 7F (entire GENERAL block) |
| 9      | Gear switch Y           | 72 05 0B 03 7F (entire GENERAL block) |
| 10     | Gear switch Z           | 72 05 0B 03 7F (entire GENERAL block) |
| 11     | Program switch          | 72 05 0B 03 7F (entire GENERAL block) |
| 12     | High/Low range switch   | 72 05 0B 03 7F (entire GENERAL block) |
| 13     | Kick down               | 72 05 0B 03 7F (entire GENERAL block) |
| 14     | Shift type              | 72 05 0B 03 7F (entire GENERAL block) |
| 15     | Engine speed (RPM)      | 72 05 0B 03 7F (entire GENERAL block) |
| 16     | Turbine speed (RPM)     | 72 05 0B 03 7F (entire GENERAL block) |
| 17     | Output speed (RPM)      | 72 05 0B 03 7F (entire GENERAL block) |
| 18     | Battery (V)             | 72 05 0B 03 7F (entire GENERAL block) |
| 19     | Solenoid valve 1        | 72 05 0B 03 7F (entire GENERAL block) |
| 20     | Solenoid valve 2        | 72 05 0B 03 7F (entire GENERAL block) |
| 21     | Solenoid valve 3        | 72 05 0B 03 7F (entire GENERAL block) |
| 22     | Modulator pressure      | 72 05 0B 03 7F (entire GENERAL block) |
| 23     | Engine temperature (°C) | 72 05 0B 03 7F (entire GENERAL block) |
| 24     | Adaptive program 1      | 72 05 0B 03 7F (entire GENERAL block) |
| 25     | Adaptive program 2      | 72 05 0B 03 7F (entire GENERAL block) |
| 26     | Adaptive program 3      | 72 05 0B 03 7F (entire GENERAL block) |

The separate pressure-input request is 72 05 0B 00 7C. The exact pressure UI fields and byte offsets are not yet sufficiently verified.

## 7.3 Outputs

No separate Auto Gearbox Outputs screen is established in the available material. Leave the category unimplemented until an actual function or traffic demonstrates otherwise.

## 7.4 Utilities

| **Utility**                            | **Hex**              | **Status**                                                                                    |
|----------------------------------------|----------------------|-----------------------------------------------------------------------------------------------|
| Reset Adaptive / reset adaptive values | 72 06 83 FF 07 08 FF | ESTABLISHED request; response/semantics should continue to be logged as a separate 72 routine |

## 7.5 Settings

| **Function / UI**     | **Hex / data**                                                            | **Status**                                       |
|-----------------------|---------------------------------------------------------------------------|--------------------------------------------------|
| Read Settings         | 72 05 93 00 E4                                                            | ESTABLISHED request                              |
| Settings response     | 72 18 60 69 65 15 95 ...                                                  | Data block observed; field decoding open         |
| Identification fields | Manufacturer; Softw. level; Coding index; CAN Softw. level; Softw version | Function/field established                                   |
| Part/VIN fields       | LR Part number; Manuf. part number; Vehicle VIN; WRITE VIN                | Function/field established; VIN-write request not yet mapped |
