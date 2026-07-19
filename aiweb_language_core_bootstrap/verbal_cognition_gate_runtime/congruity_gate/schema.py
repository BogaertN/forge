"""Immutable deterministic Slice 40D congruity-gate records.

Slice 40D evaluates only exact compatibility assertions admitted by prior
concept, sense, semantic-class, predicate, frame, role, speech-act,
effect-boundary, domain-marker, and capability-reference authority. It does
not invent compatibility, repair a candidate, compose all gates, create a
candidate disposition, select meaning, or authorize downstream consequence.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from ..governed_lifecycle.schema import GateGovernanceBundle

SLICE40D_ACCEPTED_PARENT_HEAD = "e803ad8870c542298e878a04b6b6d39b94e25dbe"
SLICE40D_ACCEPTED_PARENT_TREE = "df6cf2f9e862c466abebfb0bd23a1d6d59748e48"
SLICE40D_ACCEPTED_PARENT_SUBJECT = "Slice 40C deterministic expectancy gate runtime"
SLICE40D_SCHEMA_VERSION = "aiweb-slice40d-congruity-gate-runtime-v1"
SLICE40D_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"

class CongruityAssertionKind(str, Enum):
    CONCEPT_SENSE = "concept_sense"
    SEMANTIC_CLASS = "semantic_class"
    PREDICATE_IDENTITY = "predicate_identity"
    ACTION_ROOT_FRAME = "action_root_frame"
    PREDICATE_FRAME = "predicate_frame"
    PARTICIPANT_ROLE = "participant_role"
    PROHIBITED_ROLE_COMBINATION = "prohibited_role_combination"
    SPEECH_ACT_FORCE = "speech_act_force"
    EFFECT_BOUNDARY = "effect_boundary"
    DOMAIN_MARKER = "domain_marker"
    CAPABILITY_REFERENCE = "capability_reference"
    NEGATION_SCOPE = "negation_scope"
    QUOTATION_REPORT_ATTRIBUTION = "quotation_report_attribution"
    CORRECTION_ANCESTRY = "correction_ancestry"

class CongruityAuthorityState(str, Enum):
    ADMITTED = "admitted"
    ABSENT = "absent"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    AMBIGUOUS = "ambiguous"

class CongruityCompatibilityJudgment(str, Enum):
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    NOT_EVALUATED = "not_evaluated"

class CongruityFindingKind(str, Enum):
    COMPATIBLE_ASSERTION = "compatible_assertion"
    INCOMPATIBLE_ASSERTION = "incompatible_assertion"
    AMBIGUOUS_ASSERTION = "ambiguous_assertion"
    UNSUPPORTED_ASSERTION = "unsupported_assertion"
    CONFLICTED_ASSERTION = "conflicted_assertion"
    INDETERMINATE_AUTHORITY_ABSENT = "indeterminate_authority_absent"
    ALL_ASSERTIONS_COMPATIBLE = "all_assertions_compatible"

class CongruityOverallState(str, Enum):
    COMPATIBLE = "congruity_compatible"
    INCOMPATIBLE = "congruity_incompatible"
    AMBIGUOUS = "congruity_ambiguous"
    UNSUPPORTED = "congruity_unsupported"
    CONFLICTED = "congruity_conflicted"
    INDETERMINATE = "congruity_indeterminate"

class CongruityValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    DUPLICATE_ID = "duplicate_id"
    REFERENCE_NOT_FOUND = "reference_not_found"
    CROSS_RECORD_MISMATCH = "cross_record_mismatch"
    CONGRUITY_FAMILY_REQUIRED = "congruity_family_required"
    SEALED_GOVERNANCE_REQUIRED = "sealed_governance_required"
    GOVERNANCE_INVALID = "governance_invalid"
    AUTHORITY_STATE_INVALID = "authority_state_invalid"
    JUDGMENT_INVALID = "judgment_invalid"
    COUNT_MISMATCH = "count_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    RAW_TEXT_PROHIBITED = "raw_text_prohibited"
    NON_EXACT_COMPATIBILITY_PROHIBITED = "non_exact_compatibility_prohibited"
    REPAIR_PROHIBITED = "repair_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"

@dataclass(frozen=True, slots=True)
class CongruityValidationIssue:
    path: str
    code: CongruityValidationCode
    detail: str

@dataclass(frozen=True, slots=True)
class CongruityValidationReport:
    issues: tuple[CongruityValidationIssue, ...]
    schema_version: str = SLICE40D_SCHEMA_VERSION
    @property
    def ok(self) -> bool:
        return not self.issues

class CongruityValidationError(ValueError):
    def __init__(self, report: CongruityValidationReport) -> None:
        self.report = report
        super().__init__("; ".join(f"{i.path}:{i.code.value}:{i.detail}" for i in report.issues) or "Slice 40D congruity validation failed")

@dataclass(frozen=True, slots=True)
class CongruityGateRuntimeProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    gate_profile_ref: str
    gate_profile_version: str
    governing_authority_refs: tuple[str, ...]
    permitted_assertion_kinds: tuple[CongruityAssertionKind, ...]
    exact_admitted_assertions_only: bool
    raw_text_inspection_allowed: bool
    similarity_fallback_allowed: bool
    nearest_known_substitution_allowed: bool
    hidden_model_judgment_allowed: bool
    silent_repair_allowed: bool
    frame_rewrite_allowed: bool
    role_reassignment_allowed: bool
    capability_driven_selection_allowed: bool
    gate_composition_allowed: bool
    selected_meaning_allowed: bool
    route_tool_action_allowed: bool
    schema_version: str = SLICE40D_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class CongruityAssertion:
    assertion_id: str
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    assertion_key: str
    assertion_kind: CongruityAssertionKind
    subject_refs: tuple[str, ...]
    object_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    assertion_source_refs: tuple[str, ...]
    authority_refs: tuple[str, ...]
    required: bool
    exact_admitted_assertion: bool
    schema_version: str = SLICE40D_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class CongruityObservation:
    observation_id: str
    assertion_ref: str
    candidate_input_ref: str
    authority_state: CongruityAuthorityState
    compatibility_judgment: CongruityCompatibilityJudgment
    supporting_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE40D_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class CongruityEvaluationInput:
    evaluation_input_id: str
    governance_bundle: GateGovernanceBundle
    runtime_profile: CongruityGateRuntimeProfile
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    assertions: tuple[CongruityAssertion, ...]
    observations: tuple[CongruityObservation, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    raw_text_supplied: bool
    similarity_fallback_used: bool
    nearest_known_substitution_used: bool
    hidden_model_judgment_used: bool
    silent_repair_used: bool
    frame_rewritten: bool
    role_reassigned: bool
    capability_driven_selection_used: bool
    schema_version: str = SLICE40D_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class CongruityFinding:
    finding_id: str
    evaluation_input_ref: str
    assertion_ref: str | None
    finding_kind: CongruityFindingKind
    assertion_kind: CongruityAssertionKind | None
    authority_state: CongruityAuthorityState
    compatibility_judgment: CongruityCompatibilityJudgment
    supporting_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    schema_version: str = SLICE40D_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class CongruityGateResult:
    result_id: str
    evaluation_input_ref: str
    review_record_id: str
    gate_id: str
    gate_profile_id: str
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    overall_state: CongruityOverallState
    findings: tuple[CongruityFinding, ...]
    assertion_count: int
    compatible_count: int
    incompatible_count: int
    ambiguous_count: int
    unsupported_count: int
    conflicted_count: int
    indeterminate_count: int
    deterministic: bool
    exact_compatibility_authority_preserved: bool
    candidate_structure_mutated: bool
    frame_rewritten: bool
    role_reassigned: bool
    similarity_fallback_used: bool
    nearest_known_substitution_used: bool
    hidden_model_judgment_used: bool
    silent_repair_used: bool
    clarification_required_created: bool
    rejection_created: bool
    refusal_relevant_created: bool
    blocked_progression_created: bool
    composed_gate_outcome_created: bool
    candidate_disposition_created: bool
    selected_meaning_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    vector_used: bool
    rag_used: bool
    semantic_similarity_used: bool
    canonical_digest: str
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE40D_SCHEMA_VERSION
