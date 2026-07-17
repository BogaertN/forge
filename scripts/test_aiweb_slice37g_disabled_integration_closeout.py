#!/usr/bin/env python3
"""Behavior, adversarial and authority-boundary tests for Slice 37G."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import builtins
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

from aiweb_language_core_bootstrap.disabled_structural_concept_bootstrap import (
    PRE_SLICE37_COMMIT,
    PRE_SLICE37_TREE,
    SLICE37_ACCEPTED_CHAIN,
    SLICE37_ACCEPTED_SCOPE,
    SLICE37_DEFERRED_SCOPE,
    SLICE37_INCREMENT_LABELS,
    SLICE37_PERMANENT_BOUNDARIES,
    SLICE37F_ACCEPTED_HEAD,
    SLICE37F_ACCEPTED_TREE,
    DisabledStructuralConceptBootstrapResult,
    DisabledStructuralConceptBootstrapState,
    DisabledStructuralConceptFixture,
    DisabledStructuralConceptInvocation,
    FIXTURE_AMBIGUOUS,
    FIXTURE_NO_MATCH,
    FIXTURE_ONE_TO_ONE,
    FIXTURE_UNMAPPED,
    FIXTURE_UNSUPPORTED,
    IntegrationStage,
    IntegrationStatus,
    build_disabled_structural_concept_bootstrap_state,
    build_fixture_invocation,
    build_slice37_acceptance_record,
    build_slice37_rollback_metadata,
    get_disabled_structural_concept_fixture,
    is_exact_accepted_fixture,
    list_disabled_structural_concept_fixtures,
    run_disabled_structural_concept_bootstrap,
    validate_acceptance_record,
    validate_fixture,
    validate_integration_result,
    validate_integration_state,
    validate_invocation,
    validate_rollback_metadata,
    validate_stage_receipt,
)
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import (
    ProposalResultStatus,
    build_default_structural_concept_proposal_profile,
)


checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("forbidden side effect or authority surface attempted")


default_state = build_disabled_structural_concept_bootstrap_state()
enabled_state = build_disabled_structural_concept_bootstrap_state(
    explicit_offline_developer_enable=True
)

for state, enabled in ((default_state, False), (enabled_state, True)):
    check(type(state) is DisabledStructuralConceptBootstrapState, "exact state type")
    check(state.state_id == state.expected_id(), "stable state identity")
    check(validate_integration_state(state).ok, "state validates")
    check(state.enabled is enabled, "state enabled exact")
    check(
        state.explicit_offline_developer_enable is enabled,
        "state explicit enable exact",
    )
    for name in (
        "disabled_by_default",
        "explicit_invocation_required",
        "accepted_static_fixture_only",
        "offline_only",
        "standard_library_only",
        "deterministic",
        "read_only",
        "in_memory_only",
        "exact_profile_bounded",
        "source_preserving",
        "structural_ancestry_preserving",
        "registry_snapshot_preserving",
        "zero_one_many_preserving",
        "explicit_unknown_preserving",
        "explicit_unsupported_preserving",
        "rollback_safe",
    ):
        check(getattr(state, name) is True, f"state true {name}")
    for name in (
        "automatic_activation_allowed",
        "arbitrary_text_invocation_allowed",
        "conventional_word_token_authority_allowed",
        "normalization_allowed",
        "semantic_similarity_allowed",
        "learned_model_allowed",
        "external_resource_loading_allowed",
        "filesystem_read_allowed",
        "filesystem_write_allowed",
        "network_allowed",
        "memory_read_allowed",
        "memory_write_allowed",
        "api_route_allowed",
        "capability_route_allowed",
        "tool_invocation_allowed",
        "action_allowed",
        "rendering_allowed",
        "delivery_allowed",
        "candidate_meaning_allowed",
        "selected_meaning_allowed",
        "selected_sense_allowed",
        "predicate_identity_allowed",
        "participant_role_allowed",
        "truth_allowed",
        "evidence_validity_allowed",
        "clarification_allowed",
        "permission_allowed",
        "runtime_self_acceptance_allowed",
        "release_authorized",
        "production_ready",
    ):
        check(getattr(state, name) is False, f"state false {name}")

try:
    enabled_state.enabled = False  # type: ignore[misc]
except FrozenInstanceError:
    check(True, "state immutable")
else:
    check(False, "state must be immutable")

for name in (
    "automatic_activation_allowed",
    "conventional_word_token_authority_allowed",
    "normalization_allowed",
    "semantic_similarity_allowed",
    "learned_model_allowed",
    "memory_read_allowed",
    "api_route_allowed",
    "tool_invocation_allowed",
    "action_allowed",
    "candidate_meaning_allowed",
    "selected_meaning_allowed",
    "truth_allowed",
    "permission_allowed",
    "release_authorized",
):
    check(
        not validate_integration_state(
            replace(enabled_state, **{name: True})
        ).ok,
        f"state rejects authority enlargement {name}",
    )

rollback = build_slice37_rollback_metadata()
acceptance = build_slice37_acceptance_record(rollback_metadata=rollback)
check(rollback.rollback_id == rollback.expected_id(), "rollback stable")
check(validate_rollback_metadata(rollback).ok, "rollback validates")
check(rollback.pre_slice37_commit == PRE_SLICE37_COMMIT, "pre Slice 37 commit")
check(rollback.pre_slice37_tree == PRE_SLICE37_TREE, "pre Slice 37 tree")
check(rollback.accepted_parent_head == SLICE37F_ACCEPTED_HEAD, "parent head")
check(rollback.accepted_parent_tree == SLICE37F_ACCEPTED_TREE, "parent tree")
check(not rollback.live_repository_mutation_authorized, "no live rollback mutation")
check(not rollback.runtime_rollback_execution_authorized, "no runtime rollback")
check(acceptance.acceptance_record_id == acceptance.expected_id(), "acceptance stable")
check(validate_acceptance_record(acceptance).ok, "acceptance validates")
check(acceptance.accepted_increment_labels == SLICE37_INCREMENT_LABELS, "labels exact")
check(acceptance.accepted_chain == SLICE37_ACCEPTED_CHAIN, "chain exact")
check(acceptance.permanent_boundaries == SLICE37_PERMANENT_BOUNDARIES, "boundaries exact")
check(acceptance.accepted_scope == SLICE37_ACCEPTED_SCOPE, "accepted scope exact")
check(acceptance.deferred_scope == SLICE37_DEFERRED_SCOPE, "deferred scope exact")
check(len(SLICE37_PERMANENT_BOUNDARIES) == 19, "nineteen permanent boundaries")
check(not acceptance.runtime_self_grants_acceptance, "no runtime acceptance")
check(acceptance.decision_owner_acceptance_required, "decision owner required")
check(not acceptance.release_authorized, "no release")
check(not acceptance.production_ready, "not production ready")

fixtures = list_disabled_structural_concept_fixtures()
check(type(fixtures) is tuple, "fixture catalog tuple")
check(len(fixtures) == 5, "five exact fixtures")
check(len({item.fixture_id for item in fixtures}) == 5, "fixture ids unique")
check(len({item.fixture_name for item in fixtures}) == 5, "fixture names unique")
check(
    tuple(item.fixture_name for item in fixtures)
    == (
        FIXTURE_ONE_TO_ONE,
        FIXTURE_AMBIGUOUS,
        FIXTURE_UNMAPPED,
        FIXTURE_UNSUPPORTED,
        FIXTURE_NO_MATCH,
    ),
    "fixture order exact",
)

expected_integration_status = {
    FIXTURE_ONE_TO_ONE: IntegrationStatus.COMPLETED_CANDIDATES,
    FIXTURE_AMBIGUOUS: IntegrationStatus.COMPLETED_UNRESOLVED,
    FIXTURE_UNMAPPED: IntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN,
    FIXTURE_UNSUPPORTED: IntegrationStatus.COMPLETED_EXPLICIT_UNSUPPORTED,
    FIXTURE_NO_MATCH: IntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN,
}

results = {}
for index, fixture in enumerate(fixtures):
    check(type(fixture) is DisabledStructuralConceptFixture, f"fixture type {index}")
    check(fixture.fixture_id == fixture.expected_id(), f"fixture stable {index}")
    check(validate_fixture(fixture).ok, f"fixture validates {index}")
    check(is_exact_accepted_fixture(fixture), f"fixture accepted {index}")
    check(
        get_disabled_structural_concept_fixture(fixture.fixture_name) == fixture,
        f"fixture lookup {index}",
    )
    check(fixture.accepted_fixture, f"fixture accepted flag {index}")
    check(fixture.synthetic, f"fixture synthetic {index}")
    check(fixture.explicit_invocation_only, f"fixture explicit {index}")
    check(fixture.offline_only, f"fixture offline {index}")
    check(fixture.in_memory_only, f"fixture in memory {index}")
    check(
        fixture.raw_text_not_carried_by_invocation,
        f"fixture source not invocation text {index}",
    )

    invocation = build_fixture_invocation(fixture.fixture_name)
    check(type(invocation) is DisabledStructuralConceptInvocation, f"invocation type {index}")
    assert invocation is not None
    check(invocation.invocation_id == invocation.expected_id(), f"invocation stable {index}")
    check(validate_invocation(invocation).ok, f"invocation validates {index}")
    check(invocation.fixture_id == fixture.fixture_id, f"invocation fixture ref {index}")
    check(not invocation.raw_text_carried_by_invocation, f"invocation no text {index}")

    disabled = run_disabled_structural_concept_bootstrap(invocation)
    check(type(disabled) is DisabledStructuralConceptBootstrapResult, f"disabled type {index}")
    check(disabled.status is IntegrationStatus.REFUSED_DISABLED, f"disabled status {index}")
    check(disabled.stage_receipt_count == 0, f"disabled no stages {index}")
    check(disabled.proposal_result is None, f"disabled no proposal {index}")
    check(validate_integration_result(disabled).ok, f"disabled validates {index}")

    first = run_disabled_structural_concept_bootstrap(
        invocation,
        integration_state=enabled_state,
    )
    second = run_disabled_structural_concept_bootstrap(
        invocation,
        integration_state=enabled_state,
    )
    results[fixture.fixture_name] = first
    check(first == second, f"deterministic repeated result {index}")
    check(first.result_id == second.result_id, f"deterministic result id {index}")
    check(first.result_id == first.expected_id(), f"result stable {index}")
    check(validate_integration_result(first).ok, f"result validates {index}")
    check(
        first.status is expected_integration_status[fixture.fixture_name],
        f"integration status {index}",
    )
    check(first.reason_code == "exact_slice36_to_slice37_candidate_chain_completed", f"reason {index}")
    check(first.stage_receipt_count == 8, f"eight stages {index}")
    check(first.exact_stage_chain_complete, f"exact chain {index}")
    check(
        tuple(item.stage for item in first.stage_receipts)
        == tuple(IntegrationStage),
        f"stage order {index}",
    )
    check(
        tuple(item.stage_ordinal for item in first.stage_receipts)
        == tuple(range(1, 9)),
        f"stage ordinals {index}",
    )
    for stage_index, receipt in enumerate(first.stage_receipts):
        check(receipt.receipt_id == receipt.expected_id(), f"receipt stable {index}-{stage_index}")
        check(validate_stage_receipt(receipt).ok, f"receipt validates {index}-{stage_index}")
        check(receipt.output_validation_passed, f"receipt validation {index}-{stage_index}")
        check(receipt.source_ancestry_preserved, f"receipt source {index}-{stage_index}")
        check(not receipt.selected_meaning_created, f"receipt no selection {index}-{stage_index}")
        check(not receipt.truth_determined, f"receipt no truth {index}-{stage_index}")
        check(not receipt.permission_inferred, f"receipt no permission {index}-{stage_index}")
        check(not receipt.memory_accessed, f"receipt no memory {index}-{stage_index}")
        check(not receipt.route_created, f"receipt no route {index}-{stage_index}")
        check(not receipt.tool_invoked, f"receipt no tool {index}-{stage_index}")
        check(not receipt.action_performed, f"receipt no action {index}-{stage_index}")
        check(not receipt.rendered, f"receipt no render {index}-{stage_index}")
        check(not receipt.delivered, f"receipt no delivery {index}-{stage_index}")

    proposal = first.proposal_result
    assert proposal is not None
    check(
        proposal.status.value == fixture.expected_proposal_status,
        f"proposal status {index}",
    )
    check(
        first.lexical_occurrence_count == fixture.expected_lexical_occurrence_count,
        f"lexical count {index}",
    )
    check(
        first.concept_candidate_count == fixture.expected_concept_candidate_count,
        f"concept count {index}",
    )
    check(
        first.sense_candidate_count == fixture.expected_sense_candidate_count,
        f"sense count {index}",
    )
    check(
        first.explicit_unknown_count == fixture.expected_unknown_count,
        f"unknown count {index}",
    )
    check(
        first.explicit_unsupported_count == fixture.expected_unsupported_count,
        f"unsupported count {index}",
    )
    check(first.proposal_profile_id == proposal.profile.profile_id, f"profile ref {index}")
    check(
        first.registry_snapshot_id == proposal.registry_snapshot.snapshot_id,
        f"snapshot ref {index}",
    )
    check(first.source_event_id == proposal.source_event_id, f"source event ref {index}")
    check(first.source_sha256 == proposal.source_sha256, f"source digest ref {index}")
    for name in (
        "candidate_meaning_created",
        "selected_meaning_created",
        "selected_sense_created",
        "predicate_identity_created",
        "participant_roles_assigned",
        "truth_determined",
        "evidence_validity_determined",
        "clarification_asked",
        "permission_inferred",
        "memory_read_performed",
        "memory_write_performed",
        "api_route_created",
        "capability_route_created",
        "tool_invoked",
        "action_performed",
        "outward_rendered",
        "delivered",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "semantic_similarity_used",
        "technical_acceptance_granted_by_runtime",
        "release_authorized",
        "production_ready",
    ):
        check(getattr(first, name) is False, f"result false {name} {index}")

check(
    results[FIXTURE_ONE_TO_ONE].proposal_result.status
    is ProposalResultStatus.CANDIDATES_PROPOSED,
    "one-to-one proposal status",
)
check(results[FIXTURE_ONE_TO_ONE].concept_candidate_count == 1, "one concept")
check(results[FIXTURE_ONE_TO_ONE].sense_candidate_count == 1, "one sense")
check(
    results[FIXTURE_AMBIGUOUS].proposal_result.status
    is ProposalResultStatus.CANDIDATES_WITH_UNRESOLVED_STATES,
    "ambiguous proposal status",
)
check(results[FIXTURE_AMBIGUOUS].concept_candidate_count == 2, "two concepts")
check(results[FIXTURE_AMBIGUOUS].sense_candidate_count == 2, "two senses")
check(
    results[FIXTURE_UNMAPPED].proposal_result.status
    is ProposalResultStatus.EXPLICIT_UNKNOWN,
    "unmapped explicit unknown",
)
check(
    results[FIXTURE_UNSUPPORTED].proposal_result.status
    is ProposalResultStatus.EXPLICIT_UNSUPPORTED,
    "unsupported explicit",
)
check(
    results[FIXTURE_NO_MATCH].lexical_occurrence_count == 0,
    "no-match no lexical occurrence",
)

# Invalid invocation/profile/state fail closed.
check(build_fixture_invocation("not-a-fixture") is None, "unknown fixture no invocation")
invalid_invocation = replace(
    build_fixture_invocation(FIXTURE_AMBIGUOUS),
    invocation_id="tampered",
)
check(
    run_disabled_structural_concept_bootstrap(
        invalid_invocation,
        integration_state=enabled_state,
    ).status is IntegrationStatus.HELD_INVALID_INVOCATION,
    "tampered invocation held",
)
profile = build_default_structural_concept_proposal_profile()
tampered_profile = replace(
    profile,
    profile_id="",
    semantic_similarity_allowed=True,
)
tampered_profile = replace(
    tampered_profile,
    profile_id=tampered_profile.expected_id(),
)
check(
    run_disabled_structural_concept_bootstrap(
        build_fixture_invocation(FIXTURE_AMBIGUOUS),
        integration_state=enabled_state,
        profile=tampered_profile,
    ).status is IntegrationStatus.HELD_INVALID_PROFILE,
    "tampered profile held",
)
invalid_state = replace(enabled_state, state_id="tampered")
check(
    run_disabled_structural_concept_bootstrap(
        build_fixture_invocation(FIXTURE_AMBIGUOUS),
        integration_state=invalid_state,
    ).status is IntegrationStatus.HELD_INVALID_STATE,
    "tampered state held",
)

# The complete chain performs no external side effect even when enabled.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(subprocess, "run", forbidden))
    stack.enter_context(patch.object(subprocess, "Popen", forbidden))
    stack.enter_context(patch.object(os, "system", forbidden))
    guarded = run_disabled_structural_concept_bootstrap(
        build_fixture_invocation(FIXTURE_ONE_TO_ONE),
        integration_state=enabled_state,
    )
check(guarded.status is IntegrationStatus.COMPLETED_CANDIDATES, "side-effect guard run")
check(validate_integration_result(guarded).ok, "side-effect guard validates")

print("AI.WEB SLICE 37G BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"fixture_count={len(fixtures)}")
print("integration_stage_count=8")
print("deterministic_repeat_count=5")
print("one_to_one_concept_candidates=1")
print("ambiguous_concept_candidates=2")
print("ambiguous_sense_candidates=2")
print("explicit_unknown_fixtures=2")
print("explicit_unsupported_fixtures=1")
print("conventional_word_token_authority=0")
print("candidate_meaning_selected_meaning_selected_sense=0")
print("truth_evidence_permission=0")
print("memory_routes_tools_actions_rendering_delivery=0")
