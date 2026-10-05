"""Land Rover Discovery 2 Td5 vehicle pack (ADR-0013): ``PACK``.

Everything Discovery 2 specific lives under this package: the module layers
(``td5``, ``slabs``, ``bcu``, ``airbag``, ``ace``, ``autobox``), the signal and fault
stores (``signals/``, ``dtc/``), the demo data (``demo/``), the sniff importers
(``sniff/``) and the UI layout (``layout.json``). The platform reaches it only through
:func:`d2diag.pack.active_pack` (entry point ``ostler.vehicle`` → ``lr_d2``).

``PACK`` is assembled lazily on first access (module ``__getattr__``), so importing a
module layer such as ``d2diag.vehicles.lr_d2.td5`` never pulls in the menus, the command
registry or the web data sources. Integrator-owned (Phase 0 spec §7).

**Build rule:** building ``PACK`` must not import anything that reads a store at import
time. ``td5.identifiers`` calls ``load_signals("td5")`` on import, which asks the active
pack for ``signals_dir`` — so ``td5`` (and everything importing it: the menus, the
catalog, the web sources) is reached only through the lazy wrappers below (``_LazyMap``,
``_td5_keygen``, the ``sources``/``generate`` closures). ``d2diag.pack`` raises a clear
error if a build re-enters pack resolution.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]          # src/d2diag/vehicles/lr_d2 → repo root (uninstalled)

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
    from d2diag.pack import ModuleSpec

    # Order = display order (catalog module list, coverage-map picker, sources).
    return (
        ModuleSpec("td5", "TD5 (engine)", address=0x13, init="fast", keygen=_td5_keygen,
                   aliases=("motor",), live=True, fault_label="TD5"),
        ModuleSpec("slabs", "SLABS (ABS + air suspension)", address=0x29, init="fast",
                   live=True, fault_label="SLABS"),
        ModuleSpec("bcu", "BCU (body control)", address=0x40, init="slow", live=False,
                   fault_label="BCU"),
        ModuleSpec("ace", "ACE (active cornering)", init="none", live=False, fault_label="ACE"),
        ModuleSpec("autobox", "EAT (auto gearbox)", init="none", aliases=("eat", "gearbox"),
                   live=False, fault_label="Auto Gearbox"),
        ModuleSpec("airbag", "SRS (airbag)", address=0x5B, init="slow", live=False,
                   fault_label="Airbag"),
    )


def _docs():
    from d2diag.pack import DocSource

    agent_only = frozenset({"CLAUDE.md", "muki01_OBD2_K-line_Reader"})
    # The Docs tab mirrors the canonical source files. The test backlog first: it is what
    # you read on the phone while sitting in the car. The answer key lives in the sibling
    # register repo ('Discovery 2/'); `tools/dashboard.py --dict-path` replaces it.
    return (
        DocSource(REPO_ROOT / "references" / "test_plan.md", group="Test plan"),
        DocSource(REPO_ROOT.parent / "Discovery 2" / "discovery2_reference tool_fault_dictionary.md",
                  group="Answer key", title="reference tool fault-code dictionary (answer key)",
                  optional=True),
        DocSource(REPO_ROOT / "docs", group="Docs", recursive=True, exclude=agent_only),
        DocSource(REPO_ROOT / "references", group="Reference", recursive=True,
                  exclude=frozenset({"test_plan.md"}) | agent_only),
    )


def _build():
    from d2diag.pack import PACK_API_VERSION, DemoSpec, VehiclePack

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
        root=REPO_ROOT,
    )


def __getattr__(name: str):
    global _PACK
    if name == "PACK":
        if _PACK is None:
            _PACK = _build()
        return _PACK
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
