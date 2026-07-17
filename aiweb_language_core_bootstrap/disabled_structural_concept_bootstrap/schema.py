"""Immutable Slice 37G disabled structural-to-concept bootstrap contracts.

Slice 37G connects the already accepted deterministic Slice 36 structural
pipeline to the accepted Slice 37 controlled registry and candidate-proposal
surface. Importing this module activates nothing and performs no I/O.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..candidate_resonant_phase_trail import CandidateResonantPhaseTrailResult
from ..deterministic_structural_derivation import (
    DeterministicStructuralDerivationResult,
)
from ..input_event_custody import InputEventCaptureResult
from ..resonant_operator_candidate_binding import (
    ResonantOperatorCandidateBindingResult,
)
from ..scope_attachment_reference_constraints import (
    ScopeAttachmentReferenceConstraintResult,
)
from ..schema import stable_record_id
from ..source_field_projection import SourceFieldProjectionResult
from ..structural_concept_candidate_proposal import (
    StructuralConceptCandidateProposalResult,
    StructuralConceptProposalProfile,
)
from ..symbolic_grammar_operator_registry import SymbolicGrammarOperatorRegistry


SLICE37G_SPEC_ID: Final[str] = (
    "aiweb-slice37g-disabled-structural-concept-bootstrap"
)
SLICE37G_SPEC_VERSION: Final[str] = (
    "aiweb-slice37g-disabled-structural-concept-bootstrap-v1"
)
SLICE37G_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-disabled-structural-concept-bootstrap-v1"
)

PRE_SLICE37_COMMIT: Final[str] = "5bd8a39b91e7ead06523e7fd0aa3ee057c795f74"
PRE_SLICE37_TREE: Final[str] = "16a7708c5ea8b208224bd3ef7a51375c8f980138"
SLICE37F_ACCEPTED_HEAD: Final[str] = "dc8f763849cd5519b7532e53615d7cac1f74d1de"
SLICE37F_ACCEPTED_TREE: Final[str] = "b1e3681da79fbdb6ad4418d7fb699d88aa8a8e41"
SLICE37F_ACCEPTED_SUBJECT: Final[str] = (
    "Slice 37F structural-to-concept candidate proposal"
)
SLICE37G_COMMIT_SUBJECT: Final[str] = (
    "Slice 37G disabled integration and Slice 37 closeout"
)

SLICE37_INCREMENT_LABELS: Final[tuple[str, ...]] = (
    "37A",
    "37B",
    "37C",
    "37D",
    "37E",
    "37F",
    "37G",
)

SLICE37_ACCEPTED_CHAIN: Final[tuple[str, ...]] = (
    "explicit accepted static fixture invocation",
    "Slice 36A exact input-event custody",
    "Slice 36B reversible source-field projection",
    "Slice 36C controlled symbolic grammar-operator registry",
    "Slice 36D source-bound resonant operator candidate binding",
    "Slice 36E immutable candidate resonant phase trails",
    "Slice 36F scope attachment and reference constraints",
    "Slice 36G deterministic structural derivation or lawful non-progress",
    "Slice 37C exact controlled concept registry snapshot",
    "Slice 37D exact sense and term mapping lookup",
    "Slice 37E structural semantic-class and relation-type metadata",
    "Slice 37F zero-one-many structural concept and sense candidate proposal",
)

SLICE37_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "surface term != concept",
    "concept != sense",
    "concept candidate != admitted concept",
    "term mapping != occurrence interpretation",
    "mapped term != selected sense",
    "sense candidate != selected meaning",
    "semantic class != authority class",
    "semantic relation type != relation fact",
    "semantic relation instance != truth",
    "source relation != source reliability",
    "evidence relation != evidence validity",
    "verification relation != verified status",
    "action concept != predicate identity",
    "action concept != permission",
    "capability concept != route",
    "memory concept != memory access",
    "delivery concept != delivery authority",
    "large registry != capable mind",
    "scale != authority",
)

SLICE37_ACCEPTED_SCOPE: Final[tuple[str, ...]] = (
    "controlled concept identity schema",
    "deterministic concept validation and lifecycle law",
    "minimal built-in concept registry",
    "controlled sense and exact term mapping registry",
    "semantic classes and relation type rules without relation facts",
    "source-preserving structural-to-concept candidate proposals",
    "disabled explicit offline bootstrap integration",
    "exact-profile bounded deterministic fixture execution",
    "first-class unknown and unsupported results",
    "complete Slice 37 rollback and closeout metadata",
)

SLICE37_DEFERRED_SCOPE: Final[tuple[str, ...]] = (
    "public or automatic language runtime activation",
    "CandidateMeaning construction",
    "selected meaning or selected sense",
    "predicate identity and participant roles",
    "truth or evidence validity",
    "clarification dialogue",
    "permission or capability authority",
    "route or tool invocation",
    "action execution",
    "memory read or write",
    "external linguistic resources",
    "outward rendering",
    "delivery",
    "release authorization",
    "production readiness",
)


class IntegrationStatus(str, Enum):
    REFUSED_DISABLED = "REFUSED_DISABLED"
    HELD_INVALID_STATE = "HELD_INVALID_STATE"
    HELD_INVALID_INVOCATION = "HELD_INVALID_INVOCATION"
    HELD_FIXTURE_NOT_ACCEPTED = "HELD_FIXTURE_NOT_ACCEPTED"
    HELD_INVALID_PROFILE = "HELD_INVALID_PROFILE"
    HELD_INVALID_BOOTSTRAP_BOUNDARY = "HELD_INVALID_BOOTSTRAP_BOUNDARY"
    HELD_STAGE_OUTPUT = "HELD_STAGE_OUTPUT"
    HELD_EXPECTATION_MISMATCH = "HELD_EXPECTATION_MISMATCH"
    COMPLETED_CANDIDATES = "COMPLETED_CANDIDATES"
    COMPLETED_UNRESOLVED = "COMPLETED_UNRESOLVED"
    COMPLETED_EXPLICIT_UNKNOWN = "COMPLETED_EXPLICIT_UNKNOWN"
    COMPLETED_EXPLICIT_UNSUPPORTED = "COMPLETED_EXPLICIT_UNSUPPORTED"


class IntegrationStage(str, Enum):
    INPUT_CUSTODY = "slice36a_input_custody"
    SOURCE_FIELD_PROJECTION = "slice36b_source_field_projection"
    OPERATOR_REGISTRY = "slice36c_operator_registry"
    OPERATOR_CANDIDATE_BINDING = "slice36d_operator_candidate_binding"
    PHASE_TRAIL_CONSTRUCTION = "slice36e_phase_trail_construction"
    SCOPE_REFERENCE_CONSTRAINTS = "slice36f_scope_reference_constraints"
    STRUCTURAL_DERIVATION = "slice36g_structural_derivation"
    CONCEPT_SENSE_PROPOSAL = "slice37f_structural_concept_candidate_proposal"


@dataclass(frozen=True, slots=True)
class DisabledStructuralConceptBootstrapState:
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
    registry_snapshot_preserving: bool
    zero_one_many_preserving: bool
    explicit_unknown_preserving: bool
    explicit_unsupported_preserving: bool
    rollback_safe: bool
    automatic_activation_allowed: bool
    arbitrary_text_invocation_allowed: bool
    conventional_word_token_authority_allowed: bool
    normalization_allowed: bool
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
    tool_invocation_allowed: bool
    action_allowed: bool
    rendering_allowed: bool
    delivery_allowed: bool
    candidate_meaning_allowed: bool
    selected_meaning_allowed: bool
    selected_sense_allowed: bool
    predicate_identity_allowed: bool
    participant_role_allowed: bool
    truth_allowed: bool
    evidence_validity_allowed: bool
    clarification_allowed: bool
    permission_allowed: bool
    runtime_self_acceptance_allowed: bool
    release_authorized: bool
    production_ready: bool
    spec_id: str = SLICE37G_SPEC_ID
    spec_version: str = SLICE37G_SPEC_VERSION
    schema_version: str = SLICE37G_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37g_bootstrap_state", self.canonical_body())


@dataclass(frozen=True, slots=True)
class DisabledStructuralConceptFixture:
    fixture_id: str
    fixture_name: str
    exact_source_text: str
    source_id: str
    channel_id: str
    sequence_number: int
    expected_proposal_status: str
    expected_lexical_occurrence_count: int
    expected_concept_candidate_count: int
    expected_sense_candidate_count: int
    expected_unknown_count: int
    expected_unsupported_count: int
    accepted_fixture: bool
    synthetic: bool
    explicit_invocation_only: bool
    offline_only: bool
    in_memory_only: bool
    raw_text_not_carried_by_invocation: bool
    schema_version: str = SLICE37G_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("fixture_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37g_fixture", self.canonical_body())


@dataclass(frozen=True, slots=True)
class DisabledStructuralConceptInvocation:
    invocation_id: str
    fixture_name: str
    fixture_id: str
    profile_id: str
    explicit_invocation: bool
    requested_operation: str
    raw_text_carried_by_invocation: bool
    schema_version: str = SLICE37G_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("invocation_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37g_invocation", self.canonical_body())


@dataclass(frozen=True, slots=True)
class IntegrationStageReceipt:
    receipt_id: str
    state_id: str
    invocation_id: str
    fixture_id: str
    stage_ordinal: int
    stage: IntegrationStage
    predecessor_record_ids: tuple[str, ...]
    output_record_id: str
    output_schema_version: str
    output_exact_type: str
    output_validation_passed: bool
    source_event_id: str
    source_sha256: str
    source_ancestry_preserved: bool
    candidate_only: bool
    selected_meaning_created: bool
    truth_determined: bool
    permission_inferred: bool
    memory_accessed: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE37G_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("receipt_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37g_stage_receipt", self.canonical_body())


@dataclass(frozen=True, slots=True)
class Slice37RollbackMetadata:
    rollback_id: str
    pre_slice37_commit: str
    pre_slice37_tree: str
    accepted_parent_head: str
    accepted_parent_tree: str
    expected_closeout_commit_subject: str
    exact_commit_checkout_required: bool
    exact_tree_match_required: bool
    separate_recovery_clone_required: bool
    git_object_verification_required: bool
    live_repository_mutation_authorized: bool
    runtime_rollback_execution_authorized: bool
    rollback_proof_external_to_runtime: bool
    schema_version: str = SLICE37G_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("rollback_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37_rollback_metadata", self.canonical_body())


@dataclass(frozen=True, slots=True)
class Slice37AcceptanceRecord:
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
    pre_slice37_commit: str
    pre_slice37_tree: str
    disabled_by_default: bool
    explicitly_invoked_only: bool
    offline_only: bool
    deterministic: bool
    read_only: bool
    exact_profile_bounded: bool
    source_preserving: bool
    no_public_runtime_authority: bool
    no_selected_meaning_authority: bool
    no_action_authority: bool
    no_memory_authority: bool
    no_route_authority: bool
    no_delivery_authority: bool
    runtime_self_grants_acceptance: bool
    decision_owner_acceptance_required: bool
    release_authorized: bool
    production_ready: bool
    schema_version: str = SLICE37G_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("acceptance_record_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37_acceptance_record", self.canonical_body())


@dataclass(frozen=True, slots=True)
class DisabledStructuralConceptBootstrapResult:
    result_id: str
    state_id: str
    invocation_id: str
    fixture_id: str
    status: IntegrationStatus
    reason_code: str
    bootstrap_authority_state_id: str
    bootstrap_boundary_id: str
    bootstrap_adapter_state_id: str
    proposal_profile_id: str
    registry_snapshot_id: str
    stage_receipts: tuple[IntegrationStageReceipt, ...]
    stage_receipt_count: int
    exact_stage_chain_complete: bool
    source_event_id: str
    source_sha256: str
    custody_result: InputEventCaptureResult | None
    projection_result: SourceFieldProjectionResult | None
    grammar_registry: SymbolicGrammarOperatorRegistry | None
    binding_result: ResonantOperatorCandidateBindingResult | None
    phase_trail_result: CandidateResonantPhaseTrailResult | None
    constraint_result: ScopeAttachmentReferenceConstraintResult | None
    structural_result: DeterministicStructuralDerivationResult | None
    proposal_result: StructuralConceptCandidateProposalResult | None
    profile: StructuralConceptProposalProfile
    acceptance_record: Slice37AcceptanceRecord
    rollback_metadata: Slice37RollbackMetadata
    lexical_occurrence_count: int
    concept_candidate_count: int
    sense_candidate_count: int
    explicit_unknown_count: int
    explicit_unsupported_count: int
    disabled_by_default: bool
    explicitly_invoked: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    read_only: bool
    in_memory_only: bool
    exact_profile_bounded: bool
    source_preserved: bool
    structural_ancestry_preserved: bool
    registry_snapshot_preserved: bool
    zero_one_many_preserved: bool
    candidate_meaning_created: bool
    selected_meaning_created: bool
    selected_sense_created: bool
    predicate_identity_created: bool
    participant_roles_assigned: bool
    truth_determined: bool
    evidence_validity_determined: bool
    clarification_asked: bool
    permission_inferred: bool
    memory_read_performed: bool
    memory_write_performed: bool
    api_route_created: bool
    capability_route_created: bool
    tool_invoked: bool
    action_performed: bool
    outward_rendered: bool
    delivered: bool
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
    spec_id: str = SLICE37G_SPEC_ID
    spec_version: str = SLICE37G_SPEC_VERSION
    schema_version: str = SLICE37G_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        return {
            "state_id": self.state_id,
            "invocation_id": self.invocation_id,
            "fixture_id": self.fixture_id,
            "status": self.status,
            "reason_code": self.reason_code,
            "bootstrap_authority_state_id": self.bootstrap_authority_state_id,
            "bootstrap_boundary_id": self.bootstrap_boundary_id,
            "bootstrap_adapter_state_id": self.bootstrap_adapter_state_id,
            "proposal_profile_id": self.proposal_profile_id,
            "registry_snapshot_id": self.registry_snapshot_id,
            "stage_receipt_ids": tuple(item.receipt_id for item in self.stage_receipts),
            "stage_receipt_count": self.stage_receipt_count,
            "exact_stage_chain_complete": self.exact_stage_chain_complete,
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "custody_result_id": getattr(self.custody_result, "result_id", ""),
            "projection_result_id": getattr(self.projection_result, "result_id", ""),
            "grammar_registry_id": getattr(self.grammar_registry, "registry_id", ""),
            "binding_result_id": getattr(self.binding_result, "result_id", ""),
            "phase_trail_result_id": getattr(self.phase_trail_result, "result_id", ""),
            "constraint_result_id": getattr(self.constraint_result, "result_id", ""),
            "structural_result_id": getattr(self.structural_result, "result_id", ""),
            "proposal_result_id": getattr(self.proposal_result, "result_id", ""),
            "profile_id": self.profile.profile_id,
            "acceptance_record_id": self.acceptance_record.acceptance_record_id,
            "rollback_metadata_id": self.rollback_metadata.rollback_id,
            "lexical_occurrence_count": self.lexical_occurrence_count,
            "concept_candidate_count": self.concept_candidate_count,
            "sense_candidate_count": self.sense_candidate_count,
            "explicit_unknown_count": self.explicit_unknown_count,
            "explicit_unsupported_count": self.explicit_unsupported_count,
            "disabled_by_default": self.disabled_by_default,
            "explicitly_invoked": self.explicitly_invoked,
            "offline_only": self.offline_only,
            "standard_library_only": self.standard_library_only,
            "deterministic": self.deterministic,
            "read_only": self.read_only,
            "in_memory_only": self.in_memory_only,
            "exact_profile_bounded": self.exact_profile_bounded,
            "source_preserved": self.source_preserved,
            "structural_ancestry_preserved": self.structural_ancestry_preserved,
            "registry_snapshot_preserved": self.registry_snapshot_preserved,
            "zero_one_many_preserved": self.zero_one_many_preserved,
            "candidate_meaning_created": self.candidate_meaning_created,
            "selected_meaning_created": self.selected_meaning_created,
            "selected_sense_created": self.selected_sense_created,
            "predicate_identity_created": self.predicate_identity_created,
            "participant_roles_assigned": self.participant_roles_assigned,
            "truth_determined": self.truth_determined,
            "evidence_validity_determined": self.evidence_validity_determined,
            "clarification_asked": self.clarification_asked,
            "permission_inferred": self.permission_inferred,
            "memory_read_performed": self.memory_read_performed,
            "memory_write_performed": self.memory_write_performed,
            "api_route_created": self.api_route_created,
            "capability_route_created": self.capability_route_created,
            "tool_invoked": self.tool_invoked,
            "action_performed": self.action_performed,
            "outward_rendered": self.outward_rendered,
            "delivered": self.delivered,
            "filesystem_read_performed": self.filesystem_read_performed,
            "filesystem_write_performed": self.filesystem_write_performed,
            "network_access_performed": self.network_access_performed,
            "external_resource_loaded": self.external_resource_loaded,
            "language_model_used": self.language_model_used,
            "embedding_used": self.embedding_used,
            "semantic_similarity_used": self.semantic_similarity_used,
            "technical_acceptance_granted_by_runtime": self.technical_acceptance_granted_by_runtime,
            "release_authorized": self.release_authorized,
            "production_ready": self.production_ready,
            "spec_id": self.spec_id,
            "spec_version": self.spec_version,
            "schema_version": self.schema_version,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice37g_bootstrap_result", self.canonical_body())
