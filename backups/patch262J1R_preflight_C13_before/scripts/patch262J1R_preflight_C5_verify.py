#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C5."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def run_script(path: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run([sys.executable, str(ROOT / path)], cwd=str(ROOT), text=True, capture_output=True, timeout=45)
    except Exception as exc:
        return False, repr(exc)
    out = (proc.stdout + proc.stderr).strip()
    tail = out.splitlines()[-1] if out else ""
    return proc.returncode == 0, tail


def main() -> int:
    files = [
        "main.py",
        "rmc_engine_v1/output_renderer.py",
        "rmc_engine_v1/manifest_compiler.py",
        "scripts/test_rmc_output_renderer_C5.py",
        "scripts/patch262J1R_preflight_C5_verify.py",
    ]
    for f in files:
        add(f"file_exists_{f}", (ROOT / f).exists(), f)

    main_text = read("main.py")
    module_text = read("rmc_engine_v1/output_renderer.py")
    add("main_has_C5_label", "Patch 262J1R-Preflight-C5" in main_text)
    add("main_delegates_to_output_renderer", "from rmc_engine_v1.output_renderer import render_manifest" in main_text)
    add("main_output_renderer_endpoint_present", '"/api/rmc/output-renderer"' in main_text)
    add("main_renderer_alias_present", '"/api/rmc/renderer"' in main_text)
    add("main_render_alias_present", '"/api/rmc/render"' in main_text)

    add("module_engine_version_C5", "rmc_output_renderer_v1_patch262J1R_preflight_C5" in module_text)
    add("module_has_render_manifest", "def render_manifest(" in module_text)
    add("module_has_R_t", "R_t" in module_text)
    add("module_enforces_manifest_before_render", "manifest_packet_missing_or_manifest_blocked" in module_text and "blocked_manifest" in module_text)
    add("module_has_fidelity_precheck", "def _fidelity_precheck" in module_text and "fidelity_score" in module_text)
    add("module_has_render_formula", "R_t = ρ(μ_t, a, s)" in module_text)
    add("module_blocks_memory_write", "memory_write_allowed" in module_text and "False" in module_text)
    add("module_echo_required", "echo_validation_required" in module_text)

    forbidden = ["subprocess", "requests", "urllib.request", "open(", "os.system", "Popen(", "eval(", "exec("]
    bad = [term for term in forbidden if term in module_text]
    add("module_no_forbidden_side_effect_terms", not bad, ",".join(bad))

    ok, detail = run_script("scripts/test_rmc_output_renderer_C5.py")
    add("test_rmc_output_renderer_C5.py_passes", ok, detail)
    for optional in (
        "scripts/test_rmc_manifest_compiler_C4.py",
        "scripts/test_rmc_correction_naming_C3R.py",
        "scripts/test_rmc_measurement_kernel_C2R.py",
        "scripts/test_rmc_evolutionary_drift_coherence_C2.py",
        "scripts/test_rmc_candidate_generator_behavior.py",
    ):
        if (ROOT / optional).exists():
            ok2, detail2 = run_script(optional)
            add(f"{Path(optional).name}_still_passes", ok2, detail2)

    print("PATCH 262J1R-PREFLIGHT-C5 VERIFY")
    print("─" * 72)
    passed = 0
    for name, ok, detail in CHECKS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")
        passed += int(ok)
    failed = len(CHECKS) - passed
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C5_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C5_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
