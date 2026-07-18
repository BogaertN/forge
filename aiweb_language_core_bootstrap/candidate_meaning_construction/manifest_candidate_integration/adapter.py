"""Exact Slice 39F-to-MSM-v1 candidate integration for Slice 39G."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from ...meaning_structure_manifest import (
    CandidateMeaningRecord,
    ExternalAuthorityKind,
    ExternalAuthorityReferenceRecord,
    LineageOriginKind,
    LineageRootRecord,
    MeaningStructureManifestV1,
    SemanticDirection,
    SemanticLifecycleState,
    SemanticPreservationClass,
    SemanticTransitionKind,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.validation import validate_manifest
from ..deterministic_constructor import (
    CandidateMeaningConstructorResult,
    CandidateMeaningConstructorStatus,
    validate_result as validate_constructor_result,
)
from .authority import (
    SLICE39G_COMPANION_VERSION,
    SLICE39G_PROFILE_VERSION,
)
from .canonical import stable_identifier
from .identity import (
    expected_profile_id,
    with_expected_alternative_relationship_id,
    with_expected_companion_id,
    with_expected_limitation_reference_id,
    with_expected_provenance_reference_id,
    with_expected_result_identity,
    with_expected_trace_reference_id,
)
from .schema import (
    CandidateAlternativeRelationshipV1,
    CandidateConstructionTraceReferenceV1,
    CandidateLimitationReferenceV1,
    CandidateMeaningManifestCompanionV1,
    CandidateProvenanceReferenceV1,
    ManifestCandidateIntegrationProfile,
    ManifestCandidateIntegrationResult,
    ManifestCandidateIntegrationStatus,
    ManifestCandidateIntegrationValidationCode,
    ManifestCandidateIntegrationValidationIssue,
)
from .validation import validate_integration_result


_PRESERVATION_CLASS_MAP = {
    "semantic_preservation.negation": SemanticPreservationClass.NEGATION,
    "semantic_preservation.condition": (
        SemanticPreservationClass.MODALITY_AND_CONDITIONAL_SCOPE
    ),
    "semantic_preservation.qualification": (
        SemanticPreservationClass.UNCERTAINTY_AND_CLAIM_STRENGTH
    ),
    "semantic_preservation.temporal": (
        SemanticPreservationClass.TIME_AND_OPERATIONAL_STATUS
    ),
    "semantic_preservation.status": (
        SemanticPreservationClass.TIME_AND_OPERATIONAL_STATUS
    ),
    "semantic_preservation.missing_information": (
        SemanticPreservationClass.UNRESOLVED_AMBIGUITY
    ),
    "semantic_preservation.conflicting_information": (
        SemanticPreservationClass.UNRESOLVED_AMBIGUITY
    ),
    "semantic_preservation.authority_sensitive_implication": (
        SemanticPreservationClass.PERMISSION_VERSUS_REQUEST
    ),
    "semantic_preservation.candidate_only": (
        SemanticPreservationClass.NON_LLM_PROVENANCE
    ),
}


def _default_profile() -> ManifestCandidateIntegrationProfile:
    provisional = ManifestCandidateIntegrationProfile(
        profile_id="pending",
        profile_key="msm_v1_candidate_integration",
        profile_version=SLICE39G_PROFILE_VERSION,
        explicitly_invoked=True,
        exact_slice39f_result_required=True,
        exact_msm_v1_schema_required=True,
        versioned_companion_required=True,
        existing_msm_schema_modification_allowed=False,
        automatic_migration_allowed=False,
        candidate_side_only=True,
        offline_only=True,
        standard_library_only=True,
        read_only=True,
        deterministic=True,
        in_memory_only=True,
        source_preserving=True,
        fail_closed=True,
        gate_outcome_allowed=False,
        selected_meaning_allowed=False,
        governed_result_allowed=False,
        outward_meaning_allowed=False,
        expression_validation_delivery_allowed=False,
        bootstrap_integration_allowed=False,
        slice39_closeout_allowed=False,
        truth_evidence_permission_allowed=False,
        route_action_memory_rendering_delivery_allowed=False,
    )
    return replace(provisional, profile_id=expected_profile_id(provisional))


DEFAULT_MANIFEST_INTEGRATION_PROFILE = _default_profile()


def _issue(
    path: str,
    code: ManifestCandidateIntegrationValidationCode,
    detail: str,
) -> ManifestCandidateIntegrationValidationIssue:
    return ManifestCandidateIntegrationValidationIssue(
        path=path,
        code=code,
        detail=detail,
    )


def _result(
    *,
    status: ManifestCandidateIntegrationStatus,
    reason_code: str,
    profile: ManifestCandidateIntegrationProfile,
    constructor_result_id: str,
    manifest: MeaningStructureManifestV1 | None = None,
    companions: tuple[CandidateMeaningManifestCompanionV1, ...] = (),
    traces: tuple[CandidateConstructionTraceReferenceV1, ...] = (),
    provenance: tuple[CandidateProvenanceReferenceV1, ...] = (),
    limitations: tuple[CandidateLimitationReferenceV1, ...] = (),
    alternatives: tuple[CandidateAlternativeRelationshipV1, ...] = (),
    issues: tuple[ManifestCandidateIntegrationValidationIssue, ...] = (),
    source_event_ids: tuple[str, ...] = (),
    source_sha256s: tuple[str, ...] = (),
    input_candidate_count: int = 0,
) -> ManifestCandidateIntegrationResult:
    integrated = manifest is not None
    record = ManifestCandidateIntegrationResult(
        result_id="pending",
        status=status,
        reason_code=reason_code,
        profile=profile,
        constructor_result_id=constructor_result_id,
        manifest=manifest,
        companions=companions,
        construction_trace_references=traces,
        provenance_references=provenance,
        limitation_references=limitations,
        alternative_relationships=alternatives,
        issues=issues,
        source_event_ids=source_event_ids,
        source_sha256s=source_sha256s,
        input_candidate_count=input_candidate_count,
        manifest_candidate_count=(
            len(manifest.candidate_meanings) if manifest is not None else 0
        ),
        explicitly_invoked=True,
        exact_constructor_result_verified=not issues,
        exact_msm_v1_verified=(
            integrated and validate_manifest(manifest).ok
        ),
        versioned_companion_used=bool(companions),
        lossless_companion_custody=bool(companions),
        candidate_side_only=True,
        manifest_integrated=integrated,
        existing_msm_schema_modified=False,
        automatic_migration_performed=False,
        non_selection_outcome_created=False,
        selected_governed_meaning_created=False,
        governed_result_reference_created=False,
        governed_outward_meaning_created=False,
        expression_link_created=False,
        validation_link_created=False,
        delivery_link_created=False,
        gate_outcome_created=False,
        selected_meaning_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        route_created=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        vector_used=False,
        rag_used=False,
        semantic_similarity_used=False,
        bootstrap_integrated=False,
        slice39_closeout_created=False,
        canonical_digest="pending",
    )
    return with_expected_result_identity(record)


def _rejected(
    issues: tuple[ManifestCandidateIntegrationValidationIssue, ...],
    *,
    constructor_result_id: str = "unavailable",
    input_candidate_count: int = 0,
) -> ManifestCandidateIntegrationResult:
    return _result(
        status=ManifestCandidateIntegrationStatus.REJECTED,
        reason_code="manifest_candidate_integration_rejected",
        profile=DEFAULT_MANIFEST_INTEGRATION_PROFILE,
        constructor_result_id=constructor_result_id,
        issues=issues,
        input_candidate_count=input_candidate_count,
    )


def _preservation_classes(
    preservation_refs: tuple[str, ...],
) -> tuple[SemanticPreservationClass, ...] | None:
    values: list[SemanticPreservationClass] = [
        SemanticPreservationClass.NON_LLM_PROVENANCE
    ]
    for reference in preservation_refs:
        mapped = _PRESERVATION_CLASS_MAP.get(reference)
        if mapped is None:
            return None
        if mapped not in values:
            values.append(mapped)
    return tuple(values)


def _candidate_record_id(state_id: str) -> str:
    return stable_identifier(
        "msm_v1_candidate_meaning_record",
        {"candidate_state_id": state_id, "adapter": "slice39g-v1"},
    )


def _external_authority_reference(
    *,
    lineage_id: str,
    authority_kind: ExternalAuthorityKind,
    external_object_ref: str,
    semantic_relevance: str,
) -> ExternalAuthorityReferenceRecord:
    record_id = stable_identifier(
        "msm_v1_candidate_external_reference",
        {
            "lineage_id": lineage_id,
            "authority_kind": authority_kind.value,
            "external_object_ref": external_object_ref,
            "semantic_relevance": semantic_relevance,
        },
    )
    return ExternalAuthorityReferenceRecord(
        record_id=record_id,
        lineage_id=lineage_id,
        authority_kind=authority_kind,
        external_object_ref=external_object_ref,
        semantic_relevance=semantic_relevance,
    )


def _transition_trace(
    *,
    lineage_id: str,
    candidate_record_id: str,
    trace_reference_id: str,
    authority_reference_id: str,
) -> SemanticTransitionTraceRecord:
    record_id = stable_identifier(
        "msm_v1_candidate_construction_transition",
        {
            "lineage_id": lineage_id,
            "candidate_record_id": candidate_record_id,
            "trace_reference_id": trace_reference_id,
            "authority_reference_id": authority_reference_id,
        },
    )
    return SemanticTransitionTraceRecord(
        record_id=record_id,
        lineage_id=lineage_id,
        from_record_ref=lineage_id,
        to_record_ref=candidate_record_id,
        from_state=SemanticLifecycleState.LINEAGE_ORIGIN,
        to_state=SemanticLifecycleState.CANDIDATE_MEANING,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=f"candidate_construction_trace:{trace_reference_id}",
        authority_reference_ref=authority_reference_id,
    )


def _empty_manifest(
    *,
    lineage_id: str,
    source_event_id: str,
) -> MeaningStructureManifestV1:
    lineage_root = LineageRootRecord(
        lineage_id=lineage_id,
        origin_kind=LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION,
        origin_ref=source_event_id,
        direction=SemanticDirection.INWARD,
    )
    manifest_id = stable_identifier(
        "msm_v1_candidate_manifest",
        {
            "lineage_id": lineage_id,
            "source_event_id": source_event_id,
            "candidate_record_ids": (),
            "external_authority_reference_ids": (),
            "semantic_transition_trace_ids": (),
        },
    )
    return MeaningStructureManifestV1(
        manifest_id=manifest_id,
        lineage_root=lineage_root,
        candidate_meanings=(),
        non_selection_outcomes=(),
        selected_governed_meanings=(),
        governed_result_references=(),
        governed_outward_meanings=(),
        expression_links=(),
        validation_links=(),
        delivery_or_containment_links=(),
        external_authority_references=(),
        semantic_transition_traces=(),
    )


def integrate_candidate_meanings_into_manifest(
    constructor_result: object,
    *,
    profile: object = DEFAULT_MANIFEST_INTEGRATION_PROFILE,
) -> ManifestCandidateIntegrationResult:
    """Adapt one exact Slice 39F result into candidate-only MSM-v1 custody."""

    issues: list[ManifestCandidateIntegrationValidationIssue] = []
    if type(constructor_result) is not CandidateMeaningConstructorResult:
        issues.append(
            _issue(
                "constructor_result",
                ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                "exact CandidateMeaningConstructorResult required",
            )
        )
    if (
        type(profile) is not ManifestCandidateIntegrationProfile
        or profile != DEFAULT_MANIFEST_INTEGRATION_PROFILE
    ):
        issues.append(
            _issue(
                "profile",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "exact canonical Slice 39G profile required",
            )
        )
    if issues:
        return _rejected(tuple(issues))

    assert type(constructor_result) is CandidateMeaningConstructorResult
    assert type(profile) is ManifestCandidateIntegrationProfile

    constructor_report = validate_constructor_result(constructor_result)
    if not constructor_report.ok:
        return _rejected(
            (
                _issue(
                    "constructor_result",
                    ManifestCandidateIntegrationValidationCode.CONSTRUCTOR_RESULT_REJECTED,
                    "Slice 39F result validation failed",
                ),
            ),
            constructor_result_id=constructor_result.result_id,
            input_candidate_count=len(constructor_result.constructed_records),
        )
    if constructor_result.status is CandidateMeaningConstructorStatus.REJECTED:
        return _rejected(
            (
                _issue(
                    "constructor_result.status",
                    ManifestCandidateIntegrationValidationCode.CONSTRUCTOR_RESULT_REJECTED,
                    "rejected Slice 39F result cannot enter MSM-v1 custody",
                ),
            ),
            constructor_result_id=constructor_result.result_id,
            input_candidate_count=len(constructor_result.constructed_records),
        )

    if constructor_result.status is CandidateMeaningConstructorStatus.ZERO_CANDIDATES:
        if not constructor_result.source_event_ids and not constructor_result.source_sha256s:
            result = _result(
                status=ManifestCandidateIntegrationStatus.ZERO_CANDIDATES,
                reason_code="zero_candidates_without_source_lineage_preserved",
                profile=profile,
                constructor_result_id=constructor_result.result_id,
                source_event_ids=(),
                source_sha256s=(),
                input_candidate_count=0,
            )
            return result
        if (
            len(constructor_result.source_event_ids) != 1
            or len(constructor_result.source_sha256s) != 1
        ):
            return _rejected(
                (
                    _issue(
                        "constructor_result.source_event_ids",
                        ManifestCandidateIntegrationValidationCode.SOURCE_LINEAGE_MISMATCH,
                        "typed zero result requires one exact source event and checksum",
                    ),
                ),
                constructor_result_id=constructor_result.result_id,
            )
        source_event_id = constructor_result.source_event_ids[0]
        source_sha256 = constructor_result.source_sha256s[0]
        lineage_id = stable_identifier(
            "msm_v1_zero_candidate_lineage",
            {
                "source_event_id": source_event_id,
                "source_sha256": source_sha256,
            },
        )
        manifest = _empty_manifest(
            lineage_id=lineage_id,
            source_event_id=source_event_id,
        )
        result = _result(
            status=ManifestCandidateIntegrationStatus.ZERO_CANDIDATES,
            reason_code="typed_zero_candidates_integrated",
            profile=profile,
            constructor_result_id=constructor_result.result_id,
            manifest=manifest,
            source_event_ids=(source_event_id,),
            source_sha256s=(source_sha256,),
            input_candidate_count=0,
        )
        report = validate_integration_result(result)
        if not report.ok:
            return _rejected(
                report.issues,
                constructor_result_id=constructor_result.result_id,
            )
        return result

    if constructor_result.status is not CandidateMeaningConstructorStatus.CONSTRUCTED:
        return _rejected(
            (
                _issue(
                    "constructor_result.status",
                    ManifestCandidateIntegrationValidationCode.CONSTRUCTOR_RESULT_REJECTED,
                    "unsupported Slice 39F status",
                ),
            ),
            constructor_result_id=constructor_result.result_id,
        )

    records = constructor_result.constructed_records
    if not records:
        return _rejected(
            (
                _issue(
                    "constructor_result.constructed_records",
                    ManifestCandidateIntegrationValidationCode.COUNT_MISMATCH,
                    "constructed status requires candidate records",
                ),
            ),
            constructor_result_id=constructor_result.result_id,
        )

    candidate_lineage_ids = {
        item.candidate_meaning_state.identity.lineage_id for item in records
    }
    source_event_ids = {
        item.candidate_meaning_state.provenance.source_event_id for item in records
    }
    source_sha256s = {
        item.candidate_meaning_state.provenance.source_sha256 for item in records
    }
    if (
        not candidate_lineage_ids
        or len(source_event_ids) != 1
        or len(source_sha256s) != 1
        or tuple(sorted(source_event_ids)) != constructor_result.source_event_ids
        or tuple(sorted(source_sha256s)) != constructor_result.source_sha256s
    ):
        return _rejected(
            (
                _issue(
                    "constructor_result",
                    ManifestCandidateIntegrationValidationCode.SOURCE_LINEAGE_MISMATCH,
                    "all candidates must share exact source lineage and checksum",
                ),
            ),
            constructor_result_id=constructor_result.result_id,
            input_candidate_count=len(records),
        )

    ordered_records = tuple(
        sorted(records, key=lambda item: item.deterministic_position)
    )
    manifest_record_ids = {
        item.candidate_meaning_state.identity.candidate_meaning_id: (
            _candidate_record_id(item.candidate_meaning_state.state_id)
        )
        for item in ordered_records
    }

    candidate_records: list[CandidateMeaningRecord] = []
    trace_references: list[CandidateConstructionTraceReferenceV1] = []
    provenance_references: list[CandidateProvenanceReferenceV1] = []
    limitation_references: list[CandidateLimitationReferenceV1] = []
    alternative_relationships: list[CandidateAlternativeRelationshipV1] = []
    external_authority_references: list[ExternalAuthorityReferenceRecord] = []
    semantic_transition_traces: list[SemanticTransitionTraceRecord] = []
    alternatives_by_candidate: dict[str, list[str]] = defaultdict(list)

    source_event_id = next(iter(source_event_ids))
    source_sha256 = next(iter(source_sha256s))
    lineage_id = stable_identifier(
        "msm_v1_candidate_lineage",
        {
            "source_event_id": source_event_id,
            "source_sha256": source_sha256,
            "constructor_result_id": constructor_result.result_id,
        },
    )

    for item in ordered_records:
        state = item.candidate_meaning_state
        content = state.content
        preservation_classes = _preservation_classes(
            content.preservation_class_refs
        )
        if preservation_classes is None:
            return _rejected(
                (
                    _issue(
                        "candidate.preservation_class_refs",
                        ManifestCandidateIntegrationValidationCode.UNKNOWN_PRESERVATION_CLASS,
                        "unrecognized preservation class reference",
                    ),
                ),
                constructor_result_id=constructor_result.result_id,
                input_candidate_count=len(records),
            )
        manifest_candidate_record_id = manifest_record_ids[
            state.identity.candidate_meaning_id
        ]
        communicative_act = (
            content.communicative_act_candidate
            if content.communicative_act_candidate is not None
            else "unresolved_candidate_communicative_act"
        )
        candidate_records.append(
            CandidateMeaningRecord(
                record_id=manifest_candidate_record_id,
                lineage_id=lineage_id,
                source_expression_ref=source_event_id,
                communicative_act=communicative_act,
                concept_refs=content.concept_candidate_refs,
                relation_refs=content.semantic_relation_candidate_refs,
                meaning_modifiers=content.meaning_modifiers,
                ambiguity_reasons=(),
                unresolved_referents=content.unresolved_referent_refs,
                authority_sensitive_implications=(
                    content.authority_sensitive_implications
                ),
                preservation_classes=preservation_classes,
            )
        )

        trace_reference = with_expected_trace_reference_id(
            CandidateConstructionTraceReferenceV1(
                trace_reference_id="pending",
                manifest_candidate_record_id=manifest_candidate_record_id,
                candidate_meaning_id=state.identity.candidate_meaning_id,
                candidate_lineage_id=state.identity.lineage_id,
                candidate_state_id=state.state_id,
                constructor_record_id=item.record_id,
                constructor_result_id=constructor_result.result_id,
                construction_receipt_id=item.construction_receipt.receipt_id,
                deterministic_position=item.deterministic_position,
                duplicate_occurrence_count=item.duplicate_occurrence_count,
                exact_typed_predecessors_verified=(
                    item.exact_typed_predecessors_verified
                ),
                exact_ancestry_verified=item.exact_ancestry_verified,
                exact_snapshots_verified=item.exact_snapshots_verified,
                source_preserved=item.source_preserved,
            )
        )
        trace_references.append(trace_reference)

        custody = item.predecessor_custody
        provenance = state.provenance
        provenance_reference = with_expected_provenance_reference_id(
            CandidateProvenanceReferenceV1(
                provenance_reference_id="pending",
                manifest_candidate_record_id=manifest_candidate_record_id,
                candidate_meaning_id=state.identity.candidate_meaning_id,
                candidate_lineage_id=state.identity.lineage_id,
                candidate_provenance_id=provenance.provenance_id,
                predecessor_custody_id=custody.custody_id,
                source_event_id=provenance.source_event_id,
                source_sha256=provenance.source_sha256,
                input_event_id=provenance.input_event_id,
                root_source_span_id=provenance.root_source_span_id,
                slice37_result_id=provenance.slice37_result_id,
                slice37_registry_snapshot_id=(
                    provenance.slice37_registry_snapshot_id
                ),
                slice38_result_id=provenance.slice38_result_id,
                slice38_registry_snapshot_id=(
                    provenance.slice38_registry_snapshot_id
                ),
                compatibility_registry_snapshot_id=(
                    provenance.compatibility_registry_snapshot_id
                ),
                predecessor_result_ids=custody.predecessor_result_ids,
                predecessor_receipt_ids=tuple(
                    receipt.receipt_id for receipt in custody.stage_receipts
                ),
                source_span_reference_ids=tuple(
                    reference.reference_id
                    for reference in custody.source_span_references
                ),
                structural_rule_reference_ids=tuple(
                    reference.reference_id
                    for reference in custody.structural_rule_references
                ),
                operator_reference_ids=tuple(
                    reference.reference_id
                    for reference in custody.operator_references
                ),
                registry_resource_reference_ids=tuple(
                    reference.reference_id
                    for reference in custody.registry_resource_references
                ),
                exact_ancestry_verified=item.exact_ancestry_verified,
                exact_snapshots_verified=item.exact_snapshots_verified,
                source_preserved=item.source_preserved,
            )
        )
        provenance_references.append(provenance_reference)

        limitation_reference = with_expected_limitation_reference_id(
            CandidateLimitationReferenceV1(
                limitation_reference_id="pending",
                manifest_candidate_record_id=manifest_candidate_record_id,
                candidate_meaning_id=state.identity.candidate_meaning_id,
                candidate_lineage_id=state.identity.lineage_id,
                construction_status=state.construction_status,
                status_reason_refs=state.status_reason_refs,
                limitation_refs=state.limitations,
                unresolved_alternative_refs=state.unresolved_alternative_refs,
                unresolved_referent_refs=content.unresolved_referent_refs,
                missing_role_refs=state.missing_role_refs,
                conflicting_role_refs=state.conflicting_role_refs,
                unsupported_reason_refs=content.unsupported_reason_refs,
                unknown_reason_refs=content.unknown_reason_refs,
                authority_sensitive_implication_refs=(
                    content.authority_sensitive_implications
                ),
                candidate_only=True,
                clarification_required_created=False,
                ambiguity_outcome_created=False,
                refusal_created=False,
            )
        )
        limitation_references.append(limitation_reference)

        for alternative in state.alternative_references:
            target_record_id = manifest_record_ids.get(
                alternative.alternative_candidate_meaning_id
            )
            if target_record_id is None:
                return _rejected(
                    (
                        _issue(
                            "candidate.alternative_references",
                            ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                            "alternative candidate is absent from constructor result",
                        ),
                    ),
                    constructor_result_id=constructor_result.result_id,
                    input_candidate_count=len(records),
                )
            relationship = with_expected_alternative_relationship_id(
                CandidateAlternativeRelationshipV1(
                    relationship_id="pending",
                    source_manifest_candidate_record_id=(
                        manifest_candidate_record_id
                    ),
                    alternative_manifest_candidate_record_id=target_record_id,
                    source_candidate_meaning_id=(
                        alternative.source_candidate_meaning_id
                    ),
                    alternative_candidate_meaning_id=(
                        alternative.alternative_candidate_meaning_id
                    ),
                    source_alternative_reference_id=(
                        alternative.alternative_reference_id
                    ),
                    alternative_kind=alternative.alternative_kind,
                    shared_ancestry_refs=alternative.shared_ancestry_refs,
                    differing_content_refs=alternative.differing_content_refs,
                    unresolved_reason_refs=alternative.unresolved_reason_refs,
                    candidate_only=True,
                    ranking_assigned=False,
                    preferred_candidate_assigned=False,
                    selected_alternative=False,
                    ambiguous_gate_disposition_created=False,
                )
            )
            alternative_relationships.append(relationship)
            alternatives_by_candidate[state.identity.candidate_meaning_id].append(
                relationship.relationship_id
            )

        trace_authority = _external_authority_reference(
            lineage_id=lineage_id,
            authority_kind=(
                ExternalAuthorityKind.EXISTING_RMC_MEANING_OR_RENDER_ARTIFACT
            ),
            external_object_ref=trace_reference.trace_reference_id,
            semantic_relevance="candidate_construction_trace",
        )
        provenance_authority = _external_authority_reference(
            lineage_id=lineage_id,
            authority_kind=ExternalAuthorityKind.SOURCE_CUSTODY,
            external_object_ref=provenance_reference.provenance_reference_id,
            semantic_relevance="candidate_provenance",
        )
        limitation_authority = _external_authority_reference(
            lineage_id=lineage_id,
            authority_kind=(
                ExternalAuthorityKind.EXISTING_RMC_MEANING_OR_RENDER_ARTIFACT
            ),
            external_object_ref=limitation_reference.limitation_reference_id,
            semantic_relevance="candidate_limitation",
        )
        external_authority_references.extend(
            (trace_authority, provenance_authority, limitation_authority)
        )
        semantic_transition_traces.append(
            _transition_trace(
                lineage_id=lineage_id,
                candidate_record_id=manifest_candidate_record_id,
                trace_reference_id=trace_reference.trace_reference_id,
                authority_reference_id=trace_authority.record_id,
            )
        )

    for relationship in alternative_relationships:
        external_authority_references.append(
            _external_authority_reference(
                lineage_id=lineage_id,
                authority_kind=(
                    ExternalAuthorityKind.EXISTING_RMC_MEANING_OR_RENDER_ARTIFACT
                ),
                external_object_ref=relationship.relationship_id,
                semantic_relevance="candidate_alternative_relationship",
            )
        )

    trace_by_candidate = {
        item.candidate_meaning_id: item for item in trace_references
    }
    provenance_by_candidate = {
        item.candidate_meaning_id: item for item in provenance_references
    }
    limitation_by_candidate = {
        item.candidate_meaning_id: item for item in limitation_references
    }
    companions: list[CandidateMeaningManifestCompanionV1] = []
    for item in ordered_records:
        state = item.candidate_meaning_state
        candidate_meaning_id = state.identity.candidate_meaning_id
        companion = with_expected_companion_id(
            CandidateMeaningManifestCompanionV1(
                companion_id="pending",
                companion_version=SLICE39G_COMPANION_VERSION,
                manifest_candidate_record_id=manifest_record_ids[
                    candidate_meaning_id
                ],
                candidate_meaning_id=candidate_meaning_id,
                candidate_lineage_id=state.identity.lineage_id,
                candidate_state_id=state.state_id,
                candidate_identity_ref=state.identity.candidate_meaning_id,
                candidate_content_ref=state.content.content_id,
                candidate_provenance_ref=state.provenance.provenance_id,
                construction_receipt_ref=state.construction_receipt.receipt_id,
                construction_trace_reference_id=(
                    trace_by_candidate[candidate_meaning_id].trace_reference_id
                ),
                provenance_reference_id=(
                    provenance_by_candidate[
                        candidate_meaning_id
                    ].provenance_reference_id
                ),
                limitation_reference_id=(
                    limitation_by_candidate[
                        candidate_meaning_id
                    ].limitation_reference_id
                ),
                alternative_relationship_ids=tuple(
                    alternatives_by_candidate[candidate_meaning_id]
                ),
                exact_adapter=True,
                lossless_custody=True,
                candidate_side_only=True,
                selected_meaning_created=False,
                gate_outcome_created=False,
            )
        )
        companions.append(companion)

    candidate_records_tuple = tuple(candidate_records)
    external_authority_tuple = tuple(
        sorted(
            external_authority_references,
            key=lambda item: item.record_id,
        )
    )
    semantic_transition_tuple = tuple(semantic_transition_traces)
    lineage_root = LineageRootRecord(
        lineage_id=lineage_id,
        origin_kind=LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION,
        origin_ref=source_event_id,
        direction=SemanticDirection.INWARD,
    )
    manifest_id = stable_identifier(
        "msm_v1_candidate_manifest",
        {
            "lineage_id": lineage_id,
            "source_event_id": source_event_id,
            "source_sha256": source_sha256,
            "candidate_record_ids": tuple(
                item.record_id for item in candidate_records_tuple
            ),
            "external_authority_reference_ids": tuple(
                item.record_id for item in external_authority_tuple
            ),
            "semantic_transition_trace_ids": tuple(
                item.record_id for item in semantic_transition_tuple
            ),
        },
    )
    manifest = MeaningStructureManifestV1(
        manifest_id=manifest_id,
        lineage_root=lineage_root,
        candidate_meanings=candidate_records_tuple,
        non_selection_outcomes=(),
        selected_governed_meanings=(),
        governed_result_references=(),
        governed_outward_meanings=(),
        expression_links=(),
        validation_links=(),
        delivery_or_containment_links=(),
        external_authority_references=external_authority_tuple,
        semantic_transition_traces=semantic_transition_tuple,
    )

    result = _result(
        status=ManifestCandidateIntegrationStatus.INTEGRATED,
        reason_code="candidate_meanings_integrated_with_versioned_companion",
        profile=profile,
        constructor_result_id=constructor_result.result_id,
        manifest=manifest,
        companions=tuple(companions),
        traces=tuple(trace_references),
        provenance=tuple(provenance_references),
        limitations=tuple(limitation_references),
        alternatives=tuple(alternative_relationships),
        source_event_ids=(source_event_id,),
        source_sha256s=(source_sha256,),
        input_candidate_count=len(records),
    )
    report = validate_integration_result(result)
    if not report.ok:
        return _rejected(
            report.issues,
            constructor_result_id=constructor_result.result_id,
            input_candidate_count=len(records),
        )
    return result


__all__ = (
    "DEFAULT_MANIFEST_INTEGRATION_PROFILE",
    "integrate_candidate_meanings_into_manifest",
)
