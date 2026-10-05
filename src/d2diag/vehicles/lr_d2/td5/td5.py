"""Td5 layer: Td5-specific logic on top of KWP2000.

Diagnostic session, SecurityAccess (seed→key) and reading of identifiers with
scaling to physical values (rpm, temperatures, battery voltage, injector balance …).
The scaling comes from the protocol reference — should be confirmed against the car.
"""
from __future__ import annotations

import time
from typing import Callable

from d2diag.session import EcuSession
from .identifiers import BY_NAME, LIDS, decode_lid
from .keygen import key_bytes_from_seed

TD5_DIAGNOSTIC_SESSION = 0xA0
_SECURITY_LEVEL_SEED = 0x01
_SECURITY_LEVEL_KEY = 0x02

# Fault codes: Td5 reads them as a status block via ReadDataByLocalIdentifier 0x3B
# (not standard DTC services) and clears them via StartRoutine 0xDD with 18 zero bytes.
# Derived from the Ekaitza sniff (Read_Faults.log / Read_Faults_and_clear.log).
FAULT_LID = 0x3B
_CLEAR_FAULTS_ROUTINE = 0xDD
_CLEAR_FAULTS_PADDING = b"\x00" * 18

# Output tests — PROVEN from sniff 2026-08-08 (session.log, RDL 016). The reference tool
# pulses TD5 outputs via IOControl `30 <lid> ff`; wastegate/EGR take PWM parameters.
# The injector click is StartRoutine `31 C2 0<n>`. All respond `70/71 <id>` (ack, no data).
_OUTPUTS: "dict[str, tuple[int, bytes]]" = {
    "fuel_pump":   (0xA1, b"\xff"),
    "mil_lamp":    (0xA2, b"\xff"),
    "ac_clutch":   (0xA3, b"\xff"),
    "ac_fan":      (0xA4, b"\xff"),
    "glow_plugs":  (0xB3, b"\xff"),
    "rev_counter": (0xB7, b"\xff"),
    "temp_gauge":  (0xBA, b"\xff"),
    "egr_throttle": (0xBD, b"\xff\x00\xfa\x13\x88"),  # PWM parameters (duty/frequency)
    "wastegate":   (0xBE, b"\xff\x00\x0a\x13\x88"),
}
OUTPUT_NAMES: "tuple[str, ...]" = tuple(_OUTPUTS)  # the dashboard's `output_<name>` actions
_INJECTOR_ROUTINE = 0xC2       # `31 C2 0<n>` — pulse injector n (1–5)
INJECTOR_CYLINDERS = (1, 2, 3, 4, 5)
_SECURITY_ROUTINE = 0xC0       # `31 C0` start, `33 C0` read status (03 = not immobilised)

# ReadEcuIdentification `1A xx` — the four blocks read on D2-JW 2026-10-04 (T-06, see
# references/test-plan-resolved.md). Text is ASCII, numbers are packed BCD.
_READ_ECU_ID = 0x1A
ID_VIN_BLOCK = 0x87            # VIN + build date + software number (46 bytes)
ID_PART_BLOCK = 0x9A           # ECU part number "NNN" + BCD (6 bytes)
IDENTITY_OPTIONS = (ID_VIN_BLOCK, ID_PART_BLOCK, 0x9B, 0x9C)


def _bcd(data: bytes) -> "str | None":
    """Packed BCD → digit string, or None if any nibble is not a decimal digit."""
    out = []
    for b in data:
        hi, lo = b >> 4, b & 0x0F
        if hi > 9 or lo > 9:
            return None
        out.append(f"{hi}{lo}")
    return "".join(out)


def _ascii(data: bytes) -> str:
    return data.decode("ascii", "replace").strip("\x00 ").strip()


def mask_vin(vin: str) -> str:
    """Keep only the last 4 characters: ``*************1234``. The full VIN never leaves
    :func:`decode_identity` (not logged, not in CSV, not in community uploads)."""
    vin = vin.strip()
    return "*" * max(len(vin) - 4, 0) + vin[-4:]


