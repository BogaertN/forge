# Patch 91 Live Restore Candidate Command Dry Run

Mode: DRY-RUN ONLY. No live restore authority exists.
Created: `2026-05-15T05:16:57`
Status: `LIVE_RESTORE_CANDIDATE_DRY_RUN_READY_WITH_WARNINGS_NO_AUTHORITY`
Dry-run id: `LRD-4a17a2a56b36f85fa9dee7ff`
Source approval token: `/home/nic/forge/memory/live_restore_approval_tokens_v1/2026-05-15_050820_snapshot_live_restore_approval_token_v1.json`
Source approval token id: `LRA-df9d8ffc017d8a64f2c819ec`

## Counts
- Files checked: `58`
- Would overwrite if future approved: `4`
- Already matching snapshot: `54`
- Would create if future approved: `0`
- Blockers: `0`
- Warnings: `16`

## Authority
- Live restore: `NO`
- Project writes: `NO`
- Engine writes: `NO`
- Shell execution: `NO`

## First 25 Dry-Run Rows
- `DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` `/home/nic/forge/main.py` expected=`def9b3d137a054d5b5c2685e44487cc57e657c010db50084d6f614c79b7dd9de` current=`144dc490749ef4e11b891b17db7af87dbc13e148650c9c49915881928be8eef9`
- `DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` `/home/nic/forge/config/tool_registry.json` expected=`d78daa9932ec272548ce1ac5ab12f7733f6b10b0c48c08ffb53433e56a3eae17` current=`8202a5a3743661f68bdd1f90be7dca973e94e884ed6251178e7108caf644c427`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/config/approved_paths.json` expected=`80c98f351a0ffe369ac7acd08c4390e8901dd003b7ce1448cdc3d1093b06f7c6` current=`80c98f351a0ffe369ac7acd08c4390e8901dd003b7ce1448cdc3d1093b06f7c6`
- `DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` `/home/nic/forge/config/session_scope.json` expected=`c3938638499a391a9620e3b1e4ec25d4930793ba05b47e370f06e8131a2b3797` current=`52120280d04c73b94fc66d3eecac2623f8aaabea3a9d83c2cd640e02838fc673`
- `DRY_RUN_WOULD_OVERWRITE_IF_FUTURE_PATCH_APPROVED` `/home/nic/forge/logs/forge_audit.log` expected=`44d95ae68394bd536ce0aea44cbb0738eb430e79905d1ee88b8887e087d59dfc` current=`c4063f4fcc6304da374162c76659cf85df102cb957483dcf77df4d5d607d89e8`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/engine_review_ledger_v1.json` expected=`3f0af0874087943fbee00c591a63cc2c94ae4301c3d2dd1a9d0cd412a44cefdf` current=`3f0af0874087943fbee00c591a63cc2c94ae4301c3d2dd1a9d0cd412a44cefdf`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.json` expected=`530d794800293b1f6068228266025106277f926b4d5f5ce1d85778e33a01f6a2` current=`530d794800293b1f6068228266025106277f926b4d5f5ce1d85778e33a01f6a2`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.json` expected=`6136b92f81ffe5fe898fbd714caca3f44cac1ef5178e0a81b490b31a7d78e158` current=`6136b92f81ffe5fe898fbd714caca3f44cac1ef5178e0a81b490b31a7d78e158`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.json` expected=`ee6f80af744d6f8461d5f93d001adaf2853725a84c43c212019b8a38062995ce` current=`ee6f80af744d6f8461d5f93d001adaf2853725a84c43c212019b8a38062995ce`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_192941.jsonl` expected=`4a6ab344567a9ce90cc9a305f70485613024cc76d5d5fc0ffe1bfc10b1b98a89` current=`4a6ab344567a9ce90cc9a305f70485613024cc76d5d5fc0ffe1bfc10b1b98a89`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_193652.jsonl` expected=`bd96a24def4504d7b41697b1ea8bf2e4e6716d1982f6bdf8022d903b61d21b61` current=`bd96a24def4504d7b41697b1ea8bf2e4e6716d1982f6bdf8022d903b61d21b61`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_llm_memory_reason_for_patch75.json` expected=`f66218b1fd8a5e5b314439697fb1a7c49817a38191d8aaa9d95215ea0b70ab43` current=`f66218b1fd8a5e5b314439697fb1a7c49817a38191d8aaa9d95215ea0b70ab43`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch67_archive_root_instruction_correction.json` expected=`f6b14dc692a7d7d57a04fffd1c868e9d78c4484acf11e99621cb552192c9059b` current=`f6b14dc692a7d7d57a04fffd1c868e9d78c4484acf11e99621cb552192c9059b`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch74_timestamp_helper_correction.json` expected=`a405cd3e1db5a417c92fa51159e4ff74f2dd6bfa85c88c39d212c0f62d51d145` current=`a405cd3e1db5a417c92fa51159e4ff74f2dd6bfa85c88c39d212c0f62d51d145`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.json` expected=`f9df4249d0796ba2b32e2d68e267de74c0241293dca3c3aeccd39ca332bf4dfa` current=`f9df4249d0796ba2b32e2d68e267de74c0241293dca3c3aeccd39ca332bf4dfa`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.md` expected=`c8e45e3ebc23a3d3e983f93385eff3cb60083e3cc582f36d8365c57a49dd246d` current=`c8e45e3ebc23a3d3e983f93385eff3cb60083e3cc582f36d8365c57a49dd246d`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/latest_receipt.json` expected=`f8385574e6d751d11af72eba001705a704e5ed9b3391825bc6a9d885b50ef132` current=`f8385574e6d751d11af72eba001705a704e5ed9b3391825bc6a9d885b50ef132`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/latest_tool_request.json` expected=`61478def243f911152922870c0db5a4bf6dcaabc4c5f735ffb377913c78a55d9` current=`61478def243f911152922870c0db5a4bf6dcaabc4c5f735ffb377913c78a55d9`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/llm_tool_gateway_policy.json` expected=`852cfeba9089d0c7d36de1cbde6e8888a97f94408760ec8dc468452222ef76a0` current=`852cfeba9089d0c7d36de1cbde6e8888a97f94408760ec8dc468452222ef76a0`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/indexes/session_index.json` expected=`deee7b0fc64cd88ada1597f10f882bdc07e337f4c97f385fdcfa9e25bff51d25` current=`deee7b0fc64cd88ada1597f10f882bdc07e337f4c97f385fdcfa9e25bff51d25`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/policy.json` expected=`dce804065de8d1369df5e35f5fa8e36319df1e4efee98570a5bba5b0c89a11a6` current=`dce804065de8d1369df5e35f5fa8e36319df1e4efee98570a5bba5b0c89a11a6`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json` expected=`8256715e6af43ee836b4fd31fe9b824446b9ffb4d93984874ad1b5bde071a4c5` current=`8256715e6af43ee836b4fd31fe9b824446b9ffb4d93984874ad1b5bde071a4c5`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json` expected=`c9cfa1c31ef2fd45c79cdd0998dbfe7b32798dcde15a966b6f1f3e03d394f781` current=`c9cfa1c31ef2fd45c79cdd0998dbfe7b32798dcde15a966b6f1f3e03d394f781`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/llm_memory_v1/turns/llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json` expected=`525ab1bae4078b0fcd9eeb9abdd4f146004569c016b0b916e8a93f2827f2fb7c` current=`525ab1bae4078b0fcd9eeb9abdd4f146004569c016b0b916e8a93f2827f2fb7c`
- `DRY_RUN_NOOP_ALREADY_MATCHES_SNAPSHOT` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.md` expected=`d137f535e41ab672607781000318e6c3e778d06e862fa3fd3604830f663b54a6` current=`d137f535e41ab672607781000318e6c3e778d06e862fa3fd3604830f663b54a6`

## Warnings
- /home/nic/forge/main.py: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/config/tool_registry.json: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/config/session_scope.json: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/logs/forge_audit.log: future restore would overwrite a live file that currently differs from the snapshot
- Expected volatile source drift accepted for copy: /home/nic/forge/logs/forge_audit.log
- Expected volatile source drift accepted for copy: /home/nic/forge/logs/forge_audit.log
- Expected volatile source drift accepted for copy: /home/nic/forge/logs/forge_audit.log
- Expected volatile source drift accepted for copy: /home/nic/forge/logs/forge_audit.log
- /home/nic/forge/main.py: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/config/tool_registry.json: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/config/session_scope.json: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/logs/forge_audit.log: future restore would overwrite a live file that currently differs from the snapshot
- /home/nic/forge/main.py: current live SHA differs from snapshot SHA; future restore would overwrite this file
- /home/nic/forge/config/tool_registry.json: current live SHA differs from snapshot SHA; future restore would overwrite this file
- /home/nic/forge/config/session_scope.json: current live SHA differs from snapshot SHA; future restore would overwrite this file
- /home/nic/forge/logs/forge_audit.log: current live SHA differs from snapshot SHA; future restore would overwrite this file