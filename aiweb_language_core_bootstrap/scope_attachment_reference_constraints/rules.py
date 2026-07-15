"""Closed Slice 36F scope-rule registry and active-context constructors."""

from __future__ import annotations

from typing import Final

from ..schema import stable_record_id
from .schema import (
    ACTIVE_CONTEXT_ENTRY_SCHEMA_ID,
    ACTIVE_CONTEXT_REGISTRY_SCHEMA_ID,
    CANONICAL_ROADMAP_AUTHORITY_REF,
    RMC_CONCEPT_AUTHORITY_REF,
    RMC_LANGUAGE_LAW_AUTHORITY_REF,
    RMC_PREDICATE_AUTHORITY_REF,
    SCOPE_CONSTRAINT_SCHEMA_VERSION,
    SCOPE_CONSTRAINT_SPEC_ID,
    SCOPE_CONSTRAINT_SPEC_VERSION,
    SCOPE_RULE_SCHEMA_ID,
    SLICE36D_AUTHORITY_REF,
    SLICE36E_AUTHORITY_REF,
    ActiveContextEntry,
    ActiveContextRegistry,
    AttachmentStrategy,
    AuthorityConversionGuard,
    ContextClaimForce,
    ContextEvidenceStrength,
    ContextObjectKind,
    ContextOperationalStatus,
    ContextPositionTag,
    ContextPrivacyStatus,
    ScopeAttachmentRule,
    ScopeResponsibility,
    ScopeRuleActivationStatus,
)


_RULE_VERSION: Final[str] = "1.0.0"
_CONTEXT_REGISTRY_VERSION: Final[str] = "1.0.0"

_COMMON_REFS: Final[tuple[str, ...]] = (
    CANONICAL_ROADMAP_AUTHORITY_REF,
    RMC_LANGUAGE_LAW_AUTHORITY_REF,
    RMC_CONCEPT_AUTHORITY_REF,
    RMC_PREDICATE_AUTHORITY_REF,
    SLICE36D_AUTHORITY_REF,
    SLICE36E_AUTHORITY_REF,
)


def authority_conversion_guards() -> tuple[AuthorityConversionGuard, ...]:
    return tuple(AuthorityConversionGuard)


def _rule(
    *,
    rule_key: str,
    responsibility: ScopeResponsibility,
    operator_keys: tuple[str, ...] = (),
    operator_families: tuple[str, ...] = (),
    candidate_variant_codes: tuple[str, ...] = (),
    attachment_strategy: AttachmentStrategy,
    activation_status: ScopeRuleActivationStatus,
) -> ScopeAttachmentRule:
    body = {
        "rule_key": rule_key,
        "rule_version": _RULE_VERSION,
        "responsibility": responsibility,
        "operator_keys": operator_keys,
        "operator_families": operator_families,
        "candidate_variant_codes": candidate_variant_codes,
        "attachment_strategy": attachment_strategy,
        "activation_status": activation_status,
        "exact_source_span_required": True,
        "preserve_multiple_attachments": True,
        "possible_parent_links_preserved": True,
        "possible_child_links_preserved": True,
        "no_semantic_selection": True,
        "no_authority_conversion": True,
        "source_authority_refs": _COMMON_REFS,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "rule_schema_id": SCOPE_RULE_SCHEMA_ID,
    }
    return ScopeAttachmentRule(
        rule_id=stable_record_id("scope_attachment_rule", body),
        **body,
    )


