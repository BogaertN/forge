# Patch 226A.1 — Identity Vault Profile Inventory Scan Hotfix

This hotfix replaces Patch 226A, which failed because the script used `stat.S_IMODE(...)` without importing the Python `stat` module.

## Boundary

This patch installs a corrected read-only inventory scanner only.

It does not modify Identity Vault databases, `.env`, `node_modules`, Forge registry, service contracts, RMC memory, AI.Web wrappers, or agent identity activation state.

It writes reports only under:

`/home/nic/forge/memory/identity_vault_patch226a1_profile_inventory_scan_v1/`

## Purpose

Before creating any inactive Gilligan, Athena, Neo, or Nic operational profile rows, this scanner inventories what already exists in:

- `/home/nic/identity-vault/data/identity_vault.db`
- `/home/nic/identity-vault/vault.db`
- local Identity Vault profile/template candidate files

The scan reads SQLite databases in read-only mode and does not read `.env` secret values.
