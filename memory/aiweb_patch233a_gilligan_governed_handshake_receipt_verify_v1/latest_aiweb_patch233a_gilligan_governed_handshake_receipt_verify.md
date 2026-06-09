# Patch 233A — Gilligan Governed Handshake Receipt Verification

Generated: `20260524_012713_UTC`
Verdict: `GILLIGAN_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED`
OK: `True`
Agent: `gilligan.local`
Checks: `26/26`
Source Patch 233 receipt hash: `95a12d4349eda9d484c53593394e4a90f72b7c84d38d3f5ec7959dbcc2704081`
Recomputed receipt hash: `95a12d4349eda9d484c53593394e4a90f72b7c84d38d3f5ec7959dbcc2704081`

## Boundary

This verification writes only Forge-owned reports. It does not mutate Identity Vault, does not write RMC memory, does not execute ProtoForge2, does not invoke EchoForge, and does not grant autonomous tool execution.

## Checks

- `PASS` `patch233_report_exists` — /home/nic/forge/memory/aiweb_patch233_gilligan_governed_handshake_v1/latest_aiweb_patch233_gilligan_governed_handshake.json
- `PASS` `patch233_ok` — True
- `PASS` `patch233_verdict` — HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT
- `PASS` `agent_id_gilligan` — gilligan.local
- `PASS` `active_governed_gate_used` — active_governed
- `PASS` `is_active_true` — True
- `PASS` `profile_hash_checked_in_patch233` — profile_hash_present check in Patch 233
- `PASS` `namespace_pointer_used` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local
- `PASS` `namespace_resolved_to_gilligan` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local
- `PASS` `namespace_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local
- `PASS` `namespace_children_exist` — [{'exists': True, 'file_count': 0, 'is_dir': True, 'name': 'manifests', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/manifests'}, {'exists': True, 'file_count': 0, 'is_dir': True, 'name': 'receipts', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/receipts'}, {'exists': True, 'file_count': 0, 'is_dir': True, 'name': 'echo', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/echo'}, {'exists': True, 'file_count': 0, 'is_dir': True, 'name': 'private_context', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/private_context'}, {'exists': True, 'file_count': 0, 'is_dir': True, 'name': 'phase_records', 'path': '/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local/phase_records'}]
- `PASS` `manifest_present` — manifest object present
- `PASS` `manifest_type_governed` — governed_active_agent_handshake
- `PASS` `manifest_hash_valid` — expected=a64cb2920d1ba753e15fef63945e88d2f30e2ae9bfb760b6eeb885e9d09908ea actual=a64cb2920d1ba753e15fef63945e88d2f30e2ae9bfb760b6eeb885e9d09908ea
- `PASS` `render_preview_present` — c22e01ade0bdc76306c5896499975e76b8b2db58c7bcf57e637ad7a3bd60e9e0
- `PASS` `echo_validation_passed` — ECHO_VALIDATION_PASSED_GOVERNED_ACTIVE_AGENT
- `PASS` `echo_score_high` — 0.97
- `PASS` `receipt_hash_present` — 95a12d4349eda9d484c53593394e4a90f72b7c84d38d3f5ec7959dbcc2704081
- `PASS` `receipt_hash_valid` — expected=95a12d4349eda9d484c53593394e4a90f72b7c84d38d3f5ec7959dbcc2704081 actual=95a12d4349eda9d484c53593394e4a90f72b7c84d38d3f5ec7959dbcc2704081
- `PASS` `forge_owned_receipt_written` — True
- `PASS` `identity_vault_not_written` — False
- `PASS` `rmc_memory_not_written` — False
- `PASS` `autonomous_execution_false` — writes=False boundary=False
- `PASS` `protoforge2_not_executed` — False
- `PASS` `echoforge_not_invoked` — False
- `PASS` `no_secret_or_full_chat_write` — secrets=False full_chat=False
