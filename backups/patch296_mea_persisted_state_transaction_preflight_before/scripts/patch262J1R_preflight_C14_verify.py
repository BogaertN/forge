#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C14 — Real Glyph Renderer."""
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(condition), detail))


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_script(rel: str) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode == 0, proc.stdout


def no_bad_runtime(rel: str) -> None:
    src = read(rel)
    bad_tokens = ["requests", "chromadb", "sqlite3", "subprocess", "os.system", "Popen", "socket", "open(", ".write(", "Image", "diffusers", "torch"]
    hits = [tok for tok in bad_tokens if tok in src]
    # Path.read_text appears in phase_codex, but glyph_renderer must not read files directly.
    check(f"{rel}_no_unapproved_external_runtime", not hits, ",".join(hits))


def main() -> int:
    required = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/glyph_renderer.py",
        "rmc_engine_v1/output_renderer.py",
        "scripts/test_rmc_glyph_renderer_C14.py",
        "scripts/test_rmc_output_renderer_C5.py",
        "scripts/test_rmc_phase_codex_binding.py",
        "scripts/patch262J1R_preflight_C14_verify.py",
        "scripts/README_patch262J1R_preflight_C14.md",
        "SHA256SUMS.txt",
    ]
    for rel in required:
        check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

    glyph = read("rmc_engine_v1/glyph_renderer.py")
    out = read("rmc_engine_v1/output_renderer.py")
    init = read("rmc_engine_v1/__init__.py")
    main_py = read("main.py")
    sha = read("SHA256SUMS.txt")

    check("glyph_engine_version_C14", "rmc_glyph_renderer_v1_patch262J1R_preflight_C14" in glyph)
    check("glyph_has_G_t_formula", "G_t = γ(μ_t, phase_path, codex_v2_5, seed_trace)" in glyph)
    check("glyph_has_deterministic_seed_formula", "glyph_seed = SHA256" in glyph)
    check("glyph_has_required_packet_fields", "REQUIRED_GLYPH_PACKET_FIELDS" in glyph and "glyph_svg" in glyph and "composite_seed" in glyph)
    check("glyph_has_all_render_modes", all(x in glyph for x in ["single_phase_glyph", "phase_path_glyph", "drift_state_glyph", "cold_storage_glyph", "composite_glyph"]))
    check("glyph_has_svg_templates", all(x in glyph for x in ["glyph-" if False else "_phase_body_svg", "<circle", "<polygon", "<ellipse", "<path", "<line"]))
    check("glyph_image_generation_not_authority", "image_generation_is_authority" in glyph and "False" in glyph and "cannot define canonical glyph meaning" in glyph)
    check("glyph_reads_codex_through_phase_codex", "from rmc_engine_v1.phase_codex import" in glyph)

    check("output_renderer_engine_version_C14", "rmc_output_renderer_v1_patch262J1R_preflight_C14" in out)
    check("output_renderer_imports_glyph_renderer", "from rmc_engine_v1.glyph_renderer import render_glyph_packet" in out)
    check("output_renderer_no_placeholder_glyph_refs", "fbsc_phase_glyph::" not in out)
    check("output_renderer_uses_real_glyph_kind", "GLYPH_PACKET_KIND = \"rmc_phase_glyph_render_packet_v1\"" in glyph and "glyph_packet_version" in glyph)

    check("init_registers_glyph_renderer", "\"glyph_renderer\"" in init and "rmc_engine_v1.glyph_renderer" in init)
    check("main_has_glyph_adapter", "_p262r_rmc_glyph_renderer_v1" in main_py)
    check("main_has_glyph_routes", "/api/rmc/glyph-renderer" in main_py and "/api/rmc/glyph-packet" in main_py and "/api/rmc/phase-glyph" in main_py)
    check("main_routes_to_glyph_adapter", "_p262r_rmc_glyph_renderer_v1(self.path)" in main_py)

    check("sha_excludes_pycache_pyc_venv_node_modules", "__pycache__" not in sha and ".pyc" not in sha and ".venv" not in sha and "node_modules" not in sha)
    no_bad_runtime("rmc_engine_v1/glyph_renderer.py")

    compile_targets = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/glyph_renderer.py",
        "rmc_engine_v1/output_renderer.py",
        "scripts/test_rmc_glyph_renderer_C14.py",
        "scripts/patch262J1R_preflight_C14_verify.py",
    ]
    ok_compile = True
    details = []
    for rel in compile_targets:
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
        except Exception as exc:
            ok_compile = False
            details.append(f"{rel}:{exc}")
    check("py_compile_changed_files", ok_compile, "; ".join(details))

    for rel, marker in [
        ("scripts/test_rmc_glyph_renderer_C14.py", "RESULT: glyph_renderer_C14_behavior_tests_pass=True"),
        ("scripts/test_rmc_output_renderer_C5.py", "RESULT: output_renderer_C5_behavior_tests_pass=True"),
        ("scripts/test_rmc_phase_codex_binding.py", "RESULT: phase_codex_B3_behavior_tests_pass=True"),
    ]:
        ok, output = run_script(rel)
        check(f"{rel}_passes", ok and marker in output, output[-2500:])

    print("PATCH 262J1R-PREFLIGHT-C14 VERIFY")
    print("────────────────────────────────────────────────────────────────────────")
    passed = 0
    for name, ok, detail in CHECKS:
        if ok:
            passed += 1
            print(f"[PASS] {name}" + (f" :: {detail}" if detail and name.startswith("file_exists") else ""))
        else:
            print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
    total = len(CHECKS)
    failed = total - passed
    print("────────────────────────────────────────────────────────────────────────")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C14_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C14_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
