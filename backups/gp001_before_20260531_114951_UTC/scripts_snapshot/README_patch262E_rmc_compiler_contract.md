# Patch 262E — RMC TraceRecord + Manifest Contract Panel

Adds `GET /api/rmc/compiler-contract` and a read-only RMC panel section that marks which Recursive Manifest Compiler vertical-spine stages are ready, partial, or missing.

This patch intentionally does **not** call RMC complete. It marks `current_rmc_is_shippable: false`, `trace_complete: false`, `manifest_complete: false`, and `move_to_context_library_recommended_now: false`.

No shell, no LLM, no Chroma query, no DB reads, no ingestion, no artifact export, no receipt write, no Identity Vault write, and no RMC live memory write.
