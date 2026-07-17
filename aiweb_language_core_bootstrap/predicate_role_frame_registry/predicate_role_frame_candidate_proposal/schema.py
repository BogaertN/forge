"""Immutable Slice 38G predicate, role, and frame candidate records.

This module is candidate-only.  It preserves exact ancestry and governed
registry identities, but it does not select a predicate, frame, participant
assignment, CandidateMeaning, selected meaning, permission, route, action,
memory operation, delivery, evidence status, or truth value.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, ClassVar, Final

from ...schema import stable_record_id


SLICE38G_SPEC_ID: Final[str] = (
    "aiweb-slice38g-predicate-role-frame-candidate-proposal"
)
SLICE38G_SPEC_VERSION: Final[str] = (
    "aiweb-slice38g-predicate-role-frame-candidate-proposal-v1"
)
SLICE38G_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-predicate-role-frame-candidate-proposal-v1"
)
SLICE38G_ACCEPTED_PARENT_HEAD: Final[str] = (
    "9d135e51979657ee354cabd014e02df620d05d17"
)
SLICE38G_ACCEPTED_PARENT_TREE: Final[str] = (
    "27ad163d8e77975e3963fa5d0efb95a4f16acab2"
)
SLICE38G_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 38F capability-family references and effect boundaries"
)

PROFILE_SCHEMA_ID: Final[str] = "aiweb.slice38g.profile.v1"
COMPATIBILITY_RULE_SCHEMA_ID: Final[str] = "aiweb.slice38g.compatibility_rule.v1"
COMPATIBILITY_CONFLICT_SCHEMA_ID: Final[str] = (
    "aiweb.slice38g.compatibility_conflict.v1"
)
COMPATIBILITY_SNAPSHOT_SCHEMA_ID: Final[str] = (
    "aiweb.slice38g.compatibility_snapshot.v1"
)
SLICE38_SNAPSHOT_SCHEMA_ID: Final[str] = "aiweb.slice38g.slice38_snapshot.v1"
ACTION_PREDICATE_CANDIDATE_SCHEMA_ID: Final[str] = (
    "aiweb.slice38g.action_predicate_candidate.v1"
)
ROLE_LAYOUT_CANDIDATE_SCHEMA_ID: Final[str] = (
    "aiweb.slice38g.role_layout_candidate.v1"
)
CAPABILITY_REFERENCE_CANDIDATE_SCHEMA_ID: Final[str] = (
    "aiweb.slice38g.capability_reference_candidate.v1"
)
RESULT_SCHEMA_ID: Final[str] = "aiweb.slice38g.result.v1"


class CandidateProposalStatus(str, Enum):
    CANDIDATES_PROPOSED = "candidates_proposed"
    STRUCTURALLY_INCOMPLETE = "structurally_incomplete"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    EXPLICIT_UNKNOWN = "explicit_unknown"
    EXPLICIT_UNSUPPORTED = "explicit_unsupported"
    PREDECESSOR_REJECTED = "predecessor_rejected"


class CandidateStructuralState(str, Enum):
    STRUCTURALLY_COMPLETE = "structurally_complete"
    STRUCTURALLY_INCOMPLETE = "structurally_incomplete"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class CompatibilityMatchMode(str, Enum):
    EXACT_CONCEPT = "exact_concept"
    EXACT_SENSE = "exact_sense"
    EXACT_CONCEPT_AND_SENSE = "exact_concept_and_sense"


class CompatibilityLifecycleState(str, Enum):
    CANDIDATE = "candidate"
    ARCHITECTURE_ADMITTED = "architecture_admitted"
    DEFERRED = "deferred"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"


class CandidateValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_TEXT = "invalid_text"
    INVALID_ENUM = "invalid_enum"
    INVALID_TUPLE = "invalid_tuple"
    DUPLICATE_VALUE = "duplicate_value"
    IDENTITY_MISMATCH = "identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    REFERENCE_NOT_FOUND = "reference_not_found"
    REFERENCE_VERSION_MISMATCH = "reference_version_mismatch"
    CROSS_REGISTRY_MISMATCH = "cross_registry_mismatch"
    COUNT_MISMATCH = "count_mismatch"
    ANCESTRY_MISMATCH = "ancestry_mismatch"
    STATUS_MISMATCH = "status_mismatch"
    AUTHORITY_BOUNDARY_VIOLATION = "authority_boundary_violation"
    SNAPSHOT_MISMATCH = "snapshot_mismatch"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    VALIDATOR_FAILED_CLOSED = "validator_failed_closed"


class CandidateValidationError(ValueError):
    """Raised only by explicit assertion helpers."""


@dataclass(frozen=True, slots=True)
class CandidateValidationIssue:
    path: str
    code: CandidateValidationCode
    detail: str

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "code": self.code.value,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class CandidateValidationReport:
    ok: bool
    issues: tuple[CandidateValidationIssue, ...]
    schema_version: str = SLICE38G_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "issues": tuple(item.to_dict() for item in self.issues),
            "schema_version": self.schema_version,
        }


class _StableRecord:
    """Shared deterministic identity behavior for immutable records."""

    _id_field: str
    _id_namespace: str

    def canonical_body(self) -> dict[str, object]:
        body = _plain(asdict(self))
        body.pop(self._id_field)
        return body

    def expected_id(self) -> str:
        return stable_record_id(self._id_namespace, self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return _plain(asdict(self))


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_plain(item) for item in value)
    if isinstance(value, list):
        return tuple(_plain(item) for item in value)
    if value is None or type(value) in (str, bool, int, float):
        return value
    raise TypeError(f"unsupported canonical value type: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class PredicateRoleFrameProposalProfile(_StableRecord):
    profile_id: str
    profile_key: str
    profile_version: str
    explicit_invocation_required: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    immutable_records: bool
    exact_source_ancestry_required: bool
    exact_registry_snapshot_required: bool
    exact_identity_lookup_only: bool
    zero_one_many_preserved: bool
    unresolved_alternatives_preserved: bool
    explicit_unknown_required: bool
    explicit_unsupported_required: bool
    incomplete_state_required: bool
    conflict_state_required: bool
    caller_supplied_surface_hint_allowed: bool
    normalization_allowed: bool
    nearest_known_substitution_allowed: bool
    semantic_similarity_allowed: bool
    language_model_allowed: bool
    selected_predicate_allowed: bool
    selected_frame_allowed: bool
    selected_participant_assignment_allowed: bool
    candidate_meaning_creation_allowed: bool
    selected_meaning_allowed: bool
    permission_inference_allowed: bool
    route_creation_allowed: bool
    tool_invocation_allowed: bool
    action_execution_allowed: bool
    memory_access_allowed: bool
    delivery_allowed: bool
    evidence_validity_allowed: bool
    truth_determination_allowed: bool
    clarification_outcome_allowed: bool
    refusal_outcome_allowed: bool
    blocked_progression_outcome_allowed: bool
    non_authority_boundaries: tuple[str, ...]
    spec_id: str = SLICE38G_SPEC_ID
    spec_version: str = SLICE38G_SPEC_VERSION
    schema_version: str = SLICE38G_SCHEMA_VERSION
    profile_schema_id: str = PROFILE_SCHEMA_ID

    _id_field: ClassVar[str] = "profile_id"
    _id_namespace: ClassVar[str] = "slice38g_proposal_profile"


@dataclass(frozen=True, slots=True)
class ActionRootCompatibilityRule(_StableRecord):
    rule_id: str
    rule_key: str
    match_mode: CompatibilityMatchMode
    concept_id: str | None
    concept_version: str | None
    sense_id: str | None
    sense_version: str | None
    action_root_id: str
    action_root_key: str
    action_root_version: str
    predicate_id: str
    predicate_key: str
    predicate_version: str
    allowed_frame_ids: tuple[str, ...]
    scope_tags: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    version: str
    lifecycle_state: CompatibilityLifecycleState
    candidate_only: bool
    selection_authority: bool
    permission_authority: bool
    route_authority: bool
    execution_authority: bool
    schema_version: str = SLICE38G_SCHEMA_VERSION
    rule_schema_id: str = COMPATIBILITY_RULE_SCHEMA_ID

    _id_field: ClassVar[str] = "rule_id"
    _id_namespace: ClassVar[str] = "slice38g_action_root_compatibility_rule"


@dataclass(frozen=True, slots=True)
class ActionRootCompatibilityConflict(_StableRecord):
    conflict_id: str
    conflict_key: str
    rule_refs: tuple[str, ...]
    concept_refs: tuple[str, ...]
    sense_refs: tuple[str, ...]
    action_root_refs: tuple[str, ...]
    conflict_kind: str
    reason: str
    scope_tags: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version: str
    lifecycle_state: CompatibilityLifecycleState
    operative: bool
    resolved: bool
    selected_rule_ref: str | None
    schema_version: str = SLICE38G_SCHEMA_VERSION
    conflict_schema_id: str = COMPATIBILITY_CONFLICT_SCHEMA_ID

    _id_field: ClassVar[str] = "conflict_id"
    _id_namespace: ClassVar[str] = "slice38g_action_root_compatibility_conflict"


@dataclass(frozen=True, slots=True)
class CompatibilityRegistrySnapshot(_StableRecord):
    snapshot_id: str
    registry_key: str
    registry_version: str
    rule_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    rules: tuple[ActionRootCompatibilityRule, ...]
    conflicts: tuple[ActionRootCompatibilityConflict, ...]
    rule_count: int
    conflict_count: int
    exact_identity_lookup_only: bool
    closed_world: bool
    runtime_mutation_allowed: bool
    automatic_mapping_allowed: bool
    nearest_known_substitution_allowed: bool
    semantic_similarity_allowed: bool
    language_model_allowed: bool
    selection_authority: bool
    permission_authority: bool
    route_authority: bool
    execution_authority: bool
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE38G_SCHEMA_VERSION
    snapshot_schema_id: str = COMPATIBILITY_SNAPSHOT_SCHEMA_ID

    _id_field: ClassVar[str] = "snapshot_id"
    _id_namespace: ClassVar[str] = "slice38g_compatibility_registry_snapshot"


@dataclass(frozen=True, slots=True)
class Slice38RegistrySnapshotIdentity(_StableRecord):
    snapshot_id: str
    action_root_manifest_id: str
    action_root_registry_version: str
    action_root_count: int
    predicate_count: int
    participant_role_manifest_id: str
    participant_role_registry_version: str
    participant_role_count: int
    predicate_frame_manifest_id: str
    predicate_frame_registry_version: str
    predicate_frame_count: int
    frame_role_constraint_count: int
    frame_role_concept_compatibility_count: int
    capability_reference_manifest_id: str
    capability_reference_registry_version: str
    effect_boundary_count: int
    capability_family_count: int
    frame_effect_reference_count: int
    frame_capability_reference_count: int
    exact_snapshot: bool
    external_resources_loaded: bool
    runtime_mutation_allowed: bool
    schema_version: str = SLICE38G_SCHEMA_VERSION
    snapshot_schema_id: str = SLICE38_SNAPSHOT_SCHEMA_ID

    _id_field: ClassVar[str] = "snapshot_id"
    _id_namespace: ClassVar[str] = "slice38g_slice38_registry_snapshot"


@dataclass(frozen=True, slots=True)
class CapabilityReferenceCandidate(_StableRecord):
    candidate_id: str
    frame_id: str
    frame_key: str
    frame_version: str
    frame_capability_reference_id: str
    frame_capability_reference_version: str
    capability_family_id: str
    capability_family_key: str
    capability_family_version: str
    effect_boundary_id: str
    effect_boundary_key: str
    effect_boundary_version: str
    availability_status: str
    relevance_mode: str
    source_concept_candidate_proposal_ids: tuple[str, ...]
    source_sense_candidate_proposal_ids: tuple[str, ...]
    candidate_only: bool
    capability_available: bool
    route_created: bool
    invocation_proposed: bool
    invocation_authorized: bool
    arguments_constructed: bool
    permission_granted: bool
    execution_performed: bool
    result_verified: bool
    memory_operation_performed: bool
    delivery_performed: bool
    evidence_validated: bool
    truth_determined: bool
    schema_version: str = SLICE38G_SCHEMA_VERSION
    candidate_schema_id: str = CAPABILITY_REFERENCE_CANDIDATE_SCHEMA_ID

    _id_field: ClassVar[str] = "candidate_id"
    _id_namespace: ClassVar[str] = "slice38g_capability_reference_candidate"


@dataclass(frozen=True, slots=True)
class RoleLayoutCandidate(_StableRecord):
    candidate_id: str
    frame_id: str
    frame_key: str
    frame_version: str
    action_root_id: str
    action_root_key: str
    action_root_version: str
    predicate_id: str
    predicate_key: str
    predicate_version: str
    required_roles: tuple[tuple[str, str, str], ...]
    optional_roles: tuple[tuple[str, str, str], ...]
    prohibited_roles: tuple[tuple[str, str, str], ...]
    conditional_roles: tuple[tuple[str, str, str], ...]
    missing_required_role_ids: tuple[str, ...]
    conflicting_role_ids: tuple[str, ...]
    unresolved_alternative_role_ids: tuple[str, ...]
    effect_boundary_id: str
    effect_boundary_key: str
    effect_boundary_version: str
    frame_effect_reference_id: str
    frame_effect_reference_version: str
    capability_reference_candidate_ids: tuple[str, ...]
    structural_state: CandidateStructuralState
    source_structural_ancestry_ids: tuple[str, ...]
    source_concept_candidate_proposal_ids: tuple[str, ...]
    source_sense_candidate_proposal_ids: tuple[str, ...]
    candidate_only: bool
    frame_selected: bool
    participant_assignments_created: bool
    frame_completed: bool
    permission_inferred: bool
    gate_outcome_created: bool
    route_created: bool
    execution_performed: bool
    schema_version: str = SLICE38G_SCHEMA_VERSION
    candidate_schema_id: str = ROLE_LAYOUT_CANDIDATE_SCHEMA_ID

    _id_field: ClassVar[str] = "candidate_id"
    _id_namespace: ClassVar[str] = "slice38g_role_layout_candidate"


@dataclass(frozen=True, slots=True)
class ActionRootPredicateCandidate(_StableRecord):
    candidate_id: str
    compatibility_rule_id: str
    compatibility_rule_version: str
    source_concept_candidate_proposal_ids: tuple[str, ...]
    source_sense_candidate_proposal_ids: tuple[str, ...]
    source_concept_ids_and_versions: tuple[tuple[str, str], ...]
    source_sense_ids_and_versions: tuple[tuple[str, str], ...]
    action_root_id: str
    action_root_key: str
    action_root_version: str
    predicate_id: str
    predicate_key: str
    predicate_version: str
    frame_ids_and_versions: tuple[tuple[str, str], ...]
    role_layout_candidate_ids: tuple[str, ...]
    capability_reference_candidate_ids: tuple[str, ...]
    unresolved_alternative_candidate_ids: tuple[str, ...]
    structural_state: CandidateStructuralState
    candidate_only: bool
    predicate_selected: bool
    frame_selected: bool
    participant_assignment_selected: bool
    candidate_meaning_created: bool
    selected_meaning_created: bool
    permission_inferred: bool
    route_created: bool
    action_performed: bool
    memory_accessed: bool
    delivered: bool
    evidence_validity_determined: bool
    truth_determined: bool
    schema_version: str = SLICE38G_SCHEMA_VERSION
    candidate_schema_id: str = ACTION_PREDICATE_CANDIDATE_SCHEMA_ID

    _id_field: ClassVar[str] = "candidate_id"
    _id_namespace: ClassVar[str] = "slice38g_action_root_predicate_candidate"


@dataclass(frozen=True, slots=True)
class PredicateRoleFrameCandidateProposalResult(_StableRecord):
    result_id: str
    status: CandidateProposalStatus
    reason_code: str
    source_slice37_result_id: str
    source_slice37_status: str
    source_event_id: str
    source_sha256: str
    input_event_id: str
    root_source_span_id: str
    projection_id: str
    structural_result_id: str
    structural_set_id: str
    source_span_ids: tuple[str, ...]
    structural_ancestry_ids: tuple[str, ...]
    phase_trail_ids: tuple[str, ...]
    constrained_trail_ids: tuple[str, ...]
    operator_graph_ids: tuple[str, ...]
    operator_node_ids: tuple[str, ...]
    operator_definition_ids: tuple[str, ...]
    operator_keys_and_versions: tuple[tuple[str, str], ...]
    scope_occurrence_ids: tuple[str, ...]
    attachment_candidate_ids: tuple[str, ...]
    reference_analysis_ids: tuple[str, ...]
    reference_candidate_ids: tuple[str, ...]
    concept_candidate_proposal_ids: tuple[str, ...]
    sense_candidate_proposal_ids: tuple[str, ...]
    concept_ids_and_versions: tuple[tuple[str, str], ...]
    sense_ids_and_versions: tuple[tuple[str, str], ...]
    slice37_registry_snapshot_id: str
    slice38_registry_snapshot: Slice38RegistrySnapshotIdentity
    compatibility_registry_snapshot: CompatibilityRegistrySnapshot
    action_predicate_candidates: tuple[ActionRootPredicateCandidate, ...]
    role_layout_candidates: tuple[RoleLayoutCandidate, ...]
    capability_reference_candidates: tuple[CapabilityReferenceCandidate, ...]
    unresolved_alternative_candidate_ids: tuple[str, ...]
    missing_role_ids: tuple[str, ...]
    conflicting_role_ids: tuple[str, ...]
    unsupported_reasons: tuple[str, ...]
    unknown_reasons: tuple[str, ...]
    action_predicate_candidate_count: int
    role_layout_candidate_count: int
    capability_reference_candidate_count: int
    unresolved_alternative_count: int
    missing_role_count: int
    conflicting_role_count: int
    source_ancestry_preserved: bool
    operator_ancestry_preserved: bool
    phase_trail_ancestry_preserved: bool
    scope_attachment_ancestry_preserved: bool
    registry_snapshots_preserved: bool
    zero_one_many_preserved: bool
    capability_non_invocation_boundary_preserved: bool
    candidate_order_is_ranked: bool
    selected_predicate_created: bool
    selected_frame_created: bool
    selected_participant_assignment_created: bool
    candidate_meaning_created: bool
    selected_meaning_created: bool
    permission_inferred: bool
    tool_route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    delivered: bool
    evidence_validity_determined: bool
    truth_determined: bool
    clarification_outcome_created: bool
    refusal_outcome_created: bool
    blocked_progression_outcome_created: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    semantic_similarity_used: bool
    profile: PredicateRoleFrameProposalProfile
    non_authority_boundaries: tuple[str, ...]
    spec_id: str = SLICE38G_SPEC_ID
    spec_version: str = SLICE38G_SPEC_VERSION
    schema_version: str = SLICE38G_SCHEMA_VERSION
    result_schema_id: str = RESULT_SCHEMA_ID

    _id_field: ClassVar[str] = "result_id"
    _id_namespace: ClassVar[str] = "slice38g_predicate_role_frame_candidate_result"
