#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 43F."""

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
        self.explicit_disposition_cases = 0
        self.rejection_cases = 0
        self.containment_cases = 0
        self.precedence_cases = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)

    def disposition_case(self, condition: object, label: str) -> None:
        self.explicit_disposition_cases += 1
        self.check(condition, label)

    def rejection_case(self, condition: object, label: str) -> None:
        self.rejection_cases += 1
        self.check(condition, label)

    def containment_case(self, condition: object, label: str) -> None:
        self.containment_cases += 1
        self.check(condition, label)

    def precedence_case(self, condition: object, label: str) -> None:
        self.precedence_cases += 1
        self.check(condition, label)


def build_exact_inputs(repository: Path):
    helper = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice43e_drift_materiality_classification.py"
        )
    )
    comparison, base_comparison = helper["build_exact_slice43d_result"](
        repository
    )
    classification = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "drift_materiality_classification"
    )
    exact_classification = classification.classify_drift_and_materiality(
        classification.build_classification_request(base_comparison),
        base_comparison,
    )
    return helper, comparison, classification, base_comparison, exact_classification


def classify(classification, comparison_result):
    return classification.classify_drift_and_materiality(
        classification.build_classification_request(comparison_result),
        comparison_result,
    )


def decide(disposition, classification_result):
    request = disposition.build_disposition_request(classification_result)
    return disposition.decide_echo_disposition(request, classification_result)


