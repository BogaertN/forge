#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT.parent
APP = HOME / "aiweb/apps/forge-operator-console/src"

CHECKS: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(condition), detail))

files = {
    "tab": APP / "tabs/RmcDeepDryRunTab.tsx",
    "app": APP / "App.tsx",
    "types": APP / "api/types.ts",
    "top_tabs": APP / "shell/TopTabs.tsx",
    "client": APP / "lib/rmc-api-client.ts",
    "theme": APP / "styles/theme.css",
}
for key, path in files.items():
    check(f"file_exists_{key}", path.exists(), str(path))

texts = {key: path.read_text(encoding="utf-8") if path.exists() else "" for key, path in files.items()}

tab = texts["tab"]
client = texts["client"]
app = texts["app"]
types = texts["types"]
top_tabs = texts["top_tabs"]

check("tab_registered_type", "'rmc_deep_dry_run'" in types)
check("tab_imported_app", "RmcDeepDryRunTab" in app)
check("tab_rendered_app", "rmc_deep_dry_run: <RmcDeepDryRunTab />" in app)
check("tab_visible_top_tabs", "Deep Dry-Run" in top_tabs and "rmc_deep_dry_run" in top_tabs)
check("route_key_deep_dry_run", "'deep_dry_run'" in client)
check("fallback_deep_dry_run", "deep_dry_run: '/api/rmc/deep-dry-run'" in client)
check("getter_deep_dry_run", "getDeepDryRun" in client)
check("getter_deep_preflight", "getDeepPipelinePreflight" in client)
check("getter_pf2_preview", "getProtoForge2DriftPreview" in client)
check("getter_resurrection", "getResurrectionPreview" in client)
check("panel_calls_deep_dry_run", "getDeepDryRun" in tab)
check("panel_calls_preflight", "getDeepPipelinePreflight" in tab)
check("panel_calls_pf2", "getProtoForge2DriftPreview" in tab)
check("panel_calls_resurrection", "getResurrectionPreview" in tab)
check("panel_route_manifest", "fetchRouteManifest(true)" in tab)
check("panel_read_only_text", "read-only" in tab.lower())
check("panel_forbidden_effects", "forbidden_effect_violations" in tab)
check("panel_stage_list", "StageList" in tab and "16-Stage Dry-Run Trace" in tab)
check("panel_no_raw_fetch", "fetch(" not in tab)
check("panel_no_write_calls", "getPromotionPromote" not in tab and "getGatedMemoryWriter" not in tab and "getMemoryWriter" not in tab)
check("panel_no_llm_call", "getOutputRenderer" not in tab and "model_endpoint" not in tab and "modelEndpoint" not in tab)
check("panel_mentions_identity_vault_block", "Identity Vault" in tab)
check("panel_mentions_no_memory_commit", "commit memory" in tab.lower() or "memory committed" in tab.lower())
check("theme_marker", "Patch 272" in texts["theme"])

# Backend file must still compile; route must already exist from Patch 271.
main_py = ROOT / "main.py"
check("main_py_exists", main_py.exists(), str(main_py))
try:
    ast.parse(main_py.read_text(encoding="utf-8"))
    check("main_py_ast_compiles", True)
except SyntaxError as exc:
    check("main_py_ast_compiles", False, str(exc))

# Staging copies exist.
staging = ROOT / "operator_console_src"
check("staging_tab_exists", (staging / "RmcDeepDryRunTab.tsx").exists())
check("staging_client_exists", (staging / "rmc-api-client.ts").exists())

failed = [item for item in CHECKS if not item[1]]
print("PATCH 272 VERIFY")
print("─" * 60)
for name, ok, detail in CHECKS:
    mark = "✓ [PASS]" if ok else "✗ [FAIL]"
    suffix = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{suffix}")
print("─" * 60)
print(f"  Total: {len(CHECKS)}  Passed: {len(CHECKS)-len(failed)}  Failed: {len(failed)}")
print()
if failed:
    print("RESULT: PATCH_272_VERIFY_FAIL")
    sys.exit(1)
print("RESULT: PATCH_272_VERIFY_OK")
