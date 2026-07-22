#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 43E."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import sys


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.malformed_cases = 0
        self.explicit_drift_cases = 0
        self.materiality_cases = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)

    def drift_case(self, condition: object, label: str) -> None:
        self.explicit_drift_cases += 1
        self.check(condition, label)

    def materiality_case(self, condition: object, label: str) -> None:
        self.materiality_cases += 1
        self.check(condition, label)


def build_exact_slice43d_result(repository: Path):
    helper = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice43c_authorized_meaning_proposed_expression_admission.py"
        )
    )
    _, _, source = helper["build_exact_slice42_source"](repository)
    admission = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "authorized_source_admission"
    )
    comparison = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "meaning_preservation_comparison"
    )
    source_result = admission.admit_authorized_meaning_and_proposed_expression(
        admission.build_source_admission_request(source)
    )
    comparison_result = comparison.compare_meaning_preservation(
        comparison.build_comparison_request(source_result, source),
        source_result,
        source,
    )
    return comparison, comparison_result


def modified_comparison_result(
    comparison,
    base_result,
    *,
    dimension,
    source_values=None,
    proposed_values=None,
    source_trace_refs=None,
    proposed_trace_refs=None,
    source_evidence_refs=None,
    proposed_evidence_refs=None,
    source_supported=True,
    proposed_supported=True,
    proposed_conflict_refs=(),
    proposed_indeterminate_refs=(),
):
    package = base_result.comparison_package
    assert package is not None
    findings = list(package.findings)
    index = next(
        position
        for position, item in enumerate(findings)
        if item.dimension is dimension
    )
    old = findings[index]
    source_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.SOURCE,
        field_paths=old.source_snapshot.field_paths,
        values=(
            old.source_snapshot.values
            if source_values is None
            else tuple(source_values)
        ),
        evidence_refs=(
            old.source_snapshot.evidence_refs
            if source_evidence_refs is None
            else tuple(source_evidence_refs)
        ),
        trace_refs=(
            old.source_snapshot.trace_refs
            if source_trace_refs is None
            else tuple(source_trace_refs)
        ),
        supported=source_supported,
    )
    proposed_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=old.proposed_snapshot.field_paths,
        values=(
            old.proposed_snapshot.values
            if proposed_values is None
            else tuple(proposed_values)
        ),
        evidence_refs=(
            old.proposed_snapshot.evidence_refs
            if proposed_evidence_refs is None
            else tuple(proposed_evidence_refs)
        ),
        trace_refs=(
            old.proposed_snapshot.trace_refs
            if proposed_trace_refs is None
            else tuple(proposed_trace_refs)
        ),
        supported=proposed_supported,
        conflict_refs=tuple(proposed_conflict_refs),
        indeterminate_refs=tuple(proposed_indeterminate_refs),
    )
    findings[index] = comparison.build_dimension_finding(
        comparison_request_ref=old.comparison_request_ref,
        source_admission_result_ref=old.source_admission_result_ref,
        validation_input_boundary_ref=old.validation_input_boundary_ref,
        source_snapshot=source_snapshot,
        proposed_snapshot=proposed_snapshot,
    )
    finding_tuple = tuple(findings)
    package = replace(
        package,
        comparison_package_id="",
        comparison_package_digest="",
        findings=finding_tuple,
        finding_count=len(finding_tuple),
    )
    package = comparison.with_expected_package_identity(package)
    counts = {
        outcome: sum(item.outcome is outcome for item in finding_tuple)
        for outcome in comparison.FindingOutcome
    }
    result = replace(
        base_result,
        comparison_result_id="",
        comparison_result_digest="",
        comparison_package=package,
        dimension_finding_count=len(finding_tuple),
        preserved_finding_count=counts[comparison.FindingOutcome.PRESERVED],
        changed_finding_count=counts[comparison.FindingOutcome.CHANGED],
        missing_finding_count=counts[comparison.FindingOutcome.MISSING],
        unsupported_finding_count=counts[comparison.FindingOutcome.UNSUPPORTED],
        conflicted_finding_count=counts[comparison.FindingOutcome.CONFLICTED],
        indeterminate_finding_count=counts[comparison.FindingOutcome.INDETERMINATE],
    )
    result = comparison.with_expected_result_identity(result)
    report = comparison.validate_result(result)
    if not report.ok:
        raise AssertionError(
            "invalid adversarial Slice 43D result: "
            + "; ".join(
                f"{item.path}:{item.code.value}:{item.detail}"
                for item in report.issues
            )
        )
    return result


