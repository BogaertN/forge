# IMPORT_PROBE_PLAN_V1

Status: `IMPORT_PROBE_PLAN_READY`
Created: `2026-05-17T09:11:20`
Target: `stack_linker_breather`

## Plain English

This is a generic import/path diagnostic. It can target any scoped engine name or Python file path. It does not edit files; it only probes whether imports/tests fail because of environment path behavior or file/package structure.

## Authority

- `read_only`: `True`
- `project_file_write_authority`: `False`
- `engine_file_write_authority`: `False`
- `patch_apply_authority`: `False`
- `ledger_mutation_authority`: `False`
- `shell_execution_authority`: `False`
- `subprocess_shell_false`: `True`
- `writes_forge_memory_only`: `True`

## Recommendation

Run import-probe-run latest CONFIRM_RUN_IMPORT_PROBE. Use stack_linker_breather as the first target, but this tool is generic.

## Next Commands

- `import-probe-run latest CONFIRM_RUN_IMPORT_PROBE`
- `import-probe-show run`
- `import-probe-export`
