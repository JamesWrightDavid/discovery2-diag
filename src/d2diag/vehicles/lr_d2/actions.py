"""Discovery 2 module actions (the command registry rows).

Phase 0 Step 0 stub: references :data:`d2diag.commands._ALL`. Agent A moves ``_td5_out``,
``ENGINE_OFF``, ``BRAKES`` and the rows here; ``ACTIONS`` is the frozen name.
"""
from __future__ import annotations

from d2diag import commands as _commands

ACTIONS: "tuple[_commands.Command, ...]" = tuple(_commands._ALL)
