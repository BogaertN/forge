#!/usr/bin/env python3
"""Visible behavior test for Slice 43B deterministic RMC Echo governance."""

from __future__ import annotations

from dataclasses import fields, replace
import dataclasses
from pathlib import Path
import sys


def repository_from_argv() -> Path:
    if len(sys.argv) > 2:
        raise SystemExit("usage: test_aiweb_slice43b_...py [REPOSITORY]")
    return Path(sys.argv[1] if len(sys.argv) == 2 else "/home/nic/forge").resolve()


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []
        self.malformed_cases = 0

    def check(self, condition: bool, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: bool, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)


def _fixture(core, governance):
    authorized = core.AuthorizedMeaningReferenceRecord(
        authorized_meaning_reference_id="pending:authorized",
        slice42g_integration_input_ref="slice42g:input:fixture",
        slice42g_integration_result_ref="slice42g:result:fixture",
        slice42g_integration_receipt_ref="slice42g:receipt:fixture",
        slice42h_acceptance_record_ref="slice42h:acceptance:fixture",
        source_manifest_ref="msm:source:fixture",
        successor_manifest_ref="msm:successor:fixture",
        lineage_id="lineage:fixture",
        selected_governed_meaning_ref="selected:meaning:fixture",
        selected_candidate_ref="candidate:selected:fixture",
        selection_authority_reference_ref="selection:authority:fixture",
        governed_outward_meaning_ref="outward:meaning:fixture",
        outward_expression_authority_ref="expression:authority:fixture",
        expression_eligibility_result_ref="expression:eligibility:fixture",
        preservation_obligation_package_ref="preservation:package:fixture",
        expression_plan_ref="expression:plan:fixture",
        selected_meaning_content_proof_ref="selected:proof:fixture",
        governed_outward_meaning_content_proof_ref="outward:proof:fixture",
        preserved_alternative_refs=("candidate:alternative:fixture",),
        unresolved_condition_refs=("unresolved:fixture",),
        inherited_limitation_refs=("limitation:fixture",),
        required_qualification_refs=("qualification:fixture",),
        required_caveat_refs=("caveat:fixture",),
        refusal_relevant_boundary_refs=("refusal:fixture",),
        ambiguity_refs=("ambiguity:fixture",),
        privacy_identity_boundary_refs=("privacy:fixture",),
        preservation_class_refs=("unresolved_ambiguity",),
        version_refs=("slice42g:v1", "slice42h:v1"),
    )
    authorized = governance.with_expected_id(authorized)

    proposed = core.ProposedExpressionReferenceRecord(
        proposed_expression_reference_id="pending:proposed",
        slice42f_realization_input_ref="slice42f:input:fixture",
        slice42f_realization_result_ref="slice42f:result:fixture",
        slice42f_realization_receipt_ref="slice42f:receipt:fixture",
        slice42g_integration_input_ref=authorized.slice42g_integration_input_ref,
        slice42g_integration_result_ref=authorized.slice42g_integration_result_ref,
        slice42g_integration_receipt_ref=authorized.slice42g_integration_receipt_ref,
        successor_manifest_ref=authorized.successor_manifest_ref,
        lineage_id=authorized.lineage_id,
        expression_link_ref="expression:link:fixture",
        expression_candidate_ref="expression:candidate:fixture",
        realized_expression_ref="realized:expression:fixture",
        expression_plan_ref=authorized.expression_plan_ref,
        governed_outward_meaning_ref=authorized.governed_outward_meaning_ref,
        preservation_obligation_package_ref=(
            authorized.preservation_obligation_package_ref
        ),
        realized_text_sha256="0123456789abcdef" * 4,
        realization_trace_ref="realization:trace:fixture",
        realization_receipt_ref="realization:receipt:fixture",
        admitted_realization_rule_refs=("realization:rule:fixture",),
        controlled_resource_refs=("controlled:resource:fixture",),
        applied_rule_refs=("realization:rule:fixture",),
        applied_resource_refs=("controlled:resource:fixture",),
        segment_refs=("segment:fixture",),
        version_refs=("slice42f:v1", "slice42g:v1"),
    )
    proposed = governance.with_expected_id(proposed)

    validation_input = core.EchoValidationInputBoundaryRecord(
        validation_input_boundary_id="pending:input",
        authorized_meaning_reference=authorized,
        proposed_expression_reference=proposed,
        custody_state=core.EchoValidationInputCustodyState.NOT_ADMITTED,
        required_preservation_dimensions=tuple(core.PreservationDimension),
        predecessor_receipt_refs=(
            authorized.slice42g_integration_receipt_ref,
            authorized.slice42h_acceptance_record_ref,
            proposed.slice42f_realization_receipt_ref,
        ),
        authority_version_refs=(("slice43a", "v1"),),
        schema_version_refs=(("rmc_echo_runtime", core.SCHEMA_VERSION),),
        later_admitter_ref="slice43c:admitter",
    )
    validation_input = governance.with_expected_id(validation_input)

    requirements = []
    findings = []
    drifts = []
    for index, dimension in enumerate(core.PreservationDimension):
        token = dimension.value
        requirement = core.PreservationDimensionRequirementRecord(
            dimension_requirement_id=f"pending:requirement:{index}",
            validation_input_boundary_ref=(
                validation_input.validation_input_boundary_id
            ),
            dimension=dimension,
            authorized_meaning_feature_refs=(
                f"authorized:feature:{token}",
            ),
            proposed_expression_feature_refs=(
                f"expression:feature:{token}",
            ),
            required_preservation_refs=(
                f"preserve:{token}",
            ),
            allowed_variation_refs=(
                f"surface:variation:{token}",
            ),
            prohibited_drift_refs=(
                f"prohibited:drift:{token}",
            ),
            later_comparator_ref="slice43d:comparator",
        )
        requirement = governance.with_expected_id(requirement)
        requirements.append(requirement)

        finding = core.ValidationFindingBoundaryRecord(
            validation_finding_boundary_id=f"pending:finding:{index}",
            validation_input_boundary_ref=(
                validation_input.validation_input_boundary_id
            ),
            dimension_requirement_ref=requirement.dimension_requirement_id,
            dimension=dimension,
            custody_state=core.ValidationFindingCustodyState.NOT_COMPARED,
            authorized_meaning_feature_refs=(
                requirement.authorized_meaning_feature_refs
            ),
            proposed_expression_feature_refs=(
                requirement.proposed_expression_feature_refs
            ),
            finding_reason_refs=(
                f"slice43b:not_compared:{token}",
            ),
            later_comparator_ref="slice43d:comparator",
        )
        finding = governance.with_expected_id(finding)
        findings.append(finding)

        drift = core.DriftFindingBoundaryRecord(
            drift_finding_boundary_id=f"pending:drift:{index}",
            validation_input_boundary_ref=(
                validation_input.validation_input_boundary_id
            ),
            validation_finding_boundary_ref=(
                finding.validation_finding_boundary_id
            ),
            dimension=dimension,
            custody_state=core.DriftFindingCustodyState.NOT_CLASSIFIED,
            candidate_drift_evidence_refs=(
                f"future:drift:evidence:{token}",
            ),
            candidate_materiality_refs=(
                f"future:materiality:{token}",
            ),
            classification_reason_refs=(
                f"slice43b:not_classified:{token}",
            ),
            later_classifier_ref="slice43e:classifier",
        )
        drift = governance.with_expected_id(drift)
        drifts.append(drift)

    requirements = tuple(requirements)
    findings = tuple(findings)
    drifts = tuple(drifts)

    disposition = core.EchoDispositionBoundaryRecord(
        echo_disposition_boundary_id="pending:disposition",
        validation_input_boundary_ref=(
            validation_input.validation_input_boundary_id
        ),
        validation_finding_boundary_refs=tuple(
            item.validation_finding_boundary_id for item in findings
        ),
        drift_finding_boundary_refs=tuple(
            item.drift_finding_boundary_id for item in drifts
        ),
        custody_state=core.EchoDispositionCustodyState.NOT_DECIDED,
        decision_reason_refs=("slice43b:not_decided",),
        later_decider_ref="slice43f:decider",
    )
    disposition = governance.with_expected_id(disposition)

    rejection = core.EchoRejectionBoundaryRecord(
        echo_rejection_boundary_id="pending:rejection",
        validation_input_boundary_ref=(
            validation_input.validation_input_boundary_id
        ),
        echo_disposition_boundary_ref=(
            disposition.echo_disposition_boundary_id
        ),
        custody_state=core.RejectionCustodyState.NOT_ISSUED,
        candidate_rejection_reason_refs=("future:rejection:reason",),
        preserved_ancestry_refs=(authorized.successor_manifest_ref,),
        prohibited_consequence_refs=("delivery",),
        later_rejection_issuer_ref="slice43f:rejection_issuer",
    )
    rejection = governance.with_expected_id(rejection)

    containment = core.EchoContainmentBoundaryRecord(
        echo_containment_boundary_id="pending:containment",
        validation_input_boundary_ref=(
            validation_input.validation_input_boundary_id
        ),
        echo_disposition_boundary_ref=(
            disposition.echo_disposition_boundary_id
        ),
        custody_state=core.ContainmentCustodyState.NOT_ISSUED,
        candidate_containment_reason_refs=("future:containment:reason",),
        preserved_ancestry_refs=(authorized.successor_manifest_ref,),
        downstream_prohibition_refs=("delivery", "memory_write"),
        later_containment_issuer_ref="slice43f:containment_issuer",
    )
    containment = governance.with_expected_id(containment)

    trace = core.EchoTraceBoundaryRecord(
        echo_trace_boundary_id="pending:trace",
        authorized_meaning_reference_ref=(
            authorized.authorized_meaning_reference_id
        ),
        proposed_expression_reference_ref=(
            proposed.proposed_expression_reference_id
        ),
        validation_input_boundary_ref=(
            validation_input.validation_input_boundary_id
        ),
        preservation_dimension_requirement_refs=tuple(
            item.dimension_requirement_id for item in requirements
        ),
        validation_finding_boundary_refs=tuple(
            item.validation_finding_boundary_id for item in findings
        ),
        drift_finding_boundary_refs=tuple(
            item.drift_finding_boundary_id for item in drifts
        ),
        echo_disposition_boundary_ref=(
            disposition.echo_disposition_boundary_id
        ),
        rejection_boundary_ref=rejection.echo_rejection_boundary_id,
        containment_boundary_ref=(
            containment.echo_containment_boundary_id
        ),
        predecessor_trace_refs=(proposed.realization_trace_ref,),
        predecessor_receipt_refs=(
            proposed.realization_receipt_ref,
            authorized.slice42g_integration_receipt_ref,
        ),
        authority_version_refs=(("slice43a", "v1"),),
        schema_version_refs=(("rmc_echo_runtime", core.SCHEMA_VERSION),),
    )
    trace = governance.with_expected_id(trace)

    receipt = core.EchoReceiptBoundaryRecord(
        echo_receipt_boundary_id="pending:receipt",
        authorized_meaning_reference_ref=(
            authorized.authorized_meaning_reference_id
        ),
        proposed_expression_reference_ref=(
            proposed.proposed_expression_reference_id
        ),
        validation_input_boundary_ref=(
            validation_input.validation_input_boundary_id
        ),
        echo_trace_boundary_ref=trace.echo_trace_boundary_id,
        echo_disposition_boundary_ref=(
            disposition.echo_disposition_boundary_id
        ),
        rejection_boundary_ref=rejection.echo_rejection_boundary_id,
        containment_boundary_ref=(
            containment.echo_containment_boundary_id
        ),
        required_law_refs=(
            "canonical_roadmap:slice43b",
            "document9:validation_only",
        ),
        prohibited_consequence_refs=(
            "source_admission",
            "meaning_comparison",
            "drift_classification",
            "disposition_decision",
            "delivery",
        ),
        audit_note="Validated structure only; no Echo decision performed.",
    )
    receipt = governance.with_expected_id(receipt)

    aggregate = core.RmcEchoRuntimeSchemaRecord(
        rmc_echo_runtime_schema_record_id="pending:aggregate",
        authorized_meaning_reference=authorized,
        proposed_expression_reference=proposed,
        validation_input_boundary=validation_input,
        preservation_dimension_requirements=requirements,
        validation_finding_boundaries=findings,
        drift_finding_boundaries=drifts,
        echo_disposition_boundary=disposition,
        rejection_boundary=rejection,
        containment_boundary=containment,
        trace_boundary=trace,
        receipt_boundary=receipt,
    )
    return governance.with_expected_id(aggregate)


