"""Exact deterministic Slice 36D candidate-binding engine.

The engine matches only the closed, versioned rules in ``rules.py`` against
exact Slice 36B code points. It preserves zero, one, or multiple candidates.
It does not apply an operator, assign a phase, select meaning, infer
permission, route a capability, access memory, or perform an action.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib

from ..input_event_custody import (
    CUSTODY_SCHEMA_VERSION,
    CUSTODY_SPEC_ID,
    CUSTODY_SPEC_VERSION,
)
from ..schema import stable_record_id
from ..source_field_projection import (
    SOURCE_FIELD_SCHEMA_ID,
    SourceFieldProjectionRecord,
    SourceFieldProjectionResult,
    SourceFieldProjectionStatus,
    SourceFieldSupportStatus,
    validate_source_field_projection,
    validate_source_field_projection_result,
)
from ..symbolic_grammar_operator_registry import (
    GrammarOperatorDefinition,
    SymbolicGrammarOperatorRegistry,
    build_default_symbolic_grammar_operator_registry,
    grammar_operator_for_key,
    validate_symbolic_grammar_operator_registry,
)
from .rules import build_default_resonant_operator_proposal_ruleset
from .schema import (
    ABSOLUTE_MAX_BINDING_CANDIDATES,
    ABSOLUTE_MAX_UNBOUND_SIGNALS,
    BINDING_SCHEMA_VERSION,
    BINDING_SPEC_ID,
    BINDING_SPEC_VERSION,
    DEFAULT_MAX_BINDING_CANDIDATES,
    DEFAULT_MAX_UNBOUND_SIGNALS,
    CandidateBindingLimits,
    CandidateBindingStatus,
    CandidateSupportStatus,
    DeterministicConfidenceBasis,
    NeighborCompatibilityStatus,
    ProposalOutputKind,
    ProposalRuleKind,
    ResonantOperatorBindingCandidate,
    ResonantOperatorCandidateBindingResult,
    ResonantOperatorCandidateBindingSet,
    ResonantOperatorProposalRule,
    ResonantOperatorProposalRuleSet,
    SourceEdgePolicy,
    SourcePositionPolicy,
    UnboundStructuralSignal,
)

_DEFAULT_LIMITS_SENTINEL = object()


def default_candidate_binding_limits() -> CandidateBindingLimits:
    body = {
        "max_candidates": DEFAULT_MAX_BINDING_CANDIDATES,
        "max_unbound_signals": DEFAULT_MAX_UNBOUND_SIGNALS,
        "binding_spec_id": BINDING_SPEC_ID,
        "binding_spec_version": BINDING_SPEC_VERSION,
        "schema_version": BINDING_SCHEMA_VERSION,
        "limits_schema_id": (
            "aiweb-resonant-operator-candidate-binding-limits-v1"
        ),
    }
    return CandidateBindingLimits(
        limits_id=stable_record_id("candidate_binding_limits", body),
        **body,
    )


def build_candidate_binding_limits(
    *,
    max_candidates: int = DEFAULT_MAX_BINDING_CANDIDATES,
    max_unbound_signals: int = DEFAULT_MAX_UNBOUND_SIGNALS,
) -> CandidateBindingLimits:
    body = {
        "max_candidates": max_candidates,
        "max_unbound_signals": max_unbound_signals,
        "binding_spec_id": BINDING_SPEC_ID,
        "binding_spec_version": BINDING_SPEC_VERSION,
        "schema_version": BINDING_SCHEMA_VERSION,
        "limits_schema_id": (
            "aiweb-resonant-operator-candidate-binding-limits-v1"
        ),
    }
    return CandidateBindingLimits(
        limits_id=stable_record_id("candidate_binding_limits", body),
        **body,
    )


def _limits_issues(limits: object) -> tuple[str, ...]:
    if type(limits) is not CandidateBindingLimits:
        return ("invalid_candidate_binding_limits_type",)
    issues: list[str] = []
    if limits.limits_id != limits.expected_id():
        issues.append("candidate_binding_limits_id_mismatch")
    if type(limits.max_candidates) is not int:
        issues.append("invalid_max_candidates_type")
    elif not 0 <= limits.max_candidates <= ABSOLUTE_MAX_BINDING_CANDIDATES:
        issues.append("invalid_max_candidates_range")
    if type(limits.max_unbound_signals) is not int:
        issues.append("invalid_max_unbound_signals_type")
    elif not 0 <= limits.max_unbound_signals <= ABSOLUTE_MAX_UNBOUND_SIGNALS:
        issues.append("invalid_max_unbound_signals_range")
    return tuple(issues)


def _result(
    *,
    status: CandidateBindingStatus,
    reason_code: str,
    binding_set_created: bool,
    source_preserved_in_custody: bool,
    source_event_id: str,
    source_sha256: str,
    projection_id: str,
    grammar_registry_id: str,
    proposal_ruleset_id: str,
    limits: CandidateBindingLimits | None,
    binding_set: ResonantOperatorCandidateBindingSet | None,
    validation_issue_codes: tuple[str, ...],
) -> ResonantOperatorCandidateBindingResult:
    body = {
        "status": status,
        "reason_code": reason_code,
        "binding_set_created": binding_set_created,
        "source_preserved_in_custody": source_preserved_in_custody,
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "projection_id": projection_id,
        "grammar_registry_id": grammar_registry_id,
        "proposal_ruleset_id": proposal_ruleset_id,
        "limits_id": limits.limits_id if limits else "",
        "binding_set_id": binding_set.binding_set_id if binding_set else "",
        "validation_issue_codes": validation_issue_codes,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "operator_application_performed": False,
        "phase_assignment_performed": False,
        "meaning_selected": False,
        "permission_inferred": False,
        "action_performed": False,
        "delivery_performed": False,
        "binding_spec_id": BINDING_SPEC_ID,
        "binding_spec_version": BINDING_SPEC_VERSION,
        "schema_version": BINDING_SCHEMA_VERSION,
        "result_schema_id": (
            "aiweb-resonant-operator-candidate-binding-result-v1"
        ),
    }
    return ResonantOperatorCandidateBindingResult(
        result_id=stable_record_id(
            "resonant_operator_candidate_binding_result",
            body,
        ),
        status=status,
        reason_code=reason_code,
        binding_set_created=binding_set_created,
        source_preserved_in_custody=source_preserved_in_custody,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        projection_id=projection_id,
        grammar_registry_id=grammar_registry_id,
        proposal_ruleset_id=proposal_ruleset_id,
        limits=limits,
        binding_set=binding_set,
        validation_issue_codes=validation_issue_codes,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        environment_access_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        route_registration_performed=False,
        tool_routing_performed=False,
        operator_application_performed=False,
        phase_assignment_performed=False,
        meaning_selected=False,
        permission_inferred=False,
        action_performed=False,
        delivery_performed=False,
    )


def _projection_text(projection: SourceFieldProjectionRecord) -> str:
    return "".join(atom.exact_text for atom in projection.code_points)


def _boundary_offsets(
    projection: SourceFieldProjectionRecord,
) -> tuple[int, ...]:
    return tuple(
        boundary.utf8_byte_offset
        for boundary in sorted(
            projection.boundaries,
            key=lambda item: item.ordinal,
        )
    )


def _source_span_id(
    projection: SourceFieldProjectionRecord,
    start: int,
    end: int,
    text: str,
    byte_offsets: tuple[int, ...],
) -> str:
    byte_start = byte_offsets[start]
    byte_end = byte_offsets[end]
    exact_text = text[start:end]
    body = {
        "input_event_id": projection.source_event_id,
        "source_sha256": projection.source_sha256,
        "code_point_start": start,
        "code_point_end": end,
        "utf8_byte_start": byte_start,
        "utf8_byte_end": byte_end,
        "code_point_length": end - start,
        "utf8_byte_length": byte_end - byte_start,
        "span_sha256": hashlib.sha256(
            exact_text.encode("utf-8", "strict")
        ).hexdigest(),
        "is_root_span": (
            start == 0 and end == projection.source_code_point_length
        ),
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return stable_record_id("source_span", body)


def _span_payload(
    projection: SourceFieldProjectionRecord,
    text: str,
    byte_offsets: tuple[int, ...],
    ranges: tuple[tuple[int, int], ...],
) -> tuple[
    tuple[str, ...],
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
    tuple[str, ...],
]:
    span_ids: list[str] = []
    byte_ranges: list[tuple[int, int]] = []
    fragments: list[str] = []
    for start, end in ranges:
        span_ids.append(
            _source_span_id(
                projection,
                start,
                end,
                text,
                byte_offsets,
            )
        )
        byte_ranges.append((byte_offsets[start], byte_offsets[end]))
        fragments.append(text[start:end])
    return (
        tuple(span_ids),
        ranges,
        tuple(byte_ranges),
        tuple(fragments),
    )


def _is_word_member(
    projection: SourceFieldProjectionRecord,
    index: int,
) -> bool:
    category = projection.code_points[index].general_category
    return category[:1] in {"L", "M", "N"} or category == "Pc"


def _word_edges_clear(
    projection: SourceFieldProjectionRecord,
    start: int,
    end: int,
) -> bool:
    before_clear = start == 0 or not _is_word_member(projection, start - 1)
    after_clear = (
        end == projection.source_code_point_length
        or not _is_word_member(projection, end)
    )
    return before_clear and after_clear


def _span_supported(
    projection: SourceFieldProjectionRecord,
    ranges: tuple[tuple[int, int], ...],
) -> bool:
    return all(
        atom.support_status is SourceFieldSupportStatus.SUPPORTED
        for start, end in ranges
        for atom in projection.code_points[start:end]
    )


def _exact_occurrences(
    text: str,
    form: str,
) -> tuple[tuple[int, int], ...]:
    found: list[tuple[int, int]] = []
    start = 0
    while True:
        index = text.find(form, start)
        if index < 0:
            break
        found.append((index, index + len(form)))
        start = index + 1
    return tuple(found)


def _whole_unit_matches(
    projection: SourceFieldProjectionRecord,
    text: str,
    rule: ResonantOperatorProposalRule,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    matches: set[tuple[tuple[int, int], ...]] = set()
    for form in rule.exact_forms:
        for start, end in _exact_occurrences(text, form):
            if (
                rule.edge_policy is SourceEdgePolicy.UNICODE_WORD_EDGE
                and not _word_edges_clear(projection, start, end)
            ):
                continue
            matches.add(((start, end),))
    return tuple(sorted(matches))


def _initial_sequence_matches(
    projection: SourceFieldProjectionRecord,
    text: str,
    rule: ResonantOperatorProposalRule,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    start = 0
    while start < len(text) and text[start].isspace():
        start += 1
    matches: list[tuple[tuple[int, int], ...]] = []
    for sequence in rule.exact_sequences:
        if len(sequence) != 2:
            continue
        first, second = sequence
        first_end = start + len(first)
        if text[start:first_end] != first:
            continue
        gap_end = first_end
        while gap_end < len(text) and text[gap_end].isspace():
            gap_end += 1
        if gap_end == first_end:
            continue
        second_end = gap_end + len(second)
        if text[gap_end:second_end] != second:
            continue
        if (
            rule.edge_policy is SourceEdgePolicy.UNICODE_WORD_EDGE
            and (
                not _word_edges_clear(projection, start, first_end)
                or not _word_edges_clear(
                    projection,
                    gap_end,
                    second_end,
                )
            )
        ):
            continue
        matches.append(((start, first_end), (gap_end, second_end)))
    return tuple(matches)


def _terminal_mark_matches(
    text: str,
    rule: ResonantOperatorProposalRule,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    index = len(text) - 1
    while index >= 0 and text[index].isspace():
        index -= 1
    if index < 0 or text[index] not in rule.exact_forms:
        return ()
    return (((index, index + 1),),)


def _quotation_occurrences(
    text: str,
    quotation_pairs: tuple[tuple[str, str], ...],
) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
]:
    paired: list[tuple[int, int]] = []
    unmatched: list[tuple[int, int]] = []
    occupied: set[int] = set()

    for opening, closing in quotation_pairs:
        if opening == closing:
            indexes = [
                index
                for index, character in enumerate(text)
                if character == opening and index not in occupied
            ]
            pair_count = len(indexes) // 2
            for pair_index in range(pair_count):
                left = indexes[pair_index * 2]
                right = indexes[pair_index * 2 + 1]
                paired.append((left, right))
                occupied.update((left, right))
            if len(indexes) % 2:
                last = indexes[-1]
                unmatched.append((last, last + 1))
                occupied.add(last)
            continue

        search_start = 0
        while True:
            left = text.find(opening, search_start)
            if left < 0:
                break
            if left in occupied:
                search_start = left + 1
                continue
            right = text.find(closing, left + len(opening))
            if right < 0:
                unmatched.append((left, left + len(opening)))
                occupied.add(left)
                search_start = left + len(opening)
                continue
            paired.append((left, right))
            occupied.update((left, right))
            search_start = right + len(closing)

    paired_ranges = tuple(
        ((left, left + 1), (right, right + 1))
        for left, right in sorted(set(paired))
    )
    unmatched_ranges = tuple(
        ((start, end),)
        for start, end in sorted(set(unmatched))
    )
    return paired_ranges, unmatched_ranges


def _rule_matches(
    projection: SourceFieldProjectionRecord,
    text: str,
    rule: ResonantOperatorProposalRule,
    quotation_cache: dict[
        tuple[tuple[str, str], ...],
        tuple[
            tuple[tuple[tuple[int, int], ...], ...],
            tuple[tuple[tuple[int, int], ...], ...],
        ],
    ],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    if rule.rule_kind is ProposalRuleKind.EXACT_WHOLE_UNIT:
        return _whole_unit_matches(projection, text, rule)
    if rule.rule_kind is ProposalRuleKind.EXACT_INITIAL_SEQUENCE:
        return _initial_sequence_matches(projection, text, rule)
    if rule.rule_kind is ProposalRuleKind.EXACT_TERMINAL_MARK:
        return _terminal_mark_matches(text, rule)
    if rule.rule_kind in {
        ProposalRuleKind.EXACT_QUOTATION_PAIR,
        ProposalRuleKind.EXACT_UNMATCHED_QUOTATION_OPEN,
    }:
        cached = quotation_cache.get(rule.quotation_pairs)
        if cached is None:
            cached = _quotation_occurrences(text, rule.quotation_pairs)
            quotation_cache[rule.quotation_pairs] = cached
        return (
            cached[0]
            if rule.rule_kind is ProposalRuleKind.EXACT_QUOTATION_PAIR
            else cached[1]
        )
    return ()


def _range_bounds(
    ranges: tuple[tuple[int, int], ...],
) -> tuple[int, int]:
    return min(start for start, _ in ranges), max(end for _, end in ranges)


def _neighboring(
    left: ResonantOperatorBindingCandidate,
    right: ResonantOperatorBindingCandidate,
    text: str,
) -> bool:
    left_start, left_end = _range_bounds(left.code_point_ranges)
    right_start, right_end = _range_bounds(right.code_point_ranges)
    if left_start < right_end and right_start < left_end:
        return True
    if left_end <= right_start:
        return all(character.isspace() for character in text[left_end:right_start])
    return all(character.isspace() for character in text[right_end:left_start])


def _contains(
    outer: ResonantOperatorBindingCandidate,
    inner: ResonantOperatorBindingCandidate,
) -> bool:
    outer_start, outer_end = _range_bounds(outer.code_point_ranges)
    inner_start, inner_end = _range_bounds(inner.code_point_ranges)
    return (
        outer_start <= inner_start
        and outer_end >= inner_end
        and (outer_start, outer_end) != (inner_start, inner_end)
    )


def bind_resonant_operator_candidates(
    projection_result: object,
    *,
    registry: object = None,
    ruleset: object = None,
    limits: object = _DEFAULT_LIMITS_SENTINEL,
) -> ResonantOperatorCandidateBindingResult:
    """Produce exact, non-selected operator candidates from a source field."""

    effective_limits = (
        default_candidate_binding_limits()
        if limits is _DEFAULT_LIMITS_SENTINEL
        else limits
    )
    limit_issues = _limits_issues(effective_limits)
    if limit_issues:
        return _result(
            status=CandidateBindingStatus.CANDIDATE_BINDINGS_LIMIT_EXCEEDED,
            reason_code=limit_issues[0],
            binding_set_created=False,
            source_preserved_in_custody=False,
            source_event_id="",
            source_sha256="",
            projection_id="",
            grammar_registry_id="",
            proposal_ruleset_id="",
            limits=(
                effective_limits
                if type(effective_limits) is CandidateBindingLimits
                else None
            ),
            binding_set=None,
            validation_issue_codes=limit_issues,
        )

    assert type(effective_limits) is CandidateBindingLimits

    if type(projection_result) is not SourceFieldProjectionResult:
        return _result(
            status=CandidateBindingStatus.CANDIDATE_BINDINGS_MALFORMED_SOURCE,
            reason_code="invalid_source_field_projection_result_type",
            binding_set_created=False,
            source_preserved_in_custody=False,
            source_event_id="",
            source_sha256="",
            projection_id="",
            grammar_registry_id="",
            proposal_ruleset_id="",
            limits=effective_limits,
            binding_set=None,
            validation_issue_codes=(
                "invalid_source_field_projection_result_type",
            ),
        )

    result_report = validate_source_field_projection_result(projection_result)
    if not result_report.ok:
        return _result(
            status=CandidateBindingStatus.CANDIDATE_BINDINGS_MALFORMED_SOURCE,
            reason_code="invalid_source_field_projection_result",
            binding_set_created=False,
            source_preserved_in_custody=(
                projection_result.source_preserved_in_custody
            ),
            source_event_id=projection_result.source_event_id,
            source_sha256=projection_result.source_sha256,
            projection_id=(
                projection_result.projection.projection_id
                if projection_result.projection
                else ""
            ),
            grammar_registry_id="",
            proposal_ruleset_id="",
            limits=effective_limits,
            binding_set=None,
            validation_issue_codes=tuple(
                issue.code for issue in result_report.issues
            ),
        )

    if projection_result.projection is None:
        status = (
            CandidateBindingStatus.CANDIDATE_BINDINGS_LIMIT_EXCEEDED
            if projection_result.status
            is SourceFieldProjectionStatus.SOURCE_FIELD_LIMIT_EXCEEDED
            else CandidateBindingStatus.CANDIDATE_BINDINGS_MALFORMED_SOURCE
        )
        return _result(
            status=status,
            reason_code="source_field_projection_not_available",
            binding_set_created=False,
            source_preserved_in_custody=(
                projection_result.source_preserved_in_custody
            ),
            source_event_id=projection_result.source_event_id,
            source_sha256=projection_result.source_sha256,
            projection_id="",
            grammar_registry_id="",
            proposal_ruleset_id="",
            limits=effective_limits,
            binding_set=None,
            validation_issue_codes=(
                "source_field_projection_not_available",
            ),
        )

    projection = projection_result.projection

    selected_registry = (
        build_default_symbolic_grammar_operator_registry()
        if registry is None
        else registry
    )
    registry_report = validate_symbolic_grammar_operator_registry(
        selected_registry
    )
    if not registry_report.ok:
        return _result(
            status=CandidateBindingStatus.CANDIDATE_BINDINGS_FAILED,
            reason_code="invalid_symbolic_grammar_operator_registry",
            binding_set_created=False,
            source_preserved_in_custody=True,
            source_event_id=projection.source_event_id,
            source_sha256=projection.source_sha256,
            projection_id=projection.projection_id,
            grammar_registry_id=(
                selected_registry.registry_id
                if type(selected_registry) is SymbolicGrammarOperatorRegistry
                else ""
            ),
            proposal_ruleset_id="",
            limits=effective_limits,
            binding_set=None,
            validation_issue_codes=tuple(
                issue.code for issue in registry_report.issues
            ),
        )

    assert type(selected_registry) is SymbolicGrammarOperatorRegistry

    selected_ruleset = (
        build_default_resonant_operator_proposal_ruleset(selected_registry)
        if ruleset is None
        else ruleset
    )
    from .validation import validate_resonant_operator_proposal_ruleset

    ruleset_report = validate_resonant_operator_proposal_ruleset(
        selected_ruleset,
        selected_registry,
    )
    if not ruleset_report.ok:
        return _result(
            status=CandidateBindingStatus.CANDIDATE_BINDINGS_FAILED,
            reason_code="invalid_resonant_operator_proposal_ruleset",
            binding_set_created=False,
            source_preserved_in_custody=True,
            source_event_id=projection.source_event_id,
            source_sha256=projection.source_sha256,
            projection_id=projection.projection_id,
            grammar_registry_id=selected_registry.registry_id,
            proposal_ruleset_id=(
                selected_ruleset.ruleset_id
                if type(selected_ruleset) is ResonantOperatorProposalRuleSet
                else ""
            ),
            limits=effective_limits,
            binding_set=None,
            validation_issue_codes=tuple(
                issue.code for issue in ruleset_report.issues
            ),
        )

    assert type(selected_ruleset) is ResonantOperatorProposalRuleSet

    try:
        text = _projection_text(projection)
        byte_offsets = _boundary_offsets(projection)
        if len(byte_offsets) != projection.source_code_point_length + 1:
            raise ValueError("source_boundary_count_mismatch")

        binding_set_identity = {
            "source_event_id": projection.source_event_id,
            "source_sha256": projection.source_sha256,
            "projection_id": projection.projection_id,
            "source_field_schema_id": projection.source_field_schema_id,
            "grammar_registry_id": selected_registry.registry_id,
            "grammar_registry_version": selected_registry.registry_version,
            "proposal_ruleset_id": selected_ruleset.ruleset_id,
            "proposal_ruleset_version": selected_ruleset.ruleset_version,
            "binding_spec_id": BINDING_SPEC_ID,
            "binding_spec_version": BINDING_SPEC_VERSION,
            "schema_version": BINDING_SCHEMA_VERSION,
            "binding_set_schema_id": (
                "aiweb-resonant-operator-candidate-binding-set-v1"
            ),
        }
        binding_set_id = stable_record_id(
            "resonant_operator_candidate_binding_set",
            binding_set_identity,
        )

        quotation_cache: dict[object, object] = {}
        candidate_rows: list[
            tuple[
                ResonantOperatorProposalRule,
                GrammarOperatorDefinition,
                tuple[tuple[int, int], ...],
            ]
        ] = []
        signal_rows: list[
            tuple[
                ResonantOperatorProposalRule,
                tuple[tuple[int, int], ...],
            ]
        ] = []

        for rule in selected_ruleset.rules:
            if not rule.enabled:
                continue
            matches = _rule_matches(
                projection,
                text,
                rule,
                quotation_cache,  # type: ignore[arg-type]
            )
            for ranges in matches:
                if not _span_supported(projection, ranges):
                    continue
                if rule.output_kind is ProposalOutputKind.OPERATOR_CANDIDATE:
                    definition = grammar_operator_for_key(
                        rule.candidate_operator_key,
                        selected_registry,
                    )
                    if definition is None:
                        raise ValueError("proposal_rule_operator_missing")
                    candidate_rows.append((rule, definition, ranges))
                else:
                    signal_rows.append((rule, ranges))

                if len(candidate_rows) > effective_limits.max_candidates:
                    return _result(
                        status=(
                            CandidateBindingStatus.
                            CANDIDATE_BINDINGS_LIMIT_EXCEEDED
                        ),
                        reason_code="candidate_binding_limit_exceeded",
                        binding_set_created=False,
                        source_preserved_in_custody=True,
                        source_event_id=projection.source_event_id,
                        source_sha256=projection.source_sha256,
                        projection_id=projection.projection_id,
                        grammar_registry_id=selected_registry.registry_id,
                        proposal_ruleset_id=selected_ruleset.ruleset_id,
                        limits=effective_limits,
                        binding_set=None,
                        validation_issue_codes=(
                            "candidate_binding_limit_exceeded",
                        ),
                    )
                if len(signal_rows) > effective_limits.max_unbound_signals:
                    return _result(
                        status=(
                            CandidateBindingStatus.
                            CANDIDATE_BINDINGS_LIMIT_EXCEEDED
                        ),
                        reason_code="unbound_signal_limit_exceeded",
                        binding_set_created=False,
                        source_preserved_in_custody=True,
                        source_event_id=projection.source_event_id,
                        source_sha256=projection.source_sha256,
                        projection_id=projection.projection_id,
                        grammar_registry_id=selected_registry.registry_id,
                        proposal_ruleset_id=selected_ruleset.ruleset_id,
                        limits=effective_limits,
                        binding_set=None,
                        validation_issue_codes=(
                            "unbound_signal_limit_exceeded",
                        ),
                    )

        candidate_rows.sort(
            key=lambda row: (
                _range_bounds(row[2]),
                row[1].operator_key,
                row[0].rule_key,
                row[0].candidate_variant_code,
            )
        )
        signal_rows.sort(
            key=lambda row: (
                _range_bounds(row[1]),
                row[0].rule_key,
            )
        )

        partial_source = (
            projection.status
            is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED
        )
        candidates: list[ResonantOperatorBindingCandidate] = []

        for rule, definition, ranges in candidate_rows:
            span_ids, cp_ranges, byte_ranges, fragments = _span_payload(
                projection,
                text,
                byte_offsets,
                ranges,
            )
            start, end = _range_bounds(ranges)
            competition_instance = (
                f"{rule.competition_group_code}:{start}:{end}"
                if rule.competition_group_code
                else ""
            )
            confidence_basis = (
                DeterministicConfidenceBasis.
                EXACT_OBSERVABLE_RULE_MATCH_HELD_BY_PARTIAL_SOURCE
                if partial_source
                else DeterministicConfidenceBasis.
                EXACT_OBSERVABLE_RULE_MATCH
            )
            support_status = (
                CandidateSupportStatus.HELD_PARTIALLY_UNSUPPORTED_SOURCE
                if partial_source
                else CandidateSupportStatus.SUPPORTED_EXACT_RULE_MATCH
            )
            missing_codes = rule.missing_prerequisite_codes
            if partial_source:
                missing_codes = tuple(
                    dict.fromkeys(
                        (
                            *missing_codes,
                            "source_field_contains_unsupported_material",
                        )
                    )
                )
            candidate = ResonantOperatorBindingCandidate(
                candidate_binding_id="",
                binding_set_id=binding_set_id,
                source_event_id=projection.source_event_id,
                projection_id=projection.projection_id,
                source_field_schema_id=projection.source_field_schema_id,
                root_source_span_id=projection.root_source_span_id,
                predecessor_field_build_result_id=(
                    projection.predecessor_field_build_result_id
                ),
                predecessor_field_envelope_id=(
                    projection.predecessor_field_envelope_id
                ),
                source_span_ids=span_ids,
                code_point_ranges=cp_ranges,
                utf8_byte_ranges=byte_ranges,
                exact_source_fragments=fragments,
                candidate_operator_key=definition.operator_key,
                candidate_operator_version=definition.operator_version,
                candidate_operator_definition_id=definition.definition_id,
                candidate_operator_family=definition.family.value,
                candidate_operator_glyph=definition.glyph,
                advisory_phase_affinity=definition.phase_affinity,
                grammar_registry_id=selected_registry.registry_id,
                grammar_registry_version=selected_registry.registry_version,
                proposal_ruleset_id=selected_ruleset.ruleset_id,
                proposal_ruleset_version=selected_ruleset.ruleset_version,
                proposal_rule_id=rule.rule_id,
                proposal_rule_key=rule.rule_key,
                proposal_rule_version=rule.rule_version,
                candidate_variant_code=rule.candidate_variant_code,
                competition_group_instance=competition_instance,
                observable_condition_codes=rule.observable_condition_codes,
                satisfied_prerequisite_codes=(
                    rule.satisfied_prerequisite_codes
                ),
                missing_prerequisite_codes=missing_codes,
                conflicting_evidence_codes=(
                    rule.conflicting_evidence_codes
                ),
                neighboring_candidate_binding_ids=(),
                compatible_neighboring_candidate_binding_ids=(),
                incompatible_neighboring_candidate_binding_ids=(),
                neighbor_compatibility_status=(
                    NeighborCompatibilityStatus.
                    UNRESOLVED_NO_COMPATIBILITY_TABLE
                ),
                competing_candidate_binding_ids=(),
                possible_parent_binding_ids=(),
                possible_child_binding_ids=(),
                confidence_basis=confidence_basis,
                support_status=support_status,
                unresolved=True,
                unsupported=partial_source,
                malformed=False,
                candidate_association_created=True,
                operator_occurrence_created=False,
                operator_application_performed=False,
                phase_assignment_performed=False,
                meaning_selected=False,
                permission_inferred=False,
                route_created=False,
                tool_routing_performed=False,
                action_performed=False,
                memory_read_performed=False,
                memory_write_performed=False,
                delivery_performed=False,
            )
            candidate = replace(
                candidate,
                candidate_binding_id=candidate.expected_id(),
            )
            candidates.append(candidate)

        rule_by_key = {rule.rule_key: rule for rule in selected_ruleset.rules}
        enriched: list[ResonantOperatorBindingCandidate] = []
        for candidate in candidates:
            rule = rule_by_key[candidate.proposal_rule_key]
            neighbors: list[str] = []
            competitors: list[str] = []
            parents: list[str] = []
            children: list[str] = []
            for other in candidates:
                if other.candidate_binding_id == candidate.candidate_binding_id:
                    continue
                if _neighboring(candidate, other, text):
                    neighbors.append(other.candidate_binding_id)
                if (
                    candidate.competition_group_instance
                    and candidate.competition_group_instance
                    == other.competition_group_instance
                ):
                    competitors.append(other.candidate_binding_id)
                if (
                    other.proposal_rule_key in rule.possible_child_rule_keys
                    and _contains(candidate, other)
                ):
                    children.append(other.candidate_binding_id)
                if (
                    other.proposal_rule_key in rule.possible_parent_rule_keys
                    and _contains(other, candidate)
                ):
                    parents.append(other.candidate_binding_id)
            enriched.append(
                replace(
                    candidate,
                    neighboring_candidate_binding_ids=tuple(sorted(neighbors)),
                    competing_candidate_binding_ids=tuple(
                        sorted(competitors)
                    ),
                    possible_parent_binding_ids=tuple(sorted(parents)),
                    possible_child_binding_ids=tuple(sorted(children)),
                    conflicting_evidence_codes=tuple(
                        dict.fromkeys(
                            (
                                *candidate.conflicting_evidence_codes,
                                *(
                                    ("materially_competing_candidate_present",)
                                    if competitors
                                    else ()
                                ),
                            )
                        )
                    ),
                )
            )

        signals: list[UnboundStructuralSignal] = []
        for rule, ranges in signal_rows:
            if rule.structural_signal_kind is None:
                raise ValueError("unbound_signal_kind_missing")
            span_ids, cp_ranges, byte_ranges, fragments = _span_payload(
                projection,
                text,
                byte_offsets,
                ranges,
            )
            signal = UnboundStructuralSignal(
                signal_id="",
                binding_set_id=binding_set_id,
                source_event_id=projection.source_event_id,
                projection_id=projection.projection_id,
                source_span_ids=span_ids,
                code_point_ranges=cp_ranges,
                utf8_byte_ranges=byte_ranges,
                exact_source_fragments=fragments,
                signal_kind=rule.structural_signal_kind,
                signal_code=rule.candidate_variant_code,
                proposal_rule_id=rule.rule_id,
                proposal_rule_key=rule.rule_key,
                proposal_rule_version=rule.rule_version,
                observable_condition_codes=rule.observable_condition_codes,
                satisfied_prerequisite_codes=(
                    rule.satisfied_prerequisite_codes
                ),
                missing_prerequisite_codes=tuple(
                    dict.fromkeys(
                        (
                            *rule.missing_prerequisite_codes,
                            *(
                                ("source_field_contains_unsupported_material",)
                                if partial_source
                                else ()
                            ),
                        )
                    )
                ),
                conflicting_evidence_codes=(
                    rule.conflicting_evidence_codes
                ),
                unresolved=True,
                unsupported=partial_source,
                malformed=False,
                operator_candidate_created=False,
                predicate_role_assigned=False,
                capability_binding_created=False,
                route_created=False,
                action_performed=False,
            )
            signal = replace(signal, signal_id=signal.expected_id())
            signals.append(signal)

        final_candidates = tuple(enriched)
        final_signals = tuple(signals)
        materially_competing_count = sum(
            bool(candidate.competing_candidate_binding_ids)
            for candidate in final_candidates
        )

        if partial_source:
            status = (
                CandidateBindingStatus.
                CANDIDATE_BINDINGS_PARTIALLY_UNSUPPORTED
            )
            reason_code = "candidate_bindings_held_partial_source"
        elif final_candidates:
            status = CandidateBindingStatus.CANDIDATE_BINDINGS_SUPPORTED
            reason_code = "candidate_bindings_created"
        else:
            status = CandidateBindingStatus.CANDIDATE_BINDINGS_NONE
            reason_code = "no_operator_candidate_rule_match"

        binding_set = ResonantOperatorCandidateBindingSet(
            binding_set_id=binding_set_id,
            source_event_id=projection.source_event_id,
            source_sha256=projection.source_sha256,
            projection_id=projection.projection_id,
            source_field_schema_id=projection.source_field_schema_id,
            grammar_registry_id=selected_registry.registry_id,
            grammar_registry_version=selected_registry.registry_version,
            proposal_ruleset_id=selected_ruleset.ruleset_id,
            proposal_ruleset_version=selected_ruleset.ruleset_version,
            status=status,
            candidates=final_candidates,
            unbound_structural_signals=final_signals,
            candidate_count=len(final_candidates),
            unbound_signal_count=len(final_signals),
            materially_competing_candidate_count=(
                materially_competing_count
            ),
            candidate_plurality_preserved=True,
            source_mapping_complete=True,
            source_ancestry_complete=True,
            structural_progression_allowed=(
                projection.structural_progression_allowed
                and not partial_source
                and bool(final_candidates)
            ),
            candidate_binding_available=True,
            operator_occurrence_available=False,
            operator_application_available=False,
            phase_assignment_available=False,
            meaning_selection_available=False,
            permission_authority_available=False,
            route_authority_available=False,
            tool_authority_available=False,
            action_authority_available=False,
            memory_authority_available=False,
            delivery_authority_available=False,
            hidden_fallback_allowed=False,
        )

        from .validation import validate_resonant_operator_candidate_binding_set

        binding_report = validate_resonant_operator_candidate_binding_set(
            binding_set,
            projection,
            selected_registry,
            selected_ruleset,
            _projection_already_validated=True,
        )
        if not binding_report.ok:
            return _result(
                status=CandidateBindingStatus.CANDIDATE_BINDINGS_FAILED,
                reason_code="constructed_binding_set_failed_validation",
                binding_set_created=False,
                source_preserved_in_custody=True,
                source_event_id=projection.source_event_id,
                source_sha256=projection.source_sha256,
                projection_id=projection.projection_id,
                grammar_registry_id=selected_registry.registry_id,
                proposal_ruleset_id=selected_ruleset.ruleset_id,
                limits=effective_limits,
                binding_set=None,
                validation_issue_codes=tuple(
                    issue.code for issue in binding_report.issues
                ),
            )

        return _result(
            status=status,
            reason_code=reason_code,
            binding_set_created=True,
            source_preserved_in_custody=True,
            source_event_id=projection.source_event_id,
            source_sha256=projection.source_sha256,
            projection_id=projection.projection_id,
            grammar_registry_id=selected_registry.registry_id,
            proposal_ruleset_id=selected_ruleset.ruleset_id,
            limits=effective_limits,
            binding_set=binding_set,
            validation_issue_codes=(),
        )
    except Exception as exc:
        return _result(
            status=CandidateBindingStatus.CANDIDATE_BINDINGS_FAILED,
            reason_code="candidate_binding_internal_failure",
            binding_set_created=False,
            source_preserved_in_custody=True,
            source_event_id=projection.source_event_id,
            source_sha256=projection.source_sha256,
            projection_id=projection.projection_id,
            grammar_registry_id=selected_registry.registry_id,
            proposal_ruleset_id=selected_ruleset.ruleset_id,
            limits=effective_limits,
            binding_set=None,
            validation_issue_codes=(type(exc).__name__,),
        )
