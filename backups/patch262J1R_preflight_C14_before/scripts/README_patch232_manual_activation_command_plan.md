# Patch 232 — Manual Activation Command Design and Preflight Plan

Adds two Forge commands:

- `forge-agent-activation-command-plan`
- `forge-agent-activation-command-plan-report`

This patch is plan-only. It requires the Patch 231B all-agent preflight receipt and writes a Forge-owned activation command design report under `~/forge/memory/aiweb_patch232_manual_activation_command_plan_v1/`.

Boundary:

- Does not install `forge-agent-activate-manual`
- Does not execute activation
- Does not write RMC memory
- Does not write the Identity Vault database
- Does not activate Gilligan, Athena, or Neo

Expected command surface after install: `802/802`.
