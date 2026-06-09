# Patch 236A — Neo Manual Activation Apply

Generated: `20260524_115638_UTC`
Verdict: `NEO_ACTIVATED_ACTIVE_GOVERNED`
OK: `True`
Target agent: `neo.local`

## State
Before activation_state: `inactive_draft`
After activation_state: `active_governed`
Before is_active: `False`
After is_active: `True`

## Neo governance boundary
- `neo_allowed_contract_review`: `True`
- `neo_allowed_risk_framing`: `True`
- `neo_allowed_formal_summaries`: `True`
- `neo_allowed_boundary_checks`: `True`
- `neo_can_execute_tools_by_itself`: `False`
- `neo_can_write_memory_by_itself`: `False`
- `neo_can_bypass_forge`: `False`
- `neo_can_mutate_identity_vault`: `False`
- `neo_can_read_secrets`: `False`
- `neo_can_create_patches_without_approval`: `False`

## Changed fields
- `activation_state`
- `is_active`
- `last_validated_at`

## Backup
DB backup: `/home/nic/forge/memory/aiweb_patch236a_neo_manual_activation_apply_v1/db_backups/identity_vault_before_neo_activation_20260524_115638_UTC.db`
Backup sha256: `5ecc9f044e1638ccb804ca577e6dab42ab10a10e17f0e4d18751f75cef9abc16`

## Blockers
- none

No autonomous execution, no secret reads, no database autonomy, no Forge bypass, and no memory autonomy are granted by this patch.
