# GENERIC_REVISION_SANDBOX_POLICY_V1

Status: GENERIC_REVISION_SANDBOX_POLICY_READY


```json
{
  "authority": {
    "engine_file_write_authority": false,
    "ledger_mutation_authority": false,
    "patch_apply_authority": false,
    "project_file_write_authority": false,
    "sandbox_only": true,
    "subprocess_shell_false": true
  },
  "created_at": "2026-05-18T17:14:07",
  "purpose": "Run latest LLM-built revision candidate inside a Forge-owned sandbox with dependency copying, safe test execution, and local LLM review.",
  "report_type": "GENERIC_REVISION_SANDBOX_POLICY_V1",
  "required_token": "CONFIRM_RUN_GENERIC_REVISION_SANDBOX",
  "schema_version": "generic_revision_sandbox_v1_patch141",
  "status": "GENERIC_REVISION_SANDBOX_POLICY_READY"
}
```