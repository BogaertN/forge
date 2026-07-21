#!/usr/bin/env python3
"""Focused behavior test for Slice 42B deterministic governance."""

from __future__ import annotations

from dataclasses import fields, replace
from enum import Enum
import copy
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


def _fixture(core, governance):
    source = core.SelectedMeaningExpressionSourceCustodyRecord(
        source_custody_id="pending:source",
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
    source = governance.with_expected_id(source)

    authority = core.OutwardExpressionAuthorityRequirementRecord(
        authority_requirement_id="pending:authority",
        selected_meaning_source_custody_ref=source.source_custody_id,
        required_outward_expression_authority_ref=(
            "outward-authority:required:fixture"
        ),
        required_authority_scope_refs=("scope:fixture",),
        required_expression_purpose_refs=("purpose:fixture",),
        required_predecessor_receipt_refs=(
            source.slice41e_integration_receipt_ref,
            source.selection_receipt_ref,
        ),
        required_version_refs=("slice42a:v1",),
        missing_authority_refs=("outward-authority:required:fixture",),
    )
    authority = governance.with_expected_id(authority)

    obligations = core.ExpressionPreservationObligationCustodyRecord(
        obligation_custody_id="pending:obligations",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=(
            authority.authority_requirement_id
        ),
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
    obligations = governance.with_expected_id(obligations)

    eligibility = core.ExpressionEligibilityStatusRecord(
        expression_eligibility_status_id="pending:eligibility",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=(
            authority.authority_requirement_id
        ),
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=core.ExpressionEligibilityCustodyState.NOT_EVALUATED,
        status_reason_refs=("slice42b:validation-only",),
        later_evaluator_ref="slice42c:evaluator:deferred",
    )
    eligibility = governance.with_expected_id(eligibility)

    outward = core.GovernedOutwardMeaningBoundaryRecord(
        governed_outward_meaning_boundary_id="pending:outward",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=(
            authority.authority_requirement_id
        ),
        expression_eligibility_status_ref=(
            eligibility.expression_eligibility_status_id
        ),
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=core.OutwardMeaningCustodyState.NOT_CONSTRUCTED,
        permitted_claim_refs=(),
        required_qualification_refs=obligations.required_caveat_refs,
        prohibited_enlargement_refs=("no-claim-strength-upgrade",),
        external_dependency_refs=(),
        ancestry_refs=(source.selected_governed_meaning_ref,),
        later_constructor_ref="slice42e:constructor:deferred",
    )
    outward = governance.with_expected_id(outward)

    plan = core.ExpressionPlanBoundaryRecord(
        expression_plan_boundary_id="pending:plan",
        governed_outward_meaning_boundary_ref=(
            outward.governed_outward_meaning_boundary_id
        ),
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=core.ExpressionPlanCustodyState.NOT_CONSTRUCTED,
        ordering_constraint_refs=("higher-order-obligations-first",),
        modifier_custody_refs=("modifier:fixture",),
        qualification_custody_refs=outward.required_qualification_refs,
        caveat_custody_refs=obligations.required_caveat_refs,
        refusal_custody_refs=obligations.refusal_relevant_boundary_refs,
        unresolved_custody_refs=obligations.unresolved_condition_refs,
        ancestry_refs=outward.ancestry_refs,
        later_planner_ref="slice42e:planner:deferred",
    )
    plan = governance.with_expected_id(plan)

    realized = core.RealizedExpressionBoundaryRecord(
        realized_expression_boundary_id="pending:realized",
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        governed_outward_meaning_boundary_ref=(
            outward.governed_outward_meaning_boundary_id
        ),
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        custody_state=core.RealizedExpressionCustodyState.NOT_REALIZED,
        expression_candidate_ref=None,
        realized_text_sha256=None,
        admitted_realization_rule_refs=(),
        controlled_resource_refs=(),
        realization_trace_ref=None,
        realization_receipt_ref=None,
        later_realizer_ref="slice42f:realizer:deferred",
    )
    realized = governance.with_expected_id(realized)

    trace = core.ExpressionTraceBoundaryRecord(
        expression_trace_boundary_id="pending:trace",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=(
            authority.authority_requirement_id
        ),
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        expression_eligibility_status_ref=(
            eligibility.expression_eligibility_status_id
        ),
        governed_outward_meaning_boundary_ref=(
            outward.governed_outward_meaning_boundary_id
        ),
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        realized_expression_boundary_ref=realized.realized_expression_boundary_id,
        predecessor_trace_refs=(source.selection_trace_ref,),
        predecessor_receipt_refs=(
            source.slice41e_integration_receipt_ref,
            source.selection_receipt_ref,
        ),
        authority_version_refs=(("slice41f", "v1"),),
        schema_version_refs=(("slice42a", core.SCHEMA_VERSION),),
    )
    trace = governance.with_expected_id(trace)

    receipt = core.ExpressionReceiptBoundaryRecord(
        expression_receipt_boundary_id="pending:receipt",
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=(
            authority.authority_requirement_id
        ),
        expression_eligibility_status_ref=(
            eligibility.expression_eligibility_status_id
        ),
        governed_outward_meaning_boundary_ref=(
            outward.governed_outward_meaning_boundary_id
        ),
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        realized_expression_boundary_ref=realized.realized_expression_boundary_id,
        expression_trace_boundary_ref=trace.expression_trace_boundary_id,
        required_law_refs=(
            "canonical-roadmap:slice42b",
            "document9:outbound-preservation",
        ),
        prohibited_consequence_refs=core.PROHIBITED_AUTHORITY_PATHS,
        audit_note="Validated structure only; no expression authority.",
    )
    receipt = governance.with_expected_id(receipt)

    aggregate = core.OutwardExpressionRuntimeSchemaRecord(
        outward_expression_runtime_schema_record_id="pending:aggregate",
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
    aggregate = governance.with_expected_id(aggregate)
    return aggregate


def _version_custody(governance, aggregate):
    record = governance.OutwardExpressionVersionCustody(
        custody_id="pending:version",
        runtime_schema_record_id=(
            aggregate.outward_expression_runtime_schema_record_id
        ),
        runtime_schema_version=aggregate.schema_version,
        runtime_schema_id=aggregate.schema_id,
        runtime_spec_id=aggregate.spec_id,
        runtime_spec_version=aggregate.spec_version,
        validation_profile_version=governance.VALIDATION_PROFILE_VERSION,
        record_schema_versions=governance.expected_record_schema_versions(
            aggregate
        ),
        predecessor_references=governance.expected_predecessor_references(
            aggregate
        ),
        accepted_parent_head=governance.SLICE42B_ACCEPTED_PARENT_HEAD,
        accepted_parent_tree=governance.SLICE42B_ACCEPTED_PARENT_TREE,
        accepted_parent_subject=governance.SLICE42B_ACCEPTED_PARENT_SUBJECT,
        canonical_field_order_version=(
            governance.CANONICAL_FIELD_ORDER_VERSION
        ),
        digest_algorithm=governance.DIGEST_ALGORITHM,
        non_llm_provenance=True,
        timestamps_in_identity=False,
        randomness_in_identity=False,
        process_identity_in_identity=False,
        filesystem_state_in_identity=False,
        environment_state_in_identity=False,
        hash_table_order_in_identity=False,
        selected_meaning_chain_admission_authorized=False,
        outward_expression_authority_admission_authorized=False,
        expression_eligibility_evaluation_authorized=False,
        preservation_obligation_projection_authorized=False,
        governed_outward_meaning_construction_authorized=False,
        expression_plan_construction_authorized=False,
        surface_realization_authorized=False,
        msm_v1_mutation_or_integration_authorized=False,
        echo_validation_authorized=False,
        bootstrap_integration_authorized=False,
        delivery_authorized=False,
        truth_evidence_permission_execution_authorized=False,
        route_api_network_filesystem_memory_tool_action_authorized=False,
        external_resource_authority=False,
        model_embedding_vector_rag_similarity_authority=False,
        gp014_supersession_authorized=False,
    )
    return governance.with_expected_id(record)


def _lifecycle(governance, aggregate, version, stage, predecessors=(), **truths):
    boolean_names = (
        "automatic_progression",
        "canonical_serialization_performed",
        "deterministic_identity_validated",
        "predecessor_references_validated",
        "cross_record_consistency_validated",
        "malformed_record_rejected",
        "unknown_version_rejected",
        "duplicate_record_rejected",
        "identity_collision_rejected",
        "structural_validity_grants_expression_authority",
        "selected_meaning_chain_admitted",
        "outward_expression_authority_admitted",
        "expression_eligibility_evaluated",
        "preservation_obligations_projected",
        "governed_outward_meaning_created",
        "expression_plan_created",
        "expression_candidate_created",
        "human_readable_text_produced",
        "msm_v1_modified_or_integrated",
        "echo_validation_performed",
        "bootstrap_integration_enabled",
        "delivered",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "route_or_api_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed_or_written",
        "filesystem_or_network_accessed",
        "external_resource_loaded",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    values = {name: False for name in boolean_names}
    values.update(truths)
    record = governance.OutwardExpressionLifecycleRecord(
        lifecycle_record_id="pending:lifecycle",
        runtime_schema_record_id=(
            aggregate.outward_expression_runtime_schema_record_id
        ),
        version_custody_ref=version.custody_id,
        validation_profile_version=governance.VALIDATION_PROFILE_VERSION,
        stage=stage,
        predecessor_lifecycle_record_ids=predecessors,
        predecessor_reference_ids=tuple(
            value for _, value in version.predecessor_references
        ),
        validation_issue_digest_refs=(),
        reason_refs=("slice42b:explicit-lifecycle",),
        **values,
    )
    return governance.with_expected_id(record)


def _transition(governance, aggregate, version, source, target):
    record = governance.OutwardExpressionLifecycleTransitionRecord(
        transition_id="pending:transition",
        runtime_schema_record_id=(
            aggregate.outward_expression_runtime_schema_record_id
        ),
        source_lifecycle_record_id=source.lifecycle_record_id,
        target_lifecycle_record_id=target.lifecycle_record_id,
        from_stage=source.stage,
        to_stage=target.stage,
        transition_kind=(
            governance.OutwardExpressionLifecycleTransitionKind.BIND_VERSION
        ),
        version_custody_ref=version.custody_id,
        validation_profile_version=governance.VALIDATION_PROFILE_VERSION,
        predecessor_transition_refs=(),
        reason_refs=("slice42b:bind-version",),
        automatic_transition=False,
        structural_validity_grants_expression_authority=False,
        selected_meaning_chain_admitted=False,
        outward_expression_authority_admitted=False,
        expression_eligibility_evaluated=False,
        preservation_obligations_projected=False,
        governed_outward_meaning_created=False,
        expression_plan_created=False,
        surface_realization_performed=False,
        msm_v1_modified_or_integrated=False,
        echo_validation_performed=False,
        bootstrap_integration_enabled=False,
        delivered=False,
        truth_evidence_permission_execution_created=False,
        route_api_network_filesystem_memory_tool_action_created=False,
        external_resource_or_model_authority_created=False,
        gp014_superseded=False,
    )
    return governance.with_expected_id(record)


def main() -> int:
    repository = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sys.path.insert(0, str(repository))

    from aiweb_language_core_bootstrap import outward_expression_runtime as core
    from aiweb_language_core_bootstrap.outward_expression_runtime import (
        governed_lifecycle as governance,
    )

    ledger = Ledger()

    ledger.check(
        governance.SLICE42B_ACCEPTED_PARENT_HEAD
        == "bf38d5dbefd27d6cc69f38f5053071316d1ded63",
        "exact accepted parent HEAD",
    )
    ledger.check(
        governance.SLICE42B_ACCEPTED_PARENT_TREE
        == "ce3232f0adef1de5b7488ff1ec10a919cd9b54af",
        "exact accepted parent tree",
    )
    ledger.check(
        governance.SLICE42B_ACCEPTED_PARENT_SUBJECT
        == "Slice 42A outward expression runtime core schema and authority contract",
        "exact accepted parent subject",
    )
    ledger.check(
        len(governance.SUPPORTED_RECORD_TYPES) == 14,
        "14 canonical record types",
    )
    ledger.check(
        len(governance.OutwardExpressionLifecycleStage) == 12,
        "12 lifecycle stages",
    )
    ledger.check(
        len(governance.OutwardExpressionLifecycleTransitionKind) == 13,
        "13 lifecycle transition kinds",
    )
    ledger.check(
        len(governance.OUTWARD_EXPRESSION_LIFECYCLE_TRANSITION_RULES) == 41,
        "41 explicit lifecycle transition rules",
    )

    aggregate = _fixture(core, governance)

    core_records = (
        aggregate.selected_meaning_source_custody,
        aggregate.outward_expression_authority_requirement,
        aggregate.preservation_obligation_custody,
        aggregate.expression_eligibility_status,
        aggregate.governed_outward_meaning_boundary,
        aggregate.expression_plan_boundary,
        aggregate.realized_expression_boundary,
        aggregate.expression_trace_boundary,
        aggregate.expression_receipt_boundary,
        aggregate,
    )
    validator_by_type = {
        core.SelectedMeaningExpressionSourceCustodyRecord:
            governance.validate_source_custody,
        core.OutwardExpressionAuthorityRequirementRecord:
            governance.validate_authority_requirement,
        core.ExpressionPreservationObligationCustodyRecord:
            governance.validate_preservation_obligation_custody,
        core.ExpressionEligibilityStatusRecord:
            governance.validate_expression_eligibility_status,
        core.GovernedOutwardMeaningBoundaryRecord:
            governance.validate_governed_outward_meaning_boundary,
        core.ExpressionPlanBoundaryRecord:
            governance.validate_expression_plan_boundary,
        core.RealizedExpressionBoundaryRecord:
            governance.validate_realized_expression_boundary,
        core.ExpressionTraceBoundaryRecord:
            governance.validate_expression_trace_boundary,
        core.ExpressionReceiptBoundaryRecord:
            governance.validate_expression_receipt_boundary,
        core.OutwardExpressionRuntimeSchemaRecord:
            governance.validate_runtime_schema_record,
    }
    malformed_validation_cases = 0

    for record in core_records:
        validator = validator_by_type[type(record)]
        ledger.check(validator(record).ok, f"valid {type(record).__name__}")
        ledger.check(
            governance.expected_record_id(record)
            == getattr(record, governance.identity_field(type(record))),
            f"expected identity exact {type(record).__name__}",
        )
        ledger.check(
            not hasattr(record, "__dict__"),
            f"slotted immutable record {type(record).__name__}",
        )
        for item in fields(type(record)):
            if item.init:
                value = getattr(record, item.name)
                replacement = None
                supported_mutation = True
                if type(value) is str:
                    replacement = ""
                elif type(value) is tuple:
                    replacement = []
                elif isinstance(value, Enum):
                    replacement = value.value
                elif value is None:
                    replacement = " invalid "
                else:
                    supported_mutation = False
                if supported_mutation:
                    malformed_validation_cases += 1
                    mutated = replace(record, **{item.name: replacement})
                    ledger.check(
                        not validator(mutated).ok,
                        f"malformed field rejected {type(record).__name__}.{item.name}",
                    )
            elif type(item.default) is bool:
                malformed_validation_cases += 1
                mutated = copy.copy(record)
                object.__setattr__(mutated, item.name, not item.default)
                ledger.check(
                    not validator(mutated).ok,
                    f"fixed authority flag rejected {type(record).__name__}.{item.name}",
                )

        for fixed_name in ("schema_version", "schema_id"):
            if hasattr(record, fixed_name):
                malformed_validation_cases += 1
                mutated = copy.copy(record)
                object.__setattr__(mutated, fixed_name, "unknown:version")
                ledger.check(
                    not validator(mutated).ok,
                    f"fixed schema field rejected {type(record).__name__}.{fixed_name}",
                )

    runtime_report = governance.validate_runtime_schema_record(aggregate)
    ledger.check(runtime_report.ok, "valid runtime record accepted")
    ledger.check(len(runtime_report.issues) == 0, "valid runtime has zero issues")
    ledger.check(
        governance.assert_valid_runtime_schema_record(aggregate) is aggregate,
        "runtime assertion returns immutable record",
    )

    canonical_once = governance.canonical_record_bytes(aggregate)
    canonical_twice = governance.canonical_record_bytes(aggregate)
    ledger.check(canonical_once == canonical_twice, "canonical bytes deterministic")
    ledger.check(
        governance.deterministic_record_digest(aggregate)
        == governance.deterministic_record_digest(aggregate),
        "canonical digest deterministic",
    )
    ledger.check(b": " not in canonical_once and b", " not in canonical_once, "canonical separators compact")
    ledger.check(b"\n" not in canonical_once, "canonical bytes newline free")

    for record_type in governance.SUPPORTED_RECORD_TYPES:
        ledger.check(
            governance.canonical_field_order(record_type)
            == tuple(item.name for item in fields(record_type)),
            f"canonical order exact {record_type.__name__}",
        )

    field_pairs = tuple(
        (item.name, getattr(aggregate, item.name))
        for item in fields(type(aggregate))
    )
    ledger.check(
        governance.validate_field_pairs(type(aggregate), field_pairs).ok,
        "canonical field pairs accepted",
    )
    ledger.check(
        not governance.validate_field_pairs(
            type(aggregate),
            field_pairs[:-1],
        ).ok,
        "missing field rejected",
    )
    ledger.check(
        not governance.validate_field_pairs(
            type(aggregate),
            field_pairs + (field_pairs[0],),
        ).ok,
        "duplicate field rejected",
    )
    ledger.check(
        not governance.validate_field_pairs(
            type(aggregate),
            tuple(reversed(field_pairs)),
        ).ok,
        "noncanonical field order rejected",
    )
    ledger.check(
        not governance.validate_field_pairs(
            type(aggregate),
            field_pairs[:-1] + (("unknown_field", None),),
        ).ok,
        "unknown field rejected",
    )

    source = aggregate.selected_meaning_source_custody
    malformed_source = replace(source, selected_candidate_ref="")
    ledger.check(
        not governance.validate_source_custody(malformed_source).ok,
        "malformed source rejected",
    )
    duplicate_tuple_source = replace(
        source,
        preserved_alternative_refs=("candidate:x", "candidate:x"),
    )
    ledger.check(
        not governance.validate_source_custody(duplicate_tuple_source).ok,
        "duplicate tuple value rejected",
    )
    wrong_identity_source = replace(source, source_custody_id="wrong:identity")
    ledger.check(
        not governance.validate_source_custody(wrong_identity_source).ok,
        "identity mismatch rejected",
    )

    broken_authority = replace(
        aggregate.outward_expression_authority_requirement,
        missing_authority_refs=(),
    )
    broken_aggregate = replace(
        aggregate,
        outward_expression_authority_requirement=broken_authority,
    )
    broken_aggregate = governance.with_expected_id(broken_aggregate)
    ledger.check(
        not governance.validate_runtime_schema_record(broken_aggregate).ok,
        "missing outward authority remains rejected",
    )

    broken_plan = replace(
        aggregate.expression_plan_boundary,
        caveat_custody_refs=(),
    )
    broken_aggregate = replace(aggregate, expression_plan_boundary=broken_plan)
    broken_aggregate = governance.with_expected_id(broken_aggregate)
    ledger.check(
        not governance.validate_runtime_schema_record(broken_aggregate).ok,
        "caveat custody omission rejected",
    )

    authority_mutated = replace(
        aggregate.outward_expression_authority_requirement,
        required_expression_purpose_refs=("purpose:changed",),
        authority_requirement_id=(
            aggregate.outward_expression_authority_requirement.authority_requirement_id
        ),
    )
    collision_report = governance.validate_identity_collection((
        aggregate.outward_expression_authority_requirement,
        authority_mutated,
    ))
    ledger.check(
        any(
            issue.code is governance.OutwardExpressionValidationCode.IDENTITY_COLLISION
            for issue in collision_report.issues
        ),
        "identity collision rejected",
    )
    duplicate_report = governance.validate_identity_collection((source, source))
    ledger.check(
        any(
            issue.code is governance.OutwardExpressionValidationCode.DUPLICATE_RECORD_ID
            for issue in duplicate_report.issues
        ),
        "duplicate record identity rejected",
    )

    version = _version_custody(governance, aggregate)
    version_report = governance.validate_version_custody(
        version,
        runtime_record=aggregate,
    )
    ledger.check(version_report.ok, "exact version custody accepted")
    ledger.check(
        governance.assert_valid_version_custody(
            version,
            runtime_record=aggregate,
        ) is version,
        "version assertion returns immutable record",
    )
    unknown_version = replace(
        version,
        runtime_schema_version="unknown-version-v999",
    )
    unknown_version = governance.with_expected_id(unknown_version)
    unknown_report = governance.validate_version_custody(
        unknown_version,
        runtime_record=aggregate,
    )
    ledger.check(
        any(
            issue.code is governance.OutwardExpressionValidationCode.UNKNOWN_VERSION
            for issue in unknown_report.issues
        ),
        "unknown version rejected",
    )
    wrong_predecessors = replace(version, predecessor_references=())
    wrong_predecessors = governance.with_expected_id(wrong_predecessors)
    ledger.check(
        not governance.validate_version_custody(
            wrong_predecessors,
            runtime_record=aggregate,
        ).ok,
        "missing exact predecessor references rejected",
    )

    declared = _lifecycle(
        governance,
        aggregate,
        version,
        governance.OutwardExpressionLifecycleStage.SCHEMA_DECLARED,
    )
    version_bound = _lifecycle(
        governance,
        aggregate,
        version,
        governance.OutwardExpressionLifecycleStage.VERSION_BOUND,
        predecessors=(declared.lifecycle_record_id,),
    )
    transition = _transition(
        governance,
        aggregate,
        version,
        declared,
        version_bound,
    )
    decision = governance.evaluate_lifecycle_transition(
        declared,
        version_bound,
        transition,
    )
    ledger.check(decision.allowed, "explicit bind-version transition accepted")
    ledger.check(len(decision.issues) == 0, "allowed transition has zero issues")
    ledger.check(
        governance.assert_lifecycle_transition(
            declared,
            version_bound,
            transition,
        ) is transition,
        "transition assertion returns immutable transition",
    )

    illegal_transition = replace(
        transition,
        transition_kind=(
            governance.OutwardExpressionLifecycleTransitionKind.SEAL_RECORD
        ),
    )
    illegal_transition = governance.with_expected_id(illegal_transition)
    ledger.check(
        not governance.evaluate_lifecycle_transition(
            declared,
            version_bound,
            illegal_transition,
        ).allowed,
        "illegal lifecycle transition rejected",
    )
    automatic_transition = replace(transition, automatic_transition=True)
    automatic_transition = governance.with_expected_id(automatic_transition)
    ledger.check(
        not governance.evaluate_lifecycle_transition(
            declared,
            version_bound,
            automatic_transition,
        ).allowed,
        "automatic lifecycle transition rejected",
    )

    sealed = _lifecycle(
        governance,
        aggregate,
        version,
        governance.OutwardExpressionLifecycleStage.RECORD_SEALED,
        predecessors=(version_bound.lifecycle_record_id,),
        canonical_serialization_performed=True,
        deterministic_identity_validated=True,
        predecessor_references_validated=True,
        cross_record_consistency_validated=True,
    )
    ledger.check(
        governance.validate_lifecycle_record(sealed).ok,
        "sealed validation custody accepted",
    )
    authority_tampered = replace(
        sealed,
        structural_validity_grants_expression_authority=True,
    )
    authority_tampered = governance.with_expected_id(authority_tampered)
    ledger.check(
        not governance.validate_lifecycle_record(authority_tampered).ok,
        "structural validity cannot grant expression authority",
    )

    bundle = governance.OutwardExpressionGovernanceBundle(
        bundle_id="outward_expression_governance_bundle:" + "0" * 64,
        bundle_digest="0" * 64,
        runtime_schema_record=aggregate,
        version_custody=version,
        lifecycle_record=version_bound,
        lifecycle_transitions=(transition,),
        validation_only=True,
        immutable_successor_records=True,
        exact_predecessor_references_required=True,
        duplicate_and_collision_rejection_required=True,
        unknown_version_rejection_required=True,
        malformed_record_rejection_required=True,
        cross_record_consistency_required=True,
        structural_validity_grants_expression_authority=False,
        selected_meaning_chain_admitted=False,
        outward_expression_authority_admitted=False,
        expression_eligibility_evaluated=False,
        preservation_obligations_projected=False,
        governed_outward_meaning_created=False,
        expression_plan_created=False,
        expression_candidate_created=False,
        human_readable_text_produced=False,
        msm_v1_modified_or_integrated=False,
        echo_validation_performed=False,
        bootstrap_integration_enabled=False,
        delivered=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_or_api_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed_or_written=False,
        filesystem_or_network_accessed=False,
        external_resource_loaded=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    bundle = governance.with_expected_bundle_identity(bundle)
    bundle_report = governance.validate_governance_bundle(bundle)
    ledger.check(bundle_report.ok, "valid governance bundle accepted")

    governance_records_and_validators = (
        (version, lambda value: governance.validate_version_custody(
            value, runtime_record=aggregate
        )),
        (declared, governance.validate_lifecycle_record),
        (version_bound, governance.validate_lifecycle_record),
        (sealed, governance.validate_lifecycle_record),
        (transition, governance.validate_lifecycle_transition_record),
        (bundle, governance.validate_governance_bundle),
    )
    for record, validator in governance_records_and_validators:
        ledger.check(validator(record).ok, f"valid governance {type(record).__name__}")
        for item in fields(type(record)):
            value = getattr(record, item.name)
            replacement = None
            supported_mutation = True
            if type(value) is str:
                replacement = ""
            elif type(value) is tuple:
                replacement = []
            elif isinstance(value, Enum):
                replacement = value.value
            elif type(value) is bool:
                replacement = not value
            else:
                supported_mutation = False
            if not supported_mutation:
                continue
            malformed_validation_cases += 1
            mutated = replace(record, **{item.name: replacement})
            ledger.check(
                not validator(mutated).ok,
                f"governance field rejected {type(record).__name__}.{item.name}",
            )
    ledger.check(
        governance.assert_valid_governance_bundle(bundle) is bundle,
        "bundle assertion returns immutable bundle",
    )
    invalid_bundle = replace(bundle, outward_expression_authority_admitted=True)
    invalid_bundle = governance.with_expected_bundle_identity(invalid_bundle)
    ledger.check(
        not governance.validate_governance_bundle(invalid_bundle).ok,
        "bundle expression authority prohibited",
    )

    repeat_ids = tuple(
        governance.expected_record_id(item)
        for item in (
            aggregate.selected_meaning_source_custody,
            aggregate.outward_expression_authority_requirement,
            aggregate.preservation_obligation_custody,
            aggregate.expression_eligibility_status,
            aggregate.governed_outward_meaning_boundary,
            aggregate.expression_plan_boundary,
            aggregate.realized_expression_boundary,
            aggregate.expression_trace_boundary,
            aggregate.expression_receipt_boundary,
            aggregate,
            version,
            declared,
            version_bound,
            transition,
        )
    )
    ledger.check(
        repeat_ids == tuple(
            governance.expected_record_id(item)
            for item in (
                aggregate.selected_meaning_source_custody,
                aggregate.outward_expression_authority_requirement,
                aggregate.preservation_obligation_custody,
                aggregate.expression_eligibility_status,
                aggregate.governed_outward_meaning_boundary,
                aggregate.expression_plan_boundary,
                aggregate.realized_expression_boundary,
                aggregate.expression_trace_boundary,
                aggregate.expression_receipt_boundary,
                aggregate,
                version,
                declared,
                version_bound,
                transition,
            )
        ),
        "all deterministic identities repeat exactly",
    )

    print("AI.WEB SLICE 42B DETERMINISTIC VALIDATION IDENTITY VERSIONING LIFECYCLE TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={malformed_validation_cases}")
    print("record_types=14")
    print(f"lifecycle_stages={len(governance.OutwardExpressionLifecycleStage)}")
    print(
        "lifecycle_transition_kinds="
        + str(len(governance.OutwardExpressionLifecycleTransitionKind))
    )
    print(
        "lifecycle_transition_rules="
        + str(len(governance.OUTWARD_EXPRESSION_LIFECYCLE_TRANSITION_RULES))
    )
    print("canonical_serialization=1")
    print("deterministic_sha256_identities=1")
    print("exact_predecessor_references=1")
    print("schema_and_profile_version_custody=1")
    print("immutable_successor_records=1")
    print("duplicate_rejection=1")
    print("identity_collision_rejection=1")
    print("unknown_version_rejection=1")
    print("malformed_record_rejection=1")
    print("cross_record_consistency_validation=1")
    print("structurally_valid_record_is_expression_authorized=0")
    print("selected_meaning_chain_admitted=0")
    print("outward_expression_authority_admitted=0")
    print("expression_eligibility_evaluated=0")
    print("preservation_obligations_projected=0")
    print("governed_outward_meaning_created=0")
    print("expression_plan_or_text_created=0")
    print("msm_v1_modified_or_integrated=0")
    print("echo_validation_delivery_action=0")
    print("model_embedding_vector_rag_similarity_authority=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures:
        print("AI.WEB SLICE 42B BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 42B BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
