# Patch 232A — Gilligan Manual Activation Dry-Run Gate

Generated: `20260524_010516_UTC`
Verdict: `GILLIGAN_MANUAL_ACTIVATION_DRY_RUN_READY`
OK: `True`
Target agent: `gilligan.local`

## Boundary

- `forge_owned_dry_run_report`: `True`
- `rmc_memory_written`: `False`
- `identity_vault_database_written`: `False`
- `agent_identity_activation_performed`: `False`
- `manual_activation_command_installed`: `False`
- `manual_activation_command_executed`: `False`
- `protoforge2_execution_performed`: `False`
- `echoforge_creation_performed`: `False`
- `env_secret_values_read`: `False`

## Mutation preview

Before:
- `activation_state`: `inactive_draft`
- `is_active`: `False`
- `namespace_path`: `/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local`
- `profile_hash`: ``

After preview:
- `activation_state`: `active_governed`
- `is_active`: `1`
- `last_validated_at`: `20260524_010516_UTC`
- `session_state`: `initialize_only_if_missing_or_explicitly_allowed`
- `activation_receipt_type`: `forge_manual_activation_receipt`
- `activation_manifest_hash`: `c9f20e59c8aad9cedfcf123ff83e709674db49c9ea737f1f15ea80e64ccff604`

Fields allowed to change in the future apply:
- `activation_state`
- `is_active`
- `last_validated_at`
- `activation_receipt_id`
- `activation_profile_hash`
- `activation_manifest_hash`
- `session_state (only if missing or explicitly allowed)`

Fields confirmed unchanged by the future contract:
- `agent_id`
- `role`
- `permissions`
- `forbidden_actions`
- `service_contracts`
- `profile_hash source fields`
- `rmc_namespace_pointer`
- `governance_boundaries`

## Active does not mean autonomous

- `forge_may_select_gilligan_identity_context`: `True`
- `forge_may_read_gilligan_permissions`: `True`
- `forge_may_use_gilligan_rmc_namespace_pointer`: `True`
- `forge_may_log_gilligan_handshake_receipts`: `True`
- `gilligan_can_execute_tools_by_itself`: `False`
- `gilligan_can_write_memory_by_itself`: `False`
- `gilligan_can_bypass_forge`: `False`
- `gilligan_can_mutate_identity_vault`: `False`
- `gilligan_can_create_patches_without_approval`: `False`

This is a dry-run gate. It previews the activation mutation but performs no Identity Vault write and no activation.

Patch 232B — install and run the Gilligan-only manual activation apply command.
