#!/usr/bin/env python3
"""Patch 282 verifier — MEA Candidate Set Preview/Gate."""
from __future__ import annotations

import hashlib
import importlib
import py_compile
import re
import subprocess
import sys
from pathlib import Path

PATCH = "Patch 282 — MEA Candidate Set Preview/Gate"
ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "main.py",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/unknown_detector.py",
    "rmc_engine_v1/mea/proof_debt_scorer.py",
    "rmc_engine_v1/mea/information_gain_scorer.py",
    "rmc_engine_v1/mea/convergence_scorer.py",
    "rmc_engine_v1/mea/goal_ancestry_scorer.py",
    "rmc_engine_v1/mea/operator_cost_scorer.py",
    "rmc_engine_v1/mea/operator_registry.py",
    "rmc_engine_v1/mea/replay_engine.py",
    "rmc_engine_v1/mea/claim_status_classifier.py",
    "rmc_engine_v1/mea/api_preview.py",
    "rmc_engine_v1/mea/seed_manifest_gate.py",
    "rmc_engine_v1/mea/candidate_set_gate.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch282_verify.py",
    "scripts/test_patch282_mea_candidate_set_gate.py",
    "scripts/README_282.md",
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
    "/api/mea/problem-manifest-preview",
    "/api/mea/unknown-vector-preview",
    "/api/mea/claim-status-preview",
    "/api/mea/replay-preview",
    "/api/mea/seed-manifest-gate/status",
    "/api/mea/seed-manifest-gate",
]

FORBIDDEN_RUNTIME_PATTERNS = [
    r"subprocess\.",
    r"os\.system",
    r"Popen\(",
    r"eval\(",
    r"exec\(",
    r"requests\.",
    r"urllib\.request",
    r"open\(",
    r"Path\([^\n]*\)\.write_text",
    r"\.write_text\(",
    r"\.write_bytes\(",
]

results: list[tuple[bool, str, str]] = []


def record(ok: bool, name: str, detail: str = "") -> None:
    results.append((ok, name, detail))
    mark = "✓ [PASS]" if ok else "✗ [FAIL]"
    extra = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{extra}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sha256sums() -> None:
    sums = ROOT / "SHA256SUMS.txt"
    if not sums.exists():
        record(False, "sha256sums_match", "SHA256SUMS.txt missing")
        return
    ok = True
    details = []
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        path = ROOT / rel
        if not path.exists():
            ok = False
            details.append(f"missing {rel}")
            continue
        actual = sha256(path)
        if actual != expected:
            ok = False
            details.append(f"mismatch {rel}")
    record(ok, "sha256sums_match", "all listed files match" if ok else "; ".join(details[:5]))


def boundary_scan(rel: str) -> None:
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    hits = []
    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        if re.search(pattern, text):
            hits.append(pattern)
    record(not hits, f"runtime_boundary_scan:{rel}", "clean" if not hits else ", ".join(hits))