def _version_custody(governance, aggregate):
    record = governance.RmcEchoVersionCustody(
        custody_id="pending:version",
        runtime_schema_record_id=(
            aggregate.rmc_echo_runtime_schema_record_id
        ),
        runtime_schema_version=aggregate.schema_version,
        runtime_schema_id=aggregate.schema_id,
        runtime_spec_id=aggregate.spec_id,
        runtime_spec_version=aggregate.spec_version,
        validation_profile_version=governance.VALIDATION_PROFILE_VERSION,
        record_schema_versions=governance.expected_record_schema_versions(
            aggregate
        ),
        predecessor_references=governance.expected_predecessor_references(
            aggregate
        ),
        accepted_parent_head=governance.SLICE43B_ACCEPTED_PARENT_HEAD,
        accepted_parent_tree=governance.SLICE43B_ACCEPTED_PARENT_TREE,
        accepted_parent_subject=governance.SLICE43B_ACCEPTED_PARENT_SUBJECT,
        canonical_field_order_version=(
            governance.CANONICAL_FIELD_ORDER_VERSION
        ),
        digest_algorithm=governance.DIGEST_ALGORITHM,
        non_llm_provenance=True,
        timestamps_in_identity=False,
        randomness_in_identity=False,
        process_identity_in_identity=False,
        filesystem_state_in_identity=False,
        environment_state_in_identity=False,
        hash_table_order_in_identity=False,
        slice42_source_admission_authorized=False,
        meaning_preservation_comparison_authorized=False,
        validation_finding_construction_authorized=False,
        drift_classification_authorized=False,
        materiality_decision_authorized=False,
        echo_disposition_decision_authorized=False,
        rejection_or_containment_issuance_authorized=False,
        expression_repair_authorized=False,
        msm_v1_mutation_or_integration_authorized=False,
        bootstrap_integration_authorized=False,
        delivery_authorized=False,
        truth_evidence_permission_execution_authorized=False,
        route_api_network_filesystem_memory_tool_action_authorized=False,
        external_resource_authority=False,
        model_embedding_vector_rag_similarity_authority=False,
        gp014_supersession_authorized=False,
    )
    return governance.with_expected_id(record)


