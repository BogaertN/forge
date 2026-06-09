# Patch 232B — Gilligan Manual Activation Apply

Adds two Forge commands:

- `forge-agent-activate-manual <agent_id> CONFIRM_GILLIGAN_ACTIVE_GOVERNED`
- `forge-agent-activate-manual-report`

This patch performs the first governed Identity Vault activation mutation for `gilligan.local` only. It refuses Athena, Neo, and every unknown target.

Approved mutation scope:

- `gilligan.local activation_state: inactive_draft -> active_governed`
- `gilligan.local is_active: 0 -> 1`
- `gilligan.local last_validated_at: current UTC timestamp`
- `session_state` initialization only if present and empty
- equivalent activation-state mirrors inside the profile JSON payload when that is where the profile stores activation fields

Boundary:

- No autonomous tool execution
- No live RMC memory write
- No EchoForge
- No ProtoForge2 execution
- No patch autonomy
- No Athena/Neo activation
- No Identity Vault mutation beyond the approved Gilligan activation fields

The command writes a Forge-owned activation receipt and a local backup copy of the Identity Vault DB under Forge memory before mutation.

Expected command surface after install: `806/806`.
