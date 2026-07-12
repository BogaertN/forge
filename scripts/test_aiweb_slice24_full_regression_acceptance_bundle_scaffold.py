#!/usr/bin/env python3
"""Source behavior test for Slice 24 full regression acceptance bundle scaffold."""

from pathlib import Path
import shutil
import tempfile

# Ensure direct script execution can import the repo-root package.
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_full_regression_acceptance_bundle_scaffold.catalog import active_required_commands, matrix_summary, classify_catalog_paths
from aiweb_full_regression_acceptance_bundle_scaffold.receipt import build_receipt, validate_receipt
from aiweb_full_regression_acceptance_bundle_scaffold.runner import build_acceptance_plan, run_acceptance_bundle
from aiweb_full_regression_acceptance_bundle_scaffold.source_guard import run_source_guards
from aiweb_full_regression_acceptance_bundle_scaffold.verify import verify_slice24_boundary
from aiweb_full_regression_acceptance_bundle_scaffold.context import scan_python_cache


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    commands = active_required_commands()
    summary = matrix_summary()

    assert len(commands) == 45
    assert summary["required_behavior_test_count"] == 23
    assert summary["required_slice_verifier_count"] == 22
    assert set(summary["required_slices"]) == set(range(1, 22)) | {23}

    classifications = classify_catalog_paths([
        "scripts/test_aiweb_slice01_proof_scaffold.py",
        "scripts/aiweb_slice01_proof_scaffold_verify.py",
        "backups/patch224_before/main.py",
        "memory/archive/proof_receipt.json",
        "scripts/patch999_legacy_verify.py",
        "docs/proof_receipt.md",
    ])
    assert classifications["blocker_count"] == 0
    assert classifications["counts"]["REQUIRED_ACTIVE_BEHAVIOR_TEST"] == 1
    assert classifications["counts"]["REQUIRED_ACTIVE_SLICE_VERIFIER"] == 1
    assert classifications["counts"]["HISTORICAL_BACKUP_NOT_ACTIVE_AUTHORITY"] == 1
    assert classifications["counts"]["MEMORY_ARCHIVE_NOT_ACTIVE_AUTHORITY"] == 1

    receipt_a = build_receipt({
        "required_command_count": 45,
        "passed_command_count": 45,
        "failed_command_count": 0,
        "source_guard_passed": True,
        "external_context_passed": True,
        "accepted": True,
    })
    receipt_b = build_receipt({
        "required_command_count": 45,
        "passed_command_count": 45,
        "failed_command_count": 0,
        "source_guard_passed": True,
        "external_context_passed": True,
        "accepted": True,
    })
    assert receipt_a == receipt_b
    assert not validate_receipt(receipt_a)

    guards = run_source_guards(repo)
    assert all(result.passed for result in guards), [failure for result in guards for failure in result.failures]

    cache_probe = Path(tempfile.mkdtemp(prefix="slice24_cache_policy_probe_"))
    try:
        managed_venv_cache = cache_probe / ".venv" / "lib" / "python3.12" / "site-packages" / "sample" / "__pycache__"
        managed_venv_cache.mkdir(parents=True)
        (managed_venv_cache / "sample.cpython-312.pyc").write_bytes(b"managed-venv-bytecode")

        managed_plain_venv_cache = cache_probe / "venv" / "lib" / "python3.12" / "site-packages" / "sample" / "__pycache__"
        managed_plain_venv_cache.mkdir(parents=True)
        (managed_plain_venv_cache / "sample.cpython-312.pyc").write_bytes(b"managed-plain-venv-bytecode")

        before_managed_scan = tuple(
            sorted(
                path.relative_to(cache_probe).as_posix()
                for path in cache_probe.rglob("*")
            )
        )
        assert scan_python_cache(cache_probe) == ()
        after_managed_scan = tuple(
            sorted(
                path.relative_to(cache_probe).as_posix()
                for path in cache_probe.rglob("*")
            )
        )
        assert before_managed_scan == after_managed_scan

        source_cache = cache_probe / "source_package" / "__pycache__"
        source_cache.mkdir(parents=True)
        cached_module = source_cache / "module.cpython-312.pyc"
        cached_module.write_bytes(b"source-bytecode")
        source_pyc = cache_probe / "source_package" / "loose.pyc"
        source_pyc.write_bytes(b"loose-source-bytecode")
        source_pyo = cache_probe / "source_package" / "legacy.pyo"
        source_pyo.write_bytes(b"source-optimized-bytecode")

        expected_cache_hits = tuple(
            sorted(
                (
                    str(source_cache),
                    str(source_pyc),
                    str(source_pyo),
                )
            )
        )
        before_source_scan = tuple(
            sorted(
                path.relative_to(cache_probe).as_posix()
                for path in cache_probe.rglob("*")
            )
        )
        assert scan_python_cache(cache_probe) == expected_cache_hits
        after_source_scan = tuple(
            sorted(
                path.relative_to(cache_probe).as_posix()
                for path in cache_probe.rglob("*")
            )
        )
        assert before_source_scan == after_source_scan
    finally:
        shutil.rmtree(cache_probe, ignore_errors=True)

    probe_dir = Path(tempfile.mkdtemp(prefix="slice24_behavior_probe_"))
    try:
        dry = run_acceptance_bundle(repo, result_dir=probe_dir, require_clean_context=False, execute_required_commands=False)
        assert dry["summary"]["required_command_count"] == 45
        assert dry["summary"]["skipped_command_count"] == 45
        assert dry["accepted"] is False
        assert dry["accepted_scope"]["exact_only"] is True
    finally:
        shutil.rmtree(probe_dir, ignore_errors=True)

    live_structural_probe = repo / ".slice24_structural_probe"
    assert not live_structural_probe.exists()
    verify_result = verify_slice24_boundary(repo)
    assert verify_result.passed, verify_result.failures
    assert not live_structural_probe.exists()

    print("AIWEB SLICE 24 SOURCE BEHAVIOR TEST: PASS")
    print(f"required_command_count={len(commands)}")
    print(f"required_behavior_test_count={summary['required_behavior_test_count']}")
    print(f"required_slice_verifier_count={summary['required_slice_verifier_count']}")
    print(f"source_guard_count={len(guards)}")
    print(f"receipt_id={receipt_a.receipt_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
