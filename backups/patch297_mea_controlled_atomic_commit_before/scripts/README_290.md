# Patch 290 — MEA True Gate Engine Extension Preview

Patch 290 installs `rmc_engine_v1/mea/gate_engine.py`, a reusable deterministic gate engine over Patch 288 generated candidates and Patch 289 coherence scoring boundaries.

This patch is still preview-only. It does not create `/api/mea/seal`, does not seal candidates, does not commit live candidates, does not advance a live manifest, does not write memory, does not write Chroma, does not touch Identity Vault, does not call an LLM, does not execute shell commands, does not perform network I/O, and does not mutate the Operator Console UI or launcher.

## New routes

- `GET /api/mea/gate-engine/status`
- `GET /api/mea/gate-engine-preview`
- `POST /api/mea/gate-engine-gate`

## Approval token

`APPROVE_MEA_GATE_ENGINE_PREVIEW`

## Gate law

Scores can rank candidates, but scores cannot override gates.

The reusable gate vector checks:

- replay gate
- tamper/hash gate
- proof debt gate
- convergence gate
- information gain gate
- drift gate
- phase gate
- claim status gate
- render scope gate
- seal permission gate
- memory permission gate

## Canonical expected decisions

- `cg_recall_001` -> `REFERENCE_ONLY`
- `cg_hypothesis_001` -> `PASS_PREVIEW_ONLY`
- `cg_branch_001` -> `PASS_BOUNDED_PREVIEW_ONLY`
- `cg_tamper_001` -> `REJECTED`

All candidates remain seal-blocked and memory-blocked.
