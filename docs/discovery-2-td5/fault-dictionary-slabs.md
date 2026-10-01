---
title: "SLABS (ABS/SLS) fault dictionary"
area: docs
status: stable
version: 1.0
updated: 2026-10-01
summary: >
  Generated fault dictionary for the slabs module — every known code with its meaning, likely cause, severity and (inferred) P-code. Generated from src/d2diag/dtc/slabs.json; do not hand-edit.
---


# SLABS (ABS/SLS) fault dictionary

_Generated from the fault-meaning store (`src/d2diag/dtc/slabs.json`) — do not edit by hand; refine the store and re-run `tools/gen_fault_docs.py`._

| Code | Fault | P-code | Severity | Meaning | Likely cause |
|---|---|---|---|---|---|
| `012` | Pump Fail — Monitor Line | — | — | Pump Fail — Monitor Line (SLABS ABS/SLS fault 012). | Pump monitor line fault — check the monitor wiring. |
| `013` | Pump Fail — Pump Not Running When On | — | — | Pump Fail — Pump Not Running When On (SLABS ABS/SLS fault 013). | Pump commanded on but not running — check the pump, relay and supply. |
| `014` | Pump Fail — Pump Sticking | — | — | Pump Fail — Pump Sticking (SLABS ABS/SLS fault 014). | Mechanical sticking — inspect the valve/pump. |
| `015` | Pump Fail — Pump Running When Not On | — | — | Pump Fail — Pump Running When Not On (SLABS ABS/SLS fault 015). | Pump running when off — check the relay and pump drive. |
| `016` | Shuttle Valve Switch Long Term Failure | — | — | Shuttle Valve Switch Long Term Failure (SLABS ABS/SLS fault 016). | See the workshop manual fault-finding for this circuit. |
| `017` | ECU Internal Valve Relay Bad | — | — | ECU Internal Valve Relay Bad (SLABS ABS/SLS fault 017). | Internal valve relay fault — ECU suspect. |
| `020` | No Batt Supply Voltage | — | — | No Batt Supply Voltage (SLABS ABS/SLS fault 020). | See the workshop manual fault-finding for this circuit. |
| `021` | Engine PWM Signal Bad | — | — | Engine PWM Signal Bad (SLABS ABS/SLS fault 021). | See the workshop manual fault-finding for this circuit. |
| `022` | ECU Gnd or Reference Gnd Bad | — | — | ECU Gnd or Reference Gnd Bad (SLABS ABS/SLS fault 022). | See the workshop manual fault-finding for this circuit. |
| `023` | Gear Info Not Valid | — | — | Gear Info Not Valid (SLABS ABS/SLS fault 023). | See the workshop manual fault-finding for this circuit. |
| `030` | Front Right In Valve — Open Circuit | — | — | Front Right In Valve — Open Circuit (SLABS ABS/SLS fault 030). | Open circuit — check the component and its wiring/connector. |
| `031` | Front Right Out Valve — Open Circuit | — | — | Front Right Out Valve — Open Circuit (SLABS ABS/SLS fault 031). | Open circuit — check the component and its wiring/connector. |
| `032` | Front Left In Valve — Open Circuit | — | — | Front Left In Valve — Open Circuit (SLABS ABS/SLS fault 032). | Open circuit — check the component and its wiring/connector. |
| `033` | Front Left Out Valve — Open Circuit | — | — | Front Left Out Valve — Open Circuit (SLABS ABS/SLS fault 033). | Open circuit — check the component and its wiring/connector. |
| `034` | Rear Right In Valve — Open Circuit | — | — | Rear Right In Valve — Open Circuit (SLABS ABS/SLS fault 034). | Open circuit — check the component and its wiring/connector. |
| `035` | Rear Right Out Valve — Open Circuit | — | — | Rear Right Out Valve — Open Circuit (SLABS ABS/SLS fault 035). | Open circuit — check the component and its wiring/connector. |
| `036` | Rear Left In Valve — Open Circuit | — | — | Rear Left In Valve — Open Circuit (SLABS ABS/SLS fault 036). | Open circuit — check the component and its wiring/connector. |
| `037` | Rear Left Out Valve — Open Circuit | — | — | Rear Left Out Valve — Open Circuit (SLABS ABS/SLS fault 037). | Open circuit — check the component and its wiring/connector. |
| `040` | Pump Relay — Open Circuit | — | — | Pump Relay — Open Circuit (SLABS ABS/SLS fault 040). | Open circuit — check the component and its wiring/connector. |
| `041` | Brake Light Relay — Open Circuit | — | — | Brake Light Relay — Open Circuit (SLABS ABS/SLS fault 041). | Open circuit — check the component and its wiring/connector. |
| `044` | Front Right Sensor — Output Low | — | — | Front Right Sensor — Output Low (SLABS ABS/SLS fault 044). | Wheel-speed signal low — check the sensor air gap, reluctor ring and wiring. |
| `045` | Rear Left Sensor — Output Low | — | — | Rear Left Sensor — Output Low (SLABS ABS/SLS fault 045). | Wheel-speed signal low — check the sensor air gap, reluctor ring and wiring. |
| `046` | Front Left Sensor — Output Low | — | — | Front Left Sensor — Output Low (SLABS ABS/SLS fault 046). | Wheel-speed signal low — check the sensor air gap, reluctor ring and wiring. |
| `047` | Rear Right Sensor — Output Low | — | — | Rear Right Sensor — Output Low (SLABS ABS/SLS fault 047). | Wheel-speed signal low — check the sensor air gap, reluctor ring and wiring. |
| `050` | Front Right In Valve — Short To Gnd | — | — | Front Right In Valve — Short To Gnd (SLABS ABS/SLS fault 050). | Short to ground — check the wiring for a short to chassis. |
| `051` | Front Right Out Valve — Short To Gnd | — | — | Front Right Out Valve — Short To Gnd (SLABS ABS/SLS fault 051). | Short to ground — check the wiring for a short to chassis. |
| `052` | Front Left In Valve — Short To Gnd | — | — | Front Left In Valve — Short To Gnd (SLABS ABS/SLS fault 052). | Short to ground — check the wiring for a short to chassis. |
| `053` | Front Left Out Valve — Short To Gnd | — | — | Front Left Out Valve — Short To Gnd (SLABS ABS/SLS fault 053). | Short to ground — check the wiring for a short to chassis. |
| `054` | Rear Right In Valve — Short To Gnd | — | — | Rear Right In Valve — Short To Gnd (SLABS ABS/SLS fault 054). | Short to ground — check the wiring for a short to chassis. |
| `055` | Rear Right Out Valve — Short To Gnd | — | — | Rear Right Out Valve — Short To Gnd (SLABS ABS/SLS fault 055). | Short to ground — check the wiring for a short to chassis. |
| `056` | Rear Left In Valve — Short To Gnd | — | — | Rear Left In Valve — Short To Gnd (SLABS ABS/SLS fault 056). | Short to ground — check the wiring for a short to chassis. |
| `057` | Rear Left Out Valve — Short To Gnd | — | — | Rear Left Out Valve — Short To Gnd (SLABS ABS/SLS fault 057). | Short to ground — check the wiring for a short to chassis. |
| `060` | Pump Relay — Short To Gnd | — | — | Pump Relay — Short To Gnd (SLABS ABS/SLS fault 060). | Short to ground — check the wiring for a short to chassis. |
| `061` | Brake Light Relay — Short To Gnd | — | — | Brake Light Relay — Short To Gnd (SLABS ABS/SLS fault 061). | Short to ground — check the wiring for a short to chassis. |
| `064` | Front Right Sensor — Electric Fail | — | — | Front Right Sensor — Electric Fail (SLABS ABS/SLS fault 064). | Wheel-speed sensor electrical failure — check the sensor and wiring. |
| `065` | Rear Left Sensor — Electric Fail | — | — | Rear Left Sensor — Electric Fail (SLABS ABS/SLS fault 065). | Wheel-speed sensor electrical failure — check the sensor and wiring. |
| `066` | Front Left Sensor — Electric Fail | — | — | Front Left Sensor — Electric Fail (SLABS ABS/SLS fault 066). | Wheel-speed sensor electrical failure — check the sensor and wiring. |
| `067` | Rear Right Sensor — Electric Fail | — | — | Rear Right Sensor — Electric Fail (SLABS ABS/SLS fault 067). | Wheel-speed sensor electrical failure — check the sensor and wiring. |
| `070` | Front Right In Valve — Short to Supply | — | — | Front Right In Valve — Short to Supply (SLABS ABS/SLS fault 070). | Short to +12V — check the wiring for a short to supply. |
| `071` | Front Right Out Valve — Short to Supply | — | — | Front Right Out Valve — Short to Supply (SLABS ABS/SLS fault 071). | Short to +12V — check the wiring for a short to supply. |
| `072` | Front Left In Valve — Short to Supply | — | — | Front Left In Valve — Short to Supply (SLABS ABS/SLS fault 072). | Short to +12V — check the wiring for a short to supply. |
| `073` | Front Left Out Valve — Short to Supply | — | — | Front Left Out Valve — Short to Supply (SLABS ABS/SLS fault 073). | Short to +12V — check the wiring for a short to supply. |
| `074` | Rear Right In Valve — Short to Supply | — | — | Rear Right In Valve — Short to Supply (SLABS ABS/SLS fault 074). | Short to +12V — check the wiring for a short to supply. |
| `075` | Rear Right Out Valve — Short to Supply | — | — | Rear Right Out Valve — Short to Supply (SLABS ABS/SLS fault 075). | Short to +12V — check the wiring for a short to supply. |
| `076` | Rear Left In Valve — Short to Supply | — | — | Rear Left In Valve — Short to Supply (SLABS ABS/SLS fault 076). | Short to +12V — check the wiring for a short to supply. |
| `077` | Rear Left Out Valve — Short to Supply | — | — | Rear Left Out Valve — Short to Supply (SLABS ABS/SLS fault 077). | Short to +12V — check the wiring for a short to supply. |
| `080` | Pump Relay — Short To Supply | — | — | Pump Relay — Short To Supply (SLABS ABS/SLS fault 080). | Short to +12V — check the wiring for a short to supply. |
| `081` | Brake Light Relay — Short to Supply | — | — | Brake Light Relay — Short to Supply (SLABS ABS/SLS fault 081). | Short to +12V — check the wiring for a short to supply. |
| `090` | Front Right In Valve — Drive Short to Supply | — | — | Front Right In Valve — Drive Short to Supply (SLABS ABS/SLS fault 090). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `091` | Front Right Out Valve — Drive Short to Supply | — | — | Front Right Out Valve — Drive Short to Supply (SLABS ABS/SLS fault 091). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `092` | Front Left In Valve — Drive Short to Supply | — | — | Front Left In Valve — Drive Short to Supply (SLABS ABS/SLS fault 092). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `093` | Front Left Out Valve — Drive Short to Supply | — | — | Front Left Out Valve — Drive Short to Supply (SLABS ABS/SLS fault 093). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `094` | Rear Right In Valve — Drive Short to Supply | — | — | Rear Right In Valve — Drive Short to Supply (SLABS ABS/SLS fault 094). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `095` | Rear Right Out Valve — Drive Short to Supply | — | — | Rear Right Out Valve — Drive Short to Supply (SLABS ABS/SLS fault 095). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `096` | Rear Left In Valve — Drive Short to Supply | — | — | Rear Left In Valve — Drive Short to Supply (SLABS ABS/SLS fault 096). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `097` | Rear Left Out Valve — Drive Short to Supply | — | — | Rear Left Out Valve — Drive Short to Supply (SLABS ABS/SLS fault 097). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `100` | Pump Relay — Drive Short to Supply | — | — | Pump Relay — Drive Short to Supply (SLABS ABS/SLS fault 100). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `101` | Brake Light Relay — Drive Short to Supply | — | — | Brake Light Relay — Drive Short to Supply (SLABS ABS/SLS fault 101). | Driver short to +12V — suspect the ECU driver or a harness short to supply. |
| `110` | Sticking Throttle Detected | — | — | Sticking Throttle Detected (SLABS ABS/SLS fault 110). | Mechanical sticking — inspect the valve/pump. |
| `111` | Shuttle Valve Sticking | — | — | Shuttle Valve Sticking (SLABS ABS/SLS fault 111). | Mechanical sticking — inspect the valve/pump. |
| `112` | Internal ECU comms error | — | — | Internal ECU comms error (SLABS ABS/SLS fault 112). | See the workshop manual fault-finding for this circuit. |
| `113` | Shuttle Valve Switch Dynamic Failure | — | — | Shuttle Valve Switch Dynamic Failure (SLABS ABS/SLS fault 113). | See the workshop manual fault-finding for this circuit. |
| `114` | Shuttle Valve Switch Electrical Failure | — | — | Shuttle Valve Switch Electrical Failure (SLABS ABS/SLS fault 114). | See the workshop manual fault-finding for this circuit. |

