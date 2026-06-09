# Patch 223 — AI.Web Service Contracts Verify

This patch adds a read-only verifier for the five AI.Web service contract draft files.

It verifies:

- `/home/nic/aiweb/service_contracts/forge.contract.json`
- `/home/nic/aiweb/service_contracts/rmc.contract.json`
- `/home/nic/aiweb/service_contracts/identity_vault.contract.json`
- `/home/nic/aiweb/service_contracts/protoforge2.contract.json`
- `/home/nic/aiweb/service_contracts/echoforge.contract.json`

Boundary:

- Does not register Forge connector commands.
- Does not activate agent identities.
- Does not write Identity Vault databases.
- Does not write RMC memory.
- Does not modify Forge registry.
- Does not read `.env` secret values.
- Writes only verification reports under `/home/nic/forge/memory/aiweb_patch223_service_contracts_verify_v1/`.

Run from Forge root:

```bash
python -m py_compile scripts/aiweb_patch223_service_contracts_verify.py
python scripts/aiweb_patch223_service_contracts_verify.py
cat ~/forge/memory/aiweb_patch223_service_contracts_verify_v1/latest_aiweb_patch223_service_contracts_verify.md
```
