---
title: "Land Rover Discovery 2 Diagnostic Protocol Capability Inventory"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
summary: >
  Entry point of the consolidated Discovery 2 capability inventory: status vocabulary, shared protocol patterns, the per-module capability matrix and the safety note, with links to one page per module.
---

# Land Rover Discovery 2 Diagnostic Protocol Capability Inventory

**TD5 · SLABS · BCU/DCU · ACE · Auto Gearbox · Airbag**

Consolidated inventory of module capabilities, observed K-line behavior, established hex commands, and unresolved areas. It serves two purposes: a technical handoff and working reference for continued implementation in d2diag, and a **shareable progress report for the Discovery 2 / Td5 community** — to show how far this open reverse-engineering effort has come and to exchange findings and experience. Vehicle-identifying values and security credentials are deliberately excluded (see §11).

## 1. How to read this document

This document separates established protocol behavior from strong candidates and open questions. Observed function ordering and field wording are preserved where they may matter for byte/bit mapping.

| **Status**       | **Meaning**                                                                                            |
|------------------|--------------------------------------------------------------------------------------------------------|
| ESTABLISHED      | Observed directly in raw traffic or verified against the vehicle in multiple observations.             |
| STRONG CANDIDATE | The structure is supported by multiple observations, but exact semantics/bit mapping are not proven.   |
| OPEN             | The function is known to exist or appears in traffic, but there is insufficient evidence to decode it. |
| NOT ESTABLISHED  | No separate function or traffic has been verified; it should not be implemented as fact.               |

Important methodology rule: logger comments often land in the middle of an already-running stream. An annotation must therefore be associated with the traffic regime/screen and searched backward in time, rather than automatically assigned to the nearest frame.

## 2. Common protocol patterns

### 2.1 TD5/SLABS-style KWP2000 framing

After initialization, TD5 and SLABS use unaddressed length-prefixed frames:

> \<len\> \<SID\> \<data...\> \<checksum\>

Checksum = the sum of all preceding bytes modulo 256. A positive response is normally SID + 0x40. Examples: 21 → 61, 31 → 71, 3E → 7E.

| **Service** | **Meaning**                         |
|-------------|-------------------------------------|
| 21 / 61     | ReadDataByLocalIdentifier           |
| 30 / 70     | InputOutputControlByLocalIdentifier |
| 31 / 71     | StartRoutine / actuator test        |
| 33 / 73     | RoutineResults                      |
| 3E / 7E     | TesterPresent                       |
| 1A / 5A     | ReadECUIdentification               |
| 14 / 54     | Clear diagnostic information        |
| 27 / 67     | SecurityAccess                      |

### 2.2 SLABS initialization

| **Item**                   | **Hex / behavior**                                  | **Status / notes**                                                                                                                                        |
|----------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Fast-init physical address | 0x29                                                | ESTABLISHED                                                                                                                                               |
| StartCommunication         | 81 29 F7 81 22                                      | ESTABLISHED                                                                                                                                               |
| Response                   | 03 C1 57 8F AA                                      | ESTABLISHED; C1 = positive response to 0x81, 57/8F keywords.                                                                                              |
| Keepalive                  | 01 3E 3F → 01 7E 7F                                 | ESTABLISHED, approx. 1 Hz.                                                                                                                                |
| StopCommunication          | 01 82 83 → 01 C2 C3                                 | ESTABLISHED in our own implementation.                                                                                                                    |
| Fast-init TiniH            | Empirically adjusted until connection became stable | ESTABLISHED as the root cause of the previous sporadic initialization attempts. The exact working timing value should be retained in code/protocol notes. |

Practical conclusion: SLABS proved significantly more sensitive to effective TiniH than TD5. Once TiniH was adjusted, initialization became stable; the application layer had been correct throughout.

## Modules

| Module | Page |
| ------ | ---- |
| TD5 engine ECU | [td5.md](td5.md) |
| SLABS | [slabs.md](slabs.md) |
| BCU / DCU | [bcu.md](bcu.md) |
| ACE | [ace.md](ace.md) |
| Auto gearbox | [autobox.md](autobox.md) |
| Airbag | [airbag.md](airbag.md) |
| Open questions | [open-questions.md](open-questions.md) |

## 9. Consolidated capability matrix

| **Module**   | **Fault codes**                                   | **Inputs**                              | **Outputs**                            | **Utilities**                                      | **Settings**                                                   |
|--------------|---------------------------------------------------|-----------------------------------------|----------------------------------------|----------------------------------------------------|----------------------------------------------------------------|
| TD5          | Very good                                         | Very good                               | Almost fully solved                    | Known security routines                            | Extensive UI; bulk mapping partly open                         |
| SLABS        | Read/current/logged/clear solved                  | Groups + several mappings               | Many actuators; lamp tests missing     | ABS bleed known                                    | LID group known; individual mapping open                       |
| BCU/DCU      | No conventional screen established                | Very extensive function set                       | Entire function list known; bank/bit mapping open | EKA solved; keys/plip UI known                     | Very extensive; LID/bit mapping open                           |
| ACE          | Read/clear structure established, fault bits open | 15 UI items; bulk offsets open          | 5 UI items; raw mapping open           | 3 calibration commands established + 3 bleed steps | No separate screen established                                 |
| Auto Gearbox | Read/clear confirmed                              | GENERAL complete; pressure group exists | No separate screen established         | Reset adaptive established                         | Read request + UI identification established; data decode open |
| Airbag       | Record format + clear established                 | No separate screen established          | No separate screen established         | No separate screen established                     | 16 identification/config fields established                    |


## 11. Document status and safety note


This master intentionally excludes vehicle-identifying values, security credentials, and provenance details while retaining the protocol structure required for implementation. Uncertain associations are explicitly marked as OPEN or STRONG CANDIDATE.

This document is a protocol inventory, not a guarantee of safe service procedures. Write/actuator functions can affect brakes, suspension, immobilization, and configuration. In an implementation, read-only functions should be kept separate from writes, and all writes should require explicit user action.
