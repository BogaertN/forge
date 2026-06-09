#!/usr/bin/env python3
"""Patch 283 verifier — MEA Hard Gate Report / Candidate Gate Engine Preview."""
from __future__ import annotations

import hashlib
import importlib
import py_compile
import re
import subprocess
import sys
from pathlib import Path

PATCH = "Patch 283R — MEA Hard Gate Report POST Dispatch Hotfix"
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
    "rmc_engine_v1/mea/hard_gate_report.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch283_verify.py",
    "scripts/test_patch283_mea_hard_gate_report.py",
    "scripts/README_283.md",
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
    "/api/mea/candidate-set-gate/status",
    "/api/mea/candidate-set-preview",
    "/api/mea/candidate-set-gate",
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
    print("PATCH 283R VERIFIER — MEA Hard Gate Report POST Dispatch Hotfix")
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

    boundary_scan("rmc_engine_v1/mea/hard_gate_report.py")
    boundary_scan("rmc_engine_v1/mea/discovery_kernel.py")

    try:
        mea = importlib.import_module("rmc_engine_v1.mea")
        required_exports = [
            "HARD_GATE_REPORT_PATCH_ID",
            "HARD_GATE_REPORT_APPROVAL_TOKEN",
            "hard_gate_report_status",
            "hard_gate_report_boundary",
            "build_hard_gate_report_preview",
            "evaluate_hard_gate_report_request",
        ]
        record(all(hasattr(mea, name) for name in required_exports), "mea_import_patch283_exports")
        record(mea.HARD_GATE_REPORT_PATCH_ID == PATCH, "patch283R_id_export", getattr(mea, "HARD_GATE_REPORT_PATCH_ID", ""))
        record(mea.HARD_GATE_REPORT_APPROVAL_TOKEN == "APPROVE_MEA_HARD_GATE_REPORT", "hard_gate_token_export")
        status = mea.hard_gate_report_status()
        boundary = mea.hard_gate_report_boundary()
        preview = mea.build_hard_gate_report_preview()
        reject = mea.evaluate_hard_gate_report_request({"use_fixture": True})
        approved = mea.evaluate_hard_gate_report_request({"approval_token": "APPROVE_MEA_HARD_GATE_REPORT", "use_fixture": True})
        record(status.get("status") == "OK", "hard_gate_status_ok")
        record(status.get("live_candidate_commit_active") is False, "hard_gate_status_live_commit_inactive")
        record(boundary.get("non_mutating") is True, "hard_gate_boundary_non_mutating")
        record(boundary.get("requires_approval_token") is True, "hard_gate_boundary_requires_token")
        for key in ("writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "seals_candidates", "promotes_to_memory"):
            record(boundary.get(key) is False, f"hard_gate_boundary_no_{key}")
        record(preview.get("candidate_count") == 4, "hard_gate_candidate_count_4", str(preview.get("candidate_count")))
        record(preview.get("selectable_preview_count") == 2, "hard_gate_selectable_count_2", str(preview.get("selectable_preview_count")))
        record(preview.get("rejected_count") == 1, "hard_gate_rejected_count_1", str(preview.get("rejected_count")))
        record(preview.get("reference_only_count") == 1, "hard_gate_reference_count_1", str(preview.get("reference_only_count")))
        record(preview.get("best_candidate_id") == "c_hypothesis_001", "hard_gate_best_hypothesis", str(preview.get("best_candidate_id")))
        by_id = {c.get("candidate_id"): c for c in preview.get("candidate_gate_reports", [])}
        record(by_id.get("c_hypothesis_001", {}).get("hard_gate_decision") == "PASS_PREVIEW_ONLY", "hard_gate_hypothesis_pass")
        record(by_id.get("c_branch_derive_001", {}).get("hard_gate_decision") == "PASS_BOUNDED_PREVIEW_ONLY", "hard_gate_branch_pass_bounded")
        record(by_id.get("c_recall_001", {}).get("hard_gate_decision") == "REFERENCE_ONLY", "hard_gate_recall_reference")
        record(by_id.get("c_rejected_tamper_001", {}).get("hard_gate_decision") == "REJECTED", "hard_gate_tamper_rejected")
        record(all(c.get("candidate_sealing_permitted") is False for c in preview.get("candidate_gate_reports", [])), "hard_gate_no_seal_permission")
        record(all(c.get("memory_promotion_permitted") is False for c in preview.get("candidate_gate_reports", [])), "hard_gate_no_memory_promotion")
        record(reject.get("status") == "REJECTED" and reject.get("reason_code") == "approval_token_required", "hard_gate_missing_token_rejected")
        record(approved.get("status") == "OK" and approved.get("accepted") is True, "hard_gate_fixture_approved_preview_only")
        record(approved.get("seals_candidates") is False, "hard_gate_approved_no_seal")
    except Exception as exc:
        record(False, "patch283_import_behavior", str(exc)[:240])

    main_text = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    for route in PRESERVED_ROUTES:
        record(route in main_text, f"preserved_route:{route}")
    for route in ("/api/mea/hard-gate-report/status", "/api/mea/hard-gate-report-preview"):
        record(route in main_text, f"new_get_route:{route}")
    record("/api/mea/hard-gate-report-gate" in main_text, "new_post_route:/api/mea/hard-gate-report-gate")
    record("/api/mea/candidate-hard-gate" in main_text, "alias_post_route:/api/mea/candidate-hard-gate")
    record('_p283_mea_hard_gate_report_gate_post_v1(req, self.path)' in main_text, "main_post_dispatch_hard_gate")
    record('_p281_req_path in ("/api/mea/hard-gate-report-gate", "/api/mea/candidate-hard-gate")' in main_text, "main_post_dispatch_hard_gate_alias")
    record('"/api/mea/seal"' not in main_text and "'/api/mea/seal'" not in main_text, "no_mea_seal_route")
    record('"/api/mea/candidates"' not in main_text and "'/api/mea/candidates'" not in main_text, "no_live_candidates_route")
    record("/api/mea/problem-manifest\"" not in main_text and "/api/mea/problem-manifest'" not in main_text, "no_live_problem_manifest_route")

    test_script = ROOT / "scripts/test_patch283_mea_hard_gate_report.py"
    if test_script.exists():
        proc = subprocess.run([sys.executable, str(test_script)], cwd=str(ROOT), text=True, capture_output=True)
        print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="")
        record(proc.returncode == 0, "behavior_test_script_exit_0", f"returncode={proc.returncode}")

    passed = sum(1 for ok, _, _ in results if ok)
    total = len(results)
    failed = total - passed
    print(f"RESULT: PATCH_283R_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
