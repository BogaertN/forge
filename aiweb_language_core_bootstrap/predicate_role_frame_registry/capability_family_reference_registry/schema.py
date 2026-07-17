"""Immutable Slice 38F capability-reference and effect-boundary contracts.

This module defines architecture-only records for effect-boundary identities,
capability-family identities, exact frame-to-effect references, and exact
frame-to-capability relevance references.  The records are deliberately
non-operational.  They do not prove capability availability, create routes,
construct invocation arguments, authorize invocation, execute actions, access
memory, deliver output, admit external resources, modify runtime state, or
satisfy permission.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final, TypeAlias

from ...schema import stable_record_id


SLICE38F_SPEC_ID: Final[str] = (
    "aiweb-slice38f-capability-family-references-effect-boundaries"
)
SLICE38F_SPEC_VERSION: Final[str] = (
    "aiweb-slice38f-capability-family-references-effect-boundaries-v1"
)
SLICE38F_SCHEMA_VERSION: Final[str] = (
    "aiweb-capability-family-reference-registry-schema-v1"
)
SLICE38F_ACCEPTED_PARENT_HEAD: Final[str] = (
    "93e0fcf5322f8beae9fe8ed7e0d57805f2c63674"
)
SLICE38F_ACCEPTED_PARENT_TREE: Final[str] = (
    "c2b2ae647a1ca45cf83927b9ccef39941e85067e"
)
SLICE38F_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 38E predicate-frame constraints and role compatibility"
)


class CapabilityReferenceLifecycleState(str, Enum):
    OBSERVED = "observed"
    CANDIDATE = "candidate"
    ARCHITECTURE_ADMITTED = "architecture_admitted"
    ADMITTED = "admitted"
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
    REVIEW_REQUIRED = "review_required"
    HISTORICAL_ONLY = "historical_only"


class EffectBoundaryClass(str, Enum):
    NO_ACTION = "no_action"
    READ_ONLY = "read_only"
    COMMUNICATIVE_ONLY = "communicative_only"
    VERIFICATION_REVIEW_ONLY = "verification_review_only"
    SIMULATION_ONLY = "simulation_only"
    PROTECTED_MATHEMATICAL_OUTPUT_ONLY = "protected_mathematical_output_only"


class CapabilityReferenceMode(str, Enum):
    READ_ONLY_POSSIBLE = "read_only_possible"
    COMPARISON_POSSIBLE = "comparison_possible"
    DRAFT_POSSIBLE = "draft_possible"
    VERIFICATION_REVIEW_POSSIBLE = "verification_review_possible"
    SIMULATION_POSSIBLE = "simulation_possible"
    PROTECTED_MATHEMATICAL_POSSIBLE = "protected_mathematical_possible"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    DEFERRED = "deferred"
    BLOCKED = "blocked"


class CapabilityAvailabilityStatus(str, Enum):
    NOT_EVALUATED = "not_evaluated"
    NOT_PROVEN = "not_proven"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    DEFERRED = "deferred"


class CapabilityReferenceResourceKind(str, Enum):
    PROVENANCE_REFERENCE = "provenance_reference"
    NAMESPACE_IDENTITY = "namespace_identity"
    EFFECT_BOUNDARY_IDENTITY = "effect_boundary_identity"
    CAPABILITY_FAMILY_IDENTITY = "capability_family_identity"
    FRAME_EFFECT_BOUNDARY_REFERENCE = "frame_effect_boundary_reference"
    FRAME_CAPABILITY_FAMILY_REFERENCE = "frame_capability_family_reference"
    CAPABILITY_EFFECT_COMPATIBILITY = "capability_effect_compatibility"
    LIFECYCLE_AUTHORITY = "lifecycle_authority"
    LIFECYCLE_TRANSITION = "lifecycle_transition"
    REGISTRY_MANIFEST = "registry_manifest"


class CapabilityReferenceTransitionKind(str, Enum):
    OBSERVE = "observe"
    PROPOSE = "propose"
    ARCHITECTURE_ADMIT = "architecture_admit"
    ADMIT = "admit"
    BOUND = "bound"
    DEFER = "defer"
    MARK_UNKNOWN = "mark_unknown"
    MARK_UNRESOLVED = "mark_unresolved"
    MARK_AMBIGUOUS = "mark_ambiguous"
    MARK_UNSUPPORTED = "mark_unsupported"
    MARK_CONFLICTED = "mark_conflicted"
    QUARANTINE = "quarantine"
    DEPRECATE = "deprecate"
    SUPERSEDE = "supersede"
    REJECT = "reject"
    REQUIRE_REVIEW = "require_review"
    MARK_HISTORICAL = "mark_historical"


class CapabilityReferenceValidationCode(str, Enum):
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
    SCOPE_OVERLAP = "scope_overlap"
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
    FRAME_REFERENCE_INVALID = "frame_reference_invalid"
    EFFECT_REFERENCE_INVALID = "effect_reference_invalid"
    CAPABILITY_REFERENCE_INVALID = "capability_reference_invalid"
    EFFECT_COMPATIBILITY_INVALID = "effect_compatibility_invalid"
    CAPABILITY_AVAILABILITY_COLLAPSE = "capability_availability_collapse"
    ROUTE_COLLAPSE = "route_collapse"
    INVOCATION_COLLAPSE = "invocation_collapse"
    ARGUMENT_CONSTRUCTION_COLLAPSE = "argument_construction_collapse"
    PERMISSION_COLLAPSE = "permission_collapse"
    EXECUTION_COLLAPSE = "execution_collapse"
    RESULT_PROOF_COLLAPSE = "result_proof_collapse"
    MEMORY_AUTHORITY_COLLAPSE = "memory_authority_collapse"
    DELIVERY_AUTHORITY_COLLAPSE = "delivery_authority_collapse"
    EXTERNAL_RESOURCE_AUTHORITY_COLLAPSE = "external_resource_authority_collapse"
    IMPLEMENTATION_AUTHORITY_COLLAPSE = "implementation_authority_collapse"
    FRAME_COMPLETION_PERMISSION_COLLAPSE = "frame_completion_permission_collapse"
    DEFAULT_REFERENCE_PROHIBITED = "default_reference_prohibited"
    NEAREST_KNOWN_SUBSTITUTION_PROHIBITED = "nearest_known_substitution_prohibited"
    SIMILARITY_AUTHORITY_PROHIBITED = "similarity_authority_prohibited"
    REGISTRY_NOT_READ_ONLY = "registry_not_read_only"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    MANIFEST_BOUNDARY_MISMATCH = "manifest_boundary_mismatch"
    VALIDATOR_FAILED_CLOSED = "validator_failed_closed"


@dataclass(frozen=True, slots=True)
class CapabilityReferenceValidationIssue:
    path: str
    code: CapabilityReferenceValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class CapabilityReferenceValidationReport:
    ok: bool
    issues: tuple[CapabilityReferenceValidationIssue, ...]
    schema_version: str = SLICE38F_SCHEMA_VERSION


class CapabilityReferenceValidationError(ValueError):
    """Raised when a Slice 38F validation report is unsuccessful."""

    def __init__(self, report: CapabilityReferenceValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 38F capability-reference validation failed")


@dataclass(frozen=True, slots=True)
class CapabilityReferenceProvenanceReference:
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
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.PROVENANCE_REFERENCE
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("provenance_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_capability_provenance", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CapabilityReferenceNamespaceIdentity:
    namespace_id: str
    namespace_key: str
    preferred_label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unknown_state_policy: str
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.NAMESPACE_IDENTITY
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("namespace_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_capability_namespace", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EffectBoundaryIdentity:
    effect_boundary_id: str
    namespace_id: str
    effect_boundary_key: str
    preferred_label: str
    effect_class: EffectBoundaryClass
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    allowed_consequence_descriptions: tuple[str, ...]
    prohibited_escalations: tuple[str, ...]
    authority_dependencies: tuple[str, ...]
    unknown_state_policy: str
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs: tuple[str, ...]
    permission_satisfied: bool
    capability_available: bool
    route_resolved: bool
    capability_invoked: bool
    execution_performed: bool
    evidence_validated: bool
    memory_authority_supplied: bool
    delivery_authorized: bool
    external_resource_admitted: bool
    implementation_performed: bool
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.EFFECT_BOUNDARY_IDENTITY
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("effect_boundary_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_effect_boundary", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CapabilityFamilyIdentity:
    capability_family_id: str
    namespace_id: str
    capability_family_key: str
    preferred_label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    supported_effect_boundary_refs: tuple[str, ...]
    permitted_reference_modes: tuple[CapabilityReferenceMode, ...]
    authority_dependencies: tuple[str, ...]
    availability_proof_dependencies: tuple[str, ...]
    route_proof_dependencies: tuple[str, ...]
    invocation_proof_dependencies: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unknown_state_policy: str
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs: tuple[str, ...]
    installed: bool
    available: bool
    route_registered: bool
    invocation_contract_installed: bool
    runtime_loaded: bool
    tool_bound: bool
    external_resource_loaded: bool
    implementation_authorized: bool
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.CAPABILITY_FAMILY_IDENTITY
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("capability_family_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_capability_family", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FrameEffectBoundaryReference:
    frame_effect_reference_id: str
    frame_id: str
    frame_key: str
    frame_version: str
    effect_boundary_id: str
    effect_boundary_key: str
    effect_boundary_version: str
    classification_basis: tuple[str, ...]
    authority_dependencies: tuple[str, ...]
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    unknown_state_policy: str
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs: tuple[str, ...]
    frame_selected: bool
    effect_permission_satisfied: bool
    capability_available: bool
    route_resolved: bool
    invocation_proposed: bool
    invocation_authorized: bool
    execution_performed: bool
    result_verified: bool
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.FRAME_EFFECT_BOUNDARY_REFERENCE
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("frame_effect_reference_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_frame_effect_reference", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FrameCapabilityFamilyReference:
    frame_capability_reference_id: str
    frame_id: str
    frame_key: str
    frame_version: str
    capability_family_id: str
    capability_family_key: str
    capability_family_version: str
    frame_effect_reference_id: str
    effect_boundary_id: str
    effect_boundary_key: str
    relevance_mode: CapabilityReferenceMode
    availability_status: CapabilityAvailabilityStatus
    relevance_basis: tuple[str, ...]
    authority_dependencies: tuple[str, ...]
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    unknown_state_policy: str
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs: tuple[str, ...]
    capability_available: bool
    route_identity: str | None
    route_available: bool
    invocation_identity: str | None
    invocation_proposed: bool
    invocation_authorized: bool
    argument_bundle_id: str | None
    arguments_constructed: bool
    permission_id: str | None
    permission_granted: bool
    execution_receipt_id: str | None
    execution_performed: bool
    result_verified: bool
    tool_bound: bool
    memory_operation_performed: bool
    delivery_performed: bool
    external_resource_admitted: bool
    implementation_performed: bool
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.FRAME_CAPABILITY_FAMILY_REFERENCE
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("frame_capability_reference_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice38f_frame_capability_reference",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CapabilityEffectCompatibilityRecord:
    compatibility_id: str
    capability_family_id: str
    capability_family_key: str
    effect_boundary_id: str
    effect_boundary_key: str
    permitted_reference_modes: tuple[CapabilityReferenceMode, ...]
    compatibility_basis: tuple[str, ...]
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs: tuple[str, ...]
    proves_capability_availability: bool
    creates_route: bool
    authorizes_invocation: bool
    authorizes_execution: bool
    satisfies_permission: bool
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.CAPABILITY_EFFECT_COMPATIBILITY
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("compatibility_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice38f_capability_effect_compatibility",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CapabilityReferenceLifecycleAuthorityRecord:
    authority_id: str
    authority_key: str
    decision_owner: str
    authority_basis: tuple[str, ...]
    approved_scope: tuple[str, ...]
    prohibited_scope: tuple[str, ...]
    human_approval: bool
    non_llm_decision: bool
    automatic_transition_allowed: bool
    implementation_authorized: bool
    capability_availability_authorized: bool
    route_authorized: bool
    invocation_authorized: bool
    action_authorized: bool
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs: tuple[str, ...]
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.LIFECYCLE_AUTHORITY
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("authority_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_lifecycle_authority", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CapabilityReferenceLifecycleTransitionRecord:
    transition_id: str
    resource_lineage_id: str
    source_resource_id: str
    target_resource_id: str
    source_version: str
    target_version: str
    from_state: CapabilityReferenceLifecycleState
    to_state: CapabilityReferenceLifecycleState
    transition_kind: CapabilityReferenceTransitionKind
    reason: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    authority_record_ref: str
    human_approval: bool
    prior_record_preserved: bool
    automatic_transition: bool
    in_place_mutation_performed: bool
    capability_availability_created: bool
    route_created: bool
    invocation_created: bool
    permission_created: bool
    execution_created: bool
    result_proof_created: bool
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.LIFECYCLE_TRANSITION
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("transition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_lifecycle_transition", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CapabilityFamilyReferenceRegistryManifest:
    manifest_id: str
    registry_id: str
    namespace_id: str
    effect_boundary_refs: tuple[str, ...]
    effect_boundary_keys: tuple[str, ...]
    capability_family_refs: tuple[str, ...]
    capability_family_keys: tuple[str, ...]
    frame_effect_reference_refs: tuple[str, ...]
    frame_capability_reference_refs: tuple[str, ...]
    compatibility_refs: tuple[str, ...]
    transition_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    frames_without_capability_reference: tuple[str, ...]
    unbound_capability_family_keys: tuple[str, ...]
    deferred_capability_family_keys: tuple[str, ...]
    effect_boundary_count: int
    capability_family_count: int
    frame_effect_reference_count: int
    frame_capability_reference_count: int
    compatibility_count: int
    transition_count: int
    active_correction_count: int
    active_conflict_count: int
    source_term_lookup_installed: bool
    occurrence_frame_selection_installed: bool
    occurrence_role_assignment_installed: bool
    candidate_meaning_creation_installed: bool
    selected_meaning_installed: bool
    gate_outcome_installed: bool
    capability_availability_registry_installed: bool
    route_registry_installed: bool
    invocation_registry_installed: bool
    argument_builder_installed: bool
    tool_activation_installed: bool
    action_execution_installed: bool
    evidence_validation_installed: bool
    memory_access_installed: bool
    rendering_installed: bool
    delivery_installed: bool
    external_resource_loading_installed: bool
    implementation_installed: bool
    nearest_known_substitution_installed: bool
    semantic_similarity_installed: bool
    llm_authority_installed: bool
    default_capability_reference_installed: bool
    registry_read_only: bool
    registry_closed: bool
    exact_identity_lookup_only: bool
    version: str
    lifecycle_state: CapabilityReferenceLifecycleState
    provenance_refs_manifest: tuple[str, ...]
    resource_kind: CapabilityReferenceResourceKind = (
        CapabilityReferenceResourceKind.REGISTRY_MANIFEST
    )
    schema_version: str = SLICE38F_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("manifest_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38f_registry_manifest", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CapabilityFamilyReferenceRegistry:
    manifest: CapabilityFamilyReferenceRegistryManifest
    current_namespace: CapabilityReferenceNamespaceIdentity
    effect_boundaries: tuple[EffectBoundaryIdentity, ...]
    effect_boundary_histories: tuple[tuple[EffectBoundaryIdentity, ...], ...]
    capability_families: tuple[CapabilityFamilyIdentity, ...]
    capability_family_histories: tuple[tuple[CapabilityFamilyIdentity, ...], ...]
    frame_effect_references: tuple[FrameEffectBoundaryReference, ...]
    frame_effect_reference_histories: tuple[
        tuple[FrameEffectBoundaryReference, ...], ...
    ]
    frame_capability_references: tuple[FrameCapabilityFamilyReference, ...]
    frame_capability_reference_histories: tuple[
        tuple[FrameCapabilityFamilyReference, ...], ...
    ]
    compatibility_records: tuple[CapabilityEffectCompatibilityRecord, ...]
    compatibility_histories: tuple[
        tuple[CapabilityEffectCompatibilityRecord, ...], ...
    ]
    authority_records: tuple[CapabilityReferenceLifecycleAuthorityRecord, ...]
    transitions: tuple[CapabilityReferenceLifecycleTransitionRecord, ...]
    provenance_records: tuple[CapabilityReferenceProvenanceReference, ...]


CapabilityReferenceGovernedResource: TypeAlias = (
    EffectBoundaryIdentity
    | CapabilityFamilyIdentity
    | FrameEffectBoundaryReference
    | FrameCapabilityFamilyReference
    | CapabilityEffectCompatibilityRecord
)
