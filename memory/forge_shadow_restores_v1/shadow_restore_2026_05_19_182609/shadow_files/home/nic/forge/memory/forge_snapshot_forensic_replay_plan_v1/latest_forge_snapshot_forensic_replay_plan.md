# FORGE_SNAPSHOT_FORENSIC_REPLAY_PLAN

- **status**: `FORGE_SNAPSHOT_FORENSIC_REPLAY_PLAN_READY`
- **active_patch**: `Patch 151 — Snapshot / Forensic Replay Plan`
- **current_phase**: `S16 — Snapshot / forensic replay plan`
- **next_patch**: `Patch 152 — Snapshot Create / Verify`
- **plan_target**: `next`
- **snapshot_evidence_created**: `False`
- **live_restore_authority**: `False`

## Plan Summary
- Patch 151 is a plan-only safety layer.
- It defines what Forge must snapshot before future live apply gates can pass.
- It does not copy live project files, restore files, run shell commands, or grant write authority.
- Live apply remains blocked until snapshot creation, shadow restore, rollback binding, sandbox/test binding, and human approval exist.

## Snapshot Domains
- **D01** — Forge runtime core: `PLAN_ONLY`
- **D02** — Build governance memory: `PLAN_ONLY`
- **D03** — Engine authority and test evidence: `PLAN_ONLY`
- **D04** — Operator visibility surfaces: `PLAN_ONLY`
- **D05** — Audit tail capture: `PLAN_ONLY_NEVER_OVERWRITE_AUDIT_LOG`

## Forbidden Paths
- `~/.ssh`
- `*.pem`
- `*.key`
- `*.env`
- `secrets`
- `credentials`
- `token files`
- `old Chroma DB write paths`
- `node_modules`
- `.venv`
- `__pycache__`

## Next Commands
- `forge-snapshot-plan-build next`
- `forge-snapshot-plan-export`
- `forge-build-sequence`
- `forge-status-api-build`
- `forge-dashboard-build`
- `Install Patch 152 when ready`

## Authority
- **read_only**: `True`
- **forge_memory_write_only**: `True`
- **snapshot_create_authority**: `False`
- **shadow_restore_authority**: `False`
- **live_restore_authority**: `False`
- **project_file_write_authority**: `False`
- **engine_file_write_authority**: `False`
- **patch_apply_authority**: `False`
- **shell_execution_authority**: `False`
- **network_or_server_start_authority**: `False`
