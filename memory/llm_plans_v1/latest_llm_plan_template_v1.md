# LLM_PLAN_TEMPLATE_V1

- **Created:** 2026-05-16T23:56:28

- **Status:** LLM_PLAN_TEMPLATE_READY_NO_ACTION_AUTHORITY


## Plain English

This is the shape future LLM plans must use. It is not an executable patch and grants no write authority.


## Required Fields

- `goal`
- `target_files`
- `source_evidence`
- `runtime_roles`
- `risk_level`
- `expected_changes`
- `test_plan`
- `rollback_plan`
- `requires_human_approval`


## Template

```json
{
  "schema_version": "llm_plan_packet_schema_v1_patch119",
  "packet_type": "LLM_PLANNING_PACKET",
  "goal": "",
  "target_files": [],
  "source_evidence": [],
  "runtime_roles": [],
  "risk_level": "MEDIUM",
  "expected_changes": [],
  "test_plan": [],
  "rollback_plan": [],
  "requires_human_approval": true,
  "llm_notes": "",
  "forge_validation_notes": [],
  "authority": {
    "llm_may_draft": true,
    "forge_must_validate": true,
    "human_approval_required": true,
    "project_file_write_authority": false,
    "forge_self_write_authority": false,
    "patch_apply_authority": false,
    "shell_execution_authority": false,
    "chroma_write_authority": false,
    "ledger_mutation_authority": false
  },
  "validation_requirements": {
    "target_files_must_exist": true,
    "target_files_must_be_in_scope": true,
    "source_evidence_must_exist": true,
    "runtime_roles_must_be_known": true,
    "current_sha_must_match_before_apply": true,
    "snapshot_required_before_write": true,
    "sandbox_required_before_write": true,
    "safe_tests_required_before_write_when_available": true,
    "rollback_plan_required_before_write": true
  }
}
```


## Authority

```json
{
  "mode": "SCHEMA_TEMPLATE_ONLY",
  "project_file_write_authority": false,
  "forge_self_write_authority": false,
  "patch_apply_authority": false,
  "shell_execution_authority": false,
  "chroma_write_authority": false,
  "ledger_mutation_authority": false,
  "llm_autonomous_decision_authority": false
}
```


## Next Commands

```text
llm-plan-show latest
```
```text
llm-plan-validate latest
```
```text
llm-plan-export
```
```text
forge-next
```
