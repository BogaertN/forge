"""Immutable Slice 38E predicate-frame and role-constraint contracts.

The records in this module describe architecture-level predicate frames,
frame-internal role requirements, role-to-concept compatibility policy,
structural-state policy, provenance, versioning, and lifecycle ancestry.
They do not interpret source text, assign participant roles, select a frame,
construct CandidateMeaning, decide a gate outcome, validate evidence, satisfy
permission, bind a capability, register a route, invoke a tool, execute an
action, access memory, render output, or authorize delivery.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final, TypeAlias

from ...schema import stable_record_id


SLICE38E_SPEC_ID: Final[str] = "aiweb-slice38e-predicate-frame-constraints-role-compatibility"
SLICE38E_SPEC_VERSION: Final[str] = (
    "aiweb-slice38e-predicate-frame-constraints-role-compatibility-v1"
)
SLICE38E_SCHEMA_VERSION: Final[str] = "aiweb-predicate-frame-constraint-registry-schema-v1"
SLICE38E_ACCEPTED_PARENT_HEAD: Final[str] = "9e3668bb4c740bfde24711b56664a494db92f5ac"
SLICE38E_ACCEPTED_PARENT_TREE: Final[str] = "9e97c79796c553a7e9ceb5db1fe4bafce30281a2"
SLICE38E_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 38D participant-role identity and registry"
)


class PredicateFrameLifecycleState(str, Enum):
    OBSERVED = "observed"
    CANDIDATE = "candidate"
    ARCHITECTURE_ADMITTED = "architecture_admitted"
    ADMITTED = "admitted"
    OPERATIONALLY_BOUNDED = "operationally_bounded"
    IMPLEMENTATION_DEFERRED = "implementation_deferred"
    UNKNOWN = "unknown"
    UNRESOLVED = "unresolved"
    STRUCTURALLY_INCOMPLETE = "structurally_incomplete"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    QUARANTINED = "quarantined"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"
    NON_CONFORMING = "non_conforming"
    REVIEW_REQUIRED = "review_required"
    HISTORICAL_ONLY = "historical_only"


class PredicateFrameStructuralState(str, Enum):
    STRUCTURALLY_COMPLETE = "structurally_complete"
    STRUCTURALLY_INCOMPLETE = "structurally_incomplete"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class FrameRoleRequirement(str, Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    PROHIBITED = "prohibited"
    CONDITIONAL = "conditional"


class FrameRoleCardinality(str, Enum):
    EXACTLY_ONE = "exactly_one"
    ZERO_OR_ONE = "zero_or_one"
    ONE_OR_MORE = "one_or_more"
    ZERO_OR_MORE = "zero_or_more"


class FrameSpeechAct(str, Enum):
    REQUEST = "request"
    QUESTION = "question"
    REPORT = "report"
    PROPOSAL = "proposal"
    PROHIBITION = "prohibition"
    REFUSAL = "refusal"
    HYPOTHETICAL = "hypothetical"
    CONDITIONAL = "conditional"
    QUOTED = "quoted"


class FrameEffectClassification(str, Enum):
    NO_ACTION = "no_action"
    READ_ONLY = "read_only"
    COMMUNICATIVE_ONLY = "communicative_only"
    VERIFICATION_REVIEW_ONLY = "verification_review_only"
    SIMULATION_ONLY = "simulation_only"


class FrameCapabilityReferenceStatus(str, Enum):
    NOT_POPULATED = "not_populated"
    DEFERRED_TO_SLICE38F = "deferred_to_slice38f"


class RoleConceptCompatibilityMode(str, Enum):
    EXACT_ADMITTED_SUPPORT_REQUIRED = "exact_admitted_support_required"
    UNKNOWN_IF_EXACT_SUPPORT_ABSENT = "unknown_if_exact_support_absent"


class PredicateFrameResourceKind(str, Enum):
    PROVENANCE_REFERENCE = "provenance_reference"
    NAMESPACE_IDENTITY = "namespace_identity"
    PREDICATE_FRAME_IDENTITY = "predicate_frame_identity"
    FRAME_ROLE_CONSTRAINT = "frame_role_constraint"
    ROLE_CONCEPT_COMPATIBILITY = "role_concept_compatibility"
    STRUCTURAL_STATE_POLICY = "structural_state_policy"
    LIFECYCLE_AUTHORITY = "lifecycle_authority"
    LIFECYCLE_TRANSITION = "lifecycle_transition"
    REGISTRY_MANIFEST = "registry_manifest"


class PredicateFrameTransitionKind(str, Enum):
    OBSERVE = "observe"
    PROPOSE = "propose"
    ARCHITECTURE_ADMIT = "architecture_admit"
    ADMIT = "admit"
    BOUND = "bound"
    DEFER = "defer"
    MARK_UNKNOWN = "mark_unknown"
    MARK_UNRESOLVED = "mark_unresolved"
    MARK_INCOMPLETE = "mark_incomplete"
    MARK_AMBIGUOUS = "mark_ambiguous"
    MARK_UNSUPPORTED = "mark_unsupported"
    MARK_CONFLICTED = "mark_conflicted"
    QUARANTINE = "quarantine"
    DEPRECATE = "deprecate"
    SUPERSEDE = "supersede"
    REJECT = "reject"
    REQUIRE_REVIEW = "require_review"
    MARK_HISTORICAL = "mark_historical"


class PredicateFrameValidationCode(str, Enum):
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
    ACTION_ROOT_REFERENCE_INVALID = "action_root_reference_invalid"
    PREDICATE_REFERENCE_INVALID = "predicate_reference_invalid"
    ROLE_REFERENCE_INVALID = "role_reference_invalid"
    ROLE_REQUIREMENT_INVALID = "role_requirement_invalid"
    ROLE_CARDINALITY_INVALID = "role_cardinality_invalid"
    ROLE_SET_PARTITION_INVALID = "role_set_partition_invalid"
    ROLE_CO_REQUIREMENT_INVALID = "role_co_requirement_invalid"
    ROLE_CONFLICT_INVALID = "role_conflict_invalid"
    CONCEPT_COMPATIBILITY_INVALID = "concept_compatibility_invalid"
    SPEECH_ACT_CONSTRAINT_INVALID = "speech_act_constraint_invalid"
    EFFECT_CLASSIFICATION_INVALID = "effect_classification_invalid"
    STRUCTURAL_STATE_POLICY_INVALID = "structural_state_policy_invalid"
    FRAME_COMPLETION_PERMISSION_COLLAPSE = "frame_completion_permission_collapse"
    OCCURRENCE_ASSIGNMENT_PROHIBITED = "occurrence_assignment_prohibited"
    FRAME_SELECTION_PROHIBITED = "frame_selection_prohibited"
    CAPABILITY_REFERENCE_PROHIBITED = "capability_reference_prohibited"
    RUNTIME_AUTHORITY_PROHIBITED = "runtime_authority_prohibited"
    NEAREST_KNOWN_SUBSTITUTION_PROHIBITED = "nearest_known_substitution_prohibited"
    SIMILARITY_AUTHORITY_PROHIBITED = "similarity_authority_prohibited"
    REGISTRY_NOT_READ_ONLY = "registry_not_read_only"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    MANIFEST_BOUNDARY_MISMATCH = "manifest_boundary_mismatch"
    VALIDATOR_FAILED_CLOSED = "validator_failed_closed"


@dataclass(frozen=True, slots=True)
class PredicateFrameValidationIssue:
    path: str
    code: PredicateFrameValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class PredicateFrameValidationReport:
    ok: bool
    issues: tuple[PredicateFrameValidationIssue, ...]
    schema_version: str = SLICE38E_SCHEMA_VERSION


class PredicateFrameValidationError(ValueError):
    """Raised when a Slice 38E validation report is not successful."""

    def __init__(self, report: PredicateFrameValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 38E predicate-frame validation failed")


@dataclass(frozen=True, slots=True)
class PredicateFrameProvenanceReference:
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
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.PROVENANCE_REFERENCE
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("provenance_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_frame_provenance", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateFrameNamespaceIdentity:
    namespace_id: str
    namespace_key: str
    preferred_label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: PredicateFrameLifecycleState
    provenance_refs: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unknown_state_policy: str
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.NAMESPACE_IDENTITY
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("namespace_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_frame_namespace", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FrameRoleConstraint:
    constraint_id: str
    frame_key: str
    role_id: str
    role_key: str
    requirement: FrameRoleRequirement
    cardinality: FrameRoleCardinality
    condition_key: str | None
    co_required_role_ids: tuple[str, ...]
    conflicting_role_ids: tuple[str, ...]
    concept_compatibility_ref: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: PredicateFrameLifecycleState
    provenance_refs: tuple[str, ...]
    occurrence_assignment_allowed: bool
    gate_outcome_created: bool
    authority_satisfied: bool
    capability_argument_created: bool
    execution_authorized: bool
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.FRAME_ROLE_CONSTRAINT
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("constraint_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_frame_role_constraint", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RoleConceptCompatibilityRule:
    compatibility_id: str
    frame_key: str
    role_id: str
    role_key: str
    mode: RoleConceptCompatibilityMode
    allowed_concept_refs: tuple[str, ...]
    allowed_semantic_class_refs: tuple[str, ...]
    prohibited_concept_refs: tuple[str, ...]
    semantic_class_membership_sufficient: bool
    exact_concept_allowlist_required: bool
    unknown_if_exact_support_absent: bool
    external_only_support_allowed: bool
    quarantined_support_allowed: bool
    similarity_support_allowed: bool
    occurrence_assignment_allowed: bool
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: PredicateFrameLifecycleState
    provenance_refs: tuple[str, ...]
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.ROLE_CONCEPT_COMPATIBILITY
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("compatibility_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_role_concept_compatibility", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateFrameIdentity:
    frame_id: str
    namespace_id: str
    frame_key: str
    preferred_label: str
    definition: str
    linked_action_root_id: str
    linked_action_root_key: str
    linked_predicate_id: str
    linked_predicate_key: str
    purpose: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    version: str
    lifecycle_state: PredicateFrameLifecycleState
    provenance_refs: tuple[str, ...]
    required_role_constraint_refs: tuple[str, ...]
    optional_role_constraint_refs: tuple[str, ...]
    prohibited_role_constraint_refs: tuple[str, ...]
    conditional_role_constraint_refs: tuple[str, ...]
    role_cardinality_constraint_refs: tuple[str, ...]
    role_co_requirement_refs: tuple[str, ...]
    role_conflict_refs: tuple[str, ...]
    role_concept_compatibility_refs: tuple[str, ...]
    permitted_speech_acts: tuple[FrameSpeechAct, ...]
    scope_constraint_refs: tuple[str, ...]
    effect_classification: FrameEffectClassification
    authority_dependencies: tuple[str, ...]
    evidence_boundaries: tuple[str, ...]
    memory_boundaries: tuple[str, ...]
    delivery_boundaries: tuple[str, ...]
    runtime_boundaries: tuple[str, ...]
    external_resource_boundaries: tuple[str, ...]
    capability_reference_status: FrameCapabilityReferenceStatus
    capability_reference_refs: tuple[str, ...]
    unknown_frame_policy: str
    incomplete_frame_policy: str
    ambiguous_frame_policy: str
    conflicted_frame_policy: str
    unsupported_frame_policy: str
    structurally_complete_is_permission: bool
    occurrence_frame_selection_allowed: bool
    occurrence_role_assignment_allowed: bool
    frame_completion_allowed: bool
    capability_binding_allowed: bool
    gate_outcome_created: bool
    execution_authorized: bool
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.PREDICATE_FRAME_IDENTITY
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("frame_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_predicate_frame", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FrameStructuralStatePolicy:
    policy_id: str
    state: PredicateFrameStructuralState
    definition: str
    trigger_conditions: tuple[str, ...]
    preserved_obligations: tuple[str, ...]
    prohibited_consequences: tuple[str, ...]
    gate_outcome_created: bool
    permission_created: bool
    capability_binding_created: bool
    execution_authorized: bool
    version: str
    lifecycle_state: PredicateFrameLifecycleState
    provenance_refs: tuple[str, ...]
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.STRUCTURAL_STATE_POLICY
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("policy_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_structural_state_policy", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateFrameLifecycleAuthorityRecord:
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
    capability_authorized: bool
    action_authorized: bool
    version: str
    lifecycle_state: PredicateFrameLifecycleState
    provenance_refs: tuple[str, ...]
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.LIFECYCLE_AUTHORITY
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("authority_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_frame_lifecycle_authority", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateFrameLifecycleTransitionRecord:
    transition_id: str
    frame_lineage_id: str
    source_frame_id: str
    target_frame_id: str
    source_version: str
    target_version: str
    from_state: PredicateFrameLifecycleState
    to_state: PredicateFrameLifecycleState
    transition_kind: PredicateFrameTransitionKind
    reason: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    authority_record_ref: str
    human_approval: bool
    prior_record_preserved: bool
    automatic_transition: bool
    in_place_mutation_performed: bool
    frame_selection_performed: bool
    role_assignment_performed: bool
    capability_binding_performed: bool
    gate_outcome_created: bool
    runtime_authority_supplied: bool
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.LIFECYCLE_TRANSITION
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("transition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_frame_lifecycle_transition", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateFrameRegistryManifest:
    manifest_id: str
    registry_id: str
    namespace_id: str
    frame_refs: tuple[str, ...]
    frame_keys: tuple[str, ...]
    role_constraint_refs: tuple[str, ...]
    compatibility_refs: tuple[str, ...]
    structural_state_policy_refs: tuple[str, ...]
    transition_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    admitted_frame_count: int
    role_constraint_count: int
    compatibility_rule_count: int
    structural_state_policy_count: int
    transition_count: int
    active_correction_count: int
    active_conflict_count: int
    source_term_lookup_installed: bool
    occurrence_frame_selection_installed: bool
    occurrence_role_assignment_installed: bool
    candidate_meaning_creation_installed: bool
    selected_meaning_installed: bool
    gate_outcome_installed: bool
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
    nearest_known_frame_substitution_installed: bool
    semantic_similarity_installed: bool
    llm_authority_installed: bool
    registry_read_only: bool
    registry_closed: bool
    exact_identity_lookup_only: bool
    version: str
    lifecycle_state: PredicateFrameLifecycleState
    provenance_refs_manifest: tuple[str, ...]
    resource_kind: PredicateFrameResourceKind = PredicateFrameResourceKind.REGISTRY_MANIFEST
    schema_version: str = SLICE38E_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("manifest_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38e_predicate_frame_registry_manifest", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateFrameRegistry:
    manifest: PredicateFrameRegistryManifest
    current_namespace: PredicateFrameNamespaceIdentity
    admitted_frames: tuple[PredicateFrameIdentity, ...]
    frame_histories: tuple[tuple[PredicateFrameIdentity, ...], ...]
    role_constraints: tuple[FrameRoleConstraint, ...]
    compatibility_rules: tuple[RoleConceptCompatibilityRule, ...]
    structural_state_policies: tuple[FrameStructuralStatePolicy, ...]
    authority_records: tuple[PredicateFrameLifecycleAuthorityRecord, ...]
    transitions: tuple[PredicateFrameLifecycleTransitionRecord, ...]
    provenance_records: tuple[PredicateFrameProvenanceReference, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


PredicateFrameGovernedResource: TypeAlias = (
    PredicateFrameNamespaceIdentity
    | PredicateFrameIdentity
    | FrameRoleConstraint
    | RoleConceptCompatibilityRule
    | FrameStructuralStatePolicy
)
