# Patch 224 — AI.Web Read-Only Connector Commands

Adds the first Forge CLI connector command layer after the service-contract gate.

Commands added:

- `forge-rmc-status`
- `forge-rmc-test-status`
- `forge-identity-status`
- `forge-agent-list`
- `forge-agent-show <agent_id>`
- `forge-system-boundary-map`

Boundary:

- No RMC memory writes.
- No Identity Vault database writes.
- No `.env` secret reads.
- No agent identity activation.
- No EchoForge build execution.
- No ProtoForge2 live execution.
- No Forge tool registry mutation.

This patch writes a read-only helper module and modifies Forge `main.py` only after backing it up.
