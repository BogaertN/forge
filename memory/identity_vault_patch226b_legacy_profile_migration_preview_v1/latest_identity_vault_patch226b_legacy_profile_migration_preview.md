# Identity Vault Patch 226B Legacy Profile Migration Preview

Timestamp: `20260523_210044_UTC`
Verdict: **FAIL**

## Boundary
- This patch is read-only except for writing reports under Forge memory.
- It reads canonical and legacy SQLite databases through read-only connections.
- It does not read `.env` secret values.
- It does not write databases, create profiles, or activate identities.

## Canonical Database
- path: `/home/nic/identity-vault/data/identity_vault.db` opened_readonly=`True` ok=`True`
- row counts: `{'agent_profiles': 0, 'audit_logs': 0, 'feedback_logs': 0, 'session_state': 0, 'sqlite_sequence': 0, 'user_profiles': 0}`

## Legacy Database
- path: `/home/nic/identity-vault/vault.db` opened_readonly=`True` ok=`True`
- row counts: `{'feedback_logs': 0, 'profiles': 1, 'session_state': 1, 'sqlite_sequence': 0}`
- schemas:
  - `feedback_logs`: `id, profile_id, type, data, timestamp`
  - `profiles`: `id, type, data, version, last_updated, ipfs_hash, zkp_metadata`
  - `session_state`: `id, phase, waiting_for, last_feedback, last_action, timestamp`
  - `sqlite_sequence`: `name, seq`

### Legacy Profile Preview
```json
[
  {
    "id": "user789",
    "type": "user",
    "data": {
      "redacted": true,
      "length": 190,
      "sha16": "24e4b7f1aac0798a",
      "colon_segment_count": 3,
      "segment_lengths": [
        24,
        132,
        32
      ],
      "format_guess": "colon_delimited_ciphertext_or_encoded_payload",
      "json_type": null
    },
    "version": "1.0.0",
    "last_updated": "2025-09-30 09:03:50",
    "ipfs_hash": null,
    "zkp_metadata": null
  }
]
```

## Template Alignment
- user template exists=`True` json_ok=`False` alignment=`None`
- agent template exists=`True` json_ok=`False` alignment=`None`

## Migration Preview
- preview records: `1`
```json
[
  {
    "target_table": "user_profiles",
    "target_lookup_id": "user789",
    "write_status": "PREVIEW_ONLY_NOT_WRITTEN",
    "can_auto_migrate_full_profile": false,
    "reason": "Legacy payload is encrypted/encoded or not safely readable as blueprint JSON; preserve source reference and create/verify profile manually unless app-level decryption is explicitly approved.",
    "suggested_core_fields": {
      "user_id": "user789",
      "canonical_name": "",
      "version": "1.0.0",
      "is_active": 0,
      "profile_schema_version": "1.0.0-blueprint"
    },
    "suggested_operational_profile_json_skeleton": {
      "user_id": "user789",
      "canonical_name": "",
      "spirit_name": "",
      "project_affiliations": [],
      "identity_tags": [],
      "version": "1.0.0",
      "last_updated": "2025-09-30 09:03:50",
      "project_context": {
        "current_project": "AI.Web",
        "phase": "",
        "current_files": [],
        "active_collaborators": [],
        "subsystems": [
          "Identity Vault",
          "Forge",
          "RMC"
        ],
        "goals": []
      },
      "interaction_preferences": {},
      "meta_rules": {},
      "session_state": {
        "phase": "",
        "waiting_for": "",
        "last_feedback": "",
        "last_action": "",
        "timestamp": "2025-09-30 09:03:50"
      },
      "legacy_migration_reference": {
        "source_database": "/home/nic/identity-vault/vault.db",
        "source_table": "profiles",
        "source_id": "user789",
        "payload_format_guess": "colon_delimited_ciphertext_or_encoded_payload",
        "payload_sha16": "24e4b7f1aac0798a"
      }
    }
  }
]
```

## Safety Checks
- `env_secret_values_read`: `False`
- `env_stat_unchanged`: `True`
- `canonical_db_sha_unchanged`: `True`
- `legacy_db_sha_unchanged`: `True`
- `database_write_performed`: `False`
- `profiles_created`: `False`
- `agent_identity_activation_performed`: `False`

## Findings
- **WARN** `IV_LEGACY_PROFILE_PRESENT` — Legacy Vault has `1` profile row(s).
- **WARN** `IV_LEGACY_PAYLOAD_NOT_PLAINTEXT_JSON` — Legacy payload appears encrypted/encoded, so this patch does not map private content into the canonical profile.
- **INFO** `IV_NO_MUTATION` — No profiles were created and no identities were activated.

## Recommended Next Safe Step
If the legacy `user789` encrypted/encoded row is not useful, create inactive draft canonical profiles from the Identity Vault blueprint/templates: one Nic user profile and inactive Gilligan/Athena/Neo agent profiles. Preserve the legacy row as a migration reference only. Do not activate identities yet.
