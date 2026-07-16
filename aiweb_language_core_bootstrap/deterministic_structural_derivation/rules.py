"""Closed deterministic rule registry for Slice 36G."""

from __future__ import annotations

from typing import Final

from ..schema import stable_record_id
from .schema import (
    CANONICAL_ROADMAP_AUTHORITY_REF,
    RMC_LANGUAGE_LAW_AUTHORITY_REF,
    SLICE36A_AUTHORITY_REF,
    SLICE36B_AUTHORITY_REF,
    SLICE36C_AUTHORITY_REF,
    SLICE36D_AUTHORITY_REF,
    SLICE36E_AUTHORITY_REF,
    SLICE36F_AUTHORITY_REF,
    SLICE39_AUTHORITY_REF,
    SLICE40_AUTHORITY_REF,
    STRUCTURAL_DERIVATION_SCHEMA_VERSION,
    STRUCTURAL_DERIVATION_SPEC_ID,
    STRUCTURAL_DERIVATION_SPEC_VERSION,
    STRUCTURAL_RULE_SCHEMA_ID,
    StructuralDerivationRule,
    StructuralTraceLayer,
)


_RULE_VERSION: Final[str] = "1.0.0"
_COMMON_REFS: Final[tuple[str, ...]] = (
    CANONICAL_ROADMAP_AUTHORITY_REF,
    RMC_LANGUAGE_LAW_AUTHORITY_REF,
    SLICE36A_AUTHORITY_REF,
    SLICE36B_AUTHORITY_REF,
    SLICE36C_AUTHORITY_REF,
    SLICE36D_AUTHORITY_REF,
    SLICE36E_AUTHORITY_REF,
    SLICE36F_AUTHORITY_REF,
    SLICE39_AUTHORITY_REF,
    SLICE40_AUTHORITY_REF,
)


def _rule(
    *,
    key: str,
    layer: StructuralTraceLayer,
    purpose: str,
    creates_candidate: bool = False,
) -> StructuralDerivationRule:
    body = {
        "rule_key": key,
        "rule_version": _RULE_VERSION,
        "trace_layer": layer,
        "purpose_code": purpose,
        "exact_predecessor_record_required": True,
        "creates_structural_candidate": creates_candidate,
        "creates_selected_meaning": False,
        "asks_clarification_question": False,
        "performs_semantic_rejection": False,
        "source_authority_refs": _COMMON_REFS,
        "structural_derivation_spec_id": STRUCTURAL_DERIVATION_SPEC_ID,
        "structural_derivation_spec_version": STRUCTURAL_DERIVATION_SPEC_VERSION,
        "schema_version": STRUCTURAL_DERIVATION_SCHEMA_VERSION,
        "rule_schema_id": STRUCTURAL_RULE_SCHEMA_ID,
    }
    return StructuralDerivationRule(
        rule_id=stable_record_id("structural_derivation_rule", body),
        **body,
    )


def build_default_structural_derivation_rules() -> tuple[StructuralDerivationRule, ...]:
    return (
        _rule(
            key="preserve_input_custody_ancestry",
            layer=StructuralTraceLayer.SOURCE_CUSTODY,
            purpose="preserve_exact_input_event_and_root_span",
        ),
        _rule(
            key="verify_source_field_reconstruction",
            layer=StructuralTraceLayer.SOURCE_RECONSTRUCTION,
            purpose="prove_exact_reconstruction_from_source_field",
        ),
        _rule(
            key="preserve_operator_binding_ancestry",
            layer=StructuralTraceLayer.OPERATOR_BINDING,
            purpose="preserve_all_participating_and_unbound_binding_records",
        ),
        _rule(
            key="preserve_phase_trail_ancestry",
            layer=StructuralTraceLayer.PHASE_TRAIL,
            purpose="preserve_immutable_phase_trail_and_applications",
        ),
        _rule(
            key="preserve_scope_attachment_candidates",
            layer=StructuralTraceLayer.SCOPE_ATTACHMENT,
            purpose="preserve_every_scope_occurrence_and_attachment_alternative",
        ),
        _rule(
            key="preserve_reference_candidates",
            layer=StructuralTraceLayer.REFERENCE,
            purpose="preserve_every_reference_analysis_and_context_candidate",
        ),
        _rule(
            key="build_explicit_operator_graph",
            layer=StructuralTraceLayer.STRUCTURAL_DERIVATION,
            purpose="build_nodes_and_only_explicit_ancestry_conflict_edges",
        ),
        _rule(
            key="compute_bounded_source_coverage",
            layer=StructuralTraceLayer.SOURCE_COVERAGE,
            purpose="compute_consumed_and_unconsumed_exact_source_ranges",
        ),
        _rule(
            key="construct_candidate_per_constrained_trail",
            layer=StructuralTraceLayer.STRUCTURAL_DERIVATION,
            purpose="create_one_candidate_for_each_preserved_constrained_trail",
            creates_candidate=True,
        ),
        _rule(
            key="classify_lawful_non_progress",
            layer=StructuralTraceLayer.NON_PROGRESS,
            purpose="preserve_every_supported_non_progress_reason_without_guessing",
        ),
    )


def structural_derivation_rule_for_key(
    rule_key: str,
    rules: tuple[StructuralDerivationRule, ...] | None = None,
) -> StructuralDerivationRule | None:
    active = rules if rules is not None else build_default_structural_derivation_rules()
    for rule in active:
        if rule.rule_key == rule_key:
            return rule
    return None
