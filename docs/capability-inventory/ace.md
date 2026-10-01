---
title: "Capability inventory — ACE (Lucas)"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
depends_on: [docs/capability-inventory/overview.md]
summary: >
  ACE capability inventory: fault read/clear structure, 15 inputs, 5 outputs, calibration and bleed utilities; raw mapping mostly open.
---

# Capability inventory — ACE (Lucas)

Part of the [capability inventory](overview.md). Status words (ESTABLISHED, STRONG CANDIDATE, OPEN, NOT ESTABLISHED) are defined there.

PARTIAL The functions for inputs, outputs, and utilities are documented. The raw protocol uses a different bulk format from TD5/SLABS, and ACE is disabled on the test vehicle, making the fault baseline difficult to interpret.

## 6.1 Fault codes

| **Function**       | **Raw traffic**                                             | **Status / explanation**                                                                   |
|--------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Read faults        | 67 \| 67 11 \<18-byte fault block\> | ESTABLISHED fault-block structure from one session (a 67-framed block after the 67 11 header). Specific decoded fault codes redacted. |
| Clear faults       | 8C \| 8C 00                                                 | ESTABLISHED                                                                                |
| Keepalive / status | 04 \| 04 00 ; 07 \| 07 00                                   | ESTABLISHED as recurring exchanges                                                         |

Important revised interpretation: duplicated bytes such as 67 67, 04 04, 07 07, 8C 8C, 15 15, and 65 65 are best explained as a request byte followed by a response whose first byte echoes the command, because direction is not encoded in the available one-wire traffic logs. E0 E0 and F0 F0, however, occur inside the payload and are genuine duplicated payload bytes. ACE is disabled on the test vehicle, so observed valve/pressure faults may be secondary effects and do not reliably identify the original fault.

## 6.2 Inputs

| **\#** | UI label                     | **Raw structure / status**                                                         |
|--------|------------------------------|------------------------------------------------------------------------------------|
| 1      | Engine Speed (rpm)           | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 2      | Road Speed (Km/h)            | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 3      | Battery Voltage (V)          | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 4      | DCV1 Current (AMP)           | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 5      | DCV2 Current (AMP)           | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 6      | PCV Current (AMP)            | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 7      | Pressure Sensor (bar)        | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 8      | Residual Pressure (bar)      | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 9      | System Pressure (bar)        | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 10     | Upper Lateral Acccelerometer | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 11     | Lower Lateral Acccelerometer | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 12     | Ignition Switch              | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 13     | Reverse Switch               | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 14     | Main Relay                   | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |
| 15     | Warning Lamp                 | A common 65 bulk block streams at ~1 Hz; individual offset/scaling not yet mapped. |

The core input exchange is 41 bytes. The log also contained 44-byte gap frames in which a separate 07 \| 07 00 keepalive had been appended directly after the 41-byte block. This proves that the gap logger sometimes merges logical exchanges and that keepalive traffic must be stripped before offset mapping.

## 6.3 Outputs

| Output                | **Status**                                                                    |
|-----------------------|-------------------------------------------------------------------------------|
| Main relay(Force ON)  | Function/field established; exact raw command not reliably mapped in the current material |
| Main relay(Force OFF) | Function/field established; exact raw command not reliably mapped in the current material |
| Warning Lamp          | Function/field established; exact raw command not reliably mapped in the current material |
| Dir. Control Valve 1  | Function/field established; exact raw command not reliably mapped in the current material |
| Dir. Control Valve 2  | Function/field established; exact raw command not reliably mapped in the current material |

## 6.4 Utilities

| **Utility**            | **Hex**      | **Status**                               |
|------------------------|--------------|------------------------------------------|
| Calib. Accelerometer 1 | 15 \| 15 FF  | ESTABLISHED                              |
| Calib. Accelerometer 2 | 16 \| 16 FF  | ESTABLISHED                              |
| Set Calibrated         | 10 \| 10 00  | ESTABLISHED                              |
| OIL BLEEDING STEP 1    | START / STOP | Function/field established; raw command not isolated |
| OIL BLEEDING STEP 2    | START / STOP | Function/field established; raw command not isolated |
| OIL BLEEDING STEP 3    | START / STOP | Function/field established; raw command not isolated |

## 6.5 Settings

No separate ACE Settings screen is established in the available material. The calibration functions are under Utility and should not be moved to Settings merely because they change persistent state.
