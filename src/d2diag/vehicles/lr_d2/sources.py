"""Discovery 2 data sources: the Td5 and SLABS live readers and their derived fields.

The pack's ``sources`` factory (:func:`make_sources`) builds ``{module id: DataSource}``
for the car: :class:`Td5DataSource`, :class:`SlabsDataSource` and an
:class:`~d2diag.web.sources.InfoDataSource` per module with no live reader yet.
The generic pieces (``DataSource``, raw logging, the transport, ``read_block``) live in
:mod:`d2diag.web.sources`; this is the one pack file allowed to import ``d2diag.web``
(the consumer boundary).
"""
from __future__ import annotations

import json
import os
import time

from d2diag.signals import load_signals
from d2diag.web.sources import (  # noqa: F401 — platform pieces, re-exported for old importers
    DataSource,
    InfoDataSource,
    _parse_lids,
    _RawLogPaused,
    _raw_log_path,
    _read_block_cmd,
    _sleep_kw,
    _transport,
    resolve_serial_port,
)

from .td5.identifiers import BY_NAME, signal_status
from .td5.td5 import INJECTOR_CYLINDERS, OUTPUT_NAMES

# Td5 module actions the Td5 source dispatches. Must match the td5 entries of
# ``d2diag.commands.REGISTRY`` that are not planned — tests/test_commands.py checks both ways.
TD5_ACTIONS: "frozenset[str]" = frozenset(
    [f"output_{n}" for n in OUTPUT_NAMES]
    + [f"injector_{n}" for n in INJECTOR_CYLINDERS]
    + ["security_status", "read_identity"])


def _security_message(status: "int | None") -> str:
    """Plain-language immobiliser status. Only ``03`` is proven (RDL 016)."""
    if status is None:
        return "No status byte in the reply"
    if status == 0x03:
        return "Not immobilised (status 03)"
    return f"Immobiliser status 0x{status:02X} — meaning not confirmed"


# Full reference tool coverage: also read LIDs the reference tool polls but we haven't mapped yet, so
# the raw log captures ALL available data — then unmapped fields can be found from a normal
# drive (that's how MAF was found in 1D 2026-08-21). "Don't throw away the bytes we haven't named."
#
# TD5 (not session-sensitive): read the extra LIDs EVERY cycle so they're sampled alongside rpm.
# 1E/1F/20 = confirmed responding in the fuelling block (lid_sweep 2026-08-21); 1E carries
# switch/digital-in bits (byte0 bit0 = brake, car test 2026-08-21). 36 = the second
# switch block (Ekaitza) — added to catch A/C/handbrake bits. (37/38
# from SimonRafferty do NOT respond on RDL016, removed.)
_TD5_COVERAGE_EXTRA = (0x1E, 0x1F, 0x20, 0x36)
# SLABS (MUST be polled lightly — block reading kills the session): these LIDs are rotated
# ONE per cycle (the 0x54 heights are read every cycle anyway). Source: slabs/menu.py +
# references/reference_tool_menu_map.md (the reference tool menu's input block).
_SLABS_COVERAGE = frozenset({
    0x11, 0x3B, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
    0x50, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
})

# Fuel computer: fields derived from injection quantity + rpm + speed. Not a LID read →
# unit + confidence are given here (injection_qty is a candidate, so consumption is too).
_INJ_PER_REV = 2.5          # 5-cyl 4-stroke: 5/2 injections per crankshaft revolution
_DIESEL_G_PER_L = 832.0     # diesel density
_DERIVED_TD5 = {
    "fuel_rate":        ("L/h", "candidate"),
    "economy":          ("L/100km", "candidate"),
    "trip_economy":     ("L/100km", "candidate"),
    "lifetime_economy": ("L/100km", "candidate"),
}

