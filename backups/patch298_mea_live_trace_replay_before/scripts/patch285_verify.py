#!/usr/bin/env python3
"""Patch 285 verifier — MEA Seal Packet Preview / Future Seal Payload Normalizer."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import py_compile
import subprocess
import sys

PATCH = "Patch 285 — MEA Seal Packet Preview / Future Seal Payload Normalizer"
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
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch285_verify.py",
    "scripts/test_patch285_mea_seal_packet_preview.py",
    "scripts/README_285.md",
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
]
NEW_ROUTES = [
    "/api/mea/seal-packet/status",
    "/api/mea/seal-packet-preview",
    "/api/mea/seal-packet-gate",
    "/api/mea/future-seal-payload-gate",
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


print("PATCH 285 VERIFIER — MEA Seal Packet Preview / Future Seal Payload Normalizer")
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

for rel in ["rmc_engine_v1/mea/seal_packet_preview.py", "rmc_engine_v1/mea/discovery_kernel.py"]:
    text = (ROOT / rel).read_text()
    forbidden = ["subprocess", "os.system", "open(", "requests", "urllib", "sqlite3", "chromadb"]
    found = [item for item in forbidden if item in text]
    check(f"runtime_boundary_scan:{rel}", not found, "clean" if not found else str(found))

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_PACKET_PATCH_ID,
    SEAL_PACKET_APPROVAL_TOKEN,
    SEAL_PACKET_STATUS_ROUTE,
    SEAL_PACKET_PREVIEW_ROUTE,
    SEAL_PACKET_POST_ROUTE,
    SEAL_PACKET_ALIAS_ROUTE,
    seal_packet_boundary,
    seal_packet_status,
    build_seal_packet_preview,
    evaluate_seal_packet_request,
    build_seal_packet_gate_preview,
    build_seal_packet_rejection_preview,
    kernel_identity,
)

check("patch285_id_export", SEAL_PACKET_PATCH_ID == PATCH, SEAL_PACKET_PATCH_ID)
check("seal_packet_token_export", SEAL_PACKET_APPROVAL_TOKEN == "APPROVE_MEA_SEAL_PACKET_PREVIEW")
check("seal_packet_routes_exported", {SEAL_PACKET_STATUS_ROUTE, SEAL_PACKET_PREVIEW_ROUTE, SEAL_PACKET_POST_ROUTE, SEAL_PACKET_ALIAS_ROUTE} == set(NEW_ROUTES))

b = seal_packet_boundary()
for key in ["non_mutating", "requires_approval_token"]:
    check(f"seal_packet_boundary_{key}", b.get(key) is True)
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "seals_candidates", "promotes_to_memory", "renders_user_output", "seal_route_available", "memory_promotion_route_available"]:
    check(f"seal_packet_boundary_no_{key}", b.get(key) is False)

status = seal_packet_status()
check("seal_packet_status_ok", status.get("status") == "OK")
check("seal_packet_status_sealing_inactive", status.get("candidate_sealing_active") is False)
check("seal_packet_status_memory_inactive", status.get("memory_promotion_active") is False)
check("seal_packet_status_required_hash", "packet_hash" in status.get("required_packet_fields", []))

preview = build_seal_packet_preview()
check("seal_packet_preview_status_ok", preview.get("status") == "OK")
check("seal_packet_preview_count_2", preview.get("packet_preview_count") == 2, str(preview.get("packet_preview_count")))
check("seal_packet_preview_blocked_count_2", preview.get("blocked_packet_count") == 2, str(preview.get("blocked_packet_count")))
check("seal_packet_best_hypothesis", preview.get("best_packet_candidate_id") == "c_hypothesis_001", str(preview.get("best_packet_candidate_id")))
check("seal_packet_best_claim_hypothesis", preview.get("best_packet_claim_status") == "hypothesis", str(preview.get("best_packet_claim_status")))
check("seal_packet_hashes_unique", preview.get("packet_hashes_unique") is True)
check("seal_packet_hash_stability", preview.get("packet_hash_stability_proven") is True)
check("seal_packet_no_execution", preview.get("seal_execution_permitted") is False)
check("seal_packet_no_route", preview.get("seal_route_available") is False)
check("seal_packet_no_memory", preview.get("memory_promotion_active") is False)
packets = {p["source_candidate_id"]: p for p in preview.get("seal_packets", [])}
check("hypothesis_packet_present", "c_hypothesis_001" in packets)
check("branch_packet_present", "c_branch_derive_001" in packets)
check("hypothesis_packet_hash_64", isinstance(packets["c_hypothesis_001"].get("packet_hash"), str) and len(packets["c_hypothesis_001"]["packet_hash"]) == 64)
check("hypothesis_packet_body_hash_match", packets["c_hypothesis_001"].get("packet_hash") == packets["c_hypothesis_001"].get("packet_body", {}).get("packet_hash"))
check("hypothesis_packet_claim_hypothesis", packets["c_hypothesis_001"].get("packet_body", {}).get("claim_status") == "hypothesis")
check("hypothesis_packet_no_seal", packets["c_hypothesis_001"].get("seal_execution_permitted") is False)
check("hypothesis_packet_no_memory", packets["c_hypothesis_001"].get("memory_promotion_permitted") is False)

reject = build_seal_packet_rejection_preview()
check("missing_token_rejected", reject.get("status") == "REJECTED" and reject.get("reason_code") == "approval_token_required")
approved = build_seal_packet_gate_preview()
check("approved_fixture_status_ok", approved.get("status") == "OK")
check("approved_fixture_accepted", approved.get("accepted") is True)
check("approved_fixture_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_fixture_packet_count_2", approved.get("packet_preview_count") == 2)
check("approved_fixture_no_seal", approved.get("seals_candidates") is False and approved.get("seal_execution_permitted") is False)
check("approved_fixture_no_memory", approved.get("promotes_to_memory") is False)

kid = kernel_identity()
check("kernel_stage_patch285", kid.get("kernel_stage") == "seal_packet_preview_patch285", str(kid.get("kernel_stage")))
check("kernel_seal_packet_visible", kid.get("seal_packet_preview_visible") is True)
check("kernel_sealing_inactive", kid.get("sealing_active") is False)

main_text = (ROOT / "main.py").read_text()
for route in PRESERVED:
    check(f"preserved_route:{route}", route in main_text)
for route in NEW_ROUTES:
    check(f"new_route:{route}", route in main_text)
check("main_get_dispatch_seal_packet_status", "def _p285_mea_seal_packet_status_v1" in main_text and "/api/mea/seal-packet/status" in main_text)
check("main_get_dispatch_seal_packet_preview", "def _p285_mea_seal_packet_preview_v1" in main_text and "/api/mea/seal-packet-preview" in main_text)
check("main_post_dispatch_seal_packet", "def _p285_mea_seal_packet_gate_post_v1" in main_text and "/api/mea/seal-packet-gate" in main_text)
check("main_post_dispatch_seal_packet_alias", "/api/mea/future-seal-payload-gate" in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text and "'/api/mea/seal'" not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

res = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch285_mea_seal_packet_preview.py")], cwd=str(ROOT), text=True, capture_output=True)
print(res.stdout, end="")
if res.stderr:
    print(res.stderr, end="")
check("behavior_test_script_exit_0", res.returncode == 0, f"returncode={res.returncode}")

print(f"RESULT: PATCH_285_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
