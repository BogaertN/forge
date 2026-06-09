# Patch 288 — MEA Candidate Generator Runtime Preview

This patch adds the first generated-candidate runtime preview layer.

Patch 287 produced unverified drafts `d_i = O_gen(M_t)`. Patch 288 applies deterministic verification operators and returns candidate previews `c_i = O_verify ∘ O_gen(M_t)`.

New module:

`rmc_engine_v1/mea/candidate_generator.py`

New routes:

`GET /api/mea/candidate-generator/status`
`GET /api/mea/candidate-generator-preview`
`POST /api/mea/candidate-generator-gate`

Approval token:

`APPROVE_MEA_CANDIDATE_GENERATOR_PREVIEW`

Boundary:

No `/api/mea/seal`, no live candidate commit, no live manifest advance, no candidate sealing, no memory promotion, no Chroma writes, no Identity Vault writes, no LLM calls, no shell execution, no network I/O, and no UI mutation.
