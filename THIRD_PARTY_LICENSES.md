# Third-party licenses and sources

## td5keygen — SecurityAccess seed→key

`src/d2diag/td5/keygen.py` is a Python port of the algorithm in
[pajacobson/td5keygen](https://github.com/pajacobson/td5keygen).

> BSD 2-Clause License
>
> Copyright (c) 2017, paul@discotd5.com
> Python-variant (keytool.py): Copyright (c) 2017, xabiergarmendia@gmail.com
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions are met:
>
> 1. Redistributions of source code must retain the above copyright notice, this
>    list of conditions and the following disclaimer.
> 2. Redistributions in binary form must reproduce the above copyright notice,
>    this list of conditions and the following disclaimer in the documentation
>    and/or other materials provided with the distribution.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
> ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
> WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
> DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
> ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
> (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
> LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
> ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
> (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
> SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Ekaitza_Itzali — protocol reference (no code used)

[EA2EGA/Ekaitza_Itzali](https://github.com/EA2EGA/Ekaitza_Itzali) has been used as a
**reference for protocol facts** (frame format, ECU addresses, init sequence,
identifiers + scaling, plus the fault-code map for `21 3B` — offset/bitmask →
fault text, which are facts about the ECU's diagnostics). No source code from there is
copied — the repo has no license, so only non-protectable facts about the protocol have been used.
The init/session/security/fault-code sequences are moreover verified against the repo's
sniff logs (`Sniffing/*.log`). Credits in that project go to OffTrack
(ECU disassembly) and Luca72 (Arduino reference).

The Td5 fault-code map (`21 3B`) is additionally **cross-validated against a public,
community-spread list of Td5 fault codes** — same names on the same offset/bit,
which also yielded the more precise status distinction Logged Low / Logged High /
Current. Only factual data (offset/bit → fault text) has been used.

## BinOwl_Td5Gauge — protocol reference (GPL-3.0, no code used)

[k0sci3j/BinOwl_Td5Gauge](https://github.com/k0sci3j/BinOwl_Td5Gauge) — an ESP32 Td5
gauge, **GPL-3.0**. Reviewed 2026-08-25 as a **reference for protocol facts only**
(LID -> field offsets and scalings, frame lengths, init/keepalive sequence); see
`references/td5-external-findings.md`. When this was reviewed the project
was MIT-licensed, so only non-protectable facts about the ECU protocol were used, each
verified against our own captures. Since ADR-0012 the project is AGPL-3.0-or-later, which
is compatible with GPL-3.0: code could now be reused **with** its GPL-3.0 notice and
attribution recorded here — none has been so far.

## muki01/OBD2_K-line_Reader — K-line reference (MIT snapshot; upstream now GPL-3.0)

[muki01/OBD2_K-line_Reader](https://github.com/muki01/OBD2_K-line_Reader) — OBD2 K-line
scan-tool firmware (ISO 9141 / ISO 14230) for Arduino/ESP32, © 2023 Muksin Muksin.
**MIT until `91ae045` (2026-10-01); GPL-3.0 (plus a commercial licence) since `aef63b4`
(2026-10-03).** We use the MIT snapshot only and never port from upstream HEAD (ADR-0019).
The companion OBD2_KLine_Library carries non-commercial headers: facts only.
The MIT snapshot (Basic_Code + Schematics, upstream `a1946a7`) is in `references/muki01_OBD2_K-line_Reader/`
as a reference for the ESP32 port (fast init timing, burst reading, L9637D interface). MIT
allows reuse with the copyright and license notice retained; keep this
attribution if code from there is ported in.

## GeoNames — place names in the demo sessions (CC BY 4.0)

The place labels in `src/d2diag/demo/sessions/*/meta.json` were resolved from the
platform's offline gazetteer, which is trimmed from the [GeoNames](https://www.geonames.org/)
`cities1000` and admin-name dumps, licensed **CC BY 4.0**. The gazetteer itself ships with
the platform ([openostler/ostler](https://github.com/openostler/ostler)).
