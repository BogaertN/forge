#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C10.

C10 hardens the first three audit-priority items:
1) projection_status is a required μ_t manifest field.
2) Echo Validator uses output-mode thresholds (text >= 0.82, formal_text 0.85).
3) Output Renderer builds/enforces a sentence plan with forbidden_claims.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"__READ_ERROR__ {type(exc).__name__}: {exc}"


def run_script(rel: str, marker: str, timeout: int = 120) -> tuple[bool, str]:
    path = ROOT / rel
    if not path.exists():
        return False, f"missing {rel}"
    proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    out = proc.stdout.strip()
    return proc.returncode == 0 and marker in out, out[-800:]


def no_forbidden_io(src: str) -> bool:
    forbidden = [
        "subprocess.",
        "os.system",
        "Popen(",
        "requests.",
        "urllib.request",
        "openai",
        "ollama",
        "chromadb",
        "sqlite3",
        "IdentityVaultClient",
        "identity_vault.write",
        "write_text(",
        "open(\"w",
        "open('w",
    ]
    return not any(term in src for term in forbidden)


def main() -> int:
    manifest = ROOT / "rmc_engine_v1" / "manifest_compiler.py"
    renderer = ROOT / "rmc_engine_v1" / "output_renderer.py"
    echo = ROOT / "rmc_engine_v1" / "echo_validator.py"
    test = ROOT / "scripts" / "test_rmc_contract_guardrails_C10.py"
    sha = ROOT / "SHA256SUMS.txt"

    add("file_exists_manifest_compiler", manifest.exists(), str(manifest.relative_to(ROOT)))
    add("file_exists_output_renderer", renderer.exists(), str(renderer.relative_to(ROOT)))
    add("file_exists_echo_validator", echo.exists(), str(echo.relative_to(ROOT)))
    add("file_exists_C10_behavior_test", test.exists(), str(test.relative_to(ROOT)))
    add("file_exists_SHA256SUMS", sha.exists(), str(sha.relative_to(ROOT)))

    manifest_text = read(manifest)
    renderer_text = read(renderer)
    echo_text = read(echo)
    sha_text = read(sha)

    add("manifest_engine_version_C10", "rmc_manifest_compiler_v1_patch262J1R_preflight_C10" in manifest_text)
    add("manifest_requires_projection_status", '"projection_status"' in manifest_text and "REQUIRED_MANIFEST_FIELDS" in manifest_text)
    add("manifest_projection_status_helper", "def _projection_status" in manifest_text and "projection_allowed_now" in manifest_text)

    add("renderer_engine_version_C10", "rmc_output_renderer_v1_patch262J1R_preflight_C10" in renderer_text)
    add("renderer_has_sentence_plan", "def _sentence_plan" in renderer_text and "core_claim" in renderer_text and "forbidden_claims" in renderer_text)
    add("renderer_enforces_forbidden_claims", "def _sentence_plan_validation" in renderer_text and "forbidden_hits" in renderer_text and "forbidden_claims_present_in_rendered_output" in renderer_text)
    add("renderer_requires_projection_status", '"projection_status"' in renderer_text and "REQUIRED_MU_FIELDS" in renderer_text)

    add("echo_engine_version_C10", "rmc_echo_validator_v1_patch262J1R_preflight_C10" in echo_text)
    add("echo_has_threshold_table", "ECHO_THRESHOLDS_BY_MODE" in echo_text and '"text": 0.82' in echo_text and '"formal_text": 0.85' in echo_text and '"json_packet": 0.90' in echo_text)
    add("echo_uses_threshold_helper", "def _threshold_for_render" in echo_text and "echo_threshold_key" in echo_text)
    add("echo_requires_projection_status", '"projection_status"' in echo_text and "REQUIRED_MU_FIELDS" in echo_text)

    for rel, src in [
        ("manifest_compiler.py", manifest_text),
        ("output_renderer.py", renderer_text),
        ("echo_validator.py", echo_text),
    ]:
        add(f"{rel}_no_unapproved_io_or_llm", no_forbidden_io(src))

    bad_sha = [line for line in sha_text.splitlines() if "__pycache__" in line or ".pyc" in line or ".venv" in line or "node_modules" in line]
    add("sha_excludes_pycache_pyc_venv_node_modules", not bad_sha, "; ".join(bad_sha[:3]))

    tests = [
        ("scripts/test_rmc_contract_guardrails_C10.py", "RESULT: rmc_contract_guardrails_C10_behavior_tests_pass=True"),
        ("scripts/test_rmc_manifest_compiler_C4.py", "RESULT: manifest_compiler_C4_behavior_tests_pass=True"),
        ("scripts/test_rmc_output_renderer_C5.py", "RESULT: output_renderer_C5_behavior_tests_pass=True"),
        ("scripts/test_rmc_echo_validator_C6.py", "RESULT: echo_validator_C6_behavior_tests_pass=True"),
        ("scripts/test_rmc_pipeline_summary_C9.py", "RESULT: pipeline_summary_C9_behavior_tests_pass=True"),
        ("scripts/test_rmc_memory_writer_C7.py", "RESULT: memory_writer_C7_behavior_tests_pass=True"),
    ]
    for rel, marker in tests:
        ok, detail = run_script(rel, marker)
        add(rel.replace("/", "_") + "_passes", ok, detail)

    print("PATCH 262J1R-PREFLIGHT-C10 VERIFY")
    print("─" * 72)
    passed = 0
    for name, ok, detail in CHECKS:
        if ok:
            passed += 1
            print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))
        else:
            print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(CHECKS) - passed}")
    if passed == len(CHECKS):
        print("RESULT: PATCH_262J1R_PREFLIGHT_C10_VERIFY_OK")
        return 0
    print("RESULT: PATCH_262J1R_PREFLIGHT_C10_VERIFY_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
