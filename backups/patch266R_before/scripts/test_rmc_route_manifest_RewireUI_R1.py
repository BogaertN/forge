#!/usr/bin/env python3
"""Patch 262-RewireUI-R1 behavior checks.

Static contract checks only: verifies backend route discovery and React client wiring
without starting Forge, querying Chroma, calling an LLM, or writing memory.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
CLIENT_TS = ROOT / "operator_console_src" / "rmc-api-client.ts"
CLIENT_JS = ROOT / "operator_console_src" / "rmc-api-client.js"

REQUIRED_CANONICAL = [
    "/api/rmc/route-manifest",
    "/api/rmc/chroma-status",
    "/api/rmc/memory-recaller",
    "/api/rmc/trace-spine",
    "/api/rmc/phase-parser",
    "/api/rmc/drift-analyzer",
    "/api/rmc/candidate-conclusion",
    "/api/rmc/evolutionary-drift-explorer",
    "/api/rmc/coherence-scorer",
    "/api/rmc/correction-naming",
    "/api/rmc/manifest-compiler",
    "/api/rmc/llm-renderer/status",
    "/api/rmc/output-renderer",
    "/api/rmc/glyph-renderer/status",
    "/api/rmc/phase-glyph",
    "/api/rmc/glyph-packet",
    "/api/rmc/echo-validator",
    "/api/rmc/memory-writer",
    "/api/rmc/gated-memory-writer",
    "/api/rmc/pipeline-summary",
    "/api/rmc/active-loop-state",
    "/api/rmc/promotion-path/status",
    "/api/rmc/promotion-path/preview",
    "/api/rmc/promotion-path/promote",
]

REQUIRED_CLIENT_EXPORTS = [
    "fetchRouteManifest",
    "getCanonicalRmcPath",
    "fetchRmcEndpoint",
    "getLlmRendererStatus",
    "getOutputRenderer",
    "getGlyphRendererStatus",
    "getPhaseGlyph",
    "getGlyphPacket",
    "getPromotionStatus",
    "getPromotionPreview",
    "useRmcPipeline",
    "useActiveLoopState",
]

failures = []

def check(name, condition, detail=""):
    if condition:
        print(f"[PASS] {name}{(' :: ' + detail) if detail else ''}")
    else:
        print(f"[FAIL] {name}{(' :: ' + detail) if detail else ''}")
        failures.append(name)

main = MAIN.read_text(encoding="utf-8") if MAIN.exists() else ""
client = CLIENT_TS.read_text(encoding="utf-8") if CLIENT_TS.exists() else ""
client_js = CLIENT_JS.read_text(encoding="utf-8") if CLIENT_JS.exists() else ""

check("main_exists", MAIN.exists(), str(MAIN))
check("client_ts_exists", CLIENT_TS.exists(), str(CLIENT_TS))
check("client_js_exists", CLIENT_JS.exists(), str(CLIENT_JS))
check("route_manifest_helper_present", "_p262z_rmc_route_manifest_entries_v1" in main and "_p262z_rmc_route_manifest_v1" in main)
check("operator_contract_uses_route_manifest_entries", "_p262z_rmc_route_manifest_entries_v1()" in main and "canonical_rmc_route_count" in main)
check("route_manifest_dispatch_present", 'elif _p249_req_path == "/api/rmc/route-manifest"' in main and "_p262z_rmc_route_manifest_v1()" in main)
check("route_manifest_before_forge_status", main.find('/api/rmc/route-manifest') < main.find('/api/forge/status') if '/api/forge/status' in main else False)

route_entries = re.findall(r'"route_key"\s*:\s*"([^"]+)"', main)
check("route_manifest_has_38_plus_canonical_entries", len(set(route_entries)) >= 38, f"found={len(set(route_entries))}")

for path in REQUIRED_CANONICAL:
    check(f"canonical_path_present_{path}", path in main)

check("llm_renderer_c16_preserved", "/api/rmc/llm-renderer/status" in main and "llm_renderer" in main and "model_endpoint" in main)
check("glyph_c14_routes_preserved", "/api/rmc/glyph-renderer/status" in main and "/api/rmc/phase-glyph" in main and "/api/rmc/glyph-packet" in main)
check("promotion_token_correct", "APPROVE_RMC_PROMOTION" in main)
check("bad_promotion_token_absent", "APPROVE_PROMOTE_MEMORY" not in main)
check("memory_write_token_preserved", "APPROVE_RMC_MEMORY_WRITE" in main)
check("route_manifest_boundary_read_only", "read_only_canonical_route_discovery" in main and '"writes_files": False' in main)

for exported in REQUIRED_CLIENT_EXPORTS:
    check(f"client_export_{exported}", f"function {exported}" in client or f"const {exported}" in client or f"export const {exported}" in client or f"export async function {exported}" in client)

check("client_fetches_route_manifest", "fetchRouteManifest" in client and "/api/rmc/route-manifest" in client)
check("client_caches_manifest", "routeManifestCache" in client)
check("client_has_local_llm_params", "llm_renderer" in client and "model_endpoint" in client and "model" in client)
check("client_has_c16_llm_route", "/api/rmc/llm-renderer/status" in client)
check("client_has_c14_glyph_routes", "/api/rmc/glyph-renderer/status" in client and "/api/rmc/phase-glyph" in client and "/api/rmc/glyph-packet" in client)
check("client_has_c12_promotion_routes", "/api/rmc/promotion-path/status" in client and "APPROVE_RMC_PROMOTION" in main)
check("client_js_compat_present", "fetchRouteManifest" in client_js and "getOutputRenderer" in client_js)
check("no_direct_model_authority_claim", "llm_output_is_authority" not in client)
check("no_shell_exec_in_client", "exec(" not in client and "child_process" not in client)

if failures:
    print(f"RESULT: rewireui_R1_behavior_tests_pass=False failures={len(failures)}")
    sys.exit(1)
print("RESULT: rewireui_R1_behavior_tests_pass=True")
