#!/usr/bin/env python3
"""Patch 289 verifier — MEA Coherence Scorer Extension Preview."""
from __future__ import annotations
import hashlib
import os
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
    "rmc_engine_v1/mea/candidate_generator.py",
    "rmc_engine_v1/mea/coherence_extension.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch289_verify.py",
    "scripts/test_patch289_mea_coherence_extension.py",
    "scripts/README_289.md",
]
RUNTIME_SCAN = [
    "rmc_engine_v1/mea/coherence_extension.py",
]
FORBIDDEN = [
    "subprocess", "os.system", "os.popen", "eval(", "exec(", "open(",
    "requests", "urllib", "httpx", "socket", "sqlite3", "chromadb",
    "anthropic", "openai", "langchain",
]
ROUTES_GET = [
    "/api/mea/coherence-extension/status",
    "/api/mea/coherence-extension-preview",
]
ROUTES_POST = [
    "/api/mea/coherence-extension-gate",
]

passes = 0
fails = 0

def check(name: str, condition: bool, detail: object = "") -> None:
    global passes, fails
    if condition:
        passes += 1
        print(f"  ✓ [PASS] {name}{' — ' + str(detail) if detail != '' else ''}")
    else:
        fails += 1
        print(f"  ✗ [FAIL] {name}{' — ' + str(detail) if detail != '' else ''}")

print("PATCH 289 VERIFIER — MEA Coherence Scorer Extension Preview")
print(f"Forge root: {ROOT}")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

for rel in REQUIRED:
    check(f"required_file:{rel}", (ROOT / rel).exists())

sha_file = ROOT / "SHA256SUMS.txt"
sha_ok = True
if sha_file.exists():
    for line in sha_file.read_text().splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        p = ROOT / rel
        if not p.exists():
            print(f"    missing checksum target: {rel}")
            sha_ok = False
            continue
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != digest:
            print(f"    sha mismatch: {rel}")
            sha_ok = False
else:
    sha_ok = False
check("sha256sums_match", sha_ok)

for rel in REQUIRED:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:240])

for rel in RUNTIME_SCAN:
    src = (ROOT / rel).read_text()
    bad = [item for item in FORBIDDEN if item in src]
    check(f"runtime_boundary_scan:{rel}", not bad, bad if bad else "clean")

from rmc_engine_v1.mea import (
    COHERENCE_EXTENSION_APPROVAL_TOKEN,
    COHERENCE_EXTENSION_PATCH_ID,
    COHERENCE_EXTENSION_POST_ROUTE,
    COHERENCE_EXTENSION_PREVIEW_ROUTE,
    COHERENCE_EXTENSION_STATUS_ROUTE,
    build_coherence_extension_preview,
    build_foundation_kernel,
    coherence_extension_boundary,
    coherence_extension_status,
    evaluate_coherence_extension_request,
)

check("patch_id_export", COHERENCE_EXTENSION_PATCH_ID == "Patch 289 — MEA Coherence Scorer Extension Preview")
check("token_export", COHERENCE_EXTENSION_APPROVAL_TOKEN == "APPROVE_MEA_COHERENCE_EXTENSION_PREVIEW")
check("route_export_status", COHERENCE_EXTENSION_STATUS_ROUTE in ROUTES_GET)
check("route_export_preview", COHERENCE_EXTENSION_PREVIEW_ROUTE in ROUTES_GET)
check("route_export_post", COHERENCE_EXTENSION_POST_ROUTE in ROUTES_POST)

boundary = coherence_extension_boundary()
for key in ("writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui"):
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_score_can_rank", boundary.get("score_can_rank") is True)
check("boundary_score_cannot_override", boundary.get("score_can_override_gates") is False)

status = coherence_extension_status()
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("coherence_extension_visible") is True)
check("status_score_no_override", status.get("score_can_override_gates") is False)
check("status_no_seal", status.get("candidate_sealing_active") is False and status.get("seal_route_available") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)

