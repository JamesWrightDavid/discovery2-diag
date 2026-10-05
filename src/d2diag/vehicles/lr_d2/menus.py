"""Discovery 2 module menus: every NanoCom function per module (ADR-0008).

Phase 0 Step 0 stub: references :data:`d2diag.menus.MENUS`. Agent A moves the dict here;
``MENUS`` is the frozen name (display order = the coverage-map picker order).
"""
from __future__ import annotations

from d2diag import menus as _menus

MENUS: "dict[str, list]" = _menus.MENUS
