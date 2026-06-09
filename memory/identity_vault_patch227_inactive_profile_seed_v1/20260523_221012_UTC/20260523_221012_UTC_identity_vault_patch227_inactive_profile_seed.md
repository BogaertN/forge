# Identity Vault Patch 227 Inactive Draft Profile Seed

Timestamp: `20260523_221012_UTC`
Verdict: **PASS**

## Boundary
- This patch writes only inactive draft profile rows into the canonical Identity Vault database.
- It does not activate identities, write RMC memory, read `.env` secret values, modify Forge registry, or change template files.

## Backup
- backup root: `/home/nic/forge/backups/patch227_identity_vault_profiles_before/20260523_221012_UTC`
- backup ok: `True`

## Template Gate
- `user` path=`/home/nic/identity-vault/templates/user-template.json` json_ok=`True` inactive_defaults_ok=`True` sha16=`e02dd7a6f0d5b26d`
- `agent` path=`/home/nic/identity-vault/templates/agent-template.json` json_ok=`True` inactive_defaults_ok=`True` sha16=`2449b3a0f0c190bb`

## Write Report
- inserted rows: `4`
  - `user_profiles` `nic_bogaert` hash16=`59412c799a127fbf`
  - `agent_profiles` `gilligan.local` hash16=`5b4f576f57903bc8` rmc_namespace=`rmc/agents/gilligan.local`
  - `agent_profiles` `athena.local` hash16=`073115d88626d43e` rmc_namespace=`rmc/agents/athena.local`
  - `agent_profiles` `neo.local` hash16=`df922d109948a5e5` rmc_namespace=`rmc/agents/neo.local`

## Validation
- overall ok: `True`
- user `nic_bogaert` is_active=`0` hash_ok=`True` ok=`True`
- agent `gilligan.local` activation_state=`inactive_draft` is_active=`0` rmc_namespace=`rmc/agents/gilligan.local` pointer_only=`True` hash_ok=`True` ok=`True`
- agent `athena.local` activation_state=`inactive_draft` is_active=`0` rmc_namespace=`rmc/agents/athena.local` pointer_only=`True` hash_ok=`True` ok=`True`
- agent `neo.local` activation_state=`inactive_draft` is_active=`0` rmc_namespace=`rmc/agents/neo.local` pointer_only=`True` hash_ok=`True` ok=`True`

## Database Row Counts
- before canonical rows: `{'agent_profiles': 0, 'audit_logs': 0, 'feedback_logs': 0, 'session_state': 0, 'sqlite_sequence': 0, 'user_profiles': 0}`
- after canonical rows: `{'agent_profiles': 3, 'audit_logs': 0, 'feedback_logs': 0, 'session_state': 0, 'sqlite_sequence': 2, 'user_profiles': 1}`
- legacy rows after: `{'feedback_logs': 0, 'profiles': 1, 'session_state': 1, 'sqlite_sequence': 0}`

## Safety Checks
- `env_secret_values_read`: `False`
- `env_stat_unchanged`: `True`
- `canonical_db_changed_as_expected`: `True`
- `legacy_db_sha_unchanged`: `True`
- `user_template_sha_unchanged`: `True`
- `agent_template_sha_unchanged`: `True`
- `tool_registry_sha_unchanged`: `True`
- `rmc_fingerprints_unchanged`: `True`
- `profiles_created`: `True`
- `profile_rows_expected`: `True`
- `agent_identity_activation_performed`: `False`
- `all_seeded_profiles_inactive`: `True`
- `rmc_memory_write_performed`: `False`
- `forge_tool_registry_modified`: `False`

## Findings
- **INFO** `IV_INACTIVE_DRAFT_PROFILES_WRITTEN` — nic_bogaert, gilligan.local, athena.local, and neo.local seeded into canonical Identity Vault.
- **INFO** `IV_NO_ACTIVATION_PERFORMED` — All seeded profiles remain inactive draft rows.
- **INFO** `IV_RMC_POINTERS_ONLY` — Agent RMC namespaces are stored as pointers only; no RMC memory records were written.

## Next Safe Step
Run Patch 227A to independently verify inactive draft profiles and then manually test `forge-agent-list` and `forge-agent-show gilligan.local`.
