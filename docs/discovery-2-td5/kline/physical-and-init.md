---
title: "K-line physical layer and init handshakes"
area: docs
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [docs/discovery-2-td5/kline-protocol.md]
summary: >
  The K-line physical layer, ISO 14230-2 fast init with the timing that works on cheap KKL cables, and the 5-baud slow init used by the BCU.
---

# K-line physical layer and init handshakes

Part of [the shared K-line / KWP2000 layer](../kline-protocol.md). Confidence tags (🟢 🟡 🔴) are defined there.

## 1. Physical layer

| Fact | Value | Confidence |
|---|---|---|
| Bit rate | 10 400 baud | 🟢 the working rate against every module; `DEFAULT_BAUDRATE = 10400` |
| Framing | 8 data bits, no parity, 1 stop bit (8N1) | 🟢 |
| Wire | Single shared, **half-duplex** K-line (pin 7 at the OBD connector) | 🟢 |
| Cable | Cheap **KKL 409.1 USB** adapter (FTDI-based) | 🟢 this is the hardware the whole project runs on |

K-line is one wire that both sides drive, so **every byte the tester sends is echoed
back** on the same line and must be read and discarded before the ECU's reply. The
K-line layer consumes this echo automatically (`KLine.request` reads the first valid
frame as the echo, the next as the response).

Because it is a single shared bus, only one module can be spoken to at a time. The
fault-scan reads modules strictly one after another: establish → read → release,
never overlapping.

> **macOS gotcha (🟢):** always open `/dev/cu.*`, never `/dev/tty.*`. The `tty`
> device blocks on DCD and will hang. `resolve_serial_port("auto")` handles this.

The `SerialTransport` keeps the byte interface (`send`/`receive`) clean and exposes
the serial-specific hooks (`baudrate`, `send_break`, `fast_init_low`, `slow_init`,
`reset_input_buffer`) that only the K-line layer is allowed to touch. A
`LoggingTransport` can wrap any transport transparently and record all raw TX/RX to
a timestamped file:

```
2026-07-21T12:00:00.123456Z TX 81 13 F7 81 0C
2026-07-21T12:00:00.234567Z RX 83 F7 13 C1 EA 8F
```

(On the in-car Raspberry Pi the log is `fsync`ed to the SD card every ~2 s rather
than per line, to survive an abrupt power cut when the engine is switched off
without hammering the card.)

---

## 2. Fast init (ISO 14230-2)

The Td5 engine ECU and SLABS are woken with a **fast init**: a fixed wake-up pulse
on the line, immediately followed by a `StartCommunication` request.

### The pulse

| Phase | Nominal | Confidence |
|---|---|---|
| TiniL — line **low** | 25 ms ± 1 | 🟡 from ISO 14230-2; matches muki01 (`delay(25)`) and Ekaitza |
| TiniH — line **high** | 25 ms ± 1 | 🟡 same sources |
| then | send `StartCommunication` | 🟢 |

The 25 ms + 25 ms figure is confirmed by two independent open references
(muki01/OBD2_K-line, MIT; Ekaitza_Itzali sniff logs) and produces a working init
against the real car, but the exact millisecond bounds are the ISO spec's, not
something we measured the ECU's tolerance of — hence 🟡 on the numbers, 🟢 that a
25/25 pulse wakes the car.

Timing this pulse on a non-realtime OS over USB is the hard part. Two problems:

1. **`time.sleep()` overshoots.** Measured on macOS, `sleep(25 ms)` actually
   returns after 25.3–32.0 ms (median ~29). So the *high* period is produced by
   sleeping to ~2 ms short of the target and then spin-waiting the rest
   (`_precise_wait`). 🟢 (measured)
2. **The low pulse must be deterministic.** An OS-timed UART break jitters with the
   scheduler; when it comes out too short the Td5 never enters diagnostic mode and
   answers `7F 81 10` (generalReject). So the low pulse is produced by a hardware
   trick where possible — **see the platform split below.**

### The macOS baud-360 trick vs the Linux `send_break` fix 🟢

`fast_init_low` needs to hold the line low for 25 ms. It does this differently per
platform, and getting this wrong was a **real bug fixed 2026-08-21**:

- **macOS (and `loop://` tests):** drop the port to ~360 baud and send a single
  `0x00` byte. A start bit plus 8 zero data bits = 9 low bits in a row; at 360 baud
  that is ~25 ms. The pulse length is set by the UART's bit clock (hardware), not by
  the OS scheduler, so it is stable even over USB. The trailing stop bit is high, so
  `fast_init_low` returns how long the line has *already* been high (~2.8 ms at
  360 baud plus baud-restore/buffer-flush cost) and the caller subtracts that from
  TiniH so the high period isn't systematically too long.

