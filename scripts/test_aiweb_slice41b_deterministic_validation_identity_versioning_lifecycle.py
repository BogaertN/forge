#!/usr/bin/env python3
"""Visible behavior test for AI.Web Slice 41B."""

from __future__ import annotations

import argparse
import copy
from dataclasses import FrozenInstanceError, fields, replace
import importlib
import sys
from pathlib import Path


PARENT_PACKAGE = "aiweb_language_core_bootstrap.selected_meaning_runtime"
PACKAGE = PARENT_PACKAGE + ".governed_lifecycle"
EXPECTED_PARENT_HEAD = "9c9a9135d07991446a720b845611bf3c153db522"
EXPECTED_PARENT_TREE = "781a691f863aba4defc2dab12df192be6c18b075"
EXPECTED_PARENT_SUBJECT = (
    "Slice 41A selected meaning runtime core schema and authority contract"
)


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)


def _raw_fixture(m):
    candidate = m.SelectionCandidateCustodyRecord(
        selection_candidate_custody_id="placeholder",
        candidate_meaning_id="candidate_meaning:demo",
        candidate_state_id="candidate_state:demo",
        candidate_lineage_id="lineage:demo",
        source_expression_ref="source_expression:demo",
        manifest_candidate_record_ref="msm_candidate_record:demo",
        manifest_candidate_companion_ref="msm_candidate_companion:demo",
        candidate_identity_ref="candidate_identity:demo",
        candidate_content_ref="candidate_content:demo",
        candidate_provenance_ref="candidate_provenance:demo",
        candidate_construction_receipt_ref="candidate_receipt:demo",
        candidate_set_ref="candidate_set:demo",
        candidate_set_member_ref="candidate_set_member:demo",
        candidate_lifecycle_ref="candidate_lifecycle:demo",
        gate_candidate_input_ref="gate_candidate_input:demo",
        predecessor_receipt_refs=("slice39h_receipt:demo",),
    )
    return candidate


