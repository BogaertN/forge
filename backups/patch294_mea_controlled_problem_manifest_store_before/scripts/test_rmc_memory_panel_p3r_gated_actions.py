#!/usr/bin/env python3
"""Behavior checks for Patch 262-UI-MemoryPanel-P3R.

This is a source-level and executable-JS guard test for the React-side gated
promotion arming logic. It does not call the backend and performs no writes.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "operator_console_src" / "RmcMemoryTab.tsx"
GUARDS_TS = ROOT / "operator_console_src" / "rmc-ui-guards.ts"
GUARDS_JS = ROOT / "operator_console_src" / "rmc-ui-guards.js"
CLIENT_TS = ROOT / "operator_console_src" / "rmc-api-client.ts"

passes: list[str] = []
fails: list[str] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        passes.append(name)
        print(f"[PASS] {name}{' :: ' + detail if detail else ''}")
    else:
        fails.append(name)
        print(f"[FAIL] {name}{' :: ' + detail if detail else ''}")

panel = PANEL.read_text(encoding="utf-8") if PANEL.exists() else ""
guards_ts = GUARDS_TS.read_text(encoding="utf-8") if GUARDS_TS.exists() else ""
guards_js = GUARDS_JS.read_text(encoding="utf-8") if GUARDS_JS.exists() else ""
client_ts = CLIENT_TS.read_text(encoding="utf-8") if CLIENT_TS.exists() else ""

check("panel_exists", PANEL.exists(), str(PANEL))
check("guards_ts_exists", GUARDS_TS.exists(), str(GUARDS_TS))
check("guards_js_exists", GUARDS_JS.exists(), str(GUARDS_JS))
check("client_ts_exists", CLIENT_TS.exists(), str(CLIENT_TS))
check("panel_imports_guard", "../lib/rmc-ui-guards" in panel)
check("panel_uses_evaluate_arm_state", "evaluateGuardPromotionArmState" in panel)
check("panel_has_confirmation_state", "promotionConfirmation" in panel)
check("panel_requires_confirmation_phrase", "Required confirmation" in panel and "PROMOTE <candidate_id>" in panel)
check("panel_shows_arm_state", "Promotion arm state" in panel)
check("panel_disables_button_until_canPromote", "disabled={!canPromote}" in panel)
check("panel_resets_token_on_preview", "setPromotionApproval('')" in panel)
check("panel_resets_confirmation_on_preview", "setPromotionConfirmation('')" in panel)
check("guard_token_exact", "APPROVE_RMC_PROMOTION" in guards_ts and "APPROVE_RMC_PROMOTION" in guards_js)
check("guard_preview_required", "promotion_preview_required" in guards_ts)
check("guard_preview_current_required", "preview_candidate_mismatch" in guards_ts)
check("guard_exact_token_required", "exact_approval_token_required" in guards_ts)
check("guard_exact_confirmation_required", "exact_confirmation_phrase_required" in guards_ts)
check("guard_duplicate_blocks", "duplicate_promotion_detected" in guards_ts)
check("guard_unsafe_paths_block", "unsafe_paths_present" in guards_ts)
check("guard_missing_fields_block", "missing_required_fields_present" in guards_ts)
check("client_preserves_correct_promote_token", "APPROVE_RMC_PROMOTION" in client_ts)
check("bad_token_absent", "APPROVE_PROMOTE_MEMORY" not in panel + guards_ts + client_ts)
check("no_shell_exec", "child_process" not in panel + guards_ts + guards_js + client_ts and "exec(" not in guards_ts)

node_code = f'''
import {{ createRequire }} from 'node:module';
const require = createRequire(import.meta.url);
const {{ evaluatePromotionArmState, buildPromotionConfirmationPhrase, PROMOTION_TOKEN }} = require({json.dumps(str(GUARDS_JS))});
const preview = {{
  candidate_id: 'rmccand_test_001',
  promotion_allowed: true,
  writes_files: false,
  memory_write_allowed: false,
  unsafe_paths: [],
  missing_required_fields: [],
  duplicate_check: {{ duplicate: false }},
  stable_memory_preview: {{ source_candidate_id: 'rmccand_test_001' }}
}};
const armed = evaluatePromotionArmState({{
  candidateId: 'rmccand_test_001',
  approvalToken: PROMOTION_TOKEN,
  confirmationPhrase: 'PROMOTE rmccand_test_001',
  preview
}});
const noPreview = evaluatePromotionArmState({{
  candidateId: 'rmccand_test_001',
  approvalToken: PROMOTION_TOKEN,
  confirmationPhrase: 'PROMOTE rmccand_test_001',
  preview: null
}});
const badConfirm = evaluatePromotionArmState({{
  candidateId: 'rmccand_test_001',
  approvalToken: PROMOTION_TOKEN,
  confirmationPhrase: 'PROMOTE WRONG',
  preview
}});
const duplicate = evaluatePromotionArmState({{
  candidateId: 'rmccand_test_001',
  approvalToken: PROMOTION_TOKEN,
  confirmationPhrase: 'PROMOTE rmccand_test_001',
  preview: {{ ...preview, duplicate_check: {{ duplicate: true }} }}
}});
console.log(JSON.stringify({{
  phrase: buildPromotionConfirmationPhrase('rmccand_test_001'),
  armed,
  noPreview,
  badConfirm,
  duplicate,
}}));
'''
try:
    result = subprocess.run(["node", "--input-type=module", "-e", node_code], text=True, capture_output=True, check=True)
    payload = json.loads(result.stdout)
    check("js_phrase_exact", payload["phrase"] == "PROMOTE rmccand_test_001")
    check("js_armed_when_all_conditions_pass", payload["armed"]["armed"] is True)
    check("js_no_preview_blocks", payload["noPreview"]["armed"] is False and "promotion_preview_required" in payload["noPreview"]["reasonCodes"])
    check("js_bad_confirmation_blocks", payload["badConfirm"]["armed"] is False and "exact_confirmation_phrase_required" in payload["badConfirm"]["reasonCodes"])
    check("js_duplicate_blocks", payload["duplicate"]["armed"] is False and "duplicate_promotion_detected" in payload["duplicate"]["reasonCodes"])
except Exception as exc:
    check("js_guard_behavior_executes", False, repr(exc))

print(f"Total: {len(passes) + len(fails)}")
print(f"Passed: {len(passes)}")
print(f"Failed: {len(fails)}")
if fails:
    print("RESULT: rmc_memory_panel_p3r_gated_actions_tests_pass=False")
    raise SystemExit(1)
print("RESULT: rmc_memory_panel_p3r_gated_actions_tests_pass=True")
