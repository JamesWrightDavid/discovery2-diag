# SPDX-FileCopyrightText: 2026 OpenOstler contributors
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""VSS metrics on the D2 signal store (ADR-0016, U0 seams spec §D).

Every ``metric`` in the pack must resolve through ``openostler.metrics.is_known``; the
common-set fields carry the expected path; and within a module a metric names one field
(length variants of the same field may share it). Skips on a platform without metrics.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

metrics = pytest.importorskip("openostler.metrics")

_STORE = Path(__file__).resolve().parents[1] / "src" / "d2diag" / "signals"

EXPECTED = {
    ("td5", "rpm"): "Vehicle.Powertrain.CombustionEngine.Speed",
    ("td5", "speed"): "Vehicle.Speed",
    ("td5", "battery"): "Vehicle.LowVoltageBattery.CurrentVoltage",
    ("td5", "coolant_temp"): "Vehicle.Powertrain.CombustionEngine.EngineCoolant.Temperature",
    ("td5", "ext_temp"): "Vehicle.Exterior.AirTemperature",
    ("td5", "manifold_press"): "Vehicle.Powertrain.CombustionEngine.MAP",
    ("td5", "ambient_press_1"): "Vehicle.Exterior.AirPressure",
    ("td5", "maf_sensor"): "Vehicle.Powertrain.CombustionEngine.MAF",
    ("td5", "accel_pedal_pct"): "Vehicle.Chassis.Accelerator.PedalPosition",
    ("slabs", "battery"): "Vehicle.LowVoltageBattery.CurrentVoltage",
    ("slabs", "transfer_low"): "Vehicle.Powertrain.Transmission.IsLowRangeEngaged",
    ("slabs", "height_left"): "Vehicle.Ostler.Chassis.RideHeight.RearLeftRaw",
    ("slabs", "height_right"): "Vehicle.Ostler.Chassis.RideHeight.RearRightRaw",
}

# Pack-private or not-yet-canonical fields that must stay unmapped.
UNMAPPED = [
    ("td5", "balance_1"), ("td5", "injection_qty"), ("td5", "maf"), ("td5", "battery_direct"),
    ("td5", "ambient_press_2"), ("slabs", "wheel_speed_fl"), ("slabs", "ecu_supply"),
]


def _records():
    for p in sorted(_STORE.glob("*.json")):
        for r in json.loads(p.read_text(encoding="utf-8")):
            yield p.stem, r


def test_every_metric_resolves():
    bad = [(m, r["name"], r["metric"]) for m, r in _records()
           if "metric" in r and not metrics.is_known(r["metric"])]
    assert not bad, f"unknown VSS paths: {bad}"


def test_common_set_fields_have_expected_metric():
    got = {(m, r["name"]): r.get("metric") for m, r in _records()}
    for key, path in EXPECTED.items():
        assert key in got, f"{key} missing from the store"
        assert got[key] == path, f"{key}: {got[key]!r} != {path!r}"
    # Every record of a mapped name carries it (length variants included).
    for m, r in _records():
        if (m, r["name"]) in EXPECTED:
            assert r.get("metric") == EXPECTED[(m, r["name"])], (m, r["name"], r.get("offset"))


def test_only_expected_fields_are_mapped():
    mapped = {(m, r["name"]) for m, r in _records() if "metric" in r}
    assert mapped == set(EXPECTED)
    for key in UNMAPPED:
        assert key not in mapped


def test_metric_unique_per_module():
    owners: "dict[tuple[str, str], set[str]]" = defaultdict(set)
    for m, r in _records():
        if "metric" in r:
            owners[(m, r["metric"])].add(r["name"])
    dup = {k: v for k, v in owners.items() if len(v) > 1}
    assert not dup, f"one metric mapped by several fields in a module: {dup}"
