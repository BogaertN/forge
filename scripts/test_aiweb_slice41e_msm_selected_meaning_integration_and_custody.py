#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 41E."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, fields, replace
import importlib
from pathlib import Path
import runpy
import sys

PACKAGE = (
    "aiweb_language_core_bootstrap.selected_meaning_runtime."
    "msm_selected_meaning_integration"
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


def _rich_chain(repository: Path):
    helpers41c = _namespace(
        repository,
        "test_aiweb_slice41c_selection_eligibility_evaluation_runtime.py",
    )
    helpers40g = _namespace(
        repository,
        "test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py",
    )
    helpers41d = _namespace(
        repository,
        "test_aiweb_slice41d_selected_meaning_construction_alternative_preservation.py",
    )

    msm = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest"
    )
    msm_validation = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest.validation"
    )
    msm_lifecycle = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest.lifecycle"
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
    candidate_integration = importlib.import_module(
        "aiweb_language_core_bootstrap.candidate_meaning_construction."
        "manifest_candidate_integration"
    )
    eligibility = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime.eligibility_evaluation"
    )
    selection_core = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime"
    )
    selection_governed = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime.governed_lifecycle"
    )
    construction = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime."
        "selected_meaning_construction"
    )

    bundles, family_results, _ = helpers40g["build_family_results"](
        repository,
        gate_core,
        gate_governed,
    )
    base_manifest, selected_candidate = helpers41c["_manifest_fixture"](msm)
    candidate_companion = helpers41c["_manifest_companion"](
        candidate_integration,
        selected_candidate,
    )
    composition_result = helpers41c["_composition_fixture"](
        composition,
        helpers40g,
        bundles,
        family_results,
        "eligible",
    )
    gate_result = custody.integrate_gate_results_into_manifest(
        base_manifest,
        selected_candidate.record_id,
        *family_results,
        composition_result,
    )

    source = gate_result.successor_manifest
    alternative_candidate = replace(
        selected_candidate,
        record_id="msm_candidate_record:alternative",
        communicative_act="report",
        concept_refs=("concept:alternative",),
        relation_refs=(),
        authority_sensitive_implications=("alternative_not_selected",),
    )
    existing_authority = msm.ExternalAuthorityReferenceRecord(
        record_id="authority:existing_nonselection",
        lineage_id=source.lineage_root.lineage_id,
        authority_kind=msm.ExternalAuthorityKind.SOURCE_CUSTODY,
        external_object_ref="source_custody:existing",
        semantic_relevance="existing_nonselection_custody",
    )
    source = replace(
        source,
        manifest_id="manifest:rich_preexisting_custody",
        candidate_meanings=(selected_candidate, alternative_candidate),
        external_authority_references=(existing_authority,),
    )
    existing_outcome = msm.NonSelectionOutcomeRecord(
        record_id="nonselection:existing_alternative",
        lineage_id=source.lineage_root.lineage_id,
        outcome_kind=msm.NonSelectionOutcomeKind.UNRESOLVED,
        candidate_refs=(alternative_candidate.record_id,),
        reasons=("preserved_existing_unresolved_alternative",),
        required_clarifications=(),
        external_authority_refs=(existing_authority.record_id,),
    )
    appended = msm_lifecycle.append_lifecycle_successor(
        source,
        trace_record_id="trace:existing_nonselection",
        from_record_ref=alternative_candidate.record_id,
        successor=existing_outcome,
        transition_kind=msm.SemanticTransitionKind.ANCESTRY,
        reason="existing_nonselection_outcome_preserved",
        authority_reference_ref=existing_authority.record_id,
    )
    source = replace(
        appended.manifest,
        manifest_id="manifest:rich_with_existing_nonselection",
    )
    assert msm_validation.validate_manifest(source).ok

    companion = custody.with_id(
        replace(
            gate_result.companion,
            companion_id="",
            successor_manifest_id=source.manifest_id,
        ),
        "slice40h_msm_gate_custody_companion",
        "companion_id",
    )
    gate_result = custody.with_id(
        replace(
            gate_result,
            result_id="",
            successor_manifest_id=source.manifest_id,
            successor_manifest=source,
            companion=companion,
            projected_outcome_count=len(source.non_selection_outcomes),
        ),
        "slice40h_msm_gate_integration_result",
        "result_id",
    )
    assert custody.validate_result(gate_result).ok

    governance_bundle = helpers41c["_governance_bundle"](
        selection_core,
        selection_governed,
        eligibility,
        custody,
        selected_candidate,
        candidate_companion,
        gate_result.companion,
        composition_result,
        "eligible",
    )
    evaluation_input = helpers41c["_evaluation_input"](
        eligibility,
        governance_bundle,
        selected_candidate,
        candidate_companion,
        gate_result.companion,
        composition_result,
        "eligible",
    )
    eligibility_result = eligibility.evaluate_selection_eligibility(evaluation_input)
    construction_input = helpers41d["_construction_input"](
        construction,
        evaluation_input,
        eligibility_result,
    )
    construction_package = construction.construct_selected_meaning_package(
        construction_input
    )
    return (
        msm,
        msm_validation,
        msm_lifecycle,
        custody,
        eligibility,
        construction,
        gate_result,
        construction_input,
        construction_package,
        selected_candidate,
        alternative_candidate,
        existing_outcome,
    )


