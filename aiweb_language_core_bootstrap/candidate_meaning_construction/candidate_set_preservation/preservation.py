"""Deterministic Slice 39E candidate-set preservation runtime."""

from __future__ import annotations

from collections import Counter
from dataclasses import fields
from itertools import combinations
from typing import Iterable

from ..candidate_semantic_content import (
    CandidateSemanticContentAssemblyResult,
    CandidateSemanticContentStatus,
    validate_assembly_result,
)
from .identity import with_expected_id
from .schema import (
    SLICE39E_PROFILE_VERSION,
    CandidateExactDuplicateGroup,
    CandidateMaterialAlternativeReference,
    CandidateMeaningSet,
    CandidateSetMember,
    CandidateSetPreservationResult,
    CandidateSetProfileIdentity,
    CandidateSetStatus,
    CandidateSetValidationCode,
    CandidateSetValidationIssue,
    CandidateSharedAncestryReference,
)


DEFAULT_SET_PROFILE = with_expected_id(
    CandidateSetProfileIdentity(
        profile_id="pending",
        profile_key="aiweb.slice39e.exact_candidate_set_preservation",
        profile_version=SLICE39E_PROFILE_VERSION,
        zero_one_many_preservation_required=True,
        deterministic_ordering_required=True,
        exact_duplicate_detection_required=True,
        duplicate_occurrence_preservation_required=True,
        material_alternative_references_required=True,
        shared_ancestry_preservation_required=True,
        candidate_specific_boundaries_required=True,
        ranking_allowed=False,
        confidence_scoring_allowed=False,
        preferred_candidate_allowed=False,
        winner_selection_allowed=False,
        nearest_candidate_allowed=False,
        tie_breaking_allowed=False,
        automatic_ambiguity_resolution_allowed=False,
        ambiguous_meaning_state_creation_allowed=False,
        gate_progression_allowed=False,
        truth_evidence_permission_allowed=False,
        route_action_memory_rendering_delivery_allowed=False,
    )
)


def _issue(path: str, code: CandidateSetValidationCode, detail: str) -> CandidateSetValidationIssue:
    return CandidateSetValidationIssue(path=path, code=code, detail=detail)


def _ordered_intersection(values: Iterable[tuple[str, ...]]) -> tuple[str, ...]:
    groups = tuple(values)
    if not groups:
        return ()
    shared = set(groups[0])
    for group in groups[1:]:
        shared.intersection_update(group)
    return tuple(sorted(shared))


def _result_sort_key(result: CandidateSemanticContentAssemblyResult) -> tuple[str, str]:
    assert result.assembly is not None
    return (result.assembly.canonical_digest, result.result_id)


def _difference_dimensions(left: CandidateSemanticContentAssemblyResult, right: CandidateSemanticContentAssemblyResult) -> tuple[str, ...]:
    assert left.assembly is not None and right.assembly is not None
    left_payload = left.assembly.payload
    right_payload = right.assembly.payload
    dimensions: list[str] = []
    ignored = {
        "payload_id", "lineage_id", "candidate_only", "selected_content",
        "participant_assignments_created", "referents_resolved",
        "clarification_question_emitted", "schema_version",
    }
    for item in fields(type(left_payload)):
        if item.name in ignored:
            continue
        if getattr(left_payload, item.name) != getattr(right_payload, item.name):
            dimensions.append(item.name)
    if left.assembly.candidate_meaning_content.content_id != right.assembly.candidate_meaning_content.content_id:
        dimensions.append("candidate_content_id")
    if left.lineage_id != right.lineage_id:
        dimensions.append("lineage_id")
    if left.assembly.canonical_digest != right.assembly.canonical_digest and not dimensions:
        dimensions.append("exact_candidate_record")
    return tuple(dimensions)


