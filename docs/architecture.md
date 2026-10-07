---
title: Architecture and key seams
area: docs
status: stable
version: 2.4
updated: 2026-10-07
depends_on: [SCOPE.md, CONSTITUTION.md]
summary: >
  Developer map of the Discovery 2 pack: how it plugs into the Ostler platform (PACK and
  the VehiclePack contract), the module layers, the seams to understand before changing
  things (frame formats, EcuSession, signal store, data sources) and the dev commands.
---

# Architecture and key seams

The boundary and mission are in [SCOPE.md](../SCOPE.md). The rules that must not be
broken are in [CONSTITUTION.md](../CONSTITUTION.md). This page is the working map of the
pack. The platform's own map (server, UI, logbook, geo) is in the
[platform repo](https://github.com/openostler/ostler/blob/main/docs/architecture.md).

## Commands

```bash
python -m venv .venv && . .venv/bin/activate
pip install "openostler @ git+https://github.com/openostler/ostler@main"   # the platform
pip install -e ".[dev]"          # this pack: registers the openostler.vehicle entry point

pytest -q                        # whole suite, no hardware needed
pytest tests/test_slabs.py -q    # one file
pytest tests/test_pack_contract.py -q   # the VehiclePack contract

# Generators (CI runs --check)
python3 tools/gen_signal_header.py [--check]   # esp32/kline_node/signals_td5.h
python3 tools/gen_faultmap.py [--check]        # td5/slabs faultmap.json
python3 tools/gen_fault_docs.py [--check]      # docs/discovery-2-td5/fault-dictionary*.md
python3 tools/make_demo_session.py             # src/d2diag/demo/sessions/

# Read-only sanity check against a module
python3 tools/verify_ecu.py td5|slabs /dev/cu.usbserial-XXXX
```

The dashboard is the platform's (`tools/dashboard.py` in openostler/ostler); with this
pack installed it serves the Discovery 2. `pyproject.toml` sets
`pythonpath = ["src", "."]` for pytest, but the platform resolves its pack through the
entry point, so the pack must be installed. There is no linter or formatter config, so
match the surrounding style.

## How the pack plugs in

```
openostler.pack.active_pack()
   └─ entry point openostler.vehicle: lr_d2 = "d2diag:PACK"
        └─ d2diag/__init__.py: PACK built lazily on first access
             modules (ModuleSpec: id, name, address, init, keygen, aliases, live, kline)
             sources(port) → {td5: Td5DataSource, slabs: SlabsDataSource, others: InfoDataSource}
             signals_dir, dtc_dir, actions, menus, unlinked_ok, derived_fields
             faultscan readers, sniff spec + importers, demo, docs, layout.json
```

- **Canonical module ids** are the store ids: `td5, slabs, bcu, ace, autobox, airbag`.
  Legacy ids (`motor`, `eat`, `gearbox`) are declared once as aliases and migrated on read
  by the platform.
- **Lazy build.** `td5.identifiers` reads the signal store at import time, and the store
  path comes from the active pack, so building `PACK` must not import `td5` eagerly; the
  menus, keygen, derived fields and sources are reached through lazy wrappers.
- **Docs** are only offered from a source checkout (editable install); a wheel ships the
  data, not `docs/` or `references/`.
- **`layout.json`** is the screen layout the platform UI reads (`GET /pack` → `layout`),
  checked against the platform's `schemas/layout.schema.json` by `test_pack_contract.py`.
  It declares `driver_side: "right"` (the D2 is right-hand drive), so the platform puts
  its rail on the right on landscape screens (platform UI spec §3.3; added 2026-10-06).

## The stack

The comms layers come from the platform; the module layer is this pack.

```
Transport      openostler.transport: raw bytes in/out (SerialTransport, LoggingTransport)
K-Line         openostler.kline (encode/decode, fast/slow init, echo, retries)
KWP2000        openostler.kwp2000: service IDs, negative responses, responsePending
EcuSession     openostler.session: shared lifecycle/keepalive/read_block + tolerant retry
Profiles       d2diag.kline_profiles: each module's K-line profile + open_session()
Module layer   d2diag.td5 · slabs · airbag · bcu (+ ace/ autobox/ menu stubs)
Data sources   d2diag.sources (Td5/SLABS sources over openostler.web.sources.DataSource)
```

## Key seams

- **Two frame formats.**
  - Addressed framing (`0x8n`, target+source) is used only for StartCommunication and
    fast init.
  - After that, the whole session uses unaddressed length-prefixed frames
    (`<len> <SID> … <cs>`). `kline.read_frame` sniffs the format byte.
  - Airbag is the exception: it uses addressed framing throughout at 0x5B.
- **`EcuSession` is where module layers share behaviour.**
  - Subclasses set `name` and call `_establish(after=…)`.
  - Td5 passes `after=self.connect` (StartDiagnosticSession + SecurityAccess seed→key).
  - SLABS passes `after=None`, because its services work right after fast init. Its
    profile's keep-alive is a bare `3E` (`_keepalive_sub = None` covers a session built
    without a profile).
- **K-line profiles are data** (platform ADR-0022, K-line profiles spec migration step 2).
  - `d2diag/kline_profiles.py` declares the Td5, SLABS, BCU and airbag overrides of the
    platform built-ins (`kwp2000_fast`/`kwp2000_slow`) as `ModuleSpec.kline`: tester
    `0xF7`, header and length mode, keep-alive frame, 5-baud `~address` handling, and the
    platform's link idles and P3 guard switched off.
  - `open_session(module, transport)` builds every session (sources, fault scan, tools)
    via `KLine.from_profile`, `KWP2000.from_profile` and the session's `profile`.
  - Settle and retry sleeps, the SLABS init-variant cycle and `1A 8A` confirm, and the
    Td5/airbag sessions stay module code. `tests/test_kline_profiles_d2.py` pins that the
    wire bytes and sleeps equal the legacy constructors'.
