"""Immutable Slice 37A controlled concept-authority schema contracts.

This module defines record shapes only. It does not populate a registry, look
up a term, map a source occurrence, select a concept or sense, construct a
semantic relation edge, consume a Slice 36 structural result, create
CandidateMeaning, inspect files, access memory, register a route, invoke a
tool, render output, or authorize an action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id


SLICE37A_SPEC_ID: Final[str] = "aiweb-slice37a-controlled-concept-authority-schema"
SLICE37A_SPEC_VERSION: Final[str] = (
    "aiweb-slice37a-controlled-concept-authority-schema-v1"
)
SLICE37A_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-controlled-concept-sense-registry-schema-v1"
)
SLICE37A_ACCEPTED_PARENT_HEAD: Final[str] = (
    "5bd8a39b91e7ead06523e7fd0aa3ee057c795f74"
)
SLICE37A_ACCEPTED_PARENT_TREE: Final[str] = (
    "16a7708c5ea8b208224bd3ef7a51375c8f980138"
)
SLICE37A_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 36H bounded bootstrap integration and Slice 36 closeout"
)
HISTORICAL_SLICE8_COMMIT: Final[str] = (
    "f55c3ff076cbb7e30344a82f51707fbd3997130c"
)
HISTORICAL_SLICE8_SUBJECT: Final[str] = "Slice 8 concept boundary scaffold"

CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES: Final[tuple[str, ...]] = (
    "surface term is not concept identity",
    "concept identity is not sense identity",
    "term mapping is not occurrence-level interpretation",
    "mapped term is not selected sense",
    "sense candidate is not CandidateMeaning",
    "semantic class is not authority class",
    "semantic relation type is not a relation fact",
    "semantic relation is not truth",
    "source relation is not source reliability",
    "evidence relation is not evidence validity",
    "verification relation is not verified status",
    "action concept is not predicate identity",
    "action concept is not permission",
    "capability concept is not tool route",
    "memory concept is not memory access",
    "delivery concept is not delivery authority",
    "registry scale is not semantic authority",
)

SLICE37A_DEFERRED_SCOPE: Final[tuple[str, ...]] = (
    "deterministic identity and lifecycle transition law in Slice 37B",
    "minimal admitted built-in registry population in Slice 37C",
    "controlled sense and exact term mapping in Slice 37D",
    "semantic classes and relation-type rules in Slice 37E",
    "Slice 36 structural-to-concept candidate proposal in Slice 37F",
    "disabled integration and Slice 37 closeout in Slice 37G",
    "predicate and participant-role authority in Slice 38",
    "CandidateMeaning construction in Slice 39",
    "gate selection and ambiguity disposition in Slice 40",
)


class ConceptResourceKind(str, Enum):
    AUTHORITY_PROFILE = "authority_profile"
    SCHEMA_CONTRACT = "schema_contract"
    PROVENANCE_REFERENCE = "provenance_reference"
    NAMESPACE_IDENTITY = "namespace_identity"
    CONCEPT_IDENTITY = "concept_identity"
    SENSE_IDENTITY = "sense_identity"
    LEXICAL_REFERENCE = "lexical_reference"
    TERM_CONCEPT_MAPPING_IDENTITY = "term_concept_mapping_identity"
    SEMANTIC_CLASS_IDENTITY = "semantic_class_identity"
    SEMANTIC_RELATION_FAMILY_IDENTITY = "semantic_relation_family_identity"
    SEMANTIC_RELATION_TYPE_IDENTITY = "semantic_relation_type_identity"


class ConceptLifecycleState(str, Enum):
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


class LexicalReferenceKind(str, Enum):
    SOURCE_TERM = "source_term"
    CONTROLLED_INTERNAL_EXPRESSION = "controlled_internal_expression"
    CONTROLLED_OUTWARD_EXPRESSION = "controlled_outward_expression"
    DOMAIN_TERM = "domain_term"
    USER_DEFINED_BOUNDED_EXPRESSION = "user_defined_bounded_expression"
    EXTERNAL_REFERENCE_LABEL = "external_reference_label"


class RelationDirection(str, Enum):
    DIRECTED = "directed"
    SYMMETRIC = "symmetric"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class ConceptAuthorityProfile:
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
    unknown_state_first_class: bool
    unresolved_state_first_class: bool
    ambiguity_preserved: bool
    scale_is_not_authority: bool
    registry_population_installed: bool
    concept_lookup_allowed: bool
    source_occurrence_mapping_allowed: bool
    sense_selection_allowed: bool
    semantic_relation_edge_population_allowed: bool
    structural_result_consumption_allowed: bool
    candidate_meaning_creation_allowed: bool
    selected_meaning_allowed: bool
    predicate_authority_allowed: bool
    participant_role_authority_allowed: bool
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
    spec_id: str = SLICE37A_SPEC_ID
    spec_version: str = SLICE37A_SPEC_VERSION
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("profile_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37a_concept_authority_profile", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptRegistrySchemaContract:
    contract_id: str
    resource_kinds: tuple[ConceptResourceKind, ...]
    required_record_families: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    deferred_scope: tuple[str, ...]
    registry_entry_count: int
    concept_entry_count: int
    sense_entry_count: int
    lexical_reference_entry_count: int
    term_mapping_entry_count: int
    semantic_class_entry_count: int
    relation_family_entry_count: int
    relation_type_entry_count: int
    registry_population_installed: bool
    lookup_installed: bool
    mapping_installed: bool
    sense_selection_installed: bool
    relation_edge_population_installed: bool
    structural_integration_installed: bool
    historical_slice8_preserved: bool
    historical_slice8_superseded: bool
    spec_id: str = SLICE37A_SPEC_ID
    spec_version: str = SLICE37A_SPEC_VERSION
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("contract_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37a_concept_registry_schema_contract", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptProvenanceReference:
    provenance_id: str
    authority_document: str
    authority_section: str
    source_kind: str
    source_reference: str
    version: str
    non_llm_provenance: bool
    external_resource_admitted: bool
    runtime_loaded: bool
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.PROVENANCE_REFERENCE
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("provenance_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("concept_provenance", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptNamespaceIdentity:
    namespace_id: str
    namespace_key: str
    label: str
    definition: str
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    scope_tags: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.NAMESPACE_IDENTITY
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("namespace_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("concept_namespace", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ControlledConceptIdentity:
    concept_id: str
    namespace_id: str
    concept_key: str
    preferred_label: str
    definition: str
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    semantic_class_refs: tuple[str, ...]
    sense_refs: tuple[str, ...]
    relation_type_refs: tuple[str, ...]
    scope_tags: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.CONCEPT_IDENTITY
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("concept_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("controlled_concept", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ControlledSenseIdentity:
    sense_id: str
    concept_id: str
    namespace_id: str
    sense_key: str
    definition: str
    differentiation_basis: tuple[str, ...]
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    lexical_reference_refs: tuple[str, ...]
    scope_tags: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.SENSE_IDENTITY
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("sense_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("controlled_sense", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ControlledLexicalReference:
    lexical_reference_id: str
    namespace_id: str
    exact_form: str
    reference_kind: LexicalReferenceKind
    language_tag: str
    case_sensitive: bool
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    scope_tags: tuple[str, ...]
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.LEXICAL_REFERENCE
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("lexical_reference_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("controlled_lexical_reference", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TermConceptMappingIdentity:
    mapping_id: str
    lexical_reference_id: str
    namespace_scope: tuple[str, ...]
    domain_scope: tuple[str, ...]
    concept_candidate_refs: tuple[str, ...]
    sense_candidate_refs: tuple[str, ...]
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    occurrence_interpretation_selected: bool
    selected_concept_ref: str | None
    selected_sense_ref: str | None
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.TERM_CONCEPT_MAPPING_IDENTITY
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("mapping_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("term_concept_mapping", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SemanticClassIdentity:
    semantic_class_id: str
    namespace_id: str
    class_key: str
    label: str
    definition: str
    parent_class_refs: tuple[str, ...]
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.SEMANTIC_CLASS_IDENTITY
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("semantic_class_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("semantic_class", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SemanticRelationFamilyIdentity:
    relation_family_id: str
    namespace_id: str
    family_key: str
    label: str
    definition: str
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.SEMANTIC_RELATION_FAMILY_IDENTITY
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("relation_family_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("semantic_relation_family", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SemanticRelationTypeIdentity:
    relation_type_id: str
    relation_family_id: str
    namespace_id: str
    relation_key: str
    label: str
    definition: str
    direction: RelationDirection
    domain_class_refs: tuple[str, ...]
    range_class_refs: tuple[str, ...]
    inverse_relation_type_ref: str | None
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    relation_instances_populated: bool
    prohibited_authorities: tuple[str, ...]
    resource_kind: ConceptResourceKind = ConceptResourceKind.SEMANTIC_RELATION_TYPE_IDENTITY
    schema_version: str = SLICE37A_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("relation_type_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("semantic_relation_type", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
