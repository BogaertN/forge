# Patch 229A — RMC Namespace Scaffold Apply

Purpose: apply the reviewed Patch 229 namespace scaffold preview by creating directories only under the preview-selected RMC root.

This patch adds:

- `forge-rmc-namespace-scaffold-apply`
- `forge-rmc-namespace-scaffold-apply-report`

Boundary:

- Creates namespace directories only from `/home/nic/forge/memory/rmc_patch229_namespace_scaffold_preview_v1/latest_rmc_patch229_namespace_scaffold_preview.json`.
- Writes an apply report only under `/home/nic/forge/memory/rmc_patch229a_namespace_scaffold_apply_v1/`.
- Does not write RMC memory records.
- Does not mutate Identity Vault.
- Does not read `.env` values.
- Does not activate agents.

Expected next patch after successful apply: Patch 229B — RMC namespace scaffold verification.
