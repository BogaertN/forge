"""Closed deterministic proposal-rule catalogue for Slice 36D.

The catalogue is intentionally small. It proves exact source-bound candidate
formation for a bounded set of law-derived structural signals. It is not a
general lexicon, part-of-speech system, phrase-frequency table, or fallback
parser.
"""

from __future__ import annotations

from typing import Final

from ..schema import stable_record_id
from ..symbolic_grammar_operator_registry import (
    SymbolicGrammarOperatorRegistry,
    build_default_symbolic_grammar_operator_registry,
    grammar_operator_for_key,
)
from .schema import (
    BINDING_SCHEMA_VERSION,
    BINDING_SPEC_ID,
    BINDING_SPEC_VERSION,
    EXPECTED_DEFAULT_RULE_COUNT,
    RMC_DOCUMENT_5_BOUNDARY_REF,
    RMC_SECTION_39_ACTION_AUTHORITY_REF,
    RMC_SECTION_39_AUTHORITY_REF,
    RMC_SECTION_39_CANDIDATE_AUTHORITY_REF,
    RMC_SECTION_39_MISSING_SUPPORT_AUTHORITY_REF,
    RMC_SECTION_39_NEGATION_AUTHORITY_REF,
    RMC_SECTION_39_PLURALITY_AUTHORITY_REF,
    SLICE36B_SOURCE_AUTHORITY_REF,
    SLICE36C_REGISTRY_AUTHORITY_REF,
    ProposalOutputKind,
    ProposalRuleKind,
    ResonantOperatorProposalRule,
    ResonantOperatorProposalRuleSet,
    SourceEdgePolicy,
    SourcePositionPolicy,
    StructuralSignalKind,
)

RULESET_VERSION: Final[str] = "1.0.0"
RULE_VERSION: Final[str] = "1.0.0"

_COMMON_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    RMC_SECTION_39_AUTHORITY_REF,
    RMC_SECTION_39_CANDIDATE_AUTHORITY_REF,
    RMC_SECTION_39_MISSING_SUPPORT_AUTHORITY_REF,
    RMC_SECTION_39_PLURALITY_AUTHORITY_REF,
    SLICE36B_SOURCE_AUTHORITY_REF,
    SLICE36C_REGISTRY_AUTHORITY_REF,
)

_PROHIBITED_MECHANISMS: Final[dict[str, bool]] = {
    "normalization_authorized": False,
    "casefolding_authorized": False,
    "tokenization_authorized": False,
    "phrase_frequency_authorized": False,
    "statistical_scoring_authorized": False,
    "embedding_authorized": False,
    "vector_similarity_authorized": False,
    "nearest_neighbor_authorized": False,
    "language_model_authorized": False,
    "memory_resemblance_authorized": False,
    "web_search_authorized": False,
    "hidden_parser_authorized": False,
    "capability_influence_authorized": False,
}


def _case_variants(value: str) -> tuple[str, ...]:
    candidates = (value, value[:1].upper() + value[1:], value.upper())
    return tuple(dict.fromkeys(candidates))


def _operator_identity(
    registry: SymbolicGrammarOperatorRegistry,
    operator_key: str | None,
) -> tuple[str | None, str | None]:
    if operator_key is None:
        return None, None
    definition = grammar_operator_for_key(operator_key, registry)
    if definition is None:
        raise ValueError(f"unknown grammar operator: {operator_key}")
    return definition.operator_version, definition.definition_id


