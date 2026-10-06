"""The Discovery 2 modules' K-line behaviour as profile data (platform spec K-line profiles
§1, migration step 2; ADR-0022 in the platform repo).

Each live-capable module declares the overrides that turn the platform's generic built-in
(``kwp2000_fast`` for a fast-init module, ``kwp2000_slow`` for a 5-baud one) into exactly
what the pack sends today. :data:`KLINE` feeds ``ModuleSpec.kline`` in ``d2diag.PACK``;
``ModuleSpec.kline_profile()`` adds ``init_address``/``target`` from the module address
and names the profile after the module. :func:`open_session` builds a module session
through ``KLine.from_profile`` / ``KWP2000.from_profile`` / ``EcuSession(profile=…)``.

Every value keeps the wire byte for byte as before the migration:

* ``source: 0xF7`` — the tester address the D2 has always used (the platform default is
  ``0xF1``). Td5 and SLABS init frames (``81 13 F7 81 0C``, ``81 29 F7 81 22``) and the
  airbag's addressed frames (``82 5B F7 …``) carry it.
* ``header``/``length`` — Td5, SLABS and BCU run unaddressed session frames with the length
  in the format byte; the airbag (TRW SPS) addresses every frame.
* ``pre_init_idle: 0.0`` — no idle inside the link before an init pulse, as before. The
  D2's own settle before the first attempt (Td5 5 s, SLABS 0.3 s) and its retry quiet
  periods (Td5 8 s, SLABS 28 s, airbag/BCU 2 s) stay in each layer's ``establish``: they
  run once per establish and between attempts, not before every init (spec §4.3, "D2
  profiles … keep their own idles").
* ``abandoned_idle: 0.0`` and ``timing.p3_min: 0.0`` — the platform's abandoned-session
  idle and P3min guard stay off until a car run says otherwise (``references/test_plan.md``).
* ``keepalive`` — Td5 and BCU send ``3E 01``; SLABS a bare ``3E`` (sniffed ``01 3E 3F``).
* ``confirm_address: "report"`` — the airbag and BCU 5-baud inits are read by the legacy
  ``slow_init`` path, which does not check the ``~address``; the profile states that
  (platform spec open question 5).

What stays pack code: the SLABS init-variant cycle (functional F1, functional F7, physical
F7), the ``1A 8A`` confirm and its 150 ms delay, the settle and retry sleeps above, the Td5
session + SecurityAccess, and the airbag ``10 81`` session.

ACE and the auto gearbox have no K-line profile (``init="none"``, proprietary framing).
"""
from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:  # pragma: no cover
    from openostler.kline.profiles import KLineProfile
    from openostler.session import EcuSession
    from openostler.transport.base import Transport

TESTER = 0xF7            # the D2 tester address (every capture since 2026-08-04)

# Shared by every D2 K-line module: the link idles and the P3 guard stay off (see above).
_HYGIENE: "dict[str, Any]" = {"pre_init_idle": 0.0, "abandoned_idle": 0.0,
                              "timing": {"p3_min": 0.0}}

# Td5 (0x13): fast init 81 13 F7 81 0C → C1, then unaddressed frames; keep-alive 3E 01.
TD5_KLINE: Mapping[str, Any] = MappingProxyType({
    "init_functional": False, "source": TESTER, "header": "none", "length": "format",
    "keepalive": b"\x3E\x01", **_HYGIENE})

# SLABS (0x29): fast init (the variant cycle is pack code), unaddressed frames, bare 3E
# about once a second (the DataSource's 1 Hz bus period).
SLABS_KLINE: Mapping[str, Any] = MappingProxyType({
    "init_functional": True, "source": TESTER, "header": "none", "length": "format",
    "keepalive": b"\x3E", "keepalive_interval": 1.0, **_HYGIENE})

# BCU (0x40): 5-baud init (key bytes E5 8F), unaddressed frames, keep-alive 3E 01
# (sniffed 02 3E 01 41).
BCU_KLINE: Mapping[str, Any] = MappingProxyType({
    "source": TESTER, "header": "none", "length": "format", "keepalive": b"\x3E\x01",
    "confirm_address": "report", **_HYGIENE})

# Airbag (0x5B): 5-baud init (key bytes E9 8F), addressed frames 8x 5B F7 on every message.
AIRBAG_KLINE: Mapping[str, Any] = MappingProxyType({
    "source": TESTER, "header": "physical", "length": "format",
    "confirm_address": "report", **_HYGIENE})

# Module id → ``ModuleSpec.kline``.
KLINE: Mapping[str, Mapping[str, Any]] = MappingProxyType({
    "td5": TD5_KLINE, "slabs": SLABS_KLINE, "bcu": BCU_KLINE, "airbag": AIRBAG_KLINE})


def profile(module_id: str) -> "KLineProfile":
    """The resolved K-line profile of a D2 module (``ModuleSpec.kline_profile()``).

    Built from the pack's module list without building the whole ``PACK``. Raises
    ``KeyError`` for a module without a K-line profile."""
    from . import _modules

    for m in _modules():
        if m.id == module_id:
            p = m.kline_profile()
            if p is not None:
                return p
            break
    raise KeyError(f"no K-line profile for D2 module {module_id!r}")


def open_session(module_id: str, transport: "Transport") -> "EcuSession":
    """A module session on ``transport``, built from the module's profile:
    ``Td5``/``Slabs``/``Bcu``/``Airbag`` over ``KWP2000.from_profile(KLine.from_profile(…))``.
    Not opened, not established."""
    from openostler.kline import KLine
    from openostler.kwp2000 import KWP2000

    p = profile(module_id)
    kwp = KWP2000.from_profile(KLine.from_profile(transport, p), p)
    if module_id == "td5":
        from .td5 import Td5 as cls
    elif module_id == "slabs":
        from .slabs import Slabs as cls
    elif module_id == "bcu":
        from .bcu import Bcu as cls
    elif module_id == "airbag":
        from .airbag import Airbag as cls
    else:  # pragma: no cover — profile() already refused it
        raise KeyError(module_id)
    # Same as cls(kwp, profile=p) (EcuSession.__init__ only stores it); set afterwards so a
    # test double standing in for a layer class may take just the KWP2000.
    session = cls(kwp)
    session.profile = p
    return session


__all__ = ["TESTER", "TD5_KLINE", "SLABS_KLINE", "BCU_KLINE", "AIRBAG_KLINE", "KLINE",
           "profile", "open_session"]
