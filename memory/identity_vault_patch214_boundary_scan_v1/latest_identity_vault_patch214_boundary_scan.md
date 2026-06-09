# Identity Vault Patch 214 Boundary Scan Report

Timestamp: `20260523_192940_UTC`
Verdict: **PASS**

## Boundary
- This scan is read-only except for writing this report under Forge memory.
- It does not modify Identity Vault, databases, Forge tools, Forge registry, RMC memory, AI.Web wrappers, or agent identity configuration.
- It does not print `.env` contents or secret values; it records only metadata and hashes.

## Root
- root: `identity-vault`
- exists: `True`
- node_modules present: `True`
- sensitive hits: `2`
- database hits: `2`

## Top-Level Entries
- `.dockerignore`
- `.env`
- `.env.example`
- `.git`
- `.gitignore`
- `API_Reference.md`
- `Design_Manual_System_Blueprint.md`
- `Dockerfile`
- `Identity_Vault_Pro.md`
- `Integrating_Legacy_LLMs.md`
- `Product_Overview_Solution_Brief.md`
- `Quick_Setup_Features_Guide.md`
- `README.md`
- `Security_Guide.md`
- `Troubleshooting_Guide.md`
- `User_Manual.md`
- `cli.js`
- `data`
- `db.js`
- `docker-compose.dev.yml`
- `docker-compose.yml`
- `install.sh`
- `nginx.conf`
- `node_modules`
- `package-lock.json`
- `package.json`
- `plugins`
- `public`
- `routes`
- `schemas.js`
- `scripts`
- `security.config.js`
- `server.js`
- `templates`
- `tests`
- `utils`
- `vault.db`

## Package Summary
- name: `identity-vault`
- version: `1.0.0`
- scripts: `build, build:docs, cli, db:backup, db:migrate, db:restore, db:seed, debug, deploy, dev, docker:build, docker:build:dev, docker:logs, docker:run, docker:run:dev, docker:shell, docker:stop, format, format:check, health, install:dev, k8s:delete, k8s:deploy, lint, lint:check, monitoring:start, monitoring:stop, postinstall, preinstall, prepare, release, release:dry, security:audit, security:scan, start, test, test:e2e, test:integration, test:unit, test:watch, type-check, validate`
- dependencies: `@langchain/core, archiver, bcryptjs, chalk, commander, compression, cors, crypto-js, dotenv, express, express-rate-limit, express-validator, fs-extra, helmet, ipfs-core, joi, json-diff, jsonwebtoken, lodash, moment, morgan, multer, multiformats, ngrok, node-cron, node-fetch, prom-client, snarkjs, socket.io, sqlite3, uuid, winston, winston-daily-rotate-file, ws`
- dev dependencies: `@semantic-release/changelog, @semantic-release/git, @semantic-release/github, @types/archiver, @types/bcryptjs, @types/cors, @types/crypto-js, @types/express, @types/jest, @types/jsonwebtoken, @types/lodash, @types/multer, @types/node, @types/uuid, @types/ws, eslint, eslint-config-airbnb-base, eslint-plugin-import, eslint-plugin-jest, eslint-plugin-security, husky, jest, lint-staged, nodemon, prettier, semantic-release, snyk, supertest, ts-jest, tsx, typedoc, typescript`

## Sensitive / Runtime Files Detected
- `identity-vault/.env` size=`1605` mode=`0o664` sha256=`cf889320efcfdfa308b810d435219af658dc1ff33bb4f9229a8d9c33ca8dc2f2`
- `identity-vault/.env.example` size=`6787` mode=`0o664` sha256=`7a03ca41c258f7d900899466561662c58e60158f490d9a220ac47467ac8f5274`

## Database Files Detected
- `identity-vault/data/identity_vault.db` size=`57344` mode=`0o644` sha256=`d185eb83a37a9be907ff6525deb241778772fbc7fcc51794efc4c94ab6ecf32f`
- `identity-vault/vault.db` size=`36864` mode=`0o644` sha256=`1bfcaca815f7149d32b30e261c20d0679d7182191fe55cfa63ce830c287d87b9`

## SQLite Read-Only Schema Summary
- `identity-vault/data/identity_vault.db` ok=`True`
  - tables: `agent_profiles, audit_logs, feedback_logs, session_state, sqlite_sequence, user_profiles`
  - `agent_profiles` rows: `0`
  - `audit_logs` rows: `0`
  - `feedback_logs` rows: `0`
  - `session_state` rows: `0`
  - `user_profiles` rows: `0`
- `identity-vault/vault.db` ok=`True`
  - tables: `feedback_logs, profiles, session_state, sqlite_sequence`
  - `feedback_logs` rows: `0`
  - `profiles` rows: `1`
  - `session_state` rows: `1`

## Git / Ignore Hygiene
- `has_env_rule`: `True`
- `has_node_modules_rule`: `True`
- `has_db_rule`: `False`
- git repo: `True`
- git status returncode: `0`
```text
 M .env.example
 M package.json
 M server.js
 M utils/encryption.js
?? .dockerignore
?? Dockerfile
?? data/
?? docker-compose.dev.yml
?? docker-compose.yml
?? install.sh
?? nginx.conf
?? scripts/
?? security.config.js
```

## Findings
- **WARN** `IV_NODE_MODULES_PRESENT` — node_modules is present and should not be packaged into future patches.
- **WARN** `IV_ENV_PRESENT` — .env is present. Do not package it; rotate secrets if it was shared outside the machine.
- **WARN** `IV_MULTIPLE_DATABASES` — Multiple database files found (2). A canonical database path must be selected before integration.
- **INFO** `IV_GITIGNORE_DB_RULE_MISSING` — .gitignore does not clearly ignore local database/runtime state files.

## Next Safe Step
If this report is understood, create the next patch as an Identity Vault hygiene plan, not an integration patch. The plan should choose the canonical database path, exclude node_modules and .env from future packaging, and prepare a read-only service contract. Do not activate agent identities yet.