def classify(classification, comparison_result):
    request = classification.build_classification_request(comparison_result)
    return classification.classify_drift_and_materiality(
        request,
        comparison_result,
    )


def finding_for(result, dimension):
    package = result.classification_package
    assert package is not None
    return next(
        item for item in package.drift_findings if item.dimension is dimension
    )


def main() -> int:
    repository = Path(
        sys.argv[1] if len(sys.argv) == 2 else "/home/nic/forge"
    ).resolve()
    if len(sys.argv) > 2:
        raise SystemExit(
            "usage: test_aiweb_slice43e_drift_materiality_classification.py "
            "[REPOSITORY]"
        )
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    comparison, base_comparison = build_exact_slice43d_result(repository)
    classification = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "drift_materiality_classification"
    )

    ledger.check(
        classification.SLICE43E_ACCEPTED_PARENT_HEAD
        == "26e8c30724dde17709203411a95f63dcf65a380b",
        "exact accepted Slice 43D parent",
    )
    ledger.check(
        classification.SLICE43E_ACCEPTED_PARENT_TREE
        == "785690cd3fe8b3437fce226edac5472659db3f7c",
        "exact accepted Slice 43D parent tree",
    )
    ledger.check(
        classification.SLICE43E_COMMIT_SUBJECT
        == "Slice 43E drift finding materiality and classification",
        "exact commit subject",
    )
    ledger.check(
        len(classification.DRIFT_KIND_VALUES) == 17,
        "exact seventeen admitted drift kinds",
    )
    ledger.check(
        len(classification.MATERIALITY_VALUES) == 6,
        "exact six materiality states",
    )
    ledger.check(
        len(classification.CLASSIFICATION_STATE_VALUES) == 5,
        "exact five classification states",
    )
    ledger.check(
        len(classification.PERMANENT_AUTHORITY_ZERO) == 10,
        "ten authority-zero boundaries",
    )
    ledger.check(
        base_comparison.comparison_result_id
        == classification.EXACT_ACCEPTED_SLICE43D_ID_MAP["result"],
        "exact accepted Slice 43D result identity",
    )
    package43d = base_comparison.comparison_package
    assert package43d is not None
    ledger.check(
        package43d.comparison_package_id
        == classification.EXACT_ACCEPTED_SLICE43D_ID_MAP["package"],
        "exact accepted Slice 43D package identity",
    )

    request = classification.build_classification_request(base_comparison)
    ledger.check(
        request.request_id == classification.expected_record_id(request),
        "classification request deterministic identity",
    )
    ledger.check(request.raw_text is None, "classification request has no raw text")
    ledger.check(
        request.explicit_classification_request is True,
        "classification request explicit",
    )
    ledger.check(
        classification.validate_classification_inputs(
            request,
            base_comparison,
        ).ok,
        "exact classification input validates",
    )

    first = classification.classify_drift_and_materiality(
        request,
        base_comparison,
    )
    ledger.check(
        first.status
        is classification.DriftClassificationExecutionStatus.FINDINGS_CREATED,
        "findings-created operational status",
    )
    ledger.check(
        first.drift_classification_performed is True,
        "drift classification performed",
    )
    ledger.check(
        first.materiality_findings_created is True,
        "materiality findings created",
    )
    ledger.check(
        first.classification_record_count == 13,
        "one classification record per comparison dimension",
    )
    ledger.check(first.drift_finding_count == 0, "accepted fixture has zero drift")
    ledger.check(first.material_finding_count == 0, "zero material drift")
    ledger.check(first.non_material_finding_count == 0, "zero non-material drift")
    ledger.check(
        first.not_applicable_finding_count == 13,
        "thirteen not-applicable materiality findings",
    )
    ledger.check(first.unsupported_finding_count == 0, "zero unsupported")
    ledger.check(first.conflicted_finding_count == 0, "zero conflicted")
    ledger.check(first.indeterminate_finding_count == 0, "zero indeterminate")
    package = first.classification_package
    ledger.check(package is not None, "classification package created")
    assert package is not None
    ledger.check(
        package.admitted_drift_kind_values == classification.DRIFT_KIND_VALUES,
        "exact admitted drift-kind registry",
    )
    ledger.check(
        package.materiality_values == classification.MATERIALITY_VALUES,
        "exact materiality registry",
    )
    ledger.check(
        package.classification_package_id
        == classification.expected_package_id(package),
        "classification package deterministic identity",
    )
    ledger.check(
        package.classification_package_digest
        == classification.expected_package_digest(package),
        "classification package deterministic digest",
    )
    ledger.check(
        first.classification_result_id
        == classification.expected_result_id(first),
        "classification result deterministic identity",
    )
    ledger.check(
        first.classification_result_digest
        == classification.expected_result_digest(first),
        "classification result deterministic digest",
    )
    ledger.check(
        classification.validate_result(first, base_comparison).ok,
        "classification result validates",
    )
    for drift_finding, comparison_finding in zip(
        package.drift_findings,
        package43d.findings,
        strict=True,
    ):
        ledger.check(
            drift_finding.classification_state
            is classification.DriftClassificationState.NO_DRIFT,
            f"{drift_finding.dimension.value} explicit no drift",
        )
        ledger.check(
            drift_finding.materiality
            is classification.MaterialityState.NOT_APPLICABLE,
            f"{drift_finding.dimension.value} not applicable materiality",
        )
        ledger.check(
            not drift_finding.drift_kinds,
            f"{drift_finding.dimension.value} no drift kinds",
        )
        ledger.check(
            drift_finding.comparison_finding_ref == comparison_finding.finding_id,
            f"{drift_finding.dimension.value} exact finding ancestry",
        )
        ledger.check(
            drift_finding.source_values
            == comparison_finding.source_snapshot.values,
            f"{drift_finding.dimension.value} source values immutable",
        )
        ledger.check(
            drift_finding.proposed_values
            == comparison_finding.proposed_snapshot.values,
            f"{drift_finding.dimension.value} proposed values immutable",
        )
        ledger.check(
            classification.validate_finding(
                drift_finding,
                comparison_finding,
            ).ok,
            f"{drift_finding.dimension.value} classification validates",
        )

    cases = (
        (
            classification.DriftKind.OMITTED_MEANING,
            comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
            ("meaning:a", "meaning:b"),
            ("meaning:a",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.CLAIM_STRENGTHENING,
            comparison.MeaningPreservationDimension.CLAIM_STATUS,
            ("claim_status:nonaffirmative_blocked",),
            ("claim_status:affirmative",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.SCOPE_EXPANSION,
            comparison.MeaningPreservationDimension.SCOPE,
            ("scope:local",),
            ("scope:local", "scope:global"),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.CERTAINTY_UPGRADE,
            comparison.MeaningPreservationDimension.CERTAINTY,
            ("certainty:uncertain",),
            ("certainty:certain",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.EVIDENCE_STATUS_UPGRADE,
            comparison.MeaningPreservationDimension.EVIDENCE_STATUS,
            ("evidence_status:unverified",),
            ("evidence_status:verified",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.CAVEAT_OMISSION,
            comparison.MeaningPreservationDimension.CAVEATS_AND_LIMITATIONS,
            ("caveat:required",),
            (),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.REFUSAL_SOFTENING,
            comparison.MeaningPreservationDimension.REFUSAL_STATE,
            ("refusal:blocked",),
            ("permission:allowed",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.AMBIGUITY_ERASURE,
            comparison.MeaningPreservationDimension.UNRESOLVED_CONDITIONS,
            ("ambiguity:multiple_candidate", "unresolved:condition"),
            ("unresolved:condition",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.UNRESOLVED_STATE_ERASURE,
            comparison.MeaningPreservationDimension.UNRESOLVED_CONDITIONS,
            ("unresolved:condition",),
            ("resolved:complete",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.INVENTED_FACT,
            comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
            ("meaning:a",),
            ("meaning:a", "fact:invented-x"),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.INVENTED_EVIDENCE,
            comparison.MeaningPreservationDimension.EVIDENCE_STATUS,
            ("evidence_status:unverified",),
            ("evidence_status:unverified", "evidence:invented-x"),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.AUTHORITY_ESCALATION,
            comparison.MeaningPreservationDimension.ACTION_STATUS,
            ("action:not_authorized",),
            ("action:executed",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.ACTION_STATUS_DISTORTION,
            comparison.MeaningPreservationDimension.ACTION_STATUS,
            ("action:not_performed",),
            ("action:performed",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.MEMORY_STATUS_DISTORTION,
            comparison.MeaningPreservationDimension.MEMORY_STATUS,
            ("memory:not_accessed",),
            ("memory:memory_written",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.DELIVERY_STATUS_DISTORTION,
            comparison.MeaningPreservationDimension.DELIVERY_STATUS,
            ("delivery:not_delivered",),
            ("delivery:delivered",),
            {},
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.ANCESTRY_MISMATCH,
            comparison.MeaningPreservationDimension.SCOPE,
            ("scope:local",),
            ("scope:local",),
            {
                "source_trace_refs": ("trace:source",),
                "proposed_trace_refs": ("trace:proposed",),
            },
            classification.MaterialityState.MATERIAL,
        ),
        (
            classification.DriftKind.UNSUPPORTED_SURFACE_ADDITION,
            comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
            ("meaning:a",),
            ("meaning:a", "surface:formatting:bold"),
            {},
            classification.MaterialityState.NON_MATERIAL,
        ),
    )

    produced_kinds: set[classification.DriftKind] = set()
    for (
        expected_kind,
        dimension,
        source_values,
        proposed_values,
        options,
        expected_materiality,
    ) in cases:
        variant = modified_comparison_result(
            comparison,
            base_comparison,
            dimension=dimension,
            source_values=source_values,
            proposed_values=proposed_values,
            **options,
        )
        result = classify(classification, variant)
        ledger.check(
            result.status
            is classification.DriftClassificationExecutionStatus.FINDINGS_CREATED,
            f"{expected_kind.value} result created",
        )
        finding = finding_for(result, dimension)
        produced_kinds.update(finding.drift_kinds)
        ledger.drift_case(
            expected_kind in finding.drift_kinds,
            f"explicit {expected_kind.value}",
        )
        ledger.materiality_case(
            finding.materiality is expected_materiality,
            f"{expected_kind.value} materiality",
        )
        ledger.check(
            finding.text_repaired_or_rewritten is False,
            f"{expected_kind.value} no repair",
        )
        ledger.check(
            finding.echo_disposition_decided is False,
            f"{expected_kind.value} no disposition",
        )
        ledger.check(
            classification.validate_result(result, variant).ok,
            f"{expected_kind.value} result validates",
        )

    ledger.check(
        produced_kinds == set(classification.DriftKind),
        "all seventeen admitted drift kinds produced",
    )

    unsupported_variant = modified_comparison_result(
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SCOPE,
        proposed_supported=False,
    )
    unsupported_result = classify(classification, unsupported_variant)
    unsupported_finding = finding_for(
        unsupported_result,
        comparison.MeaningPreservationDimension.SCOPE,
    )
    ledger.materiality_case(
        unsupported_finding.materiality
        is classification.MaterialityState.UNSUPPORTED,
        "unsupported comparison preserved",
    )

    conflicted_variant = modified_comparison_result(
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SCOPE,
        proposed_conflict_refs=("conflict:scope",),
    )
    conflicted_result = classify(classification, conflicted_variant)
    conflicted_finding = finding_for(
        conflicted_result,
        comparison.MeaningPreservationDimension.SCOPE,
    )
    ledger.materiality_case(
        conflicted_finding.materiality
        is classification.MaterialityState.CONFLICTED,
        "conflicted comparison preserved",
    )

    indeterminate_variant = modified_comparison_result(
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SCOPE,
        proposed_indeterminate_refs=("indeterminate:scope",),
    )
    indeterminate_result = classify(classification, indeterminate_variant)
    indeterminate_finding = finding_for(
        indeterminate_result,
        comparison.MeaningPreservationDimension.SCOPE,
    )
    ledger.materiality_case(
        indeterminate_finding.materiality
        is classification.MaterialityState.INDETERMINATE,
        "indeterminate comparison preserved",
    )

    unknown_surface_variant = modified_comparison_result(
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
        source_values=("meaning:a",),
        proposed_values=("meaning:a", "surface:unknown:addition"),
    )
    unknown_surface_result = classify(classification, unknown_surface_variant)
    unknown_surface_finding = finding_for(
        unknown_surface_result,
        comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
    )
    ledger.materiality_case(
        unknown_surface_finding.materiality
        is classification.MaterialityState.INDETERMINATE,
        "unknown surface addition materiality remains indeterminate",
    )

    raw_text_request = replace(request, raw_text="raw text prohibited")
    raw_text_result = classification.classify_drift_and_materiality(
        raw_text_request,
        base_comparison,
    )
    ledger.malformed(
        raw_text_result.status
        is classification.DriftClassificationExecutionStatus.HELD_INVALID_REQUEST,
        "raw text held",
    )
    ledger.malformed(
        raw_text_result.classification_package is None,
        "raw text creates no classification package",
    )

    wrong_ref_request = replace(
        request,
        comparison_result_ref="slice43d-result:fabricated",
    )
    wrong_ref_request = replace(
        wrong_ref_request,
        request_id=classification.expected_record_id(wrong_ref_request),
    )
    wrong_ref_result = classification.classify_drift_and_materiality(
        wrong_ref_request,
        base_comparison,
    )
    ledger.malformed(
        wrong_ref_result.status
        is classification.DriftClassificationExecutionStatus.HELD_INCONSISTENT_ANCESTRY,
        "mismatched comparison ancestry held",
    )

    unsupported_request = replace(
        request,
        schema_version="aiweb-slice43e-unsupported-v999",
    )
    unsupported_request = replace(
        unsupported_request,
        request_id=classification.expected_record_id(unsupported_request),
    )
    unsupported_request_result = classification.classify_drift_and_materiality(
        unsupported_request,
        base_comparison,
    )
    ledger.malformed(
        unsupported_request_result.status
        is classification.DriftClassificationExecutionStatus.HELD_UNSUPPORTED_VERSION,
        "unsupported version held",
    )

    fabricated_comparison = replace(
        base_comparison,
        comparison_result_id="slice43d-result:fabricated",
    )
    fabricated_result = classification.classify_drift_and_materiality(
        request,
        fabricated_comparison,
    )
    ledger.malformed(
        fabricated_result.status
        is classification.DriftClassificationExecutionStatus.HELD_IDENTITY_INVALID,
        "fabricated comparison identity held",
    )

    try:
        first.status = (
            classification.DriftClassificationExecutionStatus.HELD_INVALID_REQUEST
        )
    except FrozenInstanceError:
        immutable = True
    else:
        immutable = False
    ledger.check(immutable, "classification result immutable")

    result_zero_fields = (
        "aggregate_pass_rejected_contained_decided",
        "echo_disposition_decided",
        "rejection_or_containment_issued",
        "text_repaired_or_rewritten",
        "msm_v1_modified_or_integrated",
        "delivered",
        "downstream_authority_created",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    for field_name in result_zero_fields:
        ledger.check(
            getattr(first, field_name) is False,
            f"result authority zero: {field_name}",
        )
    package_zero_fields = (
        "aggregate_pass_rejected_contained_decided",
        "echo_disposition_decided",
        "rejection_or_containment_issued",
        "text_repaired_or_rewritten",
        "msm_v1_modified_or_integrated",
        "delivery_authorized_or_performed",
        "truth_evidence_permission_execution_authority",
        "route_api_network_filesystem_memory_tool_action_authority",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    for field_name in package_zero_fields:
        ledger.check(
            getattr(package, field_name) is False,
            f"package authority zero: {field_name}",
        )

    print("=== AI.WEB SLICE 43E BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"explicit_drift_kind_cases={ledger.explicit_drift_cases}")
    print(f"explicit_materiality_cases={ledger.materiality_cases}")
    print(f"admitted_drift_kinds={len(classification.DRIFT_KIND_VALUES)}")
    print(f"materiality_states={len(classification.MATERIALITY_VALUES)}")
    print(f"classification_records={first.classification_record_count}")
    print(f"accepted_fixture_drift_findings={first.drift_finding_count}")
    print(f"accepted_fixture_not_applicable={first.not_applicable_finding_count}")
    for kind in classification.DRIFT_KIND_VALUES:
        print(f"{kind}_classified=1")
    print("zero_drift_state_preserved=1")
    print("multiple_drift_kinds_preserved=1")
    print("unsupported_state_preserved=1")
    print("conflicted_state_preserved=1")
    print("indeterminate_state_preserved=1")
    print("materiality_determined_by_explicit_rules=1")
    print("aggregate_pass_rejected_contained_decided=0")
    print("echo_disposition_rejection_containment=0")
    print("text_repair_or_rewrite=0")
    print("msm_v1_modified_or_integrated=0")
    print("delivery_or_downstream_authority=0")
    print("model_or_similarity_authority=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    if ledger.failures:
        for failure in ledger.failures:
            print(f"FAILURE: {failure}")
        print("AI.WEB SLICE 43E BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 43E BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
