#!/usr/bin/env python3
"""Verifier for Patch 262-UI-MemoryPanel-P3R."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "operator_console_src/RmcMemoryTab.tsx",
    "operator_console_src/rmc-api-client.ts",
    "operator_console_src/rmc-api-client.js",
    "operator_console_src/rmc-ui-guards.ts",
    "operator_console_src/rmc-ui-guards.js",
    "operator_console_src/README_patch262_UIMemoryPanelP3R.md",
    "scripts/test_rmc_memory_panel_p3r_gated_actions.py",
    "scripts/patch262_UIMemoryPanelP3R_verify.py",
    "SHA256SUMS.txt",
]
BAD_PATTERNS = ["__pycache__", ".pyc", ".venv", "node_modules", "chroma_db", ".sqlite", ".db"]
passes: list[str] = []
fails: list[str] = []

def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        passes.append(name)
        print(f"[PASS] {name}{' :: ' + detail if detail else ''}")
    else:
        fails.append(name)
        print(f"[FAIL] {name}{' :: ' + detail if detail else ''}")

for rel in REQUIRED:
    check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

sha_path = ROOT / "SHA256SUMS.txt"
sha_text = sha_path.read_text(encoding="utf-8") if sha_path.exists() else ""
check("sha_excludes_bad_artifacts", not any(p in sha_text for p in BAD_PATTERNS))
if sha_path.exists():
    ok = True
    details = []
    for line in sha_text.splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        path = ROOT / rel
        if not path.exists():
            ok = False
            details.append(f"missing:{rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            ok = False
            details.append(f"mismatch:{rel}")
    check("sha_manifest_hashes_ok", ok, ";".join(details[:5]))

panel = (ROOT / "operator_console_src/RmcMemoryTab.tsx").read_text(encoding="utf-8")
guards_ts = (ROOT / "operator_console_src/rmc-ui-guards.ts").read_text(encoding="utf-8")
guards_js = (ROOT / "operator_console_src/rmc-ui-guards.js").read_text(encoding="utf-8")
check("panel_imports_guard_module", "../lib/rmc-ui-guards" in panel)
check("guard_ts_exports_evaluate", "export function evaluatePromotionArmState" in guards_ts)
check("guard_js_commonjs_exports", "module.exports" in guards_js and "export const" not in guards_js and "export function" not in guards_js)
check("promotion_token_exact", "APPROVE_RMC_PROMOTION" in guards_ts and "APPROVE_RMC_PROMOTION" in guards_js)
check("bad_promotion_token_absent", "APPROVE_PROMOTE_MEMORY" not in guards_ts + guards_js + panel)
check("requires_preview_before_promote", "promotion_preview_required" in guards_ts and "promotion_preview_required" in guards_js)
check("requires_exact_confirmation", "exact_confirmation_phrase_required" in guards_ts and "exact_confirmation_phrase_required" in guards_js)
check("requires_preview_candidate_match", "preview_candidate_mismatch" in guards_ts and "preview_candidate_mismatch" in guards_js)
check("blocks_duplicate", "duplicate_promotion_detected" in guards_ts and "duplicate_promotion_detected" in guards_js)
check("blocks_unsafe_paths", "unsafe_paths_present" in guards_ts and "unsafe_paths_present" in guards_js)
check("blocks_missing_fields", "missing_required_fields_present" in guards_ts and "missing_required_fields_present" in guards_js)
check("panel_button_disabled_until_guard_armed", "disabled={!canPromote}" in panel and "promotionArmState.armed" in panel)
check("panel_no_raw_rmc_fetch", "fetch('/api/rmc" not in panel and 'fetch("/api/rmc' not in panel)
check("client_no_shell_exec", "child_process" not in panel + guards_ts + guards_js and "exec(" not in guards_js)

compile_cmd = ["python", "-m", "py_compile", "scripts/test_rmc_memory_panel_p3r_gated_actions.py", "scripts/patch262_UIMemoryPanelP3R_verify.py"]
proc = subprocess.run(compile_cmd, cwd=ROOT, text=True, capture_output=True)
check("py_compile_verify_scripts", proc.returncode == 0, proc.stderr[:200])
proc = subprocess.run(["python", "scripts/test_rmc_memory_panel_p3r_gated_actions.py"], cwd=ROOT, text=True, capture_output=True)
print(proc.stdout, end="")
if proc.stderr:
    print(proc.stderr, end="")
check("behavior_test_passes", proc.returncode == 0)

print("─" * 72)
print(f"Total: {len(passes) + len(fails)}")
print(f"Passed: {len(passes)}")
print(f"Failed: {len(fails)}")
if fails:
    print("RESULT: PATCH_262_UI_MEMORY_PANEL_P3R_VERIFY_OK_FALSE")
    raise SystemExit(1)
print("RESULT: PATCH_262_UI_MEMORY_PANEL_P3R_VERIFY_OK")
