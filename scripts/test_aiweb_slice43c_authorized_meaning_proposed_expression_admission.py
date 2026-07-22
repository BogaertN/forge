#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 43C."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
import importlib
from pathlib import Path
import runpy
import sys


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.malformed_cases = 0
        self.explicit_rejections = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)

    def rejection(self, condition: object, label: str) -> None:
        self.explicit_rejections += 1
        self.check(condition, label)


def build_exact_slice42_source(repository: Path):
    helper = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice42g_msm_outward_expression_integration.py"
        )
    )
    integration, integration_input = helper["build_slice42g_input"](
        repository
    )
    closeout = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "disabled_outward_expression_closeout"
    )
    fixture = closeout.list_outward_expression_closeout_fixtures()[0]
    state = closeout.build_disabled_outward_expression_closeout_state(
        explicit_offline_developer_enable=True
    )
    invocation = closeout.build_outward_expression_closeout_invocation(
        fixture.fixture_name
    )
    result = closeout.run_disabled_outward_expression_closeout(
        invocation,
        state=state,
        integration_input=integration_input,
    )
    closeout.assert_valid_result(result)
    return integration, integration_input, result


def main() -> int:
    repository = Path(
        sys.argv[1] if len(sys.argv) == 2 else "/home/nic/forge"
    ).resolve()
    if len(sys.argv) > 2:
        raise SystemExit(
            "usage: test_aiweb_slice43c_authorized_meaning_"
            "proposed_expression_admission.py [REPOSITORY]"
        )
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    package = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "authorized_source_admission"
    )
    surface = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "surface_realization"
    )
    integration, integration_input, source = build_exact_slice42_source(
        repository
    )

    ledger.check(
        package.SLICE43C_ACCEPTED_PARENT_HEAD
        == "42db0a12fd0b09dbe002fe652d869987dd955ed6",
        "exact accepted Slice 43B parent",
    )
    ledger.check(
        package.SLICE43C_ACCEPTED_PARENT_TREE
        == "bd734175783e413fab30084f686d80fde9e76b29",
        "exact accepted Slice 43B tree",
    )
    ledger.check(
        package.SLICE43C_COMMIT_SUBJECT
        == "Slice 43C authorized meaning and proposed-expression admission",
        "exact commit subject",
    )
    ledger.check(
        len(package.EXACT_ACCEPTED_IDS) >= 20,
        "closed exact accepted identity catalog",
    )
    ledger.check(
        len(package.REQUIRED_ADMISSION_COMPONENTS) == 5,
        "five exact admission components",
    )
    ledger.check(
        len(package.REQUIRED_REJECTION_CATEGORIES) == 8,
        "eight required rejection categories",
    )
    ledger.check(
        len(package.PERMANENT_AUTHORITY_ZERO) == 10,
        "ten permanent authority-zero declarations",
    )

    ledger.check(
        source.result_id == package.EXACT_ACCEPTED_ID_MAP["slice42h_result"],
        "exact Slice 42H result identity",
    )
    ledger.check(
        source.acceptance_record.record_id
        == package.EXACT_ACCEPTED_ID_MAP["slice42h_acceptance"],
        "exact Slice 42 acceptance record identity",
    )

    request = package.build_source_admission_request(source)
    ledger.check(
        request.request_id == package.expected_record_id(request),
        "request deterministic identity",
    )
    ledger.check(request.raw_text is None, "request carries no raw text")
    ledger.check(
        request.explicit_admission_request is True,
        "request is explicit",
    )

    # The admission call performs the complete exact-source validation once.
    # Determinism is then proved from canonical package/result identities and
    # digests, avoiding redundant traversal of the full accepted Slice 42 tree.
    first = package.admit_authorized_meaning_and_proposed_expression(request)
    ledger.check(
        first.status is package.SourceAdmissionStatus.ADMITTED,
        "exact accepted source admitted",
    )
    ledger.check(first.source_admitted is True, "source admission recorded")
    ledger.check(
        first.exact_accepted_slice42_ancestry is True,
        "exact ancestry recorded",
    )
    ledger.check(
        first.selected_governed_meaning_admitted is True,
        "selected governed meaning admitted",
    )
    ledger.check(
        first.governed_outward_meaning_admitted is True,
        "governed outward meaning admitted",
    )
    ledger.check(
        first.realized_expression_candidate_admitted is True,
        "realized expression candidate admitted",
    )
    ledger.check(
        first.msm_v1_expression_link_admitted is True,
        "MSM-v1 expression link admitted",
    )
    ledger.check(
        first.slice42_trace_and_custody_admitted is True,
        "Slice 42 trace and custody admitted",
    )
    ledger.check(not first.rejection_codes, "admitted result has no rejections")
    ledger.check(
        first.admission_package is not None,
        "admitted result contains package",
    )
    assert first.admission_package is not None
    admission_package = first.admission_package

    ledger.check(
        package.validate_admission_package(admission_package).ok,
        "admission package validates",
    )
    ledger.check(package.validate_result(first).ok, "admission result validates")
    ledger.check(
        admission_package.admission_package_id
        == package.expected_package_id(admission_package),
        "admission package deterministic ID",
    )
    ledger.check(
        admission_package.admission_package_digest
        == package.expected_package_digest(admission_package),
        "admission package deterministic digest",
    )
    ledger.check(
        first.admission_result_id == package.expected_result_id(first),
        "result deterministic ID",
    )
    ledger.check(
        first.admission_result_digest == package.expected_result_digest(first),
        "result deterministic digest",
    )

    meaning = admission_package.authorized_meaning_admission
    expression = admission_package.proposed_expression_admission
    boundary = admission_package.validation_input_boundary
    authorized = meaning.authorized_meaning_reference
    proposed = expression.proposed_expression_reference

    ledger.check(
        authorized.selected_governed_meaning_ref
        == package.EXACT_ACCEPTED_ID_MAP["selected_meaning"],
        "authorized exact selected meaning",
    )
    ledger.check(
        authorized.governed_outward_meaning_ref
        == package.EXACT_ACCEPTED_ID_MAP["governed_outward_meaning"],
        "authorized exact outward meaning",
    )
    ledger.check(
        proposed.expression_candidate_ref
        == package.EXACT_ACCEPTED_ID_MAP["expression_candidate"],
        "proposed exact candidate",
    )
    ledger.check(
        proposed.expression_link_ref
        == package.EXACT_ACCEPTED_ID_MAP["expression_link"],
        "proposed exact expression link",
    )
    ledger.check(
        proposed.realized_text_sha256
        == package.EXACT_REALIZED_TEXT_SHA256,
        "proposed exact realized text digest",
    )
    ledger.check(
        authorized.lineage_id == proposed.lineage_id == "lineage:demo",
        "shared exact lineage",
    )
    ledger.check(
        authorized.slice42g_integration_input_ref
        == proposed.slice42g_integration_input_ref,
        "shared Slice 42G input",
    )
    ledger.check(
        authorized.slice42g_integration_result_ref
        == proposed.slice42g_integration_result_ref,
        "shared Slice 42G result",
    )
    ledger.check(
        authorized.slice42g_integration_receipt_ref
        == proposed.slice42g_integration_receipt_ref,
        "shared Slice 42G receipt",
    )
    ledger.check(
        authorized.successor_manifest_ref
        == proposed.successor_manifest_ref,
        "shared successor manifest",
    )
    ledger.check(
        authorized.expression_plan_ref == proposed.expression_plan_ref,
        "shared expression plan",
    )
    ledger.check(
        authorized.preservation_obligation_package_ref
        == proposed.preservation_obligation_package_ref,
        "shared obligation package",
    )
    ledger.check(
        boundary.authorized_meaning_reference.authorized_meaning_reference_id
        == authorized.authorized_meaning_reference_id,
        "boundary contains authorized reference",
    )
    ledger.check(
        boundary.proposed_expression_reference.proposed_expression_reference_id
        == proposed.proposed_expression_reference_id,
        "boundary contains proposed reference",
    )
    ledger.check(
        len(boundary.required_preservation_dimensions) == 22,
        "all 22 preservation dimensions retained",
    )
    ledger.check(
        boundary.input_admitted is False,
        "Slice 43A locked input-admitted field remains false",
    )
    ledger.check(
        admission_package.admitted_for_slice43d_comparison is True,
        "43C companion carries admission state",
    )
    ledger.check(
        admission_package.meaning_preservation_comparison_performed is False,
        "comparison remains deferred",
    )

    for name in (
        "raw_text_admitted",
        "orphan_expression_admitted",
        "recomputed_or_fabricated_identity_admitted",
        "unsupported_version_admitted",
        "missing_link_admitted",
        "already_delivered_candidate_admitted",
        "unauthorized_candidate_admitted",
        "meaning_preservation_comparison_performed",
        "drift_classification_performed",
        "echo_disposition_decided",
        "rejection_or_containment_issued",
        "msm_v1_modified_or_integrated",
        "delivered",
        "downstream_authority_created",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    ):
        ledger.check(getattr(first, name) is False, f"result boundary {name}")

    for name in (
        "meaning_preservation_comparison_performed",
        "validation_findings_created",
        "drift_findings_created",
        "materiality_decided",
        "echo_disposition_decided",
        "rejection_issued",
        "containment_issued",
        "msm_v1_modified_or_integrated",
        "delivery_authorized_or_performed",
        "truth_evidence_permission_execution_authority",
        "route_api_network_filesystem_memory_tool_action_authority",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    ):
        ledger.check(
            getattr(admission_package, name) is False,
            f"package boundary {name}",
        )

    # Frozen immutability.
    for record in (
        request,
        meaning,
        expression,
        admission_package,
        first,
    ):
        try:
            setattr(record, fields(record)[0].name, "mutated")
        except (FrozenInstanceError, AttributeError, TypeError):
            ledger.check(True, f"{type(record).__name__} immutable")
        else:
            ledger.check(False, f"{type(record).__name__} immutable")

    # Raw text is rejected even when an accepted source is also supplied.
    raw_request = package.build_source_admission_request(
        source,
        raw_text="arbitrary raw text",
    )
    raw_result = package.admit_authorized_meaning_and_proposed_expression(
        raw_request
    )
    ledger.rejection(
        raw_result.status is package.SourceAdmissionStatus.HELD_RAW_TEXT,
        "raw text rejected",
    )
    ledger.check(
        package.SourceAdmissionCode.RAW_TEXT_WITHOUT_ACCEPTED_ANCESTRY
        in raw_result.rejection_codes,
        "raw text rejection code",
    )

    # Invalid request type and fabricated request identity.
    invalid_type = package.admit_authorized_meaning_and_proposed_expression(
        object()
    )
    ledger.rejection(
        invalid_type.status
        is package.SourceAdmissionStatus.HELD_INVALID_REQUEST,
        "invalid request type rejected",
    )
    fabricated_request = replace(
        request,
        request_id="slice43c_source_admission_request:" + "f" * 64,
    )
    fabricated_request_result = (
        package.admit_authorized_meaning_and_proposed_expression(
            fabricated_request
        )
    )
    ledger.rejection(
        package.SourceAdmissionCode.REQUEST_ID_INVALID
        in fabricated_request_result.rejection_codes,
        "fabricated request identity rejected",
    )

    # Unsupported source version.
    candidate = source.integration_input.surface_realization_result.expression_candidate
    unsupported_candidate = replace(
        candidate,
        schema_version="unsupported-slice42f-version",
    )
    unsupported_surface_result = replace(
        source.integration_input.surface_realization_result,
        expression_candidate=unsupported_candidate,
    )
    unsupported_integration_input = replace(
        source.integration_input,
        surface_realization_result=unsupported_surface_result,
    )
    unsupported_source = replace(
        source,
        integration_input=unsupported_integration_input,
    )
    unsupported_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(unsupported_source)
    )
    ledger.rejection(
        unsupported_result.status
        is package.SourceAdmissionStatus.HELD_UNSUPPORTED_VERSION,
        "unsupported version rejected",
    )

    # Missing expression link.
    missing_successor = replace(
        source.integration_result.successor_manifest,
        expression_links=(),
    )
    missing_integration_result = replace(
        source.integration_result,
        successor_manifest=missing_successor,
    )
    missing_source = replace(
        source,
        integration_result=missing_integration_result,
    )
    missing_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(missing_source)
    )
    ledger.rejection(
        missing_result.status
        is package.SourceAdmissionStatus.HELD_MISSING_LINK,
        "missing expression link rejected",
    )

    # Orphan expression.
    orphan_link = replace(
        source.integration_result.expression_link_record,
        governed_outward_meaning_ref="slice42g_integrated_governed_outward_meaning:"
        + "e" * 64,
    )
    orphan_integration_result = replace(
        source.integration_result,
        expression_link_record=orphan_link,
    )
    orphan_source = replace(
        source,
        integration_result=orphan_integration_result,
    )
    orphan_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(orphan_source)
    )
    ledger.rejection(
        orphan_result.status
        is package.SourceAdmissionStatus.HELD_ORPHAN_EXPRESSION,
        "orphan expression rejected",
    )

    # Fabricated and recomputed candidate identities.
    fabricated_candidate = replace(
        candidate,
        expression_candidate_id="unvalidated-expression-candidate:"
        + "a" * 64,
    )
    fabricated_surface_result = replace(
        source.integration_input.surface_realization_result,
        expression_candidate=fabricated_candidate,
    )
    fabricated_input = replace(
        source.integration_input,
        surface_realization_result=fabricated_surface_result,
    )
    fabricated_source = replace(source, integration_input=fabricated_input)
    fabricated_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(fabricated_source)
    )
    ledger.rejection(
        fabricated_result.status
        is package.SourceAdmissionStatus.HELD_IDENTITY_INVALID,
        "fabricated candidate identity rejected",
    )

    modified_candidate = replace(
        candidate,
        realized_text=candidate.realized_text + " changed",
    )
    recomputed_candidate = surface.with_expected_candidate_identity(
        modified_candidate
    )
    recomputed_surface_result = replace(
        source.integration_input.surface_realization_result,
        expression_candidate=recomputed_candidate,
    )
    recomputed_input = replace(
        source.integration_input,
        surface_realization_result=recomputed_surface_result,
    )
    recomputed_source = replace(source, integration_input=recomputed_input)
    recomputed_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(recomputed_source)
    )
    ledger.rejection(
        recomputed_result.status
        is package.SourceAdmissionStatus.HELD_IDENTITY_INVALID,
        "recomputed non-accepted candidate identity rejected",
    )

    # Already delivered candidate.
    delivered_source = replace(
        source,
        delivered=True,
        delivery_authorized=True,
    )
    delivered_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(delivered_source)
    )
    ledger.rejection(
        delivered_result.status
        is package.SourceAdmissionStatus.HELD_ALREADY_DELIVERED,
        "already delivered candidate rejected",
    )

    # Candidate without exact realization authority.
    unauthorized_authority = replace(
        source.integration_input.surface_realization_input.realization_authority_record,
        expression_candidate_creation_authorized=False,
    )
    unauthorized_surface_input = replace(
        source.integration_input.surface_realization_input,
        realization_authority_record=unauthorized_authority,
    )
    unauthorized_integration_input = replace(
        source.integration_input,
        surface_realization_input=unauthorized_surface_input,
    )
    unauthorized_source = replace(
        source,
        integration_input=unauthorized_integration_input,
    )
    unauthorized_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(unauthorized_source)
    )
    ledger.rejection(
        unauthorized_result.status
        is package.SourceAdmissionStatus.HELD_UNAUTHORIZED_CANDIDATE,
        "unauthorized candidate rejected",
    )

    # Inconsistent lineage.
    inconsistent_outward = replace(
        source.integration_result.governed_outward_meaning_record,
        lineage_id="lineage:fabricated",
    )
    inconsistent_integration_result = replace(
        source.integration_result,
        governed_outward_meaning_record=inconsistent_outward,
    )
    inconsistent_source = replace(
        source,
        integration_result=inconsistent_integration_result,
    )
    inconsistent_result = package.admit_authorized_meaning_and_proposed_expression(
        package.build_source_admission_request(inconsistent_source)
    )
    ledger.rejection(
        inconsistent_result.status
        is package.SourceAdmissionStatus.HELD_INCONSISTENT_ANCESTRY,
        "inconsistent lineage rejected",
    )

    held_results = (
        raw_result,
        invalid_type,
        fabricated_request_result,
        unsupported_result,
        missing_result,
        orphan_result,
        fabricated_result,
        recomputed_result,
        delivered_result,
        unauthorized_result,
        inconsistent_result,
    )
    for index, held in enumerate(held_results):
        ledger.check(
            held.source_admitted is False,
            f"held result {index} source not admitted",
        )
        ledger.check(
            held.admission_package is None,
            f"held result {index} has no admission package",
        )
        ledger.check(
            package.validate_result(held).ok,
            f"held result {index} validates",
        )
        ledger.check(
            held.delivered is False
            and held.downstream_authority_created is False,
            f"held result {index} no consequence",
        )

    # Source records remain unchanged after all admissions.
    ledger.check(
        source.result_id
        == package.EXACT_ACCEPTED_ID_MAP["slice42h_result"],
        "source result identity remained unchanged",
    )
    ledger.check(
        source.integration_input.integration_input_id
        == package.EXACT_ACCEPTED_ID_MAP["slice42g_input"],
        "exact Slice 42G input identity remained unchanged",
    )

    print("=== AI.WEB SLICE 43C BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"explicit_rejection_cases={ledger.explicit_rejections}")
    print("admission_components=5")
    print("required_rejection_categories=8")
    print("selected_governed_meaning_admitted=1")
    print("governed_outward_meaning_admitted=1")
    print("realized_expression_candidate_admitted=1")
    print("msm_v1_expression_link_admitted=1")
    print("slice42_trace_and_custody_admitted=1")
    print("raw_text_admitted=0")
    print("orphan_expression_admitted=0")
    print("recomputed_or_fabricated_identity_admitted=0")
    print("unsupported_version_admitted=0")
    print("missing_link_admitted=0")
    print("already_delivered_candidate_admitted=0")
    print("unauthorized_candidate_admitted=0")
    print("meaning_preservation_comparison_performed=0")
    print("drift_classification_or_materiality=0")
    print("echo_disposition_rejection_containment=0")
    print("msm_v1_modified_or_integrated=0")
    print("delivery_or_downstream_authority=0")
    print("model_or_similarity_authority=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    if ledger.failures:
        for failure in ledger.failures:
            print(f"FAIL: {failure}")
        print("AI.WEB SLICE 43C BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 43C BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
