# Identity Vault Patch 215 Hygiene Plan

Timestamp: `20260523_193303_UTC`
Verdict: **PASS**

## Boundary
- This is a planning scan only.
- It writes reports only under Forge memory.
- Does not modify: `Identity Vault files`
- Does not modify: `Identity Vault databases`
- Does not modify: `.env`
- Does not modify: `node_modules`
- Does not modify: `Forge tools`
- Does not modify: `Forge registry`
- Does not modify: `RMC memory`
- Does not modify: `AI.Web wrappers`
- Does not modify: `agent identity configuration`

## Root
- root: `/home/nic/identity-vault`
- exists: `True`

## Canonical Database Decision
- selected canonical path: `/home/nic/identity-vault/data/identity_vault.db`
- legacy path: `/home/nic/identity-vault/vault.db`
- status: `PLAN_ONLY_NOT_APPLIED`
- reason: `data/identity_vault.db` already exists under the app data directory.
- reason: It contains explicit `agent_profiles` and `user_profiles` tables needed for future agent identity boundaries.
- reason: `vault.db` appears to be a legacy root-level runtime database and should not be selected as the forward canonical path without migration review.
- reason: The legacy database schema is narrower and lacks the newer identity tables visible in the data-directory database.
- migration rule: Do not delete or move `vault.db`; treat it as a legacy migration candidate until a later backup + schema migration patch is approved.

## Database Summary
- `/home/nic/identity-vault/data/identity_vault.db` ok=`True` exists=`True`
  - tables: `agent_profiles, audit_logs, feedback_logs, session_state, sqlite_sequence, user_profiles`
  - `agent_profiles` rows: `0`
  - `audit_logs` rows: `0`
  - `feedback_logs` rows: `0`
  - `session_state` rows: `0`
  - `sqlite_sequence` rows: `0`
  - `user_profiles` rows: `0`
- `/home/nic/identity-vault/vault.db` ok=`True` exists=`True`
  - tables: `feedback_logs, profiles, session_state, sqlite_sequence`
  - `feedback_logs` rows: `0`
  - `profiles` rows: `1`
  - `session_state` rows: `1`
  - `sqlite_sequence` rows: `0`

## Sensitive / Runtime File Policy
- `identity-vault/.env` size=`1605` mode=`0o664` sha256=`cf889320efcfdfa308b810d435219af658dc1ff33bb4f9229a8d9c33ca8dc2f2`
- `identity-vault/.env.example` size=`6787` mode=`0o664` sha256=`7a03ca41c258f7d900899466561662c58e60158f490d9a220ac47467ac8f5274`
- `.env` must never be packaged or printed.
- `node_modules/` must never be packaged.
- SQLite database files must not be packaged into patch tarballs unless a future backup/migration patch explicitly requires it and records approval.

## Recommended Ignore / Packaging Exclusion Rules
- `.env`
- `.env.*`
- `!.env.example`
- `node_modules/`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `data/*.db`
- `data/*.sqlite`
- `data/*.sqlite3`
- `backups/`
- `logs/`
- `coverage/`
- `dist/`

## Findings
- **WARN** `IV_NODE_MODULES_PRESENT` — node_modules is present. Do not package it into patches or archives.
- **WARN** `IV_ENV_PRESENT` — .env exists. Do not package it. Rotate secrets if it was shared outside the local machine.
- **WARN** `IV_MULTIPLE_DATABASES` — Multiple SQLite databases exist. Use the plan-selected canonical DB and preserve the other as legacy until migration review.

## Hygiene Plan
1. **Freeze Identity Vault before changes** — Create timestamped backup of package.json, .gitignore, .dockerignore, database metadata, and both database files before any hygiene patch modifies files. Status: `future patch only`
2. **Lock packaging exclusions** — Update archive/patch packaging policy so `.env`, `node_modules/`, SQLite databases, logs, coverage, and runtime backups are never included in future patch tarballs. Status: `future patch only`
3. **Select canonical database path** — Treat `identity-vault/data/identity_vault.db` as canonical because it has the newer agent/user profile schema; keep `identity-vault/vault.db` as legacy migration candidate. Status: `plan decision only`
4. **Prepare database migration review** — Compare rows/schemas, export a migration preview if data exists, and refuse deletion until backup + verification exists. Status: `future patch only`
5. **Create read-only service contract** — Use the generated draft contract as the boundary for the future Forge Identity Vault adapter. Status: `this script writes draft only under Forge memory`
6. **Build read-only adapter after hygiene** — Forge may read identity metadata and RMC namespace pointers, but cannot activate identities or write Identity Vault state until a later approval gate. Status: `future patch only`

## Read-Only Service Contract Draft
- contract: `identity_vault_readonly_service_contract_draft`
- version: `0.1.0-plan-only`
- status: `DRAFT_NOT_ACTIVE`
- role: Agent identity, permissions, profile metadata, and memory namespace pointers. It is not an agent runtime and not the shared memory store.
- allowed writes: none
- future adapter rule: Forge may ask Identity Vault who an agent is, what permissions it has, and which RMC namespace it points to; Forge may not execute agents inside Identity Vault.

## Output Files
- JSON plan: `/home/nic/forge/memory/identity_vault_patch215_hygiene_plan_v1/20260523_193303_UTC/20260523_193303_UTC_identity_vault_patch215_hygiene_plan.json`
- service contract draft: `/home/nic/forge/memory/identity_vault_patch215_hygiene_plan_v1/20260523_193303_UTC/20260523_193303_UTC_identity_vault_readonly_service_contract_draft.json`

## Next Safe Step
Create a future hygiene patch that backs up Identity Vault, adds ignore/packaging rules, and writes the service contract as a draft file only. Do not activate agent identities yet.