def main() -> int:
    print(f"PATCH 282 VERIFIER — MEA Candidate Set Preview/Gate")
    print(f"Forge root: {ROOT}")
    sys.path.insert(0, str(ROOT))

    for rel in REQUIRED:
        record((ROOT / rel).exists(), f"required_file:{rel}")

    check_sha256sums()

    for rel in REQUIRED:
        if rel.endswith(".py") and (ROOT / rel).exists():
            try:
                py_compile.compile(str(ROOT / rel), doraise=True)
                record(True, f"py_compile:{rel}")
            except Exception as exc:
                record(False, f"py_compile:{rel}", str(exc)[:180])

    boundary_scan("rmc_engine_v1/mea/candidate_set_gate.py")
    boundary_scan("rmc_engine_v1/mea/discovery_kernel.py")

    try:
        mea = importlib.import_module("rmc_engine_v1.mea")
        required_exports = [
            "CANDIDATE_SET_GATE_PATCH_ID",
            "CANDIDATE_SET_GATE_APPROVAL_TOKEN",
            "candidate_set_gate_status",
            "candidate_set_gate_boundary",
            "build_candidate_set_preview",
            "evaluate_candidate_set_request",
        ]
        record(all(hasattr(mea, name) for name in required_exports), "mea_import_patch282_exports")
        record(mea.CANDIDATE_SET_GATE_PATCH_ID == PATCH, "patch282_id_export", getattr(mea, "CANDIDATE_SET_GATE_PATCH_ID", ""))
        record(mea.CANDIDATE_SET_GATE_APPROVAL_TOKEN == "APPROVE_MEA_CANDIDATE_SET_GATE", "candidate_set_gate_token_export")
        status = mea.candidate_set_gate_status()
        boundary = mea.candidate_set_gate_boundary()
        preview = mea.build_candidate_set_preview()
        reject = mea.evaluate_candidate_set_request({"use_fixture": True})
        approved = mea.evaluate_candidate_set_request({"approval_token": "APPROVE_MEA_CANDIDATE_SET_GATE", "use_fixture": True})
        record(status.get("status") == "OK", "candidate_set_status_ok")
        record(status.get("live_candidate_commit_active") is False, "candidate_set_status_live_commit_inactive")
        record(boundary.get("non_mutating") is True, "candidate_set_boundary_non_mutating")
        record(boundary.get("requires_approval_token") is True, "candidate_set_boundary_requires_token")
        for key in ("writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "seals_candidates", "promotes_to_memory"):
            record(boundary.get(key) is False, f"candidate_set_boundary_no_{key}")
        record(preview.get("candidate_count") == 4, "candidate_preview_count_4", str(preview.get("candidate_count")))
        record(preview.get("accepted_preview_count", 0) >= 1, "candidate_preview_has_accepted_candidate", str(preview.get("accepted_preview_count")))
        record(preview.get("rejected_count", 0) >= 1, "candidate_preview_has_rejected_candidate", str(preview.get("rejected_count")))
        record(preview.get("reference_only_count", 0) >= 1, "candidate_preview_has_reference_candidate", str(preview.get("reference_only_count")))
        by_id = {c.get("candidate_id"): c for c in preview.get("candidates", [])}
        record(by_id.get("c_hypothesis_001", {}).get("claim_status_report", {}).get("claim_status") == "hypothesis", "candidate_hypothesis_not_verified")
        record(by_id.get("c_recall_001", {}).get("gate_status") == "REFERENCE_ONLY", "candidate_recall_reference_only")
        record(by_id.get("c_rejected_tamper_001", {}).get("gate_status") == "REJECTED", "candidate_tamper_rejected")
        record(all(c.get("candidate_sealing_permitted") is False for c in preview.get("candidates", [])), "candidate_preview_no_seal_permission")
        record(reject.get("status") == "REJECTED" and reject.get("reason_code") == "approval_token_required", "candidate_set_missing_token_rejected")
        record(approved.get("status") == "OK" and approved.get("accepted") is True, "candidate_set_fixture_approved_preview_only")
        record(approved.get("seals_candidates") is False, "candidate_set_approved_no_seal")
    except Exception as exc:
        record(False, "patch282_import_behavior", str(exc)[:240])

    main_text = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    for route in PRESERVED_ROUTES:
        record(route in main_text, f"preserved_route:{route}")
    for route in ("/api/mea/candidate-set-gate/status", "/api/mea/candidate-set-preview"):
        record(route in main_text, f"new_get_route:{route}")
    record("/api/mea/candidate-set-gate" in main_text, "new_post_route:/api/mea/candidate-set-gate")
    record("/api/mea/candidate-preview-gate" in main_text, "alias_post_route:/api/mea/candidate-preview-gate")
    record("/api/mea/seal" not in main_text, "no_mea_seal_route")
    record("/api/mea/candidates" not in main_text, "no_live_candidates_route")
    record("/api/mea/problem-manifest\"" not in main_text and "/api/mea/problem-manifest'" not in main_text, "no_live_problem_manifest_route")

    test_script = ROOT / "scripts/test_patch282_mea_candidate_set_gate.py"
    if test_script.exists():
        proc = subprocess.run([sys.executable, str(test_script)], cwd=str(ROOT), text=True, capture_output=True)
        print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="")
        record(proc.returncode == 0, "behavior_test_script_exit_0", f"returncode={proc.returncode}")

    passed = sum(1 for ok, _, _ in results if ok)
    total = len(results)
    failed = total - passed
    print(f"RESULT: PATCH_282_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