# Presentation metadata for fields that are computed here rather than read from a LID
# (so they are not in the signal store). /fields merges these with the store, so the UI
# has ONE metadata source per module. Keys are canonical module ids.
DERIVED_FIELDS: "dict[str, dict[str, dict]]" = {
    "td5": {
        "fuel_rate": {"label": "Fuel rate", "group": "Fuelling", "span": [0, 20],
                      "description": "Fuel flow from injection quantity × rpm (derived, candidate)."},
        "economy": {"span": [0, 25], "label": "Fuel economy", "group": "Fuelling",
                    "description": "Live consumption — only meaningful while moving (derived, candidate)."},
        "trip_economy": {"span": [0, 25], "label": "Trip economy", "group": "Fuelling",
                         "description": "Average consumption since the dashboard started (derived, candidate)."},
        "lifetime_economy": {"span": [0, 25], "label": "Lifetime economy", "group": "Fuelling",
                             "description": "Average consumption across all logged driving (derived, candidate)."},
    },
    "slabs": {
        "height_left_mm": {"unit": "mm", "c": "proven", "label": "Height left", "group": "Ride height",
                           "span": [0, 360], "normal": [154, 189],
                           "description": "Left ride height in mm (derived from the raw sensor)."},
        "height_right_mm": {"unit": "mm", "c": "proven", "label": "Height right", "group": "Ride height",
                            "span": [0, 360], "normal": [154, 189],
                            "description": "Right ride height in mm (derived from the raw sensor)."},
    },
}
for _k, (_u, _c) in _DERIVED_TD5.items():
    DERIVED_FIELDS["td5"][_k].update(unit=_u, c=_c)


class _FuelComputer:
    """Instantaneous consumption + trip and lifetime averages from injection quantity
    (mg/stroke), rpm and speed. Integrates with REAL time between polls (time.monotonic).

    L/h = inj[mg/stroke] × injections/rev × rpm × 60 / 1e6 / (density g/ml).
    Trip = since the object was created (dashboard start). Lifetime = persisted to file.
    """

    def __init__(self, state_path: "str | None" = None,
                 clock: "callable" = time.monotonic) -> None:
        self._state_path = state_path
        self._clock = clock
        self._last: "float | None" = None
        self._trip_fuel = 0.0   # L
        self._trip_dist = 0.0   # km
        self._life_fuel, self._life_dist = self._load()
        self._tick = 0

    def _load(self) -> "tuple[float, float]":
        if self._state_path and os.path.exists(self._state_path):
            try:
                d = json.load(open(self._state_path, encoding="utf-8"))
                return float(d.get("fuel_l", 0.0)), float(d.get("dist_km", 0.0))
            except (OSError, ValueError, TypeError):
                pass
        return 0.0, 0.0

    def _save(self) -> None:
        if not self._state_path:
            return
        try:
            tmp = self._state_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"fuel_l": round(self._life_fuel, 4),
                           "dist_km": round(self._life_dist, 3)}, fh)
            os.replace(tmp, self._state_path)
        except OSError:
            pass

    def pause(self) -> None:
        """Zero the clock (on module switch/reconnect) so a gap isn't integrated."""
        self._last = None

    def update(self, inj_mg: "float | None", rpm: "float | None",
               speed_kmh: "float | None") -> "dict":
        now = self._clock()
        rate = None
        if inj_mg is not None and rpm:
            rate = inj_mg * _INJ_PER_REV * rpm * 60.0 / 1e6 / (_DIESEL_G_PER_L / 1000.0)
        if self._last is not None and rate is not None:
            dt_h = min(now - self._last, 3.0) / 3600.0   # cap 3 s → no spike after a pause
            self._trip_fuel += rate * dt_h
            self._life_fuel += rate * dt_h
            if speed_kmh:
                d = speed_kmh * dt_h
                self._trip_dist += d
                self._life_dist += d
        self._last = now

        out: "dict[str, float]" = {}
        if rate is not None:
            out["fuel_rate"] = round(rate, 2)
            if speed_kmh and speed_kmh > 5:                 # economy only when moving
                out["economy"] = round(rate / speed_kmh * 100.0, 1)
        if self._trip_dist > 0.1:
            out["trip_economy"] = round(self._trip_fuel / self._trip_dist * 100.0, 1)
        if self._life_dist > 1.0:
            out["lifetime_economy"] = round(self._life_fuel / self._life_dist * 100.0, 1)
        self._tick += 1
        if self._tick % 60 == 0:                            # persist lifetime ~every 30-60 s
            self._save()
        return out

# Unit map from the identifier table (name → unit).
UNITS = {name: sig.unit for name, sig in BY_NAME.items()}