def decode_identity(blocks: "dict[int, bytes]") -> "dict[str, object]":
    """Decode the ``1A`` blocks (option → data after ``5A <opt>``) into identity fields.

    Layout from references/test-plan-resolved.md (T-06, 2026-10-04):

    * ``1A 9A``: ``"NNN"`` + 3 BCD bytes → ``part_no`` (e.g. ``NNN000130``) — matches the
      factory tool's "ECU Part Number" form.
    * ``1A 87``: @0-10 ASCII = first 11 VIN characters, @11-13 BCD = 6-digit serial
      (candidate) → ``vin_masked`` only; @15-18 BCD ``DDMMYYYY`` → ``build_date``
      (candidate: build or programming date); @20-25 ``"NNW"`` + BCD → ``software_no``
      (candidate meaning).
    * ``1A 9B`` / ``1A 9C``: one byte each, meaning open → hex ``id_9b`` / ``id_9c``.

    The full VIN is assembled only to be masked; it is never returned.
    """
    ident: "dict[str, object]" = {"part_no": None, "vin_masked": None, "build_date": None,
                                  "software_no": None, "id_9b": None, "id_9c": None}
    part = blocks.get(ID_PART_BLOCK)
    if part is not None and len(part) >= 6:
        digits = _bcd(part[3:6])
        ident["part_no"] = _ascii(part[:3]) + (digits if digits is not None else part[3:6].hex())
    vin_blk = blocks.get(ID_VIN_BLOCK)
    if vin_blk is not None and len(vin_blk) >= 11:
        serial = _bcd(vin_blk[11:14]) if len(vin_blk) >= 14 else None
        ident["vin_masked"] = mask_vin(_ascii(vin_blk[:11]) + (serial or ""))
        if len(vin_blk) >= 19:
            d = _bcd(vin_blk[15:19])
            if d is not None:
                ident["build_date"] = f"{d[4:8]}-{d[2:4]}-{d[0:2]}"   # DDMMYYYY → ISO
        if len(vin_blk) >= 26:
            sw = _bcd(vin_blk[23:26])
            if sw is not None:
                ident["software_no"] = _ascii(vin_blk[20:23]) + sw
    for opt, key in ((0x9B, "id_9b"), (0x9C, "id_9c")):
        if blocks.get(opt) is not None:
            ident[key] = blocks[opt].hex(" ")
    ident["candidate_fields"] = ["vin_masked", "build_date", "software_no"]
    return ident

# Defaults for establish(): bus idle before init and number of full retries.
_DEFAULT_IDLE = 5.0
_DEFAULT_ATTEMPTS = 6


