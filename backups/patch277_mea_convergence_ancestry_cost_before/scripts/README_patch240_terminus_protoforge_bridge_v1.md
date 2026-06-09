# Patch 240 — Terminus ProtoForge Bridge v1

Purpose:
Attach the already-installed Patch 239 ProtoForge connector to the live Forge Terminus UI.

This patch does not create a full redesign, tab system, or 3D panel yet.
It only fixes the missed bridge: Terminus `/api/command` did not know how to call the Patch 239 ProtoForge connector commands.

Adds to Terminus UI allowlist:
- forge-protoforge-status
- forge-protoforge-simulation-plan <type>
- forge-protoforge-result-show [run_id]

Adds a UI-side gate for:
- forge-protoforge-simulation-run-approved

Gate word:
- RUN-PROTOFORGE

Also adds a small ProtoForge section to the current left sidebar.

Boundary:
- No new Forge CLI commands
- No command-surface count increase expected
- No Forge UI redesign yet
- No Identity Vault writes
- No RMC live memory writes
- No arbitrary simulation type
- No uncontrolled PyBullet execution
- UI calls route through Forge connector, not around Forge

After install:
1. Start Forge.
2. Run `forge-command-surface`.
3. Run `forge-ui-start`.
4. Open `http://localhost:7477`.
5. Use the new ProtoForge sidebar entries.
