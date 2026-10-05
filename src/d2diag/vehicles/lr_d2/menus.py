"""Discovery 2 module menus: every NanoCom function per module (ADR-0008).

Each module's ``*/menu.py`` lists groups (``id``, ``page``, ``cat``, optional ``parent`` and
``nanocom``) of items that link a signal-store field (``sig``), registry actions
(``actions``) or, when unlinked, carry a hand ``status``. The platform catalog
(:mod:`d2diag.catalog`) derives each item's status and safety from those links.

Reached lazily through ``PACK.menus`` (the module menus import ``td5``, which reads the
signal store at import time).
"""
from __future__ import annotations

from .ace.menu import ACE_MENU
from .airbag.menu import AIRBAG_MENU
from .autobox.menu import AUTOBOX_MENU
from .bcu.menu import BCU_MENU
from .slabs.menu import SLABS_MENU
from .td5.menu import TD5_MENU

# Order = display order in the dashboard's coverage-map picker.
MENUS: "dict[str, list]" = {
    "td5": TD5_MENU,
    "slabs": SLABS_MENU,
    "bcu": BCU_MENU,
    "ace": ACE_MENU,
    "autobox": AUTOBOX_MENU,
    "airbag": AIRBAG_MENU,
}