def _fixture(m, g):
    candidate = g.with_expected_id(_raw_fixture(m))
    gate = g.with_expected_id(m.GateCustodyReferenceRecord(
        gate_custody_reference_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        msm_gate_custody_companion_ref="msm_gate_companion:demo",
        expectancy_family_custody_ref="gate_family_custody:expectancy",
        congruity_family_custody_ref="gate_family_custody:congruity",
        connectedness_family_custody_ref="gate_family_custody:connectedness",
        recoverable_purpose_family_custody_ref="gate_family_custody:recoverable_purpose",
        expectancy_result_ref="expectancy_result:demo",
        congruity_result_ref="congruity_result:demo",
        connectedness_result_ref="connectedness_result:demo",
        recoverable_purpose_result_ref="recoverable_purpose_result:demo",
        composition_result_ref="gate_composition_result:demo",
        composition_disposition_refs=("disposition:candidate_supported_for_later_selection_review",),
        candidate_specific_disposition_refs=("candidate_disposition:demo",),
        gate_profile_refs=(
            "gate_profile:expectancy:v1", "gate_profile:congruity:v1",
            "gate_profile:connectedness:v1", "gate_profile:recoverable_purpose:v1",
        ),
        gate_trace_refs=("gate_trace:demo",),
        gate_provenance_refs=("gate_provenance:demo",),
        gate_limitation_refs=("gate_limitation:demo",),
    ))
    alternatives = g.with_expected_id(m.AlternativeCandidateCustodyRecord(
        alternative_candidate_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        candidate_set_ref=candidate.candidate_set_ref,
        preserved_alternative_candidate_refs=("candidate_meaning:alternative",),
        non_selected_candidate_refs=("candidate_meaning:alternative",),
        alternative_relationship_refs=("alternative_relationship:demo",),
        alternative_disposition_refs=("alternative_disposition:preserved",),
        material_ambiguity_refs=("material_ambiguity:demo",),
        clarification_relevant_refs=("clarification_relevant:demo",),
        shared_ancestry_refs=("shared_ancestry:demo",),
        exact_duplicate_group_refs=(),
    ))
    unresolved = g.with_expected_id(m.UnresolvedStateCustodyRecord(
        unresolved_state_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        unresolved_candidate_refs=("candidate_meaning:alternative",),
        unknown_refs=("unknown:demo",),
        unsupported_refs=("unsupported:demo",),
        conflicted_refs=("conflicted:demo",),
        clarification_dependency_refs=("clarification_dependency:demo",),
        held_refs=("held:demo",),
        blocked_progression_refs=("blocked_progression:demo",),
        refusal_relevant_refs=("refusal_relevant:demo",),
        missing_authority_refs=("missing_authority:demo",),
        missing_structure_refs=("missing_structure:demo",),
        deferred_dependency_refs=("slice41c",),
    ))
    limitations = g.with_expected_id(m.InheritedLimitationCustodyRecord(
        inherited_limitation_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        source_limitation_refs=("source_limitation:demo",),
        candidate_limitation_refs=("candidate_limitation:demo",),
        gate_limitation_refs=("gate_limitation:demo",),
        effect_boundary_refs=("effect_boundary:read_only",),
        domain_sensitive_refs=("domain_sensitive:software",),
        authority_sensitive_distinction_refs=("request_meaning_is_not_authorization",),
        evidence_boundary_refs=("evidence_boundary:not_validated",),
        memory_boundary_refs=("memory_boundary:no_access_no_write",),
        privacy_boundary_refs=("privacy_boundary:preserve",),
        delivery_boundary_refs=("delivery_boundary:not_authorized",),
        execution_boundary_refs=("execution_boundary:not_authorized",),
        correction_ancestry_refs=("correction_ancestry:demo",),
        supersession_ancestry_refs=("supersession_ancestry:demo",),
    ))
    requirement = g.with_expected_id(m.SelectionAuthorityRequirementRecord(
        selection_authority_requirement_id="placeholder",
        requirement_key="exact_candidate_specific_gate_support",
        requirement_version="v1.0.0",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        governing_document_refs=("document6", "document9", "document10"),
        required_authority_profile_refs=("selection_authority_profile:demo",),
        required_candidate_state_refs=("candidate_state:constructed",),
        required_gate_disposition_refs=("candidate_supported_for_later_selection_review",),
        required_alternative_custody_refs=(alternatives.alternative_candidate_custody_id,),
        required_unresolved_custody_refs=(unresolved.unresolved_state_custody_id,),
        required_limitation_custody_refs=(limitations.inherited_limitation_custody_id,),
        required_predecessor_receipt_refs=("slice40h_receipt:demo",),
        deferred_authority_refs=("slice41c", "slice41d", "slice41e"),
    ))
    eligibility = g.with_expected_id(m.SelectionEligibilityStatusRecord(
        selection_eligibility_status_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(requirement.selection_authority_requirement_id,),
        alternative_candidate_custody_ref=alternatives.alternative_candidate_custody_id,
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=limitations.inherited_limitation_custody_id,
        custody_state=m.SelectionEligibilityCustodyState.NOT_EVALUATED,
        status_reason_refs=("slice41b_validation_only",),
        later_evaluator_ref="slice41c",
    ))
    decision = g.with_expected_id(m.SelectedMeaningDecisionStatusRecord(
        selected_meaning_decision_status_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=eligibility.selection_eligibility_status_id,
        custody_state=m.SelectedMeaningDecisionCustodyState.NOT_DECIDED,
        decision_reason_refs=("slice41b_validation_only",),
        later_constructor_ref="slice41d",
    ))
    trace = g.with_expected_id(m.SelectionTraceBoundaryRecord(
        selection_trace_boundary_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(requirement.selection_authority_requirement_id,),
        alternative_candidate_custody_ref=alternatives.alternative_candidate_custody_id,
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=limitations.inherited_limitation_custody_id,
        selection_eligibility_status_ref=eligibility.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=decision.selected_meaning_decision_status_id,
        source_trace_refs=("source_trace:demo",),
        candidate_trace_refs=("candidate_trace:demo",),
        gate_trace_refs=("gate_trace:demo",),
        composition_trace_refs=("composition_trace:demo",),
        predecessor_receipt_refs=("slice40h_receipt:demo",),
        authority_version_refs=(("document6", "v1"),),
        schema_version_refs=(("msm_gate_custody", "v1"),),
    ))
    receipt = g.with_expected_id(m.SelectionReceiptBoundaryRecord(
        selection_receipt_boundary_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=eligibility.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=decision.selected_meaning_decision_status_id,
        selection_trace_boundary_ref=trace.selection_trace_boundary_id,
        required_law_refs=(
            "selected_meaning_is_not_truth", "selected_meaning_is_not_evidence",
            "selected_meaning_is_not_permission", "selected_meaning_is_not_execution",
        ),
        prohibited_consequence_refs=(
            "truth_determination", "evidence_validation", "permission_grant",
            "execution_authorization", "route_creation", "tool_invocation",
            "memory_write", "output_rendering", "delivery",
        ),
        audit_note="Validation custody only; no selection receipt exists.",
    ))
    runtime = g.with_expected_id(m.SelectedMeaningRuntimeSchemaRecord(
        selected_meaning_runtime_schema_record_id="placeholder",
        selection_candidate_custody=candidate,
        gate_custody_reference=gate,
        selection_authority_requirements=(requirement,),
        alternative_candidate_custody=alternatives,
        unresolved_state_custody=unresolved,
        inherited_limitation_custody=limitations,
        selection_eligibility_status=eligibility,
        selected_meaning_decision_status=decision,
        selection_trace_boundary=trace,
        selection_receipt_boundary=receipt,
    ))
    version = g.with_expected_id(g.SelectedMeaningVersionCustody(
        custody_id="placeholder",
        runtime_schema_record_id=runtime.selected_meaning_runtime_schema_record_id,
        runtime_schema_version=runtime.schema_version,
        runtime_schema_id=runtime.schema_id,
        runtime_spec_id=runtime.spec_id,
        runtime_spec_version=runtime.spec_version,
        record_schema_versions=g.expected_record_schema_versions(runtime),
        predecessor_references=g.expected_predecessor_references(runtime),
        accepted_parent_head=g.SLICE41B_ACCEPTED_PARENT_HEAD,
        accepted_parent_tree=g.SLICE41B_ACCEPTED_PARENT_TREE,
        accepted_parent_subject=g.SLICE41B_ACCEPTED_PARENT_SUBJECT,
        canonical_field_order_version=g.CANONICAL_FIELD_ORDER_VERSION,
        digest_algorithm=g.DIGEST_ALGORITHM,
        non_llm_provenance=True,
        timestamps_in_identity=False,
        randomness_in_identity=False,
        process_identity_in_identity=False,
        filesystem_state_in_identity=False,
        environment_state_in_identity=False,
        hash_table_order_in_identity=False,
        eligibility_evaluation_authorized=False,
        candidate_ranking_authorized=False,
        selection_authorized=False,
        selected_meaning_construction_authorized=False,
        msm_v1_mutation_authorized=False,
        bootstrap_integration_authorized=False,
        truth_evidence_permission_execution_authorized=False,
        route_tool_action_memory_rendering_delivery_authorized=False,
    ))
    lifecycle = g.with_expected_id(g.SelectedMeaningLifecycleRecord(
        lifecycle_record_id="placeholder",
        runtime_schema_record_id=runtime.selected_meaning_runtime_schema_record_id,
        version_custody_ref=version.custody_id,
        stage=g.SelectedMeaningLifecycleStage.SCHEMA_DECLARED,
        predecessor_lifecycle_record_ids=(),
        predecessor_reference_ids=tuple(value for _, value in version.predecessor_references),
        validation_issue_digest_refs=(),
        reason_refs=("slice41b_schema_declared",),
        automatic_progression=False,
        canonical_serialization_performed=False,
        deterministic_identity_validated=False,
        predecessor_references_validated=False,
        cross_record_consistency_validated=False,
        malformed_record_rejected=False,
        unknown_version_rejected=False,
        duplicate_record_rejected=False,
        identity_collision_rejected=False,
        eligibility_evaluated=False,
        gate_result_created=False,
        candidate_ranked=False,
        selection_performed=False,
        selected_meaning_created=False,
        msm_v1_modified=False,
        bootstrap_integration_enabled=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_written=False,
        rendered=False,
        delivered=False,
    ))
    bundle = g.with_expected_bundle_identity(g.SelectedMeaningGovernanceBundle(
        bundle_id="placeholder",
        bundle_digest="0" * 64,
        runtime_schema_record=runtime,
        version_custody=version,
        lifecycle_record=lifecycle,
        lifecycle_transitions=(),
        validation_only=True,
        immutable_successor_records=True,
        exact_predecessor_references_required=True,
        duplicate_and_collision_rejection_required=True,
        unknown_version_rejection_required=True,
        eligibility_evaluated=False,
        gate_result_created=False,
        candidate_ranked=False,
        selection_performed=False,
        selected_meaning_created=False,
        msm_v1_modified=False,
        bootstrap_integration_enabled=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_written=False,
        rendered=False,
        delivered=False,
    ))
    return runtime, version, lifecycle, bundle


