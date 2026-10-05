"""Deterministic synthetic demo drive written through ``SessionRecorder`` (ADR-0009/0010).

``generate(root)`` writes one ~12-minute session at 5 Hz with a fake clock: GPS from the
parametric loop in ``gps.route`` (empty moorland, not a road), and engine channels that
follow the speed — rpm from speed and gear, coolant warm-up, boost from load, battery
charging. Same inputs → byte-identical files. Run it via ``tools/make_demo_session.py``.

Timeline (session time) for the replay demo (ADR-0010):

* 0:00 ``state`` line (connected, motor, demo); GPS-derived ``GPS_LonAcc``/``GPS_LatAcc``
  throughout.
* 2:10 at the first stop: Td5 output test ``output_ac_fan`` (a ``command`` event; the
  car is stationary, as actuator tests must be).
* 6:00 module switch motor → slabs (the session continues; ``conn`` stays connected);
  from here the SLABS channels (heights, battery, wheel speeds) at ~1 Hz.
* 9:00 at the third stop: ``pump_on`` → ``active_test`` on, ``pump_off`` 8 s later → off.
* Three retrospective notes in ``notes.jsonl`` (fixed ids and created times).
"""
from __future__ import annotations

import calendar
import math
import os
import re
import shutil

from ..gps.nmea import Fix
from ..gps.route import PERIOD_S, demo_route, speed_at
from .notes import NoteLog
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


SWITCH_S = 360.0            # motor → slabs
FAN_TEST_S = 130.0          # output_ac_fan at the first stop (125–145 s)
PUMP_ON_S, PUMP_OFF_S = 540.0, 548.0  # SLABS pump test at the third stop (535–560 s)
SLABS_UNITS = {"height_left": "", "height_right": "", "battery": "V",
               "wheel_speed_fl": "", "wheel_speed_fr": "", "wheel_speed_rl": "",
               "wheel_speed_rr": ""}
NOTES = (  # (id, t_ms, t_end_ms, text, tags, created)
    ("a1b2c3d4", 120000, None, "Rough idle after the junction", ["issue"],
     "2026-10-05T09:30:00.000Z"),
    ("5e6f7a8b", 175000, 230000, "Full-throttle climb: boost and coolant look fine",
     ["driving"], "2026-10-05T09:31:00.000Z"),
    ("9c0d1e2f", 540000, 548000, "ABS pump test while stopped, pump audible", ["test"],
     "2026-10-05T09:32:00.000Z"),
)


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


def slabs(t: float) -> dict:
    """SLABS channels at ``t``: raw ride heights with a little body movement, the ABS
    battery reading and four wheel speeds following the road speed (cornering spread)."""
    v = speed_at(t)
    bounce = 3.0 * math.sin(t * 1.7) * min(1.0, v / 40.0)
    roll = 2.0 * math.sin(t / 9.0) * min(1.0, v / 60.0)
    spread = 0.015 * math.sin(t / 9.0)
    return {
        "height_left": int(round(149 + bounce + roll)),
        "height_right": int(round(158 + bounce - roll)),
        "battery": round(13.95 + 0.04 * math.sin(t / 7.0), 2),
        "wheel_speed_fl": round(v * (1 + spread), 1),
        "wheel_speed_fr": round(v * (1 - spread), 1),
        "wheel_speed_rl": round(v * (1 + spread * 0.8), 1),
        "wheel_speed_rr": round(v * (1 - spread * 0.8), 1),
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
    pump = {"action": "pump_on", "label": "ABS pump on", "since": start + PUMP_ON_S,
            "stop": "pump_off"}
    for i in range(n):
        t = i / hz
        now["t"] = t
        if t < SWITCH_S:
            module, sig, units = "motor", engine(t), UNITS
        else:
            module, units = "slabs", SLABS_UNITS
            sig = slabs(t) if i % hz == 0 else {}  # SLABS is polled lightly: ~1 Hz
        snap = {"conn": "connected", "status": "connected", "module": module,
                "mode": "demo", "faults": [], "fault_watch": False,
                "logging": {"recording": False},
                "active_test": pump if PUMP_ON_S <= t < PUMP_OFF_S else None,
                "signals": {k: {"v": v, "u": units[k]} for k, v in sig.items()}}
        if abs(t - FAN_TEST_S) < 1e-9:
            rec.event("command", action="output_ac_fan", ok=True, message="A/C fan (mock)")
        if abs(t - PUMP_ON_S) < 1e-9:
            rec.event("command", action="pump_on", ok=True, message="ABS pump on (mock)")
        if abs(t - PUMP_OFF_S) < 1e-9:
            rec.event("command", action="pump_off", ok=True, message="ABS pump off (mock)")
        rec.feed(snap, _fix(t, int(round((start + t) * 1000))))
    sid = rec.status()["session"]
    log = NoteLog(os.path.join(root, sid), fsync=lambda fd: None)
    for nid, t_ms, t_end, text, tags, created in NOTES:
        log.add(t_ms, text=text, tags=tags, kind="note", source="retro", t_end=t_end,
                nid=nid, created=created)
    now["t"] = n / hz
    rec.close()
    return sid
