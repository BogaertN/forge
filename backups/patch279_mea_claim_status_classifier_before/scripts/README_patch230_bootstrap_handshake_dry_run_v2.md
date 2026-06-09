# Patch 230 — AI.Web Bootstrap Handshake Dry-Run v2

Purpose: add the first dry-run handshake command after RMC namespace scaffolds are verified.

New Forge commands:

- `forge-bootstrap-handshake-dry-run [agent_id]`
- `forge-bootstrap-handshake-report`

Default agent: `gilligan.local`.

Boundary:

- Writes only a Forge-owned report under `/home/nic/forge/memory/aiweb_patch230_bootstrap_handshake_dry_run_v2/`.
- Reads Identity Vault through SQLite read-only mode.
- Reads the existing Patch 229B scaffold verification report.
- Verifies the selected agent namespace scaffold exists.
- Compiles a dry-run manifest preview.
- Stops because the profile is expected to be `inactive_draft`.
- Does not write RMC memory.
- Does not mutate Identity Vault.
- Does not activate any agent.
- Does not execute ProtoForge2.
- Does not call EchoForge creation.

Expected runtime verdict for the current build:

`HANDSHAKE_DRY_RUN_PROFILE_FOUND_BUT_INACTIVE`

That verdict is a pass. It proves Forge can see the profile and namespace pointer while respecting the inactive activation gate.
