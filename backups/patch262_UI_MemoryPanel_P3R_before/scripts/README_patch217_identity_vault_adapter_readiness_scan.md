# Patch 217 — Identity Vault Adapter Readiness Scan

This patch adds a read-only readiness scanner for the future Forge-to-Identity-Vault adapter.

It does not install an adapter. It does not activate agent identities.

## Files Added

- `forge/scripts/identity_vault_patch217_adapter_readiness_scan.py`
- `forge/scripts/README_patch217_identity_vault_adapter_readiness_scan.md`

## Boundary

The script reads only:

- the draft Identity Vault service contract,
- approved package metadata,
- `.gitignore` / `.dockerignore` text,
- SQLite schema and row counts through a read-only SQLite connection.

The script does not read `.env` secret values. It records `.env` stat metadata only.

The script writes reports only under:

- `forge/memory/identity_vault_patch217_adapter_readiness_scan_v1/`

## Expected Use

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile scripts/identity_vault_patch217_adapter_readiness_scan.py
python scripts/identity_vault_patch217_adapter_readiness_scan.py
cat ~/forge/memory/identity_vault_patch217_adapter_readiness_scan_v1/latest_identity_vault_patch217_adapter_readiness_scan.md
```
