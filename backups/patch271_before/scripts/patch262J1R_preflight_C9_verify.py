#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C9."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

checks: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, bool(ok), detail))


def run_script(rel: str, expected: str) -> tuple[bool, str]:
    path = ROOT / rel
    if not path.exists():
        return False, f"missing {rel}"
    proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    out = proc.stdout.strip()
    return proc.returncode == 0 and expected in out, out[-500:]

main_py = ROOT / "main.py"
module = ROOT / "rmc_engine_v1" / "rmc_pipeline.py"
test = ROOT / "scripts" / "test_rmc_pipeline_summary_C9.py"
sha_file = ROOT.parent / "SHA256SUMS.txt"

add("file_exists_main.py", main_py.exists(), "main.py")
add("file_exists_rmc_pipeline.py", module.exists(), "rmc_engine_v1/rmc_pipeline.py")
add("file_exists_test_rmc_pipeline_summary_C9.py", test.exists(), "scripts/test_rmc_pipeline_summary_C9.py")

main_text = main_py.read_text(encoding="utf-8", errors="replace") if main_py.exists() else ""
module_text = module.read_text(encoding="utf-8", errors="replace") if module.exists() else ""
sha_text = sha_file.read_text(encoding="utf-8", errors="replace") if sha_file.exists() else ""

add("main_has_C9_label", "PATCH 262J1R-PREFLIGHT-C9" in main_text)
add("main_pipeline_summary_endpoint_present", '"/api/rmc/pipeline-summary"' in main_text)
add("main_full_pipeline_alias_present", '"/api/rmc/full-pipeline"' in main_text)
add("main_compact_trace_alias_present", '"/api/rmc/compact-trace"' in main_text)
add("main_delegates_to_rmc_pipeline_module", "build_pipeline_summary" in main_text and "rmc_engine_v1.rmc_pipeline" in main_text)
add("main_commit_guard_requires_commit_flag", "commit_flag and approval" in main_text)

add("module_engine_version_C9", "rmc_pipeline_summary_v1_patch262J1R_preflight_C9" in module_text)
add("module_has_build_pipeline_summary", "def build_pipeline_summary" in module_text)
add("module_has_first_blocker", "def _first_blocker" in module_text)
add("module_classifies_algorithm_failure_gate_refusal", "algorithm_failure" in module_text and "gate_refusal" in module_text and "read_only_refusal" in module_text)
add("module_compact_surface_default", "source_reports_included" in module_text and "include_full_reports" in module_text)
add("module_artifact_hygiene_records_C8", "c8_checksum_manifest_issue_folded_into_C9" in module_text)

for forbidden in ("subprocess", "os.system", "requests.", "openai", "Ollama", "write_text(", "open(\"w", ".replace(path", "sqlite3", "chromadb"):
    # The module should not perform I/O or external calls. It may import hashlib/re/datetime only.
    add(f"module_no_forbidden_{forbidden}", forbidden not in module_text)

if sha_file.exists():
    bad_sha = [line for line in sha_text.splitlines() if "__pycache__" in line or line.strip().endswith(".pyc") or ".pyc" in line]
    add("sha256_manifest_excludes_pycache_and_pyc", not bad_sha, "; ".join(bad_sha[:3]))
else:
    add("sha256_manifest_excludes_pycache_and_pyc", False, "SHA256SUMS.txt missing")

ok, detail = run_script("scripts/test_rmc_pipeline_summary_C9.py", "RESULT: pipeline_summary_C9_behavior_tests_pass=True")
add("test_rmc_pipeline_summary_C9.py_passes", ok, detail)

# Guard tests from the existing spine. These must pass when present, but the C9
# package itself does not re-ship every earlier test.
optional_guards = [
    ("scripts/test_rmc_memory_writer_C8.py", "RESULT: memory_writer_C8_behavior_tests_pass=True"),
    ("scripts/test_rmc_memory_writer_C7.py", "RESULT: memory_writer_C7_behavior_tests_pass=True"),
    ("scripts/test_rmc_echo_validator_C6.py", "RESULT: echo_validator_C6_behavior_tests_pass=True"),
    ("scripts/test_rmc_output_renderer_C5.py", "RESULT: output_renderer_C5_behavior_tests_pass=True"),
    ("scripts/test_rmc_manifest_compiler_C4.py", "RESULT: manifest_compiler_C4_behavior_tests_pass=True"),
    ("scripts/test_rmc_correction_naming_C3R.py", "RESULT: correction_naming_C3R_behavior_tests_pass=True"),
    ("scripts/test_rmc_measurement_kernel_C2R.py", "RESULT: measurement_kernel_C2R_behavior_tests_pass=True"),
]
for rel, expected in optional_guards:
    if (ROOT / rel).exists():
        ok, detail = run_script(rel, expected)
        add(rel.replace("/", "_") + "_still_passes", ok, detail)

print("PATCH 262J1R-PREFLIGHT-C9 VERIFY")
print("─" * 72)
passed = 0
for name, ok, detail in checks:
    if ok:
        passed += 1
        print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))
    else:
        print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
print("─" * 72)
print(f"Total: {len(checks)}")
print(f"Passed: {passed}")
print(f"Failed: {len(checks) - passed}")
if passed == len(checks):
    print("RESULT: PATCH_262J1R_PREFLIGHT_C9_VERIFY_OK")
    raise SystemExit(0)
print("RESULT: PATCH_262J1R_PREFLIGHT_C9_VERIFY_FAILED")
raise SystemExit(1)
