#!/usr/bin/env python3
"""Patch 291 verifier — MEA Seal Engine Dry-Run."""
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
    "rmc_engine_v1/mea/candidate_generator.py",
    "rmc_engine_v1/mea/gate_engine.py",
    "rmc_engine_v1/mea/seal_engine.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch291_verify.py",
    "scripts/test_patch291_mea_seal_engine.py",
    "scripts/README_291.md",
]
NEW_GET_ROUTES = ["/api/mea/seal-engine/status", "/api/mea/seal-engine-dry-run"]
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


print("PATCH 291 VERIFIER — MEA Seal Engine Dry-Run")
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

runtime_text = (ROOT / "rmc_engine_v1/mea/seal_engine.py").read_text()
violations = [term for term in FORBIDDEN_RUNTIME_STRINGS if term in runtime_text]
check("runtime_boundary_scan:rmc_engine_v1/mea/seal_engine.py", not violations, "clean" if not violations else violations)

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_ENGINE_PATCH_ID,
    SEAL_ENGINE_SCHEMA_VERSION,
    SEAL_ENGINE_STATUS_ROUTE,
    SEAL_ENGINE_DRY_RUN_ROUTE,
    SEAL_ENGINE_FORMULA,
    SEAL_ENGINE_ALGORITHM_REFERENCE,
    SEAL_OBJECT_REQUIRED_FIELDS,
    build_seal_engine_dry_run,
    seal_engine_boundary,
    seal_engine_status,
    kernel_identity,
)

check("patch_id_export", SEAL_ENGINE_PATCH_ID == "Patch 291 — MEA Seal Engine Dry-Run", SEAL_ENGINE_PATCH_ID)
check("schema_export", SEAL_ENGINE_SCHEMA_VERSION == "mea_seal_engine_dry_run_v1_patch291", SEAL_ENGINE_SCHEMA_VERSION)
check("route_export_status", SEAL_ENGINE_STATUS_ROUTE == "/api/mea/seal-engine/status")
check("route_export_dry_run", SEAL_ENGINE_DRY_RUN_ROUTE == "/api/mea/seal-engine-dry-run")
check("formula_mentions_gate_results", "GateResults" in SEAL_ENGINE_FORMULA)
check("algorithm_reference_algorithm4", "Algorithm 4" in SEAL_ENGINE_ALGORITHM_REFERENCE)
check("required_fields_manifest_hash", "manifest_hash" in SEAL_OBJECT_REQUIRED_FIELDS)
check("required_fields_remaining_unknowns", "remaining_unknowns" in SEAL_OBJECT_REQUIRED_FIELDS)
check("required_fields_output_permissions", "output_permissions" in SEAL_OBJECT_REQUIRED_FIELDS)

boundary = seal_engine_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates",
    "executes_seal", "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_dry_run_only", boundary.get("dry_run_only") is True)
check("boundary_no_post_routes", boundary.get("creates_post_routes") is False and boundary.get("post_routes") == [])
check("boundary_seal_route_unavailable", boundary.get("seal_route_available") is False)
check("boundary_no_memory_route", boundary.get("memory_promotion_route_available") is False)

status = seal_engine_status()
dry_run = build_seal_engine_dry_run()
objects = dry_run.get("seal_objects", [])
objects_by_id = {o.get("candidate_id"): o for o in objects}
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("seal_engine_visible") is True)
check("status_patch291", status.get("current_patch") == SEAL_ENGINE_PATCH_ID, status.get("current_patch"))
check("status_no_execution", status.get("seal_execution_permitted") is False)
check("status_no_route", status.get("seal_route_available") is False)
check("status_no_memory", status.get("memory_write_active") is False and status.get("memory_promotion_active") is False)
check("dry_run_ok", dry_run.get("status") == "OK")
check("dry_run_object_count_2", dry_run.get("seal_object_count") == 2, dry_run.get("seal_object_count"))
check("dry_run_blocked_count_2", dry_run.get("blocked_candidate_count") == 2, dry_run.get("blocked_candidate_count"))
check("dry_run_best_hypothesis", dry_run.get("best_dry_run_candidate_id") == "cg_hypothesis_001", dry_run.get("best_dry_run_candidate_id"))
check("dry_run_hash_stability", dry_run.get("seal_object_hash_stability_proven") is True)
check("dry_run_no_execution", dry_run.get("seal_execution_permitted") is False and dry_run.get("executed") is False)
check("dry_run_no_seal", dry_run.get("seals_candidates") is False and dry_run.get("candidate_sealing_active") is False)
check("dry_run_no_advance", dry_run.get("advances_live_manifest") is False and dry_run.get("live_manifest_advance_active") is False)
check("dry_run_no_memory", dry_run.get("writes_memory") is False and dry_run.get("memory_promotion_active") is False)

