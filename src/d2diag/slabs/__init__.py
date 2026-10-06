"""SLABS layer (Wabco ABS/SLS) — fast init 0x29, proven from sniffed reference tool traffic.

See ``references/slabs/overview.md``. Connection:
``d2diag.kline_profiles.open_session("slabs", transport)`` (the module's K-line profile).
"""
from .faults import SLABS_FAULT_BITS, decode_fault_block
from .slabs import SLABS_ADDRESS, Slabs

__all__ = ["Slabs", "SLABS_ADDRESS", "decode_fault_block", "SLABS_FAULT_BITS"]
