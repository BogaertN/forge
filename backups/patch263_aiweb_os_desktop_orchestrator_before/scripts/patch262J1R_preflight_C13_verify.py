#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C13 — Candidate Overextension Check."""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, condition, detail))
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def run_script(script: str) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(ROOT / script)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode == 0, proc.stdout.strip()


def main() -> int:
    required = [
        "rmc_engine_v1/candidate_generator.py",
        "rmc_engine_v1/evolutionary_drift_explorer.py",
        "scripts/test_rmc_candidate_overextension_C13.py",
        "scripts/test_rmc_candidate_generator_behavior.py",
        "scripts/test_rmc_evolutionary_drift_coherence_C2.py",
        "scripts/README_patch262J1R_preflight_C13.md",
        "SHA256SUMS.txt",
    ]
    for rel in required:
        check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

    cg = text("rmc_engine_v1/candidate_generator.py")
    ex = text("rmc_engine_v1/evolutionary_drift_explorer.py")
    sha = text("SHA256SUMS.txt") if (ROOT / "SHA256SUMS.txt").exists() else ""

    check("candidate_generator_engine_version_C13", "rmc_candidate_generator_v2_patch262J1R_preflight_C13" in cg)
    check("candidate_boundary_declares_overextension_gate", "overextension_gate" in cg and "N_max" in cg)
    check("candidate_has_apply_overextension_contract", "def _apply_overextension_contract" in cg)
    check("candidate_marks_overextended", 'candidate["overextended"]' in cg and 'candidate["novelty_over_budget"]' in cg)
    check("candidate_exposes_N_c_N_max", 'candidate["N_c"]' in cg and 'candidate["N_max"]' in cg)
    check("candidate_summary_counts_overextended", "overextended_candidate_count" in cg and "overextended_candidate_ids" in cg)
    check("candidate_does_not_delete_overextended", "Do not delete the candidate at generation time" in cg)

    check("explorer_honors_overextended_marker", "candidate_marked_overextended_route_to_review_or_archive" in ex)
    check("scorer_marks_overextended_unscoreable", "not_scoreable_due_to_overextended_novelty" in ex)
    check("explorer_bounded_for_scoring_blocks_overextended", "not candidate.get(\"overextended\")" in ex)

    forbidden_runtime = re.compile(r"\b(subprocess|socket|requests|urllib|sqlite3|chromadb|openai|ollama|anthropic)\b")
    for rel in ["rmc_engine_v1/candidate_generator.py", "rmc_engine_v1/evolutionary_drift_explorer.py"]:
        body = text(rel)
        check(f"{rel}_no_unapproved_external_runtime", forbidden_runtime.search(body) is None)
        check(f"{rel}_no_write_open", "open(" not in body and ".write(" not in body)

    bad_sha_terms = ["__pycache__", ".pyc", ".venv", "node_modules", "dist", "chroma_db", ".sqlite", ".db"]
    check("sha_excludes_pycache_pyc_venv_node_modules", not any(t in sha for t in bad_sha_terms))

    proc = subprocess.run([sys.executable, "-m", "py_compile", "rmc_engine_v1/candidate_generator.py", "rmc_engine_v1/evolutionary_drift_explorer.py", "scripts/test_rmc_candidate_overextension_C13.py"], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    check("py_compile_changed_files", proc.returncode == 0, proc.stdout.strip())

    for script in [
        "scripts/test_rmc_candidate_overextension_C13.py",
        "scripts/test_rmc_candidate_generator_behavior.py",
        "scripts/test_rmc_evolutionary_drift_coherence_C2.py",
    ]:
        ok, out = run_script(script)
        tail = "\n".join(out.splitlines()[-6:])
        check(f"{script}_passes", ok, tail)

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C13_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C13_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
