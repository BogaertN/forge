"""Immutable deterministic Slice 40G gate-composition records.

Slice 40G composes the exact candidate-specific results from expectancy,
congruity, connectedness, and recoverable-purpose review.  Composition is by
preservation rather than collapse: one gate cannot substitute for, erase, or
launder another gate.  The output is a non-selection disposition record only.
It never creates selected meaning or downstream authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..expectancy_gate.schema import ExpectancyGateResult
from ..congruity_gate.schema import CongruityGateResult
from ..connectedness_gate.schema import ConnectednessGateResult
from ..recoverable_purpose_gate.schema import RecoverablePurposeGateResult
from ..governed_lifecycle.schema import GateGovernanceBundle


SLICE40G_ACCEPTED_PARENT_HEAD = "8dd471f4e20024a3b64e5eb9ffac39815090fb39"
SLICE40G_ACCEPTED_PARENT_TREE = "1d8b5ac529f6af78e17d69c264aabc4471481909"
SLICE40G_ACCEPTED_PARENT_SUBJECT = (
    "Slice 40F deterministic intended-purport recoverable-purpose runtime"
)
SLICE40G_SCHEMA_VERSION = (
    "aiweb-slice40g-gate-composition-non-selection-disposition-runtime-v1"
)
SLICE40G_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"


class GateCompositionDispositionKind(str, Enum):
    MATERIAL_AMBIGUITY_PRESERVED = "material_ambiguity_preserved"
    CLARIFICATION_RELEVANT = "clarification_relevant"
    UNSUPPORTED = "unsupported"
    REFUSAL_RELEVANT = "refusal_relevant"
    HELD = "held"
    BLOCKED_PROGRESSION = "blocked_progression"
    CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW = (
        "candidate_supported_for_later_selection_review"
    )


class GateCompositionAuthorityState(str, Enum):
    ADMITTED = "admitted"
    ABSENT = "absent"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    AMBIGUOUS = "ambiguous"


class GateCompositionJudgment(str, Enum):
    APPLIES = "applies"
    DOES_NOT_APPLY = "does_not_apply"
    NOT_EVALUATED = "not_evaluated"


class GateCompositionFindingKind(str, Enum):
    DISPOSITION_APPLIED = "disposition_applied"
    DISPOSITION_NOT_APPLIED = "disposition_not_applied"
    AMBIGUOUS_AUTHORITY = "ambiguous_authority"
    UNSUPPORTED_AUTHORITY = "unsupported_authority"
    CONFLICTED_AUTHORITY = "conflicted_authority"
    INDETERMINATE_AUTHORITY_ABSENT = "indeterminate_authority_absent"
    ALL_FAMILY_RESULTS_PRESERVED = "all_family_results_preserved"


class GateCompositionStatus(str, Enum):
    COMPOSED = "composition_complete"
    AMBIGUOUS_AUTHORITY = "composition_ambiguous_authority"
    UNSUPPORTED_AUTHORITY = "composition_unsupported_authority"
    CONFLICTED_AUTHORITY = "composition_conflicted_authority"
    INDETERMINATE_AUTHORITY = "composition_indeterminate_authority"


class GateCompositionValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    DUPLICATE_ID = "duplicate_id"
    REFERENCE_NOT_FOUND = "reference_not_found"
    CROSS_RECORD_MISMATCH = "cross_record_mismatch"
    SEALED_GOVERNANCE_REQUIRED = "sealed_governance_required"
    GOVERNANCE_INVALID = "governance_invalid"
    EXACT_FAMILY_RESULTS_REQUIRED = "exact_family_results_required"
    RESULT_INVALID = "result_invalid"
    AUTHORITY_STATE_INVALID = "authority_state_invalid"
    JUDGMENT_INVALID = "judgment_invalid"
    DISPOSITION_BASIS_REQUIRED = "disposition_basis_required"
    GATE_SUBSTITUTION_PROHIBITED = "gate_substitution_prohibited"
    OUTCOME_ERASURE_PROHIBITED = "outcome_erasure_prohibited"
    FLATTENING_PROHIBITED = "flattening_prohibited"
    GLOBALIZATION_PROHIBITED = "globalization_prohibited"
    BRANCH_ERASURE_PROHIBITED = "branch_erasure_prohibited"
    BOUNDARY_REWRITE_PROHIBITED = "boundary_rewrite_prohibited"
    AUTOMATIC_DISPOSITION_PROHIBITED = "automatic_disposition_prohibited"
    POSITIVE_DISPOSITION_INVALID = "positive_disposition_invalid"
    COUNT_MISMATCH = "count_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"


@dataclass(frozen=True, slots=True)
class GateCompositionValidationIssue:
    path: str
    code: GateCompositionValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class GateCompositionValidationReport:
    issues: tuple[GateCompositionValidationIssue, ...]
    schema_version: str = SLICE40G_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class GateCompositionValidationError(ValueError):
    def __init__(self, report: GateCompositionValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(detail or "Slice 40G gate-composition validation failed")


@dataclass(frozen=True, slots=True)
class GateCompositionRuntimeProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    governing_authority_refs: tuple[str, ...]
    permitted_disposition_kinds: tuple[GateCompositionDispositionKind, ...]
    exact_family_results_required: bool
    preserve_all_gate_results: bool
    candidate_specific_composition_required: bool
    gate_substitution_allowed: bool
    gate_outcome_erasure_allowed: bool
    generic_flattening_allowed: bool
    global_pass_generalization_allowed: bool
    global_failure_generalization_allowed: bool
    candidate_branch_erasure_allowed: bool
    effect_boundary_rewrite_allowed: bool
    domain_marker_erasure_allowed: bool
    no_action_boundary_conversion_allowed: bool
    automatic_ambiguity_allowed: bool
    automatic_clarification_allowed: bool
    automatic_refusal_allowed: bool
    safest_candidate_selection_allowed: bool
    selected_meaning_allowed: bool
    downstream_authority_allowed: bool
    schema_version: str = SLICE40G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateCompositionDispositionAssertion:
    assertion_id: str
    candidate_input_ref: str
    candidate_branch_ref: str
    disposition_kind: GateCompositionDispositionKind
    authority_state: GateCompositionAuthorityState
    judgment: GateCompositionJudgment
    gate_result_refs: tuple[str, ...]
    supporting_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    conflicting_refs: tuple[str, ...]
    ambiguity_refs: tuple[str, ...]
    clarification_refs: tuple[str, ...]
    unsupported_refs: tuple[str, ...]
    refusal_relevance_refs: tuple[str, ...]
    hold_refs: tuple[str, ...]
    blocked_progression_refs: tuple[str, ...]
    later_selection_review_refs: tuple[str, ...]
    later_authority_dependency_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    domain_marker_refs: tuple[str, ...]
    no_action_boundary_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    candidate_specific: bool
    schema_version: str = SLICE40G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateCompositionEvaluationInput:
    evaluation_input_id: str
    governance_bundles: tuple[GateGovernanceBundle, ...]
    runtime_profile: GateCompositionRuntimeProfile
    candidate_input_ref: str
    candidate_branch_ref: str
    candidate_version: str
    expectancy_result: ExpectancyGateResult
    congruity_result: CongruityGateResult
    connectedness_result: ConnectednessGateResult
    recoverable_purpose_result: RecoverablePurposeGateResult
    disposition_assertions: tuple[GateCompositionDispositionAssertion, ...]
    family_candidate_input_refs: tuple[str, ...]
    candidate_branch_refs: tuple[str, ...]
    material_competing_candidate_refs: tuple[str, ...]
    competing_candidate_disposition_refs: tuple[str, ...]
    user_suppliable_clarification_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    domain_marker_refs: tuple[str, ...]
    no_action_boundary_refs: tuple[str, ...]
    authority_boundary_refs: tuple[str, ...]
    later_authority_dependency_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    candidate_ancestry_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    raw_text_used_as_selected_meaning: bool
    gate_substitution_used: bool
    gate_outcome_erased: bool
    generic_flattening_used: bool
    global_pass_generalized: bool
    global_failure_generalized: bool
    candidate_branch_erased: bool
    effect_boundary_rewritten: bool
    domain_marker_erased: bool
    no_action_boundary_converted: bool
    automatic_ambiguity_used: bool
    automatic_clarification_used: bool
    automatic_refusal_used: bool
    safest_candidate_selected: bool
    candidate_structure_mutated: bool
    schema_version: str = SLICE40G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateCompositionFinding:
    finding_id: str
    evaluation_input_ref: str
    assertion_ref: str | None
    finding_kind: GateCompositionFindingKind
    disposition_kind: GateCompositionDispositionKind | None
    authority_state: GateCompositionAuthorityState
    judgment: GateCompositionJudgment
    gate_result_refs: tuple[str, ...]
    supporting_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    conflicting_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE40G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateNonSelectionDisposition:
    disposition_id: str
    evaluation_input_ref: str
    assertion_ref: str
    candidate_input_ref: str
    candidate_branch_ref: str
    disposition_kind: GateCompositionDispositionKind
    gate_result_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    later_authority_dependency_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    domain_marker_refs: tuple[str, ...]
    no_action_boundary_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    non_selection_only: bool
    schema_version: str = SLICE40G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateCompositionResult:
    result_id: str
    evaluation_input_ref: str
    candidate_input_ref: str
    candidate_branch_ref: str
    expectancy_result_id: str
    expectancy_result_digest: str
    expectancy_candidate_input_ref: str
    congruity_result_id: str
    congruity_result_digest: str
    congruity_candidate_input_ref: str
    connectedness_result_id: str
    connectedness_result_digest: str
    connectedness_candidate_input_ref: str
    recoverable_purpose_result_id: str
    recoverable_purpose_result_digest: str
    recoverable_purpose_candidate_input_ref: str
    composition_status: GateCompositionStatus
    dispositions: tuple[CandidateNonSelectionDisposition, ...]
    findings: tuple[GateCompositionFinding, ...]
    assertion_count: int
    applied_disposition_count: int
    not_applied_count: int
    ambiguous_authority_count: int
    unsupported_authority_count: int
    conflicted_authority_count: int
    indeterminate_authority_count: int
    material_ambiguity_count: int
    clarification_relevant_count: int
    unsupported_disposition_count: int
    refusal_relevant_count: int
    held_count: int
    blocked_progression_count: int
    later_selection_review_count: int
    deterministic: bool
    family_results_preserved: bool
    family_result_count: int
    candidate_branches_preserved: bool
    effect_boundaries_preserved: bool
    domain_markers_preserved: bool
    no_action_boundaries_preserved: bool
    candidate_ancestry_preserved: bool
    version_discipline_preserved: bool
    material_ambiguity_preserved: bool
    clarification_relevant_created: bool
    unsupported_disposition_created: bool
    refusal_relevant_disposition_created: bool
    held_disposition_created: bool
    blocked_progression_created: bool
    positive_selection_review_disposition_created: bool
    candidate_accepted: bool
    candidate_rejected: bool
    candidate_clarified: bool
    selected_meaning_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    capability_availability_created: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    memory_written: bool
    rendered: bool
    delivered: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    vector_used: bool
    rag_used: bool
    semantic_similarity_used: bool
    raw_text_used_as_selected_meaning: bool
    gate_substitution_used: bool
    gate_outcome_erased: bool
    generic_flattening_used: bool
    global_pass_generalized: bool
    global_failure_generalized: bool
    candidate_branch_erased: bool
    effect_boundary_rewritten: bool
    domain_marker_erased: bool
    no_action_boundary_converted: bool
    automatic_ambiguity_used: bool
    automatic_clarification_used: bool
    automatic_refusal_used: bool
    safest_candidate_selected: bool
    candidate_structure_mutated: bool
    canonical_digest: str
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE40G_SCHEMA_VERSION
