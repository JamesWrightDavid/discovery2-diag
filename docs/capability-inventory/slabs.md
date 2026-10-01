---
title: "Capability inventory — SLABS (Wabco ABS/SLS)"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
depends_on: [docs/capability-inventory/overview.md]
summary: >
  SLABS capability inventory: faults, inputs, outputs (actuators), ABS bleed utilities and settings, with established commands and open items.
---

# Capability inventory — SLABS (Wabco ABS/SLS)

Part of the [capability inventory](overview.md). Status words (ESTABLISHED, STRONG CANDIDATE, OPEN, NOT ESTABLISHED) are defined there.

ESTABLISHED Initialization and the base session are solved. Fault read/clear, several live LIDs, and many actuator/bleed commands have been directly observed. Individual settings mapping and some lamp/analog fields remain open.

## 4.1 Fault codes

| **Function**   | **Hex**                                       | **Status / explanation**                                                                          |
|----------------|-----------------------------------------------|---------------------------------------------------------------------------------------------------|
| Logged faults  | 21 11 → 16-byte bit block                     | ESTABLISHED. Before clear, two bits were set; after clear the block became zero.                  |
| Current faults | 21 47 → 16-byte bit block                     | ESTABLISHED. At baseline the block was 00 = no current faults.                                    |
| Clear faults   | 14 FF FF → 54                                 | ESTABLISHED and tested on the vehicle.                                                            |
| Known baseline | example: one wheel-sensor fault + one valve fault (specific codes redacted) | Correlated with the displayed fault state; the full 47-fault bit map requires more anchor points. |

## 4.2 Inputs

| Screen           | **LIDs**                          | **What we know**                                                                                                                      | **Status** |
|------------------|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|------------|
| SLS Inputs       | 21 53, 21 54, 21 55               | 21 54 byte0=left height, byte1=right height. 53/55 contain supply/value/exhaust/compressor-related data, but scaling is not complete. | PARTIAL    |
| ABS Inputs       | 21 43, 21 44, 21 49, 21 50, 21 57 | 21 43 = 4 wheel speeds; 21 50 = 4 wheel sensor-voltage channels; 44/49/57 contain valve/pump/supply/HDC/engine-related fields.        | PARTIAL    |
| ABS-SLS Switches | 21 42, 21 48, 21 56, 21 58        | Any Door Open = 21 56 byte0 bit0 is confirmed. Other signals: neutral, low range, diff lock, reverse, HDC, shuttle, plip.             | PARTIAL    |

## 4.3 Outputs

| **Function**             | **Hex**                           | **Status / notes**                                                                                                                         |
|--------------------------|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| ABS pump relay           | 31 25 \<p\>                       | ESTABLISHED. 31 25 08 FA observed as ON; 31 25 02 FA as the other/reset state.                                                             |
| SLS exhaust valve        | 31 2F 28                          | ESTABLISHED                                                                                                                                |
| SLS compressor           | 31 30 28                          | ESTABLISHED                                                                                                                                |
| SLS buzzer               | 31 31 0A                          | ESTABLISHED                                                                                                                                |
| Raise left               | 31 33 28                          | ESTABLISHED                                                                                                                                |
| Raise right              | 31 34 28                          | ESTABLISHED                                                                                                                                |
| Lower left               | 31 35 28                          | ESTABLISHED                                                                                                                                |
| Lower right              | 31 36 28                          | ESTABLISHED                                                                                                                                |
| Wheel inlet/outlet tests | 31 22 \<sub\> \<params...\>       | ESTABLISHED structure; sub 10=FR, 11=FL, 12=RR, 13=RL.                                                                                     |
| Instrument lamp tests    | TC/ABS/HDC/brake/SLS/offroad etc. | NOT DECODED. In the final test session, only TesterPresent was transmitted while the UI showed inactive; no new 31 routines were observed. |

## 4.4 Utilities

| **Utility**                       | **Hex / structure**   | **Status**                                                                     |
|-----------------------------------|-----------------------|--------------------------------------------------------------------------------|
| ABS Power Bleed                   | 31 22 04 00 49 C4 ... | ESTABLISHED                                                                    |
| ABS/Module Bleed – wheel circuits | 31 22 10/11/12/13 ... | ESTABLISHED wheel selection; parameters include a 2-bit mask per wheel.        |
| Additional module bleed step      | 31 22 14 ...          | ESTABLISHED as a separate sub-ID; exact step semantics not fully documented |

## 4.5 Settings

| **LID** | **Observed baseline** | **Status / interpretation**                                                                |
|---------|-----------------------|--------------------------------------------------------------------------------------------|
| 21 45   | 7F                    | ESTABLISHED raw value; individual setting unknown                                          |
| 21 46   | 78 76                 | ESTABLISHED raw value; individual setting unknown                                          |
| 21 49   | 00 00 01              | ESTABLISHED raw value; also used on the ABS input screen, so context must be kept separate |
| 21 59   | 00 0F 0F 0F           | ESTABLISHED raw value; individual setting unknown                                          |

Important limitation: two order-based attempts to associate these LIDs with individual settings produced contradictory results. No individual SLABS setting should therefore be marked as solved without a controlled A/B/A differential test.
