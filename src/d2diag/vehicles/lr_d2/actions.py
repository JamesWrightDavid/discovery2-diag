"""Discovery 2 module actions: the command registry rows (ADR-0008).

Every action the dashboard can send to a Discovery 2 module, with its status, safety and
confirmation friction. The platform (:mod:`d2diag.commands`) builds ``registry()`` from
``PACK.actions`` (this ``ACTIONS`` tuple) and judges refusals; this file is data only.
Order is the registry order (``commands.for_module``).
"""
from __future__ import annotations

from d2diag.commands import STATIONARY, Command

# Preconditions shown before an actuator or service action (the UI ticks them off).
ENGINE_OFF = STATIONARY + ("Engine off",)
BRAKES = STATIONARY + ("Brake bleed in progress (fluid topped up, bleed nipples ready)",)


def _td5_out(action: str, label: str, ref: str, **kw) -> Command:
    return Command(action, "td5", label, ref=ref, preconditions=ENGINE_OFF, **kw)


ACTIONS: "tuple[Command, ...]" = (
    # ---- Td5: outputs (IOControl 30 xx), injector click (31 C2 0n) — experimental ----
    _td5_out("output_fuel_pump", "Fuel pump", "30 A1 FF"),
    _td5_out("output_mil_lamp", "MIL lamp", "30 A2 FF", confirm="none"),
    _td5_out("output_ac_clutch", "A/C clutch", "30 A3 FF"),
    _td5_out("output_ac_fan", "A/C fan", "30 A4 FF"),
    _td5_out("output_glow_plugs", "Glow plugs", "30 B3 FF"),
    _td5_out("output_rev_counter", "Rev counter", "30 B7 FF", confirm="none"),
    _td5_out("output_temp_gauge", "Temp gauge", "30 BA FF", confirm="none"),
    _td5_out("output_egr_throttle", "EGR throttle", "30 BD FF 00 FA 13 88"),
    _td5_out("output_wastegate", "Wastegate modulator", "30 BE FF 00 0A 13 88"),
    *[_td5_out(f"injector_{n}", f"Injector {n} click", f"31 C2 0{n}") for n in range(1, 6)],
    # ---- Td5: utilities ----
    Command("security_status", "td5", "Get security status", safety="read", confirm="preconditions",
            preconditions=("Ignition on",), ref="31 C0 → 33 C0 (read-only)"),
    Command("read_identity", "td5", "Read ECU identity", safety="read", confirm="none",
            preconditions=(), ref="1A 87 / 1A 9A / 1A 9B / 1A 9C (VIN never logged)"),
    Command("learn_security_code", "td5", "Learn security code", status="planned", safety="gated",
            confirm="typed", ref="never sent (immobiliser state change)"),
    # ---- SLABS: outputs (simple tests) — verified on RDL 016 ----
    Command("buzzer", "slabs", "Buzzer test", status="verified", confirm="none", ref="31 31 0A"),
    Command("compressor", "slabs", "Compressor test", status="verified", ref="31 30 28"),
    Command("exhaust", "slabs", "Exhaust valve test", status="verified", ref="31 2F 28"),
    Command("pump_on", "slabs", "ABS pump on", status="verified", stop="pump_off", ref="31 25 08 FA"),
    Command("pump_off", "slabs", "ABS pump off", status="verified", confirm="none", preconditions=(),
            ref="31 25 02 FA"),
    # ---- SLABS: utilities — bleed and height (service) ----
    *[Command(f"wheel_{c}", "slabs", f"Wheel test {c.upper()}", status="verified", safety="service",
              ref=r) for c, r in (("fl", "31 22 11 0C"), ("fr", "31 22 10 03"),
                                  ("rl", "31 22 13 C0"), ("rr", "31 22 12 30"))],
    Command("bleed_power_on", "slabs", "Power bleed — start", status="verified", safety="service",
            preconditions=BRAKES, stop="bleed_power_off", ref="31 22 04 00 49 C4"),
    Command("bleed_power_off", "slabs", "Power bleed — stop", status="verified", safety="service",
            confirm="none", preconditions=(), ref="31 22 04 00 40 00"),
    Command("bleed_module", "slabs", "Modulator bleed (4 steps)", status="verified", safety="service",
            preconditions=BRAKES, ref="31 22 11..14"),
    *[Command(f"{d}_{s}", "slabs", f"{d.capitalize()} {s} corner", status="verified", safety="service",
              ref=r) for d, s, r in (("raise", "left", "31 33 28"), ("raise", "right", "31 34 28"),
                                    ("lower", "left", "31 35 28"), ("lower", "right", "31 36 28"))],
    Command("store_heights", "slabs", "Store target heights", status="planned", safety="gated",
            confirm="typed", ref="writes calibration — needs its own ADR"),
    # ---- BCU (all security functions gated by ADR-0007) ----
    Command("eka_read", "bcu", "Read EKA code", status="planned", safety="gated", confirm="typed",
            ref="21 CC behind SecurityAccess (ADR-0007)"),
    Command("eka_set", "bcu", "Set EKA code", status="planned", safety="gated", confirm="typed",
            ref="3B CC — never sent"),
    Command("key_program", "bcu", "Key programming", status="planned", safety="gated", confirm="typed",
            ref="never sent"),
    # ---- ACE / autobox: known from the NanoCom, not wired ----
    Command("ace_calibrate_1", "ace", "Calibrate accelerometer 1", status="planned", safety="gated",
            confirm="typed", ref="15 15 FF — writes calibration"),
    Command("ace_calibrate_2", "ace", "Calibrate accelerometer 2", status="planned", safety="gated",
            confirm="typed", ref="16 16 FF — writes calibration"),
    Command("ace_set_calibrated", "ace", "Set calibrated", status="planned", safety="gated",
            confirm="typed", ref="10 10 00 — reported to lock up ACE ECUs"),
    Command("ace_bleed", "ace", "Oil bleed (3 steps)", status="planned", safety="service", ref="not captured"),
    Command("autobox_reset_adaptives", "autobox", "Reset adaptive values", status="planned",
            safety="service", ref="72 06 83 FF 07 08 FF (undecoded)"),
)
