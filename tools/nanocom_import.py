"""Import a labelled NanoCom capture → signal-store candidate mappings.

    PYTHONPATH=src python3 tools/nanocom_import.py logs/nanocom-20261001.log
    PYTHONPATH=src python3 tools/nanocom_import.py logs/session.log --module td5 --write

Reads a capture logged by ``tools/esp32_read.py`` with ``>>> screen …`` / ``>>> value …``
markers (see ``references/nanocom_capture_protocol.md``), runs the auto-mapper per
labelled value and prints a markdown report. ``--write`` persists each solved mapping as
a **candidate** in ``src/d2diag/signals/<module>.json`` with the capture name as
provenance. This tool never talks to the car — it reads a log and writes JSON.

The logic lives in :mod:`d2diag.sniff.importer` so it stays unit-testable.
"""
from __future__ import annotations

import argparse
import sys

from d2diag.sniff.importer import import_capture, render_report


def main() -> int:
    ap = argparse.ArgumentParser(description="Import a labelled NanoCom capture")
    ap.add_argument("log", help="capture log (from tools/esp32_read.py)")
    ap.add_argument("--module", help="only this store module (e.g. td5, slabs, bcu)")
    ap.add_argument("--write", action="store_true",
                    help="persist solved mappings as candidates in the signal store")
    args = ap.parse_args()

    report = import_capture(args.log, write=args.write, module_filter=args.module)
    sys.stdout.write(render_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
