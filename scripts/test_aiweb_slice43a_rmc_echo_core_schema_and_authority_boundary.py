#!/usr/bin/env python3
"""Visible behavior test for Slice 43A schema-only custody."""

from __future__ import annotations

import dataclasses
from pathlib import Path
import sys


def repository_from_argv() -> Path:
    if len(sys.argv) > 2:
        raise SystemExit("usage: test_aiweb_slice43a_...py [REPOSITORY]")
    return Path(sys.argv[1] if len(sys.argv) == 2 else "/home/nic/forge").resolve()


class Ledger:
    def __init__(self) -> None:
        self.passes = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if condition is True:
            self.passes += 1
        else:
            self.failures.append(label)


def main() -> int:
    repository = repository_from_argv()
    sys.path.insert(0, str(repository))

    from aiweb_language_core_bootstrap.rmc_echo_runtime import (
        ACCEPTED_PARENT_HEAD,
        ACCEPTED_PARENT_SUBJECT,
        ACCEPTED_PARENT_TREE,
        BOOTSTRAP_INTEGRATION_ALLOWED,
        CANONICAL_SERIALIZATION_ALLOWED,
        CONTAINMENT_ISSUANCE_ALLOWED,
        DELIVERY_AUTHORITY_ALLOWED,
        DORMANT_ECHO_VALIDATOR_REUSE_DECISION,
        DRIFT_CLASSIFICATION_ALLOWED,
        ECHO_DISPOSITION_DECISION_ALLOWED,
        ECHO_DISPOSITION_VALUES,
        EXPECTED_COMMIT_SUBJECT,
        EXPRESSION_REPAIR_ALLOWED,
        IDENTITY_VALIDATION_ALLOWED,
        MATERIALITY_DECISION_ALLOWED,
        MEANING_PRESERVATION_COMPARISON_ALLOWED,
        MSM_VALIDATION_LINK_CREATION_ALLOWED,
        MSM_VALIDATION_LINK_INTEGRATION_DECISION,
        MSM_V1_AUTOMATIC_MIGRATION_ALLOWED,
        MSM_V1_SCHEMA_MODIFICATION_ALLOWED,
        PERMANENT_RMC_ECHO_BOUNDARIES,
        PRESERVATION_DIMENSION_VALUES,
        PROHIBITED_AUTHORITY_PATHS,
        REJECTION_ISSUANCE_ALLOWED,
        SCHEMA_VERSION,
        SLICE19_SCAFFOLD_REUSE_DECISION,
        SLICE42_SOURCE_ADMISSION_ALLOWED,
        SLICE42_SOURCE_ADMISSION_DECISION,
        VALIDATION_FINDING_CREATION_ALLOWED,
        AuthorizedMeaningReferenceRecord,
        ContainmentCustodyState,
        DriftFindingBoundaryRecord,
        DriftFindingCustodyState,
        EchoContainmentBoundaryRecord,
        EchoDisposition,
        EchoDispositionBoundaryRecord,
        EchoDispositionCustodyState,
        EchoReceiptBoundaryRecord,
        EchoRejectionBoundaryRecord,
        EchoTraceBoundaryRecord,
        EchoValidationInputBoundaryRecord,
        EchoValidationInputCustodyState,
        PreservationDimension,
        PreservationDimensionRequirementRecord,
        ProposedExpressionReferenceRecord,
        RejectionCustodyState,
        RmcEchoRuntimeSchemaRecord,
        ValidationFindingBoundaryRecord,
        ValidationFindingCustodyState,
    )

    ledger = Ledger()
    ledger.check(repository.is_dir(), "repository exists")
    ledger.check(ACCEPTED_PARENT_HEAD == "ebe931909b59a40ac4ef202b89d8f4f2702104a3", "parent head")
    ledger.check(ACCEPTED_PARENT_TREE == "efab06b171dfd5a34b56c0cff81026788e40a1e0", "parent tree")
    ledger.check(ACCEPTED_PARENT_SUBJECT == "Slice 42H disabled bootstrap integration and Slice 42 closeout", "parent subject")
    ledger.check(EXPECTED_COMMIT_SUBJECT == "Slice 43A RMC Echo core schema and authority boundary", "commit subject")
    ledger.check(SCHEMA_VERSION == "aiweb-slice43a-rmc-echo-core-schema-v1", "schema version")
    ledger.check(ECHO_DISPOSITION_VALUES == ("PASSED", "REJECTED", "CONTAINED"), "disposition vocabulary")
    ledger.check(tuple(item.value for item in EchoDisposition) == ECHO_DISPOSITION_VALUES, "disposition enum order")
    ledger.check(tuple(item.value for item in PreservationDimension) == PRESERVATION_DIMENSION_VALUES, "dimension enum order")
    ledger.check(len(PRESERVATION_DIMENSION_VALUES) == 22, "dimension count")
    ledger.check(len(PERMANENT_RMC_ECHO_BOUNDARIES) >= 40, "permanent boundary count")
    ledger.check(len(PROHIBITED_AUTHORITY_PATHS) >= 40, "prohibited path count")
    ledger.check(SLICE42_SOURCE_ADMISSION_DECISION == "deferred_to_slice43c_exact_slice42_ancestry_admission", "43C deferral")
    ledger.check(MSM_VALIDATION_LINK_INTEGRATION_DECISION == "deferred_to_slice43g_exact_additive_adapter", "43G deferral")
    ledger.check(SLICE19_SCAFFOLD_REUSE_DECISION == "protected_historical_boundary_only_not_runtime_authority", "Slice 19 historical")
    ledger.check(DORMANT_ECHO_VALIDATOR_REUSE_DECISION == "historical_only_no_import_no_call_no_runtime_authority", "legacy validator historical")

    for value, label in (
        (IDENTITY_VALIDATION_ALLOWED, "identity validation denied"),
        (CANONICAL_SERIALIZATION_ALLOWED, "serialization denied"),
        (SLICE42_SOURCE_ADMISSION_ALLOWED, "source admission denied"),
        (MEANING_PRESERVATION_COMPARISON_ALLOWED, "comparison denied"),
        (VALIDATION_FINDING_CREATION_ALLOWED, "finding creation denied"),
        (DRIFT_CLASSIFICATION_ALLOWED, "drift classification denied"),
        (MATERIALITY_DECISION_ALLOWED, "materiality denied"),
        (ECHO_DISPOSITION_DECISION_ALLOWED, "disposition denied"),
        (REJECTION_ISSUANCE_ALLOWED, "rejection denied"),
        (CONTAINMENT_ISSUANCE_ALLOWED, "containment denied"),
        (EXPRESSION_REPAIR_ALLOWED, "repair denied"),
        (MSM_VALIDATION_LINK_CREATION_ALLOWED, "MSM link denied"),
        (MSM_V1_SCHEMA_MODIFICATION_ALLOWED, "MSM rewrite denied"),
        (MSM_V1_AUTOMATIC_MIGRATION_ALLOWED, "MSM migration denied"),
        (BOOTSTRAP_INTEGRATION_ALLOWED, "bootstrap denied"),
        (DELIVERY_AUTHORITY_ALLOWED, "delivery denied"),
    ):
        ledger.check(value is False, label)

    authorized = AuthorizedMeaningReferenceRecord(
        authorized_meaning_reference_id="echo-meaning-ref-1",
        slice42g_integration_input_ref="slice42g-input-1",
        slice42g_integration_result_ref="slice42g-result-1",
        slice42g_integration_receipt_ref="slice42g-receipt-1",
        slice42h_acceptance_record_ref="slice42h-acceptance-1",
        source_manifest_ref="manifest-before",
        successor_manifest_ref="manifest-after",
        lineage_id="lineage-1",
        selected_governed_meaning_ref="selected-meaning-1",
        selected_candidate_ref="candidate-1",
        selection_authority_reference_ref="selection-authority-1",
        governed_outward_meaning_ref="outward-meaning-1",
        outward_expression_authority_ref="expression-authority-1",
        expression_eligibility_result_ref="eligibility-result-1",
        preservation_obligation_package_ref="obligation-package-1",
        expression_plan_ref="expression-plan-1",
        selected_meaning_content_proof_ref="selected-proof-1",
        governed_outward_meaning_content_proof_ref="outward-proof-1",
        preserved_alternative_refs=("candidate-2",),
        unresolved_condition_refs=("unresolved-1",),
        inherited_limitation_refs=("limitation-1",),
        required_qualification_refs=("qualification-1",),
        required_caveat_refs=("caveat-1",),
        refusal_relevant_boundary_refs=("refusal-1",),
        ambiguity_refs=("ambiguity-1",),
        privacy_identity_boundary_refs=("privacy-1",),
        preservation_class_refs=("unresolved_ambiguity",),
        version_refs=("slice42g-v1", "slice42h-v1"),
    )
    proposed = ProposedExpressionReferenceRecord(
        proposed_expression_reference_id="echo-expression-ref-1",
        slice42f_realization_input_ref="slice42f-input-1",
        slice42f_realization_result_ref="slice42f-result-1",
        slice42f_realization_receipt_ref="slice42f-receipt-1",
        slice42g_integration_input_ref="slice42g-input-1",
        slice42g_integration_result_ref="slice42g-result-1",
        slice42g_integration_receipt_ref="slice42g-receipt-1",
        successor_manifest_ref="manifest-after",
        lineage_id="lineage-1",
        expression_link_ref="expression-link-1",
        expression_candidate_ref="expression-candidate-1",
        realized_expression_ref="realized-expression-1",
        expression_plan_ref="expression-plan-1",
        governed_outward_meaning_ref="outward-meaning-1",
        preservation_obligation_package_ref="obligation-package-1",
        realized_text_sha256="0" * 64,
        realization_trace_ref="realization-trace-1",
        realization_receipt_ref="realization-receipt-1",
        admitted_realization_rule_refs=("rule-1",),
        controlled_resource_refs=("resource-1",),
        applied_rule_refs=("rule-1",),
        applied_resource_refs=("resource-1",),
        segment_refs=("segment-1",),
        version_refs=("slice42f-v1", "slice42g-v1"),
    )
    validation_input = EchoValidationInputBoundaryRecord(
        validation_input_boundary_id="echo-input-1",
        authorized_meaning_reference=authorized,
        proposed_expression_reference=proposed,
        custody_state=EchoValidationInputCustodyState.NOT_ADMITTED,
        required_preservation_dimensions=tuple(PreservationDimension),
        predecessor_receipt_refs=("slice42h-receipt-1",),
        authority_version_refs=(("slice42", "v1"),),
        schema_version_refs=(("MSM-v1", "MSM-v1"),),
        later_admitter_ref="slice43c-admitter",
    )
    requirement = PreservationDimensionRequirementRecord(
        dimension_requirement_id="dimension-requirement-1",
        validation_input_boundary_ref="echo-input-1",
        dimension=PreservationDimension.UNRESOLVED_AMBIGUITY,
        authorized_meaning_feature_refs=("unresolved-1",),
        proposed_expression_feature_refs=("segment-1",),
        required_preservation_refs=("must-remain-unresolved",),
        allowed_variation_refs=("surface-form-only",),
        prohibited_drift_refs=("silent-resolution",),
        later_comparator_ref="slice43d-comparator",
    )
    finding = ValidationFindingBoundaryRecord(
        validation_finding_boundary_id="validation-finding-1",
        validation_input_boundary_ref="echo-input-1",
        dimension_requirement_ref="dimension-requirement-1",
        dimension=PreservationDimension.UNRESOLVED_AMBIGUITY,
        custody_state=ValidationFindingCustodyState.NOT_COMPARED,
        authorized_meaning_feature_refs=("unresolved-1",),
        proposed_expression_feature_refs=("segment-1",),
        finding_reason_refs=("not-compared-in-43a",),
        later_comparator_ref="slice43d-comparator",
    )
    drift = DriftFindingBoundaryRecord(
        drift_finding_boundary_id="drift-finding-1",
        validation_input_boundary_ref="echo-input-1",
        validation_finding_boundary_ref="validation-finding-1",
        dimension=PreservationDimension.UNRESOLVED_AMBIGUITY,
        custody_state=DriftFindingCustodyState.NOT_CLASSIFIED,
        candidate_drift_evidence_refs=("future-evidence-1",),
        candidate_materiality_refs=("future-materiality-1",),
        classification_reason_refs=("not-classified-in-43a",),
        later_classifier_ref="slice43e-classifier",
    )
    disposition = EchoDispositionBoundaryRecord(
        echo_disposition_boundary_id="disposition-1",
        validation_input_boundary_ref="echo-input-1",
        validation_finding_boundary_refs=("validation-finding-1",),
        drift_finding_boundary_refs=("drift-finding-1",),
        custody_state=EchoDispositionCustodyState.NOT_DECIDED,
        decision_reason_refs=("not-decided-in-43a",),
        later_decider_ref="slice43f-decider",
    )
    rejection = EchoRejectionBoundaryRecord(
        echo_rejection_boundary_id="rejection-1",
        validation_input_boundary_ref="echo-input-1",
        echo_disposition_boundary_ref="disposition-1",
        custody_state=RejectionCustodyState.NOT_ISSUED,
        candidate_rejection_reason_refs=("future-rejection-reason",),
        preserved_ancestry_refs=("manifest-after",),
        prohibited_consequence_refs=("delivery",),
        later_rejection_issuer_ref="slice43f-rejection-issuer",
    )
    containment = EchoContainmentBoundaryRecord(
        echo_containment_boundary_id="containment-1",
        validation_input_boundary_ref="echo-input-1",
        echo_disposition_boundary_ref="disposition-1",
        custody_state=ContainmentCustodyState.NOT_ISSUED,
        candidate_containment_reason_refs=("future-containment-reason",),
        preserved_ancestry_refs=("manifest-after",),
        downstream_prohibition_refs=("delivery", "memory-write"),
        later_containment_issuer_ref="slice43f-containment-issuer",
    )
    trace = EchoTraceBoundaryRecord(
        echo_trace_boundary_id="trace-1",
        authorized_meaning_reference_ref="echo-meaning-ref-1",
        proposed_expression_reference_ref="echo-expression-ref-1",
        validation_input_boundary_ref="echo-input-1",
        preservation_dimension_requirement_refs=("dimension-requirement-1",),
        validation_finding_boundary_refs=("validation-finding-1",),
        drift_finding_boundary_refs=("drift-finding-1",),
        echo_disposition_boundary_ref="disposition-1",
        rejection_boundary_ref="rejection-1",
        containment_boundary_ref="containment-1",
        predecessor_trace_refs=("realization-trace-1",),
        predecessor_receipt_refs=("realization-receipt-1",),
        authority_version_refs=(("slice43a", "v1"),),
        schema_version_refs=(("rmc-echo", SCHEMA_VERSION),),
    )
    receipt = EchoReceiptBoundaryRecord(
        echo_receipt_boundary_id="receipt-1",
        authorized_meaning_reference_ref="echo-meaning-ref-1",
        proposed_expression_reference_ref="echo-expression-ref-1",
        validation_input_boundary_ref="echo-input-1",
        echo_trace_boundary_ref="trace-1",
        echo_disposition_boundary_ref="disposition-1",
        rejection_boundary_ref="rejection-1",
        containment_boundary_ref="containment-1",
        required_law_refs=("document-9", "canonical-roadmap:slice43a"),
        prohibited_consequence_refs=("delivery", "execution"),
        audit_note="Schema boundary only; no Echo decision performed.",
    )
    aggregate = RmcEchoRuntimeSchemaRecord(
        rmc_echo_runtime_schema_record_id="rmc-echo-schema-record-1",
        authorized_meaning_reference=authorized,
        proposed_expression_reference=proposed,
        validation_input_boundary=validation_input,
        preservation_dimension_requirements=(requirement,),
        validation_finding_boundaries=(finding,),
        drift_finding_boundaries=(drift,),
        echo_disposition_boundary=disposition,
        rejection_boundary=rejection,
        containment_boundary=containment,
        trace_boundary=trace,
        receipt_boundary=receipt,
    )

    record_types = (
        AuthorizedMeaningReferenceRecord,
        ProposedExpressionReferenceRecord,
        EchoValidationInputBoundaryRecord,
        PreservationDimensionRequirementRecord,
        ValidationFindingBoundaryRecord,
        DriftFindingBoundaryRecord,
        EchoDispositionBoundaryRecord,
        EchoRejectionBoundaryRecord,
        EchoContainmentBoundaryRecord,
        EchoTraceBoundaryRecord,
        EchoReceiptBoundaryRecord,
        RmcEchoRuntimeSchemaRecord,
    )
    for record_type in record_types:
        params = record_type.__dataclass_params__
        ledger.check(params.frozen is True, f"{record_type.__name__} frozen")
        ledger.check(hasattr(record_type, "__slots__"), f"{record_type.__name__} slotted")

    for record in (authorized, proposed, validation_input, requirement, finding, drift, disposition, rejection, containment, trace, receipt, aggregate):
        ledger.check(record.schema_version == SCHEMA_VERSION, f"{type(record).__name__} schema version")

    locked_false = (
        (authorized.source_admitted, "authorized source not admitted"),
        (proposed.source_admitted, "proposed source not admitted"),
        (validation_input.input_admitted, "validation input not admitted"),
        (requirement.comparison_performed, "dimension not compared"),
        (finding.comparison_performed, "finding comparison not performed"),
        (drift.drift_classified, "drift not classified"),
        (drift.materiality_decided, "materiality not decided"),
        (disposition.disposition_decided, "disposition not decided"),
        (rejection.rejection_issued, "rejection not issued"),
        (containment.containment_issued, "containment not issued"),
        (trace.trace_created, "trace not created"),
        (receipt.receipt_created, "receipt not created"),
        (aggregate.validation_performed, "validation not performed"),
        (aggregate.meaning_preservation_comparison_performed, "aggregate comparison not performed"),
        (aggregate.echo_disposition_decided, "aggregate disposition not decided"),
        (aggregate.msm_v1_validation_link_integrated, "MSM validation link not integrated"),
        (aggregate.delivered, "not delivered"),
        (aggregate.language_model_used, "no language model"),
        (aggregate.legacy_echo_validator_used, "no legacy validator"),
        (aggregate.echo_forge_used, "no EchoForge"),
        (aggregate.gp014_superseded, "GP-014 not superseded"),
    )
    for value, label in locked_false:
        ledger.check(value is False, label)
    ledger.check(finding.finding_outcome_ref is None, "finding outcome absent")
    ledger.check(drift.drift_classification_ref is None, "drift classification absent")
    ledger.check(drift.materiality_ref is None, "materiality absent")
    ledger.check(disposition.disposition is None, "disposition absent")
    ledger.check(aggregate.schema_only is True, "schema only")
    ledger.check(aggregate.trace_boundary.trace_boundary_only is True, "trace boundary only")
    ledger.check(aggregate.receipt_boundary.receipt_boundary_only is True, "receipt boundary only")

    try:
        aggregate.validation_performed = True
    except (dataclasses.FrozenInstanceError, AttributeError):
        ledger.check(True, "aggregate immutable")
    else:
        ledger.check(False, "aggregate immutable")

    try:
        EchoDispositionBoundaryRecord(
            echo_disposition_boundary_id="bad",
            validation_input_boundary_ref="bad",
            validation_finding_boundary_refs=(),
            drift_finding_boundary_refs=(),
            custody_state=EchoDispositionCustodyState.NOT_DECIDED,
            decision_reason_refs=(),
            later_decider_ref=None,
            disposition=EchoDisposition.PASSED,
        )
    except TypeError:
        ledger.check(True, "disposition cannot be initialized in 43A")
    else:
        ledger.check(False, "disposition cannot be initialized in 43A")

    print("=== AI.WEB SLICE 43A BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"checks={ledger.passes + len(ledger.failures)}")
    print(f"passes={ledger.passes}")
    print(f"failures={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL:", failure)
    verdict = "PASS" if not ledger.failures else "FAIL"
    print(f"SLICE 43A BEHAVIOR: {verdict}")
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
