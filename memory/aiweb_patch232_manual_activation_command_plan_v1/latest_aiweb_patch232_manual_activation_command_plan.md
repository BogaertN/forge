# Patch 232 — Manual Activation Command Design and Preflight Plan

Generated: `20260524_005847_UTC`
Verdict: `MANUAL_ACTIVATION_COMMAND_PLAN_WRITTEN`
OK: `True`
Plan only: `True`
Future command: `forge-agent-activate-manual <agent_id>`

## Prior 231B Gate

- `path`: `/home/nic/forge/memory/aiweb_patch231b_identity_activation_preflight_all_v1/latest_aiweb_patch231b_identity_activation_preflight_all.json`
- `exists`: `True`
- `verdict`: `ALL_TARGET_AGENTS_READY_FOR_MANUAL_ACTIVATION`
- `ok`: `True`
- `ready_agents_count`: `3`
- `target_agents_count`: `3`

## Manual Activation Contract

- `command_name`: `forge-agent-activate-manual`
- `syntax`: `forge-agent-activate-manual <agent_id>`
- `no_default_agent`: `True`
- `allowed_targets`: `['gilligan.local', 'athena.local', 'neo.local']`
- `requires_explicit_agent_id`: `True`
- `requires_manual_user_approval`: `True`
- `requires_valid_profile_hash`: `True`
- `requires_valid_service_contracts`: `True`
- `requires_valid_rmc_namespace`: `True`
- `requires_passing_echo_validator`: `True`
- `requires_fresh_agent_preflight`: `True`
- `requires_patch231b_all_agents_ready_or_explicit_single_agent_exception`: `True`
- `requires_forge_audit_receipt`: `True`
- `must_refuse_if_agent_already_active`: `True`
- `must_refuse_if_activation_state_not_inactive_draft`: `True`
- `must_refuse_if_identity_profile_changed_after_preflight`: `True`
- `must_refuse_if_rmc_namespace_changed_after_preflight`: `True`

## Future Preflight Steps

- Read the selected Identity Vault profile by explicit agent_id.
- Verify profile hash and compare to the last successful Patch 231A/231B preflight receipt.
- Verify activation_state == inactive_draft and is_active == 0 before activation.
- Verify required service contracts, permissions, forbidden actions, and required profile fields still exist.
- Verify the resolved RMC namespace path exists and is inside the approved ancestral_memory root.
- Run a dry-run manifest compile and echo validation before any state change.
- Require manual approval text/token in the future activation command flow.
- Write a Forge audit receipt before and after any future activation state mutation.
- Abort on any mismatch; do not auto-repair and do not partially activate.

## Fields Allowed to Change in a Future Activation

- `activation_state: inactive_draft -> active_manual_approved`
- `is_active: 0 -> 1`
- `activated_at_utc`
- `activated_by`
- `activation_receipt_id`
- `activation_profile_hash`
- `activation_rmc_namespace_path`
- `activation_service_contract_snapshot_hash`

## Fields Never Changed Automatically

- `agent_id`
- `display_name`
- `role`
- `purpose`
- `permissions`
- `forbidden_actions`
- `service_contracts`
- `rmc_namespace_pointer`
- `profile_hash_algorithm`
- `created_at_utc`
- `source_identity_document`

## Rollback Contract

- `rollback_requires_separate_manual_command`: `True`
- `future_rollback_command`: `forge-agent-deactivate-manual <agent_id>`
- `rollback_changes_only_activation_fields`: `True`
- `rollback_preserves_activation_receipts`: `True`
- `rollback_does_not_delete_rmc_memory`: `True`
- `rollback_does_not_delete_identity_profile`: `True`
- `rollback_writes_forge_audit_receipt`: `True`

## Boundary

- `forge_owned_plan_report`: `True`
- `rmc_memory_written`: `False`
- `identity_vault_database_written`: `False`
- `agent_identity_activation_performed`: `False`
- `manual_activation_command_installed`: `False`
- `manual_activation_command_executed`: `False`
- `protoforge2_execution_performed`: `False`
- `echoforge_creation_performed`: `False`
- `env_secret_values_read`: `False`

This patch designs the future manual activation command contract only. It does not install forge-agent-activate-manual and cannot activate an identity.

Patch 232A — manual activation command dry-run/preflight gate, still not activation.
