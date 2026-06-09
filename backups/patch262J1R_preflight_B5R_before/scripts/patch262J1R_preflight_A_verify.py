#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-A — Phase Parser Engine Extraction.

Run from forge root:
    python scripts/patch262J1R_preflight_A_verify.py

Expected output when patch is correctly installed:
    RESULT: PATCH_262J1R_PREFLIGHT_A_VERIFY_OK
"""

import sys
import os
import subprocess
import importlib
import inspect

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FORGE_ROOT)

PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, str, str]] = []


def check(name: str, value: bool, detail: str = "") -> None:
    results.append((name, PASS if value else FAIL, detail))


# ── 1. phase_parser engine module ────────────────────────────────────────────

try:
    from rmc_engine_v1 import phase_parser as _pp
    check("phase_parser_module_importable", True)
except ImportError as exc:
    check("phase_parser_module_importable", False, str(exc))
    _pp = None  # type: ignore[assignment]

if _pp is not None:
    check("phase_parser_has_parse_phase", hasattr(_pp, "parse_phase"))
    check("phase_parser_has_boundary", hasattr(_pp, "phase_parser_boundary"))
    check("phase_parser_has_catalog", hasattr(_pp, "phase_catalog"))

    boundary = _pp.phase_parser_boundary()
    check("phase_parser_main_py_is_thin_adapter",
          boundary.get("calls_main_py_functions") is False
          and boundary.get("source_text_supplied_by_adapter") is True)
    check("phase_parser_no_side_effects",
          boundary.get("writes_files") is False
          and boundary.get("writes_rmc_memory") is False
          and boundary.get("calls_llm") is False)

    result = _pp.parse_phase("test phase parser smoke test")
    check("phase_parser_smoke_returns_dict",
          isinstance(result, dict) and "phase_state" in result and "input_event" in result)
    check("phase_parser_smoke_no_writes",
          result.get("writes_files") is False
          and result.get("rmc_live_memory_write") is False
          and result.get("approved_output") is False)

    src = inspect.getsource(_pp)
    check("phase_parser_no_subprocess_in_source", "subprocess" not in src)
    check("phase_parser_no_open_write_in_source",
          not any(f'open(' in line and '"w"' in line for line in src.splitlines()))


# ── 2. coherence_math regression (clamp/phase_num now exported) ───────────────

try:
    from rmc_engine_v1.coherence_math import clamp, phase_num, score_candidate
    check("coherence_math_clamp_exported", True)
    check("coherence_math_clamp_correct", clamp(2.0) == 1.0 and clamp(-1.0) == 0.0)
    check("coherence_math_phase_num_exported", True)
    check("coherence_math_phase_num_correct", phase_num("Φ6") == 6 and phase_num("phi3") == 3)
except ImportError as exc:
    check("coherence_math_clamp_exported", False, str(exc))
    check("coherence_math_phase_num_exported", False)
    check("coherence_math_clamp_correct", False)
    check("coherence_math_phase_num_correct", False)

# Circuit breaker zero-score regression
try:
    cb_report = {
        "source_drift_report": {
            "circuit_breaker": {"triggered": True},
            "epsilon_s": {"sigma_res": 0.1, "D_score": 0.1,
                          "phase_deviation_normalized": 0.1, "epsilon_s": 0.1},
            "chi_t": {"required": False},
            "drift_classes": [],
            "source_phase_parser": {
                "phase_state": {"phase_primary": "Φ1", "phase_path_hypothesis": ["Φ1"],
                                "confidence": 0.9},
                "input_event": {"event_id": "v", "x_t_raw_input_preview": "v"},
            },
        },
        "candidate_set_id": "v",
    }
    sc = score_candidate(
        {"candidate_id": "v", "title": "v", "confidence": 0.99, "required_limitations": []},
        cb_report,
    )
    check("coherence_math_circuit_breaker_zeroes_score",
          sc["coherence_score"] == 0.0,
          f"score={sc['coherence_score']!r}")
    check("coherence_math_circuit_breaker_blocks_manifest",
          sc["manifest_gate"]["allowed"] is False)
except Exception as exc:
    check("coherence_math_circuit_breaker_zeroes_score", False, str(exc))
    check("coherence_math_circuit_breaker_blocks_manifest", False)


# ── 3. manifest_compiler regression ──────────────────────────────────────────

try:
    from rmc_engine_v1.manifest_compiler import (
        compile_manifest_dry_run, manifest_compiler_boundary
    )
    mc_b = manifest_compiler_boundary()
    check("manifest_compiler_schema_validation_active",
          mc_b.get("schema_validation_active") is True)
    blocked = compile_manifest_dry_run({})
    check("manifest_compiler_refuses_empty_input",
          blocked["manifest_compilation_allowed"] is False
          and blocked["manifest_packet"] is None)
except ImportError as exc:
    check("manifest_compiler_schema_validation_active", False, str(exc))
    check("manifest_compiler_refuses_empty_input", False)


# ── 4. main.py does not own phase parser logic ────────────────────────────────

main_py_path = os.path.join(FORGE_ROOT, "main.py")
if os.path.exists(main_py_path):
    with open(main_py_path, encoding="utf-8") as f:
        main_src = f.read()
    check("main_py_old_phase_catalog_gone",
          "_p262f_phase_catalog" not in main_src,
          "Old _p262f_phase_catalog function removed from main.py")
    check("main_py_old_rank_phases_gone",
          "_p262f_rank_phases" not in main_src,
          "Old _p262f_rank_phases function removed from main.py")
    check("main_py_thin_adapter_present",
          "_p262f_resolve_source" in main_src and "_p262f_rmc_phase_parser_v1" in main_src,
          "Thin adapter functions present in main.py")
    check("main_py_imports_phase_parser",
          "from rmc_engine_v1.phase_parser import" in main_src,
          "main.py imports from rmc_engine_v1.phase_parser")
    check("main_py_clamp_delegates_to_kernel",
          "from rmc_engine_v1.coherence_math import clamp" in main_src
          or "Delegates to rmc_engine_v1.coherence_math.clamp" in main_src,
          "Duplicate clamp fixed to delegate to kernel")
else:
    check("main_py_old_phase_catalog_gone", False, "main.py not found at forge root")
    check("main_py_old_rank_phases_gone", False)
    check("main_py_thin_adapter_present", False)
    check("main_py_imports_phase_parser", False)
    check("main_py_clamp_delegates_to_kernel", False)


# ── 5. Behavioral tests ───────────────────────────────────────────────────────

for script_name, result_key in [
    ("test_rmc_phase_parser_behavior.py", "phase_parser_behavior_tests_pass"),
    ("test_rmc_coherence_math_behavior.py", "coherence_math_behavior_tests_pass"),
]:
    script_path = os.path.join(FORGE_ROOT, "scripts", script_name)
    if os.path.exists(script_path):
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, cwd=FORGE_ROOT,
        )
        tests_pass = proc.returncode == 0
        check(result_key, tests_pass,
              "exit=0" if tests_pass else f"exit={proc.returncode}\n{proc.stdout[-600:]}")
    else:
        check(result_key, False, f"{script_name} not found")


# ── 6. No new Forge commands ──────────────────────────────────────────────────

import rmc_engine_v1.phase_parser as _pp_mod
import inspect
pp_src = inspect.getsource(_pp_mod)
check("no_forge_commands_in_phase_parser",
      "forge_commands" not in pp_src and "cmd_forge_" not in pp_src)

check("adds_forge_commands", "forge_commands" not in pp_src and "cmd_forge_" not in pp_src,
      "phase_parser.py adds no Forge CLI commands")


# ── Summary ───────────────────────────────────────────────────────────────────

passed = sum(1 for _, v, _ in results if v == PASS)
failed = sum(1 for _, v, _ in results if v == FAIL)

print(f"\nPATCH 262J1R-PREFLIGHT-A VERIFIER — Phase Parser Engine Extraction")
print(f"{'─' * 72}")
for name, verdict, detail in results:
    marker = "✓" if verdict == PASS else "✗"
    line = f"  {marker} [{verdict}] {name}"
    if verdict == FAIL or (detail and len(detail) < 80):
        line += f"\n        {detail}"
    print(line)
print(f"{'─' * 72}")
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
print()

print("MACHINE_READABLE_VERDICTS:")
keys = [
    "phase_parser_module_importable",
    "phase_parser_main_py_is_thin_adapter",
    "phase_parser_no_side_effects",
    "coherence_math_circuit_breaker_zeroes_score",
    "manifest_compiler_schema_validation_active",
    "main_py_old_phase_catalog_gone",
    "main_py_thin_adapter_present",
    "main_py_imports_phase_parser",
    "phase_parser_behavior_tests_pass",
    "coherence_math_behavior_tests_pass",
    "adds_forge_commands",
]
for k in keys:
    for name, verdict, _ in results:
        if name == k:
            print(f"  {k}={verdict == PASS}")
            break

if failed == 0:
    print(f"\nRESULT: PATCH_262J1R_PREFLIGHT_A_VERIFY_OK")
    sys.exit(0)
else:
    print(f"\nRESULT: PATCH_262J1R_PREFLIGHT_A_VERIFY_FAIL ({failed} failed)")
    sys.exit(1)
