#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 41D."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, fields, replace
import importlib
from pathlib import Path
import runpy
import sys

PACKAGE = (
    "aiweb_language_core_bootstrap.selected_meaning_runtime."
    "selected_meaning_construction"
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


def _eligibility_fixture(repository: Path, case_name: str):
    eligibility_helpers = _namespace(
        repository,
        "test_aiweb_slice41c_selection_eligibility_evaluation_runtime.py",
    )
    gate_helpers = _namespace(
        repository,
        "test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py",
    )
    eligibility = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime.eligibility_evaluation"
    )
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
    integration = importlib.import_module(
        "aiweb_language_core_bootstrap.candidate_meaning_construction."
        "manifest_candidate_integration"
    )

    bundles, family_results, _ = gate_helpers["build_family_results"](
        repository,
        gate_core,
        gate_governed,
    )
    manifest, candidate = eligibility_helpers["_manifest_fixture"](msm)
    companion = eligibility_helpers["_manifest_companion"](integration, candidate)
    composition_result = eligibility_helpers["_composition_fixture"](
        composition,
        gate_helpers,
        bundles,
        family_results,
        case_name,
    )
    gate_integration = custody.integrate_gate_results_into_manifest(
        manifest,
        candidate.record_id,
        *family_results,
        composition_result,
    )
    bundle = eligibility_helpers["_governance_bundle"](
        core,
        governed,
        eligibility,
        custody,
        candidate,
        companion,
        gate_integration.companion,
        composition_result,
        case_name,
    )
    evaluation_input = eligibility_helpers["_evaluation_input"](
        eligibility,
        bundle,
        candidate,
        companion,
        gate_integration.companion,
        composition_result,
        case_name,
    )
    result = eligibility.evaluate_selection_eligibility(evaluation_input)
    return eligibility, manifest, evaluation_input, result


