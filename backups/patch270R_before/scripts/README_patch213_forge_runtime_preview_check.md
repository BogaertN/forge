# Patch 213 - Forge RMC Runtime Preview Check

This patch adds a read-only verifier script:

`forge/scripts/rmc_patch213_forge_runtime_preview_check.py`

Purpose:

- Confirm Forge's command-surface command still exists.
- Confirm Patch 212's RMC read-only tool definitions are present in `agents/forge/tools.py`.
- Confirm `tool_registry.json` is still untouched by RMC tool names.
- Import Forge's tool layer and run read-only preview smoke calls.
- Write a report under `~/forge/memory/rmc_patch213_forge_runtime_preview_v1/`.

This patch does not modify Forge tools, the registry, Identity Vault, RMC memory, AI.Web wrappers, or agent identity configuration.

After the script passes, the next manual check is to run Forge interactively and use `forge-command-surface` to confirm no command regression.
