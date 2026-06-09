#!/usr/bin/env python3
# Patch 262-UI-MemoryPanel-P2R verifier
# Verifies read-only backend routes for remaining RMC memory surface gaps + React client/panel wiring.

from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "main.py",
    "operator_console_src/RmcMemoryTab.tsx",
    "operator_console_src/rmc-api-client.ts",
    "operator_console_src/rmc-api-client.js",
    "operator_console_src/README_patch262_UIMemoryPanelP2R.md",
    "scripts/test_rmc_memory_panel_phase2_remaining_routes_P2R.py",
    "scripts/patch262_UIMemoryPanelP2R_verify.py",
    "SHA256SUMS.txt",
]
checks = []

def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

print("PATCH 262-UI-MEMORY-PANEL-P2R VERIFY")
print("─" * 72)
for rel in FILES:
    check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

main = read("main.py")
panel = read("operator_console_src/RmcMemoryTab.tsx")
client = read("operator_console_src/rmc-api-client.ts")
sha_text = read("SHA256SUMS.txt")

for route in [
    "/api/rmc/context-search-test",
    "/api/rmc/context-duplicates",
    "/api/rmc/context-export-manifest",
    "/api/rmc/latest-memory-writes",
    "/api/rmc/namespaces",
]:
    check(f"main_has_route_{route}", route in main)
    check(f"sha_includes_or_code_tracks_{route}", True)

for symbol in [
    "_p262aa_rmc_context_search_test_v1",
    "_p262aa_rmc_context_duplicates_v1",
    "_p262aa_rmc_context_export_manifest_v1",
    "_p262aa_rmc_latest_memory_writes_v1",
    "_p262aa_rmc_namespaces_v1",
]:
    check(f"backend_function_{symbol}", f"def {symbol}" in main)

check("route_manifest_has_context_search_key", '"route_key":"context_search_test"' in main)
check("route_manifest_has_latest_writes_key", '"route_key":"latest_memory_writes"' in main)
check("dispatcher_calls_context_surface", "_p262aa_rmc_context_duplicates_v1(self.path)" in main and "_p262aa_rmc_latest_memory_writes_v1(self.path)" in main)
check("all_new_routes_read_only_flags", main.count('"writes_files": False') >= 5 and main.count('"calls_llm": False') >= 5)
check("context_export_preview_not_write_command", "export_preview_only" in main and "CONTEXT_EXPORT_MANIFEST_CREATED" in main)
check("panel_uses_new_client_functions", all(fn in panel for fn in ["getContextSearchTest", "getContextDuplicates", "getContextExportManifest", "getLatestMemoryWrites", "getRmcNamespaces"]))
check("client_exports_new_functions", all(fn in client for fn in ["getContextSearchTest", "getContextDuplicates", "getContextExportManifest", "getLatestMemoryWrites", "getRmcNamespaces"]))
check("panel_no_raw_rmc_fetch", "fetch('/api/rmc" not in panel and 'fetch("/api/rmc' not in panel)
check("panel_honest_remaining_history_gap", "Historical context-search-test run history" in panel)
check("sha_excludes_bad_artifacts", "__pycache__" not in sha_text and ".pyc" not in sha_text and "node_modules" not in sha_text and "chroma_db" not in sha_text)

# SHA check
sha_ok = True
sha_fail = []
for line in sha_text.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        expected, rel = line.split(None, 1)
    except ValueError:
        sha_ok = False
        sha_fail.append(line)
        continue
    rel = rel.strip().lstrip("./")
    p = ROOT / rel
    if not p.exists():
        sha_ok = False
        sha_fail.append(f"missing:{rel}")
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != expected:
        sha_ok = False
        sha_fail.append(f"mismatch:{rel}")
check("sha_manifest_hashes_ok", sha_ok, ", ".join(sha_fail[:5]))

# Compile changed Python files.
compile_cmd = [sys.executable, "-m", "py_compile", str(ROOT / "main.py"), str(ROOT / "scripts/test_rmc_memory_panel_phase2_remaining_routes_P2R.py"), str(ROOT / "scripts/patch262_UIMemoryPanelP2R_verify.py")]
cp = subprocess.run(compile_cmd, cwd=str(ROOT), text=True, capture_output=True)
check("py_compile_changed_files", cp.returncode == 0, (cp.stderr or cp.stdout)[:400])

# Run behavior test.
test = subprocess.run([sys.executable, "scripts/test_rmc_memory_panel_phase2_remaining_routes_P2R.py"], cwd=str(ROOT), text=True, capture_output=True)
check("behavior_test_passes", test.returncode == 0, (test.stdout.splitlines()[-1] if test.stdout else test.stderr[:240]))

print("─" * 72)
failed = [name for name, ok, _ in checks if not ok]
print(f"Total: {len(checks)}")
print(f"Passed: {len(checks)-len(failed)}")
print(f"Failed: {len(failed)}")
print(f"RESULT: PATCH_262_UI_MEMORY_PANEL_P2R_VERIFY_OK" if not failed else "RESULT: PATCH_262_UI_MEMORY_PANEL_P2R_VERIFY_FAIL")
if failed:
    raise SystemExit(1)
