# Patch 287 — MEA Operator Engine Preview

Adds the preview-only MEA operator engine. This layer executes registered deterministic operators and returns unverified drafts `d_i = O_gen(M_t)`. Drafts are not candidates, not sealed, not renderable, and not memory-promotable.

New routes:

- `GET /api/mea/operator-engine/status`
- `GET /api/mea/operator-engine-preview`
- `POST /api/mea/operator-engine-gate`

Approval token: `APPROVE_MEA_OPERATOR_ENGINE_PREVIEW`

Still forbidden: `/api/mea/seal`, live candidate commit, live manifest advance, file writes, memory writes, Chroma writes, Identity Vault writes, LLM calls, shell execution, network I/O, rendering, and memory promotion.
