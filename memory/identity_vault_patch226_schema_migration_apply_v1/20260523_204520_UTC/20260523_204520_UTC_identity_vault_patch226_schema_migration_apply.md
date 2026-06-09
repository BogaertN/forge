# Identity Vault Patch 226 Schema Migration Apply

Timestamp: `20260523_204520_UTC`
Verdict: **PASS**

## Boundary
- This patch applies only the approved Identity Vault schema migration needed for full operational profile payload support.
- It backs up the canonical and legacy SQLite databases before migration.
- It adds JSON payload/profile metadata columns and indexes only.
- It does not create live agent profiles or activate identities.
- It does not modify .env, node_modules, Forge registry, service contracts, RMC memory, or AI.Web wrappers.
- It does not read .env secret values; only stat metadata is compared.

## Backup
- backup root: `/home/nic/forge/backups/patch226_identity_vault_schema_migration_before/20260523_204520_UTC`
- `canonical_db`: **COPIED**
- `legacy_db`: **COPIED**
- `identity_contract_draft`: **COPIED**
- `aiweb_identity_contract`: **COPIED**
- `tool_registry`: **COPIED**

## Migration Strategy
- selected: `hybrid_json_payload_plus_indexed_core_columns`
- Adds full operational profile JSON payload columns while preserving indexed lookup columns.
- Defaults all lifecycle state to `inactive`.
- Does not create live agent profiles or activate identities.

## Database Before
- canonical DB: `/home/nic/identity-vault/data/identity_vault.db`
- agent_profiles columns before: `id, agent_id, canonical_name, role, capabilities, limits, enforcement, created_at, updated_at, version, is_active`
- user_profiles columns before: `id, user_id, canonical_name, interaction_preferences, meta_rules, session_defaults, drift_tracking, created_at, updated_at, version, is_active`
- row counts before: `{'agent_profiles': 0, 'user_profiles': 0, 'audit_logs': 0, 'feedback_logs': 0, 'session_state': 0}`

## SQL Actions
- `EXECUTED` `ALTER TABLE agent_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT '{}'`
- `EXECUTED` `ALTER TABLE agent_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint'`
- `EXECUTED` `ALTER TABLE agent_profiles ADD COLUMN rmc_namespace TEXT`
- `EXECUTED` `ALTER TABLE agent_profiles ADD COLUMN activation_state TEXT NOT NULL DEFAULT 'inactive'`
- `EXECUTED` `ALTER TABLE agent_profiles ADD COLUMN profile_hash TEXT`
- `EXECUTED` `ALTER TABLE agent_profiles ADD COLUMN last_validated_at TEXT`
- `EXECUTED` `ALTER TABLE user_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT '{}'`
- `EXECUTED` `ALTER TABLE user_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint'`
- `EXECUTED` `ALTER TABLE user_profiles ADD COLUMN profile_hash TEXT`
- `EXECUTED` `ALTER TABLE user_profiles ADD COLUMN last_validated_at TEXT`
- `EXECUTED_OR_ALREADY_PRESENT` `CREATE INDEX IF NOT EXISTS idx_agent_profiles_agent_id ON agent_profiles(agent_id)`
- `EXECUTED_OR_ALREADY_PRESENT` `CREATE INDEX IF NOT EXISTS idx_agent_profiles_activation_state ON agent_profiles(activation_state)`
- `EXECUTED_OR_ALREADY_PRESENT` `CREATE INDEX IF NOT EXISTS idx_agent_profiles_rmc_namespace ON agent_profiles(rmc_namespace)`
- `EXECUTED_OR_ALREADY_PRESENT` `CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)`

## Database After
- opened read-only after migration: `True`
- agent_profiles columns after: `id, agent_id, canonical_name, role, capabilities, limits, enforcement, created_at, updated_at, version, is_active, operational_profile_json, profile_schema_version, rmc_namespace, activation_state, profile_hash, last_validated_at`
- user_profiles columns after: `id, user_id, canonical_name, interaction_preferences, meta_rules, session_defaults, drift_tracking, created_at, updated_at, version, is_active, operational_profile_json, profile_schema_version, profile_hash, last_validated_at`
- row counts after: `{'agent_profiles': 0, 'user_profiles': 0, 'audit_logs': 0, 'feedback_logs': 0, 'session_state': 0}`
- indexes after: `idx_agent_profiles_activation_state, idx_agent_profiles_agent_id, idx_agent_profiles_rmc_namespace, idx_audit_logs_profile, idx_feedback_logs_profile, idx_session_state_profile, idx_user_profiles_user_id, sqlite_autoindex_agent_profiles_1, sqlite_autoindex_user_profiles_1`

## Required Column Verification
- agent required additions present: `True`
- user required additions present: `True`
- required indexes present: `True`
- missing agent columns: `[]`
- missing user columns: `[]`
- missing indexes: `[]`

## No Live Profile / Activation Check
- agent rows before: `0`
- agent rows after: `0`
- user rows before: `0`
- user rows after: `0`
- live agent profiles created: `False`
- agent identity activation performed: `False`

## Safety Checks
- `env_secret_values_read`: `False`
- `env_stat_unchanged`: `True`
- `canonical_db_schema_changed_expected`: `True`
- `legacy_db_unchanged`: `True`
- `identity_contract_draft_unchanged`: `True`
- `aiweb_identity_contract_unchanged`: `True`
- `forge_tool_registry_modified`: `False`
- `database_write_performed`: `True`
- `database_content_rows_created`: `False`
- `agent_identity_activation_performed`: `False`
- `schema_migration_executed`: `True`

## Findings
- **INFO** `IV_SCHEMA_MIGRATION_APPLIED` — Operational profile JSON payload and metadata columns are present on canonical Identity Vault tables.
- **INFO** `IV_INDEXES_READY` — Required lookup indexes are present for agent_id, activation_state, rmc_namespace, and user_id.
- **INFO** `IV_NO_PROFILE_ROWS_CREATED` — Schema migration did not create live user or agent profile rows.
- **INFO** `IV_IDENTITIES_REMAIN_INACTIVE` — No identity activation was performed.

## Next Safe Step
Run a post-migration schema alignment verification. If it passes, create inactive draft Gilligan/Athena/Neo operational profile rows from the Identity Vault blueprint. Do not activate identities yet.
