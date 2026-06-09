#!/usr/bin/env python3
"""Static endpoint/UI contract tests for Patch 262J1R-Preflight-B5."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")

checks = []

def add(name: str, condition: bool, detail: str = ""):
    checks.append((name, condition, detail))

for path in [
    "/api/rmc/dataset-growth/status",
    "/api/rmc/dataset-growth/capture-preview",
    "/api/rmc/dataset-growth/capture",
    "/api/rmc/dataset-growth/coverage",
]:
    add(f"endpoint_registered_{path}", path in MAIN)

add("adapter_status_exists", "def _p262b5_rmc_dataset_growth_status_v1" in MAIN)
add("adapter_preview_exists", "def _p262b5_rmc_dataset_growth_capture_preview_v1" in MAIN)
add("adapter_capture_exists", "def _p262b5_rmc_dataset_growth_capture_v1" in MAIN)
add("adapter_coverage_exists", "def _p262b5_rmc_dataset_growth_coverage_v1" in MAIN)
add("ui_output_slot_present", "rmc_dataset_growth_slot" in MAIN)
add("ui_mentions_dataset_root", "/home/nic/forge/memory/rmc_dataset_v1" in MAIN)
add("route_capture_dispatch_present", '_p249_req_path == "/api/rmc/dataset-growth/capture"' in MAIN)
add("normal_runtime_reference_mutation_denied", "canonical reference files are never mutated" in MAIN)

passed = 0
failed = 0
for name, condition, detail in checks:
    if condition:
        passed += 1
        print(f"✓ {name} {detail}".rstrip())
    else:
        failed += 1
        print(f"✗ {name} {detail}".rstrip())

print(f"Total: {passed + failed}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
if failed:
    raise SystemExit(1)
print("RESULT: dataset_growth_B5_endpoint_contract_tests_pass=True")
