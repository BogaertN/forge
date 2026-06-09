# Identity Vault Patch 225B Operational Profile Schema Migration Plan

Timestamp: `20260523_203848_UTC`
Verdict: **FAIL**

## Boundary
- This patch is a read-only migration planning pass.
- It writes reports only under Forge memory.
- It does not modify Identity Vault code, databases, .env, node_modules, Forge registry, service contracts, RMC memory, or agent identity activation state.
- It does not read .env secret values.
- It does not execute ALTER TABLE or create live agent profiles.

## Current Schema Summary
- canonical DB: `/home/nic/identity-vault/data/identity_vault.db` opened_readonly=`True` ok=`True`
- tables: `agent_profiles, audit_logs, feedback_logs, session_state, sqlite_sequence, user_profiles`
- `agent_profiles` columns: `id, agent_id, canonical_name, role, capabilities, limits, enforcement, created_at, updated_at, version, is_active`
  - exact fields present: `5/22`
  - alias fields present: `4`
  - missing fields: `13`
- `user_profiles` columns: `id, user_id, canonical_name, interaction_preferences, meta_rules, session_defaults, drift_tracking, created_at, updated_at, version, is_active`
  - exact fields present: `5/11`
  - alias fields present: `1`
  - missing fields: `5`

## Selected Migration Strategy
- selected: `hybrid_json_payload_plus_indexed_core_columns`
- reason: The live schema already has useful indexed core columns such as agent_id/user_id, canonical_name, role, version, is_active, created_at, and updated_at.
- reason: The manual blueprint contains many nested/list fields that fit poorly as separate scalar columns during bootstrap.
- reason: A JSON payload column preserves the full operational identity exactly while keeping a few indexed columns available for fast lookup and safe previews.
- reason: This avoids prematurely over-normalizing the schema before real agent usage patterns exist.

## Planned Agent Profile Additions
- `operational_profile_json` `TEXT` — Full Agent Operational Identity JSON payload matching the manual blueprint.
- `profile_schema_version` `TEXT` — Version of the operational identity payload schema.
- `rmc_namespace` `TEXT` — Read-only pointer to the agent-scoped RMC namespace. Not memory content.
- `activation_state` `TEXT` — inactive/draft/active lifecycle marker. Default must be inactive.
- `profile_hash` `TEXT` — Hash of operational_profile_json for tamper-evidence.
- `last_validated_at` `TEXT` — Timestamp of last schema/profile validation.

## Planned User Profile Additions
- `operational_profile_json` `TEXT` — Full User Operational Identity JSON payload matching the manual blueprint.
- `profile_schema_version` `TEXT` — Version of the operational identity payload schema.
- `profile_hash` `TEXT` — Hash of operational_profile_json for tamper-evidence.
- `last_validated_at` `TEXT` — Timestamp of last schema/profile validation.

## SQL Plan Preview
```sql
-- Patch 226 candidate SQL plan only; do not execute in Patch 225B.
ALTER TABLE agent_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE agent_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint';
ALTER TABLE agent_profiles ADD COLUMN rmc_namespace TEXT;
ALTER TABLE agent_profiles ADD COLUMN activation_state TEXT NOT NULL DEFAULT 'inactive';
ALTER TABLE agent_profiles ADD COLUMN profile_hash TEXT;
ALTER TABLE agent_profiles ADD COLUMN last_validated_at TEXT;
ALTER TABLE user_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE user_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint';
ALTER TABLE user_profiles ADD COLUMN profile_hash TEXT;
ALTER TABLE user_profiles ADD COLUMN last_validated_at TEXT;
CREATE INDEX IF NOT EXISTS idx_agent_profiles_agent_id ON agent_profiles(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_profiles_activation_state ON agent_profiles(activation_state);
CREATE INDEX IF NOT EXISTS idx_agent_profiles_rmc_namespace ON agent_profiles(rmc_namespace);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
```

## Contract / Boundary Checks
- `identity_vault_draft` exists=`True` json_ok=`True` ok=`False` name=`None`
- `aiweb_identity_vault` exists=`True` json_ok=`True` ok=`True` name=`identity_vault`

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
- `schema_migration_executed`: `False`

## Findings
- **INFO** `IV_AGENT_PROFILE_JSON_PAYLOAD_REQUIRED` — Live agent_profiles is missing 13 blueprint fields; plan chooses a full operational_profile_json payload column plus indexed core columns.
- **INFO** `IV_USER_PROFILE_JSON_PAYLOAD_REQUIRED` — Live user_profiles is missing 5 blueprint fields; plan chooses a full operational_profile_json payload column plus indexed core columns.
- **INFO** `IV_NO_SCHEMA_MIGRATION_EXECUTED` — Patch 225B writes a migration plan only; no ALTER TABLE statements were executed.
- **FAIL** `IV_SCHEMA_PLAN_BLOCKER` — contract baseline invalid
- **FAIL** `IV_SCHEMA_PLAN_BLOCKER` — safety snapshot changed or forbidden action detected

## Recommended Next Safe Step
Create Patch 226 as a backed-up schema migration apply patch that adds JSON payload/profile metadata columns only. It must not create live agent profiles or activate identities. After Patch 226 passes, create inactive draft Gilligan/Athena/Neo profiles from the Identity Vault blueprint.
