#!/usr/bin/env python3
"""
forge/scripts/patch275_verify.py

Patch 275 verifier — MEA / Forge Discovery Kernel Foundation.
Run from HOME unless instructed otherwise:
    cd ~
    python forge/scripts/patch275_verify.py

Optional:
    python forge/scripts/patch275_verify.py --forge-root /path/to/forge
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import os
import py_compile
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

FORBIDDEN_IN_MEA = (
    "subprocess",
    "os.system",
    "Popen",
    "socket",
    "requests",
    "urllib.request",
    "eval(",
    "exec(",
    "open(",
    ".write(",
    "sqlite3",
    "chromadb",
)

REQUIRED_FILES = [
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/unknown_detector.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch275_verify.py",
    "scripts/test_patch275_mea_foundation.py",
    "scripts/README_275.md",
    "SHA256SUMS.txt",
]

PRESERVED_ROUTES = [
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
]


def find_forge_root(cli_value: str | None) -> Path:
    if cli_value:
        return Path(cli_value).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "forge" / "main.py").exists():
        return (cwd / "forge").resolve()
    if (cwd / "main.py").exists() and (cwd / "rmc_engine_v1").exists():
        return cwd
    home_forge = Path.home() / "forge"
    if (home_forge / "main.py").exists():
        return home_forge.resolve()
    raise SystemExit("Could not locate Forge root. Run from cd ~ or pass --forge-root /path/to/forge")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def record(results: List[Tuple[str, str]], ok: bool, name: str, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"  {'✓' if ok else '✗'} [{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    results.append((status, name))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()
    forge = find_forge_root(args.forge_root)
    print("PATCH 275R VERIFIER — MEA / Forge Discovery Kernel Foundation Visibility")
    print(f"Forge root: {forge}")
    results: List[Tuple[str, str]] = []

    for rel in REQUIRED_FILES:
        record(results, (forge / rel).exists(), f"required_file:{rel}")

    # Check SHA256SUMS format against patch files that exist.
    sums = forge / "SHA256SUMS.txt"
    if sums.exists():
        ok = True
        bad: List[str] = []
        for raw in sums.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            parts = raw.split(maxsplit=1)
            if len(parts) != 2:
                ok = False; bad.append(raw); continue
            expected, rel = parts
            rel = rel.lstrip("*")
            target = forge.parent / rel if rel.startswith("forge/") else forge / rel
            if not target.exists() or sha256(target) != expected:
                ok = False; bad.append(rel)
        record(results, ok, "sha256sums_match", ", ".join(bad[:5]) if bad else "")

    # Compile only changed files.
    compile_targets = [
        forge / "main.py",
        forge / "rmc_engine_v1/mea/__init__.py",
        forge / "rmc_engine_v1/mea/manifest_schema.py",
        forge / "rmc_engine_v1/mea/unknown_detector.py",
        forge / "rmc_engine_v1/mea/discovery_kernel.py",
        forge / "scripts/patch275_verify.py",
        forge / "scripts/test_patch275_mea_foundation.py",
    ]
    for path in compile_targets:
        try:
            py_compile.compile(str(path), doraise=True)
            record(results, True, f"py_compile:{path.relative_to(forge)}")
        except Exception as exc:
            record(results, False, f"py_compile:{path.relative_to(forge)}", str(exc))

    # Static boundary scan: no writes/shell/network in MEA runtime modules.
    for rel in ("rmc_engine_v1/mea/manifest_schema.py", "rmc_engine_v1/mea/unknown_detector.py", "rmc_engine_v1/mea/discovery_kernel.py", "rmc_engine_v1/mea/__init__.py"):
        text = (forge / rel).read_text(encoding="utf-8")
        hits = [token for token in FORBIDDEN_IN_MEA if token in text]
        record(results, not hits, f"runtime_boundary_scan:{rel}", ", ".join(hits))

    # Import and behavior smoke.
    sys.path.insert(0, str(forge))
    try:
        mea = importlib.import_module("rmc_engine_v1.mea")
        manifest = mea.build_144hz_test_manifest()
        vector = mea.detect_unknowns(manifest)
        kernel_probe = mea.kernel_foundation_probe()
        record(results, True, "mea_import_and_144hz_fixture")
        record(results, vector.unknown_count == 2, "144hz_explicit_unknown_count_is_2", str(vector.unknown_count))
        record(results, vector.unverified_count >= 1, "144hz_unverified_gap_detected", str(vector.unverified_count))
        record(results, manifest.claim_status == "test_required", "144hz_seed_status_test_required", manifest.claim_status)
        record(results, manifest.proof_debt == 0.85, "144hz_seed_proof_debt_085", str(manifest.proof_debt))
        record(results, len(mea.canonical_hash(manifest)) == 64, "canonical_hash_64_hex")
        record(results, kernel_probe["identity"]["kernel_name"] == "Forge Discovery Kernel", "kernel_identity_visible")
        record(results, kernel_probe["identity"]["full_runtime_active"] is False, "kernel_full_runtime_inactive")
        record(results, kernel_probe["identity"]["foundation_visible"] is True, "kernel_foundation_visible")
    except Exception as exc:
        record(results, False, "mea_import_and_behavior", repr(exc))

    # main.py route preservation and Patch 275 endpoint.
    main_py = (forge / "main.py").read_text(encoding="utf-8") if (forge / "main.py").exists() else ""
    for route in PRESERVED_ROUTES:
        record(results, route in main_py, f"preserved_route:{route}")
    record(results, "/api/mea/foundation-status" in main_py, "new_route:/api/mea/foundation-status")
    record(results, "def _p275_mea_foundation_status_v1" in main_py, "foundation_status_function_present")
    record(results, "discovery_kernel" in main_py, "discovery_kernel_reported_by_endpoint")
    record(results, "kernel_foundation_probe" in main_py, "kernel_probe_available_to_endpoint")
    record(results, "_p275_mea_foundation_status_v1" in main_py and "writes_files" in main_py, "foundation_status_boundary_declared")
    record(results, "def do_POST" in main_py and "/api/mea/foundation-status" not in main_py[main_py.find("def do_POST"):], "no_mea_post_route")

    # Run behavior script if present.
    behavior = forge / "scripts/test_patch275_mea_foundation.py"
    if behavior.exists():
        proc = subprocess.run([sys.executable, str(behavior), "--forge-root", str(forge)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(proc.stdout)
        record(results, proc.returncode == 0, "behavior_test_script_exit_0", f"returncode={proc.returncode}")

    passed = sum(1 for status, _ in results if status == "PASS")
    failed = sum(1 for status, _ in results if status == "FAIL")
    print(f"RESULT: PATCH_275R_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{len(results)} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