def _integration_input(package, gate_result, construction_input, construction_package):
    value = package.MsmSelectedMeaningIntegrationInput(
        integration_input_id="placeholder",
        source_gate_integration_result=gate_result,
        selected_meaning_construction_input=construction_input,
        selected_meaning_package=construction_package,
        authority_profile=package.APPROVED_STRICT_PROFILE,
        semantic_transition_reason="slice41e:additive_selected_meaning_integration",
        version_refs=("slice40h:v1.0.0", "slice41d:v1.0.0", "slice41e:v1.0.0"),
        msm_schema_rewrite_requested=False,
        automatic_migration_requested=False,
        candidate_deletion_requested=False,
        non_selection_deletion_requested=False,
        gate_custody_deletion_requested=False,
        governed_result_requested=False,
        outward_meaning_requested=False,
        expression_link_requested=False,
        validation_link_requested=False,
        delivery_link_requested=False,
        truth_claim_requested=False,
        evidence_claim_requested=False,
        permission_requested=False,
        execution_requested=False,
        route_requested=False,
        tool_requested=False,
        action_requested=False,
        memory_access_requested=False,
        memory_write_requested=False,
        rendering_requested=False,
        delivery_requested=False,
        bootstrap_integration_requested=False,
    )
    return package.with_expected_input_id(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    package = importlib.import_module(PACKAGE)
    (
        msm,
        msm_validation,
        msm_lifecycle,
        custody,
        eligibility,
        construction,
        gate_result,
        construction_input,
        construction_package,
        selected_candidate,
        alternative_candidate,
        existing_outcome,
    ) = _rich_chain(repository)

    integration_input = _integration_input(
        package,
        gate_result,
        construction_input,
        construction_package,
    )
    source = gate_result.successor_manifest
    source_before = source

    ledger.check(custody.validate_result(gate_result).ok, "exact Slice 40H result valid")
    ledger.check(construction.validate_construction_input(construction_input).ok, "exact Slice 41D input valid")
    ledger.check(
        construction.validate_package(
            construction_package,
            construction_input=construction_input,
        ).ok,
        "exact Slice 41D package valid",
    )
    ledger.check(package.validate_authority_profile(package.APPROVED_STRICT_PROFILE).ok, "strict profile valid")
    ledger.check(package.validate_integration_input(integration_input).ok, "integration input valid")

    result = package.integrate_selected_meaning_into_manifest(integration_input)
    repeated = package.integrate_selected_meaning_into_manifest(integration_input)
    ledger.check(result == repeated, "deterministic repeated result")
    ledger.check(result.result_id == repeated.result_id, "deterministic result identity")
    ledger.check(result.canonical_digest == repeated.canonical_digest, "deterministic result digest")
    ledger.check(source == source_before, "source manifest remained immutable")
    ledger.check(package.validate_integration_result(result, integration_input=integration_input).ok, "result validates")
    ledger.check(msm_validation.validate_manifest(result.successor_manifest).ok, "complete successor manifest validates")

    successor = result.successor_manifest
    selected = result.integrated_selected_meaning_record
    dormant = construction_package.selected_meaning_record
    authority = result.authority_reference_record
    trace = result.semantic_transition_trace

    ledger.check(len(source.candidate_meanings) == 2, "source has two candidate meanings")
    ledger.check(len(source.non_selection_outcomes) == 1, "source has existing non-selection outcome")
    ledger.check(successor.candidate_meanings == source.candidate_meanings, "all candidates retained exactly")
    ledger.check(successor.non_selection_outcomes == source.non_selection_outcomes, "all non-selection outcomes retained exactly")
    ledger.check(successor.selected_governed_meanings == (selected,), "one selected meaning appended")
    ledger.check(successor.external_authority_references == (*source.external_authority_references, authority), "authority reference appended only")
    ledger.check(successor.semantic_transition_traces == (*source.semantic_transition_traces, trace), "semantic transition trace appended only")
    ledger.check(selected.selected_candidate_ref == selected_candidate.record_id, "exact selected candidate reference")
    ledger.check(selected.selection_authority_ref == construction_package.selection_receipt.receipt_id, "exact Slice 41D receipt authority")
    ledger.check(authority.external_object_ref == construction_package.selection_receipt.receipt_id, "authority record binds Slice 41D receipt")
    ledger.check(trace.from_record_ref == selected_candidate.record_id, "transition begins at exact candidate")
    ledger.check(trace.to_record_ref == selected.record_id, "transition ends at integrated selected record")
    ledger.check(trace.authority_reference_ref == authority.record_id, "transition binds authority record")
    ledger.check(trace.transition_kind is msm.SemanticTransitionKind.ANCESTRY, "lawful ancestry transition")
    ledger.check(trace.from_state is msm.SemanticLifecycleState.CANDIDATE_MEANING, "candidate source state")
    ledger.check(trace.to_state is msm.SemanticLifecycleState.SELECTED_GOVERNED_MEANING, "selected target state")

    for name in (
        "lineage_id",
        "selected_candidate_ref",
        "communicative_act",
        "concept_refs",
        "relation_refs",
        "meaning_modifiers",
        "inherited_limitations",
        "authority_sensitive_distinctions",
        "preservation_classes",
    ):
        ledger.check(getattr(selected, name) == getattr(dormant, name), f"dormant content preserved: {name}")
    ledger.check(selected.communicative_act == selected_candidate.communicative_act, "candidate act copied exactly")
    ledger.check(selected.concept_refs == selected_candidate.concept_refs, "candidate concepts copied exactly")
    ledger.check(selected.relation_refs == selected_candidate.relation_refs, "candidate relations copied exactly")
    ledger.check(selected.meaning_modifiers == selected_candidate.meaning_modifiers, "candidate modifiers copied exactly")
    ledger.check(selected.authority_sensitive_distinctions == selected_candidate.authority_sensitive_implications, "authority distinctions copied exactly")
    ledger.check(selected.preservation_classes == selected_candidate.preservation_classes, "preservation classes copied exactly")
    ledger.check(selected.inherited_limitations == construction_package.inherited_limitation_refs, "limitations copied exactly")

    companion = result.companion
    receipt = result.receipt
    ledger.check(companion.slice40h_custody_companion == gate_result.companion, "exact Slice 40H companion retained")
    ledger.check(companion.dormant_selected_meaning_ref == dormant.record_id, "dormant 41D record retained by reference")
    ledger.check(companion.integrated_selected_meaning_ref == selected.record_id, "integrated record retained by reference")
    ledger.check(companion.selection_receipt_ref == construction_package.selection_receipt.receipt_id, "selection receipt retained")
    ledger.check(companion.candidate_refs_before == companion.candidate_refs_after, "candidate custody before equals after")
    ledger.check(companion.non_selection_outcome_refs_before == companion.non_selection_outcome_refs_after, "non-selection custody before equals after")
    ledger.check(alternative_candidate.record_id in companion.candidate_refs_after, "non-selected candidate preserved")
    ledger.check(existing_outcome.record_id in companion.non_selection_outcome_refs_after, "existing non-selection outcome preserved")
    ledger.check(companion.candidate_ancestry_preserved, "candidate ancestry preserved")
    ledger.check(companion.gate_ancestry_preserved, "gate ancestry preserved")
    ledger.check(companion.slice40h_companion_retained, "Slice 40H custody retained")
    ledger.check(receipt.source_manifest_sha256 != receipt.successor_manifest_sha256, "successor hash differs lawfully")
    ledger.check(receipt.candidate_count_before == receipt.candidate_count_after == 2, "candidate counts retained")
    ledger.check(receipt.non_selection_count_before == receipt.non_selection_count_after == 1, "non-selection counts retained")
    ledger.check(receipt.selected_count_before == 0 and receipt.selected_count_after == 1, "selected count increment exact")

    for name in package.SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS:
        ledger.check(getattr(successor, name) == (), f"downstream section empty: {name}")

    for name in (
        "msm_schema_modified",
        "automatic_migration_performed",
        "candidate_deleted",
        "non_selection_outcome_deleted",
        "gate_custody_deleted",
        "governed_result_reference_created",
        "governed_outward_meaning_created",
        "expression_link_created",
        "validation_link_created",
        "delivery_link_created",
        "truth_determined",
        "evidence_validated",
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
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
        "bootstrap_integration_enabled",
    ):
        ledger.check(getattr(result, name) is False, f"prohibited authority remains false: {name}")

    try:
        result.selected_meaning_integrated = False
    except FrozenInstanceError:
        immutable = True
    else:
        immutable = False
    ledger.check(immutable, "result records immutable")
    ledger.check(all(item.default is not None or item.default_factory is not None for item in fields(type(result))), "result dataclass inspectable")

    # Fail-closed input mutations.
    ledger.malformed(
        not package.validate_integration_input(replace(integration_input, integration_input_id="bad")).ok,
        "wrong input identity rejected",
    )
    ledger.malformed(
        not package.validate_integration_input(replace(integration_input, semantic_transition_reason=" padded ")).ok,
        "noncanonical reason rejected",
    )
    ledger.malformed(
        not package.validate_integration_input(replace(integration_input, version_refs=())).ok,
        "missing versions rejected",
    )
    for field_name in (
        "msm_schema_rewrite_requested",
        "automatic_migration_requested",
        "candidate_deletion_requested",
        "non_selection_deletion_requested",
        "gate_custody_deletion_requested",
        "governed_result_requested",
        "outward_meaning_requested",
        "expression_link_requested",
        "validation_link_requested",
        "delivery_link_requested",
        "truth_claim_requested",
        "evidence_claim_requested",
        "permission_requested",
        "execution_requested",
        "route_requested",
        "tool_requested",
        "action_requested",
        "memory_access_requested",
        "memory_write_requested",
        "rendering_requested",
        "delivery_requested",
        "bootstrap_integration_requested",
    ):
        ledger.malformed(
            not package.validate_integration_input(replace(integration_input, **{field_name: True})).ok,
            f"prohibited input request rejected: {field_name}",
        )
    ledger.malformed(
        not package.validate_integration_input(replace(integration_input, source_gate_integration_result="bad")).ok,
        "wrong Slice 40H type rejected without exception",
    )
    ledger.malformed(
        not package.validate_integration_input(replace(integration_input, selected_meaning_construction_input="bad")).ok,
        "wrong Slice 41D input type rejected without exception",
    )
    ledger.malformed(
        not package.validate_integration_input(replace(integration_input, selected_meaning_package="bad")).ok,
        "wrong Slice 41D package type rejected without exception",
    )
    bad_profile = package.with_expected_profile_id(
        replace(package.APPROVED_STRICT_PROFILE, profile_id="placeholder", msm_schema_rewrite_allowed=True)
    )
    ledger.malformed(
        not package.validate_integration_input(replace(integration_input, authority_profile=bad_profile)).ok,
        "authority-expanding profile rejected",
    )

    # Fail-closed result and custody mutations.
    ledger.malformed(
        not package.validate_integration_result(replace(result, result_id="bad"), integration_input=integration_input).ok,
        "wrong result ID rejected",
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, canonical_digest="0" * 64), integration_input=integration_input).ok,
        "wrong result digest rejected",
    )
    enriched_selected = replace(
        selected,
        record_id="placeholder",
        concept_refs=(*selected.concept_refs, "concept:invented"),
    )
    enriched_selected = replace(
        enriched_selected,
        record_id=package.expected_selected_record_id(enriched_selected),
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, integrated_selected_meaning_record=enriched_selected), integration_input=integration_input).ok,
        "reidentified semantic enrichment rejected",
    )
    deleted_selected = replace(selected, record_id="placeholder", concept_refs=())
    deleted_selected = replace(
        deleted_selected,
        record_id=package.expected_selected_record_id(deleted_selected),
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, integrated_selected_meaning_record=deleted_selected), integration_input=integration_input).ok,
        "reidentified semantic deletion rejected",
    )
    wrong_authority_selected = replace(
        selected,
        record_id="placeholder",
        selection_authority_ref=construction_package.eligibility_result_ref,
    )
    wrong_authority_selected = replace(
        wrong_authority_selected,
        record_id=package.expected_selected_record_id(wrong_authority_selected),
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, integrated_selected_meaning_record=wrong_authority_selected), integration_input=integration_input).ok,
        "wrong selection authority rejected",
    )
    tampered_authority = replace(authority, external_object_ref="receipt:tampered")
    tampered_authority = replace(tampered_authority, record_id=package.expected_authority_reference_id(tampered_authority))
    ledger.malformed(
        not package.validate_integration_result(replace(result, authority_reference_record=tampered_authority), integration_input=integration_input).ok,
        "reidentified authority receipt tampering rejected",
    )
    tampered_trace = replace(trace, reason="trace:tampered")
    tampered_trace = replace(tampered_trace, record_id=package.expected_transition_trace_id(tampered_trace))
    ledger.malformed(
        not package.validate_integration_result(replace(result, semantic_transition_trace=tampered_trace), integration_input=integration_input).ok,
        "reidentified transition tampering rejected",
    )
    ledger.malformed(
        not package.validate_integration_result(
            replace(result, successor_manifest=replace(successor, candidate_meanings=(selected_candidate,))),
            integration_input=integration_input,
        ).ok,
        "candidate deletion from successor rejected",
    )
    ledger.malformed(
        not package.validate_integration_result(
            replace(result, successor_manifest=replace(successor, non_selection_outcomes=())),
            integration_input=integration_input,
        ).ok,
        "non-selection deletion from successor rejected",
    )
    ledger.malformed(
        not package.validate_integration_result(
            replace(result, successor_manifest=replace(successor, governed_outward_meanings=(object(),))),
            integration_input=integration_input,
        ).ok,
        "outward section population rejected",
    )
    altered_40h = replace(gate_result.companion, composition_result_id="composition:tampered")
    tampered_companion = package.with_expected_companion_id(
        replace(companion, companion_id="placeholder", slice40h_custody_companion=altered_40h)
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, companion=tampered_companion), integration_input=integration_input).ok,
        "reidentified Slice 40H custody tampering rejected",
    )
    tampered_receipt = package.with_expected_receipt_id(
        replace(receipt, receipt_id="placeholder", candidate_count_after=1)
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, receipt=tampered_receipt), integration_input=integration_input).ok,
        "reidentified receipt count tampering rejected",
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, governed_outward_meaning_created=True), integration_input=integration_input).ok,
        "outward authority flag rejected",
    )
    ledger.malformed(
        not package.validate_integration_result(replace(result, msm_schema_modified=True), integration_input=integration_input).ok,
        "schema rewrite claim rejected",
    )
    ledger.malformed(
        not package.validate_integration_result("bad", integration_input=integration_input).ok,
        "wrong result type rejected",
    )
    ledger.malformed(
        not package.validate_integration_result(result, integration_input=None).ok,
        "missing input rejected",
    )

    print("AI.WEB SLICE 41E MSM-V1 SELECTED MEANING INTEGRATION AND CUSTODY TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print("source_candidate_meanings=2")
    print("source_non_selection_outcomes=1")
    print("successor_selected_meanings=1")
    print("exact_slice40h_result_required=1")
    print("exact_slice40h_custody_companion_required=1")
    print("exact_slice41d_input_and_package_required=1")
    print("exact_selected_candidate_reference=1")
    print("exact_selection_receipt_authority=1")
    print("immutable_msm_v1_successor=1")
    print("candidate_and_gate_ancestry_preserved=1")
    print("all_candidate_meanings_retained=1")
    print("all_non_selection_outcomes_retained=1")
    print("slice40h_custody_companion_retained=1")
    print("lawful_semantic_transition_trace=1")
    print("complete_successor_manifest_validated=1")
    print("msm_v1_schema_modified=0")
    print("automatic_migration_performed=0")
    print("candidate_or_non_selection_deleted=0")
    print("governed_result_or_outward_meaning_created=0")
    print("expression_validation_delivery_links=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print("filesystem_network_external_resource=0")
    print("language_model_embedding_vector_rag_similarity=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures:
        print("AI.WEB SLICE 41E BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 41E BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
