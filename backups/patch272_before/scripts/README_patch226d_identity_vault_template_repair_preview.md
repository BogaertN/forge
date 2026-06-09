# Patch 226D — Identity Vault Template Repair Preview

Purpose: read the malformed Identity Vault template files and generate repaired JSON template previews without modifying Identity Vault.

## Boundary

This patch writes only under:

`/home/nic/forge/memory/identity_vault_patch226d_template_repair_preview_v1/`

It does not overwrite:

`/home/nic/identity-vault/templates/user-template.json`
`/home/nic/identity-vault/templates/agent-template.json`

It does not write databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.

## Run

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile scripts/identity_vault_patch226d_template_repair_preview.py
python scripts/identity_vault_patch226d_template_repair_preview.py
cat ~/forge/memory/identity_vault_patch226d_template_repair_preview_v1/latest_identity_vault_patch226d_template_repair_preview.md
cat ~/forge/memory/identity_vault_patch226d_template_repair_preview_v1/latest_user_template_repaired_preview.json
cat ~/forge/memory/identity_vault_patch226d_template_repair_preview_v1/latest_agent_template_repaired_preview.json
```
