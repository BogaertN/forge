#!/usr/bin/env python3
"""Patch 286 verifier — MEA Seal Packet Audit Chain / Hash Stability Ledger Preview."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import py_compile
import subprocess
import sys

PATCH = "Patch 286 — MEA Seal Packet Audit Chain / Hash Stability Ledger Preview"
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
    "rmc_engine_v1/mea/seal_packet_preview.py",
    "rmc_engine_v1/mea/seal_packet_audit_chain.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch286_verify.py",
    "scripts/test_patch286_mea_seal_audit_chain.py",
    "scripts/README_286.md",
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
    "/api/mea/seal-readiness/status",
    "/api/mea/seal-readiness-preview",
    "/api/mea/seal-readiness-gate",
    "/api/mea/seal-packet/status",
    "/api/mea/seal-packet-preview",
    "/api/mea/seal-packet-gate",
]
NEW_ROUTES = [
    "/api/mea/seal-audit-chain/status",
    "/api/mea/seal-audit-chain-preview",
    "/api/mea/seal-audit-chain-gate",
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


print("PATCH 286 VERIFIER — MEA Seal Packet Audit Chain / Hash Stability Ledger Preview")
print(f"Forge root: {ROOT}")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

for rel in REQUIRED:
    check(f"required_file:{rel}", (ROOT / rel).exists())

ok = True
for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
    if not line.strip():
        continue
    digest, rel = line.split(maxsplit=1)
    rel = rel.strip().lstrip("*")
    p = ROOT / rel
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        ok = False
        print(f"    sha mismatch: {rel}")
check("sha256sums_match", ok, "all listed files match" if ok else "mismatch")

for rel in REQUIRED:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:120])

for rel in ["rmc_engine_v1/mea/seal_packet_audit_chain.py", "rmc_engine_v1/mea/discovery_kernel.py"]:
    text = (ROOT / rel).read_text()
    forbidden = ["subprocess", "os.system", "open(", "requests", "urllib", "sqlite3", "chromadb"]
    found = [item for item in forbidden if item in text]
    check(f"runtime_boundary_scan:{rel}", not found, "clean" if not found else str(found))

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_AUDIT_CHAIN_PATCH_ID,
    SEAL_AUDIT_CHAIN_APPROVAL_TOKEN,
    SEAL_AUDIT_CHAIN_STATUS_ROUTE,
    SEAL_AUDIT_CHAIN_PREVIEW_ROUTE,
    SEAL_AUDIT_CHAIN_POST_ROUTE,
    seal_audit_chain_boundary,
    seal_audit_chain_status,
    build_seal_audit_chain_preview,
    evaluate_seal_audit_chain_request,
    build_seal_audit_chain_gate_preview,
    build_seal_audit_chain_rejection_preview,
    kernel_identity,
)

check("patch286_id_export", SEAL_AUDIT_CHAIN_PATCH_ID == PATCH, SEAL_AUDIT_CHAIN_PATCH_ID)
check("seal_audit_token_export", SEAL_AUDIT_CHAIN_APPROVAL_TOKEN == "APPROVE_MEA_SEAL_AUDIT_CHAIN_PREVIEW")
check("seal_audit_routes_exported", {SEAL_AUDIT_CHAIN_STATUS_ROUTE, SEAL_AUDIT_CHAIN_PREVIEW_ROUTE, SEAL_AUDIT_CHAIN_POST_ROUTE} == set(NEW_ROUTES))

b = seal_audit_chain_boundary()
for key in ["non_mutating", "requires_approval_token"]:
    check(f"seal_audit_boundary_{key}", b.get(key) is True)
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "promotes_to_memory", "renders_user_output", "seal_route_available", "memory_promotion_route_available"]:
    check(f"seal_audit_boundary_no_{key}", b.get(key) is False)

status = seal_audit_chain_status()
check("seal_audit_status_ok", status.get("status") == "OK")
check("seal_audit_status_sealing_inactive", status.get("candidate_sealing_active") is False)
check("seal_audit_status_memory_inactive", status.get("memory_promotion_active") is False)
check("seal_audit_status_required_hashes", "seal_packet_hash" in status.get("required_link_fields", []))

preview = build_seal_audit_chain_preview()
check("seal_audit_preview_status_ok", preview.get("status") == "OK")
check("seal_audit_link_count_2", preview.get("audit_link_count") == 2, str(preview.get("audit_link_count")))
check("seal_audit_blocked_count_2", preview.get("blocked_audit_count") == 2, str(preview.get("blocked_audit_count")))
check("seal_audit_best_hypothesis", preview.get("best_audit_candidate_id") == "c_hypothesis_001", str(preview.get("best_audit_candidate_id")))
check("seal_audit_best_claim_hypothesis", preview.get("best_audit_claim_status") == "hypothesis", str(preview.get("best_audit_claim_status")))
check("seal_audit_link_hashes_unique", preview.get("audit_link_hashes_unique") is True)
check("seal_audit_link_hash_stability", preview.get("audit_link_hash_stability_proven") is True)
check("seal_audit_chain_hash_stability", preview.get("audit_chain_hash_stability_proven") is True)
check("seal_audit_no_execution", preview.get("seal_execution_permitted") is False)
check("seal_audit_no_route", preview.get("seal_route_available") is False)
check("seal_audit_no_memory", preview.get("memory_promotion_active") is False)
links = {link["candidate_id"]: link for link in preview.get("audit_links", [])}
check("hypothesis_audit_link_present", "c_hypothesis_001" in links)
check("branch_audit_link_present", "c_branch_derive_001" in links)
check("hypothesis_audit_link_hash_64", isinstance(links["c_hypothesis_001"].get("audit_link_hash"), str) and len(links["c_hypothesis_001"]["audit_link_hash"]) == 64)
check("hypothesis_audit_packet_hash_64", isinstance(links["c_hypothesis_001"].get("seal_packet_hash"), str) and len(links["c_hypothesis_001"]["seal_packet_hash"]) == 64)
check("hypothesis_audit_claim_hypothesis", links["c_hypothesis_001"].get("claim_status") == "hypothesis")

reject = build_seal_audit_chain_rejection_preview()
check("missing_token_rejected", reject.get("status") == "REJECTED" and reject.get("reason_code") == "approval_token_required")
approved = build_seal_audit_chain_gate_preview()
check("approved_fixture_status_ok", approved.get("status") == "OK")
check("approved_fixture_accepted", approved.get("accepted") is True)
check("approved_fixture_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_fixture_link_count_2", approved.get("audit_link_count") == 2)
check("approved_fixture_no_seal", approved.get("seals_candidates") is False and approved.get("seal_execution_permitted") is False)
check("approved_fixture_no_memory", approved.get("promotes_to_memory") is False)

kid = kernel_identity()
check("kernel_stage_patch286", kid.get("kernel_stage") == "seal_packet_audit_chain_preview_patch286", str(kid.get("kernel_stage")))
check("kernel_seal_audit_visible", kid.get("seal_audit_chain_visible") is True)
check("kernel_sealing_inactive", kid.get("sealing_active") is False)

main_text = (ROOT / "main.py").read_text()
for route in PRESERVED:
    check(f"preserved_route:{route}", route in main_text)
for route in NEW_ROUTES:
    check(f"new_route:{route}", route in main_text)
check("main_get_dispatch_seal_audit_status", "def _p286_mea_seal_audit_chain_status_v1" in main_text and "/api/mea/seal-audit-chain/status" in main_text)
check("main_get_dispatch_seal_audit_preview", "def _p286_mea_seal_audit_chain_preview_v1" in main_text and "/api/mea/seal-audit-chain-preview" in main_text)
check("main_post_dispatch_seal_audit", "def _p286_mea_seal_audit_chain_gate_post_v1" in main_text and "/api/mea/seal-audit-chain-gate" in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text and "'/api/mea/seal'" not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

res = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch286_mea_seal_audit_chain.py")], cwd=str(ROOT), text=True, capture_output=True)
print(res.stdout, end="")
if res.stderr:
    print(res.stderr, end="")
check("behavior_test_script_exit_0", res.returncode == 0, f"returncode={res.returncode}")

print(f"RESULT: PATCH_286_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
