# Patch 232A — Gilligan Manual Activation Dry-Run Gate

Adds two Forge commands:

- `forge-agent-activate-gilligan-dry-run`
- `forge-agent-activate-gilligan-dry-run-report`

This patch is a dry-run gate only. It previews the future Identity Vault mutation for `gilligan.local` only:

- `activation_state: inactive_draft -> active_governed`
- `is_active: 0 -> 1`
- `last_validated_at: current UTC timestamp`
- `session_state: initialize only if missing or explicitly allowed`

Boundary:

- Does not install `forge-agent-activate-manual`
- Does not write Identity Vault
- Does not write live RMC memory
- Does not activate Gilligan
- Does not activate Athena or Neo
- Does not allow autonomous tool execution

Expected command surface after install: `804/804`.
