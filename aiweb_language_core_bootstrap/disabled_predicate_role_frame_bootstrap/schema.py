"""Immutable Slice 38H disabled bootstrap and closeout contracts.

The records in this module are deterministic, standard-library-only and
in-memory.  Importing this module activates nothing and grants no meaning,
permission, route, invocation, tool, action, memory, delivery, evidence or
truth authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..disabled_structural_concept_bootstrap import (
    DisabledStructuralConceptBootstrapResult,
)
from ..predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    PredicateRoleFrameCandidateProposalResult,
)
from ..schema import stable_record_id


SLICE38H_SPEC_ID: Final[str] = "aiweb-slice38-disabled-predicate-role-frame-bootstrap"
SLICE38H_SPEC_VERSION: Final[str] = (
    "aiweb-slice38-disabled-predicate-role-frame-bootstrap-v1"
)
SLICE38H_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-slice38-disabled-predicate-role-frame-bootstrap-v1"
)

PRE_SLICE38_COMMIT: Final[str] = "f891a33487ea8bc811243627f1d834be7a43f972"
PRE_SLICE38_TREE: Final[str] = "f087c3f6cec8caecc19539628b1d4ab08b4918c1"
SLICE38G_ACCEPTED_HEAD: Final[str] = "bf8ef1893c4093e950676699155c41dac4f34b2b"
SLICE38G_ACCEPTED_TREE: Final[str] = "ad5180f412b91aafde6eba875ffda4f17779c1d5"
SLICE38G_ACCEPTED_SUBJECT: Final[str] = (
    "Slice 38G predicate role and frame candidate proposal"
)
SLICE38H_COMMIT_SUBJECT: Final[str] = (
    "Slice 38H disabled bootstrap integration and Slice 38 closeout"
)

SLICE38_INCREMENT_LABELS: Final[tuple[str, ...]] = (
    "38A", "38B", "38C", "38D", "38E", "38F", "38G", "38H",
)

SLICE38_ACCEPTED_CHAIN: Final[tuple[str, ...]] = (
    "accepted Slice 37G disabled structural-concept bootstrap result",
    "exact Slice 37F concept and sense candidate proposal",
    "exact structural ancestry and registry-snapshot custody",
    "Slice 38C admitted action-root and predicate lookup",
    "Slice 38D admitted participant-role identity lookup",
    "Slice 38E compatible predicate-frame identity lookup",
    "Slice 38F non-operational capability-family reference lookup",
    "Slice 38G zero-one-many candidate proposal or explicit non-progress",
)

SLICE38_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "surface verb != action root",
    "action concept != predicate identity",
    "predicate identity != predicate frame",
    "semantic relation != participant role",
    "concept compatibility != role assignment",
    "role assignment candidate != admitted participant assignment",
    "complete frame != selected frame",
    "complete frame != permission",
    "speech act != action",
    "request != authorization",
    "report != evidence",
    "verification predicate != verified status",
    "memory predicate != memory access",
    "delivery predicate != delivery authority",
    "installation predicate != code-application authority",
    "capability reference != route",
    "route reference != invocation",
    "effect classification != execution",
    "unknown predicate != nearest known predicate",
    "large predicate registry != capable mind",
    "scale != authority",
)

SLICE38_ACCEPTED_SCOPE: Final[tuple[str, ...]] = (
    "controlled action-root and predicate identities",
    "controlled participant-role identities",
    "controlled predicate-frame constraints",
    "non-operational capability-family references",
    "effect-boundary classifications",
    "source-preserving predicate-role-frame candidate proposals",
    "explicit unknown unsupported incomplete ambiguous and conflicted states",
    "disabled exact-fixture bootstrap integration",
    "deterministic repeated-result proof",
    "protected-predecessor checksum proof",
    "disposable-clone pre-Slice-38 recovery proof",
    "exact future staged-path containment declaration",
)

SLICE38_DEFERRED_SCOPE: Final[tuple[str, ...]] = (
    "public runtime activation",
    "arbitrary text invocation",
    "candidate selection",
    "selected predicate",
    "selected frame",
    "selected participant assignment",
    "CandidateMeaning construction",
    "selected meaning",
    "ambiguity resolution",
    "clarification",
    "refusal",
    "blocked progression",
    "truth determination",
    "evidence validity",
    "permission",
    "capability availability",
    "route creation",
    "invocation",
    "tool use",
    "action execution",
    "memory access",
    "external-resource admission",
    "rendering",
    "delivery",
    "release authorization",
    "production readiness",
)


class CloseoutIntegrationStatus(str, Enum):
    REFUSED_DISABLED = "REFUSED_DISABLED"
    HELD_INVALID_STATE = "HELD_INVALID_STATE"
    HELD_INVALID_INVOCATION = "HELD_INVALID_INVOCATION"
    HELD_FIXTURE_NOT_ACCEPTED = "HELD_FIXTURE_NOT_ACCEPTED"
    HELD_INVALID_PROFILE = "HELD_INVALID_PROFILE"
    HELD_INVALID_PREDECESSOR_OUTPUT = "HELD_INVALID_PREDECESSOR_OUTPUT"
    HELD_EXPECTATION_MISMATCH = "HELD_EXPECTATION_MISMATCH"
    COMPLETED_EXPLICIT_UNKNOWN = "COMPLETED_EXPLICIT_UNKNOWN"
    COMPLETED_EXPLICIT_UNSUPPORTED = "COMPLETED_EXPLICIT_UNSUPPORTED"


class CloseoutIntegrationStage(str, Enum):
    SLICE37_DISABLED_BOOTSTRAP = "slice37g_disabled_structural_concept_bootstrap"
    SLICE38_CANDIDATE_PROPOSAL = "slice38g_predicate_role_frame_candidate_proposal"


@dataclass(frozen=True, slots=True)
class DisabledPredicateRoleFrameBootstrapState:
    state_id: str
    enabled: bool
    explicit_offline_developer_enable: bool
    disabled_by_default: bool
    explicit_invocation_required: bool
    accepted_static_fixture_only: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    read_only: bool
    in_memory_only: bool
    exact_profile_bounded: bool
    source_preserving: bool
    structural_ancestry_preserving: bool
    operator_ancestry_preserving: bool
    phase_trail_ancestry_preserving: bool
    scope_attachment_ancestry_preserving: bool
    registry_snapshot_preserving: bool
    zero_one_many_preserving: bool
    explicit_non_progress_preserving: bool
    rollback_safe: bool
    automatic_activation_allowed: bool
    arbitrary_text_invocation_allowed: bool
    normalization_allowed: bool
    nearest_known_substitution_allowed: bool
    semantic_similarity_allowed: bool
    learned_model_allowed: bool
    external_resource_loading_allowed: bool
    filesystem_read_allowed: bool
    filesystem_write_allowed: bool
    network_allowed: bool
    memory_read_allowed: bool
    memory_write_allowed: bool
    api_route_allowed: bool
    capability_route_allowed: bool
    invocation_allowed: bool
    tool_allowed: bool
    action_allowed: bool
    rendering_allowed: bool
    delivery_allowed: bool
    selected_predicate_allowed: bool
    selected_frame_allowed: bool
    selected_participant_assignment_allowed: bool
    candidate_meaning_allowed: bool
    selected_meaning_allowed: bool
    clarification_allowed: bool
    refusal_allowed: bool
    blocked_progression_allowed: bool
    truth_allowed: bool
    evidence_validity_allowed: bool
    permission_allowed: bool
    runtime_self_acceptance_allowed: bool
    release_authorized: bool
    production_ready: bool
    spec_id: str = SLICE38H_SPEC_ID
    spec_version: str = SLICE38H_SPEC_VERSION
    schema_version: str = SLICE38H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38h_bootstrap_state", self.canonical_body())


@dataclass(frozen=True, slots=True)
class DisabledPredicateRoleFrameFixture:
    fixture_id: str
    fixture_name: str
    slice37_fixture_name: str
    expected_slice37_status: str
    expected_slice38_status: str
    expected_action_predicate_candidate_count: int
    expected_role_layout_candidate_count: int
    expected_capability_reference_candidate_count: int
    accepted_fixture: bool
    synthetic: bool
    explicit_invocation_only: bool
    offline_only: bool
    in_memory_only: bool
    raw_text_not_carried_by_invocation: bool
    schema_version: str = SLICE38H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("fixture_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38h_fixture", self.canonical_body())


@dataclass(frozen=True, slots=True)
class DisabledPredicateRoleFrameInvocation:
    invocation_id: str
    fixture_name: str
    fixture_id: str
    proposal_profile_id: str
    compatibility_snapshot_id: str
    slice38_registry_snapshot_id: str
    explicit_invocation: bool
    requested_operation: str
    raw_text_carried_by_invocation: bool
    schema_version: str = SLICE38H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("invocation_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38h_invocation", self.canonical_body())


@dataclass(frozen=True, slots=True)
class CloseoutStageReceipt:
    receipt_id: str
    state_id: str
    invocation_id: str
    fixture_id: str
    stage_ordinal: int
    stage: CloseoutIntegrationStage
    predecessor_record_ids: tuple[str, ...]
    output_record_id: str
    output_schema_version: str
    output_exact_type: str
    output_validation_passed: bool
    source_event_id: str
    source_sha256: str
    source_ancestry_preserved: bool
    candidate_only: bool
    selected_predicate_created: bool
    selected_frame_created: bool
    selected_participant_assignment_created: bool
    candidate_meaning_created: bool
    selected_meaning_created: bool
    permission_inferred: bool
    route_created: bool
    invocation_proposed: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    evidence_validity_determined: bool
    truth_determined: bool
    schema_version: str = SLICE38H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("receipt_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38h_stage_receipt", self.canonical_body())


@dataclass(frozen=True, slots=True)
class Slice38RollbackMetadata:
    rollback_id: str
    pre_slice38_commit: str
    pre_slice38_tree: str
    accepted_parent_head: str
    accepted_parent_tree: str
    accepted_parent_subject: str
    expected_closeout_commit_subject: str
    exact_commit_checkout_required: bool
    exact_tree_match_required: bool
    separate_recovery_clone_required: bool
    git_object_verification_required: bool
    live_repository_mutation_authorized: bool
    runtime_rollback_execution_authorized: bool
    rollback_proof_external_to_runtime: bool
    schema_version: str = SLICE38H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("rollback_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38_rollback_metadata", self.canonical_body())


@dataclass(frozen=True, slots=True)
class Slice38AcceptanceRecord:
    acceptance_record_id: str
    decision_owner: str
    accepted_increment_labels: tuple[str, ...]
    accepted_chain: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    accepted_scope: tuple[str, ...]
    deferred_scope: tuple[str, ...]
    rollback_metadata_id: str
    accepted_parent_head: str
    accepted_parent_tree: str
    pre_slice38_commit: str
    pre_slice38_tree: str
    disabled_by_default: bool
    explicitly_invoked_only: bool
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    read_only: bool
    exact_profile_bounded: bool
    source_preserving: bool
    no_selected_predicate_authority: bool
    no_selected_frame_authority: bool
    no_selected_participant_authority: bool
    no_candidate_meaning_authority: bool
    no_selected_meaning_authority: bool
    no_permission_authority: bool
    no_route_authority: bool
    no_action_authority: bool
    no_memory_authority: bool
    no_delivery_authority: bool
    runtime_self_grants_acceptance: bool
    decision_owner_acceptance_required: bool
    release_authorized: bool
    production_ready: bool
    schema_version: str = SLICE38H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("acceptance_record_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38_acceptance_record", self.canonical_body())


@dataclass(frozen=True, slots=True)
class DisabledPredicateRoleFrameBootstrapResult:
    result_id: str
    state_id: str
    invocation_id: str
    fixture_id: str
    status: CloseoutIntegrationStatus
    reason_code: str
    stage_receipts: tuple[CloseoutStageReceipt, ...]
    stage_receipt_count: int
    exact_stage_chain_complete: bool
    source_event_id: str
    source_sha256: str
    slice37_result: DisabledStructuralConceptBootstrapResult | None
    slice38_result: PredicateRoleFrameCandidateProposalResult | None
    acceptance_record: Slice38AcceptanceRecord
    rollback_metadata: Slice38RollbackMetadata
    action_predicate_candidate_count: int
    role_layout_candidate_count: int
    capability_reference_candidate_count: int
    unresolved_alternative_count: int
    missing_role_count: int
    conflicting_role_count: int
    disabled_by_default: bool
    explicitly_invoked: bool
    fixture_only: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    read_only: bool
    in_memory_only: bool
    exact_profile_bounded: bool
    source_preserved: bool
    structural_ancestry_preserved: bool
    operator_ancestry_preserved: bool
    phase_trail_ancestry_preserved: bool
    scope_attachment_ancestry_preserved: bool
    registry_snapshots_preserved: bool
    zero_one_many_preserved: bool
    selected_predicate_created: bool
    selected_frame_created: bool
    selected_participant_assignment_created: bool
    candidate_meaning_created: bool
    selected_meaning_created: bool
    clarification_outcome_created: bool
    refusal_outcome_created: bool
    blocked_progression_outcome_created: bool
    permission_inferred: bool
    capability_availability_created: bool
    route_created: bool
    invocation_proposed: bool
    tool_invoked: bool
    action_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    outward_rendered: bool
    delivered: bool
    evidence_validity_determined: bool
    truth_determined: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    semantic_similarity_used: bool
    technical_acceptance_granted_by_runtime: bool
    release_authorized: bool
    production_ready: bool
    schema_version: str = SLICE38H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice38h_bootstrap_result", self.canonical_body())
