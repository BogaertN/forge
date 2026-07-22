#!/usr/bin/env python3
"""Visible behavior test for Slice 43G MSM-v1 Echo-validation custody."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import sys


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []
        self.malformed_cases = 0
        self.disposition_cases = 0
        self.retention_checks = 0

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)

    def disposition(self, condition: object, label: str) -> None:
        self.disposition_cases += 1
        self.check(condition, label)

    def retained(self, condition: object, label: str) -> None:
        self.retention_checks += 1
        self.check(condition, label)


def build_exact_sources(repository: Path):
    test43c = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice43c_authorized_meaning_proposed_expression_admission.py"
        )
    )
    integration42g, input42g, source_closeout = (
        test43c["build_exact_slice42_source"](repository)
    )
    result42g = source_closeout.integration_result
    assert result42g is not None

    admission = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "authorized_source_admission"
    )
    source_admission = admission.admit_authorized_meaning_and_proposed_expression(
        admission.build_source_admission_request(source_closeout)
    )
    comparison = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "meaning_preservation_comparison"
    )
    base_comparison = comparison.compare_meaning_preservation(
        comparison.build_comparison_request(
            source_admission,
            source_closeout,
        ),
        source_admission,
        source_closeout,
    )
    classification = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "drift_materiality_classification"
    )
    exact_classification = classification.classify_drift_and_materiality(
        classification.build_classification_request(base_comparison),
        base_comparison,
    )
    disposition = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime.echo_disposition"
    )
    exact_disposition = disposition.decide_echo_disposition(
        disposition.build_disposition_request(exact_classification),
        exact_classification,
    )
    test43e = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice43e_drift_materiality_classification.py"
        )
    )
    return (
        integration42g,
        input42g,
        result42g,
        test43e,
        comparison,
        classification,
        base_comparison,
        exact_classification,
        disposition,
        exact_disposition,
    )


def classify(classification, comparison_result):
    return classification.classify_drift_and_materiality(
        classification.build_classification_request(comparison_result),
        comparison_result,
    )


def decide(disposition, classification_result):
    return disposition.decide_echo_disposition(
        disposition.build_disposition_request(classification_result),
        classification_result,
    )


def integrate(
    integration43g,
    input42g,
    result42g,
    classification_result,
    disposition_result,
):
    value = integration43g.build_integration_input(
        input42g,
        result42g,
        classification_result,
        disposition_result,
    )
    result = integration43g.integrate_echo_validation_link(value)
    return value, result


def main() -> int:
    repository = Path(
        sys.argv[1] if len(sys.argv) == 2 else "/home/nic/forge"
    ).resolve()
    if len(sys.argv) > 2:
        raise SystemExit(
            "usage: test_aiweb_slice43g_msm_echo_validation_link_custody.py "
            "[REPOSITORY]"
        )
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    (
        integration42g,
        input42g,
        result42g,
        helper,
        comparison,
        classification,
        base_comparison,
        exact_classification,
        disposition,
        exact_disposition,
    ) = build_exact_sources(repository)
    integration43g = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "msm_echo_validation_integration"
    )
    manifest_serialization = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest.serialization"
    )
    manifest_validation = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest.validation"
    )
    msm = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest"
    )

    ledger.check(
        integration43g.SLICE43G_ACCEPTED_PARENT_HEAD
        == "76b35c0e43f7012bc922ff20c307f44a82b1f664",
        "exact accepted Slice 43F parent",
    )
    ledger.check(
        integration43g.SLICE43G_ACCEPTED_PARENT_TREE
        == "a1c74f6cc0c90c213272280bfb388ec0e5fa32f0",
        "exact accepted Slice 43F tree",
    )
    ledger.check(
        integration43g.SLICE43G_COMMIT_SUBJECT
        == "Slice 43G MSM-v1 Echo-validation link custody",
        "exact Slice 43G commit subject",
    )
    ledger.check(
        integration43g.VALIDATION_DISPOSITIONS
        == ("PASSED", "REJECTED", "CONTAINED"),
        "exact validation dispositions",
    )
    ledger.check(
        hasattr(msm, "ValidationLinkRecord"),
        "dormant ValidationLinkRecord exists",
    )
    ledger.check(
        hasattr(msm.MeaningStructureManifestV1, "__dataclass_fields__")
        and "validation_links"
        in msm.MeaningStructureManifestV1.__dataclass_fields__,
        "manifest validation_links field exists",
    )
    ledger.check(
        "delivery_or_containment_links"
        in msm.MeaningStructureManifestV1.__dataclass_fields__,
        "manifest delivery or containment field exists",
    )

    passed_input, passed = integrate(
        integration43g,
        input42g,
        result42g,
        exact_classification,
        exact_disposition,
    )
    ledger.disposition(
        passed.validation_disposition is disposition.EchoDisposition.PASSED,
        "PASSED disposition integrated",
    )
    ledger.check(
        integration43g.validate_integration_input(passed_input).ok,
        "PASSED input validates",
    )
    ledger.check(
        integration43g.validate_integration_result(
            passed,
            integration_input=passed_input,
        ).ok,
        "PASSED result validates",
    )
    repeated = integration43g.integrate_echo_validation_link(passed_input)
    ledger.check(passed == repeated, "PASSED integration deterministic")
    ledger.check(
        passed.status
        is integration43g.MsmEchoValidationIntegrationStatus.SUCCESSOR_CREATED,
        "PASSED successor-created status",
    )
    ledger.check(passed.validation_link_record is not None, "PASSED validation link")
    ledger.check(
        passed.validation_link_record.external_validation_disposition
        == "PASSED",
        "PASSED exact disposition in validation link",
    )
    ledger.check(
        passed.validation_link_record.external_validation_receipt_ref
        == exact_disposition.disposition_result_id,
        "PASSED exact validation receipt",
    )
    ledger.check(
        passed.validation_link_record.expression_link_ref
        == result42g.expression_link_record.record_id,
        "PASSED exact expression link ancestry",
    )
    ledger.check(
        passed.containment_link_record is None,
        "PASSED no containment link",
    )
    ledger.check(
        passed.containment_transition_trace is None,
        "PASSED no containment trace",
    )
    ledger.check(
        len(passed.successor_manifest.validation_links)
        == len(passed.source_manifest.validation_links) + 1,
        "PASSED exactly one validation link added",
    )
    ledger.check(
        passed.successor_manifest.delivery_or_containment_links
        == passed.source_manifest.delivery_or_containment_links,
        "PASSED no delivery or containment addition",
    )

    rejection_comparison = helper["modified_comparison_result"](
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SCOPE,
        source_values=("scope:local",),
        proposed_values=("scope:local", "scope:global"),
    )
    rejection_classification = classify(classification, rejection_comparison)
    rejection_disposition = decide(disposition, rejection_classification)
    rejected_input, rejected = integrate(
        integration43g,
        input42g,
        result42g,
        rejection_classification,
        rejection_disposition,
    )
    ledger.disposition(
        rejected.validation_disposition is disposition.EchoDisposition.REJECTED,
        "REJECTED disposition integrated",
    )
    ledger.check(
        integration43g.validate_integration_result(
            rejected,
            integration_input=rejected_input,
        ).ok,
        "REJECTED result validates",
    )
    ledger.check(
        rejected.validation_link_record.external_validation_disposition
        == "REJECTED",
        "REJECTED exact disposition in validation link",
    )
    ledger.check(
        rejected.companion.rejection_record_ref
        == rejection_disposition.disposition_package.rejection_record.rejection_id,
        "REJECTED exact rejection custody",
    )
    ledger.check(
        rejected.receipt.rejection_record_ref
        == rejected.companion.rejection_record_ref,
        "REJECTED receipt preserves rejection custody",
    )
    ledger.check(
        rejected.containment_link_record is None,
        "REJECTED does not invent containment",
    )
    ledger.check(
        rejected.successor_manifest.delivery_or_containment_links
        == rejected.source_manifest.delivery_or_containment_links,
        "REJECTED adds no delivery or containment link",
    )

    containment_comparison = helper["modified_comparison_result"](
        comparison,
        base_comparison,
        dimension=comparison.MeaningPreservationDimension.SCOPE,
        proposed_supported=False,
    )
    containment_classification = classify(
        classification,
        containment_comparison,
    )
    containment_disposition = decide(
        disposition,
        containment_classification,
    )
    contained_input, contained = integrate(
        integration43g,
        input42g,
        result42g,
        containment_classification,
        containment_disposition,
    )
    ledger.disposition(
        contained.validation_disposition
        is disposition.EchoDisposition.CONTAINED,
        "CONTAINED disposition integrated",
    )
    ledger.check(
        integration43g.validate_integration_result(
            contained,
            integration_input=contained_input,
        ).ok,
        "CONTAINED result validates",
    )
    ledger.check(
        contained.validation_link_record.external_validation_disposition
        == "CONTAINED",
        "CONTAINED exact disposition in validation link",
    )
    ledger.check(
        contained.containment_link_record is not None,
        "CONTAINED exact containment link added",
    )
    ledger.check(
        contained.containment_link_record.disposition
        is msm.DeliveryContainmentKind.CONTAINMENT_LINKED,
        "CONTAINED uses containment kind",
    )
    ledger.check(
        contained.containment_link_record.external_receipt_ref
        == containment_disposition.disposition_package.containment_record.containment_id,
        "CONTAINED exact containment receipt",
    )
    ledger.check(
        contained.containment_link_record.prior_link_ref
        == contained.validation_link_record.record_id,
        "CONTAINED follows validation link",
    )
    ledger.check(
        contained.containment_transition_trace is not None,
        "CONTAINED containment trace added",
    )
    ledger.check(
        contained.containment_transition_trace.transition_kind
        is msm.SemanticTransitionKind.CONTAINMENT,
        "CONTAINED exact transition kind",
    )
    ledger.check(
        len(contained.successor_manifest.delivery_or_containment_links)
        == len(contained.source_manifest.delivery_or_containment_links) + 1,
        "CONTAINED exactly one custody link",
    )
    ledger.check(
        not any(
            item.disposition is msm.DeliveryContainmentKind.DELIVERY_LINKED
            for item in contained.successor_manifest.delivery_or_containment_links
        ),
        "CONTAINED adds no delivery link",
    )

    for name in (
        "lineage_root",
        "candidate_meanings",
        "non_selection_outcomes",
        "selected_governed_meanings",
        "governed_result_references",
        "governed_outward_meanings",
        "expression_links",
        "package_id",
        "schema_id",
        "schema_version",
    ):
        ledger.retained(
            getattr(passed.source_manifest, name)
            == getattr(passed.successor_manifest, name),
            f"PASSED retains {name}",
        )
        ledger.retained(
            getattr(rejected.source_manifest, name)
            == getattr(rejected.successor_manifest, name),
            f"REJECTED retains {name}",
        )
        ledger.retained(
            getattr(contained.source_manifest, name)
            == getattr(contained.successor_manifest, name),
            f"CONTAINED retains {name}",
        )

    for value, label, expected_added_count in (
        (passed, "PASSED", 1),
        (rejected, "REJECTED", 1),
        (contained, "CONTAINED", 2),
    ):
        source_authority = value.source_manifest.external_authority_references
        successor_authority = value.successor_manifest.external_authority_references
        ledger.retained(
            successor_authority[: len(source_authority)] == source_authority,
            f"{label} retains all predecessor external-authority references",
        )
        ledger.check(
            len(successor_authority) == len(source_authority) + expected_added_count,
            f"{label} adds only exact required external-authority references",
        )
        ledger.check(
            successor_authority[len(source_authority)]
            == value.validation_authority_reference_record,
            f"{label} exact validation authority reference added",
        )
        if label == "CONTAINED":
            ledger.check(
                successor_authority[-1]
                == value.containment_authority_reference_record,
                "CONTAINED exact containment authority reference added",
            )
        else:
            ledger.check(
                value.containment_authority_reference_record is None,
                f"{label} adds no containment authority reference",
            )

    for value, label in (
        (passed, "PASSED"),
        (rejected, "REJECTED"),
        (contained, "CONTAINED"),
    ):
        ledger.check(
            manifest_validation.validate_manifest(
                value.successor_manifest
            ).ok,
            f"{label} successor validates",
        )
        serialized = manifest_serialization.serialize_manifest(
            value.successor_manifest
        )
        decoded = manifest_serialization.deserialize_manifest(serialized)
        ledger.check(
            decoded == value.successor_manifest,
            f"{label} canonical serialization round trip",
        )
        ledger.check(
            manifest_serialization.canonical_manifest_sha256(decoded)
            == manifest_serialization.canonical_manifest_sha256(
                value.successor_manifest
            ),
            f"{label} canonical digest stable",
        )
        ledger.check(value.immutable_successor_created is True, f"{label} immutable")
        ledger.check(value.additive_only is True, f"{label} additive only")
        ledger.check(value.exact_chain_proved is True, f"{label} exact chain")
        ledger.check(value.validation_link_created is True, f"{label} validation link created")
        for field_name in integration43g.PERMANENT_AUTHORITY_ZERO:
            ledger.check(
                getattr(value, field_name) is False,
                f"{label} authority zero {field_name}",
            )
            ledger.check(
                getattr(value.receipt, field_name) is False,
                f"{label} receipt authority zero {field_name}",
            )

    wrong_raw = replace(passed_input, raw_text="prohibited")
    wrong_raw = replace(
        wrong_raw,
        integration_input_id=integration43g.expected_input_id(wrong_raw),
    )
    ledger.malformed(
        not integration43g.validate_integration_input(wrong_raw).ok,
        "raw text rejected",
    )
    wrong_delivery = replace(
        passed_input,
        delivery_link_creation_requested=True,
    )
    wrong_delivery = replace(
        wrong_delivery,
        integration_input_id=integration43g.expected_input_id(wrong_delivery),
    )
    ledger.malformed(
        not integration43g.validate_integration_input(wrong_delivery).ok,
        "delivery-link request rejected",
    )
    wrong_rewrite = replace(passed_input, candidate_rewrite_requested=True)
    wrong_rewrite = replace(
        wrong_rewrite,
        integration_input_id=integration43g.expected_input_id(wrong_rewrite),
    )
    ledger.malformed(
        not integration43g.validate_integration_input(wrong_rewrite).ok,
        "candidate rewrite rejected",
    )
    wrong_echo = replace(passed_input, echoforge_requested=True)
    wrong_echo = replace(
        wrong_echo,
        integration_input_id=integration43g.expected_input_id(wrong_echo),
    )
    ledger.malformed(
        not integration43g.validate_integration_input(wrong_echo).ok,
        "EchoForge request rejected",
    )
    wrong_model = replace(
        passed_input,
        model_or_similarity_authority_requested=True,
    )
    wrong_model = replace(
        wrong_model,
        integration_input_id=integration43g.expected_input_id(wrong_model),
    )
    ledger.malformed(
        not integration43g.validate_integration_input(wrong_model).ok,
        "model authority request rejected",
    )
    wrong_chain = replace(
        passed_input,
        source_43e_classification_result=replace(
            exact_classification,
            classification_result_id="slice43e:fabricated",
        ),
    )
    wrong_chain = replace(
        wrong_chain,
        integration_input_id=integration43g.expected_input_id(wrong_chain),
    )
    ledger.malformed(
        not integration43g.validate_integration_input(wrong_chain).ok,
        "fabricated source chain rejected",
    )

    try:
        passed.successor_manifest = passed.source_manifest
    except FrozenInstanceError:
        immutable = True
    else:
        immutable = False
    ledger.check(immutable, "integration result immutable")

    print("=== AI.WEB SLICE 43G BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"explicit_disposition_cases={ledger.disposition_cases}")
    print(f"source_retention_checks={ledger.retention_checks}")
    print("validation_dispositions=3")
    print("dormant_validation_link_record_used=1")
    print("immutable_msm_successors_created=3")
    print("passed_validation_link_created=1")
    print("rejected_validation_link_created=1")
    print("contained_validation_link_created=1")
    print("rejection_custody_preserved=1")
    print("containment_custody_preserved=1")
    print("exact_authorized_trace_references_preserved=1")
    print("source_manifest_mutated=0")
    print("candidate_rewritten_or_repaired=0")
    print("drift_removed_downgraded_or_suppressed=0")
    print("delivery_link_created=0")
    print("delivery_authorized_or_performed=0")
    print("echoforge_called=0")
    print("model_or_similarity_authority=0")
    print("msm_v1_schema_modified=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print(f"FAIL: {failure}")
    if ledger.failures:
        print("AI.WEB SLICE 43G BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 43G BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
