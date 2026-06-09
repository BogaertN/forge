#!/usr/bin/env python3
"""
forge/scripts/patch276_verify.py

Patch 276 verifier — MEA Scoring Foundations.
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
from typing import List, Tuple

PATCH = "Patch 276 — MEA Scoring Foundations"
FORGE_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "main.py",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/unknown_detector.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "rmc_engine_v1/mea/proof_debt_scorer.py",
    "rmc_engine_v1/mea/information_gain_scorer.py",
    "scripts/patch276_verify.py",
    "scripts/test_patch276_mea_scoring_foundations.py",
    "scripts/README_276.md",
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
    "rmc_engine_v1/mea/proof_debt_scorer.py",
    "rmc_engine_v1/mea/information_gain_scorer.py",
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
    os.chdir(FORGE_ROOT)
    sys.path.insert(0, str(FORGE_ROOT))
    r = Results()
    print(f"PATCH 276 VERIFIER — MEA Scoring Foundations")
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
        proof_score = mea.score_proof_debt(fixture)
        info_score = mea.score_information_gain(fixture, fixture)
        kernel_probe = mea.kernel_foundation_probe()
        r.check("mea_import_patch276_exports", True)
        r.check("proof_debt_formula", proof_score.formula == "B(c_i) = 1 - E(c_i)")
        r.check("proof_debt_144hz_is_085", proof_score.proof_debt == 0.85, str(proof_score.proof_debt))
        r.check("evidence_support_144hz_is_015", proof_score.evidence_support == 0.15, str(proof_score.evidence_support))
        r.check("proof_debt_blocks_verified_claim", proof_score.blocks_verified_claim is True)
        r.check("proof_debt_blocks_derived_claim", proof_score.blocks_derived_claim is True)
        r.check("information_gain_formula", info_score.formula == "I(c_i) = delta-K + delta-Q + delta-X")
        r.check("information_gain_self_is_zero", info_score.information_gain == 0.0, str(info_score.information_gain))
        r.check("information_gain_self_is_recall", info_score.is_noop_recall is True)
        r.check("kernel_stage_patch276", kernel_probe["identity"]["kernel_stage"] == "scoring_foundation_read_only")
        r.check("kernel_scoring_foundation_visible", kernel_probe["identity"].get("scoring_foundation_visible") is True)
        r.check("kernel_scoring_runtime_inactive", kernel_probe["identity"].get("scoring_runtime_active") is False)
    except Exception as exc:
        r.check("mea_import_and_scoring", False, repr(exc)[:240])

    main_text = rel("main.py").read_text(encoding="utf-8")
    for route in PRESERVED_ROUTES:
        r.check(f"preserved_route:{route}", route in main_text)
    r.check("foundation_status_reports_patch276", "Patch 276 — MEA Scoring Foundations" in main_text)
    r.check("endpoint_reports_proof_debt_scorer", "proof_debt_scorer" in main_text)
    r.check("endpoint_reports_information_gain_scorer", "information_gain_scorer" in main_text)
    r.check("no_mea_post_route", "POST /api/mea" not in main_text and "def _p276_mea_post" not in main_text and "/api/mea/seed" not in main_text and "/api/mea/seal" not in main_text)

    behavior_script = rel("scripts/test_patch276_mea_scoring_foundations.py")
    proc = subprocess.run([sys.executable, str(behavior_script)], cwd=str(FORGE_ROOT), text=True, capture_output=True)
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="")
    r.check("behavior_test_script_exit_0", proc.returncode == 0, f"returncode={proc.returncode}")

    print(f"RESULT: PATCH_276_VERIFY {'PASS' if r.failed == 0 else 'FAIL'}  Total:{r.passed + r.failed} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
