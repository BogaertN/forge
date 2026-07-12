#!/usr/bin/env python3
"""Tests for Slice 19 RMC Echo Boundary Scaffold."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED_BOUNDARY_KEYS = {
    "echo_validation_not_implemented",
    "echo_not_delivery",
    "echo_not_public_release",
    "echo_not_output_approval",
    "echo_not_renderer_authority",
    "echo_not_selected_meaning_authority",
    "echo_not_source_authority",
    "echo_not_predicate_authority",
    "echo_not_concept_authority",
    "echo_not_gp014",
    "echo_not_gp015_repair",
    "echo_not_production_integration",
}

PAYLOAD_PATHS = (
    "aiweb_rmc_echo_boundary_scaffold/__init__.py",
    "aiweb_rmc_echo_boundary_scaffold/authority.py",
    "aiweb_rmc_echo_boundary_scaffold/boundary.py",
    "aiweb_rmc_echo_boundary_scaffold/core.py",
    "aiweb_rmc_echo_boundary_scaffold/receipt.py",
    "aiweb_rmc_echo_boundary_scaffold/verify.py",
    "scripts/README_aiweb_slice19_rmc_echo_boundary_scaffold.md",
    "scripts/aiweb_slice19_rmc_echo_boundary_verify.py",
    "scripts/test_aiweb_slice19_rmc_echo_boundary_scaffold.py",
)

EXPECTED_BASE_HEAD = "9af49a428c9fd87f16a1a03b98947aada6c55b6c"
EXPECTED_SLICE19_SUBJECT = "Slice 19 RMC Echo boundary scaffold"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_git(repo: Path, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode, result.stdout.rstrip("\n"), result.stderr.rstrip("\n")


def test_package_invariants(repo_root: Path) -> None:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    boundary = importlib.import_module("aiweb_rmc_echo_boundary_scaffold.boundary")
    authority = importlib.import_module("aiweb_rmc_echo_boundary_scaffold.authority")
    receipt = importlib.import_module("aiweb_rmc_echo_boundary_scaffold.receipt")
    verify = importlib.import_module("aiweb_rmc_echo_boundary_scaffold.verify")

    report = boundary.build_boundary_report()
    failures = boundary.validate_boundary_report(report)
    assert_true(failures == (), "boundary report failed validation: " + repr(failures))

    keys = set(report["boundary_keys"])
    assert_true(keys == REQUIRED_BOUNDARY_KEYS, "boundary keys changed")
    assert_true(report["implementation_state"] == "not_implemented", "Echo implementation state changed")
    assert_true(report["relationship"] == "separate_later_authority_layer", "Echo relationship changed")

    denied = [
        "implementation",
        "delivery",
        "public_release",
        "output_approval",
        "renderer_authority",
        "selected_meaning_authority",
        "source_authority",
        "predicate_authority",
        "concept_authority",
        "gp014",
        "gp015_repair",
        "production_integration",
    ]
    for claim in denied:
        decision = authority.authority_decision_for_claim(claim)
        assert_true(decision["allowed"] is False, "claim should be denied: " + claim)

    positive = authority.authority_decision_for_claim("separate later authority layer")
    assert_true(positive["allowed"] is True, "boundary description should be allowed")
    assert_true(positive["decision"] == "allowed_as_boundary_description_only", "wrong positive decision")

    unknown = authority.authority_decision_for_claim("release to users")
    assert_true(unknown["allowed"] is False, "unknown claim should be denied")

    built_receipt = receipt.build_slice19_receipt()
    assert_true(len(built_receipt["receipt_sha256"]) == 64, "receipt digest invalid")
    receipt_body = built_receipt["receipt"]
    assert_true(receipt_body["repo_write_authorized"] is False, "receipt grants repo write")
    assert_true(receipt_body["delivery_authorized"] is False, "receipt grants delivery")
    assert_true(receipt_body["public_release_authorized"] is False, "receipt grants public release")
    assert_true(receipt_body["output_approval_authorized"] is False, "receipt grants output approval")
    assert_true(receipt_body["production_integration_authorized"] is False, "receipt grants production integration")
    assert_true(receipt_body["gp014_modified"] is False, "receipt modifies GP-014")
    assert_true(receipt_body["gp014_imported"] is False, "receipt imports GP-014")
    assert_true(receipt_body["gp014_called"] is False, "receipt calls GP-014")
    assert_true(receipt_body["gp015_repaired"] is False, "receipt repairs GP-015")

    invariant_failures = verify.verify_slice19_invariants(repo_root / "aiweb_rmc_echo_boundary_scaffold")
    assert_true(invariant_failures == (), "invariant failures: " + repr(invariant_failures))


def copy_payload_to_repo(source_root: Path, repo: Path) -> None:
    for rel in PAYLOAD_PATHS:
        source = source_root / rel
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
        if rel.endswith(".py"):
            dest.chmod(0o755 if rel.startswith("scripts/") else 0o644)


def create_base_repo(source_root: Path) -> Path:
    temp = Path(tempfile.mkdtemp(prefix="slice19_verify_context_"))
    repo = temp / "repo"
    repo.mkdir()

    subprocess.run(["git", "-C", str(repo), "init"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-b", "main"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "slice19@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Slice19 Test"], check=True)
    (repo / "BASE.txt").write_text("slice18r1 base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "BASE.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "Slice 18R1 verifier context correction"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    code, head, err = run_git(repo, "rev-parse", "HEAD")
    assert_true(code == 0, "failed to read synthetic base head: " + err)

    # The production verifier uses the real base hash. For context behavior, test
    # the script as source text with its base hash rewritten to the synthetic base.
    verifier_text = (source_root / "scripts/aiweb_slice19_rmc_echo_boundary_verify.py").read_text(encoding="utf-8")
    verifier_text = verifier_text.replace(EXPECTED_BASE_HEAD, head)
    verifier_path = temp / "verify_rebased.py"
    verifier_path.write_text(verifier_text, encoding="utf-8")
    verifier_path.chmod(0o755)

    (temp / "verifier_path.txt").write_text(str(verifier_path), encoding="utf-8")
    return repo


def run_rebased_verifier(repo: Path) -> tuple[int, dict[str, object]]:
    verifier_path = Path(repo.parent / "verifier_path.txt").read_text(encoding="utf-8")
    result = subprocess.run(
        [sys.executable, verifier_path, str(repo), "--json"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise AssertionError("unexpected verifier process failure: " + result.stderr)
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError("verifier did not return JSON: " + result.stdout) from exc
    return result.returncode, report


def test_repository_contexts(source_root: Path) -> None:
    repo = create_base_repo(source_root)

    copy_payload_to_repo(source_root, repo)
    code, report = run_rebased_verifier(repo)
    assert_true(code == 0, "precommit context should pass: " + repr(report))
    assert_true(report["context_label"] == "slice19_precommit_patch_context", "wrong precommit context")

    subprocess.run(["git", "-C", str(repo), "add", "--", *PAYLOAD_PATHS], check=True)
    code, report = run_rebased_verifier(repo)
    assert_true(code == 0, "staged precommit context should pass: " + repr(report))
    assert_true(report["context_label"] == "slice19_precommit_patch_context", "wrong staged context")

    subprocess.run(["git", "-C", str(repo), "commit", "-m", EXPECTED_SLICE19_SUBJECT], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    code, report = run_rebased_verifier(repo)
    assert_true(code == 0, "postcommit context should pass: " + repr(report))
    assert_true(report["context_label"] == "slice19_or_later_clean_committed_context", "wrong postcommit context")

    (repo / "DESCENDANT.txt").write_text("future clean descendant\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "DESCENDANT.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "future descendant"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    code, report = run_rebased_verifier(repo)
    assert_true(code == 0, "clean descendant should pass: " + repr(report))
    assert_true(report["context_label"] == "slice19_or_later_clean_committed_context", "wrong descendant context")

    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    code, report = run_rebased_verifier(repo)
    assert_true(code == 1, "dirty postcommit descendant should fail")
    assert_true(report["verdict"] == "FAIL", "dirty report should fail")


def main() -> int:
    source_root = Path(__file__).resolve().parents[1]
    test_package_invariants(source_root)
    test_repository_contexts(source_root)
    print("SLICE19_RMC_ECHO_BOUNDARY_TEST=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
