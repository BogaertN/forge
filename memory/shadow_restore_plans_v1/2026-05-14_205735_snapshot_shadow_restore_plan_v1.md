# Patch 85 Shadow Restore Plan

Mode: PLAN ONLY. No files copied. No restore authority exists.
Created: `2026-05-14T20:57:35`
Status: `SHADOW_RESTORE_PLAN_READY_NO_COPY_NO_RESTORE`
Source snapshot receipt: `/home/nic/forge/memory/snapshots_v1/2026-05-14_204425_snapshot_create_v1.json`
Planned shadow root NOT CREATED: `/home/nic/forge/memory/shadow_restore_plans_v1/2026-05-14_205735_shadow_restore_target_NOT_CREATED`

## Counts
- Planned files: `58`
- Blockers: `0`
- Warnings: `1`

## Authority
- shadow_restore_plan_authority: `True`
- shadow_restore_copy_authority: `False`
- restore_authority: `False`
- project_file_write_authority: `False`
- engine_file_write_authority: `False`
- delete_authority: `False`
- quarantine_authority: `False`
- shell_execution_authority: `False`
- chroma_write_authority: `False`
- snapshot_create_authority: `False`
- final_lockfile_authority: `False`

## Blockers
- None

## Planned Files
- `shadow_files/0001_def9b3d137a054d5_main.py` ← `files/0001_def9b3d137a054d5_forge_main_py.py` → original `/home/nic/forge/main.py`
- `shadow_files/0002_d78daa9932ec2725_tool_registry.json` ← `files/0002_d78daa9932ec2725_tool_registry.json` → original `/home/nic/forge/config/tool_registry.json`
- `shadow_files/0003_80c98f351a0ffe36_approved_paths.json` ← `files/0003_80c98f351a0ffe36_approved_paths.json` → original `/home/nic/forge/config/approved_paths.json`
- `shadow_files/0004_c3938638499a391a_session_scope.json` ← `files/0004_c3938638499a391a_session_scope.json` → original `/home/nic/forge/config/session_scope.json`
- `shadow_files/0005_44d95ae68394bd53_forge_audit.log` ← `files/0005_f3b83ebb71b0886b_audit_log.log` → original `/home/nic/forge/logs/forge_audit.log`
- `shadow_files/0006_3f0af0874087943f_engine_review_ledger_v1.json` ← `files/0006_3f0af0874087943f_engine_review_ledger.json` → original `/home/nic/forge/memory/code_library_v1/manifests/engine_review_ledger_v1.json`
- `shadow_files/0007_530d794800293b1f_2026-05-14_201722_snapshot_plan_v1.json` ← `files/0007_530d794800293b1f_latest_snapshot_plan.json` → original `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.json`
- `shadow_files/0008_6136b92f81ffe5fe_2026-05-14_195958_engine_approved_candidate_readiness_report.json` ← `files/0008_6136b92f81ffe5fe_latest_readiness_report.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.json`
- `shadow_files/0009_ee6f80af744d6f84_2026-05-14_200919_code_relationship_intelligence_report.json` ← `files/0009_ee6f80af744d6f84_latest_relationship_report.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.json`
- `shadow_files/0010_4a6ab344567a9ce9_forge_2026_05_14_192941.jsonl` ← `files/0010_4a6ab344567a9ce9_conversations_forge_2026_05_14_192941.jsonl` → original `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_192941.jsonl`
- `shadow_files/0011_bd96a24def4504d7_forge_2026_05_14_193652.jsonl` ← `files/0011_bd96a24def4504d7_conversations_forge_2026_05_14_193652.jsonl` → original `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_193652.jsonl`
- `shadow_files/0012_f66218b1fd8a5e5b_seed_llm_memory_reason_for_patch75.json` ← `files/0012_f66218b1fd8a5e5b_corrections_seed_llm_memory_reason_for_patch75.json` → original `/home/nic/forge/memory/llm_memory_v1/corrections/seed_llm_memory_reason_for_patch75.json`
- `shadow_files/0013_f6b14dc692a7d7d5_seed_patch67_archive_root_instruction_correction.json` ← `files/0013_f6b14dc692a7d7d5_corrections_seed_patch67_archive_root_instruction_correction.json` → original `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch67_archive_root_instruction_correction.json`
- `shadow_files/0014_a405cd3e1db5a417_seed_patch74_timestamp_helper_correction.json` ← `files/0014_a405cd3e1db5a417_corrections_seed_patch74_timestamp_helper_correction.json` → original `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch74_timestamp_helper_correction.json`
- `shadow_files/0015_f9df4249d0796ba2_2026-05-14_193152_llm_memory_export.json` ← `files/0015_f9df4249d0796ba2_exports_2026-05-14_193152_llm_memory_export.json` → original `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.json`
- `shadow_files/0016_c8e45e3ebc23a3d3_2026-05-14_193152_llm_memory_export.md` ← `files/0016_c8e45e3ebc23a3d3_exports_2026-05-14_193152_llm_memory_export.md` → original `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.md`
- `shadow_files/0017_f8385574e6d751d1_latest_receipt.json` ← `files/0017_f8385574e6d751d1_indexes_latest_receipt.json` → original `/home/nic/forge/memory/llm_memory_v1/indexes/latest_receipt.json`
- `shadow_files/0018_61478def243f9111_latest_tool_request.json` ← `files/0018_61478def243f9111_indexes_latest_tool_request.json` → original `/home/nic/forge/memory/llm_memory_v1/indexes/latest_tool_request.json`
- `shadow_files/0019_852cfeba9089d0c7_llm_tool_gateway_policy.json` ← `files/0019_852cfeba9089d0c7_indexes_llm_tool_gateway_policy.json` → original `/home/nic/forge/memory/llm_memory_v1/indexes/llm_tool_gateway_policy.json`
- `shadow_files/0020_deee7b0fc64cd88a_session_index.json` ← `files/0020_deee7b0fc64cd88a_indexes_session_index.json` → original `/home/nic/forge/memory/llm_memory_v1/indexes/session_index.json`
- `shadow_files/0021_dce804065de8d136_policy.json` ← `files/0021_dce804065de8d136_policy.json` → original `/home/nic/forge/memory/llm_memory_v1/policy.json`
- `shadow_files/0022_8256715e6af43ee8_llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json` ← `files/0022_8256715e6af43ee8_tool_requests_llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json` → original `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json`
- `shadow_files/0023_c9cfa1c31ef2fd45_llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json` ← `files/0023_c9cfa1c31ef2fd45_tool_requests_llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json` → original `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json`
- `shadow_files/0024_525ab1bae4078b0f_llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json` ← `files/0024_525ab1bae4078b0f_turns_llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json` → original `/home/nic/forge/memory/llm_memory_v1/turns/llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json`
- `shadow_files/0025_d137f535e41ab672_2026-05-14_201722_snapshot_plan_v1.md` ← `files/0025_d137f535e41ab672_2026-05-14_201722_snapshot_plan_v1.md` → original `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.md`
- `shadow_files/0026_291edf81adc83787_2026-05-14_201821_snapshot_plan_export_v1.json` ← `files/0026_291edf81adc83787_2026-05-14_201821_snapshot_plan_export_v1.json` → original `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201821_snapshot_plan_export_v1.json`
- `shadow_files/0027_b2581dede56226f7_2026-05-14_201821_snapshot_plan_export_v1.md` ← `files/0027_b2581dede56226f7_2026-05-14_201821_snapshot_plan_export_v1.md` → original `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201821_snapshot_plan_export_v1.md`
- `shadow_files/0028_60d553b337454a81_2026-05-12_173450_code_index_integrity.json` ← `files/0028_60d553b337454a81_2026-05-12_173450_code_index_integrity.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173450_code_index_integrity.json`
- `shadow_files/0029_872dbc59770061a3_2026-05-12_173526_code_engine_inventory.json` ← `files/0029_872dbc59770061a3_2026-05-12_173526_code_engine_inventory.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173526_code_engine_inventory.json`
- `shadow_files/0030_9529ee49f9f62b25_2026-05-12_173651_code_engine_duplicates.json` ← `files/0030_9529ee49f9f62b25_2026-05-12_173651_code_engine_duplicates.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173651_code_engine_duplicates.json`
- `shadow_files/0031_8de902108eb00daa_2026-05-12_173737_code_engine_canonical_plan.json` ← `files/0031_8de902108eb00daa_2026-05-12_173737_code_engine_canonical_plan.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_173737_code_engine_canonical_plan.json`
- `shadow_files/0032_c54e6f70f2ed2be7_2026-05-12_175412_symbolic_runtime_map.json` ← `files/0032_c54e6f70f2ed2be7_2026-05-12_175412_symbolic_runtime_map.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175412_symbolic_runtime_map.json`
- `shadow_files/0033_79c5ea985fea6a39_2026-05-12_175522_symbolic_runtime_gaps.json` ← `files/0033_79c5ea985fea6a39_2026-05-12_175522_symbolic_runtime_gaps.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175522_symbolic_runtime_gaps.json`
- `shadow_files/0034_674f12426ef78bb6_2026-05-12_175550_symbolic_runtime_export.json` ← `files/0034_674f12426ef78bb6_2026-05-12_175550_symbolic_runtime_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175550_symbolic_runtime_export.json`
- `shadow_files/0035_3b23b6654a610be1_2026-05-12_175550_symbolic_runtime_export.md` ← `files/0035_3b23b6654a610be1_2026-05-12_175550_symbolic_runtime_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_175550_symbolic_runtime_export.md`
- `shadow_files/0036_ddc790f63db243e5_2026-05-12_190340_test_inventory.json` ← `files/0036_ddc790f63db243e5_2026-05-12_190340_test_inventory.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_190340_test_inventory.json`
- `shadow_files/0037_106df90e3c9c7b61_2026-05-12_195339_engine_canonical_review.json` ← `files/0037_106df90e3c9c7b61_2026-05-12_195339_engine_canonical_review.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_195339_engine_canonical_review.json`
- `shadow_files/0038_2c2a45b3537e32a5_2026-05-12_195509_engine_canonical_review_export.json` ← `files/0038_2c2a45b3537e32a5_2026-05-12_195509_engine_canonical_review_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_195509_engine_canonical_review_export.json`
- `shadow_files/0039_1930eeed2d51eab3_2026-05-12_195509_engine_canonical_review_export.md` ← `files/0039_1930eeed2d51eab3_2026-05-12_195509_engine_canonical_review_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_195509_engine_canonical_review_export.md`
- `shadow_files/0040_8f6839da3df34ac5_2026-05-12_200356_engine_canonical_decision_draft.json` ← `files/0040_8f6839da3df34ac5_2026-05-12_200356_engine_canonical_decision_draft.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_200356_engine_canonical_decision_draft.json`
- `shadow_files/0041_3367015a04c82aae_2026-05-12_200444_engine_canonical_decision_draft_export.json` ← `files/0041_3367015a04c82aae_2026-05-12_200444_engine_canonical_decision_draft_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_200444_engine_canonical_decision_draft_export.json`
- `shadow_files/0042_72b286ae91be96b1_2026-05-12_200444_engine_canonical_decision_draft_export.md` ← `files/0042_72b286ae91be96b1_2026-05-12_200444_engine_canonical_decision_draft_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_200444_engine_canonical_decision_draft_export.md`
- `shadow_files/0043_a03469fa913fe2c9_2026-05-12_202152_engine_canonical_lockfile_draft.json` ← `files/0043_a03469fa913fe2c9_2026-05-12_202152_engine_canonical_lockfile_draft.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_202152_engine_canonical_lockfile_draft.json`
- `shadow_files/0044_a03469fa913fe2c9_2026-05-12_202324_engine_canonical_lockfile_draft_export.json` ← `files/0044_a03469fa913fe2c9_2026-05-12_202324_engine_canonical_lockfile_draft_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_202324_engine_canonical_lockfile_draft_export.json`
- `shadow_files/0045_a58cb729e6fa84ea_2026-05-12_202324_engine_canonical_lockfile_draft_export.md` ← `files/0045_a58cb729e6fa84ea_2026-05-12_202324_engine_canonical_lockfile_draft_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_202324_engine_canonical_lockfile_draft_export.md`
- `shadow_files/0046_fd83e9c17484c419_2026-05-12_203422_engine_review_ledger_export.json` ← `files/0046_fd83e9c17484c419_2026-05-12_203422_engine_review_ledger_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_203422_engine_review_ledger_export.json`
- `shadow_files/0047_665cfb66b9f5e03e_2026-05-12_203422_engine_review_ledger_export.md` ← `files/0047_665cfb66b9f5e03e_2026-05-12_203422_engine_review_ledger_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_203422_engine_review_ledger_export.md`
- `shadow_files/0048_be47fc83b351a130_2026-05-12_204309_engine_review_batch_export.json` ← `files/0048_be47fc83b351a130_2026-05-12_204309_engine_review_batch_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_204309_engine_review_batch_export.json`
- `shadow_files/0049_f6d0e37c037e0e3f_2026-05-12_204309_engine_review_batch_export.md` ← `files/0049_f6d0e37c037e0e3f_2026-05-12_204309_engine_review_batch_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_204309_engine_review_batch_export.md`
- `shadow_files/0050_8487047d9e11eff1_2026-05-12_205514_engine_human_approved_lockfile_candidate.json` ← `files/0050_8487047d9e11eff1_2026-05-12_205514_engine_human_approved_lockfile_candidate.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_205514_engine_human_approved_lockfile_candidate.json`
- `shadow_files/0051_8487047d9e11eff1_2026-05-12_205547_engine_human_approved_lockfile_candidate_export.json` ← `files/0051_8487047d9e11eff1_2026-05-12_205547_engine_human_approved_lockfile_candidate_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_205547_engine_human_approved_lockfile_candidate_export.json`
- `shadow_files/0052_9c4fc856728c1b8e_2026-05-12_205547_engine_human_approved_lockfile_candidate_export.md` ← `files/0052_9c4fc856728c1b8e_2026-05-12_205547_engine_human_approved_lockfile_candidate_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-12_205547_engine_human_approved_lockfile_candidate_export.md`
- `shadow_files/0053_6a279b7c8b2d3b3c_2026-05-14_195109_engine_brief_export.json` ← `files/0053_6a279b7c8b2d3b3c_2026-05-14_195109_engine_brief_export.json` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195109_engine_brief_export.json`
- `shadow_files/0054_583c00439e34e3e7_2026-05-14_195109_engine_brief_export.md` ← `files/0054_583c00439e34e3e7_2026-05-14_195109_engine_brief_export.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195109_engine_brief_export.md`
- `shadow_files/0055_399858c2b96c5c92_2026-05-14_195958_engine_approved_candidate_readiness_report.md` ← `files/0055_399858c2b96c5c92_2026-05-14_195958_engine_approved_candidate_readiness_report.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.md`
- `shadow_files/0056_720c4109b7fb25df_2026-05-14_200919_code_relationship_intelligence_report.md` ← `files/0056_720c4109b7fb25df_2026-05-14_200919_code_relationship_intelligence_report.md` → original `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.md`
- `shadow_files/0057_5207d4b17cacf3f9_code_index_current.json` ← `files/0057_5207d4b17cacf3f9_code_index_current.json` → original `/home/nic/forge/memory/code_library_v1/manifests/_code_index_current.json`
- `shadow_files/0058_44c117b4f0e649ad_engine_review_batch_plan_v1.json` ← `files/0058_44c117b4f0e649ad_engine_review_batch_plan_v1.json` → original `/home/nic/forge/memory/code_library_v1/manifests/engine_review_batch_plan_v1.json`