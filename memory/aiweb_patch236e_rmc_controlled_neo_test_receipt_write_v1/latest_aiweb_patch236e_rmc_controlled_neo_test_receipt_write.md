# Patch 236E — Controlled Neo RMC Test Receipt Write

Generated: `20260524_121937_UTC`
Verdict: `RMC_TEST_RECEIPT_WRITTEN_GOVERNED_NEO`
OK: `True`
Agent: `neo.local`
Write type: `test_receipt`
RMC test receipt path: `/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/receipts/neo_handshake_test_20260524_121937_UTC.json`
Receipt hash: `174adc1c00d0354dd954e1db000f482969d90bf238c5615be4bdce233c07104e`
File sha256: `c2607d96baba40638156fde38f7382f0579c8858da102e5a7d1ac141f3f2b7b7`

## Boundary
- `forge_owned_patch236e_report`: `True`
- `rmc_test_receipt_written`: `True`
- `rmc_write_type`: `test_receipt`
- `identity_vault_database_written`: `False`
- `agent_memory_written`: `False`
- `long_term_memory_written`: `False`
- `private_memory_written`: `False`
- `shared_memory_written`: `False`
- `full_chat_content_written`: `False`
- `secret_values_written`: `False`
- `secret_values_read`: `False`
- `private_memory_payloads_read`: `False`
- `private_memory_exposure_granted`: `False`
- `autonomous_tool_execution_performed`: `False`
- `protoforge2_execution_performed`: `False`
- `echoforge_creation_performed`: `False`

## Blockers
- none

## Checks
- `PASS` `target_agent_exact` — neo.local
- `PASS` `prior_236d_verified` — NEO_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED
- `PASS` `prior_236c_accepted` — NEO_HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT
- `PASS` `profile_found` — None
- `PASS` `agent_id_matches` — neo.local
- `PASS` `activation_state_active_governed` — active_governed
- `PASS` `is_active_true` — True
- `PASS` `profile_hash_present` — df922d109948a5e5f29d647422a22145467720577ed80ffe27da783f07cae537
- `PASS` `namespace_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local
- `PASS` `receipts_dir_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/receipts
- `PASS` `source_manifest_hash_present` — bd7cdaade1c99170251f705d0aab99adedd425737ea794b64968875bfe7d9475
- `PASS` `source_receipt_hash_present` — f330bbc2479812404db7d5ceb2f6a80e12b58cc44c54ab8eb80c1947ccef2ad7
- `PASS` `source_echo_passed` — ECHO_VALIDATION_PASSED_NEO_GOVERNED_ACTIVE_AGENT
- `PASS` `source_echo_score_safe` — 0.97
- `PASS` `receipt_hash_verified_by_236d` — f330bbc2479812404db7d5ceb2f6a80e12b58cc44c54ab8eb80c1947ccef2ad7
- `PASS` `write_type_is_test_receipt` — test_receipt
- `PASS` `write_type_not_forbidden` — test_receipt
- `PASS` `no_identity_vault_write_this_patch` — Identity Vault unchanged
- `PASS` `no_agent_memory_write_this_patch` — agent_memory forbidden
- `PASS` `no_long_term_memory_write_this_patch` — long_term_memory forbidden
- `PASS` `no_private_memory_write_this_patch` — private_memory forbidden
- `PASS` `no_shared_memory_write_this_patch` — shared_memory forbidden
- `PASS` `no_secret_data_write_this_patch` — secret values forbidden
- `PASS` `no_full_chat_write_this_patch` — full chat content forbidden
- `PASS` `no_private_memory_exposure_this_patch` — private memory exposure forbidden
- `PASS` `no_autonomous_execution_this_patch` — Forge-controlled receipt write only
- `PASS` `rmc_test_receipt_file_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/receipts/neo_handshake_test_20260524_121937_UTC.json
- `PASS` `rmc_test_receipt_hash_present` — 174adc1c00d0354dd954e1db000f482969d90bf238c5615be4bdce233c07104e
- `PASS` `rmc_test_receipt_file_sha_present` — c2607d96baba40638156fde38f7382f0579c8858da102e5a7d1ac141f3f2b7b7
- `PASS` `rmc_test_receipt_write_type_safe` — test_receipt
- `PASS` `receipt_boundary_no_memory_pollution` — {'identity_vault_database_written': False, 'rmc_memory_written': False, 'agent_memory_written': False, 'long_term_memory_written': False, 'private_memory_written': False, 'shared_memory_written': False, 'secret_values_written': False, 'secret_values_read': False, 'private_memory_payloads_read': False, 'full_chat_content_written': False, 'autonomous_tool_execution_performed': False, 'protoforge2_execution_performed': False, 'echoforge_creation_performed': False}
- `PASS` `receipt_boundary_no_secret_or_chat` — {'identity_vault_database_written': False, 'rmc_memory_written': False, 'agent_memory_written': False, 'long_term_memory_written': False, 'private_memory_written': False, 'shared_memory_written': False, 'secret_values_written': False, 'secret_values_read': False, 'private_memory_payloads_read': False, 'full_chat_content_written': False, 'autonomous_tool_execution_performed': False, 'protoforge2_execution_performed': False, 'echoforge_creation_performed': False}
- `PASS` `receipt_boundary_no_private_memory_exposure` — False
