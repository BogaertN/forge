#!/usr/bin/env python3
"""Patch 292 verifier — MEA Controlled Seal Candidate Gate."""
from __future__ import annotations

import hashlib
import os
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "main.py",
    "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/seal_engine.py",
    "rmc_engine_v1/mea/seal_candidate_gate.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch292_verify.py",
    "scripts/test_patch292_mea_seal_candidate_gate.py",
    "scripts/README_292.md",
]
FORBIDDEN_RUNTIME_STRINGS = [
    "subprocess", "os.system", "open(", "requests", "urllib", "httpx", "sqlite3",
    "chromadb", "anthropic", "openai", "langchain", "socket", "Popen",
]
passes = 0
fails = 0


def check(name: str, cond: bool, detail: object = "") -> None:
    global passes, fails
    if cond:
        passes += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        fails += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")

print("PATCH 292 VERIFIER — MEA Controlled Seal Candidate Gate")
print(f"Forge root: {ROOT}")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

for rel in REQUIRED_FILES:
    check(f"required_file:{rel}", (ROOT / rel).exists())

sha_ok = True
try:
    for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        path = ROOT / rel
        if not path.exists():
            print(f"    missing listed file: {rel}")
            sha_ok = False
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            print(f"    sha mismatch: {rel}")
            sha_ok = False
except Exception as exc:
    print(f"    sha check error: {exc}")
    sha_ok = False
check("sha256sums_match", sha_ok)

for rel in REQUIRED_FILES:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:160])

runtime_text = (ROOT / "rmc_engine_v1/mea/seal_candidate_gate.py").read_text()
violations = [term for term in FORBIDDEN_RUNTIME_STRINGS if term in runtime_text]
check("runtime_boundary_scan:rmc_engine_v1/mea/seal_candidate_gate.py", not violations, "clean" if not violations else violations)

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_CANDIDATE_GATE_APPROVAL_TOKEN,
    SEAL_CANDIDATE_GATE_FORMULA,
    SEAL_CANDIDATE_GATE_PATCH_ID,
    SEAL_CANDIDATE_GATE_POST_ROUTE,
    SEAL_CANDIDATE_GATE_SCHEMA_VERSION,
    build_seal_candidate_gate_preview,
    build_seal_candidate_gate_rejection_preview,
    evaluate_seal_candidate_gate_request,
    kernel_identity,
    seal_candidate_gate_boundary,
)

check("patch_id_export", SEAL_CANDIDATE_GATE_PATCH_ID == "Patch 292 — MEA Controlled Seal Candidate Gate", SEAL_CANDIDATE_GATE_PATCH_ID)
check("schema_export", SEAL_CANDIDATE_GATE_SCHEMA_VERSION == "mea_seal_candidate_gate_v1_patch292", SEAL_CANDIDATE_GATE_SCHEMA_VERSION)
check("route_export_post", SEAL_CANDIDATE_GATE_POST_ROUTE == "/api/mea/seal-candidate-gate")
check("token_export", SEAL_CANDIDATE_GATE_APPROVAL_TOKEN == "APPROVE_MEA_SEAL_CANDIDATE_GATE")
check("formula_mentions_candidate_hash", "CandidateHashMatch" in SEAL_CANDIDATE_GATE_FORMULA)
check("formula_mentions_packet_hash", "PacketHashAuditMatch" in SEAL_CANDIDATE_GATE_FORMULA)
check("formula_execution_false", "execution=false" in SEAL_CANDIDATE_GATE_FORMULA)

boundary = seal_candidate_gate_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_post_only", boundary.get("creates_post_routes") is True and boundary.get("creates_get_routes") is False)
check("boundary_requires_token", boundary.get("requires_approval_token") is True)
check("boundary_requires_candidate_hash", boundary.get("requires_candidate_hash_match") is True)
check("boundary_requires_packet_audit", boundary.get("requires_packet_hash_audit_match") is True)
check("boundary_response_only", boundary.get("sealed_candidate_object_response_only") is True)
check("boundary_no_real_seal_route", boundary.get("seal_route_available") is False)

