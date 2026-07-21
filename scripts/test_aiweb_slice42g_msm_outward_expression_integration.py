#!/usr/bin/env python3
"""Visible behavior test for AI.Web Slice 42G."""

from __future__ import annotations

from dataclasses import replace
import importlib
import runpy
import sys
from pathlib import Path
from typing import Any


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)


def load_script(path: Path) -> dict[str, Any]:
    return runpy.run_path(str(path))


def build_slice42g_input(repo: Path) -> tuple[Any, Any]:
    test42f = load_script(
        repo / "scripts/test_aiweb_slice42f_deterministic_surface_realization.py"
    )
    realization, realization_input = test42f["build_slice42f_input"](repo)
    realization_result = realization.realize_surface_expression(realization_input)
    realization.assert_valid_surface_realization_result(
        realization_result,
        realization_input=realization_input,
    )

    closeout = (
        realization_input.plan_input.projection_input
        .expression_eligibility_evaluation_input
        .selected_meaning_closeout_result
    )
    selected_input = closeout.integration_input
    selected_result = closeout.integration_result
    assert selected_input is not None and selected_result is not None

    integration = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "msm_outward_expression_integration"
    )
    value = integration.with_expected_input_id(
        integration.MsmOutwardExpressionIntegrationInput(
            integration_input_id="pending",
            source_selected_meaning_integration_input=selected_input,
            source_selected_meaning_integration_result=selected_result,
            surface_realization_input=realization_input,
            surface_realization_result=realization_result,
            authority_profile=integration.APPROVED_STRICT_PROFILE,
            outward_transition_reason=(
                "slice42g:additive-selected-to-governed-outward-meaning"
            ),
            expression_transition_reason=(
                "slice42g:additive-governed-outward-meaning-to-expression-link"
            ),
            version_refs=(
                selected_result.schema_version,
                realization_result.schema_version,
                integration.SLICE42G_SCHEMA_VERSION,
            ),
            msm_schema_rewrite_requested=False,
            automatic_migration_requested=False,
            source_manifest_mutation_requested=False,
            candidate_deletion_requested=False,
            non_selection_deletion_requested=False,
            selected_meaning_rewrite_requested=False,
            alternative_deletion_requested=False,
            unresolved_resolution_requested=False,
            governed_result_creation_requested=False,
            validation_link_creation_requested=False,
            delivery_link_creation_requested=False,
            expression_candidate_rewrite_requested=False,
            claim_strengthening_requested=False,
            certainty_upgrade_requested=False,
            evidence_status_upgrade_requested=False,
            caveat_omission_requested=False,
            refusal_softening_requested=False,
            ambiguity_erasure_requested=False,
            unsupported_state_erasure_requested=False,
            echo_validation_requested=False,
            delivery_requested=False,
            truth_evidence_permission_execution_requested=False,
            route_tool_action_memory_filesystem_network_requested=False,
            external_resource_or_model_authority_requested=False,
            bootstrap_integration_requested=False,
            gp014_supersession_requested=False,
        )
    )
    return integration, value


def altered_tuple(values: tuple[Any, ...], fabricated: Any) -> tuple[Any, ...]:
    if values:
        return values[1:]
    return (fabricated,)


