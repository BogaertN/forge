#!/usr/bin/env python3
"""Patch 287 verifier — MEA Operator Engine Preview."""
from __future__ import annotations
import hashlib, os, py_compile, subprocess, sys
from pathlib import Path

PATCH = "Patch 287 — MEA Operator Engine Preview"
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "main.py", "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/operator_registry.py",
    "rmc_engine_v1/mea/operator_engine.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch287_verify.py",
    "scripts/test_patch287_mea_operator_engine.py",
    "scripts/README_287.md",
]
PRESERVED_ROUTES = [
    "/api/mea/foundation-status", "/api/mea/seal-audit-chain/status",
    "/api/mea/seal-audit-chain-preview", "/api/mea/seal-audit-chain-gate",
    "/api/mea/seal-packet/status", "/api/mea/seal-packet-gate",
]
NEW_ROUTES = [
    "/api/mea/operator-engine/status",
    "/api/mea/operator-engine-preview",
    "/api/mea/operator-engine-gate",
]
passes = fails = 0

def check(name: str, cond: bool, detail: str = "") -> None:
    global passes, fails
    if cond:
        passes += 1
        print(f"  ✓ [PASS] {name}{' — '+detail if detail else ''}")
    else:
        fails += 1
        print(f"  ✗ [FAIL] {name}{' — '+detail if detail else ''}")

print(f"PATCH 287 VERIFIER — {PATCH}")
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
check("sha256sums_match", ok)

for rel in REQUIRED:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:160])

src = (ROOT / "rmc_engine_v1/mea/operator_engine.py").read_text()
bad = [x for x in ["subprocess", "os.system", "open(", "requests", "urllib", "httpx", "sqlite3", "chromadb", "anthropic", "openai", "langchain"] if x in src]
check("runtime_boundary_scan:rmc_engine_v1/mea/operator_engine.py", not bad, str(bad) if bad else "clean")

from rmc_engine_v1.mea import (
    OPERATOR_ENGINE_PATCH_ID,
    OPERATOR_ENGINE_APPROVAL_TOKEN,
    OPERATOR_ENGINE_STATUS_ROUTE,
    OPERATOR_ENGINE_PREVIEW_ROUTE,
    OPERATOR_ENGINE_POST_ROUTE,
    OPERATOR_ENGINE_FORMULA,
    operator_engine_boundary,
    operator_engine_status,
    build_operator_engine_preview,
    build_operator_engine_rejection_preview,
    evaluate_operator_engine_request,
    run_operator_preview,
    build_144hz_test_manifest,
    canonical_hash,
    kernel_identity,
)

check("patch287_id_export", OPERATOR_ENGINE_PATCH_ID == PATCH, OPERATOR_ENGINE_PATCH_ID)
check("token_export", OPERATOR_ENGINE_APPROVAL_TOKEN == "APPROVE_MEA_OPERATOR_ENGINE_PREVIEW")
check("routes_exported", {OPERATOR_ENGINE_STATUS_ROUTE, OPERATOR_ENGINE_PREVIEW_ROUTE, OPERATOR_ENGINE_POST_ROUTE} == set(NEW_ROUTES))
check("formula_export", OPERATOR_ENGINE_FORMULA == "d_i = O_gen(M_t); c_i = O_verify ∘ d_i")

boundary = operator_engine_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates",
    "promotes_to_memory", "renders_user_output", "seal_route_available",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False)
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_creates_post_routes", boundary.get("creates_post_routes") is True)
check("boundary_requires_token", boundary.get("requires_approval_token") is True)
check("boundary_draft_not_candidate", boundary.get("draft_is_not_candidate") is True)

status = operator_engine_status()
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("operator_engine_visible") is True)
check("status_no_live_execution", status.get("live_operator_execution_active") is False)
check("status_no_seal", status.get("draft_sealing_active") is False)
check("status_no_render", status.get("draft_rendering_active") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)

