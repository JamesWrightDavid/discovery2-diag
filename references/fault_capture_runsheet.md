---
title: "Fault capture run-sheet — T-30, every fault screen against its raw frame"
area: references
status: stable
version: 1.0
updated: 2026-10-04
summary: >
  Printable field run-sheet for T-30: open each module's fault screen on the NanoCom while the passive tap records, type each displayed fault line as a v fault= marker, and let tools/nanocom_import.py pair it with the raw reply to promote candidate fault meanings to proven. Read and photograph only; never clear before reading.
---

# Fault capture run-sheet — T-30

One pass through every module's **Faults – Read** screen with the passive tap recording.
For each screen, type what the NanoCom shows. Afterwards `tools/nanocom_import.py` pairs
every typed line with the raw fault reply from the same screen and reports which store
entries the capture supports (see the spec,
[2026-10-04-fault-screen-import-design.md](../specs/2026-10-04-fault-screen-import-design.md)).

Rig, tap wiring and the marker shorthand: [nanocom_capture_protocol.md](nanocom_capture_protocol.md).

## ⚠️ Safety

- **Read faults only.** Do **not** clear anything until every screen has been read, typed
  and photographed. A clear destroys the evidence.
- **Airbag:** faults only. Never any output or utility.
- **ACE:** never "Set Calibrated" or "Set Tested". An owner reports both locked up ACE
  ECUs. Never run the DCV output tests: the vehicle can jerk violently.
- Stationary, handbrake on, ignition on. SLABS stops talking above ~8 km/h by design.

## Before the first screen

1. Start the logger (`tools/esp32_read.py`). Type `note nanocom firmware <version>` from the
   NanoCom's About/version screen. Quirks differ by firmware.
2. Photograph every fault screen as well as typing it. The photo is the evidence a person
   checks if the importer reports a conflict.

## Per screen

Order: Td5, SLABS, airbag, gearbox, ACE. Hold each screen ~10 s so the reply is captured.

```
s <module>/faults
v fault=<first line, exactly as shown>
v fault=<next line …>
```

If the screen shows no faults, type `v fault=none`. Copy the text **verbatim**, including
codes, punctuation and the state word. Examples:

| Module | Type it like this | Watch for |
|---|---|---|
| td5 | `v fault=(12,7) GLOWPLUG LAMP DRIVE OPEN LOAD, (CURRENT)` | `byte15.bit7` and `byte18.bit6` are set on this car and unnamed, so any line you see there names them. Re-read the line the baseline wrote as `001-07`. |
| slabs | `v fault=20-05 right front wheel speed sensor output too low intermittent 254 times` | Include the **"N times"** line. It shows whether the first number is the count. |
| airbag | `v fault=Code 004 - <text> (intermittent)` | 004 and 022 are this car's faults; a match promotes both. |
| autobox | `v fault=P1884-33 <text>` | Include the internal number after the P-code if shown. |
| ace | `v fault=04-04 <text>` | 04-04 has no known text anywhere. If you export a TXT file, compare its codes with the screen (one owner saw 18-04 on screen and 04-02 in the TXT). |

**SLABS wheel corners:** if you also map wheel-speed or sensor channels, unplug one sensor
and check which corner reacts. Don't trust NanoCom's corner label; it is wrong on the P38's
Wabco unit.

## After the session

```
PYTHONPATH=src python3 tools/nanocom_import.py logs/<capture>.log
```

The report gives a verdict for every typed line:

| Verdict | Meaning | What to do |
|---|---|---|
| **supported → promotable** | the code is set in the raw reply and the text matches a candidate entry | rerun with `--write`. Airbag rows are promoted in `references/airbag_fault_codes.md`; Td5/SLABS print the hand edit. |
| supported | the same, but already proven | nothing |
| name proposal | set in the raw reply, but the store has no name | add the name as candidate by hand, citing the photo |
| text conflict | the screen's text differs from the store | check the photo, then correct the entry or note the tool quirk |
| not in raw | the displayed code isn't in the raw reply | check the capture: was the screen marked before its reply? |
| text agrees (ACE/gearbox) | the text matches, but their raw replies aren't decoded yet | keep the raw block in the report; it seeds the decoder |

Then record the session in [test_plan.md](test_plan.md) (T-30) and close the items it
settles.