def _conf_map(module: str) -> "dict[str, str]":
    """{signal name → confidence} from the signal store (proven/candidate)."""
    out: "dict[str, str]" = {}
    for s in load_signals(module):
        out.setdefault(s.name, s.confidence)  # first record of a length-variant name wins
    return out


def _conf_of(module: str, name: str, conf: "dict[str, str]") -> str:
    """Confidence for a signal — from the store, otherwise a heuristic for derived fields.
    The trust view (Verified/Explorer) filters on this."""
    if name in conf:
        return conf[name]
    if module == "slabs":
        if name.startswith("height_"):
            return "proven"          # derived from a proven height
        if name.startswith(("wheel_speed_", "abs_sensor_")):
            return "candidate"        # wheel speed/voltage: scale not confirmed
    return "proven"


def _sig(values: "dict[str, float]", module: str = "td5") -> "dict[str, dict]":
    """Package {name: value} → {name: {"v", "u", "s", "c"}} (c = confidence)."""
    conf = _conf_map(module)
    out = {}
    for k, v in values.items():
        vr = round(v, 2)
        if k in _DERIVED_TD5:                # computed fields (fuel computer)
            unit, c = _DERIVED_TD5[k]
        else:
            unit, c = UNITS.get(k, ""), _conf_of(module, k, conf)
        out[k] = {"v": vr, "u": unit, "s": signal_status(k, vr), "c": c}
    return out



