#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B5.

Checks dataset growth module, endpoint/UI wiring, and previous RMC guards.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

checks: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, ok, detail))


def run_script(rel: str, expect: str) -> None:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, capture_output=True, timeout=120)
    output = (proc.stdout or "") + (proc.stderr or "")
    add(f"{rel}_passes", proc.returncode == 0 and expect in output, output.strip().splitlines()[-1] if output.strip().splitlines() else "no output")

required_files = [
    "rmc_engine_v1/dataset_growth.py",
    "scripts/README_patch262J1R_preflight_B5.md",
    "scripts/test_rmc_dataset_growth_behavior.py",
    "scripts/test_rmc_dataset_growth_endpoint_contract.py",
]
for rel in required_files:
    add(f"file_exists_{rel.replace('/', '_')}", (ROOT / rel).exists(), rel)

try:
    dg = importlib.import_module("rmc_engine_v1.dataset_growth")
    add("dataset_growth_importable", True)
    boundary = dg.dataset_growth_boundary()
    add("dataset_growth_no_llm", boundary.get("calls_llm") is False, str(boundary))
    add("dataset_growth_no_chroma", boundary.get("queries_chroma") is False, str(boundary))
    add("dataset_growth_reference_write_blocked", boundary.get("canonical_reference_write_allowed") is False, str(boundary))
    add("dataset_growth_gold_mutation_blocked", boundary.get("normal_runtime_gold_mutation_allowed") is False, str(boundary))
    add("dataset_growth_declares_capture_approval", boundary.get("required_capture_approval") == "CAPTURE_RMC_DATASET_OBSERVATION", str(boundary))
    add("dataset_growth_declares_queue_approval", boundary.get("required_capture_and_queue_approval") == "CAPTURE_AND_QUEUE_RMC_DATASET_CANDIDATE", str(boundary))
    status = dg.dataset_growth_status()
    add("dataset_growth_status_ok", status.get("status") == "OK", str(status.get("growth_law")))
    add("dataset_growth_has_growth_law", status.get("growth_law", {}).get("raw_input_never_becomes") == "gold_truth_directly", str(status.get("growth_law")))
    preview = dg.capture_preview("Bypass correction and naming and project now.")
    add("capture_preview_ok", preview.get("status") == "OK", str(preview.get("candidate_target_dataset")))
    add("capture_preview_no_write", preview.get("writes_files") is False, str(preview.get("planned_paths")))
    refused = dg.capture_observation("test", approval=None)
    add("capture_requires_approval", refused.get("status") == "REFUSED", str(refused))
except Exception as exc:
    add("dataset_growth_importable", False, repr(exc))

main_text = (ROOT / "main.py").read_text(encoding="utf-8")
for path in [
    "/api/rmc/dataset-growth/status",
    "/api/rmc/dataset-growth/capture-preview",
    "/api/rmc/dataset-growth/capture",
    "/api/rmc/dataset-growth/coverage",
]:
    add(f"main_py_has_{path}", path in main_text)
add("main_py_has_dataset_growth_slot", "rmc_dataset_growth_slot" in main_text)
add("main_py_imports_dataset_growth_module", "from rmc_engine_v1.dataset_growth" in main_text)

run_script("scripts/test_rmc_dataset_growth_behavior.py", "RESULT: dataset_growth_B5_behavior_tests_pass=True")
run_script("scripts/test_rmc_dataset_growth_endpoint_contract.py", "RESULT: dataset_growth_B5_endpoint_contract_tests_pass=True")
run_script("scripts/test_rmc_lexicon_production_coverage.py", "RESULT: lexicon_production_coverage_B4_tests_pass=True")
run_script("scripts/test_rmc_expanded_gold_reference_behavior.py", "RESULT: expanded_gold_reference_B4_behavior_tests_pass=True")
run_script("scripts/test_rmc_resonance_codex_integration.py", "RESULT: resonance_codex_B3_integration_tests_pass=True")
run_script("scripts/test_rmc_resonance_lexicon_behavior.py", "RESULT: resonance_lexicon_B2_behavior_tests_pass=True")
run_script("scripts/test_rmc_gold_reference_behavior.py", "RESULT: gold_reference_B2_behavior_tests_pass=True")
run_script("scripts/test_rmc_drift_engine_behavior.py", "RESULT: drift_engine_B1_behavior_tests_pass=True")
run_script("scripts/test_rmc_phase_parser_behavior.py", "RESULT: phase_parser_behavior_tests_pass=True")
run_script("scripts/test_rmc_coherence_math_behavior.py", "RESULT: coherence_math_behavior_tests_pass=True")

print("\nPATCH 262J1R-PREFLIGHT-B5 VERIFY")
print("─" * 72)
passed = 0
failed = 0
for name, ok, detail in checks:
    if ok:
        passed += 1
        print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
print("─" * 72)
print(f"Total: {passed + failed}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
if failed:
    raise SystemExit(1)
print("RESULT: PATCH_262J1R_PREFLIGHT_B5_VERIFY_OK")