def _construction_input(package, evaluation_input, eligibility_result):
    value = package.SelectedMeaningConstructionInput(
        construction_input_id="placeholder",
        eligibility_evaluation_input=evaluation_input,
        eligibility_result=eligibility_result,
        authority_profile=package.APPROVED_STRICT_PROFILE,
        selection_reason_refs=(
            "slice41c:eligible_for_selected_meaning_construction",
            "candidate_specific_support:exact",
        ),
        ambiguity_ancestry_refs=("ambiguity_ancestry:preserved_prior_branch",),
        clarification_ancestry_refs=("clarification_ancestry:preserved_prior_exchange",),
        trace_refs=("slice41d:input_trace",),
        provenance_refs=("slice41d:input_provenance",),
        version_refs=("slice41d:v1.0.0",),
        candidate_ranking_used=False,
        confidence_scoring_used=False,
        probability_ranking_used=False,
        semantic_similarity_used=False,
        nearest_known_substitution_used=False,
        language_model_used=False,
        hidden_classifier_used=False,
        only_candidate_automatic_selection_used=False,
        first_candidate_automatic_selection_used=False,
        safest_candidate_automatic_selection_used=False,
        alternative_erasure_requested=False,
        unresolved_alternative_erasure_requested=False,
        ambiguity_ancestry_erasure_requested=False,
        clarification_ancestry_erasure_requested=False,
        refusal_relevance_erasure_requested=False,
        blocked_progression_erasure_requested=False,
        msm_v1_mutation_requested=False,
        outward_meaning_requested=False,
        downstream_authority_requested=False,
    )
    return package.with_expected_construction_input_id(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    package = importlib.import_module(PACKAGE)
    eligibility, manifest, evaluation_input, eligibility_result = _eligibility_fixture(
        repository,
        "eligible",
    )
    ledger.check(
        eligibility_result.outcome
        is eligibility.SelectionEligibilityOutcome.ELIGIBLE_FOR_SELECTED_MEANING_CONSTRUCTION,
        "successful 41C eligibility fixture",
    )
    ledger.check(
        eligibility.validate_evaluation_input(evaluation_input).ok,
        "41C input valid",
    )
    ledger.check(
        eligibility.validate_result(
            eligibility_result,
            evaluation_input=evaluation_input,
        ).ok,
        "41C result valid",
    )

    original_manifest = manifest
    construction_input = _construction_input(
        package,
        evaluation_input,
        eligibility_result,
    )
    input_report = package.validate_construction_input(construction_input)
    ledger.check(input_report.ok, f"41D input valid: {input_report.issues}")
    result = package.construct_selected_meaning_package(construction_input)
    repeat = package.construct_selected_meaning_package(construction_input)
    ledger.check(result == repeat, "deterministic package repeat")
    ledger.check(result.package_id == repeat.package_id, "deterministic package ID")
    ledger.check(
        package.validate_package(result, construction_input=construction_input).ok,
        "package validates",
    )

    candidate = construction_input.selected_candidate_record
    selected = result.selected_meaning_record
    ledger.check(result.selected_candidate_record == candidate, "exact candidate record preserved")
    ledger.check(
        result.selected_candidate_companion == construction_input.selected_candidate_companion,
        "exact candidate companion preserved",
    )
    ledger.check(selected.selected_candidate_ref == candidate.record_id, "candidate identity exact")
    ledger.check(selected.lineage_id == candidate.lineage_id, "lineage exact")
    ledger.check(selected.communicative_act == candidate.communicative_act, "communicative act exact")
    ledger.check(selected.concept_refs == candidate.concept_refs, "concept refs exact")
    ledger.check(selected.relation_refs == candidate.relation_refs, "relation refs exact")
    ledger.check(selected.meaning_modifiers == candidate.meaning_modifiers, "modifiers exact")
    ledger.check(selected.preservation_classes == candidate.preservation_classes, "preservation classes exact")
    ledger.check(
        selected.authority_sensitive_distinctions
        == candidate.authority_sensitive_implications,
        "authority-sensitive distinctions exact",
    )
    ledger.check(bool(selected.inherited_limitations), "limitations inherited")
    ledger.check(result.content_proof.semantic_content_exact, "semantic proof exact")
    ledger.check(
        result.content_proof.candidate_semantic_digest
        == result.content_proof.selected_semantic_digest,
        "semantic digests equal",
    )
    ledger.check(not result.content_proof.semantic_enrichment_detected, "no enrichment")
    ledger.check(not result.content_proof.semantic_deletion_detected, "no deletion")
    ledger.check(not result.content_proof.added_concept_refs, "no added concepts")
    ledger.check(not result.content_proof.removed_concept_refs, "no removed concepts")
    ledger.check(not result.content_proof.added_relation_refs, "no added relations")
    ledger.check(not result.content_proof.removed_relation_refs, "no removed relations")
    ledger.check(not result.content_proof.added_meaning_modifiers, "no added modifiers")
    ledger.check(not result.content_proof.removed_meaning_modifiers, "no removed modifiers")
    ledger.check(not result.content_proof.added_preservation_classes, "no added preservation classes")
    ledger.check(not result.content_proof.removed_preservation_classes, "no removed preservation classes")

    expected_non_selected = evaluation_input.alternative_candidate_custody.non_selected_candidate_refs
    ledger.check(bool(expected_non_selected), "fixture contains non-selected candidate")
    ledger.check(
        tuple(item.alternative_candidate_ref for item in result.preserved_alternatives)
        == expected_non_selected,
        "all non-selected candidates preserved by exact reference",
    )
    for alternative in result.preserved_alternatives:
        ledger.check(alternative.preserved_by_exact_reference, "alternative exact reference")
        ledger.check(not alternative.selected, "alternative not selected")
        ledger.check(not alternative.deleted, "alternative not deleted")
        ledger.check(not alternative.ranked, "alternative not ranked")
        ledger.check(not alternative.confidence_scored, "alternative not scored")
    ledger.check(result.unresolved_alternatives_preserved_separately, "unresolved alternatives separate")
    ledger.check(result.ambiguity_ancestry_preserved, "ambiguity ancestry preserved")
    ledger.check(result.clarification_ancestry_preserved, "clarification ancestry preserved")
    ledger.check("ambiguity_ancestry:preserved_prior_branch" in result.ambiguity_ancestry_refs, "explicit ambiguity ancestry retained")
    ledger.check("clarification_ancestry:preserved_prior_exchange" in result.clarification_ancestry_refs, "explicit clarification ancestry retained")
    ledger.check(result.inherited_limitations_preserved, "limitations preservation flag")
    ledger.check(result.blocked_consequences_preserved, "blocked consequences preservation flag")
    ledger.check(result.refusal_relevance_preserved, "refusal preservation flag")
    ledger.check(result.selection_trace.deterministic, "deterministic trace")
    ledger.check(result.selection_receipt.deterministic, "deterministic receipt")
    ledger.check(
        result.selection_receipt.trace_ref == result.selection_trace.trace_id,
        "receipt binds trace",
    )
    ledger.check(
        result.selection_trace.content_proof_ref == result.content_proof.proof_id,
        "trace binds proof",
    )
    ledger.check(result.decision_record.decision_performed, "selection decision performed")
    ledger.check(not result.decision_record.candidate_ranked, "selection did not rank")
    ledger.check(not result.decision_record.only_candidate_claimed, "no only-candidate claim")
    ledger.check(
        not result.decision_record.historical_candidate_exhaustiveness_claimed,
        "no historical candidate exhaustiveness claim",
    )

    ledger.check(manifest == original_manifest, "input MSM object unchanged")
    ledger.check(not manifest.selected_governed_meanings, "MSM selected section remains empty")
    ledger.check(result.selected_meaning_created, "selected meaning constructed")
    ledger.check(not result.msm_v1_modified, "MSM-v1 not modified")
    ledger.check(not result.governed_outward_meaning_created, "no outward meaning")
    ledger.check(not result.alternatives_erased, "no alternatives erased")
    for name in (
        "candidate_ranked",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "route_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed",
        "memory_written",
        "rendered",
        "delivered",
        "external_resource_loaded",
        "language_model_used",
        "hidden_classifier_used",
        "confidence_scoring_used",
        "probability_ranking_used",
        "semantic_similarity_used",
        "nearest_known_substitution_used",
        "bootstrap_integration_enabled",
    ):
        ledger.check(getattr(result, name) is False, f"package {name} false")

    ledger.check(
        result.package_id == package.expected_package_id(result),
        "package ID exact",
    )
    ledger.check(
        result.package_digest == package.expected_package_digest(result),
        "package digest exact",
    )
    ledger.check(
        selected.record_id == package.expected_selected_meaning_record_id(selected),
        "selected meaning ID exact",
    )
    for record_type in package.SUPPORTED_RECORD_TYPES:
        ledger.check(
            tuple(item.name for item in fields(record_type))
            == package.canonical_field_order(record_type),
            f"canonical field order {record_type.__name__}",
        )

    try:
        result.package_id = "changed"
        immutable = False
    except FrozenInstanceError:
        immutable = True
    ledger.check(immutable, "package immutable")

    _, _, held_input, held_result = _eligibility_fixture(repository, "held")
    bad_noneligible = _construction_input(package, held_input, held_result)
    ledger.malformed(
        not package.validate_construction_input(bad_noneligible).ok,
        "non-eligible 41C result rejected",
    )
    ledger.malformed(
        not package.validate_construction_input(
            replace(construction_input, construction_input_id="wrong")
        ).ok,
        "noncanonical input ID rejected",
    )
    ledger.malformed(
        not package.validate_construction_input(
            package.with_expected_construction_input_id(
                replace(
                    construction_input,
                    construction_input_id="placeholder",
                    semantic_similarity_used=True,
                )
            )
        ).ok,
        "semantic similarity rejected",
    )
    ledger.malformed(
        not package.validate_construction_input(
            package.with_expected_construction_input_id(
                replace(
                    construction_input,
                    construction_input_id="placeholder",
                    alternative_erasure_requested=True,
                )
            )
        ).ok,
        "alternative erasure request rejected",
    )
    ledger.malformed(
        not package.validate_construction_input(
            package.with_expected_construction_input_id(
                replace(
                    construction_input,
                    construction_input_id="placeholder",
                    language_model_used=True,
                )
            )
        ).ok,
        "language model use rejected",
    )

    enriched_selected = replace(
        selected,
        concept_refs=selected.concept_refs + ("concept:invented",),
    )
    enriched_package = replace(result, selected_meaning_record=enriched_selected)
    ledger.malformed(
        not package.validate_package(
            enriched_package,
            construction_input=construction_input,
        ).ok,
        "semantic enrichment rejected",
    )
    deleted_selected = replace(selected, concept_refs=())
    deleted_package = replace(result, selected_meaning_record=deleted_selected)
    ledger.malformed(
        not package.validate_package(
            deleted_package,
            construction_input=construction_input,
        ).ok,
        "semantic deletion rejected",
    )
    missing_alternative = replace(result, preserved_alternatives=())
    ledger.malformed(
        not package.validate_package(
            missing_alternative,
            construction_input=construction_input,
        ).ok,
        "missing non-selected candidate rejected",
    )
    erased_alternative = replace(
        result.preserved_alternatives[0],
        deleted=True,
    )
    erased_package = replace(
        result,
        preserved_alternatives=(erased_alternative,),
    )
    ledger.malformed(
        not package.validate_package(
            erased_package,
            construction_input=construction_input,
        ).ok,
        "deleted alternative rejected",
    )
    wrong_lineage = replace(selected, lineage_id="lineage:wrong")
    ledger.malformed(
        not package.validate_package(
            replace(result, selected_meaning_record=wrong_lineage),
            construction_input=construction_input,
        ).ok,
        "lineage change rejected",
    )
    wrong_authority = replace(selected, selection_authority_ref="eligibility:wrong")
    ledger.malformed(
        not package.validate_package(
            replace(result, selected_meaning_record=wrong_authority),
            construction_input=construction_input,
        ).ok,
        "selection authority change rejected",
    )
    ledger.malformed(
        not package.validate_package(
            replace(result, package_digest="0" * 64),
            construction_input=construction_input,
        ).ok,
        "package digest tampering rejected",
    )
    ledger.malformed(
        not package.validate_package(
            replace(result, selection_trace=replace(result.selection_trace, trace_id="trace:wrong")),
            construction_input=construction_input,
        ).ok,
        "trace tampering rejected",
    )
    ledger.malformed(
        not package.validate_package(
            replace(result, selection_receipt=replace(result.selection_receipt, receipt_id="receipt:wrong")),
            construction_input=construction_input,
        ).ok,
        "receipt tampering rejected",
    )
    ledger.malformed(
        not package.validate_package(
            replace(result, msm_v1_modified=True),
            construction_input=construction_input,
        ).ok,
        "MSM mutation claim rejected",
    )
    ledger.malformed(
        not package.validate_package(
            replace(result, candidate_ranked=True),
            construction_input=construction_input,
        ).ok,
        "candidate ranking claim rejected",
    )

    ledger.malformed(
        not package.validate_package(
            package.with_expected_package_identity(
                replace(
                    result,
                    selection_trace=package.with_expected_trace_id(
                        replace(
                            result.selection_trace,
                            trace_id="placeholder",
                            gate_custody_ref="gate-custody:tampered",
                        )
                    ),
                )
            ),
            construction_input=construction_input,
        ).ok,
        "reidentified trace custody tampering rejected",
    )
    ledger.malformed(
        not package.validate_package(
            package.with_expected_package_identity(
                replace(
                    result,
                    selection_receipt=package.with_expected_receipt_id(
                        replace(
                            result.selection_receipt,
                            receipt_id="placeholder",
                            required_law_refs=("law:tampered",),
                        )
                    ),
                )
            ),
            construction_input=construction_input,
        ).ok,
        "reidentified receipt custody tampering rejected",
    )
    ledger.malformed(
        not package.validate_package(
            package.with_expected_package_identity(
                replace(
                    result,
                    decision_record=package.with_expected_decision_id(
                        replace(
                            result.decision_record,
                            decision_id="placeholder",
                            selection_reason_refs=("reason:tampered",),
                        )
                    ),
                )
            ),
            construction_input=construction_input,
        ).ok,
        "reidentified decision custody tampering rejected",
    )
    reidentified_alternative = package.with_expected_preservation_id(
        replace(
            result.preserved_alternatives[0],
            preservation_id="placeholder",
            ambiguity_ancestry_refs=("ambiguity:tampered",),
        )
    )
    ledger.malformed(
        not package.validate_package(
            package.with_expected_package_identity(
                replace(result, preserved_alternatives=(reidentified_alternative,))
            ),
            construction_input=construction_input,
        ).ok,
        "reidentified alternative custody tampering rejected",
    )

    print("AI.WEB SLICE 41D SELECTED MEANING CONSTRUCTION AND ALTERNATIVE PRESERVATION TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print("selected_meaning_packages=1")
    print("successful_slice41c_eligibility_required=1")
    print("exact_selected_candidate_identity_and_lineage=1")
    print("exact_semantic_content_copy=1")
    print("authority_sensitive_distinctions_preserved=1")
    print("inherited_limitations_and_blocked_consequences=1")
    print("every_non_selected_candidate_preserved=1")
    print("unresolved_alternatives_preserved_separately=1")
    print("ambiguity_and_clarification_ancestry_preserved=1")
    print("deterministic_selection_trace_and_receipt=1")
    print("selected_candidate_only_candidate_claim=0")
    print("semantic_enrichment=0")
    print("semantic_deletion=0")
    print("alternatives_deleted=0")
    print("candidate_ranked=0")
    print("msm_v1_modified=0")
    print("governed_outward_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print("language_model_hidden_classifier_similarity=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures:
        print("AI.WEB SLICE 41D BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 41D BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
