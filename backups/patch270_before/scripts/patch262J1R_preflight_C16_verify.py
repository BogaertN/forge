#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C16 — Optional LLM Renderer Boundary."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def read(rel: str) -> str:
    path = ROOT / rel
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"__READ_ERROR__:{exc}"


def run_script(rel: str, marker: str) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, capture_output=True, timeout=45)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0 and marker in out, out[-2400:]


def py_compile(paths: list[str]) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, "-m", "py_compile", *paths], cwd=str(ROOT), text=True, capture_output=True, timeout=45)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def sha_manifest_ok() -> tuple[bool, str]:
    sha = ROOT / "SHA256SUMS.txt"
    if not sha.exists():
        return False, "SHA256SUMS.txt missing"
    bad: list[str] = []
    for line in sha.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, rel = line.split(None, 1)
        except ValueError:
            bad.append(f"bad_line:{line}")
            continue
        rel = rel.strip().lstrip("*")
        path = ROOT / rel
        if not path.exists():
            bad.append(f"missing:{rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            bad.append(f"mismatch:{rel}")
    return not bad, "; ".join(bad[:8])


def no_bad_artifacts(text: str) -> bool:
    return not any(term in text for term in ["__pycache__", ".pyc", ".venv", "node_modules", "dist/", "build/"])


def main() -> int:
    files = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/llm_renderer.py",
        "rmc_engine_v1/output_renderer.py",
        "scripts/test_rmc_llm_renderer_C16.py",
        "scripts/patch262J1R_preflight_C16_verify.py",
        "scripts/README_patch262J1R_preflight_C16.md",
        "SHA256SUMS.txt",
    ]
    for rel in files:
        add(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

    main_py = read("main.py")
    init_py = read("rmc_engine_v1/__init__.py")
    llm_py = read("rmc_engine_v1/llm_renderer.py")
    renderer_py = read("rmc_engine_v1/output_renderer.py")
    sha_txt = read("SHA256SUMS.txt")

    add("llm_engine_version_C16", "rmc_llm_renderer_v1_patch262J1R_preflight_C16" in llm_py)
    add("llm_default_off", '"default_enabled": False' in llm_py and "normalize_llm_toggle" in llm_py)
    add("llm_endpoint_guard_local_only", "LOCAL_HOSTS" in llm_py and "LLM_RENDERER_ENDPOINT_HOST_REFUSED" in llm_py)
    add("llm_sentence_plan_prompt", "SENTENCE_PLAN_JSON" in llm_py and "MANIFEST_SUMMARY_JSON" in llm_py)
    add("llm_no_shell_writes", "subprocess" not in llm_py and "os.system" not in llm_py and "write_text(" not in llm_py and "open(\"w" not in llm_py and "open('w" not in llm_py)
    add("renderer_engine_version_C16", "rmc_output_renderer_v1_patch262J1R_preflight_C16" in renderer_py)
    add("renderer_imports_optional_llm_boundary", "render_text_with_optional_llm" in renderer_py and "llm_renderer_enabled" in renderer_py)
    add("renderer_default_deterministic_path", "_render_text_deterministic" in renderer_py and "llm_renderer_default_off" in renderer_py)
    add("renderer_sentence_guard_after_llm", "_sentence_plan_validation(rendered, sentence_plan)" in renderer_py and "forbidden_claims_present_in_rendered_output" in renderer_py)
    add("main_has_llm_status_route", "/api/rmc/llm-renderer/status" in main_py and "_p262t_rmc_llm_renderer_status_v1" in main_py)
    add("main_passes_llm_toggle_to_renderer", "llm_renderer_enabled" in main_py and "model_endpoint" in main_py and "llm_timeout_seconds" in main_py)
    add("init_registers_llm_renderer", '"llm_renderer"' in init_py and "rmc_engine_v1.llm_renderer" in init_py)
    add("sha_manifest_hashes_ok", *sha_manifest_ok())
    add("sha_excludes_bad_artifacts", no_bad_artifacts(sha_txt))

    ok, detail = py_compile([
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/llm_renderer.py",
        "rmc_engine_v1/output_renderer.py",
        "scripts/test_rmc_llm_renderer_C16.py",
    ])
    add("py_compile_changed_files", ok, detail)

    for rel, marker in [
        ("scripts/test_rmc_llm_renderer_C16.py", "RESULT: llm_renderer_C16_behavior_tests_pass=True"),
        ("scripts/test_rmc_echo_validator_C6.py", "RESULT: echo_validator_C6_behavior_tests_pass=True"),
        ("scripts/test_rmc_memory_writer_C7.py", "RESULT: memory_writer_C7_behavior_tests_pass=True"),
    ]:
        ok, detail = run_script(rel, marker)
        add(rel.replace("/", "_") + "_passes", ok, detail)

    print("PATCH 262J1R-PREFLIGHT-C16 VERIFY")
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
        print("RESULT: PATCH_262J1R_PREFLIGHT_C16_VERIFY_OK")
        return 0
    print("RESULT: PATCH_262J1R_PREFLIGHT_C16_VERIFY_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
