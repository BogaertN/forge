# Identity Vault Patch 221 DB Canonical Path + Testability Apply

Timestamp: `20260523_200040_UTC`
Verdict: **FAIL**

## Boundary
- This patch modifies Identity Vault JS path references and writes one static test file only after backup.
- It does not modify Identity Vault database contents.
- It does not read .env secret values.
- It does not package node_modules, register Forge tools, write RMC memory, or activate agent identities.

## Backup
- backup root: `/home/nic/forge/backups/patch221_identity_vault_db_canonical_testability_before/20260523_200040_UTC`
- `/home/nic/identity-vault/db.js`: **COPIED**
- `/home/nic/identity-vault/package.json`: **COPIED**
- `/home/nic/identity-vault/tests/db.canonical.test.js`: **SKIPPED (missing)**
- `/home/nic/identity-vault/cli.js`: **COPIED**
- `/home/nic/identity-vault/server.js`: **COPIED**

## Canonical DB Decision
- canonical DB path: `/home/nic/identity-vault/data/identity_vault.db`
- legacy DB path preserved: `/home/nic/identity-vault/vault.db`
- canonical DB exists: `True`
- legacy DB exists: `True`

## File Changes
- files changed: `3`
  - `cli.js`
  - `server.js`
  - `tests/db.canonical.test.js`
- canonical static test written: `True`

## Legacy Reference Scan
- before legacy refs in JS: `6`
- after legacy refs in JS: `10`
- remaining legacy refs:
  - `cli.js`: `1`
  - `db.js`: `1`
  - `scripts/init-database.js`: `2`
  - `scripts/reset-database.js`: `1`
  - `server.js`: `1`
  - `tests/db.canonical.test.js`: `4`

## Syntax Checks
- `db.js`: **PASS** returncode=`0`
- `tests/db.canonical.test.js`: **PASS** returncode=`0`
- `cli.js`: **PASS** returncode=`0`
- `server.js`: **PASS** returncode=`0`

## Optional Jest Check
- attempted: `True`
- ok: `False` returncode=`1`

## Database Read-Only Summary
- canonical: path=`/home/nic/identity-vault/data/identity_vault.db` ok=`True` opened_readonly=`True`
  - tables: `agent_profiles, audit_logs, feedback_logs, session_state, sqlite_sequence, user_profiles`
- legacy_preserved: path=`/home/nic/identity-vault/vault.db` ok=`True` opened_readonly=`True`
  - tables: `feedback_logs, profiles, session_state, sqlite_sequence`

## No-Mutation / Safety Checks
- `env_secret_values_read`: `False`
- `env_stat_unchanged`: `True`
- `canonical_db_sha_unchanged`: `True`
- `legacy_db_sha_unchanged`: `True`
- `database_write_performed`: `False`
- `agent_identity_activation_performed`: `False`
- `forge_tool_registry_modified`: `False`

## Findings
- **WARN** `IV_LEGACY_DB_REFS_REMAIN` — Some vault.db references remain in scanned JS files; review before connector registration.
- **INFO** `IV_NODE_SYNTAX_OK` — Changed/tested JS files pass node --check.
- **INFO** `IV_CANONICAL_DB_READONLY_OK` — Canonical DB opens read-only after path normalization.
- **FAIL** `IV_SAFETY_SNAPSHOT_CHANGED` — A protected safety snapshot changed unexpectedly.
- **WARN** `IV_OPTIONAL_JEST_FAILED` — Static canonical DB Jest test did not pass in this environment; inspect stdout/stderr tail in JSON report.

## Next Safe Step
Create the five AI.Web service contract draft files under `/home/nic/aiweb/service_contracts/`, then verify them before adding Forge read-only connector commands.
