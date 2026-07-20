#!/usr/bin/env python3
"""Visible behavior test for AI.Web Slice 41A schema-only contracts."""

from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import sys
from dataclasses import FrozenInstanceError, fields, is_dataclass
from enum import Enum
from pathlib import Path


PACKAGE = "aiweb_language_core_bootstrap.selected_meaning_runtime"
EXPECTED_EXPORTS = ('ACCEPTED_PARENT_HEAD', 'ACCEPTED_PARENT_SUBJECT', 'ACCEPTED_PARENT_TREE', 'ALTERNATIVE_CANDIDATE_CUSTODY_SCHEMA_ID', 'AlternativeCandidateCustodyRecord', 'BOOTSTRAP_INTEGRATION_ALLOWED', 'DECISION_CUSTODY_STATE_VALUES', 'DEFERRED_SLICE41_RUNTIME_AUTHORITY', 'ELIGIBILITY_CUSTODY_STATE_VALUES', 'GATE_CUSTODY_REFERENCE_SCHEMA_ID', 'GateCustodyReferenceRecord', 'INHERITED_LIMITATION_CUSTODY_SCHEMA_ID', 'InheritedLimitationCustodyRecord', 'MSM_SELECTED_MEANING_INTEGRATION_DECISION', 'MSM_V1_AUTOMATIC_MIGRATION_ALLOWED', 'MSM_V1_SCHEMA_MODIFICATION_ALLOWED', 'PACKAGE_ID', 'PACKAGE_NAME', 'PERMANENT_SELECTED_MEANING_BOUNDARIES', 'POSITIVE_ELIGIBILITY_NAMING_DECISION', 'PROHIBITED_AUTHORITY_PATHS', 'SCHEMA_ABBREVIATION', 'SCHEMA_NAME', 'SCHEMA_VERSION', 'SELECTED_GOVERNED_MEANING_CONSTRUCTION_ALLOWED', 'SELECTED_MEANING_DECISION_STATUS_SCHEMA_ID', 'SELECTED_MEANING_RUNTIME_SCHEMA_RECORD_SCHEMA_ID', 'SELECTION_AUTHORITY_REQUIREMENT_SCHEMA_ID', 'SELECTION_CANDIDATE_CUSTODY_SCHEMA_ID', 'SELECTION_DECISION_NAMING_DECISION', 'SELECTION_ELIGIBILITY_EVALUATION_ALLOWED', 'SELECTION_ELIGIBILITY_STATUS_SCHEMA_ID', 'SELECTION_PERFORMANCE_ALLOWED', 'SELECTION_RECEIPT_BOUNDARY_SCHEMA_ID', 'SELECTION_TRACE_BOUNDARY_SCHEMA_ID', 'SPEC_ID', 'SPEC_VERSION', 'SelectedMeaningDecisionCustodyState', 'SelectedMeaningDecisionStatusRecord', 'SelectedMeaningRuntimeSchemaRecord', 'SelectionAuthorityRequirementRecord', 'SelectionCandidateCustodyRecord', 'SelectionEligibilityCustodyState', 'SelectionEligibilityStatusRecord', 'SelectionReceiptBoundaryRecord', 'SelectionTraceBoundaryRecord', 'UNRESOLVED_STATE_CUSTODY_SCHEMA_ID', 'UnresolvedStateCustodyRecord')
EXPECTED_ELIGIBILITY_STATES = (
    "not_evaluated",
    "ready_for_later_evaluation",
    "evaluation_deferred",
    "evaluation_unavailable",
)
EXPECTED_DECISION_STATES = (
    "not_decided",
    "ready_for_later_decision",
    "decision_deferred",
    "decision_unavailable",
)
EXPECTED_PARENT_HEAD = "fcc6b57e62e95cbfe2dbc80b88a212432c681907"
EXPECTED_PARENT_TREE = "55dc8ebf863c2df547ae31b38e3445b25f6cc22a"
EXPECTED_PARENT_SUBJECT = (
    "Slice 40H MSM gate integration disabled bootstrap and Slice 40 closeout"
)
FORBIDDEN_OUTCOME_VALUES = {
    "eligible",
    "ineligible",
    "accepted",
    "rejected",
    "selected",
    "clarification_required",
    "ambiguous",
    "unsupported",
    "refusal",
    "held",
    "blocked",
}
FIXED_TRUE_FIELDS = (
    "candidate_only",
    "selection_candidate_reference_only",
    "exact_candidate_match_required",
    "all_four_gate_families_required",
    "composition_required",
    "gate_results_preserved_exactly",
    "alternatives_preserved",
    "unresolved_state_preserved",
    "limitations_preserved",
    "trace_boundary_only",
    "receipt_boundary_only",
    "schema_only",
    "versioned_companion",
)
FIXED_FALSE_FIELDS = (
    "candidate_eligibility_evaluated",
    "candidate_ranked",
    "candidate_selected",
    "gate_results_re_evaluated",
    "composition_recomputed",
    "selection_performed",
    "requirement_satisfied",
    "requirement_failed",
    "authority_granted",
    "alternatives_ranked",
    "confidence_scores_created",
    "preferred_candidate_created",
    "alternatives_discarded",
    "ambiguity_resolved",
    "unresolved_state_resolved",
    "clarification_emitted",
    "refusal_issued",
    "progression_authorized",
    "limitations_released",
    "scope_enlarged",
    "authority_enlarged",
    "eligibility_evaluated",
    "eligible_for_selected_meaning_construction",
    "not_eligible_determined",
    "decision_performed",
    "selected_meaning_created",
    "msm_v1_modified",
    "trace_validated",
    "selection_trace_created",
    "receipt_validated",
    "selection_receipt_created",
    "deterministic_identity_calculated",
    "validation_performed",
    "canonical_serialization_performed",
    "lifecycle_transition_performed",
    "selection_eligibility_evaluated",
    "selection_decision_performed",
    "msm_v1_schema_modified",
    "msm_v1_automatic_migration_performed",
    "bootstrap_integration_enabled",
    "governed_outward_meaning_created",
    "truth_determined",
    "evidence_validated",
    "proof_claim_created",
    "permission_granted",
    "execution_authorized",
    "capability_availability_created",
    "route_created",
    "tool_invoked",
    "action_performed",
    "memory_accessed",
    "memory_written",
    "rendered",
    "delivered",
    "external_resource_loaded",
    "language_model_used",
    "embedding_used",
    "vector_used",
    "rag_used",
    "semantic_similarity_used",
)
FORBIDDEN_SCHEMA_TOKENS = (
    "hashlib",
    "subprocess",
    "socket",
    "urllib",
    "requests",
    "open(",
    "pathlib",
    "select_candidate",
    "rank_candidate",
    "choose_candidate",
    "discard_candidate",
    "resolve_ambiguity",
    "create_selected_meaning",
    "SelectedGovernedMeaningRecord(",
    "integrate_gate_results_into_manifest(",
)


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)


