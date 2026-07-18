"""Deterministic Slice 39D candidate semantic-content assembly."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from ..governed_lifecycle import with_expected_content_id
from ..schema import CandidateMeaningContent
from ..predecessor_custody import (
    PredecessorCustodyStatus,
    validate_binding_result,
)
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import (
    AttachmentStatus,
    AuthorityConversionGuard,
    ReferenceAnalysisStatus,
    ScopeAttachmentReferenceConstraintResult,
    ScopeResponsibility,
    validate_scope_attachment_reference_constraint_result,
)
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import (
    StructuralConceptCandidateProposalResult,
    validate_proposal_result,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    PredicateRoleFrameCandidateProposalResult,
    validate_result as validate_slice38_result,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.semantic_class_relation_registry import (
    SEMANTIC_CLASS_RELATION_REGISTRY,
)
from .identity import with_expected_assembly_identity, with_expected_id
from .schema import (
    SLICE39D_PROFILE_VERSION,
    CandidateCommunicativePurpose,
    CandidateReferentReference,
    CandidateRequestedActDescription,
    CandidateSemanticContentAssembly,
    CandidateSemanticContentAssemblyResult,
    CandidateSemanticContentPayload,
    CandidateSemanticContentProfileIdentity,
    CandidateSemanticContentStatus,
    CandidateSemanticContentValidationCode,
    CandidateSemanticContentValidationIssue,
    CandidateSemanticDistinction,
    CandidateSemanticRelationReference,
    CommunicativeForceCandidate,
    ReferentCandidateKind,
    SemanticDistinctionKind,
)
from .validation import (
    validate_assembly,
    validate_assembly_result,
    validate_profile,
    validate_semantic_relation_reference,
)


def _profile() -> CandidateSemanticContentProfileIdentity:
    return with_expected_id(
        CandidateSemanticContentProfileIdentity(
            profile_id="pending",
            profile_key="slice39d.exact_candidate_semantic_content",
            profile_version=SLICE39D_PROFILE_VERSION,
            exact_predecessor_custody_required=True,
            exact_candidate_identity_required=True,
            exact_registry_identity_required=True,
            exact_source_span_support_required=True,
            zero_one_many_preservation_required=True,
            communicative_force_plurality_allowed=True,
            semantic_relation_candidate_references_allowed=True,
            role_assignment_allowed=False,
            referent_resolution_allowed=False,
            clarification_question_emission_allowed=False,
            candidate_ranking_allowed=False,
            candidate_selection_allowed=False,
            gate_progression_allowed=False,
            truth_evidence_permission_allowed=False,
            route_action_memory_rendering_delivery_allowed=False,
        )
    )


DEFAULT_CONTENT_PROFILE = _profile()


def _issue(path: str, code: CandidateSemanticContentValidationCode, detail: str) -> CandidateSemanticContentValidationIssue:
    return CandidateSemanticContentValidationIssue(path, code, detail)


def _empty_result(
    status: CandidateSemanticContentStatus,
    reason_code: str,
    *,
    issues: tuple[CandidateSemanticContentValidationIssue, ...] = (),
    source_event_id: str = "unknown:source_event",
    source_sha256: str = "0" * 64,
    lineage_id: str = "unknown:lineage",
) -> CandidateSemanticContentAssemblyResult:
    result = CandidateSemanticContentAssemblyResult(
        result_id="pending",
        status=status,
        reason_code=reason_code,
        assembly=None,
        issues=issues,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        lineage_id=lineage_id,
        communicative_force_candidate_count=0,
        requested_act_description_count=0,
        semantic_relation_reference_count=0,
        referent_reference_count=0,
        distinction_count=0,
        candidate_semantic_content_assembled=False,
        participant_assignments_created=False,
        referents_resolved=False,
        clarification_question_emitted=False,
        candidate_ranked=False,
        candidate_selected=False,
        gate_progression_created=False,
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
        semantic_similarity_used=False,
    )
    return with_expected_id(result)


def make_semantic_relation_candidate_reference(
    *,
    relation_type_key: str,
    source_concept_candidate_ids: tuple[str, ...],
    target_concept_candidate_ids: tuple[str, ...],
    source_record_ids: tuple[str, ...],
    source_span_ids: tuple[str, ...],
) -> CandidateSemanticRelationReference:
    """Build a candidate-only relation-type reference, never a relation fact."""

    matches = tuple(
        item
        for item in SEMANTIC_CLASS_RELATION_REGISTRY.relation_types
        if item.relation_key == relation_type_key
    )
    if len(matches) != 1:
        raise ValueError("exact admitted semantic relation type key required")
    relation_type = matches[0]
    record = CandidateSemanticRelationReference(
        reference_id="pending",
        relation_type_id=relation_type.relation_type_id,
        relation_type_key=relation_type.relation_key,
        relation_type_version=relation_type.version,
        relation_family_id=relation_type.relation_family_id,
        source_concept_candidate_ids=source_concept_candidate_ids,
        target_concept_candidate_ids=target_concept_candidate_ids,
        source_record_ids=source_record_ids,
        source_span_ids=source_span_ids,
        candidate_only=True,
        relation_instance_asserted=False,
        truth_determined=False,
        evidence_validated=False,
    )
    record = with_expected_id(record)
    report = validate_semantic_relation_reference(record)
    if not report.ok:
        raise ValueError("invalid candidate semantic relation reference")
    return record


def _ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


def _force_candidates(action_roots: tuple[str, ...], responsibilities: tuple[ScopeResponsibility, ...]) -> tuple[CommunicativeForceCandidate, ...]:
    candidates: list[CommunicativeForceCandidate] = []
    if ScopeResponsibility.INTERROGATION in responsibilities:
        candidates.append(CommunicativeForceCandidate.QUESTION)
    if "report" in action_roots or ScopeResponsibility.REPORTED_SPEECH in responsibilities:
        candidates.append(CommunicativeForceCandidate.REPORT)
    if (
        "request" in action_roots
        or "inspect" in action_roots
        or ScopeResponsibility.IMPERATIVE_SURFACE_FORM in responsibilities
    ):
        candidates.append(CommunicativeForceCandidate.REQUEST)
    if (
        ScopeResponsibility.COMPLETION_CLAIMS in responsibilities
        and CommunicativeForceCandidate.QUESTION not in candidates
    ):
        candidates.append(CommunicativeForceCandidate.ASSERTION)
    if not candidates:
        candidates.append(CommunicativeForceCandidate.UNRESOLVED)
    canonical_order = tuple(CommunicativeForceCandidate)
    return tuple(item for item in canonical_order if item in candidates)


def _distinction_kind(responsibility: ScopeResponsibility) -> SemanticDistinctionKind | None:
    if responsibility is ScopeResponsibility.CONDITION:
        return SemanticDistinctionKind.CONDITION
    if responsibility in (ScopeResponsibility.NEGATION, ScopeResponsibility.PROHIBITION):
        return SemanticDistinctionKind.NEGATION
    if responsibility is ScopeResponsibility.TEMPORAL_STATUS:
        return SemanticDistinctionKind.TEMPORAL
    if responsibility in (
        ScopeResponsibility.OPERATIONAL_STATUS,
        ScopeResponsibility.HYPOTHETICAL_STATUS,
        ScopeResponsibility.COMPLETION_CLAIMS,
    ):
        return SemanticDistinctionKind.STATUS
    if responsibility in (
        ScopeResponsibility.MODALITY,
        ScopeResponsibility.EVIDENCE_STRENGTH,
        ScopeResponsibility.CLAIM_FORCE,
        ScopeResponsibility.QUANTIFICATION,
        ScopeResponsibility.EXCEPTION,
        ScopeResponsibility.EXCLUSION,
        ScopeResponsibility.PRIVACY,
        ScopeResponsibility.DISCLOSURE_LIMITATION,
        ScopeResponsibility.QUOTATION,
        ScopeResponsibility.REPORTED_SPEECH,
        ScopeResponsibility.PROPOSAL,
    ):
        return SemanticDistinctionKind.QUALIFICATION
    return None


def _make_distinction(
    kind: SemanticDistinctionKind,
    code: str,
    source_record_ids: tuple[str, ...],
    source_span_ids: tuple[str, ...] = (),
    exact_source_fragments: tuple[str, ...] = (),
) -> CandidateSemanticDistinction:
    return with_expected_id(
        CandidateSemanticDistinction(
            distinction_id="pending",
            kind=kind,
            distinction_code=code,
            source_record_ids=source_record_ids,
            source_span_ids=source_span_ids,
            exact_source_fragments=exact_source_fragments,
            candidate_only=True,
            selected=False,
            outcome_created=False,
        )
    )


def _referent_kind(exact_reference_form: str, context_object_id: str | None) -> ReferentCandidateKind:
    lowered = exact_reference_form.casefold()
    if "source" in lowered:
        return ReferentCandidateKind.SOURCE
    if "comparison" in lowered or "target" in lowered:
        return ReferentCandidateKind.COMPARISON_TARGET
    if context_object_id is not None:
        return ReferentCandidateKind.OTHER_CONTEXT_OBJECT
    return ReferentCandidateKind.UNRESOLVED


def assemble_candidate_semantic_content(
    predecessor_binding: object,
    constraints: object,
    slice37: object,
    slice38: object,
    *,
    profile: object = DEFAULT_CONTENT_PROFILE,
    semantic_relation_references: object = (),
) -> CandidateSemanticContentAssemblyResult:
    """Assemble one candidate-only semantic payload from exact predecessors."""

    type_issues: list[CandidateSemanticContentValidationIssue] = []
    from ..predecessor_custody.schema import CandidateMeaningPredecessorBindingResult
    exact_types = (
        (predecessor_binding, CandidateMeaningPredecessorBindingResult, "predecessor_binding"),
        (constraints, ScopeAttachmentReferenceConstraintResult, "constraints"),
        (slice37, StructuralConceptCandidateProposalResult, "slice37"),
        (slice38, PredicateRoleFrameCandidateProposalResult, "slice38"),
        (profile, CandidateSemanticContentProfileIdentity, "profile"),
    )
    for value, expected, path in exact_types:
        if type(value) is not expected:
            type_issues.append(_issue(path, CandidateSemanticContentValidationCode.TYPE_MISMATCH, f"exact {expected.__name__} required"))
    if type(semantic_relation_references) is not tuple:
        type_issues.append(_issue("semantic_relation_references", CandidateSemanticContentValidationCode.INVALID_TUPLE, "exact tuple required"))
    if type_issues:
        return _empty_result(CandidateSemanticContentStatus.CONTENT_REJECTED, "type_validation_failed", issues=tuple(type_issues))

    binding_report = validate_binding_result(predecessor_binding)
    constraint_report = validate_scope_attachment_reference_constraint_result(constraints)
    slice37_report = validate_proposal_result(slice37)
    slice38_report = validate_slice38_result(slice38)
    profile_report = validate_profile(profile)
    issues: list[CandidateSemanticContentValidationIssue] = []
    for report, path in (
        (binding_report, "predecessor_binding"),
        (constraint_report, "constraints"),
        (slice37_report, "slice37"),
        (slice38_report, "slice38"),
        (profile_report, "profile"),
    ):
        if not report.ok:
            issues.append(_issue(path, CandidateSemanticContentValidationCode.PREDECESSOR_CUSTODY_INVALID, "accepted predecessor validation failed"))
    if profile != DEFAULT_CONTENT_PROFILE:
        issues.append(_issue("profile", CandidateSemanticContentValidationCode.PROFILE_MISMATCH, "exact canonical Slice 39D profile required"))

    source_event_id = predecessor_binding.source_event_id
    source_sha256 = predecessor_binding.source_sha256
    lineage_id = predecessor_binding.custody.lineage_id if predecessor_binding.custody is not None else "unknown:lineage"

    if predecessor_binding.status is PredecessorCustodyStatus.NO_CANDIDATE_PREDECESSOR:
        return _empty_result(
            CandidateSemanticContentStatus.NO_CANDIDATE_CONTENT,
            "no_candidate_predecessor",
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            lineage_id=lineage_id,
        )
    if predecessor_binding.status is not PredecessorCustodyStatus.BOUND or predecessor_binding.custody is None:
        issues.append(_issue("predecessor_binding.status", CandidateSemanticContentValidationCode.PREDECESSOR_CUSTODY_INVALID, "bound Slice 39C custody required"))
    if constraints.constraint_set is None:
        issues.append(_issue("constraints.constraint_set", CandidateSemanticContentValidationCode.REQUIRED_VALUE_MISSING, "constraint set required"))
    if (
        constraints.source_event_id != source_event_id
        or slice37.source_event_id != source_event_id
        or slice38.source_event_id != source_event_id
    ):
        issues.append(_issue("source_event", CandidateSemanticContentValidationCode.SOURCE_EVENT_MISMATCH, "mixed source events"))
    if predecessor_binding.custody is not None:
        provenance = predecessor_binding.custody.provenance
        if slice37.result_id != provenance.slice37_result_id or slice38.result_id != provenance.slice38_result_id:
            issues.append(_issue("candidate_lineage", CandidateSemanticContentValidationCode.MIXED_CANDIDATE_LINEAGE, "Slice 37/38 results do not match custody"))
    relation_records: tuple[CandidateSemanticRelationReference, ...] = semantic_relation_references
    for index, item in enumerate(relation_records):
        report = validate_semantic_relation_reference(item)
        if not report.ok:
            issues.append(_issue(f"semantic_relation_references[{index}]", CandidateSemanticContentValidationCode.SEMANTIC_RELATION_REFERENCE_FABRICATED, "relation reference validation failed"))
    if issues:
        return _empty_result(
            CandidateSemanticContentStatus.CONTENT_REJECTED,
            "predecessor_or_lineage_validation_failed",
            issues=tuple(issues),
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            lineage_id=lineage_id,
        )

    custody = predecessor_binding.custody
    assert custody is not None and constraints.constraint_set is not None
    provenance = custody.provenance
    source_span_set = set(provenance.source_span_ids)
    concept_candidate_ids = set(provenance.concept_candidate_proposal_ids)

    relation_type_map = {
        item.relation_type_id: item
        for item in SEMANTIC_CLASS_RELATION_REGISTRY.relation_types
    }
    relation_issues: list[CandidateSemanticContentValidationIssue] = []
    for index, item in enumerate(relation_records):
        admitted = relation_type_map.get(item.relation_type_id)
        if (
            admitted is None
            or admitted.relation_key != item.relation_type_key
            or admitted.version != item.relation_type_version
            or admitted.relation_family_id != item.relation_family_id
        ):
            relation_issues.append(_issue(f"semantic_relation_references[{index}]", CandidateSemanticContentValidationCode.SEMANTIC_RELATION_REFERENCE_FABRICATED, "exact admitted relation type identity required"))
        if not set(item.source_concept_candidate_ids).issubset(concept_candidate_ids) or not set(item.target_concept_candidate_ids).issubset(concept_candidate_ids):
            relation_issues.append(_issue(f"semantic_relation_references[{index}]", CandidateSemanticContentValidationCode.CONCEPT_REFERENCE_FABRICATED, "relation endpoints must be exact concept candidates"))
        if not set(item.source_span_ids).issubset(source_span_set):
            relation_issues.append(_issue(f"semantic_relation_references[{index}].source_span_ids", CandidateSemanticContentValidationCode.SOURCE_SPAN_MISMATCH, "relation source spans must be in custody"))
    if relation_issues:
        return _empty_result(
            CandidateSemanticContentStatus.CONTENT_REJECTED,
            "semantic_relation_reference_rejected",
            issues=tuple(relation_issues),
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            lineage_id=lineage_id,
        )

    occurrences = tuple(
        occurrence
        for trail in constraints.constraint_set.constrained_trails
        for occurrence in trail.scope_occurrences
    )
    analyses = tuple(
        analysis
        for trail in constraints.constraint_set.constrained_trails
        for analysis in trail.reference_analyses
    )
    responsibilities = tuple(item.responsibility for item in occurrences)
    action_roots = tuple(item.action_root_key for item in slice38.action_predicate_candidates)
    force_candidates = _force_candidates(action_roots, responsibilities)
    purpose_span_ids = _ordered_unique(
        span_id for occurrence in occurrences for span_id in occurrence.exact_source_span_ids
    ) or (provenance.root_source_span_id,)
    purpose = with_expected_id(
        CandidateCommunicativePurpose(
            purpose_id="pending",
            purpose_keys=_ordered_unique((*action_roots, *(f"scope.{item.value}" for item in responsibilities))) or ("unresolved",),
            force_candidates=force_candidates,
            source_action_predicate_candidate_ids=provenance.action_predicate_candidate_ids,
            source_scope_occurrence_ids=tuple(item.occurrence_id for item in occurrences),
            source_span_ids=purpose_span_ids,
            candidate_only=True,
            force_selected=False,
            gate_disposition_created=False,
        )
    )

    concept_by_id = {item.proposal_id: item for item in slice37.concept_candidates}
    role_by_id = {item.candidate_id: item for item in slice38.role_layout_candidates}
    requested_acts: list[CandidateRequestedActDescription] = []
    for action in slice38.action_predicate_candidates:
        linked_roles = tuple(role_by_id[item] for item in action.role_layout_candidate_ids if item in role_by_id)
        span_ids = _ordered_unique(
            span_id
            for candidate_id in action.source_concept_candidate_proposal_ids
            for span_id in getattr(concept_by_id.get(candidate_id), "source_span_ids", ())
        ) or (provenance.root_source_span_id,)
        effect_pairs = _ordered_unique(
            f"{item.effect_boundary_id}|{item.effect_boundary_version}"
            for item in linked_roles
        )
        requested_acts.append(
            with_expected_id(
                CandidateRequestedActDescription(
                    requested_act_id="pending",
                    action_predicate_candidate_id=action.candidate_id,
                    action_root_id=action.action_root_id,
                    action_root_key=action.action_root_key,
                    action_root_version=action.action_root_version,
                    predicate_id=action.predicate_id,
                    predicate_key=action.predicate_key,
                    predicate_version=action.predicate_version,
                    frame_ids_and_versions=action.frame_ids_and_versions,
                    role_layout_candidate_ids=action.role_layout_candidate_ids,
                    effect_boundary_ids_and_versions=tuple(tuple(value.split("|", 1)) for value in effect_pairs),
                    capability_reference_candidate_ids=action.capability_reference_candidate_ids,
                    source_concept_candidate_ids=action.source_concept_candidate_proposal_ids,
                    source_sense_candidate_ids=action.source_sense_candidate_proposal_ids,
                    source_span_ids=span_ids,
                    candidate_only=True,
                    permission_granted=False,
                    route_created=False,
                    invocation_proposed=False,
                    execution_performed=False,
                )
            )
        )

    referents: list[CandidateReferentReference] = []
    for analysis in analyses:
        if analysis.candidates:
            for candidate in analysis.candidates:
                referents.append(
                    with_expected_id(
                        CandidateReferentReference(
                            referent_id="pending",
                            kind=_referent_kind(analysis.exact_reference_form, candidate.context_object_id),
                            reference_analysis_id=analysis.analysis_id,
                            reference_candidate_id=candidate.reference_candidate_id,
                            context_object_id=candidate.context_object_id,
                            exact_reference_form=analysis.exact_reference_form,
                            source_span_ids=analysis.source_span_ids,
                            candidate_only=True,
                            referent_resolved=False,
                            selected=False,
                        )
                    )
                )
        else:
            referents.append(
                with_expected_id(
                    CandidateReferentReference(
                        referent_id="pending",
                        kind=ReferentCandidateKind.UNRESOLVED,
                        reference_analysis_id=analysis.analysis_id,
                        reference_candidate_id=None,
                        context_object_id=None,
                        exact_reference_form=analysis.exact_reference_form or "unresolved_reference",
                        source_span_ids=analysis.source_span_ids or (provenance.root_source_span_id,),
                        candidate_only=True,
                        referent_resolved=False,
                        selected=False,
                    )
                )
            )

    distinctions: list[CandidateSemanticDistinction] = []
    for occurrence in occurrences:
        distinctions.append(_make_distinction(
            SemanticDistinctionKind.SCOPE,
            f"scope.{occurrence.responsibility.value}",
            (occurrence.occurrence_id,),
            occurrence.exact_source_span_ids,
            occurrence.exact_source_fragments,
        ))
        distinctions.append(_make_distinction(
            SemanticDistinctionKind.ATTACHMENT,
            f"attachment.{occurrence.attachment_status.value}",
            (occurrence.occurrence_id, occurrence.attachment_rule_id),
            occurrence.exact_source_span_ids,
            occurrence.exact_source_fragments,
        ))
        kind = _distinction_kind(occurrence.responsibility)
        if kind is not None:
            distinctions.append(_make_distinction(
                kind,
                f"responsibility.{occurrence.responsibility.value}",
                (occurrence.occurrence_id,),
                occurrence.exact_source_span_ids,
                occurrence.exact_source_fragments,
            ))
        if occurrence.attachment_status in (
            AttachmentStatus.MULTIPLE_ATTACHMENTS,
            AttachmentStatus.UNRESOLVED_ATTACHMENT,
            AttachmentStatus.UNSUPPORTED_ATTACHMENT,
            AttachmentStatus.MALFORMED_ATTACHMENT,
        ):
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.LIMITATION,
                f"attachment_limit.{occurrence.attachment_status.value}",
                (occurrence.occurrence_id,),
                occurrence.exact_source_span_ids,
                occurrence.exact_source_fragments,
            ))
        for guard in occurrence.authority_guard_codes:
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.AUTHORITY_SENSITIVE_IMPLICATION,
                f"authority_guard.{guard.value}",
                (occurrence.occurrence_id,),
                occurrence.exact_source_span_ids,
                occurrence.exact_source_fragments,
            ))

    for analysis in analyses:
        if analysis.missing_context or analysis.unresolved or analysis.status in (
            ReferenceAnalysisStatus.MISSING_CONTEXT_REFERENCE,
            ReferenceAnalysisStatus.UNRESOLVED_REFERENCE,
        ):
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.MISSING_INFORMATION,
                f"reference.{analysis.status.value}",
                (analysis.analysis_id,),
                analysis.source_span_ids,
                (analysis.exact_reference_form,) if analysis.exact_reference_form else (),
            ))
        if analysis.candidate_count > 1:
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.CONFLICTING_INFORMATION,
                "reference.multiple_candidates",
                (analysis.analysis_id,),
                analysis.source_span_ids,
                (analysis.exact_reference_form,) if analysis.exact_reference_form else (),
            ))
        if analysis.unsupported_reference_form or analysis.prohibited_context_dependency:
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.LIMITATION,
                f"reference.{analysis.status.value}",
                (analysis.analysis_id,),
                analysis.source_span_ids,
                (analysis.exact_reference_form,) if analysis.exact_reference_form else (),
            ))

    action_by_id = {item.candidate_id: item for item in slice38.action_predicate_candidates}
    for role in slice38.role_layout_candidates:
        linked_action_ids = tuple(
            item.candidate_id
            for item in slice38.action_predicate_candidates
            if role.candidate_id in item.role_layout_candidate_ids
        )
        source_spans = _ordered_unique(
            span_id
            for action_id in linked_action_ids
            for concept_id in action_by_id[action_id].source_concept_candidate_proposal_ids
            for span_id in getattr(concept_by_id.get(concept_id), "source_span_ids", ())
        ) or (provenance.root_source_span_id,)
        for role_id in role.missing_required_role_ids:
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.MISSING_INFORMATION,
                f"missing_role.{role_id}",
                (role.candidate_id, role_id),
                source_spans,
            ))
        for role_id in role.conflicting_role_ids:
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.CONFLICTING_INFORMATION,
                f"conflicting_role.{role_id}",
                (role.candidate_id, role_id),
                source_spans,
            ))
        if role.structural_state.value != "structurally_complete":
            distinctions.append(_make_distinction(
                SemanticDistinctionKind.LIMITATION,
                f"role_layout_state.{role.structural_state.value}",
                (role.candidate_id,),
                source_spans,
            ))

    for reason in (*slice38.unsupported_reasons, *slice38.unknown_reasons):
        distinctions.append(_make_distinction(
            SemanticDistinctionKind.LIMITATION,
            f"slice38_reason.{reason}",
            (slice38.result_id,),
            (provenance.root_source_span_id,),
        ))
    for candidate_id in slice38.unresolved_alternative_candidate_ids:
        distinctions.append(_make_distinction(
            SemanticDistinctionKind.LIMITATION,
            f"unresolved_alternative.{candidate_id}",
            (slice38.result_id, candidate_id),
            (provenance.root_source_span_id,),
        ))

    distinct_by_id: dict[str, CandidateSemanticDistinction] = {}
    for item in distinctions:
        distinct_by_id.setdefault(item.distinction_id, item)
    distinctions_tuple = tuple(distinct_by_id.values())
    by_kind = {
        kind: tuple(item.distinction_id for item in distinctions_tuple if item.kind is kind)
        for kind in SemanticDistinctionKind
    }

    role_layout_ids = provenance.role_layout_candidate_ids
    frame_candidate_refs = role_layout_ids
    effect_boundary_refs = _ordered_unique(item.effect_boundary_id for item in slice38.role_layout_candidates)
    source_refs = tuple(item.referent_id for item in referents if item.kind is ReferentCandidateKind.SOURCE)
    comparison_refs = tuple(item.referent_id for item in referents if item.kind is ReferentCandidateKind.COMPARISON_TARGET)
    payload = with_expected_id(
        CandidateSemanticContentPayload(
            payload_id="pending",
            lineage_id=custody.lineage_id,
            communicative_purpose_ref=purpose.purpose_id,
            communicative_force_candidates=purpose.force_candidates,
            requested_act_description_refs=tuple(item.requested_act_id for item in requested_acts),
            concept_candidate_refs=provenance.concept_candidate_proposal_ids,
            sense_candidate_refs=provenance.sense_candidate_proposal_ids,
            semantic_relation_candidate_refs=tuple(item.reference_id for item in relation_records),
            action_root_candidate_refs=provenance.action_predicate_candidate_ids,
            predicate_candidate_refs=provenance.action_predicate_candidate_ids,
            frame_candidate_refs=frame_candidate_refs,
            role_layout_candidate_refs=role_layout_ids,
            referent_candidate_refs=tuple(item.referent_id for item in referents),
            source_reference_refs=source_refs,
            comparison_target_reference_refs=comparison_refs,
            condition_refs=by_kind[SemanticDistinctionKind.CONDITION],
            negation_refs=by_kind[SemanticDistinctionKind.NEGATION],
            qualification_refs=by_kind[SemanticDistinctionKind.QUALIFICATION],
            temporal_distinction_refs=by_kind[SemanticDistinctionKind.TEMPORAL],
            status_distinction_refs=by_kind[SemanticDistinctionKind.STATUS],
            scope_refs=by_kind[SemanticDistinctionKind.SCOPE],
            attachment_refs=by_kind[SemanticDistinctionKind.ATTACHMENT],
            limitation_refs=by_kind[SemanticDistinctionKind.LIMITATION],
            missing_information_refs=by_kind[SemanticDistinctionKind.MISSING_INFORMATION],
            conflicting_information_refs=by_kind[SemanticDistinctionKind.CONFLICTING_INFORMATION],
            authority_sensitive_implication_refs=by_kind[SemanticDistinctionKind.AUTHORITY_SENSITIVE_IMPLICATION],
            effect_boundary_refs=effect_boundary_refs,
            capability_family_reference_refs=provenance.capability_reference_candidate_ids,
            candidate_only=True,
            selected_content=False,
            participant_assignments_created=False,
            referents_resolved=False,
            clarification_question_emitted=False,
        )
    )

    modifier_refs = _ordered_unique((
        *payload.condition_refs,
        *payload.negation_refs,
        *payload.qualification_refs,
        *payload.temporal_distinction_refs,
        *payload.status_distinction_refs,
        *payload.scope_refs,
        *payload.attachment_refs,
    ))
    preservation_refs = _ordered_unique(
        f"semantic_preservation.{item.kind.value}"
        for item in distinctions_tuple
        if item.kind in (
            SemanticDistinctionKind.NEGATION,
            SemanticDistinctionKind.CONDITION,
            SemanticDistinctionKind.QUALIFICATION,
            SemanticDistinctionKind.TEMPORAL,
            SemanticDistinctionKind.STATUS,
            SemanticDistinctionKind.MISSING_INFORMATION,
            SemanticDistinctionKind.CONFLICTING_INFORMATION,
            SemanticDistinctionKind.AUTHORITY_SENSITIVE_IMPLICATION,
        )
    ) or ("semantic_preservation.candidate_only",)
    candidate_content = with_expected_content_id(
        CandidateMeaningContent(
            content_id="pending",
            communicative_act_candidate=purpose.purpose_id,
            concept_candidate_refs=payload.concept_candidate_refs,
            sense_candidate_refs=payload.sense_candidate_refs,
            semantic_relation_candidate_refs=payload.semantic_relation_candidate_refs,
            action_root_predicate_candidate_refs=payload.action_root_candidate_refs,
            frame_candidate_refs=payload.frame_candidate_refs,
            role_layout_candidate_refs=payload.role_layout_candidate_refs,
            referent_candidate_refs=payload.referent_candidate_refs,
            capability_reference_candidate_refs=payload.capability_family_reference_refs,
            effect_boundary_refs=payload.effect_boundary_refs,
            meaning_modifiers=modifier_refs,
            limitations=payload.limitation_refs,
            unresolved_referent_refs=tuple(item.referent_id for item in referents if item.kind is ReferentCandidateKind.UNRESOLVED),
            missing_role_refs=payload.missing_information_refs,
            conflicting_role_refs=payload.conflicting_information_refs,
            unsupported_reason_refs=tuple(item.distinction_id for item in distinctions_tuple if item.kind is SemanticDistinctionKind.LIMITATION and item.distinction_code.startswith("slice38_reason.")),
            unknown_reason_refs=tuple(item.distinction_id for item in distinctions_tuple if item.kind is SemanticDistinctionKind.MISSING_INFORMATION),
            authority_sensitive_implications=payload.authority_sensitive_implication_refs,
            preservation_class_refs=preservation_refs,
        )
    )

    assembly = CandidateSemanticContentAssembly(
        assembly_id="pending",
        lineage_id=custody.lineage_id,
        predecessor_custody=custody,
        profile=profile,
        communicative_purpose=purpose,
        requested_act_descriptions=tuple(requested_acts),
        semantic_relation_references=relation_records,
        referent_references=tuple(referents),
        distinctions=distinctions_tuple,
        payload=payload,
        candidate_meaning_content=candidate_content,
        exact_predecessor_custody_verified=True,
        exact_candidate_references_verified=True,
        exact_registry_references_verified=True,
        exact_source_span_support_verified=True,
        zero_one_many_preserved=True,
        candidate_semantic_content_assembled=True,
        participant_assignments_created=False,
        referents_resolved=False,
        clarification_question_emitted=False,
        candidate_ranked=False,
        candidate_selected=False,
        gate_progression_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        route_created=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        canonical_digest="pending",
    )
    assembly = with_expected_assembly_identity(assembly)
    report = validate_assembly(assembly)
    if not report.ok:
        return _empty_result(
            CandidateSemanticContentStatus.CONTENT_REJECTED,
            "assembled_content_validation_failed",
            issues=report.issues,
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            lineage_id=lineage_id,
        )

    result = with_expected_id(
        CandidateSemanticContentAssemblyResult(
            result_id="pending",
            status=CandidateSemanticContentStatus.ASSEMBLED,
            reason_code="candidate_semantic_content_assembled",
            assembly=assembly,
            issues=(),
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            lineage_id=custody.lineage_id,
            communicative_force_candidate_count=len(purpose.force_candidates),
            requested_act_description_count=len(requested_acts),
            semantic_relation_reference_count=len(relation_records),
            referent_reference_count=len(referents),
            distinction_count=len(distinctions_tuple),
            candidate_semantic_content_assembled=True,
            participant_assignments_created=False,
            referents_resolved=False,
            clarification_question_emitted=False,
            candidate_ranked=False,
            candidate_selected=False,
            gate_progression_created=False,
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
            semantic_similarity_used=False,
        )
    )
    final_report = validate_assembly_result(result)
    if not final_report.ok:
        return _empty_result(
            CandidateSemanticContentStatus.CONTENT_REJECTED,
            "result_validation_failed",
            issues=final_report.issues,
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            lineage_id=lineage_id,
        )
    return result


__all__ = (
    "DEFAULT_CONTENT_PROFILE",
    "assemble_candidate_semantic_content",
    "make_semantic_relation_candidate_reference",
)
