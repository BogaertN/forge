#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "operator_console_src" / "RmcMemoryTab.tsx"
PRIMS = ROOT / "operator_console_src" / "rmc-panel-primitives.tsx"
GUARDS = ROOT / "operator_console_src" / "rmc-ui-guards.ts"
HEALTH = ROOT / "operator_console_src" / "rmc-panel-health.ts"
CLIENT = ROOT / "operator_console_src" / "rmc-api-client.ts"

checks: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, condition, detail))
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")

panel = PANEL.read_text(encoding="utf-8") if PANEL.exists() else ""
prims = PRIMS.read_text(encoding="utf-8") if PRIMS.exists() else ""
guards = GUARDS.read_text(encoding="utf-8") if GUARDS.exists() else ""
health = HEALTH.read_text(encoding="utf-8") if HEALTH.exists() else ""
client = CLIENT.read_text(encoding="utf-8") if CLIENT.exists() else ""

check("panel_exists", PANEL.exists(), str(PANEL))
check("primitives_exists", PRIMS.exists(), str(PRIMS))
check("guards_still_exists", GUARDS.exists(), str(GUARDS))
check("health_still_exists", HEALTH.exists(), str(HEALTH))
check("client_still_exists", CLIENT.exists(), str(CLIENT))

required_exports = [
    "JsonRecord",
    "asText",
    "jsonPreview",
    "getPath",
    "statusClass",
    "Metric",
    "Section",
    "JsonDetails",
    "DirectoryList",
    "RouteAvailability",
    "ReviewQueueList",
]
for symbol in required_exports:
    check(f"primitive_export_{symbol}", re.search(rf"export (function|type) {re.escape(symbol)}\b", prims) is not None)

check("panel_imports_primitives", "../lib/rmc-panel-primitives" in panel)
for symbol in ["Metric", "Section", "JsonDetails", "DirectoryList", "RouteAvailability", "ReviewQueueList", "getPath"]:
    check(f"panel_uses_{symbol}", symbol in panel)

for forbidden in [
    "function asText",
    "function jsonPreview",
    "function statusClass",
    "function Metric",
    "function Section",
    "function JsonDetails",
    "function DirectoryList",
    "function RouteAvailability",
    "function ReviewQueueList",
]:
    check(f"panel_no_inline_{forbidden.replace(' ', '_')}", forbidden not in panel)

check("panel_preserves_p4_endpoint_health", "UI Endpoint Health / Partial Load Guard" in panel and "summarizeEndpointHealth" in panel)
check("panel_preserves_p3_promotion_guard", "evaluateGuardPromotionArmState" in panel and "PROMOTE <candidate_id>" in panel)
check("panel_preserves_llm_default_off", "useState(false)" in panel and "Enable optional local LLM draft" in panel)
check("panel_preserves_route_manifest", "fetchRouteManifest(true)" in panel)
check("panel_no_raw_rmc_fetch", "fetch(\'/api/rmc" not in panel and "fetch(\"/api/rmc" not in panel)
check("panel_no_shell_exec", not re.search(r"exec\s*\(|spawn\s*\(|child_process|rm -rf|curl\s", panel))
check("primitives_no_network", not re.search(r"fetch\s*\(|XMLHttpRequest|axios", prims))
check("primitives_no_shell_exec", not re.search(r"exec\s*\(|spawn\s*\(|child_process|rm -rf|curl\s", prims))
check("primitives_no_promotion_write_call", "getPromotionPromote" not in prims and "APPROVE_RMC_PROMOTION" not in prims)
check("guard_preserves_exact_token", "APPROVE_RMC_PROMOTION" in guards and "APPROVE_PROMOTE_MEMORY" not in guards)
check("health_preserves_partial_load", "makeEndpointHealth" in health and "summarizeEndpointHealth" in health)
check("client_preserves_route_manifest", "fetchRouteManifest" in client and "getCanonicalRmcPath" in client)

failed = [name for name, ok, _ in checks if not ok]
print(f"Total: {len(checks)}")
print(f"Passed: {len(checks)-len(failed)}")
print(f"Failed: {len(failed)}")
if failed:
    print("FAILED_CHECKS:", ", ".join(failed))
    print("RESULT: rmc_memory_panel_p5_component_split_tests_pass=False")
    raise SystemExit(1)
print("RESULT: rmc_memory_panel_p5_component_split_tests_pass=True")
