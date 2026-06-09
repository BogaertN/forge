# Patch 226 — Identity Vault Schema Migration Apply

This patch applies the minimal backed-up schema migration required for the existing local Identity Vault to represent the full Self-Hosted Identity Vault operational profile blueprint.

It adds JSON payload/profile metadata columns and indexes to the canonical database:

`/home/nic/identity-vault/data/identity_vault.db`

It does not create live profiles. It does not activate identities. It does not read `.env` secret values. It does not write RMC memory or modify Forge registry.

Run from `~/forge`:

```bash
python -m py_compile scripts/identity_vault_patch226_schema_migration_apply.py
python scripts/identity_vault_patch226_schema_migration_apply.py
cat ~/forge/memory/identity_vault_patch226_schema_migration_apply_v1/latest_identity_vault_patch226_schema_migration_apply.md
```
