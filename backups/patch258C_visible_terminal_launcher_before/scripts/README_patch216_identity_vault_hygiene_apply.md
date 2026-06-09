# Patch 216 — Identity Vault Hygiene Apply

This patch adds one Forge script:

- `forge/scripts/identity_vault_patch216_hygiene_apply.py`

The script performs the first approved Identity Vault hygiene changes:

1. Creates a timestamped backup under `~/forge/backups/patch216_identity_vault_hygiene_before/`.
2. Backs up Identity Vault metadata and both SQLite database files.
3. Adds managed runtime/packaging exclusion blocks to `~/identity-vault/.gitignore` and `~/identity-vault/.dockerignore`.
4. Writes `~/identity-vault/service_contracts/identity_vault_readonly_service_contract.draft.json`.
5. Writes a report under `~/forge/memory/identity_vault_patch216_hygiene_apply_v1/`.

Boundary:

- Does not activate agent identities.
- Does not modify Identity Vault database contents.
- Does not print `.env` contents or secret values.
- Does not modify Forge registry, RMC memory, or AI.Web wrappers.

Run from `~/forge` with the Forge virtual environment active:

```bash
python -m py_compile scripts/identity_vault_patch216_hygiene_apply.py
python scripts/identity_vault_patch216_hygiene_apply.py
cat ~/forge/memory/identity_vault_patch216_hygiene_apply_v1/latest_identity_vault_patch216_hygiene_apply.md
cat ~/identity-vault/service_contracts/identity_vault_readonly_service_contract.draft.json
```
