"""The D2 modules' K-line profiles (platform spec K-line profiles §1, migration step 2).

The profile-built sessions (``d2diag.kline_profiles.open_session``) must put the same bytes
on the wire, with the same sleeps, as the legacy constructors they replace. Each case runs
the same establish → reads → keep-alive → release against a generic fake ECU twice, once
per construction, and compares every sent frame and every sleep."""
import json
from pathlib import Path

import pytest

from d2diag import PACK
from d2diag.airbag import AIRBAG_ADDRESS, Airbag
from d2diag.bcu import BCU_ADDRESS, Bcu
from d2diag.kline_profiles import KLINE, TESTER, open_session, profile
from d2diag.slabs import SLABS_ADDRESS, Slabs
from d2diag.td5 import Td5
from openostler.kline import KLine, encode
from openostler.kline.frame import decode
from openostler.kwp2000 import KWP2000
from tests.fakes import FakeKLineEcu


class _AnyEcu(FakeKLineEcu):
    """Answers every decodable request positively (C1 57 8F to an init, C2 to 82,
    a seed to 27 01, 16 data bytes to 21 xx); ``silent_inits`` inits go unanswered.
    Replies are addressed when the request was."""

    def __init__(self, silent_inits: int = 0) -> None:
        super().__init__()
        self.silent_inits = silent_inits
        self.slow_inits: "list[int]" = []

    def send(self, data: bytes) -> int:
        data = bytes(data)
        self.sent.append(data)
        self._rx.extend(data)
        try:
            d = decode(data).data
        except Exception:  # noqa: BLE001 — not a whole frame
            return len(data)
        if d[:1] == b"\x81":
            if self.silent_inits > 0:
                self.silent_inits -= 1
                return len(data)
            rep = b"\xc1\x57\x8f"
        elif d[:1] == b"\x82":
            rep = b"\xc2"
        elif d[:2] == b"\x27\x01":
            rep = b"\x67\x01\x12\x34"
        elif d[:1] == b"\x21":
            rep = b"\x61" + d[1:2] + bytes(range(16))
        else:
            rep = bytes([d[0] | 0x40]) + d[1:2]
        addressed = bool(data[0] & 0x80)
        self._rx.extend(encode(rep, TESTER, data[1] if addressed else 0x13,
                               addressed=addressed))
        return len(data)

    def slow_init(self, address: int) -> bytes:
        self.slow_inits.append(address)
        if self.silent_inits > 0:
            self.silent_inits -= 1
            return b""
        return b"\x55\xe9\x8f"


def _legacy(mid: str, ecu):
    if mid == "td5":
        return Td5(KWP2000(KLine(ecu), tolerant=True))
    if mid == "slabs":
        return Slabs(KWP2000(KLine(ecu, target=SLABS_ADDRESS), tolerant=True))
    if mid == "bcu":
        return Bcu(KWP2000(KLine(ecu, target=BCU_ADDRESS), tolerant=True))
    return Airbag(KWP2000(KLine(ecu, target=AIRBAG_ADDRESS), tolerant=True, addressed=True))


def _exercise(mid: str, session, sleeps: list):
    sleep = sleeps.append
    session.open()
    try:
        session.establish(sleep=sleep)
        session.read_local(0x1C)
        session.tester_present()
    except Exception as exc:  # noqa: BLE001 — the failure path must match too
        sleeps.append(type(exc).__name__)
    finally:
        session.release()


@pytest.mark.parametrize("silent", [0, 1, 99])
@pytest.mark.parametrize("mid", ["td5", "slabs", "bcu", "airbag"])
def test_profile_session_sends_the_same_bytes_and_sleeps(mid, silent):
    runs = []
    for build in (_legacy, open_session):
        ecu, sleeps = _AnyEcu(silent), []
        _exercise(mid, build(mid, ecu), sleeps)
        runs.append((ecu.sent, ecu.slow_inits, sleeps))
    assert runs[0] == runs[1]
    assert runs[0][0]                                   # something went out


def test_init_frames_on_the_wire():
    ecu = _AnyEcu()
    open_session("td5", ecu).establish(sleep=lambda s: None)
    assert bytes.fromhex("8113F7810C") in ecu.sent      # 81 13 F7 81 0C
    ecu = _AnyEcu()
    s = open_session("slabs", ecu)
    s.establish(sleep=lambda s: None)
    assert ecu.sent[1] == encode(b"\x81", 0x29, 0xF1, addressed=True, functional=True)
    ecu = _AnyEcu()
    open_session("airbag", ecu).establish(sleep=lambda s: None)
    assert ecu.slow_inits == [0x5B]
    assert ecu.sent[-1][:3] == bytes.fromhex("825BF7")  # addressed 10 81 from F7


def test_slabs_keepalive_is_the_profiles_bare_3e():
    ecu = _AnyEcu()
    open_session("slabs", ecu).tester_present()
    assert ecu.sent == [bytes.fromhex("013E3F")]
    ecu = _AnyEcu()
    open_session("td5", ecu).tester_present()
    assert ecu.sent == [bytes.fromhex("023E0141")]


def test_profiles_resolve_with_the_d2_values():
    want = {"td5": (0x13, "fast", False), "slabs": (0x29, "fast", False),
            "bcu": (0x40, "5baud", False), "airbag": (0x5B, "5baud", True)}
    for mid, (addr, init, addressed) in want.items():
        p = profile(mid)
        assert p.name == mid and p.framing == "kwp2000" and p.init == init
        assert p.init_address == p.target == addr and p.source == 0xF7
        assert p.addressed is addressed and p.length == "format" and p.tolerant
        assert p.baud == 10400 and p.parity == "N" and p.release == b"\x82"
        assert p.idle_before_init == 0.0 and p.idle_after_abandoned == 0.0
        assert p.timing.p3_min == 0.0 and p.timing.p4 == 0.0
        assert p.timing.reply_timeout == 1.0 and p.init_low == p.init_high == 0.025
    assert profile("td5").keepalive == b"\x3E\x01" and not profile("td5").init_functional
    assert profile("slabs").keepalive == b"\x3E" and profile("slabs").keepalive_interval == 1.0
    assert profile("bcu").confirm_address == profile("airbag").confirm_address == "report"


def test_pack_modules_carry_the_overrides():
    by_id = {m.id: m for m in PACK.modules}
    for mid, overrides in KLINE.items():
        assert dict(by_id[mid].kline) == dict(overrides)
        assert by_id[mid].kline_profile() == profile(mid)
    for mid in ("ace", "autobox"):
        assert by_id[mid].kline_profile() is None
    with pytest.raises(KeyError):
        profile("ace")


def test_overrides_validate_against_the_platform_schema():
    jsonschema = pytest.importorskip("jsonschema")
    import openostler

    schema_path = (Path(openostler.__file__).resolve().parents[2] / "schemas"
                   / "kline-profile.schema.json")
    if not schema_path.is_file():
        pytest.skip("platform schema not available (wheel install)")
    v = jsonschema.Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
    for mid, overrides in KLINE.items():
        doc = {k: (val.hex(" ").upper() if isinstance(val, bytes) else val)
               for k, val in overrides.items()}
        assert list(v.iter_errors(doc)) == [], mid
