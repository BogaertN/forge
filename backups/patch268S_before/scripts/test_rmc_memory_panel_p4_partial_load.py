#!/usr/bin/env python3
"""Patch 262-UI-MemoryPanel-P4 behavior tests.

Static + executable tests for the React-side partial-load guard. These tests do not
call backend routes, do not write memory, and do not execute shell commands beyond
Node importing the JS helper.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "operator_console_src" / "RmcMemoryTab.tsx"
HEALTH_TS = ROOT / "operator_console_src" / "rmc-panel-health.ts"
HEALTH_JS = ROOT / "operator_console_src" / "rmc-panel-health.js"
GUARDS_TS = ROOT / "operator_console_src" / "rmc-ui-guards.ts"
CLIENT_TS = ROOT / "operator_console_src" / "rmc-api-client.ts"

checks: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))

panel = PANEL.read_text(encoding="utf-8") if PANEL.exists() else ""
health_ts = HEALTH_TS.read_text(encoding="utf-8") if HEALTH_TS.exists() else ""
health_js = HEALTH_JS.read_text(encoding="utf-8") if HEALTH_JS.exists() else ""
guards_ts = GUARDS_TS.read_text(encoding="utf-8") if GUARDS_TS.exists() else ""
client_ts = CLIENT_TS.read_text(encoding="utf-8") if CLIENT_TS.exists() else ""

check("panel_exists", PANEL.exists(), str(PANEL))
check("health_ts_exists", HEALTH_TS.exists(), str(HEALTH_TS))
check("health_js_exists", HEALTH_JS.exists(), str(HEALTH_JS))
check("guard_ts_still_exists", GUARDS_TS.exists(), str(GUARDS_TS))
check("client_ts_still_exists", CLIENT_TS.exists(), str(CLIENT_TS))

check("panel_imports_endpoint_health", "../lib/rmc-panel-health" in panel)
check("panel_tracks_endpointHealth_state", "endpointHealth" in panel and "setEndpointHealth" in panel)
check("panel_tracks_lastLoadedAt", "lastLoadedAt" in panel and "setLastLoadedAt" in panel)
check("panel_has_partial_load_guard_section", "UI Endpoint Health / Partial Load Guard" in panel)
check("panel_has_partial_load_error", "Partial RMC UI load" in panel)
check("panel_uses_endpoint_summary", "endpointSummary" in panel and "summarizeEndpointHealth" in panel)
check("panel_isolates_endpoint_failures", "try {" in panel and "catch (err)" in panel and "makeEndpointHealth(key, false" in panel)
check("panel_uses_safe_call_list", "const calls: Array<[keyof PanelData" in panel)
check("panel_no_Promise_all_single_failure_blank", "Promise.all([" not in panel)
check("panel_preserves_p3_guard", "evaluateGuardPromotionArmState" in panel and "canPromote" in panel)
check("panel_preserves_exact_confirmation", "PROMOTE <candidate_id>" in panel)
check("panel_preserves_llm_toggle_default_off", "useState(false)" in panel and "llmEnabled" in panel)
check("panel_no_raw_rmc_fetch", "fetch('/api/rmc" not in panel and 'fetch("/api/rmc' not in panel)
check("panel_no_shell_exec", "exec(" not in panel and "child_process" not in panel)
check("health_ts_exports_makeEndpointHealth", "export function makeEndpointHealth" in health_ts)
check("health_ts_exports_summarizeEndpointHealth", "export function summarizeEndpointHealth" in health_ts)
check("health_js_commonjs_exports", "module.exports" in health_js and "makeEndpointHealth" in health_js)
check("client_preserves_route_manifest", "fetchRouteManifest" in client_ts)
check("guard_preserves_promotion_token", "APPROVE_RMC_PROMOTION" in guards_ts)

node_result = None
try:
    completed = subprocess.run(
        [
            "node",
            "-e",
            f"""
            const h = require({json.dumps(str(HEALTH_JS))});
            const ok = h.makeEndpointHealth('routeManifest', true, null, '2026-01-01T00:00:00Z');
            const bad = h.makeEndpointHealth('promotionStatus', false, 'boom', '2026-01-01T00:00:00Z');
            const summary = h.summarizeEndpointHealth({{ ok, bad }});
            console.log(JSON.stringify({{ ok, bad, summary }}));
            """,
        ],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    node_result = json.loads(completed.stdout)
    check("js_health_helper_executes", True)
    check("js_health_ok_status", node_result["ok"]["status"] == "OK")
    check("js_health_failed_status", node_result["bad"]["status"] == "FAILED")
    check("js_health_summary_counts", node_result["summary"]["total"] == 2 and node_result["summary"]["failed"] == 1 and node_result["summary"]["degraded"] is True)
except Exception as exc:  # noqa: BLE001
    check("js_health_helper_executes", False, repr(exc))

for name, passed, detail in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}{' :: ' + detail if detail else ''}")

failed = [name for name, passed, _ in checks if not passed]
print(f"Total: {len(checks)}")
print(f"Passed: {len(checks) - len(failed)}")
print(f"Failed: {len(failed)}")
if failed:
    print("RESULT: rmc_memory_panel_p4_partial_load_tests_pass=False")
    raise SystemExit(1)
print("RESULT: rmc_memory_panel_p4_partial_load_tests_pass=True")
