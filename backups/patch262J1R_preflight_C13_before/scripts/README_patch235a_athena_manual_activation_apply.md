# Patch 235A — Athena Manual Activation Apply

This patch installs the Athena-only, explicit-token manual activation apply command.

## Commands added

- `forge-agent-activate-athena-manual athena.local CONFIRM_ATHENA_ACTIVE_GOVERNED`
- `forge-agent-activate-athena-manual-report`

## Boundary

This patch may write only the approved Athena Identity Vault activation fields:

- `activation_state`: `inactive_draft` → `active_governed`
- `is_active`: `0`/`False` → `1`/`True`
- `last_validated_at`: current UTC timestamp
- `session_state`: initialized only if present and empty

It must not grant autonomous tool execution, memory autonomy, secret reads, Forge bypass, patch autonomy, ProtoForge2 execution, or EchoForge creation.

## Required command

```bash
forge-agent-activate-athena-manual athena.local CONFIRM_ATHENA_ACTIVE_GOVERNED
```

The command refuses missing/incorrect tokens and refuses every target except `athena.local`.

## Report path

```bash
/home/nic/forge/memory/aiweb_patch235a_athena_manual_activation_apply_v1/
```