preview = build_coherence_extension_preview()
check("preview_ok", preview.get("status") == "OK")
check("preview_candidate_count_4", preview.get("candidate_count") == 4, preview.get("candidate_count"))
check("preview_score_hash_stable", preview.get("score_hash_stability_proven") is True)
check("preview_score_can_rank", preview.get("score_can_rank") is True)
check("preview_score_no_override", preview.get("score_can_override_gates") is False)
check("preview_no_seal", preview.get("seals_candidates") is False and preview.get("candidate_sealing_active") is False)
check("preview_no_memory", preview.get("promotes_to_memory") is False and preview.get("memory_promotion_active") is False)
check("preview_uses_generated_candidates", preview.get("candidate_generator_preview_summary", {}).get("drafts_generated_by_operator_engine") is True)

scores = {item.get("candidate_id"): item for item in preview.get("scored_candidates", [])}
for cid in ("cg_recall_001", "cg_hypothesis_001", "cg_branch_001", "cg_tamper_001"):
    item = scores.get(cid, {})
    check(f"score_exists:{cid}", bool(item))
    check(f"score_no_override:{cid}", item.get("score_can_override_gate") is False)
    check(f"score_hash_64:{cid}", isinstance(item.get("score_hash"), str) and len(item.get("score_hash")) == 64)

check("recall_not_discovery", scores.get("cg_recall_001", {}).get("ranking_block_reason") == "reference_only_recall_not_discovery")
check("hypothesis_not_verified", scores.get("cg_hypothesis_001", {}).get("claim_status_after_score") == "hypothesis")
check("branch_not_verified", scores.get("cg_branch_001", {}).get("claim_status_after_score") == "speculative_branch")
check("tamper_rejected", scores.get("cg_tamper_001", {}).get("claim_status_after_score") == "rejected")
check("tamper_effective_zero", scores.get("cg_tamper_001", {}).get("effective_rank_score") == 0.0)

rej = evaluate_coherence_extension_request({})
check("missing_token_rejected", rej.get("status") == "REJECTED")
check("missing_token_reason", rej.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", rej.get("writes_files") is False and rej.get("writes_memory") is False)

ok = evaluate_coherence_extension_request({"approval_token": COHERENCE_EXTENSION_APPROVAL_TOKEN})
check("approved_status_ok", ok.get("status") == "OK")
check("approved_preview_only", ok.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_no_seal", ok.get("seals_candidates") is False)
check("approved_no_memory", ok.get("promotes_to_memory") is False)
check("approved_score_no_override", ok.get("score_can_override_gates") is False)

kernel = build_foundation_kernel()
identity = kernel.identity()
check("kernel_stage_patch289", identity.get("kernel_stage") == "coherence_extension_preview_patch289", identity.get("kernel_stage"))
check("kernel_coherence_visible", identity.get("coherence_extension_visible") is True)
check("kernel_score_no_override", identity.get("score_can_override_gates") is False)
check("kernel_sealing_inactive", identity.get("sealing_active") is False)

main_text = (ROOT / "main.py").read_text()
for route in ROUTES_GET + ROUTES_POST:
    check(f"new_route:{route}", route in main_text)
check("main_get_dispatch_coherence_status", "_p289_mea_coherence_extension_status_v1(self.path)" in main_text)
check("main_get_dispatch_coherence_preview", "_p289_mea_coherence_extension_preview_v1(self.path)" in main_text)
check("main_post_dispatch_coherence_gate", "_p289_mea_coherence_extension_gate_post_v1(req, self.path)" in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

res = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch289_mea_coherence_extension.py")], cwd=str(ROOT), text=True, capture_output=True)
print(res.stdout, end="")
if res.stderr:
    print(res.stderr[:1000], end="")
check("behavior_test_exit_0", res.returncode == 0, f"returncode={res.returncode}")

print(f"RESULT: PATCH_289_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes + fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