- **Linux (Raspberry Pi):** **the baud trick does not work.** FTDI on Linux
  (`ftdi_sio`) cannot actually do a baud rate as low as 360 — the kernel clamps it,
  so the `0x00` byte goes out at ~4500 baud and the low pulse is only **~2 ms
  instead of 25 ms → the ECU never wakes.** Measured in the car 2026-08-21: the baud
  trick gave `low_ms` 1.9–2.8 and **never** produced a C1; the OS-timed
  `send_break` gave `low_ms` 26 ms and C1 **on the first try.** So on Linux the code
  falls back to `send_break` (a real UART break condition held for the duration),
  which returns 0 high-time to compensate because a break is pure low time with no
  stop bit.

This platform split is why the same code can wake the car on the in-car Pi and on a
laptop, using two different mechanisms for the identical 25 ms pulse.

The actual pulse is always measured, not assumed: `KLine.last_pulse` records the
real `low_ms` / `high_ms` / `pre_high_ms` for every attempt, because the nominal
values say nothing about what a USB serial stack actually did.

### The StartCommunication response

| Message | Bytes | Confidence |
|---|---|---|
| Request (addressed) | `81 13 F7 81 0C` — StartCommunication `0x81` to ECU `0x13` from tester `0xF7` | 🟢 |
| Positive response | starts with **`0xC1`** (= `0x81 + 0x40`), followed by two key bytes | 🟢 |
| Td5 response | `C1 57 8F` | 🟢 (RDL016) |
| SLABS response | `C1 57 8F` | 🟢 (RDL016) |

`0xC1` is the universal "communication started" marker — muki01 checks the same
`resultBuffer[3] == 0xC1` on generic OBD-II, and we saw it against the Td5.

### Echo handling and tolerant reads

Cheap KKL cables + a non-realtime OS produce turnaround glitches: a stray byte
(e.g. `0xF8` / `0x00`) can slip in at the TX→RX turnaround, and FTDI latency jitter
during init can shred an otherwise valid frame's checksum. Two mechanisms cope:

- **`fast_init` (strict):** sends `StartCommunication` **once** and reads a valid
  frame. StartCommunication must never be retried — a second one is rejected as
  "already in session" (generalReject). 🟢
- **`fast_init_tolerant` / tolerant reads:** read the *whole* response burst raw
  (until ~60 ms of silence) and **search it for `0xC1`** instead of demanding a
  checksum-clean frame. A noise-damaged C1 frame (e.g. `03 c1 38 0e f8 00`) still
  *contains* `0xC1`, so we register "session open" on the first try and avoid the
  re-init loop that would otherwise re-open the session repeatedly and lock the ECU.
  The tolerant reader carefully **skips the echo first** before searching, because a
  *functional* request frame itself begins `0xC1` — without skipping, the search
  finds our own echo and falsely reports a session on an empty bus (seen in the car
  2026-08-19). 🟢

Keeping `tolerant=True` on KWP2000 for these cables is a hard rule — it is what
compensates for FTDI latency jitter during fast init.

---

## 5. Slow init (5-baud) — BCU

The BCU (Valeo body control unit) is not woken with a fast init. It uses the classic
**ISO 9141 / ISO 14230 5-baud slow init**:

| Step | Detail | Confidence |
|---|---|---|
| Address | `0x40` | 🟢 confirmed BCU in car 2026-08-20 (previously a candidate from the 2026-08-05 address hunt) |
| Address transmission | bit-banged on the break condition at **200 ms/bit** (5 baud): start bit (0), 8 data bits **LSB-first**, stop bit (1), 8N1 | 🟢 |
| ECU sync | ECU replies `0x55` at the normal baud, then two key bytes | 🟢 |
| Key bytes (KW1 KW2) | **`E5 8F`** | 🟢 (KW2 `0x8F` = KWP2000, same low key byte as the engine's `57 8F`) |
| Handshake completion | wait W4 (~30 ms), send `~KW2` (inverted), read `~address` (`0xBF`) confirmation | 🟢 |

`parse_slow_init` pulls (KW1, KW2) from a response that begins `0x55`; no leading
`0x55` means no module answered that address. (Note: the address-byte bit builder
was fixed 2026-08-04 — an earlier 7-bit + mis-computed-parity version produced the
wrong byte for addresses with an odd number of set bits, which would have made a
slow-init address scan miss exactly the interesting candidates. `0x40` happened to
come out right and hid the bug.)

The BCU also requires **ignition cycling** to attach in the factory tool
(off → key → on → key); that is a module quirk documented with the BCU, not a
K-line-layer rule.

---
