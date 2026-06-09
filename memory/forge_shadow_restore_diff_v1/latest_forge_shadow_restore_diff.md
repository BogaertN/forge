# FORGE_SHADOW_RESTORE_FORENSIC_DIFF

- **status**: `FORGE_SHADOW_RESTORE_FORENSIC_DIFF_READY`
- **active_patch**: `Patch 153 — Shadow Restore / Forensic Diff`
- **current_phase**: `S17C — Shadow Restore / Forensic Diff`
- **next_patch**: `Patch 154 — Dashboard v2 / Operator Control Panel`
- **snapshot_id**: `forge_snapshot_2026_05_19_181211`
- **shadow_id**: `shadow_restore_2026_05_19_182609`
- **snapshot_root**: `/home/nic/forge/memory/forge_snapshots_v1/forge_snapshot_2026_05_19_181211`
- **shadow_root**: `/home/nic/forge/memory/forge_shadow_restores_v1/shadow_restore_2026_05_19_182609`
- **file_count**: `542`
- **problem_count**: `0`

## Summary
- **shadow_matches_snapshot**: `True`
- **shadow_mismatch_count**: `0`
- **shadow_missing_count**: `0`
- **live_unchanged_count**: `524`
- **live_changed_since_snapshot_count**: `18`
- **live_missing_count**: `0`
- **live_restore_performed**: `False`

## Next Commands
- `forge-shadow-restore-export`
- `forge-build-sequence`
- `forge-status-api-build`
- `forge-dashboard-build`
- `Install Patch 154 when ready`

## Authority
- **shadow_restore_write**: `True`
- **forge_owned_shadow_write**: `True`
- **live_restore_authority**: `False`
- **project_file_write_authority**: `False`
- **engine_file_write_authority**: `False`
- **patch_apply_authority**: `False`
- **shell_execution_authority**: `False`
- **audit_log_overwrite**: `False`
- **forensic_diff_only**: `True`
