"""Static Slice 37C provenance, lifecycle history, and admitted records.

The governance batch proves semantic admission under Slice 37B law.  Its
registry-population flags remain false because semantic admission and installing
a read-only registry are separate authorities.  Slice 37C population authority
is carried by the separate registry manifest.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Final

from ..schema import (
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
    ControlledConceptIdentity,
)
from ..governed_lifecycle.identity import (
    expected_resource_lineage_id,
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
)
from .authority import (
    BUILT_IN_CONCEPT_DEFINITIONS,
    SLICE37C_COMMON_PROHIBITED_USES,
    SLICE37C_DECISION_OWNER_REF,
    SLICE37C_HUMAN_APPROVAL_REF,
    SLICE37C_NAMESPACE_DEFINITION,
    SLICE37C_NAMESPACE_KEY,
    SLICE37C_NAMESPACE_LABEL,
    SLICE37C_NAMESPACE_PERMITTED_USES,
    SLICE37C_NAMESPACE_SCOPE,
    SLICE37C_PROHIBITED_AUTHORITIES,
    BuiltInConceptDefinition,
)


def _with_provenance_id(
    record: ConceptProvenanceReference,
) -> ConceptProvenanceReference:
    return replace(
        record,
        provenance_id=record.expected_id(),
    )


def _provenance(
    *,
    authority_section: str,
    source_reference: str,
) -> ConceptProvenanceReference:
    return _with_provenance_id(
        ConceptProvenanceReference(
            provenance_id="",
            authority_document=(
                "Document 4 — RMC Concept Lexicon and Semantic Relation Graph v1"
            ),
            authority_section=authority_section,
            source_kind="permanent_architecture_authority",
            source_reference=source_reference,
            version="v1",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            prohibited_authorities=SLICE37C_PROHIBITED_AUTHORITIES,
        )
    )


NAMESPACE_PROVENANCE: Final[ConceptProvenanceReference] = _provenance(
    authority_section="Parts II–III, internal namespace and concept-admission law",
    source_reference="document4:internal-language-core-concept-namespace",
)

CONCEPT_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=definition.authority_section,
        source_reference=definition.source_reference,
    )
    for definition in BUILT_IN_CONCEPT_DEFINITIONS
)

PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = (
    NAMESPACE_PROVENANCE,
    *CONCEPT_PROVENANCE_RECORDS,
)


def _namespace(
    *,
    version: str,
    state: ConceptLifecycleState,
) -> ConceptNamespaceIdentity:
    return with_recomputed_resource_id(
        ConceptNamespaceIdentity(
            namespace_id="",
            namespace_key=SLICE37C_NAMESPACE_KEY,
            label=SLICE37C_NAMESPACE_LABEL,
            definition=SLICE37C_NAMESPACE_DEFINITION,
            version=version,
            lifecycle_state=state,
            provenance_ref=NAMESPACE_PROVENANCE.provenance_id,
            scope_tags=SLICE37C_NAMESPACE_SCOPE,
            permitted_uses=SLICE37C_NAMESPACE_PERMITTED_USES,
            prohibited_uses=SLICE37C_COMMON_PROHIBITED_USES,
            prohibited_authorities=SLICE37C_PROHIBITED_AUTHORITIES,
        )
    )


NAMESPACE_OBSERVED: Final[ConceptNamespaceIdentity] = _namespace(
    version="v1",
    state=ConceptLifecycleState.OBSERVED,
)
NAMESPACE_CANDIDATE: Final[ConceptNamespaceIdentity] = _namespace(
    version="v2",
    state=ConceptLifecycleState.CANDIDATE,
)
CURRENT_NAMESPACE: Final[ConceptNamespaceIdentity] = _namespace(
    version="v3",
    state=ConceptLifecycleState.ARCHITECTURE_ADMITTED,
)

NAMESPACE_HISTORY: Final[tuple[ConceptNamespaceIdentity, ...]] = (
    NAMESPACE_OBSERVED,
    NAMESPACE_CANDIDATE,
    CURRENT_NAMESPACE,
)


def _concept(
    definition: BuiltInConceptDefinition,
    provenance: ConceptProvenanceReference,
    *,
    version: str,
    state: ConceptLifecycleState,
) -> ControlledConceptIdentity:
    return with_recomputed_resource_id(
        ControlledConceptIdentity(
            concept_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            concept_key=definition.concept_key,
            preferred_label=definition.preferred_label,
            definition=definition.definition,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            semantic_class_refs=(),
            sense_refs=(),
            relation_type_refs=(),
            scope_tags=definition.scope_tags,
            permitted_uses=definition.permitted_uses,
            prohibited_uses=definition.prohibited_uses,
            prohibited_authorities=definition.prohibited_authorities,
        )
    )


def _concept_history(
    definition: BuiltInConceptDefinition,
    provenance: ConceptProvenanceReference,
) -> tuple[
    ControlledConceptIdentity,
    ControlledConceptIdentity,
    ControlledConceptIdentity,
]:
    return (
        _concept(
            definition,
            provenance,
            version="v1",
            state=ConceptLifecycleState.OBSERVED,
        ),
        _concept(
            definition,
            provenance,
            version="v2",
            state=ConceptLifecycleState.CANDIDATE,
        ),
        _concept(
            definition,
            provenance,
            version="v3",
            state=ConceptLifecycleState.ADMITTED,
        ),
    )


CONCEPT_HISTORIES: Final[
    tuple[
        tuple[
            ControlledConceptIdentity,
            ControlledConceptIdentity,
            ControlledConceptIdentity,
        ],
        ...,
    ]
] = tuple(
    _concept_history(definition, provenance)
    for definition, provenance in zip(
        BUILT_IN_CONCEPT_DEFINITIONS,
        CONCEPT_PROVENANCE_RECORDS,
        strict=True,
    )
)

ADMITTED_CONCEPTS: Final[
    tuple[ControlledConceptIdentity, ...]
] = tuple(
    history[-1]
    for history in CONCEPT_HISTORIES
)


def _authority(
    source: ConceptNamespaceIdentity | ControlledConceptIdentity,
    target: ConceptNamespaceIdentity | ControlledConceptIdentity,
    provenance: ConceptProvenanceReference,
    *,
    review_complete: bool,
) -> ConceptLifecycleAuthorityRecord:
    return with_expected_authority_id(
        ConceptLifecycleAuthorityRecord(
            authority_id="",
            authority_provenance_ref=provenance.provenance_id,
            decision_owner_ref=SLICE37C_DECISION_OWNER_REF,
            human_approval_ref=SLICE37C_HUMAN_APPROVAL_REF,
            human_approved=True,
            reason=(
                "Preserve the explicit Slice 37C lifecycle transition from "
                f"{source.lifecycle_state.value} {source.version} to "
                f"{target.lifecycle_state.value} {target.version} for one "
                "bounded Document 4 semantic resource."
            ),
            scope=target.scope_tags,
            affected_record_refs=(
                source.namespace_id
                if isinstance(source, ConceptNamespaceIdentity)
                else source.concept_id,
                target.namespace_id
                if isinstance(target, ConceptNamespaceIdentity)
                else target.concept_id,
            ),
            prohibited_uses=(
                "runtime activation",
                "silent semantic expansion",
                "registry population without the separate Slice 37C manifest",
            ),
            unresolved_dependency_refs=(),
            missing_authority_refs=(),
            conflict_review_complete=review_complete,
            unknown_state_review_complete=review_complete,
            later_dependency_review_complete=review_complete,
            non_llm_provenance=True,
            external_resource_decision_ref=None,
            runtime_authorized=False,
            implementation_authorized=False,
            registry_population_authorized=False,
        )
    )


def _transition(
    source: ConceptNamespaceIdentity | ControlledConceptIdentity,
    target: ConceptNamespaceIdentity | ControlledConceptIdentity,
    authority: ConceptLifecycleAuthorityRecord,
    *,
    kind: ConceptLifecycleTransitionKind,
) -> ConceptLifecycleTransitionRecord:
    source_id = (
        source.namespace_id
        if isinstance(source, ConceptNamespaceIdentity)
        else source.concept_id
    )
    target_id = (
        target.namespace_id
        if isinstance(target, ConceptNamespaceIdentity)
        else target.concept_id
    )
    return with_expected_transition_id(
        ConceptLifecycleTransitionRecord(
            transition_id="",
            lineage_id=expected_resource_lineage_id(source),
            resource_kind=source.resource_kind,
            source_resource_id=source_id,
            target_resource_id=target_id,
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


_NAMESPACE_OBSERVATION_AUTHORITY = _authority(
    NAMESPACE_OBSERVED,
    NAMESPACE_CANDIDATE,
    NAMESPACE_PROVENANCE,
    review_complete=False,
)
_NAMESPACE_ADMISSION_AUTHORITY = _authority(
    NAMESPACE_CANDIDATE,
    CURRENT_NAMESPACE,
    NAMESPACE_PROVENANCE,
    review_complete=True,
)

NAMESPACE_AUTHORITIES: Final[
    tuple[ConceptLifecycleAuthorityRecord, ...]
] = (
    _NAMESPACE_OBSERVATION_AUTHORITY,
    _NAMESPACE_ADMISSION_AUTHORITY,
)

NAMESPACE_TRANSITIONS: Final[
    tuple[ConceptLifecycleTransitionRecord, ...]
] = (
    _transition(
        NAMESPACE_OBSERVED,
        NAMESPACE_CANDIDATE,
        _NAMESPACE_OBSERVATION_AUTHORITY,
        kind=ConceptLifecycleTransitionKind.OBSERVATION_REVIEW,
    ),
    _transition(
        NAMESPACE_CANDIDATE,
        CURRENT_NAMESPACE,
        _NAMESPACE_ADMISSION_AUTHORITY,
        kind=ConceptLifecycleTransitionKind.ARCHITECTURE_ADMISSION,
    ),
)


def _concept_authorities_and_transitions(
    history: tuple[
        ControlledConceptIdentity,
        ControlledConceptIdentity,
        ControlledConceptIdentity,
    ],
    provenance: ConceptProvenanceReference,
) -> tuple[
    tuple[ConceptLifecycleAuthorityRecord, ...],
    tuple[ConceptLifecycleTransitionRecord, ...],
]:
    observed, candidate, admitted = history

    observation_authority = _authority(
        observed,
        candidate,
        provenance,
        review_complete=False,
    )
    admission_authority = _authority(
        candidate,
        admitted,
        provenance,
        review_complete=True,
    )

    return (
        (
            observation_authority,
            admission_authority,
        ),
        (
            _transition(
                observed,
                candidate,
                observation_authority,
                kind=ConceptLifecycleTransitionKind.OBSERVATION_REVIEW,
            ),
            _transition(
                candidate,
                admitted,
                admission_authority,
                kind=ConceptLifecycleTransitionKind.ADMISSION,
            ),
        ),
    )


_CONCEPT_AUTHORITY_TRANSITION_GROUPS = tuple(
    _concept_authorities_and_transitions(history, provenance)
    for history, provenance in zip(
        CONCEPT_HISTORIES,
        CONCEPT_PROVENANCE_RECORDS,
        strict=True,
    )
)

CONCEPT_AUTHORITIES: Final[
    tuple[ConceptLifecycleAuthorityRecord, ...]
] = tuple(
    authority
    for authorities, _ in _CONCEPT_AUTHORITY_TRANSITION_GROUPS
    for authority in authorities
)

CONCEPT_TRANSITIONS: Final[
    tuple[ConceptLifecycleTransitionRecord, ...]
] = tuple(
    transition
    for _, transitions in _CONCEPT_AUTHORITY_TRANSITION_GROUPS
    for transition in transitions
)

ALL_RESOURCES: Final[
    tuple[ConceptNamespaceIdentity | ControlledConceptIdentity, ...]
] = (
    *NAMESPACE_HISTORY,
    *(
        resource
        for history in CONCEPT_HISTORIES
        for resource in history
    ),
)

ALL_AUTHORITIES: Final[
    tuple[ConceptLifecycleAuthorityRecord, ...]
] = (
    *NAMESPACE_AUTHORITIES,
    *CONCEPT_AUTHORITIES,
)

ALL_TRANSITIONS: Final[
    tuple[ConceptLifecycleTransitionRecord, ...]
] = (
    *NAMESPACE_TRANSITIONS,
    *CONCEPT_TRANSITIONS,
)

GOVERNANCE_BATCH: Final[ConceptGovernanceBatch] = with_expected_batch_id(
    ConceptGovernanceBatch(
        batch_id="",
        provenance_records=PROVENANCE_RECORDS,
        resources=ALL_RESOURCES,
        authority_records=ALL_AUTHORITIES,
        transitions=ALL_TRANSITIONS,
        registry_population_installed=False,
        lookup_installed=False,
        occurrence_mapping_installed=False,
        sense_selection_installed=False,
        relation_instance_population_installed=False,
        structural_integration_installed=False,
        runtime_activation_installed=False,
    )
)
