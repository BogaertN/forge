# Patch 212 — RMC Read-Only Tool Registration

This patch registers four read-only RMC preview functions into Forge's live tool surface by appending a guarded block to `~/forge/agents/forge/tools.py`.

Registered tools:

- `rmc_phase_parse_preview`
- `rmc_drift_check_preview`
- `rmc_echo_validate_preview`
- `rmc_pipeline_preview`

Boundary:

- Does not modify `tool_registry.json`.
- Does not wire Gilligan personality mode.
- Does not touch Identity Vault.
- Does not write RMC memory.
- Does not modify AI.Web runtime wrapper modules.

Run order:

1. Extract patch.
2. Run `python scripts/rmc_patch212_register_readonly_tools.py`.
3. Run `python scripts/rmc_patch212_verify.py`.
4. Review the reports under `~/forge/memory/`.
