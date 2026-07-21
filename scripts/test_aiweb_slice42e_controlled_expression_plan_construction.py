#!/usr/bin/env python3
"""Visible behavior test for AI.Web Slice 42E."""

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


def build_slice42e_input(repo: Path) -> tuple[Any, Any]:
    test42d = load_script(
        repo / "scripts/test_aiweb_slice42d_preservation_obligation_projection.py"
    )
    projection, projection_input = test42d["build_slice42d_input"](repo)
    projection_result = projection.project_preservation_obligations(projection_input)
    projection.assert_valid_projection_result(
        projection_result,
        projection_input=projection_input,
    )

    planning = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "expression_plan_construction"
    )
    package = projection_result.obligation_package
    disposition = planning.ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN
    receipts = tuple(
        dict.fromkeys(
            package.predecessor_receipt_refs
            + (
                projection_input.projection_authority_record
                .projection_authority_receipt_ref,
            )
        )
    )
    versions = tuple(
        dict.fromkeys(
            package.version_refs
            + (projection.SLICE42D_SCHEMA_VERSION, planning.SLICE42E_SCHEMA_VERSION)
        )
    )
    authority = planning.with_expected_id(
        planning.ExpressionPlanConstructionAuthorityRecord(
            planning_authority_record_id="pending",
            authority_key=planning.SLICE42E_PLAN_AUTHORITY_KEY,
            authority_version=planning.SLICE42E_PROFILE_VERSION,
            projection_input_ref=projection_input.projection_input_id,
            projection_result_ref=projection_result.result_id,
            obligation_package_ref=package.obligation_package_id,
            selected_meaning_source_custody_ref=package.selected_meaning_source_custody_ref,
            outward_expression_authority_record_ref=package.outward_expression_authority_record_ref,
            source_eligibility_outcome=projection_result.source_eligibility_outcome,
            permitted_disposition=disposition,
            permitted_structural_order=planning.structural_order(),
            predecessor_receipt_refs=receipts,
            version_refs=versions,
            disposition_authority_ref="plan-authority-disposition:slice42e-fixture:explicit",
            planning_authority_receipt_ref="plan-authority-receipt:slice42e-fixture:explicit",
            authority_active=True,
            expression_plan_construction_authorized=True,
            affirmative_meaning_plan_authorized=False,
            containment_plan_authorized=True,
            governed_outward_meaning_construction_authorized=False,
            surface_realization_authorized=False,
            expression_candidate_creation_authorized=False,
            msm_v1_mutation_or_integration_authorized=False,
            echo_validation_authorized=False,
            delivery_authorized=False,
            truth_evidence_permission_execution_authorized=False,
            route_api_network_filesystem_memory_tool_action_authorized=False,
            external_resource_or_model_authority=False,
            gp014_supersession_authorized=False,
        )
    )
    plan_input = planning.with_expected_id(
        planning.ExpressionPlanConstructionInput(
            plan_input_id="pending",
            projection_input=projection_input,
            projection_result=projection_result,
            planning_authority_record=authority,
            planning_reason_refs=("slice42e:controlled-plan-construction",),
            trace_refs=package.trace_refs,
            provenance_refs=(projection_result.result_id, package.obligation_package_id),
            version_refs=(projection.SLICE42D_SCHEMA_VERSION, planning.SLICE42E_SCHEMA_VERSION),
            obligation_omission_requested=False,
            structural_reordering_requested=False,
            modifier_omission_requested=False,
            modifier_invention_requested=False,
            qualification_omission_requested=False,
            caveat_omission_requested=False,
            refusal_softening_requested=False,
            unresolved_resolution_requested=False,
            ambiguity_erasure_requested=False,
            unsupported_state_erasure_requested=False,
            lower_order_override_requested=False,
            selected_meaning_rewrite_requested=False,
            human_readable_wording_requested=False,
            downstream_authority_requested=False,
        )
    )
    return planning, plan_input


def tampered_plan_result(planning: Any, result: Any, **changes: Any) -> Any:
    assert result.expression_plan is not None
    plan = planning.with_expected_plan_identity(
        replace(result.expression_plan, **changes)
    )
    return planning.with_expected_result_identity(
        replace(result, expression_plan=plan)
    )


