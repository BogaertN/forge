"""Deterministic validators for Slice 36F records."""

from __future__ import annotations

from collections.abc import Iterable

from ..candidate_resonant_phase_trail import (
    CandidateResonantPhaseTrailResult,
    validate_candidate_resonant_phase_trail_result,
)
from ..resonant_operator_candidate_binding import (
    ResonantOperatorCandidateBindingResult,
    build_default_resonant_operator_proposal_ruleset,
    validate_resonant_operator_candidate_binding_result,
)
from ..schema import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    issue,
)
from ..source_field_projection import (
    SourceFieldProjectionResult,
    validate_source_field_projection_result,
)
from ..symbolic_grammar_operator_registry import (
    build_default_symbolic_grammar_operator_registry,
)
from .rules import (
    authority_conversion_guards,
    build_default_scope_attachment_rules,
)
from .schema import (
    ABSOLUTE_MAX_ACTIVE_CONTEXT_ENTRIES,
    ABSOLUTE_MAX_GOVERNED_SPANS_PER_OCCURRENCE,
    ABSOLUTE_MAX_REFERENCE_CANDIDATES,
    ABSOLUTE_MAX_SCOPE_OCCURRENCES,
    ACTIVE_CONTEXT_ENTRY_SCHEMA_ID,
    ACTIVE_CONTEXT_REGISTRY_SCHEMA_ID,
    CONSTRAINED_TRAIL_SCHEMA_ID,
    CONSTRAINT_RESULT_SCHEMA_ID,
    CONSTRAINT_SET_SCHEMA_ID,
    GOVERNED_SPAN_SCHEMA_ID,
    REFERENCE_ANALYSIS_SCHEMA_ID,
    REFERENCE_CANDIDATE_SCHEMA_ID,
    SCOPE_CONSTRAINT_SCHEMA_VERSION,
    SCOPE_CONSTRAINT_SPEC_ID,
    SCOPE_CONSTRAINT_SPEC_VERSION,
    SCOPE_LIMITS_SCHEMA_ID,
    SCOPE_OCCURRENCE_SCHEMA_ID,
    SCOPE_POLICY_SCHEMA_ID,
    SCOPE_RULE_SCHEMA_ID,
    ActiveContextEntry,
    ActiveContextRegistry,
    AttachmentStatus,
    GovernedSpanCandidate,
    ReferenceAnalysis,
    ReferenceAnalysisStatus,
    ReferenceContextCandidate,
    ScopeAttachmentOccurrence,
    ScopeAttachmentReferenceConstraintResult,
    ScopeAttachmentReferenceConstraintSet,
    ScopeAttachmentRule,
    ScopeConstraintLimits,
    ScopeConstraintPolicy,
    ScopeConstrainedCandidateTrail,
)


def _report(issues: Iterable[ValidationIssue]) -> ValidationReport:
    values = tuple(issues)
    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not values,
        issues=values,
    )


def _required_text(
    issues: list[ValidationIssue],
    field: str,
    value: object,
) -> None:
    if not isinstance(value, str) or not value:
        issues.append(issue(field, "required_non_empty_text"))


def _unique_text(
    issues: list[ValidationIssue],
    field: str,
    value: object,
    *,
    allow_empty: bool = True,
) -> None:
    if not isinstance(value, tuple):
        issues.append(issue(field, "must_be_tuple"))
        return
    if not allow_empty and not value:
        issues.append(issue(field, "required_non_empty_tuple"))
    if any(not isinstance(item, str) or not item for item in value):
        issues.append(issue(field, "invalid_text_tuple"))
    if len(value) != len(set(value)):
        issues.append(issue(field, "duplicate_values"))


def _must_false(
    issues: list[ValidationIssue],
    obj: object,
    names: tuple[str, ...],
) -> None:
    for name in names:
        if getattr(obj, name, None) is not False:
            issues.append(issue(name, "must_remain_false"))


def _must_true(
    issues: list[ValidationIssue],
    obj: object,
    names: tuple[str, ...],
) -> None:
    for name in names:
        if getattr(obj, name, None) is not True:
            issues.append(issue(name, "must_remain_true"))


