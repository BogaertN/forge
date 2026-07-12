"""Structural verifier for the Slice 24 full regression bundle scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .authority import SLICE24_PATCH_FILES, REQUIRED_BEHAVIOR_TESTS, REQUIRED_SLICE_VERIFIERS, REQUIRED_EXTERNAL_CONTEXT_CHECKS, REQUIRED_SOURCE_GUARDS, SLICE24_HARD_BOUNDARY
from .catalog import active_required_commands, matrix_summary, classify_catalog_paths
from .receipt import build_receipt, validate_receipt
from .runner import build_acceptance_plan, run_acceptance_bundle
from .source_guard import run_source_guards

@dataclass(frozen=True)
class Slice24VerificationResult:
    passed: bool
    context_label: str
    checked_files: tuple[str, ...]
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "context_label": self.context_label,
            "checked_files": list(self.checked_files),
            "failures": list(self.failures),
        }


def _context_label(root: Path) -> str:
    git_dir = root / ".git"
    if not git_dir.exists():
        return "git_context_not_required_for_source_behavior_test"
    return "slice24_patch_context"


def verify_slice24_boundary(root: str | Path) -> Slice24VerificationResult:
    root = Path(root)
    failures: list[str] = []

    for rel in SLICE24_PATCH_FILES:
        if not (root / rel).is_file():
            failures.append(f"missing_patch_file:{rel}")

    if len(REQUIRED_BEHAVIOR_TESTS) != 23:
        failures.append("required_behavior_test_count_not_23")
    if len(REQUIRED_SLICE_VERIFIERS) != 22:
        failures.append("required_slice_verifier_count_not_22")
    if len(REQUIRED_EXTERNAL_CONTEXT_CHECKS) != 1:
        failures.append("required_external_context_check_count_not_1")
    if len(REQUIRED_SOURCE_GUARDS) != 6:
        failures.append("required_source_guard_count_not_6")

    commands = active_required_commands()
    if len(commands) != 45:
        failures.append("active_required_command_count_not_45")

    plan = build_acceptance_plan()
    if plan["matrix"]["required_command_count"] != 45:
        failures.append("acceptance_plan_required_command_count_not_45")
    if plan["broad_claim_allowed"] is not False:
        failures.append("acceptance_plan_allows_broad_claim")

    required_slices = set(plan["matrix"]["required_slices"])
    if required_slices != set(range(1, 22)) | {23}:
        failures.append("required_slice_set_is_not_1_through_21_plus_23")

    classifications = classify_catalog_paths([
        "scripts/test_aiweb_slice01_proof_scaffold.py",
        "scripts/aiweb_slice01_proof_scaffold_verify.py",
        "backups/patch224_before/main.py",
        "memory/archive/proof_receipt.json",
        "scripts/patch999_legacy_verify.py",
        "docs/proof_receipt.md",
    ])
    if classifications["blocker_count"] != 0:
        failures.append("classification_policy_left_known_paths_as_blockers")

    source_guard_results = run_source_guards(root)
    for result in source_guard_results:
        if not result.passed:
            failures.extend(result.failures)

    dry_result = run_acceptance_bundle(root, result_dir=root / ".slice24_structural_probe", require_clean_context=False, execute_required_commands=False)
    if dry_result["summary"]["required_command_count"] != 45:
        failures.append("dry_acceptance_probe_required_command_count_not_45")
    if dry_result["accepted"] is not False:
        failures.append("dry_acceptance_probe_claimed_acceptance_without_execution")

    receipt = build_receipt({
        "required_command_count": 45,
        "passed_command_count": 45,
        "failed_command_count": 0,
        "source_guard_passed": True,
        "external_context_passed": True,
        "accepted": True,
    })
    if validate_receipt(receipt):
        failures.append("deterministic_receipt_validation_failed")

    if "no_memory_write" not in SLICE24_HARD_BOUNDARY:
        failures.append("hard_boundary_missing_no_memory_write")

    return Slice24VerificationResult(not failures, _context_label(root), tuple(SLICE24_PATCH_FILES), tuple(failures))
