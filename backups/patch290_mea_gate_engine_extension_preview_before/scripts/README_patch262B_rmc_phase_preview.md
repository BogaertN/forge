# Patch 262B — RMC Phase Graph / Frequency Preview Read-Only

Adds `GET /api/rmc/phase-preview`.

This endpoint derives a read-only phase graph and numeric frequency preview from the verified `/api/rmc/memory-object` manifest trace. It does not generate audio, cymatic geometry, Chroma queries, memory writes, file writes, shell execution, or Identity Vault/RMC live memory writes.
