"""Pair labelled NanoCom fault screens with the raw fault frames in the same capture (T-30).

Marker convention (see ``specs/2026-10-04-fault-screen-import-design.md``)::

    >>> screen <module>/faults
    >>> value fault=<the fault line exactly as the tool shows it>     (one per line)
    >>> value fault=none                                              (empty screen)

For each fault screen this collects the latest raw fault reply seen since the screen marker
and judges every displayed line against it and against the fault store:

* **supported**: the displayed code's bit/number is set in the raw reply *and* the text
  agrees with the store name, so it can be promoted from ``candidate`` to ``proven``.
* **name proposal**: set in the raw reply, but the store has no name for it.
* **text conflict**: the text disagrees with the store name.
* **not in raw**: the displayed code's bit/number is absent from the raw reply.

Set bits/records that no displayed line explains are listed as leftovers. ACE and the EAT
gearbox have no raw decoder yet, so their raw replies are only kept beside the displayed
codes. Nothing here talks to the car.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher

from openostler.sniff import capture
from .importer import parse_marker

FAULT_VALUE = "fault"

# Words that name the *kind* of fault: the displayed text's ones must all appear in the
# store name, otherwise "open circuit" could agree with "short to ground".
_KIND_WORDS = {"open", "short", "ground", "battery", "supply", "high", "low", "temp",
               "load", "stuck", "missing", "invalid", "range", "corrupted", "fail",
               "failure", "long", "partial", "pre", "post"}
_SYNONYMS = {
    "temperature": "temp", "glowplug": "glow plug", "tacho": "tachometer",
    "overboosting": "over boosting", "underboosting": "under boosting",
    "pre-tensioner": "pretensioner", "pretensioners": "pretensioner",
    "drivers": "driver", "driver's": "driver", "passengers": "passenger",
    "lh": "left hand", "rh": "right hand", "left-hand": "left hand",
    "right-hand": "right hand", "dcv": "direction control valve",
    "directional": "direction", "electrical": "electric", "mechanic": "mechanical",
    "failed": "fail", "failure": "fail",
}
_STOP = {"the", "a", "an", "of", "in", "with", "has", "been", "is", "measures", "code",
         "fault", "circuit", "drive", "output", "detected", "problem", "signal", "s"}
_STATE = re.compile(r"\(\s*(logged(?: high| low)?|current|permanent|intermittent)\s*\)", re.I)


def _words(text: str) -> "list[str]":
    t = _STATE.sub(" ", text.lower())
    t = re.sub(r"[^a-z0-9' -]+", " ", t)
    out: "list[str]" = []
    for w in t.split():
        w = _SYNONYMS.get(w, w)
        out.extend(w.split())
    return [w for w in out if w not in _STOP and not w.isdigit()]


def state_word(text: str) -> str:
    """The tool's trailing state word, normalised (``logged high``, ``current`` …) or ``""``."""
    m = _STATE.findall(text)
    return m[-1].lower() if m else ""


def text_agrees(shown: str, stored: str) -> bool:
    """True if a displayed fault text means the same as a stored name.

    Normalised word containment (≥ 0.8 of the shorter side) or a close string match, and
    every fault-kind word in the displayed text must appear in the stored name.
    """
    a, b = _words(shown), _words(stored)
    if not a or not b:
        return False
    if not {w for w in a if w in _KIND_WORDS} <= set(b):
        return False
    sa, sb = set(a), set(b)
    contain = len(sa & sb) / min(len(sa), len(sb))
    ratio = SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()
    return contain >= 0.8 or ratio >= 0.85


# --------------------------------------------------------------------------- parsing ---

