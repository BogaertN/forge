#!/usr/bin/env python3
"""Patch 296 verifier — MEA Persisted-State Seal / Advance Transaction Preflight."""
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
    "rmc_engine_v1/mea/live_candidates.py",
    "rmc_engine_v1/mea/seal_transaction_preflight.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch296_verify.py",
    "scripts/test_patch296_mea_seal_transaction_preflight.py",
    "scripts/README_296.md",
]
PROHIBITED_IMPORT_ROOTS = {
    "subprocess", "requests", "urllib", "httpx", "sqlite3", "chromadb",
    "anthropic", "openai", "langchain", "socket",
}
PROHIBITED_CALLS = {"open", "os.system", "subprocess.run", "subprocess.Popen", "Path.write_text", "Path.write_bytes"}
passes = 0
fails = 0


def check(name: str, condition: bool, detail: object = "") -> None:
    global passes, fails
    if condition:
        passes += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        fails += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


print("PATCH 296 VERIFIER — MEA Persisted-State Seal / Advance Transaction Preflight")
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

runtime_text = (ROOT / "rmc_engine_v1/mea/seal_transaction_preflight.py").read_text(encoding="utf-8")
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
for text_name, marker in [
    ("reads_verified_persisted_state", "problem_manifest_store_status"),
    ("uses_live_candidate_chain", "build_live_candidates_payload"),
    ("requires_explicit_selection", "submitted_candidate_id_and_hash_not_rank"),
    ("compiles_seal_packet_preview", "transaction_seal_packet_hash"),
    ("compiles_audit_chain_preview", "transaction_audit_chain_hash"),
    ("compiles_next_manifest", "proposed_new_manifest_hash"),
    ("compiles_receipt_preview", "receipt_preview_hash"),
    ("compiles_rollback_preview", "rollback_preview_hash"),
    ("defers_output_binding", "OUTPUT_HASH_BINDING_DEFERRED"),
]:
    check(f"runtime_{text_name}", marker in runtime_text)

from rmc_engine_v1.mea import (  # noqa: E402
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
    TRANSACTION_PREFLIGHT_FORMULA,
    TRANSACTION_PREFLIGHT_PATCH_ID,
    TRANSACTION_PREFLIGHT_POST_ROUTE,
    TRANSACTION_PREFLIGHT_SCHEMA_VERSION,
    build_live_candidates_payload,
    evaluate_problem_manifest_store_request,
    evaluate_seal_transaction_preflight_request,
    kernel_identity,
    transaction_preflight_boundary,
)

check("patch_id_export", TRANSACTION_PREFLIGHT_PATCH_ID == "Patch 296 — MEA Persisted-State Seal / Advance Transaction Preflight", TRANSACTION_PREFLIGHT_PATCH_ID)
check("schema_export", TRANSACTION_PREFLIGHT_SCHEMA_VERSION == "mea_seal_transaction_preflight_v1_patch296", TRANSACTION_PREFLIGHT_SCHEMA_VERSION)
check("route_export", TRANSACTION_PREFLIGHT_POST_ROUTE == "/api/mea/seal-transaction-preflight")
check("token_export", TRANSACTION_PREFLIGHT_APPROVAL_TOKEN == "APPROVE_MEA_SEAL_TRANSACTION_PREFLIGHT")
check("formula_persisted_binding", "Integrity(M_t)" in TRANSACTION_PREFLIGHT_FORMULA and "HashBind(M_t,c*)" in TRANSACTION_PREFLIGHT_FORMULA)
check("formula_no_execution", all(term in TRANSACTION_PREFLIGHT_FORMULA for term in ["execute=false", "persist=false", "memory=false"]))

