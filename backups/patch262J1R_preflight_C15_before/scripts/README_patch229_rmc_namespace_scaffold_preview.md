# Patch 229 — RMC Namespace Scaffold Preview

Purpose: add Forge commands that preview the RMC shared/agent namespace scaffold layout before any RMC namespace folders are created.

Commands added:

- `forge-rmc-namespace-scaffold-preview`
- `forge-rmc-namespace-scaffold-report`

Write boundary:

- Allowed write: Forge-owned report only under `/home/nic/forge/memory/rmc_patch229_namespace_scaffold_preview_v1/`
- Forbidden: creating `/home/nic/aiweb/rmc` folders
- Forbidden: writing RMC memory
- Forbidden: writing Identity Vault database
- Forbidden: activating agents
- Forbidden: reading `.env` secret values

Expected next patch after review: Patch 229A — RMC namespace scaffold apply.
