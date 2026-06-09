# Patch 262J1R-Preflight-C13 — Candidate Overextension Check

Purpose: implement the next RMC production-hardening item from the audit:

> Candidate generator overextension check — Mark candidates exceeding N_max as `overextended` before they reach the evolutionary explorer.

## Files changed

- `forge/rmc_engine_v1/candidate_generator.py`
- `forge/rmc_engine_v1/evolutionary_drift_explorer.py`
- `forge/scripts/test_rmc_candidate_overextension_C13.py`
- `forge/scripts/patch262J1R_preflight_C13_verify.py`
- `forge/scripts/README_patch262J1R_preflight_C13.md`

## Contract

C13 enforces the preflight novelty-bound contract:

`0 < N(c) <= N_max`

Every candidate receives an `overextension_check` containing:

- `N_c`
- `N_max`
- `task_type`
- `epsilon_s`
- `bounded_evolutionary_drift`
- `overextended`
- `reason_codes`

Candidates exceeding the task novelty budget are not deleted. They are marked and routed to review/archive so the downstream explorer/scorer cannot treat them as ordinary bounded novelty.

## Safety

This patch is read-only at runtime. It does not write files, call an LLM, query Chroma, execute shell commands, write Identity Vault, or mutate memory.