def _rule(
    *,
    registry: SymbolicGrammarOperatorRegistry,
    rule_key: str,
    rule_kind: ProposalRuleKind,
    output_kind: ProposalOutputKind,
    operator_key: str | None,
    candidate_variant_code: str,
    competition_group_code: str = "",
    exact_forms: tuple[str, ...] = (),
    exact_sequences: tuple[tuple[str, ...], ...] = (),
    quotation_pairs: tuple[tuple[str, str], ...] = (),
    position_policy: SourcePositionPolicy = SourcePositionPolicy.ANYWHERE,
    edge_policy: SourceEdgePolicy = SourceEdgePolicy.NONE,
    observable_condition_codes: tuple[str, ...],
    satisfied_prerequisite_codes: tuple[str, ...],
    missing_prerequisite_codes: tuple[str, ...],
    conflicting_evidence_codes: tuple[str, ...] = (),
    structural_signal_kind: StructuralSignalKind | None = None,
    possible_parent_rule_keys: tuple[str, ...] = (),
    possible_child_rule_keys: tuple[str, ...] = (),
    authority_refs: tuple[str, ...] = _COMMON_AUTHORITY_REFS,
) -> ResonantOperatorProposalRule:
    operator_version, definition_id = _operator_identity(
        registry,
        operator_key,
    )
    body = {
        "rule_key": rule_key,
        "rule_version": RULE_VERSION,
        "rule_kind": rule_kind,
        "output_kind": output_kind,
        "candidate_operator_key": operator_key,
        "candidate_operator_version": operator_version,
        "candidate_operator_definition_id": definition_id,
        "candidate_variant_code": candidate_variant_code,
        "competition_group_code": competition_group_code,
        "exact_forms": exact_forms,
        "exact_sequences": exact_sequences,
        "quotation_pairs": quotation_pairs,
        "position_policy": position_policy,
        "edge_policy": edge_policy,
        "required_projection_status_values": (
            "SOURCE_FIELD_SUPPORTED",
            "SOURCE_FIELD_PARTIALLY_UNSUPPORTED",
        ),
        "observable_condition_codes": observable_condition_codes,
        "satisfied_prerequisite_codes": satisfied_prerequisite_codes,
        "missing_prerequisite_codes": missing_prerequisite_codes,
        "conflicting_evidence_codes": conflicting_evidence_codes,
        "structural_signal_kind": structural_signal_kind,
        "possible_parent_rule_keys": possible_parent_rule_keys,
        "possible_child_rule_keys": possible_child_rule_keys,
        "enabled": True,
        "exact_match_required": True,
        "source_span_required": True,
        **_PROHIBITED_MECHANISMS,
        "source_authority_refs": authority_refs,
        "binding_spec_id": BINDING_SPEC_ID,
        "binding_spec_version": BINDING_SPEC_VERSION,
        "schema_version": BINDING_SCHEMA_VERSION,
        "rule_schema_id": "aiweb-resonant-operator-proposal-rule-v1",
    }
    return ResonantOperatorProposalRule(
        rule_id=stable_record_id(
            "resonant_operator_proposal_rule",
            body,
        ),
        **body,
    )


