"""Deterministic synthetic demo drive written through ``SessionRecorder`` (ADR-0009).

``generate(root)`` writes one ~12-minute session at 5 Hz with a fake clock: GPS from the
parametric loop in ``gps.route`` (empty moorland, not a road), and engine channels that
follow the speed — rpm from speed and gear, coolant warm-up, boost from load, battery
charging. Same inputs → byte-identical files. Run it via ``tools/make_demo_session.py``.
"""
from __future__ import annotations

import calendar
import math
import os
import re
import shutil

from ..gps.nmea import Fix
from ..gps.route import PERIOD_S, demo_route, speed_at
from .recorder import SessionRecorder

START_UTC = (2026, 10, 5, 9, 0, 0)  # fixed, so the id is stable: 20261005T090000Z
HZ = 5
IDLE_RPM = 760
TYRE_CIRC_M = 2.43           # 235/70 R16
GEARS = (3.69, 2.13, 1.40, 1.00, 0.77)  # R380 box
FINAL = 3.54
_UP_KMH = (16, 30, 48, 66)  # change up above these speeds

UNITS = {"rpm": "rpm", "speed": "km/h", "coolant_temp": "°C", "air_temp": "°C",
         "battery": "V", "manifold_press": "bar", "accel_pedal_pct": "%"}


def _gear(v: float) -> int:
    return 1 + sum(1 for x in _UP_KMH if v > x)


def engine(t: float) -> dict:
    """Engine channels at ``t`` seconds into the drive."""
    v = speed_at(t)
    a = (speed_at(t + 0.5) - speed_at(t - 0.5)) / 3.6 if t >= 0.5 else 0.0  # m/s²
    g = _gear(v)
    wheel_rpm = v / 3.6 / TYRE_CIRC_M * 60.0
    rpm = wheel_rpm * GEARS[g - 1] * FINAL
    if v < 8:  # pulling away: clutch slipping
        rpm = IDLE_RPM + v * 55 + max(0.0, a) * 120
    rpm = max(IDLE_RPM, rpm) + 6.0 * math.sin(t * 2.1)
    load = max(0.0, a) * 0.75 + 0.28 * (v / 90.0) ** 2
    boost = min(1.3, load) * min(1.0, max(0.0, (rpm - 900) / 700.0))
    if a < -0.3:
        boost = 0.0
    pedal = 0.0 if a < -0.3 else min(100.0, 6.0 + 0.22 * v + 38.0 * max(0.0, a))
    coolant = 21.0 + (88.0 - 21.0) * (1 - math.exp(-t / 170.0))
    if coolant > 86.5:
        coolant = 86.5 + 1.2 * (0.5 + 0.5 * math.sin(t / 35.0))
    air = 13.0 + 7.0 * (1 - math.exp(-t / 500.0)) - 0.02 * v
    battery = 14.12 + 0.05 * math.sin(t / 6.0) - (0.15 if rpm < 900 else 0.0)
    return {
        "rpm": int(round(rpm)),
        "speed": int(round(v)),
        "coolant_temp": round(coolant, 1),
        "air_temp": round(air, 1),
        "battery": round(battery, 2),
        "manifold_press": round(1.01 + boost, 3),
        "accel_pedal_pct": round(pedal, 1),
    }


def _fix(t: float, utc_ms: int) -> Fix:
    p = demo_route(t)
    i = int(t)
    return Fix(utc_ms=utc_ms, lat=round(p["lat"], 6), lon=round(p["lon"], 6),
               speed_kmh=round(p["speed_kmh"], 2), heading=round(p["heading"], 1),
               alt_m=round(p["alt_m"], 1), sats=10 + (i // 97) % 3,
               hdop=round(0.7 + 0.1 * ((i // 53) % 3), 1), fix=True, mono=t, src="mock")


def generate(root: str, duration_s: float = PERIOD_S, hz: int = HZ) -> str:
    """Write the demo session under ``root`` (replacing any earlier demo session dirs)
    and return its id."""
    os.makedirs(root, exist_ok=True)
    for d in os.listdir(root):
        if re.match(r"^[0-9]{8}T[0-9]{6}Z(-[0-9]+)?$", d):
            shutil.rmtree(os.path.join(root, d))
    start = calendar.timegm(START_UTC + (0, 0, 0))
    now = {"t": 0.0}
    rec = SessionRecorder(root, clock=lambda: start + now["t"], mono=lambda: now["t"],
                          source="demo", synthetic=True, poll_hz=hz, min_free_bytes=0,
                          fsync=lambda fd: None)
    n = int(round(duration_s * hz))
    for i in range(n):
        t = i / hz
        now["t"] = t
        eng = engine(t)
        snap = {"conn": "connected", "status": "connected", "module": "motor",
                "mode": "demo", "faults": [],
                "signals": {k: {"v": v, "u": UNITS[k]} for k, v in eng.items()}}
        rec.feed(snap, _fix(t, int(round((start + t) * 1000))))
    sid = rec.status()["session"]
    now["t"] = n / hz
    rec.close()
    return sid
