"""Discovery 2 catalog data: store signals deliberately not linked from any menu item.

The drift guard in ``tests/test_catalog.py`` fails when a store signal is neither linked
from a menu item nor listed here (``PACK.unlinked_ok``).
"""
from __future__ import annotations

UNLINKED_OK: "dict[str, frozenset[str]]" = {
    "td5": frozenset({
        "ext_temp",  # phantom: the sensor is not fitted on the Td5, constant 150 °C (ignore)
    }),
    "slabs": frozenset(),
}
