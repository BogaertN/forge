# Patch 235 — Athena Manual Activation Dry-Run Gate

This patch adds two commands:

- `forge-agent-activate-athena-dry-run`
- `forge-agent-activate-athena-dry-run-report`

Boundary:

- Dry-run only.
- Writes only Forge-owned reports under `/home/nic/forge/memory/aiweb_patch235_athena_manual_activation_dry_run_v1/`.
- Does not write Identity Vault.
- Does not write RMC memory.
- Does not activate Athena.
- Does not activate Neo.
- Does not alter Gilligan.
- Does not grant autonomous execution.

Expected dry-run verdict:

`ATHENA_MANUAL_ACTIVATION_DRY_RUN_READY`

This patch keeps the sequence one-agent-at-a-time after Gilligan's controlled RMC test receipt has been verified.
