# Patch 262G — RMC Drift Analyzer Read-Only

Adds the second real RMC compiler module:

`GET /api/rmc/drift-analyzer`

This endpoint consumes the read-only Phase Parser dry-run and produces a drift report anchored to the `memory/drift.py` / ProtoForge2 drift framework:

- syntactic drift
- semantic drift
- recursive drift
- catastrophic drift
- evolutionary drift
- resonant drift
- structural drift
- ε_s preview
- phase deviation preview
- χ(t) correction preview
- circuit-breaker preview

Boundary:

- no new Forge commands
- no shell
- no LLM call
- no Chroma query
- no DB reads
- no file writes
- no Identity Vault write
- no RMC live memory write

Next patch: Patch 262H — RMC Candidate Conclusion Dry-Run.