def _fixture(module):
    candidate = module.SelectionCandidateCustodyRecord(
        selection_candidate_custody_id="selection_candidate_custody:demo",
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
    gate = module.GateCustodyReferenceRecord(
        gate_custody_reference_id="gate_custody_reference:demo",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        msm_gate_custody_companion_ref="msm_gate_companion:demo",
        expectancy_family_custody_ref="gate_family_custody:expectancy",
        congruity_family_custody_ref="gate_family_custody:congruity",
        connectedness_family_custody_ref="gate_family_custody:connectedness",
        recoverable_purpose_family_custody_ref=(
            "gate_family_custody:recoverable_purpose"
        ),
        expectancy_result_ref="expectancy_result:demo",
        congruity_result_ref="congruity_result:demo",
        connectedness_result_ref="connectedness_result:demo",
        recoverable_purpose_result_ref="recoverable_purpose_result:demo",
        composition_result_ref="gate_composition_result:demo",
        composition_disposition_refs=(
            "disposition:candidate_supported_for_later_selection_review",
        ),
        candidate_specific_disposition_refs=(
            "candidate_disposition:demo",
        ),
        gate_profile_refs=(
            "gate_profile:expectancy:v1",
            "gate_profile:congruity:v1",
            "gate_profile:connectedness:v1",
            "gate_profile:recoverable_purpose:v1",
        ),
        gate_trace_refs=("gate_trace:demo",),
        gate_provenance_refs=("gate_provenance:demo",),
        gate_limitation_refs=("gate_limitation:demo",),
    )
    requirement = module.SelectionAuthorityRequirementRecord(
        selection_authority_requirement_id="selection_authority_requirement:demo",
        requirement_key="exact_candidate_specific_gate_support",
        requirement_version="v1.0.0",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        governing_document_refs=("document6", "document9", "document10"),
        required_authority_profile_refs=("selection_authority_profile:demo",),
        required_candidate_state_refs=("candidate_state:constructed",),
        required_gate_disposition_refs=(
            "candidate_supported_for_later_selection_review",
        ),
        required_alternative_custody_refs=("alternative_custody:demo",),
        required_unresolved_custody_refs=("unresolved_custody:demo",),
        required_limitation_custody_refs=("limitation_custody:demo",),
        required_predecessor_receipt_refs=("slice40h_receipt:demo",),
        deferred_authority_refs=("slice41c", "slice41d", "slice41e"),
    )
    alternatives = module.AlternativeCandidateCustodyRecord(
        alternative_candidate_custody_id="alternative_custody:demo",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        candidate_set_ref="candidate_set:demo",
        preserved_alternative_candidate_refs=("candidate_meaning:alternative",),
        non_selected_candidate_refs=("candidate_meaning:alternative",),
        alternative_relationship_refs=("alternative_relationship:demo",),
        alternative_disposition_refs=("alternative_disposition:preserved",),
        material_ambiguity_refs=("material_ambiguity:demo",),
        clarification_relevant_refs=("clarification_relevant:demo",),
        shared_ancestry_refs=("shared_ancestry:demo",),
        exact_duplicate_group_refs=(),
    )
    unresolved = module.UnresolvedStateCustodyRecord(
        unresolved_state_custody_id="unresolved_custody:demo",
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
    )
    limitations = module.InheritedLimitationCustodyRecord(
        inherited_limitation_custody_id="limitation_custody:demo",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        source_limitation_refs=("source_limitation:demo",),
        candidate_limitation_refs=("candidate_limitation:demo",),
        gate_limitation_refs=("gate_limitation:demo",),
        effect_boundary_refs=("effect_boundary:read_only",),
        domain_sensitive_refs=("domain_sensitive:software",),
        authority_sensitive_distinction_refs=(
            "request_meaning_is_not_authorization",
        ),
        evidence_boundary_refs=("evidence_boundary:not_validated",),
        memory_boundary_refs=("memory_boundary:no_access_no_write",),
        privacy_boundary_refs=("privacy_boundary:preserve",),
        delivery_boundary_refs=("delivery_boundary:not_authorized",),
        execution_boundary_refs=("execution_boundary:not_authorized",),
        correction_ancestry_refs=("correction_ancestry:demo",),
        supersession_ancestry_refs=("supersession_ancestry:demo",),
    )
    eligibility = module.SelectionEligibilityStatusRecord(
        selection_eligibility_status_id="selection_eligibility_status:demo",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(
            requirement.selection_authority_requirement_id,
        ),
        alternative_candidate_custody_ref=(
            alternatives.alternative_candidate_custody_id
        ),
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=(
            limitations.inherited_limitation_custody_id
        ),
        custody_state=module.SelectionEligibilityCustodyState.NOT_EVALUATED,
        status_reason_refs=("slice41a_schema_only",),
        later_evaluator_ref="slice41c",
    )
    decision = module.SelectedMeaningDecisionStatusRecord(
        selected_meaning_decision_status_id="selected_meaning_decision_status:demo",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=eligibility.selection_eligibility_status_id,
        custody_state=module.SelectedMeaningDecisionCustodyState.NOT_DECIDED,
        decision_reason_refs=("slice41a_schema_only",),
        later_constructor_ref="slice41d",
    )
    trace = module.SelectionTraceBoundaryRecord(
        selection_trace_boundary_id="selection_trace_boundary:demo",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(
            requirement.selection_authority_requirement_id,
        ),
        alternative_candidate_custody_ref=(
            alternatives.alternative_candidate_custody_id
        ),
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=(
            limitations.inherited_limitation_custody_id
        ),
        selection_eligibility_status_ref=eligibility.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=(
            decision.selected_meaning_decision_status_id
        ),
        source_trace_refs=("source_trace:demo",),
        candidate_trace_refs=("candidate_trace:demo",),
        gate_trace_refs=("gate_trace:demo",),
        composition_trace_refs=("composition_trace:demo",),
        predecessor_receipt_refs=("slice40h_receipt:demo",),
        authority_version_refs=(("document6", "v1"),),
        schema_version_refs=(("msm_gate_custody", "v1"),),
    )
    receipt = module.SelectionReceiptBoundaryRecord(
        selection_receipt_boundary_id="selection_receipt_boundary:demo",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=eligibility.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=(
            decision.selected_meaning_decision_status_id
        ),
        selection_trace_boundary_ref=trace.selection_trace_boundary_id,
        required_law_refs=(
            "selected_meaning_is_not_truth",
            "selected_meaning_is_not_evidence",
            "selected_meaning_is_not_permission",
            "selected_meaning_is_not_execution",
        ),
        prohibited_consequence_refs=(
            "truth_determination",
            "evidence_validation",
            "permission_grant",
            "execution_authorization",
            "route_creation",
            "tool_invocation",
            "memory_write",
            "output_rendering",
            "delivery",
        ),
        audit_note="Schema boundary only; no selection receipt exists.",
    )
    aggregate = module.SelectedMeaningRuntimeSchemaRecord(
        selected_meaning_runtime_schema_record_id=(
            "selected_meaning_runtime_schema_record:demo"
        ),
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
    )
    return (
        candidate,
        gate,
        requirement,
        alternatives,
        unresolved,
        limitations,
        eligibility,
        decision,
        trace,
        receipt,
        aggregate,
    )


def _expect_type_error(ledger: Ledger, label: str, callable_obj) -> None:
    try:
        callable_obj()
    except TypeError:
        ledger.check(True, label)
    except Exception as error:
        ledger.check(False, f"{label} wrong error {type(error).__name__}")
    else:
        ledger.check(False, label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    ledger = Ledger()
    module = importlib.import_module(PACKAGE)
    schema_module = importlib.import_module(f"{PACKAGE}.schema")
    authority_module = importlib.import_module(f"{PACKAGE}.authority")
    identity_module = importlib.import_module(f"{PACKAGE}.identity")

    ledger.check(tuple(module.__all__) == EXPECTED_EXPORTS, "exact public exports")
    ledger.check(len(module.__all__) == len(set(module.__all__)), "exports unique")
    for name in EXPECTED_EXPORTS:
        ledger.check(hasattr(module, name), f"export exists {name}")

    eligibility_values = tuple(item.value for item in module.SelectionEligibilityCustodyState)
    decision_values = tuple(item.value for item in module.SelectedMeaningDecisionCustodyState)
    ledger.check(eligibility_values == EXPECTED_ELIGIBILITY_STATES, "exact eligibility custody states")
    ledger.check(decision_values == EXPECTED_DECISION_STATES, "exact decision custody states")
    ledger.check(tuple(module.ELIGIBILITY_CUSTODY_STATE_VALUES) == eligibility_values, "eligibility authority tuple")
    ledger.check(tuple(module.DECISION_CUSTODY_STATE_VALUES) == decision_values, "decision authority tuple")
    ledger.check(set(eligibility_values).isdisjoint(FORBIDDEN_OUTCOME_VALUES), "eligibility states exclude outcomes")
    ledger.check(set(decision_values).isdisjoint(FORBIDDEN_OUTCOME_VALUES), "decision states exclude outcomes")
    for value in (*module.SelectionEligibilityCustodyState, *module.SelectedMeaningDecisionCustodyState):
        ledger.check(isinstance(value, str), f"enum string {value.value}")
        ledger.check(isinstance(value, Enum), f"enum identity {value.value}")

    ledger.check(module.ACCEPTED_PARENT_HEAD == EXPECTED_PARENT_HEAD, "accepted parent HEAD")
    ledger.check(module.ACCEPTED_PARENT_TREE == EXPECTED_PARENT_TREE, "accepted parent tree")
    ledger.check(module.ACCEPTED_PARENT_SUBJECT == EXPECTED_PARENT_SUBJECT, "accepted parent subject")
    ledger.check(module.MSM_V1_SCHEMA_MODIFICATION_ALLOWED is False, "MSM-v1 modification blocked")
    ledger.check(module.MSM_V1_AUTOMATIC_MIGRATION_ALLOWED is False, "MSM-v1 migration blocked")
    ledger.check(module.SELECTION_ELIGIBILITY_EVALUATION_ALLOWED is False, "eligibility evaluation blocked")
    ledger.check(module.SELECTION_PERFORMANCE_ALLOWED is False, "selection performance blocked")
    ledger.check(module.SELECTED_GOVERNED_MEANING_CONSTRUCTION_ALLOWED is False, "selected meaning construction blocked")
    ledger.check(module.BOOTSTRAP_INTEGRATION_ALLOWED is False, "bootstrap integration blocked")
    ledger.check(module.MSM_SELECTED_MEANING_INTEGRATION_DECISION == "deferred_to_slice41e_exact_additive_adapter", "MSM integration deferred")
    ledger.check("slice41c" in module.POSITIVE_ELIGIBILITY_NAMING_DECISION, "positive eligibility name deferred")
    ledger.check("slice41d" in module.SELECTION_DECISION_NAMING_DECISION, "selection decision name deferred")
    ledger.check(len(module.PERMANENT_SELECTED_MEANING_BOUNDARIES) == 50, "permanent boundary count")
    ledger.check(len(module.PROHIBITED_AUTHORITY_PATHS) == 32, "prohibited authority path count")
    ledger.check(len(module.DEFERRED_SLICE41_RUNTIME_AUTHORITY) == 18, "deferred runtime authority count")

    records = _fixture(module)
    record_types = tuple(type(item) for item in records)
    ledger.check(len(record_types) == 11, "record type count")
    ledger.check(len(set(record_types)) == 11, "record types unique")

    for record_type, instance in zip(record_types, records):
        ledger.check(is_dataclass(record_type), f"dataclass {record_type.__name__}")
        ledger.check(getattr(record_type, "__dataclass_params__").frozen is True, f"frozen {record_type.__name__}")
        ledger.check(hasattr(record_type, "__slots__"), f"slots {record_type.__name__}")
        ledger.check(not hasattr(instance, "__dict__"), f"no dict {record_type.__name__}")
        ledger.check(record_type.__module__ == f"{PACKAGE}.schema", f"exact module {record_type.__name__}")
        for item in fields(record_type):
            ledger.check(bool(item.name), f"field named {record_type.__name__}.{item.name}")
            try:
                setattr(instance, item.name, getattr(instance, item.name))
            except (FrozenInstanceError, AttributeError):
                ledger.check(True, f"immutable {record_type.__name__}.{item.name}")
            except Exception as error:
                ledger.check(False, f"immutability wrong error {record_type.__name__}.{item.name}:{type(error).__name__}")
            else:
                ledger.check(False, f"mutable {record_type.__name__}.{item.name}")

    for instance in records:
        available = {item.name: item for item in fields(instance)}
        for field_name in FIXED_TRUE_FIELDS:
            if field_name in available:
                ledger.check(getattr(instance, field_name) is True, f"fixed true {type(instance).__name__}.{field_name}")
                ledger.check(available[field_name].init is False, f"fixed true non-init {type(instance).__name__}.{field_name}")
        for field_name in FIXED_FALSE_FIELDS:
            if field_name in available:
                ledger.check(getattr(instance, field_name) is False, f"fixed false {type(instance).__name__}.{field_name}")
                ledger.check(available[field_name].init is False, f"fixed false non-init {type(instance).__name__}.{field_name}")

    aggregate = records[-1]
    ledger.check(aggregate.selection_candidate_custody is records[0], "aggregate exact candidate custody")
    ledger.check(aggregate.gate_custody_reference is records[1], "aggregate exact gate custody")
    ledger.check(aggregate.selection_authority_requirements == (records[2],), "aggregate exact authority requirements")
    ledger.check(aggregate.alternative_candidate_custody is records[3], "aggregate exact alternatives")
    ledger.check(aggregate.unresolved_state_custody is records[4], "aggregate exact unresolved custody")
    ledger.check(aggregate.inherited_limitation_custody is records[5], "aggregate exact limitations")
    ledger.check(aggregate.selection_eligibility_status is records[6], "aggregate exact eligibility custody")
    ledger.check(aggregate.selected_meaning_decision_status is records[7], "aggregate exact decision custody")
    ledger.check(aggregate.selection_trace_boundary is records[8], "aggregate exact trace boundary")
    ledger.check(aggregate.selection_receipt_boundary is records[9], "aggregate exact receipt boundary")
    ledger.check(tuple(aggregate.permanent_boundaries) == tuple(module.PERMANENT_SELECTED_MEANING_BOUNDARIES), "aggregate permanent boundaries")

    _expect_type_error(
        ledger,
        "missing required constructor field rejected",
        lambda: module.SelectionCandidateCustodyRecord(),
    )
    _expect_type_error(
        ledger,
        "unknown constructor field rejected",
        lambda: module.SelectionCandidateCustodyRecord(
            selection_candidate_custody_id="x",
            candidate_meaning_id="x",
            candidate_state_id="x",
            candidate_lineage_id="x",
            source_expression_ref="x",
            manifest_candidate_record_ref="x",
            manifest_candidate_companion_ref="x",
            candidate_identity_ref="x",
            candidate_content_ref="x",
            candidate_provenance_ref="x",
            candidate_construction_receipt_ref="x",
            candidate_set_ref="x",
            candidate_set_member_ref="x",
            candidate_lifecycle_ref="x",
            gate_candidate_input_ref="x",
            predecessor_receipt_refs=(),
            invented_field=True,
        ),
    )
    _expect_type_error(
        ledger,
        "candidate selected flag cannot be injected",
        lambda: module.SelectionCandidateCustodyRecord(
            selection_candidate_custody_id="x",
            candidate_meaning_id="x",
            candidate_state_id="x",
            candidate_lineage_id="x",
            source_expression_ref="x",
            manifest_candidate_record_ref="x",
            manifest_candidate_companion_ref="x",
            candidate_identity_ref="x",
            candidate_content_ref="x",
            candidate_provenance_ref="x",
            candidate_construction_receipt_ref="x",
            candidate_set_ref="x",
            candidate_set_member_ref="x",
            candidate_lifecycle_ref="x",
            gate_candidate_input_ref="x",
            predecessor_receipt_refs=(),
            candidate_selected=True,
        ),
    )
    _expect_type_error(
        ledger,
        "eligibility outcome cannot be injected",
        lambda: module.SelectionEligibilityStatusRecord(
            selection_eligibility_status_id="x",
            selection_candidate_custody_ref="x",
            gate_custody_reference_ref="x",
            selection_authority_requirement_refs=(),
            alternative_candidate_custody_ref="x",
            unresolved_state_custody_ref="x",
            inherited_limitation_custody_ref="x",
            custody_state=module.SelectionEligibilityCustodyState.NOT_EVALUATED,
            status_reason_refs=(),
            later_evaluator_ref=None,
            eligibility_evaluated=True,
        ),
    )
    _expect_type_error(
        ledger,
        "selection decision cannot be injected",
        lambda: module.SelectedMeaningDecisionStatusRecord(
            selected_meaning_decision_status_id="x",
            selection_candidate_custody_ref="x",
            selection_eligibility_status_ref="x",
            custody_state=module.SelectedMeaningDecisionCustodyState.NOT_DECIDED,
            decision_reason_refs=(),
            later_constructor_ref=None,
            decision_performed=True,
        ),
    )
    _expect_type_error(
        ledger,
        "alternatives discarded cannot be injected",
        lambda: module.AlternativeCandidateCustodyRecord(
            alternative_candidate_custody_id="x",
            selection_candidate_custody_ref="x",
            candidate_set_ref="x",
            preserved_alternative_candidate_refs=(),
            non_selected_candidate_refs=(),
            alternative_relationship_refs=(),
            alternative_disposition_refs=(),
            material_ambiguity_refs=(),
            clarification_relevant_refs=(),
            shared_ancestry_refs=(),
            exact_duplicate_group_refs=(),
            alternatives_discarded=True,
        ),
    )
    _expect_type_error(
        ledger,
        "MSM modification cannot be injected",
        lambda: module.SelectedMeaningRuntimeSchemaRecord(
            selected_meaning_runtime_schema_record_id="x",
            selection_candidate_custody=records[0],
            gate_custody_reference=records[1],
            selection_authority_requirements=(records[2],),
            alternative_candidate_custody=records[3],
            unresolved_state_custody=records[4],
            inherited_limitation_custody=records[5],
            selection_eligibility_status=records[6],
            selected_meaning_decision_status=records[7],
            selection_trace_boundary=records[8],
            selection_receipt_boundary=records[9],
            msm_v1_schema_modified=True,
        ),
    )
    _expect_type_error(
        ledger,
        "selected meaning creation cannot be injected",
        lambda: module.SelectedMeaningRuntimeSchemaRecord(
            selected_meaning_runtime_schema_record_id="x",
            selection_candidate_custody=records[0],
            gate_custody_reference=records[1],
            selection_authority_requirements=(records[2],),
            alternative_candidate_custody=records[3],
            unresolved_state_custody=records[4],
            inherited_limitation_custody=records[5],
            selection_eligibility_status=records[6],
            selected_meaning_decision_status=records[7],
            selection_trace_boundary=records[8],
            selection_receipt_boundary=records[9],
            selected_meaning_created=True,
        ),
    )
    try:
        module.SelectionEligibilityCustodyState("eligible")
    except ValueError:
        ledger.check(True, "forbidden eligibility enum value rejected")
    else:
        ledger.check(False, "forbidden eligibility enum value rejected")
    try:
        module.SelectedMeaningDecisionCustodyState("selected")
    except ValueError:
        ledger.check(True, "forbidden decision enum value rejected")
    else:
        ledger.check(False, "forbidden decision enum value rejected")

    package_dir = repository / "aiweb_language_core_bootstrap" / "selected_meaning_runtime"
    expected_files = ("__init__.py", "authority.py", "identity.py", "schema.py")
    actual_files = tuple(sorted(item.name for item in package_dir.iterdir() if item.is_file()))
    ledger.check(actual_files == expected_files, "exact package file set")
    for name in expected_files:
        source = (package_dir / name).read_text(encoding="utf-8")
        ast.parse(source)
        ledger.check(True, f"AST parse {name}")
        for token in FORBIDDEN_SCHEMA_TOKENS:
            ledger.check(token not in source, f"forbidden token absent {name}:{token}")

    schema_tree = ast.parse((package_dir / "schema.py").read_text(encoding="utf-8"))
    executable_defs = tuple(
        node
        for node in ast.walk(schema_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
    )
    ledger.check(not executable_defs, "schema contains no executable functions")
    forbidden_import_roots = {
        "aiweb_language_core_bootstrap.meaning_structure_manifest",
        "aiweb_language_core_bootstrap.candidate_meaning_construction",
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime",
        "aiweb_language_core_bootstrap.msm_gate_custody",
    }
    imported = set()
    for node in ast.walk(schema_tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    ledger.check(imported.isdisjoint(forbidden_import_roots), "predecessor runtimes not imported")

    old_selected = repository / "aiweb_selected_meaning_boundary_scaffold"
    ledger.check(old_selected.is_dir(), "Slice 16 boundary scaffold preserved")
    msm_records = repository / "aiweb_language_core_bootstrap" / "meaning_structure_manifest" / "_records.py"
    msm_text = msm_records.read_text(encoding="utf-8")
    ledger.check("class SelectedGovernedMeaningRecord" in msm_text, "dormant MSM selected record preserved")
    ledger.check("selected_governed_meanings: tuple[SelectedGovernedMeaningRecord, ...]" in msm_text, "dormant MSM selected collection preserved")
    bootstrap_text = (
        repository
        / "aiweb_language_core_bootstrap"
        / "meaning_structure_manifest"
        / "bootstrap_integration.py"
    ).read_text(encoding="utf-8")
    ledger.check("selected_governed_meanings=()" in bootstrap_text, "MSM bootstrap selected meanings remain empty")

    print("AI.WEB SLICE 41A SELECTED MEANING RUNTIME CORE SCHEMA BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print("malformed_constructor_cases=10")
    print("record_types=11")
    print("eligibility_custody_state_count=4")
    print("decision_custody_state_count=4")
    print(f"permanent_boundaries={len(module.PERMANENT_SELECTED_MEANING_BOUNDARIES)}")
    print(f"prohibited_authority_paths={len(module.PROHIBITED_AUTHORITY_PATHS)}")
    print("protected_predecessor_files=587")
    print("exact_payload_paths=12")
    print("schema_only=1")
    print("exact_candidate_and_gate_custody_shapes=1")
    print("alternative_and_unresolved_custody_shapes=1")
    print("inherited_limitation_custody_shape=1")
    print("eligibility_status_is_custody_only=1")
    print("decision_status_is_custody_only=1")
    print("selection_eligibility_evaluated=0")
    print("candidate_ranked=0")
    print("alternatives_discarded=0")
    print("ambiguity_resolved=0")
    print("selection_decision_performed=0")
    print("selected_meaning_created=0")
    print("msm_v1_schema_modified=0")
    print("bootstrap_integration_enabled=0")
    print("governed_outward_meaning_created=0")
    print("truth_evidence_proof_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print("language_model_embedding_vector_rag_similarity=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print(f"FAIL: {failure}")
    if ledger.failures:
        print("AI.WEB SLICE 41A BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 41A BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
