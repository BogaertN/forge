#!/usr/bin/env python3
"""Verifier for Patch 262-UI-MemoryPanel-P4."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "operator_console_src/RmcMemoryTab.tsx",
    "operator_console_src/rmc-api-client.ts",
    "operator_console_src/rmc-api-client.js",
    "operator_console_src/rmc-ui-guards.ts",
    "operator_console_src/rmc-ui-guards.js",
    "operator_console_src/rmc-panel-health.ts",
    "operator_console_src/rmc-panel-health.js",
    "operator_console_src/README_patch262_UIMemoryPanelP4.md",
    "scripts/test_rmc_memory_panel_p4_partial_load.py",
    "scripts/patch262_UIMemoryPanelP4_verify.py",
    "SHA256SUMS.txt",
]

checks: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))

for rel in REQUIRED:
    check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

sha_file = ROOT / "SHA256SUMS.txt"
sha_text = sha_file.read_text(encoding="utf-8") if sha_file.exists() else ""
check("sha_excludes_bad_artifacts", all(bad not in sha_text for bad in ["__pycache__", ".pyc", ".venv", "node_modules", "chroma_db", ".sqlite", ".db"]))

try:
    completed = subprocess.run(["sha256sum", "-c", "SHA256SUMS.txt"], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    check("sha_manifest_hashes_ok", True, completed.stdout.splitlines()[-1] if completed.stdout else "")
except subprocess.CalledProcessError as exc:
    check("sha_manifest_hashes_ok", False, exc.stdout)

panel = (ROOT / "operator_console_src/RmcMemoryTab.tsx").read_text(encoding="utf-8") if (ROOT / "operator_console_src/RmcMemoryTab.tsx").exists() else ""
health_ts = (ROOT / "operator_console_src/rmc-panel-health.ts").read_text(encoding="utf-8") if (ROOT / "operator_console_src/rmc-panel-health.ts").exists() else ""
health_js = (ROOT / "operator_console_src/rmc-panel-health.js").read_text(encoding="utf-8") if (ROOT / "operator_console_src/rmc-panel-health.js").exists() else ""

check("panel_imports_health_module", "../lib/rmc-panel-health" in panel)
check("panel_has_endpoint_health_section", "UI Endpoint Health / Partial Load Guard" in panel)
check("panel_has_partial_load_failure_isolation", "Partial RMC UI load" in panel and "makeEndpointHealth(key, false" in panel)
check("panel_preserves_promotion_guard", "evaluateGuardPromotionArmState" in panel and "PROMOTION_TOKEN" in panel)
check("health_ts_no_network_or_writes", all(token not in health_ts for token in ["fetch(", "XMLHttpRequest", "localStorage", "exec(", "child_process"] ))
check("health_js_commonjs", "module.exports" in health_js)

try:
    subprocess.run([sys.executable, "-m", "py_compile", "scripts/test_rmc_memory_panel_p4_partial_load.py", "scripts/patch262_UIMemoryPanelP4_verify.py"], cwd=str(ROOT), text=True, check=True)
    check("py_compile_verify_scripts", True)
except subprocess.CalledProcessError as exc:
    check("py_compile_verify_scripts", False, str(exc))

try:
    completed = subprocess.run([sys.executable, "scripts/test_rmc_memory_panel_p4_partial_load.py"], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    check("behavior_test_passes", "RESULT: rmc_memory_panel_p4_partial_load_tests_pass=True" in completed.stdout, completed.stdout.splitlines()[-1] if completed.stdout else "")
except subprocess.CalledProcessError as exc:
    check("behavior_test_passes", False, exc.stdout)

for name, passed, detail in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}{' :: ' + detail if detail else ''}")

failed = [name for name, passed, _ in checks if not passed]
print("────────────────────────────────────────────────────────────────────────")
print(f"Total: {len(checks)}")
print(f"Passed: {len(checks) - len(failed)}")
print(f"Failed: {len(failed)}")
if failed:
    print("RESULT: PATCH_262_UI_MEMORY_PANEL_P4_VERIFY_OK_FALSE")
    raise SystemExit(1)
print("RESULT: PATCH_262_UI_MEMORY_PANEL_P4_VERIFY_OK")
