"""Old import paths for the code that moved into the Discovery 2 pack (Phase 0, ADR-0013).

``d2diag.{td5,slabs,bcu,airbag,ace,autobox}[.*]``, ``d2diag.sniff.{library,emulator_map,
importer,fault_import}`` and ``d2diag.logbook.synth`` now live under
``d2diag.vehicles.lr_d2``. A meta-path finder maps each old name to the **same module
object** as the new one (never a copy), so ``monkeypatch`` works through either name and
nothing is executed twice. Installed once from ``d2diag/__init__.py``; deleted at the repo
split together with the old names' last importers.
"""
from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import sys

_NEW = "d2diag.vehicles.lr_d2"

# old name (prefix) → new name (prefix). A prefix also covers its submodules.
ALIASES = {
    **{f"d2diag.{p}": f"{_NEW}.{p}" for p in ("td5", "slabs", "bcu", "airbag", "ace", "autobox")},
    **{f"d2diag.sniff.{m}": f"{_NEW}.sniff.{m}"
       for m in ("library", "emulator_map", "importer", "fault_import")},
    "d2diag.logbook.synth": f"{_NEW}.synth",
}


def target_for(fullname: str) -> "str | None":
    """The new module name for an old one, or None if ``fullname`` is not aliased."""
    for old, new in ALIASES.items():
        if fullname == old or fullname.startswith(old + "."):
            return new + fullname[len(old):]
    return None


class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target: str) -> None:
        self._target = target
        self._real_spec = None

    def create_module(self, spec):
        module = importlib.import_module(self._target)
        self._real_spec = getattr(module, "__spec__", None)
        return module

    def exec_module(self, module) -> None:
        # The import system stamped the alias spec on the shared module: restore the real one.
        if self._real_spec is not None:
            module.__spec__ = self._real_spec


class AliasFinder(importlib.abc.MetaPathFinder):
    """Resolves an old D2 import path to the module under ``d2diag.vehicles.lr_d2``."""

    def find_spec(self, fullname, path=None, target=None):
        new = target_for(fullname)
        if new is None:
            return None
        if new not in sys.modules and importlib.util.find_spec(new) is None:
            return None
        return importlib.machinery.ModuleSpec(fullname, _AliasLoader(new))


def install() -> None:
    """Put the finder first on ``sys.meta_path`` (idempotent)."""
    if not any(isinstance(f, AliasFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, AliasFinder())
