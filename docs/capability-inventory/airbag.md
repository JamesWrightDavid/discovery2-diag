---
title: "Capability inventory — Airbag — TRW SPS Type 2A"
area: docs
status: draft
version: 1.0
updated: 2026-10-01
depends_on: [docs/capability-inventory/overview.md]
summary: >
  Airbag capability inventory: fault record format and clear, 16 identification/configuration fields; read-only in this project.
---

# Capability inventory — Airbag — TRW SPS Type 2A

Part of the [capability inventory](overview.md). Status words (ESTABLISHED, STRONG CANDIDATE, OPEN, NOT ESTABLISHED) are defined there.

PARTIAL The fault record format is decoded. Settings/identification are documented, but no separate live Inputs, Outputs, or Utilities screen is established.

## 8.1 Fault codes

| **Function**     | **Hex**                                            | **Status / explanation**                                        |
|------------------|----------------------------------------------------|-----------------------------------------------------------------|
| Read fault class | 21 02 → 61 02 + \[status\]\[fault-number\] records | ESTABLISHED. Fault number matches the displayed value directly. |
| Observed record  | 90 04                                              | Fault 004: Airbag warning lamp open circuit intermittent (candidate pairing — see references/airbag_fault_codes.md). |
| Observed record  | 90 16                                              | Fault 022: Left pretensioner open circuit intermittent (candidate — see references/airbag_fault_codes.md). |
| Other read class | 21 01                                              | Observed empty in the observation; exact class meaning open.    |
| Clear faults     | 14 → 54                                            | ESTABLISHED; addressed KWP frame in the raw log.                |

Status byte 0x90 is a strong candidate for “open circuit intermittent”, but the general meaning of the status bits requires more faults/observations.

## 8.2 Inputs

No separate live Inputs screen is established. Do not implement speculative inputs.

## 8.3 Outputs

No separate Outputs screen is established.

## 8.4 Utilities

No separate Utilities are established.

## 8.5 Settings

| **\#** | Fields                  | **Status / notes**                                                                    |
|--------|-------------------------|---------------------------------------------------------------------------------------|
| 1      | Manufacturer            | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 2      | Model                   | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 3      | Software version        | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 4      | Hardware version        | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 5      | Serial number           | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 6      | Date of build           | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 7      | Part reference          | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 8      | Part number             | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 9      | VIN                     | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 10     | Driver's airbag         | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 11     | Passenger's airbag      | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 12     | Right hand Pretensioner | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 13     | Left hand Pretensioner  | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 14     | Driver's side airbag    | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 15     | Passenger's side airbag | Function/field established; identification/configuration. Only VIN is documented as programmable. |
| 16     | Rolamites               | Function/field established; identification/configuration. Only VIN is documented as programmable. |
