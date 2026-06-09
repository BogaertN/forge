# Patch 259 — Left Rail Command Launcher

Purpose: wire the production Operator Console left rail into existing safe UI surfaces and Forge's existing `/api/command` bridge.

This patch does not add Forge CLI commands. It does not add a new backend endpoint. It does not grant shell access. It does not grant direct file write access. It does not write Identity Vault or RMC live memory.

Buttons wired:

- Open Terminus: opens `/` fallback Terminus in a new browser tab.
- Capture Page: switches to Forge Output and focuses the existing Page Capture panel.
- ProtoForge Status: runs existing safe command `forge-protoforge-status` through `/api/command`.
- Plan Cube Sim: runs existing safe command `forge-protoforge-simulation-plan pybullet_fixed_falling_cube` through `/api/command`.
- Run Approved Sim: prompts the operator, then uses the existing gated command `forge-protoforge-simulation-run-approved` with gate `RUN-PROTOFORGE`.
- Latest Result: runs existing safe command `forge-protoforge-result-show` through `/api/command`.

Next patch: Patch 260 — Right Rail Runtime Status.
