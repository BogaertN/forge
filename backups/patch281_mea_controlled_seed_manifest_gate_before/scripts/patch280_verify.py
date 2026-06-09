#!/usr/bin/env python3
"""
forge/scripts/patch280_verify.py

Patch 280 verifier — MEA Read-Only API / Operator Console Visibility.
Verifies GET-only preview routes and read-only boundary constraints.
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

PATCH = "Patch 280 — MEA Read-Only API / Operator Console Visibility"
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
    "rmc_engine_v1/mea/api_preview.py",
    "scripts/patch280_verify.py",
    "scripts/test_patch280_mea_read_only_api_visibility.py",
    "scripts/README_280.md",
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

NEW_GET_ROUTES = [
    "/api/mea/problem-manifest-preview",
    "/api/mea/unknown-vector-preview",
    "/api/mea/claim-status-preview",
    "/api/mea/replay-preview",
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
    "rmc_engine_v1/mea/api_preview.py",
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
    print("PATCH 280 VERIFIER — MEA Read-Only API / Operator Console Visibility")
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
        r.check("mea_import_patch280_exports", True)
        r.check("patch280_id_export", mea.API_PREVIEW_PATCH_ID == PATCH, mea.API_PREVIEW_PATCH_ID)
        routes = mea.MEA_READ_ONLY_PREVIEW_ROUTES
        r.check("preview_route_count_4", len(routes) == 4, str(len(routes)))
        for route in NEW_GET_ROUTES:
            r.check(f"preview_route_exported:{route}", route in routes.values())
        boundary = mea.api_preview_boundary()
        r.check("api_boundary_read_only", boundary.get("read_only") is True)
        r.check("api_boundary_get_only", boundary.get("get_routes_only") is True)
        r.check("api_boundary_no_post", boundary.get("creates_post_routes") is False)
        r.check("api_boundary_no_writes", boundary.get("writes_files") is False and boundary.get("writes_memory") is False)
        r.check("api_boundary_no_llm", boundary.get("calls_llm") is False)
        r.check("api_boundary_no_shell", boundary.get("executes_shell") is False)
        r.check("api_boundary_no_seal", boundary.get("seals_candidates") is False)
        r.check("api_boundary_no_seed", boundary.get("seeds_live_manifests") is False)
        visibility = mea.operator_console_visibility_manifest()
        r.check("operator_console_visibility_4_routes", len(visibility.get("routes", [])) == 4)
        r.check("operator_console_forbidden_seal", "/api/mea/seal" in visibility.get("forbidden_routes", []))
        problem = mea.build_problem_manifest_preview()
        unknown = mea.build_unknown_vector_preview()
        claim = mea.build_claim_status_preview()
        replay = mea.build_replay_preview()
        r.check("problem_preview_ok", problem.get("status") == "OK" and problem.get("problem_manifest", {}).get("problem_id") == "144hz_substrate_status")
        r.check("unknown_preview_2_unknowns", unknown.get("unknown_vector", {}).get("unknown_count") == 2)
        r.check("claim_preview_self_recall", claim.get("self_recall_classification", {}).get("claim_status") == "recall")
        r.check("claim_preview_hypothesis_not_verified", claim.get("hypothesis_path_classification", {}).get("claim_status") == "hypothesis")
        r.check("replay_preview_noop_confirmed", replay.get("noop_replay", {}).get("replay_confirmed") is True)
        r.check("replay_preview_sealing_inactive", replay.get("sealing_active") is False and replay.get("sealing_permitted_by_endpoint") is False)
        kernel = mea.kernel_identity()
        r.check("kernel_stage_patch280", kernel.get("kernel_stage") == "read_only_api_visibility_patch280", kernel.get("kernel_stage"))
        r.check("kernel_read_only_api_visible", kernel.get("read_only_api_visible") is True)
        r.check("kernel_sealing_inactive", kernel.get("sealing_active") is False)
    except Exception as exc:
        r.check("mea_import_and_patch280_api_preview", False, repr(exc)[:240])

    main_text = rel("main.py").read_text(encoding="utf-8")
    for route in PRESERVED_ROUTES:
        r.check(f"preserved_route:{route}", route in main_text)
    for route in NEW_GET_ROUTES:
        r.check(f"new_get_route:{route}", route in main_text)
    r.check("foundation_status_reports_patch280", PATCH in main_text)
    r.check("route_manifest_lists_problem_preview", "mea_problem_manifest_preview" in main_text)
    r.check("route_manifest_lists_unknown_preview", "mea_unknown_vector_preview" in main_text)
    r.check("route_manifest_lists_claim_preview", "mea_claim_status_preview" in main_text)
    r.check("route_manifest_lists_replay_preview", "mea_replay_preview" in main_text)
    r.check("no_mea_post_route", "POST /api/mea" not in main_text and "/api/mea/seed" not in main_text and "/api/mea/seal" not in main_text and "/api/mea/candidates" not in main_text)

    behavior_script = rel("scripts/test_patch280_mea_read_only_api_visibility.py")
    proc = subprocess.run([sys.executable, str(behavior_script)], cwd=str(FORGE_ROOT), text=True, capture_output=True)
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="")
    r.check("behavior_test_script_exit_0", proc.returncode == 0, f"returncode={proc.returncode}")

    print(f"RESULT: PATCH_280_VERIFY {'PASS' if r.failed == 0 else 'FAIL'}  Total:{r.passed + r.failed} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
