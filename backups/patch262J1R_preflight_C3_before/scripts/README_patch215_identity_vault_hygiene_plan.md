# Patch 215 — Identity Vault Hygiene Plan

This patch adds a read-only planning script:

- `forge/scripts/identity_vault_patch215_hygiene_plan.py`

The script inspects Identity Vault metadata and writes a plan under:

- `~/forge/memory/identity_vault_patch215_hygiene_plan_v1/`

It does not modify Identity Vault, databases, `.env`, `node_modules`, Forge tools, Forge registry, RMC memory, AI.Web wrappers, or agent identity configuration.

The plan selects a proposed canonical database path, records packaging exclusions, and writes a draft read-only Identity Vault service contract for later Forge integration.
