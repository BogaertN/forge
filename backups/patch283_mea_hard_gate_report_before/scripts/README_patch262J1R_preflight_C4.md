# Patch 262J1R-Preflight-C4 — Recursive Manifest Compiler / μ_t

This patch adds the first real Recursive Manifest Compiler stage. It consumes C3R Correction/Naming output and compiles `μ_t` only when measured gates pass.

It is read-only. It does not render final language, project output, write memory, call an LLM, execute shell, touch Identity Vault, or mutate canonical reference files.

New module:

- `forge/rmc_engine_v1/manifest_compiler.py`

Updated endpoints:

- `/api/rmc/manifest-compiler`
- `/api/rmc/recursive-manifest-compiler`
- `/api/rmc/manifest`

A weak candidate returns a blocked manifest candidate with reasons. A strong corrected and named candidate compiles a pre-language manifest packet with required fields: `claim`, `phase_path`, `operator_path`, `memory_links`, `confidence`, `novelty`, `drift_status`, and `output_targets`.
