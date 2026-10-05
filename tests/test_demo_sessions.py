"""The committed synthetic demo sessions (ADR-0009, ADR-0010, ADR-0011): the pack's
``synth`` regenerates them byte for byte, and the platform store lists them as demo logs."""
import os

import pytest

from openostler.logbook.store import SessionStore

from d2diag import PACK
from d2diag.synth import DEMO_IDS, generate, generate_log1, generate_log2

DEMO1, DEMO2 = DEMO_IDS
DEMO_ROOT = str(PACK.demo.sessions_dir)


def test_demo_logs_are_synthetic_and_listed(tmp_path):
    store = SessionStore(str(tmp_path / "none"))
    pub = store.list(public=True)
    assert [m["id"] for m in pub] == [DEMO1, DEMO2]  # newest first
    assert [m["name"] for m in pub] == ["Demo log 1", "Demo log 2"]
    for m in pub:
        assert m["synthetic"] is True and m["source"] == "demo" and m["has_gps"] is True
        assert "synthetic" in m["description"] and len(m["description"]) <= 2000
        size = sum(os.path.getsize(os.path.join(DEMO_ROOT, m["id"], f))
                   for f in os.listdir(os.path.join(DEMO_ROOT, m["id"])))
        assert size < 600_000
    m1, m2 = pub
    assert 600 <= m1["duration_s"] <= 800 and m1["rows"] >= 3000
    assert 360 <= m2["duration_s"] <= 480 and m2["modules"] == ["slabs"]
    d = store.data(DEMO1, ["speed", "rpm"])
    assert d["decimated"] is True and d["track"] and len(d["track"]) <= 5000


def test_demo_logs_have_place_labels(tmp_path):
    store = SessionStore(str(tmp_path / "none"))
    m1, m2 = store.meta(DEMO1, public=True), store.meta(DEMO2, public=True)
    for m in (m1, m2):
        for k in ("place_start", "place_end", "place"):
            assert m[k]["source"] == "geonames" and m[k]["label"]
    assert m1["place"]["label"].endswith("Scotland")
    assert "Devon" in m2["place"]["label"]


def test_demo_log2_is_slabs_with_faults_heights_and_two_notes(tmp_path):
    store = SessionStore(str(tmp_path / "none"))
    notes = store.notes(DEMO2, public=True)
    assert len(notes) == 2 and store.meta(DEMO2)["note_count"] == 2
    d = store.data(DEMO2, ["height_left", "height_right", "wheel_speed_fr"],
                   max_points=100000)
    hl = [v for v in d["ch"]["height_left"] if v is not None]
    assert max(hl) - min(hl) >= 15  # the raise/lower test and the rough ground
    faults = {f for f in d["text"]["faults"] if f}
    assert any("wheel speed" in f for f in faults) and any("shuttle" in f for f in faults)
    ev = store.events(DEMO2, public=True)
    assert [e["action"] for e in ev if e["type"] == "command"] == ["raise_left", "lower_left"]
    assert any(e["type"] == "fault_watch" and e["on"] for e in ev)


@pytest.mark.parametrize("which", [0, 1])
def test_demo_generation_is_deterministic(tmp_path, which):
    fn = (generate_log1, generate_log2)[which]
    sid = fn(str(tmp_path / "a"))
    sid2 = fn(str(tmp_path / "b"))
    assert sid == sid2 == DEMO_IDS[which]
    files = sorted(os.listdir(tmp_path / "a" / sid))
    assert files == sorted(f for f in os.listdir(os.path.join(DEMO_ROOT, sid))
                           if not f.startswith("."))
    for f in files:
        a = (tmp_path / "a" / sid / f).read_bytes()
        assert a == (tmp_path / "b" / sid / f).read_bytes()
        assert a == open(os.path.join(DEMO_ROOT, sid, f), "rb").read(), \
            f"committed demo {sid}/{f} is stale: run tools/make_demo_session.py"


def test_generate_writes_both_demo_logs(tmp_path):
    assert generate(str(tmp_path)) == list(DEMO_IDS)
    assert sorted(os.listdir(tmp_path)) == sorted(DEMO_IDS)


