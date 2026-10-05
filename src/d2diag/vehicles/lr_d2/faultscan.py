"""Discovery 2 "read all fault codes": one reader per readable module (shared K-line bus).

Each reader takes the resolved serial port, establishes, reads the fault codes and always
releases (CONSTITUTION: the next module inits on the same bus). The platform
(:func:`d2diag.faultscan.read_all`) calls them in order, with a quiet gap in between.

Phase 0 Step 0: the bodies are copied verbatim from ``d2diag.faultscan._live_report``
(which still runs them until agent A makes ``read_all`` generic and deletes its copy).
``FAULTSCAN`` and ``UNIMPLEMENTED`` are the frozen names.
"""
from __future__ import annotations

from d2diag.pack import FaultReader


def read_td5(real_port: str) -> "list[str]":
    from d2diag.kline import KLine
    from d2diag.kwp2000 import KWP2000
    from d2diag.transport import SerialTransport

    from .td5 import Td5

    t = Td5(KWP2000(KLine(SerialTransport(real_port, timeout=1.0)), tolerant=True))
    t.open()
    try:
        t.establish()
        return list(t.read_faults())  # undecoded byte<off>.bit<n> faults included
    finally:
        t.release()  # close the session cleanly — the next module inits on the same bus


def read_slabs(real_port: str) -> "list[str]":
    from d2diag.kline import KLine
    from d2diag.kwp2000 import KWP2000
    from d2diag.transport import SerialTransport

    from .slabs import SLABS_ADDRESS, Slabs

    s = Slabs(KWP2000(KLine(SerialTransport(real_port, timeout=1.0), target=SLABS_ADDRESS),
                      tolerant=True))
    s.open()
    try:
        s.establish()
        f = s.read_faults()  # {"loggade":[…], "aktuella":[…]}  (logged / current)
        return [x + " (Logged)" for x in f.get("loggade", [])] + \
               [x + " (Current)" for x in f.get("aktuella", [])]
    finally:
        s.release()  # close the session cleanly — the next module inits on the same bus


def read_airbag(real_port: str) -> "list[str]":
    """Experimental and read-only by construction (no clear, no outputs, no security)."""
    from d2diag.kline import KLine
    from d2diag.kwp2000 import KWP2000
    from d2diag.transport import SerialTransport

    from .airbag import AIRBAG_ADDRESS, Airbag

    a = Airbag(KWP2000(KLine(SerialTransport(real_port, timeout=1.0), target=AIRBAG_ADDRESS),
                       tolerant=True, addressed=True))
    a.open()
    try:
        a.establish()
        return [f"{r['number']:03d}: {r['status_text']}" for r in a.read_faults()]
    finally:
        a.release()  # close the session cleanly — the next module inits on the same bus


FAULTSCAN: "tuple[FaultReader, ...]" = (
    FaultReader("TD5", read_td5),
    FaultReader("SLABS", read_slabs),
    FaultReader("Airbag", read_airbag, note="experimental",
                error_note="experimental (may need SecurityAccess we can't do)"),
)

# Modules that don't yet have a reading comms class (proprietary protocols).
# Step 0: referenced from d2diag.faultscan._UNIMPLEMENTED; agent A moves the data here.
def _unimplemented() -> "tuple[tuple[str, str], ...]":
    from d2diag import faultscan as _fs

    return tuple((name, note) for name, note in _fs._UNIMPLEMENTED)


UNIMPLEMENTED: "tuple[tuple[str, str], ...]" = _unimplemented()
