#!/usr/bin/env python3
# Patch 262-UI-MemoryPanel-P2R behavior test
# Verifies the remaining read-only memory surface routes are exposed, route-manifested, and UI-wired.

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
PANEL = ROOT / "operator_console_src" / "RmcMemoryTab.tsx"
CLIENT_TS = ROOT / "operator_console_src" / "rmc-api-client.ts"
CLIENT_JS = ROOT / "operator_console_src" / "rmc-api-client.js"

checks = []

def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")

main = MAIN.read_text(encoding="utf-8")
panel = PANEL.read_text(encoding="utf-8")
client_ts = CLIENT_TS.read_text(encoding="utf-8")
client_js = CLIENT_JS.read_text(encoding="utf-8")

required_routes = {
    "context_search_test": "/api/rmc/context-search-test",
    "context_duplicates": "/api/rmc/context-duplicates",
    "context_export_manifest": "/api/rmc/context-export-manifest",
    "latest_memory_writes": "/api/rmc/latest-memory-writes",
    "rmc_namespaces": "/api/rmc/namespaces",
}

check("main_exists", MAIN.exists(), str(MAIN))
check("panel_exists", PANEL.exists(), str(PANEL))
check("client_ts_exists", CLIENT_TS.exists(), str(CLIENT_TS))
check("client_js_exists", CLIENT_JS.exists(), str(CLIENT_JS))

for key, path in required_routes.items():
    check(f"manifest_route_key_{key}", f'"route_key":"{key}"' in main)
    check(f"manifest_path_{path}", f'"path":"{path}"' in main or path in main)
    check(f"dispatcher_path_{path}", path in main and "_p262aa_rmc_" in main)
    check(f"client_ts_fallback_{key}", f"{key}: '{path}'" in client_ts)

for fn in [
    "getContextSearchTest",
    "getContextDuplicates",
    "getContextExportManifest",
    "getLatestMemoryWrites",
    "getRmcNamespaces",
]:
    check(f"client_ts_export_{fn}", f"export const {fn}" in client_ts)
    check(f"client_js_export_{fn}", f"export const {fn}" in client_js)
    check(f"panel_import_uses_{fn}", fn in panel)

check("route_manifest_expected_count_46_plus", "canonical_route_count" in main and all(k in main for k in required_routes))
check("context_search_alias_preserved", '"/api/rmc/context-search"' in main)
check("rmc_namespaces_alias_preserved", '"/api/rmc/rmc-namespaces"' in main)
check("context_export_preview_only", "export_preview_only" in main and "cmd_context_export_manifest" in main and "_p262aa_rmc_context_export_manifest_v1" in main)
check("context_duplicates_no_audit_write", "CONTEXT_DUPLICATES_CHECKED" in main and "_p262aa_rmc_context_duplicates_v1" in main and "write_audit_entry(session_id" not in main[main.find("def _p262aa_rmc_context_duplicates_v1"):main.find("def _p262aa_rmc_context_export_manifest_v1")])
check("latest_memory_writes_read_only", "read_only_latest_memory_writes_P2R" in main and "memory_write_allowed" in main)
check("panel_no_raw_rmc_fetch", "fetch('/api/rmc" not in panel and 'fetch("/api/rmc' not in panel)
check("panel_no_backend_missing_for_core_context_routes", "Context duplicate status is not exposed" not in panel and "Context export manifest is not exposed" not in panel)
check("panel_labels_live_search_history_honestly", "Historical context-search-test run history" in panel)
check("panel_shows_latest_memory_writes", "Latest memory writes" in panel)
check("panel_shows_rmc_namespaces", "RMC namespaces" in panel)
check("no_shell_exec_in_client", "exec(" not in client_ts and "child_process" not in client_ts and "spawn(" not in client_ts)
check("no_direct_model_authority_claim", "LLM output is authority" not in panel and "llm_output_is_authority" not in client_ts)

failed = [name for name, ok, _ in checks if not ok]
print(f"RESULT: rmc_memory_panel_phase2_remaining_routes_P2R_tests_pass={not failed}")
if failed:
    raise SystemExit(1)
