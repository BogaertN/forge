"""Deterministic immutable Slice 38D registry records."""

from __future__ import annotations

from typing import Final

from .authority import (
    ROLE_DEFINITIONS,
    ROLE_DEPENDENCY_REFS,
    ROLE_DISTINCTION_DEFINITIONS,
    SLICE38D_COMMON_PROHIBITED_USES,
    SLICE38D_DECISION_OWNER_REF,
    SLICE38D_HUMAN_APPROVAL_REF,
    SLICE38D_NAMESPACE_DEFINITION,
    SLICE38D_NAMESPACE_KEY,
    SLICE38D_NAMESPACE_LABEL,
    SLICE38D_NAMESPACE_NON_SCOPE,
    SLICE38D_NAMESPACE_PERMITTED_USES,
    SLICE38D_NAMESPACE_SCOPE,
)
from .identity import expected_lineage_id, with_expected_id
from .schema import (
    ParticipantRoleDependencyKind,
    ParticipantRoleDependencyRecord,
    ParticipantRoleIdentity,
    ParticipantRoleLifecycleAuthorityRecord,
    ParticipantRoleLifecycleState as S,
    ParticipantRoleLifecycleTransitionRecord,
    ParticipantRoleNamespaceIdentity,
    ParticipantRoleProvenanceReference,
    ParticipantRoleRelationshipKind,
    ParticipantRoleRelationshipRecord,
    ParticipantRoleResourceKind,
    ParticipantRoleTransitionKind,
)


_PROHIBITED_AUTHORITIES: Final[tuple[str, ...]] = (
    "no LLM, embedding, classifier, vector, RAG, or similarity authority",
    "no surface lookup, role assignment, frame completion, or selected meaning",
    "no evidence, memory, capability, route, tool, action, rendering, or delivery authority",
    "no external-resource runtime admission or implementation authority",
)

DOCUMENT5_PROVENANCE: Final[ParticipantRoleProvenanceReference] = with_expected_id(
    ParticipantRoleProvenanceReference(
        provenance_id="",
        authority_document="Document 5 — RMC Predicate–Role Frame Registry v1",
        authority_section="Sections 26–39, especially 29, 31, 32, 33, and 38",
        source_kind="permanent_architecture_authority",
        source_reference="google-drive:1yi9uWt69k74T4n_69weDM8qGaZjyAvCpbYl0-zCwVvQ",
        version="v1.0.0",
        non_llm_provenance=True,
        external_resource_admitted=False,
        runtime_loaded=False,
        implementation_authorized=False,
        prohibited_authorities=_PROHIBITED_AUTHORITIES,
    )
)
ROADMAP_PROVENANCE: Final[ParticipantRoleProvenanceReference] = with_expected_id(
    ParticipantRoleProvenanceReference(
        provenance_id="",
        authority_document="AI.Web Forge Canonical Production Roadmap v1.0",
        authority_section="Slice 38D — Participant-Role Identity and Registry",
        source_kind="canonical_implementation_sequence",
        source_reference="google-drive:1pdHY1KD8KlBT7vzWyUAp6zUVjJlM5ewoVnCMvV6yRiA",
        version="v1.0.0",
        non_llm_provenance=True,
        external_resource_admitted=False,
        runtime_loaded=False,
        implementation_authorized=False,
        prohibited_authorities=_PROHIBITED_AUTHORITIES,
    )
)
LIVE_SOURCE_PROVENANCE: Final[ParticipantRoleProvenanceReference] = with_expected_id(
    ParticipantRoleProvenanceReference(
        provenance_id="",
        authority_document="Slice 38C committed live source and R2 evidence",
        authority_section="HEAD 2a1830041c0ed8fbff8aa6ca3129385fce8e68f4",
        source_kind="verified_live_source_evidence",
        source_reference=(
            "source-packet:1e9d44dfbe256f2438baa24357b65741462b294b0ef120021a0cd73e8a59ee3e;"
            "slice38c-r2:58906489a9e6d429f0152b741165ee17a7ed59e2f2bdd18421f68e4e900f181c"
        ),
        version="v1.0.0",
        non_llm_provenance=True,
        external_resource_admitted=False,
        runtime_loaded=False,
        implementation_authorized=False,
        prohibited_authorities=_PROHIBITED_AUTHORITIES,
    )
)
PROVENANCE_RECORDS: Final[tuple[ParticipantRoleProvenanceReference, ...]] = (
    DOCUMENT5_PROVENANCE,
    ROADMAP_PROVENANCE,
    LIVE_SOURCE_PROVENANCE,
)
_PROVENANCE_REFS: Final[tuple[str, ...]] = tuple(
    record.provenance_id for record in PROVENANCE_RECORDS
)


