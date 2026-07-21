#!/usr/bin/env python3
"""Visible behavior test for AI.Web Slice 42D."""

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


def build_slice42c_state(repo: Path) -> tuple[Any, Any, Any]:
    test42c = load_script(
        repo
        / "scripts/test_aiweb_slice42c_authorized_meaning_admission_"
        "expression_eligibility.py"
    )
    closeout, source, requirement, governance_bundle = test42c[
        "build_fixture"
    ](repo)

    eligibility = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "expression_eligibility"
    )

    outward_authority = eligibility.with_expected_id(
        eligibility.OutwardExpressionAuthorityRecord(
            authority_record_id="pending",
            authority_key=(
                requirement.required_outward_expression_authority_ref
            ),
            authority_version="v1.0.0",
            selected_meaning_source_custody_ref=source.source_custody_id,
            authority_requirement_ref=requirement.authority_requirement_id,
            authority_scope_refs=requirement.required_authority_scope_refs,
            expression_purpose_refs=(
                requirement.required_expression_purpose_refs
            ),
            predecessor_receipt_refs=(
                requirement.required_predecessor_receipt_refs
            ),
            version_refs=requirement.required_version_refs,
            disposition_authority_ref=(
                "authority-disposition:slice42d-fixture:explicit"
            ),
            authority_receipt_ref=(
                "authority-receipt:slice42d-fixture:explicit"
            ),
            authority_active=True,
            eligibility_evaluation_authorized=True,
            expression_planning_progression_authorized=True,
            preservation_obligation_projection_authorized=False,
            governed_outward_meaning_construction_authorized=False,
            expression_plan_construction_authorized=False,
            surface_realization_authorized=False,
            msm_v1_mutation_or_integration_authorized=False,
            echo_validation_authorized=False,
            delivery_authorized=False,
            truth_evidence_permission_execution_authorized=False,
            route_api_network_filesystem_memory_tool_action_authorized=False,
            external_resource_or_model_authority=False,
            gp014_supersession_authorized=False,
        )
    )

    evaluation_input = eligibility.with_expected_id(
        eligibility.ExpressionEligibilityEvaluationInput(
            evaluation_input_id="pending",
            selected_meaning_closeout_result=closeout,
            selected_meaning_source_custody=source,
            outward_expression_authority_requirement=requirement,
            outward_expression_governance_bundle=governance_bundle,
            outward_expression_authority_record=outward_authority,
            evaluation_reason_refs=("slice42d:exact-slice42c-state",),
            trace_refs=(source.selection_trace_ref,),
            provenance_refs=(closeout.result_id, governance_bundle.bundle_id),
            version_refs=(eligibility.SLICE42C_SCHEMA_VERSION,),
            selected_meaning_alone_claimed_sufficient=False,
            authority_inference_requested=False,
            record_repair_requested=False,
            scope_expansion_requested=False,
            purpose_expansion_requested=False,
            refusal_softening_requested=False,
            unresolved_resolution_requested=False,
            blocked_consequence_erasure_requested=False,
            downstream_authority_requested=False,
        )
    )
    result = eligibility.evaluate_expression_eligibility(evaluation_input)
    eligibility.assert_valid_result(result, evaluation_input=evaluation_input)
    return eligibility, evaluation_input, result


