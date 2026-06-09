# Patch 225C — Identity Vault Schema Plan Reconcile

Read-only reconcile for Patch 225B.

This patch does not change Identity Vault, databases, `.env`, service contracts, Forge registry, RMC memory, or agent identity activation state.

It writes reports only under:

`/home/nic/forge/memory/identity_vault_patch225c_schema_plan_reconcile_v1/`

Run:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile scripts/identity_vault_patch225c_schema_plan_reconcile.py
python scripts/identity_vault_patch225c_schema_plan_reconcile.py
cat ~/forge/memory/identity_vault_patch225c_schema_plan_reconcile_v1/latest_identity_vault_patch225c_schema_plan_reconcile.md
```