def _common_identity(
    issues: list[ValidationIssue],
    obj: object,
    schema_id_field: str,
    expected_schema_id: str,
) -> None:
    if getattr(obj, "scope_constraint_spec_id", None) != SCOPE_CONSTRAINT_SPEC_ID:
        issues.append(issue("scope_constraint_spec_id", "unexpected_value"))
    if (
        getattr(obj, "scope_constraint_spec_version", None)
        != SCOPE_CONSTRAINT_SPEC_VERSION
    ):
        issues.append(
            issue("scope_constraint_spec_version", "unexpected_value")
        )
    if getattr(obj, "schema_version", None) != SCOPE_CONSTRAINT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unexpected_value"))
    if getattr(obj, schema_id_field, None) != expected_schema_id:
        issues.append(issue(schema_id_field, "unexpected_value"))


def validate_scope_constraint_policy(
    policy: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(policy) is not ScopeConstraintPolicy:
        return _report((issue("policy", "invalid_type"),))

    if policy.policy_id != policy.expected_id():
        issues.append(issue("policy_id", "stable_id_mismatch"))

    _common_identity(
        issues,
        policy,
        "policy_schema_id",
        SCOPE_POLICY_SCHEMA_ID,
    )
    _must_true(
        issues,
        policy,
        (
            "explicit_context_only",
            "active_context_must_be_immutable",
            "exact_reference_match_only",
            "preserve_all_lawful_attachments",
        ),
    )
    _must_false(
        issues,
        policy,
        (
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
        ),
    )

    if policy.false_authority_conversions != authority_conversion_guards():
        issues.append(
            issue(
                "false_authority_conversions",
                "complete_guard_set_required",
            )
        )

    return _report(issues)


def validate_scope_constraint_limits(
    limits: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(limits) is not ScopeConstraintLimits:
        return _report((issue("limits", "invalid_type"),))

    if limits.limits_id != limits.expected_id():
        issues.append(issue("limits_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        limits,
        "limits_schema_id",
        SCOPE_LIMITS_SCHEMA_ID,
    )

    values = (
        (
            "max_scope_occurrences",
            limits.max_scope_occurrences,
            True,
            ABSOLUTE_MAX_SCOPE_OCCURRENCES,
        ),
        (
            "max_governed_spans_per_occurrence",
            limits.max_governed_spans_per_occurrence,
            False,
            ABSOLUTE_MAX_GOVERNED_SPANS_PER_OCCURRENCE,
        ),
        (
            "max_active_context_entries",
            limits.max_active_context_entries,
            True,
            ABSOLUTE_MAX_ACTIVE_CONTEXT_ENTRIES,
        ),
        (
            "max_reference_candidates",
            limits.max_reference_candidates,
            True,
            ABSOLUTE_MAX_REFERENCE_CANDIDATES,
        ),
    )
    for name, value, allow_zero, maximum in values:
        minimum = 0 if allow_zero else 1
        if (
            type(value) is not int
            or value < minimum
            or value > maximum
        ):
            issues.append(issue(name, "invalid_limit"))

    return _report(issues)


def validate_scope_attachment_rule(
    rule: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(rule) is not ScopeAttachmentRule:
        return _report((issue("rule", "invalid_type"),))

    if rule.rule_id != rule.expected_id():
        issues.append(issue("rule_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        rule,
        "rule_schema_id",
        SCOPE_RULE_SCHEMA_ID,
    )
    _required_text(issues, "rule_key", rule.rule_key)
    _required_text(issues, "rule_version", rule.rule_version)
    _unique_text(issues, "operator_keys", rule.operator_keys)
    _unique_text(issues, "operator_families", rule.operator_families)
    _unique_text(
        issues,
        "candidate_variant_codes",
        rule.candidate_variant_codes,
    )
    _must_true(
        issues,
        rule,
        (
            "exact_source_span_required",
            "preserve_multiple_attachments",
            "possible_parent_links_preserved",
            "possible_child_links_preserved",
            "no_semantic_selection",
            "no_authority_conversion",
        ),
    )

    return _report(issues)


def validate_default_scope_attachment_rules() -> ValidationReport:
    issues: list[ValidationIssue] = []
    rules = build_default_scope_attachment_rules()

    if len(rules) != 21:
        issues.append(issue("rules", "exact_rule_count_mismatch"))

    if len({rule.rule_id for rule in rules}) != len(rules):
        issues.append(issue("rules", "duplicate_rule_id"))
    if len({rule.rule_key for rule in rules}) != len(rules):
        issues.append(issue("rules", "duplicate_rule_key"))

    for index, rule in enumerate(rules):
        report = validate_scope_attachment_rule(rule)
        for value in report.issues:
            issues.append(
                issue(
                    f"rules[{index}].{value.field}",
                    value.code,
                    value.detail,
                )
            )

    return _report(issues)


def validate_active_context_entry(
    entry: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(entry) is not ActiveContextEntry:
        return _report((issue("entry", "invalid_type"),))

    if entry.entry_id != entry.expected_id():
        issues.append(issue("entry_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        entry,
        "entry_schema_id",
        ACTIVE_CONTEXT_ENTRY_SCHEMA_ID,
    )
    _required_text(
        issues,
        "context_object_id",
        entry.context_object_id,
    )
    _unique_text(
        issues,
        "exact_identifiers",
        entry.exact_identifiers,
    )
    _unique_text(
        issues,
        "exact_reference_forms",
        entry.exact_reference_forms,
    )
    _unique_text(
        issues,
        "source_event_ids",
        entry.source_event_ids,
    )
    if entry.ordinal is not None and (
        type(entry.ordinal) is not int or entry.ordinal < 1
    ):
        issues.append(issue("ordinal", "invalid_ordinal"))
    if len(entry.position_tags) != len(set(entry.position_tags)):
        issues.append(issue("position_tags", "duplicate_values"))

    _must_true(issues, entry, ("caller_supplied", "immutable"))
    _must_false(
        issues,
        entry,
        (
            "concept_identity_assigned",
            "predicate_role_assigned",
            "capability_binding_created",
            "release_authorized",
        ),
    )

    return _report(issues)


def validate_active_context_registry(
    registry: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(registry) is not ActiveContextRegistry:
        return _report((issue("active_context_registry", "invalid_type"),))

    if registry.registry_id != registry.expected_id():
        issues.append(issue("registry_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        registry,
        "registry_schema_id",
        ACTIVE_CONTEXT_REGISTRY_SCHEMA_ID,
    )
    if registry.exact_entry_count != len(registry.entries):
        issues.append(issue("exact_entry_count", "count_mismatch"))
    if len({entry.entry_id for entry in registry.entries}) != len(
        registry.entries
    ):
        issues.append(issue("entries", "duplicate_entry_id"))

    _must_true(
        issues,
        registry,
        (
            "explicit_only",
            "immutable",
            "closed_world_for_this_analysis",
        ),
    )
    _must_false(
        issues,
        registry,
        (
            "automatic_memory_search",
            "automatic_file_search",
            "automatic_repository_history_search",
            "automatic_web_search",
            "similarity_search",
            "nearest_object_fallback",
            "capability_influence",
        ),
    )

    for index, entry in enumerate(registry.entries):
        report = validate_active_context_entry(entry)
        for value in report.issues:
            issues.append(
                issue(
                    f"entries[{index}].{value.field}",
                    value.code,
                    value.detail,
                )
            )

    return _report(issues)


def validate_governed_span_candidate(
    span: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(span) is not GovernedSpanCandidate:
        return _report((issue("governed_span", "invalid_type"),))

    if span.governed_span_id != span.expected_id():
        issues.append(issue("governed_span_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        span,
        "governed_span_schema_id",
        GOVERNED_SPAN_SCHEMA_ID,
    )
    _unique_text(
        issues,
        "source_span_ids",
        span.source_span_ids,
        allow_empty=False,
    )
    if not span.code_point_ranges:
        issues.append(issue("code_point_ranges", "required_non_empty_tuple"))
    if not span.utf8_byte_ranges:
        issues.append(issue("utf8_byte_ranges", "required_non_empty_tuple"))
    if not span.exact_source_fragments:
        issues.append(
            issue("exact_source_fragments", "required_non_empty_tuple")
        )
    _must_true(issues, span, ("candidate_only",))
    _must_false(
        issues,
        span,
        (
            "selected",
            "concept_meaning_created",
            "predicate_role_assigned",
        ),
    )

    return _report(issues)


def validate_scope_attachment_occurrence(
    occurrence: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(occurrence) is not ScopeAttachmentOccurrence:
        return _report((issue("scope_occurrence", "invalid_type"),))

    if occurrence.occurrence_id != occurrence.expected_id():
        issues.append(issue("occurrence_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        occurrence,
        "occurrence_schema_id",
        SCOPE_OCCURRENCE_SCHEMA_ID,
    )
    _unique_text(
        issues,
        "exact_source_span_ids",
        occurrence.exact_source_span_ids,
        allow_empty=False,
    )

    expected_flags = {
        AttachmentStatus.SINGULAR_ATTACHMENT: (
            True,
            False,
            False,
            False,
            False,
        ),
        AttachmentStatus.MULTIPLE_ATTACHMENTS: (
            False,
            True,
            False,
            False,
            False,
        ),
        AttachmentStatus.MALFORMED_ATTACHMENT: (
            False,
            False,
            True,
            False,
            False,
        ),
        AttachmentStatus.UNSUPPORTED_ATTACHMENT: (
            False,
            False,
            False,
            True,
            False,
        ),
        AttachmentStatus.UNRESOLVED_ATTACHMENT: (
            False,
            False,
            False,
            False,
            True,
        ),
    }[occurrence.attachment_status]

    actual_flags = (
        occurrence.singular_attachment,
        occurrence.multiple_attachment,
        occurrence.malformed_attachment,
        occurrence.unsupported_attachment,
        occurrence.unresolved_attachment,
    )
    if actual_flags != expected_flags:
        issues.append(issue("attachment_status", "status_flag_mismatch"))

    if occurrence.singular_attachment and len(
        occurrence.possible_governed_spans
    ) != 1:
        issues.append(issue("possible_governed_spans", "singular_count_mismatch"))
    if occurrence.multiple_attachment and len(
        occurrence.possible_governed_spans
    ) < 2:
        issues.append(issue("possible_governed_spans", "multiple_count_mismatch"))

    if occurrence.authority_guard_codes != authority_conversion_guards():
        issues.append(
            issue("authority_guard_codes", "complete_guard_set_required")
        )

    for index, span in enumerate(occurrence.possible_governed_spans):
        report = validate_governed_span_candidate(span)
        for value in report.issues:
            issues.append(
                issue(
                    f"possible_governed_spans[{index}].{value.field}",
                    value.code,
                    value.detail,
                )
            )

    if occurrence.selected_attachment_id is not None:
        issues.append(issue("selected_attachment_id", "must_remain_none"))

    _must_false(
        issues,
        occurrence,
        (
            "original_trail_mutated",
            "selected_meaning",
            "permission_inferred",
            "capability_authorized",
            "route_created",
            "tool_routing_performed",
            "memory_read_performed",
            "memory_write_performed",
            "action_performed",
            "delivery_performed",
            "release_authorized",
        ),
    )

    return _report(issues)


def validate_reference_context_candidate(
    candidate: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(candidate) is not ReferenceContextCandidate:
        return _report((issue("reference_candidate", "invalid_type"),))

    if candidate.reference_candidate_id != candidate.expected_id():
        issues.append(issue("reference_candidate_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        candidate,
        "reference_candidate_schema_id",
        REFERENCE_CANDIDATE_SCHEMA_ID,
    )
    _must_true(issues, candidate, ("candidate_only",))
    _must_false(
        issues,
        candidate,
        (
            "selected",
            "reference_resolved",
            "concept_meaning_created",
            "predicate_role_assigned",
            "capability_binding_created",
        ),
    )

    return _report(issues)


def validate_reference_analysis(
    analysis: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(analysis) is not ReferenceAnalysis:
        return _report((issue("reference_analysis", "invalid_type"),))

    if analysis.analysis_id != analysis.expected_id():
        issues.append(issue("analysis_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        analysis,
        "reference_analysis_schema_id",
        REFERENCE_ANALYSIS_SCHEMA_ID,
    )
    if analysis.candidate_count != len(analysis.candidates):
        issues.append(issue("candidate_count", "count_mismatch"))

    expected_count_rules = {
        ReferenceAnalysisStatus.ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE: (
            lambda count: count == 1
        ),
        ReferenceAnalysisStatus.MULTIPLE_REFERENCE_CANDIDATES: (
            lambda count: count > 1
        ),
        ReferenceAnalysisStatus.UNRESOLVED_REFERENCE: (
            lambda count: count == 0
        ),
        ReferenceAnalysisStatus.UNSUPPORTED_REFERENCE_FORM: (
            lambda count: count == 0
        ),
        ReferenceAnalysisStatus.MISSING_CONTEXT_REFERENCE: (
            lambda count: count == 0
        ),
        ReferenceAnalysisStatus.PROHIBITED_CONTEXT_DEPENDENCY: (
            lambda count: count == 0
        ),
    }
    if not expected_count_rules[analysis.status](analysis.candidate_count):
        issues.append(issue("status", "candidate_count_status_mismatch"))

    if analysis.multiple_candidates_preserved != (
        analysis.candidate_count > 1
    ):
        issues.append(issue("multiple_candidates_preserved", "flag_mismatch"))

    if analysis.selected_context_entry_id is not None:
        issues.append(
            issue("selected_context_entry_id", "must_remain_none")
        )

    _must_false(
        issues,
        analysis,
        (
            "reference_resolved",
            "concept_meaning_created",
            "predicate_role_assigned",
            "capability_binding_created",
            "memory_search_performed",
            "file_search_performed",
            "repository_history_search_performed",
            "web_search_performed",
            "embedding_performed",
            "language_model_used",
            "similarity_search_performed",
        ),
    )

    for index, candidate in enumerate(analysis.candidates):
        report = validate_reference_context_candidate(candidate)
        for value in report.issues:
            issues.append(
                issue(
                    f"candidates[{index}].{value.field}",
                    value.code,
                    value.detail,
                )
            )

    return _report(issues)


def validate_scope_constrained_candidate_trail(
    trail: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(trail) is not ScopeConstrainedCandidateTrail:
        return _report((issue("constrained_trail", "invalid_type"),))

    if trail.constrained_trail_id != trail.expected_id():
        issues.append(issue("constrained_trail_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        trail,
        "constrained_trail_schema_id",
        CONSTRAINED_TRAIL_SCHEMA_ID,
    )
    if trail.scope_occurrence_count != len(trail.scope_occurrences):
        issues.append(issue("scope_occurrence_count", "count_mismatch"))
    if trail.reference_analysis_count != len(trail.reference_analyses):
        issues.append(issue("reference_analysis_count", "count_mismatch"))
    if trail.authority_guard_codes != authority_conversion_guards():
        issues.append(
            issue("authority_guard_codes", "complete_guard_set_required")
        )

    _must_true(
        issues,
        trail,
        ("original_trail_preserved", "candidate_only"),
    )
    _must_false(
        issues,
        trail,
        (
            "original_trail_mutated",
            "selected_trail",
            "selected_attachment",
            "reference_resolved",
            "selected_meaning",
            "concept_meaning_created",
            "predicate_role_assigned",
            "permission_inferred",
            "capability_authorized",
            "route_created",
            "tool_routing_performed",
            "memory_read_performed",
            "memory_write_performed",
            "action_performed",
            "delivery_performed",
            "release_authorized",
        ),
    )

    for index, occurrence in enumerate(trail.scope_occurrences):
        report = validate_scope_attachment_occurrence(occurrence)
        for value in report.issues:
            issues.append(
                issue(
                    f"scope_occurrences[{index}].{value.field}",
                    value.code,
                    value.detail,
                )
            )

    for index, analysis in enumerate(trail.reference_analyses):
        report = validate_reference_analysis(analysis)
        for value in report.issues:
            issues.append(
                issue(
                    f"reference_analyses[{index}].{value.field}",
                    value.code,
                    value.detail,
                )
            )

    return _report(issues)


def validate_scope_attachment_reference_constraint_set(
    constraint_set: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(constraint_set) is not ScopeAttachmentReferenceConstraintSet:
        return _report((issue("constraint_set", "invalid_type"),))

    if constraint_set.constraint_set_id != constraint_set.expected_id():
        issues.append(issue("constraint_set_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        constraint_set,
        "constraint_set_schema_id",
        CONSTRAINT_SET_SCHEMA_ID,
    )
    if constraint_set.constrained_trail_count != len(
        constraint_set.constrained_trails
    ):
        issues.append(issue("constrained_trail_count", "count_mismatch"))

    occurrences = tuple(
        occurrence
        for trail in constraint_set.constrained_trails
        for occurrence in trail.scope_occurrences
    )
    analyses = tuple(
        analysis
        for trail in constraint_set.constrained_trails
        for analysis in trail.reference_analyses
    )

    count_checks = {
        "scope_occurrence_count": len(occurrences),
        "reference_analysis_count": len(analyses),
        "singular_attachment_count": sum(
            item.singular_attachment for item in occurrences
        ),
        "multiple_attachment_count": sum(
            item.multiple_attachment for item in occurrences
        ),
        "unresolved_attachment_count": sum(
            item.unresolved_attachment for item in occurrences
        ),
        "malformed_attachment_count": sum(
            item.malformed_attachment for item in occurrences
        ),
        "unsupported_attachment_count": sum(
            item.unsupported_attachment for item in occurrences
        ),
    }
    for field, expected in count_checks.items():
        if getattr(constraint_set, field) != expected:
            issues.append(issue(field, "count_mismatch"))

    if constraint_set.false_authority_conversion_count != len(
        authority_conversion_guards()
    ):
        issues.append(
            issue(
                "false_authority_conversion_count",
                "guard_count_mismatch",
            )
        )

    if not constraint_set.all_original_trails_preserved:
        issues.append(
            issue(
                "all_original_trails_preserved",
                "must_remain_true",
            )
        )
    if not constraint_set.all_lawful_attachments_preserved:
        issues.append(
            issue(
                "all_lawful_attachments_preserved",
                "must_remain_true",
            )
        )

    for field in (
        "selected_trail_id",
        "selected_attachment_id",
        "resolved_reference_entry_id",
    ):
        if getattr(constraint_set, field) is not None:
            issues.append(issue(field, "must_remain_none"))

    _must_false(
        issues,
        constraint_set,
        (
            "selected_meaning",
            "concept_authority_available",
            "predicate_authority_available",
            "permission_authority_available",
            "capability_authority_available",
            "route_authority_available",
            "tool_authority_available",
            "memory_authority_available",
            "action_authority_available",
            "delivery_authority_available",
            "release_authority_available",
            "hidden_fallback_allowed",
        ),
    )

    for index, trail in enumerate(constraint_set.constrained_trails):
        report = validate_scope_constrained_candidate_trail(trail)
        for value in report.issues:
            issues.append(
                issue(
                    f"constrained_trails[{index}].{value.field}",
                    value.code,
                    value.detail,
                )
            )

    return _report(issues)


def validate_scope_attachment_reference_constraint_result(
    result: object,
    projection_result: object | None = None,
    binding_result: object | None = None,
    phase_trail_result: object | None = None,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if type(result) is not ScopeAttachmentReferenceConstraintResult:
        return _report((issue("result", "invalid_type"),))

    if result.result_id != result.expected_id():
        issues.append(issue("result_id", "stable_id_mismatch"))
    _common_identity(
        issues,
        result,
        "result_schema_id",
        CONSTRAINT_RESULT_SCHEMA_ID,
    )

    if result.policy is not None:
        report = validate_scope_constraint_policy(result.policy)
        for value in report.issues:
            issues.append(
                issue(f"policy.{value.field}", value.code, value.detail)
            )
    if result.limits is not None:
        report = validate_scope_constraint_limits(result.limits)
        for value in report.issues:
            issues.append(
                issue(f"limits.{value.field}", value.code, value.detail)
            )
    if result.active_context_registry is not None:
        report = validate_active_context_registry(
            result.active_context_registry
        )
        for value in report.issues:
            issues.append(
                issue(
                    f"active_context_registry.{value.field}",
                    value.code,
                    value.detail,
                )
            )
    if result.constraint_set is not None:
        report = validate_scope_attachment_reference_constraint_set(
            result.constraint_set
        )
        for value in report.issues:
            issues.append(
                issue(
                    f"constraint_set.{value.field}",
                    value.code,
                    value.detail,
                )
            )

    _must_false(
        issues,
        result,
        (
            "filesystem_read_performed",
            "filesystem_write_performed",
            "repository_history_search_performed",
            "network_access_performed",
            "environment_access_performed",
            "memory_read_performed",
            "memory_write_performed",
            "web_search_performed",
            "embedding_performed",
            "language_model_used",
            "similarity_search_performed",
            "selected_trail",
            "selected_attachment",
            "reference_resolved",
            "selected_meaning",
            "concept_meaning_created",
            "predicate_role_assigned",
            "permission_inferred",
            "capability_authorized",
            "route_registration_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
            "release_authorized",
        ),
    )

    if result.constraint_set_created != (result.constraint_set is not None):
        issues.append(
            issue("constraint_set_created", "presence_flag_mismatch")
        )

    if (
        projection_result is not None
        and binding_result is not None
        and phase_trail_result is not None
    ):
        registry = build_default_symbolic_grammar_operator_registry()
        ruleset = build_default_resonant_operator_proposal_ruleset(
            registry
        )
        predecessor_reports = (
            validate_source_field_projection_result(projection_result),
            validate_resonant_operator_candidate_binding_result(
                binding_result,
                (
                    projection_result.projection
                    if type(projection_result) is SourceFieldProjectionResult
                    else None
                ),
                registry,
                ruleset,
            ),
            validate_candidate_resonant_phase_trail_result(
                phase_trail_result,
                projection_result,
                binding_result,
                registry,
            ),
        )
        if not all(report.ok for report in predecessor_reports):
            issues.append(
                issue("predecessors", "invalid_predecessor_contract")
            )
        else:
            projection = projection_result.projection
            binding_set = binding_result.binding_set
            trail_set = phase_trail_result.phase_trail_set

            if projection is not None:
                if result.source_event_id != projection.source_event_id:
                    issues.append(
                        issue("source_event_id", "ancestry_mismatch")
                    )
                if result.projection_id != projection.projection_id:
                    issues.append(
                        issue("projection_id", "ancestry_mismatch")
                    )
            if binding_set is not None and (
                result.binding_set_id != binding_set.binding_set_id
            ):
                issues.append(
                    issue("binding_set_id", "ancestry_mismatch")
                )
            expected_trail_set_id = (
                trail_set.phase_trail_set_id if trail_set is not None else ""
            )
            if result.phase_trail_set_id != expected_trail_set_id:
                issues.append(
                    issue("phase_trail_set_id", "ancestry_mismatch")
                )

            if result.constraint_set is not None and trail_set is not None:
                original_ids = {
                    trail.phase_trail_id for trail in trail_set.trails
                }
                constrained_ids = {
                    trail.phase_trail_id
                    for trail in result.constraint_set.constrained_trails
                }
                if original_ids != constrained_ids:
                    issues.append(
                        issue(
                            "constraint_set.constrained_trails",
                            "trail_preservation_mismatch",
                        )
                    )

    return _report(issues)
