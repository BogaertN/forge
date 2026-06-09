#!/usr/bin/env python3
# Patch 262-UI-MemoryPanel-P2 behavior/static tests.
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path.cwd()
PANEL = ROOT / "operator_console_src" / "RmcMemoryTab.tsx"
CLIENT_TS = ROOT / "operator_console_src" / "rmc-api-client.ts"
CLIENT_JS = ROOT / "operator_console_src" / "rmc-api-client.js"

checks: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))

panel = PANEL.read_text(encoding="utf-8") if PANEL.exists() else ""
client_ts = CLIENT_TS.read_text(encoding="utf-8") if CLIENT_TS.exists() else ""
client_js = CLIENT_JS.read_text(encoding="utf-8") if CLIENT_JS.exists() else ""

check("panel_file_exists", PANEL.exists(), str(PANEL))
check("client_ts_exists", CLIENT_TS.exists(), str(CLIENT_TS))
check("client_js_exists", CLIENT_JS.exists(), str(CLIENT_JS))

required_imports = [
    "fetchRouteManifest",
    "getMemoryStatus",
    "getChromaStatus",
    "getActiveLoopState",
    "getPromotionStatus",
    "getPromotionPreview",
    "getPromotionPromote",
    "getGlyphRendererStatus",
    "getLlmRendererStatus",
    "getOutputRenderer",
    "getPipelineSummary",
    "getDatasetGrowthStatus",
    "getDatasetGrowthCoverage",
]
for token in required_imports:
    check(f"panel_import_or_uses_{token}", token in panel)

required_labels = [
    "RMC Memory Panel Phase 2",
    "Canonical Route Manifest / API Truth",
    "Context Library / Memory Surface",
    "Active Loop State / Session Continuity",
    "Promotion Path / Review Queue",
    "Renderer / Optional Local LLM Toggle",
    "Chroma / Glyph / Dataset Growth Boundaries",
]
for label in required_labels:
    check(f"panel_label_{label[:24]}", label in panel)

check("panel_uses_route_manifest_source_of_truth", "fetchRouteManifest(true)" in panel and "/api/rmc/route-manifest" in panel)
check("panel_no_raw_rmc_fetch", not re.search(r"fetch\s*\(\s*['\"]\/api\/rmc", panel))
check("panel_no_shell_exec", "exec(" not in panel and "child_process" not in panel and "spawn(" not in panel)
check("panel_no_direct_model_authority", "llm_output_is_not_authority" in panel and "does not approve output" in panel)
check("panel_llm_default_off", "useState(false)" in panel and "llm_renderer: llmEnabled ? 'on' : 'off'" in panel)
check("panel_local_model_endpoint_visible", "http://localhost:11434/api/generate" in panel)
check("promotion_exact_token_required", "APPROVE_RMC_PROMOTION" in panel and "promotionApproval === PROMOTION_TOKEN" in panel)
check("bad_promotion_token_absent", "APPROVE_PROMOTE_MEMORY" not in panel and "APPROVE_PROMOTE_MEMORY" not in client_ts)
check("promotion_button_disabled_until_token", "disabled={!canPromote}" in panel)
check("known_backend_gaps_are_labeled_not_faked", "backend route missing" in panel and "context_duplicates" in panel and "context_export_manifest" in panel)

client_exports = [
    "fetchRouteManifest",
    "getCanonicalRmcPath",
    "fetchRmcEndpoint",
    "getMemoryStatus",
    "getChromaStatus",
    "getDatasetGrowthStatus",
    "getDatasetGrowthCoverage",
    "getLlmRendererStatus",
    "getOutputRenderer",
    "getGlyphRendererStatus",
    "getPromotionStatus",
    "getPromotionPreview",
    "getPromotionPromote",
    "promoteCandidate",
]
for token in client_exports:
    check(f"client_ts_export_{token}", token in client_ts)

check("client_ts_uses_route_manifest", "/api/rmc/route-manifest" in client_ts and "routeManifestCache" in client_ts)
check("client_ts_preserves_c16_llm_route", "/api/rmc/llm-renderer/status" in client_ts and "model_endpoint" in client_ts)
check("client_ts_preserves_c12_promotion_token", "APPROVE_RMC_PROMOTION" in client_ts)
check("client_js_compat_exports_promotion", "getPromotionPromote" in client_js and "APPROVE_RMC_PROMOTION" in client_js)
check("client_no_shell_exec", "child_process" not in client_ts + client_js and "exec(" not in client_ts + client_js)

for name, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{' :: ' + detail if detail else ''}")

failed = [name for name, ok, _ in checks if not ok]
if failed:
    print(f"RESULT: rmc_memory_panel_phase2_ui_tests_pass=False failed={failed}")
    sys.exit(1)

print("RESULT: rmc_memory_panel_phase2_ui_tests_pass=True")
