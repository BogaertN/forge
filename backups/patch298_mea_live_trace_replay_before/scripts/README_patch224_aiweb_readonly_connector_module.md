# Patch 224 — AI.Web Read-Only Connector Module

Adds a Forge-side read-only connector helper module:

- `forge/agents/forge/aiweb_readonly_connectors.py`

And a verifier:

- `forge/scripts/aiweb_patch224_readonly_connector_module_verify.py`

This patch does not register Forge commands yet.

The staged connector functions are:

- `forge-rmc-status`
- `forge-rmc-test-status`
- `forge-identity-status`
- `forge-agent-list`
- `forge-agent-show <agent_id>`
- `forge-system-boundary-map`

Boundary:

- No memory writes.
- No app creation.
- No agent mutation.
- No Identity Vault database writes.
- No RMC memory writes.
- No `.env` secret reads.
- No Forge registry writes.
