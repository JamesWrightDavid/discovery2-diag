---
title: "Discovery 2 SLABS (Wabco) — fault code list"
area: references
status: stable
version: 1.3
updated: 2026-10-04
summary: >
  Numbered SLABS fault types (self-levelling and ABS) from rswsolutions; its numbering is NOT the reference tool's (both car anchors disagree), so the store keys these rsw-NNN as candidate.
---

# Discovery 2 SLABS (Wabco) — fault code list

Numbered fault types for the SLABS ECU (self-levelling + ABS). Source:
[rswsolutions.com — Discovery II ABS Codes](https://rswsolutions.com/category/discovery-ii-abs-codes/)
(paginated, retrieved 2026-08-07). The reference tool guide states "up to 47 different faults";
rsw lists more numbered entries (012–114) — probably including link-/engine-related ones.

> ⚠️ **These are the DISPLAY numbers (the tool's), not necessarily raw K-line indices.**
> Just as for Td5, we must cross-validate **raw fault byte/bit ↔ number ↔ text**
> by **sniffing the reference tool** while it reads SLABS fault codes (capture both the raw bytes
> and the displayed code at the same time). Only then can the `d2diag` SLABS decoder be built.

## ⚠️ rsw numbers are not the reference tool's numbers (2026-10-04)

Both car-proven anchors contradict this list:

| Reference tool on RDL 016 (raw bit proven) | rsw number for the same fault | rsw text at the tool's number |
|---|---|---|
| `020` right front wheel-speed sensor, output too low (byte 3 bit 4) | `044` | `020` = No Batt Supply Voltage |
| `027` shuttle valve switch, electrical failure (byte 10 bit 4) | `114` | `027` = not in the list |

So the store (`src/d2diag/dtc/slabs.json`) keys these entries `rsw-NNN`, as **candidate**.
They keep the fault-type knowledge but can never be looked up by a tool number. Before that
change, a live `020` was shown with the meaning "No Batt Supply Voltage", which was wrong.

**Since 2026-10-04 the two anchors are keyed by raw bit** (`3.4`, `10.4`), as **proven**. The
decoder names a known bit by its text alone, with no number in front. The reference tool's
`020`/`027` turned out to be occurrence counts (below), so they are not fault numbers.

The four "Sensor — Bad Output" entries have no number in the rsw page text. "082" appears
only in an image filename. They are not stored.

## NanoCom's SLABS display format is unresolved (2026-10-04)

Owners' NanoCom screens on other Discovery 2s show a two-field `NN-MM` display with a count:

| Shown | Text |
|---|---|
| `16-08` | rear right sensor output too low, intermittent 16 times |
| `24-08` | rear right wheel sensor output too low |
| `16-07` | front left sensor output too low, intermittent 016 times |
| `03-06` | rear right outlet valve open circuit |

Sources: landyzone threads 360005, 379966, 351211 and 321133.

**Update (third research pass): the first field is an occurrence count.** Two more
first-hand screens settle it:
- "11-05 shuttle valve electrical fail 011 times", the same after every clear
  (https://www.landyzone.co.uk/land-rover/shuttle-valve-switch-11-05-from-nanocom.373296/);
- one front-left "output too low" fault that read `20-07` and later `16-07`
  (https://www.landyzone.co.uk/land-rover/nsf-abs-sensor-output-too-low.262396/).

The second field is not a unique fault ID either:
- `-05` is both "front right output too low" (this car's `020-05`) and "shuttle valve
  electrical fail" (`11-05`, `23-05`, this car's `027-05`);
- `-06`, `-07` and `-08` follow the rear-left, front-left and rear-right sensors.

So on NanoCom's SLABS screen the **text** identifies the fault. This car's `020`/`027` were
probably the counts that day.

**The vendor guide confirms it.** The NanoCom SLABS guide says: "Faults are listed as
Current or Intermittent, together with the number of times the system has detected the
fault. The system can detect up too 47 different faults."
(https://www.blackbox-solutions.com/site/support/download?id=18). The tool shows a count,
and the number in front of the text is it.

How sure this was before the guide: fairly, not fully.
- Three independent forum screens fit it (two checked first-hand).
- But this repo's baseline notes record "×254" next to both faults. If the first field were
  the count, those would have read 20 and 27, not 254.
- So the decoder no longer uses the number at all. That holds either way, and T-30 settles
  the question.

Earlier reading of the same evidence: in the first three, the first field matches the occurrence count. That would make it a
count, not a code, and would make this car's `020-05` "20 times, code 05". But the second
field doesn't behave like a fault code either: `03-06` is a valve fault, yet a sensor fault
also ends in `06`.

So what the displayed numbers *mean* is open. What is proven is the raw bit → fault text
pairing for this car's two faults (byte 3 bit 4, byte 10 bit 4). The store keys them by the
displayed `020` / `027` only because that is what the decoder emits. Next session, photograph
the SLABS fault screen with its "times" line (T-30). Members also report NanoCom mixing up
SLABS sensor positions.

## Systematic structure (important clue)
The codes are regular → the raw indices likely map systematically. Per **8 valves**
(4 wheels × in/out) and per **fault type** there is a code:
open circuit → short to gnd → short to supply → **drive** short to supply.
Same for the **4 wheel-speed sensors** (electric fail / output low / bad output),
**pump relay**, **brake-light relay** and **pump** (monitor/sticking/running).

## Full lista

| Code | Description |
|---|---|
| 012 | Pump Fail — Monitor Line |
| 013 | Pump Fail — Pump Not Running When On |
| 014 | Pump Fail — Pump Sticking |
| 015 | Pump Fail — Pump Running When Not On |
| 016 | Shuttle Valve Switch Long Term Failure |
| 017 | ECU Internal Valve Relay Bad |
| 020 | No Batt Supply Voltage |
| 021 | Engine PWM Signal Bad |
| 022 | ECU Gnd or Reference Gnd Bad |
| 023 | Gear Info Not Valid |
| 030 | Front Right In Valve — Open Circuit |
| 031 | Front Right Out Valve — Open Circuit |
| 032 | Front Left In Valve — Open Circuit |
| 033 | Front Left Out Valve — Open Circuit |
| 034 | Rear Right In Valve — Open Circuit |
| 035 | Rear Right Out Valve — Open Circuit |
| 036 | Rear Left In Valve — Open Circuit |
| 037 | Rear Left Out Valve — Open Circuit |
| 040 | Pump Relay — Open Circuit |
| 041 | Brake Light Relay — Open Circuit |
| 044 | Front Right Sensor — Output Low |
| 045 | Rear Left Sensor — Output Low |
| 046 | Front Left Sensor — Output Low |
| 047 | Rear Right Sensor — Output Low |
| 050 | Front Right In Valve — Short To Gnd |
| 051 | Front Right Out Valve — Short To Gnd |
| 052 | Front Left In Valve — Short To Gnd |
| 053 | Front Left Out Valve — Short To Gnd |
| 054 | Rear Right In Valve — Short To Gnd |
| 055 | Rear Right Out Valve — Short To Gnd |
| 056 | Rear Left In Valve — Short To Gnd |
| 057 | Rear Left Out Valve — Short To Gnd |
| 060 | Pump Relay — Short To Gnd |
| 061 | Brake Light Relay — Short To Gnd |
| 064 | Front Right Sensor — Electric Fail |
| 065 | Rear Left Sensor — Electric Fail |
| 066 | Front Left Sensor — Electric Fail |
| 067 | Rear Right Sensor — Electric Fail |
| 070 | Front Right In Valve — Short to Supply |
| 071 | Front Right Out Valve — Short to Supply |
| 072 | Front Left In Valve — Short to Supply |
| 073 | Front Left Out Valve — Short to Supply |
| 074 | Rear Right In Valve — Short to Supply |
| 075 | Rear Right Out Valve — Short to Supply |
| 076 | Rear Left In Valve — Short to Supply |
| 077 | Rear Left Out Valve — Short to Supply |
| 080 | Pump Relay — Short To Supply |
| 081 | Brake Light Relay — Short to Supply |
| ~082–089 | Sensor — Bad Output (Front Right / Rear Left / Front Left / Rear Right) *(exact numbers not captured — verify)* |
| 090 | Front Right In Valve — Drive Short to Supply |
| 091 | Front Right Out Valve — Drive Short to Supply |
| 092 | Front Left In Valve — Drive Short to Supply |
| 093 | Front Left Out Valve — Drive Short to Supply |
| 094 | Rear Right In Valve — Drive Short to Supply |
| 095 | Rear Right Out Valve — Drive Short to Supply |
| 096 | Rear Left In Valve — Drive Short to Supply |
| 097 | Rear Left Out Valve — Drive Short to Supply |
| 100 | Pump Relay — Drive Short to Supply |
| 101 | Brake Light Relay — Drive Short to Supply |
| 110 | Sticking Throttle Detected |
| 111 | Shuttle Valve Sticking |
| 112 | Internal ECU comms error |
| 113 | Shuttle Valve Switch Dynamic Failure |
| 114 | Shuttle Valve Switch Electrical Failure |

## Three-amigos link
The "three amigos" (ABS + TC + HDC lamps) light up for many of these — especially
**wheel-speed sensor faults** (044–047 low, 064–067 electric fail, ~082–089 bad
output) and the **shuttle valve** (016, 111, 113, 114). During the sniff: read SLABS fault codes
and note which are **Current** vs **Intermittent** + counter → cross against this list.
