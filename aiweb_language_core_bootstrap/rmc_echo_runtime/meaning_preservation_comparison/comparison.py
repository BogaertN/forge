"""Deterministic Slice 43D meaning-preservation comparison."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from ..authorized_source_admission import (
    SourceAdmissionResult,
)
from ...outward_expression_runtime.disabled_outward_expression_closeout import (
    DisabledOutwardExpressionCloseoutResult,
)
from .authority import (
    COMPARISON_DIMENSION_VALUES,
    COMPARISON_RULE_REF_MAP,
    EXACT_ACCEPTED_SLICE43C_ID_MAP,
    REQUESTED_OPERATION,
)
from .identity import (
    with_expected_id,
    with_expected_package_identity,
    with_expected_result_identity,
    with_expected_snapshot_identity,
)
from .rules import (
    outcome_for_snapshots,
    source_objects,
    status_for_codes,
    unique_values,
)
from .schema import (
    ComparisonCode,
    ComparisonExecutionStatus,
    DimensionValueSnapshot,
    FindingOutcome,
    MeaningPreservationComparisonPackage,
    MeaningPreservationComparisonRequest,
    MeaningPreservationComparisonResult,
    MeaningPreservationDimension,
    MeaningPreservationFinding,
    SnapshotSide,
)
from .validation import validate_comparison_inputs, validate_result


def build_comparison_request(
    source_admission_result: SourceAdmissionResult,
    source_closeout_result: DisabledOutwardExpressionCloseoutResult,
) -> MeaningPreservationComparisonRequest:
    request = MeaningPreservationComparisonRequest(
        request_id="",
        source_admission_result_ref=source_admission_result.admission_result_id,
        source_closeout_result_ref=source_closeout_result.result_id,
        requested_operation=REQUESTED_OPERATION,
        raw_text=None,
        explicit_comparison_request=True,
    )
    return with_expected_id(request)


def make_dimension_snapshot(
    *,
    dimension: MeaningPreservationDimension,
    side: SnapshotSide,
    field_paths: tuple[str, ...],
    values: tuple[str, ...],
    evidence_refs: tuple[str, ...] = (),
    trace_refs: tuple[str, ...] = (),
    supported: bool = True,
    conflict_refs: tuple[str, ...] = (),
    indeterminate_refs: tuple[str, ...] = (),
) -> DimensionValueSnapshot:
    snapshot = DimensionValueSnapshot(
        snapshot_id="",
        dimension=dimension,
        side=side,
        field_paths=field_paths,
        values=values,
        evidence_refs=unique_values(evidence_refs),
        trace_refs=unique_values(trace_refs),
        supported=supported,
        conflict_refs=unique_values(conflict_refs),
        indeterminate_refs=unique_values(indeterminate_refs),
        value_digest="",
    )
    return with_expected_snapshot_identity(snapshot)


def build_dimension_finding(
    *,
    comparison_request_ref: str,
    source_admission_result_ref: str,
    validation_input_boundary_ref: str,
    source_snapshot: DimensionValueSnapshot,
    proposed_snapshot: DimensionValueSnapshot,
) -> MeaningPreservationFinding:
    outcome = outcome_for_snapshots(source_snapshot, proposed_snapshot)
    reason_refs = {
        FindingOutcome.PRESERVED: ("slice43d-finding:exact-values-preserved",),
        FindingOutcome.CHANGED: ("slice43d-finding:exact-values-changed",),
        FindingOutcome.MISSING: ("slice43d-finding:required-value-missing",),
        FindingOutcome.UNSUPPORTED: ("slice43d-finding:comparison-unsupported",),
        FindingOutcome.CONFLICTED: ("slice43d-finding:conflicting-values",),
        FindingOutcome.INDETERMINATE: ("slice43d-finding:indeterminate-values",),
    }[outcome]
    finding = MeaningPreservationFinding(
        finding_id="",
        comparison_request_ref=comparison_request_ref,
        source_admission_result_ref=source_admission_result_ref,
        validation_input_boundary_ref=validation_input_boundary_ref,
        dimension=source_snapshot.dimension,
        outcome=outcome,
        source_snapshot=source_snapshot,
        proposed_snapshot=proposed_snapshot,
        comparison_rule_ref=COMPARISON_RULE_REF_MAP[
            source_snapshot.dimension.value
        ],
        evidence_refs=unique_values(
            source_snapshot.evidence_refs,
            proposed_snapshot.evidence_refs,
        ),
        trace_refs=unique_values(
            source_snapshot.trace_refs,
            proposed_snapshot.trace_refs,
        ),
        reason_refs=reason_refs,
        exact_value_equality=(
            bool(source_snapshot.values)
            and source_snapshot.values == proposed_snapshot.values
        ),
        required_value_missing=(
            not source_snapshot.values or not proposed_snapshot.values
        ),
        finding_only=True,
        drift_classified=False,
        materiality_decided=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        expression_rewritten=False,
    )
    return with_expected_id(finding)


def _snapshot_pair(
    *,
    dimension: MeaningPreservationDimension,
    source_paths: tuple[str, ...],
    proposed_paths: tuple[str, ...],
    source_values: tuple[str, ...],
    proposed_values: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    trace_refs: tuple[str, ...],
) -> tuple[DimensionValueSnapshot, DimensionValueSnapshot]:
    source = make_dimension_snapshot(
        dimension=dimension,
        side=SnapshotSide.SOURCE,
        field_paths=source_paths,
        values=source_values,
        evidence_refs=evidence_refs,
        trace_refs=trace_refs,
    )
    proposed = make_dimension_snapshot(
        dimension=dimension,
        side=SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=proposed_paths,
        values=proposed_values,
        evidence_refs=evidence_refs,
        trace_refs=trace_refs,
    )
    return source, proposed


def _dimension_snapshot_pairs(
    source_closeout_result: DisabledOutwardExpressionCloseoutResult,
    source_admission_result: SourceAdmissionResult,
) -> tuple[tuple[DimensionValueSnapshot, DimensionValueSnapshot], ...]:
    objects = source_objects(source_closeout_result)
    package = source_admission_result.admission_package
    assert package is not None
    selected = objects["selected_record"]
    selected_result = objects["selected_result"]
    candidate = objects["candidate"]
    outward = objects["outward"]
    obligation = objects["obligation_package"]
    plan = objects["expression_plan"]
    eligibility = objects["eligibility_result"]

    common_evidence = unique_values(
        (
            source_admission_result.admission_result_id,
            package.admission_package_id,
            package.validation_input_boundary.validation_input_boundary_id,
            source_closeout_result.result_id,
            source_closeout_result.acceptance_record.record_id,
            obligation.obligation_package_id,
            plan.expression_plan_id,
            candidate.expression_candidate_id,
            outward.record_id,
            objects["expression_link"].record_id,
        ),
        package.source_receipt_refs,
    )
    common_trace = unique_values(
        package.source_trace_refs,
        tuple(candidate.trace_refs),
    )

    semantic_source = (
        selected.record_id,
        selected.selected_candidate_ref,
        selected_result.companion.content_proof_ref,
    )
    semantic_proposed = tuple(
        value
        for value in semantic_source
        if value in candidate.selected_meaning_refs
    )

    purpose_source = (
        f"communicative_act:{selected.communicative_act}",
        "purpose_boundary:permission_versus_request",
    )
    purpose_proposed_values: list[str] = []
    if selected.record_id in candidate.selected_meaning_refs:
        purpose_proposed_values.append(
            f"communicative_act:{selected.communicative_act}"
        )
    if "permission_versus_request" in candidate.preservation_class_refs:
        purpose_proposed_values.append(
            "purpose_boundary:permission_versus_request"
        )

    claim_source = (
        "claim_status:nonaffirmative_blocked",
        "validation_status:unvalidated",
    )
    claim_proposed: list[str] = []
    if (
        eligibility.outcome.value == "blocked"
        and plan.disposition.value == "blocked_consequence_plan"
        and "affirmative-claim-authorized:false" in outward.permitted_claims
        and candidate.disposition.value == "blocked_expression_candidate"
        and candidate.authorized_claim_not_strengthened
    ):
        claim_proposed.append("claim_status:nonaffirmative_blocked")
    if candidate.unvalidated_expression_candidate and not candidate.echo_approved:
        claim_proposed.append("validation_status:unvalidated")

    caveat_source = unique_values(
        tuple(obligation.inherited_limitation_refs),
        tuple(obligation.required_caveat_refs),
        tuple(plan.required_qualification_refs),
    )
    caveat_proposed = unique_values(
        tuple(candidate.inherited_limitation_refs),
        tuple(candidate.required_caveat_refs),
        tuple(candidate.required_qualification_refs),
    )

    refusal_source = (
        "refusal_state:required",
        "claim_status:nonaffirmative",
    ) if plan.blocked_consequence_plan else tuple(
        obligation.refusal_relevant_boundary_refs
    )
    refusal_proposed: tuple[str, ...]
    if (
        candidate.refusal_language_produced
        and candidate.disposition.value == "blocked_expression_candidate"
    ):
        refusal_proposed = (
            "refusal_state:required",
            "claim_status:nonaffirmative",
        )
    else:
        refusal_proposed = tuple(candidate.refusal_relevant_boundary_refs)

    unresolved_source = unique_values(
        tuple(obligation.unresolved_condition_refs),
        tuple(obligation.ambiguity_refs),
        tuple(obligation.unsupported_state_refs),
    )
    unresolved_proposed = unique_values(
        tuple(candidate.unresolved_condition_refs),
        tuple(candidate.ambiguity_refs),
        tuple(candidate.unsupported_state_refs),
    )

    action_source = (
        "action_status:not_authorized",
        "execution_status:not_authorized",
    )
    action_proposed: list[str] = []
    if not candidate.action_performed:
        action_proposed.append("action_status:not_authorized")
    if not candidate.execution_authorized:
        action_proposed.append("execution_status:not_authorized")

    memory_source = unique_values(
        tuple(obligation.memory_authority_refs),
        ("memory_write:false",),
    )
    memory_proposed = unique_values(
        tuple(candidate.memory_authority_refs),
        (
            "memory_write:false"
            if not candidate.memory_accessed_or_written
            else "memory_write:true",
        ),
    )

    delivery_source = unique_values(
        tuple(obligation.delivery_authority_refs),
        ("delivery_performed:false",),
    )
    delivery_proposed = unique_values(
        tuple(candidate.delivery_authority_refs),
        (
            "delivery_performed:false"
            if not candidate.delivered
            else "delivery_performed:true",
        ),
    )

    next_step_source = (
        "next_step:echo_validation",
        "hold_status:unvalidated_no_delivery",
    )
    next_step_proposed: list[str] = []
    if candidate.unvalidated_expression_candidate:
        next_step_proposed.append("next_step:echo_validation")
    if not candidate.echo_approved and not candidate.delivery_authorized:
        next_step_proposed.append("hold_status:unvalidated_no_delivery")

    pairs = (
        _snapshot_pair(
            dimension=MeaningPreservationDimension.SEMANTIC_CONTENT,
            source_paths=(
                "selected_record.record_id",
                "selected_record.selected_candidate_ref",
                "selected_result.companion.content_proof_ref",
            ),
            proposed_paths=("candidate.selected_meaning_refs",),
            source_values=semantic_source,
            proposed_values=semantic_proposed,
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.COMMUNICATIVE_PURPOSE,
            source_paths=(
                "selected_record.communicative_act",
                "selected_record.preservation_classes",
            ),
            proposed_paths=(
                "candidate.selected_meaning_refs",
                "candidate.preservation_class_refs",
            ),
            source_values=purpose_source,
            proposed_values=tuple(purpose_proposed_values),
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.CLAIM_STATUS,
            source_paths=(
                "eligibility_result.outcome",
                "expression_plan.disposition",
                "outward.permitted_claims",
            ),
            proposed_paths=(
                "candidate.disposition",
                "candidate.authorized_claim_not_strengthened",
                "candidate.unvalidated_expression_candidate",
            ),
            source_values=claim_source,
            proposed_values=tuple(claim_proposed),
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.SCOPE,
            source_paths=("obligation.active_scope_refs",),
            proposed_paths=("candidate.active_scope_refs",),
            source_values=tuple(obligation.active_scope_refs),
            proposed_values=tuple(candidate.active_scope_refs),
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.CERTAINTY,
            source_paths=("obligation.certainty_level_refs",),
            proposed_paths=("candidate.certainty_level_refs",),
            source_values=tuple(obligation.certainty_level_refs),
            proposed_values=tuple(candidate.certainty_level_refs),
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.EVIDENCE_STATUS,
            source_paths=("obligation.evidence_status_refs",),
            proposed_paths=("candidate.evidence_status_refs",),
            source_values=tuple(obligation.evidence_status_refs),
            proposed_values=tuple(candidate.evidence_status_refs),
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.CAVEATS_AND_LIMITATIONS,
            source_paths=(
                "obligation.inherited_limitation_refs",
                "obligation.required_caveat_refs",
                "expression_plan.required_qualification_refs",
            ),
            proposed_paths=(
                "candidate.inherited_limitation_refs",
                "candidate.required_caveat_refs",
                "candidate.required_qualification_refs",
            ),
            source_values=caveat_source,
            proposed_values=caveat_proposed,
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.REFUSAL_STATE,
            source_paths=(
                "expression_plan.blocked_consequence_plan",
                "obligation.refusal_relevant_boundary_refs",
            ),
            proposed_paths=(
                "candidate.refusal_language_produced",
                "candidate.refusal_relevant_boundary_refs",
                "candidate.disposition",
            ),
            source_values=refusal_source,
            proposed_values=refusal_proposed,
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.UNRESOLVED_CONDITIONS,
            source_paths=(
                "obligation.unresolved_condition_refs",
                "obligation.ambiguity_refs",
                "obligation.unsupported_state_refs",
            ),
            proposed_paths=(
                "candidate.unresolved_condition_refs",
                "candidate.ambiguity_refs",
                "candidate.unsupported_state_refs",
            ),
            source_values=unresolved_source,
            proposed_values=unresolved_proposed,
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.ACTION_STATUS,
            source_paths=(
                "eligibility_result.outcome",
                "eligibility_result.admission_record.blocked_consequence_refs",
            ),
            proposed_paths=(
                "candidate.action_performed",
                "candidate.execution_authorized",
            ),
            source_values=action_source,
            proposed_values=tuple(action_proposed),
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.MEMORY_STATUS,
            source_paths=("obligation.memory_authority_refs",),
            proposed_paths=(
                "candidate.memory_authority_refs",
                "candidate.memory_accessed_or_written",
            ),
            source_values=memory_source,
            proposed_values=memory_proposed,
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=MeaningPreservationDimension.DELIVERY_STATUS,
            source_paths=("obligation.delivery_authority_refs",),
            proposed_paths=(
                "candidate.delivery_authority_refs",
                "candidate.delivered",
            ),
            source_values=delivery_source,
            proposed_values=delivery_proposed,
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
        _snapshot_pair(
            dimension=(
                MeaningPreservationDimension.REQUIRED_NEXT_STEP_OR_HOLD_STATUS
            ),
            source_paths=(
                "candidate.unvalidated_expression_candidate",
                "source_closeout_result.expression_candidate_remains_unvalidated",
            ),
            proposed_paths=(
                "candidate.unvalidated_expression_candidate",
                "candidate.echo_approved",
                "candidate.delivery_authorized",
            ),
            source_values=next_step_source,
            proposed_values=tuple(next_step_proposed),
            evidence_refs=common_evidence,
            trace_refs=common_trace,
        ),
    )
    return pairs


def _held_result(
    request: object,
    source_admission_result: object,
    source_closeout_result: object,
    issue_codes: tuple[ComparisonCode, ...],
    reason_refs: tuple[str, ...],
) -> MeaningPreservationComparisonResult:
    request_ref = getattr(request, "request_id", "invalid-request")
    admission_ref = getattr(
        source_admission_result,
        "admission_result_id",
        "invalid-admission-result",
    )
    closeout_ref = getattr(
        source_closeout_result,
        "result_id",
        "invalid-closeout-result",
    )
    result = MeaningPreservationComparisonResult(
        comparison_result_id="",
        comparison_result_digest="",
        status=status_for_codes(issue_codes),
        issue_codes=issue_codes,
        reason_refs=reason_refs,
        comparison_request_ref=request_ref,
        source_admission_result_ref=admission_ref,
        source_closeout_result_ref=closeout_ref,
        comparison_package=None,
        comparison_performed=False,
        findings_created=False,
        dimension_finding_count=0,
        preserved_finding_count=0,
        changed_finding_count=0,
        missing_finding_count=0,
        unsupported_finding_count=0,
        conflicted_finding_count=0,
        indeterminate_finding_count=0,
        aggregate_pass_rejected_contained_decided=False,
        drift_classification_performed=False,
        materiality_decided=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        expression_rewritten=False,
        msm_v1_modified_or_integrated=False,
        delivered=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    return with_expected_result_identity(result)


def compare_meaning_preservation(
    request: object,
    source_admission_result: object,
    source_closeout_result: object,
) -> MeaningPreservationComparisonResult:
    report = validate_comparison_inputs(
        request,
        source_admission_result,
        source_closeout_result,
    )
    if not report.ok:
        codes = tuple(dict.fromkeys(item.code for item in report.issues))
        reasons = tuple(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        return _held_result(
            request,
            source_admission_result,
            source_closeout_result,
            codes,
            reasons,
        )

    assert isinstance(request, MeaningPreservationComparisonRequest)
    assert isinstance(source_admission_result, SourceAdmissionResult)
    assert isinstance(
        source_closeout_result,
        DisabledOutwardExpressionCloseoutResult,
    )
    package43c = source_admission_result.admission_package
    assert package43c is not None

    findings = tuple(
        build_dimension_finding(
            comparison_request_ref=request.request_id,
            source_admission_result_ref=(
                source_admission_result.admission_result_id
            ),
            validation_input_boundary_ref=(
                package43c.validation_input_boundary.validation_input_boundary_id
            ),
            source_snapshot=source_snapshot,
            proposed_snapshot=proposed_snapshot,
        )
        for source_snapshot, proposed_snapshot in _dimension_snapshot_pairs(
            source_closeout_result,
            source_admission_result,
        )
    )

    comparison_package = MeaningPreservationComparisonPackage(
        comparison_package_id="",
        comparison_package_digest="",
        comparison_request_ref=request.request_id,
        source_admission_result_ref=source_admission_result.admission_result_id,
        source_admission_package_ref=package43c.admission_package_id,
        source_closeout_result_ref=source_closeout_result.result_id,
        validation_input_boundary_ref=(
            package43c.validation_input_boundary.validation_input_boundary_id
        ),
        findings=findings,
        comparison_dimension_values=COMPARISON_DIMENSION_VALUES,
        finding_count=len(findings),
        comparison_performed=True,
        findings_created=True,
        aggregate_pass_rejected_contained_decided=False,
        drift_classification_performed=False,
        materiality_decided=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        expression_rewritten=False,
        msm_v1_modified_or_integrated=False,
        delivery_authorized_or_performed=False,
        truth_evidence_permission_execution_authority=False,
        route_api_network_filesystem_memory_tool_action_authority=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    comparison_package = with_expected_package_identity(comparison_package)

    counts = {
        outcome: sum(item.outcome is outcome for item in findings)
        for outcome in FindingOutcome
    }
    result = MeaningPreservationComparisonResult(
        comparison_result_id="",
        comparison_result_digest="",
        status=ComparisonExecutionStatus.FINDINGS_CREATED,
        issue_codes=(),
        reason_refs=(
            "slice43d:dimension-specific-findings-created",
            "slice43d:no-aggregate-disposition",
        ),
        comparison_request_ref=request.request_id,
        source_admission_result_ref=source_admission_result.admission_result_id,
        source_closeout_result_ref=source_closeout_result.result_id,
        comparison_package=comparison_package,
        comparison_performed=True,
        findings_created=True,
        dimension_finding_count=len(findings),
        preserved_finding_count=counts[FindingOutcome.PRESERVED],
        changed_finding_count=counts[FindingOutcome.CHANGED],
        missing_finding_count=counts[FindingOutcome.MISSING],
        unsupported_finding_count=counts[FindingOutcome.UNSUPPORTED],
        conflicted_finding_count=counts[FindingOutcome.CONFLICTED],
        indeterminate_finding_count=counts[FindingOutcome.INDETERMINATE],
        aggregate_pass_rejected_contained_decided=False,
        drift_classification_performed=False,
        materiality_decided=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        expression_rewritten=False,
        msm_v1_modified_or_integrated=False,
        delivered=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    result = with_expected_result_identity(result)
    result_report = validate_result(result)
    if not result_report.ok:
        return _held_result(
            request,
            source_admission_result,
            source_closeout_result,
            tuple(dict.fromkeys(item.code for item in result_report.issues)),
            tuple(
                f"{item.path}:{item.code.value}:{item.detail}"
                for item in result_report.issues
            ),
        )
    return result


__all__ = (
    "build_comparison_request",
    "build_dimension_finding",
    "compare_meaning_preservation",
    "make_dimension_snapshot",
)