class Td5DataSource(DataSource):
    """Real Td5 ECU. Establishes the session lazily and re-reads on error.

    Requires hardware; imports heavy dependencies locally.
    """

    name = "td5"
    store_module = "td5"

    def __init__(self, port: str, read_faults: bool = True,
                 raw_log_dir: "str | None" = None,
                 fuel_state_path: "str | None" = None) -> None:
        self._port = port
        self._read_faults = read_faults
        self._raw_log_path = _raw_log_path("td5", raw_log_dir)
        self._fuel = _FuelComputer(fuel_state_path)  # fuel computer (instantaneous/trip/lifetime)
        self._td5 = None
        self._faults: "list[str]" = []
        self._fault_tick = 0
        self.fault_every = 10  # read fault codes every Nth poll (1 = "fault watch", every cycle)
        self.on_progress = None  # callback(str): live status during blocking establishment

    def is_connected(self) -> bool:
        return self._td5 is not None

    def _connect(self):
        from d2diag.kline import KLine
        from d2diag.kwp2000 import KWP2000
        from .td5 import Td5

        if self.on_progress:
            self.on_progress("opening the cable")
        port = resolve_serial_port(self._port)  # auto-detect on every attempt
        td5 = Td5(KWP2000(KLine(_transport(port, self._raw_log_path)), tolerant=True))
        td5.open()
        td5.establish(progress=self.on_progress, **_sleep_kw(self.on_sleep))
        return td5

    def disconnect(self) -> None:
        # release() = StopDiagnosticSession + close. Just close() leaves the TD5 session
        # open on the shared bus → the next module (SLABS) gets 7F 81 10 on its init.
        try:
            if self._td5 is not None:
                self._td5.release()
        except Exception:  # noqa: BLE001
            pass
        self._td5 = None
        self._fuel.pause()  # zero the fuel computer's clock so the reconnect gap isn't counted

    def set_port(self, spec: str) -> None:
        self._port = spec

    def menu_map(self) -> "list":
        from .td5.menu import TD5_MENU
        return TD5_MENU

    def poll(self) -> "dict":
        try:
            if self._td5 is None:
                self._td5 = self._connect()
            signals = self._td5.read_all()
            if not signals:
                # the session is "up" but all reads failed (noise/dropped cable) →
                # treat as lost contact so we reconnect on the next poll.
                raise RuntimeError("no signals read — noise or lost connection")
            # Full coverage: read the unmapped LIDs the reference tool polls → they land in the raw log
            # (not decoded, but captured for future mapping). An error here must not
            # fell the poll — read_all already succeeded.
            try:
                self._td5.read_block(_TD5_COVERAGE_EXTRA)
            except Exception:  # noqa: BLE001
                pass
            # Fuel computer: instantaneous L/h + L/100km, trip and lifetime averages, from
            # injection quantity + rpm + speed. Derived fields, integrated over time.
            signals.update(self._fuel.update(
                signals.get("injection_qty"), signals.get("rpm"), signals.get("speed")))
            # read fault codes less often (expensive); every ~10th poll
            if self._read_faults and self._fault_tick % self.fault_every == 0:
                try:
                    # keep undecoded byte<off>.bit<n> faults: hiding them let a clear wipe faults
                    # nobody saw (2026-10-03). The UI shows them by their raw position.
                    self._faults = list(self._td5.read_faults())
                except Exception:  # noqa: BLE001
                    pass
            self._fault_tick += 1
            return {
                "status": "connected",
                "source": self.name,
                "signals": _sig(signals),
                "faults": self._faults,
            }
        except Exception as exc:  # noqa: BLE001 — drop the session and reconnect next poll
            try:
                if self._td5 is not None:
                    self._td5.release()  # tear down the link (82) — otherwise 7F 81 10 on reconnect
            except Exception:  # noqa: BLE001
                pass
            self._td5 = None
            return {"status": "error", "source": self.name, "signals": {}, "faults": [],
                    "error": f"{type(exc).__name__}: {exc}"}

    def command(self, action: str, params: "dict | None" = None) -> "dict":
        if action == "read_block":
            return _read_block_cmd(self._td5, params)
        if action == "clear_faults":
            if self._td5 is None:
                return {"ok": False, "error": "not connected to the ECU"}
            try:
                self._td5.clear_faults()
                self._fault_tick = 0  # force a re-read of fault codes next poll
                return {"ok": True, "message": "Fault codes cleared"}
            except Exception as exc:  # noqa: BLE001
                return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        # Output tests (IOControl) + injector pulse. Proven from sniff 2026-08-08 but
        # NEVER run from our code against the car → experimental until verified.
        # The server gates every one through d2diag.commands.refusal() before it gets here.
        if action not in TD5_ACTIONS:
            return {"ok": False, "error": f"unknown command: {action}"}
        if self._td5 is None:
            return {"ok": False, "error": "not connected to the ECU"}
        if action == "read_identity":
            return self._read_identity()
        try:
            if action == "security_status":
                raw = bytes(self._td5.security_status_raw())
                status = raw[1] if len(raw) >= 2 else None
                return {"ok": True, "message": _security_message(status),
                        "raw": raw.hex(" "), "status": status}
            if action.startswith("output_"):
                name = action[len("output_"):]
                self._td5.output_test(name)
                return {"ok": True, "message": f"Output test: {name}"}
            if action.startswith("injector_"):
                cyl = int(action[len("injector_"):])
                self._td5.injector_pulse(cyl)
                return {"ok": True, "message": f"Injector {cyl} pulse"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        return {"ok": False, "error": f"unknown command: {action}"}

    def _read_identity(self) -> "dict":
        """``1A 87/9A/9B/9C`` → {ok, identity}. The VIN is masked in the Td5 layer, and the
        raw bus log is paused for the read so the VIN block never reaches a file. Errors
        carry the exception type only (a message could quote raw reply bytes)."""
        try:
            with _RawLogPaused(self._td5):
                ident = self._td5.read_identity()
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"identity read failed ({type(exc).__name__})"}
        if not any(ident.get(k) for k in ("part_no", "vin_masked")):
            return {"ok": False, "error": "no identity block answered", "identity": ident}
        return {"ok": True, "message": "ECU identity", "identity": ident}


# --- SLABS (Wabco ABS/SLS) ------------------------------------------------ #
_SLABS_UNITS = {k: m["unit"] for k, m in DERIVED_FIELDS["slabs"].items()}


def _slabs_sig(values: "dict[str, float]") -> "dict[str, dict]":
    conf = _conf_map("slabs")
    return {k: {"v": round(v, 1), "u": _SLABS_UNITS.get(k, ""), "s": None,
                "c": _conf_of("slabs", k, conf)}
            for k, v in values.items()}


