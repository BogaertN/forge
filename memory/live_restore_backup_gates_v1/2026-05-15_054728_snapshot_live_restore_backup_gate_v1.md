# Patch 92 Live Restore Backup Gate

Created: `2026-05-15T05:47:28`
Status: `LIVE_RESTORE_BACKUP_GATE_READY_WITH_WARNINGS_NO_AUTHORITY`
Backup gate ID: `LBG-2de0cfe4e1fe6c66bd537765`
Source dry-run: `/home/nic/forge/memory/live_restore_dry_runs_v1/2026-05-15_051657_snapshot_live_restore_candidate_dry_run_v1.json`

## Counts
- Files bound: `58`
- Live files requiring backup before restore: `58`
- Future overwrite candidates: `4`
- Future create candidates: `0`
- Already matching snapshot: `54`
- Blockers: `0`
- Warnings: `13`

## Authority
- Backup copy: `NO`
- Live restore: `NO`
- Project writes: `NO`
- Engine writes: `NO`
- Shell execution: `NO`

## Future Backup Copy Requirements
- A future backup-copy patch must create backups before any live restore patch can exist.
- The future backup copy must bind to this backup_gate_id and prove current live hashes still match this gate receipt.
- The future backup copy must write only under /home/nic/forge/memory/live_restore_backups_v1/ until separately verified.
- No live restore command may run unless a verified backup receipt exists and matches the same dry-run/proposal chain.

## First 25 Backup Gate Rows
- backup_required=`True` action=`DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` live=`/home/nic/forge/main.py` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/main.py`
- backup_required=`True` action=`DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` live=`/home/nic/forge/config/tool_registry.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/config/tool_registry.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/config/approved_paths.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/config/approved_paths.json`
- backup_required=`True` action=`DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` live=`/home/nic/forge/config/session_scope.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/config/session_scope.json`
- backup_required=`True` action=`DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` live=`/home/nic/forge/logs/forge_audit.log` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/logs/forge_audit.log`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/code_library_v1/manifests/engine_review_ledger_v1.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/code_library_v1/manifests/engine_review_ledger_v1.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_192941.jsonl` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_192941.jsonl`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_193652.jsonl` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_193652.jsonl`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/corrections/seed_llm_memory_reason_for_patch75.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/corrections/seed_llm_memory_reason_for_patch75.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch67_archive_root_instruction_correction.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/corrections/seed_patch67_archive_root_instruction_correction.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch74_timestamp_helper_correction.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/corrections/seed_patch74_timestamp_helper_correction.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.md` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.md`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/indexes/latest_receipt.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/indexes/latest_receipt.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/indexes/latest_tool_request.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/indexes/latest_tool_request.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/indexes/llm_tool_gateway_policy.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/indexes/llm_tool_gateway_policy.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/indexes/session_index.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/indexes/session_index.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/policy.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/policy.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/llm_memory_v1/turns/llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/llm_memory_v1/turns/llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json`
- backup_required=`True` action=`DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` live=`/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.md` backup_plan=`/home/nic/forge/memory/live_restore_backups_v1/FUTURE_BACKUP_ONLY/LBG-2de0cfe4e1fe6c66bd537765/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.md`

## Warnings
- /home/nic/forge/config/session_scope.json: current live SHA differs from snapshot SHA; future restore would overwrite this file
- /home/nic/forge/config/session_scope.json: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/config/session_scope.json: future restore would overwrite this live file; backup is mandatory before restore
- /home/nic/forge/config/tool_registry.json: current live SHA differs from snapshot SHA; future restore would overwrite this file
- /home/nic/forge/config/tool_registry.json: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/config/tool_registry.json: future restore would overwrite this live file; backup is mandatory before restore
- /home/nic/forge/logs/forge_audit.log: current live SHA differs from snapshot SHA; future restore would overwrite this file
- /home/nic/forge/logs/forge_audit.log: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/logs/forge_audit.log: future restore would overwrite this live file; backup is mandatory before restore
- /home/nic/forge/main.py: current live SHA differs from snapshot SHA; future restore would overwrite this file
- /home/nic/forge/main.py: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/main.py: future restore would overwrite this live file; backup is mandatory before restore
- Expected volatile source drift accepted for copy: /home/nic/forge/logs/forge_audit.log