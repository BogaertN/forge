#!/usr/bin/env python3
"""Visible behavior test for AI.Web Slice 41C."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, fields, replace
import importlib
from pathlib import Path
import runpy
import sys

PACKAGE = (
    "aiweb_language_core_bootstrap.selected_meaning_runtime."
    "eligibility_evaluation"
)


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.malformed_cases = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)


def _namespace(repository: Path, filename: str):
    return runpy.run_path(str(repository / "scripts" / filename))


def _manifest_fixture(msm):
    candidate = msm.CandidateMeaningRecord(
        record_id="msm_candidate_record:demo",
        lineage_id="lineage:demo",
        source_expression_ref="source_expression:demo",
        communicative_act="request",
        concept_refs=("concept:demo",),
        relation_refs=("relation:demo",),
        meaning_modifiers=(),
        ambiguity_reasons=(),
        unresolved_referents=(),
        authority_sensitive_implications=("meaning_not_permission",),
        preservation_classes=(
            msm.SemanticPreservationClass.PERMISSION_VERSUS_REQUEST,
            msm.SemanticPreservationClass.NON_LLM_PROVENANCE,
        ),
    )
    lineage = msm.LineageRootRecord(
        lineage_id="lineage:demo",
        origin_kind=msm.LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION,
        origin_ref="source_expression:demo",
        direction=msm.SemanticDirection.INWARD,
    )
    manifest = msm.MeaningStructureManifestV1(
        manifest_id="manifest:demo",
        lineage_root=lineage,
        candidate_meanings=(candidate,),
        non_selection_outcomes=(),
        selected_governed_meanings=(),
        governed_result_references=(),
        governed_outward_meanings=(),
        expression_links=(),
        validation_links=(),
        delivery_or_containment_links=(),
        external_authority_references=(),
        semantic_transition_traces=(),
    )
    return manifest, candidate


def _manifest_companion(integration_package, candidate):
    return integration_package.CandidateMeaningManifestCompanionV1(
        companion_id="msm_candidate_companion:demo",
        companion_version="v1.0.0",
        manifest_candidate_record_id=candidate.record_id,
        candidate_meaning_id="candidate_meaning:demo",
        candidate_lineage_id=candidate.lineage_id,
        candidate_state_id="candidate_state:demo",
        candidate_identity_ref="candidate_identity:demo",
        candidate_content_ref="candidate_content:demo",
        candidate_provenance_ref="candidate_provenance:demo",
        construction_receipt_ref="candidate_receipt:demo",
        construction_trace_reference_id="trace_reference:demo",
        provenance_reference_id="provenance_reference:demo",
        limitation_reference_id="limitation_reference:demo",
        alternative_relationship_ids=("alternative_relationship:demo",),
        exact_adapter=True,
        lossless_custody=True,
        candidate_side_only=True,
        selected_meaning_created=False,
        gate_outcome_created=False,
    )


def _composition_fixture(
    composition,
    helpers,
    bundles,
    family_results,
    case_name: str,
):
    result_refs = tuple(item.result_id for item in family_results)
    candidate_ref = "candidate_composition:demo:v1"
    branch_ref = "candidate_branch:demo:primary"
    changes: dict[str, tuple[str, ...]] = {}

    if case_name in {"eligible", "not_eligible"}:
        assertions = (
            helpers["make_assertion"](
                composition,
                candidate_ref,
                branch_ref,
                result_refs,
                composition.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
            ),
        )
    elif case_name == "held":
        assertions = tuple(
            helpers["make_assertion"](
                composition,
                candidate_ref,
                branch_ref,
                result_refs,
                kind,
            )
            for kind in (
                composition.GateCompositionDispositionKind.HELD,
                composition.GateCompositionDispositionKind.BLOCKED_PROGRESSION,
                composition.GateCompositionDispositionKind.REFUSAL_RELEVANT,
            )
        )
    elif case_name == "materially_unresolved":
        assertions = (
            helpers["make_assertion"](
                composition,
                candidate_ref,
                branch_ref,
                result_refs,
                composition.GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED,
            ),
        )
        changes.update(
            material_competing_candidate_refs=("candidate_meaning:alternative",),
            competing_candidate_disposition_refs=("alternative_disposition:held",),
        )
    elif case_name == "clarification_dependent":
        assertions = (
            helpers["make_assertion"](
                composition,
                candidate_ref,
                branch_ref,
                result_refs,
                composition.GateCompositionDispositionKind.CLARIFICATION_RELEVANT,
            ),
        )
        changes["user_suppliable_clarification_refs"] = (
            "clarification_support:user_can_supply_exact_referent",
        )
    elif case_name == "unsupported":
        assertions = (
            helpers["make_assertion"](
                composition,
                candidate_ref,
                branch_ref,
                result_refs,
                composition.GateCompositionDispositionKind.UNSUPPORTED,
            ),
        )
    elif case_name == "conflicted":
        assertions = (
            helpers["make_assertion"](
                composition,
                candidate_ref,
                branch_ref,
                result_refs,
                composition.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
                authority=composition.GateCompositionAuthorityState.CONFLICTED,
            ),
        )
    elif case_name == "indeterminate":
        assertions = (
            helpers["make_assertion"](
                composition,
                candidate_ref,
                branch_ref,
                result_refs,
                composition.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
                authority=composition.GateCompositionAuthorityState.ABSENT,
            ),
        )
    else:
        raise ValueError(f"unknown case: {case_name}")

    evaluation_input = helpers["make_input"](
        composition,
        bundles,
        family_results,
        assertions,
        **changes,
    )
    return composition.evaluate_gate_composition(evaluation_input)


def _governance_bundle(
    core,
    governed,
    eligibility,
    custody,
    manifest_candidate,
    manifest_companion,
    gate_companion,
    composition_result,
    case_name: str,
):
    candidate = governed.with_expected_id(core.SelectionCandidateCustodyRecord(
        selection_candidate_custody_id="placeholder",
        candidate_meaning_id=manifest_companion.candidate_meaning_id,
        candidate_state_id=manifest_companion.candidate_state_id,
        candidate_lineage_id=manifest_companion.candidate_lineage_id,
        source_expression_ref=manifest_candidate.source_expression_ref,
        manifest_candidate_record_ref=manifest_candidate.record_id,
        manifest_candidate_companion_ref=manifest_companion.companion_id,
        candidate_identity_ref=manifest_companion.candidate_identity_ref,
        candidate_content_ref=manifest_companion.candidate_content_ref,
        candidate_provenance_ref=manifest_companion.candidate_provenance_ref,
        candidate_construction_receipt_ref=manifest_companion.construction_receipt_ref,
        candidate_set_ref="candidate_set:demo",
        candidate_set_member_ref="candidate_set_member:demo",
        candidate_lifecycle_ref="candidate_lifecycle:demo",
        gate_candidate_input_ref=composition_result.candidate_input_ref,
        predecessor_receipt_refs=("slice40h_receipt:demo",),
    ))

    family_map = {item.family: item for item in gate_companion.family_custody}
    disposition_ids = tuple(
        item.disposition_id for item in composition_result.dispositions
    )
    gate = governed.with_expected_id(core.GateCustodyReferenceRecord(
        gate_custody_reference_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        msm_gate_custody_companion_ref=gate_companion.companion_id,
        expectancy_family_custody_ref=family_map[
            custody.GateFamilyName.EXPECTANCY
        ].custody_id,
        congruity_family_custody_ref=family_map[
            custody.GateFamilyName.CONGRUITY
        ].custody_id,
        connectedness_family_custody_ref=family_map[
            custody.GateFamilyName.CONNECTEDNESS
        ].custody_id,
        recoverable_purpose_family_custody_ref=family_map[
            custody.GateFamilyName.RECOVERABLE_PURPOSE
        ].custody_id,
        expectancy_result_ref=composition_result.expectancy_result_id,
        congruity_result_ref=composition_result.congruity_result_id,
        connectedness_result_ref=composition_result.connectedness_result_id,
        recoverable_purpose_result_ref=(
            composition_result.recoverable_purpose_result_id
        ),
        composition_result_ref=composition_result.result_id,
        composition_disposition_refs=disposition_ids,
        candidate_specific_disposition_refs=disposition_ids,
        gate_profile_refs=("gate_profile:composition:v1",),
        gate_trace_refs=("gate_trace:demo",),
        gate_provenance_refs=("gate_provenance:demo",),
        gate_limitation_refs=("gate_limitation:demo",),
    ))

    material = case_name == "materially_unresolved"
    alternative = governed.with_expected_id(core.AlternativeCandidateCustodyRecord(
        alternative_candidate_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        candidate_set_ref=candidate.candidate_set_ref,
        preserved_alternative_candidate_refs=("candidate_meaning:alternative",),
        non_selected_candidate_refs=("candidate_meaning:alternative",),
        alternative_relationship_refs=("alternative_relationship:demo",),
        alternative_disposition_refs=("alternative_disposition:preserved",),
        material_ambiguity_refs=("material_ambiguity:demo",) if material else (),
        clarification_relevant_refs=(
            ("clarification_relevant:demo",)
            if case_name == "clarification_dependent"
            else ()
        ),
        shared_ancestry_refs=("shared_ancestry:demo",),
        exact_duplicate_group_refs=(),
    ))

    unresolved = governed.with_expected_id(core.UnresolvedStateCustodyRecord(
        unresolved_state_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        unresolved_candidate_refs=(
            ("candidate_meaning:alternative",) if material else ()
        ),
        unknown_refs=(),
        unsupported_refs=(
            ("unsupported:demo",) if case_name == "unsupported" else ()
        ),
        conflicted_refs=(
            ("conflicted:demo",) if case_name == "conflicted" else ()
        ),
        clarification_dependency_refs=(
            ("clarification_dependency:demo",)
            if case_name == "clarification_dependent"
            else ()
        ),
        held_refs=(("held:demo",) if case_name == "held" else ()),
        blocked_progression_refs=(
            ("blocked_progression:demo",) if case_name == "held" else ()
        ),
        refusal_relevant_refs=(
            ("refusal_relevant:demo",) if case_name == "held" else ()
        ),
        missing_authority_refs=(
            ("missing_authority:demo",) if case_name == "held" else ()
        ),
        missing_structure_refs=(),
        deferred_dependency_refs=(
            ("later_authority:slice41d",) if case_name == "held" else ()
        ),
    ))

    limitation = governed.with_expected_id(core.InheritedLimitationCustodyRecord(
        inherited_limitation_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        source_limitation_refs=("source_limitation:demo",),
        candidate_limitation_refs=(),
        gate_limitation_refs=("gate_limitation:demo",),
        effect_boundary_refs=("effect_boundary:no_action",),
        domain_sensitive_refs=(),
        authority_sensitive_distinction_refs=("meaning_not_permission",),
        evidence_boundary_refs=("evidence_not_validated",),
        memory_boundary_refs=("memory_not_accessed",),
        privacy_boundary_refs=(),
        delivery_boundary_refs=("delivery_not_authorized",),
        execution_boundary_refs=("execution_not_authorized",),
        correction_ancestry_refs=(),
        supersession_ancestry_refs=(),
    ))

    required_dispositions = tuple(
        item.disposition_kind.value for item in composition_result.dispositions
    ) or (composition_result.composition_status.value,)
    requirement = governed.with_expected_id(core.SelectionAuthorityRequirementRecord(
        selection_authority_requirement_id="placeholder",
        requirement_key="strict_candidate_specific_selection_eligibility",
        requirement_version="v1.0.0",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        governing_document_refs=(
            "canonical_roadmap:slice41c",
            "document6:selection_eligibility",
            "slice40g",
            "slice40h",
            "slice41a",
            "slice41b",
        ),
        required_authority_profile_refs=(
            eligibility.APPROVED_STRICT_PROFILE.profile_id,
        ),
        required_candidate_state_refs=(candidate.candidate_state_id,),
        required_gate_disposition_refs=required_dispositions,
        required_alternative_custody_refs=(
            alternative.alternative_candidate_custody_id,
        ),
        required_unresolved_custody_refs=(
            unresolved.unresolved_state_custody_id,
        ),
        required_limitation_custody_refs=(
            limitation.inherited_limitation_custody_id,
        ),
        required_predecessor_receipt_refs=("slice40h_receipt:demo",),
        deferred_authority_refs=("slice41d", "slice41e"),
    ))

    prior = governed.with_expected_id(core.SelectionEligibilityStatusRecord(
        selection_eligibility_status_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(
            requirement.selection_authority_requirement_id,
        ),
        alternative_candidate_custody_ref=(
            alternative.alternative_candidate_custody_id
        ),
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=(
            limitation.inherited_limitation_custody_id
        ),
        custody_state=core.SelectionEligibilityCustodyState.READY_FOR_LATER_EVALUATION,
        status_reason_refs=("slice41c_evaluator_ready",),
        later_evaluator_ref="slice41c",
    ))
    decision = governed.with_expected_id(core.SelectedMeaningDecisionStatusRecord(
        selected_meaning_decision_status_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=prior.selection_eligibility_status_id,
        custody_state=core.SelectedMeaningDecisionCustodyState.NOT_DECIDED,
        decision_reason_refs=("slice41d_deferred",),
        later_constructor_ref="slice41d",
    ))
    trace = governed.with_expected_id(core.SelectionTraceBoundaryRecord(
        selection_trace_boundary_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(
            requirement.selection_authority_requirement_id,
        ),
        alternative_candidate_custody_ref=(
            alternative.alternative_candidate_custody_id
        ),
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=(
            limitation.inherited_limitation_custody_id
        ),
        selection_eligibility_status_ref=prior.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=(
            decision.selected_meaning_decision_status_id
        ),
        source_trace_refs=("source_trace:demo",),
        candidate_trace_refs=("candidate_trace:demo",),
        gate_trace_refs=("gate_trace:demo",),
        composition_trace_refs=("composition_trace:demo",),
        predecessor_receipt_refs=("slice40h_receipt:demo",),
        authority_version_refs=(("slice41c_profile", "v1.0.0"),),
        schema_version_refs=(
            ("slice40h", gate_companion.schema_version),
            ("slice40g", composition_result.schema_version),
        ),
    ))
    receipt = governed.with_expected_id(core.SelectionReceiptBoundaryRecord(
        selection_receipt_boundary_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=prior.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=(
            decision.selected_meaning_decision_status_id
        ),
        selection_trace_boundary_ref=trace.selection_trace_boundary_id,
        required_law_refs=("eligibility_is_not_selection",),
        prohibited_consequence_refs=(
            "selected_meaning_creation",
            "msm_mutation",
            "permission",
            "execution",
        ),
        audit_note="Slice 41C eligibility evaluation only.",
    ))
    runtime = governed.with_expected_id(core.SelectedMeaningRuntimeSchemaRecord(
        selected_meaning_runtime_schema_record_id="placeholder",
        selection_candidate_custody=candidate,
        gate_custody_reference=gate,
        selection_authority_requirements=(requirement,),
        alternative_candidate_custody=alternative,
        unresolved_state_custody=unresolved,
        inherited_limitation_custody=limitation,
        selection_eligibility_status=prior,
        selected_meaning_decision_status=decision,
        selection_trace_boundary=trace,
        selection_receipt_boundary=receipt,
    ))
    version = governed.with_expected_id(governed.SelectedMeaningVersionCustody(
        custody_id="placeholder",
        runtime_schema_record_id=runtime.selected_meaning_runtime_schema_record_id,
        runtime_schema_version=runtime.schema_version,
        runtime_schema_id=runtime.schema_id,
        runtime_spec_id=runtime.spec_id,
        runtime_spec_version=runtime.spec_version,
        record_schema_versions=governed.expected_record_schema_versions(runtime),
        predecessor_references=governed.expected_predecessor_references(runtime),
        accepted_parent_head=governed.SLICE41B_ACCEPTED_PARENT_HEAD,
        accepted_parent_tree=governed.SLICE41B_ACCEPTED_PARENT_TREE,
        accepted_parent_subject=governed.SLICE41B_ACCEPTED_PARENT_SUBJECT,
        canonical_field_order_version=governed.CANONICAL_FIELD_ORDER_VERSION,
        digest_algorithm=governed.DIGEST_ALGORITHM,
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
    lifecycle = governed.with_expected_id(governed.SelectedMeaningLifecycleRecord(
        lifecycle_record_id="placeholder",
        runtime_schema_record_id=runtime.selected_meaning_runtime_schema_record_id,
        version_custody_ref=version.custody_id,
        stage=governed.SelectedMeaningLifecycleStage.RECORD_SEALED,
        predecessor_lifecycle_record_ids=(),
        predecessor_reference_ids=tuple(
            value for _, value in version.predecessor_references
        ),
        validation_issue_digest_refs=(),
        reason_refs=("slice41b_record_sealed",),
        automatic_progression=False,
        canonical_serialization_performed=True,
        deterministic_identity_validated=True,
        predecessor_references_validated=True,
        cross_record_consistency_validated=True,
        malformed_record_rejected=True,
        unknown_version_rejected=True,
        duplicate_record_rejected=True,
        identity_collision_rejected=True,
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
    return governed.with_expected_bundle_identity(governed.SelectedMeaningGovernanceBundle(
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


def _evaluation_input(
    eligibility,
    bundle,
    manifest_candidate,
    manifest_companion,
    gate_companion,
    composition_result,
    case_name: str,
):
    value = eligibility.SelectionEligibilityEvaluationInput(
        evaluation_input_id="placeholder",
        governance_bundle=bundle,
        manifest_candidate_record=manifest_candidate,
        manifest_candidate_companion=manifest_companion,
        msm_gate_custody_companion=gate_companion,
        gate_composition_result=composition_result,
        authority_profile=eligibility.APPROVED_STRICT_PROFILE,
        candidate_dispositions=composition_result.dispositions,
        explicit_positive_support_refs=(
            tuple(
                disposition.disposition_id
                for disposition in composition_result.dispositions
                if disposition.disposition_kind.value
                == "candidate_supported_for_later_selection_review"
            )
            if case_name in {"eligible", "not_eligible"}
            else ()
        ),
        explicit_not_eligible_refs=(
            ("selection_authority:not_eligible",)
            if case_name == "not_eligible"
            else ()
        ),
        authority_profile_refs=(eligibility.APPROVED_STRICT_PROFILE.profile_id,),
        trace_refs=("slice41c:trace",),
        provenance_refs=("slice41c:provenance",),
        version_refs=("slice41c:v1",),
        candidate_ranking_used=False,
        confidence_scoring_used=False,
        probability_ranking_used=False,
        semantic_similarity_used=False,
        nearest_known_substitution_used=False,
        language_model_used=False,
        hidden_classifier_used=False,
        only_candidate_automatic_eligibility_used=False,
        first_candidate_automatic_eligibility_used=False,
        safest_candidate_automatic_eligibility_used=False,
        refusal_relevance_erased=False,
        blocked_progression_erased=False,
        unresolved_alternatives_erased=False,
        understood_meaning_converted_to_permission=False,
    )
    return eligibility.with_expected_evaluation_input_id(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    eligibility = importlib.import_module(PACKAGE)
    core = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime"
    )
    governed = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime.governed_lifecycle"
    )
    gate_core = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
    )
    gate_governed = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.governed_lifecycle"
    )
    composition = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.gate_composition"
    )
    custody = importlib.import_module(
        "aiweb_language_core_bootstrap.msm_gate_custody"
    )
    msm = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest"
    )
    integration_package = importlib.import_module(
        "aiweb_language_core_bootstrap.candidate_meaning_construction."
        "manifest_candidate_integration"
    )

    gate_helpers = _namespace(
        repository,
        "test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py",
    )
    bundles, family_results, _ = gate_helpers["build_family_results"](
        repository,
        gate_core,
        gate_governed,
    )
    manifest, manifest_candidate = _manifest_fixture(msm)
    manifest_companion = _manifest_companion(
        integration_package,
        manifest_candidate,
    )

    from aiweb_language_core_bootstrap.meaning_structure_manifest.validation import (
        validate_manifest,
    )
    ledger.check(validate_manifest(manifest).ok, "valid MSM-v1 fixture")

    expected_outcomes = {
        "eligible": eligibility.SelectionEligibilityOutcome.ELIGIBLE_FOR_SELECTED_MEANING_CONSTRUCTION,
        "held": eligibility.SelectionEligibilityOutcome.HELD_PENDING_AUTHORITY,
        "materially_unresolved": eligibility.SelectionEligibilityOutcome.MATERIALLY_UNRESOLVED,
        "clarification_dependent": eligibility.SelectionEligibilityOutcome.CLARIFICATION_DEPENDENT,
        "unsupported": eligibility.SelectionEligibilityOutcome.UNSUPPORTED,
        "conflicted": eligibility.SelectionEligibilityOutcome.CONFLICTED,
        "indeterminate": eligibility.SelectionEligibilityOutcome.INDETERMINATE,
        "not_eligible": eligibility.SelectionEligibilityOutcome.NOT_ELIGIBLE,
    }

    case_inputs = {}
    case_results = {}
    for case_name, expected_outcome in expected_outcomes.items():
        composition_result = _composition_fixture(
            composition,
            gate_helpers,
            bundles,
            family_results,
            case_name,
        )
        gate_integration = custody.integrate_gate_results_into_manifest(
            manifest,
            manifest_candidate.record_id,
            *family_results,
            composition_result,
        )
        ledger.check(
            custody.validate_result(gate_integration).ok,
            f"valid Slice 40H custody {case_name}",
        )
        bundle = _governance_bundle(
            core,
            governed,
            eligibility,
            custody,
            manifest_candidate,
            manifest_companion,
            gate_integration.companion,
            composition_result,
            case_name,
        )
        ledger.check(
            governed.validate_governance_bundle(bundle).ok,
            f"valid Slice 41B bundle {case_name}",
        )
        evaluation_input = _evaluation_input(
            eligibility,
            bundle,
            manifest_candidate,
            manifest_companion,
            gate_integration.companion,
            composition_result,
            case_name,
        )
        input_report = eligibility.validate_evaluation_input(evaluation_input)
        ledger.check(input_report.ok, f"valid 41C input {case_name}: {input_report.issues}")
        result = eligibility.evaluate_selection_eligibility(evaluation_input)
        result_repeat = eligibility.evaluate_selection_eligibility(evaluation_input)
        ledger.check(result == result_repeat, f"deterministic repeat {case_name}")
        ledger.check(result.outcome is expected_outcome, f"outcome {case_name}")
        ledger.check(
            eligibility.validate_result(
                result,
                evaluation_input=evaluation_input,
            ).ok,
            f"valid result {case_name}",
        )
        ledger.check(
            result.eligible_for_selected_meaning_construction
            is (case_name == "eligible"),
            f"eligibility flag {case_name}",
        )
        ledger.check(result.alternatives_preserved, f"alternatives preserved {case_name}")
        ledger.check(result.unresolved_states_preserved, f"unresolved preserved {case_name}")
        ledger.check(result.refusal_relevance_preserved, f"refusal preserved {case_name}")
        ledger.check(result.blocked_progression_preserved, f"blocked preserved {case_name}")
        ledger.check(result.inherited_limitations_preserved, f"limitations preserved {case_name}")
        ledger.check(
            not any((
                result.candidate_ranked,
                result.selection_performed,
                result.selected_meaning_created,
                result.msm_v1_modified,
                result.bootstrap_integration_enabled,
                result.truth_determined,
                result.evidence_validated,
                result.permission_granted,
                result.execution_authorized,
                result.route_created,
                result.tool_invoked,
                result.action_performed,
                result.memory_accessed,
                result.memory_written,
                result.rendered,
                result.delivered,
                result.external_resource_loaded,
                result.language_model_used,
                result.hidden_classifier_used,
                result.confidence_scoring_used,
                result.probability_ranking_used,
                result.semantic_similarity_used,
                result.nearest_known_substitution_used,
                result.only_candidate_automatic_eligibility_used,
                result.first_candidate_automatic_eligibility_used,
                result.safest_candidate_automatic_eligibility_used,
                result.refusal_relevance_erased,
                result.blocked_progression_erased,
                result.unresolved_alternatives_erased,
                result.understood_meaning_converted_to_permission,
            )),
            f"authority zero {case_name}",
        )
        case_inputs[case_name] = evaluation_input
        case_results[case_name] = result

    eligible_input = case_inputs["eligible"]
    eligible_result = case_results["eligible"]
    ledger.check(
        bool(eligible_result.preserved_alternative_candidate_refs),
        "nonmaterial alternatives remain visible in eligible result",
    )
    ledger.check(
        not eligible_result.material_ambiguity_refs,
        "nonmaterial alternative is not silently called material ambiguity",
    )
    held_result = case_results["held"]
    ledger.check(bool(held_result.refusal_relevant_refs), "refusal relevance retained")
    ledger.check(bool(held_result.blocked_progression_refs), "blocked progression retained")

    ledger.check(
        eligibility.canonical_record_bytes(eligible_input)
        == eligibility.canonical_record_bytes(eligible_input),
        "canonical input repeat",
    )
    ledger.check(
        eligible_result.result_id == eligibility.expected_result_id(eligible_result),
        "result identity",
    )
    ledger.check(
        eligible_result.canonical_digest
        == eligibility.expected_result_digest(eligible_result),
        "result digest",
    )
    ledger.check(
        len(eligibility.APPROVED_SELECTION_AUTHORITY_PROFILES) == 1,
        "one approved profile",
    )
    ledger.check(
        tuple(eligibility.SelectionEligibilityOutcome)
        == eligibility.APPROVED_STRICT_PROFILE.permitted_outcomes,
        "exact outcome profile",
    )
    for record_type in eligibility.SUPPORTED_RECORD_TYPES:
        ledger.check(
            tuple(item.name for item in fields(record_type))
            == eligibility.canonical_field_order(record_type),
            f"canonical field order {record_type.__name__}",
        )

    try:
        eligible_result.outcome = eligibility.SelectionEligibilityOutcome.NOT_ELIGIBLE
        immutable = False
    except FrozenInstanceError:
        immutable = True
    ledger.check(immutable, "result immutable")

    bad_candidate = replace(
        eligible_input.manifest_candidate_record,
        record_id="msm_candidate_record:wrong",
    )
    ledger.malformed(
        not eligibility.validate_evaluation_input(
            replace(
                eligible_input,
                evaluation_input_id="placeholder",
                manifest_candidate_record=bad_candidate,
            )
        ).ok,
        "candidate mismatch rejected",
    )
    bad_profile = replace(
        eligibility.APPROVED_STRICT_PROFILE,
        profile_version="v2.0.0",
    )
    ledger.malformed(
        not eligibility.validate_authority_profile(bad_profile).ok,
        "unknown profile rejected",
    )
    bad_strategy = replace(
        eligible_input,
        evaluation_input_id="placeholder",
        semantic_similarity_used=True,
    )
    ledger.malformed(
        not eligibility.validate_evaluation_input(bad_strategy).ok,
        "semantic similarity rejected",
    )
    bad_support = replace(
        eligible_input,
        evaluation_input_id="placeholder",
        explicit_positive_support_refs=("unbound_support:wrong_candidate",),
    )
    bad_support = eligibility.with_expected_evaluation_input_id(bad_support)
    ledger.malformed(
        not eligibility.validate_evaluation_input(bad_support).ok,
        "unbound positive support rejected",
    )
    duplicate_dispositions = replace(
        eligible_input,
        evaluation_input_id="placeholder",
        candidate_dispositions=(
            eligible_input.candidate_dispositions[0],
            eligible_input.candidate_dispositions[0],
        ),
    )
    duplicate_dispositions = eligibility.with_expected_evaluation_input_id(
        duplicate_dispositions
    )
    ledger.malformed(
        not eligibility.validate_evaluation_input(duplicate_dispositions).ok,
        "duplicate disposition rejected",
    )
    bad_family = replace(
        eligible_input.msm_gate_custody_companion,
        family_custody=eligible_input.msm_gate_custody_companion.family_custody[:-1],
    )
    bad_family_input = replace(
        eligible_input,
        evaluation_input_id="placeholder",
        msm_gate_custody_companion=bad_family,
    )
    bad_family_input = eligibility.with_expected_evaluation_input_id(
        bad_family_input
    )
    ledger.malformed(
        not eligibility.validate_evaluation_input(bad_family_input).ok,
        "missing gate family rejected",
    )
    tampered_outcome = replace(
        eligible_result,
        outcome=eligibility.SelectionEligibilityOutcome.NOT_ELIGIBLE,
    )
    tampered_outcome = eligibility.with_expected_result_identity(tampered_outcome)
    ledger.malformed(
        not eligibility.validate_result(
            tampered_outcome,
            evaluation_input=eligible_input,
        ).ok,
        "tampered outcome rejected",
    )
    authority_result = replace(
        eligible_result,
        selected_meaning_created=True,
    )
    authority_result = eligibility.with_expected_result_identity(authority_result)
    ledger.malformed(
        not eligibility.validate_result(
            authority_result,
            evaluation_input=eligible_input,
        ).ok,
        "selected meaning authority rejected",
    )
    for malformed in (None, "", object()):
        ledger.malformed(
            not eligibility.validate_evaluation_input(malformed).ok,
            f"malformed input rejected {type(malformed).__name__}",
        )
        ledger.malformed(
            not eligibility.validate_result(malformed).ok,
            f"malformed result rejected {type(malformed).__name__}",
        )

    print("AI.WEB SLICE 41C SELECTION ELIGIBILITY EVALUATION RUNTIME TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print("eligibility_outcomes=8")
    print("approved_selection_authority_profiles=1")
    print("exact_msm_v1_candidate_required=1")
    print("exact_slice40h_gate_custody_required=1")
    print("all_four_gate_family_results_required=1")
    print("exact_slice40g_composition_required=1")
    print("explicit_candidate_specific_support_required=1")
    print("unresolved_and_alternative_custody_preserved=1")
    print("eligible_for_selected_meaning_construction=1")
    print("held_pending_authority=1")
    print("materially_unresolved=1")
    print("clarification_dependent=1")
    print("unsupported=1")
    print("conflicted=1")
    print("indeterminate=1")
    print("not_eligible=1")
    print("candidate_ranked=0")
    print("selection_performed=0")
    print("selected_meaning_created=0")
    print("msm_v1_modified=0")
    print("confidence_probability_similarity_nearest_known=0")
    print("language_model_hidden_classifier=0")
    print("refusal_blocked_alternatives_erased=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL:", failure)
    if ledger.failures:
        print("AI.WEB SLICE 41C BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 41C BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
