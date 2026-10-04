"""SLABS fault code decoding.

The fault memory is read as a **16-byte bit-per-fault block** (same technique as the Td5's
`21 3B`), via two identifiers:
  - ``21 11`` = **logged** faults
  - ``21 47`` = **current** faults

A set bit at (byte offset, bit) = one fault. The mapping (byte,bit) → fault text is partly
known: confirmed **anchor points** come from the sniffed session 2026-08-07 where `21 11` had
exactly two bits set that corresponded to the baseline's two faults, and were cleared to zero
after clear. The reference tool showed them as `020-05` and `027-05`, but on NanoCom's SLABS
screen the first field is (on forum evidence) an occurrence count, not a fault number — so
faults are identified by raw bit and text here, never by that number. The other bits are
decoded generically until more anchor points are obtained (e.g. via "provoke a known fault").
See ``references/slabs_fault_codes.md``.
"""
from __future__ import annotations

FAULT_BLOCK_LEN = 16

# Confirmed (byte offset, bit) → fault text. Sniff 2026-08-07:
# 21 11 = `00 00 00 10 00 00 00 00 00 00 10 00 00 00 00 00` (tool showed 020-05 + 027-05).
SLABS_FAULT_BITS: "dict[tuple[int, int], str]" = {
    (3, 4): "right front wheel speed sensor — output too low",
    (10, 4): "shuttle valve switch — electrical failure",
}


def decode_fault_block(block: bytes) -> "list[str]":
    """Decode a 16-byte SLABS fault block into a list of fault texts.

    Known bits yield their text; unknown ones yield ``"unknown (byte i, bit b)"``.
    """
    faults: "list[str]" = []
    for i, byte in enumerate(block[:FAULT_BLOCK_LEN]):
        for b in range(8):
            if byte & (1 << b):
                known = SLABS_FAULT_BITS.get((i, b))
                if known:
                    faults.append(known)
                else:
                    faults.append(f"unknown (byte {i}, bit {b})")
    return faults
