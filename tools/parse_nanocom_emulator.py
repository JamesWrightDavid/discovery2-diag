#!/usr/bin/env python3
"""Generate the NanoCom emulator menu tree for the Discovery 2 Td5.

Reads the (gitignored) emulator JSON from ``captures/nanocom/emulator.json`` and writes the
derived tree to ``references/nanocom/`` as both structured JSON and a Markdown outline.

    PYTHONPATH=src python3 tools/parse_nanocom_emulator.py

Logic lives in ``d2diag.sniff.emulator_map`` (so it stays testable); this is a thin wrapper.
The raw emulator is Black Box Solutions' proprietary reference — only the derived tree is
committed (see references/nanocom/overview.md).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from d2diag.sniff.emulator_map import td5_tree, to_markdown  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(REPO, "captures", "nanocom", "emulator.json")
OUT_DIR = os.path.join(REPO, "references", "nanocom")


def main() -> int:
    if not os.path.exists(SRC):
        print(f"emulator JSON not found at {SRC}", file=sys.stderr)
        print("Put the emulator export under captures/nanocom/ (kept out of git).", file=sys.stderr)
        return 1
    tree = td5_tree(SRC)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "td5_menu_tree.json"), "w", encoding="utf-8") as fh:
        json.dump(tree, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    header = (
        "---\n"
        'title: "NanoCom emulator — Discovery 2 Td5 menu tree (generated)"\n'
        "area: references\n"
        "status: stable\n"
        "version: 1.0\n"
        "updated: 2026-10-02\n"
        "summary: >\n"
        "  Generated menu tree of the NanoCom Evolution emulator for the Discovery 2 Td5:\n"
        "  every module and its faults/inputs/outputs/settings/utility functions, with the\n"
        "  emulator page path and screen image for each leaf. Regenerate with\n"
        "  tools/parse_nanocom_emulator.py; do not hand-edit.\n"
        "---\n\n"
        "# NanoCom emulator — Discovery 2 Td5 menu tree (generated)\n\n"
        "Source: the NanoCom Evolution online emulator export (Black Box Solutions),\n"
        "kept out of git under `captures/nanocom/`. This is the authoritative list of **what\n"
        "functions the tool exposes per module**; the per-leaf field lists are transcribed in\n"
        "the per-module feature maps. Generated — do not hand-edit.\n\n"
    )
    with open(os.path.join(OUT_DIR, "td5_menu_tree.md"), "w", encoding="utf-8") as fh:
        fh.write(header + to_markdown(tree))
    print(f"Wrote td5_menu_tree.json + td5_menu_tree.md to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
