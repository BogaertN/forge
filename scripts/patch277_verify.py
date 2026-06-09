#!/usr/bin/env python3
"""
forge/scripts/patch277_verify.py

Patch 277 verifier — MEA Convergence / Ancestry / Cost Scoring.
Verifies the additive read-only scoring layer without mutating Forge state.
"""

from __future__ import annotations

import hashlib
import importlib
import os
import py_compile
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple

PATCH = "Patch 277 — MEA Convergence / Ancestry / Cost Scoring"
FORGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PARENT = FORGE_ROOT.parent

REQUIRED_FILES = [
    "main.py",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/unknown_detector.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "rmc_engine_v1/mea/proof_debt_scorer.py",
    "rmc_engine_v1/mea/information_gain_scorer.py",
    "rmc_engine_v1/mea/convergence_scorer.py",
    "rmc_engine_v1/mea/goal_ancestry_scorer.py",
    "rmc_engine_v1/mea/operator_cost_scorer.py",
    "scripts/patch277_verify.py",
    "scripts/test_patch277_mea_convergence_ancestry_cost.py",
    "scripts/README_277.md",
    "SHA256SUMS.txt",
]

PRESERVED_ROUTES = [
    "/api/rmc/deep-dry-run",
    "/api/rmc/deep-pipeline-preflight",
    "/api/rmc/protoforge2-drift-preview",
    "/api/rmc/resurrection-preview",
    "/api/rmc/containment-router",
    "/api/rmc/chi-correction-preview",
    "/api/rmc/route-manifest",
    "/api/aiweb-os/lifecycle-manifest",
    "/api/aiweb-os/status",
    "/api/aiweb-os/logs",
    "/api/aiweb-os/build-manifest",
    "/api/mea/foundation-status",
]

FORBIDDEN_RUNTIME_PATTERNS = [
    r"\bsubprocess\b",
    r"\bos\.system\b",
    r"\bPopen\b",
    r"\brequests\b",
    r"\burllib\b",
    r"\bsocket\b",
    r"\bopen\s*\(",
    r"write_text\s*\(",
    r"write_bytes\s*\(",
    r"\.write\s*\(",
    r"chromadb",
    r"ChromaClient",
    r"identity_vault\.db",
    r"vault\.db",
]
RUNTIME_SCAN_FILES = [
    "rmc_engine_v1/mea/convergence_scorer.py",
    "rmc_engine_v1/mea/goal_ancestry_scorer.py",
    "rmc_engine_v1/mea/operator_cost_scorer.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
]


def rel(path: str) -> Path:
    return FORGE_ROOT / path


class Results:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        if ok:
            self.passed += 1
            suffix = f" — {detail}" if detail else ""
            print(f"  ✓ [PASS] {name}{suffix}")
        else:
            self.failed += 1
            suffix = f" — {detail}" if detail else ""
            print(f"  ✗ [FAIL] {name}{suffix}")


def verify_sha256sums() -> Tuple[bool, str]:
    sums = rel("SHA256SUMS.txt")
    if not sums.exists():
        return False, "SHA256SUMS.txt missing"
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, filename = line.split(maxsplit=1)
        filename = filename.strip().lstrip("*")
        if filename.startswith("forge/"):
            fpath = PROJECT_PARENT / filename
        else:
            fpath = FORGE_ROOT / filename
        if not fpath.exists():
            return False, f"missing {filename}"
        actual = hashlib.sha256(fpath.read_bytes()).hexdigest()
        if actual != expected:
            return False, f"hash mismatch {filename}"
    return True, "all listed files match"


def scan_forbidden(path: Path) -> Tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return False, f"forbidden pattern {pattern!r} in {path.relative_to(FORGE_ROOT)}"
    return True, "clean"


