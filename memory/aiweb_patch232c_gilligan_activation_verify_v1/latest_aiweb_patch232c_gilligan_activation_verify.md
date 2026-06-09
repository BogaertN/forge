# Patch 232C — Gilligan Activation Verification

Generated: `20260524_011541_UTC`
Verdict: `GILLIGAN_ACTIVATION_VERIFIED_ACTIVE_GOVERNED`
OK: `True`
Checks: `28/28`

## Agent states

- `gilligan.local` activation_state=`active_governed` is_active=`True`
- `athena.local` activation_state=`inactive_draft` is_active=`False`
- `neo.local` activation_state=`inactive_draft` is_active=`False`

## Boundary

This verification writes only Forge-owned reports. It does not mutate Identity Vault, does not write RMC memory, and does not grant autonomous tool execution.

## Checks

- `PASS` `patch232b_report_exists` — /home/nic/forge/memory/aiweb_patch232b_gilligan_manual_activation_apply_v1/latest_aiweb_patch232b_gilligan_manual_activation_apply.json
- `PASS` `patch232b_report_parses` — parsed
- `PASS` `patch232b_apply_ok` — True
- `PASS` `patch232b_expected_verdict` — GILLIGAN_ACTIVATED_ACTIVE_GOVERNED
- `PASS` `patch232b_target_gilligan` — gilligan.local
- `PASS` `patch232b_identity_db_written` — True
- `PASS` `patch232b_rmc_memory_not_written` — False
- `PASS` `patch232b_backup_exists` — /home/nic/forge/memory/aiweb_patch232b_gilligan_manual_activation_apply_v1/db_backups/identity_vault_before_gilligan_activation_20260524_011103_UTC.db
- `PASS` `changed_fields_within_allowed_scope` — activation_state, is_active, last_validated_at
- `PASS` `required_activation_fields_changed` — activation_state, is_active, last_validated_at
- `PASS` `mutation_scope_did_not_touch_athena` — False
- `PASS` `mutation_scope_did_not_touch_neo` — False
- `PASS` `gilligan_profile_read_ok` — read
- `PASS` `gilligan_active_governed` — active_governed
- `PASS` `gilligan_is_active_true` — True
- `PASS` `gilligan_last_validated_present` — 2026-05-24T01:11:03Z
- `PASS` `gilligan_namespace_present` — rmc/agents/gilligan.local
- `PASS` `athena.local_profile_read_ok` — read
- `PASS` `athena.local_still_inactive_draft` — inactive_draft
- `PASS` `athena.local_is_active_false` — False
- `PASS` `neo.local_profile_read_ok` — read
- `PASS` `neo.local_still_inactive_draft` — inactive_draft
- `PASS` `neo.local_is_active_false` — False
- `PASS` `post_activation_preflight_no_longer_ready` — BLOCKED_ACTIVATION_PREFLIGHT_ACTIVATION_STATE_NOT_INACTIVE_DRAFT
- `PASS` `post_activation_preflight_blocks_reactivation` — BLOCKED_ACTIVATION_PREFLIGHT_ACTIVATION_STATE_NOT_INACTIVE_DRAFT
- `PASS` `no_autonomous_tool_execution_granted` — {'forge_may_log_gilligan_handshake_receipts': True, 'forge_may_read_gilligan_permissions': True, 'forge_may_select_gilligan_identity_context': True, 'forge_may_use_gilligan_rmc_namespace_pointer': True, 'gilligan_can_bypass_forge': False, 'gilligan_can_create_patches_without_approval': False, 'gilligan_can_execute_tools_by_itself': False, 'gilligan_can_mutate_identity_vault': False, 'gilligan_can_write_memory_by_itself': False}
- `PASS` `no_forge_bypass_granted` — {'forge_may_log_gilligan_handshake_receipts': True, 'forge_may_read_gilligan_permissions': True, 'forge_may_select_gilligan_identity_context': True, 'forge_may_use_gilligan_rmc_namespace_pointer': True, 'gilligan_can_bypass_forge': False, 'gilligan_can_create_patches_without_approval': False, 'gilligan_can_execute_tools_by_itself': False, 'gilligan_can_mutate_identity_vault': False, 'gilligan_can_write_memory_by_itself': False}
- `PASS` `no_patch_autonomy_granted` — {'forge_may_log_gilligan_handshake_receipts': True, 'forge_may_read_gilligan_permissions': True, 'forge_may_select_gilligan_identity_context': True, 'forge_may_use_gilligan_rmc_namespace_pointer': True, 'gilligan_can_bypass_forge': False, 'gilligan_can_create_patches_without_approval': False, 'gilligan_can_execute_tools_by_itself': False, 'gilligan_can_mutate_identity_vault': False, 'gilligan_can_write_memory_by_itself': False}
