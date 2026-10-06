"""tools/module_scan.py is Parked-only (platform spec K-line profiles §2, owner Q4): an init
sweep refuses to start without --confirm-parked or a "yes" at its prompt, and opens no port."""
import sys

import tools.module_scan as tool


def test_refuses_without_confirm_parked(monkeypatch, capsys):
    opened = []
    monkeypatch.setattr(tool, "SerialTransport", lambda *a, **k: opened.append(a))
    monkeypatch.setattr(tool, "EspTransport", lambda *a, **k: opened.append(a))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False, raising=False)
    assert tool.main(["/dev/null-port", "--esp"]) == 2
    assert opened == []
    assert "only when Parked" in capsys.readouterr().err


def test_confirmation():
    assert tool.confirm_parked(True, interactive=False) is True
    assert tool.confirm_parked(False, interactive=False) is False
    assert tool.confirm_parked(False, ask=lambda _q: "yes", interactive=True) is True
    assert tool.confirm_parked(False, ask=lambda _q: "", interactive=True) is False
