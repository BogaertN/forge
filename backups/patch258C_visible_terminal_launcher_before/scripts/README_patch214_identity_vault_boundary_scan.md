# Patch 214 — Identity Vault Boundary Scan

This patch adds a read-only scanner for `~/identity-vault`.

It does not integrate Identity Vault into Forge yet. It does not activate agent identities. It does not modify databases, `.env`, Forge tools, Forge registry, AI.Web wrappers, or RMC memory.

The scanner writes reports only under:

`~/forge/memory/identity_vault_patch214_boundary_scan_v1/`

The scanner checks:

- Whether `~/identity-vault` exists.
- Top-level files and folders.
- Whether `node_modules` is present.
- Whether sensitive/runtime files such as `.env` exist.
- Whether database files exist.
- SQLite schema and row-count summaries using read-only mode.
- `package.json` scripts and dependency names.
- `.gitignore` hygiene for `.env`, `node_modules`, and local DB/runtime files.
- Git status if the folder is a git repository.

It does not print secret values from `.env`.

Next safe step after this scan: create an Identity Vault hygiene plan before any live integration.
