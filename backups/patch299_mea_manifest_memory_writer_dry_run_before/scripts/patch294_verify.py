#!/usr/bin/env python3
"""Patch 294 verifier — MEA Controlled Problem Manifest Store."""
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
    "rmc_engine_v1/mea/seed_manifest_gate.py",
    "rmc_engine_v1/mea/manifest_advance_preview.py",
    "rmc_engine_v1/mea/problem_manifest_store.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch294_verify.py",
    "scripts/test_patch294_mea_problem_manifest_store.py",
    "scripts/README_294.md",
]
PROHIBITED_RUNTIME_STRINGS = [
    "subprocess", "os.system", "requests", "urllib", "httpx", "sqlite3",
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


print("PATCH 294 VERIFIER — MEA Controlled Problem Manifest Store")
print(f"Forge root: {ROOT}")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

for rel in REQUIRED_FILES:
    check(f"required_file:{rel}", (ROOT / rel).exists())

sha_ok = True
cache_entries = []
try:
    for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
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
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
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

runtime_text = (ROOT / "rmc_engine_v1/mea/problem_manifest_store.py").read_text()
violations = [term for term in PROHIBITED_RUNTIME_STRINGS if term in runtime_text]
check("runtime_boundary_scan:no_llm_shell_network_db_vault", not violations, "clean" if not violations else violations)
check("runtime_persistence_is_atomic", "os.replace" in runtime_text and "os.fsync" in runtime_text and "tempfile.mkstemp" in runtime_text)
check("runtime_uses_exclusive_lock", "fcntl.flock" in runtime_text and "LOCK_EX" in runtime_text)
check("runtime_fixed_store_root", '"runtime_state" / STORE_DIRECTORY_NAME' in runtime_text)
check("runtime_rejects_overwrite", "existing_manifest_conflict_no_overwrite" in runtime_text)
check("runtime_rejects_candidate_advance", "manifest_advance_not_allowed" in runtime_text)
check("runtime_disambiguates_sealed", "means_candidate_sealed" in runtime_text and "means_seal_executed" in runtime_text)

from rmc_engine_v1.mea import (  # noqa: E402
    PROBLEM_MANIFEST_GET_ROUTE,
    PROBLEM_MANIFEST_POST_ROUTE,
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    PROBLEM_MANIFEST_STORE_FORMULA,
    PROBLEM_MANIFEST_STORE_PATCH_ID,
    PROBLEM_MANIFEST_STORE_SCHEMA_VERSION,
    kernel_identity,
    problem_manifest_store_boundary,
)

check("patch_id_export", PROBLEM_MANIFEST_STORE_PATCH_ID == "Patch 294 — MEA Controlled Problem Manifest Store", PROBLEM_MANIFEST_STORE_PATCH_ID)
check("schema_export", PROBLEM_MANIFEST_STORE_SCHEMA_VERSION == "mea_problem_manifest_store_v1_patch294", PROBLEM_MANIFEST_STORE_SCHEMA_VERSION)
check("get_route_export", PROBLEM_MANIFEST_GET_ROUTE == "/api/mea/problem-manifest")
check("post_route_export", PROBLEM_MANIFEST_POST_ROUTE == "/api/mea/problem-manifest")
check("token_export", PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN == "APPROVE_MEA_PROBLEM_MANIFEST_STORE")
check("formula_mentions_atomic_store", "AtomicWrite" in PROBLEM_MANIFEST_STORE_FORMULA)
check("formula_forbids_advance", "advances_live_manifest=false" in PROBLEM_MANIFEST_STORE_FORMULA)
check("formula_forbids_memory", "writes_memory=false" in PROBLEM_MANIFEST_STORE_FORMULA)

boundary = problem_manifest_store_boundary()
for key in ["writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "renders_user_output"]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
for key in ["writes_files", "writes_mea_runtime_state", "writes_atomic_state_record", "writes_audit_receipt", "writes_rollback_plan", "uses_file_lock", "seeds_live_manifests", "allows_initial_seed_only", "rejects_overwrite"]:
    check(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
check("boundary_no_seal_route", boundary.get("seal_route_available") is False)
check("boundary_downstream_not_wired", boundary.get("downstream_candidate_generation_reads_persisted_state") is False)

kernel = kernel_identity()
check("kernel_stage_patch294", kernel.get("kernel_stage") == "problem_manifest_store_patch294", kernel.get("kernel_stage"))
check("kernel_store_visible", kernel.get("problem_manifest_store_visible") is True)
check("kernel_state_write_declared", kernel.get("boundary", {}).get("writes_files") is True)
check("kernel_seed_write_declared", kernel.get("boundary", {}).get("seeds_live_manifests") is True)
check("kernel_no_candidate_advance", kernel.get("candidate_driven_manifest_advance_active") is False)
check("kernel_no_seal", kernel.get("seal_route_available") is False)

main_text = (ROOT / "main.py").read_text()
check("new_get_route:/api/mea/problem-manifest", '"route_key":"mea_problem_manifest_store"' in main_text and '"method":"GET","path":"/api/mea/problem-manifest"' in main_text)
check("new_post_route:/api/mea/problem-manifest", '"route_key":"mea_problem_manifest_seed"' in main_text and '"method":"POST","path":"/api/mea/problem-manifest"' in main_text)
check("main_get_dispatch_problem_manifest", "_p294_mea_problem_manifest_get_v1" in main_text and 'elif _p249_req_path == "/api/mea/problem-manifest":' in main_text)
check("main_post_dispatch_problem_manifest", "_p294_mea_problem_manifest_post_v1" in main_text and 'if _p281_req_path == "/api/mea/problem-manifest":' in main_text)
check("foundation_status_patch294", '"mode": "mea_foundation_status_patch294"' in main_text and '"current_patch": "Patch 294 — MEA Controlled Problem Manifest Store"' in main_text)
check("foundation_reports_problem_store", '"problem_manifest_store": {' in main_text)
check("intentional_supersession_problem_manifest_route_now_live", '"/api/mea/problem-manifest"' in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route_yet", '"/api/mea/candidates"' not in main_text)

behavior = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch294_mea_problem_manifest_store.py")], cwd=str(ROOT), text=True, capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

print(f"RESULT: PATCH_294_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
