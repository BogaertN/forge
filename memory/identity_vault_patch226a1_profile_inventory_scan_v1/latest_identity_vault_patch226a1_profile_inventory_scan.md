# Identity Vault Patch 226A.1 Profile Inventory Scan

Timestamp: `20260523_205321_UTC`
Verdict: **FAIL**

## Boundary
- This hotfix replaces the failed Patch 226A scanner that missed `import stat`.
- This scan is read-only except for writing reports under Forge memory.
- It reads canonical and legacy SQLite databases through read-only connections.
- It does not read `.env` secret values.
- It does not write databases, create profiles, or activate identities.

## Roots
- Identity Vault root: `/home/nic/identity-vault` exists=`True`
- Canonical DB: `/home/nic/identity-vault/data/identity_vault.db` exists=`True`
- Legacy DB: `/home/nic/identity-vault/vault.db` exists=`True`

## Canonical Database Inventory
- opened_readonly: `True` ok=`True`
- tables: `agent_profiles, audit_logs, feedback_logs, session_state, sqlite_sequence, user_profiles`
  - `agent_profiles` rows: `0`
  - `audit_logs` rows: `0`
  - `feedback_logs` rows: `0`
  - `session_state` rows: `0`
  - `user_profiles` rows: `0`

### Canonical Profile Previews
- `agent_profiles` preview rows returned: `0`
- `session_state` preview rows returned: `0`
- `user_profiles` preview rows returned: `0`

## Legacy Database Inventory
- opened_readonly: `True` ok=`True`
- tables: `feedback_logs, profiles, session_state, sqlite_sequence`
  - `feedback_logs` rows: `0`
  - `profiles` rows: `1`
  - `session_state` rows: `1`

### Legacy Profile / Session Previews
- `profiles` preview rows returned: `1`
```json
[
  {
    "id": "user789",
    "version": "1.0.0"
  }
]
```
- `session_state` preview rows returned: `1`
```json
[
  {
    "id": "user789"
  }
]
```

## Profile Candidate Files
- candidate files found: `8`
  - `agent_profile_or_template_candidate`: `2`
  - `profile_or_identity_candidate`: `3`
  - `user_profile_or_template_candidate`: `3`

### Candidate File List
- `routes/agents.js` class=`agent_profile_or_template_candidate` size=`8380` sha16=`fa26d01ec353549a`
- `templates/agent-template.json` class=`agent_profile_or_template_candidate` size=`643` sha16=`ed18366ba9e5808a`
- `Identity_Vault_Pro.md` class=`profile_or_identity_candidate` size=`7400` sha16=`4a28d181b6dc4e92`
- `routes/profiles.js` class=`profile_or_identity_candidate` size=`8255` sha16=`904ae253504e8366`
- `service_contracts/identity_vault_readonly_service_contract.draft.json` class=`profile_or_identity_candidate` size=`1922` sha16=`2e1573ae148f68ea` keys=`activation_rule, allowed_reads, allowed_writes, audit_requirement, canonical_database_path, contract_name, controlled_by, created_at_utc, created_by_patch, forbidden_reads, forbidden_writes, future_adapter_rules`
- `User_Manual.md` class=`user_profile_or_template_candidate` size=`27020` sha16=`aef5da956133202b`
- `templates/user-template.json` class=`user_profile_or_template_candidate` size=`1662` sha16=`97aeb120737d7c2e`
- `tests/db.canonical.test.js` class=`user_profile_or_template_candidate` size=`1134` sha16=`803e6633125327dc`

## Safety Checks
- `env_secret_values_read`: `False`
- `env_stat_unchanged`: `True`
- `canonical_db_sha_unchanged`: `True`
- `legacy_db_sha_unchanged`: `True`
- `database_write_performed`: `False`
- `agent_identity_activation_performed`: `False`
- `profiles_created`: `False`

## Findings
- **INFO** `IV_CANONICAL_DB_READONLY_OK` — Canonical Identity Vault database opened in read-only mode.
- **WARN** `IV_LEGACY_PROFILE_ROWS_FOUND` — Legacy database contains 2 profile/session rows that may need migration review.
- **INFO** `IV_CANONICAL_PROFILE_ROWS_EMPTY` — Canonical user_profiles and agent_profiles are currently empty.
- **WARN** `IV_PROFILE_CANDIDATE_FILES_FOUND` — Found 8 local profile/template candidate files for review.
- **FAIL** `IV_INVENTORY_SAFETY_CHECK_FAILED` — A no-mutation safety check failed.

## Recommended Next Safe Step
Review the legacy DB previews and candidate files. If useful prior profiles exist, create a migration-preview patch that maps them into the new operational_profile_json structure without activation. If no useful profiles exist, create inactive draft Gilligan/Athena/Neo and Nic user profiles from the Identity Vault blueprint.
