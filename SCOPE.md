---
title: "Scope & architecture"
area: root
status: stable
version: 2.0
updated: 2026-10-06
summary: >
  This repo is the Ostler pack for the Land Rover Discovery 2 (Td5): the Discovery 2 module layers, signal and fault data, menus, actions, demo data, importers, tools, ESP32 node and research. The platform (comms core, server, UI, logbook) lives in openostler/ostler.
---

# Scope & architecture

**This repo is the Ostler pack for the Land Rover Discovery 2 (Td5).** Its mission is the
Discovery 2 half of "communication with the car and interpretation of its data": what
modules the car has, how to reach and unlock them, what every byte means, and how its
fault codes read. The platform that runs it (comms core, web server and UI, logbook, GPS,
integrations) lives in [openostler/ostler](https://github.com/openostler/ostler)
(ADR-0013, ADR-0014 there).

## Where this pack sits

```
PLATFORM (openostler)  transport · kline · kwp2000 · session · ports       COMMS
                       signals/dtc loaders · catalog · commands · sniff     generic INTERPRETATION
                       web server + UI · logbook · gps · geo · community    CONSUMERS
        ▲  VehiclePack contract: entry point openostler.vehicle → lr_d2 → d2diag:PACK
        │
PACK (this repo, d2diag)
  module layers   td5/ slabs/ bcu/ airbag/ ace/ autobox/
  data            signals/*.json (SSOT) · dtc/*.json · faultmaps · layout.json · demo/
  hooks           actions · menus · faultscan · sniff_spec · sources · synth · sniff importers
ESP32 node        esp32/ — a second comms node; its decode header is generated from signals/
```

## The hard rules

- **The platform never imports this pack.** It reaches it only through `PACK`.
- **This pack imports only the platform's public modules** (`openostler.*`), never copies
  them. Only `sources.py` imports the platform's `openostler.web` layer.
- **`src/d2diag/signals/*.json` is the one interpretation contract.** Python decodes it at
  runtime; the ESP32 header is *generated* from it, never hand-copied (hand-copying caused
  the MAF mis-map).

## What lives where

- `src/d2diag/` — the pack (`d2diag` import package, `PACK`).
- `esp32/` — the ESP32 K-line node and sniffer firmware; `hardware/` — its board notes.
- `tools/` — Discovery 2 CLI and reverse-engineering utilities.
- `references/` + `docs/` — protocol knowledge; `references/test_plan.md` is the living
  car-test backlog.
- `server/` — the community endpoint, here only until it seeds the private cloud repo.

## Deliberately out of scope

- **Platform code**: the comms core, server, UI, logbook, deploy and installers live in
  the platform repo.
- **HEVAC (climate) control** lives in a separate ESP32 project.
- The car's own faults and maintenance history belong in the sister project
  `../Discovery 2/`, not here.

See [docs/architecture.md](docs/architecture.md) for the pack's code map and
[CONSTITUTION.md](CONSTITUTION.md) for the hard rules.
