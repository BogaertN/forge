# Patch 262J1R-Preflight-C12R — Promotion HTTP Route Repair

C12 implemented the promotion engine and adapter, and its verifier proved the engine contract.
The live backend returned `404` for `/api/rmc/promotion-path/status` because the HTTP dispatcher did not route the C12 paths to `_p262q_rmc_promotion_path_v1()`.

This patch is intentionally narrow. It only repairs `main.py` dispatch for:

- `/api/rmc/promotion-path/status`
- `/api/rmc/promotion-path/preview`
- `/api/rmc/promotion-path/promote`
- aliases `/api/rmc/promotion-preview`, `/api/rmc/promotion-commit`, `/api/rmc/promote-memory`

Status and preview remain read-only. Promote still requires `APPROVE_RMC_PROMOTION` inside the promotion engine.

No engine math, memory format, UI, Chroma, LLM, or Identity Vault behavior is changed.
