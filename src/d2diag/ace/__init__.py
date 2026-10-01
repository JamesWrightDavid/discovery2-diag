"""ACE layer (Lucas Active Cornering Enhancement) — menu data first.

The protocol layer is built after an ACE sniff. See `references/menus/ace.md`
(ACE section) and the fault code dictionary (the dictionary, ACE 0001–0048).
"""
from .menu import ACE_MENU

__all__ = ["ACE_MENU"]
