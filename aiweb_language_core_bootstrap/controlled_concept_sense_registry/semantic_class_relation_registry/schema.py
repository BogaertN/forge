"""Immutable Slice 37E semantic-class and relation-type records.

This package installs a closed structural organization layer over the exact
Slice 37D registry. It defines classes, concept-to-class memberships, relation
families, relation types, domain/range eligibility, one explicitly authorized
inverse pair, relation-version identities, prohibited implications, and
unresolved relation-state policy.

It creates no semantic relation instance, selects no source meaning, evaluates
no truth or evidence, applies no status, imports no external resource, and
performs no runtime, route, tool, memory, action, rendering, delivery, identity,
or economic operation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ...schema import stable_record_id
from ..governed_lifecycle.schema import ConceptGovernanceBatch
from ..schema import (
    ConceptLifecycleState,
    RelationDirection,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
)
from ..sense_term_mapping_registry.schema import SenseTermMappingRegistry


SLICE37E_SPEC_ID: Final[str] = (
    "aiweb-slice37e-semantic-classes-relation-type-rules"
)
SLICE37E_SPEC_VERSION: Final[str] = (
    "aiweb-slice37e-semantic-classes-relation-type-rules-v1"
)
SLICE37E_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-semantic-class-relation-type-registry-schema-v1"
)
SLICE37E_ACCEPTED_PARENT_HEAD: Final[str] = (
    "bd0dd1016e5348247a23fec42dbee906756a7a7e"
)
SLICE37E_ACCEPTED_PARENT_TREE: Final[str] = (
    "1bb0ed1064712b0c904a8adfad912ed009e21d30"
)
SLICE37E_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 37D controlled sense and exact term mapping registry"
)
SLICE37E_SOURCE_AUTHORITY_PACKET_SHA256: Final[str] = (
    "d63802b9b3186b8cbb79300d66cd52f083ce580a30db6cc1b63b72f01ba6a8c7"
)

SLICE37E_EXPECTED_CLASS_COUNT: Final[int] = 6
SLICE37E_EXPECTED_MEMBERSHIP_COUNT: Final[int] = 6
SLICE37E_EXPECTED_RELATION_FAMILY_COUNT: Final[int] = 6
SLICE37E_EXPECTED_RELATION_TYPE_COUNT: Final[int] = 6
SLICE37E_EXPECTED_INVERSE_DECLARATION_COUNT: Final[int] = 1
SLICE37E_EXPECTED_RELATION_VERSION_COUNT: Final[int] = 6
SLICE37E_EXPECTED_RELATION_STATE_POLICY_COUNT: Final[int] = 4
SLICE37E_EXPECTED_PROHIBITED_IMPLICATION_COUNT: Final[int] = 16


class SemanticClassLevel(str, Enum):
    FOUNDATIONAL = "foundational"
    SPECIALIZED = "specialized"


class MembershipResolutionState(str, Enum):
    ADMITTED_MEMBERSHIP = "admitted_membership"
    NO_ADMITTED_MEMBERSHIP = "no_admitted_membership"
    UNKNOWN_CONCEPT = "unknown_concept"
    UNKNOWN_CLASS = "unknown_class"
    CONFLICTED_MEMBERSHIP = "conflicted_membership"


class RelationSymmetry(str, Enum):
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    UNRESOLVED = "unresolved"


class RelationEligibilityState(str, Enum):
    ELIGIBLE_TYPE_ONLY = "eligible_type_only"
    UNKNOWN_RELATION_TYPE = "unknown_relation_type"
    UNKNOWN_DOMAIN_CONCEPT = "unknown_domain_concept"
    UNKNOWN_RANGE_CONCEPT = "unknown_range_concept"
    DOMAIN_CLASS_NOT_PERMITTED = "domain_class_not_permitted"
    RANGE_CLASS_NOT_PERMITTED = "range_class_not_permitted"
    PROHIBITED_SCOPE_EXPANSION = "prohibited_scope_expansion"
    CONFLICTED_RELATION = "conflicted_relation"
    UNSUPPORTED_RELATION = "unsupported_relation"


class RelationStateKind(str, Enum):
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    PROHIBITED_EXPANSION = "prohibited_expansion"


class ProhibitedImplicationKind(str, Enum):
    CLASS_MEMBERSHIP_TO_EVIDENCE = "class_membership_to_evidence"
    CLASS_MEMBERSHIP_TO_MEMORY = "class_membership_to_memory"
    CLASS_MEMBERSHIP_TO_PERMISSION = "class_membership_to_permission"
    CLASS_MEMBERSHIP_TO_ACTION = "class_membership_to_action"
    CLASS_MEMBERSHIP_TO_DELIVERY = "class_membership_to_delivery"
    CLASS_MEMBERSHIP_TO_IDENTITY = "class_membership_to_identity"
    CLASS_MEMBERSHIP_TO_RUNTIME = "class_membership_to_runtime"
    CLASS_MEMBERSHIP_TO_ECONOMIC_AUTHORITY = (
        "class_membership_to_economic_authority"
    )
    RELATION_TYPE_TO_RELATION_FACT = "relation_type_to_relation_fact"
    RELATION_INSTANCE_TO_TRUTH = "relation_instance_to_truth"
    SOURCE_RELATION_TO_SOURCE_RELIABILITY = (
        "source_relation_to_source_reliability"
    )
    EVIDENCE_RELATION_TO_EVIDENCE_VALIDITY = (
        "evidence_relation_to_evidence_validity"
    )
    VERIFICATION_RELATION_TO_VERIFIED_STATUS = (
        "verification_relation_to_verified_status"
    )
    STATUS_RELATION_TO_STATUS_APPLICATION = (
        "status_relation_to_status_application"
    )
    ARCHITECTURE_RELATION_TO_IMPLEMENTATION = (
        "architecture_relation_to_implementation"
    )
    CLASS_OR_RELATION_TO_AUTOMATIC_INHERITANCE = (
        "class_or_relation_to_automatic_inheritance"
    )


class SemanticClassRelationValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SCOPE = "invalid_scope"
    INVALID_ENUM = "invalid_enum"
    IDENTITY_MISMATCH = "identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    REFERENCE_NOT_FOUND = "reference_not_found"
    REFERENCE_KIND_MISMATCH = "reference_kind_mismatch"
    DUPLICATE_VALUE = "duplicate_value"
    REGISTRY_COUNT_MISMATCH = "registry_count_mismatch"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    REGISTRY_NOT_READ_ONLY = "registry_not_read_only"
    GOVERNANCE_BATCH_INVALID = "governance_batch_invalid"
    PREDECESSOR_REGISTRY_MISMATCH = "predecessor_registry_mismatch"
    CLASS_MEMBERSHIP_AUTHORITY_PROHIBITED = (
        "class_membership_authority_prohibited"
    )
    CLASS_MEMBERSHIP_EDGE_PROHIBITED = "class_membership_edge_prohibited"
    RELATION_INSTANCE_POPULATION_PROHIBITED = (
        "relation_instance_population_prohibited"
    )
    RELATION_TRUTH_AUTHORITY_PROHIBITED = (
        "relation_truth_authority_prohibited"
    )
    DOMAIN_RANGE_RULE_MISMATCH = "domain_range_rule_mismatch"
    DIRECTION_SYMMETRY_MISMATCH = "direction_symmetry_mismatch"
    INVERSE_DECLARATION_MISMATCH = "inverse_declaration_mismatch"
    VERSION_IDENTITY_MISMATCH = "version_identity_mismatch"
    PROHIBITED_IMPLICATION_MISMATCH = "prohibited_implication_mismatch"
    RELATION_STATE_POLICY_MISMATCH = "relation_state_policy_mismatch"
    LATER_AUTHORITY_INSTALLED = "later_authority_installed"


@dataclass(frozen=True, slots=True)
class SemanticClassRelationValidationIssue:
    path: str
    code: SemanticClassRelationValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class SemanticClassRelationValidationReport:
    ok: bool
    issues: tuple[SemanticClassRelationValidationIssue, ...]
    schema_version: str = SLICE37E_SCHEMA_VERSION


class SemanticClassRelationValidationError(ValueError):
    """Raised when Slice 37E validation fails closed."""

    def __init__(self, report: SemanticClassRelationValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            detail or "Slice 37E semantic-class/relation validation failed"
        )


@dataclass(frozen=True, slots=True)
class SemanticClassDefinition:
    definition_id: str
    semantic_class_ref: str
    class_level: SemanticClassLevel
    parent_class_refs: tuple[str, ...]
    inclusion_rules: tuple[str, ...]
    exclusion_rules: tuple[str, ...]
    scope_tags: tuple[str, ...]
    multiple_membership_permitted: bool
    class_membership_creates_authority: bool
    class_membership_creates_relation_instance: bool
    prohibited_implication_refs: tuple[str, ...]
    provenance_ref: str
    version: str
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("definition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_semantic_class_definition",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptClassMembershipRule:
    membership_id: str
    concept_ref: str
    semantic_class_ref: str
    membership_basis: tuple[str, ...]
    scope_tags: tuple[str, ...]
    version: str
    lifecycle_state: ConceptLifecycleState
    provenance_ref: str
    creates_evidence_authority: bool
    creates_memory_authority: bool
    creates_permission_authority: bool
    creates_action_authority: bool
    creates_delivery_authority: bool
    creates_identity_authority: bool
    creates_runtime_authority: bool
    creates_economic_authority: bool
    creates_relation_instance: bool
    prohibited_implication_refs: tuple[str, ...]
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("membership_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_concept_class_membership",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelationFamilyDefinition:
    definition_id: str
    relation_family_ref: str
    relationship_domain: str
    eligible_resource_kinds: tuple[str, ...]
    scope_tags: tuple[str, ...]
    relation_type_refs: tuple[str, ...]
    relation_instances_admitted: bool
    prohibited_implication_refs: tuple[str, ...]
    provenance_ref: str
    version: str
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("definition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_relation_family_definition",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelationTypeRule:
    rule_id: str
    relation_type_ref: str
    permitted_domain_class_refs: tuple[str, ...]
    permitted_range_class_refs: tuple[str, ...]
    direction: RelationDirection
    symmetry: RelationSymmetry
    inverse_declaration_ref: str | None
    scope_tags: tuple[str, ...]
    sense_bounded_participation_required: bool
    status_sensitive: bool
    ancestry_sensitive: bool
    conditional: bool
    relation_instances_admitted: bool
    truth_determined: bool
    evidence_sufficiency_determined: bool
    verified_status_applied: bool
    implementation_determined: bool
    prohibited_implication_refs: tuple[str, ...]
    provenance_ref: str
    version: str
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("rule_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_relation_type_rule",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InverseRelationDeclaration:
    declaration_id: str
    relation_type_ref: str
    inverse_relation_type_ref: str
    explicitly_authorized: bool
    reciprocal_pair: bool
    creates_relation_instance: bool
    source_reference: str
    provenance_ref: str
    version: str
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("declaration_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_inverse_relation_declaration",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelationVersionIdentity:
    relation_version_id: str
    relation_type_ref: str
    relation_lineage_ref: str
    current_version: str
    predecessor_version_refs: tuple[str, ...]
    current: bool
    provenance_ref: str
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("relation_version_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_relation_version_identity",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelationStatePolicy:
    state_policy_id: str
    state_kind: RelationStateKind
    definition: str
    permitted_uses: tuple[str, ...]
    prohibited_repairs: tuple[str, ...]
    creates_relation_instance: bool
    determines_truth: bool
    authorizes_consequence: bool
    provenance_ref: str
    version: str
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("state_policy_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_relation_state_policy",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProhibitedImplicationRule:
    implication_rule_id: str
    implication_kind: ProhibitedImplicationKind
    allowed: bool
    reason: str
    provenance_ref: str
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("implication_rule_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_prohibited_implication_rule",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelationEligibilityRequest:
    request_id: str
    relation_type_id: str
    domain_concept_id: str
    range_concept_id: str
    requested_scope_tags: tuple[str, ...]
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("request_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_relation_eligibility_request",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelationEligibilityResult:
    result_id: str
    request_ref: str
    state: RelationEligibilityState
    relation_type_ref: str | None
    matched_domain_membership_refs: tuple[str, ...]
    matched_range_membership_refs: tuple[str, ...]
    eligible_for_later_instance_review: bool
    relation_instance_created: bool
    relation_fact_asserted: bool
    truth_determined: bool
    evidence_sufficiency_determined: bool
    verified_status_applied: bool
    implementation_determined: bool
    reason: str
    prohibited_implication_refs: tuple[str, ...]
    schema_version: str = SLICE37E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_relation_eligibility_result",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SemanticClassRelationRegistryManifest:
    manifest_id: str
    registry_key: str
    source_authority_packet_sha256: str
    decision_owner_ref: str
    human_approval_ref: str
    human_approved: bool
    read_only: bool
    closed_set: bool
    authority_limitations: tuple[str, ...]
    semantic_class_refs: tuple[str, ...]
    class_definition_refs: tuple[str, ...]
    membership_refs: tuple[str, ...]
    relation_family_refs: tuple[str, ...]
    relation_family_definition_refs: tuple[str, ...]
    relation_type_refs: tuple[str, ...]
    relation_type_rule_refs: tuple[str, ...]
    inverse_declaration_refs: tuple[str, ...]
    relation_version_refs: tuple[str, ...]
    relation_state_policy_refs: tuple[str, ...]
    prohibited_implication_refs: tuple[str, ...]
    exact_class_id_lookup_allowed: bool
    exact_relation_family_id_lookup_allowed: bool
    exact_relation_type_id_lookup_allowed: bool
    exact_membership_lookup_allowed: bool
    type_eligibility_evaluation_allowed: bool
    registry_population_authorized: bool
    semantic_class_population_authorized: bool
    class_membership_population_authorized: bool
    relation_family_population_authorized: bool
    relation_type_population_authorized: bool
    inverse_declaration_population_authorized: bool
    relation_instance_population_installed: bool
    relation_fact_assertion_installed: bool
    source_occurrence_interpretation_installed: bool
    sense_selection_installed: bool
    candidate_meaning_creation_installed: bool
    structural_integration_installed: bool
    truth_evaluation_installed: bool
    evidence_validation_installed: bool
    verified_status_application_installed: bool
    permission_authority_installed: bool
    action_authority_installed: bool
    memory_authority_installed: bool
    identity_authority_installed: bool
    economic_authority_installed: bool
    runtime_activation_installed: bool
    route_registration_installed: bool
    tool_activation_installed: bool
    rendering_installed: bool
    delivery_installed: bool
    external_resource_loading_installed: bool
    llm_authority_installed: bool
    embedding_installed: bool
    semantic_similarity_installed: bool
    structural_candidate_integration_deferred_to_slice37f: bool
    schema_version: str = SLICE37E_SCHEMA_VERSION
    spec_id: str = SLICE37E_SPEC_ID
    spec_version: str = SLICE37E_SPEC_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("manifest_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37e_semantic_class_relation_registry_manifest",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SemanticClassRelationRegistry:
    manifest: SemanticClassRelationRegistryManifest
    predecessor_registry: SenseTermMappingRegistry
    governance_batch: ConceptGovernanceBatch
    semantic_classes: tuple[SemanticClassIdentity, ...]
    class_definitions: tuple[SemanticClassDefinition, ...]
    memberships: tuple[ConceptClassMembershipRule, ...]
    relation_families: tuple[SemanticRelationFamilyIdentity, ...]
    relation_family_definitions: tuple[RelationFamilyDefinition, ...]
    relation_types: tuple[SemanticRelationTypeIdentity, ...]
    relation_type_rules: tuple[RelationTypeRule, ...]
    inverse_declarations: tuple[InverseRelationDeclaration, ...]
    relation_versions: tuple[RelationVersionIdentity, ...]
    relation_state_policies: tuple[RelationStatePolicy, ...]
    prohibited_implications: tuple[ProhibitedImplicationRule, ...]

    def canonical_body(self) -> dict[str, object]:
        return {
            "manifest_id": self.manifest.manifest_id,
            "predecessor_registry_digest": (
                self.predecessor_registry.registry_digest()
            ),
            "governance_batch_id": self.governance_batch.batch_id,
            "semantic_class_ids": tuple(
                item.semantic_class_id for item in self.semantic_classes
            ),
            "class_definition_ids": tuple(
                item.definition_id for item in self.class_definitions
            ),
            "membership_ids": tuple(
                item.membership_id for item in self.memberships
            ),
            "relation_family_ids": tuple(
                item.relation_family_id for item in self.relation_families
            ),
            "relation_family_definition_ids": tuple(
                item.definition_id
                for item in self.relation_family_definitions
            ),
            "relation_type_ids": tuple(
                item.relation_type_id for item in self.relation_types
            ),
            "relation_type_rule_ids": tuple(
                item.rule_id for item in self.relation_type_rules
            ),
            "inverse_declaration_ids": tuple(
                item.declaration_id for item in self.inverse_declarations
            ),
            "relation_version_ids": tuple(
                item.relation_version_id for item in self.relation_versions
            ),
            "relation_state_policy_ids": tuple(
                item.state_policy_id for item in self.relation_state_policies
            ),
            "prohibited_implication_ids": tuple(
                item.implication_rule_id
                for item in self.prohibited_implications
            ),
        }

    def registry_digest(self) -> str:
        return stable_record_id(
            "slice37e_semantic_class_relation_registry",
            self.canonical_body(),
        )
