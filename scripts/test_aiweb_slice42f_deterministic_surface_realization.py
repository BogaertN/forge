#!/usr/bin/env python3
"""Visible behavior test for AI.Web Slice 42F."""

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


def build_slice42f_input(repo: Path) -> tuple[Any, Any]:
    test42e = load_script(
        repo / "scripts/test_aiweb_slice42e_controlled_expression_plan_construction.py"
    )
    planning, plan_input = test42e["build_slice42e_input"](repo)
    plan_result = planning.construct_expression_plan(plan_input)
    planning.assert_valid_plan_result(plan_result, plan_input=plan_input)
    assert plan_result.expression_plan is not None
    plan = plan_result.expression_plan

    realization = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "surface_realization"
    )

    template_specs = (
        (
            "template:authorized_meaning_plan",
            planning.ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
            "The governed expression plan authorizes a bounded affirmative expression.",
        ),
        (
            "template:blocked_consequence_plan",
            planning.ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
            "I cannot present the selected meaning as an authorized affirmative claim because the governed expression state is blocked.",
        ),
        (
            "template:refusal_preserving_plan",
            planning.ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
            "I must refuse the governed affirmative expression while preserving the selected meaning and its refusal boundaries.",
        ),
        (
            "template:unresolved_preserving_plan",
            planning.ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN,
            "I cannot present a resolved affirmative claim because the governed expression state remains unresolved.",
        ),
    )
    records = tuple(
        realization.with_expected_id(
            realization.ControlledRealizationResourceRecord(
                resource_record_id="pending",
                resource_key=key,
                resource_kind=(
                    realization.ControlledRealizationResourceKind
                    .DISPOSITION_TEMPLATE
                ),
                resource_text=text,
                bound_selected_meaning_ref=None,
                permitted_plan_dispositions=(disposition,),
                authority_ref="surface-resource-authority:slice42f-fixture",
                resource_version=realization.SLICE42F_RESOURCE_PROFILE_VERSION,
                admitted=True,
                deterministic=True,
                external_resource=False,
                model_generated=False,
            )
        )
        for key, disposition, text in template_specs
    )
    resources = realization.with_expected_id(
        realization.ControlledRealizationResourceBundle(
            resource_bundle_id="pending",
            profile_key=realization.SLICE42F_RESOURCE_PROFILE_KEY,
            profile_version=realization.SLICE42F_RESOURCE_PROFILE_VERSION,
            records=records,
            admitted_rule_refs=realization.SLICE42F_ADMITTED_RULE_REFS,
            resource_authority_receipt_ref=(
                "surface-resource-authority-receipt:slice42f-fixture"
            ),
            deterministic=True,
            external_resource_loaded=False,
            model_or_similarity_authority_used=False,
        )
    )
    authority = realization.with_expected_id(
        realization.SurfaceRealizationAuthorityRecord(
            realization_authority_record_id="pending",
            authority_key=realization.SLICE42F_REALIZATION_AUTHORITY_KEY,
            authority_version=realization.SLICE42F_PROFILE_VERSION,
            plan_input_ref=plan_input.plan_input_id,
            plan_result_ref=plan_result.result_id,
            expression_plan_ref=plan.expression_plan_id,
            selected_meaning_source_custody_ref=(
                plan.selected_meaning_source_custody_ref
            ),
            source_plan_disposition=plan.disposition,
            permitted_realization_disposition=(
                realization.determine_realization_disposition(
                    plan.disposition
                )
            ),
            admitted_rule_refs=realization.SLICE42F_ADMITTED_RULE_REFS,
            controlled_resource_bundle_ref=resources.resource_bundle_id,
            predecessor_receipt_refs=plan.predecessor_receipt_refs,
            version_refs=tuple(
                dict.fromkeys(
                    plan.version_refs
                    + (
                        planning.SLICE42E_SCHEMA_VERSION,
                        realization.SLICE42F_SCHEMA_VERSION,
                    )
                )
            ),
            disposition_authority_ref=(
                "surface-realization-disposition:slice42f-fixture:explicit"
            ),
            realization_authority_receipt_ref=(
                "surface-realization-authority-receipt:slice42f-fixture:explicit"
            ),
            authority_active=True,
            surface_realization_authorized=True,
            authorized_claim_realization_authorized=False,
            containment_realization_authorized=True,
            expression_candidate_creation_authorized=True,
            governed_outward_meaning_construction_authorized=False,
            msm_v1_mutation_or_integration_authorized=False,
            echo_validation_authorized=False,
            delivery_authorized=False,
            truth_evidence_permission_execution_authorized=False,
            route_api_network_filesystem_memory_tool_action_authorized=False,
            external_resource_or_model_authority=False,
            gp014_supersession_authorized=False,
        )
    )
    realization_input = realization.with_expected_id(
        realization.SurfaceRealizationInput(
            realization_input_id="pending",
            plan_input=plan_input,
            plan_result=plan_result,
            realization_authority_record=authority,
            controlled_resource_bundle=resources,
            realization_reason_refs=(
                "slice42f:deterministic-surface-realization",
            ),
            trace_refs=plan.trace_refs,
            provenance_refs=(
                plan_result.result_id,
                plan.expression_plan_id,
                resources.resource_bundle_id,
            ),
            version_refs=(
                planning.SLICE42E_SCHEMA_VERSION,
                realization.SLICE42F_SCHEMA_VERSION,
            ),
            free_form_generation_requested=False,
            unadmitted_rule_requested=False,
            unadmitted_resource_requested=False,
            claim_invention_requested=False,
            claim_strengthening_requested=False,
            scope_expansion_requested=False,
            certainty_upgrade_requested=False,
            evidence_status_upgrade_requested=False,
            limitation_omission_requested=False,
            qualification_omission_requested=False,
            caveat_omission_requested=False,
            refusal_softening_requested=False,
            unresolved_resolution_requested=False,
            ambiguity_erasure_requested=False,
            unsupported_state_erasure_requested=False,
            selected_meaning_rewrite_requested=False,
            downstream_authority_requested=False,
        )
    )
    return realization, realization_input