def _rejected(issues: tuple[CandidateSetValidationIssue, ...], reason: str = "candidate_set_rejected") -> CandidateSetPreservationResult:
    return with_expected_id(
        CandidateSetPreservationResult(
            result_id="pending",
            status=CandidateSetStatus.SET_REJECTED,
            reason_code=reason,
            candidate_set=None,
            issues=issues,
            source_event_id=None,
            source_sha256=None,
            input_candidate_count=0,
            unique_candidate_count=0,
            exact_duplicate_occurrence_count=0,
            alternative_reference_count=0,
            zero_candidates_preserved=False,
            one_candidate_preserved_without_selection=False,
            multiple_candidates_preserved_independently=False,
            deterministic_ordering_verified=False,
            exact_duplicate_detection_verified=False,
            shared_ancestry_preserved=False,
            candidate_specific_boundaries_preserved=False,
            candidates_ranked=False,
            confidence_scores_created=False,
            preferred_candidate_created=False,
            winner_selected=False,
            nearest_candidate_selected=False,
            tie_breaking_performed=False,
            ambiguity_resolved=False,
            ambiguous_meaning_state_created=False,
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


def preserve_candidate_set(
    candidate_results: object,
    *,
    profile: object = DEFAULT_SET_PROFILE,
) -> CandidateSetPreservationResult:
    """Preserve zero, one, or many exact Slice 39D candidates without evaluation."""

    issues: list[CandidateSetValidationIssue] = []
    if type(candidate_results) is not tuple:
        issues.append(_issue("candidate_results", CandidateSetValidationCode.INVALID_TUPLE, "exact tuple required"))
    if type(profile) is not CandidateSetProfileIdentity:
        issues.append(_issue("profile", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateSetProfileIdentity required"))
    elif profile != DEFAULT_SET_PROFILE:
        issues.append(_issue("profile", CandidateSetValidationCode.PROFILE_MISMATCH, "exact canonical Slice 39E profile required"))
    if issues:
        return _rejected(tuple(issues), "type_or_profile_validation_failed")

    assert type(candidate_results) is tuple
    valid_results: list[CandidateSemanticContentAssemblyResult] = []
    for index, result in enumerate(candidate_results):
        path = f"candidate_results[{index}]"
        if type(result) is not CandidateSemanticContentAssemblyResult:
            issues.append(_issue(path, CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateSemanticContentAssemblyResult required"))
            continue
        report = validate_assembly_result(result)
        if not report.ok:
            issues.append(_issue(path, CandidateSetValidationCode.CANDIDATE_RESULT_INVALID, "Slice 39D validation failed"))
            continue
        if result.status is not CandidateSemanticContentStatus.ASSEMBLED or result.assembly is None:
            issues.append(_issue(path, CandidateSetValidationCode.CANDIDATE_NOT_ASSEMBLED, "assembled Slice 39D candidate required"))
            continue
        valid_results.append(result)
    if issues:
        return _rejected(tuple(issues), "candidate_validation_failed")

    source_event_ids = {item.source_event_id for item in valid_results}
    source_sha256s = {item.source_sha256 for item in valid_results}
    if len(source_event_ids) > 1:
        issues.append(_issue("candidate_results", CandidateSetValidationCode.SOURCE_EVENT_MISMATCH, "one source event required per candidate set"))
    if len(source_sha256s) > 1:
        issues.append(_issue("candidate_results", CandidateSetValidationCode.SOURCE_CHECKSUM_MISMATCH, "one source checksum required per candidate set"))
    if issues:
        return _rejected(tuple(issues), "cross_source_candidate_set_rejected")

    sorted_occurrences = tuple(sorted(valid_results, key=_result_sort_key))
    result_counts = Counter(item.result_id for item in sorted_occurrences)
    unique_by_id = {item.result_id: item for item in sorted_occurrences}
    unique_results = tuple(sorted(unique_by_id.values(), key=_result_sort_key))

    members: list[CandidateSetMember] = []
    primary_member_by_result: dict[str, CandidateSetMember] = {}
    position = 0
    for result in unique_results:
        assert result.assembly is not None
        assembly = result.assembly
        content = assembly.candidate_meaning_content
        count = result_counts[result.result_id]
        for occurrence_index in range(1, count + 1):
            position += 1
            member = with_expected_id(
                CandidateSetMember(
                    member_id="pending",
                    deterministic_position=position,
                    duplicate_occurrence_index=occurrence_index,
                    candidate_result_id=result.result_id,
                    candidate_assembly_id=assembly.assembly_id,
                    candidate_payload_id=assembly.payload.payload_id,
                    candidate_content_id=content.content_id,
                    candidate_canonical_digest=assembly.canonical_digest,
                    lineage_id=result.lineage_id,
                    source_event_id=result.source_event_id,
                    source_sha256=result.source_sha256,
                    source_span_ids=assembly.predecessor_custody.provenance.source_span_ids,
                    limitation_refs=content.limitations,
                    missing_role_refs=content.missing_role_refs,
                    conflicting_role_refs=content.conflicting_role_refs,
                    effect_boundary_refs=content.effect_boundary_refs,
                    capability_reference_refs=content.capability_reference_candidate_refs,
                    candidate_only=True,
                    exact_duplicate_detected=count > 1,
                    ranked=False,
                    confidence_scored=False,
                    preferred=False,
                    selected=False,
                    ambiguous_state_created=False,
                )
            )
            members.append(member)
            primary_member_by_result.setdefault(result.result_id, member)

    duplicate_groups: list[CandidateExactDuplicateGroup] = []
    for result in unique_results:
        count = result_counts[result.result_id]
        if count <= 1:
            continue
        group_members = tuple(item for item in members if item.candidate_result_id == result.result_id)
        duplicate_groups.append(
            with_expected_id(
                CandidateExactDuplicateGroup(
                    duplicate_group_id="pending",
                    candidate_result_id=result.result_id,
                    canonical_candidate_digest=result.assembly.canonical_digest,
                    primary_member_id=group_members[0].member_id,
                    duplicate_member_ids=tuple(item.member_id for item in group_members[1:]),
                    occurrence_count=count,
                    exact_duplicate=True,
                    silently_collapsed=False,
                    ranking_assigned=False,
                    selected_candidate_assigned=False,
                )
            )
        )

    shared_ancestry: tuple[CandidateSharedAncestryReference, ...] = ()
    if unique_results:
        provenances = tuple(item.assembly.predecessor_custody.provenance for item in unique_results)
        shared_record = with_expected_id(
            CandidateSharedAncestryReference(
                shared_ancestry_id="pending",
                member_ids=tuple(item.member_id for item in members),
                source_event_id=unique_results[0].source_event_id,
                source_sha256=unique_results[0].source_sha256,
                lineage_ids=tuple(sorted({item.lineage_id for item in unique_results})),
                shared_source_span_ids=_ordered_intersection(item.source_span_ids for item in provenances),
                shared_structural_ancestry_ids=_ordered_intersection(item.structural_ancestry_ids for item in provenances),
                shared_operator_definition_ids=_ordered_intersection(item.operator_definition_ids for item in provenances),
                shared_concept_candidate_ids=_ordered_intersection(item.concept_candidate_proposal_ids for item in provenances),
                shared_sense_candidate_ids=_ordered_intersection(item.sense_candidate_proposal_ids for item in provenances),
                shared_action_predicate_candidate_ids=_ordered_intersection(item.action_predicate_candidate_ids for item in provenances),
                shared_role_layout_candidate_ids=_ordered_intersection(item.role_layout_candidate_ids for item in provenances),
                shared_predecessor_receipt_ids=_ordered_intersection(item.predecessor_receipt_ids for item in provenances),
                ancestry_preserved=True,
                lineages_merged=False,
            )
        )
        shared_ancestry = (shared_record,)

    alternatives: list[CandidateMaterialAlternativeReference] = []
    if len(unique_results) > 1:
        shared_ref = shared_ancestry[0].shared_ancestry_id
        for left, right in combinations(unique_results, 2):
            left_member = primary_member_by_result[left.result_id]
            right_member = primary_member_by_result[right.result_id]
            dimensions = _difference_dimensions(left, right)
            alternatives.append(
                with_expected_id(
                    CandidateMaterialAlternativeReference(
                        alternative_reference_id="pending",
                        left_member_id=left_member.member_id,
                        right_member_id=right_member.member_id,
                        left_candidate_result_id=left.result_id,
                        right_candidate_result_id=right.result_id,
                        shared_ancestry_ref=shared_ref,
                        exact_difference_dimensions=dimensions,
                        left_limitation_refs=left_member.limitation_refs,
                        right_limitation_refs=right_member.limitation_refs,
                        left_missing_role_refs=left_member.missing_role_refs,
                        right_missing_role_refs=right_member.missing_role_refs,
                        left_conflicting_role_refs=left_member.conflicting_role_refs,
                        right_conflicting_role_refs=right_member.conflicting_role_refs,
                        left_effect_boundary_refs=left_member.effect_boundary_refs,
                        right_effect_boundary_refs=right_member.effect_boundary_refs,
                        left_capability_reference_refs=left_member.capability_reference_refs,
                        right_capability_reference_refs=right_member.capability_reference_refs,
                        exact_duplicate=False,
                        materially_distinct_by_exact_content=bool(dimensions),
                        ambiguity_determined=False,
                        ranked=False,
                        preferred=False,
                        selected=False,
                        tie_broken=False,
                    )
                )
            )

    input_count = len(sorted_occurrences)
    unique_count = len(unique_results)
    duplicate_occurrence_count = input_count - unique_count
    if input_count == 0:
        status = CandidateSetStatus.ZERO_CANDIDATES
        reason = "zero_candidates_preserved_explicitly"
    elif input_count == 1:
        status = CandidateSetStatus.ONE_CANDIDATE
        reason = "one_candidate_preserved_without_selection"
    else:
        status = CandidateSetStatus.MULTIPLE_CANDIDATES
        reason = "multiple_candidates_preserved_independently"

    source_event_id = unique_results[0].source_event_id if unique_results else None
    source_sha256 = unique_results[0].source_sha256 if unique_results else None
    candidate_set = CandidateMeaningSet(
        candidate_set_id="pending",
        status=status,
        profile=profile,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        candidate_results=unique_results,
        members=tuple(members),
        exact_duplicate_groups=tuple(duplicate_groups),
        shared_ancestry_references=shared_ancestry,
        material_alternative_references=tuple(alternatives),
        input_candidate_count=input_count,
        unique_candidate_count=unique_count,
        exact_duplicate_occurrence_count=duplicate_occurrence_count,
        alternative_reference_count=len(alternatives),
        deterministic_ordering_verified=True,
        exact_duplicate_detection_verified=True,
        duplicate_occurrences_preserved=True,
        shared_ancestry_preserved=True,
        candidate_specific_boundaries_preserved=True,
        candidates_ranked=False,
        confidence_scores_created=False,
        preferred_candidate_created=False,
        winner_selected=False,
        nearest_candidate_selected=False,
        tie_breaking_performed=False,
        ambiguity_resolved=False,
        ambiguous_meaning_state_created=False,
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
    candidate_set = with_expected_id(candidate_set)

    result = CandidateSetPreservationResult(
        result_id="pending",
        status=status,
        reason_code=reason,
        candidate_set=candidate_set,
        issues=(),
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        input_candidate_count=input_count,
        unique_candidate_count=unique_count,
        exact_duplicate_occurrence_count=duplicate_occurrence_count,
        alternative_reference_count=len(alternatives),
        zero_candidates_preserved=status is CandidateSetStatus.ZERO_CANDIDATES,
        one_candidate_preserved_without_selection=status is CandidateSetStatus.ONE_CANDIDATE,
        multiple_candidates_preserved_independently=status is CandidateSetStatus.MULTIPLE_CANDIDATES,
        deterministic_ordering_verified=True,
        exact_duplicate_detection_verified=True,
        shared_ancestry_preserved=True,
        candidate_specific_boundaries_preserved=True,
        candidates_ranked=False,
        confidence_scores_created=False,
        preferred_candidate_created=False,
        winner_selected=False,
        nearest_candidate_selected=False,
        tie_breaking_performed=False,
        ambiguity_resolved=False,
        ambiguous_meaning_state_created=False,
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


__all__ = ("DEFAULT_SET_PROFILE", "preserve_candidate_set")
