"""Static Slice 37D sense, lexical-reference, mapping, and lifecycle records.

The combined governance batch reuses the exact Slice 37C concept resources and
adds only Slice 37D semantic-resource histories. Registry population and exact
lookup are authorized by the separate Slice 37D manifest, not by lifecycle
admission alone.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Final, TypeVar

from ..built_in_registry.records import (
    ADMITTED_CONCEPTS,
    CURRENT_NAMESPACE,
    GOVERNANCE_BATCH as SLICE37C_GOVERNANCE_BATCH,
)
from ..governed_lifecycle.identity import (
    expected_resource_lineage_id,
    resource_id,
    with_expected_authority_id,
    with_expected_batch_id,
    with_expected_transition_id,
    with_recomputed_resource_id,
)
from ..governed_lifecycle.schema import (
    ConceptGovernanceBatch,
    ConceptLifecycleAuthorityRecord,
    ConceptLifecycleTransitionKind,
    ConceptLifecycleTransitionRecord,
    GovernedConceptResource,
)
from ..schema import (
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    ConceptLifecycleState,
    ConceptProvenanceReference,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    TermConceptMappingIdentity,
)
from .authority import (
    LEXICAL_REFERENCE_DEFINITIONS,
    MAPPING_DEFINITIONS,
    OUTWARD_ELIGIBLE_LEXICAL_KEYS,
    SENSE_DEFINITIONS,
    SLICE37D_COMMON_PROHIBITED_USES,
    SLICE37D_DECISION_OWNER_REF,
    SLICE37D_HUMAN_APPROVAL_REF,
    SLICE37D_PROHIBITED_AUTHORITIES,
    LexicalReferenceDefinition,
    MappingDefinition,
    SenseDefinition,
)
from .identity import (
    with_expected_eligibility_id,
    with_expected_expansion_refusal_id,
)
from .schema import (
    MappingExpansionRefusal,
    OutwardExpressionEligibilityReference,
    OutwardExpressionEligibilityState,
    ProhibitedExpansionKind,
)


T = TypeVar("T", bound=GovernedConceptResource)


def _with_provenance_id(
    record: ConceptProvenanceReference,
) -> ConceptProvenanceReference:
    return replace(record, provenance_id=record.expected_id())


def _provenance(
    *,
    authority_section: str,
    source_reference: str,
    source_kind: str,
) -> ConceptProvenanceReference:
    return _with_provenance_id(
        ConceptProvenanceReference(
            provenance_id="",
            authority_document=(
                "Document 4 — RMC Concept Lexicon and Semantic Relation Graph v1"
            ),
            authority_section=authority_section,
            source_kind=source_kind,
            source_reference=source_reference,
            version="v1",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


LEXICAL_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=definition.authority_section,
        source_reference=definition.source_reference,
        source_kind="controlled_lexical_reference_authority",
    )
    for definition in LEXICAL_REFERENCE_DEFINITIONS
)

SENSE_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=definition.authority_section,
        source_reference=definition.source_reference,
        source_kind="controlled_sense_identity_authority",
    )
    for definition in SENSE_DEFINITIONS
)

MAPPING_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=definition.authority_section,
        source_reference=definition.source_reference,
        source_kind="exact_term_mapping_authority",
    )
    for definition in MAPPING_DEFINITIONS
)

OUTWARD_ELIGIBILITY_PROVENANCE: Final[ConceptProvenanceReference] = _provenance(
    authority_section="Document 4, Sections 20–21",
    source_reference="document4:outward-expression-eligibility-reference-only",
    source_kind="outward_expression_eligibility_reference_authority",
)

NEW_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = (
    *LEXICAL_PROVENANCE_RECORDS,
    *SENSE_PROVENANCE_RECORDS,
    *MAPPING_PROVENANCE_RECORDS,
    OUTWARD_ELIGIBILITY_PROVENANCE,
)


CONCEPT_BY_KEY: Final[dict[str, object]] = {
    concept.concept_key: concept
    for concept in ADMITTED_CONCEPTS
}


def _lexical_reference(
    definition: LexicalReferenceDefinition,
    provenance: ConceptProvenanceReference,
    *,
    version: str,
    state: ConceptLifecycleState,
) -> ControlledLexicalReference:
    return with_recomputed_resource_id(
        ControlledLexicalReference(
            lexical_reference_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            exact_form=definition.exact_form,
            reference_kind=definition.reference_kind,
            language_tag=definition.language_tag,
            case_sensitive=definition.case_sensitive,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            scope_tags=definition.scope_tags,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def _three_stage_history(factory, definition, provenance):
    return (
        factory(
            definition,
            provenance,
            version="v1",
            state=ConceptLifecycleState.OBSERVED,
        ),
        factory(
            definition,
            provenance,
            version="v2",
            state=ConceptLifecycleState.CANDIDATE,
        ),
        factory(
            definition,
            provenance,
            version="v3",
            state=ConceptLifecycleState.ADMITTED,
        ),
    )


LEXICAL_REFERENCE_HISTORIES: Final[
    tuple[
        tuple[
            ControlledLexicalReference,
            ControlledLexicalReference,
            ControlledLexicalReference,
        ],
        ...,
    ]
] = tuple(
    _three_stage_history(
        _lexical_reference,
        definition,
        provenance,
    )
    for definition, provenance in zip(
        LEXICAL_REFERENCE_DEFINITIONS,
        LEXICAL_PROVENANCE_RECORDS,
        strict=True,
    )
)

CURRENT_LEXICAL_REFERENCES: Final[
    tuple[ControlledLexicalReference, ...]
] = tuple(history[-1] for history in LEXICAL_REFERENCE_HISTORIES)

LEXICAL_REFERENCE_BY_KEY: Final[
    dict[str, ControlledLexicalReference]
] = {
    definition.lexical_key: record
    for definition, record in zip(
        LEXICAL_REFERENCE_DEFINITIONS,
        CURRENT_LEXICAL_REFERENCES,
        strict=True,
    )
}


def _sense(
    definition: SenseDefinition,
    provenance: ConceptProvenanceReference,
    *,
    version: str,
    state: ConceptLifecycleState,
) -> ControlledSenseIdentity:
    concept = CONCEPT_BY_KEY[definition.concept_key]
    lexical_refs = tuple(
        LEXICAL_REFERENCE_BY_KEY[key].lexical_reference_id
        for key in definition.lexical_keys
    )

    return with_recomputed_resource_id(
        ControlledSenseIdentity(
            sense_id="",
            concept_id=concept.concept_id,
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            sense_key=definition.sense_key,
            definition=definition.definition,
            differentiation_basis=definition.differentiation_basis,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            lexical_reference_refs=lexical_refs,
            scope_tags=definition.scope_tags,
            permitted_uses=definition.permitted_uses,
            prohibited_uses=definition.prohibited_uses,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


SENSE_HISTORIES: Final[
    tuple[
        tuple[
            ControlledSenseIdentity,
            ControlledSenseIdentity,
            ControlledSenseIdentity,
        ],
        ...,
    ]
] = tuple(
    _three_stage_history(
        _sense,
        definition,
        provenance,
    )
    for definition, provenance in zip(
        SENSE_DEFINITIONS,
        SENSE_PROVENANCE_RECORDS,
        strict=True,
    )
)

CURRENT_SENSES: Final[tuple[ControlledSenseIdentity, ...]] = tuple(
    history[-1]
    for history in SENSE_HISTORIES
)

SENSE_BY_KEY: Final[dict[str, ControlledSenseIdentity]] = {
    definition.sense_key: record
    for definition, record in zip(
        SENSE_DEFINITIONS,
        CURRENT_SENSES,
        strict=True,
    )
}


def _mapping(
    definition: MappingDefinition,
    provenance: ConceptProvenanceReference,
    *,
    version: str,
    state: ConceptLifecycleState,
) -> TermConceptMappingIdentity:
    lexical_reference = LEXICAL_REFERENCE_BY_KEY[definition.lexical_key]

    return with_recomputed_resource_id(
        TermConceptMappingIdentity(
            mapping_id="",
            lexical_reference_id=lexical_reference.lexical_reference_id,
            namespace_scope=definition.namespace_scope,
            domain_scope=definition.domain_scope,
            concept_candidate_refs=tuple(
                CONCEPT_BY_KEY[key].concept_id
                for key in definition.concept_keys
            ),
            sense_candidate_refs=tuple(
                SENSE_BY_KEY[key].sense_id
                for key in definition.sense_keys
            ),
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            occurrence_interpretation_selected=False,
            selected_concept_ref=None,
            selected_sense_ref=None,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def _mapping_history(
    definition: MappingDefinition,
    provenance: ConceptProvenanceReference,
) -> tuple[
    TermConceptMappingIdentity,
    TermConceptMappingIdentity,
    TermConceptMappingIdentity,
]:
    return (
        _mapping(
            definition,
            provenance,
            version="v1",
            state=ConceptLifecycleState.OBSERVED,
        ),
        _mapping(
            definition,
            provenance,
            version="v2",
            state=ConceptLifecycleState.CANDIDATE,
        ),
        _mapping(
            definition,
            provenance,
            version="v3",
            state=definition.lifecycle_state,
        ),
    )


MAPPING_HISTORIES: Final[
    tuple[
        tuple[
            TermConceptMappingIdentity,
            TermConceptMappingIdentity,
            TermConceptMappingIdentity,
        ],
        ...,
    ]
] = tuple(
    _mapping_history(definition, provenance)
    for definition, provenance in zip(
        MAPPING_DEFINITIONS,
        MAPPING_PROVENANCE_RECORDS,
        strict=True,
    )
)

CURRENT_MAPPINGS: Final[tuple[TermConceptMappingIdentity, ...]] = tuple(
    history[-1]
    for history in MAPPING_HISTORIES
)

MAPPING_BY_KEY: Final[dict[str, TermConceptMappingIdentity]] = {
    definition.mapping_key: record
    for definition, record in zip(
        MAPPING_DEFINITIONS,
        CURRENT_MAPPINGS,
        strict=True,
    )
}


def _authority(
    source: GovernedConceptResource,
    target: GovernedConceptResource,
    provenance: ConceptProvenanceReference,
    *,
    final_review_complete: bool,
) -> ConceptLifecycleAuthorityRecord:
    return with_expected_authority_id(
        ConceptLifecycleAuthorityRecord(
            authority_id="",
            authority_provenance_ref=provenance.provenance_id,
            decision_owner_ref=SLICE37D_DECISION_OWNER_REF,
            human_approval_ref=SLICE37D_HUMAN_APPROVAL_REF,
            human_approved=True,
            reason=(
                "Preserve the explicit Slice 37D lifecycle transition from "
                f"{source.lifecycle_state.value} {source.version} to "
                f"{target.lifecycle_state.value} {target.version} for one "
                "bounded sense, lexical-reference, or exact mapping resource."
            ),
            scope=(
                target.scope_tags
                if hasattr(target, "scope_tags")
                else (
                    *target.namespace_scope,
                    *target.domain_scope,
                )
            ),
            affected_record_refs=(resource_id(source), resource_id(target)),
            prohibited_uses=SLICE37D_COMMON_PROHIBITED_USES,
            unresolved_dependency_refs=(),
            missing_authority_refs=(),
            conflict_review_complete=final_review_complete,
            unknown_state_review_complete=final_review_complete,
            later_dependency_review_complete=final_review_complete,
            non_llm_provenance=True,
            external_resource_decision_ref=None,
            runtime_authorized=False,
            implementation_authorized=False,
            registry_population_authorized=False,
        )
    )


def _transition(
    source: GovernedConceptResource,
    target: GovernedConceptResource,
    authority: ConceptLifecycleAuthorityRecord,
    *,
    kind: ConceptLifecycleTransitionKind,
) -> ConceptLifecycleTransitionRecord:
    return with_expected_transition_id(
        ConceptLifecycleTransitionRecord(
            transition_id="",
            lineage_id=expected_resource_lineage_id(source),
            resource_kind=source.resource_kind,
            source_resource_id=resource_id(source),
            target_resource_id=resource_id(target),
            source_version=source.version,
            target_version=target.version,
            from_state=source.lifecycle_state,
            to_state=target.lifecycle_state,
            transition_kind=kind,
            authority_record_ref=authority.authority_id,
            quarantine_cause_refs=(),
            quarantine_release_requirement_refs=(),
            resolved_quarantine_cause_refs=(),
            superseding_resource_ref=None,
            blocked_reentry_keys=(),
            verified_scope_refs=(),
            prior_disposition_transition_ref=None,
            historical_only_after_transition=False,
            prior_record_preserved=True,
            automatic_transition=False,
        )
    )


def _authorities_and_transitions(
    history: tuple[T, T, T],
    provenance: ConceptProvenanceReference,
) -> tuple[
    tuple[ConceptLifecycleAuthorityRecord, ConceptLifecycleAuthorityRecord],
    tuple[ConceptLifecycleTransitionRecord, ConceptLifecycleTransitionRecord],
]:
    observed, candidate, current = history

    observation_authority = _authority(
        observed,
        candidate,
        provenance,
        final_review_complete=False,
    )
    final_authority = _authority(
        candidate,
        current,
        provenance,
        final_review_complete=(
            current.lifecycle_state is ConceptLifecycleState.ADMITTED
        ),
    )

    final_kind = {
        ConceptLifecycleState.ADMITTED: ConceptLifecycleTransitionKind.ADMISSION,
        ConceptLifecycleState.AMBIGUOUS: (
            ConceptLifecycleTransitionKind.MARK_AMBIGUOUS
        ),
        ConceptLifecycleState.UNSUPPORTED: (
            ConceptLifecycleTransitionKind.MARK_UNSUPPORTED
        ),
    }[current.lifecycle_state]

    return (
        (observation_authority, final_authority),
        (
            _transition(
                observed,
                candidate,
                observation_authority,
                kind=ConceptLifecycleTransitionKind.OBSERVATION_REVIEW,
            ),
            _transition(
                candidate,
                current,
                final_authority,
                kind=final_kind,
            ),
        ),
    )


_NEW_HISTORY_PROVENANCE_GROUPS = (
    *zip(
        LEXICAL_REFERENCE_HISTORIES,
        LEXICAL_PROVENANCE_RECORDS,
        strict=True,
    ),
    *zip(
        SENSE_HISTORIES,
        SENSE_PROVENANCE_RECORDS,
        strict=True,
    ),
    *zip(
        MAPPING_HISTORIES,
        MAPPING_PROVENANCE_RECORDS,
        strict=True,
    ),
)

_NEW_AUTHORITY_TRANSITION_GROUPS = tuple(
    _authorities_and_transitions(history, provenance)
    for history, provenance in _NEW_HISTORY_PROVENANCE_GROUPS
)

NEW_AUTHORITIES: Final[
    tuple[ConceptLifecycleAuthorityRecord, ...]
] = tuple(
    authority
    for authorities, _ in _NEW_AUTHORITY_TRANSITION_GROUPS
    for authority in authorities
)

NEW_TRANSITIONS: Final[
    tuple[ConceptLifecycleTransitionRecord, ...]
] = tuple(
    transition
    for _, transitions in _NEW_AUTHORITY_TRANSITION_GROUPS
    for transition in transitions
)

NEW_RESOURCE_HISTORIES: Final[
    tuple[tuple[GovernedConceptResource, ...], ...]
] = (
    *LEXICAL_REFERENCE_HISTORIES,
    *SENSE_HISTORIES,
    *MAPPING_HISTORIES,
)

NEW_RESOURCES: Final[tuple[GovernedConceptResource, ...]] = tuple(
    resource
    for history in NEW_RESOURCE_HISTORIES
    for resource in history
)

GOVERNANCE_BATCH: Final[ConceptGovernanceBatch] = with_expected_batch_id(
    ConceptGovernanceBatch(
        batch_id="",
        provenance_records=(
            *SLICE37C_GOVERNANCE_BATCH.provenance_records,
            *NEW_PROVENANCE_RECORDS,
        ),
        resources=(
            *SLICE37C_GOVERNANCE_BATCH.resources,
            *NEW_RESOURCES,
        ),
        authority_records=(
            *SLICE37C_GOVERNANCE_BATCH.authority_records,
            *NEW_AUTHORITIES,
        ),
        transitions=(
            *SLICE37C_GOVERNANCE_BATCH.transitions,
            *NEW_TRANSITIONS,
        ),
        registry_population_installed=False,
        lookup_installed=False,
        occurrence_mapping_installed=False,
        sense_selection_installed=False,
        relation_instance_population_installed=False,
        structural_integration_installed=False,
        runtime_activation_installed=False,
    )
)


def _eligibility_for(
    lexical_key: str,
) -> OutwardExpressionEligibilityReference:
    lexical_reference = LEXICAL_REFERENCE_BY_KEY[lexical_key]
    mapping = MAPPING_BY_KEY[lexical_key]

    return with_expected_eligibility_id(
        OutwardExpressionEligibilityReference(
            eligibility_id="",
            lexical_reference_id=lexical_reference.lexical_reference_id,
            concept_ref=mapping.concept_candidate_refs[0],
            sense_ref=mapping.sense_candidate_refs[0],
            eligibility_state=(
                OutwardExpressionEligibilityState.ELIGIBLE_REFERENCE_ONLY
            ),
            reason=(
                "The exact Slice 37C preferred label is eligible to be "
                "referenced by later outward-expression planning. This record "
                "does not render, validate, release, or deliver language."
            ),
            version="v1",
            provenance_ref=OUTWARD_ELIGIBILITY_PROVENANCE.provenance_id,
            rendering_authorized=False,
            delivery_authorized=False,
            runtime_authorized=False,
            prohibited_authorities=SLICE37D_PROHIBITED_AUTHORITIES,
        )
    )


OUTWARD_ELIGIBILITY_REFERENCES: Final[
    tuple[OutwardExpressionEligibilityReference, ...]
] = tuple(
    _eligibility_for(key)
    for key in OUTWARD_ELIGIBLE_LEXICAL_KEYS
)


PROHIBITED_EXPANSION_REFUSALS: Final[
    tuple[MappingExpansionRefusal, ...]
] = tuple(
    with_expected_expansion_refusal_id(
        MappingExpansionRefusal(
            refusal_id="",
            expansion_kind=kind,
            allowed=False,
            reason=(
                f"{kind.value} is prohibited in Slice 37D. Exact term lookup "
                "must preserve missing, unmapped, ambiguous, and unsupported "
                "states rather than generating or ranking substitutes."
            ),
            prohibited_authorities=SLICE37D_PROHIBITED_AUTHORITIES,
        )
    )
    for kind in ProhibitedExpansionKind
)
