# Patch 225B — Identity Vault Operational Profile Schema Migration Plan

This patch adds a read-only planning script:

`forge/scripts/identity_vault_patch225b_schema_migration_plan.py`

It compares the live Identity Vault SQLite schema against the Self-Hosted Identity Vault operational profile blueprint and produces a migration plan only.

It does not modify Identity Vault code, databases, `.env`, `node_modules`, service contracts, Forge registry, RMC memory, or agent identity activation state.

Expected use:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile scripts/identity_vault_patch225b_schema_migration_plan.py
python scripts/identity_vault_patch225b_schema_migration_plan.py
cat ~/forge/memory/identity_vault_patch225b_schema_migration_plan_v1/latest_identity_vault_patch225b_schema_migration_plan.md
```
