"""Discovery 2 catalog data: store signals deliberately not linked from any menu item
(the drift guard in ``tests/test_catalog.py``).

Phase 0 Step 0 stub: built from :data:`d2diag.catalog.UNLINKED_OK`. Agent A moves the data
here; ``UNLINKED_OK`` (``{module: frozenset[str]}``) is the frozen name.
"""
from __future__ import annotations

from d2diag import catalog as _catalog

UNLINKED_OK: "dict[str, frozenset[str]]" = {
    m: frozenset(names) for m, names in _catalog.UNLINKED_OK.items()}