def main() -> int:
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sys.path.insert(0, str(repo))
    integration, value = build_slice42g_input(repo)
    ledger = Ledger()

    ledger.check(
        integration.validate_integration_input(value).ok,
        "exact integration input validates",
    )
    result = integration.integrate_outward_meaning_and_expression_link(value)
    ledger.check(
        integration.validate_integration_result(
            result,
            integration_input=value,
        ).ok,
        "exact integration result validates",
    )
    repeated = integration.integrate_outward_meaning_and_expression_link(value)
    ledger.check(result == repeated, "deterministic repeated integration")

    source = result.source_manifest
    successor = result.successor_manifest
    candidate = value.expression_candidate
    selected = (
        value.source_selected_meaning_integration_result
        .integrated_selected_meaning_record
    )
    authority = result.external_authority_reference_record
    outward = result.governed_outward_meaning_record
    expression = result.expression_link_record
    selected_trace = result.selected_to_outward_trace
    expression_trace = result.outward_to_expression_trace
    companion = result.companion
    receipt = result.receipt

    ledger.check(source is value.source_manifest, "exact source manifest custody")
    ledger.check(successor != source, "immutable successor created")
    ledger.check(successor.manifest_id != source.manifest_id, "new manifest identity")
    ledger.check(successor.lineage_root == source.lineage_root, "lineage root preserved")
    ledger.check(successor.candidate_meanings == source.candidate_meanings, "candidate meanings retained")
    ledger.check(successor.non_selection_outcomes == source.non_selection_outcomes, "non-selection outcomes retained")
    ledger.check(successor.selected_governed_meanings == source.selected_governed_meanings, "selected meanings retained")
    ledger.check(successor.governed_result_references == source.governed_result_references, "governed-result references unchanged")
    ledger.check(successor.validation_links == source.validation_links, "validation links unchanged")
    ledger.check(successor.delivery_or_containment_links == source.delivery_or_containment_links, "delivery links unchanged")
    ledger.check(len(successor.governed_outward_meanings) == len(source.governed_outward_meanings) + 1, "one outward meaning added")
    ledger.check(successor.governed_outward_meanings[-1] == outward, "exact outward meaning appended")
    ledger.check(len(successor.expression_links) == len(source.expression_links) + 1, "one expression link added")
    ledger.check(successor.expression_links[-1] == expression, "exact expression link appended")
    ledger.check(len(successor.external_authority_references) == len(source.external_authority_references) + 1, "one authority reference added")
    ledger.check(successor.external_authority_references[-1] == authority, "exact authority reference appended")
    ledger.check(len(successor.semantic_transition_traces) == len(source.semantic_transition_traces) + 2, "two lifecycle traces added")
    ledger.check(successor.semantic_transition_traces[-2:] == (selected_trace, expression_trace), "exact lifecycle traces appended")

    ledger.check(authority.external_object_ref == candidate.expression_candidate_id, "authority binds exact candidate")
    ledger.check(outward.prior_selected_meaning_ref == selected.record_id, "outward meaning binds exact selected meaning")
    ledger.check(outward.outward_basis_refs == (selected.record_id, authority.record_id), "outward basis exact")
    ledger.check(outward.external_dependency_refs == (authority.record_id,), "outward dependency exact")
    ledger.check(expression.governed_outward_meaning_ref == outward.record_id, "expression link binds exact outward meaning")
    ledger.check(expression.expression_candidate_ref == candidate.expression_candidate_id, "expression link binds exact candidate")
    ledger.check(selected_trace.from_record_ref == selected.record_id, "selected trace origin exact")
    ledger.check(selected_trace.to_record_ref == outward.record_id, "selected trace target exact")
    ledger.check(expression_trace.from_record_ref == outward.record_id, "expression trace origin exact")
    ledger.check(expression_trace.to_record_ref == expression.record_id, "expression trace target exact")
    ledger.check(selected_trace.authority_reference_ref == authority.record_id, "selected trace authority exact")
    ledger.check(expression_trace.authority_reference_ref == authority.record_id, "expression trace authority exact")

    derived = integration.derive_outward_meaning_fields(value)
    ledger.check(outward.lineage_id == derived["lineage_id"], "outward lineage derived")
    ledger.check(outward.permitted_claims == derived["permitted_claims"], "permitted claims exact")
    ledger.check(outward.required_qualifications == derived["required_qualifications"], "qualifications exact")
    ledger.check(outward.prohibited_enlargements == derived["prohibited_enlargements"], "prohibited enlargements exact")
    ledger.check(outward.preservation_classes == derived["preservation_classes"], "preservation classes exact")
    for ref in candidate.required_caveat_refs:
        ledger.check(ref in outward.required_qualifications, "candidate caveat retained " + ref)
    for ref in candidate.refusal_relevant_boundary_refs:
        ledger.check(ref in outward.required_qualifications, "candidate refusal retained " + ref)
    for ref in candidate.unresolved_condition_refs:
        ledger.check(ref in outward.required_qualifications, "candidate unresolved retained " + ref)
    for ref in candidate.ambiguity_refs:
        ledger.check(ref in outward.required_qualifications, "candidate ambiguity retained " + ref)

    ledger.check(companion.source_manifest_id == source.manifest_id, "companion source exact")
    ledger.check(companion.successor_manifest_id == successor.manifest_id, "companion successor exact")
    ledger.check(companion.selected_governed_meaning_ref == selected.record_id, "companion selected meaning exact")
    ledger.check(companion.expression_candidate_ref == candidate.expression_candidate_id, "companion candidate exact")
    ledger.check(companion.integrated_governed_outward_meaning_ref == outward.record_id, "companion outward exact")
    ledger.check(companion.integrated_expression_link_ref == expression.record_id, "companion expression exact")
    ledger.check(companion.candidate_refs_before == companion.candidate_refs_after, "companion candidates retained")
    ledger.check(companion.non_selection_refs_before == companion.non_selection_refs_after, "companion non-selection retained")
    ledger.check(companion.selected_refs_before == companion.selected_refs_after, "companion selected retained")
    ledger.check(companion.governed_result_refs_before == companion.governed_result_refs_after, "companion governed results retained")
    ledger.check(companion.validation_link_refs_before == companion.validation_link_refs_after, "companion validations retained")
    ledger.check(companion.delivery_link_refs_before == companion.delivery_link_refs_after, "companion delivery retained")
    ledger.check(companion.exact_adapter, "companion exact adapter")
    ledger.check(companion.lossless_custody, "companion lossless custody")
    ledger.check(companion.immutable_successor, "companion immutable successor")
    ledger.check(companion.alternatives_and_unresolved_retained, "companion alternatives retained")
    ledger.check(companion.candidate_remains_unvalidated, "companion candidate unvalidated")
    ledger.check(companion.complete_successor_manifest_validated, "companion manifest validated")
    ledger.check(not companion.msm_schema_modified, "companion no schema modification")
    ledger.check(not companion.automatic_migration_performed, "companion no migration")

    ledger.check(receipt.source_manifest_ref == source.manifest_id, "receipt source exact")
    ledger.check(receipt.successor_manifest_ref == successor.manifest_id, "receipt successor exact")
    ledger.check(receipt.expression_candidate_ref == candidate.expression_candidate_id, "receipt candidate exact")
    ledger.check(receipt.outward_meaning_count_after == receipt.outward_meaning_count_before + 1, "receipt one outward addition")
    ledger.check(receipt.expression_link_count_after == receipt.expression_link_count_before + 1, "receipt one expression addition")
    ledger.check(receipt.validation_link_count_after == receipt.validation_link_count_before, "receipt no validation addition")
    ledger.check(receipt.delivery_link_count_after == receipt.delivery_link_count_before, "receipt no delivery addition")
    ledger.check(receipt.deterministic, "receipt deterministic")
    ledger.check(receipt.additive_only, "receipt additive only")
    ledger.check(receipt.complete_manifest_validated, "receipt manifest validated")
    ledger.check(receipt.candidate_remains_unvalidated, "receipt candidate unvalidated")

    positive_flags = (
        "deterministic",
        "additive_only",
        "immutable_successor_created",
        "exact_slice41e_chain_preserved",
        "exact_slice42f_candidate_preserved",
        "dormant_msm_records_used",
        "selected_meaning_preserved",
        "all_candidate_meanings_retained",
        "all_non_selection_outcomes_retained",
        "alternatives_and_unresolved_retained",
        "governed_outward_meaning_integrated",
        "expression_link_integrated",
        "complete_successor_manifest_validated",
        "candidate_remains_unvalidated",
    )
    for name in positive_flags:
        ledger.check(getattr(result, name) is True, "result positive " + name)

    prohibited_flags = (
        "msm_schema_modified",
        "automatic_migration_performed",
        "source_manifest_mutated",
        "candidate_deleted",
        "non_selection_outcome_deleted",
        "selected_meaning_rewritten",
        "governed_result_reference_created",
        "validation_link_created",
        "delivery_link_created",
        "expression_candidate_rewritten",
        "claim_strengthened",
        "certainty_upgraded",
        "evidence_status_upgraded",
        "caveat_omitted",
        "refusal_softened",
        "ambiguity_erased",
        "unsupported_state_erased",
        "echo_validation_performed",
        "echo_approved",
        "delivery_authorized",
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
        "bootstrap_integration_enabled",
        "gp014_superseded",
    )
    for name in prohibited_flags:
        ledger.check(getattr(result, name) is False, "result boundary " + name)

    for field in (
        "msm_schema_rewrite_requested",
        "automatic_migration_requested",
        "source_manifest_mutation_requested",
        "candidate_deletion_requested",
        "non_selection_deletion_requested",
        "selected_meaning_rewrite_requested",
        "alternative_deletion_requested",
        "unresolved_resolution_requested",
        "governed_result_creation_requested",
        "validation_link_creation_requested",
        "delivery_link_creation_requested",
        "expression_candidate_rewrite_requested",
        "claim_strengthening_requested",
        "certainty_upgrade_requested",
        "evidence_status_upgrade_requested",
        "caveat_omission_requested",
        "refusal_softening_requested",
        "ambiguity_erasure_requested",
        "unsupported_state_erasure_requested",
        "echo_validation_requested",
        "delivery_requested",
        "truth_evidence_permission_execution_requested",
        "route_tool_action_memory_filesystem_network_requested",
        "external_resource_or_model_authority_requested",
        "bootstrap_integration_requested",
        "gp014_supersession_requested",
    ):
        tampered = integration.with_expected_input_id(
            replace(value, integration_input_id="pending", **{field: True})
        )
        ledger.check(
            not integration.validate_integration_input(tampered).ok,
            "prohibited input rejected " + field,
        )

    bad_profile = integration.with_expected_profile_id(
        replace(
            value.authority_profile,
            profile_id="pending",
            complete_successor_validation_required=False,
        )
    )
    bad_profile_input = integration.with_expected_input_id(
        replace(
            value,
            integration_input_id="pending",
            authority_profile=bad_profile,
        )
    )
    ledger.check(
        not integration.validate_integration_input(bad_profile_input).ok,
        "weakened profile rejected",
    )

    missing_candidate_link = replace(
        result.expression_link_record,
        expression_candidate_ref="fabricated-expression-candidate:missing",
    )
    ledger.check(
        not integration.validate_integration_result(
            replace(result, expression_link_record=missing_candidate_link),
            integration_input=value,
        ).ok,
        "fabricated expression link rejected",
    )
    omitted_qualification = replace(
        outward,
        required_qualifications=altered_tuple(
            outward.required_qualifications,
            "fabricated-required-qualification",
        ),
    )
    ledger.check(
        not integration.validate_integration_result(
            replace(result, governed_outward_meaning_record=omitted_qualification),
            integration_input=value,
        ).ok,
        "qualification custody tamper rejected",
    )
    companion_loss = replace(
        companion,
        preserved_alternative_refs=altered_tuple(
            companion.preserved_alternative_refs,
            "fabricated-alternative-ref",
        ),
    )
    ledger.check(
        not integration.validate_integration_result(
            replace(result, companion=companion_loss),
            integration_input=value,
        ).ok,
        "alternative custody tamper rejected",
    )
    receipt_echo = replace(receipt, echo_validated_or_approved=True)
    ledger.check(
        not integration.validate_integration_result(
            replace(result, receipt=receipt_echo),
            integration_input=value,
        ).ok,
        "fabricated Echo approval rejected",
    )

    print("AI.WEB SLICE 42G MSM-V1 OUTWARD-MEANING AND EXPRESSION-LINK CUSTODY TEST")
    print("check_count=" + str(ledger.check_count))
    print("source_manifest_id=" + source.manifest_id)
    print("successor_manifest_id=" + successor.manifest_id)
    print("candidate_meanings_retained=" + str(int(successor.candidate_meanings == source.candidate_meanings)))
    print("non_selection_outcomes_retained=" + str(int(successor.non_selection_outcomes == source.non_selection_outcomes)))
    print("selected_governed_meanings_retained=" + str(int(successor.selected_governed_meanings == source.selected_governed_meanings)))
    print("governed_outward_meanings_added=" + str(len(successor.governed_outward_meanings) - len(source.governed_outward_meanings)))
    print("expression_links_added=" + str(len(successor.expression_links) - len(source.expression_links)))
    print("external_authority_references_added=" + str(len(successor.external_authority_references) - len(source.external_authority_references)))
    print("semantic_transition_traces_added=" + str(len(successor.semantic_transition_traces) - len(source.semantic_transition_traces)))
    print("complete_successor_manifest_validated=" + str(int(result.complete_successor_manifest_validated)))
    print("candidate_remains_unvalidated=" + str(int(result.candidate_remains_unvalidated)))
    print("msm_v1_schema_modified=" + str(int(result.msm_schema_modified)))
    print("automatic_migration_performed=" + str(int(result.automatic_migration_performed)))
    print("validation_link_created=" + str(int(result.validation_link_created)))
    print("delivery_link_created=" + str(int(result.delivery_link_created)))
    print("echo_validation_or_approval=" + str(int(result.echo_validation_performed or result.echo_approved)))
    print("failure_count=" + str(len(ledger.failures)))
    for failure in ledger.failures:
        print("FAIL: " + failure)
    print(
        "AI.WEB SLICE 42G BEHAVIOR TEST: "
        + ("PASS" if not ledger.failures else "FAIL")
    )
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
