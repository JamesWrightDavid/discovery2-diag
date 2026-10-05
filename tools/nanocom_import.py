"""Import a labelled NanoCom capture → signal-store candidate mappings.

    PYTHONPATH=src python3 tools/nanocom_import.py logs/nanocom-20261001.log
    PYTHONPATH=src python3 tools/nanocom_import.py logs/session.log --module td5 --write

Reads a capture logged by ``tools/esp32_read.py`` with ``>>> screen …`` / ``>>> value …``
markers (see ``references/nanocom_capture_protocol.md``), runs the auto-mapper per
labelled value and prints a markdown report. ``--write`` persists each solved mapping as
a **candidate** in ``src/d2diag/vehicles/lr_d2/signals/<module>.json`` with the capture name as
provenance.

Fault screens (``s <module>/faults`` + ``v fault=<as shown>``, T-30) are paired with the
raw fault reply on the same screen and judged against the fault store
(``references/fault_capture_runsheet.md``). With ``--write``, airbag/autobox/ace rows
that the capture fully supports are promoted to proven in
``references/<module>_fault_codes.md`` and the store and dictionary are regenerated; Td5
and SLABS promotions are printed as hand edits. This tool never talks to the car.

The logic lives in :mod:`d2diag.sniff.importer` so it stays unit-testable.
"""
from __future__ import annotations

import argparse
import sys

from pathlib import Path

from d2diag.sniff.fault_import import import_faults, promote_in_reference, render_fault_report
from d2diag.sniff.importer import import_capture, render_report

_REFS = Path(__file__).resolve().parents[1] / "references"


def main() -> int:
    ap = argparse.ArgumentParser(description="Import a labelled NanoCom capture")
    ap.add_argument("log", help="capture log (from tools/esp32_read.py)")
    ap.add_argument("--module", help="only this store module (e.g. td5, slabs, bcu)")
    ap.add_argument("--write", action="store_true",
                    help="persist solved mappings as candidates in the signal store")
    args = ap.parse_args()

    report = import_capture(args.log, write=args.write, module_filter=args.module)
    sys.stdout.write(render_report(report))

    faults = import_faults(args.log)
    if args.module:
        faults["screens"] = [s for s in faults["screens"] if s["module"] == args.module]
    sys.stdout.write("\n" + render_fault_report(faults))
    if args.write:
        changed = sorted({sc["module"] for sc in faults["screens"] for r in sc["rows"]
                          if r["promotable"] and promote_in_reference(
                              sc["module"], r["key"], faults["capture"], _REFS)})
        if changed:
            import subprocess
            root = Path(__file__).resolve().parents[1]
            for tool in ("gen_dtc_seed.py", "gen_fault_docs.py"):
                subprocess.run([sys.executable, str(root / "tools" / tool), "--force"]
                               if tool == "gen_dtc_seed.py" else
                               [sys.executable, str(root / "tools" / tool)], check=True)
            sys.stdout.write(f"\nPromoted to proven in references/: {', '.join(changed)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
