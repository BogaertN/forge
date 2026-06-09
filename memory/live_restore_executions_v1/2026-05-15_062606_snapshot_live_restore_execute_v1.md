# Patch 94 Live Restore Execute Receipt

Status: `LIVE_RESTORE_EXECUTED_WITH_WARNINGS_AUDIT_LOG_PROTECTED`
Execution ID: `LRE-dfe69add79c0ae76463cec42`
Actual restore performed: `True`
Files restored: `57`
Protected skips: `1`
Blockers: `0`
Warnings: `18`

## Authority
Live restore is strictly bound to prior receipts. No shell, delete, quarantine, Chroma, or final lockfile authority is granted.

## Protected skip
`/home/nic/forge/logs/forge_audit.log` is not overwritten so the live audit chain remains intact.

## Rows
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/main.py`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/config/tool_registry.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/config/approved_paths.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/config/session_scope.json`
- `SKIPPED_PROTECTED_AUDIT_LOG_NOT_RESTORED` `/home/nic/forge/logs/forge_audit.log`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/engine_review_ledger_v1.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_192941.jsonl`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_193652.jsonl`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_llm_memory_reason_for_patch75.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch67_archive_root_instruction_correction.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch74_timestamp_helper_correction.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/latest_receipt.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/latest_tool_request.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/llm_tool_gateway_policy.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/session_index.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/policy.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/turns/llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201821_snapshot_plan_export_v1.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201821_snapshot_plan_export_v1.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173450_code_index_integrity.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173526_code_engine_inventory.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173651_code_engine_duplicates.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173737_code_engine_canonical_plan.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175412_symbolic_runtime_map.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175522_symbolic_runtime_gaps.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175550_symbolic_runtime_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175550_symbolic_runtime_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_190340_test_inventory.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_195339_engine_canonical_review.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_195509_engine_canonical_review_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_195509_engine_canonical_review_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_200356_engine_canonical_decision_draft.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_200444_engine_canonical_decision_draft_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_200444_engine_canonical_decision_draft_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_202152_engine_canonical_lockfile_draft.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_202324_engine_canonical_lockfile_draft_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_202324_engine_canonical_lockfile_draft_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_203422_engine_review_ledger_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_203422_engine_review_ledger_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_204309_engine_review_batch_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_204309_engine_review_batch_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_205514_engine_human_approved_lockfile_candidate.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_205547_engine_human_approved_lockfile_candidate_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_205547_engine_human_approved_lockfile_candidate_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195109_engine_brief_export.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195109_engine_brief_export.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.md`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/_code_index_current.json`
- `LIVE_FILE_RESTORED_FROM_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/engine_review_batch_plan_v1.json`