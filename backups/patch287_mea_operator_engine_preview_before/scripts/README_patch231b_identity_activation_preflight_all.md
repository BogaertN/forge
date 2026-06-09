# Patch 231B — Multi-Agent Activation Preflight Verification

Adds read-only batch preflight commands for the three approved inactive draft identities:

- `forge-agent-activation-preflight-all`
- `forge-agent-activation-preflight-all-report`

Boundary: batch verification only. No activation command is installed or executed. No RMC memory write. No Identity Vault DB write. No agent activation.

Expected command surface after install: `800/800`.

Expected successful verdict if all profiles are ready:

`ALL_TARGET_AGENTS_READY_FOR_MANUAL_ACTIVATION`

If any profile fails, the command should return:

`BLOCKED_ACTIVATION_PREFLIGHT_ALL_TARGETS`

with explicit per-agent blockers.
