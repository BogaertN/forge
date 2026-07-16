"""Immutable Slice 37F structural-to-concept candidate proposal records.

The records preserve exact Slice 36 source and structural ancestry while
exposing only zero, one, or multiple controlled concept and sense candidates
from the exact Slice 37D registry. They do not create CandidateMeaning, select
meaning or sense, define predicates or participant roles, determine truth or
evidence validity, ask clarification, authorize permission/capabilities/tools/
actions, access memory, render output, or deliver anything.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id


SLICE37F_SPEC_ID: Final[str] = (
    "aiweb-slice37f-structural-concept-candidate-proposal"
)
SLICE37F_SPEC_VERSION: Final[str] = (
    "aiweb-slice37f-structural-concept-candidate-proposal-v1"
)
SLICE37F_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-structural-concept-candidate-proposal-v1"
)
SLICE37F_ACCEPTED_PARENT_HEAD: Final[str] = (
    "721f0377f674311c50a0ae2adf3d03e89190e966"
)
SLICE37F_ACCEPTED_PARENT_TREE: Final[str] = (
    "249345fe2e130bee30ac2cb3fd74c8eeff6ea726"
)
SLICE37F_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 37E semantic classes and relation type rules"
)

PROPOSAL_PROFILE_SCHEMA_ID: Final[str] = "aiweb.slice37f.profile.v1"
REGISTRY_SNAPSHOT_SCHEMA_ID: Final[str] = "aiweb.slice37f.registry_snapshot.v1"
STRUCTURAL_ANCESTRY_SCHEMA_ID: Final[str] = "aiweb.slice37f.structural_ancestry.v1"
LEXICAL_OCCURRENCE_SCHEMA_ID: Final[str] = "aiweb.slice37f.lexical_occurrence.v1"
CONCEPT_PROPOSAL_SCHEMA_ID: Final[str] = "aiweb.slice37f.concept_proposal.v1"
SENSE_PROPOSAL_SCHEMA_ID: Final[str] = "aiweb.slice37f.sense_proposal.v1"
PROPOSAL_RESULT_SCHEMA_ID: Final[str] = "aiweb.slice37f.result.v1"

SLICE37F_NON_AUTHORITY_BOUNDARIES: Final[tuple[str, ...]] = (
    "structural result is not meaning",
    "exact lexical occurrence is not concept identity",
    "registry lookup is not occurrence-level interpretation",
    "concept candidate is not CandidateMeaning",
    "sense candidate is not selected sense",
    "candidate order is deterministic record order and carries no rank",
    "single candidate availability is not selection",
    "multiple candidates must remain unresolved alternatives",
    "unknown is not permission to guess or normalize",
    "unsupported is not rejected, false, failed, or silently repaired",
    "semantic class membership is not truth, evidence, or authority",
    "semantic relation type is not a relation instance or fact",
    "action-related concept is not predicate identity or permission",
    "capability-related concept is not route or tool authority",
    "memory-related concept is not memory access authority",
    "delivery-related concept is not rendering or delivery authority",
)


class ProposalResultStatus(str, Enum):
    CANDIDATES_PROPOSED = "candidates_proposed"
    CANDIDATES_WITH_UNRESOLVED_STATES = "candidates_with_unresolved_states"
    EXPLICIT_UNKNOWN = "explicit_unknown"
    EXPLICIT_UNSUPPORTED = "explicit_unsupported"
    EXPLICIT_UNKNOWN_AND_UNSUPPORTED = "explicit_unknown_and_unsupported"
    PREDECESSOR_REJECTED = "predecessor_rejected"


class LexicalOccurrenceDisposition(str, Enum):
    MAPPED = "mapped"
    AMBIGUOUS = "ambiguous"
    UNMAPPED = "unmapped"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class StructuralConceptProposalProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    explicit_invocation_required: bool
    offline_only: bool
    standard_library_only: bool
    deterministic: bool
    immutable_records: bool
    exact_source_preservation_required: bool
    exact_case_sensitive_matching: bool
    ascii_identifier_boundary_profile: bool
    normalization_allowed: bool
    casefolding_allowed: bool
    spelling_correction_allowed: bool
    stemming_allowed: bool
    synonym_expansion_allowed: bool
    nearest_match_allowed: bool
    frequency_ranking_allowed: bool
    semantic_similarity_allowed: bool
    model_inference_allowed: bool
    dictionary_fallback_allowed: bool
    language_tags: tuple[str, ...]
    namespace_id: str
    namespace_scope: tuple[str, ...]
    domain_scope: tuple[str, ...]
    structural_result_consumption_allowed: bool
    exact_term_lookup_allowed: bool
    concept_candidate_proposal_allowed: bool
    sense_candidate_proposal_allowed: bool
    preserve_zero_one_many: bool
    preserve_unresolved_alternatives: bool
    explicit_unknown_required: bool
    explicit_unsupported_required: bool
    candidate_meaning_creation_allowed: bool
    selected_meaning_allowed: bool
    selected_sense_allowed: bool
    predicate_identity_allowed: bool
    participant_role_assignment_allowed: bool
    truth_determination_allowed: bool
    evidence_validity_determination_allowed: bool
    clarification_allowed: bool
    permission_inference_allowed: bool
    capability_routing_allowed: bool
    tool_invocation_allowed: bool
    action_execution_allowed: bool
    memory_read_allowed: bool
    memory_write_allowed: bool
    outward_rendering_allowed: bool
    delivery_allowed: bool
    non_authority_boundaries: tuple[str, ...] = SLICE37F_NON_AUTHORITY_BOUNDARIES
    spec_id: str = SLICE37F_SPEC_ID
    spec_version: str = SLICE37F_SPEC_VERSION
    schema_version: str = SLICE37F_SCHEMA_VERSION
    profile_schema_id: str = PROPOSAL_PROFILE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("profile_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37f_proposal_profile", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RegistrySnapshotIdentity:
    snapshot_id: str
    concept_registry_manifest_id: str
    concept_registry_digest: str
    concept_registry_version: str
    sense_mapping_manifest_id: str
    sense_mapping_registry_digest: str
    sense_mapping_registry_version: str
    semantic_class_relation_manifest_id: str
    semantic_class_relation_registry_digest: str
    semantic_class_relation_registry_version: str
    namespace_id: str
    namespace_version: str
    concept_count: int
    sense_count: int
    lexical_reference_count: int
    mapping_count: int
    semantic_class_count: int
    relation_family_count: int
    relation_type_count: int
    relation_instance_count: int
    exact_snapshot: bool
    external_resources_loaded: bool
    runtime_mutation_allowed: bool
    spec_id: str = SLICE37F_SPEC_ID
    spec_version: str = SLICE37F_SPEC_VERSION
    schema_version: str = SLICE37F_SCHEMA_VERSION
    snapshot_schema_id: str = REGISTRY_SNAPSHOT_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("snapshot_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37f_registry_snapshot", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralCandidateAncestry:
    ancestry_id: str
    lexical_occurrence_id: str
    structural_result_id: str
    structural_set_id: str
    structural_candidate_id: str
    source_event_id: str
    source_sha256: str
    root_source_span_id: str
    projection_id: str
    constrained_trail_id: str
    phase_trail_id: str
    operator_graph_id: str
    source_coverage_proof_id: str
    participating_binding_ids: tuple[str, ...]
    operator_node_ids: tuple[str, ...]
    operator_definition_ids: tuple[str, ...]
    operator_keys_and_versions: tuple[tuple[str, str], ...]
    scope_occurrence_ids: tuple[str, ...]
    attachment_candidate_ids: tuple[str, ...]
    reference_analysis_ids: tuple[str, ...]
    reference_candidate_ids: tuple[str, ...]
    intersecting_operator_node_ids: tuple[str, ...]
    intersecting_scope_occurrence_ids: tuple[str, ...]
    intersecting_attachment_candidate_ids: tuple[str, ...]
    intersecting_reference_analysis_ids: tuple[str, ...]
    unresolved_operator_span_ids: tuple[str, ...]
    conflicting_operator_binding_ids: tuple[str, ...]
    attachment_alternative_ids: tuple[str, ...]
    reference_alternative_ids: tuple[str, ...]
    non_progress_reasons: tuple[str, ...]
    exact_ancestry_complete: bool
    source_reconstruction_proven: bool
    candidate_only: bool
    selected_structure: bool
    spec_id: str = SLICE37F_SPEC_ID
    spec_version: str = SLICE37F_SPEC_VERSION
    schema_version: str = SLICE37F_SCHEMA_VERSION
    ancestry_schema_id: str = STRUCTURAL_ANCESTRY_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("ancestry_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37f_structural_ancestry", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExactLexicalOccurrenceProposal:
    occurrence_id: str
    structural_result_id: str
    structural_set_id: str
    source_event_id: str
    source_sha256: str
    input_event_id: str
    root_source_span_id: str
    projection_id: str
    exact_source_text: str
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    source_span_ids: tuple[str, ...]
    lexical_reference_id: str
    lexical_reference_version: str
    lexical_reference_lifecycle_state: str
    lexical_reference_provenance_ref: str
    lexical_reference_kind: str
    lexical_language_tag: str
    lookup_request_id: str
    lookup_result_id: str
    lookup_state: str
    lookup_multiplicity: str
    mapping_ids_and_versions: tuple[tuple[str, str], ...]
    concept_candidate_proposal_ids: tuple[str, ...]
    sense_candidate_proposal_ids: tuple[str, ...]
    structural_ancestry_ids: tuple[str, ...]
    disposition: LexicalOccurrenceDisposition
    unresolved_alternative_ids: tuple[str, ...]
    exact_match: bool
    candidate_order_is_ranked: bool
    selected_concept_id: str | None
    selected_sense_id: str | None
    explicit_unknown: bool
    explicit_unsupported: bool
    reason: str
    non_authority_boundaries: tuple[str, ...]
    spec_id: str = SLICE37F_SPEC_ID
    spec_version: str = SLICE37F_SPEC_VERSION
    schema_version: str = SLICE37F_SCHEMA_VERSION
    occurrence_schema_id: str = LEXICAL_OCCURRENCE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("occurrence_id")
        return body

    def identity_body(self) -> dict[str, object]:
        return {
            "structural_result_id": self.structural_result_id,
            "structural_set_id": self.structural_set_id,
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "input_event_id": self.input_event_id,
            "root_source_span_id": self.root_source_span_id,
            "projection_id": self.projection_id,
            "exact_source_text": self.exact_source_text,
            "code_point_start": self.code_point_start,
            "code_point_end": self.code_point_end,
            "utf8_byte_start": self.utf8_byte_start,
            "utf8_byte_end": self.utf8_byte_end,
            "source_span_ids": self.source_span_ids,
            "lexical_reference_id": self.lexical_reference_id,
            "lexical_reference_version": self.lexical_reference_version,
            "lookup_request_id": self.lookup_request_id,
            "lookup_result_id": self.lookup_result_id,
            "spec_id": self.spec_id,
            "spec_version": self.spec_version,
            "schema_version": self.schema_version,
            "occurrence_schema_id": self.occurrence_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice37f_lexical_occurrence", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptCandidateProposal:
    proposal_id: str
    lexical_occurrence_id: str
    structural_result_id: str
    structural_ancestry_ids: tuple[str, ...]
    profile_id: str
    registry_snapshot_id: str
    exact_matched_lexical_reference_id: str
    exact_matched_lexical_reference_version: str
    mapping_ids_and_versions: tuple[tuple[str, str], ...]
    concept_id: str
    concept_key: str
    concept_version: str
    concept_lifecycle_state: str
    concept_provenance_ref: str
    related_sense_candidate_ids: tuple[str, ...]
    unresolved_alternative_concept_ids: tuple[str, ...]
    candidate_only: bool
    selected: bool
    candidate_meaning_created: bool
    truth_determined: bool
    evidence_validity_determined: bool
    permission_inferred: bool
    capability_route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    outward_rendered: bool
    delivered: bool
    non_authority_boundaries: tuple[str, ...]
    spec_id: str = SLICE37F_SPEC_ID
    spec_version: str = SLICE37F_SPEC_VERSION
    schema_version: str = SLICE37F_SCHEMA_VERSION
    proposal_schema_id: str = CONCEPT_PROPOSAL_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("proposal_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37f_concept_candidate", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SenseCandidateProposal:
    proposal_id: str
    lexical_occurrence_id: str
    structural_result_id: str
    structural_ancestry_ids: tuple[str, ...]
    profile_id: str
    registry_snapshot_id: str
    exact_matched_lexical_reference_id: str
    exact_matched_lexical_reference_version: str
    mapping_ids_and_versions: tuple[tuple[str, str], ...]
    concept_id: str
    sense_id: str
    sense_key: str
    sense_version: str
    sense_lifecycle_state: str
    sense_provenance_ref: str
    unresolved_alternative_sense_ids: tuple[str, ...]
    candidate_only: bool
    selected: bool
    selected_sense_created: bool
    candidate_meaning_created: bool
    predicate_identity_created: bool
    participant_roles_assigned: bool
    truth_determined: bool
    evidence_validity_determined: bool
    clarification_asked: bool
    permission_inferred: bool
    capability_route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    outward_rendered: bool
    delivered: bool
    non_authority_boundaries: tuple[str, ...]
    spec_id: str = SLICE37F_SPEC_ID
    spec_version: str = SLICE37F_SPEC_VERSION
    schema_version: str = SLICE37F_SCHEMA_VERSION
    proposal_schema_id: str = SENSE_PROPOSAL_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("proposal_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37f_sense_candidate", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralConceptCandidateProposalResult:
    result_id: str
    status: ProposalResultStatus
    reason_code: str
    structural_result_id: str
    structural_set_id: str
    source_event_id: str
    source_sha256: str
    input_event_id: str
    root_source_span_id: str
    projection_id: str
    profile: StructuralConceptProposalProfile
    registry_snapshot: RegistrySnapshotIdentity
    lexical_occurrences: tuple[ExactLexicalOccurrenceProposal, ...]
    structural_ancestries: tuple[StructuralCandidateAncestry, ...]
    concept_candidates: tuple[ConceptCandidateProposal, ...]
    sense_candidates: tuple[SenseCandidateProposal, ...]
    structural_non_progress_reasons: tuple[str, ...]
    unmatched_exact_source_fragments: tuple[str, ...]
    unmatched_source_span_ids: tuple[str, ...]
    unmatched_code_point_ranges: tuple[tuple[int, int], ...]
    lexical_occurrence_count: int
    structural_ancestry_count: int
    concept_candidate_count: int
    sense_candidate_count: int
    explicit_unknown_count: int
    explicit_unsupported_count: int
    unresolved_alternative_count: int
    zero_one_many_preserved: bool
    structural_plurality_preserved: bool
    source_ancestry_preserved: bool
    operator_ancestry_preserved: bool
    scope_attachment_ancestry_preserved: bool
    exact_registry_lookup_only: bool
    candidate_order_is_ranked: bool
    candidate_meaning_created: bool
    selected_meaning_created: bool
    selected_sense_created: bool
    predicate_identity_created: bool
    participant_roles_assigned: bool
    truth_determined: bool
    evidence_validity_determined: bool
    clarification_asked: bool
    permission_inferred: bool
    capability_route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    outward_rendered: bool
    delivered: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    semantic_similarity_used: bool
    non_authority_boundaries: tuple[str, ...] = SLICE37F_NON_AUTHORITY_BOUNDARIES
    spec_id: str = SLICE37F_SPEC_ID
    spec_version: str = SLICE37F_SPEC_VERSION
    schema_version: str = SLICE37F_SCHEMA_VERSION
    result_schema_id: str = PROPOSAL_RESULT_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("slice37f_proposal_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
