# Patch 220 — Identity Vault Drift Auto-Confirm Safety Apply

This patch installs one Forge-side script:

- `forge/scripts/identity_vault_patch220_drift_auto_confirm_safety_apply.py`

The script backs up `~/identity-vault/utils/drift.js`, removes the unsafe forced auto-confirm pattern found by Patch 219, and verifies syntax with `node --check`.

It does not read `.env` values, write databases, register Forge tools, write RMC memory, or activate agent identities.
