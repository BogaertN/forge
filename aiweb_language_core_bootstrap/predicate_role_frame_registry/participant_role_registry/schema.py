"""Immutable Slice 38D participant-role registry contracts.

The records in this module represent controlled participant-role identity,
role-governance dependencies, role-distinction relationships, lifecycle
ancestry, correction records, and conflict records.  They do not assign a
role to source text, select meaning, complete a predicate frame, validate
evidence, bind a capability, invoke a route or tool, execute an action,
access memory, render output, or authorize delivery.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final, TypeAlias

from ...schema import stable_record_id


SLICE38D_SPEC_ID: Final[str] = "aiweb-slice38d-participant-role-identity-registry"
SLICE38D_SPEC_VERSION: Final[str] = (
    "aiweb-slice38d-participant-role-identity-registry-v1"
)
SLICE38D_SCHEMA_VERSION: Final[str] = (
    "aiweb-participant-role-identity-registry-schema-v1"
)
SLICE38D_ACCEPTED_PARENT_HEAD: Final[str] = (
    "2a1830041c0ed8fbff8aa6ca3129385fce8e68f4"
)
SLICE38D_ACCEPTED_PARENT_TREE: Final[str] = (
    "020866a5ba8a41a2485a08cd0333d75ce246ac1a"
)
SLICE38D_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 38C minimal built-in action-root registry"
)
SLICE38D_SOURCE_AUTHORITY_PACKET_SHA256: Final[str] = (
    "1e9d44dfbe256f2438baa24357b65741462b294b0ef120021a0cd73e8a59ee3e"
)
SLICE38D_SLICE38C_R2_EVIDENCE_SHA256: Final[str] = (
    "58906489a9e6d429f0152b741165ee17a7ed59e2f2bdd18421f68e4e900f181c"
)


class ParticipantRoleLifecycleState(str, Enum):
    OBSERVED = "observed"
    CANDIDATE = "candidate"
    ADMITTED = "admitted"
    ARCHITECTURE_ADMITTED = "architecture_admitted"
    OPERATIONALLY_BOUNDED = "operationally_bounded"
    IMPLEMENTATION_DEFERRED = "implementation_deferred"
    UNKNOWN = "unknown"
    UNRESOLVED = "unresolved"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    QUARANTINED = "quarantined"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"
    NON_CONFORMING = "non_conforming"
    REVIEW_REQUIRED = "review_required"


class ParticipantRoleResourceKind(str, Enum):
    PROVENANCE_REFERENCE = "provenance_reference"
    NAMESPACE_IDENTITY = "namespace_identity"
    PARTICIPANT_ROLE_IDENTITY = "participant_role_identity"
    ROLE_DEPENDENCY = "role_dependency"
    ROLE_RELATIONSHIP = "role_relationship"
    ROLE_CORRECTION = "role_correction"
    ROLE_CONFLICT = "role_conflict"
    LIFECYCLE_AUTHORITY = "lifecycle_authority"
    LIFECYCLE_TRANSITION = "lifecycle_transition"
    REGISTRY_MANIFEST = "registry_manifest"


class ParticipantRoleDependencyKind(str, Enum):
    PREDICATE_FRAME_CONTEXT_REQUIRED = "predicate_frame_context_required"
    ACTION_ROOT_CONTEXT_REQUIRED = "action_root_context_required"
    CONCEPT_COMPATIBILITY_REVIEW_REQUIRED = (
        "concept_compatibility_review_required"
    )
    SPEECH_ACT_CONTEXT_REQUIRED = "speech_act_context_required"
    EFFECT_BOUNDARY_REVIEW_REQUIRED = "effect_boundary_review_required"
    LATER_AUTHORITY_REQUIRED = "later_authority_required"


class ParticipantRoleRelationshipKind(str, Enum):
    MUST_REMAIN_DISTINCT = "must_remain_distinct"
    DEPENDENCY = "dependency"
    CORRECTION_ANCESTRY = "correction_ancestry"
    CONFLICT = "conflict"
    SUPERSESSION = "supersession"


class ParticipantRoleTransitionKind(str, Enum):
    OBSERVE = "observe"
    PROPOSE = "propose"
    ADMIT = "admit"
    ARCHITECTURE_ADMIT = "architecture_admit"
    BOUND = "bound"
    DEFER = "defer"
    MARK_UNKNOWN = "mark_unknown"
    MARK_UNRESOLVED = "mark_unresolved"
    MARK_AMBIGUOUS = "mark_ambiguous"
    MARK_UNSUPPORTED = "mark_unsupported"
    MARK_CONFLICTED = "mark_conflicted"
    QUARANTINE = "quarantine"
    CORRECT = "correct"
    RESOLVE_CONFLICT = "resolve_conflict"
    DEPRECATE = "deprecate"
    SUPERSEDE = "supersede"
    REJECT = "reject"
    REQUIRE_REVIEW = "require_review"


class ParticipantRoleValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    VERSION_NOT_ADVANCING = "version_not_advancing"
    IDENTITY_MISMATCH = "identity_mismatch"
    LINEAGE_MISMATCH = "lineage_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    RESOURCE_KIND_MISMATCH = "resource_kind_mismatch"
    INVALID_ENUM = "invalid_enum"
    DUPLICATE_VALUE = "duplicate_value"
    DUPLICATE_IDENTITY = "duplicate_identity"
    DUPLICATE_KEY = "duplicate_key"
    REFERENCE_NOT_FOUND = "reference_not_found"
    REFERENCE_KIND_MISMATCH = "reference_kind_mismatch"
    SCOPE_REQUIRED = "scope_required"
    NON_SCOPE_REQUIRED = "non_scope_required"
    SCOPE_OVERLAP = "scope_overlap"
    PROVENANCE_REQUIRED = "provenance_required"
    PROVENANCE_INVALID = "provenance_invalid"
    LIFECYCLE_STATE_INVALID = "lifecycle_state_invalid"
    TRANSITION_NOT_PERMITTED = "transition_not_permitted"
    TRANSITION_KIND_MISMATCH = "transition_kind_mismatch"
    AUTHORITY_RECORD_NOT_FOUND = "authority_record_not_found"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"
    NON_LLM_PROVENANCE_REQUIRED = "non_llm_provenance_required"
    ANCESTRY_REQUIRED = "ancestry_required"
    PRIOR_RECORD_NOT_PRESERVED = "prior_record_not_preserved"
    IN_PLACE_MUTATION_PROHIBITED = "in_place_mutation_prohibited"
    CORRECTION_ANCESTRY_INVALID = "correction_ancestry_invalid"
    CONFLICT_BOUNDARY_INVALID = "conflict_boundary_invalid"
    DEPENDENCY_BOUNDARY_INVALID = "dependency_boundary_invalid"
    RELATIONSHIP_BOUNDARY_INVALID = "relationship_boundary_invalid"
    ROLE_ASSIGNMENT_PROHIBITED = "role_assignment_prohibited"
    FRAME_COMPLETION_PROHIBITED = "frame_completion_prohibited"
    SEMANTIC_RELATION_COLLAPSE = "semantic_relation_collapse"
    CONCEPT_ASSIGNMENT_COLLAPSE = "concept_assignment_collapse"
    SOURCE_SPAN_ACTOR_COLLAPSE = "source_span_actor_collapse"
    GRAMMAR_ROLE_COLLAPSE = "grammar_role_collapse"
    NEAREST_KNOWN_SUBSTITUTION_PROHIBITED = (
        "nearest_known_substitution_prohibited"
    )
    SIMILARITY_AUTHORITY_PROHIBITED = "similarity_authority_prohibited"
    RUNTIME_AUTHORITY_PROHIBITED = "runtime_authority_prohibited"
    EXTERNAL_RESOURCE_AUTHORITY_PROHIBITED = (
        "external_resource_authority_prohibited"
    )
    REGISTRY_NOT_READ_ONLY = "registry_not_read_only"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    MANIFEST_BOUNDARY_MISMATCH = "manifest_boundary_mismatch"
    VALIDATOR_FAILED_CLOSED = "validator_failed_closed"


@dataclass(frozen=True, slots=True)
class ParticipantRoleValidationIssue:
    path: str
    code: ParticipantRoleValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ParticipantRoleValidationReport:
    ok: bool
    issues: tuple[ParticipantRoleValidationIssue, ...]
    schema_version: str = SLICE38D_SCHEMA_VERSION


class ParticipantRoleValidationError(ValueError):
    """Raised when a Slice 38D validation report is not successful."""

    def __init__(self, report: ParticipantRoleValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 38D participant-role validation failed")


@dataclass(frozen=True, slots=True)
class ParticipantRoleProvenanceReference:
    provenance_id: str
    authority_document: str
    authority_section: str
    source_kind: str
    source_reference: str
    version: str
    non_llm_provenance: bool
    external_resource_admitted: bool
    runtime_loaded: bool
    implementation_authorized: bool
    prohibited_authorities: tuple[str, ...]
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.PROVENANCE_REFERENCE
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("provenance_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38d_role_provenance", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleNamespaceIdentity:
    namespace_id: str
    namespace_key: str
    preferred_label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: ParticipantRoleLifecycleState
    provenance_refs: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unknown_state_policy: str
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.NAMESPACE_IDENTITY
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("namespace_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38d_role_namespace", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleIdentity:
    role_id: str
    namespace_id: str
    role_key: str
    preferred_label: str
    role_category_key: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: ParticipantRoleLifecycleState
    provenance_refs: tuple[str, ...]
    frame_dependency_required: bool
    action_root_dependency_required: bool
    concept_compatibility_review_required: bool
    semantic_relation_separation_required: bool
    grammar_separation_required: bool
    speech_act_separation_required: bool
    effect_boundary_review_required: bool
    authority_non_satisfaction_required: bool
    occurrence_assignment_allowed: bool
    role_selection_allowed: bool
    dependency_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    correction_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    unknown_state_policy: str
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.PARTICIPANT_ROLE_IDENTITY
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("role_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("participant_role_identity", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleDependencyRecord:
    dependency_id: str
    dependency_key: str
    role_id: str
    dependency_kinds: tuple[ParticipantRoleDependencyKind, ...]
    dependency_refs: tuple[str, ...]
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: ParticipantRoleLifecycleState
    provenance_refs: tuple[str, ...]
    satisfied_by_role_identity: bool
    satisfied_by_registry_membership: bool
    runtime_authority_supplied: bool
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.ROLE_DEPENDENCY
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("dependency_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("participant_role_dependency", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleRelationshipRecord:
    relationship_id: str
    relationship_key: str
    relationship_kind: ParticipantRoleRelationshipKind
    left_role_id: str
    right_role_id: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: ParticipantRoleLifecycleState
    provenance_refs: tuple[str, ...]
    role_assignment_performed: bool
    frame_constraint_created: bool
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.ROLE_RELATIONSHIP
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("relationship_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("participant_role_relationship", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleCorrectionRecord:
    correction_id: str
    role_lineage_id: str
    source_role_id: str
    target_role_id: str
    source_version: str
    target_version: str
    corrected_fields: tuple[str, ...]
    reason: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    authority_record_ref: str
    prior_record_preserved: bool
    in_place_mutation_performed: bool
    runtime_authority_supplied: bool
    lifecycle_state: ParticipantRoleLifecycleState
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.ROLE_CORRECTION
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("correction_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("participant_role_correction", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleConflictRecord:
    conflict_id: str
    conflict_key: str
    role_refs: tuple[str, ...]
    conflict_kind: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    authority_record_ref: str
    resolved: bool
    resolution_ref: str | None
    role_assignment_allowed: bool
    frame_use_allowed: bool
    capability_binding_allowed: bool
    runtime_authority_supplied: bool
    lifecycle_state: ParticipantRoleLifecycleState
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.ROLE_CONFLICT
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("conflict_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("participant_role_conflict", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleLifecycleAuthorityRecord:
    authority_id: str
    authority_provenance_refs: tuple[str, ...]
    decision_owner_ref: str
    human_approval_ref: str
    human_approved: bool
    reason: str
    scope: tuple[str, ...]
    affected_record_refs: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unresolved_dependency_refs: tuple[str, ...]
    conflict_review_complete: bool
    unknown_state_review_complete: bool
    version_review_complete: bool
    scope_non_scope_review_complete: bool
    provenance_review_complete: bool
    semantic_relation_boundary_review_complete: bool
    grammar_boundary_review_complete: bool
    concept_assignment_boundary_review_complete: bool
    source_span_actor_boundary_review_complete: bool
    non_llm_provenance: bool
    role_assignment_authorized: bool
    frame_completion_authorized: bool
    runtime_authorized: bool
    implementation_authorized: bool
    registry_population_authorized: bool
    resource_kind: ParticipantRoleResourceKind = (
        ParticipantRoleResourceKind.LIFECYCLE_AUTHORITY
    )
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("authority_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("participant_role_lifecycle_authority", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleLifecycleTransitionRecord:
    transition_id: str
    lineage_id: str
    resource_kind: ParticipantRoleResourceKind
    source_resource_id: str
    target_resource_id: str
    source_version: str
    target_version: str
    from_state: ParticipantRoleLifecycleState
    to_state: ParticipantRoleLifecycleState
    transition_kind: ParticipantRoleTransitionKind
    authority_record_ref: str
    reason: str
    scope: tuple[str, ...]
    affected_role_refs: tuple[str, ...]
    dependency_refs: tuple[str, ...]
    correction_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    prior_record_preserved: bool
    automatic_transition: bool
    in_place_mutation_performed: bool
    nearest_known_substitution_performed: bool
    similarity_authority_used: bool
    role_assignment_performed: bool
    runtime_authority_supplied: bool
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("transition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("participant_role_lifecycle_transition", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


ParticipantRoleGovernedResource: TypeAlias = (
    ParticipantRoleNamespaceIdentity
    | ParticipantRoleIdentity
    | ParticipantRoleDependencyRecord
    | ParticipantRoleRelationshipRecord
)


@dataclass(frozen=True, slots=True)
class ParticipantRoleRegistryManifest:
    manifest_id: str
    registry_key: str
    namespace_ref: str
    role_refs: tuple[str, ...]
    role_lineage_refs: tuple[str, ...]
    role_keys: tuple[str, ...]
    dependency_refs: tuple[str, ...]
    relationship_refs: tuple[str, ...]
    correction_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    transition_refs: tuple[str, ...]
    authority_ref: str
    action_root_registry_manifest_ref: str
    source_authority_packet_sha256: str
    slice38c_r2_evidence_sha256: str
    accepted_parent_head: str
    accepted_parent_tree: str
    decision_owner_ref: str
    human_approval_ref: str
    human_approved: bool
    registry_population_authorized: bool
    read_only: bool
    closed_set: bool
    exact_identity_lookup_allowed: bool
    exact_internal_key_lookup_allowed: bool
    surface_form_lookup_allowed: bool
    surface_normalization_allowed: bool
    occurrence_role_assignment_installed: bool
    concept_candidate_to_role_assignment_installed: bool
    semantic_relation_to_role_conversion_installed: bool
    source_span_to_actor_conversion_installed: bool
    grammatical_position_to_role_conversion_installed: bool
    nearest_known_role_substitution_installed: bool
    semantic_similarity_installed: bool
    predicate_frame_population_installed: bool
    frame_completion_installed: bool
    capability_reference_population_installed: bool
    capability_routing_installed: bool
    route_registration_installed: bool
    tool_activation_installed: bool
    action_execution_installed: bool
    evidence_validation_installed: bool
    memory_access_installed: bool
    rendering_installed: bool
    delivery_installed: bool
    external_resource_loading_installed: bool
    llm_authority_installed: bool
    correction_schema_supported: bool
    conflict_schema_supported: bool
    dependency_schema_supported: bool
    relationship_schema_supported: bool
    lifecycle_history_preserved: bool
    predicate_frames_deferred_to_slice38e: bool
    effect_and_capability_references_deferred_to_slice38f: bool
    occurrence_candidate_proposal_deferred_to_slice38g: bool
    disabled_integration_deferred_to_slice38h: bool
    deferred_role_candidates: tuple[str, ...]
    authority_limitations: tuple[str, ...]
    spec_id: str = SLICE38D_SPEC_ID
    spec_version: str = SLICE38D_SPEC_VERSION
    schema_version: str = SLICE38D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("manifest_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38d_participant_role_manifest", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRoleRegistry:
    manifest: ParticipantRoleRegistryManifest
    current_namespace: ParticipantRoleNamespaceIdentity
    admitted_roles: tuple[ParticipantRoleIdentity, ...]
    role_histories: tuple[tuple[ParticipantRoleIdentity, ...], ...]
    dependencies: tuple[ParticipantRoleDependencyRecord, ...]
    dependency_histories: tuple[tuple[ParticipantRoleDependencyRecord, ...], ...]
    relationships: tuple[ParticipantRoleRelationshipRecord, ...]
    relationship_histories: tuple[tuple[ParticipantRoleRelationshipRecord, ...], ...]
    corrections: tuple[ParticipantRoleCorrectionRecord, ...]
    conflicts: tuple[ParticipantRoleConflictRecord, ...]
    authority_records: tuple[ParticipantRoleLifecycleAuthorityRecord, ...]
    transitions: tuple[ParticipantRoleLifecycleTransitionRecord, ...]
    provenance_records: tuple[ParticipantRoleProvenanceReference, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