def build_slice42d_input(repo: Path) -> tuple[Any, Any]:
    eligibility, evaluation_input, eligibility_result = build_slice42c_state(
        repo
    )
    projection = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "preservation_obligation_projection"
    )

    source = evaluation_input.selected_meaning_source_custody
    requirement = evaluation_input.outward_expression_authority_requirement
    outward_authority = evaluation_input.outward_expression_authority_record

    projection_authority = projection.with_expected_id(
        projection.PreservationObligationProjectionAuthorityRecord(
            projection_authority_record_id="pending",
            authority_key=projection.SLICE42D_PROJECTION_AUTHORITY_KEY,
            authority_version=projection.SLICE42D_PROFILE_VERSION,
            expression_eligibility_evaluation_input_ref=(
                evaluation_input.evaluation_input_id
            ),
            expression_eligibility_result_ref=eligibility_result.result_id,
            selected_meaning_source_custody_ref=source.source_custody_id,
            outward_expression_authority_requirement_ref=(
                requirement.authority_requirement_id
            ),
            outward_expression_authority_record_ref=(
                outward_authority.authority_record_id
            ),
            source_eligibility_outcome=eligibility_result.outcome,
            projection_scope_refs=outward_authority.authority_scope_refs,
            predecessor_receipt_refs=(
                source.slice41e_integration_receipt_ref,
                source.selection_receipt_ref,
                outward_authority.authority_receipt_ref,
            ),
            version_refs=(
                eligibility.SLICE42C_SCHEMA_VERSION,
                projection.SLICE42D_SCHEMA_VERSION,
                outward_authority.authority_version,
            ),
            disposition_authority_ref=(
                "projection-authority-disposition:slice42d-fixture:explicit"
            ),
            projection_authority_receipt_ref=(
                "projection-authority-receipt:slice42d-fixture:explicit"
            ),
            authority_active=True,
            preservation_obligation_projection_authorized=True,
            governed_outward_meaning_construction_authorized=False,
            expression_plan_construction_authorized=False,
            surface_realization_authorized=False,
            msm_v1_mutation_or_integration_authorized=False,
            echo_validation_authorized=False,
            delivery_authorized=False,
            truth_evidence_permission_execution_authorized=False,
            route_api_network_filesystem_memory_tool_action_authorized=False,
            external_resource_or_model_authority=False,
            gp014_supersession_authorized=False,
        )
    )

    projection_input = projection.with_expected_id(
        projection.PreservationObligationProjectionInput(
            projection_input_id="pending",
            expression_eligibility_evaluation_input=evaluation_input,
            expression_eligibility_result=eligibility_result,
            projection_authority_record=projection_authority,
            projection_reason_refs=("slice42d:exact-obligation-projection",),
            trace_refs=(source.selection_trace_ref,),
            provenance_refs=(
                eligibility_result.result_id,
                projection_authority.projection_authority_record_id,
            ),
            version_refs=(
                eligibility.SLICE42C_SCHEMA_VERSION,
                projection.SLICE42D_SCHEMA_VERSION,
            ),
            scope_expansion_requested=False,
            certainty_upgrade_requested=False,
            evidence_status_upgrade_requested=False,
            limitation_omission_requested=False,
            caveat_omission_requested=False,
            refusal_softening_requested=False,
            unresolved_resolution_requested=False,
            ambiguity_erasure_requested=False,
            unsupported_state_erasure_requested=False,
            memory_authority_upgrade_requested=False,
            external_resource_status_upgrade_requested=False,
            delivery_authority_upgrade_requested=False,
            selected_meaning_rewrite_requested=False,
            downstream_authority_requested=False,
        )
    )
    return projection, projection_input


def tampered_package_result(
    projection: Any,
    result: Any,
    **changes: Any,
) -> Any:
    package = projection.with_expected_package_identity(
        replace(result.obligation_package, **changes)
    )
    return projection.with_expected_result_identity(
        replace(result, obligation_package=package)
    )


def altered_tuple(
    values: tuple[str, ...],
    fabricated: str,
) -> tuple[str, ...]:
    if values:
        return values[1:]
    return (fabricated,)