boundary = transaction_preflight_boundary()
for key in [
    "non_mutating", "creates_post_routes", "requires_approval_token", "requires_explicit_candidate_selection",
    "requires_source_manifest_hash_match", "requires_source_state_content_hash_match", "reads_mea_runtime_state",
    "requires_persisted_state_integrity", "uses_live_candidate_api_chain", "compiles_transaction_seal_packet_preview",
    "compiles_transaction_audit_chain_preview", "compiles_manifest_advance_preview", "compiles_receipt_preview", "compiles_rollback_preview",
]:
    check(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
for key in [
    "creates_get_routes", "score_can_select", "score_can_override_gates", "writes_files", "writes_mea_runtime_state",
    "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory",
    "renders_user_output", "seal_route_available",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

with tempfile.TemporaryDirectory(prefix="patch296_verify_") as tmp:
    store = Path(tmp) / "state"
    seeded = evaluate_problem_manifest_store_request(
        {"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True},
        store_root=store,
        now_utc="2026-05-30T00:00:00+00:00",
    )
    live = build_live_candidates_payload(store_root=store)
    row = next(item for item in live["candidates"] if item["candidate_id"] == "cg_hypothesis_001")
    req = {
        "approval_token": TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
        "source_manifest_hash": live["source_manifest_hash"],
        "source_state_content_hash": live["source_state_content_hash"],
        "candidate_id": row["candidate_id"],
        "candidate_hash": row["candidate_hash"],
        "candidate_set_hash": live["candidate_set_hash"],
        "gate_report_hash": row["gate_report_hash"],
    }
    payload = evaluate_seal_transaction_preflight_request(req, store_root=store)
    check("temp_seed_ok", seeded.get("gate_status") == "PERSISTED_INITIAL_SEED", seeded.get("gate_status"))
    check("preflight_payload_ok", payload.get("status") == "OK" and payload.get("gate_status") == "ACCEPTED_PREFLIGHT_ONLY")
    check("preflight_source_bound", payload.get("source_state_integrity_verified") is True and payload.get("source_manifest_hash_matches_persisted_state") is True and payload.get("source_state_content_hash_matches_persisted_state") is True)
    check("preflight_candidate_bound", payload.get("candidate_generated_from_persisted_state") is True and payload.get("candidate_hash_matches_live_report") is True)
    check("preflight_explicit_not_rank", payload.get("candidate_id") == "cg_hypothesis_001" and payload.get("highest_ranked_candidate_id") == "cg_branch_001" and payload.get("ranked_candidate_auto_selected") is False)
    check("preflight_hash_stable", payload.get("transaction_hash_stability_proven") is True)
    check("preflight_non_mutating", payload.get("writes_files") is False and payload.get("advances_live_manifest") is False and payload.get("executes_seal") is False and payload.get("writes_memory") is False)

kernel = kernel_identity()
check("kernel_stage_patch296", kernel.get("kernel_stage") == "persisted_state_transaction_preflight_patch296", kernel.get("kernel_stage"))
check("kernel_transaction_visible", kernel.get("transaction_preflight_visible") is True)
check("kernel_transaction_route", kernel.get("transaction_preflight_post_route") == "/api/mea/seal-transaction-preflight")
check("kernel_no_real_seal", kernel.get("seal_route_available") is False)

main_text = (ROOT / "main.py").read_text(encoding="utf-8")
check("route_catalog_transaction_preflight", '"route_key":"mea_seal_transaction_preflight"' in main_text and '"method":"POST","path":"/api/mea/seal-transaction-preflight"' in main_text)
check("main_post_dispatch_transaction_preflight", "_p296_mea_seal_transaction_preflight_post_v1" in main_text and '_p281_req_path == "/api/mea/seal-transaction-preflight"' in main_text)
check("foundation_status_patch296", '"mode": "mea_foundation_status_patch296"' in main_text and '"current_patch": "Patch 296 — MEA Persisted-State Seal / Advance Transaction Preflight"' in main_text)
check("foundation_reports_transaction_preflight", '"seal_transaction_preflight": {' in main_text and '"seal_transaction_preflight": True' in main_text)
check("no_real_mea_seal_route", '"path":"/api/mea/seal"' not in main_text and '_p281_req_path == "/api/mea/seal"' not in main_text)

behavior = subprocess.run(
    [sys.executable, str(ROOT / "scripts/test_patch296_mea_seal_transaction_preflight.py")],
    cwd=str(ROOT), text=True, capture_output=True,
    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

print(f"RESULT: PATCH_296_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
