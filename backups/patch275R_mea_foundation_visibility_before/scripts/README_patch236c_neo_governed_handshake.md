# Patch 236C — Neo Governed Handshake

Adds the first governed active-agent handshake for `neo.local` after Patch 236B verified all three identities as `active_governed`.

## Commands

- `forge-neo-governed-handshake`
- `forge-neo-governed-handshake-report`

## Boundary

This patch writes only a Forge-owned handshake report/receipt under Forge memory. It does not mutate the Identity Vault, does not write RMC memory, does not expose private memory, does not read secrets, does not execute ProtoForge2, does not invoke EchoForge, and does not grant autonomous execution.

Expected verdict: `NEO_HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT`.
