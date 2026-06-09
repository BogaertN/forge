# Patch 86 Shadow Restore Copy Sandbox Receipt

Mode: FORGE-OWNED SHADOW COPY ONLY. No live restore authority exists.
Created: `2026-05-14T21:03:40`
Status: `SHADOW_COPY_SANDBOX_READY_NO_LIVE_RESTORE`
Shadow root: `/home/nic/forge/memory/shadow_restores_v1/2026-05-14_210340_shadow_restore_copy_sandbox`

## Counts
- Files planned: `58`
- Files copied: `58`
- Hash mismatches: `0`
- Blockers: `0`
- Warnings: `2`

## Authority
- shadow_restore_plan_authority: `True`
- shadow_restore_copy_authority: `True`
- restore_authority: `False`
- live_restore_authority: `False`
- project_file_write_authority: `False`
- engine_file_write_authority: `False`
- delete_authority: `False`
- quarantine_authority: `False`
- shell_execution_authority: `False`
- chroma_write_authority: `False`
- snapshot_create_authority: `False`
- final_lockfile_authority: `False`

## Notes
- Patch 86 copied snapshot files only into a Forge-owned shadow area.
- This is not a restore. Live Forge and AI.Web project files were not modified by this command.
- A future restore-readiness patch must be separate and explicit before any live restore can exist.

## Warnings
- Expected volatile source drift accepted for copy: /home/nic/forge/logs/forge_audit.log
- Expected volatile source drift accepted for copy: /home/nic/forge/logs/forge_audit.log

