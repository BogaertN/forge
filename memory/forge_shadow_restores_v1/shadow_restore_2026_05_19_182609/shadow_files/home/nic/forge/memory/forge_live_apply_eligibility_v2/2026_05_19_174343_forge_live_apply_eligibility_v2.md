# FORGE_LIVE_APPLY_ELIGIBILITY_V2

- **status**: `FORGE_LIVE_APPLY_ELIGIBILITY_V2_READY_NOT_ELIGIBLE`
- **active_patch**: `Patch 150 — Live Apply Eligibility Gate v2`
- **target**: `next`
- **eligible_for_live_apply**: `False`
- **current_phase**: `S15 — Live apply eligibility gate v2`
- **next_patch**: `Patch 151 — Snapshot / Forensic Replay Plan`
- **gate_pass_count**: `7`
- **gate_warn_count**: `0`
- **gate_fail_count**: `5`

## Eligibility Gates
- **G01** — `PASS` — LLM proposal exists: FORGE_LLM_PATCH_PROPOSAL_V2_DRAFT_READY_NO_WRITE_AUTHORITY
- **G02** — `PASS` — LLM proposal verified: FORGE_LLM_PATCH_PROPOSAL_V2_VERIFIED_READ_ONLY
- **G03** — `PASS` — Source authority visible: FORGE_SOURCE_AUTHORITY_HARDENING_READY
- **G04** — `FAIL` — Canonical tests clean: pass=None fail=None
- **G05** — `PASS` — Patch impact clean: high=0 test_issues=0
- **G06** — `PASS` — Build phase gate clean: pass=8 warn=0 fail=0
- **G07** — `PASS` — Status/dashboard agree: status_api=Patch 150 — Live Apply Eligibility Gate v2 dashboard=Patch 150 — Live Apply Eligibility Gate v2
- **G08** — `PASS` — Deferred queue visible: FORGE_DEFERRED_ENGINE_REPAIR_QUEUE_READY
- **G09** — `FAIL` — Snapshot freshness: No Patch 150+ live apply may be eligible until snapshot/shadow-restore evidence exists.
- **G10** — `FAIL` — Sandbox/test binding for target: No target-specific fresh sandbox pass is bound to this live-apply request.
- **G11** — `FAIL` — Rollback readiness: No target-specific rollback artifact is bound to this live-apply request.
- **G12** — `FAIL` — Human approval: No explicit human live-apply approval token is present. This is correct for read-only Patch 150.

## Blocking Reasons
- G04: pass=None fail=None
- G09: No Patch 150+ live apply may be eligible until snapshot/shadow-restore evidence exists.
- G10: No target-specific fresh sandbox pass is bound to this live-apply request.
- G11: No target-specific rollback artifact is bound to this live-apply request.
- G12: No explicit human live-apply approval token is present. This is correct for read-only Patch 150.

## Next Commands
- `forge-live-eligibility-v2-export`
- `forge-build-sequence`
- `forge-status-api-build`
- `forge-dashboard-build`
- `Install Patch 151 when ready`

## Authority
- **read_only**: `True`
- **forge_memory_write_only**: `True`
- **proposal_only**: `True`
- **project_file_write_authority**: `False`
- **engine_file_write_authority**: `False`
- **patch_apply_authority**: `False`
- **shell_execution_authority**: `False`
- **network_or_server_start_authority**: `False`
- **human_approval_required**: `True`