def _namespace(version: str, state: S) -> ParticipantRoleNamespaceIdentity:
    return with_expected_id(
        ParticipantRoleNamespaceIdentity(
            namespace_id="",
            namespace_key=SLICE38D_NAMESPACE_KEY,
            preferred_label=SLICE38D_NAMESPACE_LABEL,
            definition=SLICE38D_NAMESPACE_DEFINITION,
            scope=SLICE38D_NAMESPACE_SCOPE,
            non_scope=SLICE38D_NAMESPACE_NON_SCOPE,
            version=version,
            lifecycle_state=state,
            provenance_refs=_PROVENANCE_REFS,
            permitted_uses=SLICE38D_NAMESPACE_PERMITTED_USES,
            prohibited_uses=SLICE38D_COMMON_PROHIBITED_USES,
            unknown_state_policy=(
                "Unknown, unresolved, ambiguous, unsupported, conflicted, quarantined, "
                "and deferred role material remains explicit and cannot be guessed."
            ),
        )
    )


NAMESPACE_HISTORY: Final[tuple[ParticipantRoleNamespaceIdentity, ...]] = (
    _namespace("v1.0.0", S.CANDIDATE),
    _namespace("v1.1.0", S.ARCHITECTURE_ADMITTED),
)
CURRENT_NAMESPACE: Final[ParticipantRoleNamespaceIdentity] = NAMESPACE_HISTORY[-1]


def _role(definition, version: str, state: S) -> ParticipantRoleIdentity:
    return with_expected_id(
        ParticipantRoleIdentity(
            role_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            role_key=definition.role_key,
            preferred_label=definition.preferred_label,
            role_category_key=definition.role_category_key,
            definition=definition.definition,
            scope=definition.scope,
            non_scope=definition.non_scope,
            version=version,
            lifecycle_state=state,
            provenance_refs=_PROVENANCE_REFS,
            frame_dependency_required=True,
            action_root_dependency_required=True,
            concept_compatibility_review_required=True,
            semantic_relation_separation_required=True,
            grammar_separation_required=True,
            speech_act_separation_required=True,
            effect_boundary_review_required=True,
            authority_non_satisfaction_required=True,
            occurrence_assignment_allowed=False,
            role_selection_allowed=False,
            dependency_refs=(),
            relationship_refs=(),
            correction_refs=(),
            conflict_refs=(),
            unknown_state_policy=(
                f"Unknown or ambiguous uses resembling {definition.role_key!r} remain "
                "unassigned and are not coerced to this role."
            ),
            permitted_uses=definition.permitted_uses,
            prohibited_uses=definition.prohibited_uses,
        )
    )


_BASE_ROLE_HISTORIES = tuple(
    (
        _role(definition, "v1.0.0", S.CANDIDATE),
        _role(definition, "v1.1.0", S.ARCHITECTURE_ADMITTED),
    )
    for definition in ROLE_DEFINITIONS
)
_BASE_ADMITTED_ROLES = tuple(history[-1] for history in _BASE_ROLE_HISTORIES)
_ROLE_BY_KEY = {record.role_key: record for record in _BASE_ADMITTED_ROLES}


def _dependency(role: ParticipantRoleIdentity, version: str, state: S) -> ParticipantRoleDependencyRecord:
    return with_expected_id(
        ParticipantRoleDependencyRecord(
            dependency_id="",
            dependency_key=f"{role.role_key}:governed-context-dependencies",
            role_id=role.role_id,
            dependency_kinds=(
                ParticipantRoleDependencyKind.PREDICATE_FRAME_CONTEXT_REQUIRED,
                ParticipantRoleDependencyKind.ACTION_ROOT_CONTEXT_REQUIRED,
                ParticipantRoleDependencyKind.CONCEPT_COMPATIBILITY_REVIEW_REQUIRED,
                ParticipantRoleDependencyKind.SPEECH_ACT_CONTEXT_REQUIRED,
                ParticipantRoleDependencyKind.EFFECT_BOUNDARY_REVIEW_REQUIRED,
            ),
            dependency_refs=ROLE_DEPENDENCY_REFS,
            definition=(
                f"The {role.role_key!r} role remains dependent on a licensing predicate "
                "frame, action-root context, concept-compatibility review, speech-act "
                "context, and effect-boundary review. Registry membership satisfies none."
            ),
            scope=(*SLICE38D_NAMESPACE_SCOPE, f"role-dependency:{role.role_key}"),
            non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "dependency satisfaction"),
            version=version,
            lifecycle_state=state,
            provenance_refs=_PROVENANCE_REFS,
            satisfied_by_role_identity=False,
            satisfied_by_registry_membership=False,
            runtime_authority_supplied=False,
            permitted_uses=("preserve explicit later-authority dependencies",),
            prohibited_uses=SLICE38D_COMMON_PROHIBITED_USES,
        )
    )