def main() -> int:
    os.chdir(PROJECT_PARENT)
    sys.path.insert(0, str(FORGE_ROOT))
    r = Results()
    print("PATCH 277 VERIFIER — MEA Convergence / Ancestry / Cost Scoring")
    print(f"Forge root: {FORGE_ROOT}")

    for file_name in REQUIRED_FILES:
        r.check(f"required_file:{file_name}", rel(file_name).exists())

    ok, detail = verify_sha256sums()
    r.check("sha256sums_match", ok, detail)

    for file_name in REQUIRED_FILES:
        if file_name.endswith(".py") and rel(file_name).exists():
            try:
                py_compile.compile(str(rel(file_name)), doraise=True)
                r.check(f"py_compile:{file_name}", True)
            except Exception as exc:
                r.check(f"py_compile:{file_name}", False, str(exc)[:200])

    for file_name in RUNTIME_SCAN_FILES:
        ok, detail = scan_forbidden(rel(file_name))
        r.check(f"runtime_boundary_scan:{file_name}", ok, detail)

    try:
        mea = importlib.import_module("rmc_engine_v1.mea")
        fixture = mea.build_144hz_test_manifest()
        convergence = mea.score_convergence(fixture, fixture)
        ancestry = mea.score_goal_ancestry(fixture, fixture)
        empty_cost = mea.score_operator_cost(fixture)
        cheap_cost = mea.score_operator_cost(["check_phase", "check_constraint"])
        expensive_cost = mea.score_operator_cost(["run_simulation", "external_search"])
        kernel_probe = mea.kernel_foundation_probe()
        r.check("mea_import_patch277_exports", True)
        r.check("convergence_formula", convergence.formula == "Omega(c_i) = satisfied_success_conditions / total_success_conditions")
        r.check("convergence_144hz_self_bounded", 0.0 <= convergence.omega <= 1.0, str(convergence.omega))
        r.check("goal_ancestry_formula", ancestry.formula == "A(c_i) = retained_root_goal_anchors across goal_ancestry")
        r.check("goal_ancestry_144hz_self_high", ancestry.ancestry_score >= 0.95, str(ancestry.ancestry_score))
        r.check("operator_cost_formula", empty_cost.formula == "K(c_i) = normalized_sum(operator_costs)")
        r.check("operator_cost_empty_zero", empty_cost.operator_cost == 0.0, str(empty_cost.operator_cost))
        r.check("operator_cost_cheap_low", cheap_cost.operator_cost < 0.20, str(cheap_cost.operator_cost))
        r.check("operator_cost_expensive_high", expensive_cost.operator_cost >= 0.90, str(expensive_cost.operator_cost))
        r.check("kernel_stage_patch277", kernel_probe["identity"]["kernel_stage"] == "scoring_foundation_read_only_patch277")
        r.check("kernel_convergence_visible", kernel_probe["identity"].get("convergence_scoring_visible") is True)
        r.check("kernel_goal_ancestry_visible", kernel_probe["identity"].get("goal_ancestry_scoring_visible") is True)
        r.check("kernel_operator_cost_visible", kernel_probe["identity"].get("operator_cost_scoring_visible") is True)
        r.check("kernel_scoring_runtime_inactive", kernel_probe["identity"].get("scoring_runtime_active") is False)
    except Exception as exc:
        r.check("mea_import_and_patch277_scoring", False, repr(exc)[:240])

    main_text = rel("main.py").read_text(encoding="utf-8")
    for route in PRESERVED_ROUTES:
        r.check(f"preserved_route:{route}", route in main_text)
    r.check("foundation_status_reports_patch277", PATCH in main_text)
    r.check("endpoint_reports_convergence_scorer", "convergence_scorer" in main_text)
    r.check("endpoint_reports_goal_ancestry_scorer", "goal_ancestry_scorer" in main_text)
    r.check("endpoint_reports_operator_cost_scorer", "operator_cost_scorer" in main_text)
    r.check("no_mea_post_route", "POST /api/mea" not in main_text and "/api/mea/seed" not in main_text and "/api/mea/seal" not in main_text)

    behavior_script = rel("scripts/test_patch277_mea_convergence_ancestry_cost.py")
    proc = subprocess.run([sys.executable, str(behavior_script)], cwd=str(FORGE_ROOT), text=True, capture_output=True)
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="")
    r.check("behavior_test_script_exit_0", proc.returncode == 0, f"returncode={proc.returncode}")

    print(f"RESULT: PATCH_277_VERIFY {'PASS' if r.failed == 0 else 'FAIL'}  Total:{r.passed + r.failed} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
