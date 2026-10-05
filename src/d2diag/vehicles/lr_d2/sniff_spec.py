"""Discovery 2 sniff detection: diagnostic addresses and framing detectors.

Phase 0 Step 0 stub: references the maps and predicates still in
:mod:`d2diag.sniff.modules`. Agent A moves the address maps and the ``_airbag/_eat/_ace/
_bcu`` predicates here; ``SNIFF`` (a :class:`d2diag.pack.SniffSpec`) is the frozen name.
Detector ``how`` strings match :func:`d2diag.sniff.modules.scan` output exactly.
"""
from __future__ import annotations

from d2diag.pack import Detector, SniffSpec
from d2diag.sniff import modules as _m


def _nanocom(path: str, **kw):
    from .sniff.importer import import_capture

    return import_capture(path, **kw)


def _fault_screen(path: str):
    from .sniff.fault_import import import_faults

    return import_faults(path)


SNIFF = SniffSpec(
    fast_init=dict(_m.FAST_INIT_ADDRESSES),
    slow_init=dict(_m.SLOW_INIT_ADDRESSES),
    extra_scan=(0x18, 0x5A),                   # the 0x18 responder, and 0x5A
    authoritative=(Detector("airbag", "addressed 0x5b", _m._airbag_signal),),
    hints=(
        Detector("autobox", "72-framed", _m._eat_signal),
        Detector("ace", "bulk pairs", _m._ace_signal),
        Detector("bcu", "eka 21/3b cc", _m._bcu_signal),
    ),
    tester=_m.TESTER,
    importers={"nanocom": _nanocom, "fault_screen": _fault_screen},
)