def parse_display(module: str, text: str) -> "dict":
    """Split one displayed fault line into its code and text. → ``{key, text, count}``.

    ``key`` is the store key the display points at (td5 ``off.bit``, airbag ``008``,
    autobox ``P1884`` (+ ``-NN`` when shown), ace ``04-02``), or ``""`` when the display
    carries no usable code (SLABS: its leading number is an occurrence count).
    """
    t = text.strip()
    out = {"key": "", "text": t, "count": None}
    if module == "td5":
        m = re.match(r"^\(?\s*(\d{1,2})\s*[,.\-]\s*(\d{1,2})\s*\)?\s*(.*)$", t)
        if m:
            x, y = int(m.group(1)), int(m.group(2))
            if 1 <= x <= 35 and 1 <= y <= 8:
                out.update(key=f"{x - 1}.{y - 1}", text=m.group(3).strip())
    elif module == "airbag":
        m = re.match(r"^(?:code\s*)?(\d{1,3})\s*[-:–,]?\s*(.*)$", t, re.I)
        if m:
            out.update(key=f"{int(m.group(1)):03d}", text=m.group(2).strip())
    elif module == "slabs":
        m = re.search(r"(?:intermittent\s*)?(\d+)\s*times", t, re.I)
        if m:
            out["count"] = int(m.group(1))
            t = (t[:m.start()] + t[m.end():]).strip(" .,(")
        t = re.sub(r"^\d{1,3}\s*-\s*\d{1,2}\s*[:.]?\s*", "", t)
        t = re.sub(r"\s*[.:]?\s*\d{1,3}\s*-\s*\d{1,2}\s*$", "", t)
        out["text"] = t.strip(" .")
    elif module == "autobox":
        m = re.match(r"^(?:code\s*)?(P[0-9A-F]{4})(?:\s*[- ]\s*(\d{1,2})\b)?\s*[-:]?\s*(.*)$",
                     t, re.I)
        if m:
            key = m.group(1).upper() + (f"-{int(m.group(2))}" if m.group(2) else "")
            out.update(key=key, text=m.group(3).strip())
    elif module == "ace":
        m = re.match(r"^(?:fault\s*)?(\d{1,3})\s*-\s*(\d{1,2})\s*[:.]?\s*(.*)$", t, re.I)
        if m:
            out.update(key=f"{int(m.group(1)):02d}-{int(m.group(2)):02d}",
                       text=m.group(3).strip())
    return out


def _set_bits(block: bytes, length: int) -> "list[str]":
    return [f"{off}.{bit}" for off, byte in enumerate(block[:length])
            for bit in range(8) if byte & (1 << bit)]


def _airbag_records(data: "list[int]") -> "bytes | None":
    """The record bytes of an addressed airbag ``61 02`` reply in a sniffed line, or None.

    Accepts ``[8n] F7 5B 61 02 …``; with a format byte the length is exact, otherwise the
    line's last byte is taken as the checksum.
    """
    for i in range(len(data) - 3):
        if data[i:i + 4] == [0xF7, 0x5B, 0x61, 0x02]:
            start = i + 4
            fmt = data[i - 1] if i > 0 else 0
            if fmt & 0xC0 == 0x80 and (fmt & 0x3F) >= 2:
                end = i + 2 + (fmt & 0x3F)
            else:
                end = len(data) - 1
            return bytes(data[start:end])
    return None


# ---------------------------------------------------------------------- collection ---

