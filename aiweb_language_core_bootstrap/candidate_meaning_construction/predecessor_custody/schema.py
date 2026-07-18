"""Immutable Slice 39C complete predecessor-custody records.

The records in this module bind exact accepted Slice 36, 37 and 38 ancestry
to the Slice 39A provenance shape. They construct no semantic payload and
grant no ranking, selection, gate, truth, evidence, permission, route, action,
memory, rendering or delivery authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import CandidateMeaningProvenance


SLICE39C_ACCEPTED_PARENT_HEAD = "2ecaf057dc4e25f664eceda01adaf6698209c940"
SLICE39C_ACCEPTED_PARENT_TREE = "a10320c4093db3c4fc8766859542de1153e3caa3"
SLICE39C_ACCEPTED_PARENT_SUBJECT = (
    "Slice 39B deterministic validation identity versioning lifecycle"
)
SLICE39C_SPEC_ID = "aiweb-slice39c-complete-predecessor-custody"
SLICE39C_SPEC_VERSION = "aiweb-slice39c-complete-predecessor-custody-v1"
SLICE39C_SCHEMA_VERSION = (
    "aiweb-language-core-slice39c-complete-predecessor-custody-v1"
)
SLICE39C_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"


class PredecessorCustodyStatus(str, Enum):
    BOUND = "bound"
    NO_CANDIDATE_PREDECESSOR = "no_candidate_predecessor"
    PREDECESSOR_REJECTED = "predecessor_rejected"


class PredecessorCustodyStage(str, Enum):
    INPUT_EVENT_CUSTODY = "input_event_custody"
    SOURCE_FIELD_PROJECTION = "source_field_projection"
    OPERATOR_CANDIDATE_BINDING = "operator_candidate_binding"
    CANDIDATE_PHASE_TRAILS = "candidate_phase_trails"
    SCOPE_ATTACHMENT_REFERENCE_CONSTRAINTS = (
        "scope_attachment_reference_constraints"
    )
    DETERMINISTIC_STRUCTURAL_DERIVATION = (
        "deterministic_structural_derivation"
    )
    SLICE37_CONCEPT_SENSE_CANDIDATES = "slice37_concept_sense_candidates"
    SLICE38_PREDICATE_ROLE_FRAME_CANDIDATES = (
        "slice38_predicate_role_frame_candidates"
    )


class RegistryResourceKind(str, Enum):
    CONCEPT = "concept"
    SENSE = "sense"
    ACTION_ROOT = "action_root"
    PREDICATE = "predicate"
    PARTICIPANT_ROLE = "participant_role"
    PREDICATE_FRAME = "predicate_frame"
    EFFECT_BOUNDARY = "effect_boundary"
    CAPABILITY_FAMILY = "capability_family"
    FRAME_EFFECT_REFERENCE = "frame_effect_reference"
    FRAME_CAPABILITY_REFERENCE = "frame_capability_reference"


class PredecessorCustodyValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    INVALID_ENUM = "invalid_enum"
    INVALID_TUPLE = "invalid_tuple"
    DUPLICATE_VALUE = "duplicate_value"
    IDENTITY_MISMATCH = "identity_mismatch"
    MISSING_PREDECESSOR_REFERENCE = "missing_predecessor_reference"
    PREDECESSOR_VALIDATION_FAILED = "predecessor_validation_failed"
    SOURCE_EVENT_MISMATCH = "source_event_mismatch"
    SOURCE_CHECKSUM_MISMATCH = "source_checksum_mismatch"
    SOURCE_SPAN_FABRICATED = "source_span_fabricated"
    SOURCE_SPAN_RANGE_MISMATCH = "source_span_range_mismatch"
    STRUCTURAL_ANCESTRY_MISMATCH = "structural_ancestry_mismatch"
    OPERATOR_ANCESTRY_MISMATCH = "operator_ancestry_mismatch"
    PHASE_TRAIL_ANCESTRY_MISMATCH = "phase_trail_ancestry_mismatch"
    SCOPE_ANCESTRY_MISMATCH = "scope_ancestry_mismatch"
    REGISTRY_SNAPSHOT_MISMATCH = "registry_snapshot_mismatch"
    RESOURCE_IDENTITY_FABRICATED = "resource_identity_fabricated"
    RESOURCE_VERSION_MISMATCH = "resource_version_mismatch"
    ROLE_IDENTITY_FABRICATED = "role_identity_fabricated"
    FRAME_IDENTITY_FABRICATED = "frame_identity_fabricated"
    CROSS_LINEAGE_CANDIDATE_MERGE = "cross_lineage_candidate_merge"
    GENERATED_SUBSTITUTE_ANCESTRY = "generated_substitute_ancestry"
    CONSTRUCTION_PROFILE_MISMATCH = "construction_profile_mismatch"
    RECEIPT_CHAIN_MISMATCH = "receipt_chain_mismatch"
    PROVENANCE_MISMATCH = "provenance_mismatch"
    SEMANTIC_PAYLOAD_PROHIBITED = "semantic_payload_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"
    NONDETERMINISTIC_INPUT_PROHIBITED = "nondeterministic_input_prohibited"


@dataclass(frozen=True, slots=True)
class PredecessorCustodyValidationIssue:
    path: str
    code: PredecessorCustodyValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class PredecessorCustodyValidationReport:
    issues: tuple[PredecessorCustodyValidationIssue, ...]
    schema_version: str = SLICE39C_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class PredecessorCustodyValidationError(ValueError):
    def __init__(self, report: PredecessorCustodyValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 39C predecessor custody rejected")


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructionProfileIdentity:
    profile_id: str
    profile_key: str
    profile_version: str
    required_stages: tuple[str, ...]
    exact_source_event_required: bool
    exact_source_checksum_required: bool
    exact_source_span_reconstruction_required: bool
    exact_structural_rule_ancestry_required: bool
    exact_operator_ancestry_required: bool
    exact_phase_trail_ancestry_required: bool
    exact_scope_attachment_reference_ancestry_required: bool
    exact_registry_snapshot_required: bool
    exact_resource_version_required: bool
    zero_one_many_preservation_required: bool
    cross_lineage_merge_allowed: bool
    generated_substitute_ancestry_allowed: bool
    semantic_payload_construction_allowed: bool
    candidate_ranking_allowed: bool
    candidate_selection_allowed: bool
    gate_progression_allowed: bool
    truth_evidence_permission_allowed: bool
    route_action_memory_rendering_delivery_allowed: bool
    spec_id: str = SLICE39C_SPEC_ID
    spec_version: str = SLICE39C_SPEC_VERSION
    schema_version: str = SLICE39C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SourceSpanCustodyReference:
    reference_id: str
    span_id: str
    input_event_id: str
    source_sha256: str
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    span_sha256: str
    is_root_span: bool
    observed_in_record_ids: tuple[str, ...]
    schema_version: str = SLICE39C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class StructuralRuleCustodyReference:
    reference_id: str
    trace_id: str
    structural_candidate_id: str
    derivation_rule_id: str
    derivation_rule_key: str
    derivation_rule_version: str
    source_rule_ids_and_versions: tuple[tuple[str, str], ...]
    input_record_ids: tuple[str, ...]
    output_record_ids: tuple[str, ...]
    source_span_ids: tuple[str, ...]
    schema_version: str = SLICE39C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class OperatorCustodyReference:
    reference_id: str
    candidate_binding_id: str
    operator_definition_id: str
    operator_key: str
    operator_version: str
    grammar_registry_id: str
    grammar_registry_version: str
    proposal_rule_id: str
    proposal_rule_version: str
    source_span_ids: tuple[str, ...]
    phase_trail_ids: tuple[str, ...]
    application_ids: tuple[str, ...]
    schema_version: str = SLICE39C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RegistryResourceCustodyReference:
    reference_id: str
    resource_kind: RegistryResourceKind
    resource_id: str
    resource_key: str
    resource_version: str
    registry_snapshot_id: str
    source_candidate_ids: tuple[str, ...]
    parent_resource_ids: tuple[str, ...]
    relation_reference_ids: tuple[str, ...]
    schema_version: str = SLICE39C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class PredecessorCustodyReceipt:
    receipt_id: str
    stage_ordinal: int
    stage: PredecessorCustodyStage
    predecessor_record_ids: tuple[str, ...]
    output_record_id: str
    output_schema_version: str
    source_event_id: str
    source_sha256: str
    exact_validation_passed: bool
    exact_lineage_preserved: bool
    generated_substitute_ancestry_used: bool
    semantic_payload_constructed: bool
    candidate_ranked: bool
    candidate_selected: bool
    gate_progression_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    route_created: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE39C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningPredecessorCustody:
    custody_id: str
    lineage_id: str
    provenance: CandidateMeaningProvenance
    construction_profile: CandidateMeaningConstructionProfileIdentity
    source_span_references: tuple[SourceSpanCustodyReference, ...]
    structural_rule_references: tuple[StructuralRuleCustodyReference, ...]
    operator_references: tuple[OperatorCustodyReference, ...]
    registry_resource_references: tuple[RegistryResourceCustodyReference, ...]
    stage_receipts: tuple[PredecessorCustodyReceipt, ...]
    predecessor_result_ids: tuple[str, ...]
    exact_source_event_match: bool
    exact_source_checksum_match: bool
    exact_source_spans_verified: bool
    exact_structural_ancestry_verified: bool
    exact_operator_ancestry_verified: bool
    exact_phase_trail_ancestry_verified: bool
    exact_scope_attachment_reference_ancestry_verified: bool
    exact_registry_snapshots_verified: bool
    exact_resource_versions_verified: bool
    zero_one_many_preserved: bool
    cross_lineage_candidate_merge_performed: bool
    generated_substitute_ancestry_used: bool
    semantic_payload_constructed: bool
    candidate_ranked: bool
    candidate_selected: bool
    gate_progression_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    route_created: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    canonical_digest: str
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE39C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningPredecessorBindingResult:
    result_id: str
    status: PredecessorCustodyStatus
    reason_code: str
    custody: CandidateMeaningPredecessorCustody | None
    issues: tuple[PredecessorCustodyValidationIssue, ...]
    source_event_id: str
    source_sha256: str
    slice37_result_id: str
    slice38_result_id: str
    source_span_reference_count: int
    structural_rule_reference_count: int
    operator_reference_count: int
    registry_resource_reference_count: int
    stage_receipt_count: int
    semantic_payload_constructed: bool
    candidate_ranked: bool
    candidate_selected: bool
    gate_progression_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    route_created: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    semantic_similarity_used: bool
    schema_version: str = SLICE39C_SCHEMA_VERSION
