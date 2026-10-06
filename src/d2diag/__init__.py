"""Ostler pack for the Land Rover Discovery 2 (Td5): ``PACK`` (ADR-0013, ADR-0014).

This distribution (``d2diag``) is a vehicle pack for the Ostler platform
(``openostler``, https://github.com/openostler/ostler). Everything Discovery 2 specific
lives in this package: the module layers
(``td5``, ``slabs``, ``bcu``, ``airbag``, ``ace``, ``autobox``), the signal and fault
stores (``signals/``, ``dtc/``), the demo data (``demo/``), the sniff importers
(``sniff/``) and the UI layout (``layout.json``). The platform reaches it only through
:func:`openostler.pack.active_pack` (entry point ``openostler.vehicle`` → ``lr_d2`` →
``d2diag:PACK``); the pack must be installed, there is no built-in fallback.

``PACK`` is assembled lazily on first access (module ``__getattr__``), so importing a
module layer such as ``d2diag.td5`` never pulls in the menus, the command
registry or the web data sources. Integrator-owned (Phase 0 spec §7).

**Build rule:** building ``PACK`` must not import anything that reads a store at import
time. ``td5.identifiers`` calls ``load_signals("td5")`` on import, which asks the active
pack for ``signals_dir`` — so ``td5`` (and everything importing it: the menus, the
catalog, the web sources) is reached only through the lazy wrappers below (``_LazyMap``,
``_td5_keygen``, the ``sources``/``generate`` closures). ``openostler.pack`` raises a clear
error if a build re-enters pack resolution.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

__version__ = "0.1.0"

HERE = Path(__file__).resolve().parent
# src/d2diag → repo root. Only meaningful in a source checkout or an editable install; a
# wheel install has no repo around it (see _repo_root()).
REPO_ROOT = HERE.parents[1]

PACK_ID = "lr_d2"
PACK_NAME = "Land Rover Discovery 2 Td5"
DEFAULT_MODULE = "td5"

# Store modules whose signal store the admin mapper may write (was server._ALLOWED_MODULES).
WRITABLE_SIGNAL_MODULES = ("td5", "slabs", "airbag")
# Prefixes of module-command families (was server._MODULE_COMMAND_PREFIXES): an action like
# these that is not registered for the active module is refused as unknown.
MODULE_COMMAND_PREFIXES = ("output_", "injector_", "raise_", "lower_", "wheel_",
                           "bleed_", "pump_")

_PACK = None


class _LazyMap(Mapping):
    """A read-only mapping computed on first use (keeps store-reading imports out of the
    pack build)."""

    def __init__(self, load) -> None:
        self._load = load
        self._data = None

    def _d(self) -> Mapping:
        if self._data is None:
            self._data = self._load()
        return self._data

    def __getitem__(self, key):
        return self._d()[key]

    def __iter__(self):
        return iter(self._d())

    def __len__(self) -> int:
        return len(self._d())

    def __repr__(self) -> str:
        return f"_LazyMap({dict(self._d())!r})"


def _td5_keygen(seed_hi: int, seed_lo: int) -> bytes:
    """Td5 seed → key (``td5.keygen.key_bytes_from_seed``), imported on first use."""
    from .td5.keygen import key_bytes_from_seed

    return key_bytes_from_seed(seed_hi, seed_lo)


def _menus():
    from .menus import MENUS

    return MENUS


def _unlinked_ok():
    from .catalog_data import UNLINKED_OK

    return UNLINKED_OK


def _derived_fields():
    from .sources import DERIVED_FIELDS

    return DERIVED_FIELDS


def _generate(root: str) -> "list[str]":
    from .synth import generate

    return generate(root)


def _modules():
    from openostler.pack import ModuleSpec

    from .kline_profiles import KLINE

    # Order = display order (catalog module list, coverage-map picker, sources).
    # ``kline`` = the module's K-line profile overrides (kline_profiles.py).
    return (
        ModuleSpec("td5", "TD5 (engine)", address=0x13, init="fast", keygen=_td5_keygen,
                   aliases=("motor",), live=True, fault_label="TD5", kline=KLINE["td5"]),
        ModuleSpec("slabs", "SLABS (ABS + air suspension)", address=0x29, init="fast",
                   live=True, fault_label="SLABS", kline=KLINE["slabs"]),
        ModuleSpec("bcu", "BCU (body control)", address=0x40, init="slow", live=False,
                   fault_label="BCU", kline=KLINE["bcu"]),
        ModuleSpec("ace", "ACE (active cornering)", init="none", live=False, fault_label="ACE"),
        ModuleSpec("autobox", "EAT (auto gearbox)", init="none", aliases=("eat", "gearbox"),
                   live=False, fault_label="Auto Gearbox"),
        ModuleSpec("airbag", "SRS (airbag)", address=0x5B, init="slow", live=False,
                   fault_label="Airbag", kline=KLINE["airbag"]),
    )


def _repo_root() -> "Path | None":
    """The checkout root when this package runs from a source tree (editable install,
    ``PYTHONPATH=src``), else None: the docs are not shipped in the wheel."""
    if (REPO_ROOT / "pyproject.toml").is_file() and (REPO_ROOT / "references").is_dir():
        return REPO_ROOT
    return None


def _docs():
    from openostler.pack import DocSource

    root = _repo_root()
    if root is None:          # wheel install: the Docs tab shows no pack docs
        return ()
    agent_only = frozenset({"CLAUDE.md", "muki01_OBD2_K-line_Reader"})
    # The Docs tab mirrors the canonical source files. The test backlog first: it is what
    # you read on the phone while sitting in the car. The answer key lives in the sibling
    # register repo ('Discovery 2/'); the platform's
    # `tools/dashboard.py --dict-path` replaces it.
    return (
        DocSource(root / "references" / "test_plan.md", group="Test plan", optional=True),
        DocSource(root.parent / "Discovery 2" / "discovery2_reference tool_fault_dictionary.md",
                  group="Answer key", title="reference tool fault-code dictionary (answer key)",
                  optional=True),
        DocSource(root / "docs", group="Docs", recursive=True, exclude=agent_only,
                  optional=True),
        DocSource(root / "references", group="Reference", recursive=True,
                  exclude=frozenset({"test_plan.md"}) | agent_only, optional=True),
    )


def _build():
    from openostler.pack import PACK_API_VERSION, DemoSpec, VehiclePack

    from .actions import ACTIONS
    from .faultscan import FAULTSCAN, UNIMPLEMENTED
    from .sniff_spec import SNIFF

    modules = _modules()
    ids = tuple(m.id for m in modules)

    def sources(port, *, raw_log_dir=None, state_dir=None):
        from .sources import make_sources

        return make_sources(port, raw_log_dir=raw_log_dir, state_dir=state_dir, module_ids=ids)

    return VehiclePack(
        id=PACK_ID,
        name=PACK_NAME,
        api_version=PACK_API_VERSION,
        modules=modules,
        default_module=DEFAULT_MODULE,
        sources=sources,
        signals_dir=HERE / "signals",
        dtc_dir=HERE / "dtc",
        actions=ACTIONS,
        menus=_LazyMap(_menus),
        unlinked_ok=_LazyMap(_unlinked_ok),
        derived_fields=_LazyMap(_derived_fields),
        writable_signal_modules=WRITABLE_SIGNAL_MODULES,
        module_command_prefixes=MODULE_COMMAND_PREFIXES,
        faultscan=FAULTSCAN,
        faultscan_unimplemented=UNIMPLEMENTED,
        sniff=SNIFF,
        demo=DemoSpec(sessions_dir=HERE / "demo" / "sessions",
                      sniff_log=HERE / "demo" / "sniff-demo.txt", generate=_generate),
        docs=_docs(),
        layout=json.loads((HERE / "layout.json").read_text(encoding="utf-8")),
        root=_repo_root() or HERE,
    )


def __getattr__(name: str):
    global _PACK
    if name == "PACK":
        if _PACK is None:
            _PACK = _build()
        return _PACK
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
