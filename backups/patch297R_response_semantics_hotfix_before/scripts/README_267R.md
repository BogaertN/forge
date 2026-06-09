# Patch 267R — χ(t) Correction Gate Preview

Formula: χ(t) = Φ₁·α + Σ(Δψ / t)
All thresholds named: intervention (0.35), circuit_breaker (0.72),
Babel Cutoff (0.78, ProtoForge2_RPMC_doctrine). Settle window: 3.33s.

## New endpoint
  /api/rmc/chi-correction-preview

## New module
  forge/rmc_engine_v1/chi_correction_gate.py

50/50 tests pass. 16/16 verifier checks pass.

## Install
```bash
cd /home/nic && tar -xzf ~/patch267R_chi_correction_gate_preview.tar.gz
python3 -m py_compile forge/main.py && echo OK
python3 forge/scripts/patch267R_verify.py
```
Requires: Patches 265R, 266R installed first.
