"""Deterministic validation for Slice 36D candidate-binding records."""

from __future__ import annotations

import hashlib

from ..input_event_custody import (
    CUSTODY_SCHEMA_VERSION,
    CUSTODY_SPEC_ID,
    CUSTODY_SPEC_VERSION,
)
from ..schema import ValidationReport, issue, stable_record_id
from ..source_field_projection import (
    SOURCE_FIELD_SCHEMA_ID,
    SourceFieldProjectionRecord,
    SourceFieldProjectionStatus,
    validate_source_field_projection,
)
from ..symbolic_grammar_operator_registry import (
    SymbolicGrammarOperatorRegistry,
    grammar_operator_for_key,
    validate_symbolic_grammar_operator_registry,
)
from .schema import (
    ABSOLUTE_MAX_BINDING_CANDIDATES,
    ABSOLUTE_MAX_UNBOUND_SIGNALS,
    BINDING_CANDIDATE_SCHEMA_ID,
    BINDING_LIMITS_SCHEMA_ID,
    BINDING_RESULT_SCHEMA_ID,
    BINDING_RULE_SCHEMA_ID,
    BINDING_RULESET_SCHEMA_ID,
    BINDING_SCHEMA_VERSION,
    BINDING_SET_SCHEMA_ID,
    BINDING_SPEC_ID,
    BINDING_SPEC_VERSION,
    EXPECTED_DEFAULT_RULE_COUNT,
    UNBOUND_SIGNAL_SCHEMA_ID,
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
    StructuralSignalKind,
    UnboundStructuralSignal,
)