def build_default_scope_attachment_rules() -> tuple[ScopeAttachmentRule, ...]:
    """Return the closed Slice 36F v1 rule set.

    Rules never identify source forms. They operate only on accepted Slice 36D
    candidate bindings and exact Slice 36B source coordinates.
    """

    active = ScopeRuleActivationStatus.ACTIVE_FOR_ACCEPTED_BINDING
    waiting = (
        ScopeRuleActivationStatus.REGISTERED_AWAITING_BINDING_AUTHORITY
    )
    no_attachment = AttachmentStrategy.NO_ATTACHMENT_UNTIL_AUTHORIZED_BINDING

    rules = (
        _rule(
            rule_key="36f.negation.rightward-prefixes",
            responsibility=ScopeResponsibility.NEGATION,
            operator_keys=("grammar_negation",),
            operator_families=("negation",),
            attachment_strategy=(
                AttachmentStrategy.RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.prohibition.rightward-prefixes",
            responsibility=ScopeResponsibility.PROHIBITION,
            operator_keys=("grammar_prohibition",),
            operator_families=("prohibition",),
            attachment_strategy=(
                AttachmentStrategy.RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.condition.rightward-prefixes",
            responsibility=ScopeResponsibility.CONDITION,
            operator_keys=("grammar_condition",),
            operator_families=("condition",),
            attachment_strategy=(
                AttachmentStrategy.RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.hypothetical.modality-surface",
            responsibility=ScopeResponsibility.HYPOTHETICAL_STATUS,
            operator_keys=("grammar_modality",),
            operator_families=("modality",),
            attachment_strategy=(
                AttachmentStrategy.RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.quotation.exact-interior",
            responsibility=ScopeResponsibility.QUOTATION,
            operator_keys=("grammar_quotation_containment",),
            operator_families=("quotation_containment",),
            attachment_strategy=AttachmentStrategy.EXACT_DELIMITED_INTERIOR,
            activation_status=active,
        ),
        _rule(
            rule_key="36f.reported-speech.direct-quotation-candidate",
            responsibility=ScopeResponsibility.REPORTED_SPEECH,
            operator_keys=("grammar_quotation_containment",),
            operator_families=("quotation_containment",),
            candidate_variant_codes=("possible_direct_quotation",),
            attachment_strategy=AttachmentStrategy.EXACT_DELIMITED_INTERIOR,
            activation_status=active,
        ),
        _rule(
            rule_key="36f.interrogation.terminal-question-surface",
            responsibility=ScopeResponsibility.INTERROGATION,
            operator_keys=("grammar_boundary",),
            operator_families=("boundary",),
            candidate_variant_codes=("terminal_question_boundary",),
            attachment_strategy=(
                AttachmentStrategy.SOURCE_UNIT_WITHOUT_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.imperative-surface.initial-do-not",
            responsibility=ScopeResponsibility.IMPERATIVE_SURFACE_FORM,
            operator_keys=("grammar_prohibition",),
            operator_families=("prohibition",),
            candidate_variant_codes=(
                "initial_do_not_prohibitory_surface",
            ),
            attachment_strategy=(
                AttachmentStrategy.SOURCE_UNIT_WITHOUT_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.proposal.awaiting-binding-authority",
            responsibility=ScopeResponsibility.PROPOSAL,
            operator_keys=("grammar_uncertainty",),
            operator_families=("uncertainty",),
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.completion.surface-seal-not-world-state",
            responsibility=ScopeResponsibility.COMPLETION_CLAIMS,
            operator_keys=("fbsc_loop_seal",),
            operator_families=("completion",),
            candidate_variant_codes=(
                "possible_loop_seal_from_period",
            ),
            attachment_strategy=(
                AttachmentStrategy.SOURCE_UNIT_WITHOUT_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.exception.rightward-prefixes",
            responsibility=ScopeResponsibility.EXCEPTION,
            operator_keys=("grammar_exception",),
            operator_families=("exception",),
            attachment_strategy=(
                AttachmentStrategy.RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.exclusion.awaiting-binding-authority",
            responsibility=ScopeResponsibility.EXCLUSION,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.modality.rightward-prefixes",
            responsibility=ScopeResponsibility.MODALITY,
            operator_keys=("grammar_modality",),
            operator_families=("modality",),
            attachment_strategy=(
                AttachmentStrategy.RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY
            ),
            activation_status=active,
        ),
        _rule(
            rule_key="36f.temporal-status.awaiting-binding-authority",
            responsibility=ScopeResponsibility.TEMPORAL_STATUS,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.operational-status.awaiting-binding-authority",
            responsibility=ScopeResponsibility.OPERATIONAL_STATUS,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.quantification.awaiting-binding-authority",
            responsibility=ScopeResponsibility.QUANTIFICATION,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.privacy.awaiting-binding-authority",
            responsibility=ScopeResponsibility.PRIVACY,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.disclosure-limitation.awaiting-binding-authority",
            responsibility=ScopeResponsibility.DISCLOSURE_LIMITATION,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.evidence-strength.awaiting-binding-authority",
            responsibility=ScopeResponsibility.EVIDENCE_STRENGTH,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.claim-force.awaiting-binding-authority",
            responsibility=ScopeResponsibility.CLAIM_FORCE,
            attachment_strategy=no_attachment,
            activation_status=waiting,
        ),
        _rule(
            rule_key="36f.reference.self-and-explicit-context-only",
            responsibility=ScopeResponsibility.REFERENCE,
            operator_keys=("grammar_reference",),
            operator_families=("reference",),
            attachment_strategy=AttachmentStrategy.SELF_ONLY,
            activation_status=active,
        ),
    )

    return tuple(sorted(rules, key=lambda item: item.rule_key))


def rules_for_candidate(
    *,
    operator_key: str,
    operator_family: str,
    candidate_variant_code: str,
    rules: tuple[ScopeAttachmentRule, ...] | None = None,
) -> tuple[ScopeAttachmentRule, ...]:
    selected = rules or build_default_scope_attachment_rules()
    matches = []

    for rule in selected:
        if (
            rule.activation_status
            is not ScopeRuleActivationStatus.ACTIVE_FOR_ACCEPTED_BINDING
        ):
            continue

        key_match = (
            not rule.operator_keys
            or operator_key in rule.operator_keys
        )
        family_match = (
            not rule.operator_families
            or operator_family in rule.operator_families
        )
        variant_match = (
            not rule.candidate_variant_codes
            or candidate_variant_code in rule.candidate_variant_codes
        )

        if key_match and family_match and variant_match:
            matches.append(rule)

    return tuple(matches)


def build_active_context_entry(
    *,
    context_object_id: str,
    object_kind: ContextObjectKind,
    exact_identifiers: tuple[str, ...] = (),
    exact_reference_forms: tuple[str, ...] = (),
    ordinal: int | None = None,
    position_tags: tuple[ContextPositionTag, ...] = (),
    operational_status: ContextOperationalStatus = (
        ContextOperationalStatus.UNSPECIFIED
    ),
    privacy_status: ContextPrivacyStatus = (
        ContextPrivacyStatus.UNSPECIFIED
    ),
    evidence_strength: ContextEvidenceStrength = (
        ContextEvidenceStrength.UNSPECIFIED
    ),
    claim_force: ContextClaimForce = ContextClaimForce.UNSPECIFIED,
    source_event_ids: tuple[str, ...] = (),
) -> ActiveContextEntry:
    body = {
        "context_object_id": context_object_id,
        "object_kind": object_kind,
        "exact_identifiers": exact_identifiers,
        "exact_reference_forms": exact_reference_forms,
        "ordinal": ordinal,
        "position_tags": position_tags,
        "operational_status": operational_status,
        "privacy_status": privacy_status,
        "evidence_strength": evidence_strength,
        "claim_force": claim_force,
        "source_event_ids": source_event_ids,
        "caller_supplied": True,
        "immutable": True,
        "concept_identity_assigned": False,
        "predicate_role_assigned": False,
        "capability_binding_created": False,
        "release_authorized": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "entry_schema_id": ACTIVE_CONTEXT_ENTRY_SCHEMA_ID,
    }
    return ActiveContextEntry(
        entry_id=stable_record_id("active_context_entry", body),
        **body,
    )


def build_active_context_registry(
    entries: tuple[ActiveContextEntry, ...] = (),
    *,
    registry_version: str = _CONTEXT_REGISTRY_VERSION,
) -> ActiveContextRegistry:
    ordered = tuple(sorted(entries, key=lambda item: item.entry_id))
    body = {
        "registry_version": registry_version,
        "entries": ordered,
        "exact_entry_count": len(ordered),
        "explicit_only": True,
        "immutable": True,
        "closed_world_for_this_analysis": True,
        "automatic_memory_search": False,
        "automatic_file_search": False,
        "automatic_repository_history_search": False,
        "automatic_web_search": False,
        "similarity_search": False,
        "nearest_object_fallback": False,
        "capability_influence": False,
        "scope_constraint_spec_id": SCOPE_CONSTRAINT_SPEC_ID,
        "scope_constraint_spec_version": SCOPE_CONSTRAINT_SPEC_VERSION,
        "schema_version": SCOPE_CONSTRAINT_SCHEMA_VERSION,
        "registry_schema_id": ACTIVE_CONTEXT_REGISTRY_SCHEMA_ID,
    }
    return ActiveContextRegistry(
        registry_id=stable_record_id("active_context_registry", body),
        **body,
    )
