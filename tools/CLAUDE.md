# tools/

Discovery 2 CLI entry points and reverse-engineering utilities. They import the platform
as `openostler.*` and the pack as `d2diag.*`; install both (`pip install -e .` next to the
platform) so the signal store resolves through the active pack. The dashboard itself is
the platform's `tools/dashboard.py`.

## Files

- `verify_ecu.py`, `module_scan.py`, `bcu_scan.py` — read-only live checks, the address
  scan and the BCU input scan (logic in `openostler.modscan`, `d2diag/bcu/scan.py`).
- `decode_session.py`, `analyze_capture.py`, `raw_analyze.py`, `diffmap.py`,
  `lid_sweep.py`, `map_inputs.py`, `map_gui.py`, `nanocom_import.py`,
  `parse_nanocom_emulator.py` — capture analysis and mapping (`nanocom_import` logic in
  `src/d2diag/sniff/importer.py`).
- `build_protocol_library.py`, `export_signals.py`, `gen_signal_header.py`,
  `gen_faultmap.py`, `gen_fault_docs.py`, `gen_dtc_seed.py` — generators from the
  canonical stores. `make_demo_session.py` — regenerates `src/d2diag/demo/sessions/`.

## Editing rules

- Keep logic in `src/d2diag/`. Tools are thin wrappers so the logic stays testable.
- Generators read the canonical store. Never hand-edit their output; CI runs `--check`.
