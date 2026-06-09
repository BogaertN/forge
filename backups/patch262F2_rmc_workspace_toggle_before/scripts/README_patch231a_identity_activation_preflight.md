# Patch 231A — Identity Activation Preflight

Adds read-only commands:

- `forge-agent-activation-preflight <agent_id>`
- `forge-agent-activation-preflight-report`

Boundary: preflight only. No activation command is installed. No live RMC memory write. No Identity Vault database write. No agent activation. The command writes Forge-owned preflight receipts only under `/home/nic/forge/memory/aiweb_patch231a_identity_activation_preflight_v1/`.

Expected successful readiness verdict is `READY_FOR_MANUAL_ACTIVATION`. If real profile contracts, permissions, forbidden actions, hash evidence, namespace, or inactive state checks are missing, the command must return `BLOCKED_ACTIVATION_PREFLIGHT_<REASON>` with explicit blockers.
