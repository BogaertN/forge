# IMPORT_PROBE_RUN_V1

Status: `IMPORT_PROBE_FAIL`
Created: `2026-05-17T09:11:39`
Target: `stack_linker_breather`

## Plain English

Generic import/path probe result. A passing probe means this target can run under the scoped diagnostic environment. A failing probe means the target needs either test-runner path adjustment or file/package repair review.

## Authority

- `read_only`: `True`
- `project_file_write_authority`: `False`
- `engine_file_write_authority`: `False`
- `patch_apply_authority`: `False`
- `ledger_mutation_authority`: `False`
- `writes_forge_memory_only`: `True`
- `subprocess_shell_false`: `True`

## Recommendation

Do not alter live files yet; inspect package structure, imports, and test assumptions through a separate repair proposal.
