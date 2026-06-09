# Identity Vault Patch 225A Operational Profile Schema Alignment Scan

Timestamp: `20260523_203609_UTC`
Verdict: **WARN**

## Boundary
- This scan is read-only except for writing reports under Forge memory.
- It compares the live Identity Vault SQLite schema to the Self-Hosted Identity Vault operational profile blueprint.
- It does not modify Identity Vault code, databases, .env, node_modules, Forge registry, service contracts, RMC memory, or agent identity activation state.
- It does not read .env secret values.

## Blueprint Source
- Source: Self-Hosted Identity Vault design manual, Operational Identity Profiles section.
- required user profile fields: `11`
- required agent profile fields: `22`
- This scan uses the manual's user/agent operational identity structures as the comparison baseline.

## Roots
- forge_root: `/home/nic/forge`
- identity_vault_root: `/home/nic/identity-vault`
- aiweb_root: `/home/nic/aiweb`
- canonical_db: `/home/nic/identity-vault/data/identity_vault.db`
- legacy_db_preserved: `/home/nic/identity-vault/vault.db`
- identity_contract_draft: `/home/nic/identity-vault/service_contracts/identity_vault_readonly_service_contract.draft.json`
- aiweb_identity_contract: `/home/nic/aiweb/service_contracts/identity_vault.contract.json`

## Contract Baseline
- `identity_contract_draft_exists`: `True`
- `identity_contract_draft_loaded`: `True`
- `identity_contract_draft_status`: `DRAFT_NOT_ACTIVE`
- `identity_contract_draft_version`: `0.1.1-draft-file`
- `aiweb_identity_contract_exists`: `True`
- `aiweb_identity_contract_loaded`: `True`
- `aiweb_identity_contract_name`: `identity_vault`

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

## Live Schema Alignment
### `agent_profiles`
- columns: `id, agent_id, canonical_name, role, capabilities, limits, enforcement, created_at, updated_at, version, is_active`
- exact blueprint fields present: `5/22`
- json/profile container present: `False`
- representation strategy ready: `False`
- missing required blueprint fields:
  - `last_updated`
  - `symbolic_signature`
  - `description`
  - `limitations`
  - `persona`
  - `voice_style`
  - `quotes_or_character_inspiration`
  - `special_style_notes`
  - `permissions`
  - `authority`
  - `enforcement_rules`
  - `forbidden_actions`
  - `session_state`
  - `last_action`
  - `last_feedback`
  - `log_fields`
  - `timestamp`

### `user_profiles`
- columns: `id, user_id, canonical_name, interaction_preferences, meta_rules, session_defaults, drift_tracking, created_at, updated_at, version, is_active`
- exact blueprint fields present: `5/11`
- json/profile container present: `False`
- representation strategy ready: `False`
- missing required blueprint fields:
  - `spirit_name`
  - `project_affiliations`
  - `identity_tags`
  - `last_updated`
  - `project_context`
  - `session_state`

## Code / API Reference Scan
- files scanned: `11`
  - `db.js`
  - `schemas.js`
  - `server.js`
  - `cli.js`
  - `routes/agents.js`
  - `routes/profiles.js`
  - `tests/server.test.js`
  - `tests/db.canonical.test.js`
  - `Design_Manual_System_Blueprint.md`
  - `Identity_Vault_Pro.md`
  - `README.md`
- API/table endpoint hits:
  - `/agent-identity`: `5`
  - `/operational-identity`: `8`
  - `agentProfile`: `3`
- blueprint fields not referenced in scanned code/docs: `0`

## JS Syntax Checks
- `db.js`: **PASS** returncode=`0` exists=`True`
- `server.js`: **PASS** returncode=`0` exists=`True`
- `cli.js`: **PASS** returncode=`0` exists=`True`
- `schemas.js`: **PASS** returncode=`0` exists=`True`
- `tests/db.canonical.test.js`: **PASS** returncode=`0` exists=`True`
- `tests/server.test.js`: **PASS** returncode=`0` exists=`True`

## Safety Checks
- `env_secret_values_read`: `False`
- `env_stat_unchanged`: `True`
- `canonical_db_sha_unchanged`: `True`
- `legacy_db_sha_unchanged`: `True`
- `identity_contract_draft_unchanged`: `True`
- `aiweb_identity_contract_unchanged`: `True`
- `database_write_performed`: `False`
- `agent_identity_activation_performed`: `False`
- `forge_tool_registry_modified`: `False`

## Findings
- **WARN** `IV_AGENT_PROFILE_SCHEMA_THIN` — agent_profiles cannot yet represent the full Agent Operational Identity blueprint as columns or a clear JSON payload container.
- **WARN** `IV_USER_PROFILE_SCHEMA_THIN` — user_profiles cannot yet represent the full User Operational Identity blueprint as columns or a clear JSON payload container.
- **INFO** `IV_ENV_NOT_READ` — .env exists locally if present, but this scan did not read secret values.

## Recommended Next Safe Step
Create a schema migration plan patch before running the bootstrap handshake. The plan should decide whether Identity Vault should store full operational profiles as JSON payload columns, normalized profile tables, or both. Do not create live agent profiles or activate identities until the schema can represent the manual's profile structure.
