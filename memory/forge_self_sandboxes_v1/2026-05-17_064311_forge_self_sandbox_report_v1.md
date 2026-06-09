# FORGE_SELF_SANDBOX_REPORT_V1

- Status: `FORGE_SELF_SANDBOX_APPLY_BLOCKED_OR_FAILED`
- Created: `2026-05-17T06:43:11`
- Authority: `SANDBOX_ONLY`

## Plain English

Forge built and checked a sandbox copy. Live Forge files were not changed.

- Sandbox ID: `FSSB-2026-05-17_064303`
- Sandbox root: `/home/nic/forge/memory/forge_self_sandboxes_v1/sandboxes/FSSB-2026-05-17_064303`

## Problems

- check_failed:expected_command_scan:['forge-self-sandbox-policy', 'forge-self-sandbox-plan', 'forge-self-sandbox-apply', 'forge-self-sandbox-show', 'forge-self-sandbox-clean', 'forge-self-sandbox-export']

## Checks

- `py_compile_main` → `PASS`
- `expected_command_scan` → `FAIL`
- `tool_registry_json_parse` → `PASS`

## Next Commands

- `forge-self-sandbox-show report`
- `forge-self-sandbox-export`
- `forge-next`
