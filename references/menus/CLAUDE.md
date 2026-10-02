# references/menus/

Reference-tool menu transcriptions: one file per module, in the exact UI order. They
drive the `*_MENU` coverage maps in `src/d2diag/*/menu.py`.

## Files

- `overview.md` — provenance, the capture workflow and the session template.
- `bcu-inputs.md`, `bcu-settings.md`, `bcu-outputs-utilities.md` — DCU/BCU.
- `ace.md`, `autobox.md`, `airbag.md`, `td5.md` — the other modules.
- `cruise.md` — Hella cruise control (from the emulator; V8 branch, Td5 cruise unconfirmed).

## Editing rules

- Keep the tool's menu order and spelling exactly, typos included. Order may equal
  byte/bit order.
- Displayed values are screenshot examples. Never record them as protocol constants.
- When a capture maps an item, update the matching `menu.py` status and the signal
  store. Do not record the mapping here.
