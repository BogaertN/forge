# Patch 221A — Identity Vault DB Canonical Reconcile

This patch reconciles the Patch 221 failure before the system moves to the AI.Web service-contract layer.

It backs up the current Identity Vault DB-related JavaScript files, removes remaining root-level `vault.db` runtime references from targeted JS files, rewrites the canonical DB static test so it does not create false legacy-reference hits, and verifies that `.env`, the canonical database, the legacy database, and the draft service contract remain unchanged.

Boundary:
- Does not read `.env` secret values.
- Does not write Identity Vault database contents.
- Does not register Forge tools.
- Does not write RMC memory.
- Does not activate agent identities.

Run from `~/forge`:

```bash
python -m py_compile scripts/identity_vault_patch221a_db_canonical_reconcile.py
python scripts/identity_vault_patch221a_db_canonical_reconcile.py
cat ~/forge/memory/identity_vault_patch221a_db_canonical_reconcile_v1/latest_identity_vault_patch221a_db_canonical_reconcile.md
```
