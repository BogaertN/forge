#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-B3 phase codex binding."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.phase_codex import (  # noqa: E402
    get_phase_profile,
    phase_codex_boundary,
    phase_codex_preview,
    validate_phase_codex,
)

checks = []

def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))

validation = validate_phase_codex()
check("codex_validation_ok", validation.get("status") == "OK", repr(validation))
check("codex_has_nine_phases", validation.get("phase_count") == 9, str(validation.get("phase_count")))

for phase in [f"Φ{i}" for i in range(1, 10)]:
    prof = get_phase_profile(phase)
    check(f"{phase}_profile_present", bool(prof), repr(prof))
    check(f"{phase}_has_glyph", bool(prof.get("glyph")), repr(prof))
    check(f"{phase}_has_hex", str(prof.get("hex", "")).startswith("#"), str(prof.get("hex")))
    check(f"{phase}_has_function_hook", str(prof.get("function_hook", "")).endswith(")"), str(prof.get("function_hook")))
    check(f"{phase}_has_cold_storage_form", bool(prof.get("cold_storage_form")), str(prof.get("cold_storage_form")))

p6 = get_phase_profile("Φ6")
p8 = get_phase_profile("Φ8")
p9 = get_phase_profile("Φ9")
check("phi6_is_grace", p6.get("phase_name") == "Grace", repr(p6))
check("phi6_hook_is_restore", p6.get("function_hook") == "restore_resonance_alignment()", str(p6.get("function_hook")))
check("phi8_is_power_projection_gate", p8.get("gate_role") == "projection_gate", repr(p8))
check("phi9_is_recursive_evolution", p9.get("phase_name") == "Recursive Evolution", repr(p9))

boundary = phase_codex_boundary()
check("boundary_side_effect_free", boundary.get("side_effect_free") is True, repr(boundary))
check("boundary_no_writes", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False, repr(boundary))
check("boundary_no_llm", boundary.get("calls_llm") is False, repr(boundary))

preview = phase_codex_preview()
check("preview_read_only", preview.get("read_only") is True, repr(preview))
check("preview_has_color_map", len(preview.get("color_map", {})) >= 9, repr(preview.get("color_map")))
check("preview_has_runtime_hooks", len(preview.get("runtime_hooks", {})) == 9, repr(preview.get("runtime_hooks")))

total = len(checks)
passed = sum(1 for _, ok, _ in checks if ok)
failed = total - passed
for name, ok, detail in checks:
    print(("✓" if ok else "✗"), name, detail if not ok else "")
print(f"Total: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
if failed:
    print("RESULT: phase_codex_B3_behavior_tests_pass=False")
    raise SystemExit(1)
print("RESULT: phase_codex_B3_behavior_tests_pass=True")
