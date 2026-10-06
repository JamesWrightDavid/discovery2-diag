# Ostler pack for Land Rover Discovery 2

The **Land Rover Discovery 2 (Td5)** vehicle pack for **[Ostler](https://ostler.tech)**,
the open, smart-home-like ecosystem for your car ([openostler/ostler](https://github.com/openostler/ostler)).

The D2 is a little too old for CAN bus: it talks to its control modules over **K-line**.
With a cheap OBD2-to-USB KKL cable (~€20–30) or an ESP32 tap, the platform speaks that
protocol, and this pack tells it what the Discovery 2 is: which modules it has, how to
reach and unlock them, what every byte means, and how its fault codes read. It is
reverse-engineered from sniffed bus traffic and community documentation.

> ⚠️ **Hobby / research project.** It reads a lot reliably, but it is not a finished
> commercial tool. Use at your own risk; see the [safety notes](#safety).

Ostler is not affiliated with or endorsed by Jaguar Land Rover. "Land Rover" and
"Discovery" are used only to say which vehicle this pack is for.

## Goals

The full pack goals are in [GOALS.md](GOALS.md).

- **Full Discovery 2 coverage:** every module the car carries (Td5, SLABS, BCU, airbag,
  ACE, EAT and any still-unconfirmed address) read over K-line, with faults, live data,
  tests and procedures.
- **NanoCom-parity map:** every menu item of the reference tool mapped to our LIDs and
  routines, each with an honest status, so the gap to a closed dealer-class tool is visible.
- **Verified signals:** every field is `proven` against the car or `candidate`; the
  in-car backlog ([references/test_plan.md](references/test_plan.md)) turns candidates
  into proven, and coverage never regresses.
- **The platform's reference pack and conformance fixture:** the pack the `VehiclePack`
  contract, the generated UI and the decode pipeline are tested against.
- **Contributing upstream:** CC BY-SA data in an OBDb-compatible shape, offered to OBDb
  (which has no D2/Td5 entry), and a shareable progress report for the Td5 community.
- **Safe by construction:** read-first, airbag read-only, gated actuators, EKA read/set only
  gated and opt-in (no key programming in any default path), no VIN or raw capture ever committed.

## Part of Ostler

This pack is one part of **Ostler**: *an open, smart-home-like ecosystem for your car. It
reads your car's diagnostics and live data, then grows with add-ons.* A base hardware pack
turns the car's existing systems into a connected IoT platform, and add-on modules
(guardian alarm, cameras, relay boxes, sensors, displays) join over standard IP
networking, with Home Assistant integration, for the Discovery 2 first and then any car. The platform's
full goals are in
[openostler/ostler GOALS.md](https://github.com/openostler/ostler/blob/main/GOALS.md).

## What is in this pack

| Part | Where |
|---|---|
| Module layers: **Td5** engine ECU (seed→key, live data, faults, output and injector tests), **SLABS** (ABS + self-levelling air suspension: faults, live data, actuator tests, ABS bleed), **BCU**, **airbag/SRS** (read-only), **ACE**, **EAT** auto gearbox | `src/d2diag/{td5,slabs,bcu,airbag,ace,autobox}/` |
| Signal store (the single source of truth for LID field mappings) | `src/d2diag/signals/*.json` |
| Fault-meaning store and fault-bit maps | `src/d2diag/dtc/*.json`, `src/d2diag/{td5,slabs}/faultmap.json` |
| Menus, actions (command registry), fault-scan order, data sources | `src/d2diag/{menus,actions,faultscan,sources}.py` |
| Sniff spec, NanoCom capture and fault-screen importers, protocol library | `src/d2diag/sniff_spec.py`, `src/d2diag/sniff/` |
| UI layout manifest | `src/d2diag/layout.json` |
| Demo: two synthetic sessions and a sniff log, plus their generator | `src/d2diag/demo/`, `src/d2diag/synth.py` |
| D2 tools: ECU checks, module and BCU scans, capture analysis, mappers, generators | [`tools/`](tools/CLAUDE.md) |
| ESP32 K-line node firmware (live view, sniffer) | [`esp32/`](esp32/README.md) |
| The knowledge base: every module, signal and service tagged 🟢 proven / 🟡 assumed / 🔴 unknown | [`docs/`](docs/README.md), [`references/`](references/CLAUDE.md) |

The pack plugs into the platform through the `VehiclePack` contract (entry point group
`openostler.vehicle`, name `lr_d2`, object `d2diag:PACK`). The platform never imports the
pack directly.

## Install with the platform

The platform is the app (K-line core, web dashboard, logbook, GPS); this pack is the data
and the Discovery 2 code. Install both:

```bash
python -m venv .venv && . .venv/bin/activate
pip install "openostler @ git+https://github.com/openostler/ostler@main"
pip install "d2diag @ git+https://github.com/JamesWrightDavid/discovery2-diag@main"
```

Then run the platform's dashboard (see the
[platform README](https://github.com/openostler/ostler)); it finds this pack through its
entry point. Exactly one installed pack is picked up automatically; with several, set
`OSTLER_VEHICLE=lr_d2`.

The module layers also work as a library:

```python
from openostler.kline import KLine
from openostler.kwp2000 import KWP2000
from openostler.transport import SerialTransport
from d2diag.td5 import Td5

td5 = Td5(KWP2000(KLine(SerialTransport("/dev/cu.usbserial-XXXX")), tolerant=True))
with td5:
    td5.establish()             # fast init → session → SecurityAccess unlock
    print(td5.read_faults())
    print(td5.read_all())       # decoded live data
```

## Develop

```bash
pip install "openostler @ git+https://github.com/openostler/ostler@main"   # or: pip install -e ../ostler
pip install -e ".[dev]"
pytest -q
python3 tools/gen_signal_header.py --check
python3 tools/gen_faultmap.py --check
python3 tools/gen_fault_docs.py --check
```

Tests run without hardware against a simulated half-duplex ECU (`tests/fakes.py`).
`tests/test_pack_contract.py` checks the pack against the platform's contract; it needs
the pack installed so the entry point exists. Read-only checks against the car:

```bash
python3 tools/verify_ecu.py td5   /dev/cu.usbserial-XXXX
python3 tools/verify_ecu.py slabs /dev/cu.usbserial-XXXX
```

Project rules for contributors and agents: [CLAUDE.md](CLAUDE.md) and
[CONSTITUTION.md](CONSTITUTION.md). What is proven and what is still open:
[references/protocol_state_handoff.md](references/protocol_state_handoff.md) and the
in-car backlog [references/test_plan.md](references/test_plan.md).

## Safety

K-line is a shared bus and this pack can *write* to ECUs. The design is read-first and
conservative:

- Fault reads and live data are read-only.
- Actuator tests (ABS pump, valves, air suspension) run only when you press the button,
  always behind a confirmation, and should be done **stationary with the ignition on**.
- **The airbag/SRS module is read-only by construction**: no clear, no outputs, no
  security writes. Never actuate pyrotechnic circuits.
- BCU output writes and the active mapping harness are gated or read-only by default.

## Credits

This project stands on other people's work. Full licences and exactly what was used are
in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

- **leijoma** started this repository (upstream
  [Leijoma/discovery2-diag](https://github.com/Leijoma/discovery2-diag)); their
  MIT-licensed work stays credited.
- **seed→key** (immobiliser SecurityAccess): ported from
  [pajacobson/td5keygen](https://github.com/pajacobson/td5keygen) (BSD-2-Clause).
- **Protocol reference** (framing, ECU addresses, init/session, identifiers, fault-code
  map): [EA2EGA/Ekaitza_Itzali](https://github.com/EA2EGA/Ekaitza_Itzali), protocol facts
  only, no code copied. Credits there to OffTrack (ECU disassembly) and Luca72 (Arduino
  reference).
- **K-line front-end** (fast-init timing, burst reads, L9637D):
  [muki01/OBD2_K-line_Reader](https://github.com/muki01/OBD2_K-line_Reader) (MIT snapshot; upstream GPL-3.0 since 2026-10-03).
- **Td5 fault-code text**: cross-validated against a public, community-maintained Td5
  fault-code list (offset/bit → fault text only).
- Thanks to the **Land Rover community** (forums and shared notes) for fault codes, menu
  structures and protocol tips.

Contributing data or code? Add yourself here, and see [CONTRIBUTING.md](CONTRIBUTING.md).

## Licences

- **Code:** [AGPL-3.0-or-later](LICENSE). A **commercial licence** is available from the
  maintainer.
- **Vehicle data** (`src/d2diag/signals/`, `src/d2diag/dtc/`, the fault maps, the layout,
  the demo data and the fault-code tables): [CC BY-SA 4.0](LICENSE-DATA).
- **Contributions** are accepted under the [Contributor License Agreement](CLA.md).
- Versions published before 2026-10-06 were MIT-licensed; copies obtained under those terms
  keep them.
- **Trademarks:** "Ostler" and "OpenOstler" are trademarks; the licences grant no rights to
  the names. See [TRADEMARKS.md](TRADEMARKS.md).
