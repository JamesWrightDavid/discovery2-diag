"""Offline BCU SecurityAccess seed→key derivation — maths on captured pairs only.

The Valeo BCU gates its EKA read behind KWP2000 SecurityAccess (``27 01`` seed →
``27 02`` key), with a 2-byte seed that rolls every session. The algorithm ``key =
f(seed)`` is unknown, and — as ``references/valeo_bcu_capabilities.md`` records — it
cannot be recovered from the pairs we have, because getting the *correct* key for a rolled
seed needs a tool that already knows ``f``. A rented NanoCom **is** that tool: sniffing it
unlock the BCU gives many clean ``(seed, key)`` pairs, one per rolled seed.

This module is the offline half: given those pairs, it tries a family of candidate
transforms and reports the one that reproduces **every** pair. It is pure arithmetic on
captured data — it never opens a port or sends a byte. Using a derived key on the live car
is a separate, gated action (ADR-0007), not built here.

A model is only reported when it fits all pairs **and** there are more pairs than the
model has free parameters, so a transform is confirmed, not merely interpolated. With too
few pairs the report says ``unconfirmed`` rather than guessing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

MASK16 = 0xFFFF


def _rotl16(v: int, n: int) -> int:
    n &= 15
    return ((v << n) | (v >> (16 - n))) & MASK16 if n else v & MASK16


def _swap16(v: int) -> int:
    return ((v & 0xFF) << 8) | ((v >> 8) & 0xFF)


def _inv_odd(a: int) -> "int | None":
    """Modular inverse of an odd ``a`` mod 2**16 (None if ``a`` is even)."""
    if a % 2 == 0:
        return None
    return pow(a, -1, 1 << 16)


@dataclass(frozen=True)
class Model:
    """A fitted seed→key transform."""

    name: str
    params: "dict"
    dof: int
    fn: Callable[[int], int]

    def key(self, seed: int) -> int:
        return self.fn(seed & MASK16) & MASK16


# ---- candidate families ------------------------------------------------- #
# Each builder takes the pairs and returns a Model fitted to the FIRST pair(s), or None
# if it cannot be parameterised. fit() then checks the model against all pairs.
def _identity(pairs):
    return Model("identity", {}, 0, lambda s: s)


def _xor_mask(pairs):
    s0, k0 = pairs[0]
    m = (s0 ^ k0) & MASK16
    return Model("xor-mask", {"mask": m}, 1, lambda s, m=m: s ^ m)


def _add_const(pairs):
    s0, k0 = pairs[0]
    c = (k0 - s0) & MASK16
    return Model("add-const", {"const": c}, 1, lambda s, c=c: (s + c) & MASK16)


def _swap_xor(pairs):
    s0, k0 = pairs[0]
    m = (_swap16(s0) ^ k0) & MASK16
    return Model("byteswap-xor", {"mask": m}, 1, lambda s, m=m: _swap16(s) ^ m)


def _rotl_xor(pairs):
    """Rotate-left by n then XOR a mask: search n=1..15, derive the mask from pair 0."""
    s0, k0 = pairs[0]
    for n in range(1, 16):
        m = (_rotl16(s0, n) ^ k0) & MASK16
        model = Model("rotl-xor", {"rot": n, "mask": m}, 1,
                      lambda s, n=n, m=m: _rotl16(s, n) ^ m)
        if all(model.key(s) == k for s, k in pairs):
            return model
    return None


def _affine(pairs):
    """key = (a*seed + b) mod 2**16, a odd. Solved from two pairs with distinct seeds."""
    (s0, k0) = pairs[0]
    for s1, k1 in pairs[1:]:
        ds = (s1 - s0) & MASK16
        inv = _inv_odd(ds)
        if inv is None:
            continue
        a = ((k1 - k0) * inv) & MASK16
        b = (k0 - a * s0) & MASK16
        return Model("affine", {"a": a, "b": b}, 2,
                     lambda s, a=a, b=b: (a * s + b) & MASK16)
    return None


def _td5(pairs):
    """The Td5 LFSR keygen — included so a shared algorithm would be recognised."""
    from ..td5.keygen import key_from_seed
    return Model("td5-lfsr", {}, 0, key_from_seed)


# Simplest first: a lower-dof model that fits is preferred over a richer one.
_FAMILIES = [_identity, _xor_mask, _add_const, _swap_xor, _td5, _rotl_xor, _affine]


def _normalise(pairs) -> "list[tuple[int, int]]":
    out = []
    for s, k in pairs:
        out.append((int(s) & MASK16, int(k) & MASK16))
    return out


def fit(pairs) -> "dict":
    """Find the simplest transform that reproduces every ``(seed, key)`` pair.

    ``pairs``: an iterable of ``(seed, key)`` as 16-bit ints. → a report dict:
    ``{ok, model, params, dof, pairs_used}`` on a confirmed fit, otherwise
    ``{ok: False, reason, pairs_used}``. A model counts as confirmed only when it fits
    all pairs and ``pairs_used > dof`` (more evidence than free parameters).
    """
    norm = _normalise(pairs)
    if len(norm) < 2:
        return {"ok": False, "reason": "need at least 2 pairs to confirm anything",
                "pairs_used": len(norm)}
    if len({s for s, _ in norm}) < 2:
        return {"ok": False, "reason": "all seeds identical — cannot constrain a transform",
                "pairs_used": len(norm)}
    for build in _FAMILIES:
        model = build(norm)
        if model is None:
            continue
        if len(norm) <= model.dof:
            continue  # not enough evidence to confirm this many free parameters
        if all(model.key(s) == k for s, k in norm):
            return {"ok": True, "model": model.name, "params": model.params,
                    "dof": model.dof, "pairs_used": len(norm)}
    return {"ok": False, "reason": "no candidate family fits all pairs",
            "pairs_used": len(norm)}


def build_keygen(report: "dict") -> "Callable[[int], int] | None":
    """Reconstruct the key(seed) callable from a confirmed :func:`fit` report."""
    if not report.get("ok"):
        return None
    name, p = report["model"], report.get("params", {})
    if name == "identity":
        return lambda s: s & MASK16
    if name == "xor-mask":
        return lambda s: (s ^ p["mask"]) & MASK16
    if name == "add-const":
        return lambda s: (s + p["const"]) & MASK16
    if name == "byteswap-xor":
        return lambda s: _swap16(s) ^ p["mask"]
    if name == "rotl-xor":
        return lambda s: _rotl16(s, p["rot"]) ^ p["mask"]
    if name == "affine":
        return lambda s: (p["a"] * s + p["b"]) & MASK16
    if name == "td5-lfsr":
        from ..td5.keygen import key_from_seed
        return key_from_seed
    return None
