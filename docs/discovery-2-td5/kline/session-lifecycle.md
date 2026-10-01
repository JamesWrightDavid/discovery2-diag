---
title: "Session lifecycle: establish, keepalive, teardown"
area: docs
status: stable
version: 1.0
updated: 2026-10-01
depends_on: [docs/discovery-2-td5/kline-protocol.md]
summary: >
  How a module session is established, kept alive and torn down (StopDiagnosticSession 20 vs StopCommunication 82), and why a stale link causes 7F 81 10.
---

# Session lifecycle: establish, keepalive, teardown

Part of [the shared K-line / KWP2000 layer](../kline-protocol.md). Confidence tags (🟢 🟡 🔴) are defined there.

## 7. Session lifecycle: establish, keepalive, teardown

`EcuSession` is where the module layers share behaviour. A subclass sets `name` and
calls `_establish(after=…)`:

- **Td5:** `after=self.connect` — after init it runs StartDiagnosticSession and the
  SecurityAccess seed→key unlock. Has a session to close (`_has_session = True`).
- **SLABS:** `after=None` — no session, no unlock; services work immediately after
  fast init. `_has_session = False`.

### Keepalive timing

`tester_present()` (`3E` → `7E`) keeps a session alive between requests, within a
roughly **~2 s** window before the ECU times the link out. Two important details:

- **SLABS needs a bare `3E`** (no sub-function byte): the sniffed frame is
  `01 3e 3f` → `01 7e 7f`. A `3E 01` **kills its session.** SLABS overrides the
  keepalive sub-function to `None` for exactly this. 🟢
- Td5 and the others use the standard `3E 01`. 🟢

**SLABS must be polled lightly (🟢):** ~1 Hz keepalive plus a *few* reads. Block-
reading many LIDs every 0.5 s cycle killed the session after ~15 s. The dashboard's
SLABS source reads only the heights (`21 54`) per cycle and faults at most every
10th poll, and rotates the wider input block one LID per cycle to stay near 1 Hz.

### Teardown — the hard-won rules 🟢

These only bite against the real shared bus, and getting them wrong produces a bug
that outlives the process:

> **A `7F 81 10` (generalReject) on StartCommunication means a link is still open on
> the bus.**

There are **two** teardowns and both matter:

| Teardown | SID | Ends | Applies to |
|---|---|---|---|
| StopDiagnosticSession | `0x20` | a *diagnostic session* | Td5 only |
| StopCommunication | `0x82` | the *communication link* fast init created | **every** module |

Fast init opens a communication link even for modules with no diagnostic session
(SLABS). If you only close the serial port, that link **lives on inside the ECU**,
and the next StartCommunication — even from a completely fresh process — is met with
`7F 81 10` until the module's own timeout expires. **Proven in the car 2026-08-18:**
a fresh process, SLABS as the very first module talked to, got generalReject on the
first attempt because a previous run had died with the link open. The log shows the
pattern: three empty polls → `close()` without an `82` → every following init
rejected for ~90 s.

Therefore:

- **Always end a module with `EcuSession.release()`** — on module switch **and** on
  error paths — never a bare `close()`. `release()` = `end_session()` (best-effort
  `20` if there's a session, then always `82`) + `close()`.
- `_establish` sends a **best-effort `82` once before every init attempt**, to clear
  a stale link left by a previous run, *before* the quiet period — not between
  retries.

> **The quiet period is not a politeness pause.** Across every factory-tool sniff
> (2026-08-07/08/09), each successful SLABS init came on the **first** attempt after
> **25–28 s of no traffic to the module**, and the tool never made a fast retry.
> Sending *anything at all* during the wait — including an `82` — **resets the
> wait.** So `_establish` clears the link once, then goes silent; it does not try to
> fix a stuck link with a shorter idle or more frames. 🟢

---
