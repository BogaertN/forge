# Patch 90 Live Restore Approval Token

Mode: APPROVAL TOKEN ONLY. No live restore authority exists.
Created: `2026-05-15T05:08:20`
Status: `LIVE_RESTORE_APPROVAL_TOKEN_READY_WITH_WARNINGS_NO_AUTHORITY`
Approval token: `LRA-df9d8ffc017d8a64f2c819ec`
Source preflight: `/home/nic/forge/memory/live_restore_preflight_v1/2026-05-14_212207_snapshot_live_restore_preflight_v1.json`

## Counts
- Bound files: `58`
- Overwrite candidates if future approved: `4`
- Already matching snapshot: `54`
- Missing targets if future approved: `0`
- Blockers: `0`
- Warnings: `12`

## Authority
- Live restore: `NO`
- Project writes: `NO`
- Engine writes: `NO`
- Shell execution: `NO`

## Human Review Acknowledgement Required For Future Patch Only
- I understand this token does not restore files.
- I understand future restore authority would require a separate patch.
- I understand any future live restore must re-run preflight against current disk state.
- I understand overwrite candidates must be backed up immediately before any future restore.
- I understand Forge must refuse secrets, credentials, keys, .env, ~/.ssh, and unscoped paths.

## First 25 Bound Rows
- `LIVE_TARGET_DIFFERS_FROM_SNAPSHOT_WOULD_OVERWRITE_ONLY_IF_FUTURE_APPROVED` `/home/nic/forge/main.py` expected=`def9b3d137a054d5b5c2685e44487cc57e657c010db50084d6f614c79b7dd9de` live_at_preflight=`821e44fbe5dea6644ff5279c665893d342411d90cf48b802b5e8e722d5f2c31f`
- `LIVE_TARGET_DIFFERS_FROM_SNAPSHOT_WOULD_OVERWRITE_ONLY_IF_FUTURE_APPROVED` `/home/nic/forge/config/tool_registry.json` expected=`d78daa9932ec272548ce1ac5ab12f7733f6b10b0c48c08ffb53433e56a3eae17` live_at_preflight=`7e4c1d31219aa0c95e2614b541aa89b15b36dd3bcf76ab09afef30ac19c731dc`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/config/approved_paths.json` expected=`80c98f351a0ffe369ac7acd08c4390e8901dd003b7ce1448cdc3d1093b06f7c6` live_at_preflight=`80c98f351a0ffe369ac7acd08c4390e8901dd003b7ce1448cdc3d1093b06f7c6`
- `LIVE_TARGET_DIFFERS_FROM_SNAPSHOT_WOULD_OVERWRITE_ONLY_IF_FUTURE_APPROVED` `/home/nic/forge/config/session_scope.json` expected=`c3938638499a391a9620e3b1e4ec25d4930793ba05b47e370f06e8131a2b3797` live_at_preflight=`7c8329adb4d93c4aec5b73ac1236b331de44cb870e9489a0da618a91a9e9726b`
- `LIVE_TARGET_DIFFERS_FROM_SNAPSHOT_WOULD_OVERWRITE_ONLY_IF_FUTURE_APPROVED` `/home/nic/forge/logs/forge_audit.log` expected=`44d95ae68394bd536ce0aea44cbb0738eb430e79905d1ee88b8887e087d59dfc` live_at_preflight=`33214142d60bd7aa252176bd42b2f0c433613670acf7408a39c6018e8b0b0c8b`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/code_library_v1/manifests/engine_review_ledger_v1.json` expected=`3f0af0874087943fbee00c591a63cc2c94ae4301c3d2dd1a9d0cd412a44cefdf` live_at_preflight=`3f0af0874087943fbee00c591a63cc2c94ae4301c3d2dd1a9d0cd412a44cefdf`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.json` expected=`530d794800293b1f6068228266025106277f926b4d5f5ce1d85778e33a01f6a2` live_at_preflight=`530d794800293b1f6068228266025106277f926b4d5f5ce1d85778e33a01f6a2`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_195958_engine_approved_candidate_readiness_report.json` expected=`6136b92f81ffe5fe898fbd714caca3f44cac1ef5178e0a81b490b31a7d78e158` live_at_preflight=`6136b92f81ffe5fe898fbd714caca3f44cac1ef5178e0a81b490b31a7d78e158`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/code_library_v1/manifests/2026-05-14_200919_code_relationship_intelligence_report.json` expected=`ee6f80af744d6f8461d5f93d001adaf2853725a84c43c212019b8a38062995ce` live_at_preflight=`ee6f80af744d6f8461d5f93d001adaf2853725a84c43c212019b8a38062995ce`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_192941.jsonl` expected=`4a6ab344567a9ce90cc9a305f70485613024cc76d5d5fc0ffe1bfc10b1b98a89` live_at_preflight=`4a6ab344567a9ce90cc9a305f70485613024cc76d5d5fc0ffe1bfc10b1b98a89`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/conversations/forge_2026_05_14_193652.jsonl` expected=`bd96a24def4504d7b41697b1ea8bf2e4e6716d1982f6bdf8022d903b61d21b61` live_at_preflight=`bd96a24def4504d7b41697b1ea8bf2e4e6716d1982f6bdf8022d903b61d21b61`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_llm_memory_reason_for_patch75.json` expected=`f66218b1fd8a5e5b314439697fb1a7c49817a38191d8aaa9d95215ea0b70ab43` live_at_preflight=`f66218b1fd8a5e5b314439697fb1a7c49817a38191d8aaa9d95215ea0b70ab43`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch67_archive_root_instruction_correction.json` expected=`f6b14dc692a7d7d57a04fffd1c868e9d78c4484acf11e99621cb552192c9059b` live_at_preflight=`f6b14dc692a7d7d57a04fffd1c868e9d78c4484acf11e99621cb552192c9059b`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/corrections/seed_patch74_timestamp_helper_correction.json` expected=`a405cd3e1db5a417c92fa51159e4ff74f2dd6bfa85c88c39d212c0f62d51d145` live_at_preflight=`a405cd3e1db5a417c92fa51159e4ff74f2dd6bfa85c88c39d212c0f62d51d145`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.json` expected=`f9df4249d0796ba2b32e2d68e267de74c0241293dca3c3aeccd39ca332bf4dfa` live_at_preflight=`f9df4249d0796ba2b32e2d68e267de74c0241293dca3c3aeccd39ca332bf4dfa`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/exports/2026-05-14_193152_llm_memory_export.md` expected=`c8e45e3ebc23a3d3e983f93385eff3cb60083e3cc582f36d8365c57a49dd246d` live_at_preflight=`c8e45e3ebc23a3d3e983f93385eff3cb60083e3cc582f36d8365c57a49dd246d`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/indexes/latest_receipt.json` expected=`f8385574e6d751d11af72eba001705a704e5ed9b3391825bc6a9d885b50ef132` live_at_preflight=`f8385574e6d751d11af72eba001705a704e5ed9b3391825bc6a9d885b50ef132`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/indexes/latest_tool_request.json` expected=`61478def243f911152922870c0db5a4bf6dcaabc4c5f735ffb377913c78a55d9` live_at_preflight=`61478def243f911152922870c0db5a4bf6dcaabc4c5f735ffb377913c78a55d9`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/indexes/llm_tool_gateway_policy.json` expected=`852cfeba9089d0c7d36de1cbde6e8888a97f94408760ec8dc468452222ef76a0` live_at_preflight=`852cfeba9089d0c7d36de1cbde6e8888a97f94408760ec8dc468452222ef76a0`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/indexes/session_index.json` expected=`deee7b0fc64cd88ada1597f10f882bdc07e337f4c97f385fdcfa9e25bff51d25` live_at_preflight=`deee7b0fc64cd88ada1597f10f882bdc07e337f4c97f385fdcfa9e25bff51d25`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/policy.json` expected=`dce804065de8d1369df5e35f5fa8e36319df1e4efee98570a5bba5b0c89a11a6` live_at_preflight=`dce804065de8d1369df5e35f5fa8e36319df1e4efee98570a5bba5b0c89a11a6`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194126_5699890aff5e9f1d.json` expected=`8256715e6af43ee836b4fd31fe9b824446b9ffb4d93984874ad1b5bde071a4c5` live_at_preflight=`8256715e6af43ee836b4fd31fe9b824446b9ffb4d93984874ad1b5bde071a4c5`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/tool_requests/llm_tool_request_2026-05-14_194137_737eb8f2dc742d1e.json` expected=`c9cfa1c31ef2fd45c79cdd0998dbfe7b32798dcde15a966b6f1f3e03d394f781` live_at_preflight=`c9cfa1c31ef2fd45c79cdd0998dbfe7b32798dcde15a966b6f1f3e03d394f781`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/llm_memory_v1/turns/llm_turn_2026-05-14_193028_f806f8edb4b7aba8.json` expected=`525ab1bae4078b0fcd9eeb9abdd4f146004569c016b0b916e8a93f2827f2fb7c` live_at_preflight=`525ab1bae4078b0fcd9eeb9abdd4f146004569c016b0b916e8a93f2827f2fb7c`
- `LIVE_TARGET_ALREADY_MATCHES_SNAPSHOT_NO_OVERWRITE_NEEDED` `/home/nic/forge/memory/snapshot_plans_v1/2026-05-14_201722_snapshot_plan_v1.md` expected=`d137f535e41ab672607781000318e6c3e778d06e862fa3fd3604830f663b54a6` live_at_preflight=`d137f535e41ab672607781000318e6c3e778d06e862fa3fd3604830f663b54a6`

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