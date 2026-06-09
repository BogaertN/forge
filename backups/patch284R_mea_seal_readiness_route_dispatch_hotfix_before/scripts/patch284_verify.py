#!/usr/bin/env python3
"""Patch 284 verifier — MEA Seal Readiness Preview / Seal Readiness Report."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import py_compile
import subprocess
import sys

PATCH = "Patch 284 — MEA Seal Readiness Preview / Seal Readiness Report"
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
    "rmc_engine_v1/mea/seal_readiness.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch284_verify.py",
    "scripts/test_patch284_mea_seal_readiness.py",
    "scripts/README_284.md",
    "SHA256SUMS.txt",
]
PRESERVED = [
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
    "/api/mea/hard-gate-report/status",
    "/api/mea/hard-gate-report-preview",
    "/api/mea/hard-gate-report-gate",
]

passes = 0
fails = 0

def check(name: str, cond: bool, detail: str = ""):
    global passes, fails
    if cond:
        passes += 1
        print(f"  ✓ [PASS] {name}{' — ' + detail if detail else ''}")
    else:
        fails += 1
        print(f"  ✗ [FAIL] {name}{' — ' + detail if detail else ''}")

print("PATCH 284 VERIFIER — MEA Seal Readiness Preview / Seal Readiness Report")
print(f"Forge root: {ROOT}")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

for rel in REQUIRED:
    check(f"required_file:{rel}", (ROOT/rel).exists())

# sha256
ok = True
for line in (ROOT/"SHA256SUMS.txt").read_text().splitlines():
    if not line.strip():
        continue
    digest, rel = line.split(maxsplit=1)
    rel = rel.strip().lstrip("*")
    p = ROOT/rel
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        ok = False
        print(f"    sha mismatch: {rel}")
check("sha256sums_match", ok, "all listed files match" if ok else "mismatch")

for rel in REQUIRED:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT/rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:120])

# boundary source scans
for rel in ["rmc_engine_v1/mea/seal_readiness.py", "rmc_engine_v1/mea/discovery_kernel.py"]:
    text = (ROOT/rel).read_text()
    forbidden = ["subprocess", "os.system", "open(", "requests", "urllib", "sqlite3", "chromadb"]
    found = [item for item in forbidden if item in text]
    check(f"runtime_boundary_scan:{rel}", not found, "clean" if not found else str(found))

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_READINESS_PATCH_ID,
    SEAL_READINESS_APPROVAL_TOKEN,
    SEAL_READINESS_STATUS_ROUTE,
    SEAL_READINESS_PREVIEW_ROUTE,
    SEAL_READINESS_POST_ROUTE,
    SEAL_READINESS_ALIAS_ROUTE,
    seal_readiness_boundary,
    seal_readiness_status,
    build_seal_readiness_preview,
    evaluate_seal_readiness_request,
    build_seal_readiness_gate_preview,
    build_seal_readiness_rejection_preview,
    kernel_identity,
)

check("patch284_id_export", SEAL_READINESS_PATCH_ID == PATCH, SEAL_READINESS_PATCH_ID)
check("seal_readiness_token_export", SEAL_READINESS_APPROVAL_TOKEN == "APPROVE_MEA_SEAL_READINESS_REPORT")
b = seal_readiness_boundary()
for key in ["non_mutating", "requires_approval_token"]:
    check(f"seal_readiness_boundary_{key}", b.get(key) is True)
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "seals_candidates", "promotes_to_memory", "renders_user_output", "seal_route_available", "memory_promotion_route_available"]:
    check(f"seal_readiness_boundary_no_{key}", b.get(key) is False)

status = seal_readiness_status()
check("seal_readiness_status_ok", status.get("status") == "OK")
check("seal_readiness_status_live_commit_inactive", status.get("live_candidate_commit_active") is False)
check("seal_readiness_status_sealing_inactive", status.get("candidate_sealing_active") is False)
check("seal_readiness_status_memory_inactive", status.get("memory_promotion_active") is False)

preview = build_seal_readiness_preview()
check("seal_preview_status_ok", preview.get("status") == "OK")
check("seal_preview_candidate_count_4", preview.get("candidate_count") == 4, str(preview.get("candidate_count")))
check("seal_preview_ready_count_2", preview.get("seal_ready_preview_count") == 2, str(preview.get("seal_ready_preview_count")))
check("seal_preview_reference_count_1", preview.get("reference_only_count") == 1)
check("seal_preview_rejected_count_1", preview.get("rejected_count") == 1)
check("seal_preview_best_hypothesis", preview.get("best_seal_ready_candidate_id") == "c_hypothesis_001", str(preview.get("best_seal_ready_candidate_id")))
check("seal_preview_no_execution", preview.get("seal_execution_permitted") is False)
check("seal_preview_no_route", preview.get("seal_route_available") is False)
check("seal_preview_no_memory", preview.get("memory_promotion_active") is False)
reports = {r["candidate_id"]: r for r in preview.get("seal_readiness_reports", [])}
check("recall_not_sealable", reports["c_recall_001"]["readiness_decision"] == "NOT_SEALABLE_REFERENCE_ONLY")
check("hypothesis_seal_ready_preview", reports["c_hypothesis_001"]["readiness_decision"] == "SEAL_READY_PREVIEW_ONLY")
check("hypothesis_not_executed", reports["c_hypothesis_001"]["seal_execution_permitted"] is False)
check("hypothesis_payload_hash_present", isinstance(reports["c_hypothesis_001"].get("future_seal_payload_hash"), str) and len(reports["c_hypothesis_001"]["future_seal_payload_hash"]) == 64)
check("branch_bounded_ready", reports["c_branch_derive_001"]["readiness_decision"] == "BOUNDED_SEAL_READY_PREVIEW_ONLY")
check("tamper_not_sealable", reports["c_rejected_tamper_001"]["readiness_decision"] == "NOT_SEALABLE_REJECTED")
check("all_no_seal_execution", all(r.get("seal_execution_permitted") is False for r in reports.values()))

reject = build_seal_readiness_rejection_preview()
check("missing_token_rejected", reject.get("status") == "REJECTED" and reject.get("reason_code") == "approval_token_required")
approved = build_seal_readiness_gate_preview()
check("approved_fixture_status_ok", approved.get("status") == "OK")
check("approved_fixture_accepted", approved.get("accepted") is True)
check("approved_fixture_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_fixture_candidate_count_4", approved.get("candidate_count") == 4)
check("approved_fixture_no_seal", approved.get("seals_candidates") is False and approved.get("seal_execution_permitted") is False)
check("approved_fixture_no_memory", approved.get("promotes_to_memory") is False)

kid = kernel_identity()
check("kernel_stage_patch284", kid.get("kernel_stage") == "seal_readiness_preview_patch284", str(kid.get("kernel_stage")))
check("kernel_seal_readiness_visible", kid.get("seal_readiness_visible") is True)
check("kernel_sealing_inactive", kid.get("sealing_active") is False)

main_text = (ROOT/"main.py").read_text()
for route in PRESERVED:
    check(f"preserved_route:{route}", route in main_text)
for route in ["/api/mea/seal-readiness/status", "/api/mea/seal-readiness-preview", "/api/mea/seal-readiness-gate", "/api/mea/seal-preview-gate"]:
    check(f"new_route:{route}", route in main_text)
check("main_post_dispatch_seal_readiness", "_p284_mea_seal_readiness_gate_post_v1" in main_text and "/api/mea/seal-readiness-gate" in main_text)
check("main_post_dispatch_seal_alias", "/api/mea/seal-preview-gate" in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text and "'/api/mea/seal'" not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

# Run behavior script
res = subprocess.run([sys.executable, str(ROOT/"scripts/test_patch284_mea_seal_readiness.py")], cwd=str(ROOT), text=True, capture_output=True)
print(res.stdout, end="")
if res.stderr:
    print(res.stderr, end="")
check("behavior_test_script_exit_0", res.returncode == 0, f"returncode={res.returncode}")

print(f"RESULT: PATCH_284_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
