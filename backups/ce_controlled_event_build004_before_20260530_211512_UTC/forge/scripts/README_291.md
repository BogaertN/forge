# Patch 291 — MEA Seal Engine Dry-Run

Patch 291 adds `rmc_engine_v1/mea/seal_engine.py` as a deterministic dry-run seal object compiler.

It exposes:

- `GET /api/mea/seal-engine/status`
- `GET /api/mea/seal-engine-dry-run`

This is not the real `/api/mea/seal` route. It compiles the future seal object shape from generated candidates, reusable gate-engine reports, and normalized dry-run packets, but it does not execute the seal.

Hard boundary:

- no `/api/mea/seal`
- no live candidate commit
- no live manifest advance
- no candidate sealing
- no memory write
- no memory promotion
- no Chroma write
- no Identity Vault write
- no LLM call
- no shell execution
- no network I/O
- no user rendering

Expected dry-run seal objects:

- `cg_hypothesis_001` as `hypothesis`
- `cg_branch_001` as `speculative_branch`

Expected blocked candidates:

- `cg_recall_001`
- `cg_tamper_001`
