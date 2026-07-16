"""Immutable contracts for Slice 36H bounded structural bootstrap integration.

The records in this module are standard-library-only, deterministic, in-memory
contracts. Importing this module does not activate the bootstrap, read source
text, inspect files, access memory, register a route, invoke a tool, render an
answer, or create semantic authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
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
from ..symbolic_grammar_operator_registry import SymbolicGrammarOperatorRegistry


SLICE36H_SPEC_ID: Final[str] = "aiweb-slice36-bounded-structural-bootstrap"
SLICE36H_SPEC_VERSION: Final[str] = (
    "aiweb-slice36-bounded-structural-bootstrap-v1"
)
SLICE36H_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-slice36-bounded-structural-bootstrap-v1"
)

PRE_SLICE36_COMMIT: Final[str] = "6089037388680c144ff666cd3737a03e1ff34ef5"
PRE_SLICE36_TREE: Final[str] = "a32d8159367a5d9ac23c6363d7c577fc3a684046"
SLICE36G_ACCEPTED_HEAD: Final[str] = "e5d3ed5ad92e6061cb68cbf6de89a4a98296f2e4"
SLICE36G_ACCEPTED_TREE: Final[str] = "d02521016bbc8bbfcc53cb3dba37548c444261eb"
SLICE36H_COMMIT_SUBJECT: Final[str] = (
    "Slice 36H bounded bootstrap integration and Slice 36 closeout"
)

SLICE36_INCREMENT_LABELS: Final[tuple[str, ...]] = (
    "36A",
    "36B0",
    "36B",
    "36C",
    "36D",
    "36E",
    "36F",
    "36G",
    "36H",
)

SLICE36_ACCEPTED_CHAIN: Final[tuple[str, ...]] = (
    "explicit fixture or later-authorized exact caller",
    "Slice 36A exact input custody",
    "Slice 36B reversible source-field projection",
    "Slice 36C controlled symbolic grammar-operator registry",
    "Slice 36D source-bound operator candidate binding",
    "Slice 36E immutable candidate phase-trail construction",
    "Slice 36F scope attachment and reference constraints",
    "Slice 36G bounded structural derivation or explicit non-progress",
)

SLICE36_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "source event != meaning",
    "source span != tokenized cognition",
    "source field != concept",
    "source observation != grammar operator",
    "operator candidate != applied operator",
    "applied operator != selected meaning",
    "phase trail != semantic truth",
    "structure != meaning",
    "scope operator != final attachment",
    "reference candidate != resolved reference",
    "structural candidate != candidate meaning",
    "candidate meaning != selected meaning",
    "recognized imperative surface != permission",
    "recognized action-bearing structure != capability authority",
    "recognized capability term != tool route",
    "quoted instruction != active instruction",
    "operator completion != world-state completion",
    "unsupported != guessed",
    "unresolved != failed",
    "containment != deletion",
    "correction != mutation",
)

SLICE36_MATHEMATICAL_DIRECTION: Final[tuple[str, ...]] = (
    "I_t is the exact immutable input-event custody record",
    "Pi_s(I_t) = F_0 is deterministic reversible source-field projection",
    "G_r(F_0) -> {B_1, B_2, ..., B_n} creates operator-binding candidates",
    "O_k(P_i) -> P_i_prime creates an immutable successor candidate state",
    "D(P_1, P_2, ..., P_n) yields bounded structure or explicit non-progress",
)

SLICE36_ACCEPTED_SCOPE: Final[tuple[str, ...]] = (
    "exact source custody",
    "reversible source coordinates",
    "closed deterministic operator proposal rules",
    "source-bound operator candidates",
    "immutable candidate grammar-state transformations",
    "candidate phase trails",
    "scope attachment and explicit-context reference candidates",
    "bounded structural candidates",
    "explicit lawful non-progress",
    "disabled explicit offline fixture integration",
    "traceable rollback metadata",
)

SLICE36_DEFERRED_SCOPE: Final[tuple[str, ...]] = (
    "approved caller catalog installation",
    "public runtime activation",
    "concept and sense authority owned by Slice 37",
    "predicate and participant-role authority owned by Slice 38",
    "CandidateMeaning construction owned by Slice 39",
    "gate evaluation and clarification or rejection disposition owned by Slice 40",
    "truth and evidence-validity determination",
    "MSM semantic custody after later meaning authority acts",
    "MEA unresolved-manifest evolution in its separate domain",
    "memory read or write",
    "external linguistic resource loading",
    "API or capability routing",
    "tool activation",
    "action execution",
    "outward rendering",
    "delivery authorization",
    "release authorization",
    "production readiness",
)


class BootstrapInvocationKind(str, Enum):
    SYNTHETIC_FIXTURE = "synthetic_fixture"
    APPROVED_CALLER = "approved_caller"


class BootstrapIntegrationStatus(str, Enum):
    REFUSED_DISABLED = "REFUSED_DISABLED"
    HELD_INVALID_STATE = "HELD_INVALID_STATE"
    HELD_INVALID_INVOCATION = "HELD_INVALID_INVOCATION"
    HELD_FIXTURE_NOT_ACCEPTED = "HELD_FIXTURE_NOT_ACCEPTED"
    HELD_APPROVED_CALLER_CATALOG_NOT_INSTALLED = (
        "HELD_APPROVED_CALLER_CATALOG_NOT_INSTALLED"
    )
    HELD_INVALID_BOOTSTRAP_BOUNDARY = "HELD_INVALID_BOOTSTRAP_BOUNDARY"
    HELD_STAGE_PREDECESSOR = "HELD_STAGE_PREDECESSOR"
    HELD_STAGE_OUTPUT = "HELD_STAGE_OUTPUT"
    HELD_EXPECTATION_MISMATCH = "HELD_EXPECTATION_MISMATCH"
    COMPLETED_STRUCTURAL_CANDIDATES = "COMPLETED_STRUCTURAL_CANDIDATES"
    COMPLETED_LAWFUL_NON_PROGRESS = "COMPLETED_LAWFUL_NON_PROGRESS"


class BootstrapStage(str, Enum):
    INPUT_CUSTODY = "slice36a_input_custody"
    SOURCE_FIELD_PROJECTION = "slice36b_source_field_projection"
    OPERATOR_REGISTRY = "slice36c_operator_registry"
    OPERATOR_CANDIDATE_BINDING = "slice36d_operator_candidate_binding"
    PHASE_TRAIL_CONSTRUCTION = "slice36e_phase_trail_construction"
    SCOPE_REFERENCE_CONSTRAINTS = "slice36f_scope_reference_constraints"
    STRUCTURAL_DERIVATION = "slice36g_structural_derivation"


class BootstrapStageStatus(str, Enum):
    COMPLETED = "completed"
    HELD_PREDECESSOR = "held_predecessor"
    HELD_OUTPUT = "held_output"


@dataclass(frozen=True, slots=True)
class BoundedStructuralBootstrapState:
    state_id: str
    enabled: bool
    explicit_offline_developer_enable: bool
    disabled_by_default: bool
    explicit_invocation_required: bool
    accepted_fixture_only: bool
    approved_caller_path_defined: bool
    approved_caller_catalog_installed: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    read_only: bool
    in_memory_only: bool
    source_preserving: bool
    operator_trace_preserving: bool
    phase_trace_preserving: bool
    bounded_supported_profile_only: bool
    non_llm: bool
    rollback_safe: bool
    raw_text_alone_allowed: bool
    arbitrary_input_allowed: bool
    automatic_activation_allowed: bool
    hidden_fallback_parser_allowed: bool
    conventional_nlp_authority_allowed: bool
    external_linguistic_resource_loading_allowed: bool
    filesystem_search_allowed: bool
    filesystem_read_allowed: bool
    filesystem_write_allowed: bool
    repository_history_search_allowed: bool
    network_allowed: bool
    web_access_allowed: bool
    environment_lookup_allowed: bool
    memory_read_allowed: bool
    memory_write_allowed: bool
    protected_memory_retrieval_allowed: bool
    llm_allowed: bool
    embedding_allowed: bool
    vector_database_allowed: bool
    semantic_similarity_allowed: bool
    learned_parser_allowed: bool
    neural_classifier_allowed: bool
    rag_allowed: bool
    main_connection_allowed: bool
    api_route_allowed: bool
    capability_route_allowed: bool
    tool_activation_allowed: bool
    action_execution_allowed: bool
    outward_rendering_allowed: bool
    evidence_validation_allowed: bool
    delivery_authorization_allowed: bool
    candidate_meaning_allowed: bool
    selected_meaning_allowed: bool
    concept_resolution_allowed: bool
    predicate_authority_allowed: bool
    participant_role_authority_allowed: bool
    permission_inference_allowed: bool
    capability_authority_allowed: bool
    release_authorized: bool
    production_ready: bool
    spec_id: str = SLICE36H_SPEC_ID
    spec_version: str = SLICE36H_SPEC_VERSION
    schema_version: str = SLICE36H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice36_bounded_structural_bootstrap_state",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BoundedStructuralFixtureRecord:
    fixture_id: str
    fixture_name: str
    exact_source_text: str
    source_sha256: str
    source_id: str
    channel_id: str
    sequence_number: int
    correlation_id: str
    requested_context_dependencies: tuple[str, ...]
    expected_custody_status: str
    expected_projection_status: str
    expected_binding_status: str
    expected_phase_trail_status: str
    expected_constraint_status: str
    expected_structural_status: str
    expected_structural_candidate_count: int
    expected_non_progress_reasons: tuple[str, ...]
    synthetic: bool
    accepted_fixture: bool
    explicit_invocation_only: bool
    offline_only: bool
    in_memory_only: bool
    external_context_required: bool
    external_resource_allowed: bool
    memory_allowed: bool
    route_allowed: bool
    action_allowed: bool
    rendering_allowed: bool
    delivery_allowed: bool
    selected_meaning_allowed: bool
    schema_version: str = SLICE36H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("fixture_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice36_bounded_structural_fixture",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BoundedStructuralBootstrapInvocation:
    invocation_id: str
    invocation_kind: BootstrapInvocationKind
    fixture_name: str
    fixture_id: str
    approved_caller_id: str
    explicit_invocation: bool
    requested_operation: str
    raw_text_carried_by_invocation: bool
    schema_version: str = SLICE36H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("invocation_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice36_bounded_structural_bootstrap_invocation",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BootstrapStageReceipt:
    receipt_id: str
    invocation_id: str
    state_id: str
    stage_ordinal: int
    stage: BootstrapStage
    stage_status: BootstrapStageStatus
    reason_code: str
    predecessor_stage: str
    predecessor_record_id: str
    predecessor_schema_version: str
    predecessor_exact_type: str
    expected_predecessor_schema_version: str
    predecessor_identity_verified: bool
    predecessor_version_verified: bool
    supporting_record_ids: tuple[str, ...]
    output_record_id: str
    output_schema_version: str
    output_exact_type: str
    output_validation_passed: bool
    stage_completed: bool
    stage_skipped: bool
    source_event_id: str
    source_sha256: str
    source_ancestry_preserved: bool
    candidate_only: bool
    interpretation_performed: bool
    semantic_classification_performed: bool
    core_rsoc_operator_application_performed: bool
    selected_meaning_created: bool
    evidence_validation_performed: bool
    filesystem_search_performed: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    repository_history_search_performed: bool
    network_access_performed: bool
    web_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    capability_route_performed: bool
    tool_activation_performed: bool
    action_performed: bool
    outward_rendering_performed: bool
    delivery_authorized: bool
    spec_id: str = SLICE36H_SPEC_ID
    spec_version: str = SLICE36H_SPEC_VERSION
    schema_version: str = SLICE36H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("receipt_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice36_bounded_structural_stage_receipt",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Slice36RollbackMetadata:
    rollback_id: str
    pre_slice36_commit: str
    pre_slice36_tree: str
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
    schema_version: str = SLICE36H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("rollback_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice36_rollback_metadata",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Slice36AcceptanceRecord:
    acceptance_record_id: str
    decision_owner: str
    accepted_increment_labels: tuple[str, ...]
    accepted_chain: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    mathematical_direction: tuple[str, ...]
    accepted_scope: tuple[str, ...]
    deferred_scope: tuple[str, ...]
    rollback_metadata_id: str
    accepted_parent_head: str
    accepted_parent_tree: str
    pre_slice36_commit: str
    pre_slice36_tree: str
    disabled_by_default: bool
    explicitly_invoked_only: bool
    offline_only: bool
    deterministic: bool
    source_preserving: bool
    no_public_runtime_authority: bool
    no_selected_meaning_authority: bool
    no_action_authority: bool
    no_delivery_authority: bool
    runtime_self_grants_acceptance: bool
    decision_owner_acceptance_required: bool
    release_authorized: bool
    production_ready: bool
    spec_id: str = SLICE36H_SPEC_ID
    spec_version: str = SLICE36H_SPEC_VERSION
    schema_version: str = SLICE36H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("acceptance_record_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice36_acceptance_record",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BoundedStructuralBootstrapResult:
    result_id: str
    state_id: str
    invocation_id: str
    fixture_id: str
    status: BootstrapIntegrationStatus
    reason_code: str
    bootstrap_schema_version: str
    bootstrap_authority_state_id: str
    bootstrap_boundary_id: str
    component_registry_id: str
    import_policy_id: str
    bootstrap_adapter_state_id: str
    stage_receipts: tuple[BootstrapStageReceipt, ...]
    stage_receipt_count: int
    completed_stage_count: int
    exact_stage_chain_complete: bool
    no_stage_skipped: bool
    source_event_id: str
    source_sha256: str
    source_reconstruction_proven: bool
    all_predecessor_records_exact: bool
    all_predecessor_versions_exact: bool
    final_structural_candidate_count: int
    final_non_progress_reasons: tuple[str, ...]
    custody_result: InputEventCaptureResult | None
    projection_result: SourceFieldProjectionResult | None
    grammar_registry: SymbolicGrammarOperatorRegistry | None
    binding_result: ResonantOperatorCandidateBindingResult | None
    phase_trail_result: CandidateResonantPhaseTrailResult | None
    constraint_result: ScopeAttachmentReferenceConstraintResult | None
    structural_result: DeterministicStructuralDerivationResult | None
    acceptance_record: Slice36AcceptanceRecord
    rollback_metadata: Slice36RollbackMetadata
    disabled_by_default: bool
    explicitly_invoked: bool
    fixture_only: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    read_only: bool
    in_memory_only: bool
    raw_text_alone_activated: bool
    hidden_fallback_parser_used: bool
    conventional_nlp_authority_used: bool
    external_linguistic_resource_loaded: bool
    filesystem_search_performed: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    repository_history_search_performed: bool
    network_access_performed: bool
    web_access_performed: bool
    environment_lookup_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    protected_memory_retrieval_performed: bool
    llm_used: bool
    embedding_used: bool
    vector_database_used: bool
    semantic_similarity_used: bool
    learned_parser_used: bool
    neural_classifier_used: bool
    rag_used: bool
    api_route_activated: bool
    capability_route_activated: bool
    tool_activated: bool
    action_executed: bool
    outward_rendering_performed: bool
    evidence_validation_performed: bool
    candidate_meaning_created: bool
    selected_meaning_created: bool
    concept_resolved: bool
    predicate_identity_created: bool
    participant_roles_assigned: bool
    permission_inferred: bool
    capability_authorized: bool
    delivery_authorized: bool
    technical_acceptance_granted_by_runtime: bool
    release_authorized: bool
    production_ready: bool
    spec_id: str = SLICE36H_SPEC_ID
    spec_version: str = SLICE36H_SPEC_VERSION
    schema_version: str = SLICE36H_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        return {
            "state_id": self.state_id,
            "invocation_id": self.invocation_id,
            "fixture_id": self.fixture_id,
            "status": self.status,
            "reason_code": self.reason_code,
            "bootstrap_schema_version": self.bootstrap_schema_version,
            "bootstrap_authority_state_id": self.bootstrap_authority_state_id,
            "bootstrap_boundary_id": self.bootstrap_boundary_id,
            "component_registry_id": self.component_registry_id,
            "import_policy_id": self.import_policy_id,
            "bootstrap_adapter_state_id": self.bootstrap_adapter_state_id,
            "stage_receipts": self.stage_receipts,
            "stage_receipt_count": self.stage_receipt_count,
            "completed_stage_count": self.completed_stage_count,
            "exact_stage_chain_complete": self.exact_stage_chain_complete,
            "no_stage_skipped": self.no_stage_skipped,
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "source_reconstruction_proven": self.source_reconstruction_proven,
            "all_predecessor_records_exact": self.all_predecessor_records_exact,
            "all_predecessor_versions_exact": self.all_predecessor_versions_exact,
            "final_structural_candidate_count": self.final_structural_candidate_count,
            "final_non_progress_reasons": self.final_non_progress_reasons,
            "custody_result_id": getattr(self.custody_result, "result_id", ""),
            "projection_result_id": getattr(self.projection_result, "result_id", ""),
            "grammar_registry_id": getattr(self.grammar_registry, "registry_id", ""),
            "binding_result_id": getattr(self.binding_result, "result_id", ""),
            "phase_trail_result_id": getattr(self.phase_trail_result, "result_id", ""),
            "constraint_result_id": getattr(self.constraint_result, "result_id", ""),
            "structural_result_id": getattr(self.structural_result, "result_id", ""),
            "acceptance_record_id": self.acceptance_record.acceptance_record_id,
            "rollback_metadata_id": self.rollback_metadata.rollback_id,
            "disabled_by_default": self.disabled_by_default,
            "explicitly_invoked": self.explicitly_invoked,
            "fixture_only": self.fixture_only,
            "offline_only": self.offline_only,
            "standard_library_only": self.standard_library_only,
            "deterministic": self.deterministic,
            "read_only": self.read_only,
            "in_memory_only": self.in_memory_only,
            "raw_text_alone_activated": self.raw_text_alone_activated,
            "hidden_fallback_parser_used": self.hidden_fallback_parser_used,
            "conventional_nlp_authority_used": self.conventional_nlp_authority_used,
            "external_linguistic_resource_loaded": self.external_linguistic_resource_loaded,
            "filesystem_search_performed": self.filesystem_search_performed,
            "filesystem_read_performed": self.filesystem_read_performed,
            "filesystem_write_performed": self.filesystem_write_performed,
            "repository_history_search_performed": self.repository_history_search_performed,
            "network_access_performed": self.network_access_performed,
            "web_access_performed": self.web_access_performed,
            "environment_lookup_performed": self.environment_lookup_performed,
            "memory_read_performed": self.memory_read_performed,
            "memory_write_performed": self.memory_write_performed,
            "protected_memory_retrieval_performed": self.protected_memory_retrieval_performed,
            "llm_used": self.llm_used,
            "embedding_used": self.embedding_used,
            "vector_database_used": self.vector_database_used,
            "semantic_similarity_used": self.semantic_similarity_used,
            "learned_parser_used": self.learned_parser_used,
            "neural_classifier_used": self.neural_classifier_used,
            "rag_used": self.rag_used,
            "api_route_activated": self.api_route_activated,
            "capability_route_activated": self.capability_route_activated,
            "tool_activated": self.tool_activated,
            "action_executed": self.action_executed,
            "outward_rendering_performed": self.outward_rendering_performed,
            "evidence_validation_performed": self.evidence_validation_performed,
            "candidate_meaning_created": self.candidate_meaning_created,
            "selected_meaning_created": self.selected_meaning_created,
            "concept_resolved": self.concept_resolved,
            "predicate_identity_created": self.predicate_identity_created,
            "participant_roles_assigned": self.participant_roles_assigned,
            "permission_inferred": self.permission_inferred,
            "capability_authorized": self.capability_authorized,
            "delivery_authorized": self.delivery_authorized,
            "technical_acceptance_granted_by_runtime": self.technical_acceptance_granted_by_runtime,
            "release_authorized": self.release_authorized,
            "production_ready": self.production_ready,
            "spec_id": self.spec_id,
            "spec_version": self.spec_version,
            "schema_version": self.schema_version,
        }

    def expected_id(self) -> str:
        return stable_record_id(
            "slice36_bounded_structural_bootstrap_result",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def source_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
