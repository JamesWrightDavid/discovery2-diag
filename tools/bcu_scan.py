"""BCU read-only input scan (T-16) — does the BCU give live inputs WITHOUT SecurityAccess?

    PYTHONPATH=src python3 tools/bcu_scan.py --serial auto                 # one scan, table
    PYTHONPATH=src python3 tools/bcu_scan.py --serial auto --serve CMD --out OUT.jsonl

Ignition cycle first (off → on) so the BCU enters diagnostic mode. One-shot mode inits,
scans ``21 D8..E9, 2C, 2D`` twice in shuffled order (``d2diag.bcu.scan``), prints the
classification and releases. ``--serve`` holds ONE session (re-inits are flaky on the BCU):
it keeps it alive with ``3E 01`` and, for every line appended to the CMD file, runs a scan
labelled with that line and appends a JSON record to OUT (``quit`` releases and exits).
That is the differential workflow: baseline, change one input, scan again, compare.

Read-only by construction: only 5-baud init, ``3E 01``, ``21 xx`` reads and ``82``.
Never ``21 CC`` (EKA) and never SecurityAccess — enforced in ``d2diag.bcu.scan``.
Raw TX/RX goes to ``logs/raw-bcu-<time>.log`` (gitignored).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from d2diag.bcu.bcu import BCU_ADDRESS, Bcu  # noqa: E402
from d2diag.bcu.scan import INPUT_LIDS, moved, scan  # noqa: E402
from openostler.kline import KLine  # noqa: E402
from openostler.kwp2000 import KWP2000  # noqa: E402
from openostler.ports import resolve_serial_port  # noqa: E402
from openostler.transport import SerialTransport  # noqa: E402
from openostler.transport.logging_transport import LoggingTransport  # noqa: E402

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def _table(res) -> str:
    return "\n".join(f"  21 {lid:02X}  {kind:<13} {detail}" for lid, (kind, detail) in res.items())


def _record(label, res, base) -> dict:
    return {"time": time.strftime("%H:%M:%S"), "label": label,
            "lids": {f"{lid:02x}": [k, d] for lid, (k, d) in res.items()},
            "moved_vs_first": {f"{lid:02x}": list(v) for lid, v in moved(base, res).items()}
            if base else {}}


def main() -> int:
    ap = argparse.ArgumentParser(description="BCU read-only input scan (T-16)")
    ap.add_argument("--serial", default="auto")
    ap.add_argument("--serve", metavar="CMD", help="command file to watch (one label per line)")
    ap.add_argument("--out", metavar="OUT", help="JSONL results file (with --serve)")
    args = ap.parse_args()

    log = os.path.join(_ROOT, "logs", time.strftime("raw-bcu-%Y%m%d-%H%M%S.log"))
    t = LoggingTransport(SerialTransport(resolve_serial_port(args.serial), timeout=1.0), log)
    bcu = Bcu(KWP2000(KLine(t, target=BCU_ADDRESS), tolerant=True))
    bcu.open()
    try:
        kw = bcu.establish(progress=lambda m: print("  ·", m, flush=True))
        print(f"BCU keybytes {kw[0]:02X} {kw[1]:02X}", flush=True)
        if not args.serve:
            print(_table(scan(bcu.read_local, INPUT_LIDS)))
            return 0
        open(args.serve, "a").close()
        pos, base, last_tp = os.path.getsize(args.serve), None, time.monotonic()
        print(f"serving: append a label line to {args.serve}; 'quit' to release", flush=True)
        while True:
            with open(args.serve) as fh:
                fh.seek(pos)
                lines = fh.read().splitlines()
                pos = fh.tell()
            for label in (x.strip() for x in lines):
                if not label:
                    continue
                if label == "quit":
                    return 0
                res = scan(bcu.read_local, INPUT_LIDS)
                base = base or res
                with open(args.out, "a") as out:
                    out.write(json.dumps(_record(label, res, base)) + "\n")
                print(f"[{label}] scanned {len(res)} LIDs", flush=True)
                last_tp = time.monotonic()
            if time.monotonic() - last_tp > 1.5:
                try:
                    bcu.tester_present()
                except Exception as exc:  # noqa: BLE001 — note it; a scan will show the state
                    print("keepalive failed:", type(exc).__name__, exc, flush=True)
                last_tp = time.monotonic()
            time.sleep(0.2)
    finally:
        bcu.release()
        print("released; raw log:", log, flush=True)


if __name__ == "__main__":
    sys.exit(main())
