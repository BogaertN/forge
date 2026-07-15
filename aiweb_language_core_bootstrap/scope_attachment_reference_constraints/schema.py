"""Immutable records for Slice 36F scope, attachment, and references.

This module is standard-library only. Records are candidate-only and carry no
concept, predicate, capability, route, tool, memory, action, delivery, release,
or selected-meaning authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum

from ..schema import stable_record_id


SCOPE_CONSTRAINT_SPEC_ID = (
    "aiweb.slice36f.scope_attachment_reference_constraints"
)
SCOPE_CONSTRAINT_SPEC_VERSION = "1.0.0"
SCOPE_CONSTRAINT_SCHEMA_VERSION = "aiweb-slice36f-v1"

SCOPE_RULE_SCHEMA_ID = "aiweb.slice36f.scope_rule.v1"
SCOPE_POLICY_SCHEMA_ID = "aiweb.slice36f.scope_policy.v1"
SCOPE_LIMITS_SCHEMA_ID = "aiweb.slice36f.scope_limits.v1"
ACTIVE_CONTEXT_ENTRY_SCHEMA_ID = "aiweb.slice36f.active_context_entry.v1"
ACTIVE_CONTEXT_REGISTRY_SCHEMA_ID = (
    "aiweb.slice36f.active_context_registry.v1"
)
GOVERNED_SPAN_SCHEMA_ID = "aiweb.slice36f.governed_span_candidate.v1"
SCOPE_OCCURRENCE_SCHEMA_ID = "aiweb.slice36f.scope_occurrence.v1"
REFERENCE_CANDIDATE_SCHEMA_ID = (
    "aiweb.slice36f.reference_context_candidate.v1"
)
REFERENCE_ANALYSIS_SCHEMA_ID = "aiweb.slice36f.reference_analysis.v1"
CONSTRAINED_TRAIL_SCHEMA_ID = "aiweb.slice36f.constrained_trail.v1"
CONSTRAINT_SET_SCHEMA_ID = "aiweb.slice36f.constraint_set.v1"
CONSTRAINT_RESULT_SCHEMA_ID = "aiweb.slice36f.constraint_result.v1"

DEFAULT_MAX_SCOPE_OCCURRENCES = 32768
DEFAULT_MAX_GOVERNED_SPANS_PER_OCCURRENCE = 256
DEFAULT_MAX_ACTIVE_CONTEXT_ENTRIES = 4096
DEFAULT_MAX_REFERENCE_CANDIDATES = 4096

ABSOLUTE_MAX_SCOPE_OCCURRENCES = 262144
ABSOLUTE_MAX_GOVERNED_SPANS_PER_OCCURRENCE = 4096
ABSOLUTE_MAX_ACTIVE_CONTEXT_ENTRIES = 65536
ABSOLUTE_MAX_REFERENCE_CANDIDATES = 65536

CANONICAL_ROADMAP_AUTHORITY_REF = (
    "AI.Web Forge Canonical Production Roadmap v1.0:Slice36F"
)
RMC_LANGUAGE_LAW_AUTHORITY_REF = (
    "RMC Language Law v1:scope-attachment-reference"
)
RMC_CONCEPT_AUTHORITY_REF = (
    "RMC Concept Lexicon and Semantic Relation Graph v1:Slice37"
)
RMC_PREDICATE_AUTHORITY_REF = (
    "RMC Predicate-Role Frame Registry v1:Slice38"
)
SLICE36D_AUTHORITY_REF = (
    "Slice36D:resonant-operator-candidate-binding"
)
SLICE36E_AUTHORITY_REF = (
    "Slice36E:candidate-resonant-phase-trail"
)


class ScopeResponsibility(str, Enum):
    NEGATION = "negation"
    PROHIBITION = "prohibition"
    CONDITION = "condition"
    HYPOTHETICAL_STATUS = "hypothetical_status"
    QUOTATION = "quotation"
    REPORTED_SPEECH = "reported_speech"
    INTERROGATION = "interrogation"
    IMPERATIVE_SURFACE_FORM = "imperative_surface_form"
    PROPOSAL = "proposal"
    COMPLETION_CLAIMS = "completion_claims"
    EXCEPTION = "exception"
    EXCLUSION = "exclusion"
    MODALITY = "modality"
    TEMPORAL_STATUS = "temporal_status"
    OPERATIONAL_STATUS = "operational_status"
    QUANTIFICATION = "quantification"
    PRIVACY = "privacy"
    DISCLOSURE_LIMITATION = "disclosure_limitation"
    EVIDENCE_STRENGTH = "evidence_strength"
    CLAIM_FORCE = "claim_force"
    REFERENCE = "reference"


class AttachmentStrategy(str, Enum):
    SELF_ONLY = "self_only"
    RIGHTWARD_PREFIXES_TO_TERMINAL_BOUNDARY = (
        "rightward_prefixes_to_terminal_boundary"
    )
    EXACT_DELIMITED_INTERIOR = "exact_delimited_interior"
    SOURCE_UNIT_WITHOUT_TERMINAL_BOUNDARY = (
        "source_unit_without_terminal_boundary"
    )
    NO_ATTACHMENT_UNTIL_AUTHORIZED_BINDING = (
        "no_attachment_until_authorized_binding"
    )


class ScopeRuleActivationStatus(str, Enum):
    ACTIVE_FOR_ACCEPTED_BINDING = "active_for_accepted_binding"
    REGISTERED_AWAITING_BINDING_AUTHORITY = (
        "registered_awaiting_binding_authority"
    )


class AttachmentStatus(str, Enum):
    SINGULAR_ATTACHMENT = "singular_attachment"
    MULTIPLE_ATTACHMENTS = "multiple_attachments"
    MALFORMED_ATTACHMENT = "malformed_attachment"
    UNSUPPORTED_ATTACHMENT = "unsupported_attachment"
    UNRESOLVED_ATTACHMENT = "unresolved_attachment"


class ReferenceAnalysisStatus(str, Enum):
    ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE = (
        "ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE"
    )
    MULTIPLE_REFERENCE_CANDIDATES = "MULTIPLE_REFERENCE_CANDIDATES"
    UNRESOLVED_REFERENCE = "UNRESOLVED_REFERENCE"
    UNSUPPORTED_REFERENCE_FORM = "UNSUPPORTED_REFERENCE_FORM"
    MISSING_CONTEXT_REFERENCE = "MISSING_CONTEXT_REFERENCE"
    PROHIBITED_CONTEXT_DEPENDENCY = "PROHIBITED_CONTEXT_DEPENDENCY"


class ScopeConstraintStatus(str, Enum):
    ZERO_SCOPE_CONSTRAINTS = "ZERO_SCOPE_CONSTRAINTS"
    ONE_SCOPE_CONSTRAINED_TRAIL = "ONE_SCOPE_CONSTRAINED_TRAIL"
    MULTIPLE_SCOPE_CONSTRAINED_TRAILS = (
        "MULTIPLE_SCOPE_CONSTRAINED_TRAILS"
    )
    CONFLICTING_SCOPE_ATTACHMENTS = "CONFLICTING_SCOPE_ATTACHMENTS"
    MALFORMED_SCOPE_ATTACHMENT = "MALFORMED_SCOPE_ATTACHMENT"
    UNSUPPORTED_SCOPE_ATTACHMENT = "UNSUPPORTED_SCOPE_ATTACHMENT"
    MISSING_CONTEXT_REFERENCE = "MISSING_CONTEXT_REFERENCE"
    PROHIBITED_CONTEXT_DEPENDENCY = "PROHIBITED_CONTEXT_DEPENDENCY"
    SCOPE_CONSTRAINT_LIMIT_EXCEEDED = "SCOPE_CONSTRAINT_LIMIT_EXCEEDED"
    SCOPE_CONSTRAINT_FAILED = "SCOPE_CONSTRAINT_FAILED"


class ContextObjectKind(str, Enum):
    FILE = "file"
    VERSION = "version"
    PATCH = "patch"
    DOCUMENT = "document"
    IDENTIFIER = "identifier"
    GENERIC_OBJECT = "generic_object"


class ContextPositionTag(str, Enum):
    PREVIOUS = "previous"
    ABOVE = "above"
    FIRST = "first"
    QUOTED = "quoted"


class ContextOperationalStatus(str, Enum):
    UNSPECIFIED = "unspecified"
    DRAFTED = "drafted"
    PROPOSED = "proposed"
    TESTED = "tested"
    VERIFIED = "verified"
    ACCEPTED = "accepted"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    ACTIVE = "active"
    INACTIVE = "inactive"


class ContextPrivacyStatus(str, Enum):
    UNSPECIFIED = "unspecified"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    PUBLIC = "public"
    DISCLOSURE_PROHIBITED = "disclosure_prohibited"


class ContextEvidenceStrength(str, Enum):
    UNSPECIFIED = "unspecified"
    PARTIAL = "partial"
    SOURCE_SUPPORTED = "source_supported"
    VERIFIED_RECORD = "verified_record"


class ContextClaimForce(str, Enum):
    UNSPECIFIED = "unspecified"
    POSSIBILITY = "possibility"
    QUESTION = "question"
    REQUEST = "request"
    PROPOSAL = "proposal"
    DRAFT = "draft"
    TEST_RESULT = "test_result"
    VERIFIED_CLAIM = "verified_claim"
    WORLD_ASSERTION = "world_assertion"


class AuthorityConversionGuard(str, Enum):
    POSSIBILITY_TO_CERTAINTY = "possibility_to_certainty"
    QUESTION_TO_COMMAND = "question_to_command"
    REQUEST_TO_PERMISSION = "request_to_permission"
    PROPOSAL_TO_IMPLEMENTATION = "proposal_to_implementation"
    DRAFTED_TO_ACCEPTED = "drafted_to_accepted"
    TESTED_TO_VERIFIED = "tested_to_verified"
    VERIFIED_CLAIM_TO_WORLD_TRUTH = (
        "verified_claim_to_world_truth"
    )
    FAILED_TO_SUCCESSFUL = "failed_to_successful"
    ROLLED_BACK_TO_ACTIVE = "rolled_back_to_active"
    QUOTED_INSTRUCTION_TO_ACTIVE_INSTRUCTION = (
        "quoted_instruction_to_active_instruction"
    )
    PRIVATE_TO_RELEASABLE = "private_to_releasable"
    PARTIAL_EVIDENCE_TO_UNIVERSAL_PROOF = (
        "partial_evidence_to_universal_proof"
    )
    RECOGNIZED_CAPABILITY_TO_AUTHORIZED_CAPABILITY = (
        "recognized_capability_to_authorized_capability"
    )


@dataclass(frozen=True, slots=True)
class ScopeConstraintPolicy:
    policy_id: str
    policy_version: str
    explicit_context_only: bool
    active_context_must_be_immutable: bool
    exact_reference_match_only: bool
    preserve_all_lawful_attachments: bool
    select_attachment_authorized: bool
    resolve_reference_authorized: bool
    concept_authority_available: bool
    predicate_authority_available: bool
    capability_authority_available: bool
    route_authority_available: bool
    tool_authority_available: bool
    memory_search_authorized: bool
    file_search_authorized: bool
    repository_history_search_authorized: bool
    web_search_authorized: bool
    embedding_authorized: bool
    language_model_authorized: bool
    similarity_authorized: bool
    nearest_object_selection_authorized: bool
    convenience_selection_authorized: bool
    capability_influence_authorized: bool
    false_authority_conversions: tuple[AuthorityConversionGuard, ...]
    source_authority_refs: tuple[str, ...]
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    policy_schema_id: str = SCOPE_POLICY_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("policy_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("scope_constraint_policy", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScopeConstraintLimits:
    limits_id: str
    max_scope_occurrences: int
    max_governed_spans_per_occurrence: int
    max_active_context_entries: int
    max_reference_candidates: int
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    limits_schema_id: str = SCOPE_LIMITS_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("limits_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("scope_constraint_limits", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScopeAttachmentRule:
    rule_id: str
    rule_key: str
    rule_version: str
    responsibility: ScopeResponsibility
    operator_keys: tuple[str, ...]
    operator_families: tuple[str, ...]
    candidate_variant_codes: tuple[str, ...]
    attachment_strategy: AttachmentStrategy
    activation_status: ScopeRuleActivationStatus
    exact_source_span_required: bool
    preserve_multiple_attachments: bool
    possible_parent_links_preserved: bool
    possible_child_links_preserved: bool
    no_semantic_selection: bool
    no_authority_conversion: bool
    source_authority_refs: tuple[str, ...]
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    rule_schema_id: str = SCOPE_RULE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("rule_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("scope_attachment_rule", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActiveContextEntry:
    entry_id: str
    context_object_id: str
    object_kind: ContextObjectKind
    exact_identifiers: tuple[str, ...]
    exact_reference_forms: tuple[str, ...]
    ordinal: int | None
    position_tags: tuple[ContextPositionTag, ...]
    operational_status: ContextOperationalStatus
    privacy_status: ContextPrivacyStatus
    evidence_strength: ContextEvidenceStrength
    claim_force: ContextClaimForce
    source_event_ids: tuple[str, ...]
    caller_supplied: bool
    immutable: bool
    concept_identity_assigned: bool
    predicate_role_assigned: bool
    capability_binding_created: bool
    release_authorized: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    entry_schema_id: str = ACTIVE_CONTEXT_ENTRY_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("entry_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("active_context_entry", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActiveContextRegistry:
    registry_id: str
    registry_version: str
    entries: tuple[ActiveContextEntry, ...]
    exact_entry_count: int
    explicit_only: bool
    immutable: bool
    closed_world_for_this_analysis: bool
    automatic_memory_search: bool
    automatic_file_search: bool
    automatic_repository_history_search: bool
    automatic_web_search: bool
    similarity_search: bool
    nearest_object_fallback: bool
    capability_influence: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    registry_schema_id: str = ACTIVE_CONTEXT_REGISTRY_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("registry_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("active_context_registry", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GovernedSpanCandidate:
    governed_span_id: str
    source_event_id: str
    projection_id: str
    source_span_ids: tuple[str, ...]
    code_point_ranges: tuple[tuple[int, int], ...]
    utf8_byte_ranges: tuple[tuple[int, int], ...]
    exact_source_fragments: tuple[str, ...]
    relationship_code: str
    attachment_rule_id: str
    attachment_rule_version: str
    exact_attachment_evidence_codes: tuple[str, ...]
    candidate_only: bool
    selected: bool
    concept_meaning_created: bool
    predicate_role_assigned: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    governed_span_schema_id: str = GOVERNED_SPAN_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("governed_span_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("governed_span_candidate", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScopeAttachmentOccurrence:
    occurrence_id: str
    constrained_trail_id: str
    phase_trail_id: str
    source_event_id: str
    projection_id: str
    candidate_binding_id: str
    candidate_operator_key: str
    candidate_operator_version: str
    responsibility: ScopeResponsibility
    exact_source_span_ids: tuple[str, ...]
    exact_code_point_ranges: tuple[tuple[int, int], ...]
    exact_utf8_byte_ranges: tuple[tuple[int, int], ...]
    exact_source_fragments: tuple[str, ...]
    possible_governed_spans: tuple[GovernedSpanCandidate, ...]
    possible_parent_binding_ids: tuple[str, ...]
    possible_child_binding_ids: tuple[str, ...]
    attachment_rule_id: str
    attachment_rule_key: str
    attachment_rule_version: str
    attachment_status: AttachmentStatus
    singular_attachment: bool
    multiple_attachment: bool
    malformed_attachment: bool
    unsupported_attachment: bool
    unresolved_attachment: bool
    selected_attachment_id: str | None
    authority_guard_codes: tuple[AuthorityConversionGuard, ...]
    original_trail_mutated: bool
    selected_meaning: bool
    permission_inferred: bool
    capability_authorized: bool
    route_created: bool
    tool_routing_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    action_performed: bool
    delivery_performed: bool
    release_authorized: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    occurrence_schema_id: str = SCOPE_OCCURRENCE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("occurrence_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("scope_attachment_occurrence", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReferenceContextCandidate:
    reference_candidate_id: str
    reference_binding_id: str
    source_event_id: str
    projection_id: str
    exact_reference_form: str
    source_span_ids: tuple[str, ...]
    context_registry_id: str
    context_entry_id: str
    context_object_id: str
    match_rule_code: str
    supporting_condition_codes: tuple[str, ...]
    conflicting_condition_codes: tuple[str, ...]
    candidate_only: bool
    selected: bool
    reference_resolved: bool
    concept_meaning_created: bool
    predicate_role_assigned: bool
    capability_binding_created: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    reference_candidate_schema_id: str = REFERENCE_CANDIDATE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("reference_candidate_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("reference_context_candidate", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReferenceAnalysis:
    analysis_id: str
    constrained_trail_id: str
    phase_trail_id: str
    reference_binding_id: str
    source_event_id: str
    projection_id: str
    exact_reference_form: str
    source_span_ids: tuple[str, ...]
    context_registry_id: str | None
    status: ReferenceAnalysisStatus
    candidates: tuple[ReferenceContextCandidate, ...]
    candidate_count: int
    missing_context: bool
    prohibited_context_dependency: bool
    unsupported_reference_form: bool
    unresolved: bool
    multiple_candidates_preserved: bool
    selected_context_entry_id: str | None
    reference_resolved: bool
    concept_meaning_created: bool
    predicate_role_assigned: bool
    capability_binding_created: bool
    memory_search_performed: bool
    file_search_performed: bool
    repository_history_search_performed: bool
    web_search_performed: bool
    embedding_performed: bool
    language_model_used: bool
    similarity_search_performed: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    reference_analysis_schema_id: str = REFERENCE_ANALYSIS_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("analysis_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("reference_analysis", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScopeConstrainedCandidateTrail:
    constrained_trail_id: str
    constraint_set_id: str
    phase_trail_id: str
    phase_trail_set_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    binding_set_id: str
    original_trail_record_id: str
    scope_occurrences: tuple[ScopeAttachmentOccurrence, ...]
    reference_analyses: tuple[ReferenceAnalysis, ...]
    authority_guard_codes: tuple[AuthorityConversionGuard, ...]
    scope_occurrence_count: int
    reference_analysis_count: int
    unresolved_attachment_count: int
    multiple_attachment_count: int
    conflicting_attachment_count: int
    original_trail_preserved: bool
    original_trail_mutated: bool
    candidate_only: bool
    selected_trail: bool
    selected_attachment: bool
    reference_resolved: bool
    selected_meaning: bool
    concept_meaning_created: bool
    predicate_role_assigned: bool
    permission_inferred: bool
    capability_authorized: bool
    route_created: bool
    tool_routing_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    action_performed: bool
    delivery_performed: bool
    release_authorized: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    constrained_trail_schema_id: str = CONSTRAINED_TRAIL_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("constrained_trail_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "scope_constrained_trail_seed",
            {
                "constraint_set_seed": self.constraint_set_id,
                "phase_trail_id": self.phase_trail_id,
            },
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScopeAttachmentReferenceConstraintSet:
    constraint_set_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    binding_set_id: str
    phase_trail_set_id: str
    policy_id: str
    limits_id: str
    active_context_registry_id: str | None
    status: ScopeConstraintStatus
    constrained_trails: tuple[ScopeConstrainedCandidateTrail, ...]
    constrained_trail_count: int
    scope_occurrence_count: int
    reference_analysis_count: int
    singular_attachment_count: int
    multiple_attachment_count: int
    unresolved_attachment_count: int
    malformed_attachment_count: int
    unsupported_attachment_count: int
    one_reference_candidate_count: int
    multiple_reference_candidate_count: int
    unresolved_reference_count: int
    missing_context_reference_count: int
    prohibited_context_dependency_count: int
    all_original_trails_preserved: bool
    all_lawful_attachments_preserved: bool
    false_authority_conversion_count: int
    selected_trail_id: str | None
    selected_attachment_id: str | None
    resolved_reference_entry_id: str | None
    selected_meaning: bool
    concept_authority_available: bool
    predicate_authority_available: bool
    permission_authority_available: bool
    capability_authority_available: bool
    route_authority_available: bool
    tool_authority_available: bool
    memory_authority_available: bool
    action_authority_available: bool
    delivery_authority_available: bool
    release_authority_available: bool
    hidden_fallback_allowed: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    constraint_set_schema_id: str = CONSTRAINT_SET_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("constraint_set_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "scope_constraint_set_seed",
            {
                "phase_trail_set_id": self.phase_trail_set_id,
                "policy_id": self.policy_id,
                "context_registry_id": self.active_context_registry_id,
            },
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScopeAttachmentReferenceConstraintResult:
    result_id: str
    status: ScopeConstraintStatus
    reason_code: str
    constraint_set_created: bool
    source_preserved_in_custody: bool
    source_event_id: str
    source_sha256: str
    projection_id: str
    binding_set_id: str
    phase_trail_set_id: str
    policy: ScopeConstraintPolicy | None
    limits: ScopeConstraintLimits | None
    active_context_registry: ActiveContextRegistry | None
    constraint_set: ScopeAttachmentReferenceConstraintSet | None
    validation_issue_codes: tuple[str, ...]
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    repository_history_search_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    web_search_performed: bool
    embedding_performed: bool
    language_model_used: bool
    similarity_search_performed: bool
    selected_trail: bool
    selected_attachment: bool
    reference_resolved: bool
    selected_meaning: bool
    concept_meaning_created: bool
    predicate_role_assigned: bool
    permission_inferred: bool
    capability_authorized: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    release_authorized: bool
    scope_constraint_spec_id: str = SCOPE_CONSTRAINT_SPEC_ID
    scope_constraint_spec_version: str = SCOPE_CONSTRAINT_SPEC_VERSION
    schema_version: str = SCOPE_CONSTRAINT_SCHEMA_VERSION
    result_schema_id: str = CONSTRAINT_RESULT_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("scope_attachment_reference_constraint_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
