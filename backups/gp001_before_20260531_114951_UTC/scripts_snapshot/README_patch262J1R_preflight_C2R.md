# Patch 262J1R-Preflight-C2R — RMC Measurement Kernel + Real Math Reinforcement

C2R reinforces the RMC lower spine before moving upward to Correction Engine and Naming Engine.

It adds `forge/rmc_engine_v1/measurement_kernel.py` and binds Candidate Generator, Evolutionary Drift Explorer, and Coherence Scorer to shared measured readings instead of loose named fields.

Measured readings include token boundaries, normalized Shannon entropy, structure signatures, structure deltas, semantic distance, memory fit, phase deviation, resonance variance `sigma_res`, drift severity `D_score`, symbolic `epsilon_s = (sigma_res + D_score + |ΔΦ|) / n`, novelty deltas, bounded evolutionary drift checks, circuit breaker checks, χ(t) routing recommendation, and coherence-score components.

This patch is still read-only. It does not render final language, compile a manifest, write memory, mutate references, call an LLM, execute shell, or touch Identity Vault.

Run:

```bash
python scripts/patch262J1R_preflight_C2R_verify.py
python scripts/test_rmc_measurement_kernel_C2R.py
python scripts/test_rmc_evolutionary_drift_coherence_C2.py
python scripts/test_rmc_candidate_generator_behavior.py
```

Expected results:

```text
RESULT: PATCH_262J1R_PREFLIGHT_C2R_VERIFY_OK
RESULT: measurement_kernel_C2R_behavior_tests_pass=True
RESULT: evolutionary_drift_coherence_C2R_behavior_tests_pass=True
RESULT: candidate_generator_C_behavior_tests_pass=True
```
