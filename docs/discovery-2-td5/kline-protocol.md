---
title: "The Shared K-line / KWP2000 Layer"
area: docs
status: stable
version: 1.1
updated: 2026-10-01
summary: >
  Shared K-line/KWP2000 layer: physical bus, init handshakes, the two frame formats, services and teardown rules common to all modules.
---

# The Shared K-line / KWP2000 Layer

This is the common transport-and-protocol foundation every Discovery 2 module in
this project sits on: the physical K-line, the init handshakes that wake an ECU,
the two KWP2000 frame formats, and the KWP2000 services and teardown rules shared
across Td5, SLABS, BCU, ACE, EAT and Airbag. Module-specific identifiers, scaling
and security live in the per-module docs; everything here is what they have in
common.

The stack is strictly bottom-up — each layer knows only the interface of the one
below it:

```
Transport   raw bytes in/out (SerialTransport, LoggingTransport)
K-line      frame encode/decode + fast/slow init, echo, retries, tolerant reads
KWP2000     service IDs, negative responses (0x7F + NRC), responsePending (0x78)
EcuSession  lifecycle, keepalive, establish-retry, clean teardown
Module      td5 / slabs / bcu / airbag / ace / eat
```

## Contents

| Part | Page |
| ---- | ---- |
| 1. Physical layer · 2. Fast init · 5. Slow init (BCU) | [kline/physical-and-init.md](kline/physical-and-init.md) |
| 3. Frame formats · 4. Checksum · 6. KWP2000 services | [kline/frames-and-services.md](kline/frames-and-services.md) |
| 7. Session lifecycle: establish, keepalive, teardown | [kline/session-lifecycle.md](kline/session-lifecycle.md) |

## Confidence legend

| Tag | Meaning |
|---|---|
| 🟢 **Proven** | Sent against a real vehicle and confirmed. Car, date and method cited. |
| 🟡 **Assumed** | Derived, transcribed, or matched to a published spec/range but not confirmed on our car. |
| 🔴 **Unknown** | An open question we can see but cannot yet interpret. |

The reference vehicle throughout is **RDL 016**, a Discovery 2 Td5 (ES, ZF4HP22/24).
"Sniff" means a passive RX-only ESP32 on K-line pin 7 recording while a factory-grade
tool (a borrowed reference tool) drove the bus.

---

## Provenance

Protocol *facts* learned from other open projects are credited; no code was copied.
- **muki01/OBD2_K-line** (MIT): 25 ms/25 ms fast init pulse, `0xC1` positive marker,
  permissive burst reading, 5-baud slow init.
- **Ekaitza_Itzali** (EA2EGA): real Td5 sniff logs confirming the checksum rule, the
  fast-init timing, Td5 addressing (`0x13` / tester `0xF7`) and identifiers.
- Timing measurements, the Linux/macOS platform split, the teardown behaviour and
  every 🟢 tag here were verified against RDL 016 on the dates cited.

## Changelog

- 2026-10-01 — Split into three pages under `kline/`; this page is now the hub.