for cid, status_expected in {"cg_hypothesis_001": "hypothesis", "cg_branch_001": "speculative_branch"}.items():
    obj = objects_by_id.get(cid, {})
    check(f"seal_object_exists:{cid}", bool(obj))
    check(f"seal_object_status:{cid}", obj.get("seal_status") == "DRY_RUN_ONLY_NOT_EXECUTED", obj.get("seal_status"))
    check(f"claim_status_preserved:{cid}", obj.get("claim_status") == status_expected, obj.get("claim_status"))
    check(f"seal_hash_64:{cid}", isinstance(obj.get("seal_object_hash"), str) and len(obj.get("seal_object_hash")) == 64)
    check(f"packet_hash_64:{cid}", isinstance(obj.get("normalized_packet_hash"), str) and len(obj.get("normalized_packet_hash")) == 64)
    check(f"manifest_hash_64:{cid}", isinstance(obj.get("manifest_hash"), str) and len(obj.get("manifest_hash")) == 64)
    check(f"gate_results_present:{cid}", isinstance(obj.get("gate_results"), dict) and obj.get("gate_results", {}).get("candidate_id") == cid)
    check(f"gate_report_hash_64:{cid}", isinstance(obj.get("gate_report_hash"), str) and len(obj.get("gate_report_hash")) == 64)
    check(f"remaining_unknowns:{cid}", obj.get("remaining_unknown_count", 0) >= 2)
    check(f"output_permissions:{cid}", len(obj.get("output_permissions", [])) >= 2)
    check(f"allowed_transitions:{cid}", len(obj.get("allowed_next_transitions", [])) >= 2)
    check(f"exec_false:{cid}", obj.get("executed") is False and obj.get("seal_execution_permitted") is False)
    check(f"sealed_false:{cid}", obj.get("sealed_candidate") is False)
    check(f"commit_false:{cid}", obj.get("live_candidate_commit_permitted") is False)
    check(f"advance_false:{cid}", obj.get("live_manifest_advance_permitted") is False)
    check(f"memory_false:{cid}", obj.get("memory_write_permitted") is False and obj.get("memory_promotion_permitted") is False)

kernel = kernel_identity()
check("kernel_stage_patch291", kernel.get("kernel_stage") == "seal_engine_dry_run_patch291", kernel.get("kernel_stage"))
check("kernel_seal_engine_visible", kernel.get("seal_engine_visible") is True)
check("kernel_sealing_inactive", kernel.get("sealing_active") is False)

main_text = (ROOT / "main.py").read_text()
for route in NEW_GET_ROUTES:
    check(f"new_route:{route}", route in main_text)
check("main_get_dispatch_seal_engine_status", "_p291_mea_seal_engine_status_v1" in main_text and '"/api/mea/seal-engine/status"' in main_text)
check("main_get_dispatch_seal_engine_dry_run", "_p291_mea_seal_engine_dry_run_v1" in main_text and '"/api/mea/seal-engine-dry-run"' in main_text)
check("foundation_status_patch291", '"mode": "mea_foundation_status_patch291"' in main_text and '"current_patch": "Patch 291 — MEA Seal Engine Dry-Run"' in main_text)
check("foundation_reports_seal_engine", '"seal_engine": {' in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)
check("no_post_dispatch_seal_engine", '"/api/mea/seal-engine-gate"' not in main_text)

behavior = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch291_mea_seal_engine.py")], cwd=str(ROOT), text=True, capture_output=True)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

print(f"RESULT: PATCH_291_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
