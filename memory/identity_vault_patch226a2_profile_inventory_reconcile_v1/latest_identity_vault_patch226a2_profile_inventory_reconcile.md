# Identity Vault Patch 226A.2 Profile Inventory Reconcile

Timestamp: `20260523_205601_UTC`
Verdict: **WARN**

## Boundary
- This reconcile is read-only except for writing reports under Forge memory.
- It reads canonical and legacy SQLite databases through read-only connections.
- It does not read `.env` secret values.
- It does not write databases, create profiles, or activate identities.

## Canonical Database
- path: `/home/nic/identity-vault/data/identity_vault.db` exists=`True` opened_readonly=`True` ok=`True`
- tables: `agent_profiles, audit_logs, feedback_logs, session_state, sqlite_sequence, user_profiles`
  - `agent_profiles` rows: `0`
  - `audit_logs` rows: `0`
  - `feedback_logs` rows: `0`
  - `session_state` rows: `0`
  - `sqlite_sequence` rows: `0`
  - `user_profiles` rows: `0`

## Legacy Database
- path: `/home/nic/identity-vault/vault.db` exists=`True` opened_readonly=`True` ok=`True`
- tables: `feedback_logs, profiles, session_state, sqlite_sequence`
  - `feedback_logs` rows: `0`
  - `profiles` rows: `1`
  - `session_state` rows: `1`
  - `sqlite_sequence` rows: `0`

### Legacy Schemas
- `feedback_logs` columns: `id, profile_id, type, data, timestamp`
- `profiles` columns: `id, type, data, version, last_updated, ipfs_hash, zkp_metadata`
- `session_state` columns: `id, phase, waiting_for, last_feedback, last_action, timestamp`
- `sqlite_sequence` columns: `name, seq`

### Legacy Profile / Session Preview
- `profiles` preview rows returned: `1`
```json
[
  {
    "id": "user789",
    "type": "user",
    "data": "1755df798eafe1af68537bd1:be01f1edf5896c9df4890673737838226125ab504805414a5183f037d18209eaab786296ad35a17d314b64c9fb7468e1cb5acdb66822fd5f11157c2793bc09d23969:fb4fb57ca5a479bd0ee632cf13d414b0",
    "version": "1.0.0",
    "last_updated": "2025-09-30 09:03:50",
    "ipfs_hash": null,
    "zkp_metadata": null
  }
]
```
- `session_state` preview rows returned: `1`
```json
[
  {
    "id": "user789",
    "phase": null,
    "waiting_for": null,
    "last_feedback": null,
    "last_action": null,
    "timestamp": "2025-09-30 09:03:50"
  }
]
```

## Candidate Profile / Template Files
- candidate files found: `2`
- `templates/agent-template.json` class=`agent_profile_or_template_candidate` size=`643` sha16=`ed18366ba9e5808a`
- `templates/user-template.json` class=`user_profile_or_template_candidate` size=`1662` sha16=`97aeb120737d7c2e`

## Safety Checks
- `env_secret_values_read`: `False`
- `env_stat_unchanged`: `True`
- `canonical_db_sha_unchanged`: `True`
- `legacy_db_sha_unchanged`: `True`
- `database_write_performed`: `False`
- `profiles_created`: `False`
- `agent_identity_activation_performed`: `False`

## Findings
- **INFO** `IV_CANONICAL_DB_READONLY_OK` — Canonical Identity Vault database opened in read-only mode.
- **WARN** `IV_LEGACY_PROFILE_ROWS_FOUND` — Legacy database contains profiles=1, session_state=1; review/migration preview is needed before creating new profiles.
- **INFO** `IV_CANONICAL_PROFILE_ROWS_EMPTY` — Canonical user_profiles and agent_profiles are currently empty.
- **WARN** `IV_PROFILE_CANDIDATE_FILES_FOUND` — Found 2 local profile/template candidate files for review.

## Recommended Next Safe Step
Create a migration-preview patch that maps the legacy `user789` profile/session row into the new full operational_profile_json structure without writing it yet. Also compare `templates/user-template.json` and `templates/agent-template.json` against the Self-Hosted Identity Vault blueprint before any profile rows are created.