def build_default_resonant_operator_proposal_ruleset(
    registry: SymbolicGrammarOperatorRegistry | None = None,
) -> ResonantOperatorProposalRuleSet:
    """Build the closed Slice 36D v1 proposal-rule set."""

    selected_registry = (
        registry or build_default_symbolic_grammar_operator_registry()
    )

    action_forms: list[str] = []
    for form in (
        "send",
        "delete",
        "save",
        "install",
        "update",
        "write",
        "publish",
        "run",
        "open",
        "remember",
        "proceed",
    ):
        action_forms.extend(_case_variants(form))

    reference_forms: list[str] = []
    for form in (
        "it",
        "this",
        "that",
        "they",
        "them",
        "these",
        "those",
    ):
        reference_forms.extend(_case_variants(form))

    quote_pairs = (("\"", "\""), ("“", "”"))

    rules = (
        _rule(
            registry=selected_registry,
            rule_key="36d.explicit_negation.not",
            rule_kind=ProposalRuleKind.EXACT_WHOLE_UNIT,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_negation",
            candidate_variant_code="explicit_negation_surface_not",
            exact_forms=_case_variants("not"),
            edge_policy=SourceEdgePolicy.UNICODE_WORD_EDGE,
            observable_condition_codes=(
                "exact_source_form_not",
                "unicode_word_edges_clear",
                "exact_source_order_preserved",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_source_span_membership",
                "explicit_negation_surface_observed",
            ),
            missing_prerequisite_codes=(
                "negation_scope_not_selected",
                "governed_target_not_selected",
                "meaning_gate_not_applied",
            ),
            possible_parent_rule_keys=(
                "36d.initial_do_not_prohibition",
            ),
            authority_refs=(
                *_COMMON_AUTHORITY_REFS,
                RMC_SECTION_39_NEGATION_AUTHORITY_REF,
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.initial_do_not_prohibition",
            rule_kind=ProposalRuleKind.EXACT_INITIAL_SEQUENCE,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_prohibition",
            candidate_variant_code="initial_do_not_prohibitory_surface",
            exact_sequences=(
                ("Do", "not"),
                ("do", "not"),
                ("DO", "NOT"),
            ),
            position_policy=SourcePositionPolicy.INITIAL_NON_WHITESPACE,
            edge_policy=SourceEdgePolicy.UNICODE_WORD_EDGE,
            observable_condition_codes=(
                "initial_exact_do_form",
                "one_or_more_exact_whitespace_code_points",
                "exact_not_form",
                "unicode_word_edges_clear",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_multi_span_source_mapping",
                "initial_do_not_surface_observed",
            ),
            missing_prerequisite_codes=(
                "communicative_purpose_not_selected",
                "predicate_role_support_missing",
                "target_or_referent_may_be_missing",
                "permission_and_action_authority_external",
            ),
            possible_child_rule_keys=(
                "36d.explicit_negation.not",
            ),
            authority_refs=(
                *_COMMON_AUTHORITY_REFS,
                RMC_SECTION_39_NEGATION_AUTHORITY_REF,
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.unresolved_reference_surface",
            rule_kind=ProposalRuleKind.EXACT_WHOLE_UNIT,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_reference",
            candidate_variant_code="unresolved_reference_surface",
            exact_forms=tuple(dict.fromkeys(reference_forms)),
            edge_policy=SourceEdgePolicy.UNICODE_WORD_EDGE,
            observable_condition_codes=(
                "exact_reference_surface_form",
                "unicode_word_edges_clear",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_source_span_membership",
                "reference_like_surface_observed",
            ),
            missing_prerequisite_codes=(
                "referent_not_resolved",
                "active_context_not_consulted",
                "concept_support_not_applied",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.terminal_period_boundary",
            rule_kind=ProposalRuleKind.EXACT_TERMINAL_MARK,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_boundary",
            candidate_variant_code="terminal_period_boundary",
            exact_forms=(".",),
            position_policy=SourcePositionPolicy.TERMINAL_NON_WHITESPACE,
            observable_condition_codes=(
                "exact_terminal_period",
                "trailing_source_contains_whitespace_only",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_terminal_source_span",
            ),
            missing_prerequisite_codes=(
                "clause_structure_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.terminal_period_loop_seal",
            rule_kind=ProposalRuleKind.EXACT_TERMINAL_MARK,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="fbsc_loop_seal",
            candidate_variant_code="possible_loop_seal_from_period",
            exact_forms=(".",),
            position_policy=SourcePositionPolicy.TERMINAL_NON_WHITESPACE,
            observable_condition_codes=(
                "exact_terminal_period",
                "trailing_source_contains_whitespace_only",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_terminal_source_span",
            ),
            missing_prerequisite_codes=(
                "completion_meaning_not_selected",
                "phase_trail_not_constructed",
                "loop_completion_not_proven",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.terminal_exclamation_boundary",
            rule_kind=ProposalRuleKind.EXACT_TERMINAL_MARK,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_boundary",
            candidate_variant_code="terminal_exclamation_boundary",
            exact_forms=("!",),
            position_policy=SourcePositionPolicy.TERMINAL_NON_WHITESPACE,
            observable_condition_codes=(
                "exact_terminal_exclamation_mark",
                "trailing_source_contains_whitespace_only",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_terminal_source_span",
            ),
            missing_prerequisite_codes=(
                "communicative_force_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.terminal_exclamation_loop_seal",
            rule_kind=ProposalRuleKind.EXACT_TERMINAL_MARK,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="fbsc_loop_seal",
            candidate_variant_code="possible_loop_seal_from_exclamation",
            exact_forms=("!",),
            position_policy=SourcePositionPolicy.TERMINAL_NON_WHITESPACE,
            observable_condition_codes=(
                "exact_terminal_exclamation_mark",
                "trailing_source_contains_whitespace_only",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_terminal_source_span",
            ),
            missing_prerequisite_codes=(
                "completion_meaning_not_selected",
                "phase_trail_not_constructed",
                "loop_completion_not_proven",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.terminal_question_boundary",
            rule_kind=ProposalRuleKind.EXACT_TERMINAL_MARK,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_boundary",
            candidate_variant_code="terminal_question_boundary",
            exact_forms=("?",),
            position_policy=SourcePositionPolicy.TERMINAL_NON_WHITESPACE,
            observable_condition_codes=(
                "exact_terminal_question_mark",
                "trailing_source_contains_whitespace_only",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_terminal_source_span",
            ),
            missing_prerequisite_codes=(
                "question_meaning_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.terminal_question_uncertainty",
            rule_kind=ProposalRuleKind.EXACT_TERMINAL_MARK,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_uncertainty",
            candidate_variant_code="possible_interrogative_uncertainty",
            exact_forms=("?",),
            position_policy=SourcePositionPolicy.TERMINAL_NON_WHITESPACE,
            observable_condition_codes=(
                "exact_terminal_question_mark",
                "trailing_source_contains_whitespace_only",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_terminal_source_span",
            ),
            missing_prerequisite_codes=(
                "communicative_purpose_not_selected",
                "question_scope_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.quotation_direct_candidate",
            rule_kind=ProposalRuleKind.EXACT_QUOTATION_PAIR,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_quotation_containment",
            candidate_variant_code="possible_direct_quotation",
            competition_group_code="quotation_interpretation",
            quotation_pairs=quote_pairs,
            position_policy=SourcePositionPolicy.QUOTATION_PAIR,
            observable_condition_codes=(
                "exact_opening_quotation_mark",
                "exact_closing_quotation_mark",
                "quoted_source_order_preserved",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_quotation_boundary_spans",
            ),
            missing_prerequisite_codes=(
                "quoted_speaker_or_source_support_missing",
                "reported_content_status_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.quotation_name_candidate",
            rule_kind=ProposalRuleKind.EXACT_QUOTATION_PAIR,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_quotation_containment",
            candidate_variant_code="possible_quoted_name",
            competition_group_code="quotation_interpretation",
            quotation_pairs=quote_pairs,
            position_policy=SourcePositionPolicy.QUOTATION_PAIR,
            observable_condition_codes=(
                "exact_opening_quotation_mark",
                "exact_closing_quotation_mark",
                "quoted_source_order_preserved",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_quotation_boundary_spans",
            ),
            missing_prerequisite_codes=(
                "name_or_concept_support_missing",
                "name_reference_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.quotation_title_candidate",
            rule_kind=ProposalRuleKind.EXACT_QUOTATION_PAIR,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_quotation_containment",
            candidate_variant_code="possible_quoted_title",
            competition_group_code="quotation_interpretation",
            quotation_pairs=quote_pairs,
            position_policy=SourcePositionPolicy.QUOTATION_PAIR,
            observable_condition_codes=(
                "exact_opening_quotation_mark",
                "exact_closing_quotation_mark",
                "quoted_source_order_preserved",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_quotation_boundary_spans",
            ),
            missing_prerequisite_codes=(
                "document_or_file_title_support_missing",
                "title_reference_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.quotation_literal_candidate",
            rule_kind=ProposalRuleKind.EXACT_QUOTATION_PAIR,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_quotation_containment",
            candidate_variant_code="possible_literal_string",
            competition_group_code="quotation_interpretation",
            quotation_pairs=quote_pairs,
            position_policy=SourcePositionPolicy.QUOTATION_PAIR,
            observable_condition_codes=(
                "exact_opening_quotation_mark",
                "exact_closing_quotation_mark",
                "quoted_source_order_preserved",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_quotation_boundary_spans",
            ),
            missing_prerequisite_codes=(
                "literal_context_support_missing",
                "literal_status_not_selected",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.quotation_incomplete_candidate",
            rule_kind=ProposalRuleKind.EXACT_UNMATCHED_QUOTATION_OPEN,
            output_kind=ProposalOutputKind.OPERATOR_CANDIDATE,
            operator_key="grammar_quotation_containment",
            candidate_variant_code="possible_incomplete_quotation",
            competition_group_code="quotation_interpretation",
            quotation_pairs=quote_pairs,
            position_policy=SourcePositionPolicy.UNMATCHED_QUOTATION_OPEN,
            observable_condition_codes=(
                "exact_opening_quotation_mark",
                "matching_closing_quotation_mark_absent",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_opening_quotation_span",
            ),
            missing_prerequisite_codes=(
                "closing_quotation_boundary_missing",
                "quotation_extent_unresolved",
                "quotation_interpretation_not_selected",
            ),
            conflicting_evidence_codes=(
                "source_quotation_structure_incomplete",
            ),
        ),
        _rule(
            registry=selected_registry,
            rule_key="36d.action_like_surface_unbound",
            rule_kind=ProposalRuleKind.EXACT_WHOLE_UNIT,
            output_kind=ProposalOutputKind.UNBOUND_STRUCTURAL_SIGNAL,
            operator_key=None,
            candidate_variant_code="action_like_signal_for_later_predicate_analysis",
            exact_forms=tuple(dict.fromkeys(action_forms)),
            edge_policy=SourceEdgePolicy.UNICODE_WORD_EDGE,
            observable_condition_codes=(
                "exact_action_like_surface_form",
                "unicode_word_edges_clear",
            ),
            satisfied_prerequisite_codes=(
                "validated_source_field_projection",
                "exact_source_span_membership",
                "document3_action_like_signal_surface_observed",
            ),
            missing_prerequisite_codes=(
                "authorized_grammar_operator_mapping_missing",
                "document5_action_root_support_missing",
                "predicate_role_support_missing",
                "capability_binding_not_performed",
                "permission_and_action_authority_external",
            ),
            structural_signal_kind=StructuralSignalKind.ACTION_LIKE,
            authority_refs=(
                *_COMMON_AUTHORITY_REFS,
                RMC_SECTION_39_ACTION_AUTHORITY_REF,
                RMC_DOCUMENT_5_BOUNDARY_REF,
            ),
        ),
    )

    if len(rules) != EXPECTED_DEFAULT_RULE_COUNT:
        raise AssertionError("default proposal-rule count drifted")

    body = {
        "ruleset_version": RULESET_VERSION,
        "grammar_registry_id": selected_registry.registry_id,
        "grammar_registry_version": selected_registry.registry_version,
        "rules": rules,
        "exact_rule_count": EXPECTED_DEFAULT_RULE_COUNT,
        "closed_world": True,
        "deterministic_only": True,
        "rule_order_selects_winner": False,
        "automatic_activation_authorized": False,
        "operator_application_authorized": False,
        "phase_assignment_authorized": False,
        "meaning_selection_authorized": False,
        "permission_authorized": False,
        "route_authorized": False,
        "action_authorized": False,
        "hidden_fallback_allowed": False,
        "binding_spec_id": BINDING_SPEC_ID,
        "binding_spec_version": BINDING_SPEC_VERSION,
        "schema_version": BINDING_SCHEMA_VERSION,
        "ruleset_schema_id": "aiweb-resonant-operator-proposal-ruleset-v1",
    }
    return ResonantOperatorProposalRuleSet(
        ruleset_id=stable_record_id(
            "resonant_operator_proposal_ruleset",
            body,
        ),
        **body,
    )


def proposal_rule_for_key(
    rule_key: object,
    ruleset: ResonantOperatorProposalRuleSet | None = None,
) -> ResonantOperatorProposalRule | None:
    if type(rule_key) is not str:
        return None
    selected = ruleset or build_default_resonant_operator_proposal_ruleset()
    return next(
        (rule for rule in selected.rules if rule.rule_key == rule_key),
        None,
    )
