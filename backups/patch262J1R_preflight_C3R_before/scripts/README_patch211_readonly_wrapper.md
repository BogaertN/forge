# Patch 211 — Forge RMC Read-Only Wrapper

This patch creates `forge/agents/forge/rmc_tools.py` as a read-only wrapper around the AI.Web RMC runtime modules.

It does not register tools in Forge.
It does not wire Gilligan.
It does not write RMC memory.
It does not touch Identity Vault.

Run:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile agents/forge/rmc_tools.py scripts/rmc_patch211_verify.py
python scripts/rmc_patch211_verify.py
cat ~/forge/memory/rmc_patch211_readonly_wrapper_v1/latest_rmc_patch211_readonly_wrapper.md
```
