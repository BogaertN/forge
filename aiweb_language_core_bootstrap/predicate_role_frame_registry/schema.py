"""Immutable Slice 38A action-root and predicate-identity schema contracts.

This module defines record shapes only. It performs no surface-term lookup,
concept-to-predicate conversion, predicate selection, participant-role
assignment, frame completion, capability routing, tool invocation, action,
memory access, evidence validation, rendering, delivery, or release.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id


SLICE38A_SPEC_ID: Final[str] = "aiweb-slice38a-action-root-predicate-schema"
SLICE38A_SPEC_VERSION: Final[str] = "aiweb-slice38a-action-root-predicate-schema-v1"
SLICE38A_SCHEMA_VERSION: Final[str] = "aiweb-predicate-role-frame-registry-schema-v1"
SLICE38A_ACCEPTED_PARENT_HEAD: Final[str] = "f891a33487ea8bc811243627f1d834be7a43f972"
SLICE38A_ACCEPTED_PARENT_TREE: Final[str] = "f087c3f6cec8caecc19539628b1d4ab08b4918c1"
SLICE38A_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 37G disabled integration and Slice 37 closeout"
)

PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES: Final[tuple[str, ...]] = (
    "surface verb is not action-root identity",
    "surface term is not predicate identity",
    "action concept is not predicate identity",
    "concept candidate is not predicate selection",
    "semantic relation is not participant role",
    "action-root identity is not predicate-frame identity",
    "predicate identity is not participant-role assignment",
    "predicate identity is not selected predicate",
    "predicate schema completeness is not frame completeness",
    "frame completeness is not selected meaning",
    "request is not authorization",
    "report is not evidence",
    "verification predicate is not verified status",
    "memory predicate is not memory access",
    "delivery predicate is not delivery authority",
    "installation predicate is not code-application authority",
    "capability reference is not capability route",
    "capability route is not invocation",
    "effect classification is not execution",
    "unknown predicate is not nearest known predicate",
    "external predicate resource is not Forge authority",
    "LLM explanation is not predicate authority",
    "registry scale is not capability",
    "scale is not authority",
)

SLICE38A_DEFERRED_SCOPE: Final[tuple[str, ...]] = (
    "deterministic identity versioning validation and lifecycle law in Slice 38B",
    "minimal admitted built-in action-root registry in Slice 38C",
    "participant-role identity and registry in Slice 38D",
    "predicate-frame constraints and role compatibility in Slice 38E",
    "capability-family references and effect boundaries in Slice 38F",
    "predicate role and frame candidate proposal in Slice 38G",
    "disabled integration and Slice 38 closeout in Slice 38H",
    "CandidateMeaning construction in Slice 39",
    "gate selection ambiguity clarification refusal and blocked progression in Slice 40",
)


class PredicateResourceKind(str, Enum):
    AUTHORITY_PROFILE = "authority_profile"
    SCHEMA_CONTRACT = "schema_contract"
    PROVENANCE_REFERENCE = "provenance_reference"
    NAMESPACE_IDENTITY = "namespace_identity"
    ACTION_ROOT_IDENTITY = "action_root_identity"
    PREDICATE_IDENTITY = "predicate_identity"


class PredicateLifecycleState(str, Enum):
    OBSERVED = "observed"
    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
    ADMITTED = "admitted"
    ARCHITECTURE_ADMITTED = "architecture_admitted"
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
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True, slots=True)
class PredicateAuthorityProfile:
    profile_id: str
    disabled_by_default: bool
    explicit_invocation_required: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    immutable_records: bool
    exact_version_required: bool
    provenance_required: bool
    lifecycle_state_required: bool
    scope_non_scope_required: bool
    unknown_state_first_class: bool
    unresolved_state_first_class: bool
    unsupported_state_first_class: bool
    ambiguity_preserved: bool
    action_authority_separated: bool
    predicate_frame_dependency_required: bool
    participant_role_dependency_required: bool
    speech_act_separation_required: bool
    effect_boundary_dependency_required: bool
    capability_non_invocation_required: bool
    scale_is_not_authority: bool
    registry_population_installed: bool
    action_root_lookup_allowed: bool
    predicate_selection_allowed: bool
    occurrence_interpretation_allowed: bool
    participant_role_population_allowed: bool
    role_assignment_allowed: bool
    predicate_frame_population_allowed: bool
    frame_completion_allowed: bool
    capability_family_reference_population_allowed: bool
    candidate_meaning_creation_allowed: bool
    selected_meaning_allowed: bool
    selected_predicate_allowed: bool
    selected_frame_allowed: bool
    evidence_validation_allowed: bool
    memory_read_allowed: bool
    memory_write_allowed: bool
    external_resource_loading_allowed: bool
    llm_allowed: bool
    embedding_allowed: bool
    vector_database_allowed: bool
    semantic_similarity_allowed: bool
    rag_allowed: bool
    learned_parser_allowed: bool
    neural_classifier_allowed: bool
    api_route_allowed: bool
    capability_route_allowed: bool
    tool_activation_allowed: bool
    action_execution_allowed: bool
    outward_rendering_allowed: bool
    delivery_authorization_allowed: bool
    release_authorized: bool
    production_ready: bool
    spec_id: str = SLICE38A_SPEC_ID
    spec_version: str = SLICE38A_SPEC_VERSION
    schema_version: str = SLICE38A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("profile_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38a_predicate_authority_profile", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateRegistrySchemaContract:
    contract_id: str
    resource_kinds: tuple[PredicateResourceKind, ...]
    required_record_families: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    deferred_scope: tuple[str, ...]
    registry_entry_count: int
    namespace_entry_count: int
    action_root_entry_count: int
    predicate_entry_count: int
    action_root_schema_defined: bool
    predicate_identity_schema_defined: bool
    registry_population_installed: bool
    action_root_lookup_installed: bool
    predicate_selection_installed: bool
    participant_role_schema_installed: bool
    predicate_frame_schema_installed: bool
    capability_reference_schema_installed: bool
    source_occurrence_integration_installed: bool
    selected_predicate_installed: bool
    action_authority_installed: bool
    slice37_boundaries_preserved: bool
    slice37_runtime_superseded: bool
    spec_id: str = SLICE38A_SPEC_ID
    spec_version: str = SLICE38A_SPEC_VERSION
    schema_version: str = SLICE38A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("contract_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38a_predicate_registry_schema_contract", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateProvenanceReference:
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
    resource_kind: PredicateResourceKind = PredicateResourceKind.PROVENANCE_REFERENCE
    schema_version: str = SLICE38A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("provenance_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("predicate_provenance", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateNamespaceIdentity:
    namespace_id: str
    namespace_key: str
    label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: PredicateLifecycleState
    provenance_ref: str
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unknown_state_policy: str
    prohibited_authorities: tuple[str, ...]
    resource_kind: PredicateResourceKind = PredicateResourceKind.NAMESPACE_IDENTITY
    schema_version: str = SLICE38A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("namespace_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("predicate_namespace", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActionRootIdentity:
    action_root_id: str
    namespace_id: str
    action_root_key: str
    preferred_label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: PredicateLifecycleState
    provenance_ref: str
    concept_identity_refs: tuple[str, ...]
    frame_dependency_required: bool
    participant_role_dependency_required: bool
    speech_act_separation_required: bool
    effect_boundary_dependency_required: bool
    capability_non_invocation_required: bool
    occurrence_selection_allowed: bool
    execution_authorized: bool
    unknown_state_policy: str
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    resource_kind: PredicateResourceKind = PredicateResourceKind.ACTION_ROOT_IDENTITY
    schema_version: str = SLICE38A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("action_root_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("action_root_identity", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateIdentity:
    predicate_id: str
    action_root_id: str
    namespace_id: str
    predicate_key: str
    preferred_label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: PredicateLifecycleState
    provenance_ref: str
    concept_identity_refs: tuple[str, ...]
    participant_role_schema_refs: tuple[str, ...]
    predicate_frame_schema_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    capability_family_reference_refs: tuple[str, ...]
    participant_role_dependency_required: bool
    predicate_frame_dependency_required: bool
    speech_act_separation_required: bool
    capability_non_invocation_required: bool
    occurrence_selection_allowed: bool
    selected_for_occurrence: bool
    execution_authorized: bool
    unknown_state_policy: str
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    resource_kind: PredicateResourceKind = PredicateResourceKind.PREDICATE_IDENTITY
    schema_version: str = SLICE38A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("predicate_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("predicate_identity", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
