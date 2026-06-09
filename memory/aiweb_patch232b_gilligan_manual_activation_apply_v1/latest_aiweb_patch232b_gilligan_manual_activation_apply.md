# Patch 232B — Gilligan Manual Activation Apply

Generated: `20260524_011103_UTC`
Verdict: `GILLIGAN_ACTIVATED_ACTIVE_GOVERNED`
OK: `True`
Target agent: `gilligan.local`

## State
Before activation_state: `inactive_draft`
After activation_state: `active_governed`
Before is_active: `False`
After is_active: `True`

## Boundaries
- `forge_may_select_gilligan_identity_context`: `True`
- `forge_may_read_gilligan_permissions`: `True`
- `forge_may_use_gilligan_rmc_namespace_pointer`: `True`
- `forge_may_log_gilligan_handshake_receipts`: `True`
- `gilligan_can_execute_tools_by_itself`: `False`
- `gilligan_can_write_memory_by_itself`: `False`
- `gilligan_can_bypass_forge`: `False`
- `gilligan_can_mutate_identity_vault`: `False`
- `gilligan_can_create_patches_without_approval`: `False`

## Changed fields
- `activation_state`
- `is_active`
- `last_validated_at`

## Backup
DB backup: `/home/nic/forge/memory/aiweb_patch232b_gilligan_manual_activation_apply_v1/db_backups/identity_vault_before_gilligan_activation_20260524_011103_UTC.db`
Backup sha256: `757715a5aa8407b1fa0cb71476b6ee7348096411272853250967081e534be414`

## Blockers
- none
