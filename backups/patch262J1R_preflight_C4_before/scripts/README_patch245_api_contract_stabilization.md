# Patch 245 — Forge API Contract Stabilization

Purpose:
Add stable read-only API endpoints for the production Forge Operator Console scaffold.

This patch modifies:
- `/home/nic/forge/main.py`
- `/home/nic/aiweb/apps/forge-operator-console/src/api/*`
- `/home/nic/aiweb/apps/forge-operator-console/docs/API_CONTRACT_V1.md`

It does not:
- add Forge CLI commands
- change the Forge command surface
- install npm dependencies
- run the frontend
- execute ProtoForge simulations
- write Identity Vault
- write RMC live memory

New read-only endpoints:
- `GET /api/operator/contract`
- `GET /api/forge/status`
- `GET /api/audit/tail`
- `GET /api/protoforge/reports`
- compatibility alias: `GET /api/protoforge-reports`

Existing action endpoint remains:
- `POST /api/command`

The action endpoint remains allowlist/gate controlled.