def _lifecycle(governance, aggregate, version):
    stages = (
        governance.RmcEchoLifecycleStage.SCHEMA_DECLARED,
        governance.RmcEchoLifecycleStage.VERSION_BOUND,
        governance.RmcEchoLifecycleStage.PREDECESSORS_BOUND,
        governance.RmcEchoLifecycleStage.CROSS_RECORD_VALIDATED,
        governance.RmcEchoLifecycleStage.RECORD_VALIDATED,
        governance.RmcEchoLifecycleStage.RECORD_SEALED,
    )
    kinds = (
        governance.RmcEchoLifecycleTransitionKind.BIND_VERSION,
        governance.RmcEchoLifecycleTransitionKind.BIND_PREDECESSORS,
        governance.RmcEchoLifecycleTransitionKind.VALIDATE_CROSS_RECORDS,
        governance.RmcEchoLifecycleTransitionKind.VALIDATE_RECORD,
        governance.RmcEchoLifecycleTransitionKind.SEAL_RECORD,
    )
    predecessor_ids = tuple(
        f"{name}={value}"
        for name, value in version.predecessor_references
    )
    records = []
    transitions = []
    previous_record = None
    previous_transition = None
    for index, stage in enumerate(stages):
        validated = stage in {
            governance.RmcEchoLifecycleStage.RECORD_VALIDATED,
            governance.RmcEchoLifecycleStage.RECORD_SEALED,
        }
        predecessor_validated = stage in {
            governance.RmcEchoLifecycleStage.PREDECESSORS_BOUND,
            governance.RmcEchoLifecycleStage.CROSS_RECORD_VALIDATED,
            governance.RmcEchoLifecycleStage.RECORD_VALIDATED,
            governance.RmcEchoLifecycleStage.RECORD_SEALED,
        }
        cross_validated = stage in {
            governance.RmcEchoLifecycleStage.CROSS_RECORD_VALIDATED,
            governance.RmcEchoLifecycleStage.RECORD_VALIDATED,
            governance.RmcEchoLifecycleStage.RECORD_SEALED,
        }
        record = governance.RmcEchoLifecycleRecord(
            lifecycle_record_id=f"pending:lifecycle:{index}",
            runtime_schema_record_id=(
                aggregate.rmc_echo_runtime_schema_record_id
            ),
            version_custody_ref=version.custody_id,
            validation_profile_version=(
                governance.VALIDATION_PROFILE_VERSION
            ),
            stage=stage,
            predecessor_lifecycle_record_ids=(
                (previous_record.lifecycle_record_id,)
                if previous_record is not None
                else ()
            ),
            predecessor_reference_ids=predecessor_ids,
            validation_issue_digest_refs=(),
            reason_refs=(f"slice43b:stage:{stage.value}",),
            automatic_progression=False,
            canonical_serialization_performed=validated,
            deterministic_identity_validated=validated,
            predecessor_references_validated=predecessor_validated,
            cross_record_consistency_validated=cross_validated,
            malformed_record_rejected=False,
            unknown_version_rejected=False,
            duplicate_record_rejected=False,
            identity_collision_rejected=False,
            structural_validity_grants_echo_authority=False,
            slice42_sources_admitted=False,
            meaning_preservation_comparison_performed=False,
            validation_findings_created=False,
            drift_findings_created=False,
            materiality_decided=False,
            echo_disposition_decided=False,
            rejection_issued=False,
            containment_issued=False,
            expression_repaired=False,
            msm_v1_modified_or_integrated=False,
            bootstrap_integration_enabled=False,
            delivered=False,
            truth_determined=False,
            evidence_validated=False,
            permission_granted=False,
            execution_authorized=False,
            route_or_api_created=False,
            tool_invoked=False,
            action_performed=False,
            memory_accessed_or_written=False,
            filesystem_or_network_accessed=False,
            external_resource_loaded=False,
            model_or_similarity_authority_used=False,
            gp014_superseded=False,
        )
        record = governance.with_expected_id(record)
        records.append(record)
        if previous_record is not None:
            transition = governance.RmcEchoLifecycleTransitionRecord(
                transition_id=f"pending:transition:{index - 1}",
                runtime_schema_record_id=(
                    aggregate.rmc_echo_runtime_schema_record_id
                ),
                source_lifecycle_record_id=(
                    previous_record.lifecycle_record_id
                ),
                target_lifecycle_record_id=record.lifecycle_record_id,
                from_stage=previous_record.stage,
                to_stage=record.stage,
                transition_kind=kinds[index - 1],
                version_custody_ref=version.custody_id,
                validation_profile_version=(
                    governance.VALIDATION_PROFILE_VERSION
                ),
                predecessor_transition_refs=(
                    (previous_transition.transition_id,)
                    if previous_transition is not None
                    else ()
                ),
                reason_refs=(
                    f"slice43b:transition:{kinds[index - 1].value}",
                ),
                automatic_transition=False,
                structural_validity_grants_echo_authority=False,
                slice42_source_admission_authorized=False,
                meaning_preservation_comparison_authorized=False,
                drift_classification_authorized=False,
                disposition_decision_authorized=False,
                rejection_or_containment_authorized=False,
                expression_repair_authorized=False,
                msm_v1_integration_authorized=False,
                delivery_authorized=False,
                downstream_authority_authorized=False,
                model_or_similarity_authority_used=False,
                gp014_supersession_authorized=False,
            )
            transition = governance.with_expected_id(transition)
            transitions.append(transition)
            previous_transition = transition
        previous_record = record
    return tuple(records), tuple(transitions)


