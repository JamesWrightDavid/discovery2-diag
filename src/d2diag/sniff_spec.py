"""Discovery 2 sniff detection: diagnostic addresses and framing detectors (``SNIFF``).

The platform (:mod:`openostler.sniff.modules`) tags a sniffed byte line with the module it
belongs to from this spec. The Discovery 2 buses the NanoCom touches:

- **Fast init** — addressed StartCommunication ``81 <addr> F7 81`` (Td5 ``0x13``,
  SLABS ``0x29``). An init to an address we do not recognise is tagged
  ``unknown:0xNN`` by the platform rather than dropped (cruise, HEVAC, IDM, the ``0x18``
  responder).
- **Addressed modules** — the airbag (TRW SPS, ``0x5B``) keeps ISO 14230 addressed
  framing for every message (``82 5B F7 …`` request, ``F7 5B …`` response), unlike
  the unaddressed session frames Td5/SLABS/BCU switch to. Authoritative.
- **EAT autobox** — the Bosch gearbox speaks a proprietary ``72``-framed protocol
  with an XOR checksum (request), and a ``72 <len> 60 …`` response marker. A hint.
- **ACE** — the Lucas roll-control streams bulk blocks whose leading bytes come in
  pairs (``67 67``, ``04 04``, ``07 07`` …). A hint.
- **BCU** — the Valeo body unit runs the same unaddressed KWP framing as Td5/SLABS
  (so its 5-baud slow init is invisible in a hex log), but the EKA identifier
  ``21 CC`` / ``3B CC`` is unique to it and gives a conservative signal. A hint.

The protocol facts are drawn from ``references/protocol_state_handoff.md`` and
``sniff/library.py`` (the ``KNOWN`` facts). Detector ``how`` strings are part of the
:func:`openostler.sniff.modules.scan` output.
"""
from __future__ import annotations

from openostler.pack import Detector, SniffSpec

TESTER = 0xF7  # tester source address the NanoCom/our tools use (0xF7)

# Diagnostic addresses we have a name for. Fast- and slow-init modules share the name map.
FAST_INIT_ADDRESSES = {0x13: "td5", 0x29: "slabs"}
SLOW_INIT_ADDRESSES = {0x40: "bcu", 0x5B: "airbag"}

# ACE bulk blocks lead with a doubled byte (protocol, not a sampling artefact — see
# protocol_state_handoff.md). These pairs are distinctive enough to tag the stream.
_ACE_PAIRS = {(0x67, 0x67), (0x04, 0x04), (0x07, 0x07), (0xE0, 0xE0), (0xF0, 0xF0)}

# BCU EKA identifier — no other module uses 0xCC, so `21 CC`/`3B CC` means BCU.
_BCU_EKA = {(0x21, 0xCC), (0x3B, 0xCC)}


def _find(seq: "list[int]", sub: "tuple[int, ...]") -> int:
    """Index of the first occurrence of ``sub`` in ``seq``, or -1."""
    n = len(sub)
    for i in range(len(seq) - n + 1):
        if tuple(seq[i : i + n]) == sub:
            return i
    return -1


def _airbag_signal(b: "list[int]") -> bool:
    """Addressed framing at 0x5B: request ``82 5B F7`` or response ``F7 5B``."""
    return _find(b, (0x82, 0x5B, TESTER)) >= 0 or _find(b, (TESTER, 0x5B)) >= 0


def _eat_signal(b: "list[int]") -> bool:
    """EAT autobox `72` framing: an XOR-closed request, or a `72 <len> 60` response.

    A request is ``72 <bytes…> <cs>`` where ``cs`` is the XOR of everything before it
    (verified against ``72 05 04 00 73`` and ``72 04 05 73``). The response marker is
    ``72 <len> 60 …`` (the ``60`` byte), whose trailing checksum is not XOR and is not
    validated here — the ``60`` at offset +2 is signal enough.
    """
    n = len(b)
    for i in range(n):
        if b[i] != 0x72:
            continue
        if i + 2 < n and b[i + 2] == 0x60:  # response marker `72 <len> 60 …`
            return True
        # XOR-closed request: find a window 72..cs whose running XOR hits zero.
        acc = 0
        for j in range(i, min(n, i + 16)):
            acc ^= b[j]
            if j > i + 1 and acc == 0:  # at least 72 <b> <cs>
                return True
    return False


def _ace_signal(b: "list[int]") -> bool:
    return any(_find(b, pair) >= 0 for pair in _ACE_PAIRS)


def _bcu_signal(b: "list[int]") -> bool:
    return any(_find(b, pair) >= 0 for pair in _BCU_EKA)


def _nanocom(path: str, **kw):
    from .sniff.importer import import_capture

    return import_capture(path, **kw)


def _fault_screen(path: str):
    from .sniff.fault_import import import_faults

    return import_faults(path)


SNIFF = SniffSpec(
    fast_init=dict(FAST_INIT_ADDRESSES),
    slow_init=dict(SLOW_INIT_ADDRESSES),
    extra_scan=(0x18, 0x5A),                   # the 0x18 responder, and 0x5A
    authoritative=(Detector("airbag", "addressed 0x5b", _airbag_signal),),
    hints=(  # order = check order: the first matching hint seeds the module
        Detector("autobox", "72-framed", _eat_signal),
        Detector("ace", "bulk pairs", _ace_signal),
        Detector("bcu", "eka 21/3b cc", _bcu_signal),
    ),
    tester=TESTER,
    importers={"nanocom": _nanocom, "fault_screen": _fault_screen},
)
