# GENERIC_REPAIR_EVIDENCE_PACKET_V1

Status: `GENERIC_REPAIR_EVIDENCE_PACKET_READY`
Created: `2026-05-17T09:45:24`
Target: `stack_linker_breather`

## Plain English

Generic repair evidence packet compiled from the latest import probe, code snippets, source-authority candidates, impact/risk map, relationship map, and test run data. This does not edit files or apply patches.

## Authority

- `read_only`: `True`
- `llm_call_authority`: `False`
- `project_file_write_authority`: `False`
- `engine_file_write_authority`: `False`
- `patch_apply_authority`: `False`
- `ledger_mutation_authority`: `False`
- `shell_execution_authority`: `False`
- `writes_forge_memory_only`: `True`

## Recommendation

Call the local LLM with the confirm token to draft a repair proposal from this compiled evidence. Do not apply any repair yet.

## Next Commands

- `generic-repair-llm latest CONFIRM_CALL_GENERIC_REPAIR_LLM`
- `generic-repair-show llm`
- `generic-repair-export`
