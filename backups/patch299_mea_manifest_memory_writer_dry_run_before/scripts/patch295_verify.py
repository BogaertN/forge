#!/usr/bin/env python3
"""Patch 295 verifier — MEA Controlled Live Candidate API."""
from __future__ import annotations

import ast
import hashlib
import os
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "main.py",
    "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/problem_manifest_store.py",
    "rmc_engine_v1/mea/operator_engine.py",
    "rmc_engine_v1/mea/candidate_generator.py",
    "rmc_engine_v1/mea/coherence_extension.py",
    "rmc_engine_v1/mea/gate_engine.py",
    "rmc_engine_v1/mea/live_candidates.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch295_verify.py",
    "scripts/test_patch295_mea_live_candidates.py",
    "scripts/README_295.md",
]
PROHIBITED_IMPORT_ROOTS = {
    "subprocess", "requests", "urllib", "httpx", "sqlite3", "chromadb",
    "anthropic", "openai", "langchain", "socket",
}
PROHIBITED_CALLS = {"open", "os.system", "subprocess.run", "subprocess.Popen", "Path.write_text", "Path.write_bytes"}
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


print("PATCH 295 VERIFIER — MEA Controlled Live Candidate API")
print(f"Forge root: {ROOT}")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

for rel in REQUIRED_FILES:
    check(f"required_file:{rel}", (ROOT / rel).exists())

sha_ok = True
cache_entries: list[str] = []
try:
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        if "__pycache__" in rel or rel.endswith(".pyc"):
            cache_entries.append(rel)
        path = ROOT / rel
        if not path.exists():
            print(f"    missing listed file: {rel}")
            sha_ok = False
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            print(f"    sha mismatch: {rel}")
            sha_ok = False
except Exception as exc:
    print(f"    sha check error: {exc}")
    sha_ok = False
check("sha_manifest_excludes_cache", not cache_entries, cache_entries if cache_entries else "clean")
check("sha256sums_match", sha_ok)

for rel in REQUIRED_FILES:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:160])