def _bundle(governance, aggregate, version, lifecycle_records, transitions):
    record = governance.RmcEchoGovernanceBundle(
        bundle_id="pending:bundle",
        bundle_digest="0" * 64,
        runtime_schema_record=aggregate,
        version_custody=version,
        lifecycle_records=lifecycle_records,
        lifecycle_transitions=transitions,
        validation_only=True,
        immutable_successor_records=True,
        exact_predecessor_references_required=True,
        duplicate_and_collision_rejection_required=True,
        unknown_version_rejection_required=True,
        malformed_record_rejection_required=True,
        cross_record_consistency_required=True,
        structural_validity_grants_echo_authority=False,
        slice42_sources_admitted=False,
        meaning_preservation_comparison_performed=False,
        validation_findings_created=False,
        drift_findings_created=False,
        materiality_decided=False,
        echo_disposition_decided=False,
        rejection_issued=False,
        containment_issued=False,
        expression_repaired=False,
        msm_v1_modified_or_integrated=False,
        bootstrap_integration_enabled=False,
        delivered=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_or_api_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed_or_written=False,
        filesystem_or_network_accessed=False,
        external_resource_loaded=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    return governance.with_expected_bundle_identity(record)


def main() -> int:
    repository = repository_from_argv()
    sys.path.insert(0, str(repository))

    import aiweb_language_core_bootstrap.rmc_echo_runtime as core
    import aiweb_language_core_bootstrap.rmc_echo_runtime.governed_lifecycle as governance

    ledger = Ledger()
    aggregate = _fixture(core, governance)
    version = _version_custody(governance, aggregate)
    lifecycle_records, transitions = _lifecycle(
        governance,
        aggregate,
        version,
    )
    bundle = _bundle(
        governance,
        aggregate,
        version,
        lifecycle_records,
        transitions,
    )

    ledger.check(repository.is_dir(), "repository exists")
    ledger.check(
        governance.SLICE43B_ACCEPTED_PARENT_HEAD
        == "32719319e3df8dcde42f3ececcb14863d2c541b8",
        "accepted parent head",
    )
    ledger.check(
        governance.SLICE43B_ACCEPTED_PARENT_TREE
        == "d84b9a8e9f612d1ed461bb3785aef52d2acabbef",
        "accepted parent tree",
    )
    ledger.check(
        governance.SLICE43B_ACCEPTED_PARENT_SUBJECT
        == "Slice 43A RMC Echo core schema and authority boundary",
        "accepted parent subject",
    )
    ledger.check(
        governance.SLICE43B_SCHEMA_VERSION
        == "aiweb-slice43b-rmc-echo-governance-v1",
        "governance schema version",
    )
    ledger.check(
        governance.VALIDATION_PROFILE_VERSION
        == "aiweb-slice43b-rmc-echo-validation-profile-v1",
        "validation profile version",
    )
    ledger.check(
        governance.DIGEST_ALGORITHM == "sha256",
        "SHA-256 only",
    )
    ledger.check(
        len(governance.SUPPORTED_RECORD_TYPES) == 16,
        "supported record count",
    )
    ledger.check(
        len(governance.CORE_RECORD_TYPES) == 12,
        "core record count",
    )
    ledger.check(
        len(governance.RMC_ECHO_LIFECYCLE_TRANSITION_RULES) == 41,
        "closed lifecycle rule count",
    )
    ledger.check(
        tuple(core.PreservationDimension)
        == aggregate.validation_input_boundary.required_preservation_dimensions,
        "all preservation dimensions retained",
    )
    ledger.check(
        len(aggregate.preservation_dimension_requirements) == 22,
        "requirement count",
    )
    ledger.check(
        len(aggregate.validation_finding_boundaries) == 22,
        "finding boundary count",
    )
    ledger.check(
        len(aggregate.drift_finding_boundaries) == 22,
        "drift boundary count",
    )

    core_records = (
        aggregate.authorized_meaning_reference,
        aggregate.proposed_expression_reference,
        aggregate.validation_input_boundary,
        *aggregate.preservation_dimension_requirements,
        *aggregate.validation_finding_boundaries,
        *aggregate.drift_finding_boundaries,
        aggregate.echo_disposition_boundary,
        aggregate.rejection_boundary,
        aggregate.containment_boundary,
        aggregate.trace_boundary,
        aggregate.receipt_boundary,
        aggregate,
    )
    for index, record in enumerate(core_records):
        ledger.check(
            governance.validate_record(record).ok,
            f"core record valid {index}",
        )
        ledger.check(
            getattr(record, governance.identity_field(type(record)))
            == governance.expected_record_id(record),
            f"core identity valid {index}",
        )
        ledger.check(
            governance.canonical_record_bytes(record)
            == governance.canonical_record_bytes(record),
            f"core canonical repeat {index}",
        )

    runtime_report = governance.validate_runtime_schema_record(aggregate)
    ledger.check(runtime_report.ok, "valid runtime schema record")
    version_report = governance.validate_version_custody(
        version,
        runtime_schema_record=aggregate,
    )
    ledger.check(version_report.ok, "valid version custody")
    bundle_report = governance.validate_governance_bundle(bundle)
    ledger.check(bundle_report.ok, "valid governance bundle")
    ledger.check(
        governance.assert_valid_runtime_schema_record(aggregate) is aggregate,
        "runtime assertion returns record",
    )
    ledger.check(
        governance.assert_valid_version_custody(
            version,
            runtime_schema_record=aggregate,
        )
        is version,
        "version assertion returns custody",
    )
    ledger.check(
        governance.assert_valid_governance_bundle(bundle) is bundle,
        "bundle assertion returns bundle",
    )

    first_bytes = governance.canonical_record_bytes(aggregate)
    second_bytes = governance.canonical_record_bytes(aggregate)
    ledger.check(first_bytes == second_bytes, "canonical repeat")
    ledger.check(
        governance.deterministic_record_digest(aggregate)
        == governance.deterministic_record_digest(aggregate),
        "digest repeat",
    )
    ledger.check(
        aggregate.rmc_echo_runtime_schema_record_id
        == governance.expected_runtime_schema_record_id(aggregate),
        "aggregate deterministic identity",
    )
    ledger.check(
        version.custody_id
        == governance.expected_version_custody_id(version),
        "version deterministic identity",
    )
    ledger.check(
        bundle.bundle_digest == governance.expected_bundle_digest(bundle),
        "bundle deterministic digest",
    )
    ledger.check(
        bundle.bundle_id == governance.expected_bundle_id(bundle),
        "bundle deterministic identity",
    )
    ledger.check(
        governance.canonical_json_bytes({"b": 2, "a": 1})
        == b'{"a":1,"b":2}',
        "mapping keys sorted",
    )

    for record_type in governance.SUPPORTED_RECORD_TYPES:
        ledger.check(
            tuple(item.name for item in fields(record_type))
            == governance.canonical_field_order(record_type),
            f"{record_type.__name__} canonical order",
        )
        params = record_type.__dataclass_params__
        ledger.check(params.frozen is True, f"{record_type.__name__} frozen")
        ledger.check(
            hasattr(record_type, "__slots__"),
            f"{record_type.__name__} slotted",
        )

    for source, target, transition in zip(
        lifecycle_records,
        lifecycle_records[1:],
        transitions,
    ):
        decision = governance.evaluate_lifecycle_transition(
            source,
            target,
            transition,
        )
        ledger.check(decision.allowed, f"allowed {source.stage.value}")
        ledger.check(
            governance.assert_lifecycle_transition(
                source,
                target,
                transition,
            )
            is transition,
            f"asserted {transition.transition_kind.value}",
        )
        ledger.check(
            source.lifecycle_record_id
            in target.predecessor_lifecycle_record_ids,
            f"immutable predecessor {target.stage.value}",
        )

    try:
        aggregate.validation_performed = True
    except (dataclasses.FrozenInstanceError, AttributeError):
        ledger.check(True, "core record immutable")
    else:
        ledger.check(False, "core record immutable")

    try:
        bundle.delivered = True
    except (dataclasses.FrozenInstanceError, AttributeError):
        ledger.check(True, "governance bundle immutable")
    else:
        ledger.check(False, "governance bundle immutable")

    valid_pairs = tuple(
        (item.name, getattr(aggregate, item.name))
        for item in fields(type(aggregate))
    )
    ledger.check(
        governance.validate_field_pairs(
            type(aggregate),
            valid_pairs,
        ).ok,
        "valid field pairs",
    )
    duplicate_pairs = valid_pairs + (valid_pairs[-1],)
    ledger.malformed(
        any(
            issue.code is governance.RmcEchoValidationCode.DUPLICATE_FIELD
            for issue in governance.validate_field_pairs(
                type(aggregate),
                duplicate_pairs,
            ).issues
        ),
        "duplicate field rejected",
    )
    ledger.malformed(
        any(
            issue.code is governance.RmcEchoValidationCode.MISSING_FIELD
            for issue in governance.validate_field_pairs(
                type(aggregate),
                valid_pairs[:-1],
            ).issues
        ),
        "missing field rejected",
    )
    ledger.malformed(
        any(
            issue.code is governance.RmcEchoValidationCode.UNKNOWN_FIELD
            for issue in governance.validate_field_pairs(
                type(aggregate),
                valid_pairs + (("unknown_field", False),),
            ).issues
        ),
        "unknown field rejected",
    )
    ledger.malformed(
        any(
            issue.code is governance.RmcEchoValidationCode.FIELD_ORDER_MISMATCH
            for issue in governance.validate_field_pairs(
                type(aggregate),
                tuple(reversed(valid_pairs)),
            ).issues
        ),
        "field order rejected",
    )

    bad_sha = replace(
        aggregate.proposed_expression_reference,
        realized_text_sha256="not-a-sha",
    )
    ledger.malformed(
        not governance.validate_record(bad_sha).ok,
        "malformed SHA rejected",
    )

    bad_identity = replace(
        aggregate.authorized_meaning_reference,
        authorized_meaning_reference_id="fabricated:id",
    )
    ledger.malformed(
        any(
            issue.code is governance.RmcEchoValidationCode.IDENTITY_MISMATCH
            for issue in governance.validate_record(bad_identity).issues
        ),
        "fabricated identity rejected",
    )

    bad_lineage_proposed = governance.with_expected_id(
        replace(
            aggregate.proposed_expression_reference,
            proposed_expression_reference_id="pending:bad_lineage",
            lineage_id="lineage:other",
        )
    )
    bad_lineage_input = governance.with_expected_id(
        replace(
            aggregate.validation_input_boundary,
            validation_input_boundary_id="pending:bad_lineage_input",
            proposed_expression_reference=bad_lineage_proposed,
        )
    )
    bad_lineage_aggregate = governance.with_expected_id(
        replace(
            aggregate,
            rmc_echo_runtime_schema_record_id="pending:bad_lineage_aggregate",
            proposed_expression_reference=bad_lineage_proposed,
            validation_input_boundary=bad_lineage_input,
        )
    )
    ledger.malformed(
        not governance.validate_runtime_schema_record(
            bad_lineage_aggregate
        ).ok,
        "lineage mismatch rejected",
    )

    bad_dimensions_input = governance.with_expected_id(
        replace(
            aggregate.validation_input_boundary,
            validation_input_boundary_id="pending:bad_dimensions",
            required_preservation_dimensions=(
                aggregate.validation_input_boundary.required_preservation_dimensions[:-1]
            ),
        )
    )
    bad_dimensions_aggregate = governance.with_expected_id(
        replace(
            aggregate,
            rmc_echo_runtime_schema_record_id="pending:bad_dimensions_aggregate",
            validation_input_boundary=bad_dimensions_input,
        )
    )
    ledger.malformed(
        not governance.validate_runtime_schema_record(
            bad_dimensions_aggregate
        ).ok,
        "missing preservation dimension rejected",
    )

    bad_requirement = governance.with_expected_id(
        replace(
            aggregate.preservation_dimension_requirements[0],
            dimension_requirement_id="pending:bad_requirement",
            validation_input_boundary_ref="wrong:input",
        )
    )
    bad_requirements = (
        bad_requirement,
        *aggregate.preservation_dimension_requirements[1:],
    )
    bad_requirement_aggregate = governance.with_expected_id(
        replace(
            aggregate,
            rmc_echo_runtime_schema_record_id="pending:bad_requirement_aggregate",
            preservation_dimension_requirements=bad_requirements,
        )
    )
    ledger.malformed(
        not governance.validate_runtime_schema_record(
            bad_requirement_aggregate
        ).ok,
        "wrong requirement predecessor rejected",
    )

    bad_version = governance.with_expected_id(
        replace(
            version,
            custody_id="pending:bad_version",
            runtime_schema_version="unknown:schema",
        )
    )
    ledger.malformed(
        any(
            issue.code is governance.RmcEchoValidationCode.UNKNOWN_VERSION
            for issue in governance.validate_version_custody(
                bad_version,
                runtime_schema_record=aggregate,
            ).issues
        ),
        "unknown version rejected",
    )

    bad_predecessors = governance.with_expected_id(
        replace(
            version,
            custody_id="pending:bad_predecessors",
            predecessor_references=version.predecessor_references[:-1],
        )
    )
    ledger.malformed(
        any(
            issue.code
            is governance.RmcEchoValidationCode.PREDECESSOR_REFERENCE_MISMATCH
            for issue in governance.validate_version_custody(
                bad_predecessors,
                runtime_schema_record=aggregate,
            ).issues
        ),
        "missing predecessor rejected",
    )

    duplicate_report = governance.validate_identity_collection(
        (
            aggregate.authorized_meaning_reference,
            aggregate.authorized_meaning_reference,
        )
    )
    ledger.malformed(
        any(
            issue.code
            is governance.RmcEchoValidationCode.DUPLICATE_RECORD_ID
            for issue in duplicate_report.issues
        ),
        "duplicate record rejected",
    )

    collision_record = replace(
        aggregate.authorized_meaning_reference,
        preserved_alternative_refs=("candidate:collision",),
    )
    collision_report = governance.validate_identity_collection(
        (
            aggregate.authorized_meaning_reference,
            collision_record,
        )
    )
    ledger.malformed(
        any(
            issue.code
            is governance.RmcEchoValidationCode.IDENTITY_COLLISION
            for issue in collision_report.issues
        ),
        "identity collision rejected",
    )

    bad_target = governance.with_expected_id(
        replace(
            lifecycle_records[1],
            lifecycle_record_id="pending:bad_target",
            predecessor_lifecycle_record_ids=(),
        )
    )
    bad_transition = governance.with_expected_id(
        replace(
            transitions[0],
            transition_id="pending:bad_transition",
            target_lifecycle_record_id=bad_target.lifecycle_record_id,
        )
    )
    ledger.malformed(
        not governance.evaluate_lifecycle_transition(
            lifecycle_records[0],
            bad_target,
            bad_transition,
        ).allowed,
        "missing immutable predecessor rejected",
    )

    automatic_transition = governance.with_expected_id(
        replace(
            transitions[0],
            transition_id="pending:automatic",
            automatic_transition=True,
        )
    )
    ledger.malformed(
        not governance.evaluate_lifecycle_transition(
            lifecycle_records[0],
            lifecycle_records[1],
            automatic_transition,
        ).allowed,
        "automatic transition rejected",
    )

    wrong_kind = governance.with_expected_id(
        replace(
            transitions[0],
            transition_id="pending:wrong_kind",
            transition_kind=(
                governance.RmcEchoLifecycleTransitionKind.SEAL_RECORD
            ),
        )
    )
    ledger.malformed(
        not governance.evaluate_lifecycle_transition(
            lifecycle_records[0],
            lifecycle_records[1],
            wrong_kind,
        ).allowed,
        "wrong transition kind rejected",
    )

    authority_bundle = replace(
        bundle,
        delivered=True,
    )
    authority_bundle = governance.with_expected_bundle_identity(
        authority_bundle
    )
    ledger.malformed(
        any(
            issue.code
            is governance.RmcEchoValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            for issue in governance.validate_governance_bundle(
                authority_bundle
            ).issues
        ),
        "delivery authority rejected",
    )

    flags = (
        aggregate.slice42_sources_admitted,
        aggregate.meaning_preservation_comparison_performed,
        aggregate.validation_findings_created,
        aggregate.drift_findings_created,
        aggregate.materiality_decided,
        aggregate.echo_disposition_decided,
        aggregate.rejection_issued,
        aggregate.containment_issued,
        aggregate.expression_repaired,
        aggregate.msm_v1_validation_link_integrated,
        aggregate.bootstrap_integration_enabled,
        aggregate.delivered,
        aggregate.language_model_used,
        aggregate.embedding_used,
        aggregate.vector_used,
        aggregate.rag_used,
        aggregate.semantic_similarity_used,
        aggregate.neural_parser_used,
        aggregate.hidden_classifier_used,
        aggregate.echo_forge_used,
        aggregate.legacy_echo_validator_used,
        aggregate.gp014_superseded,
        bundle.structural_validity_grants_echo_authority,
        bundle.slice42_sources_admitted,
        bundle.meaning_preservation_comparison_performed,
        bundle.echo_disposition_decided,
        bundle.delivered,
        bundle.model_or_similarity_authority_used,
        bundle.gp014_superseded,
    )
    for index, value in enumerate(flags):
        ledger.check(value is False, f"authority-zero flag {index}")

    print("=== AI.WEB SLICE 43B BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"record_types={len(governance.SUPPORTED_RECORD_TYPES)}")
    print(
        "lifecycle_stages="
        f"{len(governance.RmcEchoLifecycleStage)}"
    )
    print(
        "lifecycle_transition_kinds="
        f"{len(governance.RmcEchoLifecycleTransitionKind)}"
    )
    print(
        "lifecycle_transition_rules="
        f"{len(governance.RMC_ECHO_LIFECYCLE_TRANSITION_RULES)}"
    )
    print("canonical_serialization=1")
    print("deterministic_sha256_identities=1")
    print("supported_schema_and_profile_versions=1")
    print("immutable_successor_records=1")
    print("exact_predecessor_references=1")
    print("duplicate_rejection=1")
    print("identity_collision_rejection=1")
    print("malformed_record_rejection=1")
    print("cross_record_consistency_validation=1")
    print("slice42_sources_admitted=0")
    print("meaning_preservation_comparison_performed=0")
    print("drift_classification_or_materiality=0")
    print("echo_disposition_decided=0")
    print("rejection_or_containment_issued=0")
    print("msm_v1_modified_or_integrated=0")
    print("delivery_or_downstream_authority=0")
    print("model_or_similarity_authority=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL:", failure)
    verdict = "PASS" if not ledger.failures else "FAIL"
    print(f"AI.WEB SLICE 43B BEHAVIOR TEST: {verdict}")
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