## Copied Files
- `shadow_files/0001_def9b3d137a054d5_main.py` sha=`def9b3d137a054d5` match=`True`
- `shadow_files/0002_d78daa9932ec2725_tool_registry.json` sha=`d78daa9932ec2725` match=`True`
- `shadow_files/0003_80c98f351a0ffe36_approved_paths.json` sha=`80c98f351a0ffe36` match=`True`
- `shadow_files/0004_c3938638499a391a_session_scope.json` sha=`c3938638499a391a` match=`True`
- `shadow_files/0005_44d95ae68394bd53_forge_audit.log` sha=`44d95ae68394bd53` match=`True`
- `shadow_files/0006_3f0af0874087943f_engine_review_ledger_v1.json` sha=`3f0af0874087943f` match=`True`
- `shadow_files/0007_530d794800293b1f_2026-05-14_201722_snapshot_plan_v1.json` sha=`530d794800293b1f` match=`True`
- `shadow_files/0008_6136b92f81ffe5fe_2026-05-14_195958_engine_approved_candidate_readiness_report.json` sha=`6136b92f81ffe5fe` match=`True`
- `shadow_files/0009_ee6f80af744d6f84_2026-05-14_200919_code_relationship_intelligence_report.json` sha=`ee6f80af744d6f84` match=`True`
- `shadow_files/0010_4a6ab344567a9ce9_forge_2026_05_14_192941.jsonl` sha=`4a6ab344567a9ce9` match=`True`
- `shadow_files/0011_bd96a24def4504d7_forge_2026_05_14_193652.jsonl` sha=`bd96a24def4504d7` match=`True`
- `shadow_files/0012_f66218b1fd8a5e5b_seed_llm_memory_reason_for_patch75.json` sha=`f66218b1fd8a5e5b` match=`True`
- `shadow_files/0013_f6b14dc692a7d7d5_seed_patch67_archive_root_instruction_correction.json` sha=`f6b14dc692a7d7d5` match=`True`
- `shadow_files/0014_a405cd3e1db5a417_seed_patch74_timestamp_helper_correction.json` sha=`a405cd3e1db5a417` match=`True`
- `shadow_files/0015_f9df4249d0796ba2_2026-05-14_193152_llm_memory_export.json` sha=`f9df4249d0796ba2` match=`True`
- `shadow_files/0016_c8e45e3ebc23a3d3_2026-05-14_193152_llm_memory_export.md` sha=`c8e45e3ebc23a3d3` match=`True`
- `shadow_files/0017_f8385574e6d751d1_latest_receipt.json` sha=`f8385574e6d751d1` match=`True`
- `shadow_files/0018_61478def243f9111_latest_tool_request.json` sha=`61478def243f9111` match=`True`
- `shadow_files/0019_852cfeba9089d0c7_llm_tool_gateway_policy.json` sha=`852cfeba9089d0c7` match=`True`
- `shadow_files/0020_deee7b0fc64cd88a_session_index.json` sha=`deee7b0fc64cd88a` match=`True`
- `shadow_files/0021_dce804065de8d136_policy.json` sha=`dce804065de8d136` match=`True`
- `shadow_files/0022_8256715e6af43ee8_llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json` sha=`8256715e6af43ee8` match=`True`
- `shadow_files/0023_c9cfa1c31ef2fd45_llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json` sha=`c9cfa1c31ef2fd45` match=`True`
- `shadow_files/0024_525ab1bae4078b0f_llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json` sha=`525ab1bae4078b0f` match=`True`
- `shadow_files/0025_d137f535e41ab672_2026-05-14_201722_snapshot_plan_v1.md` sha=`d137f535e41ab672` match=`True`
- `shadow_files/0026_291edf81adc83787_2026-05-14_201821_snapshot_plan_export_v1.json` sha=`291edf81adc83787` match=`True`
- `shadow_files/0027_b2581dede56226f7_2026-05-14_201821_snapshot_plan_export_v1.md` sha=`b2581dede56226f7` match=`True`
- `shadow_files/0028_60d553b337454a81_2026-05-12_173450_code_index_integrity.json` sha=`60d553b337454a81` match=`True`
- `shadow_files/0029_872dbc59770061a3_2026-05-12_173526_code_engine_inventory.json` sha=`872dbc59770061a3` match=`True`
- `shadow_files/0030_9529ee49f9f62b25_2026-05-12_173651_code_engine_duplicates.json` sha=`9529ee49f9f62b25` match=`True`
- `shadow_files/0031_8de902108eb00daa_2026-05-12_173737_code_engine_canonical_plan.json` sha=`8de902108eb00daa` match=`True`
- `shadow_files/0032_c54e6f70f2ed2be7_2026-05-12_175412_symbolic_runtime_map.json` sha=`c54e6f70f2ed2be7` match=`True`
- `shadow_files/0033_79c5ea985fea6a39_2026-05-12_175522_symbolic_runtime_gaps.json` sha=`79c5ea985fea6a39` match=`True`
- `shadow_files/0034_674f12426ef78bb6_2026-05-12_175550_symbolic_runtime_export.json` sha=`674f12426ef78bb6` match=`True`
- `shadow_files/0035_3b23b6654a610be1_2026-05-12_175550_symbolic_runtime_export.md` sha=`3b23b6654a610be1` match=`True`
- `shadow_files/0036_ddc790f63db243e5_2026-05-12_190340_test_inventory.json` sha=`ddc790f63db243e5` match=`True`
- `shadow_files/0037_106df90e3c9c7b61_2026-05-12_195339_engine_canonical_review.json` sha=`106df90e3c9c7b61` match=`True`
- `shadow_files/0038_2c2a45b3537e32a5_2026-05-12_195509_engine_canonical_review_export.json` sha=`2c2a45b3537e32a5` match=`True`
- `shadow_files/0039_1930eeed2d51eab3_2026-05-12_195509_engine_canonical_review_export.md` sha=`1930eeed2d51eab3` match=`True`
- `shadow_files/0040_8f6839da3df34ac5_2026-05-12_200356_engine_canonical_decision_draft.json` sha=`8f6839da3df34ac5` match=`True`
- `shadow_files/0041_3367015a04c82aae_2026-05-12_200444_engine_canonical_decision_draft_export.json` sha=`3367015a04c82aae` match=`True`
- `shadow_files/0042_72b286ae91be96b1_2026-05-12_200444_engine_canonical_decision_draft_export.md` sha=`72b286ae91be96b1` match=`True`
- `shadow_files/0043_a03469fa913fe2c9_2026-05-12_202152_engine_canonical_lockfile_draft.json` sha=`a03469fa913fe2c9` match=`True`
- `shadow_files/0044_a03469fa913fe2c9_2026-05-12_202324_engine_canonical_lockfile_draft_export.json` sha=`a03469fa913fe2c9` match=`True`
- `shadow_files/0045_a58cb729e6fa84ea_2026-05-12_202324_engine_canonical_lockfile_draft_export.md` sha=`a58cb729e6fa84ea` match=`True`
- `shadow_files/0046_fd83e9c17484c419_2026-05-12_203422_engine_review_ledger_export.json` sha=`fd83e9c17484c419` match=`True`
- `shadow_files/0047_665cfb66b9f5e03e_2026-05-12_203422_engine_review_ledger_export.md` sha=`665cfb66b9f5e03e` match=`True`
- `shadow_files/0048_be47fc83b351a130_2026-05-12_204309_engine_review_batch_export.json` sha=`be47fc83b351a130` match=`True`
- `shadow_files/0049_f6d0e37c037e0e3f_2026-05-12_204309_engine_review_batch_export.md` sha=`f6d0e37c037e0e3f` match=`True`
- `shadow_files/0050_8487047d9e11eff1_2026-05-12_205514_engine_human_approved_lockfile_candidate.json` sha=`8487047d9e11eff1` match=`True`
- `shadow_files/0051_8487047d9e11eff1_2026-05-12_205547_engine_human_approved_lockfile_candidate_export.json` sha=`8487047d9e11eff1` match=`True`
- `shadow_files/0052_9c4fc856728c1b8e_2026-05-12_205547_engine_human_approved_lockfile_candidate_export.md` sha=`9c4fc856728c1b8e` match=`True`
- `shadow_files/0053_6a279b7c8b2d3b3c_2026-05-14_195109_engine_brief_export.json` sha=`6a279b7c8b2d3b3c` match=`True`
- `shadow_files/0054_583c00439e34e3e7_2026-05-14_195109_engine_brief_export.md` sha=`583c00439e34e3e7` match=`True`
- `shadow_files/0055_399858c2b96c5c92_2026-05-14_195958_engine_approved_candidate_readiness_report.md` sha=`399858c2b96c5c92` match=`True`
- `shadow_files/0056_720c4109b7fb25df_2026-05-14_200919_code_relationship_intelligence_report.md` sha=`720c4109b7fb25df` match=`True`
- `shadow_files/0057_5207d4b17cacf3f9_code_index_current.json` sha=`5207d4b17cacf3f9` match=`True`
- `shadow_files/0058_44c117b4f0e649ad_engine_review_batch_plan_v1.json` sha=`44c117b4f0e649ad` match=`True`