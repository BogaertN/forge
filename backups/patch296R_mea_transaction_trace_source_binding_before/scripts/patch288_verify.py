#!/usr/bin/env python3
"""Patch 288 verifier — MEA Candidate Generator Runtime Preview."""
from __future__ import annotations
import hashlib
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "main.py",
    "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/operator_engine.py",
    "rmc_engine_v1/mea/candidate_generator.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch288_verify.py",
    "scripts/test_patch288_mea_candidate_generator.py",
    "scripts/README_288.md",
]
NEW_ROUTES = [
    "/api/mea/candidate-generator/status",
    "/api/mea/candidate-generator-preview",
    "/api/mea/candidate-generator-gate",
]
BAD_TOKENS = ["subprocess", "os.system", "open(", "requests", "urllib", "httpx", "sqlite3", "chromadb", "anthropic", "openai", "langchain"]
passes = 0
fails = 0

def check(name: str, cond: bool, detail: str = "") -> None:
    global passes, fails
    if cond:
        passes += 1
        print(f"  ✓ [PASS] {name}{' — ' + detail if detail else ''}")
    else:
        fails += 1
        print(f"  ✗ [FAIL] {name}{' — ' + detail if detail else ''}")

print("PATCH 288 VERIFIER — MEA Candidate Generator Runtime Preview")
print(f"Forge root: {ROOT}")
sys.path.insert(0, str(ROOT))

for rel in REQUIRED:
    check(f"required_file:{rel}", (ROOT / rel).exists())

sha_ok = True
if (ROOT / "SHA256SUMS.txt").exists():
    for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        path = ROOT / rel
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            sha_ok = False
            print(f"    sha mismatch or missing: {rel}")
else:
    sha_ok = False
check("sha256sums_match", sha_ok)

for rel in REQUIRED:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:160])

src = (ROOT / "rmc_engine_v1/mea/candidate_generator.py").read_text()
bad = [token for token in BAD_TOKENS if token in src]
check("runtime_boundary_scan:rmc_engine_v1/mea/candidate_generator.py", not bad, "clean" if not bad else repr(bad))

from rmc_engine_v1.mea import (
    CANDIDATE_GENERATOR_PATCH_ID,
    CANDIDATE_GENERATOR_APPROVAL_TOKEN,
    candidate_generator_status,
    candidate_generator_boundary,
    build_candidate_generator_preview,
    build_candidate_generator_gate_preview,
    build_candidate_generator_rejection_preview,
    evaluate_candidate_generator_request,
    kernel_identity,
)

check("patch_id_export", CANDIDATE_GENERATOR_PATCH_ID == "Patch 288 — MEA Candidate Generator Runtime Preview")
check("token_export", CANDIDATE_GENERATOR_APPROVAL_TOKEN == "APPROVE_MEA_CANDIDATE_GENERATOR_PREVIEW")

boundary = candidate_generator_boundary()
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seals_candidates", "promotes_to_memory", "advances_live_manifest", "commits_live_candidates"]:
    check(f"boundary_{key}_false", boundary.get(key) is False)
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_creates_post_routes", boundary.get("creates_post_routes") is True)

status = candidate_generator_status()
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("candidate_generator_visible") is True)
check("status_no_commit", status.get("live_candidate_commit_active") is False)
check("status_no_seal", status.get("candidate_sealing_active") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)

preview = build_candidate_generator_preview()
check("preview_ok", preview.get("status") == "OK")
check("preview_candidate_count_4", preview.get("candidate_count") == 4, str(preview.get("candidate_count")))
check("preview_generated_by_operator_engine", preview.get("drafts_generated_by_operator_engine") is True)
check("preview_verification_operators_applied", preview.get("verification_operators_applied") is True)
check("preview_hash_stability", preview.get("candidate_hashes_stable") is True)
check("preview_no_seal", preview.get("candidate_sealing_active") is False and preview.get("seals_candidates") is False)
check("preview_no_memory", preview.get("memory_promotion_active") is False and preview.get("promotes_to_memory") is False)

cands = {item.get("candidate_id"): item for item in preview.get("candidates", [])}
check("candidate_recall_exists", "cg_recall_001" in cands)
check("candidate_hypothesis_exists", "cg_hypothesis_001" in cands)
check("candidate_branch_exists", "cg_branch_001" in cands)
check("candidate_tamper_exists", "cg_tamper_001" in cands)
check("recall_reference_only", cands["cg_recall_001"].get("reference_only") is True)
check("recall_not_discovery", cands["cg_recall_001"].get("claim_status") == "recall")
check("hypothesis_not_verified", cands["cg_hypothesis_001"].get("claim_status") != "verified_claim", cands["cg_hypothesis_001"].get("claim_status"))
check("hypothesis_is_hypothesis", cands["cg_hypothesis_001"].get("claim_status") == "hypothesis", cands["cg_hypothesis_001"].get("claim_status"))
check("branch_not_verified", cands["cg_branch_001"].get("claim_status") != "verified_claim")
check("tamper_rejected", cands["cg_tamper_001"].get("claim_status") == "rejected")
check("tamper_containment", cands["cg_tamper_001"].get("containment_preview") is True)
for cid, item in cands.items():
    check(f"candidate_no_seal:{cid}", item.get("candidate_sealing_permitted") is False)
    check(f"candidate_no_memory:{cid}", item.get("memory_promotion_permitted") is False)
    check(f"candidate_hash_64:{cid}", isinstance(item.get("candidate_hash"), str) and len(item.get("candidate_hash")) == 64)

rej = build_candidate_generator_rejection_preview()
check("rejection_status", rej.get("status") == "REJECTED")
check("rejection_code", rej.get("reason_code") == "approval_token_required")
check("missing_token_rejected", evaluate_candidate_generator_request({}).get("status") == "REJECTED")
ok = evaluate_candidate_generator_request({"approval_token": CANDIDATE_GENERATOR_APPROVAL_TOKEN})
check("approved_status_ok", ok.get("status") == "OK")
check("approved_preview_only", ok.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_no_seal", ok.get("seals_candidates") is False)
check("approved_no_memory", ok.get("promotes_to_memory") is False)

gate = build_candidate_generator_gate_preview()
check("gate_preview_only", gate.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")

kid = kernel_identity()
check("kernel_stage_patch288", kid.get("kernel_stage") == "candidate_generator_preview_patch288", str(kid.get("kernel_stage")))
check("kernel_candidate_generator_visible", kid.get("candidate_generator_visible") is True)
check("kernel_sealing_inactive", kid.get("sealing_active") is False)

main_text = (ROOT / "main.py").read_text()
for route in NEW_ROUTES:
    check(f"new_route:{route}", route in main_text)
check("main_get_dispatch_candidate_status", "def _p288_mea_candidate_generator_status_v1" in main_text and '"/api/mea/candidate-generator/status"' in main_text)
check("main_get_dispatch_candidate_preview", "def _p288_mea_candidate_generator_preview_v1" in main_text and '"/api/mea/candidate-generator-preview"' in main_text)
check("main_post_dispatch_candidate_gate", "def _p288_mea_candidate_generator_gate_post_v1" in main_text and '"/api/mea/candidate-generator-gate"' in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

res = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch288_mea_candidate_generator.py")], cwd=str(ROOT), text=True, capture_output=True)
print(res.stdout, end="")
if res.stderr:
    print(res.stderr[:500], end="")
check("behavior_test_exit_0", res.returncode == 0, f"returncode={res.returncode}")
print(f"RESULT: PATCH_288_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes + fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
