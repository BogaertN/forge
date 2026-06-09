#!/usr/bin/env python3
"""Patch 299 verifier — MEA Manifest Memory Writer Dry-Run."""
from __future__ import annotations

import hashlib
import importlib
import py_compile
import subprocess
import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

REQUIRED = [
    "main.py",
    "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "rmc_engine_v1/mea/manifest_memory_writer.py",
    "scripts/README_299.md",
    "scripts/patch299_verify.py",
    "scripts/test_patch299_mea_manifest_memory_writer_dry_run.py",
]

passed = 0
failed = 0


def check(name: str, condition: bool, detail: object | None = None) -> None:
    global passed, failed
    if condition:
        passed += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        failed += 1
        suffix = f" — observed={detail!r}" if detail is not None else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


def verify_sha_manifest() -> bool:
    manifest = FORGE_ROOT / "SHA256SUMS.txt"
    ok = True
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        path = FORGE_ROOT / rel
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            ok = False
    return ok


def main() -> int:
    print("PATCH 299 VERIFIER — MEA Manifest Memory Writer Dry-Run")
    print(f"Forge root: {FORGE_ROOT}")
    for rel in REQUIRED:
        check(f"required_file:{rel}", (FORGE_ROOT / rel).is_file())
    manifest_text = (FORGE_ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8")
    check("sha_manifest_excludes_cache", "__pycache__" not in manifest_text and ".pyc" not in manifest_text, "clean")
    check("sha256sums_match", verify_sha_manifest())
    for rel in REQUIRED:
        if rel.endswith(".py"):
            try:
                py_compile.compile(str(FORGE_ROOT / rel), doraise=True)
                check(f"py_compile:{rel}", True)
            except Exception as exc:
                check(f"py_compile:{rel}", False, str(exc))

    mea = importlib.import_module("rmc_engine_v1.mea")
    check("patch_id_export", mea.MANIFEST_MEMORY_WRITER_PATCH_ID == "Patch 299 — MEA Manifest Memory Writer Dry-Run", mea.MANIFEST_MEMORY_WRITER_PATCH_ID)
    check("schema_export", mea.MANIFEST_MEMORY_WRITER_SCHEMA_VERSION == "mea_manifest_memory_writer_dry_run_v1_patch299", mea.MANIFEST_MEMORY_WRITER_SCHEMA_VERSION)
    check("status_route_export", mea.MANIFEST_MEMORY_WRITER_STATUS_ROUTE == "/api/mea/memory-writer/status")
    check("dry_run_route_export", mea.MANIFEST_MEMORY_WRITER_DRY_RUN_ROUTE == "/api/mea/memory-writer-dry-run")
    boundary = mea.manifest_memory_writer_boundary()
    check("boundary_requires_replay", boundary.get("requires_live_trace_replay_verification") is True)
    check("boundary_rmc_adapter_only", boundary.get("existing_rmc_memory_writer_invoked") is False)
    for key in (
        "writes_files", "writes_mea_runtime_state", "writes_memory", "writes_rmc_memory",
        "writes_jsonl_ledger", "writes_chroma", "writes_identity_vault", "calls_llm",
        "executes_shell", "performs_network_io", "commits_live_candidates",
        "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory",
        "renders_user_output", "creates_memory_capsule", "mints_contribution_tokens",
        "canonical_seal_route_available", "seal_route_available",
    ):
        check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

    module_text = (FORGE_ROOT / "rmc_engine_v1/mea/manifest_memory_writer.py").read_text(encoding="utf-8")
    forbidden = {
        "subprocess_execution": "subprocess.",
        "os_system_execution": "os.system",
        "socket_io": "socket.",
        "requests_network": "requests.",
        "chromadb_access": "chromadb",
        "identity_vault_import": "from identity_vault",
        "file_write_open_mode": "open(\"w",
    }
    for name, token in forbidden.items():
        check(f"memory_writer_runtime_forbidden_scan:{name}", token not in module_text)

    main_text = (FORGE_ROOT / "main.py").read_text(encoding="utf-8")
    check("main_status_dispatch", "/api/mea/memory-writer/status" in main_text and "_p299_mea_memory_writer_status_v1" in main_text)
    check("main_post_dispatch", "/api/mea/memory-writer-dry-run" in main_text and "_p299_mea_memory_writer_dry_run_post_v1" in main_text)
    check("foundation_current_patch_299", "Patch 299 — MEA Manifest Memory Writer Dry-Run" in main_text)
    check("no_canonical_mea_seal_route", 'elif _p281_req_path == "/api/mea/seal"' not in main_text)
    kernel = mea.kernel_identity()
    check("kernel_stage_patch299", kernel.get("kernel_stage") == "manifest_memory_writer_dry_run_patch299", kernel.get("kernel_stage"))
    check("kernel_memory_writer_visible", kernel.get("manifest_memory_writer_visible") is True)
    check("kernel_memory_writer_non_mutating", kernel.get("manifest_memory_writer_writes_memory") is False and kernel.get("manifest_memory_writer_promotes_to_memory") is False)

    behavior = subprocess.run([sys.executable, str(FORGE_ROOT / "scripts/test_patch299_mea_manifest_memory_writer_dry_run.py")], capture_output=True, text=True)
    print(behavior.stdout, end="")
    if behavior.stderr:
        print(behavior.stderr, end="", file=sys.stderr)
    check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")
    print(f"RESULT: PATCH_299_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed+failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
