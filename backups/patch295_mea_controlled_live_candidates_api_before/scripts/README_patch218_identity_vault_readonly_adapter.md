# Patch 218 — Forge Identity Vault Read-Only Adapter

This patch installs a Forge-side read-only adapter file:

- `forge/agents/forge/identity_vault_adapter.py`

And one verifier:

- `forge/scripts/identity_vault_patch218_verify.py`

Boundary:

- Does not register Forge tools.
- Does not activate agent identities.
- Does not read `.env` secret values.
- Does not write Identity Vault databases.
- Does not write RMC memory.
- Does not modify Forge registry.

Run:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile agents/forge/identity_vault_adapter.py scripts/identity_vault_patch218_verify.py
python scripts/identity_vault_patch218_verify.py
```