DEPENDENCY_HISTORIES: Final[tuple[tuple[ParticipantRoleDependencyRecord, ...], ...]] = tuple(
    (
        _dependency(role, "v1.0.0", S.CANDIDATE),
        _dependency(role, "v1.1.0", S.ARCHITECTURE_ADMITTED),
    )
    for role in _BASE_ADMITTED_ROLES
)
DEPENDENCIES: Final[tuple[ParticipantRoleDependencyRecord, ...]] = tuple(
    history[-1] for history in DEPENDENCY_HISTORIES
)
_DEPENDENCY_BY_ROLE_ID = {record.role_id: record for record in DEPENDENCIES}


def _relationship(definition, version: str, state: S) -> ParticipantRoleRelationshipRecord:
    return with_expected_id(
        ParticipantRoleRelationshipRecord(
            relationship_id="",
            relationship_key=definition.relationship_key,
            relationship_kind=ParticipantRoleRelationshipKind.MUST_REMAIN_DISTINCT,
            left_role_id=_ROLE_BY_KEY[definition.left_role_key].role_id,
            right_role_id=_ROLE_BY_KEY[definition.right_role_key].role_id,
            definition=definition.definition,
            scope=(*SLICE38D_NAMESPACE_SCOPE, "relationship:identity-distinction"),
            non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "role assignment or frame constraint"),
            version=version,
            lifecycle_state=state,
            provenance_refs=_PROVENANCE_REFS,
            role_assignment_performed=False,
            frame_constraint_created=False,
            permitted_uses=("preserve an exact must-remain-distinct role boundary",),
            prohibited_uses=SLICE38D_COMMON_PROHIBITED_USES,
        )
    )


RELATIONSHIP_HISTORIES: Final[tuple[tuple[ParticipantRoleRelationshipRecord, ...], ...]] = tuple(
    (
        _relationship(definition, "v1.0.0", S.CANDIDATE),
        _relationship(definition, "v1.1.0", S.ARCHITECTURE_ADMITTED),
    )
    for definition in ROLE_DISTINCTION_DEFINITIONS
)
RELATIONSHIPS: Final[tuple[ParticipantRoleRelationshipRecord, ...]] = tuple(
    history[-1] for history in RELATIONSHIP_HISTORIES
)
_RELATIONSHIP_IDS_BY_ROLE: dict[str, list[str]] = {role.role_id: [] for role in _BASE_ADMITTED_ROLES}
for relationship in RELATIONSHIPS:
    _RELATIONSHIP_IDS_BY_ROLE[relationship.left_role_id].append(relationship.relationship_id)
    _RELATIONSHIP_IDS_BY_ROLE[relationship.right_role_id].append(relationship.relationship_id)

# Rebuild role records once so dependency and relationship references are exact and immutable.
def _final_role(definition, version: str, state: S) -> ParticipantRoleIdentity:
    base = _role(definition, version, state)
    dependency = _DEPENDENCY_BY_ROLE_ID[_ROLE_BY_KEY[definition.role_key].role_id]
    # Dependency records point to the base final role identity. The final role carries
    # the dependency/relationship references but retains the same semantic lineage.
    return with_expected_id(
        ParticipantRoleIdentity(
            **{
                **base.to_dict(),
                "role_id": "",
                "dependency_refs": (dependency.dependency_id,),
                "relationship_refs": tuple(sorted(_RELATIONSHIP_IDS_BY_ROLE[base.role_id])),
            }
        )
    )


# Keep current identities equal to the base records to avoid circular stable IDs.
# References are represented from dependency/relationship records into roles; the
# role schema still supports reciprocal references for later corrected versions.
ROLE_HISTORIES: Final[tuple[tuple[ParticipantRoleIdentity, ...], ...]] = _BASE_ROLE_HISTORIES
ADMITTED_ROLES: Final[tuple[ParticipantRoleIdentity, ...]] = _BASE_ADMITTED_ROLES


