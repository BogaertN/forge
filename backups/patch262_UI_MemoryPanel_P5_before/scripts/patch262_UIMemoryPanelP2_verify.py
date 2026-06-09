#!/usr/bin/env python3
# Patch 262-UI-MemoryPanel-P2 verifier.
from __future__ import annotations

import hashlib
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
REQUIRED = [
    "operator_console_src/RmcMemoryTab.tsx",
    "operator_console_src/rmc-api-client.ts",
    "operator_console_src/rmc-api-client.js",
    "operator_console_src/README_patch262_UIMemoryPanelP2.md",
    "scripts/test_rmc_memory_panel_phase2_ui.py",
    "scripts/patch262_UIMemoryPanelP2_verify.py",
    "SHA256SUMS.txt",
]

checks: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))

for rel in REQUIRED:
    check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

sha_file = ROOT / "SHA256SUMS.txt"
if sha_file.exists():
    bad_sha = any(token in sha_file.read_text(encoding="utf-8") for token in ["__pycache__", ".pyc", "node_modules", ".venv", "chroma_db", ".db"])
    check("sha_excludes_bad_artifacts", not bad_sha)
    all_ok = True
    for line in sha_file.read_text(encoding="utf-8").splitlines():
      if not line.strip():
        continue
      expected, rel = line.split(maxsplit=1)
      rel = rel.strip().lstrip("*")
      target = ROOT / rel
      if not target.exists():
        all_ok = False
        break
      actual = hashlib.sha256(target.read_bytes()).hexdigest()
      if actual != expected:
        all_ok = False
        break
    check("sha_manifest_hashes_ok", all_ok)

try:
    py_compile.compile(str(ROOT / "scripts/test_rmc_memory_panel_phase2_ui.py"), doraise=True)
    py_compile.compile(str(ROOT / "scripts/patch262_UIMemoryPanelP2_verify.py"), doraise=True)
    check("py_compile_verify_scripts", True)
except Exception as exc:
    check("py_compile_verify_scripts", False, str(exc))

proc = subprocess.run([sys.executable, "scripts/test_rmc_memory_panel_phase2_ui.py"], cwd=ROOT, text=True, capture_output=True)
check("scripts_test_rmc_memory_panel_phase2_ui_py_passes", proc.returncode == 0, (proc.stdout + proc.stderr).strip().splitlines()[-1] if (proc.stdout + proc.stderr).strip() else "")

panel = (ROOT / "operator_console_src/RmcMemoryTab.tsx").read_text(encoding="utf-8") if (ROOT / "operator_console_src/RmcMemoryTab.tsx").exists() else ""
client = (ROOT / "operator_console_src/rmc-api-client.ts").read_text(encoding="utf-8") if (ROOT / "operator_console_src/rmc-api-client.ts").exists() else ""
check("panel_declares_control_surface_only", "control surface only" in panel)
check("panel_uses_canonical_client", "../lib/rmc-api-client" in panel)
check("panel_no_raw_fetch", "fetch('/api/rmc" not in panel and 'fetch("/api/rmc' not in panel)
check("client_route_manifest_cache", "routeManifestCache" in client)
check("client_promote_requires_approval_arg", "getPromotionPromote = (candidateId: string, approval: string)" in client)

for name, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{' :: ' + detail if detail else ''}")

failed = [name for name, ok, _ in checks if not ok]
print("────────────────────────────────────────────────────────────────────────")
print(f"Total: {len(checks)}")
print(f"Passed: {len(checks) - len(failed)}")
print(f"Failed: {len(failed)}")
if failed:
    print(f"RESULT: PATCH_262_UI_MEMORY_PANEL_P2_VERIFY_FAIL failed={failed}")
    sys.exit(1)
print("RESULT: PATCH_262_UI_MEMORY_PANEL_P2_VERIFY_OK")
