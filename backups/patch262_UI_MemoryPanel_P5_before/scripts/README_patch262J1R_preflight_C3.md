# Patch 262J1R-Preflight-C3 — Correction Engine + Naming Engine

Adds `rmc_engine_v1/correction_naming_engine.py` and read-only endpoints for:

- `/api/rmc/correction-naming`
- `/api/rmc/correction-engine`
- `/api/rmc/naming-engine`

C3 consumes C2R measured coherence output and computes:

- `chi_t`: correction dry-run state with before/after measured epsilon math.
- `N_t`: naming dry-run state with deterministic identity proposal and naming confidence.

C3 does not compile a manifest, render final language, approve projection, write memory, call an LLM, execute shell, or touch Identity Vault.
