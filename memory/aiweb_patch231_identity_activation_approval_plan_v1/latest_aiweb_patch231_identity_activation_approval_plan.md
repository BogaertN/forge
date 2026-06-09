# Patch 231 — Identity Activation Approval Plan

Generated: `20260524_003437_UTC`
Verdict: `IDENTITY_ACTIVATION_APPROVAL_PLAN_WRITTEN`
OK: `True`

## Boundary

- `plan_only`: `True`
- `activation_command_installed`: `False`
- `preflight_command_installed`: `False`
- `rmc_memory_written`: `False`
- `identity_vault_database_written`: `False`
- `agent_identity_activation_performed`: `False`
- `protoforge2_execution_performed`: `False`
- `echoforge_creation_performed`: `False`

## Activation authority

- `human_operator`: `Nic at the Forge terminal`
- `forge_role`: `gatekeeper_and_audit_authority`
- `identity_vault_role`: `profile_source_of_truth`
- `rmc_role`: `memory_namespace_target_after_activation_only`
- `rule`: `No agent may become active from automatic discovery, dry-run handshake, profile read, namespace presence, renderer success, or echo validation alone.`

## Future commands defined but not installed

- `preflight_command_patch_231a`: `forge-agent-activation-preflight <agent_id>`
- `manual_activation_command_future_patch`: `forge-agent-activate-manual <agent_id>`
- `manual_activation_command_status`: `NOT_INSTALLED_IN_PATCH_231`
- `rollback_command_future_patch`: `forge-agent-activation-rollback <agent_id> <activation_receipt_id>`
- `rollback_command_status`: `NOT_INSTALLED_IN_PATCH_231`

## Manual activation requirements

- manual Forge command typed by operator
- explicit agent_id argument; no default activation target
- valid inactive Identity Vault profile
- valid profile hash or profile fingerprint captured before activation
- valid service contracts for the selected agent
- valid RMC namespace rooted under /home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/<agent_id>
- passing echo validator on activation manifest preview
- Forge-owned activation approval receipt written before any Identity Vault mutation
- operator approval recorded in Forge audit chain
- no automatic activation from dry-run, report read, namespace creation, receipt verification, or preflight success

## Patch 231A preflight checks to implement

- profile exists for supplied agent_id
- agent_id is one of the known inactive draft agents or explicitly allowed by future policy
- profile hash/fingerprint is computable and stable during preflight
- activation_state is inactive_draft
- is_active is 0/False
- RMC namespace exists and is a directory
- RMC namespace path is under the allowed ancestral_memory/agents root
- service contracts exist and pass read-only validation
- forbidden actions are present and non-empty
- permissions are present and non-empty
- required identity fields are present
- echo validator can validate activation preview
- prior Patch 230/230A inactive handshake receipts exist for at least gilligan.local before first activation path proceeds
- no live RMC memory write occurs during preflight
- no Identity Vault DB write occurs during preflight
- no agent activation occurs during preflight

## Fields allowed to change only after explicit approval

- `activation_state`
- `is_active`
- `activated_at_utc`
- `activation_receipt_id`
- `activation_profile_hash`
- `activation_namespace_path`
- `activation_approved_by`

## Fields that must never change automatically

- `agent_id`
- `canonical name / identity label`
- `role definition`
- `forbidden actions`
- `permission boundary`
- `RMC namespace root policy`
- `service contract source text`
- `profile ancestry/source record`
- `operator identity`

## Hard blocks

- missing profile
- profile hash mismatch between preflight and activation moment
- activation_state not inactive_draft at preflight
- is_active already true
- missing or outside-policy RMC namespace
- missing service contracts
- missing forbidden actions
- missing permissions
- echo validator failure
- operator approval missing
- audit write failure

## Prior receipt snapshot

- `patch230a_receipt_path`: `/home/nic/forge/memory/aiweb_patch230a_bootstrap_handshake_receipt_verify_v1/latest_aiweb_patch230a_bootstrap_handshake_receipt_verify.json`
- `patch230a_receipt_exists`: `True`
- `patch230a_receipt_ok`: `True`
- `patch230a_verdict`: `VERIFIED_HANDSHAKE_DRY_RUN_RECEIPT_INACTIVE_GATE`
- `verified_agent`: `gilligan.local`
- `verified_activation_state`: `inactive_draft`
- `verified_is_active`: `False`
- `verified_namespace_path`: `/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/gilligan.local`
- `required_previous_verdict`: `VERIFIED_HANDSHAKE_DRY_RUN_RECEIPT_INACTIVE_GATE`
- `previous_verdict_matches`: `True`

## Next step

Patch 231A — add read-only forge-agent-activation-preflight <agent_id> command.

Patch 231 is a plan-only safety layer. It does not install or run activation, does not mutate Identity Vault, and does not write live RMC memory.
