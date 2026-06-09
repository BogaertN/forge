# Patch 234 — Controlled RMC Test Receipt Write

Generated: `20260524_101634_UTC`
Verdict: `RMC_TEST_RECEIPT_WRITTEN_GOVERNED_GILLIGAN`
OK: `True`
Agent: `gilligan.local`
Checks: `25/25`
RMC receipt path: `/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/receipts/handshake_test_20260524_101634_UTC.json`
RMC receipt hash: `ffaa2e2dc1ac21007e9b41873d64b92ab51370ce12a05ba87deb70c8f4f98c28`

## Boundary

This patch writes one controlled RMC test receipt only. It does not write agent memory, long-term memory, private memory, shared memory, Identity Vault, ProtoForge2, EchoForge, secrets, or full chat content.

## Checks

- `PASS` `prior_233a_report_exists` — /home/nic/forge/memory/aiweb_patch233a_gilligan_governed_handshake_receipt_verify_v1/latest_aiweb_patch233a_gilligan_governed_handshake_receipt_verify.json
- `PASS` `prior_233a_ok` — True
- `PASS` `prior_233a_verdict` — GILLIGAN_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED
- `PASS` `prior_233_report_exists` — /home/nic/forge/memory/aiweb_patch233_gilligan_governed_handshake_v1/latest_aiweb_patch233_gilligan_governed_handshake.json
- `PASS` `prior_233_ok` — True
- `PASS` `prior_233_verdict` — HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT
- `PASS` `agent_id_gilligan` — 233=gilligan.local 233A=gilligan.local
- `PASS` `active_governed_handshake` — {'activation_state': 'active_governed', 'active_governed_required': True, 'governed_handshake_allowed': True, 'is_active': True}
- `PASS` `echo_validation_carried` — ECHO_VALIDATION_PASSED_GOVERNED_ACTIVE_AGENT score=0.97
- `PASS` `verify_echo_matches` — verify={'echo_hash': 'ae6d58e73feee360ca0ca074bca357bb87202dbf0f8b1b377979d3710740263c', 'echo_score': 0.97, 'verdict': 'ECHO_VALIDATION_PASSED_GOVERNED_ACTIVE_AGENT'} source={'active_gate_ok': True, 'boundary_ok': True, 'drift_status': 'GOVERNED_ACTIVE_HANDSHAKE_NO_AUTONOMY', 'echo_hash': 'ae6d58e73feee360ca0ca074bca357bb87202dbf0f8b1b377979d3710740263c', 'echo_score': 0.97, 'notes': 'Echo validation accepts the governed active handshake only because Forge remains authority and no autonomous execution or RMC memory write is granted.', 'ok': True, 'render_preview_ok': True, 'verdict': 'ECHO_VALIDATION_PASSED_GOVERNED_ACTIVE_AGENT'}
- `PASS` `manifest_hash_present` — a64cb2920d1ba753e15fef63945e88d2f30e2ae9bfb760b6eeb885e9d09908ea
- `PASS` `source_receipt_hash_present` — 95a12d4349eda9d484c53593394e4a90f72b7c84d38d3f5ec7959dbcc2704081
- `PASS` `namespace_resolves_to_gilligan` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local
- `PASS` `namespace_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local
- `PASS` `receipts_dir_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/receipts
- `PASS` `receipt_path_inside_receipts` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/receipts/handshake_test_20260524_101634_UTC.json
- `PASS` `write_type_test_receipt_only` — test_receipt
- `PASS` `prior_no_identity_write` — False
- `PASS` `prior_no_rmc_memory_write` — False
- `PASS` `prior_no_autonomous_execution` — False
- `PASS` `rmc_test_receipt_file_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/receipts/handshake_test_20260524_101634_UTC.json
- `PASS` `rmc_test_receipt_hash_present` — ffaa2e2dc1ac21007e9b41873d64b92ab51370ce12a05ba87deb70c8f4f98c28
- `PASS` `rmc_test_receipt_write_type_safe` — test_receipt
- `PASS` `receipt_boundary_no_memory_pollution` — {'controlled_test_receipt_only': True, 'identity_vault_database_written': False, 'agent_memory_written': False, 'long_term_memory_written': False, 'private_memory_written': False, 'shared_memory_written': False, 'full_chat_content_written': False, 'secret_values_written': False, 'autonomous_tool_execution_performed': False, 'protoforge2_execution_performed': False, 'echoforge_creation_performed': False}
- `PASS` `receipt_boundary_no_secret_or_chat` — {'controlled_test_receipt_only': True, 'identity_vault_database_written': False, 'agent_memory_written': False, 'long_term_memory_written': False, 'private_memory_written': False, 'shared_memory_written': False, 'full_chat_content_written': False, 'secret_values_written': False, 'autonomous_tool_execution_performed': False, 'protoforge2_execution_performed': False, 'echoforge_creation_performed': False}
