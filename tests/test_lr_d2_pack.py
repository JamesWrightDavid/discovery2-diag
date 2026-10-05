"""The Discovery 2 pack (d2diag:PACK) assembles, resolves as the active pack, and the
platform stores read from it."""
import pytest

from openostler import dtc, pack, signals


@pytest.fixture()
def lr_d2():
    from d2diag import PACK

    return PACK


def test_active_pack_is_the_lr_d2_pack(lr_d2):
    assert pack.active_pack() is lr_d2
    assert lr_d2.id == "lr_d2" and lr_d2.api_version == pack.PACK_API_VERSION


def test_canonical_ids_and_aliases(lr_d2):
    assert lr_d2.module_ids() == ["td5", "slabs", "bcu", "ace", "autobox", "airbag"]
    assert lr_d2.aliases() == {"motor": "td5", "eat": "autobox", "gearbox": "autobox"}
    assert lr_d2.default_module == "td5"
    assert lr_d2.canonical("motor") == "td5" and lr_d2.canonical("MOTOR") == "td5"
    assert lr_d2.canonical("gearbox") == "autobox"
    assert lr_d2.canonical("nope") == "nope" and lr_d2.canonical(None) is None
    assert lr_d2.module("eat").id == "autobox"


def test_pack_members_reference_the_live_objects(lr_d2):
    from openostler import commands, menus

    from d2diag.actions import ACTIONS

    assert lr_d2.actions is ACTIONS
    assert list(commands.registry().values()) == list(ACTIONS)
    assert dict(lr_d2.menus) == menus.MENUS
    assert set(lr_d2.derived_fields) == {"td5", "slabs"}
    assert [r.label for r in lr_d2.faultscan] == ["TD5", "SLABS", "Airbag"]
    assert lr_d2.sniff.fast_init == {0x13: "td5", 0x29: "slabs"}
    assert lr_d2.demo.sessions_dir.is_dir() and lr_d2.demo.sniff_log.is_file()
    assert (lr_d2.signals_dir / "td5.json").is_file() and (lr_d2.dtc_dir / "td5.json").is_file()
    assert lr_d2.module("td5").keygen(0x10, 0xE6) == bytes([0x90, 0x86])


def test_sources_factory_keys_follow_module_order(lr_d2):
    srcs = lr_d2.sources("auto")
    assert list(srcs) == lr_d2.module_ids()


def test_stores_read_from_the_pack(lr_d2):
    assert signals._dir() == lr_d2.signals_dir
    assert dtc._dir() == lr_d2.dtc_dir
    assert {r["name"] for r in signals.load_records("td5")}
    assert dtc.load_records("td5")
    assert pack.canonical_module("motor") == "td5"