def reidentified_result(realization: Any, result: Any, **changes: Any) -> Any:
    candidate = result.expression_candidate
    assert candidate is not None
    changed_candidate = realization.with_expected_candidate_identity(
        replace(candidate, **changes)
    )
    return realization.with_expected_result_identity(
        replace(result, expression_candidate=changed_candidate)
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
    realization, realization_input = build_slice42f_input(repo)
    ledger = Ledger()

    ledger.check(
        realization.validate_surface_realization_input(
            realization_input
        ).ok,
        "exact realization input validates",
    )
    result = realization.realize_surface_expression(realization_input)
    ledger.check(
        realization.validate_surface_realization_result(
            result,
            realization_input=realization_input,
        ).ok,
        "exact realization result validates",
    )
    repeated = realization.realize_surface_expression(realization_input)
    ledger.check(result == repeated, "deterministic repeated realization")

    candidate = result.expression_candidate
    trace = result.realization_trace
    receipt = result.realization_receipt
    ledger.check(candidate is not None, "expression candidate created")
    ledger.check(trace is not None, "realization trace created")
    ledger.check(receipt is not None, "realization receipt created")
    assert candidate is not None and trace is not None and receipt is not None

    plan = realization_input.plan_result.expression_plan
    assert plan is not None
    ledger.check(
        result.disposition
        is realization.SurfaceRealizationDisposition
        .BLOCKED_EXPRESSION_CANDIDATE,
        "blocked realization disposition preserved",
    )
    ledger.check(result.surface_realization_performed, "surface realization")
    ledger.check(result.human_readable_text_produced, "human-readable text")
    ledger.check(result.expression_candidate_created, "candidate flag")
    ledger.check(result.refusal_language_produced, "refusal language produced")
    ledger.check(
        not candidate.source_plan_disposition
        is type(plan.disposition).AUTHORIZED_MEANING_PLAN,
        "blocked plan not converted to authorized plan",
    )
    ledger.check(
        candidate.realized_text.startswith(
            "I cannot present the selected meaning as an authorized "
            "affirmative claim"
        ),
        "controlled blocked template used",
    )
    ledger.check(
        "no affirmative claim is authorized" in candidate.realized_text,
        "nonaffirmative containment visible",
    )
    ledger.check(
        "unvalidated expression candidate" in candidate.realized_text,
        "unvalidated marker visible",
    )
    ledger.check(
        "not authorized for delivery" in candidate.realized_text,
        "delivery boundary visible",
    )
    ledger.check(
        candidate.segments
        == realization.build_realization_segments(realization_input),
        "exact deterministic segments",
    )
    ledger.check(
        candidate.realized_text == " ".join(candidate.segments),
        "exact segment joining",
    )

    exact_fields = (
        "selected_meaning_refs",
        "active_scope_refs",
        "certainty_level_refs",
        "evidence_status_refs",
        "meaning_modifier_refs",
        "inherited_limitation_refs",
        "required_qualification_refs",
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
        "ancestry_refs",
        "predecessor_receipt_refs",
    )
    for name in exact_fields:
        ledger.check(
            getattr(candidate, name) == getattr(plan, name),
            f"exact plan custody {name}",
        )

    visible_groups = (
        plan.certainty_level_refs,
        plan.evidence_status_refs,
        plan.inherited_limitation_refs,
        plan.required_qualification_refs,
        plan.required_caveat_refs,
        plan.refusal_relevant_boundary_refs,
        plan.unresolved_condition_refs,
        plan.ambiguity_refs,
        plan.unsupported_state_refs,
        plan.memory_authority_refs,
        plan.external_resource_status_refs,
        plan.delivery_authority_refs,
        plan.privacy_identity_boundary_refs,
    )
    for group in visible_groups:
        for reference in group:
            ledger.check(
                reference in candidate.realized_text,
                "visible preserved reference " + reference,
            )

    ledger.check(candidate.authorized_claim_not_strengthened, "claim not strengthened")
    ledger.check(candidate.certainty_not_upgraded, "certainty not upgraded")
    ledger.check(candidate.evidence_status_not_upgraded, "evidence not upgraded")
    ledger.check(candidate.admitted_rules_only, "admitted rules only")
    ledger.check(candidate.controlled_resources_only, "controlled resources only")
    ledger.check(candidate.unvalidated_expression_candidate, "candidate unvalidated")
    ledger.check(not candidate.echo_validation_performed, "no Echo validation")
    ledger.check(not candidate.echo_approved, "not Echo approved")
    ledger.check(not candidate.delivery_authorized, "delivery not authorized")
    ledger.check(not candidate.delivered, "not delivered")
    ledger.check(trace.deterministic, "trace deterministic")
    ledger.check(not trace.semantic_strengthening_detected, "trace no strengthening")
    ledger.check(not trace.certainty_upgrade_detected, "trace no certainty upgrade")
    ledger.check(not trace.evidence_upgrade_detected, "trace no evidence upgrade")
    ledger.check(not trace.omission_detected, "trace no omission")
    ledger.check(receipt.deterministic, "receipt deterministic")
    ledger.check(receipt.unvalidated_expression_candidate, "receipt unvalidated")
    ledger.check(not receipt.echo_validated, "receipt no Echo validation")
    ledger.check(not receipt.echo_approved, "receipt not Echo approved")
    ledger.check(not receipt.delivery_authorized, "receipt no delivery authority")
    ledger.check(not receipt.delivered, "receipt not delivered")

    inactive_authority = realization.with_expected_id(
        replace(
            realization_input.realization_authority_record,
            realization_authority_record_id="pending",
            authority_active=False,
            surface_realization_authorized=False,
            containment_realization_authorized=False,
            expression_candidate_creation_authorized=False,
        )
    )
    inactive_input = realization.with_expected_id(
        replace(
            realization_input,
            realization_input_id="pending",
            realization_authority_record=inactive_authority,
        )
    )
    ledger.check(
        not realization.validate_surface_realization_input(inactive_input).ok,
        "inactive realization authority rejected",
    )

    custody_tampered_authority = realization.with_expected_id(
        replace(
            realization_input.realization_authority_record,
            realization_authority_record_id="pending",
            selected_meaning_source_custody_ref=(
                "selected-meaning-custody:fabricated"
            ),
        )
    )
    custody_tampered_input = realization.with_expected_id(
        replace(
            realization_input,
            realization_input_id="pending",
            realization_authority_record=custody_tampered_authority,
        )
    )
    ledger.check(
        not realization.validate_surface_realization_input(
            custody_tampered_input
        ).ok,
        "authority selected-meaning custody tamper rejected",
    )

    bad_resource = realization.with_expected_id(
        replace(
            realization_input.controlled_resource_bundle.records[1],
            resource_record_id="pending",
            admitted=False,
        )
    )
    bad_bundle = realization.with_expected_id(
        replace(
            realization_input.controlled_resource_bundle,
            resource_bundle_id="pending",
            records=(
                realization_input.controlled_resource_bundle.records[0],
                bad_resource,
                *realization_input.controlled_resource_bundle.records[2:],
            ),
        )
    )
    bad_bundle_input = realization.with_expected_id(
        replace(
            realization_input,
            realization_input_id="pending",
            controlled_resource_bundle=bad_bundle,
            realization_authority_record=realization.with_expected_id(
                replace(
                    realization_input.realization_authority_record,
                    realization_authority_record_id="pending",
                    controlled_resource_bundle_ref=bad_bundle.resource_bundle_id,
                )
            ),
        )
    )
    ledger.check(
        not realization.validate_surface_realization_input(bad_bundle_input).ok,
        "unadmitted resource rejected",
    )

    version_tampered_resource = realization.with_expected_id(
        replace(
            realization_input.controlled_resource_bundle.records[0],
            resource_record_id="pending",
            resource_version="v999.0.0",
        )
    )
    version_tampered_bundle = realization.with_expected_id(
        replace(
            realization_input.controlled_resource_bundle,
            resource_bundle_id="pending",
            records=(
                version_tampered_resource,
                *realization_input.controlled_resource_bundle.records[1:],
            ),
        )
    )
    version_tampered_authority = realization.with_expected_id(
        replace(
            realization_input.realization_authority_record,
            realization_authority_record_id="pending",
            controlled_resource_bundle_ref=(
                version_tampered_bundle.resource_bundle_id
            ),
        )
    )
    version_tampered_input = realization.with_expected_id(
        replace(
            realization_input,
            realization_input_id="pending",
            controlled_resource_bundle=version_tampered_bundle,
            realization_authority_record=version_tampered_authority,
        )
    )
    ledger.check(
        not realization.validate_surface_realization_input(
            version_tampered_input
        ).ok,
        "resource version tamper rejected",
    )

    request_fields = (
        "free_form_generation_requested",
        "unadmitted_rule_requested",
        "unadmitted_resource_requested",
        "claim_invention_requested",
        "claim_strengthening_requested",
        "scope_expansion_requested",
        "certainty_upgrade_requested",
        "evidence_status_upgrade_requested",
        "limitation_omission_requested",
        "qualification_omission_requested",
        "caveat_omission_requested",
        "refusal_softening_requested",
        "unresolved_resolution_requested",
        "ambiguity_erasure_requested",
        "unsupported_state_erasure_requested",
        "selected_meaning_rewrite_requested",
        "downstream_authority_requested",
    )
    for field_name in request_fields:
        bad = realization.with_expected_id(
            replace(
                realization_input,
                realization_input_id="pending",
                **{field_name: True},
            )
        )
        ledger.check(
            not realization.validate_surface_realization_input(bad).ok,
            "prohibited request rejected " + field_name,
        )

    text_tampered = reidentified_result(
        realization,
        result,
        realized_text=candidate.realized_text + " This is proven.",
    )
    ledger.check(
        not realization.validate_surface_realization_result(
            text_tampered,
            realization_input=realization_input,
        ).ok,
        "text strengthening tamper rejected",
    )
    certainty_tampered = reidentified_result(
        realization,
        result,
        certainty_level_refs=altered_tuple(
            candidate.certainty_level_refs,
            "certainty:fabricated",
        ),
    )
    ledger.check(
        not realization.validate_surface_realization_result(
            certainty_tampered,
            realization_input=realization_input,
        ).ok,
        "certainty omission rejected",
    )
    caveat_tampered = reidentified_result(
        realization,
        result,
        required_caveat_refs=altered_tuple(
            candidate.required_caveat_refs,
            "caveat:fabricated",
        ),
    )
    ledger.check(
        not realization.validate_surface_realization_result(
            caveat_tampered,
            realization_input=realization_input,
        ).ok,
        "caveat omission rejected",
    )
    resource_ref_tampered = reidentified_result(
        realization,
        result,
        applied_resource_refs=("surface-resource:fabricated",),
    )
    ledger.check(
        not realization.validate_surface_realization_result(
            resource_ref_tampered,
            realization_input=realization_input,
        ).ok,
        "applied resource identity tamper rejected",
    )
    trace_tampered = realization.with_expected_id(
        replace(
            trace,
            realization_trace_id="pending",
            segment_sha256s=("0" * 64,),
        )
    )
    trace_result = realization.with_expected_result_identity(
        replace(result, realization_trace=trace_tampered)
    )
    ledger.check(
        not realization.validate_surface_realization_result(
            trace_result,
            realization_input=realization_input,
        ).ok,
        "trace tamper rejected",
    )
    receipt_tampered = realization.with_expected_id(
        replace(
            receipt,
            realization_receipt_id="pending",
            echo_approved=True,
        )
    )
    receipt_result = realization.with_expected_result_identity(
        replace(result, realization_receipt=receipt_tampered)
    )
    ledger.check(
        not realization.validate_surface_realization_result(
            receipt_result,
            realization_input=realization_input,
        ).ok,
        "Echo approval tamper rejected",
    )

    print("AI.WEB SLICE 42F DETERMINISTIC SURFACE REALIZATION TEST")
    print(f"check_count={ledger.check_count}")
    print("source_plan_disposition=" + result.source_plan_disposition.value)
    print("realization_disposition=" + result.disposition.value)
    print("surface_realization_performed=" + str(int(result.surface_realization_performed)))
    print("human_readable_text_produced=" + str(int(result.human_readable_text_produced)))
    print("expression_candidate_created=" + str(int(result.expression_candidate_created)))
    print("realized_text_sha256=" + candidate.realized_text_sha256)
    print("realized_segment_count=" + str(len(candidate.segments)))
    print("refusal_language_produced=" + str(int(result.refusal_language_produced)))
    print("authorized_claim_strengthened=0")
    print("certainty_upgraded=0")
    print("evidence_status_upgraded=0")
    print("caveats_and_unresolved_visible=1")
    print("deterministic_trace_created=1")
    print("deterministic_receipt_created=1")
    print("unvalidated_expression_candidate=1")
    print("echo_approved=0")
    print("delivery_authorized=0")
    print("delivered=0")
    print("failure_count=" + str(len(ledger.failures)))
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures:
        print("AI.WEB SLICE 42F BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 42F BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
