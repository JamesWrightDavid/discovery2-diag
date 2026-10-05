"""Deterministic synthetic demo logs written through ``SessionRecorder`` (ADR-0009/0010/0011).

``generate(root)`` writes the two committed demo logs with a fake clock and returns their
ids. Same inputs → byte-identical files (the offline place names come from
``geo.offline``). Run it via ``tools/make_demo_session.py``.

* **"Demo log 1"** (``generate_log1``, id ``20261005T090000Z``): ~12 minutes at 5 Hz.
  GPS from the parametric loop in ``gps.route`` (empty moorland on Rannoch Moor, not a
  road), and engine channels that follow the speed — rpm from speed and gear, coolant
  warm-up, boost from load, battery charging.
* **"Demo log 2"** (``generate_log2``, id ``20261004T153000Z``): 7 minutes, SLABS only, on
  2 Hz, on a second parametric loop over the open north Dartmoor plateau (no road, no
  address):
  a parked raise/lower test, a rough section where the front-right wheel speed drops out
  (a logged fault), a shuttle-valve fault at the second stop, and two notes.

Demo log 1 timeline (session time) for the replay demo (ADR-0010):

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

import bisect
import calendar
import math
import os
import re
import shutil

from d2diag.gps.nmea import Fix
from d2diag.gps.route import PERIOD_S, demo_route, speed_at
from d2diag.logbook.notes import NoteLog
from d2diag.logbook.recorder import SessionRecorder, _read_meta, write_json_atomic

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




# ------------------------------------------------------------------ recording -- #

def _recorder(root: str, start: float, now: dict, hz: int) -> SessionRecorder:
    return SessionRecorder(root, clock=lambda: start + now["t"], mono=lambda: now["t"],
                           source="demo", synthetic=True, poll_hz=hz, min_free_bytes=0,
                           fsync=lambda fd: None)


def _finish(root: str, rec: SessionRecorder, now: dict, end_t: float, notes,
            name: str, description: str) -> str:
    """Add the retrospective notes, name the session, close it (the recorder writes the
    offline place names) and set the description."""
    sid = rec.status()["session"]
    path = os.path.join(root, sid)
    log = NoteLog(path, fsync=lambda fd: None)
    for nid, t_ms, t_end, text, tags, created in notes:
        log.add(t_ms, text=text, tags=tags, kind="note", source="retro", t_end=t_end,
                nid=nid, created=created)
    rec.set_name(name)
    now["t"] = end_t
    rec.close()
    meta_path = os.path.join(path, "meta.json")
    meta = _read_meta(meta_path) or {}
    meta["description"] = description
    write_json_atomic(meta_path, meta)
    return sid


DEMO1_NAME = "Demo log 1"
DEMO1_DESCRIPTION = (
    "A synthetic demo drive, not a real recording: a 12-minute loop drawn over empty "
    "moorland on Rannoch Moor in the Scottish Highlands (not a road). The engine (Td5) is "
    "read for the first six minutes, then the brakes and suspension (SLABS), including an "
    "ABS pump test while stopped.")


def generate_log1(root: str, duration_s: float = PERIOD_S, hz: int = HZ) -> str:
    """"Demo log 1": the Rannoch Moor drive (Td5, then SLABS). Returns its id."""
    os.makedirs(root, exist_ok=True)
    start = calendar.timegm(START_UTC + (0, 0, 0))
    now = {"t": 0.0}
    rec = _recorder(root, start, now, hz)
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
    return _finish(root, rec, now, n / hz, NOTES, DEMO1_NAME, DEMO1_DESCRIPTION)


# ------------------------------------------------------------- Demo log 2 -- #
# A second parametric loop (not a road, no addresses) over the open north Dartmoor
# plateau in Devon, around Cut Hill. SLABS only: ride heights with a parked raise/lower
# test, a rough section where the front-right wheel speed drops out (a logged fault) and
# a shuttle-valve fault that turns up during a fault check at the second stop.

START2_UTC = (2026, 10, 4, 15, 30, 0)  # id 20261004T153000Z
PERIOD2_S = 420.0
HZ2 = 2  # poll rate (GPS rows); SLABS heights every second poll (~1 Hz)
CENTER2_LAT, CENTER2_LON, BASE2_ALT_M = 50.6270, -3.9660, 560.0
_PROFILE2 = [
    (0, 0), (60, 0), (85, 32), (140, 42), (160, 18), (176, 18), (195, 38), (245, 45),
    (268, 0), (305, 0), (330, 36), (385, 40), (410, 0), (420, 0),
]
RAISE_S, RAISE_END_S = 25.0, 33.0      # raise_left while parked
LOWER_S, LOWER_END_S = 38.0, 46.0      # lower_left while parked
ROUGH_S, ROUGH_END_S = 160.0, 176.0    # rough ground: FR wheel speed drops out
FAULT_WATCH_S = 280.0                  # fault check at the second stop
FR_FAULT = "right front wheel speed sensor — output too low (Logged)"
SHUTTLE_FAULT = "shuttle valve switch — electrical failure (Current)"
NOTES2 = (  # (id, t_ms, t_end_ms, text, tags, created)
    ("3a4b5c6d", 25000, 46000,
     "Raise then lower left while parked: left height follows, right stays put", ["test"],
     "2026-10-04T15:45:00.000Z"),
    ("7e8f9a0b", 160000, 176000,
     "Front-right wheel speed drops out on the rough ground, fault logged", ["issue"],
     "2026-10-04T15:46:00.000Z"),
)
DEMO2_NAME = "Demo log 2"
DEMO2_DESCRIPTION = (
    "A synthetic demo drive, not a real recording: a 7-minute loop drawn over open "
    "moorland on north Dartmoor in Devon (not a road). Only the brakes and suspension "
    "(SLABS) are read: ride heights during a parked raise/lower test, a rough section "
    "where the front-right wheel speed drops out, and two faults.")


def _ease(profile, t: float) -> float:
    for (t0, v0), (t1, v1) in zip(profile, profile[1:]):
        if t0 <= t <= t1:
            if t1 == t0:
                return float(v1)
            x = (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * (1 - math.cos(math.pi * x)) / 2
    return 0.0


def speed2_at(t: float) -> float:
    return _ease(_PROFILE2, t % PERIOD2_S)


def _shape2(theta: float) -> "tuple[float, float]":
    """A rounded, slightly kidney-shaped loop (x east, y north) before scaling."""
    x = 0.8 * math.cos(theta) - 0.1 * math.cos(2 * theta)
    y = math.sin(theta) + 0.15 * math.sin(2 * theta + 0.4) + 0.05 * math.cos(3 * theta)
    return x, y


def _build2():
    dt = 0.1
    ts, ds = [0.0], [0.0]
    for i in range(1, int(PERIOD2_S / dt) + 1):
        t = i * dt
        ts.append(t)
        ds.append(ds[-1] + speed2_at(t - dt / 2) / 3.6 * dt)
    m = 2000
    thetas = [2 * math.pi * k / m for k in range(m + 1)]
    pts = [_shape2(th) for th in thetas]
    arc = [0.0]
    for a, b in zip(pts, pts[1:]):
        arc.append(arc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    scale = ds[-1] / arc[-1]
    return ts, ds, [a * scale for a in arc], thetas, scale


_TS2, _DS2, _ARC2, _THETA2, _SCALE2 = _build2()


def _interp(xs, ys, x: float) -> float:
    i = bisect.bisect_right(xs, x)
    if i <= 0:
        return ys[0]
    if i >= len(xs):
        return ys[-1]
    x0, x1 = xs[i - 1], xs[i]
    return ys[i - 1] + (ys[i] - ys[i - 1]) * ((x - x0) / (x1 - x0) if x1 > x0 else 0.0)


def _pos2(dist: float) -> "tuple[float, float]":
    x, y = _shape2(_interp(_ARC2, _THETA2, dist % _ARC2[-1]))
    return x * _SCALE2, y * _SCALE2


def route2(t: float) -> dict:
    """Position and motion on the Demo log 2 loop at ``t`` seconds."""
    t = t % PERIOD2_S
    dist = _interp(_TS2, _DS2, t)
    x, y = _pos2(dist)
    x2, y2 = _pos2(dist + 2.0)
    m_lat = 111_320.0
    lap = _DS2[-1]
    return {"lat": CENTER2_LAT + y / m_lat,
            "lon": CENTER2_LON + x / (m_lat * math.cos(math.radians(CENTER2_LAT))),
            "speed_kmh": speed2_at(t),
            "heading": math.degrees(math.atan2(x2 - x, y2 - y)) % 360.0,
            "alt_m": BASE2_ALT_M + 18.0 * math.sin(2 * math.pi * dist / lap + 0.6)
            + 3.0 * math.sin(10 * math.pi * dist / lap)}


def _fix2(t: float, utc_ms: int) -> Fix:
    p = route2(t)
    i = int(t)
    return Fix(utc_ms=utc_ms, lat=round(p["lat"], 6), lon=round(p["lon"], 6),
               speed_kmh=round(p["speed_kmh"], 2), heading=round(p["heading"], 1),
               alt_m=round(p["alt_m"], 1), sats=9 + (i // 71) % 3,
               hdop=round(0.8 + 0.1 * ((i // 47) % 3), 1), fix=True, mono=t, src="mock")


def _bump(t: float, t0: float, t1: float, ramp: float = 3.0) -> float:
    """0 → 1 → 0 over [t0, t1] with cosine ramps of ``ramp`` seconds."""
    if t <= t0 or t >= t1:
        return 0.0
    up = min(1.0, (t - t0) / ramp)
    down = min(1.0, (t1 - t) / ramp)
    return (1 - math.cos(math.pi * min(up, down))) / 2


def slabs2(t: float) -> dict:
    """SLABS channels for Demo log 2: heights with the parked raise/lower test, body
    movement that grows on the rough section, four wheel speeds (FR drops out there)."""
    v = speed2_at(t)
    rough = 1.0 if ROUGH_S <= t < ROUGH_END_S else 0.0
    bounce = (2.5 + 5.0 * rough) * math.sin(t * 2.3) * min(1.0, v / 25.0)
    pitch = 1.5 * math.sin(t / 5.0) * min(1.0, v / 40.0)
    lift = 12.0 * _bump(t, RAISE_S, LOWER_S + 2.0) - 9.0 * _bump(t, LOWER_S + 2.0, LOWER_END_S + 6.0)
    spread = 0.02 * math.sin(t / 7.0)
    fr = v * (1 - spread)
    if rough and int(t * 2) % 3 != 0:
        fr = 0.0  # sensor output too low: reads zero on most samples
    return {
        "height_left": int(round(146 + lift + bounce + pitch)),
        "height_right": int(round(155 + bounce - 0.6 * pitch)),
        "battery": round(13.9 + 0.05 * math.sin(t / 8.0) - (0.25 if v < 1 and
                                                              RAISE_S <= t < LOWER_END_S
                                                              else 0.0), 2),
        "wheel_speed_fl": round(v * (1 + spread), 1),
        "wheel_speed_fr": round(fr, 1),
        "wheel_speed_rl": round(v * (1 + spread * 0.8), 1),
        "wheel_speed_rr": round(v * (1 - spread * 0.8), 1),
    }


def _faults2(t: float) -> "list[str]":
    out = []
    if t >= ROUGH_END_S:
        out.append(FR_FAULT)
    if t >= FAULT_WATCH_S + 5:
        out.append(SHUTTLE_FAULT)
    return out


def _active2(t: float, start: float) -> "dict | None":
    if RAISE_S <= t < RAISE_END_S:
        return {"action": "raise_left", "label": "Raise left", "since": start + RAISE_S}
    if LOWER_S <= t < LOWER_END_S:
        return {"action": "lower_left", "label": "Lower left", "since": start + LOWER_S}
    return None


def generate_log2(root: str, duration_s: float = PERIOD2_S, hz: int = HZ2) -> str:
    """"Demo log 2": the SLABS-focused Dartmoor loop. Returns its id."""
    os.makedirs(root, exist_ok=True)
    start = calendar.timegm(START2_UTC + (0, 0, 0))
    now = {"t": 0.0}
    rec = _recorder(root, start, now, hz)
    n = int(round(duration_s * hz))
    commands = {RAISE_S: ("raise_left", "Raise left"), LOWER_S: ("lower_left", "Lower left")}
    for i in range(n):
        t = i / hz
        now["t"] = t
        # SLABS is polled lightly: heights every ~1 s cycle; faults at most every 10th poll
        sig = slabs2(t) if i % hz == 0 else {}
        snap = {"conn": "connected", "status": "connected", "module": "slabs",
                "faults": _faults2(10.0 * math.floor(t / 10.0)),
                "fault_watch": t >= FAULT_WATCH_S, "logging": {"recording": False},
                "active_test": _active2(t, start),
                "signals": {k: {"v": v, "u": SLABS_UNITS[k]} for k, v in sig.items()}}
        for at, (action, label) in commands.items():
            if abs(t - at) < 1e-9:
                rec.event("command", action=action, ok=True, message=label)
        rec.feed(snap, _fix2(t, int(round((start + t) * 1000))))
    return _finish(root, rec, now, n / hz, NOTES2, DEMO2_NAME, DEMO2_DESCRIPTION)


DEMO_IDS = ("20261005T090000Z", "20261004T153000Z")


def generate(root: str) -> "list[str]":
    """Write both demo logs under ``root`` (replacing any earlier session dirs there) and
    return their ids (Demo log 1, Demo log 2)."""
    os.makedirs(root, exist_ok=True)
    for d in os.listdir(root):
        if re.match(r"^[0-9]{8}T[0-9]{6}Z(-[0-9]+)?$", d):
            shutil.rmtree(os.path.join(root, d))
    return [generate_log1(root), generate_log2(root)]
