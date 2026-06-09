# Patch 221 — Identity Vault DB Canonical Path + Testability Apply

This patch installs one Forge-side script that normalizes Identity Vault JavaScript references away from root-level `vault.db` and toward `data/identity_vault.db`.

It also writes a static Jest test at `identity-vault/tests/db.canonical.test.js` so future test runs can catch accidental root database fallback.

Boundary:
- Does not read `.env` secret values.
- Does not write Identity Vault database contents.
- Does not modify `node_modules`.
- Does not register Forge tools.
- Does not activate agent identities.

Run from Forge:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile scripts/identity_vault_patch221_db_canonical_testability_apply.py
python scripts/identity_vault_patch221_db_canonical_testability_apply.py
cat ~/forge/memory/identity_vault_patch221_db_canonical_testability_v1/latest_identity_vault_patch221_db_canonical_testability.md
```
