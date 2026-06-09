# Patch 226E — Identity Vault Template Apply

This patch backs up and replaces the malformed Identity Vault template JSON files:

- `/home/nic/identity-vault/templates/user-template.json`
- `/home/nic/identity-vault/templates/agent-template.json`

Backup location:

- `/home/nic/forge/backups/patch226e_identity_vault_templates_before/<timestamp>/`

Report location:

- `/home/nic/forge/memory/identity_vault_patch226e_template_apply_v1/`

Boundary:

- Does not write Identity Vault databases.
- Does not create profiles.
- Does not activate identities.
- Does not read `.env` secret values.
- Does not modify Forge registry.
- Does not write RMC memory.

Run:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile scripts/identity_vault_patch226e_template_apply.py
python scripts/identity_vault_patch226e_template_apply.py
cat ~/forge/memory/identity_vault_patch226e_template_apply_v1/latest_identity_vault_patch226e_template_apply.md
```
