# Patch 231A.1 — Activation Preflight Report Route Hotfix

Purpose: fix the command router ordering for Patch 231A.

The command `forge-agent-activation-preflight-report` must be matched before the prefix route `forge-agent-activation-preflight <agent_id>`. Without this, the report command is interpreted as a preflight command with no agent_id and overwrites the latest successful report with an `AGENT_ID_REQUIRED` blocker.

Boundary:
- No new command is added.
- Expected command surface remains 798/798.
- No activation command is installed.
- No RMC memory write.
- No Identity Vault DB write.
- No agent activation.
- This is a routing/display hotfix only.

Expected after install:
- `forge-agent-activation-preflight gilligan.local` may return `READY_FOR_MANUAL_ACTIVATION` if real checks pass.
- `forge-agent-activation-preflight-report` should display the latest report without creating a new `AGENT_ID_REQUIRED` report.