def _slabs_decode_store(raws: "dict[int, bytes]") -> "dict[str, float]":
    """Decode all SLABS store fields we have raw bytes for → {name: value}.

    Store-driven, so a new confirmed mapping in ``slabs.json`` shows up in the UI
    without a code change. The heights are supplemented with derived mm fields (the SVG
    car). Fields with a state label (any_door) are NOT included here — they go as numeric
    0/1 and the label is set in the UI layer if needed.
    """
    vals: "dict[str, float]" = {}
    for sig in load_signals("slabs"):
        raw = raws.get(sig.lid)
        if raw is not None and sig.fits(raw):
            vals[sig.name] = round(sig.decode(raw), 3)
    if "height_left" in vals:
        vals["height_left_mm"] = round(vals["height_left"] * 1.4, 1)
    if "height_right" in vals:
        vals["height_right_mm"] = round(vals["height_right"] * 1.4, 1)
    return vals


def _slabs_faults_flat(f: "dict[str, list]") -> "list[str]":
    """{"logged":[…],"current":[…]} → flat list with (Logged)/(Current) tags.

    ``slabs.Slabs.read_faults`` still answers with its legacy keys ("loggade" = logged,
    "aktuella" = current); both spellings are accepted."""
    logged = f.get("logged", f.get("loggade", []))
    current = f.get("current", f.get("aktuella", []))
    return [x + " (Logged)" for x in logged] + [x + " (Current)" for x in current]


# Actuator actions (web → SLABS). Name → English label (for responses/UI).
_SLABS_ACTUATORS = {
    "buzzer": "Buzzer test", "compressor": "Compressor test", "exhaust": "Exhaust valve test",
    "pump_on": "ABS pump on", "pump_off": "ABS pump off",
    "raise_left": "Raise left", "raise_right": "Raise right",
    "lower_left": "Lower left", "lower_right": "Lower right",
    "wheel_fl": "Valve test FL", "wheel_fr": "Valve test FR",
    "wheel_rl": "Valve test RL", "wheel_rr": "Valve test RR",
    "bleed_power_on": "ABS power bleed — start", "bleed_power_off": "ABS power bleed — stop",
    "bleed_module": "ABS module bleed (4-step sequence)",
}


def _slabs_do(slabs, action: str) -> None:
    """Run an actuator action against a real Slabs object."""
    if action == "buzzer":
        slabs.buzzer()
    elif action == "compressor":
        slabs.compressor()
    elif action == "exhaust":
        slabs.exhaust_valve()
    elif action == "pump_on":
        slabs.pump_relay(True)
    elif action == "pump_off":
        slabs.pump_relay(False)
    elif action.startswith("raise_"):
        slabs.raise_corner(action.split("_", 1)[1])
    elif action.startswith("lower_"):
        slabs.lower_corner(action.split("_", 1)[1])
    elif action.startswith("wheel_"):
        slabs.wheel_test(action.split("_", 1)[1])
    elif action == "bleed_power_on":
        slabs.abs_power_bleed(True)
    elif action == "bleed_power_off":
        slabs.abs_power_bleed(False)
    elif action == "bleed_module":
        slabs.abs_module_bleed()
    else:
        raise ValueError(f"unknown command: {action}")



_SLABS_EMPTY_GRACE = 3  # empty bus calls in a row tolerated before reconnect

# ⚠️ SLABS traffic should stay at ~1 Hz — the reference tool's rate in the sniff (keepalive
# `01 3e 3f` every ~1048th ms, reads only on screen refresh). The dashboard's
# poller thread runs at 0.5 s and sent 3E + 21 54 EVERY cycle = 4 frames/s, i.e.
# ~4× the reference. Car 2026-08-18: connected 20:54:28, dead 20:54:49 (21 s).
# The rate is therefore decoupled from the server's poll interval and driven by the clock here.
_SLABS_BUS_PERIOD = 1.0    # seconds between bus calls
_SLABS_FAULT_PERIOD = 30.0  # seconds between fault-code reads (2 extra frames)