def collect_fault_screens(events) -> "list[dict]":
    """Every ``screen <module>/faults`` in a capture with its displayed lines and raw reply.

    → ``[{module, displayed: [str], raw: {...}}]``. ``raw`` holds, per module, the latest
    reply since the screen marker: td5 ``{"3b": bytes}``; slabs ``{"11"|"47": bytes}``;
    airbag ``{"02": bytes}``; autobox/ace ``{"lines": [hex …]}`` (undecoded).
    """
    screens: "list[dict]" = []
    cur: "dict | None" = None
    for _ms, kind, payload in events:
        if kind == "mark":
            mark = parse_marker(payload)
            if mark["kind"] == "screen":
                cur = None
                if mark["page"].lower().startswith("fault"):
                    cur = {"module": mark["module"], "displayed": [], "raw": {}}
                    screens.append(cur)
            elif mark["kind"] == "value" and cur is not None and mark["name"] == FAULT_VALUE:
                if mark["text"].strip().lower() != "none":
                    cur["displayed"].append(mark["text"])
            continue
        if cur is None:
            continue
        mod = cur["module"]
        if mod in ("td5", "slabs"):
            frames, _ = capture.split_frames(payload)
            for f in frames:
                p = f[1:-1]
                if len(p) >= 2 and p[0] == 0x61:
                    lid = f"{p[1]:02x}"
                    if (mod == "td5" and lid == "3b") or (mod == "slabs" and lid in ("11", "47")):
                        cur["raw"][lid] = bytes(p[2:])
        elif mod == "airbag":
            rec = _airbag_records(payload)
            if rec is not None:
                cur["raw"]["02"] = rec
        elif mod in ("autobox", "ace"):
            lead = 0x72 if mod == "autobox" else 0x67
            if lead in payload:
                cur["raw"].setdefault("lines", []).append(" ".join(f"{b:02x}" for b in payload))
    return screens


# ------------------------------------------------------------------------ evaluation ---

def _store_names(module: str) -> "dict[str, dict]":
    """``{key: {name, confidence}}`` for a module: decoder names first, then the dtc store."""
    from openostler import dtc

    out: "dict[str, dict]" = {}
    for k, m in dtc.load_meanings(module).items():
        out[k] = {"name": m.name, "confidence": m.confidence or "candidate"}
    if module == "td5":
        from ..td5.faults import FAULTS
        for f in FAULTS:
            out[f"{f.offset}.{f.mask.bit_length() - 1}"] = {"name": f.name,
                                                             "confidence": f.confidence}
    elif module == "slabs":
        from ..slabs.faults import SLABS_FAULT_BITS
        for (off, bit), text in SLABS_FAULT_BITS.items():
            out[f"{off}.{bit}"] = {"name": text, "confidence": "proven"}
    return out


def evaluate_screen(screen: "dict") -> "dict":
    """Judge one fault screen. → ``{module, rows, leftovers, raw_summary}``."""
    from ..td5.faults import FAULT_BLOCK_LEN as TD5_LEN
    from ..slabs.faults import FAULT_BLOCK_LEN as SLABS_LEN
    from ..airbag.faults import decode_faults as airbag_decode

    mod, raw = screen["module"], screen["raw"]
    names = _store_names(mod)
    rows: "list[dict]" = []
    raw_keys: "list[str] | None" = None
    if mod == "td5" and "3b" in raw:
        raw_keys = _set_bits(raw["3b"], TD5_LEN)
    elif mod == "slabs" and raw:
        raw_keys = sorted({k for blk in raw.values() for k in _set_bits(blk, SLABS_LEN)})
    elif mod == "airbag" and "02" in raw:
        raw_keys = [f"{r['number']:03d}" for r in airbag_decode(raw["02"])]

    explained: "set[str]" = set()
    for shown in screen["displayed"]:
        d = parse_display(mod, shown)
        row = {"shown": shown, "key": d["key"], "count": d["count"],
               "state": state_word(shown), "verdict": "", "stored": None}
        key = d["key"]
        if mod == "slabs":  # no usable code: find the stored name the text agrees with
            hits = [k for k, v in names.items() if text_agrees(d["text"], v["name"])]
            key = next((k for k in hits if raw_keys and k in raw_keys), hits[0] if hits else "")
            row["key"] = key
        stored = names.get(key) if key else None
        if mod == "autobox" and stored is None and key and "-" not in key:
            # display without the internal number: any row of that P-code may match
            fam = {k: v for k, v in names.items() if k.split("-")[0] == key}
            match = [k for k, v in fam.items() if text_agrees(d["text"], v["name"])]
            if match:
                key, stored = match[0], fam[match[0]]
                row["key"] = key
        row["stored"] = stored
        in_raw = None if raw_keys is None or not key else key in raw_keys
        if in_raw:
            explained.add(key)
        if in_raw is False:
            row["verdict"] = "not in raw"
        elif stored is None:
            row["verdict"] = "name proposal" if in_raw else "unknown code"
        elif text_agrees(d["text"], stored["name"]):
            # "supported" needs the raw reply too; ACE/EAT raw isn't decoded yet
            row["verdict"] = "supported" if in_raw else "text agrees"
        else:
            row["verdict"] = "text conflict"
        # Promotion needs raw proof; ACE/EAT have no raw decoder yet, so never promote them.
        row["promotable"] = (row["verdict"] == "supported" and bool(in_raw)
                             and stored is not None and stored["confidence"] != "proven")
        rows.append(row)
    leftovers = [k for k in (raw_keys or []) if k not in explained]
    return {"module": mod, "rows": rows, "leftovers": leftovers,
            "raw_keys": raw_keys, "raw_lines": raw.get("lines", [])}