preview = build_operator_engine_preview()
check("preview_ok", preview.get("status") == "OK")
check("preview_draft_count_3", preview.get("draft_count") == 3, str(preview.get("draft_count")))
check("preview_executed_count_3", preview.get("executed_draft_count") == 3, str(preview.get("executed_draft_count")))
for item in preview.get("draft_results", []):
    op = item.get("operator_id", "?")
    check(f"draft_is_draft:{op}", item.get("is_draft") is True)
    check(f"draft_not_candidate:{op}", item.get("is_candidate") is False)
    check(f"draft_unsealed:{op}", item.get("sealed") is False)
    check(f"draft_no_render:{op}", item.get("render_permitted") is False)
    check(f"draft_no_memory:{op}", item.get("memory_promotion_permitted") is False)
    check(f"draft_hash_64:{op}", isinstance(item.get("draft_hash"), str) and len(item.get("draft_hash")) == 64)

parent = build_144hz_test_manifest()
noop = run_operator_preview(parent, "noop_recall")
check("noop_executed", noop.draft_executed is True)
check("noop_hash_equals_parent", noop.draft_hash == canonical_hash(parent))
check("noop_not_candidate", noop.is_candidate is False)

hyp = run_operator_preview(parent, "hypothesize", {"hypothesis_id":"harmonic_from_90hz", "hypothesis_text":"144 Hz harmonic hypothesis", "confidence":0.35})
check("hyp_executed", hyp.draft_executed is True)
check("hyp_not_verified_claim", hyp.draft_manifest.get("claim_status") != "verified_claim")
check("hyp_not_candidate", hyp.is_candidate is False)

repeat = build_operator_engine_preview()
check("preview_hash_stability", [x.get("draft_hash") for x in preview.get("draft_results", [])] == [x.get("draft_hash") for x in repeat.get("draft_results", [])])
check("preview_id_stability", [x.get("draft_id") for x in preview.get("draft_results", [])] == [x.get("draft_id") for x in repeat.get("draft_results", [])])

rejected = build_operator_engine_rejection_preview()
check("missing_token_rejected", rejected.get("status") == "REJECTED" and rejected.get("reason_code") == "approval_token_required")
approved = evaluate_operator_engine_request({"approval_token": OPERATOR_ENGINE_APPROVAL_TOKEN})
check("approved_status_ok", approved.get("status") == "OK")
check("approved_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_no_seal", approved.get("seals_candidates") is False)
check("approved_no_memory", approved.get("promotes_to_memory") is False)

kid = kernel_identity()
check("kernel_stage_patch287", kid.get("kernel_stage") == "operator_engine_preview_patch287", str(kid.get("kernel_stage")))
check("kernel_operator_engine_visible", kid.get("operator_engine_visible") is True)
check("kernel_sealing_inactive", kid.get("sealing_active") is False)

main_text = (ROOT / "main.py").read_text()
for route in PRESERVED_ROUTES:
    check(f"preserved_route:{route}", route in main_text)
for route in NEW_ROUTES:
    check(f"new_route:{route}", route in main_text)
check("main_get_dispatch_operator_status", "_p287_mea_operator_engine_status_v1" in main_text and '"/api/mea/operator-engine/status"' in main_text)
check("main_get_dispatch_operator_preview", "_p287_mea_operator_engine_preview_v1" in main_text and '"/api/mea/operator-engine-preview"' in main_text)
check("main_post_dispatch_operator_gate", "_p287_mea_operator_engine_gate_post_v1" in main_text and '"/api/mea/operator-engine-gate"' in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

res = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch287_mea_operator_engine.py")], cwd=str(ROOT), text=True, capture_output=True)
print(res.stdout, end="")
if res.stderr:
    print(res.stderr[:500], end="")
check("behavior_test_exit_0", res.returncode == 0, f"returncode={res.returncode}")

print(f"RESULT: PATCH_287_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
