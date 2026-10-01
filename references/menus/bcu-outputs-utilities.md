---
title: "Reference tool menus — BCU outputs and utilities"
area: references
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Reference tool BCU output tests (BODY 17, SECURITY/LOCKING 14), EKA read/set and key programming utilities in exact UI order, plus the 2026-08-08 verification log.
---

# Reference tool menus — BCU outputs and utilities

> Converted on 2026-10-01 from the former `reference_tool_master_menu.md` (a Word
> transcription of the reference tool's menus; see [overview.md](overview.md)). Menu order
> and UI spelling are preserved exactly. **Displayed values are screenshot examples,
> not protocol constants.** Empty request/response columns were dropped.

## BCU — Outputs

### BCU OUTPUTS — BODY

**Protocol-order note.** The sequence below is intentionally preserved exactly as presented in reference tool. Use the continuous Seq. number when analysing captures: the BODY outputs may be read or represented as one ordered block, so do not reorder items by function. Apparent duplicate or truncated labels are retained exactly from the UI.

| Seq. | reference tool group | reference tool label | Available command |
|---|---|---|---|
| 1 | LIGHTS | Front fog lights | ON / OFF |
| 2 | LIGHTS | Rear fog lights | ON / OFF |
| 3 | LIGHTS | Daytime running lights | ON / OFF |
| 4 | LIGHTS | LH indicator enable | ON / OFF |
| 5 | LIGHTS | LH indicator enable | ON / OFF |
| 6 | WINDOWS | Front left window up | ON / OFF |
| 7 | WINDOWS | Front left window down | ON / OFF |
| 8 | WINDOWS | Front right window up | ON / OFF |
| 9 | WINDOWS | Front right window dow | ON / OFF |
| 10 | WINDOWS | Rear windows enable | ON / OFF |
| 11 | WINDOWS | Sunroof enable | ON / OFF |
| 12 | WASH WIPE | Front wiper enable | ON / OFF |
| 13 | WASH WIPE | Tail wiper enable | ON / OFF |
| 14 | WASH WIPE | Head lamp power wash | ON / OFF |
| 15 | HEATED SCREEN | Heated screen | ENABLE / DISABLE |
| 16 | HEATED SCREEN | Heat. rear screen lamp | ON / OFF |
| 17 | CHECK ENGINE | Check engine lamp | ON / OFF |

**Capture strategy.** For each output, capture the bus traffic before pressing a button, while issuing ON/ENABLE, and while issuing OFF/DISABLE. If reference tool first reads a complete BODY output-state block and then sends a separate command, keep both transactions in the log. The most useful first pass is to exercise items 1–17 strictly in sequence without navigating elsewhere.

**UI anomalies to preserve.** reference tool shows “LH indicator enable” twice in succession and truncates “Front right window dow”. These have deliberately not been corrected here. The second indicator entry may ultimately prove to be RH, but that should be established from traffic/vehicle behaviour rather than assumed.

### BCU OUTPUTS — SECURITY

**Protocol-order note.** The SECURITY/LOCKING outputs below are listed in the exact top-to-bottom order shown by reference tool across the supplied screenshots. Keep this sequence intact when correlating captures. Treat this as a separate ordered output block from BODY unless the traffic proves they are returned by one common command.

| Seq. | reference tool group | reference tool label | Available command |
|---|---|---|---|
| 1 | SECURITY | Horn | ON / OFF |
| 2 | SECURITY | BBUS ALL | ON / OFF |
| 3 | SECURITY | BBUS ST | ON / OFF |
| 4 | SECURITY | Fuel flap | ON / OFF |
| 5 | SECURITY | Alarm LED | ON / OFF |
| 6 | SECURITY | Ignition interlock | ON / OFF |
| 7 | SECURITY | Crank Enable | ON / OFF |
| 8 | SECURITY | Volumetric power | ON / OFF |
| 9 | SECURITY | Robust immo. | ON / OFF |
| 10 | SECURITY | Transponder Power | ON / OFF |
| 11 | LOCKING | Lock | ON / OFF |
| 12 | LOCKING | Unlock | ON / OFF |
| 13 | LOCKING | Superlock | ON / OFF |
| 14 | LOCKING | Single point entry | ON / OFF |

**Capture strategy.** Exercise SECURITY/LOCKING items 1–14 in this exact order. For each item, record the idle traffic, the frame(s) produced by ON, and the frame(s) produced by OFF. Locking, immobiliser and alarm-related outputs may cause state changes elsewhere in the BCU, so note extra unsolicited or follow-up traffic separately rather than assuming every changed byte belongs to the output command itself.

**Ordering index.** Outputs documented so far: BODY (17 ordered items) followed by SECURITY/LOCKING (14 ordered items). Do not merge or sort the two blocks by function during protocol analysis.

### BCU UTILITIES — EKA CODE

**Scope note.** For now, only the two EKA-code operations shown in the Utilities menu are included: READ and SET. The four code fields are treated as one four-part EKA value; no assumptions are made yet about encoding, digit range, byte order, or whether READ and SET use related service identifiers.

| Seq. | reference tool utility | Operation | Data / UI |
|---|---|---|---|
| 1 | EKA CODE | READ | Read current 4-part EKA code |
| 2 | EKA CODE | SET | Write 4-part EKA code |

**Capture priority.** READ is the safe first target: capture the request and complete reply without changing vehicle configuration. SET should be sniffed only when intentionally writing a known-valid EKA code. Record all four displayed/entered values alongside the raw frame so their representation can be mapped directly.

### BCU UTILITIES — KEY PROGRAMMING

**Scope note.** Included for completeness. Menu order and button order are preserved exactly because separate read/update/detect/synchronise operations may map to distinct protocol commands. Displayed values below are the values visible in the captured reference tool screens and should be treated as capture examples, not as assumed protocol constants.

#### Key codes / UPDATE

| Seq. | reference tool field | Displayed value | Action |
|---|---|---|---|
| 1 | Key Code 1 | 2E85E2 | SET |
| 2 | Key Code 2 | 220E02 | SET |
| 3 | Key Code 3 | F3B059 | SET |
| 4 | Key Code 4 | 21DCF6 | SET |
| 5 | Susp | 111111 | SET |
| 6 | — | — | UPDATE |

_Global update button shown below the five code rows._

#### Key detection / synchronisation

| Seq. | reference tool field | Displayed status | Action |
|---|---|---|---|
| 1 | Key 1 | NOT DETECT. | SYNC |
| 2 | Key 2 | NOT DETECT. | SYNC |
| 3 | Key 3 | NOT DETECT. | SYNC |
| 4 | Key 4 | NOT DETECT. | SYNC |
| 5 | SUSP | NOT DETECT. | SYNC |
| 6 | — | — | KEY DETECT |

_Global key-detection button shown below the five rows._

#### Suspension plip BAR CODE

| Seq. | reference tool item | Captured display / action | Candidate service / payload / notes |
|---|---|---|---|
| 1 | BAR CODE | *X11111111111X* | Transcribed from screenshot; verify exact number of 1 characters against a live capture before using it as protocol data. |
| 2 | — | SET CODE 1 | Button |
| 3 | — | UPDATE |  |

**Reverse-engineering note.** Capture read/display traffic separately from each SET, UPDATE, KEY DETECT and SYNC action. For key-code programming, change only one known field at a time and keep the complete request/response sequence, including any acknowledgement or follow-up frame. This will make it possible to distinguish field identifiers from the six-hex-digit key-code payloads.

#### Verification log — 2026-08-08

**Scope.** The complete BCU material in this document was rechecked against the supplied reference tool screenshots. Menu order, labels and displayed capture values were preserved as shown, including apparent UI typos/truncations.

Corrected all 17 values/labels in Settings → ALARM-OTHER to match the screenshots.

Filled all six BCU INFO fields from the screenshots, including the split VIN display.

Replaced the previously incorrect Outputs → SECURITY list with the full 14-item SECURITY/LOCKING sequence shown in the screenshots.

Rechecked DCU Read Inputs, BCU Instruments, Power Distribution, Settings (Lights Windows-Seats, Transm-Lock-Warn, Instrument Pack), Outputs BODY, EKA Code and Key Programming against the supplied images; no additional transcription corrections were required.

No inferred “corrections” were made to reference tool UI anomalies such as duplicated “LH indicator enable”, truncated labels, or unusual spelling. These are retained because order and exact UI wording may help protocol mapping.
