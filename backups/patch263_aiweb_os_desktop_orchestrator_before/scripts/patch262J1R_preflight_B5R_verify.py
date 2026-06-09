#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B5R — Dataset Growth Route Repair."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
checks: list[tuple[str, bool, str]] = []

def add(name: str, cond: bool, detail: str = "") -> None:
    checks.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))

def run(script: str, timeout: int = 90) -> tuple[bool, str]:
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return p.returncode == 0, (p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "")

print("PATCH 262J1R-PREFLIGHT-B5R VERIFY")
print("─" * 72)
for rel in [
    "main.py",
    "rmc_engine_v1/dataset_growth.py",
    "scripts/test_rmc_dataset_growth_route_refusals_B5R.py",
]:
    add("file_exists_" + rel.replace("/", "_"), (ROOT / rel).exists(), rel)

main_text = (ROOT / "main.py").read_text(encoding="utf-8")
add("main_has_b5r_comment", "Patch 262J1R-Preflight-B5R" in main_text)
add("main_local_urlparse_import_present", main_text.count("import urllib.parse as _pp_url") >= 2)
add("main_capture_route_present", "/api/rmc/dataset-growth/capture" in main_text)
add("main_llm_turn_routes_present", "/api/rmc/dataset-growth/llm-turn-preview" in main_text and "/api/rmc/dataset-growth/llm-turn-capture" in main_text)
add("main_document_routes_present", "/api/rmc/dataset-growth/document-preview" in main_text and "/api/rmc/dataset-growth/document-capture" in main_text)

for script in [
    "test_rmc_dataset_growth_route_refusals_B5R.py",
    "test_rmc_dataset_growth_behavior.py",
    "test_rmc_dataset_growth_endpoint_contract.py",
    "test_rmc_dataset_growth_live_hooks.py",
    "test_rmc_dataset_growth_endpoint_contract_B5A.py",
    "test_rmc_lexicon_production_coverage.py",
    "test_rmc_drift_engine_behavior.py",
    "test_rmc_phase_parser_behavior.py",
    "test_rmc_coherence_math_behavior.py",
]:
    ok, last = run(script)
    add(script + "_passes", ok, last)

print("─" * 72)
passed = sum(1 for _, ok, _ in checks if ok)
print(f"Total: {len(checks)}")
print(f"Passed: {passed}")
print(f"Failed: {len(checks)-passed}")
if passed != len(checks):
    raise SystemExit(1)
print("RESULT: PATCH_262J1R_PREFLIGHT_B5R_VERIFY_OK")
