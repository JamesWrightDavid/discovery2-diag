---
title: "HEVAC (climate) control — Design"
area: specs
status: draft
version: 1.0
updated: 2026-10-02
depends_on: [specs/2026-10-02-hardware-platform-design.md, docs/discovery-2-td5/system-map.md]
summary: >
  Control and read the Discovery 2 electronic climate control (HEVAC/ATC) without the
  diagnostic bus — by sniffing the control panel's display bus to read current state and
  injecting button presses to change it. Covers reverse-engineering method, read/write
  hardware, closed-loop control, and safety framing.
---

# HEVAC (climate) control — Design

## Goal

Read the current climate state (setpoint, fan, mode, A/C on/off, recirc) and set it
remotely — integrating A/C into the dashboard. The HEVAC is **not reachable over the
diagnostic K-line** (`system-map.md` lists it 🔴, not in the Td5 kit), so this is a
physical panel hack: **sniff the display to read, inject buttons to write.**

The HEVAC controller still governs the compressor, blower and flaps — we only operate its
own front panel. This keeps actuation one step removed from the real system (in keeping
with the "don't bypass the module" discipline).

## Read side — decode the display bus

- **RE tool: a logic analyzer first** (FX2 8-ch + sigrok/PulseView, built-in I2C decoder).
  Tap SDA/SCL + GND and capture while poking the panel. Same "capture then understand"
  pattern as the K-line sniffs.
- **Confirm the bus type** — panels may use I2C, SPI, or a proprietary segment-driver
  serial. Verify before assuming I2C.
- **Expect segment bitmaps, not values.** Reverse the segment→meaning map by changing one
  setting at a time and diffing frames — the same differential-mapping approach as
  `sniff/automap.py`.
- **Runtime capture:** RP2040 **PIO** is the strong choice for deterministic I2C sniffing
  (an ESP32 ISR struggles at speed).
- **Electrical:** stay a passive, high-impedance listener — never drive SDA/SCL (a second
  master = bus conflict). Short stub; level-shift if the panel runs 5 V.

## Write side — inject button presses

- Emulate each press with a **dry contact across the switch**: a **photoMOS relay
  (AQY21x)** or **analog switch (CD4066)** in parallel with the button, driven by MCU GPIO.
  Galvanic isolation means no dependence on the button's ground/polarity/scan voltage.
- **Mind the matrix:** if buttons are a scanned row/column matrix, bridging a switch's two
  terminals reads as that key; pulse one at a time to avoid ghosting.
- **Timing:** a press = energize ~100–200 ms; hold-to-ramp = repeated pulses.
- One isolated channel per controllable button (temp ±, fan ±, mode, A/C, recirc…).

## Closed-loop control

Read state from the display → pulse buttons until it matches the target ("set 21 °C" =
read setpoint, tap up/down to converge). Expose over the existing web API/UI as a climate
panel. Confirm each action succeeded via the decoded display before reporting done.

## Hardware

RP2040/Pico (PIO I2C sniff + GPIO optos) is ideal; ESP32 works for the write side. Plus the
logic analyzer for the RE phase. This rides on the platform spec's real-time MCU.

## Safety & gating

- Actuation path → **requires its own ADR** and sits behind an explicit gate (CONSTITUTION
  → Safety).
- Fail-safe: on error/power loss, inject nothing — the panel returns to manual control.
- Confirm the car has the **electronic ATC** (digital display/bus), not manual HVAC.

## Planned development

- **B2 (read):** logic-analyzer capture; confirm bus type; build the segment→state map;
  passive PIO reader; surface climate state in the snapshot.
- **D1 (write, gated, after ADR):** one photoMOS across a single button (e.g. fan+);
  confirm an injected press registers; expand to the full button set; closed-loop setpoint.

## Open questions / confirm

- Bus type and voltage at the panel; exact SDA/SCL (or equivalent) lines.
- Button matrix layout vs discrete lines.
- Manual HVAC vs electronic ATC on the target car.

## Changelog

- 2026-10-02 — Initial design drafted from the HEVAC conversation.
