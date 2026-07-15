"""Deterministic Slice 36F scope, attachment, and reference constraints.

The input is the accepted Slice 36B projection, Slice 36D binding result, and
Slice 36E candidate trail result. This module creates additive immutable views.
It never mutates a prior trail, selects an attachment, resolves a reference,
creates concept meaning, assigns predicate roles, or grants authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable

from ..candidate_resonant_phase_trail import (
    CandidateResonantPhaseTrail,
    CandidateResonantPhaseTrailResult,
    PhaseTrailConstructionStatus,
    validate_candidate_resonant_phase_trail_result,
)
from ..resonant_operator_candidate_binding import (
    ResonantOperatorBindingCandidate,
    ResonantOperatorCandidateBindingResult,
    UnboundStructuralSignal,
    build_default_resonant_operator_proposal_ruleset,
    validate_resonant_operator_candidate_binding_result,
)
from ..schema import stable_record_id
from ..source_field_projection import (
    SourceFieldProjectionRecord,
    SourceFieldProjectionResult,
    validate_source_field_projection_result,
)
from ..symbolic_grammar_operator_registry import (
    build_default_symbolic_grammar_operator_registry,
    validate_symbolic_grammar_operator_registry,
)
from .rules import (
    authority_conversion_guards,
    build_default_scope_attachment_rules,
    rules_for_candidate,
)
from .schema import (
    ABSOLUTE_MAX_ACTIVE_CONTEXT_ENTRIES,
    ABSOLUTE_MAX_GOVERNED_SPANS_PER_OCCURRENCE,
    ABSOLUTE_MAX_REFERENCE_CANDIDATES,
    ABSOLUTE_MAX_SCOPE_OCCURRENCES,
    ACTIVE_CONTEXT_REGISTRY_SCHEMA_ID,
    CANONICAL_ROADMAP_AUTHORITY_REF,
    CONSTRAINED_TRAIL_SCHEMA_ID,
    CONSTRAINT_RESULT_SCHEMA_ID,
    CONSTRAINT_SET_SCHEMA_ID,
    DEFAULT_MAX_ACTIVE_CONTEXT_ENTRIES,
    DEFAULT_MAX_GOVERNED_SPANS_PER_OCCURRENCE,
    DEFAULT_MAX_REFERENCE_CANDIDATES,
    DEFAULT_MAX_SCOPE_OCCURRENCES,
    GOVERNED_SPAN_SCHEMA_ID,
    REFERENCE_ANALYSIS_SCHEMA_ID,
    REFERENCE_CANDIDATE_SCHEMA_ID,
    RMC_CONCEPT_AUTHORITY_REF,
    RMC_LANGUAGE_LAW_AUTHORITY_REF,
    RMC_PREDICATE_AUTHORITY_REF,
    SCOPE_CONSTRAINT_SCHEMA_VERSION,
    SCOPE_CONSTRAINT_SPEC_ID,
    SCOPE_CONSTRAINT_SPEC_VERSION,
    SCOPE_LIMITS_SCHEMA_ID,
    SCOPE_OCCURRENCE_SCHEMA_ID,
    SCOPE_POLICY_SCHEMA_ID,
    SLICE36D_AUTHORITY_REF,
    SLICE36E_AUTHORITY_REF,
    ActiveContextEntry,
    ActiveContextRegistry,
    AttachmentStatus,
    AttachmentStrategy,
    AuthorityConversionGuard,
    ContextObjectKind,
    ContextOperationalStatus,
    ContextPositionTag,
    GovernedSpanCandidate,
    ReferenceAnalysis,
    ReferenceAnalysisStatus,
    ReferenceContextCandidate,
    ScopeAttachmentOccurrence,
    ScopeAttachmentReferenceConstraintResult,
    ScopeAttachmentReferenceConstraintSet,
    ScopeConstraintLimits,
    ScopeConstraintPolicy,
    ScopeConstraintStatus,
    ScopeConstrainedCandidateTrail,
    ScopeResponsibility,
)


_POLICY_VERSION: Final[str] = "1.0.0"
_DEFAULT_SENTINEL = object()

_SUPPORTED_DEICTIC_FORMS: Final[tuple[str, ...]] = tuple(
    value
    for base in (
        "it",
        "this",
        "that",
        "they",
        "them",
        "these",
        "those",
        "the previous file",
        "the approved version",
        "the first one",
        "the patch above",
        "the quoted document",
    )
    for value in (base, base.capitalize(), base.upper())
)


@dataclass(frozen=True, slots=True)
class _SourceUnit:
    start: int
    end: int
    source_span_ids: tuple[str, ...]
    code_point_ranges: tuple[tuple[int, int], ...]
    utf8_byte_ranges: tuple[tuple[int, int], ...]
    exact_source_fragments: tuple[str, ...]
    binding_ids: tuple[str, ...]
    boundary: bool


def build_default_scope_constraint_policy() -> ScopeConstraintPolicy:
    body = {
        "policy_version": _POLICY_VERSION,
        "explicit_context_only": True,
        "active_context_must_be_immutable": True,
        "exact_reference_match_only": True,
        "preserve_all_lawful_attachments": True,
        "select_attachment_authorized": False,
        "resolve_reference_authorized": False,
        "concept_authority_available": False,
        "predicate_authority_available": False,
        "capability_authority_available": False,
        "route_authority_available": False,
        "tool_authority_available": False,
        "memory_search_authorized": False,
        "file_search_authorized": False,
        "repository_history_search_authorized": False,
        "web_search_authorized": False,
        "embedding_authorized": False,
        "language_model_authorized": False,
        "similarity_authorized": False,
        "nearest_object_selection_authorized": False,
        "convenience_selection_authorized": False,
        "capability_influence_authorized": False,
        "false_authority_conversions": authority_conversion_guards(),
        "source_authority_refs": (
            CANONICAL_ROADMAP_AUTHORITY_REF,
            RMC_LANGUAGE_LAW_AUTHORITY_REF,
            RMC_CONCEPT_AUTHORITY_REF,
            RMC_PREDICATE_AUTHORITY_REF,
            SLICE36D_AUTHORITY_REF,
            SLICE36E_AUTHORITY_REF,
        ),
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "policy_schema_id": SCOPE_POLICY_SCHEMA_ID,
    }
    return ScopeConstraintPolicy(
        policy_id=stable_record_id("scope_constraint_policy", body),
        **body,
    )


def build_scope_constraint_limits(
    *,
    max_scope_occurrences: int = DEFAULT_MAX_SCOPE_OCCURRENCES,
    max_governed_spans_per_occurrence: int = (
        DEFAULT_MAX_GOVERNED_SPANS_PER_OCCURRENCE
    ),
    max_active_context_entries: int = DEFAULT_MAX_ACTIVE_CONTEXT_ENTRIES,
    max_reference_candidates: int = DEFAULT_MAX_REFERENCE_CANDIDATES,
) -> ScopeConstraintLimits:
    body = {
        "max_scope_occurrences": max_scope_occurrences,
        "max_governed_spans_per_occurrence": (
            max_governed_spans_per_occurrence
        ),
        "max_active_context_entries": max_active_context_entries,
        "max_reference_candidates": max_reference_candidates,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "limits_schema_id": SCOPE_LIMITS_SCHEMA_ID,
    }
    return ScopeConstraintLimits(
        limits_id=stable_record_id("scope_constraint_limits", body),
        **body,
    )


def default_scope_constraint_limits() -> ScopeConstraintLimits:
    return build_scope_constraint_limits()


def _policy_issues(policy: object) -> tuple[str, ...]:
    if type(policy) is not ScopeConstraintPolicy:
        return ("invalid_scope_constraint_policy_type",)

    issues = []
    if policy.policy_id != policy.expected_id():
        issues.append("scope_constraint_policy_id_mismatch")

    for field in (
        "explicit_context_only",
        "active_context_must_be_immutable",
        "exact_reference_match_only",
        "preserve_all_lawful_attachments",
    ):
        if getattr(policy, field, None) is not True:
            issues.append(f"scope_constraint_policy_{field}_must_be_true")

    for field in (
        "select_attachment_authorized",
        "resolve_reference_authorized",
        "concept_authority_available",
        "predicate_authority_available",
        "capability_authority_available",
        "route_authority_available",
        "tool_authority_available",
        "memory_search_authorized",
        "file_search_authorized",
        "repository_history_search_authorized",
        "web_search_authorized",
        "embedding_authorized",
        "language_model_authorized",
        "similarity_authorized",
        "nearest_object_selection_authorized",
        "convenience_selection_authorized",
        "capability_influence_authorized",
    ):
        if getattr(policy, field, None) is not False:
            issues.append(f"scope_constraint_policy_{field}_must_be_false")

    if policy.false_authority_conversions != authority_conversion_guards():
        issues.append("scope_constraint_policy_authority_guards_mismatch")

    return tuple(issues)


def _limits_issues(limits: object) -> tuple[str, ...]:
    if type(limits) is not ScopeConstraintLimits:
        return ("invalid_scope_constraint_limits_type",)

    issues = []
    if limits.limits_id != limits.expected_id():
        issues.append("scope_constraint_limits_id_mismatch")

    checks = (
        (
            "max_scope_occurrences",
            limits.max_scope_occurrences,
            ABSOLUTE_MAX_SCOPE_OCCURRENCES,
            True,
        ),
        (
            "max_governed_spans_per_occurrence",
            limits.max_governed_spans_per_occurrence,
            ABSOLUTE_MAX_GOVERNED_SPANS_PER_OCCURRENCE,
            False,
        ),
        (
            "max_active_context_entries",
            limits.max_active_context_entries,
            ABSOLUTE_MAX_ACTIVE_CONTEXT_ENTRIES,
            True,
        ),
        (
            "max_reference_candidates",
            limits.max_reference_candidates,
            ABSOLUTE_MAX_REFERENCE_CANDIDATES,
            True,
        ),
    )

    for name, value, maximum, allow_zero in checks:
        minimum = 0 if allow_zero else 1
        if type(value) is not int or not minimum <= value <= maximum:
            issues.append(f"invalid_{name}")

    return tuple(issues)


def _result(
    *,
    status: ScopeConstraintStatus,
    reason_code: str,
    constraint_set_created: bool,
    source_preserved_in_custody: bool,
    source_event_id: str,
    source_sha256: str,
    projection_id: str,
    binding_set_id: str,
    phase_trail_set_id: str,
    policy: ScopeConstraintPolicy | None,
    limits: ScopeConstraintLimits | None,
    active_context_registry: ActiveContextRegistry | None,
    constraint_set: ScopeAttachmentReferenceConstraintSet | None,
    validation_issue_codes: tuple[str, ...] = (),
) -> ScopeAttachmentReferenceConstraintResult:
    body = {
        "status": status,
        "reason_code": reason_code,
        "constraint_set_created": constraint_set_created,
        "source_preserved_in_custody": source_preserved_in_custody,
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "projection_id": projection_id,
        "binding_set_id": binding_set_id,
        "phase_trail_set_id": phase_trail_set_id,
        "policy": policy,
        "limits": limits,
        "active_context_registry": active_context_registry,
        "constraint_set": constraint_set,
        "validation_issue_codes": validation_issue_codes,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "repository_history_search_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "web_search_performed": False,
        "embedding_performed": False,
        "language_model_used": False,
        "similarity_search_performed": False,
        "selected_trail": False,
        "selected_attachment": False,
        "reference_resolved": False,
        "selected_meaning": False,
        "concept_meaning_created": False,
        "predicate_role_assigned": False,
        "permission_inferred": False,
        "capability_authorized": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "release_authorized": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "result_schema_id": CONSTRAINT_RESULT_SCHEMA_ID,
    }
    return ScopeAttachmentReferenceConstraintResult(
        result_id=stable_record_id(
            "scope_attachment_reference_constraint_result",
            body,
        ),
        **body,
    )


def _unique_text(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


def _unique_ranges(
    values: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    return tuple(dict.fromkeys(values))


def _projection_slice(
    projection: SourceFieldProjectionRecord,
    start: int,
    end: int,
) -> tuple[
    tuple[str, ...],
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
    tuple[str, ...],
]:
    atoms = tuple(
        atom
        for atom in projection.code_points
        if start <= atom.code_point_start and atom.code_point_end <= end
    )
    return (
        _unique_text(atom.source_span_id for atom in atoms),
        tuple((atom.code_point_start, atom.code_point_end) for atom in atoms),
        tuple((atom.utf8_byte_start, atom.utf8_byte_end) for atom in atoms),
        tuple(atom.exact_text for atom in atoms),
    )


def _source_units(
    binding_result: ResonantOperatorCandidateBindingResult,
) -> tuple[_SourceUnit, ...]:
    assert binding_result.binding_set is not None
    units: dict[tuple[int, int, tuple[str, ...]], _SourceUnit] = {}

    for candidate in binding_result.binding_set.candidates:
        start = min(value[0] for value in candidate.code_point_ranges)
        end = max(value[1] for value in candidate.code_point_ranges)
        key = (start, end, candidate.source_span_ids)
        boundary = candidate.candidate_operator_key in {
            "grammar_boundary",
            "fbsc_loop_seal",
        }
        existing = units.get(key)
        binding_ids = _unique_text(
            (
                *(existing.binding_ids if existing else ()),
                candidate.candidate_binding_id,
            )
        )
        units[key] = _SourceUnit(
            start=start,
            end=end,
            source_span_ids=candidate.source_span_ids,
            code_point_ranges=candidate.code_point_ranges,
            utf8_byte_ranges=candidate.utf8_byte_ranges,
            exact_source_fragments=candidate.exact_source_fragments,
            binding_ids=binding_ids,
            boundary=boundary or bool(existing and existing.boundary),
        )

    for signal in binding_result.binding_set.unbound_structural_signals:
        start = min(value[0] for value in signal.code_point_ranges)
        end = max(value[1] for value in signal.code_point_ranges)
        key = (start, end, signal.source_span_ids)
        existing = units.get(key)
        units[key] = _SourceUnit(
            start=start,
            end=end,
            source_span_ids=signal.source_span_ids,
            code_point_ranges=signal.code_point_ranges,
            utf8_byte_ranges=signal.utf8_byte_ranges,
            exact_source_fragments=signal.exact_source_fragments,
            binding_ids=existing.binding_ids if existing else (),
            boundary=bool(existing and existing.boundary),
        )

    return tuple(
        sorted(
            units.values(),
            key=lambda item: (
                item.start,
                item.end,
                item.source_span_ids,
            ),
        )
    )


def _governed_span(
    *,
    projection: SourceFieldProjectionRecord,
    start: int,
    end: int,
    relationship_code: str,
    rule_id: str,
    rule_version: str,
    evidence_codes: tuple[str, ...],
) -> GovernedSpanCandidate:
    (
        source_span_ids,
        code_point_ranges,
        utf8_byte_ranges,
        exact_source_fragments,
    ) = _projection_slice(projection, start, end)

    body = {
        "source_event_id": projection.source_event_id,
        "projection_id": projection.projection_id,
        "source_span_ids": source_span_ids,
        "code_point_ranges": code_point_ranges,
        "utf8_byte_ranges": utf8_byte_ranges,
        "exact_source_fragments": exact_source_fragments,
        "relationship_code": relationship_code,
        "attachment_rule_id": rule_id,
        "attachment_rule_version": rule_version,
        "exact_attachment_evidence_codes": evidence_codes,
        "candidate_only": True,
        "selected": False,
        "concept_meaning_created": False,
        "predicate_role_assigned": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "governed_span_schema_id": GOVERNED_SPAN_SCHEMA_ID,
    }
    return GovernedSpanCandidate(
        governed_span_id=stable_record_id("governed_span_candidate", body),
        **body,
    )


def _candidate_bounds(
    candidate: ResonantOperatorBindingCandidate,
) -> tuple[int, int]:
    return (
        min(value[0] for value in candidate.code_point_ranges),
        max(value[1] for value in candidate.code_point_ranges),
    )


def _terminal_boundary_start(
    units: tuple[_SourceUnit, ...],
    source_length: int,
) -> int:
    boundary_starts = tuple(
        unit.start for unit in units if unit.boundary
    )
    return min(boundary_starts) if boundary_starts else source_length


def _span_candidates_for_rule(
    *,
    projection: SourceFieldProjectionRecord,
    binding_result: ResonantOperatorCandidateBindingResult,
    candidate: ResonantOperatorBindingCandidate,
    rule: object,
    maximum: int,
) -> tuple[GovernedSpanCandidate, ...]:
    units = _source_units(binding_result)
    source_length = projection.source_code_point_length
    candidate_start, candidate_end = _candidate_bounds(candidate)
    strategy = rule.attachment_strategy

    if strategy is AttachmentStrategy.NO_ATTACHMENT_UNTIL_AUTHORIZED_BINDING:
        return ()

    if strategy is AttachmentStrategy.SELF_ONLY:
        return (
            _governed_span(
                projection=projection,
                start=candidate_start,
                end=candidate_end,
                relationship_code="self_attachment_candidate",
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                evidence_codes=(
                    "exact_candidate_source_span",
                    "self_attachment_only",
                ),
            ),
        )

    if strategy is AttachmentStrategy.EXACT_DELIMITED_INTERIOR:
        if len(candidate.code_point_ranges) != 2:
            return ()
        ordered = sorted(candidate.code_point_ranges)
        interior_start = ordered[0][1]
        interior_end = ordered[1][0]
        if interior_end <= interior_start:
            return ()
        return (
            _governed_span(
                projection=projection,
                start=interior_start,
                end=interior_end,
                relationship_code="exact_delimited_interior_candidate",
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                evidence_codes=(
                    "paired_delimiter_coordinates",
                    "exact_interior_code_point_range",
                ),
            ),
        )

    terminal_start = _terminal_boundary_start(units, source_length)

    if strategy is AttachmentStrategy.SOURCE_UNIT_WITHOUT_TERMINAL_BOUNDARY:
        if terminal_start <= 0:
            return ()
        return (
            _governed_span(
                projection=projection,
                start=0,
                end=terminal_start,
                relationship_code="source_unit_without_terminal_boundary",
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                evidence_codes=(
                    "source_event_boundary",
                    "terminal_boundary_excluded",
                ),
            ),
        )

    if (
        strategy
        is AttachmentStrategy.RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY
    ):
        rightward = [
            unit
            for unit in units
            if (
                unit.start >= candidate_end
                and unit.start < terminal_start
                and not unit.boundary
            )
        ]
        if not rightward:
            return ()

        starts = []
        current_end = None
        for unit in rightward:
            if current_end is None:
                starts.append((unit.start, unit.end))
                current_end = unit.end
            elif unit.start >= current_end:
                current_end = unit.end
                starts.append((rightward[0].start, current_end))

        unique_bounds = tuple(dict.fromkeys(starts))
        spans = tuple(
            _governed_span(
                projection=projection,
                start=start,
                end=end,
                relationship_code="rightward_prefix_attachment_candidate",
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                evidence_codes=(
                    "exact_rightward_source_order",
                    "terminal_boundary_not_crossed",
                    "every_prefix_preserved",
                ),
            )
            for start, end in unique_bounds[:maximum]
        )
        return spans

    return ()


def _attachment_status(
    candidate: ResonantOperatorBindingCandidate,
    rule: object,
    spans: tuple[GovernedSpanCandidate, ...],
) -> AttachmentStatus:
    if (
        candidate.candidate_variant_code
        == "possible_incomplete_quotation"
        and rule.attachment_strategy
        is AttachmentStrategy.EXACT_DELIMITED_INTERIOR
    ):
        return AttachmentStatus.MALFORMED_ATTACHMENT

    if (
        rule.attachment_strategy
        is AttachmentStrategy.NO_ATTACHMENT_UNTIL_AUTHORIZED_BINDING
    ):
        return AttachmentStatus.UNSUPPORTED_ATTACHMENT

    if not spans:
        return AttachmentStatus.UNRESOLVED_ATTACHMENT
    if len(spans) == 1:
        return AttachmentStatus.SINGULAR_ATTACHMENT
    return AttachmentStatus.MULTIPLE_ATTACHMENTS


def _scope_occurrence(
    *,
    constrained_trail_id: str,
    trail: CandidateResonantPhaseTrail,
    projection: SourceFieldProjectionRecord,
    binding_result: ResonantOperatorCandidateBindingResult,
    candidate: ResonantOperatorBindingCandidate,
    rule: object,
    limits: ScopeConstraintLimits,
) -> ScopeAttachmentOccurrence:
    spans = _span_candidates_for_rule(
        projection=projection,
        binding_result=binding_result,
        candidate=candidate,
        rule=rule,
        maximum=limits.max_governed_spans_per_occurrence,
    )
    status = _attachment_status(candidate, rule, spans)

    body = {
        "constrained_trail_id": constrained_trail_id,
        "phase_trail_id": trail.phase_trail_id,
        "source_event_id": projection.source_event_id,
        "projection_id": projection.projection_id,
        "candidate_binding_id": candidate.candidate_binding_id,
        "candidate_operator_key": candidate.candidate_operator_key,
        "candidate_operator_version": candidate.candidate_operator_version,
        "responsibility": rule.responsibility,
        "exact_source_span_ids": candidate.source_span_ids,
        "exact_code_point_ranges": candidate.code_point_ranges,
        "exact_utf8_byte_ranges": candidate.utf8_byte_ranges,
        "exact_source_fragments": candidate.exact_source_fragments,
        "possible_governed_spans": spans,
        "possible_parent_binding_ids": candidate.possible_parent_binding_ids,
        "possible_child_binding_ids": candidate.possible_child_binding_ids,
        "attachment_rule_id": rule.rule_id,
        "attachment_rule_key": rule.rule_key,
        "attachment_rule_version": rule.rule_version,
        "attachment_status": status,
        "singular_attachment": (
            status is AttachmentStatus.SINGULAR_ATTACHMENT
        ),
        "multiple_attachment": (
            status is AttachmentStatus.MULTIPLE_ATTACHMENTS
        ),
        "malformed_attachment": (
            status is AttachmentStatus.MALFORMED_ATTACHMENT
        ),
        "unsupported_attachment": (
            status is AttachmentStatus.UNSUPPORTED_ATTACHMENT
        ),
        "unresolved_attachment": (
            status is AttachmentStatus.UNRESOLVED_ATTACHMENT
        ),
        "selected_attachment_id": None,
        "authority_guard_codes": authority_conversion_guards(),
        "original_trail_mutated": False,
        "selected_meaning": False,
        "permission_inferred": False,
        "capability_authorized": False,
        "route_created": False,
        "tool_routing_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "release_authorized": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "occurrence_schema_id": SCOPE_OCCURRENCE_SCHEMA_ID,
    }
    return ScopeAttachmentOccurrence(
        occurrence_id=stable_record_id("scope_attachment_occurrence", body),
        **body,
    )


def _exact_reference_form(
    candidate: ResonantOperatorBindingCandidate,
) -> str:
    return "".join(candidate.exact_source_fragments)


def _context_match_codes(
    form: str,
    entry: ActiveContextEntry,
) -> tuple[str, ...]:
    codes = []

    if form in entry.exact_identifiers:
        codes.append("exact_explicit_identifier")
    if form in entry.exact_reference_forms:
        codes.append("exact_caller_supplied_reference_form")

    if form in {
        "the previous file",
        "The previous file",
        "THE PREVIOUS FILE",
    }:
        if (
            entry.object_kind is ContextObjectKind.FILE
            and ContextPositionTag.PREVIOUS in entry.position_tags
        ):
            codes.append("explicit_previous_file_metadata")

    if form in {
        "the approved version",
        "The approved version",
        "THE APPROVED VERSION",
    }:
        if (
            entry.object_kind is ContextObjectKind.VERSION
            and entry.operational_status
            is ContextOperationalStatus.ACCEPTED
        ):
            codes.append("explicit_accepted_version_metadata")

    if form in {
        "the first one",
        "The first one",
        "THE FIRST ONE",
    }:
        if entry.ordinal == 1:
            codes.append("explicit_ordinal_one_metadata")

    if form in {
        "the patch above",
        "The patch above",
        "THE PATCH ABOVE",
    }:
        if (
            entry.object_kind is ContextObjectKind.PATCH
            and ContextPositionTag.ABOVE in entry.position_tags
        ):
            codes.append("explicit_patch_above_metadata")

    if form in {
        "the quoted document",
        "The quoted document",
        "THE QUOTED DOCUMENT",
    }:
        if (
            entry.object_kind is ContextObjectKind.DOCUMENT
            and ContextPositionTag.QUOTED in entry.position_tags
        ):
            codes.append("explicit_quoted_document_metadata")

    return tuple(codes)


def _reference_candidate(
    *,
    candidate: ResonantOperatorBindingCandidate,
    registry: ActiveContextRegistry,
    entry: ActiveContextEntry,
    match_codes: tuple[str, ...],
) -> ReferenceContextCandidate:
    form = _exact_reference_form(candidate)
    body = {
        "reference_binding_id": candidate.candidate_binding_id,
        "source_event_id": candidate.source_event_id,
        "projection_id": candidate.projection_id,
        "exact_reference_form": form,
        "source_span_ids": candidate.source_span_ids,
        "context_registry_id": registry.registry_id,
        "context_entry_id": entry.entry_id,
        "context_object_id": entry.context_object_id,
        "match_rule_code": match_codes[0],
        "supporting_condition_codes": match_codes,
        "conflicting_condition_codes": (),
        "candidate_only": True,
        "selected": False,
        "reference_resolved": False,
        "concept_meaning_created": False,
        "predicate_role_assigned": False,
        "capability_binding_created": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "reference_candidate_schema_id": REFERENCE_CANDIDATE_SCHEMA_ID,
    }
    return ReferenceContextCandidate(
        reference_candidate_id=stable_record_id(
            "reference_context_candidate",
            body,
        ),
        **body,
    )


def _reference_analysis(
    *,
    constrained_trail_id: str,
    trail: CandidateResonantPhaseTrail,
    candidate: ResonantOperatorBindingCandidate,
    registry: ActiveContextRegistry | None,
    requested_context_dependencies: tuple[str, ...],
    maximum_candidates: int,
) -> ReferenceAnalysis:
    form = _exact_reference_form(candidate)
    context_candidates: tuple[ReferenceContextCandidate, ...] = ()
    missing_context = False
    prohibited = False
    unsupported = False
    unresolved = False

    if requested_context_dependencies:
        status = ReferenceAnalysisStatus.PROHIBITED_CONTEXT_DEPENDENCY
        prohibited = True
    elif registry is None:
        status = ReferenceAnalysisStatus.MISSING_CONTEXT_REFERENCE
        missing_context = True
    elif form not in _SUPPORTED_DEICTIC_FORMS and not any(
        form in entry.exact_identifiers
        or form in entry.exact_reference_forms
        for entry in registry.entries
    ):
        status = ReferenceAnalysisStatus.UNSUPPORTED_REFERENCE_FORM
        unsupported = True
    else:
        matches = []
        for entry in registry.entries:
            codes = _context_match_codes(form, entry)
            if codes:
                matches.append(
                    _reference_candidate(
                        candidate=candidate,
                        registry=registry,
                        entry=entry,
                        match_codes=codes,
                    )
                )

        context_candidates = tuple(
            sorted(matches, key=lambda item: item.reference_candidate_id)
        )[:maximum_candidates]

        if not context_candidates:
            status = ReferenceAnalysisStatus.UNRESOLVED_REFERENCE
            unresolved = True
        elif len(context_candidates) == 1:
            status = (
                ReferenceAnalysisStatus.
                ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE
            )
        else:
            status = (
                ReferenceAnalysisStatus.MULTIPLE_REFERENCE_CANDIDATES
            )

    body = {
        "constrained_trail_id": constrained_trail_id,
        "phase_trail_id": trail.phase_trail_id,
        "reference_binding_id": candidate.candidate_binding_id,
        "source_event_id": candidate.source_event_id,
        "projection_id": candidate.projection_id,
        "exact_reference_form": form,
        "source_span_ids": candidate.source_span_ids,
        "context_registry_id": (
            registry.registry_id if registry is not None else None
        ),
        "status": status,
        "candidates": context_candidates,
        "candidate_count": len(context_candidates),
        "missing_context": missing_context,
        "prohibited_context_dependency": prohibited,
        "unsupported_reference_form": unsupported,
        "unresolved": unresolved,
        "multiple_candidates_preserved": len(context_candidates) > 1,
        "selected_context_entry_id": None,
        "reference_resolved": False,
        "concept_meaning_created": False,
        "predicate_role_assigned": False,
        "capability_binding_created": False,
        "memory_search_performed": False,
        "file_search_performed": False,
        "repository_history_search_performed": False,
        "web_search_performed": False,
        "embedding_performed": False,
        "language_model_used": False,
        "similarity_search_performed": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "reference_analysis_schema_id": REFERENCE_ANALYSIS_SCHEMA_ID,
    }
    return ReferenceAnalysis(
        analysis_id=stable_record_id("reference_analysis", body),
        **body,
    )


def _constraint_status(
    constrained_trails: tuple[ScopeConstrainedCandidateTrail, ...],
) -> ScopeConstraintStatus:
    analyses = tuple(
        analysis
        for trail in constrained_trails
        for analysis in trail.reference_analyses
    )
    occurrences = tuple(
        occurrence
        for trail in constrained_trails
        for occurrence in trail.scope_occurrences
    )

    if any(
        analysis.status
        is ReferenceAnalysisStatus.PROHIBITED_CONTEXT_DEPENDENCY
        for analysis in analyses
    ):
        return ScopeConstraintStatus.PROHIBITED_CONTEXT_DEPENDENCY
    if any(
        occurrence.attachment_status
        is AttachmentStatus.MALFORMED_ATTACHMENT
        for occurrence in occurrences
    ):
        return ScopeConstraintStatus.MALFORMED_SCOPE_ATTACHMENT
    if any(
        occurrence.attachment_status
        is AttachmentStatus.UNSUPPORTED_ATTACHMENT
        for occurrence in occurrences
    ):
        return ScopeConstraintStatus.UNSUPPORTED_SCOPE_ATTACHMENT
    if any(
        analysis.status
        is ReferenceAnalysisStatus.MISSING_CONTEXT_REFERENCE
        for analysis in analyses
    ):
        return ScopeConstraintStatus.MISSING_CONTEXT_REFERENCE
    if any(
        occurrence.attachment_status
        is AttachmentStatus.MULTIPLE_ATTACHMENTS
        for occurrence in occurrences
    ):
        return ScopeConstraintStatus.CONFLICTING_SCOPE_ATTACHMENTS
    if not constrained_trails:
        return ScopeConstraintStatus.ZERO_SCOPE_CONSTRAINTS
    if len(constrained_trails) == 1:
        return ScopeConstraintStatus.ONE_SCOPE_CONSTRAINED_TRAIL
    return ScopeConstraintStatus.MULTIPLE_SCOPE_CONSTRAINED_TRAILS


def apply_scope_attachment_reference_constraints(
    projection_result: object,
    binding_result: object,
    phase_trail_result: object,
    *,
    active_context_registry: object = None,
    requested_context_dependencies: tuple[str, ...] = (),
    policy: object = _DEFAULT_SENTINEL,
    limits: object = _DEFAULT_SENTINEL,
) -> ScopeAttachmentReferenceConstraintResult:
    """Create immutable scope-constrained candidate trail views."""

    selected_policy = (
        build_default_scope_constraint_policy()
        if policy is _DEFAULT_SENTINEL
        else policy
    )
    selected_limits = (
        default_scope_constraint_limits()
        if limits is _DEFAULT_SENTINEL
        else limits
    )

    policy_issues = _policy_issues(selected_policy)
    limits_issues = _limits_issues(selected_limits)

    if policy_issues or limits_issues:
        return _result(
            status=ScopeConstraintStatus.SCOPE_CONSTRAINT_FAILED,
            reason_code="invalid_scope_policy_or_limits",
            constraint_set_created=False,
            source_preserved_in_custody=False,
            source_event_id="",
            source_sha256="",
            projection_id="",
            binding_set_id="",
            phase_trail_set_id="",
            policy=(
                selected_policy
                if type(selected_policy) is ScopeConstraintPolicy
                else None
            ),
            limits=(
                selected_limits
                if type(selected_limits) is ScopeConstraintLimits
                else None
            ),
            active_context_registry=None,
            constraint_set=None,
            validation_issue_codes=policy_issues + limits_issues,
        )

    assert type(selected_policy) is ScopeConstraintPolicy
    assert type(selected_limits) is ScopeConstraintLimits

    registry = build_default_symbolic_grammar_operator_registry()
    proposal_ruleset = build_default_resonant_operator_proposal_ruleset(
        registry
    )

    projection_validation = validate_source_field_projection_result(
        projection_result
    )
    binding_validation = (
        validate_resonant_operator_candidate_binding_result(
            binding_result,
            projection_result.projection,
            registry,
            proposal_ruleset,
        )
        if (
            projection_validation.ok
            and type(projection_result) is SourceFieldProjectionResult
            and projection_result.projection is not None
        )
        else None
    )
    trail_validation = (
        validate_candidate_resonant_phase_trail_result(
            phase_trail_result,
            projection_result,
            binding_result,
            registry,
        )
        if binding_validation is not None and binding_validation.ok
        else None
    )

    issue_codes = tuple(
        issue.code
        for report in (
            projection_validation,
            binding_validation,
            trail_validation,
        )
        if report is not None
        for issue in report.issues
    )

    projection = (
        projection_result.projection
        if type(projection_result) is SourceFieldProjectionResult
        else None
    )
    binding_set = (
        binding_result.binding_set
        if type(binding_result) is ResonantOperatorCandidateBindingResult
        else None
    )
    trail_set = (
        phase_trail_result.phase_trail_set
        if type(phase_trail_result) is CandidateResonantPhaseTrailResult
        else None
    )

    source_event_id = projection.source_event_id if projection else ""
    source_sha256 = projection.source_sha256 if projection else ""
    projection_id = projection.projection_id if projection else ""
    binding_set_id = binding_set.binding_set_id if binding_set else ""
    phase_trail_set_id = (
        trail_set.phase_trail_set_id if trail_set else ""
    )

    if (
        not projection_validation.ok
        or binding_validation is None
        or not binding_validation.ok
        or trail_validation is None
        or not trail_validation.ok
        or projection is None
        or binding_set is None
    ):
        return _result(
            status=ScopeConstraintStatus.SCOPE_CONSTRAINT_FAILED,
            reason_code="invalid_predecessor_contract",
            constraint_set_created=False,
            source_preserved_in_custody=bool(projection),
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            projection_id=projection_id,
            binding_set_id=binding_set_id,
            phase_trail_set_id=phase_trail_set_id,
            policy=selected_policy,
            limits=selected_limits,
            active_context_registry=None,
            constraint_set=None,
            validation_issue_codes=issue_codes,
        )

    from .validation import validate_active_context_registry

    selected_context = (
        active_context_registry
        if type(active_context_registry) is ActiveContextRegistry
        else None
    )

    if active_context_registry is not None:
        context_report = validate_active_context_registry(
            active_context_registry
        )
        if (
            not context_report.ok
            or selected_context is None
            or selected_context.exact_entry_count
            > selected_limits.max_active_context_entries
        ):
            context_codes = tuple(
                issue.code for issue in context_report.issues
            )
            if (
                selected_context is not None
                and selected_context.exact_entry_count
                > selected_limits.max_active_context_entries
            ):
                context_codes += ("active_context_entry_limit_exceeded",)

            return _result(
                status=ScopeConstraintStatus.SCOPE_CONSTRAINT_FAILED,
                reason_code="invalid_active_context_registry",
                constraint_set_created=False,
                source_preserved_in_custody=True,
                source_event_id=source_event_id,
                source_sha256=source_sha256,
                projection_id=projection_id,
                binding_set_id=binding_set_id,
                phase_trail_set_id=phase_trail_set_id,
                policy=selected_policy,
                limits=selected_limits,
                active_context_registry=selected_context,
                constraint_set=None,
                validation_issue_codes=context_codes,
            )

    if trail_set is None:
        empty_body = {
            "source_event_id": source_event_id,
            "source_sha256": source_sha256,
            "projection_id": projection_id,
            "binding_set_id": binding_set_id,
            "phase_trail_set_id": phase_trail_set_id,
            "policy_id": selected_policy.policy_id,
            "limits_id": selected_limits.limits_id,
            "active_context_registry_id": (
                selected_context.registry_id if selected_context else None
            ),
            "status": ScopeConstraintStatus.ZERO_SCOPE_CONSTRAINTS,
            "constrained_trails": (),
            "constrained_trail_count": 0,
            "scope_occurrence_count": 0,
            "reference_analysis_count": 0,
            "singular_attachment_count": 0,
            "multiple_attachment_count": 0,
            "unresolved_attachment_count": 0,
            "malformed_attachment_count": 0,
            "unsupported_attachment_count": 0,
            "one_reference_candidate_count": 0,
            "multiple_reference_candidate_count": 0,
            "unresolved_reference_count": 0,
            "missing_context_reference_count": 0,
            "prohibited_context_dependency_count": 0,
            "all_original_trails_preserved": True,
            "all_lawful_attachments_preserved": True,
            "false_authority_conversion_count": len(
                authority_conversion_guards()
            ),
            "selected_trail_id": None,
            "selected_attachment_id": None,
            "resolved_reference_entry_id": None,
            "selected_meaning": False,
            "concept_authority_available": False,
            "predicate_authority_available": False,
            "permission_authority_available": False,
            "capability_authority_available": False,
            "route_authority_available": False,
            "tool_authority_available": False,
            "memory_authority_available": False,
            "action_authority_available": False,
            "delivery_authority_available": False,
            "release_authority_available": False,
            "hidden_fallback_allowed": False,
            "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
            "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
            "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
            "constraint_set_schema_id": CONSTRAINT_SET_SCHEMA_ID,
        }
        empty_set = ScopeAttachmentReferenceConstraintSet(
            constraint_set_id=stable_record_id(
                "scope_attachment_reference_constraint_set",
                empty_body,
            ),
            **empty_body,
        )
        return _result(
            status=ScopeConstraintStatus.ZERO_SCOPE_CONSTRAINTS,
            reason_code="no_candidate_phase_trails",
            constraint_set_created=True,
            source_preserved_in_custody=True,
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            projection_id=projection_id,
            binding_set_id=binding_set_id,
            phase_trail_set_id=phase_trail_set_id,
            policy=selected_policy,
            limits=selected_limits,
            active_context_registry=selected_context,
            constraint_set=empty_set,
        )

    candidates = {
        candidate.candidate_binding_id: candidate
        for candidate in binding_set.candidates
    }

    planned_occurrence_count = 0
    constrained_trails = []

    for trail in trail_set.trails:
        constraint_set_seed = stable_record_id(
            "scope_constraint_set_seed",
            {
                "phase_trail_set_id": trail_set.phase_trail_set_id,
                "policy_id": selected_policy.policy_id,
                "context_registry_id": (
                    selected_context.registry_id
                    if selected_context
                    else None
                ),
            },
        )
        constrained_trail_id = stable_record_id(
            "scope_constrained_trail_seed",
            {
                "constraint_set_seed": constraint_set_seed,
                "phase_trail_id": trail.phase_trail_id,
            },
        )

        occurrences = []
        analyses = []

        for binding_id in trail.participating_binding_ids:
            candidate = candidates.get(binding_id)
            if candidate is None:
                continue

            candidate_rules = rules_for_candidate(
                operator_key=candidate.candidate_operator_key,
                operator_family=candidate.candidate_operator_family,
                candidate_variant_code=candidate.candidate_variant_code,
            )

            for rule in candidate_rules:
                planned_occurrence_count += 1
                if (
                    planned_occurrence_count
                    > selected_limits.max_scope_occurrences
                ):
                    return _result(
                        status=(
                            ScopeConstraintStatus.
                            SCOPE_CONSTRAINT_LIMIT_EXCEEDED
                        ),
                        reason_code="scope_occurrence_limit_exceeded",
                        constraint_set_created=False,
                        source_preserved_in_custody=True,
                        source_event_id=source_event_id,
                        source_sha256=source_sha256,
                        projection_id=projection_id,
                        binding_set_id=binding_set_id,
                        phase_trail_set_id=phase_trail_set_id,
                        policy=selected_policy,
                        limits=selected_limits,
                        active_context_registry=selected_context,
                        constraint_set=None,
                        validation_issue_codes=(
                            "scope_occurrence_limit_exceeded",
                        ),
                    )

                occurrences.append(
                    _scope_occurrence(
                        constrained_trail_id=constrained_trail_id,
                        trail=trail,
                        projection=projection,
                        binding_result=binding_result,
                        candidate=candidate,
                        rule=rule,
                        limits=selected_limits,
                    )
                )

            if candidate.candidate_operator_key == "grammar_reference":
                analyses.append(
                    _reference_analysis(
                        constrained_trail_id=constrained_trail_id,
                        trail=trail,
                        candidate=candidate,
                        registry=selected_context,
                        requested_context_dependencies=(
                            requested_context_dependencies
                        ),
                        maximum_candidates=(
                            selected_limits.max_reference_candidates
                        ),
                    )
                )

        occurrences_tuple = tuple(
            sorted(occurrences, key=lambda item: item.occurrence_id)
        )
        analyses_tuple = tuple(
            sorted(analyses, key=lambda item: item.analysis_id)
        )

        trail_body = {
            "constraint_set_id": constraint_set_seed,
            "phase_trail_id": trail.phase_trail_id,
            "phase_trail_set_id": trail.phase_trail_set_id,
            "source_event_id": trail.source_event_id,
            "source_sha256": trail.source_sha256,
            "projection_id": trail.projection_id,
            "binding_set_id": trail.binding_set_id,
            "original_trail_record_id": trail.expected_id(),
            "scope_occurrences": occurrences_tuple,
            "reference_analyses": analyses_tuple,
            "authority_guard_codes": authority_conversion_guards(),
            "scope_occurrence_count": len(occurrences_tuple),
            "reference_analysis_count": len(analyses_tuple),
            "unresolved_attachment_count": sum(
                item.unresolved_attachment
                for item in occurrences_tuple
            ),
            "multiple_attachment_count": sum(
                item.multiple_attachment
                for item in occurrences_tuple
            ),
            "conflicting_attachment_count": sum(
                item.multiple_attachment
                for item in occurrences_tuple
            ),
            "original_trail_preserved": True,
            "original_trail_mutated": False,
            "candidate_only": True,
            "selected_trail": False,
            "selected_attachment": False,
            "reference_resolved": False,
            "selected_meaning": False,
            "concept_meaning_created": False,
            "predicate_role_assigned": False,
            "permission_inferred": False,
            "capability_authorized": False,
            "route_created": False,
            "tool_routing_performed": False,
            "memory_read_performed": False,
            "memory_write_performed": False,
            "action_performed": False,
            "delivery_performed": False,
            "release_authorized": False,
            "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
            "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
            "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
            "constrained_trail_schema_id": CONSTRAINED_TRAIL_SCHEMA_ID,
        }
        constrained_trails.append(
            ScopeConstrainedCandidateTrail(
                constrained_trail_id=constrained_trail_id,
                **trail_body,
            )
        )

    constrained_tuple = tuple(
        sorted(
            constrained_trails,
            key=lambda item: item.constrained_trail_id,
        )
    )
    status = _constraint_status(constrained_tuple)

    all_occurrences = tuple(
        occurrence
        for trail in constrained_tuple
        for occurrence in trail.scope_occurrences
    )
    all_analyses = tuple(
        analysis
        for trail in constrained_tuple
        for analysis in trail.reference_analyses
    )

    set_seed = stable_record_id(
        "scope_constraint_set_seed",
        {
            "phase_trail_set_id": trail_set.phase_trail_set_id,
            "policy_id": selected_policy.policy_id,
            "context_registry_id": (
                selected_context.registry_id if selected_context else None
            ),
        },
    )

    # Replace seed-only links with the final deterministic constraint-set id by
    # making the seed itself the set identity. It is stable over all immutable
    # inputs and avoids circular record identity.
    set_body = {
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "projection_id": projection_id,
        "binding_set_id": binding_set_id,
        "phase_trail_set_id": trail_set.phase_trail_set_id,
        "policy_id": selected_policy.policy_id,
        "limits_id": selected_limits.limits_id,
        "active_context_registry_id": (
            selected_context.registry_id if selected_context else None
        ),
        "status": status,
        "constrained_trails": constrained_tuple,
        "constrained_trail_count": len(constrained_tuple),
        "scope_occurrence_count": len(all_occurrences),
        "reference_analysis_count": len(all_analyses),
        "singular_attachment_count": sum(
            item.singular_attachment for item in all_occurrences
        ),
        "multiple_attachment_count": sum(
            item.multiple_attachment for item in all_occurrences
        ),
        "unresolved_attachment_count": sum(
            item.unresolved_attachment for item in all_occurrences
        ),
        "malformed_attachment_count": sum(
            item.malformed_attachment for item in all_occurrences
        ),
        "unsupported_attachment_count": sum(
            item.unsupported_attachment for item in all_occurrences
        ),
        "one_reference_candidate_count": sum(
            item.status
            is ReferenceAnalysisStatus.
            ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE
            for item in all_analyses
        ),
        "multiple_reference_candidate_count": sum(
            item.status
            is ReferenceAnalysisStatus.MULTIPLE_REFERENCE_CANDIDATES
            for item in all_analyses
        ),
        "unresolved_reference_count": sum(
            item.status
            is ReferenceAnalysisStatus.UNRESOLVED_REFERENCE
            for item in all_analyses
        ),
        "missing_context_reference_count": sum(
            item.status
            is ReferenceAnalysisStatus.MISSING_CONTEXT_REFERENCE
            for item in all_analyses
        ),
        "prohibited_context_dependency_count": sum(
            item.status
            is ReferenceAnalysisStatus.PROHIBITED_CONTEXT_DEPENDENCY
            for item in all_analyses
        ),
        "all_original_trails_preserved": all(
            item.original_trail_preserved
            and not item.original_trail_mutated
            for item in constrained_tuple
        ),
        "all_lawful_attachments_preserved": all(
            occurrence.selected_attachment_id is None
            for occurrence in all_occurrences
        ),
        "false_authority_conversion_count": len(
            authority_conversion_guards()
        ),
        "selected_trail_id": None,
        "selected_attachment_id": None,
        "resolved_reference_entry_id": None,
        "selected_meaning": False,
        "concept_authority_available": False,
        "predicate_authority_available": False,
        "permission_authority_available": False,
        "capability_authority_available": False,
        "route_authority_available": False,
        "tool_authority_available": False,
        "memory_authority_available": False,
        "action_authority_available": False,
        "delivery_authority_available": False,
        "release_authority_available": False,
        "hidden_fallback_allowed": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "constraint_set_schema_id": CONSTRAINT_SET_SCHEMA_ID,
    }
    constraint_set = ScopeAttachmentReferenceConstraintSet(
        constraint_set_id=set_seed,
        **set_body,
    )

    reason_code = {
        ScopeConstraintStatus.ZERO_SCOPE_CONSTRAINTS: (
            "no_scope_bearing_candidate_trails"
        ),
        ScopeConstraintStatus.ONE_SCOPE_CONSTRAINED_TRAIL: (
            "one_candidate_trail_constrained"
        ),
        ScopeConstraintStatus.MULTIPLE_SCOPE_CONSTRAINED_TRAILS: (
            "multiple_candidate_trails_constrained"
        ),
        ScopeConstraintStatus.CONFLICTING_SCOPE_ATTACHMENTS: (
            "multiple_lawful_attachments_preserved"
        ),
        ScopeConstraintStatus.MALFORMED_SCOPE_ATTACHMENT: (
            "malformed_attachment_preserved"
        ),
        ScopeConstraintStatus.UNSUPPORTED_SCOPE_ATTACHMENT: (
            "unsupported_attachment_preserved"
        ),
        ScopeConstraintStatus.MISSING_CONTEXT_REFERENCE: (
            "explicit_context_registry_missing"
        ),
        ScopeConstraintStatus.PROHIBITED_CONTEXT_DEPENDENCY: (
            "prohibited_context_dependency_refused"
        ),
    }.get(status, "scope_constraints_constructed")

    result = _result(
        status=status,
        reason_code=reason_code,
        constraint_set_created=True,
        source_preserved_in_custody=True,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        projection_id=projection_id,
        binding_set_id=binding_set_id,
        phase_trail_set_id=trail_set.phase_trail_set_id,
        policy=selected_policy,
        limits=selected_limits,
        active_context_registry=selected_context,
        constraint_set=constraint_set,
    )

    from .validation import (
        validate_scope_attachment_reference_constraint_result,
    )

    report = validate_scope_attachment_reference_constraint_result(
        result,
        projection_result,
        binding_result,
        phase_trail_result,
    )
    if not report.ok:
        return _result(
            status=ScopeConstraintStatus.SCOPE_CONSTRAINT_FAILED,
            reason_code="constructed_constraint_result_failed_validation",
            constraint_set_created=False,
            source_preserved_in_custody=True,
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            projection_id=projection_id,
            binding_set_id=binding_set_id,
            phase_trail_set_id=trail_set.phase_trail_set_id,
            policy=selected_policy,
            limits=selected_limits,
            active_context_registry=selected_context,
            constraint_set=None,
            validation_issue_codes=tuple(
                issue.code for issue in report.issues
            ),
        )

    return result