def main() -> int:
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sys.path.insert(0, str(repo))
    planning, plan_input = build_slice42e_input(repo)
    ledger = Ledger()

    ledger.check(planning.validate_plan_input(plan_input).ok, "exact plan input validates")
    result = planning.construct_expression_plan(plan_input)
    ledger.check(planning.validate_plan_result(result, plan_input=plan_input).ok, "exact plan result validates")
    plan = result.expression_plan
    ledger.check(plan is not None, "controlled expression plan created")
    assert plan is not None

    package = plan_input.projection_result.obligation_package
    derived = planning.derive_plan_values(plan_input)
    ledger.check(result.disposition is planning.ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN, "blocked disposition preserved")
    ledger.check(result.expression_plan_created, "plan created")
    ledger.check(result.blocked_consequence_plan, "blocked containment plan")
    ledger.check(not result.affirmative_claim_plan, "blocked plan not affirmative")
    ledger.check(not plan.source_planning_progression_eligible, "source eligibility not upgraded")
    ledger.check(plan.containment_plan_does_not_upgrade_source_eligibility, "containment does not upgrade eligibility")
    ledger.check(plan.structural_order == planning.structural_order(), "exact structural order")
    ledger.check(len(plan.sections) == len(planning.SLICE42E_SECTION_ORDER_VALUES), "exact section count")
    ledger.check(tuple(section.section_kind for section in plan.sections) == plan.structural_order, "section kinds in exact order")
    ledger.check(tuple(section.precedence_index for section in plan.sections) == tuple(range(1, len(plan.sections) + 1)), "contiguous precedence")
    ledger.check(len({section.section_id for section in plan.sections}) == len(plan.sections), "section ids unique")
    for section in plan.sections:
        ledger.check(section.required_for_plan_custody, f"section required {section.section_kind.value}")
        ledger.check(section.omission_prohibited, f"section omission prohibited {section.section_kind.value}")
        ledger.check(section.lower_order_override_prohibited, f"section override prohibited {section.section_kind.value}")
        ledger.check(not section.human_readable_text_present, f"section no text {section.section_kind.value}")

    exact_fields = (
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
    )
    for name in exact_fields:
        ledger.check(getattr(plan, name) == getattr(package, name), f"exact obligation {name}")
    ledger.check(plan.meaning_modifier_refs == derived["meaning_modifier_refs"], "exact meaning modifiers")
    ledger.check(plan.required_qualification_refs == derived["required_qualification_refs"], "exact qualifications")
    ledger.check(plan.ancestry_refs == derived["ancestry_refs"], "exact ancestry")
    ledger.check(plan.all_slice42d_obligations_preserved, "all obligations preserved")
    ledger.check(plan.structural_ordering_determined, "ordering determined")
    ledger.check(plan.meaning_modifiers_preserved, "modifiers preserved")
    ledger.check(plan.required_qualifications_preserved, "qualifications preserved")
    ledger.check(plan.required_caveats_preserved, "caveats preserved")
    ledger.check(plan.refusal_boundaries_preserved, "refusal boundaries preserved")
    ledger.check(plan.higher_order_restrictions_dominant, "higher-order restrictions dominant")
    ledger.check(plan.selected_meaning_ancestry_preserved, "ancestry preserved")

    for name in (
        "governed_outward_meaning_created",
        "human_readable_text_produced",
        "expression_candidate_created",
        "surface_realization_performed",
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
    ):
        ledger.check(getattr(plan, name) is False, f"plan downstream zero {name}")
        ledger.check(getattr(result, name) is False, f"result downstream zero {name}")

    wrong_key = planning.with_expected_id(
        replace(plan_input.planning_authority_record, planning_authority_record_id="pending", authority_key="plan-authority:wrong")
    )
    ledger.check(not planning.validate_plan_input(planning.with_expected_id(replace(plan_input, plan_input_id="pending", planning_authority_record=wrong_key))).ok, "wrong authority key rejected")
    inactive = planning.with_expected_id(
        replace(plan_input.planning_authority_record, planning_authority_record_id="pending", authority_active=False, expression_plan_construction_authorized=False, containment_plan_authorized=False)
    )
    ledger.check(not planning.validate_plan_input(planning.with_expected_id(replace(plan_input, plan_input_id="pending", planning_authority_record=inactive))).ok, "inactive authority rejected")
    reversed_authority = planning.with_expected_id(
        replace(plan_input.planning_authority_record, planning_authority_record_id="pending", permitted_structural_order=tuple(reversed(plan_input.planning_authority_record.permitted_structural_order)))
    )
    ledger.check(not planning.validate_plan_input(planning.with_expected_id(replace(plan_input, plan_input_id="pending", planning_authority_record=reversed_authority))).ok, "reordered authority rejected")

    for field_name in (
        "obligation_omission_requested",
        "structural_reordering_requested",
        "modifier_omission_requested",
        "modifier_invention_requested",
        "qualification_omission_requested",
        "caveat_omission_requested",
        "refusal_softening_requested",
        "unresolved_resolution_requested",
        "ambiguity_erasure_requested",
        "unsupported_state_erasure_requested",
        "lower_order_override_requested",
        "selected_meaning_rewrite_requested",
        "human_readable_wording_requested",
        "downstream_authority_requested",
    ):
        bad = planning.with_expected_id(replace(plan_input, plan_input_id="pending", **{field_name: True}))
        ledger.check(not planning.validate_plan_input(bad).ok, f"prohibited request rejected {field_name}")

    reordered = tampered_plan_result(planning, result, structural_order=tuple(reversed(plan.structural_order)))
    ledger.check(not planning.validate_plan_result(reordered, plan_input=plan_input).ok, "tampered structural order rejected")
    modifier_tampered = tampered_plan_result(planning, result, meaning_modifier_refs=("modifier:fabricated",))
    ledger.check(not planning.validate_plan_result(modifier_tampered, plan_input=plan_input).ok, "fabricated modifier rejected")
    caveat_tampered = tampered_plan_result(planning, result, required_caveat_refs=())
    ledger.check(not planning.validate_plan_result(caveat_tampered, plan_input=plan_input).ok, "caveat omission rejected")
    refusal_tamper_refs = (
        ()
        if plan.refusal_relevant_boundary_refs
        else ("refusal-boundary:fabricated",)
    )
    refusal_tampered = tampered_plan_result(
        planning,
        result,
        refusal_relevant_boundary_refs=refusal_tamper_refs,
    )
    ledger.check(
        not planning.validate_plan_result(
            refusal_tampered,
            plan_input=plan_input,
        ).ok,
        "refusal boundary custody tampering rejected",
    )
    ancestry_tampered = tampered_plan_result(planning, result, ancestry_refs=("ancestry:fabricated",))
    ledger.check(not planning.validate_plan_result(ancestry_tampered, plan_input=plan_input).ok, "ancestry tampering rejected")
    text_tampered = tampered_plan_result(planning, result, human_readable_text_produced=True)
    ledger.check(not planning.validate_plan_result(text_tampered, plan_input=plan_input).ok, "text production rejected")

    print("AI.WEB SLICE 42E CONTROLLED EXPRESSION-PLAN CONSTRUCTION TEST")
    print(f"check_count={ledger.check_count}")
    print("source_eligibility_outcome=" + result.source_eligibility_outcome.value)
    print("plan_disposition=" + result.disposition.value)
    print("expression_plan_created=" + str(int(result.expression_plan_created)))
    print("plan_section_count=" + str(len(plan.sections)))
    print("blocked_plan_is_affirmative_claim=0")
    print("all_slice42d_obligations_preserved=1")
    print("structural_ordering_determined=1")
    print("human_readable_output_produced=0")
    print("governed_outward_meaning_created=0")
    print("expression_candidate_created=0")
    print("echo_validation_delivery_action=0")
    print("failure_count=" + str(len(ledger.failures)))
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures:
        print("AI.WEB SLICE 42E BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 42E BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