def main() -> int:
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sys.path.insert(0, str(repo))

    projection, projection_input = build_slice42d_input(repo)
    ledger = Ledger()

    input_report = projection.validate_projection_input(projection_input)
    ledger.check(input_report.ok, "exact projection input validates")

    result = projection.project_preservation_obligations(projection_input)
    result_report = projection.validate_projection_result(
        result,
        projection_input=projection_input,
    )
    ledger.check(result_report.ok, "exact projection result validates")

    package = result.obligation_package
    derived = projection.derive_obligation_values(projection_input)

    ledger.check(
        len(projection.SLICE42D_OBLIGATION_CATEGORY_NAMES) == 10,
        "exact ten obligation categories",
    )
    ledger.check(
        package.source_eligibility_outcome
        is projection_input.expression_eligibility_result.outcome,
        "Slice 42C disposition preserved",
    )
    ledger.check(
        result.blocked
        is projection_input.expression_eligibility_result.blocked,
        "blocked state preserved",
    )
    ledger.check(
        result.refusal_preserving
        is projection_input.expression_eligibility_result.refusal_preserving,
        "refusal-preserving state preserved",
    )
    ledger.check(
        result.unresolved_preserving
        is projection_input.expression_eligibility_result.unresolved_preserving,
        "unresolved-preserving state preserved",
    )

    projected_fields = (
        "selected_meaning_refs",
        "active_scope_refs",
        "certainty_level_refs",
        "evidence_status_refs",
        "inherited_limitation_refs",
        "required_caveat_refs",
        "refusal_relevant_boundary_refs",
        "unresolved_condition_refs",
        "ambiguity_refs",
        "unsupported_state_refs",
        "memory_authority_refs",
        "external_resource_status_refs",
        "delivery_authority_refs",
        "privacy_identity_boundary_refs",
        "preservation_class_refs",
        "predecessor_receipt_refs",
        "trace_refs",
        "provenance_refs",
        "version_refs",
    )
    for field_name in projected_fields:
        ledger.check(
            getattr(package, field_name) == derived[field_name],
            f"exact projected field {field_name}",
        )

    required_true = (
        "exact_slice42c_state_verified",
        "exact_projection_authority_verified",
        "obligation_categories_separately_projected",
        "selected_meaning_preserved",
        "active_scope_preserved",
        "certainty_preserved",
        "evidence_status_preserved",
        "inherited_limitations_preserved",
        "required_caveats_preserved",
        "refusal_boundaries_preserved",
        "unresolved_conditions_preserved",
        "ambiguity_preserved",
        "unsupported_states_preserved",
        "memory_authority_preserved",
        "external_resource_status_preserved",
        "delivery_authority_preserved",
        "projection_performed",
        "obligation_package_created",
    )
    for field_name in required_true:
        ledger.check(
            getattr(package, field_name) is True,
            f"required package proof {field_name}",
        )

    prohibited_effects = (
        "scope_upgraded",
        "certainty_upgraded",
        "evidence_status_upgraded",
        "limitation_omitted",
        "caveat_omitted",
        "refusal_softened",
        "unresolved_condition_resolved",
        "ambiguity_erased",
        "unsupported_state_erased_or_guessed",
        "memory_authority_upgraded",
        "external_resource_status_upgraded",
        "delivery_authority_upgraded",
        "selected_meaning_rewritten",
        "human_readable_text_produced",
        "governed_outward_meaning_created",
        "expression_plan_created",
        "expression_candidate_created",
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
    for field_name in prohibited_effects:
        ledger.check(
            getattr(package, field_name) is False,
            f"zero package effect {field_name}",
        )

    result_downstream = (
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
    for field_name in result_downstream:
        ledger.check(
            getattr(result, field_name) is False,
            f"zero result effect {field_name}",
        )

    authority = projection_input.projection_authority_record
    inactive_authority = projection.with_expected_id(
        replace(
            authority,
            projection_authority_record_id="pending",
            authority_active=False,
            preservation_obligation_projection_authorized=False,
        )
    )
    inactive_input = projection.with_expected_id(
        replace(
            projection_input,
            projection_input_id="pending",
            projection_authority_record=inactive_authority,
        )
    )
    ledger.check(
        not projection.validate_projection_input(inactive_input).ok,
        "inactive projection authority rejected",
    )

    downstream_authority = projection.with_expected_id(
        replace(
            authority,
            projection_authority_record_id="pending",
            expression_plan_construction_authorized=True,
        )
    )
    downstream_input = projection.with_expected_id(
        replace(
            projection_input,
            projection_input_id="pending",
            projection_authority_record=downstream_authority,
        )
    )
    ledger.check(
        not projection.validate_projection_input(downstream_input).ok,
        "projection authority with downstream grant rejected",
    )

    requested_upgrade = projection.with_expected_id(
        replace(
            projection_input,
            projection_input_id="pending",
            evidence_status_upgrade_requested=True,
        )
    )
    ledger.check(
        not projection.validate_projection_input(requested_upgrade).ok,
        "requested evidence-status upgrade rejected",
    )

    tamper_cases = {
        "selected meaning": {
            "selected_meaning_refs": altered_tuple(
                package.selected_meaning_refs,
                "selected-meaning:fabricated",
            )
        },
        "active scope": {
            "active_scope_refs": package.active_scope_refs
            + ("scope:fabricated-expansion",)
        },
        "certainty": {
            "certainty_level_refs": ("certainty:upgraded",)
        },
        "evidence status": {
            "evidence_status_refs": ("evidence:validated",)
        },
        "limitations": {
            "inherited_limitation_refs": altered_tuple(
                package.inherited_limitation_refs,
                "limitation:fabricated",
            )
        },
        "caveats": {
            "required_caveat_refs": altered_tuple(
                package.required_caveat_refs,
                "caveat:fabricated",
            )
        },
        "refusal boundaries": {
            "refusal_relevant_boundary_refs": altered_tuple(
                package.refusal_relevant_boundary_refs,
                "refusal:fabricated",
            )
        },
        "unresolved conditions": {
            "unresolved_condition_refs": altered_tuple(
                package.unresolved_condition_refs,
                "unresolved:fabricated",
            )
        },
        "ambiguity": {
            "ambiguity_refs": altered_tuple(
                package.ambiguity_refs,
                "ambiguity:fabricated",
            )
        },
        "unsupported state": {
            "unsupported_state_refs": package.unsupported_state_refs
            + ("unsupported:fabricated",)
        },
        "memory authority": {
            "memory_authority_refs": ("memory:write-authorized",)
        },
        "external resource status": {
            "external_resource_status_refs": ("resource:loaded",)
        },
        "delivery authority": {
            "delivery_authority_refs": ("delivery:authorized",)
        },
    }
    for label, changes in tamper_cases.items():
        tampered = tampered_package_result(
            projection,
            result,
            **changes,
        )
        ledger.check(
            not projection.validate_projection_result(
                tampered,
                projection_input=projection_input,
            ).ok,
            f"recomputed tampered {label} rejected",
        )

    text_tamper = tampered_package_result(
        projection,
        result,
        human_readable_text_produced=True,
    )
    ledger.check(
        not projection.validate_projection_result(
            text_tamper,
            projection_input=projection_input,
        ).ok,
        "human-readable output claim rejected",
    )

    print("AI.WEB SLICE 42D PRESERVATION-OBLIGATION PROJECTION TEST")
    print(f"check_count={ledger.check_count}")
    print(
        "source_eligibility_outcome="
        + result.source_eligibility_outcome.value
    )
    print(
        "obligation_category_count="
        + str(len(projection.SLICE42D_OBLIGATION_CATEGORY_NAMES))
    )
    print(
        "projected_selected_meaning_refs="
        + str(len(package.selected_meaning_refs))
    )
    print(
        "projected_ambiguity_refs="
        + str(len(package.ambiguity_refs))
    )
    print(
        "projected_unsupported_state_refs="
        + str(len(package.unsupported_state_refs))
    )
    print("human_readable_output_produced=0")
    print("governed_outward_meaning_created=0")
    print("expression_plan_created=0")
    print("echo_validation_delivery_action=0")
    print("failure_count=" + str(len(ledger.failures)))

    for failure in ledger.failures:
        print("FAIL: " + failure)

    if ledger.failures:
        print("AI.WEB SLICE 42D BEHAVIOR TEST: FAIL")
        return 1

    print("AI.WEB SLICE 42D BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
