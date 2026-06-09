# FORGE_SHADOW_RESTORE_PLAN

- **status**: `FORGE_SHADOW_RESTORE_PLAN_READY`
- **active_patch**: `Patch 153 — Shadow Restore / Forensic Diff`
- **current_phase**: `S17C — Shadow Restore / Forensic Diff`
- **next_patch**: `Patch 154 — Dashboard v2 / Operator Control Panel`
- **snapshot_id**: `forge_snapshot_2026_05_19_181211`
- **shadow_id**: `shadow_restore_2026_05_19_182029`
- **snapshot_root**: `/home/nic/forge/memory/forge_snapshots_v1/forge_snapshot_2026_05_19_181211`
- **shadow_root**: `/home/nic/forge/memory/forge_shadow_restores_v1/shadow_restore_2026_05_19_182029`
- **file_count**: `542`
- **verified_file_count**: `542`
- **problem_count**: `0`

## Summary
- **snapshot_verified**: `True`
- **shadow_restore_live**: `False`
- **shadow_copy_planned**: `True`
- **planned_file_count**: `542`

## Domains
- **D01** — Forge runtime core: files=`4` problems=`0`
- **D02** — Build governance memory: files=`178` problems=`0`
- **D03** — Engine authority and test evidence: files=`160` problems=`0`
- **D04** — Operator visibility surfaces: files=`199` problems=`0`
- **D05** — Audit tail capture: files=`1` problems=`0`

## Next Commands
- `forge-shadow-restore-run latest`
- `forge-shadow-restore-diff latest`
- `forge-shadow-restore-export`

## Authority
- **shadow_restore_write**: `True`
- **forge_owned_shadow_write**: `True`
- **live_restore_authority**: `False`
- **project_file_write_authority**: `False`
- **engine_file_write_authority**: `False`
- **patch_apply_authority**: `False`
- **shell_execution_authority**: `False`
- **audit_log_overwrite**: `False`
