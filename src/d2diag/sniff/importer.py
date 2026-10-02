"""Turn a labelled NanoCom capture into signal-store candidate mappings.

The capture workflow (ADR-0005, ``references/nanocom_capture_protocol.md``) is: sniff the
NanoCom passively while typing structured markers into ``tools/esp32_read.py`` —

    >>> screen <module>/<page>      which module/screen we are now on
    >>> value <name>=<plaintext>    the value the tool is displaying right now

This module reads such a log and, per named value, gathers ``(plaintext, raws-by-LID)``
samples — the same shape :func:`d2diag.sniff.automap.solve` consumes — then runs the
existing auto-mapper to find the ``(lid, offset, type, scale)`` (numeric) or ``byte.bit``
(state) that produces the plaintext. Results are **candidate** mappings written back with
:func:`d2diag.signals.upsert_field`, the capture's name as provenance; nothing here sends
a byte to the car.

Anchoring follows ``tools/analyze_capture.py``: a ``value`` marker lands *in the middle*
of the screen's polling, so each value's raws are the latest ``61 <lid>`` response seen
for each LID since the current ``screen`` marker. Changing one physical input and typing a
fresh ``value`` gives a second sample, which is what locks scale and offset.
"""
from __future__ import annotations

import os

from ..signals import upsert_field
from . import capture
from .automap import solve


def parse_marker(text: str) -> "dict":
    """Interpret a marker's text. → ``{kind, …}``.

    ``screen <module>/<page>`` → ``{kind: 'screen', module, page}``;
    ``value <name>=<text>``   → ``{kind: 'value', name, text}``;
    anything else             → ``{kind: 'note', text}``.
    """
    t = text.strip()
    low = t.lower()
    if low.startswith("screen "):
        spec = t[len("screen "):].strip()
        module, _, page = spec.partition("/")
        return {"kind": "screen", "module": module.strip().lower(), "page": page.strip()}
    if low.startswith("value "):
        spec = t[len("value "):].strip()
        name, sep, val = spec.partition("=")
        if sep:
            return {"kind": "value", "name": name.strip(), "text": val.strip()}
    return {"kind": "note", "text": t}


def _lid_responses(data: "list[int]") -> "list[tuple[str, bytes]]":
    """Every ReadDataByLocalId response (``61 <lid> <data…>``) in a sniffed line.

    → ``[(lid_hex, data_bytes)]`` in the lowercase 2-hex form ``automap`` indexes by.
    """
    out: "list[tuple[str, bytes]]" = []
    frames, _ = capture.split_frames(data)
    for f in frames:
        payload = f[1:-1]
        if len(payload) >= 2 and payload[0] == 0x61:
            out.append((f"{payload[1]:02x}", bytes(payload[2:])))
    return out


def collect_samples(events) -> "dict":
    """Group labelled values into automap input.

    → ``{(module, name): {"samples": [{text, raws}], "lids": set[str], "unit": ""}}``.
    ``module`` is the current ``screen`` marker's module, or the live-tracked module if a
    value appears before any screen marker. ``lids`` is every LID polled on the screen(s)
    where the value was recorded (the automap candidate set).
    """
    from .modules import ModuleTracker

    out: "dict" = {}
    mt = ModuleTracker()
    screen_module: "str | None" = None
    latest: "dict[str, bytes]" = {}
    screen_lids: "set[str]" = set()

    for ms, kind, payload in events:
        if kind == "data":
            mt.feed(payload)
            for lid, raw in _lid_responses(payload):
                latest[lid] = raw
                screen_lids.add(lid)
            continue
        # kind == "mark"
        mark = parse_marker(payload)
        if mark["kind"] == "screen":
            screen_module = mark["module"] or None
            latest = {}          # a new screen polls its own LIDs — don't carry stale bytes
            screen_lids = set()
        elif mark["kind"] == "value":
            module = screen_module or mt.module or "unknown"
            key = (module, mark["name"])
            slot = out.setdefault(key, {"samples": [], "lids": set(), "unit": ""})
            slot["samples"].append({"text": mark["text"], "raws": dict(latest)})
            slot["lids"].update(screen_lids)
    return out


def _store_record(module: str, name: str, unit: str, res: "dict", capture_id: str) -> "dict":
    """Build a signal-store record from an automap result (candidate confidence)."""
    rec = {"name": name, "lid": res["lid"], "offset": int(res["offset"]),
           "unit": unit, "confidence": "candidate", "source": f"nanocom:{capture_id}"}
    if res["mode"] == "numeric":
        rec.update(kind=res["kind"], scale=float(res["scale"]), bias=float(res["bias"]))
    else:  # state: a byte or a single bit, with raw→label states
        bit = res.get("bit")
        rec["kind"] = "bit" if bit is not None else "u8"
        if bit is not None:
            rec["bit"] = int(bit)
        rec["states"] = {str(v): k for k, v in res.get("mapping", {}).items()}
    return rec


def import_capture(path: str, *, write: bool = False,
                   module_filter: "str | None" = None) -> "dict":
    """Map every labelled value in a capture. → a report dict.

    ``write`` persists each solved mapping as a *candidate* in the signal store.
    ``module_filter`` restricts to one module (store name, e.g. ``td5``). Nothing is sent
    to the car: this reads a log and writes JSON.
    """
    capture_id = os.path.basename(path)
    events = capture.parse_log(path)
    grouped = collect_samples(events)
    results: "list[dict]" = []
    for (module, name), slot in sorted(grouped.items()):
        if module_filter and module != module_filter:
            continue
        lids = sorted(slot["lids"])
        res = solve(slot["samples"], lids, name, slot["unit"])
        row = {"module": module, "name": name, "n_samples": len(slot["samples"]),
               "candidate_lids": lids, "result": res, "stored": False}
        if write and res.get("ok"):
            upsert_field(module, _store_record(module, name, slot["unit"], res, capture_id))
            row["stored"] = True
        results.append(row)
    return {"capture": capture_id, "written": bool(write), "mappings": results}


def render_report(report: "dict") -> str:
    """A human-readable markdown report of an :func:`import_capture` run."""
    lines = [f"# NanoCom capture import — `{report['capture']}`", ""]
    if report["written"]:
        lines.append("_Candidate mappings were written to the signal store._\n")
    if not report["mappings"]:
        lines.append("No labelled values found. Did the capture use `>>> value <name>=<text>`?")
        return "\n".join(lines) + "\n"
    for m in report["mappings"]:
        res = m["result"]
        head = f"## {m['module']} · {m['name']}  ({m['n_samples']} sample(s))"
        lines.append(head)
        if not res.get("ok"):
            lines.append(f"- ❌ no mapping: {res.get('error', 'unknown')}")
            lines.append(f"- candidate LIDs: {', '.join(m['candidate_lids']) or '(none)'}\n")
            continue
        if res["mode"] == "numeric":
            lines.append(
                f"- ✅ `21 {res['lid']}` @{res['offset']} {res['kind']} "
                f"× {res['scale']} + {res['bias']}  (R²={res['r2']:.4f}, {res['how']}"
                f"{', clean scale' if res.get('clean') else ''})")
        else:
            lines.append(f"- ✅ state: {res.get('rule', '')}")
        lines.append(f"- stored: {'yes (candidate)' if m['stored'] else 'no'}\n")
    return "\n".join(lines) + "\n"
