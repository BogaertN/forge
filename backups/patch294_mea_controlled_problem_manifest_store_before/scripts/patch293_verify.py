#!/usr/bin/env python3
"""Patch 293 verifier — MEA Live Manifest Advance Preview."""
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
    "rmc_engine_v1/mea/seal_candidate_gate.py",
    "rmc_engine_v1/mea/manifest_advance_preview.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch293_verify.py",
    "scripts/test_patch293_mea_manifest_advance_preview.py",
    "scripts/README_293.md",
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


print("PATCH 293 VERIFIER — MEA Live Manifest Advance Preview")
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

runtime_text = (ROOT / "rmc_engine_v1/mea/manifest_advance_preview.py").read_text()
violations = [term for term in FORBIDDEN_RUNTIME_STRINGS if term in runtime_text]
check("runtime_boundary_scan:rmc_engine_v1/mea/manifest_advance_preview.py", not violations, "clean" if not violations else violations)

from rmc_engine_v1.mea import (  # noqa: E402
    MANIFEST_ADVANCE_PREVIEW_FORMULA,
    MANIFEST_ADVANCE_PREVIEW_PATCH_ID,
    MANIFEST_ADVANCE_PREVIEW_ROUTE,
    MANIFEST_ADVANCE_PREVIEW_SCHEMA_VERSION,
    build_manifest_advance_preview,
    kernel_identity,
    manifest_advance_preview_boundary,
)

check("patch_id_export", MANIFEST_ADVANCE_PREVIEW_PATCH_ID == "Patch 293 — MEA Live Manifest Advance Preview", MANIFEST_ADVANCE_PREVIEW_PATCH_ID)
check("schema_export", MANIFEST_ADVANCE_PREVIEW_SCHEMA_VERSION == "mea_manifest_advance_preview_v1_patch293", MANIFEST_ADVANCE_PREVIEW_SCHEMA_VERSION)
check("route_export", MANIFEST_ADVANCE_PREVIEW_ROUTE == "/api/mea/manifest-advance-preview")
check("formula_mentions_transition", "M_(t+1)^preview" in MANIFEST_ADVANCE_PREVIEW_FORMULA)
check("formula_persistence_false", "persistence=false" in MANIFEST_ADVANCE_PREVIEW_FORMULA)

boundary = manifest_advance_preview_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_read_only", boundary.get("read_only") is True)
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_get_only", boundary.get("creates_get_routes") is True and boundary.get("creates_post_routes") is False)
check("boundary_no_real_seal_route", boundary.get("seal_route_available") is False)
check("boundary_no_live_problem_manifest_route", boundary.get("live_problem_manifest_route_available") is False)

preview = build_manifest_advance_preview()
check("preview_ok", preview.get("status") == "OK")
check("preview_old_hash_64", isinstance(preview.get("old_manifest_hash"), str) and len(preview.get("old_manifest_hash")) == 64)
check("preview_selected_sealed_hash_64", isinstance(preview.get("selected_sealed_candidate_hash"), str) and len(preview.get("selected_sealed_candidate_hash")) == 64)
check("preview_new_hash_64", isinstance(preview.get("new_manifest_hash"), str) and len(preview.get("new_manifest_hash")) == 64)
check("preview_new_hash_stable", preview.get("new_manifest_hash_stability_proven") is True)
check("preview_transition_hash_stable", preview.get("transition_preview_hash_stability_proven") is True)
check("preview_operator_history_updated", preview.get("operator_history_update", {}).get("after_count") == 1)
check("preview_claim_history_updated", preview.get("claim_status_history_update", {}).get("proposed_after") == "hypothesis")
check("preview_unknown_vector_updated", preview.get("unknown_vector_update", {}).get("proposed_after_count") == 3)
check("preview_proof_debt_preserved", preview.get("proof_debt_update", {}).get("delta") == 0.0)
check("preview_phase_path_updated", preview.get("phase_path_update", {}).get("proposed_after") == ["Phi5"])
check("preview_no_persistence", preview.get("persistence_permitted") is False and preview.get("advances_live_manifest") is False)
check("preview_no_writes", preview.get("writes_files") is False and preview.get("writes_memory") is False)

kernel = kernel_identity()
check("kernel_stage_patch293", kernel.get("kernel_stage") == "manifest_advance_preview_patch293", kernel.get("kernel_stage"))
check("kernel_manifest_advance_visible", kernel.get("manifest_advance_preview_visible") is True)
check("kernel_manifest_advance_inactive", kernel.get("live_manifest_advance_active") is False)

main_text = (ROOT / "main.py").read_text()
check("new_route:/api/mea/manifest-advance-preview", '"/api/mea/manifest-advance-preview"' in main_text)
check("route_catalog_manifest_advance_preview", '"route_key":"mea_manifest_advance_preview"' in main_text and '"stage":"manifest_advance_preview"' in main_text)
check("main_get_dispatch_manifest_advance_preview", "_p293_mea_manifest_advance_preview_v1" in main_text and '"/api/mea/manifest-advance-preview"' in main_text)
check("foundation_status_patch293", '"mode": "mea_foundation_status_patch293"' in main_text and '"current_patch": "Patch 293 — MEA Live Manifest Advance Preview"' in main_text)
check("foundation_reports_manifest_advance_preview", '"manifest_advance_preview": {' in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

behavior = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch293_mea_manifest_advance_preview.py")], cwd=str(ROOT), text=True, capture_output=True)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

print(f"RESULT: PATCH_293_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
