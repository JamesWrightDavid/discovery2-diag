"""BCU read-only auth-boundary scan (T-16): which input LIDs read WITHOUT SecurityAccess?

Reads each LID twice in shuffled order (the BCU init is flaky, so one time-ordered sweep
cannot tell gating from comms noise) and classifies the result:

* ``DATA`` — positive reply, identical on both passes.
* ``PLACEHOLDER`` — positive, but the same payload most other LIDs return (the BCU answers
  unauthenticated reads with a fixed ``11 99 07 01 …`` block, see ``bcu.py``).
* ``DENIED`` — ``7F 21 33`` securityAccessDenied: genuinely auth-gated.
* ``NRC xx`` — another negative (``31`` = LID not supported).
* ``NO-RESPONSE`` — nothing on either pass.
* ``INCONSISTENT`` — the passes disagree: comms-flaky, not a conclusion.

**Never** reads ``21 CC`` (EKA) and never sends SecurityAccess (``27``): the owner's brief
puts BCU EKA/security out of bounds. ``FORBIDDEN_LIDS`` is enforced here, not by convention.
"""
from __future__ import annotations

import random
from collections import Counter
from typing import Callable, Iterable

from ..kline.kline import KLineError
from ..kwp2000.kwp2000 import KWP2000Error, NegativeResponse

# 21 D8..E9 + 2C/2D: the factory tool's Read Inputs sweep (sniff 2026-08-09).
INPUT_LIDS = list(range(0xD8, 0xEA)) + [0x2C, 0x2D]
FORBIDDEN_LIDS = frozenset({0xCC})  # EKA — out of bounds, never read
NRC_SECURITY_DENIED = 0x33


def read_one(read: Callable[[int], bytes], lid: int) -> "tuple[str, str]":
    """One raw read → (kind, detail). ``read`` is ``Bcu.read_local``."""
    if lid in FORBIDDEN_LIDS:
        raise ValueError(f"LID 0x{lid:02X} is forbidden (EKA)")
    try:
        return "DATA", read(lid).hex(" ")
    except NegativeResponse as exc:
        if exc.nrc == NRC_SECURITY_DENIED:
            return "DENIED", "7f 21 33"
        return f"NRC {exc.nrc:02x}", ""
    except (KWP2000Error, KLineError):
        return "NO-RESPONSE", ""


def scan(read: Callable[[int], bytes], lids: "Iterable[int]" = INPUT_LIDS, *,
         passes: int = 2, rng: "random.Random | None" = None) -> "dict[int, tuple[str, str]]":
    """Read every LID ``passes`` times, shuffled per pass, and classify each."""
    lids = list(lids)
    bad = FORBIDDEN_LIDS.intersection(lids)
    if bad:
        raise ValueError(f"forbidden LIDs requested: {sorted(bad)}")
    rng = rng or random.Random()
    seen: "dict[int, list[tuple[str, str]]]" = {lid: [] for lid in lids}
    for _ in range(passes):
        order = lids[:]
        rng.shuffle(order)
        for lid in order:
            seen[lid].append(read_one(read, lid))
    out: "dict[int, tuple[str, str]]" = {}
    for lid, results in seen.items():
        if len(set(results)) > 1:
            out[lid] = ("INCONSISTENT", " | ".join(f"{k} {d}".strip() for k, d in results))
        else:
            out[lid] = results[0]
    # A payload most DATA LIDs share is the fixed unauthenticated placeholder, not data.
    payloads = Counter(d for k, d in out.values() if k == "DATA")
    if payloads:
        common, n = payloads.most_common(1)[0]
        if n >= 3 and n > len(out) // 2:
            out = {lid: ("PLACEHOLDER", d) if (k == "DATA" and d == common) else (k, d)
                   for lid, (k, d) in out.items()}
    return out


def moved(before: "dict[int, tuple[str, str]]",
          after: "dict[int, tuple[str, str]]") -> "dict[int, tuple[str, str]]":
    """LIDs whose DATA payload changed between two scans → {lid: (before, after)}."""
    return {lid: (before[lid][1], after[lid][1]) for lid in before
            if lid in after and before[lid][0] == after[lid][0] == "DATA"
            and before[lid][1] != after[lid][1]}
