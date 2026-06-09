# FORGE_SELF_UPDATE_PROPOSAL_V1

- Status: `FORGE_SELF_UPDATE_PROPOSAL_READY_NO_WRITE_AUTHORITY`
- Created: `2026-05-17T00:02:32`
- Authority: `PROPOSAL_ONLY`

## Plain English

This proposal records what Forge may later update in itself. It does not change main.py or tool_registry.json.

## Target Files

- `/home/nic/forge/config/tool_registry.json` — allowed=True exists=True
- `/home/nic/forge/main.py` — allowed=True exists=True

## Warnings

- proposal_only_no_diff_attached
- not_live_apply_eligible_until_snapshot_sandbox_tests_and_human_approval_exist

## Next Commands

- `forge-self-update-show latest`
- `forge-self-update-verify latest`
- `forge-self-update-export`
- `forge-next`
