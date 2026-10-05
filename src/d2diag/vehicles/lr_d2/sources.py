"""Discovery 2 data sources: the Td5 and SLABS live readers and their derived fields.

Phase 0 Step 0 stub: re-exports the objects that still live in
:mod:`d2diag.web.sources` under their frozen names, plus :func:`make_sources` (the pack's
``sources`` factory). Agent B moves the bodies here; the export names are the contract.
This is the one pack file allowed to import ``d2diag.web`` (the consumer boundary).
"""
from __future__ import annotations

import os

from d2diag.web.sources import (  # noqa: F401 — re-exported (frozen names)
    _DIESEL_G_PER_L,
    _INJ_PER_REV,
    _SLABS_ACTUATORS,
    _SLABS_BUS_PERIOD,
    _SLABS_EMPTY_GRACE,
    _SLABS_FAULT_PERIOD,
    DERIVED_FIELDS as _LEGACY_DERIVED_FIELDS,
    TD5_ACTIONS,
    InfoDataSource,
    SlabsDataSource,
    Td5DataSource,
    _conf_map,
    _conf_of,
    _FuelComputer,
    _security_message,
    _sig,
    _slabs_decode_store,
    _slabs_do,
    _slabs_faults_flat,
    _slabs_sig,
)

# Derived (computed, not read from a LID) field metadata, keyed by canonical module id.
# Step 0: the same inner dicts as web.sources.DERIVED_FIELDS ("motor" → "td5").
DERIVED_FIELDS: "dict[str, dict[str, dict]]" = {
    {"motor": "td5"}.get(k, k): v for k, v in _LEGACY_DERIVED_FIELDS.items()}

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
