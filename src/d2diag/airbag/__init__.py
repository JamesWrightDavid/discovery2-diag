"""Airbag layer (TRW SPS Type 2A, SRS) — menu data first.

🔴 Read-only domain (pyrotechnics). See `references/menus/airbag.md` (Airbag)
and the dictionary (Airbag position=display code, 1–65).
"""
from .airbag import AIRBAG_ADDRESS, Airbag
from .faults import decode_faults
from .menu import AIRBAG_MENU

__all__ = ["AIRBAG_ADDRESS", "AIRBAG_MENU", "Airbag", "decode_faults"]
