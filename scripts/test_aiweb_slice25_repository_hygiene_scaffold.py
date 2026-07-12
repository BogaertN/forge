#!/usr/bin/env python3
"""Behavior test for the AI.Web Slice 25 repository-hygiene scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_repository_hygiene_scaffold.authority import (
    ACCEPTED_SCOPE_SENTENCE,
    HISTORICAL_RECORD_CLASSIFICATION,
    HISTORICAL_RECORD_RELATIVE_PATH,
    MANAGED_PYTHON_ENVIRONMENT_DIR_NAMES,
    MODIFIED_EXISTING_FILES,
    NEW_SLICE25_FILES,
    PROHIBITED_MODIFIED_PATHS,
    SLICE25_HARD_BOUNDARY,
    SLICE25_PATCH_FILES,
    SOURCE_TREE_CACHE_DIRECTORIES,
    STRUCTURAL_PROBE_CLASSIFICATION,
    STRUCTURAL_PROBE_RELATIVE_PATH,
    STRUCTURAL_PROBE_SHA256,
)
from aiweb_repository_hygiene_scaffold.verify import (
    authority_constant_failures,
    cache_policy_probe,
    forbidden_import_failures,
    required_files_present,
    syntax_failures,
    verify_slice25_boundary,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Slice 25 repository-hygiene behavior checks."
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=str(REPO_ROOT),
        help="Forge repository root",
    )
    parser.add_argument(
        "--state",
        choices=("structure", "applied", "committed"),
        default="applied",
        help="Expected repository state",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    passes: list[str] = []
    failures: list[str] = []

    def check(name: str, condition: bool) -> None:
        if condition:
            passes.append(name)
        else:
            failures.append(name)

    check(
        "historical record path is exact",
        HISTORICAL_RECORD_RELATIVE_PATH
        == (
            "memory/forge_build_sequence_v1/"
            "20260712_054028_forge_build_sequence_v1.json"
        ),
    )
    check(
        "historical record is explicitly noncanonical evidence",
        "noncanonical" in HISTORICAL_RECORD_CLASSIFICATION,
    )
    check(
        "structural probe path is exact",
        STRUCTURAL_PROBE_RELATIVE_PATH
        == ".slice24_structural_probe/slice24_acceptance_result.json",
    )
    check(
        "structural probe is explicitly test-generated evidence",
        "test_generated" in STRUCTURAL_PROBE_CLASSIFICATION,
    )
    check(
        "structural probe checksum is exact length",
        len(STRUCTURAL_PROBE_SHA256) == 64,
    )
    check(
        "managed environment names are exact",
        MANAGED_PYTHON_ENVIRONMENT_DIR_NAMES == (".venv", "venv"),
    )
    check(
        "source cache directories are exact",
        SOURCE_TREE_CACHE_DIRECTORIES
        == ("agents/__pycache__", "agents/forge/__pycache__"),
    )
    check("five existing files are modified", len(MODIFIED_EXISTING_FILES) == 5)
    check("six new files are created", len(NEW_SLICE25_FILES) == 6)
    check("eleven exact patch files are declared", len(SLICE25_PATCH_FILES) == 11)
    check(
        "main.py is protected",
        "main.py" in PROHIBITED_MODIFIED_PATHS,
    )
    check(
        ".gitignore is protected",
        ".gitignore" in PROHIBITED_MODIFIED_PATHS,
    )
    check(
        "language runtime authority remains prohibited",
        "no_language_runtime_authority" in SLICE25_HARD_BOUNDARY,
    )
    check(
        "GitHub push remains prohibited",
        "no_github_push" in SLICE25_HARD_BOUNDARY,
    )
    check(
        "accepted scope is evidence-preserving only",
        "evidence-preserving" in ACCEPTED_SCOPE_SENTENCE,
    )

    missing = required_files_present(repo)
    check("all required Slice 25 files exist", not missing)
    failures.extend(f"missing:{item}" for item in missing)

    syntax = syntax_failures(repo)
    check("all Slice 25 Python files parse", not syntax)
    failures.extend(syntax)

    forbidden = forbidden_import_failures(repo)
    check("no forbidden active model/network imports", not forbidden)
    failures.extend(forbidden)

    constants = authority_constant_failures()
    check("authority constants preserve the bounded design", not constants)
    failures.extend(constants)

    cache_probe_failures = cache_policy_probe()
    check(
        "managed environment caches are excluded and source caches detected",
        not cache_probe_failures,
    )
    failures.extend(cache_probe_failures)

    result = verify_slice25_boundary(
        repo,
        state=args.state,
        require_live_repo_identity=args.state in {"applied", "committed"},
        check_protected_files=args.state in {"applied", "committed"},
    )
    check(f"Slice 25 {args.state} boundary verifies", result.passed)
    failures.extend(result.failures)

    print("============================================================")
    print("AIWEB SLICE 25 REPOSITORY HYGIENE BEHAVIOR TEST")
    print("============================================================")
    print(f"Target repo: {repo}")
    print(f"Expected state: {args.state}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")

    if failures:
        print(
            "VERDICT: FAIL - Slice 25 behavior test failed "
            "within the requested state"
        )
        return 1

    print(
        "VERDICT: PASS - Slice 25 behavior test passed "
        "within the requested state"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
