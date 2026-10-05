# decisions/

Immutable Architecture Decision Records for the Discovery 2 pack: one locked decision per
file. Platform-wide ADRs (layering, signal store, UI, logbook, licence, the repo split
ADR-0013 and the Ostler handles ADR-0014) live in the platform repo; see `README.md`.

## Files

- `README.md` — where the platform ADRs went.
- `adr-0005-nanocom-sniff-workflow.md` — passive NanoCom capture, candidate-only import.
- `adr-0007-bcu-security-access.md` — derive the BCU seed→key offline freely; gate every
  live SecurityAccess byte.

## Editing rules

- Never edit an accepted ADR's decision. Supersede it with a new ADR and set the old
  one's frontmatter `status: superseded`.
- ADR numbers are shared with the platform repo (they were one series before the split):
  check https://github.com/openostler/ostler/tree/main/decisions for the next free number.
- Rebuild INDEX.md after adding an ADR.
