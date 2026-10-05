"""Discovery 2 "read all fault codes": one reader per readable module (shared K-line bus).

Each reader takes the resolved serial port, establishes, reads the fault codes and always
releases (CONSTITUTION: the next module inits on the same bus). The platform
(:func:`openostler.faultscan.read_all`) calls them in order, with a quiet gap in between.

TD5 and SLABS are proven and tested. Airbag (0x5B) is **experimental** (read-only,
unverified live). ACE/EAT/BCU have no comms class → listed in ``UNIMPLEMENTED``.
"""
from __future__ import annotations

from openostler.pack import FaultReader


def read_td5(real_port: str) -> "list[str]":
    from openostler.kline import KLine
    from openostler.kwp2000 import KWP2000
    from openostler.transport import SerialTransport

    from .td5 import Td5

    t = Td5(KWP2000(KLine(SerialTransport(real_port, timeout=1.0)), tolerant=True))
    t.open()
    try:
        t.establish()
        return list(t.read_faults())  # undecoded byte<off>.bit<n> faults included
    finally:
        t.release()  # close the session cleanly — the next module inits on the same bus


def read_slabs(real_port: str) -> "list[str]":
    from openostler.kline import KLine
    from openostler.kwp2000 import KWP2000
    from openostler.transport import SerialTransport

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
    from openostler.kline import KLine
    from openostler.kwp2000 import KWP2000
    from openostler.transport import SerialTransport

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
UNIMPLEMENTED: "tuple[tuple[str, str], ...]" = (
    ("ACE", "active suspension — proprietary bulk protocol, not read in code yet"),
    ("Auto Gearbox", "EAT 72-framed — ECU responds but decoding not finished"),
    ("BCU", "Valeo — no fault-code list in code yet"),
)
