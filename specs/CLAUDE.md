# specs/

Design docs (`YYYY-MM-DD-<topic>-design.md`) for the Discovery 2 pack. A design must be
approved here before implementation starts. Platform designs (UI, logbook, replay, the
platform direction, Phase 0 decoupling, hardware, tracker/alarm) live in
https://github.com/openostler/ostler/tree/main/specs.

## Files

- `2026-10-01-nanocom-capture-design.md` — NanoCom capture readiness + full system map (ADR-0005/0007).
- `2026-10-02-hevac-control-design.md` — climate control via display sniff + button
  injection. Archived: moved out of scope (a separate ESP32 project).
- `2026-10-04-dtc-coverage-design.md` — filling the fault-meaning store from forum lists, with confidence.
- `2026-10-04-fault-screen-import-design.md` — pairing labelled NanoCom fault screens with raw fault frames (T-30).
- `2026-10-04-reply-length-layouts-design.md` — store records restricted to one reply length (Td5 `21 1B` short/long).

## Editing rules

- Specs are living: bump `version` and `updated`, and append to `## Changelog`.
- Rebuild INDEX.md after editing.
