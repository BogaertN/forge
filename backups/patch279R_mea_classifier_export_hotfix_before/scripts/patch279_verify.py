#!/usr/bin/env python3
"""
forge/scripts/patch279_verify.py

Patch 279 verifier — MEA Claim Status Classifier.
Verifies the additive read-only claim classifier without mutating Forge state.
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

PATCH = "Patch 279 — MEA Claim Status Classifier"
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
    "rmc_engine_v1/mea/operator_registry.py",
    "rmc_engine_v1/mea/replay_engine.py",
    "rmc_engine_v1/mea/claim_status_classifier.py",
    "scripts/patch279_verify.py",
    "scripts/test_patch279_mea_claim_status_classifier.py",
    "scripts/README_279.md",
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
    "rmc_engine_v1/mea/claim_status_classifier.py",
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
    print("PATCH 279 VERIFIER — MEA Claim Status Classifier")
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
        noop = mea.replay_candidate(fixture, "noop_recall", {}, expected_candidate_hash=mea.canonical_hash(fixture))
        recall_class = mea.classify_claim_status(fixture, fixture, replay_result=noop)
        ops = [
            {"operator_id": "branch", "theta_k": {"branch_label": "substrate-vs-harmonic", "branch_goal": fixture.goal, "branch_unknown": ""}},
            {"operator_id": "hypothesize", "theta_k": {"hypothesis_id": "harmonic_from_90hz", "hypothesis_text": "144 Hz is a harmonic hypothesis derived from 90 Hz via the golden ratio relation.", "confidence": 0.35}},
            {"operator_id": "derive", "theta_k": {"derived_fact": "144 Hz remains hypothesis-bound until direct measurement or a sealed derivation chain exists.", "proof_debt_delta": 0.30}},
        ]
        preview = mea.replay_operator_path(fixture, ops)
        path = mea.replay_operator_path(fixture, ops, expected_final_hash=preview.produced_final_hash)
        candidate = mea.from_dict(path.final_manifest)
        hypothesis_class = mea.classify_claim_status(fixture, candidate, replay_result=path)
        tampered = mea.replay_candidate(fixture, "hypothesize", {"hypothesis_id": "harmonic_from_90hz", "hypothesis_text": "144 Hz is already empirically verified in myelin.", "confidence": 0.35}, expected_candidate_hash=preview.produced_final_hash)
        rejected_class = mea.classify_claim_status(fixture, fixture, replay_result=tampered)
        taxonomy = mea.claim_status_taxonomy()
        kernel_probe = mea.kernel_foundation_probe()
        r.check("mea_import_patch279_exports", True)
        r.check("classifier_formula", mea.CLAIM_STATUS_CLASSIFIER_FORMULA == "ClaimStatus(c*) = f(B, I, Replay, Omega, D, gates)")
        r.check("claim_status_taxonomy_has_all_statuses", len(taxonomy.get("statuses", {})) >= 12, str(len(taxonomy.get("statuses", {}))))
        r.check("self_recall_classification", recall_class.claim_status == "recall", recall_class.claim_status)
        r.check("self_recall_not_discovery", "discovery" in " ".join(recall_class.cannot_render_as))
        r.check("144hz_path_classified_hypothesis", hypothesis_class.claim_status == "hypothesis", hypothesis_class.claim_status)
        r.check("144hz_path_not_verified_claim", "verified fact" in " ".join(hypothesis_class.cannot_render_as))
        r.check("replay_failure_classified_rejected", rejected_class.claim_status == "rejected", rejected_class.claim_status)
        r.check("rejected_not_user_visible", rejected_class.user_visible is False)
        r.check("kernel_stage_patch279", kernel_probe["identity"]["kernel_stage"] == "claim_status_foundation_read_only_patch279")
        r.check("kernel_classifier_visible", kernel_probe["identity"].get("claim_status_classifier_visible") is True)
        r.check("kernel_sealing_inactive", kernel_probe["identity"].get("sealing_active") is False)
    except Exception as exc:
        r.check("mea_import_and_patch279_classifier", False, repr(exc)[:240])

    main_text = rel("main.py").read_text(encoding="utf-8")
    for route in PRESERVED_ROUTES:
        r.check(f"preserved_route:{route}", route in main_text)
    r.check("foundation_status_reports_patch279", PATCH in main_text)
    r.check("endpoint_reports_claim_status_classifier", "claim_status_classifier" in main_text)
    r.check("endpoint_reports_classifier_formula", "classifier_formula" in main_text)
    r.check("no_mea_post_route", "POST /api/mea" not in main_text and "/api/mea/seed" not in main_text and "/api/mea/seal" not in main_text)

    behavior_script = rel("scripts/test_patch279_mea_claim_status_classifier.py")
    proc = subprocess.run([sys.executable, str(behavior_script)], cwd=str(FORGE_ROOT), text=True, capture_output=True)
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="")
    r.check("behavior_test_script_exit_0", proc.returncode == 0, f"returncode={proc.returncode}")

    print(f"RESULT: PATCH_279_VERIFY {'PASS' if r.failed == 0 else 'FAIL'}  Total:{r.passed + r.failed} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
