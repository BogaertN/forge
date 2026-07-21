#!/usr/bin/env python3
"""Focused behavior test for Slice 42A outward-expression core schema."""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)


def field_names(record_type: type[object]) -> tuple[str, ...]:
    return tuple(field.name for field in dataclasses.fields(record_type))


def expect_frozen(ledger: Ledger, value: object, label: str) -> None:
    try:
        setattr(value, dataclasses.fields(value)[0].name, "mutated")
    except (dataclasses.FrozenInstanceError, AttributeError, TypeError):
        ledger.check(True, label)
    else:
        ledger.check(False, label)


def expect_constructor_rejection(
    ledger: Ledger,
    record_type: type[object],
    label: str,
) -> None:
    try:
        record_type()  # type: ignore[call-arg]
    except TypeError:
        ledger.check(True, label)
    else:
        ledger.check(False, label)


def main() -> int:
    repository = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sys.path.insert(0, str(repository))

    from aiweb_language_core_bootstrap import outward_expression_runtime as package
    from aiweb_language_core_bootstrap.disabled_selected_meaning_closeout import (
        Slice41AcceptanceRecord,
    )
    from aiweb_language_core_bootstrap.meaning_structure_manifest import (
        ExpressionLinkRecord,
        GovernedOutwardMeaningRecord,
        MeaningStructureManifestV1,
        SelectedGovernedMeaningRecord,
    )
    from aiweb_language_core_bootstrap.selected_meaning_runtime.msm_selected_meaning_integration import (
        MsmSelectedMeaningCustodyCompanionV1,
        MsmSelectedMeaningIntegrationResult,
    )
    from aiweb_language_core_bootstrap.selected_meaning_runtime.selected_meaning_construction import (
        SelectedMeaningConstructionPackage,
    )

    ledger = Ledger()

    ledger.check(
        package.ACCEPTED_PARENT_HEAD
        == "661ff1e17d8d4a982641ca39dc150b23bbb766e9",
        "exact accepted parent HEAD",
    )
    ledger.check(
        package.ACCEPTED_PARENT_TREE
        == "e56c9af88be9b845de534c62c9b82fa6af960f3f",
        "exact accepted parent tree",
    )
    ledger.check(
        package.ACCEPTED_PARENT_SUBJECT
        == "Slice 41F disabled bootstrap integration and Slice 41 closeout",
        "exact accepted parent subject",
    )
    ledger.check(
        package.EXPECTED_COMMIT_SUBJECT
        == "Slice 42A outward expression runtime core schema and authority contract",
        "exact intended commit subject",
    )
    ledger.check(
        package.MSM_OUTWARD_INTEGRATION_DECISION
        == "deferred_to_slice42g_exact_additive_adapter",
        "MSM integration deferred to Slice 42G",
    )
    ledger.check(
        package.EXPRESSION_ELIGIBILITY_NAMING_DECISION
        == "deferred_to_slice42c_exact_source_and_authority_decision",
        "Slice 42C naming decision deferred",
    )
    ledger.check(
        package.OUTWARD_MEANING_LIFECYCLE_NAMING_DECISION
        == "deferred_to_slice42b_deterministic_lifecycle_decision",
        "Slice 42B lifecycle naming deferred",
    )

    false_authority_constants = (
        "MSM_V1_SCHEMA_MODIFICATION_ALLOWED",
        "MSM_V1_AUTOMATIC_MIGRATION_ALLOWED",
        "EXPRESSION_AUTHORITY_ADMISSION_ALLOWED",
        "EXPRESSION_ELIGIBILITY_EVALUATION_ALLOWED",
        "PRESERVATION_OBLIGATION_PROJECTION_ALLOWED",
        "GOVERNED_OUTWARD_MEANING_CONSTRUCTION_ALLOWED",
        "EXPRESSION_PLAN_CONSTRUCTION_ALLOWED",
        "SURFACE_REALIZATION_ALLOWED",
        "ECHO_VALIDATION_ALLOWED",
        "BOOTSTRAP_INTEGRATION_ALLOWED",
        "DELIVERY_AUTHORITY_ALLOWED",
    )
    for name in false_authority_constants:
        ledger.check(getattr(package, name) is False, f"{name} remains false")

    ledger.check(
        tuple(state.value for state in package.ExpressionEligibilityCustodyState)
        == package.EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES,
        "eligibility custody vocabulary exact",
    )
    ledger.check(
        tuple(state.value for state in package.OutwardMeaningCustodyState)
        == package.OUTWARD_MEANING_CUSTODY_STATE_VALUES,
        "outward meaning custody vocabulary exact",
    )
    ledger.check(
        tuple(state.value for state in package.ExpressionPlanCustodyState)
        == package.EXPRESSION_PLAN_CUSTODY_STATE_VALUES,
        "expression plan custody vocabulary exact",
    )
    ledger.check(
        tuple(state.value for state in package.RealizedExpressionCustodyState)
        == package.REALIZED_EXPRESSION_CUSTODY_STATE_VALUES,
        "realization custody vocabulary exact",
    )
    ledger.check(
        package.REQUIRED_PRESERVATION_OBLIGATION_CATEGORIES
        == (
            "active_scope",
            "certainty_level",
            "evidence_status",
            "inherited_limitations",
            "required_caveats",
            "refusal_relevant_boundaries",
            "unresolved_conditions",
            "memory_authority",
            "external_resource_status",
            "delivery_authority",
        ),
        "roadmap preservation categories exact",
    )

    record_types = (
        package.SelectedMeaningExpressionSourceCustodyRecord,
        package.OutwardExpressionAuthorityRequirementRecord,
        package.ExpressionPreservationObligationCustodyRecord,
        package.ExpressionEligibilityStatusRecord,
        package.GovernedOutwardMeaningBoundaryRecord,
        package.ExpressionPlanBoundaryRecord,
        package.RealizedExpressionBoundaryRecord,
        package.ExpressionTraceBoundaryRecord,
        package.ExpressionReceiptBoundaryRecord,
        package.OutwardExpressionRuntimeSchemaRecord,
    )
    for record_type in record_types:
        ledger.check(dataclasses.is_dataclass(record_type), f"{record_type.__name__} dataclass")
        parameters = record_type.__dataclass_params__
        ledger.check(parameters.frozen is True, f"{record_type.__name__} frozen")
        ledger.check(hasattr(record_type, "__slots__"), f"{record_type.__name__} slotted")
        expect_constructor_rejection(
            ledger, record_type, f"{record_type.__name__} requires explicit custody"
        )

    predecessor_expectations = {
        MsmSelectedMeaningIntegrationResult: (
            "integration_input_ref",
            "source_manifest",
            "successor_manifest",
            "integrated_selected_meaning_record",
            "companion",
            "receipt",
            "all_candidate_meanings_retained",
            "all_non_selection_outcomes_retained",
            "selected_meaning_integrated",
            "governed_outward_meaning_created",
            "expression_link_created",
        ),
        MsmSelectedMeaningCustodyCompanionV1: (
            "selected_candidate_ref",
            "integrated_selected_meaning_ref",
            "selection_receipt_ref",
            "preserved_alternative_refs",
            "unresolved_alternative_refs",
            "candidate_ancestry_refs",
            "gate_ancestry_refs",
        ),
        SelectedMeaningConstructionPackage: (
            "selected_meaning_record",
            "preserved_alternatives",
            "unresolved_alternative_refs",
            "inherited_limitation_refs",
            "blocked_consequence_refs",
            "refusal_relevant_refs",
            "authority_sensitive_distinction_refs",
            "selection_trace",
            "selection_receipt",
        ),
        Slice41AcceptanceRecord: (
            "accepted_scope",
            "deferred_scope",
            "permanent_boundaries",
            "prohibited_authority",
            "slice41_closed",
            "slice42_started",
            "outward_expression_authority",
        ),
        SelectedGovernedMeaningRecord: (
            "selected_candidate_ref",
            "selection_authority_ref",
            "communicative_act",
            "concept_refs",
            "relation_refs",
            "meaning_modifiers",
            "inherited_limitations",
            "authority_sensitive_distinctions",
            "preservation_classes",
        ),
        GovernedOutwardMeaningRecord: (
            "outward_basis_refs",
            "prior_selected_meaning_ref",
            "permitted_claims",
            "required_qualifications",
            "prohibited_enlargements",
            "external_dependency_refs",
            "preservation_classes",
        ),
        ExpressionLinkRecord: (
            "governed_outward_meaning_ref",
            "expression_candidate_ref",
        ),
        MeaningStructureManifestV1: (
            "selected_governed_meanings",
            "governed_outward_meanings",
            "expression_links",
            "validation_links",
            "delivery_or_containment_links",
        ),
    }
    for record_type, expected in predecessor_expectations.items():
        actual = field_names(record_type)
        for name in expected:
            ledger.check(name in actual, f"predecessor field preserved {record_type.__name__}.{name}")

    source = package.SelectedMeaningExpressionSourceCustodyRecord(
        source_custody_id="slice42a:source:fixture",
        slice41e_integration_input_ref="slice41e:input:fixture",
        slice41e_integration_result_ref="slice41e:result:fixture",
        slice41e_integration_receipt_ref="slice41e:receipt:fixture",
        source_manifest_ref="msm:source:fixture",
        successor_manifest_ref="msm:successor:fixture",
        selected_governed_meaning_ref="msm:selected:fixture",
        selected_candidate_ref="candidate:fixture:selected",
        selection_authority_reference_ref="authority:selection:fixture",
        selection_eligibility_result_ref="slice41c:eligibility:fixture",
        selection_decision_ref="slice41d:decision:fixture",
        selection_trace_ref="slice41d:trace:fixture",
        selection_receipt_ref="slice41d:receipt:fixture",
        content_proof_ref="slice41d:proof:fixture",
        slice41f_acceptance_record_ref="slice41f:acceptance:fixture",
        preserved_alternative_refs=("candidate:fixture:alternative",),
        unresolved_alternative_refs=("candidate:fixture:unresolved",),
        ambiguity_ancestry_refs=("ambiguity:fixture",),
        clarification_ancestry_refs=("clarification:fixture",),
        inherited_limitation_refs=("limitation:fixture",),
        blocked_consequence_refs=("blocked:fixture",),
        refusal_relevant_refs=("refusal:fixture",),
        authority_sensitive_distinction_refs=("distinction:fixture",),
        preservation_class_refs=("uncertainty_and_claim_strength",),
    )
    authority = package.OutwardExpressionAuthorityRequirementRecord(
        authority_requirement_id="slice42a:authority-requirement:fixture",
        selected_meaning_source_custody_ref=source.source_custody_id,
        required_outward_expression_authority_ref="outward-authority:required:fixture",
        required_authority_scope_refs=("scope:fixture",),
        required_expression_purpose_refs=("purpose:fixture",),
        required_predecessor_receipt_refs=(source.selection_receipt_ref,),
        required_version_refs=("slice42a:v1",),
        missing_authority_refs=("outward-authority:required:fixture",),
    )
    obligations = package.ExpressionPreservationObligationCustodyRecord(
        obligation_custody_id="slice42a:obligations:fixture",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        active_scope_refs=("scope:fixture",),
        certainty_level_refs=("certainty:bounded",),
        evidence_status_refs=("evidence:not_validated",),
        inherited_limitation_refs=source.inherited_limitation_refs,
        required_caveat_refs=("caveat:fixture",),
        refusal_relevant_boundary_refs=source.refusal_relevant_refs,
        unresolved_condition_refs=source.unresolved_alternative_refs,
        memory_authority_refs=("memory:no_write_authority",),
        external_resource_status_refs=("resource:not_admitted",),
        delivery_authority_refs=("delivery:not_authorized",),
        ambiguity_refs=source.ambiguity_ancestry_refs,
        privacy_identity_boundary_refs=("privacy:fixture",),
        preservation_class_refs=source.preservation_class_refs,
    )
    eligibility = package.ExpressionEligibilityStatusRecord(
        expression_eligibility_status_id="slice42a:eligibility-status:fixture",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=package.ExpressionEligibilityCustodyState.NOT_EVALUATED,
        status_reason_refs=("slice42a:schema-only",),
        later_evaluator_ref="slice42c:evaluator:deferred",
    )
    outward = package.GovernedOutwardMeaningBoundaryRecord(
        governed_outward_meaning_boundary_id="slice42a:outward-boundary:fixture",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        expression_eligibility_status_ref=eligibility.expression_eligibility_status_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=package.OutwardMeaningCustodyState.NOT_CONSTRUCTED,
        permitted_claim_refs=(),
        required_qualification_refs=obligations.required_caveat_refs,
        prohibited_enlargement_refs=("no-claim-strength-upgrade",),
        external_dependency_refs=(),
        ancestry_refs=(source.selected_governed_meaning_ref,),
        later_constructor_ref="slice42d-or-42e:deferred",
    )
    plan = package.ExpressionPlanBoundaryRecord(
        expression_plan_boundary_id="slice42a:plan-boundary:fixture",
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=package.ExpressionPlanCustodyState.NOT_CONSTRUCTED,
        ordering_constraint_refs=("higher-order-obligations-first",),
        modifier_custody_refs=("modifier:fixture",),
        qualification_custody_refs=outward.required_qualification_refs,
        caveat_custody_refs=obligations.required_caveat_refs,
        refusal_custody_refs=obligations.refusal_relevant_boundary_refs,
        unresolved_custody_refs=obligations.unresolved_condition_refs,
        ancestry_refs=outward.ancestry_refs,
        later_planner_ref="slice42e:planner:deferred",
    )
    realized = package.RealizedExpressionBoundaryRecord(
        realized_expression_boundary_id="slice42a:realized-boundary:fixture",
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=package.RealizedExpressionCustodyState.NOT_REALIZED,
        expression_candidate_ref=None,
        realized_text_sha256=None,
        admitted_realization_rule_refs=(),
        controlled_resource_refs=(),
        realization_trace_ref=None,
        realization_receipt_ref=None,
        later_realizer_ref="slice42f:realizer:deferred",
    )
    trace = package.ExpressionTraceBoundaryRecord(
        expression_trace_boundary_id="slice42a:trace-boundary:fixture",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        expression_eligibility_status_ref=eligibility.expression_eligibility_status_id,
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        realized_expression_boundary_ref=realized.realized_expression_boundary_id,
        predecessor_trace_refs=(source.selection_trace_ref,),
        predecessor_receipt_refs=(source.selection_receipt_ref,),
        authority_version_refs=(("slice41f", "v1"),),
        schema_version_refs=(("slice42a", package.SCHEMA_VERSION),),
    )
    receipt = package.ExpressionReceiptBoundaryRecord(
        expression_receipt_boundary_id="slice42a:receipt-boundary:fixture",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        expression_eligibility_status_ref=eligibility.expression_eligibility_status_id,
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        realized_expression_boundary_ref=realized.realized_expression_boundary_id,
        expression_trace_boundary_ref=trace.expression_trace_boundary_id,
        required_law_refs=("canonical-roadmap:slice42a", "document9:outbound-preservation"),
        prohibited_consequence_refs=package.PROHIBITED_AUTHORITY_PATHS,
        audit_note="Schema custody only; no expression authority or text.",
    )
    aggregate = package.OutwardExpressionRuntimeSchemaRecord(
        outward_expression_runtime_schema_record_id="slice42a:schema-record:fixture",
        selected_meaning_source_custody=source,
        outward_expression_authority_requirement=authority,
        preservation_obligation_custody=obligations,
        expression_eligibility_status=eligibility,
        governed_outward_meaning_boundary=outward,
        expression_plan_boundary=plan,
        realized_expression_boundary=realized,
        expression_trace_boundary=trace,
        expression_receipt_boundary=receipt,
    )

    instances = (
        source,
        authority,
        obligations,
        eligibility,
        outward,
        plan,
        realized,
        trace,
        receipt,
        aggregate,
    )
    for value in instances:
        ledger.check(not hasattr(value, "__dict__"), f"{type(value).__name__} no mutable dict")
        ledger.check(value.schema_version == package.SCHEMA_VERSION, f"{type(value).__name__} version")
        expect_frozen(ledger, value, f"{type(value).__name__} immutable")

    ledger.check(source.exact_selected_meaning_chain_required is True, "exact chain required")
    ledger.check(source.selected_meaning_rewrite_allowed is False, "selected meaning rewrite blocked")
    ledger.check(source.alternative_deletion_allowed is False, "alternative deletion blocked")
    ledger.check(source.unresolved_resolution_allowed is False, "unresolved resolution blocked")
    ledger.check(authority.requirement_satisfied is False, "authority requirement unsatisfied")
    ledger.check(authority.expression_authorized is False, "expression not authorized")
    ledger.check(authority.selected_meaning_alone_sufficient is False, "selected meaning insufficient")
    ledger.check(authority.authority_inferred is False, "authority not inferred")

    obligation_false_fields = (
        "projection_performed",
        "obligation_package_created",
        "scope_upgraded",
        "certainty_upgraded",
        "evidence_status_upgraded",
        "caveat_omitted",
        "refusal_softened",
        "unresolved_condition_resolved",
    )
    for name in obligation_false_fields:
        ledger.check(getattr(obligations, name) is False, f"obligation field false {name}")

    ledger.check(eligibility.eligibility_evaluated is False, "eligibility not evaluated")
    ledger.check(
        eligibility.eligible_for_expression_planning is False,
        "planning eligibility not granted",
    )
    ledger.check(outward.governed_outward_meaning_created is False, "outward meaning not created")
    ledger.check(outward.selected_meaning_rewritten is False, "selected meaning not rewritten")
    ledger.check(plan.expression_plan_created is False, "plan not created")
    ledger.check(plan.final_text_created is False, "final text not created")
    ledger.check(realized.realization_performed is False, "realization not performed")
    ledger.check(realized.human_readable_text_produced is False, "human-readable text absent")
    ledger.check(realized.expression_candidate_created is False, "expression candidate absent")
    ledger.check(realized.echo_validation_performed is False, "Echo validation absent")
    ledger.check(realized.delivery_authorized is False, "delivery authority absent")
    ledger.check(trace.trace_boundary_only is True, "trace is boundary only")
    ledger.check(trace.expression_trace_created is False, "expression trace not created")
    ledger.check(receipt.receipt_boundary_only is True, "receipt is boundary only")
    ledger.check(receipt.expression_receipt_created is False, "expression receipt not created")
    ledger.check(receipt.expression_authorized is False, "receipt does not authorize")
    ledger.check(receipt.echo_validated is False, "receipt does not Echo validate")
    ledger.check(receipt.delivered is False, "receipt does not deliver")

    aggregate_false_fields = (
        "deterministic_identity_calculated",
        "validation_performed",
        "canonical_serialization_performed",
        "lifecycle_transition_performed",
        "selected_meaning_chain_admitted",
        "outward_expression_authority_admitted",
        "expression_eligibility_evaluated",
        "preservation_obligations_projected",
        "governed_outward_meaning_created",
        "expression_plan_created",
        "expression_candidate_created",
        "human_readable_text_produced",
        "msm_v1_schema_modified",
        "msm_v1_automatic_migration_performed",
        "msm_v1_outward_meaning_integrated",
        "msm_v1_expression_link_integrated",
        "bootstrap_integration_enabled",
        "echo_validation_performed",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "capability_availability_created",
        "route_created",
        "api_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed",
        "memory_written",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "rendered_for_delivery",
        "delivered",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
        "neural_parser_used",
        "hidden_classifier_used",
        "gp014_superseded",
    )
    for name in aggregate_false_fields:
        ledger.check(getattr(aggregate, name) is False, f"aggregate authority zero {name}")

    ledger.check(aggregate.schema_only is True, "aggregate schema only")
    ledger.check(aggregate.versioned_companion is True, "aggregate versioned companion")
    ledger.check(
        aggregate.permanent_boundaries == package.PERMANENT_OUTWARD_EXPRESSION_BOUNDARIES,
        "permanent boundaries exact",
    )
    ledger.check(
        aggregate.prohibited_authority_paths == package.PROHIBITED_AUTHORITY_PATHS,
        "prohibited authority exact",
    )
    for boundary in (
        "selected_meaning_may_not_be_rewritten",
        "candidate_alternatives_may_not_be_deleted",
        "unresolved_state_may_not_be_silently_resolved",
        "uncertainty_may_not_be_upgraded",
        "evidence_status_may_not_be_upgraded",
        "required_caveats_may_not_be_omitted",
        "refusal_may_not_be_softened_into_permission",
        "realized_expression_is_not_echo_validation",
        "echo_validation_belongs_to_slice43",
        "gp014_is_not_superseded",
    ):
        ledger.check(
            boundary in aggregate.permanent_boundaries,
            f"required permanent boundary {boundary}",
        )

    print("AI.WEB SLICE 42A OUTWARD EXPRESSION RUNTIME CORE SCHEMA TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_constructor_cases={len(record_types)}")
    print(f"record_types={len(record_types)}")
    print(
        "expression_eligibility_custody_states="
        + str(len(package.EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES))
    )
    print(
        "outward_meaning_custody_states="
        + str(len(package.OUTWARD_MEANING_CUSTODY_STATE_VALUES))
    )
    print(
        "expression_plan_custody_states="
        + str(len(package.EXPRESSION_PLAN_CUSTODY_STATE_VALUES))
    )
    print(
        "realized_expression_custody_states="
        + str(len(package.REALIZED_EXPRESSION_CUSTODY_STATE_VALUES))
    )
    print(f"permanent_boundaries={len(package.PERMANENT_OUTWARD_EXPRESSION_BOUNDARIES)}")
    print(f"prohibited_authority_paths={len(package.PROHIBITED_AUTHORITY_PATHS)}")
    print(
        "preservation_obligation_categories="
        + str(len(package.REQUIRED_PRESERVATION_OBLIGATION_CATEGORIES))
    )
    print("schema_only=1")
    print("exact_slice41e_and_41f_custody_shapes=1")
    print("selected_meaning_outward_meaning_plan_realization_boundaries=1")
    print("scope_certainty_evidence_caveat_refusal_unresolved_custody=1")
    print("memory_resource_delivery_authority_custody=1")
    print("expression_authority_admitted=0")
    print("expression_eligibility_evaluated=0")
    print("preservation_obligations_projected=0")
    print("governed_outward_meaning_created=0")
    print("expression_plan_created=0")
    print("human_readable_text_produced=0")
    print("msm_v1_modified_or_integrated=0")
    print("echo_validation_performed=0")
    print("truth_evidence_permission_execution_authority=0")
    print("route_api_network_filesystem_memory_tool_action_delivery=0")
    print("language_model_embedding_vector_rag_similarity_neural_classifier=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures:
        print("AI.WEB SLICE 42A BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 42A BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
