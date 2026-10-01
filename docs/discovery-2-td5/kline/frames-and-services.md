---
title: "KWP2000 frame formats, checksum and services"
area: docs
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [docs/discovery-2-td5/kline-protocol.md]
summary: >
  The two KWP2000 frame formats (addressed and length-prefixed), the checksum rule, and the KWP2000 services and negative responses shared by every module.
---

# KWP2000 frame formats, checksum and services

Part of [the shared K-line / KWP2000 layer](../kline-protocol.md). Confidence tags (🟢 🟡 🔴) are defined there.

## 3. Frame formats

Two KWP2000 frame formats are used, distinguished by the top two bits of the first
byte (the *format byte*). `read_frame` sniffs the format byte, so both work
transparently on the same session.

Format byte: bits 7–6 = address mode, bits 5–0 = length (0 → length is in a
separate following byte).

| Mode bits | Meaning | Header shape |
|---|---|---|
| `00` | no address (unaddressed) | `<len> …` |
| `10` | physical addressing | `<8n> <target> <source> …` |
| `11` | functional addressing | `<Cn> <target> <source> …` |

### Addressed (fast init / StartCommunication only)

Used **only** for StartCommunication / fast init. Carries a target and source
address:

```
81 13 F7 81 0C
8n Tgt Src data cs        (0x81 = mode 10 | length 1)
```

Physical addressing uses `0x8n`; **functional** addressing uses `0xCn`. The
functional variant (`C1 …`, source `0xF1`) is what the muki01 reference uses, and
was the **only** mode SLABS answered during our address hunt on 2026-08-05
(`C1 29 F1 81 5c` → `C1 57 8F`, while physical init to the same address was silent). 🟢

### Unaddressed (the whole session after init)

After the link is up, Td5 and SLABS switch to **unaddressed** length-prefixed
frames for everything — no target/source, just length:

```
02 10 A0 B2      02 27 01 2A      02 21 1D …
└len SID data cs┘
```

`EcuSession.read_block()` is deliberately the exact `{lid_hex: bytes}` shape the
differential mapper (`sniff/automap.py`) consumes, which is what lets a live session
feed the mapper directly.

### The Airbag exception 🟢

Airbag/SRS (TRW SPS 2A) does **not** switch to unaddressed session frames. It uses
**addressed framing on every message**, at address **`0x5B`**. Proven from
`faultread-20260809.log` line 885:

```
82 5b f7 21 02 …  →  f7 5b 61 02 90 04 90 16 00 00 …
```

The KWP2000 layer supports this with an `addressed=True` flag that prepends
format/target/source to *every* request, not just init.

---

## 4. Checksum

Every frame ends with a one-byte checksum:

> **checksum = 8-bit sum of all preceding bytes, including the length byte, mod 256.**

🟢 Confirmed against the Ekaitza sniff captures and independently validated by our
own capture parser (`tools/analyze_capture.py`) and the BCU write frames. This holds
for both frame formats — the sum runs over the entire frame up to (not including)
the checksum byte itself.

```python
checksum(b"\x02\x10\xA0") == (0x02 + 0x10 + 0xA0) & 0xFF == 0xB2
```

The frame reader is tolerant of leading junk: rather than trusting the first byte as
a format byte, it scans the receive buffer for the **first frame with a valid
checksum**, which discards turnaround glitch bytes, and keeps any trailing bytes
(e.g. a following responsePending reply) for the next read.

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

## 6. KWP2000 services

The KWP2000 layer knows service IDs, positive/negative responses and
responsePending, but nothing about any module's identifiers or scaling. A positive
response echoes the request SID **OR'd with `0x40`**.

| SID | Service | Positive resp | Used for | Confidence |
|---|---|---|---|---|
| `0x10` | StartDiagnosticSession | `0x50` | Td5 enters a diagnostic session (`10 A0` → `50`) | 🟢 |
| `0x27` | SecurityAccess | `0x67` | Td5 seed→key unlock (`27 01` seed → `67`, `27 02` key → `67`) | 🟢 |
| `0x21` | ReadDataByLocalIdentifier | `0x61` | the workhorse — read live data / faults (`21 xx`) | 🟢 |
| `0x31` | StartRoutineByLocalIdentifier | `0x71` | start a routine (e.g. injector / security routines) | 🟢 |
| `0x33` | RequestRoutineResultsByLocalIdentifier | `0x73` | read a routine's result | 🟢 |
| `0x30` | InputOutputControlByLocalIdentifier | `0x70` | actuator/output tests (`30 xx FF`) | 🟢 |
| `0x1A` | ReadEcuIdentification | `0x5A` | ECU ID / VIN (`1A 87` etc.) | 🟡 seen in captures; not yet a stack method |
| `0x3E` | TesterPresent | `0x7E` | keepalive | 🟢 |
| `0x20` | StopDiagnosticSession | `0x60` | end a diagnostic session (Td5) | 🟢 |
| `0x82` | StopCommunication | `0xC2` | tear down the communication link (all modules) | 🟢 |

**Negative response:** `7F <SID> <NRC>`. The layer raises `NegativeResponse` with
the decoded name. NRCs handled by name:

| NRC | Name |
|---|---|
| `0x10` | generalReject |
| `0x11` | serviceNotSupported |
| `0x12` | subFunctionNotSupported |
| `0x22` | conditionsNotCorrect |
| `0x31` | requestOutOfRange |
| `0x33` | securityAccessDenied |
| `0x35` | invalidKey |
| `0x36` | exceedNumberOfAttempts |
| `0x78` | **responsePending** |

**responsePending (`0x78`) 🟢:** a `7F <SID> 78` means "working on it, wait" — the
layer **waits for the next frame without resending** (up to a bounded number of
pending replies, default 6), then continues. Resending here would double-issue the
request.

**Tolerant service reads 🟢:** with `tolerant=True` (the setting for cheap cables),
each request reads the whole burst and searches it for a positive SID
(`service | 0x40`) or a negative `7F <service>`, preferring a two-byte match
(`61 <lid>`, `67 <level>`) for precision. The echo doesn't interfere because its SID
is the *request* value, not `service | 0x40`.

---
