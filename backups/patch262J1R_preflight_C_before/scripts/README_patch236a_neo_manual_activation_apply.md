# Patch 236A — Neo Manual Activation Apply

Installs the Neo-only, token-gated manual activation apply command.

Commands added:

- `forge-agent-activate-neo-manual`
- `forge-agent-activate-neo-manual-report`

Boundary:

- Only `neo.local` is allowed.
- Requires exact token: `CONFIRM_NEO_ACTIVE_GOVERNED`.
- Expected mutation: `activation_state: inactive_draft -> active_governed`, `is_active: 0 -> 1`, and `last_validated_at` update.
- Requires Patch 236 dry-run readiness.
- Requires Neo activation preflight readiness.
- Requires Gilligan and Athena to already be active_governed.
- No RMC memory write.
- No private memory exposure.
- No autonomous execution.
- No Forge bypass.
- No patch autonomy.