- **`EcuSession.read_block(lids) -> {lid_hex: bytes}`** has exactly the shape
  `openostler.sniff.automap` consumes. That lets a live session feed the differential mapper.
- **Signal store (`src/d2diag/signals/*.json`).**
  - Decoders, the dashboard and automap all read it (through `openostler.signals`).
  - Confirmed mappings are written back with `upsert_field`.
  - Each field carries `confidence`, either `proven` or `candidate`.
  - A field with a canonical meaning also carries `metric`, a COVESA VSS path such as
    `Vehicle.Speed` (platform ADR-0016). It must resolve via `openostler.metrics.is_known`.
    Pack-private fields (injector balance, EGR, raw wheel speeds) have none. The store keeps
    its own units; conversion to the VSS unit is the platform's job.
    `tests/test_metrics_d2.py` pins the mapping.
  - **Shared VSS paths.** When more than one module maps the same `metric`, exactly one
    module's records carry `"primary": true` (a JSON boolean; absent means not primary, and
    `false` is not written). The node publishes `vss/<VSS path>` only from the primary
    field and every other module's reading on its `vss/lr_d2.<module>.<field>` leaf;
    selection across sources stays on the Brain (platform module-bus messages spec v1.3
    §6, owner answer 9). Every record of the primary field carries it, length variants
    included. `tests/test_metrics_d2.py` pins one primary per shared path. Today there is
    one shared path:

    | VSS path | Modules | Primary | Why |
    | -------- | ------- | ------- | --- |
    | `Vehicle.LowVoltageBattery.CurrentVoltage` | Td5 `21 10`@0, SLABS `21 44`@12 | **Td5** | Both are `proven`. Td5 reads it at 1 mV resolution (u16 ×0.001 V) against SLABS's 62.5 mV (u8 ×0.0625 V), and ours, Ekaitza's and SimonRafferty's decoders agree on it ([td5-cross-reference](../references/td5-cross-reference.md)). Td5 live data is read while driving; SLABS diagnostics go silent once the car moves and stay dead until the next ignition cycle (proven 2026-08-29, [slabs/overview](../references/slabs/overview.md)), and SLABS is only polled lightly (~1 Hz). So the SLABS value would go stale on every drive. |

    The choice ranks the two sources by recorded evidence; it raises no confidence. No
    side-by-side Td5 and SLABS reading is recorded yet: that is T-33 in
    [test_plan](../references/test_plan.md).
- **`d2diag.sources` is the pack's protocol/UI boundary.**
  - Each `DataSource.poll()` returns `{status, signals, faults}`.
  - `DERIVED_FIELDS` (fuel computer, ride heights in mm) adds presentation metadata for
    computed fields; the UI never hard-codes labels.
  - The simulated sources live only in `tests/fake_sources.py`.
- **`faultscan.py`** lists the fault readers (TD5, SLABS, airbag); the platform's
  `faultscan.read_all` runs them strictly in sequence: establish → read → release.
- **`sniff_spec.py`** maps K-line addresses to modules and holds the authoritative and
  hint detectors the platform's `ModuleTracker` uses, plus the NanoCom and fault-screen
  importers.

## Why the protocol rules exist

- **SLABS load.** Block-reading many LIDs every 0.5 s killed the SLABS session after
  ~15 s ([references/slabs/overview.md](../references/slabs/overview.md)).
- **What `7F 81 10` means.** A generalReject on StartCommunication means a link is still
  open on the shared bus. There are two teardowns:
  - `20` StopDiagnosticSession ends a Td5 diagnostic session.
  - `82` StopCommunication ends the link that fast init created.
- **The link outlives the process.** This was proven in the car on 2026-08-18.

## Conventions

- **Fakes.** `tests/fakes.py::FakeKLineEcu` is a half-duplex ECU simulator at the
  transport level: it echoes frames like the real bus. A response can be:
  - static bytes,
  - a sequence,
  - a `callable(count)`, when a test needs different values between reads.
- **Comments explain *why*.** Say which sniff or log a protocol fact came from. When you
  learn something from the car or a capture, record it in the relevant
  `references/*.md` alongside the code change.
- **`references/test_plan.md` is the living test backlog.** Every open hardware question
  goes there, with a procedure and a decision rule written before the test. When a result
  arrives:
  - route it to its permanent home (the signal store, `references/`, or the sister
    project for the car's own faults),
  - move the item to **Resolved** with the date and outcome.
- **`TODO.md`** is code and infrastructure only.

## Changelog

- 2026-09-30 — Extracted from the former root CLAUDE.md during Vibes as Code adoption.
- 2026-10-01 — Confidence vocabulary is now `proven`/`candidate` (ADR-0006).
- 2026-10-01 — Added the React/TypeScript UI layer and its contract.
- 2026-10-05 — Added `gps/` and `logbook/`: the server feeds every poll and the latest GPS fix
  to the session recorder; `/sessions*` serves replay data (ADR-0009).
- 2026-10-06 — No mock/demo mode: always live, demo logs replayed, simulated sources
  test-only (`tests/e2e_server.py` for UI work); record only while connected; `geo/` place
  names and the SQLite session index (ADR-0011).
- 2026-10-06 — Repo split: rewritten as the pack's map; the platform layers (server, UI,
  logbook, geo) moved to openostler/ostler.
- 2026-10-06 — Signal records now carry a VSS `metric` where the meaning is canonical
  (ADR-0016, U0 seams).
- 2026-10-07 — One `primary` module per shared VSS path (the battery voltage: Td5), per the
  platform module-bus messages spec v1.3 §6.
