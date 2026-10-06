# muki01 / OBD2_K-line_Reader — reference

A saved copy of `Basic_Code/` and `Schematics/` from
[muki01/OBD2_K-line_Reader](https://github.com/muki01/OBD2_K-line_Reader), a ready-to-flash
OBD2 K-line scan-tool firmware (ISO 9141-2 / ISO 14230 KWP2000, slow and fast init) for
Arduino/ESP32. Author: Muksin Muksin (muki01).

- **Snapshot:** upstream commit `a1946a7` (2025-09-24), byte-identical except for a trailing
  newline. The repository is still on GitHub; an earlier version of this note wrongly said
  it had been removed.
- **Licence of this copy: MIT** ("Copyright (c) 2023 Muksin Muksin"). Upstream was MIT until
  `91ae045` (2026-10-01) and has been GPL-3.0, with a commercial licence offered, since
  `aef63b4` (2026-10-03). Port only from `91ae045` or earlier, with the notice kept, and
  never from HEAD.
- **Not the library.** The PlatformIO entry "muki01/OBD2 K-Line" is the companion
  [OBD2_KLine_Library](https://github.com/muki01/OBD2_KLine_Library). Its current files carry
  non-commercial or conflicting licence headers, so it is facts only and we take no code.
- **Known bug in this snapshot:** request headers come from the *selected* protocol, so
  Automatic mode sends frames with no header. Upstream later switched to the *connected*
  protocol. Use this copy as a timing reference, not as working code.
- Full audit: the Ostler platform repo, `references/research/muki01/obd2_kline_reader.md`.

## What we take from here (into the ESP32 port)

- **Fast init** (`K_Line.ino`): `digitalWrite(TX, LOW); delay(25); digitalWrite(TX, HIGH); delay(25)`
  — 25 ms low + 25 ms high with **real-time GPIO**. Positive StartCommunication = `resultBuffer[3] == 0xC1`
  (the same `C1` we saw against the Td5). Confirms our approach.
- **5-baud slow init**: sends address `0x33` at 200 ms/bit.
- **Permissive read** (`readData`): reads the whole burst until ~60 ms of silence (`DATA_REQUEST_INTERVAL`)
  and indexes fixed positions — does NOT reject on checksum. Tolerates noise better. We recreated
  the technique in `tools/live_raw.py`.
- **Inter-byte `WRITE_DELAY`** when sending.
- **Addressing:** muki01 is standard OBD-II (`C1 33 F1 81`, functional address 0x33, tester 0xF1),
  NOT the Td5's physical `81 13 F7 81` (ECU 0x13 / tester 0xF7). The Td5 addressing + identifiers
  come from Ekaitza_Itzali.

## Schematics (`Schematics/`)

- `L9637D.png` — K-line transceiver (ST L9637D) as the interface. The robust path.
- `Transistor_Schematic.png` — discrete transistor interface (equivalent to the one the user built for the ESP32).

The Ekaitza note and these schematics point the same way: **real-time timing + noise filtering** give
reliable K-line — what a cheap USB-KKL + non-real-time OS cannot manage stably.