def main() -> int:
    repository = Path(
        sys.argv[1] if len(sys.argv) == 2 else "/home/nic/forge"
    ).resolve()
    if len(sys.argv) > 2:
        raise SystemExit(
            "usage: test_aiweb_slice43f_echo_disposition_rejection_containment.py "
            "[REPOSITORY]"
        )
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    (
        helper,
        comparison,
        classification,
        base_comparison,
        exact_classification,
    ) = build_exact_inputs(repository)
    disposition = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime.echo_disposition"
    )

    ledger.check(
        disposition.SLICE43F_ACCEPTED_PARENT_HEAD
        == "2192c7ffc6df7f936ead4760f25a0f027dcffad7",
        "exact accepted Slice 43E parent",
    )
    ledger.check(
        disposition.SLICE43F_ACCEPTED_PARENT_TREE
        == "93ed56e1db485d611c0a434387eacec81a0149aa",
        "exact accepted Slice 43E parent tree",
    )
    ledger.check(
        disposition.SLICE43F_COMMIT_SUBJECT
        == "Slice 43F Echo disposition rejection and containment",
        "exact commit subject",
    )
    ledger.check(
        disposition.ECHO_DISPOSITION_VALUES
        == ("PASSED", "REJECTED", "CONTAINED"),
        "exact three Echo dispositions",
    )
    ledger.check(
        len(disposition.DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES)
        == 16,
        "exact deterministic violation registry",
    )
    ledger.check(
        disposition.PRECEDENCE_RULE_REF
        == "slice43f-precedence-law:incomplete-authority-containment-precedes-rejection",
        "exact coexistence precedence",
    )
    ledger.check(
        len(disposition.PERMANENT_AUTHORITY_ZERO) == 10,
        "ten permanent authority-zero boundaries",
    )
    ledger.check(
        exact_classification.classification_result_id
        == disposition.EXACT_ACCEPTED_SLICE43E_ID_MAP["result"],
        "exact accepted Slice 43E result identity",
    )
    exact_package43e = exact_classification.classification_package
    assert exact_package43e is not None
    ledger.check(
        exact_package43e.classification_package_id
        == disposition.EXACT_ACCEPTED_SLICE43E_ID_MAP["package"],
        "exact accepted Slice 43E package identity",
    )

    request = disposition.build_disposition_request(exact_classification)
    ledger.check(
        request.request_id == disposition.expected_record_id(request),
        "disposition request deterministic identity",
    )
    ledger.check(request.raw_text is None, "disposition request has no raw text")
    ledger.check(
        request.explicit_disposition_request is True,
        "disposition request explicit",
    )
    ledger.check(
        disposition.validate_disposition_inputs(
            request,
            exact_classification,
        ).ok,
        "exact disposition input validates",
    )

    passed = disposition.decide_echo_disposition(
        request,
        exact_classification,
    )
    ledger.disposition_case(
        passed.disposition is disposition.EchoDisposition.PASSED,
        "accepted fixture PASSED",
    )
    ledger.check(
        passed.status
        is disposition.EchoDispositionExecutionStatus.DISPOSITION_CREATED,
        "accepted fixture disposition-created status",
    )
    ledger.check(passed.disposition_decided is True, "disposition decided")
    ledger.check(passed.rejection_issued is False, "PASSED no rejection")
    ledger.check(passed.containment_issued is False, "PASSED no containment")
    passed_package = passed.disposition_package
    ledger.check(passed_package is not None, "PASSED package created")
    assert passed_package is not None
    passed_record = passed_package.disposition_record
    ledger.check(
        passed_record.disposition_state
        is disposition.EchoDispositionState.ALL_MATERIAL_OBLIGATIONS_PASS,
        "PASSED exact state",
    )
    ledger.check(
        passed_record.all_material_preservation_obligations_pass is True,
        "all material preservation obligations pass",
    )
    ledger.check(
        passed_record.deterministic_echo_law_violation is False,
        "PASSED no deterministic violation",
    )
    ledger.check(
        passed_record.incomplete_authority_blocks_progression is False,
        "PASSED no incomplete authority",
    )
    ledger.check(
        passed_record.all_finding_refs
        == tuple(item.drift_finding_id for item in exact_package43e.drift_findings),
        "PASSED retains all Slice 43E findings",
    )
    ledger.check(len(passed_record.all_finding_refs) == 13, "thirteen findings retained")
    ledger.check(len(passed_record.no_drift_finding_refs) == 13, "thirteen no-drift findings")
    ledger.check(not passed_record.non_material_finding_refs, "zero non-material findings")
    ledger.check(not passed_record.material_violation_finding_refs, "zero material violations")
    ledger.check(not passed_record.incomplete_authority_finding_refs, "zero incomplete findings")
    ledger.check(passed_package.rejection_record is None, "PASSED no rejection custody")
    ledger.check(passed_package.containment_record is None, "PASSED no containment custody")
    ledger.check(
        passed_package.disposition_package_id
        == disposition.expected_package_id(passed_package),
        "PASSED package deterministic identity",
    )
    ledger.check(
        passed_package.disposition_package_digest
        == disposition.expected_package_digest(passed_package),
        "PASSED package deterministic digest",
    )
    ledger.check(
        passed.disposition_result_id == disposition.expected_result_id(passed),
        "PASSED result deterministic identity",
    )
    ledger.check(
        passed.disposition_result_digest
        == disposition.expected_result_digest(passed),
        "PASSED result deterministic digest",
    )
    ledger.check(
        disposition.validate_result(passed, exact_classification).ok,
        "PASSED result validates",
    )

    cases = (
        (
            classification.DriftKind.OMITTED_MEANING,
            comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
            ("meaning:a", "meaning:b"),
            ("meaning:a",),
            {},
        ),
        (
            classification.DriftKind.CLAIM_STRENGTHENING,
            comparison.MeaningPreservationDimension.CLAIM_STATUS,
            ("claim_status:nonaffirmative_blocked",),
            ("claim_status:affirmative",),
            {},
        ),
        (
            classification.DriftKind.SCOPE_EXPANSION,
            comparison.MeaningPreservationDimension.SCOPE,
            ("scope:local",),
            ("scope:local", "scope:global"),
            {},
        ),
        (
            classification.DriftKind.CERTAINTY_UPGRADE,
            comparison.MeaningPreservationDimension.CERTAINTY,
            ("certainty:uncertain",),
            ("certainty:certain",),
            {},
        ),
        (
            classification.DriftKind.EVIDENCE_STATUS_UPGRADE,
            comparison.MeaningPreservationDimension.EVIDENCE_STATUS,
            ("evidence_status:unverified",),
            ("evidence_status:verified",),
            {},
        ),
        (
            classification.DriftKind.CAVEAT_OMISSION,
            comparison.MeaningPreservationDimension.CAVEATS_AND_LIMITATIONS,
            ("caveat:required",),
            (),
            {},
        ),
        (
            classification.DriftKind.REFUSAL_SOFTENING,
            comparison.MeaningPreservationDimension.REFUSAL_STATE,
            ("refusal:blocked",),
            ("permission:allowed",),
            {},
        ),
        (
            classification.DriftKind.AMBIGUITY_ERASURE,
            comparison.MeaningPreservationDimension.UNRESOLVED_CONDITIONS,
            ("ambiguity:multiple_candidate", "unresolved:condition"),
            ("unresolved:condition",),
            {},
        ),
        (
            classification.DriftKind.UNRESOLVED_STATE_ERASURE,
            comparison.MeaningPreservationDimension.UNRESOLVED_CONDITIONS,
            ("unresolved:condition",),
            ("resolved:complete",),
            {},
        ),
        (
            classification.DriftKind.INVENTED_FACT,
            comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
            ("meaning:a",),
            ("meaning:a", "fact:invented-x"),
            {},
        ),
        (
            classification.DriftKind.INVENTED_EVIDENCE,
            comparison.MeaningPreservationDimension.EVIDENCE_STATUS,
            ("evidence_status:unverified",),
            ("evidence_status:unverified", "evidence:invented-x"),
            {},
        ),
        (
            classification.DriftKind.AUTHORITY_ESCALATION,
            comparison.MeaningPreservationDimension.ACTION_STATUS,
            ("action:not_authorized",),
            ("action:executed",),
            {},
        ),
        (
            classification.DriftKind.ACTION_STATUS_DISTORTION,
            comparison.MeaningPreservationDimension.ACTION_STATUS,
            ("action:not_performed",),
            ("action:performed",),
            {},
        ),
        (
            classification.DriftKind.MEMORY_STATUS_DISTORTION,
            comparison.MeaningPreservationDimension.MEMORY_STATUS,
            ("memory:not_accessed",),
            ("memory:memory_written",),
            {},
        ),
        (
            classification.DriftKind.DELIVERY_STATUS_DISTORTION,
            comparison.MeaningPreservationDimension.DELIVERY_STATUS,
            ("delivery:not_delivered",),
            ("delivery:delivered",),
            {},
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
        ),
    )

    rejected_kinds = set()
    for expected_kind, dimension, source_values, proposed_values, options in cases:
        comparison_variant = helper["modified_comparison_result"](
            comparison,
            base_comparison,
            dimension=dimension,
            source_values=source_values,
            proposed_values=proposed_values,
            **options,
        )
        classification_variant = classify(classification, comparison_variant)
        result = decide(disposition, classification_variant)
        ledger.disposition_case(
            result.disposition is disposition.EchoDisposition.REJECTED,
            f"{expected_kind.value} REJECTED",
        )
        ledger.rejection_case(
            result.rejection_issued is True,
            f"{expected_kind.value} rejection issued",
        )
        package = result.disposition_package
        assert package is not None
        rejection = package.rejection_record
        ledger.check(rejection is not None, f"{expected_kind.value} rejection custody")
        assert rejection is not None
        rejected_kinds.update(rejection.violation_drift_kinds)
        ledger.check(
            expected_kind in rejection.violation_drift_kinds,
            f"{expected_kind.value} exact violation kind retained",
        )
        ledger.check(
            package.containment_record is None,
            f"{expected_kind.value} no containment custody",
        )
        ledger.check(
            len(rejection.retained_all_finding_refs) == 13,
            f"{expected_kind.value} retains all findings",
        )
        ledger.check(
            rejection.candidate_rewritten_or_repaired is False,
            f"{expected_kind.value} no rewrite or repair",
        )
        ledger.check(
            rejection.drift_removed_downgraded_or_suppressed is False,
            f"{expected_kind.value} no drift suppression",
        )
        ledger.check(
            rejection.delivery_authorized_or_performed is False,
            f"{expected_kind.value} no delivery",
        )
        ledger.check(
            disposition.validate_result(result, classification_variant).ok,
            f"{expected_kind.value} rejection validates",
        )

    ledger.check(
        {item.value for item in rejected_kinds}
        == set(disposition.DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES),
        "all sixteen deterministic violation kinds reject",
    )

    surface_variant = helper["modified_comparison_result"](
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
        source_values=("meaning:a",),
        proposed_values=("meaning:a", "surface:formatting:bold"),
    )
    surface_classification = classify(classification, surface_variant)
    surface_result = decide(disposition, surface_classification)
    ledger.disposition_case(
        surface_result.disposition is disposition.EchoDisposition.PASSED,
        "controlled non-material surface addition PASSED",
    )
    surface_package = surface_result.disposition_package
    assert surface_package is not None
    ledger.check(
        surface_package.non_material_finding_count == 1,
        "controlled surface addition retained as non-material",
    )
    ledger.check(
        surface_package.disposition_record.retained_drift_kinds
        == (classification.DriftKind.UNSUPPORTED_SURFACE_ADDITION,),
        "non-material drift remains visible",
    )
    ledger.check(
        surface_package.disposition_record.all_material_preservation_obligations_pass
        is True,
        "non-material drift does not fail material obligations",
    )
    ledger.check(
        disposition.validate_result(surface_result, surface_classification).ok,
        "non-material PASSED result validates",
    )

    containment_variants = (
        (
            "unsupported",
            helper["modified_comparison_result"](
                comparison,
                base_comparison,
                dimension=comparison.MeaningPreservationDimension.SCOPE,
                proposed_supported=False,
            ),
            classification.MaterialityState.UNSUPPORTED,
        ),
        (
            "conflicted",
            helper["modified_comparison_result"](
                comparison,
                base_comparison,
                dimension=comparison.MeaningPreservationDimension.SCOPE,
                proposed_conflict_refs=("conflict:scope",),
            ),
            classification.MaterialityState.CONFLICTED,
        ),
        (
            "indeterminate",
            helper["modified_comparison_result"](
                comparison,
                base_comparison,
                dimension=comparison.MeaningPreservationDimension.SCOPE,
                proposed_indeterminate_refs=("indeterminate:scope",),
            ),
            classification.MaterialityState.INDETERMINATE,
        ),
        (
            "unknown_surface",
            helper["modified_comparison_result"](
                comparison,
                base_comparison,
                dimension=comparison.MeaningPreservationDimension.SEMANTIC_CONTENT,
                source_values=("meaning:a",),
                proposed_values=("meaning:a", "surface:unknown:addition"),
            ),
            classification.MaterialityState.INDETERMINATE,
        ),
    )
    for name, comparison_variant, expected_materiality in containment_variants:
        classification_variant = classify(classification, comparison_variant)
        result = decide(disposition, classification_variant)
        ledger.disposition_case(
            result.disposition is disposition.EchoDisposition.CONTAINED,
            f"{name} CONTAINED",
        )
        ledger.containment_case(
            result.containment_issued is True,
            f"{name} containment issued",
        )
        package = result.disposition_package
        assert package is not None
        containment = package.containment_record
        ledger.check(containment is not None, f"{name} containment custody")
        assert containment is not None
        ledger.check(
            expected_materiality in containment.blocking_materiality_states,
            f"{name} blocking materiality retained",
        )
        ledger.check(
            len(containment.retained_all_finding_refs) == 13,
            f"{name} retains all findings",
        )
        ledger.check(
            containment.candidate_rewritten_or_repaired is False,
            f"{name} no rewrite or repair",
        )
        ledger.check(
            containment.drift_removed_downgraded_or_suppressed is False,
            f"{name} no drift suppression",
        )
        ledger.check(
            disposition.validate_result(result, classification_variant).ok,
            f"{name} containment validates",
        )

    material_comparison = helper["modified_comparison_result"](
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SCOPE,
        source_values=("scope:local",),
        proposed_values=("scope:local", "scope:global"),
    )
    coexistence_comparison = helper["modified_comparison_result"](
        comparison,
        material_comparison,
        dimension=comparison.MeaningPreservationDimension.EVIDENCE_STATUS,
        proposed_supported=False,
    )
    coexistence_classification = classify(
        classification,
        coexistence_comparison,
    )
    coexistence_result = decide(disposition, coexistence_classification)
    ledger.precedence_case(
        coexistence_result.disposition is disposition.EchoDisposition.CONTAINED,
        "incomplete authority containment precedes rejection",
    )
    coexistence_package = coexistence_result.disposition_package
    assert coexistence_package is not None
    coexistence_record = coexistence_package.disposition_record
    coexistence_containment = coexistence_package.containment_record
    assert coexistence_containment is not None
    ledger.check(
        coexistence_record.coexistence_precedence_applied is True,
        "coexistence precedence recorded",
    )
    ledger.check(
        bool(coexistence_record.material_violation_finding_refs),
        "coexisting material violation retained",
    )
    ledger.check(
        bool(coexistence_record.incomplete_authority_finding_refs),
        "coexisting incomplete authority retained",
    )
    ledger.check(
        coexistence_package.rejection_record is None,
        "coexistence creates no conflicting rejection custody",
    )
    ledger.check(
        disposition.PRECEDENCE_RULE_REF
        in coexistence_containment.containment_law_refs,
        "coexistence containment records precedence law",
    )
    ledger.check(
        disposition.validate_result(
            coexistence_result,
            coexistence_classification,
        ).ok,
        "coexistence containment validates",
    )

    raw_request = replace(request, raw_text="raw text prohibited")
    raw_result = disposition.decide_echo_disposition(
        raw_request,
        exact_classification,
    )
    ledger.malformed(
        raw_result.status
        is disposition.EchoDispositionExecutionStatus.HELD_INVALID_REQUEST,
        "raw text held",
    )
    ledger.malformed(
        raw_result.disposition_package is None,
        "raw text creates no package",
    )

    wrong_ref_request = replace(
        request,
        classification_result_ref="slice43e-result:fabricated",
    )
    wrong_ref_request = replace(
        wrong_ref_request,
        request_id=disposition.expected_record_id(wrong_ref_request),
    )
    wrong_ref_result = disposition.decide_echo_disposition(
        wrong_ref_request,
        exact_classification,
    )
    ledger.malformed(
        wrong_ref_result.status
        is disposition.EchoDispositionExecutionStatus.HELD_INCONSISTENT_ANCESTRY,
        "mismatched classification ancestry held",
    )

    unsupported_request = replace(
        request,
        schema_version="aiweb-slice43f-unsupported-v999",
    )
    unsupported_request = replace(
        unsupported_request,
        request_id=disposition.expected_record_id(unsupported_request),
    )
    unsupported_result = disposition.decide_echo_disposition(
        unsupported_request,
        exact_classification,
    )
    ledger.malformed(
        unsupported_result.status
        is disposition.EchoDispositionExecutionStatus.HELD_UNSUPPORTED_VERSION,
        "unsupported version held",
    )

    fabricated_classification = replace(
        exact_classification,
        classification_result_id="slice43e-result:fabricated",
    )
    fabricated_result = disposition.decide_echo_disposition(
        request,
        fabricated_classification,
    )
    ledger.malformed(
        fabricated_result.status
        is disposition.EchoDispositionExecutionStatus.HELD_IDENTITY_INVALID,
        "fabricated Slice 43E identity held",
    )

    held_classification = replace(
        exact_classification,
        classification_result_id="",
        classification_result_digest="",
        status=classification.DriftClassificationExecutionStatus.HELD_INVALID_REQUEST,
        classification_package=None,
        drift_classification_performed=False,
        materiality_findings_created=False,
        classification_record_count=0,
        drift_finding_count=0,
        material_finding_count=0,
        non_material_finding_count=0,
        not_applicable_finding_count=0,
        unsupported_finding_count=0,
        conflicted_finding_count=0,
        indeterminate_finding_count=0,
    )
    held_classification = classification.with_expected_result_identity(
        held_classification
    )
    held_request = disposition.build_disposition_request(held_classification)
    held_result = disposition.decide_echo_disposition(
        held_request,
        held_classification,
    )
    ledger.malformed(
        held_result.status
        is disposition.EchoDispositionExecutionStatus.HELD_CLASSIFICATION_NOT_READY,
        "held Slice 43E classification creates no disposition",
    )

    try:
        passed.disposition = disposition.EchoDisposition.REJECTED
    except FrozenInstanceError:
        immutable = True
    else:
        immutable = False
    ledger.check(immutable, "disposition result immutable")

    authority_zero_fields = (
        "candidate_rewritten_or_repaired",
        "drift_removed_downgraded_or_suppressed",
        "delivery_authorized_or_performed",
        "echoforge_called",
        "downstream_authority_created",
        "model_or_similarity_authority_used",
        "msm_v1_modified_or_integrated",
        "gp014_superseded",
    )
    for field_name in authority_zero_fields:
        ledger.check(
            getattr(passed, field_name) is False,
            f"result authority zero: {field_name}",
        )
        ledger.check(
            getattr(passed_package, field_name) is False,
            f"package authority zero: {field_name}",
        )
        ledger.check(
            getattr(passed_record, field_name) is False,
            f"record authority zero: {field_name}",
        )
    ledger.check(
        passed_package.truth_evidence_permission_execution_authority is False,
        "truth/evidence/permission/execution authority zero",
    )
    ledger.check(
        passed_package.route_api_network_filesystem_memory_tool_action_authority
        is False,
        "route/API/network/filesystem/memory/tool/action authority zero",
    )

    print("=== AI.WEB SLICE 43F BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"explicit_disposition_cases={ledger.explicit_disposition_cases}")
    print(f"rejection_cases={ledger.rejection_cases}")
    print(f"containment_cases={ledger.containment_cases}")
    print(f"coexistence_precedence_cases={ledger.precedence_cases}")
    print("echo_dispositions=3")
    print("classification_records=13")
    print("accepted_fixture_disposition=PASSED")
    print("controlled_non_material_surface_disposition=PASSED")
    print("all_material_violation_kinds_rejected=1")
    print("unsupported_authority_contained=1")
    print("conflicted_authority_contained=1")
    print("indeterminate_authority_contained=1")
    print("incomplete_authority_precedes_rejection=1")
    print("all_source_findings_retained=1")
    print("candidate_rewritten_or_repaired=0")
    print("drift_removed_downgraded_or_suppressed=0")
    print("delivery_authorized_or_performed=0")
    print("echoforge_called=0")
    print("model_or_similarity_authority=0")
    print("msm_v1_modified_or_integrated=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print(f"FAIL: {failure}")
    if ledger.failures:
        print("AI.WEB SLICE 43F BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 43F BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