runtime_text = (ROOT / "rmc_engine_v1/mea/live_candidates.py").read_text(encoding="utf-8")
runtime_tree = ast.parse(runtime_text)
violations: list[str] = []
for node in ast.walk(runtime_tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root in PROHIBITED_IMPORT_ROOTS:
                violations.append(f"import:{alias.name}")
    elif isinstance(node, ast.ImportFrom):
        root = str(node.module or "").split(".", 1)[0]
        if root in PROHIBITED_IMPORT_ROOTS:
            violations.append(f"from:{node.module}")
    elif isinstance(node, ast.Call):
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            cursor = node.func
            while isinstance(cursor, ast.Attribute):
                parts.append(cursor.attr)
                cursor = cursor.value
            if isinstance(cursor, ast.Name):
                parts.append(cursor.id)
            call_name = ".".join(reversed(parts))
        if call_name in PROHIBITED_CALLS or call_name.endswith(".write_text") or call_name.endswith(".write_bytes"):
            violations.append(f"call:{call_name}")
check("runtime_boundary_scan:no_llm_shell_network_db_vault_or_direct_writes", not violations, "clean" if not violations else violations)
check("runtime_reads_verified_store", "problem_manifest_store_status" in runtime_text and "source_state_integrity_verified" in runtime_text)
check("runtime_refuses_failed_integrity", "persisted_manifest_integrity_failed" in runtime_text and "candidate_generation_executed" in runtime_text)
check("runtime_uses_real_candidate_chain", "generate_candidate_from_draft" in runtime_text and "score_generated_candidate" in runtime_text and "evaluate_candidate_gate" in runtime_text)
check("runtime_reports_missing_provenance_not_guessing", "requested_invocation_source_persisted" in runtime_text and "does not infer missing provenance" in runtime_text)
check("runtime_no_selection_or_commit", '"selection_executed": False' in runtime_text and '"commits_live_candidates": False' in runtime_text)

from rmc_engine_v1.mea import (  # noqa: E402
    LIVE_CANDIDATES_FORMULA,
    LIVE_CANDIDATES_GET_ROUTE,
    LIVE_CANDIDATES_PATCH_ID,
    LIVE_CANDIDATES_SCHEMA_VERSION,
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    build_live_candidates_payload,
    evaluate_problem_manifest_store_request,
    kernel_identity,
    live_candidates_boundary,
)

check("patch_id_export", LIVE_CANDIDATES_PATCH_ID == "Patch 295 — MEA Controlled Live Candidate API", LIVE_CANDIDATES_PATCH_ID)
check("schema_export", LIVE_CANDIDATES_SCHEMA_VERSION == "mea_live_candidates_v1_patch295", LIVE_CANDIDATES_SCHEMA_VERSION)
check("get_route_export", LIVE_CANDIDATES_GET_ROUTE == "/api/mea/candidates")
check("formula_integrity_required", "Integrity(M_t)=true" in LIVE_CANDIDATES_FORMULA)
check("formula_no_mutation", all(term in LIVE_CANDIDATES_FORMULA for term in ["commit=false", "advance=false", "seal=false", "memory=false"]))

boundary = live_candidates_boundary()
for key in ["read_only", "non_mutating", "reads_mea_runtime_state", "requires_persisted_state_integrity", "generates_candidates_from_persisted_manifest", "scores_candidates", "gates_candidates"]:
    check(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
for key in ["creates_post_routes", "writes_files", "writes_mea_runtime_state", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "renders_user_output", "score_can_override_gates", "seal_route_available"]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

with tempfile.TemporaryDirectory(prefix="patch295_verify_") as tmp:
    store = Path(tmp) / "store"
    seeded = evaluate_problem_manifest_store_request(
        {"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True},
        store_root=store,
        now_utc="2026-05-30T00:00:00+00:00",
    )
    payload = build_live_candidates_payload(store_root=store)
    check("temp_seed_ok", seeded.get("gate_status") == "PERSISTED_INITIAL_SEED", seeded.get("gate_status"))
    check("candidate_payload_ok", payload.get("status") == "OK")
    check("candidate_payload_from_verified_state", payload.get("source_state_integrity_verified") is True)
    check("candidate_payload_count_4", payload.get("candidate_count") == 4, payload.get("candidate_count"))
    check("candidate_payload_hash_stable", payload.get("candidate_set_hash_stability_proven") is True)
    check("candidate_payload_does_not_select", payload.get("selection_executed") is False and payload.get("selected_candidate_id") is None)
    check("candidate_payload_no_downstream_write", payload.get("writes_files") is False and payload.get("writes_memory") is False)

kernel = kernel_identity()
check("kernel_stage_patch295", kernel.get("kernel_stage") == "controlled_live_candidates_patch295", kernel.get("kernel_stage"))
check("kernel_live_candidates_visible", kernel.get("live_candidates_visible") is True)
check("kernel_reads_persisted_state", kernel.get("downstream_candidate_generation_reads_persisted_state") is True)
check("kernel_no_candidate_advance", kernel.get("candidate_driven_manifest_advance_active") is False)
check("kernel_no_seal", kernel.get("seal_route_available") is False)

main_text = (ROOT / "main.py").read_text(encoding="utf-8")
check("new_get_route:/api/mea/candidates", '"route_key":"mea_live_candidates"' in main_text and '"method":"GET","path":"/api/mea/candidates"' in main_text)
check("main_get_dispatch_candidates", "_p295_mea_live_candidates_get_v1" in main_text and 'elif _p249_req_path == "/api/mea/candidates":' in main_text)
check("foundation_status_patch295", '"mode": "mea_foundation_status_patch295"' in main_text and '"current_patch": "Patch 295 — MEA Controlled Live Candidate API"' in main_text)
check("foundation_reports_candidates", '"live_candidates": {' in main_text)
check("no_post_candidates_route", '"method":"POST","path":"/api/mea/candidates"' not in main_text and '_p281_req_path == "/api/mea/candidates"' not in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)

behavior = subprocess.run(
    [sys.executable, str(ROOT / "scripts/test_patch295_mea_live_candidates.py")],
    cwd=str(ROOT), text=True, capture_output=True,
    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

print(f"RESULT: PATCH_295_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
