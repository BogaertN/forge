# Patch 262J1R-Preflight-C12 — Promotion Path

This patch implements the RMC dataset promotion path:

`review_queue -> stable_memory -> retrieval index`

It adds `forge/rmc_engine_v1/promotion_path.py` and thin API routes:

- `/api/rmc/promotion-path/status`
- `/api/rmc/promotion-path/preview?candidate_id=<id>`
- `/api/rmc/promotion-path/promote?candidate_id=<id>&approval=APPROVE_RMC_PROMOTION`

Status and preview are read-only. Promotion writes only after explicit approval and only inside `/home/nic/forge/memory/rmc_dataset_v1/`.

This does not mutate canonical reference files, Identity Vault, Chroma, source documents, or RMC live memory. It leaves the original review queue item in place as immutable evidence, writes a stable memory copy, writes a promotion receipt, and appends retrieval indexes.

Dangerous/circuit-breaker examples can be promoted only as `blocked_patterns` / negative evidence. They are not promoted as stable truth.
