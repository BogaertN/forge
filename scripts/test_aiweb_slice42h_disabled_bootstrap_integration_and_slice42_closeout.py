#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 42H.

This test is intentionally executed by the Decision Owner on the live Forge
repository.  Package construction does not execute this file.
"""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import subprocess
import sys
from typing import Any

PACKAGE = (
    "aiweb_language_core_bootstrap.outward_expression_runtime."
    "disabled_outward_expression_closeout"
)
SLICE42G_TEST = "test_aiweb_slice42g_msm_outward_expression_integration.py"


class Ledger:
    """Visible deterministic test ledger."""

    def __init__(self) -> None:
        self.check_count = 0
        self.malformed_cases = 0
        self.explicit_rejections = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)

    def rejection(self, condition: object, label: str) -> None:
        self.explicit_rejections += 1
        self.check(condition, label)


def run(arguments: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(repository), *arguments])


def repository_fingerprint(repository: Path) -> tuple[str, str, str]:
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
    if head.returncode or tree.returncode or status.returncode:
        return ("<git-error>", "<git-error>", "<git-error>")
    return (head.stdout.strip(), tree.stdout.strip(), status.stdout)


def build_exact_slice42g_input(repository: Path) -> tuple[Any, Any]:
    helpers = runpy.run_path(str(repository / "scripts" / SLICE42G_TEST))
    builder = helpers.get("build_slice42g_input")
    if not callable(builder):
        raise RuntimeError("accepted Slice 42G fixture builder is unavailable")
    return builder(repository)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    arguments = parser.parse_args()
    repository = Path(arguments.repository).resolve()
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    before_repository = repository_fingerprint(repository)

    package = importlib.import_module(PACKAGE)
    integration, integration_input = build_exact_slice42g_input(repository)
    direct_integration_result = integration.integrate_outward_meaning_and_expression_link(
        integration_input
    )
    ledger.check(
        integration.validate_integration_input(integration_input).ok,
        "exact Slice 42G integration input validates",
    )
    ledger.check(
        integration.validate_integration_result(
            direct_integration_result,
            integration_input=integration_input,
        ).ok,
        "exact Slice 42G integration result validates",
    )

    # Exact accepted predecessor and authority constants.
    ledger.check(
        package.PRE_SLICE42_COMMIT
        == "661ff1e17d8d4a982641ca39dc150b23bbb766e9",
        "pre-Slice-42 commit identity",
    )
    ledger.check(
        package.PRE_SLICE42_TREE
        == "e56c9af88be9b845de534c62c9b82fa6af960f3f",
        "pre-Slice-42 tree identity",
    )
    ledger.check(
        package.SLICE42G_ACCEPTED_HEAD
        == "8f3360dcb7e248f2ea1f1ced3e43b43ecbceedf5",
        "accepted Slice 42G head identity",
    )
    ledger.check(
        package.SLICE42G_ACCEPTED_TREE
        == "56325c16643a6aa061baa6a0645fbeec7f5f5588",
        "accepted Slice 42G tree identity",
    )
    ledger.check(
        package.SLICE42H_COMMIT_SUBJECT
        == "Slice 42H disabled bootstrap integration and Slice 42 closeout",
        "exact Slice 42H commit subject",
    )
    ledger.check(
        package.SLICE42_INCREMENT_LABELS
        == ("42A", "42B", "42C", "42D", "42E", "42F", "42G", "42H"),
        "fixed Slice 42 increment sequence",
    )
    ledger.check(len(package.SLICE42_ACCEPTED_CHAIN) == 8, "accepted chain count")
    ledger.check(len(package.EXPECTED_STAGE_CHAIN) == 9, "nine-stage receipt chain")
    ledger.check(
        "Echo validation belongs to Slice 43" in package.SLICE42_PERMANENT_BOUNDARIES,
        "Echo remains deferred to Slice 43",
    )
    ledger.check(
        "GP-014 is not superseded" in package.SLICE42_PERMANENT_BOUNDARIES,
        "GP-014 remains protected",
    )

    # Disabled state and explicit enablement are distinct deterministic records.
    disabled_state = package.build_disabled_outward_expression_closeout_state()
    enabled_state = package.build_disabled_outward_expression_closeout_state(
        explicit_offline_developer_enable=True
    )
    ledger.check(package.validate_state(disabled_state).ok, "disabled state validates")
    ledger.check(package.validate_state(enabled_state).ok, "enabled state validates")
    ledger.check(disabled_state.enabled is False, "disabled by default")
    ledger.check(enabled_state.enabled is True, "explicit offline enable")
    ledger.check(
        disabled_state.state_id != enabled_state.state_id,
        "state identity distinguishes enablement",
    )
    for field in (
        "disabled_by_default",
        "explicit_invocation_required",
        "accepted_static_fixture_only",
        "offline_only",
        "read_only",
        "in_memory_only",
        "deterministic",
        "exact_profile_bounded",
        "source_preserving",
        "rollback_safe",
    ):
        ledger.check(getattr(disabled_state, field) is True, "state required " + field)
    for field in (
        "automatic_activation_allowed",
        "arbitrary_input_allowed",
        "route_allowed",
        "api_allowed",
        "network_allowed",
        "filesystem_read_allowed",
        "filesystem_write_allowed",
        "memory_read_allowed",
        "memory_write_allowed",
        "tool_allowed",
        "action_allowed",
        "rendering_allowed",
        "delivery_allowed",
        "echo_validation_allowed",
        "truth_authority_allowed",
        "evidence_authority_allowed",
        "permission_authority_allowed",
        "execution_authority_allowed",
        "slice43_allowed",
    ):
        ledger.check(getattr(disabled_state, field) is False, "state boundary " + field)

    # Closed static fixture registry and exact Slice 42G custody.
    fixtures = package.list_outward_expression_closeout_fixtures()
    ledger.check(len(fixtures) == 1, "one closed accepted fixture")
    fixture = fixtures[0]
    ledger.check(package.validate_fixture(fixture).ok, "fixture validates")
    ledger.check(package.is_exact_accepted_fixture(fixture), "fixture registry membership")
    ledger.check(fixture.accepted_fixture is True, "fixture accepted")
    ledger.check(fixture.synthetic is True, "fixture synthetic")
    ledger.check(fixture.explicit_invocation_only is True, "fixture explicit only")
    ledger.check(fixture.offline_only is True, "fixture offline")
    ledger.check(fixture.in_memory_only is True, "fixture in memory")
    ledger.check(fixture.deterministic is True, "fixture deterministic")
    ledger.check(
        fixture.expected_slice42g_integration_input_id
        == integration_input.integration_input_id,
        "fixture exact Slice 42G input identity",
    )
    ledger.check(
        fixture.expected_slice42g_result_id == direct_integration_result.result_id,
        "fixture exact Slice 42G result identity",
    )
    ledger.check(
        fixture.expected_slice42g_result_digest
        == direct_integration_result.result_digest,
        "fixture exact Slice 42G result digest",
    )
    ledger.check(
        fixture.expected_successor_manifest_id
        == direct_integration_result.successor_manifest.manifest_id,
        "fixture exact successor manifest identity",
    )
    ledger.check(
        fixture.expected_selected_meaning_ref
        == direct_integration_result.governed_outward_meaning_record.prior_selected_meaning_ref,
        "fixture exact selected meaning custody",
    )
    ledger.check(
        fixture.expected_outward_meaning_ref
        == direct_integration_result.governed_outward_meaning_record.record_id,
        "fixture exact outward meaning custody",
    )
    ledger.check(
        fixture.expected_expression_link_ref
        == direct_integration_result.expression_link_record.record_id,
        "fixture exact expression-link custody",
    )

    invocation = package.build_outward_expression_closeout_invocation(
        fixture.fixture_name
    )
    ledger.check(invocation is not None, "exact invocation built")
    assert invocation is not None
    ledger.check(package.validate_invocation(invocation).ok, "invocation validates")
    ledger.check(invocation.fixture_id == fixture.fixture_id, "invocation fixture identity")
    ledger.check(invocation.arbitrary_input_carried is False, "no arbitrary input")
    ledger.check(
        package.build_outward_expression_closeout_invocation("not-accepted") is None,
        "unknown fixture has no invocation",
    )

    # Default invocation refuses and produces no stage execution or acceptance.
    refused = package.run_disabled_outward_expression_closeout(
        invocation,
        integration_input=integration_input,
    )
    ledger.check(
        refused.status is package.Slice42CloseoutStatus.REFUSED_DISABLED,
        "disabled invocation refused",
    )
    ledger.check(package.validate_result(refused).ok, "disabled refusal validates")
    ledger.check(refused.stage_receipt_count == 0, "disabled refusal has no stages")
    ledger.check(refused.explicitly_invoked is False, "disabled refusal not invoked")
    ledger.check(
        refused.final_slice42_acceptance_record_created is False,
        "disabled refusal does not close Slice 42",
    )
    ledger.check(refused.acceptance_record.slice42_closed is False, "refusal acceptance remains open")

    # Fail-closed rejection paths.
    held_state = package.run_disabled_outward_expression_closeout(
        invocation,
        state=object(),
        integration_input=integration_input,
    )
    ledger.rejection(
        held_state.status is package.Slice42CloseoutStatus.HELD_INVALID_STATE,
        "invalid state held",
    )
    bad_invocation = replace(
        invocation,
        requested_operation="fabricated-operation",
    )
    held_invocation = package.run_disabled_outward_expression_closeout(
        bad_invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    ledger.rejection(
        held_invocation.status is package.Slice42CloseoutStatus.HELD_INVALID_INVOCATION,
        "invalid invocation held",
    )
    bad_fixture_invocation = replace(
        invocation,
        fixture_id="slice42h_fixture:fabricated",
    )
    held_fixture = package.run_disabled_outward_expression_closeout(
        bad_fixture_invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    ledger.rejection(
        held_fixture.status is package.Slice42CloseoutStatus.HELD_FIXTURE_NOT_ACCEPTED,
        "unaccepted fixture held",
    )
    tampered_input = replace(
        integration_input,
        integration_input_id="slice42g_integration_input:fabricated",
    )
    held_predecessor = package.run_disabled_outward_expression_closeout(
        invocation,
        state=enabled_state,
        integration_input=tampered_input,
    )
    ledger.rejection(
        held_predecessor.status
        is package.Slice42CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
        "tampered predecessor held",
    )
    for held in (held_state, held_invocation, held_fixture, held_predecessor):
        ledger.check(package.validate_result(held).ok, "held result validates")
        ledger.check(held.stage_receipt_count == 0, "held result no stages")
        ledger.check(held.acceptance_record.slice42_closed is False, "held result no closeout")

    # Exact explicit invocation completes deterministically.
    source_input_before = integration_input
    first = package.run_disabled_outward_expression_closeout(
        invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    second = package.run_disabled_outward_expression_closeout(
        invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    third = package.run_disabled_outward_expression_closeout(
        invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    ledger.check(first == second == third, "deterministic repeated closeout")
    ledger.check(
        first.result_id == second.result_id == third.result_id,
        "deterministic result identity",
    )
    ledger.check(
        first.result_digest == second.result_digest == third.result_digest,
        "deterministic result digest",
    )
    ledger.check(
        first.deterministic_repeat_digest
        == second.deterministic_repeat_digest
        == third.deterministic_repeat_digest,
        "deterministic repeat digest",
    )
    ledger.check(
        first.status is package.Slice42CloseoutStatus.COMPLETED,
        "Slice 42 closeout completed",
    )
    result_report = package.validate_result(first)
    ledger.check(result_report.ok, "completed result validates")
    for issue in result_report.issues:
        ledger.check(False, "unexpected result issue " + issue.path + ":" + issue.detail)
    package.assert_valid_result(first)
    ledger.check(integration_input == source_input_before, "predecessor input immutable")
    ledger.check(
        first.integration_result == direct_integration_result,
        "closeout holds exact deterministic Slice 42G result",
    )

    # Exact nine-stage custody chain.
    ledger.check(first.stage_receipt_count == 9, "exact nine stage receipts")
    ledger.check(len(first.stage_receipts) == 9, "nine receipt objects")
    ledger.check(
        tuple(item.stage for item in first.stage_receipts)
        == package.EXPECTED_STAGE_CHAIN,
        "exact ordered stage chain",
    )
    ledger.check(
        tuple(item.stage_index for item in first.stage_receipts) == tuple(range(9)),
        "exact stage indexes",
    )
    for receipt in first.stage_receipts:
        ledger.check(package.validate_stage_receipt(receipt).ok, "stage receipt validates")
        ledger.check(bool(receipt.input_refs), "stage receipt input refs")
        ledger.check(bool(receipt.output_refs), "stage receipt output refs")
        ledger.check(receipt.deterministic is True, "stage deterministic")
        ledger.check(receipt.source_preserved is True, "stage source preserved")
        ledger.check(receipt.offline_only is True, "stage offline")
        ledger.check(receipt.in_memory_only is True, "stage in memory")
        for field in (
            "route_created",
            "api_created",
            "network_accessed",
            "filesystem_read_performed",
            "filesystem_write_performed",
            "memory_read_performed",
            "memory_write_performed",
            "tool_invoked",
            "action_performed",
            "rendered",
            "echo_validated",
            "delivered",
        ):
            ledger.check(getattr(receipt, field) is False, "stage boundary " + field)

    # Final Slice 42 acceptance record.
    acceptance = first.acceptance_record
    ledger.check(package.validate_acceptance_record(acceptance).ok, "acceptance validates")
    ledger.check(acceptance.accepted_increment_labels == package.SLICE42_INCREMENT_LABELS, "A-H accepted")
    ledger.check(acceptance.slice42_closed is True, "Slice 42 closed")
    ledger.check(acceptance.slice43_started is False, "Slice 43 not started")
    ledger.check(acceptance.stop_after_slice42 is True, "stop after Slice 42")
    for field in (
        "authorized_meaning_required",
        "selected_meaning_preserved",
        "scope_preserved",
        "certainty_preserved",
        "evidence_status_preserved",
        "caveats_preserved",
        "refusal_state_preserved",
        "unresolved_conditions_preserved",
        "deterministic_expression_candidate_created",
        "expression_candidate_remains_unvalidated",
    ):
        ledger.check(getattr(acceptance, field) is True, "acceptance proof " + field)
    for field in (
        "echo_validation_performed",
        "delivery_authority",
        "truth_authority",
        "evidence_authority",
        "permission_authority",
        "execution_authority",
        "runtime_self_grants_acceptance",
        "production_ready",
    ):
        ledger.check(getattr(acceptance, field) is False, "acceptance boundary " + field)

    rollback = first.rollback_metadata
    ledger.check(package.validate_rollback_metadata(rollback).ok, "rollback metadata validates")
    ledger.check(rollback.pre_slice42_commit == package.PRE_SLICE42_COMMIT, "rollback pre-Slice-42 commit")
    ledger.check(rollback.pre_slice42_tree == package.PRE_SLICE42_TREE, "rollback pre-Slice-42 tree")
    ledger.check(rollback.accepted_slice42g_head == package.SLICE42G_ACCEPTED_HEAD, "rollback Slice 42G head")
    ledger.check(rollback.accepted_slice42g_tree == package.SLICE42G_ACCEPTED_TREE, "rollback Slice 42G tree")
    ledger.check(rollback.runtime_rollback_performed is False, "runtime rollback not performed")
    ledger.check(rollback.repository_mutated is False, "repository not mutated")

    # Exact preservation through the accepted 42G output.
    result42g = first.integration_result
    assert result42g is not None
    successor = result42g.successor_manifest
    source = result42g.source_manifest
    ledger.check(result42g.selected_meaning_preserved is True, "selected meaning preserved by 42G")
    ledger.check(result42g.all_candidate_meanings_retained is True, "candidate alternatives preserved")
    ledger.check(result42g.all_non_selection_outcomes_retained is True, "non-selection preserved")
    ledger.check(result42g.alternatives_and_unresolved_retained is True, "unresolved conditions preserved")
    ledger.check(result42g.complete_successor_manifest_validated is True, "successor manifest validated")
    ledger.check(result42g.candidate_remains_unvalidated is True, "candidate remains unvalidated")
    ledger.check(successor.candidate_meanings == source.candidate_meanings, "candidate set unchanged")
    ledger.check(successor.non_selection_outcomes == source.non_selection_outcomes, "non-selection set unchanged")
    ledger.check(successor.selected_governed_meanings == source.selected_governed_meanings, "selected meaning set unchanged")
    ledger.check(len(successor.validation_links) == 0, "no validation link")
    ledger.check(len(successor.delivery_or_containment_links) == 0, "no delivery link")
    ledger.check(
        result42g.governed_outward_meaning_record.record_id
        == fixture.expected_outward_meaning_ref,
        "outward meaning identity preserved",
    )
    ledger.check(
        result42g.expression_link_record.record_id
        == fixture.expected_expression_link_ref,
        "expression-link identity preserved",
    )
    ledger.check(
        integration_input.expression_candidate.expression_candidate_id
        == fixture.expected_expression_candidate_id,
        "expression candidate identity preserved",
    )

    # Completed result's positive proofs and permanent zero-authority boundaries.
    for field in (
        "disabled_by_default",
        "explicitly_invoked",
        "accepted_static_fixture_only",
        "offline_only",
        "read_only",
        "in_memory_only",
        "deterministic",
        "exact_stage_chain_complete",
        "authorized_meaning_required",
        "selected_meaning_preserved",
        "scope_preserved",
        "certainty_preserved",
        "evidence_status_preserved",
        "caveats_preserved",
        "refusal_state_preserved",
        "unresolved_conditions_preserved",
        "deterministic_expression_candidate_created",
        "governed_outward_meaning_custody_preserved",
        "expression_link_custody_preserved",
        "complete_successor_manifest_validated",
        "expression_candidate_remains_unvalidated",
        "final_slice42_acceptance_record_created",
    ):
        ledger.check(getattr(first, field) is True, "result proof " + field)

    prohibited_result_fields = (
        "slice43_started",
        "msm_v1_schema_modified",
        "automatic_migration_performed",
        "selected_meaning_rewritten",
        "candidate_alternative_deleted",
        "unresolved_state_resolved",
        "certainty_upgraded",
        "evidence_status_upgraded",
        "caveat_omitted",
        "refusal_softened",
        "expression_candidate_rewritten",
        "validation_link_created",
        "delivery_link_created",
        "echo_validation_performed",
        "echo_approved",
        "delivery_authorized",
        "delivered",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "route_created",
        "api_created",
        "network_accessed",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "memory_read_performed",
        "memory_write_performed",
        "tool_invoked",
        "action_performed",
        "rendered",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
        "neural_parser_used",
        "hidden_classifier_used",
        "gp014_superseded",
    )
    for field in prohibited_result_fields:
        ledger.check(getattr(first, field) is False, "result boundary " + field)

    # Malformed exact-type validation cases.
    malformed_values = (None, True, 1, 1.5, "value", (), [], {}, object())
    for index, value in enumerate(malformed_values):
        ledger.malformed(not package.validate_state(value).ok, f"malformed state {index}")
        ledger.malformed(not package.validate_fixture(value).ok, f"malformed fixture {index}")
        ledger.malformed(not package.validate_invocation(value).ok, f"malformed invocation {index}")
        ledger.malformed(not package.validate_rollback_metadata(value).ok, f"malformed rollback {index}")
        ledger.malformed(not package.validate_acceptance_record(value).ok, f"malformed acceptance {index}")
        ledger.malformed(not package.validate_stage_receipt(value).ok, f"malformed receipt {index}")
        ledger.malformed(not package.validate_result(value).ok, f"malformed result {index}")

    # Deterministic tamper detection.
    ledger.rejection(
        not package.validate_state(replace(enabled_state, route_allowed=True)).ok,
        "route-enabled state rejected",
    )
    ledger.rejection(
        not package.validate_invocation(
            replace(invocation, arbitrary_input_carried=True)
        ).ok,
        "arbitrary-input invocation rejected",
    )
    ledger.rejection(
        not package.validate_fixture(
            replace(fixture, expected_candidate_count=3)
        ).ok,
        "altered closed fixture rejected",
    )
    ledger.rejection(
        not package.validate_acceptance_record(
            replace(acceptance, echo_validation_performed=True)
        ).ok,
        "fabricated Echo validation rejected",
    )
    ledger.rejection(
        not package.validate_acceptance_record(
            replace(acceptance, slice43_started=True)
        ).ok,
        "fabricated Slice 43 start rejected",
    )
    ledger.rejection(
        not package.validate_stage_receipt(
            replace(first.stage_receipts[0], delivered=True)
        ).ok,
        "fabricated stage delivery rejected",
    )
    ledger.rejection(
        not package.validate_result(replace(first, selected_meaning_rewritten=True)).ok,
        "selected-meaning rewrite rejected",
    )
    ledger.rejection(
        not package.validate_result(replace(first, certainty_upgraded=True)).ok,
        "certainty upgrade rejected",
    )
    ledger.rejection(
        not package.validate_result(replace(first, caveat_omitted=True)).ok,
        "caveat omission rejected",
    )
    ledger.rejection(
        not package.validate_result(replace(first, refusal_softened=True)).ok,
        "refusal softening rejected",
    )
    ledger.rejection(
        not package.validate_result(replace(first, delivery_authorized=True)).ok,
        "delivery authority rejected",
    )
    ledger.rejection(
        not package.validate_result(replace(first, result_digest="0" * 64)).ok,
        "result digest tamper rejected",
    )
    ledger.rejection(
        not package.validate_result(
            replace(first, stage_receipts=first.stage_receipts[:-1])
        ).ok,
        "incomplete stage chain rejected",
    )

    # Records are immutable.
    try:
        acceptance.slice42_closed = False  # type: ignore[misc]
        ledger.check(False, "acceptance record immutable")
    except (FrozenInstanceError, AttributeError, TypeError):
        ledger.check(True, "acceptance record immutable")
    try:
        first.delivery_authorized = True  # type: ignore[misc]
        ledger.check(False, "closeout result immutable")
    except (FrozenInstanceError, AttributeError, TypeError):
        ledger.check(True, "closeout result immutable")

    after_repository = repository_fingerprint(repository)
    ledger.check(before_repository == after_repository, "runtime leaves repository unchanged")

    print("AI.WEB SLICE 42H DISABLED BOOTSTRAP INTEGRATION AND SLICE 42 CLOSEOUT TEST")
    print("check_count=" + str(ledger.check_count))
    print("malformed_validation_cases=" + str(ledger.malformed_cases))
    print("explicit_rejection_cases=" + str(ledger.explicit_rejections))
    print("slice42A_through_42H_completed=" + str(int(acceptance.slice42_closed)))
    print("authorized_meaning_required=" + str(int(first.authorized_meaning_required)))
    print("selected_meaning_preserved=" + str(int(first.selected_meaning_preserved)))
    print("scope_preserved=" + str(int(first.scope_preserved)))
    print("certainty_preserved=" + str(int(first.certainty_preserved)))
    print("evidence_status_preserved=" + str(int(first.evidence_status_preserved)))
    print("caveats_preserved=" + str(int(first.caveats_preserved)))
    print("refusal_state_preserved=" + str(int(first.refusal_state_preserved)))
    print("unresolved_conditions_preserved=" + str(int(first.unresolved_conditions_preserved)))
    print("deterministic_expression_candidate_created=" + str(int(first.deterministic_expression_candidate_created)))
    print("echo_validation_performed=" + str(int(first.echo_validation_performed)))
    print("delivery_authority=" + str(int(first.delivery_authorized)))
    print("truth_authority=" + str(int(first.truth_determined)))
    print("evidence_authority=" + str(int(first.evidence_validated)))
    print("permission_authority=" + str(int(first.permission_granted)))
    print("execution_authority=" + str(int(first.execution_authorized)))
    print("slice43_started=" + str(int(first.slice43_started)))
    print("stage_receipt_count=" + str(first.stage_receipt_count))
    print("failure_count=" + str(len(ledger.failures)))
    for failure in ledger.failures:
        print("FAIL: " + failure)
    print(
        "AI.WEB SLICE 42H BEHAVIOR TEST: "
        + ("PASS" if not ledger.failures else "FAIL")
    )
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
