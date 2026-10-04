---
title: "Td5 engine fault dictionary"
area: docs
status: stable
version: 1.0
updated: 2026-10-04
summary: >
  Generated fault dictionary for the td5 module — every known code with its meaning, likely cause, severity and (inferred) P-code. Generated from src/d2diag/dtc/td5.json; do not hand-edit.
---


# Td5 engine fault dictionary

_Generated from the fault-meaning store (`src/d2diag/dtc/td5.json`) — do not edit by hand; refine the store and re-run `tools/gen_fault_docs.py`._

| Bit (off.bit) | Fault | Confidence | P-code | Severity | Meaning | Likely cause |
|---|---|---|---|---|---|---|
| `0.0` | egr inlet throttle diagnostics (Logged Low) | proven | P0403 | logged (low/short) | Egr inlet throttle: actuator/feedback diagnostic fault (short/low-side fault logged). | Check the egr inlet throttle actuator, its vacuum/feedback and the wiring. |
| `0.1` | turbocharger wastegate diagnostics (Logged Low) | proven | P0243 | logged (low/short) | Turbocharger wastegate: actuator/feedback diagnostic fault (short/low-side fault logged). | Check the turbocharger wastegate actuator, its vacuum/feedback and the wiring. |
| `0.2` | egr vacuum diagnostics (Logged Low) | proven | P0409 | logged (low/short) | Egr vacuum: actuator/feedback diagnostic fault (short/low-side fault logged). | Check the egr vacuum actuator, its vacuum/feedback and the wiring. |
| `0.3` | temperature gauge diagnostics (Logged Low) | proven | — | logged (low/short) | Temperature gauge: actuator/feedback diagnostic fault (short/low-side fault logged). | Check the temperature gauge actuator, its vacuum/feedback and the wiring. |
| `0.4` | driver demand problem 1 (Logged Low) | proven | P0121 | logged (low/short) | Driver demand problem 1. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `0.5` | driver demand problem 2 (Logged Low) | proven | P0221 | logged (low/short) | Driver demand problem 2. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `0.6` | air flow circuit (Logged Low) | proven | P0100 | logged (low/short) | Air flow circuit: sensor-circuit fault, signal low. | Short to ground or low supply — check the sensor, wiring and connector. |
| `0.7` | manifold pressure circuit (Logged Low) | proven | P0105 | logged (low/short) | Manifold pressure circuit: sensor-circuit fault, signal low. | Short to ground or low supply — check the sensor, wiring and connector. |
| `1.0` | inlet air temp. circuit (Logged Low) | proven | P0110 | logged (low/short) | Inlet air temp. circuit: sensor-circuit fault, signal low. | Short to ground or low supply — check the sensor, wiring and connector. |
| `1.1` | fuel temp. circuit (Logged Low) | proven | P0180 | logged (low/short) | Fuel temp. circuit: sensor-circuit fault, signal low. | Short to ground or low supply — check the sensor, wiring and connector. |
| `1.2` | coolant temp. circuit (Logged Low) | proven | P0115 | logged (low/short) | Coolant temp. circuit: sensor-circuit fault, signal low. | Short to ground or low supply — check the sensor, wiring and connector. |
| `1.3` | battery volts (Logged Low) | proven | P0560 | logged (low/short) | Battery volts. | See the workshop manual fault-finding for this circuit. |
| `1.4` | reference voltage (Logged Low) | proven | P0641 | logged (low/short) | Reference voltage. | See the workshop manual fault-finding for this circuit. |
| `1.5` | ambient air temp. circuit (Logged Low) | proven | P0070 | logged (low/short) | Ambient air temp. circuit: sensor-circuit fault, signal low. | Short to ground or low supply — check the sensor, wiring and connector. |
| `1.6` | driver demand supply problem (Logged Low) | proven | P0641 | logged (low/short) | Driver demand supply problem. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `1.7` | ambient pressure circuit (Logged Low) | proven | P2227 | logged (low/short) | Ambient pressure circuit: sensor-circuit fault, signal low. | Short to ground or low supply — check the sensor, wiring and connector. |
| `2.0` | egr inlet throttle diagnostics (Logged High) | proven | P0403 | logged (high/open) | Egr inlet throttle: actuator/feedback diagnostic fault (open/high-side fault logged). | Check the egr inlet throttle actuator, its vacuum/feedback and the wiring. |
| `2.1` | turbocharger wastegate diagnostics (Logged High) | proven | P0243 | logged (high/open) | Turbocharger wastegate: actuator/feedback diagnostic fault (open/high-side fault logged). | Check the turbocharger wastegate actuator, its vacuum/feedback and the wiring. |
| `2.2` | egr vacuum diagnostics (Logged High) | proven | P0409 | logged (high/open) | Egr vacuum: actuator/feedback diagnostic fault (open/high-side fault logged). | Check the egr vacuum actuator, its vacuum/feedback and the wiring. |
| `2.3` | temperature gauge diagnostics (Logged High) | proven | — | logged (high/open) | Temperature gauge: actuator/feedback diagnostic fault (open/high-side fault logged). | Check the temperature gauge actuator, its vacuum/feedback and the wiring. |
| `2.4` | driver demand problem 1 (Logged High) | proven | P0121 | logged (high/open) | Driver demand problem 1. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `2.5` | driver demand problem 2 (Logged High) | proven | P0221 | logged (high/open) | Driver demand problem 2. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `2.6` | air flow circuit (Logged High) | proven | P0100 | logged (high/open) | Air flow circuit: sensor-circuit fault, signal high. | Open circuit or break — check the sensor, wiring and connector. |
| `2.7` | manifold pressure circuit (Logged High) | proven | P0105 | logged (high/open) | Manifold pressure circuit: sensor-circuit fault, signal high. | Open circuit or break — check the sensor, wiring and connector. |
| `3.0` | inlet air temp. circuit (Logged High) | proven | P0110 | logged (high/open) | Inlet air temp. circuit: sensor-circuit fault, signal high. | Open circuit or break — check the sensor, wiring and connector. |
| `3.1` | fuel temperature circuit (Logged High) | proven | P0180 | logged (high/open) | Fuel temperature circuit: sensor-circuit fault, signal high. | Open circuit or break — check the sensor, wiring and connector. |
| `3.2` | coolant temp. circuit (Logged High) | proven | P0115 | logged (high/open) | Coolant temp. circuit: sensor-circuit fault, signal high. | Open circuit or break — check the sensor, wiring and connector. |
| `3.3` | battery volts (Logged High) | proven | P0560 | logged (high/open) | Battery volts. | See the workshop manual fault-finding for this circuit. |
| `3.4` | reference voltage (Logged High) | proven | P0641 | logged (high/open) | Reference voltage. | See the workshop manual fault-finding for this circuit. |
| `3.5` | ambient air temperature circuit (Logged High) | proven | P0070 | logged (high/open) | Ambient air temperature circuit: sensor-circuit fault, signal high. | Open circuit or break — check the sensor, wiring and connector. |
| `3.6` | driver demand supply problem (Logged High) | proven | P0641 | logged (high/open) | Driver demand supply problem. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `3.7` | ambient pressure circuit (Logged High) | proven | P2227 | logged (high/open) | Ambient pressure circuit: sensor-circuit fault, signal high. | Open circuit or break — check the sensor, wiring and connector. |
| `4.0` | egr inlet throttle diagnostics (Current) | proven | P0403 | current | Egr inlet throttle: actuator/feedback diagnostic fault. | Check the egr inlet throttle actuator, its vacuum/feedback and the wiring. |
| `4.1` | turbocharger wastegate diagnostics (Current) | proven | P0243 | current | Turbocharger wastegate: actuator/feedback diagnostic fault. | Check the turbocharger wastegate actuator, its vacuum/feedback and the wiring. |
| `4.2` | egr vacuum diagnostics (Current) | proven | P0409 | current | Egr vacuum: actuator/feedback diagnostic fault. | Check the egr vacuum actuator, its vacuum/feedback and the wiring. |
| `4.3` | temperature gauge diagnostics (Current) | proven | — | current | Temperature gauge: actuator/feedback diagnostic fault. | Check the temperature gauge actuator, its vacuum/feedback and the wiring. |
| `4.4` | driver demand problem 1 (Current) | proven | P0121 | current | Driver demand problem 1. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `4.5` | driver demand problem 2 (Current) | proven | P0221 | current | Driver demand problem 2. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `4.6` | air flow circuit (Current) | proven | P0100 | current | Air flow circuit: sensor-circuit fault. | Check the sensor, its wiring and connector. |
| `4.7` | manifold pressure circuit (Current) | proven | P0105 | current | Manifold pressure circuit: sensor-circuit fault. | Check the sensor, its wiring and connector. |
| `5.0` | inlet air temp. circuit (Current) | proven | P0110 | current | Inlet air temp. circuit: sensor-circuit fault. | Check the sensor, its wiring and connector. |
| `5.1` | fuel temperature circuit (Current) | proven | P0180 | current | Fuel temperature circuit: sensor-circuit fault. | Check the sensor, its wiring and connector. |
| `5.2` | coolant temp. circuit (Current) | proven | P0115 | current | Coolant temp. circuit: sensor-circuit fault. | Check the sensor, its wiring and connector. |
| `5.3` | battery voltage problem (Current) | proven | P0560 | current | Battery voltage problem. | See the workshop manual fault-finding for this circuit. |
| `5.4` | reference voltage (Current) | proven | P0641 | current | Reference voltage. | See the workshop manual fault-finding for this circuit. |
| `5.6` | driver demand supply problem (Current) | proven | P0641 | current | Driver demand supply problem. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `5.7` | ambient pressure circuit (Current) | proven | P2227 | current | Ambient pressure circuit: sensor-circuit fault. | Check the sensor, its wiring and connector. |
| `6.0` | cruise lamp drive over temp. (Logged) | proven | — | logged | Cruise lamp drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `6.1` | fuel used output drive over temp. (Logged) | proven | — | logged | Fuel used output drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `6.2` | radiator fan drive over temp. (Logged) | proven | P0480 | logged | Radiator fan drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `6.3` | active engine mounting over temp. (Logged) | proven | — | logged | Active engine mounting: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `6.4` | turbocharger wastegate short circuit (Logged) | proven | P0245 | logged | Turbocharger wastegate short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `6.5` | egr inlet throttle short circuit (Logged) | proven | P0405 | logged | Egr inlet throttle short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `6.6` | egr vacuum modulator short circuit (Logged) | proven | P0409 | logged | Egr vacuum modulator short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `6.7` | temperature gauge short circuit (Logged) | proven | — | logged | Temperature gauge short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `7.0` | air conditioning fan drive over temp. (Logged) | proven | — | logged | Air conditioning fan drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `7.1` | fuel pump drive over temp. (Logged) | proven | P0230 | logged | Fuel pump drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `7.2` | tacho drive over temp. (Logged) | proven | — | logged | Tacho drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `7.3` | gearbox/abs drive over temp. (Logged) | proven | — | logged | Gearbox/abs drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `7.4` | air conditioning clutch over temp. (Logged) | proven | — | logged | Air conditioning clutch: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `7.5` | mil lamp drive over temp. (Logged) | proven | — | logged | Mil lamp drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `7.6` | glow plug relay drive over temp. (Logged) | proven | P0380 | logged | Glow plug relay drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `7.7` | glowplug lamp drive over temperature (Logged) | proven | P0380 | logged | Glowplug lamp drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `8.0` | fuel used output drive open load (Logged) | proven | — | logged | Fuel used output drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `8.1` | cruise lamp drive open load (Logged) | proven | — | logged | Cruise lamp drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `8.2` | radiator fan drive open load (Logged) | proven | P0480 | logged | Radiator fan drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `8.3` | active engine mounting open load (Logged) | proven | — | logged | Active engine mounting: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `8.4` | turbocharger wastegate open load (Logged) | proven | P0244 | logged | Turbocharger wastegate: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `8.5` | egr inlet throttle open load (Logged) | proven | P0404 | logged | Egr inlet throttle: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `8.6` | egr vacuum modulator open load (Logged) | proven | P0409 | logged | Egr vacuum modulator: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `8.7` | temperature gauge open load (Logged) | proven | — | logged | Temperature gauge: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.0` | air conditioning fan drive open load (Logged) | proven | — | logged | Air conditioning fan drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.1` | fuel pump drive open load (Logged) | proven | P0230 | logged | Fuel pump drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.2` | tachometer open load (Logged) | proven | — | logged | Tachometer: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.3` | gearbox/abs drive open load (Logged) | proven | — | logged | Gearbox/abs drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.4` | air conditioning clutch open load (Logged) | proven | — | logged | Air conditioning clutch: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.5` | mil lamp drive open load (Logged) | proven | — | logged | Mil lamp drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.6` | glow plug lamp drive open load (Logged) | proven | P0380 | logged | Glow plug lamp drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `9.7` | glow plug relay drive open load (Logged) | proven | P0380 | logged | Glow plug relay drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `10.0` | cruise control lamp drive over temperature (Current) | proven | — | current | Cruise control lamp drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `10.1` | fuel used output drive over temperature (Current) | proven | — | current | Fuel used output drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `10.2` | radiator fan drive over temperature (Current) | proven | P0480 | current | Radiator fan drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `10.3` | active engine mounting over temperature (Current) | proven | — | current | Active engine mounting: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `10.4` | turbocharger wastegate short circuit (Current) | proven | P0245 | current | Turbocharger wastegate short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `10.5` | egr inlet throttle short circuit (Current) | proven | P0405 | current | Egr inlet throttle short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `10.6` | egr vacuum modulator short circuit (Current) | proven | P0409 | current | Egr vacuum modulator short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `10.7` | temperature gauge short circuit (Current) | proven | — | current | Temperature gauge short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `11.0` | air conditioning fan drive open load (Current) | proven | — | current | Air conditioning fan drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `11.1` | fuel pump drive open load (Current) | proven | P0230 | current | Fuel pump drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `11.2` | tachometer open load (Current) | proven | — | current | Tachometer: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `11.3` | gearbox/abs drive open load (Current) | proven | — | current | Gearbox/abs drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `11.4` | air conditioning clutch open load (Current) | proven | — | current | Air conditioning clutch: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `11.5` | mil lamp drive open load (Current) | proven | — | current | Mil lamp drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `11.6` | glow plug relay drive open load (Current) | proven | P0380 | current | Glow plug relay drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `11.7` | glowplug relay drive open load (Current) | proven | P0380 | current | Glowplug relay drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `12.0` | cruise control lamp drive over temp. (Current) | proven | — | current | Cruise control lamp drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `12.1` | fuel used output drive over temp. (Current) | proven | — | current | Fuel used output drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `12.2` | radiator fan drive over temp. (Current) | proven | P0480 | current | Radiator fan drive: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `12.3` | active engine mounting over temp. (Current) | proven | — | current | Active engine mounting: output driver stage over-temperature (overload protection). | Driver overloaded — check the circuit for a short or excessive current. |
| `12.4` | turbocharger wastegate short circuit (Current) | proven | P0245 | current | Turbocharger wastegate short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `12.5` | egr inlet throttle short circuit (Current) | proven | P0405 | current | Egr inlet throttle short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `12.6` | egr vacuum modulator short circuit (Current) | proven | P0409 | current | Egr vacuum modulator short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `12.7` | temperature gauge short circuit (Current) | proven | — | current | Temperature gauge short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `13.0` | air conditioning fan drive open load (Current) | proven | — | current | Air conditioning fan drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `13.1` | fuel pump drive open load (Current) | proven | P0230 | current | Fuel pump drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `13.2` | tachometer open load (Current) | proven | — | current | Tachometer: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `13.3` | gearbox/abs drive open load (Current) | proven | — | current | Gearbox/abs drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `13.4` | air conditioning clutch open load (Current) | proven | — | current | Air conditioning clutch: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `13.5` | mil lamp drive open load (Current) | proven | — | current | Mil lamp drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `13.6` | glow plug relay drive open load (Current) | proven | P0380 | current | Glow plug relay drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `13.7` | glowplug relay drive open load (Current) | proven | P0380 | current | Glowplug relay drive: output driver sees no load (open). | Open circuit — check the actuator and its wiring/connector. |
| `14.1` | high speed crank (Logged) | proven | P0335 | logged | High speed crank. | Crankshaft sensor signal issue — check the sensor and reluctor. |
| `15.1` | high speed crank (Logged) | proven | P0335 | logged | High speed crank. | Crankshaft sensor signal issue — check the sensor and reluctor. |
| `16.1` | high speed crank (Current) | proven | P0335 | current | High speed crank. | Crankshaft sensor signal issue — check the sensor and reluctor. |
| `18.1` | can rx/tx error (Logged) | proven | U0001 | logged | Can rx/tx error. | CAN bus communication fault — check the bus wiring and the modules on it (SLABS/gearbox). |
| `18.2` | can tx/rx error (Logged) | proven | U0001 | logged | Can tx/rx error. | CAN bus communication fault — check the bus wiring and the modules on it (SLABS/gearbox). |
| `18.5` | noisy crank signal has been detected (Logged) | proven | P0335 | logged | Noisy crank signal has been detected. | Crankshaft sensor signal issue — check the sensor and reluctor. |
| `18.7` | can has had reset failure (Logged) | proven | U0001 | logged | Can has had reset failure. | CAN bus communication fault — check the bus wiring and the modules on it (SLABS/gearbox). |
| `19.0` | turbocharger under boosting (Logged) | proven | P0299 | logged | Turbocharger under boosting. | Boost-control fault — check the turbo, wastegate modulator, hoses and MAP. |
| `19.1` | turbocharger over boosting (Logged) | proven | P0234 | logged | Turbocharger over boosting. | Boost-control fault — check the turbo, wastegate modulator, hoses and MAP. |
| `19.3` | egr valve stuck open (Logged) | proven | P0402 | logged | Egr valve stuck open. | EGR valve/modulator stuck — check the valve, vacuum and soot. |
| `19.4` | egr valve stuck closed (Logged) | proven | P0401 | logged | Egr valve stuck closed. | EGR valve/modulator stuck — check the valve, vacuum and soot. |
| `20.3` | driver demand 1 out of range (Logged) | proven | P0121 | logged | Driver demand 1 out of range. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `20.4` | driver demand 2 out of range (Logged) | proven | P0221 | logged | Driver demand 2 out of range. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `20.5` | problem detected with driver demand (Logged) | proven | P0120 | logged | Problem detected with driver demand. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `20.6` | inconsistencies found with driver demand (Logged) | proven | P2135 | logged | Inconsistencies found with driver demand. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `20.7` | injector trim data corrupted (Logged) | candidate | P1633 | logged | Injector trim data corrupted: stored injector classification codes are corrupt. | Re-enter the injector codes with a capable tool. |
| `21.0` | road speed missing (Logged) | proven | P0500 | logged | Road speed missing. | Road-speed signal missing — check the source (SLABS/instruments). |
| `21.2` | vehicle accel. outside bounds of cruise control (Logged) | proven | — | logged | Vehicle accel. outside bounds of cruise control. | Cruise-control input/switch fault — check the stalk and brake/clutch switches. |
| `21.6` | cruise control resume stuck closed (Logged) | proven | — | logged | Cruise control resume stuck closed. | Cruise-control input/switch fault — check the stalk and brake/clutch switches. |
| `21.7` | cruise control set stuck closed (Logged) | proven | — | logged | Cruise control set stuck closed. | Cruise-control input/switch fault — check the stalk and brake/clutch switches. |
| `22.0` | excessive can bus off (Current) | proven | U0001 | current | Excessive can bus off. | CAN bus communication fault — check the bus wiring and the modules on it (SLABS/gearbox). |
| `22.1` | can rx/tx error (Current) | proven | U0001 | current | Can rx/tx error. | CAN bus communication fault — check the bus wiring and the modules on it (SLABS/gearbox). |
| `22.2` | can tx/rx error (Current) | proven | U0001 | current | Can tx/rx error. | CAN bus communication fault — check the bus wiring and the modules on it (SLABS/gearbox). |
| `22.3` | unable to detect remote can mode (Current) | proven | U0001 | current | Unable to detect remote can mode. | CAN bus communication fault — check the bus wiring and the modules on it (SLABS/gearbox). |
| `22.4` | under boost has occurred on this trip (Current) | proven | P0299 | current | Under boost has occurred on this trip. | Boost-control fault — check the turbo, wastegate modulator, hoses and MAP. |
| `22.5` | noisy crank signal has been detected (Current) | proven | P0335 | current | Noisy crank signal has been detected. | Crankshaft sensor signal issue — check the sensor and reluctor. |
| `23.0` | turbocharger under boosting (Current) | proven | P0299 | current | Turbocharger under boosting. | Boost-control fault — check the turbo, wastegate modulator, hoses and MAP. |
| `23.1` | turbocharger over boosting (Current) | proven | P0234 | current | Turbocharger over boosting. | Boost-control fault — check the turbo, wastegate modulator, hoses and MAP. |
| `23.2` | over boost has occurred this trip (Current) | proven | P0234 | current | Over boost has occurred this trip. | Boost-control fault — check the turbo, wastegate modulator, hoses and MAP. |
| `23.3` | egr valve stuck open (Current) | proven | P0402 | current | Egr valve stuck open. | EGR valve/modulator stuck — check the valve, vacuum and soot. |
| `23.4` | egr valve stuck closed (Current) | proven | P0401 | current | Egr valve stuck closed. | EGR valve/modulator stuck — check the valve, vacuum and soot. |
| `23.6` | problem detected with auto gear box (Current) | proven | P0700 | current | Problem detected with auto gear box. | Fault reported for the automatic gearbox — read the EAT module. |
| `24.3` | driver demand 1 out of range (Logged) | proven | P0121 | logged | Driver demand 1 out of range. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `24.4` | driver demand 2 out of range (Logged) | proven | P0221 | logged | Driver demand 2 out of range. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `24.5` | problem detected with drive demand (Current) | proven | P0120 | current | Problem detected with drive demand. | See the workshop manual fault-finding for this circuit. |
| `24.6` | inconsistencies found with driver demand (Current) | proven | P2135 | current | Inconsistencies found with driver demand. | Accelerator pedal sensor — check the pedal tracks, supply and wiring. |
| `24.7` | injector trim data corrupted (Current) | proven | P1633 | current | Injector trim data corrupted: stored injector classification codes are corrupt. | Re-enter the injector codes with a capable tool. |
| `25.0` | road speed missing (Current) | proven | P0500 | current | Road speed missing. | Road-speed signal missing — check the source (SLABS/instruments). |
| `25.1` | cruise control system problem (Current) | proven | — | current | Cruise control system problem. | Cruise-control input/switch fault — check the stalk and brake/clutch switches. |
| `25.2` | vehicle accel. outside bounds for cruise control (Current) | proven | — | current | Vehicle accel. outside bounds for cruise control. | Cruise-control input/switch fault — check the stalk and brake/clutch switches. |
| `25.6` | cruise control resume stuck closed (Current) | proven | — | current | Cruise control resume stuck closed. | Cruise-control input/switch fault — check the stalk and brake/clutch switches. |
| `25.7` | cruise control set stuck closed (Current) | proven | — | current | Cruise control set stuck closed. | Cruise-control input/switch fault — check the stalk and brake/clutch switches. |
| `26.0` | inj. 1 peak charge long (Logged) | proven | P0201 | logged | Inj. 1 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `26.1` | inj. 2 peak charge long (Logged) | proven | P0202 | logged | Inj. 2 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `26.2` | inj. 3 peak charge long (Logged) | proven | P0203 | logged | Inj. 3 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `26.3` | inj. 4 peak charge long (Logged) | proven | P0204 | logged | Inj. 4 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `26.4` | inj. 5 peak charge long (Logged) | proven | P0205 | logged | Inj. 5 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `26.5` | inj. 6 peak charge long (Logged) | proven | P0206 | logged | Inj. 6 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `26.6` | topside switch failed post injection (Logged) | proven | — | logged | Topside switch failed post injection. | See the workshop manual fault-finding for this circuit. |
| `27.0` | inj. 1 peak charge short (Logged) | proven | P0201 | logged | Inj. 1 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `27.1` | inj. 2 peak charge short (Logged) | proven | P0202 | logged | Inj. 2 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `27.2` | inj. 3 peak charge short (Logged) | proven | P0203 | logged | Inj. 3 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `27.3` | inj. 4 peak charge short (Logged) | proven | P0204 | logged | Inj. 4 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `27.4` | inj. 5 peak charge short (Logged) | proven | P0205 | logged | Inj. 5 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `27.5` | inj. 6 peak charge short (Logged) | proven | P0206 | logged | Inj. 6 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `27.6` | topside switch failed pre injection (Logged) | proven | — | logged | Topside switch failed pre injection. | See the workshop manual fault-finding for this circuit. |
| `28.0` | inj. 1 peak charge long (Current) | proven | P0201 | current | Inj. 1 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `28.1` | inj. 2 peak charge long (Current) | proven | P0202 | current | Inj. 2 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `28.2` | inj. 3 peak charge long (Current) | proven | P0203 | current | Inj. 3 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `28.3` | inj. 4 peak charge long (Current) | proven | P0204 | current | Inj. 4 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `28.4` | inj. 5 peak charge long (Current) | proven | P0205 | current | Inj. 5 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `28.5` | inj. 6 peak charge long (Current) | proven | P0206 | current | Inj. 6 peak charge long: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `28.6` | topside switch failed post injection (Current) | proven | — | current | Topside switch failed post injection. | See the workshop manual fault-finding for this circuit. |
| `29.0` | inj. 1 peak charge short (Current) | proven | P0201 | current | Inj. 1 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `29.1` | inj. 2 peak charge short (Current) | proven | P0202 | current | Inj. 2 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `29.2` | inj. 3 peak charge short (Current) | proven | P0203 | current | Inj. 3 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `29.3` | inj. 4 peak charge short (Current) | proven | P0204 | current | Inj. 4 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `29.4` | inj. 5 peak charge short (Current) | proven | P0205 | current | Inj. 5 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `29.5` | inj. 6 peak charge short (Current) | proven | P0206 | current | Inj. 6 peak charge short: injector peak-charge timing out of range. | Suspect injector or harness — check resistance/connector, compare balance. |
| `29.6` | topside switch failed pre injection (Current) | proven | — | current | Topside switch failed pre injection. | See the workshop manual fault-finding for this circuit. |
| `30.0` | inj. 1 open circuit (Logged) | proven | P0201 | logged | Inj. 1 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `30.1` | inj. 2 open circuit (Logged) | proven | P0202 | logged | Inj. 2 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `30.2` | inj. 3 open circuit (Logged) | proven | P0203 | logged | Inj. 3 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `30.3` | inj. 4 open circuit (Logged) | proven | P0204 | logged | Inj. 4 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `30.4` | inj. 5 open circuit (Logged) | proven | P0205 | logged | Inj. 5 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `30.5` | inj. 6 open circuit (Logged) | proven | P0206 | logged | Inj. 6 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `31.0` | inj. 1 short circuit (Logged) | proven | P0201 | logged | Inj. 1 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `31.1` | inj. 2 short circuit (Logged) | proven | P0202 | logged | Inj. 2 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `31.2` | inj. 3 short circuit (Logged) | proven | P0203 | logged | Inj. 3 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `31.3` | inj. 4 short circuit (Logged) | proven | P0204 | logged | Inj. 4 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `31.4` | inj. 5 short circuit (Logged) | proven | P0205 | logged | Inj. 5 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `31.5` | inj. 6 short circuit (Logged) | proven | P0206 | logged | Inj. 6 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `32.0` | inj. 1 open circuit (Current) | proven | P0201 | current | Inj. 1 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `32.1` | inj. 2 open circuit (Current) | proven | P0202 | current | Inj. 2 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `32.2` | inj. 3 open circuit (Current) | proven | P0203 | current | Inj. 3 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `32.3` | inj. 4 open circuit (Current) | proven | P0204 | current | Inj. 4 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `32.4` | inj. 5 open circuit (Current) | proven | P0205 | current | Inj. 5 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `32.5` | inj. 6 open circuit (Current) | proven | P0206 | current | Inj. 6 open circuit. | Open circuit — check the actuator/injector and its wiring. |
| `33.0` | inj. 1 short circuit (Current) | proven | P0201 | current | Inj. 1 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `33.1` | inj. 2 short circuit (Current) | proven | P0202 | current | Inj. 2 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `33.2` | inj. 3 short circuit (Current) | proven | P0203 | current | Inj. 3 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `33.3` | inj. 4 short circuit (Current) | proven | P0204 | current | Inj. 4 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `33.4` | inj. 5 short circuit (Current) | proven | P0205 | current | Inj. 5 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `33.5` | inj. 6 short circuit (Current) | proven | P0206 | current | Inj. 6 short circuit. | Short in the actuator/injector or its harness — check wiring. |
| `34.0` | inj. 1 partial short circuit (Logged) | proven | P0201 | logged | Inj. 1 partial short circuit: injector partial short circuit. | Check the injector and its harness; compare cylinder balance. |
| `34.1` | inj. 2 partial short circuit (Logged) | proven | P0202 | logged | Inj. 2 partial short circuit: injector partial short circuit. | Check the injector and its harness; compare cylinder balance. |
| `34.2` | inj. 3 partial short circuit (Logged) | proven | P0203 | logged | Inj. 3 partial short circuit: injector partial short circuit. | Check the injector and its harness; compare cylinder balance. |
| `34.3` | inj. 4 partial short circuit (Logged) | proven | P0204 | logged | Inj. 4 partial short circuit: injector partial short circuit. | Check the injector and its harness; compare cylinder balance. |
| `34.4` | inj. 5 partial short circuit (Logged) | proven | P0205 | logged | Inj. 5 partial short circuit: injector partial short circuit. | Check the injector and its harness; compare cylinder balance. |
| `34.5` | inj. 6 partial short circuit (Logged) | proven | P0206 | logged | Inj. 6 partial short circuit: injector partial short circuit. | Check the injector and its harness; compare cylinder balance. |