def import_faults(path: str) -> "dict":
    """Evaluate every fault screen in a capture log. → ``{capture, screens}``."""
    import os
    events = capture.parse_log(path)
    return {"capture": os.path.basename(path),
            "screens": [evaluate_screen(s) for s in collect_fault_screens(events)]}


# ----------------------------------------------------------------------- write-back ---

_TABLE_MODULES = ("airbag", "autobox", "ace")


def promote_in_reference(module: str, key: str, capture_id: str, refs_dir) -> bool:
    """Flip one row of ``references/<module>_fault_codes.md`` from candidate to proven.

    Only for the table-backed modules (airbag/autobox/ace); the Td5 and SLABS decoders own
    their names, so those are edited by hand. Returns True if a row was changed.
    """
    from pathlib import Path
    if module not in _TABLE_MODULES:
        return False
    path = Path(refs_dir) / f"{module}_fault_codes.md"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = line.rstrip("\n").strip().strip("|").split("|")
        if len(cells) < 4 or cells[0].strip().strip("`") != key:
            continue
        if cells[2].strip() != "candidate":
            return False
        cells[2] = " proven "
        cells[3] = cells[3].rstrip() + f"; proven: nanocom:{capture_id} (T-30) "
        lines[i] = "|" + "|".join(cells) + "|\n"
        path.write_text("".join(lines), encoding="utf-8")
        return True
    return False


def render_fault_report(report: "dict") -> str:
    """Markdown report of :func:`import_faults`."""
    out = [f"# Fault screens — `{report['capture']}`", ""]
    if not report["screens"]:
        out.append("No fault screens found. Mark them with `s <module>/faults` and "
                   "`v fault=<as shown>`.")
        return "\n".join(out) + "\n"
    for sc in report["screens"]:
        mod = sc["module"]
        out.append(f"## {mod}")
        if sc["raw_keys"] is None and not sc["raw_lines"]:
            out.append("- ⚠️ no raw fault reply captured on this screen")
        elif sc["raw_keys"] is not None:
            out.append(f"- raw: {', '.join(sc['raw_keys']) or '(empty)'}")
        for line in sc["raw_lines"][-3:]:
            out.append(f"- raw (undecoded): `{line}`")
        for r in sc["rows"]:
            st = r["stored"]
            name = f" — store: “{st['name']}” ({st['confidence']})" if st else ""
            extra = f"; count {r['count']}" if r["count"] is not None else ""
            promo = " → **promotable**" if r["promotable"] else ""
            out.append(f"- `{r['key'] or '?'}` {r['verdict']}{promo}: “{r['shown']}”{name}{extra}")
            if r["promotable"] and mod in ("td5", "slabs"):
                out.append(f"  - edit by hand: set `{r['key']}` to proven in "
                           f"`src/d2diag/{mod}/faults.py`, citing this capture (T-30)")
        if sc["leftovers"]:
            out.append(f"- set in raw but not displayed: {', '.join(sc['leftovers'])}")
        out.append("")
    return "\n".join(out) + "\n"