_AFFECTED_REFS: Final[tuple[str, ...]] = (
    CURRENT_NAMESPACE.namespace_id,
    *(role.role_id for role in ADMITTED_ROLES),
    *(record.dependency_id for record in DEPENDENCIES),
    *(record.relationship_id for record in RELATIONSHIPS),
)

ADMISSION_AUTHORITY: Final[ParticipantRoleLifecycleAuthorityRecord] = with_expected_id(
    ParticipantRoleLifecycleAuthorityRecord(
        authority_id="",
        authority_provenance_refs=_PROVENANCE_REFS,
        decision_owner_ref=SLICE38D_DECISION_OWNER_REF,
        human_approval_ref=SLICE38D_HUMAN_APPROVAL_REF,
        human_approved=True,
        reason=(
            "Admit the exact closed Slice 38D role set and its identity-level "
            "dependencies and distinctions without occurrence role assignment."
        ),
        scope=SLICE38D_NAMESPACE_SCOPE,
        affected_record_refs=_AFFECTED_REFS,
        prohibited_uses=SLICE38D_COMMON_PROHIBITED_USES,
        unresolved_dependency_refs=ROLE_DEPENDENCY_REFS,
        conflict_review_complete=True,
        unknown_state_review_complete=True,
        version_review_complete=True,
        scope_non_scope_review_complete=True,
        provenance_review_complete=True,
        semantic_relation_boundary_review_complete=True,
        grammar_boundary_review_complete=True,
        concept_assignment_boundary_review_complete=True,
        source_span_actor_boundary_review_complete=True,
        non_llm_provenance=True,
        role_assignment_authorized=False,
        frame_completion_authorized=False,
        runtime_authorized=False,
        implementation_authorized=False,
        registry_population_authorized=True,
    )
)
AUTHORITY_RECORDS: Final[tuple[ParticipantRoleLifecycleAuthorityRecord, ...]] = (
    ADMISSION_AUTHORITY,
)


def _transition(source, target, affected_roles: tuple[str, ...]) -> ParticipantRoleLifecycleTransitionRecord:
    return with_expected_id(
        ParticipantRoleLifecycleTransitionRecord(
            transition_id="",
            lineage_id=expected_lineage_id(target),
            resource_kind=target.resource_kind,
            source_resource_id=(
                source.namespace_id if type(source) is ParticipantRoleNamespaceIdentity
                else source.role_id if type(source) is ParticipantRoleIdentity
                else source.dependency_id if type(source) is ParticipantRoleDependencyRecord
                else source.relationship_id
            ),
            target_resource_id=(
                target.namespace_id if type(target) is ParticipantRoleNamespaceIdentity
                else target.role_id if type(target) is ParticipantRoleIdentity
                else target.dependency_id if type(target) is ParticipantRoleDependencyRecord
                else target.relationship_id
            ),
            source_version=source.version,
            target_version=target.version,
            from_state=source.lifecycle_state,
            to_state=target.lifecycle_state,
            transition_kind=ParticipantRoleTransitionKind.ARCHITECTURE_ADMIT,
            authority_record_ref=ADMISSION_AUTHORITY.authority_id,
            reason="Explicit architecture admission with versioned ancestry preserved.",
            scope=SLICE38D_NAMESPACE_SCOPE,
            affected_role_refs=affected_roles,
            dependency_refs=ROLE_DEPENDENCY_REFS,
            correction_refs=(),
            conflict_refs=(),
            prior_record_preserved=True,
            automatic_transition=False,
            in_place_mutation_performed=False,
            nearest_known_substitution_performed=False,
            similarity_authority_used=False,
            role_assignment_performed=False,
            runtime_authority_supplied=False,
        )
    )


TRANSITIONS: Final[tuple[ParticipantRoleLifecycleTransitionRecord, ...]] = (
    _transition(NAMESPACE_HISTORY[0], NAMESPACE_HISTORY[1], ()),
    *(
        _transition(history[0], history[1], (history[1].role_id,))
        for history in ROLE_HISTORIES
    ),
    *(
        _transition(history[0], history[1], (history[1].role_id,))
        for history in DEPENDENCY_HISTORIES
    ),
    *(
        _transition(
            history[0],
            history[1],
            (history[1].left_role_id, history[1].right_role_id),
        )
        for history in RELATIONSHIP_HISTORIES
    ),
)

CORRECTIONS: Final[tuple[object, ...]] = ()
CONFLICTS: Final[tuple[object, ...]] = ()