class SlabsDataSource(DataSource):
    """Real Wabco SLABS. Establishes fast init 0x29 lazily, re-reads on error.

    Requires a TRANSMITTING K-line cable (KKL/ESP32 master) — not the passive sniff tap.
    """

    name = "slabs"
    store_module = "slabs"

    def __init__(self, port: str, read_faults: bool = True,
                 raw_log_dir: "str | None" = None) -> None:
        self._port = port
        self._read_faults = read_faults
        self._raw_log_path = _raw_log_path("slabs", raw_log_dir)
        self._slabs = None
        self._faults: "list[str]" = []
        self._tick = 0
        self.fault_every = 10  # read fault codes every Nth poll (1 = "fault watch", every cycle)
        self.on_progress = None  # callback(str): live status during blocking establishment
        self._empty_streak = 0  # number of polls in a row without a reply (grace before reconnect)
        self._last_signals: "dict" = {}  # last decoded signals (shown during the grace period)
        self._last_bus = 0.0    # monotonic time of the last bus call (the 1 Hz throttle)
        self._last_fault = 0.0  # monotonic time of the last fault-code read
        self._raws: "dict[int, bytes]" = {}   # last read raw bytes per LID (store decoding)
        self._extra_lids: "list[int]" = []    # the other store LIDs to rotate through
        self._rot = 0                          # rotation index

    def is_connected(self) -> bool:
        return self._slabs is not None

    def _connect(self):
        from d2diag.kline import KLine
        from d2diag.kwp2000 import KWP2000
        from .slabs import SLABS_ADDRESS, Slabs

        if self.on_progress:
            self.on_progress("opening the cable")
        port = resolve_serial_port(self._port)
        slabs = Slabs(KWP2000(KLine(_transport(port, self._raw_log_path), target=SLABS_ADDRESS),
                              tolerant=True))
        slabs.open()
        slabs.establish(progress=self.on_progress, **_sleep_kw(self.on_sleep))
        # The other LIDs the store cares about (the 0x54 heights are read every cycle; the rest
        # are rotated ONE per cycle so traffic stays at ~1 Hz). A new mapping in
        # slabs.json → a new field in the UI without a code change.
        # Full reference tool coverage in the rotation: all LIDs the reference tool polls (mapped +
        # unmapped), ONE per cycle so the poll stays light (0x54 is read every cycle anyway).
        # Unmapped ones aren't decoded but are captured in the raw log for future mapping.
        self._extra_lids = sorted(
            (_SLABS_COVERAGE | {sig.lid for sig in load_signals("slabs")}) - {0x54})
        return slabs

    def disconnect(self) -> None:
        # release() — SLABS has no session to end (no-op), but the symmetry makes
        # a module switch look the same regardless of source.
        try:
            if self._slabs is not None:
                self._slabs.release()
        except Exception:  # noqa: BLE001
            pass
        self._slabs = None

    def set_port(self, spec: str) -> None:
        self._port = spec

    def poll(self) -> "dict":
        try:
            if self._slabs is None:
                self._slabs = self._connect()
                self._empty_streak = 0  # fresh session → full grace before the next reconnect
            now = time.monotonic()
            if now - self._last_bus < _SLABS_BUS_PERIOD:
                # Too soon for more traffic — the server polls faster than SLABS can take.
                # Return the last read values untouched (they're at most 1 s old, which
                # is exactly the resolution the module gives anyway). NO bus calls here.
                return {"status": "connected", "source": self.name,
                        "signals": self._last_signals, "faults": self._faults}
            self._last_bus = now
            try:
                self._slabs.tester_present()  # keepalive — best effort, not a sign of life
            except Exception:  # noqa: BLE001 — a dropped 3E must not tear down the session
                pass
            # LIGHT poll: heights (21 54) EVERY cycle + ONE rotating extra LID from
            # the store. This keeps traffic at ~1 Hz (3E + 2 reads) — far below
            # the block reading that killed the session (5 LIDs × every 0.5 s cycle).
            # The reference tool ran ~1 Hz keepalive + occasional reads.
            try:
                raw = self._slabs.read_data(0x54)  # byte0=left height, byte1=right
            except Exception:  # noqa: BLE001 — a single dropped read
                raw = b""
            if raw:
                self._raws[0x54] = raw
            if self._extra_lids:  # one extra LID per cycle, rotating
                lid = self._extra_lids[self._rot % len(self._extra_lids)]
                self._rot += 1
                try:
                    extra = self._slabs.read_data(lid)
                    if extra:
                        self._raws[lid] = extra
                except Exception:  # noqa: BLE001 — a dropped extra read is harmless
                    pass
            if not raw:
                # A full reconnect costs ~20 s, so we don't tear down the session right away:
                # SLABS often goes quiet for a cycle (bus glitch, or the car started rolling).
                # Keep the session for a couple of polls and show the last known values
                # ("stale"); only after several empties in a row do we give up and reconnect.
                self._empty_streak += 1
                if self._empty_streak < _SLABS_EMPTY_GRACE:
                    return {"status": "connected", "source": self.name, "stale": True,
                            "signals": self._last_signals, "faults": self._faults}
                raise RuntimeError(
                    f"no SLABS response for {self._empty_streak} polls — lost session")
            self._empty_streak = 0
            signals = _slabs_sig(_slabs_decode_store(self._raws))
            self._last_signals = signals  # save for the grace period on an empty cycle
            # Fault codes cost two extra frames (21 11 + 21 47) → their own, very slow
            # cadence in SECONDS. A global fault-watch must not speed up SLABS.
            if self._read_faults and (now - self._last_fault) >= _SLABS_FAULT_PERIOD:
                self._last_fault = now
                try:
                    self._faults = _slabs_faults_flat(self._slabs.read_faults())
                except Exception:  # noqa: BLE001
                    pass
            self._tick += 1
            return {"status": "connected", "source": self.name,
                    "signals": signals, "faults": self._faults}
        except Exception as exc:  # noqa: BLE001
            try:
                if self._slabs is not None:
                    self._slabs.release()  # tear down the link (82) — otherwise 7F 81 10 on reconnect
            except Exception:  # noqa: BLE001
                pass
            self._slabs = None
            return {"status": "error", "source": self.name, "signals": {}, "faults": [],
                    "error": f"{type(exc).__name__}: {exc}"}

    def command(self, action: str, params: "dict | None" = None) -> "dict":
        if action == "read_block":
            return _read_block_cmd(self._slabs, params)
        if self._slabs is None:
            return {"ok": False, "error": "not connected to SLABS"}
        try:
            if action == "clear_faults":
                self._slabs.clear_faults()
                self._tick = 0
                return {"ok": True, "message": "Fault codes cleared"}
            if action in _SLABS_ACTUATORS:
                _slabs_do(self._slabs, action)
                return {"ok": True, "message": f"{_SLABS_ACTUATORS[action]} ✓"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        return {"ok": False, "error": f"unknown command: {action}"}

    def menu_map(self) -> "list":
        from .slabs.menu import SLABS_MENU
        return SLABS_MENU


# Live messages of the modules with no live-signal reader yet (faults/info only): they are
# selectable and report honestly that they are not readable on the car yet.
INFO_MESSAGES = {
    "airbag": ("Airbag/SRS is read-only by construction; live fault read is experimental "
               "and not wired into the dashboard yet. Use 'Scan all modules'."),
    "ace": "ACE uses a proprietary bulk protocol that isn't decoded yet.",
    "autobox": "The EAT gearbox answers but its fault payload isn't decoded yet.",
    "bcu": ("The BCU has no conventional fault memory; its inputs/outputs aren't "
            "wired into the dashboard yet."),
}


def make_sources(port: str, *, raw_log_dir: "str | None" = None,
                 state_dir: "str | None" = None, module_ids=None) -> "dict":
    """The car's sources ``{module id: DataSource}`` (the pack's ``sources`` factory).

    ``state_dir`` holds the fuel computer's lifetime total (``fuel_totals.json``).
    ``module_ids`` fixes the key order (the pack passes its ``modules`` order).
    """
    fuel_state_path = os.path.join(state_dir, "fuel_totals.json") if state_dir else None
    built = {
        "td5": lambda: Td5DataSource(port, raw_log_dir=raw_log_dir,
                                     fuel_state_path=fuel_state_path),
        "slabs": lambda: SlabsDataSource(port, raw_log_dir=raw_log_dir),
        **{m: (lambda m=m: InfoDataSource(m, live_message=msg)) for m, msg in INFO_MESSAGES.items()},
    }
    order = list(module_ids) if module_ids else list(built)
    return {m: built[m]() for m in order if m in built}
