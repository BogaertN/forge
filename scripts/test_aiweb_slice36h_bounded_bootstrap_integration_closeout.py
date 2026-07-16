#!/usr/bin/env python3
"""Behavior, adversarial, and authority-boundary tests for Slice 36H."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import FrozenInstanceError, fields, replace
import builtins
import importlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.bounded_structural_bootstrap import (
    PRE_SLICE36_COMMIT,
    PRE_SLICE36_TREE,
    SLICE36_ACCEPTED_CHAIN,
    SLICE36_ACCEPTED_SCOPE,
    SLICE36_DEFERRED_SCOPE,
    SLICE36_INCREMENT_LABELS,
    SLICE36_MATHEMATICAL_DIRECTION,
    SLICE36_PERMANENT_BOUNDARIES,
    SLICE36G_ACCEPTED_HEAD,
    SLICE36G_ACCEPTED_TREE,
    BootstrapIntegrationStatus,
    BootstrapInvocationKind,
    BootstrapStage,
    BootstrapStageReceipt,
    BoundedStructuralBootstrapInvocation,
    BoundedStructuralBootstrapResult,
    BoundedStructuralBootstrapState,
    BoundedStructuralFixtureRecord,
    FIXTURE_GOVERNING,
    FIXTURE_INCOMPLETE_QUOTATION,
    FIXTURE_QUOTATION_CONFLICT,
    FIXTURE_ZERO_DERIVATION,
    build_bounded_structural_bootstrap_state,
    build_fixture_bootstrap_invocation,
    build_slice36_acceptance_record,
    build_slice36_rollback_metadata,
    build_uninstalled_approved_caller_invocation,
    get_bounded_structural_fixture,
    is_exact_accepted_bounded_structural_fixture,
    list_bounded_structural_fixtures,
    run_bounded_structural_bootstrap,
    validate_bootstrap_stage_receipt,
    validate_bounded_structural_bootstrap_invocation,
    validate_bounded_structural_bootstrap_result,
    validate_bounded_structural_bootstrap_state,
    validate_bounded_structural_fixture,
    validate_slice36_acceptance_record,
    validate_slice36_rollback_metadata,
)


checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("forbidden side effect or authority surface attempted")


def enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


# Static contract inventory.
default_state = build_bounded_structural_bootstrap_state()
enabled_state = build_bounded_structural_bootstrap_state(
    explicit_offline_developer_enable=True
)
check(type(default_state) is BoundedStructuralBootstrapState, "default exact state type")
check(type(enabled_state) is BoundedStructuralBootstrapState, "enabled exact state type")
check(default_state.state_id == default_state.expected_id(), "default state stable")
check(enabled_state.state_id == enabled_state.expected_id(), "enabled state stable")
check(validate_bounded_structural_bootstrap_state(default_state).ok, "default state validates")
check(validate_bounded_structural_bootstrap_state(enabled_state).ok, "enabled state validates")
check(not default_state.enabled, "default disabled")
check(default_state.disabled_by_default, "disabled by default declared")
check(enabled_state.enabled, "explicit enable accepted")
check(enabled_state.explicit_offline_developer_enable, "explicit enable preserved")

true_state_fields = (
    "disabled_by_default",
    "explicit_invocation_required",
    "accepted_fixture_only",
    "approved_caller_path_defined",
    "offline_only",
    "standard_library_only",
    "deterministic",
    "read_only",
    "in_memory_only",
    "source_preserving",
    "operator_trace_preserving",
    "phase_trace_preserving",
    "bounded_supported_profile_only",
    "non_llm",
    "rollback_safe",
)
false_state_fields = (
    "approved_caller_catalog_installed",
    "raw_text_alone_allowed",
    "arbitrary_input_allowed",
    "automatic_activation_allowed",
    "hidden_fallback_parser_allowed",
    "conventional_nlp_authority_allowed",
    "external_linguistic_resource_loading_allowed",
    "filesystem_search_allowed",
    "filesystem_read_allowed",
    "filesystem_write_allowed",
    "repository_history_search_allowed",
    "network_allowed",
    "web_access_allowed",
    "environment_lookup_allowed",
    "memory_read_allowed",
    "memory_write_allowed",
    "protected_memory_retrieval_allowed",
    "llm_allowed",
    "embedding_allowed",
    "vector_database_allowed",
    "semantic_similarity_allowed",
    "learned_parser_allowed",
    "neural_classifier_allowed",
    "rag_allowed",
    "main_connection_allowed",
    "api_route_allowed",
    "capability_route_allowed",
    "tool_activation_allowed",
    "action_execution_allowed",
    "outward_rendering_allowed",
    "evidence_validation_allowed",
    "delivery_authorization_allowed",
    "candidate_meaning_allowed",
    "selected_meaning_allowed",
    "concept_resolution_allowed",
    "predicate_authority_allowed",
    "participant_role_authority_allowed",
    "permission_inference_allowed",
    "capability_authority_allowed",
    "release_authorized",
    "production_ready",
)
for state in (default_state, enabled_state):
    for field_name in true_state_fields:
        check(getattr(state, field_name) is True, f"state true {field_name}")
    for field_name in false_state_fields:
        check(getattr(state, field_name) is False, f"state false {field_name}")

for field_name in false_state_fields:
    tampered = replace(enabled_state, **{field_name: True})
    check(
        not validate_bounded_structural_bootstrap_state(tampered).ok,
        f"state rejects authority enlargement {field_name}",
    )
check(
    not validate_bounded_structural_bootstrap_state(
        replace(enabled_state, enabled=False)
    ).ok,
    "state rejects enable mismatch",
)

# Immutability.
try:
    enabled_state.enabled = False  # type: ignore[misc]
except FrozenInstanceError:
    check(True, "state frozen")
else:
    check(False, "state mutable")

# Rollback and acceptance metadata.
rollback = build_slice36_rollback_metadata()
acceptance = build_slice36_acceptance_record(rollback_metadata=rollback)
check(rollback.rollback_id == rollback.expected_id(), "rollback stable")
check(validate_slice36_rollback_metadata(rollback).ok, "rollback validates")
check(rollback.pre_slice36_commit == PRE_SLICE36_COMMIT, "rollback commit exact")
check(rollback.pre_slice36_tree == PRE_SLICE36_TREE, "rollback tree exact")
check(rollback.accepted_parent_head == SLICE36G_ACCEPTED_HEAD, "parent head exact")
check(rollback.accepted_parent_tree == SLICE36G_ACCEPTED_TREE, "parent tree exact")
check(not rollback.live_repository_mutation_authorized, "rollback no live mutation")
check(not rollback.runtime_rollback_execution_authorized, "runtime cannot rollback")
check(acceptance.acceptance_record_id == acceptance.expected_id(), "acceptance stable")
check(validate_slice36_acceptance_record(acceptance).ok, "acceptance validates")
check(acceptance.accepted_increment_labels == SLICE36_INCREMENT_LABELS, "increment list exact")
check(acceptance.accepted_chain == SLICE36_ACCEPTED_CHAIN, "chain exact")
check(acceptance.permanent_boundaries == SLICE36_PERMANENT_BOUNDARIES, "boundaries exact")
check(acceptance.mathematical_direction == SLICE36_MATHEMATICAL_DIRECTION, "math direction exact")
check(acceptance.accepted_scope == SLICE36_ACCEPTED_SCOPE, "accepted scope exact")
check(acceptance.deferred_scope == SLICE36_DEFERRED_SCOPE, "deferred scope exact")
check(acceptance.rollback_metadata_id == rollback.rollback_id, "rollback linked")
check(not acceptance.runtime_self_grants_acceptance, "runtime no self acceptance")
check(acceptance.decision_owner_acceptance_required, "decision owner required")
check(not acceptance.release_authorized, "no release")
check(not acceptance.production_ready, "not production ready")
check(len(SLICE36_PERMANENT_BOUNDARIES) == 21, "twenty one permanent boundaries")
check(len(SLICE36_INCREMENT_LABELS) == 9, "nine accepted increments including 36B0")

for field_name in (
    "live_repository_mutation_authorized",
    "runtime_rollback_execution_authorized",
):
    check(
        not validate_slice36_rollback_metadata(
            replace(rollback, **{field_name: True})
        ).ok,
        f"rollback rejects authority {field_name}",
    )
for field_name in (
    "runtime_self_grants_acceptance",
    "release_authorized",
    "production_ready",
):
    check(
        not validate_slice36_acceptance_record(
            replace(acceptance, **{field_name: True})
        ).ok,
        f"acceptance rejects authority {field_name}",
    )

# Exact fixture catalog.
fixtures = list_bounded_structural_fixtures()
check(type(fixtures) is tuple, "fixture catalog tuple")
check(len(fixtures) == 4, "four exact fixtures")
check(len({fixture.fixture_name for fixture in fixtures}) == 4, "fixture names unique")
check(len({fixture.fixture_id for fixture in fixtures}) == 4, "fixture ids unique")
expected_names = (
    FIXTURE_GOVERNING,
    FIXTURE_ZERO_DERIVATION,
    FIXTURE_QUOTATION_CONFLICT,
    FIXTURE_INCOMPLETE_QUOTATION,
)
check(tuple(fixture.fixture_name for fixture in fixtures) == expected_names, "fixture order exact")
for index, fixture in enumerate(fixtures):
    check(type(fixture) is BoundedStructuralFixtureRecord, f"fixture type {index}")
    check(fixture.fixture_id == fixture.expected_id(), f"fixture stable {index}")
    check(validate_bounded_structural_fixture(fixture).ok, f"fixture validates {index}")
    check(is_exact_accepted_bounded_structural_fixture(fixture), f"fixture accepted {index}")
    check(get_bounded_structural_fixture(fixture.fixture_name) == fixture, f"fixture lookup {index}")
    check(fixture.synthetic, f"fixture synthetic {index}")
    check(fixture.explicit_invocation_only, f"fixture explicit {index}")
    check(fixture.offline_only, f"fixture offline {index}")
    check(fixture.in_memory_only, f"fixture in memory {index}")
    for field_name in (
        "external_context_required",
        "external_resource_allowed",
        "memory_allowed",
        "route_allowed",
        "action_allowed",
        "rendering_allowed",
        "delivery_allowed",
        "selected_meaning_allowed",
    ):
        check(not getattr(fixture, field_name), f"fixture false {index} {field_name}")
    check(
        not is_exact_accepted_bounded_structural_fixture(
            replace(fixture, source_id="tampered")
        ),
        f"fixture exact catalog rejects mutation {index}",
    )
    check(
        not validate_bounded_structural_fixture(
            replace(fixture, source_sha256="0" * 64)
        ).ok,
        f"fixture digest mutation rejected {index}",
    )

check(get_bounded_structural_fixture("unknown") is None, "unknown fixture absent")
check(get_bounded_structural_fixture(3) is None, "non-text fixture lookup absent")
check(not is_exact_accepted_bounded_structural_fixture(object()), "object not fixture")

# Invocation contract.
invocations = []
for index, fixture in enumerate(fixtures):
    invocation = build_fixture_bootstrap_invocation(fixture.fixture_name)
    check(invocation is not None, f"invocation built {index}")
    assert invocation is not None
    invocations.append(invocation)
    check(type(invocation) is BoundedStructuralBootstrapInvocation, f"invocation type {index}")
    check(invocation.invocation_id == invocation.expected_id(), f"invocation stable {index}")
    check(validate_bounded_structural_bootstrap_invocation(invocation).ok, f"invocation validates {index}")
    check(invocation.invocation_kind is BootstrapInvocationKind.SYNTHETIC_FIXTURE, f"fixture kind {index}")
    check(invocation.fixture_id == fixture.fixture_id, f"fixture id linked {index}")
    check(invocation.explicit_invocation, f"explicit invocation {index}")
    check(not invocation.raw_text_carried_by_invocation, f"no raw text in invocation {index}")
    check(
        not validate_bounded_structural_bootstrap_invocation(
            replace(invocation, raw_text_carried_by_invocation=True)
        ).ok,
        f"raw text invocation rejected {index}",
    )
    check(
        not validate_bounded_structural_bootstrap_invocation(
            replace(invocation, explicit_invocation=False)
        ).ok,
        f"implicit invocation rejected {index}",
    )
check(build_fixture_bootstrap_invocation("unknown") is None, "unknown invocation absent")
caller = build_uninstalled_approved_caller_invocation(approved_caller_id="future.caller")
check(caller.invocation_kind is BootstrapInvocationKind.APPROVED_CALLER, "caller kind")
check(validate_bounded_structural_bootstrap_invocation(caller).ok, "caller invocation structurally valid")

# Nothing runs by default, from raw text, or from an uninstalled approved caller.
with patch(
    "aiweb_language_core_bootstrap.bounded_structural_bootstrap.integration.capture_input_event",
    forbidden,
):
    disabled = run_bounded_structural_bootstrap(invocations[0])
    raw_text = run_bounded_structural_bootstrap(
        "Do not install it.",
        integration_state=enabled_state,
    )
    approved_caller = run_bounded_structural_bootstrap(
        caller,
        integration_state=enabled_state,
    )
check(disabled.status is BootstrapIntegrationStatus.REFUSED_DISABLED, "default refusal")
check(disabled.stage_receipt_count == 0, "disabled no stages")
check(disabled.custody_result is None, "disabled no custody")
check(not disabled.raw_text_alone_activated, "disabled no raw activation")
check(raw_text.status is BootstrapIntegrationStatus.HELD_INVALID_INVOCATION, "raw text held")
check(raw_text.stage_receipt_count == 0, "raw text no stages")
check(raw_text.custody_result is None, "raw text no custody")
check(approved_caller.status is BootstrapIntegrationStatus.HELD_APPROVED_CALLER_CATALOG_NOT_INSTALLED, "caller held")
check(approved_caller.stage_receipt_count == 0, "caller no stages")
check(approved_caller.custody_result is None, "caller no custody")
check(validate_bounded_structural_bootstrap_result(disabled, invocation=invocations[0]).ok, "disabled result validates")
check(validate_bounded_structural_bootstrap_result(raw_text).ok, "raw result validates")
check(validate_bounded_structural_bootstrap_result(approved_caller, invocation=caller).ok, "caller result validates")

# Full end-to-end runs under external side-effect interdiction.
results: list[BoundedStructuralBootstrapResult] = []
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(Path, "open", forbidden))
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "read_bytes", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(subprocess, "run", forbidden))
    stack.enter_context(patch.object(subprocess, "Popen", forbidden))
    stack.enter_context(patch.object(os, "listdir", forbidden))
    stack.enter_context(patch.object(os, "scandir", forbidden))
    stack.enter_context(patch.object(os, "walk", forbidden))
    stack.enter_context(patch.object(os, "getenv", forbidden))
    stack.enter_context(patch.object(importlib, "import_module", forbidden))
    for invocation in invocations:
        results.append(
            run_bounded_structural_bootstrap(
                invocation,
                integration_state=enabled_state,
            )
        )

expected_candidate_counts = (8, 0, 4, 1)
expected_statuses = (
    BootstrapIntegrationStatus.COMPLETED_STRUCTURAL_CANDIDATES,
    BootstrapIntegrationStatus.COMPLETED_LAWFUL_NON_PROGRESS,
    BootstrapIntegrationStatus.COMPLETED_STRUCTURAL_CANDIDATES,
    BootstrapIntegrationStatus.COMPLETED_STRUCTURAL_CANDIDATES,
)
expected_stage_order = (
    BootstrapStage.INPUT_CUSTODY,
    BootstrapStage.SOURCE_FIELD_PROJECTION,
    BootstrapStage.OPERATOR_REGISTRY,
    BootstrapStage.OPERATOR_CANDIDATE_BINDING,
    BootstrapStage.PHASE_TRAIL_CONSTRUCTION,
    BootstrapStage.SCOPE_REFERENCE_CONSTRAINTS,
    BootstrapStage.STRUCTURAL_DERIVATION,
)
result_false_fields = (
    "raw_text_alone_activated",
    "hidden_fallback_parser_used",
    "conventional_nlp_authority_used",
    "external_linguistic_resource_loaded",
    "filesystem_search_performed",
    "filesystem_read_performed",
    "filesystem_write_performed",
    "repository_history_search_performed",
    "network_access_performed",
    "web_access_performed",
    "environment_lookup_performed",
    "memory_read_performed",
    "memory_write_performed",
    "protected_memory_retrieval_performed",
    "llm_used",
    "embedding_used",
    "vector_database_used",
    "semantic_similarity_used",
    "learned_parser_used",
    "neural_classifier_used",
    "rag_used",
    "api_route_activated",
    "capability_route_activated",
    "tool_activated",
    "action_executed",
    "outward_rendering_performed",
    "evidence_validation_performed",
    "candidate_meaning_created",
    "selected_meaning_created",
    "concept_resolved",
    "predicate_identity_created",
    "participant_roles_assigned",
    "permission_inferred",
    "capability_authorized",
    "delivery_authorized",
    "technical_acceptance_granted_by_runtime",
    "release_authorized",
    "production_ready",
)
stage_false_fields = (
    "stage_skipped",
    "interpretation_performed",
    "semantic_classification_performed",
    "core_rsoc_operator_application_performed",
    "selected_meaning_created",
    "evidence_validation_performed",
    "filesystem_search_performed",
    "filesystem_read_performed",
    "filesystem_write_performed",
    "repository_history_search_performed",
    "network_access_performed",
    "web_access_performed",
    "memory_read_performed",
    "memory_write_performed",
    "route_registration_performed",
    "capability_route_performed",
    "tool_activation_performed",
    "action_performed",
    "outward_rendering_performed",
    "delivery_authorized",
)

for index, (fixture, invocation, result) in enumerate(zip(fixtures, invocations, results)):
    check(type(result) is BoundedStructuralBootstrapResult, f"result type {index}")
    check(result.result_id == result.expected_id(), f"result stable {index}")
    check(result.status is expected_statuses[index], f"result status {index}")
    check(result.final_structural_candidate_count == expected_candidate_counts[index], f"candidate count {index}")
    check(result.final_non_progress_reasons == fixture.expected_non_progress_reasons, f"non-progress exact {index}")
    check(result.stage_receipt_count == 7, f"seven receipts {index}")
    check(result.completed_stage_count == 7, f"seven completed {index}")
    check(result.exact_stage_chain_complete, f"exact chain {index}")
    check(result.no_stage_skipped, f"no stage skipped {index}")
    check(result.source_reconstruction_proven, f"source reconstruction {index}")
    check(result.all_predecessor_records_exact, f"predecessor ids exact {index}")
    check(result.all_predecessor_versions_exact, f"predecessor versions exact {index}")
    check(result.source_sha256 == fixture.source_sha256, f"source digest preserved {index}")
    check(result.explicitly_invoked, f"explicit result {index}")
    check(tuple(receipt.stage for receipt in result.stage_receipts) == expected_stage_order, f"stage order {index}")
    check(tuple(receipt.stage_ordinal for receipt in result.stage_receipts) == tuple(range(1, 8)), f"ordinals {index}")
    check(len({receipt.receipt_id for receipt in result.stage_receipts}) == 7, f"receipt ids unique {index}")
    check(validate_bounded_structural_bootstrap_result(result, invocation=invocation, fixture=fixture).ok, f"result validates {index}")
    for field_name in result_false_fields:
        check(not getattr(result, field_name), f"result no authority {index} {field_name}")
    for receipt_index, receipt in enumerate(result.stage_receipts):
        check(type(receipt) is BootstrapStageReceipt, f"receipt type {index} {receipt_index}")
        check(receipt.receipt_id == receipt.expected_id(), f"receipt stable {index} {receipt_index}")
        check(validate_bootstrap_stage_receipt(receipt).ok, f"receipt validates {index} {receipt_index}")
        check(receipt.invocation_id == invocation.invocation_id, f"receipt invocation {index} {receipt_index}")
        check(receipt.state_id == enabled_state.state_id, f"receipt state {index} {receipt_index}")
        check(receipt.source_event_id == result.source_event_id, f"receipt source event {index} {receipt_index}")
        check(receipt.source_sha256 == result.source_sha256, f"receipt source hash {index} {receipt_index}")
        check(receipt.predecessor_identity_verified, f"receipt predecessor id {index} {receipt_index}")
        check(receipt.predecessor_version_verified, f"receipt predecessor version {index} {receipt_index}")
        check(receipt.output_validation_passed, f"receipt output valid {index} {receipt_index}")
        check(receipt.source_ancestry_preserved, f"receipt ancestry {index} {receipt_index}")
        for field_name in stage_false_fields:
            check(not getattr(receipt, field_name), f"receipt no authority {index} {receipt_index} {field_name}")
    structural_set = result.structural_result.structural_set
    assert structural_set is not None
    check(structural_set.candidate_count == result.final_structural_candidate_count, f"nested candidates {index}")
    check(structural_set.all_source_ancestry_preserved, f"nested source ancestry {index}")
    check(structural_set.all_source_reconstruction_proven, f"nested reconstruction {index}")
    check(structural_set.all_phase_trails_preserved, f"nested phase trails {index}")
    check(structural_set.all_scope_occurrences_preserved, f"nested scope {index}")
    check(structural_set.all_attachment_candidates_preserved, f"nested attachments {index}")
    check(structural_set.all_reference_candidates_preserved, f"nested references {index}")
    check(structural_set.selected_structural_candidate_id is None, f"nested no selected structure {index}")
    check(not structural_set.candidate_meaning_created, f"nested no candidate meaning {index}")
    check(not structural_set.selected_meaning, f"nested no selected meaning {index}")
    check(not structural_set.clarification_question_asked, f"nested no clarification {index}")
    check(not structural_set.semantic_rejection_performed, f"nested no rejection {index}")

# Exact deterministic rerun identity.
for index, (fixture, invocation, first) in enumerate(zip(fixtures, invocations, results)):
    second = run_bounded_structural_bootstrap(
        invocation,
        integration_state=enabled_state,
    )
    check(second == first, f"deterministic complete result {index}")
    check(second.result_id == first.result_id, f"deterministic result id {index}")
    check(second.stage_receipts == first.stage_receipts, f"deterministic receipts {index}")
    check(second.structural_result == first.structural_result, f"deterministic structural result {index}")
    check(validate_bounded_structural_bootstrap_result(second, invocation=invocation, fixture=fixture).ok, f"rerun validates {index}")

# Tamper rejection on completed results and receipts.
governing = results[0]
governing_fixture = fixtures[0]
governing_invocation = invocations[0]
for field_name in result_false_fields:
    tampered = replace(governing, **{field_name: True})
    check(
        not validate_bounded_structural_bootstrap_result(
            tampered,
            invocation=governing_invocation,
            fixture=governing_fixture,
        ).ok,
        f"result authority tamper rejected {field_name}",
    )
check(
    not validate_bounded_structural_bootstrap_result(
        replace(governing, stage_receipt_count=6),
        invocation=governing_invocation,
        fixture=governing_fixture,
    ).ok,
    "stage count tamper rejected",
)
check(
    not validate_bounded_structural_bootstrap_result(
        replace(governing, exact_stage_chain_complete=False),
        invocation=governing_invocation,
        fixture=governing_fixture,
    ).ok,
    "chain flag tamper rejected",
)
first_receipt = governing.stage_receipts[0]
for field_name in stage_false_fields:
    tampered_receipt = replace(first_receipt, **{field_name: True})
    check(
        not validate_bootstrap_stage_receipt(tampered_receipt).ok,
        f"receipt authority tamper rejected {field_name}",
    )
check(
    not validate_bootstrap_stage_receipt(
        replace(first_receipt, predecessor_schema_version="wrong")
    ).ok,
    "receipt predecessor version tamper rejected",
)
check(
    not validate_bootstrap_stage_receipt(
        replace(first_receipt, stage_ordinal=7)
    ).ok,
    "receipt order tamper rejected",
)

# Exact types only.
for value, validator, label in (
    (object(), validate_bounded_structural_bootstrap_state, "state"),
    (object(), validate_bounded_structural_fixture, "fixture"),
    (object(), validate_bounded_structural_bootstrap_invocation, "invocation"),
    (object(), validate_bootstrap_stage_receipt, "receipt"),
    (object(), validate_slice36_rollback_metadata, "rollback"),
    (object(), validate_slice36_acceptance_record, "acceptance"),
    (object(), validate_bounded_structural_bootstrap_result, "result"),
):
    check(not validator(value).ok, f"exact type required {label}")

# Dataclass field inventory guards against accidental record shrinkage.
check(len(fields(BoundedStructuralBootstrapState)) >= 60, "state field inventory bounded")
check(len(fields(BoundedStructuralFixtureRecord)) >= 30, "fixture field inventory bounded")
check(len(fields(BootstrapStageReceipt)) >= 45, "receipt field inventory bounded")
check(len(fields(BoundedStructuralBootstrapResult)) >= 80, "result field inventory bounded")

print("AI.WEB SLICE 36H BEHAVIOR TEST: PASS")
print(f"checks={checks}")
print("accepted_static_fixtures=4")
print("exact_integration_stages=7")
print("governing_structural_candidates=8")
print("zero_derivation_candidates=0")
print("quotation_conflict_candidates=4")
print("incomplete_quotation_candidates=1")
print("raw_text_activations=0")
print("approved_caller_catalog_entries=0")
print("selected_meanings=0")
print("routes_tools_actions_renderings_deliveries=0")
