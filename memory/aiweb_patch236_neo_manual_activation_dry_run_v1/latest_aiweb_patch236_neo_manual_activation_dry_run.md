# Patch 236 — Neo Manual Activation Dry-Run Gate

Generated: `20260524_113821_UTC`
Verdict: `NEO_MANUAL_ACTIVATION_DRY_RUN_READY`
OK: `True`
Target agent: `neo.local`

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

## Identity mutation preview

Before:
- `agent_id`: `neo.local`
- `activation_state`: `inactive_draft`
- `is_active`: `False`
- `namespace_path`: `/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local`
- `profile_hash`: `df922d109948a5e5…`

After preview:
- `agent_id`: `neo.local`
- `activation_state`: `active_governed`
- `is_active`: `1`
- `last_validated_at`: `20260524_113821_UTC`
- `session_state`: `initialize_only_if_missing_or_explicitly_allowed`
- `activation_receipt_type`: `forge_manual_activation_receipt`
- `activation_manifest_hash`: `f001351736b98d4a5915cf0e47a7d3b2ea150f56b59cda6b7180573773b44414`

## Neo public role contract

- `allowed_plain_language_summaries`: `True`
- `allowed_public_onboarding`: `True`
- `allowed_faq_drafting`: `True`
- `allowed_non_sensitive_help`: `True`
- `forbidden_private_memory_exposure`: `True`
- `forbidden_secret_reads`: `True`
- `forbidden_database_writes`: `True`
- `forbidden_identity_mutation_by_agent`: `True`
- `forbidden_tool_execution`: `True`
- `forbidden_memory_write_without_forge_receipt`: `True`

## Checks

- `PASS` `patch235f_verified` — {'path': '/home/nic/forge/memory/aiweb_patch235f_rmc_controlled_athena_test_receipt_verify_v1/latest_aiweb_patch235f_rmc_controlled_athena_test_receipt_verify.json', 'exists': True, 'ok': True, 'verdict': 'RMC_TEST_RECEIPT_VERIFIED_GOVERNED_ATHENA', 'expected_verdict': 'RMC_TEST_RECEIPT_VERIFIED_GOVERNED_ATHENA', 'verdict_matches': True, 'write_type': 'test_receipt', 'agent': 'athena.local', 'receipt_hash_valid': True, 'raw_error': None}
- `PASS` `neo_preflight_ready` — READY_FOR_MANUAL_ACTIVATION
- `PASS` `neo_profile_found` — {'agent_id': 'neo.local', 'read_ok': True, 'found': True, 'activation_state': 'inactive_draft', 'is_active': False, 'rmc_namespace': 'rmc/agents/neo.local', 'role': 'Public / Frontline Assistant Identity', 'identity_db_written_by_this_patch': False, 'raw_read_error': None}
- `PASS` `neo_inactive_draft` — activation_state='inactive_draft'
- `PASS` `neo_is_active_false` — is_active=False
- `PASS` `neo_namespace_present` — {'identity_vault_pointer': 'rmc/agents/neo.local', 'allowed_root': '/home/nic/aiweb/runtime_wrappers/ancestral_memory', 'resolved_absolute_path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local', 'status': {'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local', 'exists': True, 'is_dir': True, 'children': [{'name': 'manifests', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/manifests', 'exists': True, 'is_dir': True, 'file_count': 0}, {'name': 'receipts', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/receipts', 'exists': True, 'is_dir': True, 'file_count': 0}, {'name': 'echo', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/echo', 'exists': True, 'is_dir': True, 'file_count': 0}, {'name': 'private_context', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/private_context', 'exists': True, 'is_dir': True, 'file_count': 0}, {'name': 'phase_records', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/phase_records', 'exists': True, 'is_dir': True, 'file_count': 0}], 'all_expected_children_exist': True, 'files_or_records_written_by_this_patch': False}, 'live_memory_write_allowed': False}
- `PASS` `neo_profile_hash_present` — profile hash must be present or computable
- `PASS` `gilligan_stays_active_governed` — {'agent_id': 'gilligan.local', 'read_ok': True, 'found': True, 'activation_state': 'active_governed', 'is_active': True, 'rmc_namespace': 'rmc/agents/gilligan.local', 'role': 'Recursive Mirror / Forge-Governed Development Co-Pilot', 'identity_db_written_by_this_patch': False, 'raw_read_error': None}
- `PASS` `athena_stays_active_governed` — {'agent_id': 'athena.local', 'read_ok': True, 'found': True, 'activation_state': 'active_governed', 'is_active': True, 'rmc_namespace': 'rmc/agents/athena.local', 'role': 'Governance / Strategy / Investor-Facing Analysis Agent', 'identity_db_written_by_this_patch': False, 'raw_read_error': None}
- `PASS` `target_is_neo_only` — neo.local

This is a dry-run gate. It previews Neo activation but performs no Identity Vault write and no activation.

Patch 236A — Neo manual activation apply, token-gated and Neo-only.
