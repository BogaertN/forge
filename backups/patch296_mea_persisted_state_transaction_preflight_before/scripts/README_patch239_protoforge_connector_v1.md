
# Forge Patch 239 — ProtoForge Connector v1

This is Step 5: a tiny Forge connector to the verified ProtoForge Sandbox substrate.

Commands added:

- forge-protoforge-status
- forge-protoforge-simulation-plan [symbolic_frequency_probe|pybullet_fixed_falling_cube]
- forge-protoforge-simulation-run-approved
- forge-protoforge-result-show [run_id]

Boundary:

- No Forge UI change.
- No Identity Vault mutation.
- No RMC live memory write.
- No arbitrary simulation type.
- No shell-enabled subprocess calls.
- Simulation execution is allowed only through the prior plan command and only for allowlisted substrate types.

Expected command surface increase: +4 commands.
