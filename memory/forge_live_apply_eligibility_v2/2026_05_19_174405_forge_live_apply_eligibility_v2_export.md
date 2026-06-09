# FORGE_LIVE_APPLY_ELIGIBILITY_V2_EXPORT

- **status**: `FORGE_LIVE_APPLY_ELIGIBILITY_V2_EXPORT_READY`
- **target**: `next`
- **eligible_for_live_apply**: `False`
- **next_patch**: `Patch 151 — Snapshot / Forensic Replay Plan`
- **gate_pass_count**: `7`
- **gate_warn_count**: `0`
- **gate_fail_count**: `5`

## Blocking Reasons
- G04: pass=None fail=None
- G09: No Patch 150+ live apply may be eligible until snapshot/shadow-restore evidence exists.
- G10: No target-specific fresh sandbox pass is bound to this live-apply request.
- G11: No target-specific rollback artifact is bound to this live-apply request.
- G12: No explicit human live-apply approval token is present. This is correct for read-only Patch 150.

## Authority
- **export_only**: `True`
- **project_file_write_authority**: `False`
- **engine_file_write_authority**: `False`
- **patch_apply_authority**: `False`
- **shell_execution_authority**: `False`
