# PATCH_LIVE_READINESS_V1

Status: PATCH_LIFECYCLE_2_GATE_MATRIX_READY
Created: 2026-05-17T08:58:52
Target: stack_linker_breather
Eligible for live apply: False

## Summary
- gates_total: 13
- blocking_failures: 3
- warnings: 0
- eligible_for_live_apply: False
- known_test_issue: True
- recommended_next_patch: Patch 134 — Gated repair for stack_linker_breather import/test issue

## Gates
- source_grounded_proposal_exists: PASS — latest source-grounded proposal packet present
- source_grounded_proposal_verified: PASS — proposal verification has zero problems
- visible_local_llm_called: PASS — local Ollama model call captured with raw response
- target_file_scope_valid: PASS — primary target exists under /home/nic/aiweb
- test_target_scope_valid: PASS — test targets exist under /home/nic/aiweb
- source_evidence_candidate_bound: PASS — candidate source evidence exists with observed hashes
- patch_impact_known: PASS — target exists in patch impact map
- safe_test_result_known: PASS — latest canonical safe-test run is recorded
- target_tests_currently_pass: FAIL — target currently has known test issue; repair patch not live-apply eligible yet
- rollback_plan_present: PASS — rollback plan requirements are recorded
- fresh_snapshot_required: FAIL — no verified relevant snapshot found in this gate input
- sandbox_pass_required: PASS — sandbox report exists and passed
- human_approval_recorded: FAIL — no explicit human approval token/receipt has been recorded for live apply

## Problems
- target_tests_currently_pass: target currently has known test issue; repair patch not live-apply eligible yet
- fresh_snapshot_required: no verified relevant snapshot found in this gate input
- human_approval_recorded: no explicit human approval token/receipt has been recorded for live apply
