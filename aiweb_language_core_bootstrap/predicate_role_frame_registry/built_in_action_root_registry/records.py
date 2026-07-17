"""Static Slice 38C provenance, lifecycle histories, and admitted records.

The Slice 38B governance batch proves identity, provenance, version, and
lifecycle admission while keeping registry population false.  Population of
the closed read-only registry is authorized only by the separate Slice 38C
manifest in :mod:`registry`.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Final

from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
)
from ..governed_lifecycle.identity import (
    expected_resource_lineage_id,
    with_expected_authority_id,
    with_expected_batch_id,
    with_expected_transition_id,
    with_recomputed_resource_id,
)
from ..governed_lifecycle.schema import (
    GovernedPredicateResource,
    PredicateGovernanceBatch,
    PredicateLifecycleAuthorityRecord,
    PredicateLifecycleTransitionKind,
    PredicateLifecycleTransitionRecord,
)
from .authority import (
    BUILT_IN_ACTION_ROOT_DEFINITIONS,
    SLICE38C_COMMON_PROHIBITED_USES,
    SLICE38C_DECISION_OWNER_REF,
    SLICE38C_HUMAN_APPROVAL_REF,
    SLICE38C_NAMESPACE_DEFINITION,
    SLICE38C_NAMESPACE_KEY,
    SLICE38C_NAMESPACE_LABEL,
    SLICE38C_NAMESPACE_NON_SCOPE,
    SLICE38C_NAMESPACE_PERMITTED_USES,
    SLICE38C_NAMESPACE_SCOPE,
    SLICE38C_PROHIBITED_AUTHORITIES,
    BuiltInActionRootDefinition,
)


def _with_provenance_id(
    record: PredicateProvenanceReference,
) -> PredicateProvenanceReference:
    return replace(record, provenance_id=record.expected_id())


def _provenance(
    *,
    authority_section: str,
    source_reference: str,
) -> PredicateProvenanceReference:
    return _with_provenance_id(
        PredicateProvenanceReference(
            provenance_id="",
            authority_document=(
                "Document 5 — RMC Predicate–Role Frame Registry v1"
            ),
            authority_section=authority_section,
            source_kind="permanent_architecture_authority",
            source_reference=source_reference,
            version="v1",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=False,
            prohibited_authorities=SLICE38C_PROHIBITED_AUTHORITIES,
        )
    )


NAMESPACE_PROVENANCE: Final[PredicateProvenanceReference] = _provenance(
    authority_section="Sections 22 through 25, controlled admission and predicate identity",
    source_reference="document5:predicate-role-frame:internal-action-root-namespace",
)
ACTION_ROOT_PROVENANCE_RECORDS: Final[
    tuple[PredicateProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=definition.authority_section,
        source_reference=definition.source_reference,
    )
    for definition in BUILT_IN_ACTION_ROOT_DEFINITIONS
)
PROVENANCE_RECORDS: Final[tuple[PredicateProvenanceReference, ...]] = (
    NAMESPACE_PROVENANCE,
    *ACTION_ROOT_PROVENANCE_RECORDS,
)


def _namespace(
    *,
    version: str,
    state: PredicateLifecycleState,
) -> PredicateNamespaceIdentity:
    return with_recomputed_resource_id(
        PredicateNamespaceIdentity(
            namespace_id="",
            namespace_key=SLICE38C_NAMESPACE_KEY,
            label=SLICE38C_NAMESPACE_LABEL,
            definition=SLICE38C_NAMESPACE_DEFINITION,
            scope=SLICE38C_NAMESPACE_SCOPE,
            non_scope=SLICE38C_NAMESPACE_NON_SCOPE,
            version=version,
            lifecycle_state=state,
            provenance_ref=NAMESPACE_PROVENANCE.provenance_id,
            permitted_uses=SLICE38C_NAMESPACE_PERMITTED_USES,
            prohibited_uses=SLICE38C_COMMON_PROHIBITED_USES,
            unknown_state_policy=(
                "Unlisted or unsupported action-like material remains unknown, "
                "unsupported, ambiguous, or unresolved and is never mapped to "
                "the nearest built-in action root."
            ),
            prohibited_authorities=SLICE38C_PROHIBITED_AUTHORITIES,
        )
    )


NAMESPACE_OBSERVED: Final[PredicateNamespaceIdentity] = _namespace(
    version="v1.0.0",
    state=PredicateLifecycleState.OBSERVED,
)
NAMESPACE_CANDIDATE: Final[PredicateNamespaceIdentity] = _namespace(
    version="v1.1.0",
    state=PredicateLifecycleState.CANDIDATE,
)
NAMESPACE_REVIEWED: Final[PredicateNamespaceIdentity] = _namespace(
    version="v1.2.0",
    state=PredicateLifecycleState.REVIEWED,
)
CURRENT_NAMESPACE: Final[PredicateNamespaceIdentity] = _namespace(
    version="v1.3.0",
    state=PredicateLifecycleState.ARCHITECTURE_ADMITTED,
)
NAMESPACE_HISTORY: Final[tuple[PredicateNamespaceIdentity, ...]] = (
    NAMESPACE_OBSERVED,
    NAMESPACE_CANDIDATE,
    NAMESPACE_REVIEWED,
    CURRENT_NAMESPACE,
)


def _action_root(
    definition: BuiltInActionRootDefinition,
    provenance: PredicateProvenanceReference,
    *,
    version: str,
    state: PredicateLifecycleState,
) -> ActionRootIdentity:
    return with_recomputed_resource_id(
        ActionRootIdentity(
            action_root_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            action_root_key=definition.action_root_key,
            preferred_label=definition.preferred_label,
            definition=definition.definition,
            scope=definition.scope,
            non_scope=definition.non_scope,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            concept_identity_refs=(),
            frame_dependency_required=True,
            participant_role_dependency_required=True,
            speech_act_separation_required=True,
            effect_boundary_dependency_required=True,
            capability_non_invocation_required=True,
            occurrence_selection_allowed=False,
            execution_authorized=False,
            unknown_state_policy=(
                "Unknown, unsupported, ambiguous, conflicted, or unlisted "
                "action-like expressions remain explicit and are not coerced "
                f"to the {definition.action_root_key!r} root."
            ),
            permitted_uses=definition.permitted_uses,
            prohibited_uses=definition.prohibited_uses,
            prohibited_authorities=definition.prohibited_authorities,
        )
    )


def _action_root_history(
    definition: BuiltInActionRootDefinition,
    provenance: PredicateProvenanceReference,
) -> tuple[
    ActionRootIdentity,
    ActionRootIdentity,
    ActionRootIdentity,
    ActionRootIdentity,
]:
    return (
        _action_root(
            definition,
            provenance,
            version="v1.0.0",
            state=PredicateLifecycleState.OBSERVED,
        ),
        _action_root(
            definition,
            provenance,
            version="v1.1.0",
            state=PredicateLifecycleState.CANDIDATE,
        ),
        _action_root(
            definition,
            provenance,
            version="v1.2.0",
            state=PredicateLifecycleState.REVIEWED,
        ),
        _action_root(
            definition,
            provenance,
            version="v1.3.0",
            state=PredicateLifecycleState.ADMITTED,
        ),
    )


ACTION_ROOT_HISTORIES: Final[
    tuple[
        tuple[
            ActionRootIdentity,
            ActionRootIdentity,
            ActionRootIdentity,
            ActionRootIdentity,
        ],
        ...,
    ]
] = tuple(
    _action_root_history(definition, provenance)
    for definition, provenance in zip(
        BUILT_IN_ACTION_ROOT_DEFINITIONS,
        ACTION_ROOT_PROVENANCE_RECORDS,
        strict=True,
    )
)
ADMITTED_ACTION_ROOTS: Final[tuple[ActionRootIdentity, ...]] = tuple(
    history[-1] for history in ACTION_ROOT_HISTORIES
)


def _predicate(
    definition: BuiltInActionRootDefinition,
    action_root: ActionRootIdentity,
    provenance: PredicateProvenanceReference,
    *,
    version: str,
    state: PredicateLifecycleState,
) -> PredicateIdentity:
    return with_recomputed_resource_id(
        PredicateIdentity(
            predicate_id="",
            action_root_id=action_root.action_root_id,
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            predicate_key=definition.predicate_key,
            preferred_label=f"{definition.preferred_label} Predicate Identity",
            definition=(
                "The controlled predicate identity corresponding exactly to the "
                f"{definition.action_root_key!r} action-root record. It carries "
                "identity and dependency boundaries only and remains unselected "
                "for every source occurrence."
            ),
            scope=definition.scope,
            non_scope=definition.non_scope,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            concept_identity_refs=(),
            participant_role_schema_refs=(),
            predicate_frame_schema_refs=(),
            effect_boundary_refs=(),
            capability_family_reference_refs=(),
            participant_role_dependency_required=True,
            predicate_frame_dependency_required=True,
            speech_act_separation_required=True,
            capability_non_invocation_required=True,
            occurrence_selection_allowed=False,
            selected_for_occurrence=False,
            execution_authorized=False,
            unknown_state_policy=(
                "No occurrence is selected by registry membership. Unknown or "
                "unsupported material remains explicit and cannot fall back to "
                f"the {definition.action_root_key!r} predicate identity."
            ),
            permitted_uses=definition.permitted_uses,
            prohibited_uses=definition.prohibited_uses,
            prohibited_authorities=definition.prohibited_authorities,
        )
    )


def _predicate_history(
    definition: BuiltInActionRootDefinition,
    action_root: ActionRootIdentity,
    provenance: PredicateProvenanceReference,
) -> tuple[
    PredicateIdentity,
    PredicateIdentity,
    PredicateIdentity,
    PredicateIdentity,
]:
    return (
        _predicate(
            definition,
            action_root,
            provenance,
            version="v1.0.0",
            state=PredicateLifecycleState.OBSERVED,
        ),
        _predicate(
            definition,
            action_root,
            provenance,
            version="v1.1.0",
            state=PredicateLifecycleState.CANDIDATE,
        ),
        _predicate(
            definition,
            action_root,
            provenance,
            version="v1.2.0",
            state=PredicateLifecycleState.REVIEWED,
        ),
        _predicate(
            definition,
            action_root,
            provenance,
            version="v1.3.0",
            state=PredicateLifecycleState.ADMITTED,
        ),
    )


PREDICATE_HISTORIES: Final[
    tuple[
        tuple[
            PredicateIdentity,
            PredicateIdentity,
            PredicateIdentity,
            PredicateIdentity,
        ],
        ...,
    ]
] = tuple(
    _predicate_history(definition, action_root, provenance)
    for definition, action_root, provenance in zip(
        BUILT_IN_ACTION_ROOT_DEFINITIONS,
        ADMITTED_ACTION_ROOTS,
        ACTION_ROOT_PROVENANCE_RECORDS,
        strict=True,
    )
)
ADMITTED_PREDICATES: Final[tuple[PredicateIdentity, ...]] = tuple(
    history[-1] for history in PREDICATE_HISTORIES
)


def _record_id(record: GovernedPredicateResource) -> str:
    if isinstance(record, PredicateNamespaceIdentity):
        return record.namespace_id
    if isinstance(record, ActionRootIdentity):
        return record.action_root_id
    if isinstance(record, PredicateIdentity):
        return record.predicate_id
    raise TypeError(type(record).__name__)


def _authority(
    source: GovernedPredicateResource,
    target: GovernedPredicateResource,
    provenance: PredicateProvenanceReference,
    *,
    review_complete: bool,
) -> PredicateLifecycleAuthorityRecord:
    return with_expected_authority_id(
        PredicateLifecycleAuthorityRecord(
            authority_id="",
            authority_provenance_ref=provenance.provenance_id,
            decision_owner_ref=SLICE38C_DECISION_OWNER_REF,
            human_approval_ref=SLICE38C_HUMAN_APPROVAL_REF,
            human_approved=True,
            reason=(
                "Preserve the explicit Slice 38C lifecycle transition from "
                f"{source.lifecycle_state.value} {source.version} to "
                f"{target.lifecycle_state.value} {target.version} for one "
                "bounded Document 5 predicate resource."
            ),
            scope=target.scope,
            affected_record_refs=(_record_id(source), _record_id(target)),
            prohibited_uses=(
                "surface or occurrence-level action-root selection",
                "capability routing, invocation, or execution",
                "registry population without the separate Slice 38C manifest",
            ),
            unresolved_dependency_refs=(),
            missing_authority_refs=(),
            conflict_review_complete=review_complete,
            unknown_state_review_complete=review_complete,
            later_dependency_review_complete=review_complete,
            version_compatibility_review_complete=True,
            scope_non_scope_review_complete=True,
            provenance_review_complete=True,
            lifecycle_review_complete=True,
            non_llm_provenance=True,
            nearest_known_substitution_allowed=False,
            semantic_similarity_authority_allowed=False,
            runtime_authorized=False,
            implementation_authorized=False,
            registry_population_authorized=False,
        )
    )


def _transition(
    source: GovernedPredicateResource,
    target: GovernedPredicateResource,
    authority: PredicateLifecycleAuthorityRecord,
    *,
    kind: PredicateLifecycleTransitionKind,
) -> PredicateLifecycleTransitionRecord:
    return with_expected_transition_id(
        PredicateLifecycleTransitionRecord(
            transition_id="",
            lineage_id=expected_resource_lineage_id(source),
            resource_kind=source.resource_kind,
            source_resource_id=_record_id(source),
            target_resource_id=_record_id(target),
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
            prior_disposition_transition_ref=None,
            prior_record_preserved=True,
            automatic_transition=False,
            in_place_mutation_performed=False,
            nearest_known_substitution_performed=False,
            similarity_authority_used=False,
        )
    )


def _history_authorities_and_transitions(
    history: tuple[GovernedPredicateResource, ...],
    provenance: PredicateProvenanceReference,
    *,
    final_kind: PredicateLifecycleTransitionKind,
) -> tuple[
    tuple[PredicateLifecycleAuthorityRecord, ...],
    tuple[PredicateLifecycleTransitionRecord, ...],
]:
    if len(history) != 4:
        raise ValueError("Slice 38C histories must contain exactly four versions")

    observed, candidate, reviewed, final = history
    proposal_authority = _authority(
        observed,
        candidate,
        provenance,
        review_complete=False,
    )
    review_authority = _authority(
        candidate,
        reviewed,
        provenance,
        review_complete=True,
    )
    admission_authority = _authority(
        reviewed,
        final,
        provenance,
        review_complete=True,
    )
    return (
        (proposal_authority, review_authority, admission_authority),
        (
            _transition(
                observed,
                candidate,
                proposal_authority,
                kind=PredicateLifecycleTransitionKind.PROPOSAL,
            ),
            _transition(
                candidate,
                reviewed,
                review_authority,
                kind=PredicateLifecycleTransitionKind.REVIEW,
            ),
            _transition(
                reviewed,
                final,
                admission_authority,
                kind=final_kind,
            ),
        ),
    )


_NAMESPACE_GROUP = _history_authorities_and_transitions(
    NAMESPACE_HISTORY,
    NAMESPACE_PROVENANCE,
    final_kind=PredicateLifecycleTransitionKind.ARCHITECTURE_ADMISSION,
)
_ACTION_ROOT_GROUPS = tuple(
    _history_authorities_and_transitions(
        history,
        provenance,
        final_kind=PredicateLifecycleTransitionKind.ADMISSION,
    )
    for history, provenance in zip(
        ACTION_ROOT_HISTORIES,
        ACTION_ROOT_PROVENANCE_RECORDS,
        strict=True,
    )
)
_PREDICATE_GROUPS = tuple(
    _history_authorities_and_transitions(
        history,
        provenance,
        final_kind=PredicateLifecycleTransitionKind.ADMISSION,
    )
    for history, provenance in zip(
        PREDICATE_HISTORIES,
        ACTION_ROOT_PROVENANCE_RECORDS,
        strict=True,
    )
)

ALL_RESOURCES: Final[tuple[GovernedPredicateResource, ...]] = (
    *NAMESPACE_HISTORY,
    *(resource for history in ACTION_ROOT_HISTORIES for resource in history),
    *(resource for history in PREDICATE_HISTORIES for resource in history),
)
ALL_AUTHORITIES: Final[tuple[PredicateLifecycleAuthorityRecord, ...]] = (
    *_NAMESPACE_GROUP[0],
    *(authority for group in _ACTION_ROOT_GROUPS for authority in group[0]),
    *(authority for group in _PREDICATE_GROUPS for authority in group[0]),
)
ALL_TRANSITIONS: Final[tuple[PredicateLifecycleTransitionRecord, ...]] = (
    *_NAMESPACE_GROUP[1],
    *(transition for group in _ACTION_ROOT_GROUPS for transition in group[1]),
    *(transition for group in _PREDICATE_GROUPS for transition in group[1]),
)

GOVERNANCE_BATCH: Final[PredicateGovernanceBatch] = with_expected_batch_id(
    PredicateGovernanceBatch(
        batch_id="",
        provenance_records=PROVENANCE_RECORDS,
        resources=ALL_RESOURCES,
        authority_records=ALL_AUTHORITIES,
        transitions=ALL_TRANSITIONS,
        registry_population_installed=False,
        action_root_lookup_installed=False,
        predicate_selection_installed=False,
        nearest_known_mapping_installed=False,
        semantic_similarity_installed=False,
        capability_routing_installed=False,
        runtime_activation_installed=False,
    )
)
