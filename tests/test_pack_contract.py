"""VehiclePack contract tests (ADR-0013): the installed pack resolves through the
``openostler.vehicle`` entry point and every member is consistent with the platform's
contract and with this pack's own module list.

Needs the pack installed (``pip install -e .``) next to the platform (``openostler``):
the platform has no built-in fallback, so an uninstalled pack fails here first.
"""
from __future__ import annotations

import json
import subprocess
import sys
from importlib import metadata

import pytest

from openostler import pack as platform_pack

import d2diag

GROUP = "openostler.vehicle"


def _eps():
    eps = metadata.entry_points()
    if hasattr(eps, "select"):
        return list(eps.select(group=GROUP))
    return list(eps.get(GROUP, []))  # Python 3.9


@pytest.fixture(scope="module")
def p():
    return d2diag.PACK


# ---- resolution -------------------------------------------------------------------------- #
def test_entry_point_is_registered_and_loads_the_pack(p):
    ours = [ep for ep in _eps() if ep.name == "lr_d2"]
    assert ours, f"no {GROUP!r} entry point named lr_d2: is the pack installed (pip install -e .)?"
    assert ours[0].value == "d2diag:PACK"
    assert ours[0].load() is p


def test_platform_resolves_this_pack(p):
    assert platform_pack.active_pack() is p


def test_api_version_matches_the_platform(p):
    assert p.api_version == platform_pack.PACK_API_VERSION
    assert isinstance(p, platform_pack.VehiclePack)


def test_import_is_lazy():
    """Importing the package must not build PACK or pull in the platform web layer."""
    code = ("import sys, d2diag; "
            "assert d2diag._PACK is None; "
            "assert not any(m.startswith('openostler.web') for m in sys.modules), "
            "sorted(m for m in sys.modules if m.startswith('openostler'))")
    subprocess.run([sys.executable, "-c", code], check=True)


# ---- manifest ---------------------------------------------------------------------------- #
def test_manifest_shape(p):
    m = p.manifest()
    assert set(m) == {"id", "name", "api_version", "default_module", "modules", "aliases",
                      "layout", "metrics"}
    assert m["id"] == "lr_d2" and m["api_version"] == platform_pack.PACK_API_VERSION
    assert m["default_module"] == "td5"
    for row in m["modules"]:
        assert set(row) == {"id", "name", "aliases", "live"}
        assert isinstance(row["live"], bool) and row["name"]
    assert [r["id"] for r in m["modules"]] == p.module_ids()
    json.dumps(m)  # the /pack body must be JSON


# ---- modules, ids and aliases -------------------------------------------------------------- #
def test_module_ids_unique_and_aliases_do_not_shadow_ids(p):
    ids = p.module_ids()
    assert len(ids) == len(set(ids))
    assert p.default_module in ids
    assert not set(p.aliases()) & set(ids)
    assert set(p.aliases().values()) <= set(ids)
    for m in p.modules:
        assert m.init in ("fast", "slow", "none"), m.id
        assert (m.address is None) == (m.init == "none"), m.id
        assert m.fault_label, m.id


def test_signal_and_dtc_stores_belong_to_known_modules(p):
    ids = set(p.module_ids())
    sig = {f.stem for f in p.signals_dir.glob("*.json")}
    dtc = {f.stem for f in p.dtc_dir.glob("*.json")}
    assert sig and sig <= ids, sig - ids
    assert dtc and dtc <= ids, dtc - ids
    # Every live module has a signal store; every module but the BCU has a fault store.
    assert {m.id for m in p.modules if m.live} <= sig
    assert ids - {"bcu"} <= dtc
    for f in list(p.signals_dir.glob("*.json")) + list(p.dtc_dir.glob("*.json")):
        assert isinstance(json.loads(f.read_text(encoding="utf-8")), list), f.name
    assert set(p.writable_signal_modules) <= ids


def test_actions_refer_to_known_modules(p):
    ids = set(p.module_ids())
    keys = [(c.module, c.action) for c in p.actions]
    assert len(keys) == len(set(keys)), "duplicate (module, action)"
    for c in p.actions:
        assert c.module in ids, (c.module, c.action)


def test_menus_and_data_maps_are_keyed_by_module_ids(p):
    ids = set(p.module_ids())
    assert set(p.menus) == ids
    assert set(p.derived_fields) <= ids
    assert set(p.unlinked_ok) <= ids


def test_faultscan_and_sniff_spec(p):
    ids = set(p.module_ids())
    labels = {m.fault_label for m in p.modules}
    for r in p.faultscan:
        assert r.label in labels and callable(r.read)
    s = p.sniff
    assert set(s.fast_init.values()) <= ids and set(s.slow_init.values()) <= ids
    for d in tuple(s.authoritative) + tuple(s.hints):
        assert d.module in ids and callable(d.match)
    assert set(s.importers) == {"nanocom", "fault_screen"}
    assert all(callable(f) for f in s.importers.values())


def test_sources_factory_follows_module_order(p):
    assert list(p.sources("auto")) == p.module_ids()


def test_demo_data_ships(p):
    assert p.demo is not None
    assert p.demo.sessions_dir.is_dir() and any(p.demo.sessions_dir.iterdir())
    assert p.demo.sniff_log is not None and p.demo.sniff_log.is_file()
    assert callable(p.demo.generate)


def test_docs_are_optional_sources(p):
    for d in p.docs:
        assert d.optional, d.path


# ---- layout.json -------------------------------------------------------------------------- #
def _platform_schema(name: str) -> dict:
    """A platform JSON Schema from its source checkout; skips on a wheel install."""
    from pathlib import Path

    import openostler

    path = Path(openostler.__file__).resolve().parents[2] / "schemas" / f"{name}.schema.json"
    if not path.is_file():
        pytest.skip("platform schema not available (wheel install)")
    return json.loads(path.read_text(encoding="utf-8"))


def test_layout_validates_against_the_platform_schema(p):
    jsonschema = pytest.importorskip("jsonschema")
    schema = _platform_schema("layout")
    v = jsonschema.Draft202012Validator(schema)
    assert [e.message for e in v.iter_errors(dict(p.layout))] == []


def test_layout_declares_the_driver_side_right(p):
    """The D2 is right-hand drive: the platform's rail goes on the right (UI spec §3.3)."""
    assert p.layout["driver_side"] == "right"
    jsonschema = pytest.importorskip("jsonschema")
    schema = _platform_schema("layout")
    if "driver_side" not in schema.get("properties", {}):
        pytest.skip("the installed platform's layout schema predates driver_side")
    v = jsonschema.Draft202012Validator(schema)
    assert list(v.iter_errors({"driver_side": p.layout["driver_side"]})) == []
    assert list(v.iter_errors({"driver_side": "centre"}))  # the schema really checks it


def test_layout_is_valid(p):
    raw = json.loads((p.signals_dir.parent / "layout.json").read_text(encoding="utf-8"))
    assert raw == dict(p.layout)
    ids = set(p.module_ids())
    assert isinstance(raw.get("group_order"), list)
    assert set(raw["drive"]) <= ids
    from openostler import signals

    for mid, view in raw["drive"].items():
        assert isinstance(view.get("kind"), str), mid
        known = {r["name"] for r in signals.load_records(mid)} if mid in {
            f.stem for f in p.signals_dir.glob("*.json")} else set()
        known |= set(p.derived_fields.get(mid, {}))
        for tile in view.get("tiles", []):
            assert tile["signal"] in known, (mid, tile["signal"])