rejected = build_seal_candidate_gate_rejection_preview()
accepted = build_seal_candidate_gate_preview("cg_hypothesis_001")
branch = build_seal_candidate_gate_preview("cg_branch_001")
wrong = evaluate_seal_candidate_gate_request({
    "approval_token": SEAL_CANDIDATE_GATE_APPROVAL_TOKEN,
    "candidate_id": "cg_hypothesis_001",
    "candidate_hash": "0" * 64,
})

check("missing_token_rejected", rejected.get("status") == "REJECTED")
check("missing_token_reason", rejected.get("reason_code") == "approval_token_required", rejected.get("reason_code"))
check("missing_token_no_writes", rejected.get("writes_files") is False and rejected.get("writes_memory") is False)
check("wrong_hash_rejected", wrong.get("status") == "REJECTED")
check("wrong_hash_reason", wrong.get("reason_code") == "candidate_hash_mismatch", wrong.get("reason_code"))

check("approved_ok", accepted.get("status") == "OK")
check("approved_preview_only", accepted.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_candidate", accepted.get("candidate_id") == "cg_hypothesis_001", accepted.get("candidate_id"))
check("approved_claim_hypothesis", accepted.get("claim_status") == "hypothesis", accepted.get("claim_status"))
check("approved_hash_stability", accepted.get("sealed_candidate_preview_hash_stability_proven") is True)
for key in [
    "candidate_hash_matches_packet", "seal_packet_hash_matches_audit_chain", "gate_engine_passed",
    "claim_status_allowed", "proof_debt_compatible_with_claim_status", "replay_confirmed",
]:
    check(f"approved_{key}", accepted.get(key) is True, accepted.get(key))
check("approved_no_tamper", accepted.get("tamper_detected") is False)
check("approved_no_route_mismatch", accepted.get("route_mismatch_detected") is False)
check("approved_no_seal", accepted.get("seals_candidates") is False and accepted.get("seal_execution_permitted") is False)
check("approved_no_commit", accepted.get("commits_live_candidates") is False)
check("approved_no_advance", accepted.get("advances_live_manifest") is False)
check("approved_no_memory", accepted.get("writes_memory") is False and accepted.get("promotes_to_memory") is False)
check("branch_ok", branch.get("status") == "OK")
check("branch_claim", branch.get("claim_status") == "speculative_branch", branch.get("claim_status"))

obj = accepted.get("sealed_candidate_object", {})
check("sealed_object_present", isinstance(obj, dict) and obj.get("sealed_candidate_object_created") is True)
check("sealed_object_response_only", obj.get("sealed_candidate_live") is False and obj.get("executed") is False)
for key in ["sealed_candidate_preview_hash", "candidate_hash", "seal_packet_hash", "candidate_audit_chain_hash", "gate_report_hash", "seal_object_hash"]:
    check(f"sealed_object_{key}_64", isinstance(obj.get(key), str) and len(obj.get(key)) == 64)
check("sealed_object_remaining_unknowns", obj.get("remaining_unknown_count", 0) >= 2)
check("sealed_object_permissions", len(obj.get("output_permissions", [])) >= 2)
check("sealed_object_transitions", len(obj.get("allowed_next_transitions", [])) >= 2)
check("sealed_object_no_memory", obj.get("memory_write_permitted") is False and obj.get("memory_promotion_permitted") is False)

kernel = kernel_identity()
check("kernel_stage_patch292", kernel.get("kernel_stage") == "seal_candidate_gate_preview_patch292", kernel.get("kernel_stage"))
check("kernel_gate_visible", kernel.get("seal_candidate_gate_visible") is True)
check("kernel_sealing_inactive", kernel.get("seal_route_available") is False)

main_text = (ROOT / "main.py").read_text()
check("new_route:/api/mea/seal-candidate-gate", '"/api/mea/seal-candidate-gate"' in main_text)
check("main_post_dispatch_seal_candidate_gate", "_p292_mea_seal_candidate_gate_post_v1" in main_text and '"/api/mea/seal-candidate-gate"' in main_text)
check("foundation_status_patch292", '"mode": "mea_foundation_status_patch292"' in main_text and '"current_patch": "Patch 292 — MEA Controlled Seal Candidate Gate"' in main_text)
check("foundation_reports_seal_candidate_gate", '"seal_candidate_gate": {' in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

behavior = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch292_mea_seal_candidate_gate.py")], cwd=str(ROOT), text=True, capture_output=True)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

print(f"RESULT: PATCH_292_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