def _corrupt(record, name, value):
    clone = copy.deepcopy(record)
    object.__setattr__(clone, name, value)
    return clone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=None)
    args = parser.parse_args()
    if args.repository:
        repository = Path(args.repository).resolve()
        if str(repository) not in sys.path:
            sys.path.insert(0, str(repository))

    ledger = Ledger()
    m = importlib.import_module(PARENT_PACKAGE)
    g = importlib.import_module(PACKAGE)
    runtime, version, lifecycle, bundle = _fixture(m, g)

    ledger.check(g.SLICE41B_ACCEPTED_PARENT_HEAD == EXPECTED_PARENT_HEAD, "parent head")
    ledger.check(g.SLICE41B_ACCEPTED_PARENT_TREE == EXPECTED_PARENT_TREE, "parent tree")
    ledger.check(g.SLICE41B_ACCEPTED_PARENT_SUBJECT == EXPECTED_PARENT_SUBJECT, "parent subject")
    ledger.check(g.DIGEST_ALGORITHM == "sha256", "digest algorithm")
    ledger.check(len(g.SUPPORTED_RECORD_TYPES) == 15, "supported record types")
    ledger.check(len(g.SELECTED_MEANING_LIFECYCLE_TRANSITION_RULES) == 35, "transition rule count")

    for record_type in g.SUPPORTED_RECORD_TYPES:
        ledger.check(tuple(item.name for item in fields(record_type)) == g.canonical_field_order(record_type), f"canonical order {record_type.__name__}")

    runtime_report = g.validate_runtime_schema_record(runtime)
    version_report = g.validate_version_custody(version, runtime_record=runtime)
    lifecycle_report = g.validate_lifecycle_record(lifecycle)
    bundle_report = g.validate_governance_bundle(bundle)
    ledger.check(runtime_report.ok, f"valid runtime: {runtime_report.issues}")
    ledger.check(version_report.ok, f"valid version: {version_report.issues}")
    ledger.check(lifecycle_report.ok, f"valid lifecycle: {lifecycle_report.issues}")
    ledger.check(bundle_report.ok, f"valid bundle: {bundle_report.issues}")

    canonical_one = g.canonical_record_bytes(bundle)
    canonical_two = g.canonical_record_bytes(bundle)
    ledger.check(canonical_one == canonical_two, "canonical repeat")
    ledger.check(g.deterministic_record_digest(bundle) == g.deterministic_record_digest(bundle), "digest repeat")
    ledger.check(len(g.deterministic_record_digest(bundle)) == 64, "digest width")
    ledger.check(bundle.bundle_digest == g.expected_bundle_digest(bundle), "bundle digest")
    ledger.check(bundle.bundle_id == g.expected_bundle_id(bundle), "bundle id")

    pairs = tuple((item.name, getattr(runtime, item.name)) for item in fields(type(runtime)))
    ledger.check(g.validate_field_pairs(type(runtime), pairs).ok, "field pairs valid")
    duplicate_pairs = pairs + (pairs[0],)
    ledger.check(not g.validate_field_pairs(type(runtime), duplicate_pairs).ok, "duplicate field rejected")
    ledger.check(not g.validate_field_pairs(type(runtime), pairs[:-1]).ok, "missing field rejected")
    ledger.check(not g.validate_field_pairs(type(runtime), pairs + (("unknown", 1),)).ok, "unknown field rejected")
    ledger.check(not g.validate_field_pairs(type(runtime), tuple(reversed(pairs))).ok, "field order rejected")

    unknown_version = _corrupt(runtime, "schema_version", "unknown-version")
    ledger.check(not g.validate_runtime_schema_record(unknown_version).ok, "unknown runtime version rejected")
    unknown_governance = _corrupt(version, "governance_schema_version", "unknown-version")
    ledger.check(not g.validate_version_custody(unknown_governance, runtime_record=runtime).ok, "unknown governance version rejected")
    bad_predecessors = replace(version, predecessor_references=version.predecessor_references[:-1])
    bad_predecessors = g.with_expected_id(bad_predecessors)
    ledger.check(not g.validate_version_custody(bad_predecessors, runtime_record=runtime).ok, "missing predecessor rejected")

    requirement = runtime.selection_authority_requirements[0]
    duplicate_runtime = replace(runtime, selection_authority_requirements=(requirement, requirement))
    duplicate_runtime = g.with_expected_id(duplicate_runtime)
    duplicate_report = g.validate_runtime_schema_record(duplicate_runtime)
    ledger.check(any(item.code is g.SelectedMeaningValidationCode.DUPLICATE_RECORD_ID for item in duplicate_report.issues), "duplicate identity rejected")

    colliding_requirement = replace(requirement, requirement_key="different_requirement")
    object.__setattr__(colliding_requirement, "selection_authority_requirement_id", requirement.selection_authority_requirement_id)
    collision_runtime = replace(runtime, selection_authority_requirements=(requirement, colliding_requirement))
    collision_runtime = g.with_expected_id(collision_runtime)
    collision_report = g.validate_runtime_schema_record(collision_runtime)
    ledger.check(any(item.code is g.SelectedMeaningValidationCode.IDENTITY_COLLISION for item in collision_report.issues), "identity collision rejected")

    bad_gate = replace(runtime.gate_custody_reference, selection_candidate_custody_ref="selection_candidate_custody:wrong")
    bad_gate = g.with_expected_id(bad_gate)
    cross_runtime = replace(runtime, gate_custody_reference=bad_gate)
    cross_runtime = g.with_expected_id(cross_runtime)
    ledger.check(not g.validate_runtime_schema_record(cross_runtime).ok, "cross-record mismatch rejected")

    malformed_validators = (
        g.validate_selection_candidate_custody,
        g.validate_gate_custody_reference,
        g.validate_selection_authority_requirement,
        g.validate_alternative_candidate_custody,
        g.validate_unresolved_state_custody,
        g.validate_inherited_limitation_custody,
        g.validate_selection_eligibility_status,
        g.validate_selected_meaning_decision_status,
        g.validate_selection_trace_boundary,
        g.validate_selection_receipt_boundary,
        g.validate_runtime_schema_record,
        g.validate_version_custody,
        g.validate_lifecycle_record,
        g.validate_lifecycle_transition_record,
        g.validate_governance_bundle,
    )
    for validator in malformed_validators:
        report = validator(None)
        ledger.check(not report.ok, f"malformed None rejected {validator.__name__}")
        ledger.check(report.issues[0].code is g.SelectedMeaningValidationCode.TYPE_MISMATCH, f"malformed type code {validator.__name__}")

    try:
        runtime.schema_only = False
        immutable_runtime = False
    except FrozenInstanceError:
        immutable_runtime = True
    ledger.check(immutable_runtime, "runtime immutable")
    try:
        lifecycle.stage = g.SelectedMeaningLifecycleStage.RECORD_SEALED
        immutable_lifecycle = False
    except FrozenInstanceError:
        immutable_lifecycle = True
    ledger.check(immutable_lifecycle, "lifecycle immutable")

    target = replace(
        lifecycle,
        lifecycle_record_id="placeholder",
        stage=g.SelectedMeaningLifecycleStage.VERSION_BOUND,
        predecessor_lifecycle_record_ids=(lifecycle.lifecycle_record_id,),
        reason_refs=("slice41b_version_bound",),
    )
    target = g.with_expected_id(target)
    transition = g.with_expected_id(g.SelectedMeaningLifecycleTransitionRecord(
        transition_id="placeholder",
        runtime_schema_record_id=runtime.selected_meaning_runtime_schema_record_id,
        source_lifecycle_record_id=lifecycle.lifecycle_record_id,
        target_lifecycle_record_id=target.lifecycle_record_id,
        from_stage=lifecycle.stage,
        to_stage=target.stage,
        transition_kind=g.SelectedMeaningLifecycleTransitionKind.BIND_VERSION,
        version_custody_ref=version.custody_id,
        predecessor_transition_refs=(),
        reason_refs=("bind_exact_version",),
        automatic_transition=False,
        eligibility_evaluated=False,
        candidate_ranked=False,
        selection_performed=False,
        selected_meaning_created=False,
        msm_v1_modified=False,
        bootstrap_integration_enabled=False,
        truth_evidence_permission_execution_created=False,
        route_tool_action_memory_rendering_delivery_created=False,
    ))
    decision = g.evaluate_lifecycle_transition(lifecycle, target, transition, bundle=bundle)
    ledger.check(decision.allowed, f"allowed transition: {decision.issues}")
    ledger.check(lifecycle.stage is g.SelectedMeaningLifecycleStage.SCHEMA_DECLARED, "source unchanged")
    invalid_transition = replace(transition, transition_id="placeholder", transition_kind=g.SelectedMeaningLifecycleTransitionKind.SEAL_RECORD)
    invalid_transition = g.with_expected_id(invalid_transition)
    ledger.check(not g.evaluate_lifecycle_transition(lifecycle, target, invalid_transition).allowed, "invalid transition rejected")

    # Every valid record remains non-semantic validation custody.
    boundary_values = (
        bundle.validation_only,
        bundle.immutable_successor_records,
        bundle.exact_predecessor_references_required,
        bundle.duplicate_and_collision_rejection_required,
        bundle.unknown_version_rejection_required,
        not bundle.eligibility_evaluated,
        not bundle.gate_result_created,
        not bundle.candidate_ranked,
        not bundle.selection_performed,
        not bundle.selected_meaning_created,
        not bundle.msm_v1_modified,
        not bundle.bootstrap_integration_enabled,
        not bundle.truth_determined,
        not bundle.evidence_validated,
        not bundle.permission_granted,
        not bundle.execution_authorized,
        not bundle.route_created,
        not bundle.tool_invoked,
        not bundle.action_performed,
        not bundle.memory_written,
        not bundle.rendered,
        not bundle.delivered,
    )
    for index, condition in enumerate(boundary_values):
        ledger.check(condition, f"hard boundary {index}")

    # Repeat important checks to expose deterministic behavior over many runs.
    for index in range(64):
        ledger.check(g.validate_runtime_schema_record(runtime).ok, f"runtime repeat {index}")
        ledger.check(g.validate_governance_bundle(bundle).ok, f"bundle repeat {index}")
        ledger.check(g.canonical_record_bytes(runtime) == g.canonical_record_bytes(runtime), f"canonical repeat {index}")
        ledger.check(g.expected_runtime_schema_record_id(runtime) == runtime.selected_meaning_runtime_schema_record_id, f"identity repeat {index}")

    failures = tuple(ledger.failures)
    print("AI.WEB SLICE 41B DETERMINISTIC VALIDATION IDENTITY VERSIONING LIFECYCLE TEST")
    print(f"check_count={ledger.check_count}")
    print("record_types=15")
    print(f"lifecycle_stages={len(tuple(g.SelectedMeaningLifecycleStage))}")
    print(f"lifecycle_transition_rules={len(g.SELECTED_MEANING_LIFECYCLE_TRANSITION_RULES)}")
    print("canonical_serialization=1")
    print("deterministic_sha256_identities=1")
    print("exact_schema_version_custody=1")
    print("exact_predecessor_reference_validation=1")
    print("duplicate_rejection=1")
    print("identity_collision_rejection=1")
    print("unknown_version_rejection=1")
    print("immutable_successor_records=1")
    print("malformed_record_rejection=1")
    print("cross_record_consistency_checks=1")
    print("valid_record_is_valid_candidate_meaning=0")
    print("valid_record_is_successful_gate_result=0")
    print("valid_record_is_selection_eligibility=0")
    print("selection_lifecycle_is_selected_meaning=0")
    print("selection_eligibility_evaluated=0")
    print("candidate_ranked=0")
    print("selection_performed=0")
    print("selected_meaning_created=0")
    print("msm_v1_modified=0")
    print("bootstrap_integration_enabled=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(failures)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("AI.WEB SLICE 41B BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