def _report(issues: list[object]) -> ValidationReport:
    return ValidationReport(
        schema_version=BINDING_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def _base_issues(record: object) -> list[object]:
    issues: list[object] = []
    if getattr(record, "binding_spec_id", None) != BINDING_SPEC_ID:
        issues.append(issue("binding_spec_id", "binding_spec_id_mismatch"))
    if getattr(record, "binding_spec_version", None) != BINDING_SPEC_VERSION:
        issues.append(
            issue("binding_spec_version", "binding_spec_version_mismatch")
        )
    if getattr(record, "schema_version", None) != BINDING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    return issues


def _all_false(record: object, names: tuple[str, ...]) -> list[object]:
    issues: list[object] = []
    for name in names:
        if getattr(record, name, None) is not False:
            issues.append(issue(name, "must_remain_false"))
    return issues


def _source_text(projection: SourceFieldProjectionRecord) -> str:
    return "".join(atom.exact_text for atom in projection.code_points)


def _byte_offsets(projection: SourceFieldProjectionRecord) -> tuple[int, ...]:
    return tuple(
        boundary.utf8_byte_offset
        for boundary in sorted(projection.boundaries, key=lambda value: value.ordinal)
    )


def _expected_source_span_id(
    projection: SourceFieldProjectionRecord,
    start: int,
    end: int,
    exact_text: str,
    byte_start: int,
    byte_end: int,
) -> str:
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


def _validate_ranges(
    *,
    source_span_ids: tuple[str, ...],
    code_point_ranges: tuple[tuple[int, int], ...],
    utf8_byte_ranges: tuple[tuple[int, int], ...],
    exact_source_fragments: tuple[str, ...],
    projection: SourceFieldProjectionRecord,
) -> list[object]:
    issues: list[object] = []
    lengths = {
        len(source_span_ids),
        len(code_point_ranges),
        len(utf8_byte_ranges),
        len(exact_source_fragments),
    }
    if lengths != {len(code_point_ranges)} or not code_point_ranges:
        issues.append(issue("source_ranges", "parallel_nonempty_ranges_required"))
        return issues

    text = _source_text(projection)
    offsets = _byte_offsets(projection)
    prior_end = -1
    for index, ((start, end), (byte_start, byte_end), fragment, span_id) in enumerate(
        zip(
            code_point_ranges,
            utf8_byte_ranges,
            exact_source_fragments,
            source_span_ids,
            strict=True,
        )
    ):
        if type(start) is not int or type(end) is not int:
            issues.append(issue(f"code_point_ranges[{index}]", "integer_range_required"))
            continue
        if not 0 <= start < end <= projection.source_code_point_length:
            issues.append(issue(f"code_point_ranges[{index}]", "out_of_bounds"))
            continue
        if start < prior_end:
            issues.append(issue(f"code_point_ranges[{index}]", "ranges_not_ordered"))
        prior_end = end
        expected_fragment = text[start:end]
        if fragment != expected_fragment:
            issues.append(issue(f"exact_source_fragments[{index}]", "source_fragment_mismatch"))
        expected_bytes = (offsets[start], offsets[end])
        if (byte_start, byte_end) != expected_bytes:
            issues.append(issue(f"utf8_byte_ranges[{index}]", "utf8_range_mismatch"))
        expected_span_id = _expected_source_span_id(
            projection,
            start,
            end,
            expected_fragment,
            offsets[start],
            offsets[end],
        )
        if span_id != expected_span_id:
            issues.append(issue(f"source_span_ids[{index}]", "source_span_id_mismatch"))
    return issues


def validate_candidate_binding_limits(limits: object) -> ValidationReport:
    if type(limits) is not CandidateBindingLimits:
        return _report([issue("limits", "invalid_record_type")])
    issues = _base_issues(limits)
    if limits.limits_schema_id != BINDING_LIMITS_SCHEMA_ID:
        issues.append(issue("limits_schema_id", "limits_schema_id_mismatch"))
    if limits.limits_id != limits.expected_id():
        issues.append(issue("limits_id", "stable_identifier_mismatch"))
    if type(limits.max_candidates) is not int or not (
        0 <= limits.max_candidates <= ABSOLUTE_MAX_BINDING_CANDIDATES
    ):
        issues.append(issue("max_candidates", "invalid_limit"))
    if type(limits.max_unbound_signals) is not int or not (
        0 <= limits.max_unbound_signals <= ABSOLUTE_MAX_UNBOUND_SIGNALS
    ):
        issues.append(issue("max_unbound_signals", "invalid_limit"))
    return _report(issues)


def validate_resonant_operator_proposal_rule(
    rule: object,
    registry: object,
) -> ValidationReport:
    if type(rule) is not ResonantOperatorProposalRule:
        return _report([issue("rule", "invalid_record_type")])
    issues = _base_issues(rule)
    if rule.rule_schema_id != BINDING_RULE_SCHEMA_ID:
        issues.append(issue("rule_schema_id", "rule_schema_id_mismatch"))
    if rule.rule_id != rule.expected_id():
        issues.append(issue("rule_id", "stable_identifier_mismatch"))
    if not rule.rule_key or rule.rule_version != "1.0.0":
        issues.append(issue("rule_identity", "unsupported_or_missing"))
    if rule.enabled is not True or rule.exact_match_required is not True:
        issues.append(issue("enabled", "exact_enabled_rule_required"))
    if rule.source_span_required is not True:
        issues.append(issue("source_span_required", "must_be_true"))
    issues.extend(
        _all_false(
            rule,
            (
                "normalization_authorized",
                "casefolding_authorized",
                "tokenization_authorized",
                "phrase_frequency_authorized",
                "statistical_scoring_authorized",
                "embedding_authorized",
                "vector_similarity_authorized",
                "nearest_neighbor_authorized",
                "language_model_authorized",
                "memory_resemblance_authorized",
                "web_search_authorized",
                "hidden_parser_authorized",
                "capability_influence_authorized",
            ),
        )
    )
    if not rule.observable_condition_codes or not rule.satisfied_prerequisite_codes:
        issues.append(issue("rule_conditions", "explicit_conditions_required"))
    if not rule.missing_prerequisite_codes:
        issues.append(issue("missing_prerequisite_codes", "explicit_missing_support_required"))
    if not rule.source_authority_refs:
        issues.append(issue("source_authority_refs", "authority_trace_required"))

    payload_count = sum(
        bool(value)
        for value in (rule.exact_forms, rule.exact_sequences, rule.quotation_pairs)
    )
    if payload_count != 1:
        issues.append(issue("match_payload", "exactly_one_match_payload_required"))

    if rule.rule_kind is ProposalRuleKind.EXACT_WHOLE_UNIT and not rule.exact_forms:
        issues.append(issue("exact_forms", "required_for_rule_kind"))
    if rule.rule_kind is ProposalRuleKind.EXACT_INITIAL_SEQUENCE and not rule.exact_sequences:
        issues.append(issue("exact_sequences", "required_for_rule_kind"))
    if rule.rule_kind in {
        ProposalRuleKind.EXACT_QUOTATION_PAIR,
        ProposalRuleKind.EXACT_UNMATCHED_QUOTATION_OPEN,
    } and not rule.quotation_pairs:
        issues.append(issue("quotation_pairs", "required_for_rule_kind"))

    if type(registry) is not SymbolicGrammarOperatorRegistry:
        issues.append(issue("registry", "invalid_registry_type"))
    elif rule.output_kind is ProposalOutputKind.OPERATOR_CANDIDATE:
        if rule.structural_signal_kind is not None:
            issues.append(issue("structural_signal_kind", "must_be_none_for_operator"))
        if not rule.candidate_operator_key:
            issues.append(issue("candidate_operator_key", "required"))
        else:
            definition = grammar_operator_for_key(rule.candidate_operator_key, registry)
            if definition is None:
                issues.append(issue("candidate_operator_key", "operator_not_registered"))
            else:
                if rule.candidate_operator_version != definition.operator_version:
                    issues.append(issue("candidate_operator_version", "version_mismatch"))
                if rule.candidate_operator_definition_id != definition.definition_id:
                    issues.append(issue("candidate_operator_definition_id", "definition_id_mismatch"))
    else:
        if any(
            value is not None
            for value in (
                rule.candidate_operator_key,
                rule.candidate_operator_version,
                rule.candidate_operator_definition_id,
            )
        ):
            issues.append(issue("candidate_operator_identity", "must_be_empty_for_unbound_signal"))
        if rule.structural_signal_kind is not StructuralSignalKind.ACTION_LIKE:
            issues.append(issue("structural_signal_kind", "action_like_required"))

    return _report(issues)


def validate_resonant_operator_proposal_ruleset(
    ruleset: object,
    registry: object,
) -> ValidationReport:
    if type(ruleset) is not ResonantOperatorProposalRuleSet:
        return _report([issue("ruleset", "invalid_record_type")])
    issues = _base_issues(ruleset)
    if ruleset.ruleset_schema_id != BINDING_RULESET_SCHEMA_ID:
        issues.append(issue("ruleset_schema_id", "ruleset_schema_id_mismatch"))
    if ruleset.ruleset_id != ruleset.expected_id():
        issues.append(issue("ruleset_id", "stable_identifier_mismatch"))
    if ruleset.ruleset_version != "1.0.0":
        issues.append(issue("ruleset_version", "unsupported_version"))
    if type(registry) is not SymbolicGrammarOperatorRegistry:
        issues.append(issue("registry", "invalid_registry_type"))
    else:
        registry_report = validate_symbolic_grammar_operator_registry(registry)
        if not registry_report.ok:
            issues.append(issue("registry", "registry_validation_failed"))
        if ruleset.grammar_registry_id != registry.registry_id:
            issues.append(issue("grammar_registry_id", "registry_id_mismatch"))
        if ruleset.grammar_registry_version != registry.registry_version:
            issues.append(issue("grammar_registry_version", "registry_version_mismatch"))
    if ruleset.exact_rule_count != len(ruleset.rules):
        issues.append(issue("exact_rule_count", "rule_count_mismatch"))
    if ruleset.exact_rule_count != EXPECTED_DEFAULT_RULE_COUNT:
        issues.append(issue("exact_rule_count", "unexpected_closed_rule_count"))
    if not ruleset.closed_world or not ruleset.deterministic_only:
        issues.append(issue("ruleset_mode", "closed_deterministic_ruleset_required"))
    issues.extend(
        _all_false(
            ruleset,
            (
                "rule_order_selects_winner",
                "automatic_activation_authorized",
                "operator_application_authorized",
                "phase_assignment_authorized",
                "meaning_selection_authorized",
                "permission_authorized",
                "route_authorized",
                "action_authorized",
                "hidden_fallback_allowed",
            ),
        )
    )
    rule_ids = tuple(rule.rule_id for rule in ruleset.rules)
    rule_keys = tuple(rule.rule_key for rule in ruleset.rules)
    if len(set(rule_ids)) != len(rule_ids) or len(set(rule_keys)) != len(rule_keys):
        issues.append(issue("rules", "duplicate_rule_identity"))
    for index, rule in enumerate(ruleset.rules):
        report = validate_resonant_operator_proposal_rule(rule, registry)
        if not report.ok:
            issues.append(issue(f"rules[{index}]", "rule_validation_failed"))
    valid_keys = set(rule_keys)
    for index, rule in enumerate(ruleset.rules):
        if not set(rule.possible_parent_rule_keys).issubset(valid_keys):
            issues.append(issue(f"rules[{index}].possible_parent_rule_keys", "unknown_rule_key"))
        if not set(rule.possible_child_rule_keys).issubset(valid_keys):
            issues.append(issue(f"rules[{index}].possible_child_rule_keys", "unknown_rule_key"))
    return _report(issues)


def validate_resonant_operator_binding_candidate(
    candidate: object,
    projection: object,
    registry: object,
    ruleset: object,
) -> ValidationReport:
    if type(candidate) is not ResonantOperatorBindingCandidate:
        return _report([issue("candidate", "invalid_record_type")])
    issues = _base_issues(candidate)
    if candidate.candidate_schema_id != BINDING_CANDIDATE_SCHEMA_ID:
        issues.append(issue("candidate_schema_id", "candidate_schema_id_mismatch"))
    if candidate.candidate_binding_id != candidate.expected_id():
        issues.append(issue("candidate_binding_id", "stable_identifier_mismatch"))
    if type(projection) is not SourceFieldProjectionRecord:
        issues.append(issue("projection", "invalid_projection_type"))
        return _report(issues)
    if candidate.source_event_id != projection.source_event_id:
        issues.append(issue("source_event_id", "source_event_mismatch"))
    if candidate.projection_id != projection.projection_id:
        issues.append(issue("projection_id", "projection_mismatch"))
    if candidate.source_field_schema_id != SOURCE_FIELD_SCHEMA_ID:
        issues.append(issue("source_field_schema_id", "source_field_schema_mismatch"))
    if candidate.root_source_span_id != projection.root_source_span_id:
        issues.append(issue("root_source_span_id", "root_span_mismatch"))
    if candidate.predecessor_field_build_result_id != projection.predecessor_field_build_result_id:
        issues.append(issue("predecessor_field_build_result_id", "ancestry_mismatch"))
    if candidate.predecessor_field_envelope_id != projection.predecessor_field_envelope_id:
        issues.append(issue("predecessor_field_envelope_id", "ancestry_mismatch"))
    issues.extend(
        _validate_ranges(
            source_span_ids=candidate.source_span_ids,
            code_point_ranges=candidate.code_point_ranges,
            utf8_byte_ranges=candidate.utf8_byte_ranges,
            exact_source_fragments=candidate.exact_source_fragments,
            projection=projection,
        )
    )
    if type(registry) is not SymbolicGrammarOperatorRegistry:
        issues.append(issue("registry", "invalid_registry_type"))
    else:
        if candidate.grammar_registry_id != registry.registry_id:
            issues.append(issue("grammar_registry_id", "registry_id_mismatch"))
        definition = grammar_operator_for_key(candidate.candidate_operator_key, registry)
        if definition is None:
            issues.append(issue("candidate_operator_key", "operator_not_registered"))
        else:
            expected = (
                definition.operator_version,
                definition.definition_id,
                definition.family.value,
                definition.glyph,
                definition.phase_affinity,
            )
            actual = (
                candidate.candidate_operator_version,
                candidate.candidate_operator_definition_id,
                candidate.candidate_operator_family,
                candidate.candidate_operator_glyph,
                candidate.advisory_phase_affinity,
            )
            if actual != expected:
                issues.append(issue("candidate_operator_identity", "registry_contract_mismatch"))
    if type(ruleset) is not ResonantOperatorProposalRuleSet:
        issues.append(issue("ruleset", "invalid_ruleset_type"))
    else:
        if candidate.proposal_ruleset_id != ruleset.ruleset_id:
            issues.append(issue("proposal_ruleset_id", "ruleset_id_mismatch"))
        matching = tuple(rule for rule in ruleset.rules if rule.rule_id == candidate.proposal_rule_id)
        if len(matching) != 1:
            issues.append(issue("proposal_rule_id", "rule_not_found"))
        else:
            rule = matching[0]
            if rule.output_kind is not ProposalOutputKind.OPERATOR_CANDIDATE:
                issues.append(issue("proposal_rule_id", "rule_does_not_produce_operator_candidate"))
            if (
                candidate.proposal_rule_key,
                candidate.proposal_rule_version,
                candidate.candidate_variant_code,
            ) != (rule.rule_key, rule.rule_version, rule.candidate_variant_code):
                issues.append(issue("proposal_rule_identity", "rule_identity_mismatch"))
            if candidate.observable_condition_codes != rule.observable_condition_codes:
                issues.append(issue("observable_condition_codes", "rule_conditions_mismatch"))
            if candidate.satisfied_prerequisite_codes != rule.satisfied_prerequisite_codes:
                issues.append(issue("satisfied_prerequisite_codes", "rule_prerequisites_mismatch"))
    if candidate.neighbor_compatibility_status is not NeighborCompatibilityStatus.UNRESOLVED_NO_COMPATIBILITY_TABLE:
        issues.append(issue("neighbor_compatibility_status", "compatibility_table_not_installed"))
    if candidate.compatible_neighboring_candidate_binding_ids or candidate.incompatible_neighboring_candidate_binding_ids:
        issues.append(issue("neighbor_compatibility", "must_remain_unresolved"))
    if candidate.unresolved is not True or candidate.malformed is not False:
        issues.append(issue("candidate_state", "candidate_must_remain_unresolved_and_well_formed"))
    partial = projection.status is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED
    expected_confidence = (
        DeterministicConfidenceBasis.EXACT_OBSERVABLE_RULE_MATCH_HELD_BY_PARTIAL_SOURCE
        if partial
        else DeterministicConfidenceBasis.EXACT_OBSERVABLE_RULE_MATCH
    )
    expected_support = (
        CandidateSupportStatus.HELD_PARTIALLY_UNSUPPORTED_SOURCE
        if partial
        else CandidateSupportStatus.SUPPORTED_EXACT_RULE_MATCH
    )
    if candidate.confidence_basis is not expected_confidence:
        issues.append(issue("confidence_basis", "deterministic_basis_mismatch"))
    if candidate.support_status is not expected_support or candidate.unsupported is not partial:
        issues.append(issue("support_status", "source_support_status_mismatch"))
    if candidate.candidate_association_created is not True:
        issues.append(issue("candidate_association_created", "must_be_true"))
    issues.extend(
        _all_false(
            candidate,
            (
                "operator_occurrence_created",
                "operator_application_performed",
                "phase_assignment_performed",
                "meaning_selected",
                "permission_inferred",
                "route_created",
                "tool_routing_performed",
                "action_performed",
                "memory_read_performed",
                "memory_write_performed",
                "delivery_performed",
            ),
        )
    )
    return _report(issues)


def validate_unbound_structural_signal(
    signal: object,
    projection: object,
    ruleset: object,
) -> ValidationReport:
    if type(signal) is not UnboundStructuralSignal:
        return _report([issue("signal", "invalid_record_type")])
    issues = _base_issues(signal)
    if signal.signal_schema_id != UNBOUND_SIGNAL_SCHEMA_ID:
        issues.append(issue("signal_schema_id", "signal_schema_id_mismatch"))
    if signal.signal_id != signal.expected_id():
        issues.append(issue("signal_id", "stable_identifier_mismatch"))
    if type(projection) is not SourceFieldProjectionRecord:
        issues.append(issue("projection", "invalid_projection_type"))
        return _report(issues)
    if signal.source_event_id != projection.source_event_id or signal.projection_id != projection.projection_id:
        issues.append(issue("source_ancestry", "source_ancestry_mismatch"))
    issues.extend(
        _validate_ranges(
            source_span_ids=signal.source_span_ids,
            code_point_ranges=signal.code_point_ranges,
            utf8_byte_ranges=signal.utf8_byte_ranges,
            exact_source_fragments=signal.exact_source_fragments,
            projection=projection,
        )
    )
    if signal.signal_kind is not StructuralSignalKind.ACTION_LIKE:
        issues.append(issue("signal_kind", "unsupported_signal_kind"))
    if type(ruleset) is not ResonantOperatorProposalRuleSet:
        issues.append(issue("ruleset", "invalid_ruleset_type"))
    else:
        matching = tuple(rule for rule in ruleset.rules if rule.rule_id == signal.proposal_rule_id)
        if len(matching) != 1:
            issues.append(issue("proposal_rule_id", "rule_not_found"))
        else:
            rule = matching[0]
            if rule.output_kind is not ProposalOutputKind.UNBOUND_STRUCTURAL_SIGNAL:
                issues.append(issue("proposal_rule_id", "rule_does_not_produce_unbound_signal"))
            if signal.proposal_rule_key != rule.rule_key or signal.signal_code != rule.candidate_variant_code:
                issues.append(issue("proposal_rule_identity", "rule_identity_mismatch"))
    if signal.unresolved is not True or signal.malformed is not False:
        issues.append(issue("signal_state", "signal_must_remain_unresolved"))
    issues.extend(
        _all_false(
            signal,
            (
                "operator_candidate_created",
                "predicate_role_assigned",
                "capability_binding_created",
                "route_created",
                "action_performed",
            ),
        )
    )
    return _report(issues)


def validate_resonant_operator_candidate_binding_set(
    binding_set: object,
    projection: object,
    registry: object,
    ruleset: object,
    *,
    _projection_already_validated: bool = False,
) -> ValidationReport:
    if type(binding_set) is not ResonantOperatorCandidateBindingSet:
        return _report([issue("binding_set", "invalid_record_type")])
    issues = _base_issues(binding_set)
    if binding_set.binding_set_schema_id != BINDING_SET_SCHEMA_ID:
        issues.append(issue("binding_set_schema_id", "binding_set_schema_id_mismatch"))
    if binding_set.binding_set_id != binding_set.expected_id():
        issues.append(issue("binding_set_id", "stable_identifier_mismatch"))
    if type(projection) is not SourceFieldProjectionRecord:
        issues.append(issue("projection", "invalid_projection_type"))
        return _report(issues)
    if not _projection_already_validated:
        projection_report = validate_source_field_projection(projection)
        if not projection_report.ok:
            issues.append(issue("projection", "projection_validation_failed"))
    if (
        binding_set.source_event_id,
        binding_set.source_sha256,
        binding_set.projection_id,
        binding_set.source_field_schema_id,
    ) != (
        projection.source_event_id,
        projection.source_sha256,
        projection.projection_id,
        projection.source_field_schema_id,
    ):
        issues.append(issue("source_ancestry", "source_ancestry_mismatch"))
    if binding_set.candidate_count != len(binding_set.candidates):
        issues.append(issue("candidate_count", "candidate_count_mismatch"))
    if binding_set.unbound_signal_count != len(binding_set.unbound_structural_signals):
        issues.append(issue("unbound_signal_count", "signal_count_mismatch"))
    candidate_ids = tuple(value.candidate_binding_id for value in binding_set.candidates)
    if len(set(candidate_ids)) != len(candidate_ids):
        issues.append(issue("candidates", "duplicate_candidate_identity"))
    signal_ids = tuple(value.signal_id for value in binding_set.unbound_structural_signals)
    if len(set(signal_ids)) != len(signal_ids):
        issues.append(issue("unbound_structural_signals", "duplicate_signal_identity"))
    candidate_id_set = set(candidate_ids)
    for index, candidate in enumerate(binding_set.candidates):
        if candidate.binding_set_id != binding_set.binding_set_id:
            issues.append(issue(f"candidates[{index}].binding_set_id", "binding_set_mismatch"))
        report = validate_resonant_operator_binding_candidate(candidate, projection, registry, ruleset)
        if not report.ok:
            issues.append(issue(f"candidates[{index}]", "candidate_validation_failed"))
        for field_name in (
            "neighboring_candidate_binding_ids",
            "competing_candidate_binding_ids",
            "possible_parent_binding_ids",
            "possible_child_binding_ids",
        ):
            values = set(getattr(candidate, field_name))
            if candidate.candidate_binding_id in values or not values.issubset(candidate_id_set):
                issues.append(issue(f"candidates[{index}].{field_name}", "invalid_candidate_reference"))
    for index, signal in enumerate(binding_set.unbound_structural_signals):
        if signal.binding_set_id != binding_set.binding_set_id:
            issues.append(issue(f"signals[{index}].binding_set_id", "binding_set_mismatch"))
        report = validate_unbound_structural_signal(signal, projection, ruleset)
        if not report.ok:
            issues.append(issue(f"signals[{index}]", "signal_validation_failed"))
    expected_competing = sum(bool(value.competing_candidate_binding_ids) for value in binding_set.candidates)
    if binding_set.materially_competing_candidate_count != expected_competing:
        issues.append(issue("materially_competing_candidate_count", "competition_count_mismatch"))
    if binding_set.candidate_plurality_preserved is not True:
        issues.append(issue("candidate_plurality_preserved", "must_be_true"))
    if binding_set.source_mapping_complete is not True or binding_set.source_ancestry_complete is not True:
        issues.append(issue("source_mapping", "complete_source_mapping_required"))
    if binding_set.candidate_binding_available is not True:
        issues.append(issue("candidate_binding_available", "must_be_true"))
    issues.extend(
        _all_false(
            binding_set,
            (
                "operator_occurrence_available",
                "operator_application_available",
                "phase_assignment_available",
                "meaning_selection_available",
                "permission_authority_available",
                "route_authority_available",
                "tool_authority_available",
                "action_authority_available",
                "memory_authority_available",
                "delivery_authority_available",
                "hidden_fallback_allowed",
            ),
        )
    )
    partial = projection.status is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED
    expected_status = (
        CandidateBindingStatus.CANDIDATE_BINDINGS_PARTIALLY_UNSUPPORTED
        if partial
        else (
            CandidateBindingStatus.CANDIDATE_BINDINGS_SUPPORTED
            if binding_set.candidates
            else CandidateBindingStatus.CANDIDATE_BINDINGS_NONE
        )
    )
    if binding_set.status is not expected_status:
        issues.append(issue("status", "binding_set_status_mismatch"))
    expected_progress = (
        projection.structural_progression_allowed
        and not partial
        and bool(binding_set.candidates)
    )
    if binding_set.structural_progression_allowed is not expected_progress:
        issues.append(issue("structural_progression_allowed", "progression_status_mismatch"))
    return _report(issues)


def validate_resonant_operator_candidate_binding_result(
    result: object,
    projection: object | None = None,
    registry: object | None = None,
    ruleset: object | None = None,
) -> ValidationReport:
    if type(result) is not ResonantOperatorCandidateBindingResult:
        return _report([issue("result", "invalid_record_type")])
    issues = _base_issues(result)
    if result.result_schema_id != BINDING_RESULT_SCHEMA_ID:
        issues.append(issue("result_schema_id", "result_schema_id_mismatch"))
    if result.result_id != result.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))
    issues.extend(
        _all_false(
            result,
            (
                "filesystem_read_performed",
                "filesystem_write_performed",
                "network_access_performed",
                "environment_access_performed",
                "memory_read_performed",
                "memory_write_performed",
                "route_registration_performed",
                "tool_routing_performed",
                "operator_application_performed",
                "phase_assignment_performed",
                "meaning_selected",
                "permission_inferred",
                "action_performed",
                "delivery_performed",
            ),
        )
    )
    if result.limits is not None and not validate_candidate_binding_limits(result.limits).ok:
        issues.append(issue("limits", "limits_validation_failed"))
    if result.binding_set_created:
        if result.binding_set is None:
            issues.append(issue("binding_set", "binding_set_required"))
        elif projection is not None and registry is not None and ruleset is not None:
            report = validate_resonant_operator_candidate_binding_set(
                result.binding_set,
                projection,
                registry,
                ruleset,
            )
            if not report.ok:
                issues.append(issue("binding_set", "binding_set_validation_failed"))
        if result.binding_set is not None and result.status is not result.binding_set.status:
            issues.append(issue("status", "result_binding_set_status_mismatch"))
    elif result.binding_set is not None:
        issues.append(issue("binding_set", "must_be_none_when_not_created"))
    return _report(issues)