class Td5(EcuSession):
    name = "Td5"
    _has_session = True  # StartDiagnosticSession 0xA0 → must be closed cleanly on module switch

    # lifecycle (open/close/context) + read_block/tester_present inherited from EcuSession

    def start_session(self) -> bytes:
        """StartDiagnosticSession in the Td5's diagnostic mode (0xA0)."""
        return self._kwp.start_diagnostic_session(TD5_DIAGNOSTIC_SESSION)

    def unlock(self) -> None:
        """SecurityAccess: fetch seed, compute key, send key."""
        seed = self._kwp.request_seed(_SECURITY_LEVEL_SEED)
        if len(seed) < 2:
            raise ValueError(f"unexpected seed length: {seed.hex(' ')}")
        key = key_bytes_from_seed(seed[0], seed[1])
        self._kwp.send_key(key, _SECURITY_LEVEL_KEY)

    def connect(self) -> None:
        """StartDiagnosticSession + SecurityAccess unlock.

        Assumes established communication (fast init already done). After this
        the ECU is unlocked and ``21 xx`` reading works."""
        self.start_session()
        self.unlock()

    def establish(
        self,
        *,
        idle: float = _DEFAULT_IDLE,
        attempts: int = _DEFAULT_ATTEMPTS,
        sleep: Callable[[float], None] = time.sleep,
        progress: "Callable[[str], None] | None" = None,
    ) -> bytes:
        """Full connection: bus idle → tolerant fast init (search for C1) → session →
        unlock (via :meth:`connect`). Retries the whole sequence on noise and
        returns the C1 data field.

        Best against a fresh ECU (ignition cycle just before). ``sleep`` is injected
        for testability. Raises :class:`KWP2000Error` if it fails after
        ``attempts`` attempts. A half-open session responds ``7F`` to
        StartCommunication but can still be unlocked — so an empty C1 is tolerated
        (see :meth:`EcuSession._establish`)."""
        return self._establish(
            after=self.connect, idle=idle, attempts=attempts, retry_sleep=8.0,
            sleep=sleep, progress=progress,
        )

    # ---- reading of live data ---------------------------------------- #
    def read_lid(self, lid: int) -> "dict[str, float]":
        """Read an identifier (21 xx) and decode all signals in it."""
        return decode_lid(lid, self._kwp.read_local_identifier(lid))

    def read(self, name: str) -> float:
        """Read a single signal by name, e.g. 'rpm' or 'coolant_temp'."""
        return self.read_lid(BY_NAME[name].lid)[name]

    def read_all(self) -> "dict[str, float]":
        """Read all known LIDs → {signal_name: value}. A LID that fails is skipped."""
        out: "dict[str, float]" = {}
        for lid in LIDS:
            try:
                out.update(self.read_lid(lid))
            except Exception:  # noqa: BLE001
                pass
        return out

    # ---- fault codes -------------------------------------------------- #
    def read_faults_raw(self) -> bytes:
        """Read the Td5's fault status block (raw bytes after ``61 3B``) via 0x21 0x3B.

        Requires an unlocked session. The block is bit-coded; named decoding is done by
        :func:`d2diag.td5.faults.decode_faults`."""
        return self._kwp.read_local_identifier(FAULT_LID)

    def read_faults(self) -> "list[str]":
        """Read and decode active faults into a list of descriptions (unknown bits tagged
        (Current)/(Logged) by their byte, see :func:`~d2diag.td5.faults.tag_unknown`)."""
        from .faults import decode_faults, tag_unknown

        return tag_unknown(decode_faults(self.read_faults_raw()))

    def clear_faults(self) -> None:
        """Clear stored fault codes (StartRoutine 0xDD). Requires an unlocked session."""
        self._kwp.start_routine(_CLEAR_FAULTS_ROUTINE, _CLEAR_FAULTS_PADDING)

    # ---- output tests (require a TRANSMITTING cable) ------------------ #
    def output_names(self) -> "list[str]":
        """Names of the known output tests (for UI/CLI)."""
        return list(_OUTPUTS)

    def output_test(self, name: str) -> None:
        """Pulse a TD5 output (IOControl). ``name`` from :meth:`output_names`.

        ⚠️ Active test — only run stationary, ignition on. Byte-exact against
        the sniff (e.g. ``ac_clutch`` → ``30 A3 FF``)."""
        try:
            lid, params = _OUTPUTS[name]
        except KeyError:
            raise ValueError(f"unknown TD5 output: {name!r}") from None
        self._kwp.io_control(lid, params)

    def injector_pulse(self, cylinder: int) -> None:
        """Pulse an injector for an audible click (StartRoutine ``31 C2 0<n>``).

        ``cylinder`` 1–5. ⚠️ Active test, engine off."""
        if not 1 <= cylinder <= 5:
            raise ValueError("cylinder must be 1–5")
        self._kwp.start_routine(_INJECTOR_ROUTINE, bytes([cylinder]))

    # ---- immobiliser/security ----------------------------------------- #
    def security_status_raw(self) -> bytes:
        """`31 C0` start + `33 C0` read; returns the ``73`` reply data (echoed ``C0`` then the
        status byte). Read-only (ADR-0008: the NanoCom's 'GET SECURITY STATUS')."""
        self._kwp.start_routine(_SECURITY_ROUTINE)
        return self._kwp.request_routine_results(_SECURITY_ROUTINE)

    def security_status(self) -> int:
        """Read immobiliser status (`31 C0` start + `33 C0` read). Returns
        the status byte — **0x03 = not immobilised** (proven RDL 016). Read-only.

        (Corresponds to the reference tool's 'GET SECURITY STATUS'. 'LEARN SECURITY CODE' is a
        different, state-changing routine and is deliberately not implemented.)"""
        result = self.security_status_raw()
        # the response starts with the echoed routine id (C0), followed by the status byte
        return result[1] if len(result) >= 2 else -1

    # ---- identity (1A xx) — read-only -------------------------------- #
    def read_ecu_id(self, option: int) -> bytes:
        """ReadEcuIdentification ``1A <option>``; the data after the echoed option byte."""
        return self._kwp.request(_READ_ECU_ID, bytes([option]))[1:]

    def read_identity(self) -> "dict[str, object]":
        """Read the four ``1A`` blocks and decode them (:func:`decode_identity`).

        A block that fails is skipped and named in ``errors`` by exception type only —
        never the message, which could quote raw reply bytes (the VIN block)."""
        blocks: "dict[int, bytes]" = {}
        errors: "dict[str, str]" = {}
        for opt in IDENTITY_OPTIONS:
            try:
                blocks[opt] = self.read_ecu_id(opt)
            except Exception as exc:  # noqa: BLE001
                errors[f"{opt:02x}"] = type(exc).__name__
        ident = decode_identity(blocks)
        del blocks  # drop the raw VIN block as early as possible
        if errors:
            ident["errors"] = errors
        return ident

    # convenience
    def rpm(self) -> float:
        return self.read("rpm")

    def coolant_temp(self) -> float:
        return self.read("coolant_temp")

    def battery_voltage(self) -> float:
        return self.read("battery")
