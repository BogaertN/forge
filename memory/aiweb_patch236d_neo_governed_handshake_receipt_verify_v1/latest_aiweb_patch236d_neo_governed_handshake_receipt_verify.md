# Patch 236D — Neo Governed Handshake Receipt Verification

Generated: `20260524_121433_UTC`
Verdict: `NEO_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED`
OK: `True`
Agent: `neo.local`
Checks: `26/26`
Source Patch 236C receipt hash: `f330bbc2479812404db7d5ceb2f6a80e12b58cc44c54ab8eb80c1947ccef2ad7`
Recomputed receipt hash: `f330bbc2479812404db7d5ceb2f6a80e12b58cc44c54ab8eb80c1947ccef2ad7`

## Boundary

This verification writes only a Forge-owned report. It does not mutate Identity Vault, does not write RMC memory, does not expose private memory, does not read secrets, does not execute ProtoForge2, does not invoke EchoForge, and does not grant autonomous tool execution.

## Checks

- `PASS` `source_236c_report_exists` — /home/nic/forge/memory/aiweb_patch236c_neo_governed_handshake_v1/latest_aiweb_patch236c_neo_governed_handshake.json
- `PASS` `source_verdict_expected` — NEO_HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT
- `PASS` `source_agent_neo` — neo.local
- `PASS` `source_checks_all_passed` — 23/23
- `PASS` `activation_gate_active_governed` — active_governed / True
- `PASS` `live_neo_profile_active_governed` — active_governed / True
- `PASS` `gilligan_remains_active_governed` — active_governed / True
- `PASS` `athena_remains_active_governed` — active_governed / True
- `PASS` `namespace_path_exists` — /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local
- `PASS` `manifest_present` — bd7cdaade1c99170251f705d0aab99adedd425737ea794b64968875bfe7d9475
- `PASS` `manifest_hash_valid` — source=bd7cdaade1c99170251f705d0aab99adedd425737ea794b64968875bfe7d9475 recomputed=bd7cdaade1c99170251f705d0aab99adedd425737ea794b64968875bfe7d9475
- `PASS` `receipt_hash_valid` — source=f330bbc2479812404db7d5ceb2f6a80e12b58cc44c54ab8eb80c1947ccef2ad7 recomputed=f330bbc2479812404db7d5ceb2f6a80e12b58cc44c54ab8eb80c1947ccef2ad7
- `PASS` `echo_verdict_passed` — ECHO_VALIDATION_PASSED_NEO_GOVERNED_ACTIVE_AGENT
- `PASS` `echo_score_high` — 0.97
- `PASS` `forge_owned_receipt_only` — {'agent_memory_written': False, 'autonomous_tool_execution_performed': False, 'echoforge_creation_performed': False, 'forge_owned_handshake_receipt': True, 'full_chat_content_written': False, 'identity_vault_database_written': False, 'private_memory_payloads_read': False, 'protoforge2_execution_performed': False, 'rmc_memory_written': False, 'secret_values_read': False, 'shared_memory_written': False}
- `PASS` `no_identity_vault_write` — False
- `PASS` `no_rmc_memory_write` — False
- `PASS` `no_private_memory_exposure` — False
- `PASS` `no_secret_reads` — False
- `PASS` `no_autonomous_execution` — False
- `PASS` `no_protoforge2_execution` — False
- `PASS` `no_echoforge_creation` — False
- `PASS` `governance_boundary_forbids_secrets` — False
- `PASS` `governance_boundary_forbids_private_memory` — False
- `PASS` `governance_boundary_forbids_tools` — False
- `PASS` `governance_boundary_forge_authority` — True
