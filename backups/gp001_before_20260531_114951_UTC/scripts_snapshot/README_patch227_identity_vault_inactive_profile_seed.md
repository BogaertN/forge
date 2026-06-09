# Patch 227 — Identity Vault Inactive Draft Profile Seed

This patch writes the first canonical Identity Vault profile rows as inactive drafts only.

It writes:

- `user_profiles`: `nic_bogaert`
- `agent_profiles`: `gilligan.local`
- `agent_profiles`: `athena.local`
- `agent_profiles`: `neo.local`

It requires the repaired Identity Vault templates from Patch 226E/226F.1.

It backs up the canonical database before writing:

`/home/nic/forge/backups/patch227_identity_vault_profiles_before/<timestamp>/identity_vault.db`

It does not activate identities, write RMC memory, read `.env` secret values, modify Forge registry, or change template files.

Run from `~/forge`:

```bash
python -m py_compile scripts/identity_vault_patch227_write_inactive_draft_profiles.py
python scripts/identity_vault_patch227_write_inactive_draft_profiles.py
cat ~/forge/memory/identity_vault_patch227_inactive_profile_seed_v1/latest_identity_vault_patch227_inactive_profile_seed.md
```
