# Patch 240A — Terminus ProtoForge Browser Command Fix

Purpose:
Patch 240 made the ProtoForge sidebar visible and added API allowlist entries, but the browser-side command allowlist did not include the ProtoForge commands. Clicking those sidebar items therefore rendered the generic Forge placeholder instead of calling `/api/command`.

This patch fixes that by:

- adding `forge-protoforge-status` to Terminus browser safe commands
- adding `forge-protoforge-simulation-plan` to Terminus browser safe commands
- adding `forge-protoforge-result-show` to Terminus browser safe commands
- adding `forge-protoforge-simulation-run-approved` to Terminus browser gated commands
- allowing `/api/command` to accept either `{cmd,args}` or `{command:"cmd args"}`
- allowing a direct API call with `gate:"RUN-PROTOFORGE"` to satisfy the gate

Boundary:
- no new Forge CLI commands
- no command surface delta
- no UI redesign
- no Identity Vault write
- no RMC live memory write
- no arbitrary browser command execution
