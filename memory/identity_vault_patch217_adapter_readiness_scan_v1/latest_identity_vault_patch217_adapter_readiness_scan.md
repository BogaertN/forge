# Identity Vault Patch 217 Adapter Readiness Scan

Timestamp: `20260523_193952_UTC`
Verdict: **WARN**

## Boundary
- This scan is read-only except for writing reports under Forge memory.
- It reads the draft service contract and approved package/database metadata only.
- It opens the canonical SQLite database in read-only mode for schema and row counts only.
- It does not read .env secret values, write databases, register tools, or activate agent identities.

## Roots
- Forge root: `/home/nic/forge`
- Identity Vault root: `/home/nic/identity-vault`
- Contract path: `/home/nic/identity-vault/service_contracts/identity_vault_readonly_service_contract.draft.json`

## Contract Checks
- `contract_exists`: `True`
- `contract_loaded`: `True`
- `contract_name_ok`: `True`
- `status_ok`: `True`
- `version_ok`: `True`
- `controlled_by_forge`: `True`
- `allowed_writes_empty`: `True`
- `canonical_db_path_ok`: `True`
- `forbidden_reads_present`: `True`
- `forbidden_writes_present`: `True`
- `future_rules_present`: `True`
- `activation_rule_present`: `True`
- `overall_ok`: `False`
- issues: `overall_ok`

## Sensitive File Handling
- `.env` exists=`True` content_read=`False`
  - size=`1605` mode=`0o664`
- `.env.example` exists=`True` content_read=`False`
  - size=`6787` mode=`0o664`
- `.env` secret values were not read, printed, copied, hashed, or exported by this scan.

## Ignore Hygiene Check
- `.gitignore` managed block present: `False`
- `.dockerignore` managed block present: `False`
- required gitignore rules present: `True`
- required dockerignore rules present: `True`

## Canonical Database Read-Only Summary
- path: `/home/nic/identity-vault/data/identity_vault.db`
- exists: `True`
- opened_readonly: `True`
- ok: `True`
- tables: `agent_profiles, audit_logs, feedback_logs, session_state, sqlite_sequence, user_profiles`
  - `agent_profiles` rows: `0`
  - `audit_logs` rows: `0`
  - `feedback_logs` rows: `0`
  - `session_state` rows: `0`
  - `sqlite_sequence` rows: `0`
  - `user_profiles` rows: `0`

## Adapter Readiness Preview
- `contract_ready_for_readonly_adapter`: `False`
- `canonical_db_readonly_ok`: `True`
- `identity_tables_available`: `True`
- `package_metadata_available`: `True`
- `ignore_hygiene_ok`: `False`
- `agent_identity_activation_performed`: `False`
- `database_write_performed`: `False`
- `env_secret_values_read`: `False`

## Allowed Metadata Preview
- service: `Identity Vault`
- package name: `identity-vault`
- package version: `1.0.0`
- identity tables present: `{'agent_profiles': True, 'user_profiles': True}`
- row counts: `{'agent_profiles': 0, 'audit_logs': 0, 'feedback_logs': 0, 'session_state': 0, 'sqlite_sequence': 0, 'user_profiles': 0}`

## Findings
- **WARN** `IV_CONTRACT_DRAFT_NOT_READY` — Draft contract is missing one or more expected boundary fields.
- **INFO** `IV_ENV_LOCAL_PRESENT_NOT_READ` — .env exists locally; this scan recorded stat metadata only and did not read secret values.

## Next Safe Step
Create a future Forge Identity Vault read-only adapter file that loads this draft contract and exposes read-only metadata functions only. Do not activate agent identities yet.
