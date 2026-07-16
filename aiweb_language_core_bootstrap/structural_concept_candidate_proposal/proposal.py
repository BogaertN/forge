"""Deterministic Slice 36G-to-Slice 37 candidate proposal operation."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from ..controlled_concept_sense_registry.built_in_registry import (
    built_in_registry,
    concept_by_id,
    current_namespace,
)
from ..controlled_concept_sense_registry.semantic_class_relation_registry import (
    semantic_class_relation_registry,
)
from ..controlled_concept_sense_registry.sense_term_mapping_registry import (
    ExactTermLookupState,
    exact_term_lookup,
    lexical_reference_by_id,
    make_exact_lookup_request,
    mapping_by_id,
    sense_by_id,
    sense_term_mapping_registry,
)
from ..deterministic_structural_derivation import (
    DeterministicStructuralDerivationResult,
    StructuralAnalysisCandidate,
    validate_structural_analysis_candidate,
    validate_structural_analysis_candidate_set,
)
from ..input_event_custody import (
    InputEventCaptureResult,
    validate_input_event_capture_result,
)
from ..source_field_projection import (
    SourceFieldProjectionResult,
    validate_source_field_projection_result,
)
from .identity import with_expected_id
from .profile import build_default_structural_concept_proposal_profile
from .schema import (
    SLICE37F_NON_AUTHORITY_BOUNDARIES,
    ConceptCandidateProposal,
    ExactLexicalOccurrenceProposal,
    LexicalOccurrenceDisposition,
    ProposalResultStatus,
    RegistrySnapshotIdentity,
    SenseCandidateProposal,
    StructuralCandidateAncestry,
    StructuralConceptCandidateProposalResult,
    StructuralConceptProposalProfile,
)
from .validation import (
    assert_proposal_profile,
    assert_proposal_result,
    validate_registry_snapshot,
)


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _intersects(
    start: int,
    end: int,
    ranges: tuple[tuple[int, int], ...],
) -> bool:
    return any(start < other_end and other_start < end for other_start, other_end in ranges)


def _ascii_identifier_character(character: str) -> bool:
    return len(character) == 1 and character.isascii() and (
        character.isalnum() or character == "_"
    )


def _boundary_valid(text: str, start: int, end: int, exact_form: str) -> bool:
    if not exact_form:
        return False
    if _ascii_identifier_character(exact_form[0]) and start > 0:
        if _ascii_identifier_character(text[start - 1]):
            return False
    if _ascii_identifier_character(exact_form[-1]) and end < len(text):
        if _ascii_identifier_character(text[end]):
            return False
    return True


def _all_exact_occurrences(text: str, exact_form: str) -> tuple[tuple[int, int], ...]:
    if not exact_form:
        return ()
    matches: list[tuple[int, int]] = []
    start = 0
    while True:
        index = text.find(exact_form, start)
        if index < 0:
            break
        end = index + len(exact_form)
        if _boundary_valid(text, index, end, exact_form):
            matches.append((index, end))
        start = index + 1
    return tuple(matches)


def _registry_snapshot() -> RegistrySnapshotIdentity:
    concept_registry = built_in_registry()
    sense_registry = sense_term_mapping_registry()
    semantic_registry = semantic_class_relation_registry()
    namespace = current_namespace()
    snapshot = with_expected_id(
        RegistrySnapshotIdentity(
            snapshot_id="",
            concept_registry_manifest_id=concept_registry.manifest.manifest_id,
            concept_registry_digest=concept_registry.registry_digest(),
            concept_registry_version=concept_registry.manifest.schema_version,
            sense_mapping_manifest_id=sense_registry.manifest.manifest_id,
            sense_mapping_registry_digest=sense_registry.registry_digest(),
            sense_mapping_registry_version=sense_registry.manifest.schema_version,
            semantic_class_relation_manifest_id=semantic_registry.manifest.manifest_id,
            semantic_class_relation_registry_digest=semantic_registry.registry_digest(),
            semantic_class_relation_registry_version=semantic_registry.manifest.schema_version,
            namespace_id=namespace.namespace_id,
            namespace_version=namespace.version,
            concept_count=len(concept_registry.admitted_concepts),
            sense_count=len(sense_registry.senses),
            lexical_reference_count=len(sense_registry.lexical_references),
            mapping_count=len(sense_registry.mappings),
            semantic_class_count=len(semantic_registry.semantic_classes),
            relation_family_count=len(semantic_registry.relation_families),
            relation_type_count=len(semantic_registry.relation_types),
            relation_instance_count=0,
            exact_snapshot=True,
            external_resources_loaded=False,
            runtime_mutation_allowed=False,
        )
    )
    report = validate_registry_snapshot(snapshot)
    if not report.ok:
        raise ValueError(report.issue_codes)
    return snapshot


def _intersecting_ids(start: int, end: int, records: Iterable[object], id_field: str, ranges_field: str) -> tuple[str, ...]:
    values: list[str] = []
    for record in records:
        ranges = getattr(record, ranges_field, ())
        if _intersects(start, end, ranges):
            values.append(getattr(record, id_field))
    return _unique(values)


def _ancestry_for_candidate(
    *,
    occurrence_id: str,
    start: int,
    end: int,
    occurrence_source_span_ids: tuple[str, ...],
    structural_result: DeterministicStructuralDerivationResult,
    root_source_span_id: str,
    candidate: StructuralAnalysisCandidate,
) -> StructuralCandidateAncestry:
    operator_nodes = candidate.operator_graph.nodes
    attachment_candidates = candidate.attachment_candidates
    scope_occurrences = candidate.scope_occurrences
    reference_analyses = candidate.reference_analyses
    reference_candidates = candidate.reference_candidates

    record = StructuralCandidateAncestry(
        ancestry_id="",
        lexical_occurrence_id=occurrence_id,
        structural_result_id=structural_result.result_id,
        structural_set_id=candidate.structural_set_id,
        structural_candidate_id=candidate.structural_candidate_id,
        source_event_id=candidate.source_event_id,
        source_sha256=candidate.source_sha256,
        root_source_span_id=root_source_span_id,
        projection_id=candidate.projection_id,
        constrained_trail_id=candidate.constrained_trail_id,
        phase_trail_id=candidate.phase_trail_id,
        operator_graph_id=candidate.operator_graph.graph_id,
        source_coverage_proof_id=candidate.source_coverage.coverage_proof_id,
        participating_binding_ids=candidate.participating_binding_ids,
        operator_node_ids=tuple(item.node_id for item in operator_nodes),
        operator_definition_ids=_unique(
            item.candidate_operator_definition_id for item in operator_nodes
        ),
        operator_keys_and_versions=tuple(
            dict.fromkeys(
                (item.candidate_operator_key, item.candidate_operator_version)
                for item in operator_nodes
            )
        ),
        scope_occurrence_ids=tuple(item.occurrence_id for item in scope_occurrences),
        attachment_candidate_ids=tuple(item.governed_span_id for item in attachment_candidates),
        reference_analysis_ids=tuple(item.analysis_id for item in reference_analyses),
        reference_candidate_ids=tuple(item.reference_candidate_id for item in reference_candidates),
        intersecting_operator_node_ids=_intersecting_ids(
            start, end, operator_nodes, "node_id", "code_point_ranges"
        ),
        intersecting_scope_occurrence_ids=_intersecting_ids(
            start, end, scope_occurrences, "occurrence_id", "exact_code_point_ranges"
        ),
        intersecting_attachment_candidate_ids=_intersecting_ids(
            start, end, attachment_candidates, "governed_span_id", "code_point_ranges"
        ),
        intersecting_reference_analysis_ids=tuple(
            item.analysis_id
            for item in reference_analyses
            if set(item.source_span_ids).intersection(occurrence_source_span_ids)
        ),
        unresolved_operator_span_ids=candidate.unresolved_operator_span_ids,
        conflicting_operator_binding_ids=candidate.conflicting_operator_binding_ids,
        attachment_alternative_ids=candidate.attachment_alternative_ids,
        reference_alternative_ids=candidate.reference_alternative_ids,
        non_progress_reasons=tuple(item.value for item in candidate.non_progress_reasons),
        exact_ancestry_complete=candidate.exact_ancestry_complete,
        source_reconstruction_proven=candidate.source_reconstruction_proven,
        candidate_only=candidate.candidate_only,
        selected_structure=candidate.selected_structure,
    )
    return with_expected_id(record)


def _empty_result(
    *,
    status: ProposalResultStatus,
    reason_code: str,
    structural_result_id: str,
    structural_set_id: str,
    source_event_id: str,
    source_sha256: str,
    input_event_id: str,
    root_source_span_id: str,
    projection_id: str,
    profile: StructuralConceptProposalProfile,
    snapshot: RegistrySnapshotIdentity,
) -> StructuralConceptCandidateProposalResult:
    return with_expected_id(
        StructuralConceptCandidateProposalResult(
            result_id="",
            status=status,
            reason_code=reason_code,
            structural_result_id=structural_result_id,
            structural_set_id=structural_set_id,
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            input_event_id=input_event_id,
            root_source_span_id=root_source_span_id,
            projection_id=projection_id,
            profile=profile,
            registry_snapshot=snapshot,
            lexical_occurrences=(),
            structural_ancestries=(),
            concept_candidates=(),
            sense_candidates=(),
            structural_non_progress_reasons=(),
            unmatched_exact_source_fragments=(),
            unmatched_source_span_ids=(),
            unmatched_code_point_ranges=(),
            lexical_occurrence_count=0,
            structural_ancestry_count=0,
            concept_candidate_count=0,
            sense_candidate_count=0,
            explicit_unknown_count=1 if status in (ProposalResultStatus.EXPLICIT_UNKNOWN, ProposalResultStatus.EXPLICIT_UNKNOWN_AND_UNSUPPORTED) else 0,
            explicit_unsupported_count=1 if status in (ProposalResultStatus.EXPLICIT_UNSUPPORTED, ProposalResultStatus.EXPLICIT_UNKNOWN_AND_UNSUPPORTED, ProposalResultStatus.PREDECESSOR_REJECTED) else 0,
            unresolved_alternative_count=0,
            zero_one_many_preserved=True,
            structural_plurality_preserved=True,
            source_ancestry_preserved=True,
            operator_ancestry_preserved=True,
            scope_attachment_ancestry_preserved=True,
            exact_registry_lookup_only=True,
            candidate_order_is_ranked=False,
            candidate_meaning_created=False,
            selected_meaning_created=False,
            selected_sense_created=False,
            predicate_identity_created=False,
            participant_roles_assigned=False,
            truth_determined=False,
            evidence_validity_determined=False,
            clarification_asked=False,
            permission_inferred=False,
            capability_route_created=False,
            tool_invoked=False,
            action_performed=False,
            memory_read_performed=False,
            memory_write_performed=False,
            outward_rendered=False,
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


def _predecessor_problem(
    custody: object,
    projection: object,
    structural_result: object,
) -> str | None:
    if not isinstance(custody, InputEventCaptureResult):
        return "invalid_custody_result_type"
    if not isinstance(projection, SourceFieldProjectionResult):
        return "invalid_projection_result_type"
    if not isinstance(structural_result, DeterministicStructuralDerivationResult):
        return "invalid_structural_result_type"
    if not validate_input_event_capture_result(custody).ok:
        return "invalid_custody_result"
    if not validate_source_field_projection_result(projection).ok:
        return "invalid_projection_result"
    if custody.event is None or custody.root_span is None:
        return "custody_event_or_root_span_missing"
    if projection.projection is None:
        return "projection_record_missing"
    if structural_result.result_id != structural_result.expected_id():
        return "structural_result_identity_mismatch"
    if structural_result.structural_set is None:
        return "structural_set_missing"
    if not validate_structural_analysis_candidate_set(structural_result.structural_set).ok:
        return "invalid_structural_candidate_set"
    if any(
        not validate_structural_analysis_candidate(item).ok
        for item in structural_result.structural_set.candidates
    ):
        return "invalid_structural_candidate"
    if (
        structural_result.structural_set.all_source_ancestry_preserved is not True
        or structural_result.structural_set.all_source_reconstruction_proven is not True
        or any(
            item.exact_ancestry_complete is not True
            or item.source_reconstruction_proven is not True
            for item in structural_result.structural_set.candidates
        )
    ):
        return "structural_exact_ancestry_unsupported"
    event = custody.event
    projected = projection.projection
    structural_set = structural_result.structural_set
    identities = (
        event.input_event_id == structural_set.source_event_id,
        event.source_sha256 == structural_set.source_sha256,
        custody.result_id == structural_set.custody_result_id,
        projection.result_id == structural_set.projection_result_id,
        projected.projection_id == structural_set.projection_id,
        structural_result.source_event_id == event.input_event_id,
        structural_result.source_sha256 == event.source_sha256,
        structural_result.projection_id == projected.projection_id,
        projected.source_event_id == event.input_event_id,
        projected.source_sha256 == event.source_sha256,
        event.root_source_span_id == custody.root_span.span_id,
    )
    if not all(identities):
        return "predecessor_ancestry_mismatch"
    reconstructed = "".join(item.exact_text for item in projected.code_points)
    if reconstructed != event.exact_received_text:
        return "projection_source_reconstruction_mismatch"
    return None


def propose_structural_concept_candidates(
    custody: InputEventCaptureResult,
    projection: SourceFieldProjectionResult,
    structural_result: DeterministicStructuralDerivationResult,
    *,
    profile: StructuralConceptProposalProfile | None = None,
) -> StructuralConceptCandidateProposalResult:
    """Propose exact registry candidates while preserving all uncertainty."""

    active_profile = profile or build_default_structural_concept_proposal_profile()
    active_profile = assert_proposal_profile(active_profile)
    snapshot = _registry_snapshot()

    problem = _predecessor_problem(custody, projection, structural_result)
    if problem is not None:
        result = _empty_result(
            status=ProposalResultStatus.PREDECESSOR_REJECTED,
            reason_code=problem,
            structural_result_id=getattr(structural_result, "result_id", ""),
            structural_set_id=(
                getattr(getattr(structural_result, "structural_set", None), "structural_set_id", "")
            ),
            source_event_id=getattr(structural_result, "source_event_id", ""),
            source_sha256=getattr(structural_result, "source_sha256", ""),
            input_event_id=getattr(getattr(custody, "event", None), "input_event_id", ""),
            root_source_span_id=getattr(getattr(custody, "root_span", None), "span_id", ""),
            projection_id=getattr(structural_result, "projection_id", ""),
            profile=active_profile,
            snapshot=snapshot,
        )
        return assert_proposal_result(result)

    assert custody.event is not None
    assert custody.root_span is not None
    assert projection.projection is not None
    assert structural_result.structural_set is not None

    event = custody.event
    projected = projection.projection
    structural_set = structural_result.structural_set
    registry = sense_term_mapping_registry()

    raw_matches: list[tuple[int, int, str]] = []
    for lexical in registry.lexical_references:
        if lexical.namespace_id != active_profile.namespace_id:
            continue
        if lexical.language_tag not in active_profile.language_tags:
            continue
        if lexical.case_sensitive is not True:
            continue
        if any(not character.isascii() for character in lexical.exact_form):
            continue
        for start, end in _all_exact_occurrences(
            event.exact_received_text,
            lexical.exact_form,
        ):
            raw_matches.append((start, end, lexical.lexical_reference_id))

    raw_matches.sort(key=lambda item: (item[0], item[1], item[2]))

    if not raw_matches:
        result = _empty_result(
            status=ProposalResultStatus.EXPLICIT_UNKNOWN,
            reason_code="no_exact_controlled_lexical_occurrence",
            structural_result_id=structural_result.result_id,
            structural_set_id=structural_set.structural_set_id,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            input_event_id=event.input_event_id,
            root_source_span_id=custody.root_span.span_id,
            projection_id=projected.projection_id,
            profile=active_profile,
            snapshot=snapshot,
        )
        result = replace(
            result,
            result_id="",
            structural_non_progress_reasons=tuple(
                item.value for item in structural_set.aggregate_non_progress_reasons
            ),
            unmatched_exact_source_fragments=(event.exact_received_text,),
            unmatched_source_span_ids=tuple(
                item.source_span_id for item in projected.code_points
            ),
            unmatched_code_point_ranges=((0, event.code_point_length),),
        )
        result = with_expected_id(result)
        return assert_proposal_result(result)

    occurrences: list[ExactLexicalOccurrenceProposal] = []
    ancestries: list[StructuralCandidateAncestry] = []
    concept_candidates: list[ConceptCandidateProposal] = []
    sense_candidates: list[SenseCandidateProposal] = []

    for start, end, lexical_id in raw_matches:
        lexical = lexical_reference_by_id(lexical_id)
        request = make_exact_lookup_request(
            exact_form=lexical.exact_form,
            language_tag=lexical.language_tag,
            namespace_id=active_profile.namespace_id,
            namespace_scope=active_profile.namespace_scope,
            domain_scope=active_profile.domain_scope,
        )
        lookup = exact_term_lookup(request)
        mapping_records = tuple(mapping_by_id(item) for item in lookup.mapping_refs)
        mapping_versions = tuple((item.mapping_id, item.version) for item in mapping_records)
        source_span_ids = tuple(
            item.source_span_id
            for item in projected.code_points
            if start <= item.ordinal < end
        )
        utf8_start = event.utf8_boundary_offsets[start]
        utf8_end = event.utf8_boundary_offsets[end]

        provisional_occurrence = ExactLexicalOccurrenceProposal(
            occurrence_id="",
            structural_result_id=structural_result.result_id,
            structural_set_id=structural_set.structural_set_id,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            input_event_id=event.input_event_id,
            root_source_span_id=custody.root_span.span_id,
            projection_id=projected.projection_id,
            exact_source_text=event.exact_received_text[start:end],
            code_point_start=start,
            code_point_end=end,
            utf8_byte_start=utf8_start,
            utf8_byte_end=utf8_end,
            source_span_ids=source_span_ids,
            lexical_reference_id=lexical.lexical_reference_id,
            lexical_reference_version=lexical.version,
            lexical_reference_lifecycle_state=lexical.lifecycle_state.value,
            lexical_reference_provenance_ref=lexical.provenance_ref,
            lexical_reference_kind=lexical.reference_kind.value,
            lexical_language_tag=lexical.language_tag,
            lookup_request_id=request.request_id,
            lookup_result_id=lookup.result_id,
            lookup_state=lookup.state.value,
            lookup_multiplicity=lookup.multiplicity.value,
            mapping_ids_and_versions=mapping_versions,
            concept_candidate_proposal_ids=(),
            sense_candidate_proposal_ids=(),
            structural_ancestry_ids=(),
            disposition=LexicalOccurrenceDisposition.MAPPED,
            unresolved_alternative_ids=(),
            exact_match=lookup.exact_match,
            candidate_order_is_ranked=False,
            selected_concept_id=None,
            selected_sense_id=None,
            explicit_unknown=False,
            explicit_unsupported=False,
            reason=lookup.reason,
            non_authority_boundaries=SLICE37F_NON_AUTHORITY_BOUNDARIES,
        )
        provisional_occurrence = with_expected_id(provisional_occurrence)

        occurrence_ancestries = tuple(
            _ancestry_for_candidate(
                occurrence_id=provisional_occurrence.occurrence_id,
                start=start,
                end=end,
                occurrence_source_span_ids=source_span_ids,
                structural_result=structural_result,
                root_source_span_id=custody.root_span.span_id,
                candidate=candidate,
            )
            for candidate in structural_set.candidates
        )
        ancestry_ids = tuple(item.ancestry_id for item in occurrence_ancestries)

        occurrence_sense_candidates: list[SenseCandidateProposal] = []
        for sense_id in lookup.sense_candidate_refs:
            sense = sense_by_id(sense_id)
            alternative_senses = tuple(
                item for item in lookup.sense_candidate_refs if item != sense_id
            )
            sense_proposal = with_expected_id(
                SenseCandidateProposal(
                    proposal_id="",
                    lexical_occurrence_id=provisional_occurrence.occurrence_id,
                    structural_result_id=structural_result.result_id,
                    structural_ancestry_ids=ancestry_ids,
                    profile_id=active_profile.profile_id,
                    registry_snapshot_id=snapshot.snapshot_id,
                    exact_matched_lexical_reference_id=lexical.lexical_reference_id,
                    exact_matched_lexical_reference_version=lexical.version,
                    mapping_ids_and_versions=mapping_versions,
                    concept_id=sense.concept_id,
                    sense_id=sense.sense_id,
                    sense_key=sense.sense_key,
                    sense_version=sense.version,
                    sense_lifecycle_state=sense.lifecycle_state.value,
                    sense_provenance_ref=sense.provenance_ref,
                    unresolved_alternative_sense_ids=alternative_senses,
                    candidate_only=True,
                    selected=False,
                    selected_sense_created=False,
                    candidate_meaning_created=False,
                    predicate_identity_created=False,
                    participant_roles_assigned=False,
                    truth_determined=False,
                    evidence_validity_determined=False,
                    clarification_asked=False,
                    permission_inferred=False,
                    capability_route_created=False,
                    tool_invoked=False,
                    action_performed=False,
                    memory_accessed=False,
                    outward_rendered=False,
                    delivered=False,
                    non_authority_boundaries=SLICE37F_NON_AUTHORITY_BOUNDARIES,
                )
            )
            occurrence_sense_candidates.append(sense_proposal)

        occurrence_concept_candidates: list[ConceptCandidateProposal] = []
        for concept_id in lookup.concept_candidate_refs:
            concept = concept_by_id(concept_id)
            related_senses = tuple(
                item.proposal_id
                for item in occurrence_sense_candidates
                if item.concept_id == concept_id
            )
            alternatives = tuple(
                item for item in lookup.concept_candidate_refs if item != concept_id
            )
            concept_proposal = with_expected_id(
                ConceptCandidateProposal(
                    proposal_id="",
                    lexical_occurrence_id=provisional_occurrence.occurrence_id,
                    structural_result_id=structural_result.result_id,
                    structural_ancestry_ids=ancestry_ids,
                    profile_id=active_profile.profile_id,
                    registry_snapshot_id=snapshot.snapshot_id,
                    exact_matched_lexical_reference_id=lexical.lexical_reference_id,
                    exact_matched_lexical_reference_version=lexical.version,
                    mapping_ids_and_versions=mapping_versions,
                    concept_id=concept.concept_id,
                    concept_key=concept.concept_key,
                    concept_version=concept.version,
                    concept_lifecycle_state=concept.lifecycle_state.value,
                    concept_provenance_ref=concept.provenance_ref,
                    related_sense_candidate_ids=related_senses,
                    unresolved_alternative_concept_ids=alternatives,
                    candidate_only=True,
                    selected=False,
                    candidate_meaning_created=False,
                    truth_determined=False,
                    evidence_validity_determined=False,
                    permission_inferred=False,
                    capability_route_created=False,
                    tool_invoked=False,
                    action_performed=False,
                    memory_accessed=False,
                    outward_rendered=False,
                    delivered=False,
                    non_authority_boundaries=SLICE37F_NON_AUTHORITY_BOUNDARIES,
                )
            )
            occurrence_concept_candidates.append(concept_proposal)

        if lookup.state is ExactTermLookupState.AMBIGUOUS_MAPPING:
            disposition = LexicalOccurrenceDisposition.AMBIGUOUS
        elif lookup.state is ExactTermLookupState.UNSUPPORTED_MAPPING:
            disposition = LexicalOccurrenceDisposition.UNSUPPORTED
        elif lookup.state is ExactTermLookupState.UNMAPPED_TERM:
            disposition = LexicalOccurrenceDisposition.UNMAPPED
        else:
            disposition = LexicalOccurrenceDisposition.MAPPED

        lookup_alternatives = (
            (*lookup.concept_candidate_refs, *lookup.sense_candidate_refs)
            if (
                len(lookup.concept_candidate_refs) > 1
                or len(lookup.sense_candidate_refs) > 1
            )
            else ()
        )
        unresolved_ids = _unique(
            (
                *lookup_alternatives,
                *tuple(
                    item
                    for ancestry in occurrence_ancestries
                    for item in (
                        *ancestry.unresolved_operator_span_ids,
                        *ancestry.conflicting_operator_binding_ids,
                        *ancestry.attachment_alternative_ids,
                        *ancestry.reference_alternative_ids,
                    )
                ),
            )
        )

        occurrence = replace(
            provisional_occurrence,
            concept_candidate_proposal_ids=tuple(
                item.proposal_id for item in occurrence_concept_candidates
            ),
            sense_candidate_proposal_ids=tuple(
                item.proposal_id for item in occurrence_sense_candidates
            ),
            structural_ancestry_ids=ancestry_ids,
            disposition=disposition,
            unresolved_alternative_ids=unresolved_ids,
            explicit_unknown=disposition is LexicalOccurrenceDisposition.UNMAPPED,
            explicit_unsupported=disposition is LexicalOccurrenceDisposition.UNSUPPORTED,
        )
        occurrence = replace(occurrence, occurrence_id=occurrence.expected_id())

        # Rebind dependent records to the final occurrence identity. The first
        # provisional identity intentionally excluded child refs; this second
        # pass makes the complete immutable graph self-consistent.
        if occurrence.occurrence_id != provisional_occurrence.occurrence_id:
            occurrence_ancestries = tuple(
                with_expected_id(replace(item, lexical_occurrence_id=occurrence.occurrence_id, ancestry_id=""))
                for item in occurrence_ancestries
            )
            ancestry_ids = tuple(item.ancestry_id for item in occurrence_ancestries)
            occurrence_sense_candidates = [
                with_expected_id(
                    replace(
                        item,
                        proposal_id="",
                        lexical_occurrence_id=occurrence.occurrence_id,
                        structural_ancestry_ids=ancestry_ids,
                    )
                )
                for item in occurrence_sense_candidates
            ]
            occurrence_concept_candidates = [
                with_expected_id(
                    replace(
                        item,
                        proposal_id="",
                        lexical_occurrence_id=occurrence.occurrence_id,
                        structural_ancestry_ids=ancestry_ids,
                        related_sense_candidate_ids=tuple(
                            sense_item.proposal_id
                            for sense_item in occurrence_sense_candidates
                            if sense_item.concept_id == item.concept_id
                        ),
                    )
                )
                for item in occurrence_concept_candidates
            ]
            occurrence = replace(
                occurrence,
                occurrence_id="",
                concept_candidate_proposal_ids=tuple(
                    item.proposal_id for item in occurrence_concept_candidates
                ),
                sense_candidate_proposal_ids=tuple(
                    item.proposal_id for item in occurrence_sense_candidates
                ),
                structural_ancestry_ids=ancestry_ids,
            )
            occurrence = with_expected_id(occurrence)

        occurrences.append(occurrence)
        ancestries.extend(occurrence_ancestries)
        concept_candidates.extend(occurrence_concept_candidates)
        sense_candidates.extend(occurrence_sense_candidates)

    unknown_count = sum(item.explicit_unknown for item in occurrences)
    unsupported_count = sum(item.explicit_unsupported for item in occurrences)
    if concept_candidates or sense_candidates:
        status = (
            ProposalResultStatus.CANDIDATES_WITH_UNRESOLVED_STATES
            if unknown_count or unsupported_count or any(
                item.disposition is LexicalOccurrenceDisposition.AMBIGUOUS
                for item in occurrences
            )
            else ProposalResultStatus.CANDIDATES_PROPOSED
        )
        reason_code = "exact_registry_candidates_preserved_without_selection"
    elif unknown_count and unsupported_count:
        status = ProposalResultStatus.EXPLICIT_UNKNOWN_AND_UNSUPPORTED
        reason_code = "exact_unknown_and_unsupported_states_preserved"
    elif unsupported_count:
        status = ProposalResultStatus.EXPLICIT_UNSUPPORTED
        reason_code = "exact_unsupported_state_preserved"
    else:
        status = ProposalResultStatus.EXPLICIT_UNKNOWN
        reason_code = "exact_unknown_or_unmapped_state_preserved"

    result = with_expected_id(
        StructuralConceptCandidateProposalResult(
            result_id="",
            status=status,
            reason_code=reason_code,
            structural_result_id=structural_result.result_id,
            structural_set_id=structural_set.structural_set_id,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            input_event_id=event.input_event_id,
            root_source_span_id=custody.root_span.span_id,
            projection_id=projected.projection_id,
            profile=active_profile,
            registry_snapshot=snapshot,
            lexical_occurrences=tuple(occurrences),
            structural_ancestries=tuple(ancestries),
            concept_candidates=tuple(concept_candidates),
            sense_candidates=tuple(sense_candidates),
            structural_non_progress_reasons=tuple(
                item.value for item in structural_set.aggregate_non_progress_reasons
            ),
            unmatched_exact_source_fragments=(),
            unmatched_source_span_ids=(),
            unmatched_code_point_ranges=(),
            lexical_occurrence_count=len(occurrences),
            structural_ancestry_count=len(ancestries),
            concept_candidate_count=len(concept_candidates),
            sense_candidate_count=len(sense_candidates),
            explicit_unknown_count=unknown_count,
            explicit_unsupported_count=unsupported_count,
            unresolved_alternative_count=sum(
                len(item.unresolved_alternative_ids) for item in occurrences
            ),
            zero_one_many_preserved=True,
            structural_plurality_preserved=(
                structural_set.selected_structural_candidate_id is None
            ),
            source_ancestry_preserved=True,
            operator_ancestry_preserved=True,
            scope_attachment_ancestry_preserved=True,
            exact_registry_lookup_only=True,
            candidate_order_is_ranked=False,
            candidate_meaning_created=False,
            selected_meaning_created=False,
            selected_sense_created=False,
            predicate_identity_created=False,
            participant_roles_assigned=False,
            truth_determined=False,
            evidence_validity_determined=False,
            clarification_asked=False,
            permission_inferred=False,
            capability_route_created=False,
            tool_invoked=False,
            action_performed=False,
            memory_read_performed=False,
            memory_write_performed=False,
            outward_rendered=False,
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
    return assert_proposal_result(result)
