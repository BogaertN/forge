#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C4."""
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
        "rmc_engine_v1/manifest_compiler.py",
        "scripts/test_rmc_manifest_compiler_C4.py",
        "scripts/patch262J1R_preflight_C4_verify.py",
    ]
    for f in files:
        add(f"file_exists_{f}", (ROOT / f).exists(), f)

    main_text = read("main.py")
    module_text = read("rmc_engine_v1/manifest_compiler.py")
    add("main_has_C4_label", "Patch 262J1R-Preflight-C4" in main_text)
    add("main_delegates_to_manifest_compiler", "from rmc_engine_v1.manifest_compiler import compile_manifest" in main_text)
    add("main_manifest_endpoint_present", '"/api/rmc/manifest-compiler"' in main_text)
    add("main_recursive_manifest_alias_present", '"/api/rmc/recursive-manifest-compiler"' in main_text)
    add("main_manifest_alias_present", '"/api/rmc/manifest"' in main_text)

    add("module_engine_version_C4", "rmc_manifest_compiler_v1_patch262J1R_preflight_C4" in module_text)
    add("module_has_compile_manifest", "def compile_manifest(" in module_text)
    add("module_has_mu_t", "μ_t" in module_text)
    add("module_enforces_schema_fields", all(field in module_text for field in ["claim", "phase_path", "operator_path", "memory_links", "confidence", "novelty", "drift_status", "output_targets"]))
    add("module_checks_stable_naming", "stable_naming" in module_text and "naming_confidence_strong" in module_text)
    add("module_checks_phase6_before_projection", "phase6_and_7_before_projection_if_projection_requested" in module_text)
    add("module_separates_manifest_from_rendering", "renders_final_language" in module_text and "False" in module_text)
    add("module_uses_measurement_kernel", "from rmc_engine_v1.measurement_kernel" in module_text)

    forbidden = ["subprocess", "requests", "urllib.request", "open(", "os.system", "Popen(", "eval(", "exec("]
    bad = [term for term in forbidden if term in module_text]
    add("module_no_forbidden_side_effect_terms", not bad, ",".join(bad))

    ok, detail = run_script("scripts/test_rmc_manifest_compiler_C4.py")
    add("test_rmc_manifest_compiler_C4.py_passes", ok, detail)
    for optional in (
        "scripts/test_rmc_correction_naming_C3R.py",
        "scripts/test_rmc_measurement_kernel_C2R.py",
        "scripts/test_rmc_evolutionary_drift_coherence_C2.py",
        "scripts/test_rmc_candidate_generator_behavior.py",
    ):
        if (ROOT / optional).exists():
            ok2, detail2 = run_script(optional)
            add(f"{Path(optional).name}_still_passes", ok2, detail2)

    print("PATCH 262J1R-PREFLIGHT-C4 VERIFY")
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
        print("RESULT: PATCH_262J1R_PREFLIGHT_C4_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C4_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
