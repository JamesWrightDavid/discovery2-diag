# CLAUDE.md — Entry Point

The **Ostler pack for Land Rover Discovery 2** (Td5) over **K-line** (pre-CAN): the
Discovery 2 module layers, signal and fault data, menus, actions, demo data, importers,
tools and research. It is reverse-engineered from sniffed bus traffic. The platform that
runs it is [openostler/ostler](https://github.com/openostler/ostler) (import `openostler`);
this pack is the `d2diag` distribution, registered under the `openostler.vehicle` entry
point as `lr_d2 = "d2diag:PACK"`. This repo follows the
[Vibes as Code](https://github.com/JamesWrightDavid/Vibes-as-Code) method: orient
cheaply, then load on demand.

## Read first, every session

1. **[INDEX.md](INDEX.md)** is the manifest: every doc's path, area, status and
   ~100-token summary, plus reading paths.
2. **[CONSTITUTION.md](CONSTITUTION.md)** holds this pack's hard rules (protocol, safety,
   data honesty). It defers to the platform's constitution for platform rules. Load it in
   full and never summarize it.

## Then load on demand

- The pack's code map, commands and key seams: [docs/architecture.md](docs/architecture.md).
- The pack's goals, and the platform's in brief: [GOALS.md](GOALS.md).
- Mission and boundary with the platform: [SCOPE.md](SCOPE.md).
- What is proven, candidate or open per module:
  [references/protocol_state_handoff.md](references/protocol_state_handoff.md).
- What to test next in the car: [references/test_plan.md](references/test_plan.md).
- Why a choice was made: [decisions/](decisions/CLAUDE.md) (platform ADRs are in the
  platform repo).
- Designs in progress: [specs/](specs/CLAUDE.md).

## Working rules

- UX first (platform ADR-0045): no screen, setup flow or widget without an approved UX
  brief; build it against recorded fixtures before wiring. Decoding, protocol and pack-data
  work need no brief.
- Design before code: write a spec in `specs/` and get it approved before implementing.
  Platform changes go to the platform repo.
- Install the platform, then the pack (`pip install -e ".[dev]"`), and run `pytest -q`
  before committing code. It needs no hardware.
- After editing docs, run `python3 skill/scripts/validate_frontmatter.py`, then
  `python3 skill/scripts/build_index.py`. `INDEX.md` is generated, so never hand-edit it.
- Record car and capture findings in `references/` and the signal store in the same
  commit as the code change. Close out the matching `references/test_plan.md` item.
