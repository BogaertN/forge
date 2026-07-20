"""Immutable Slice 41C selection-eligibility evaluation records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...candidate_meaning_construction.manifest_candidate_integration.schema import (
    CandidateMeaningManifestCompanionV1,
)
from ...meaning_structure_manifest import CandidateMeaningRecord
from ...msm_gate_custody.schema import MsmGateCustodyCompanionV1
from ...verbal_cognition_gate_runtime.gate_composition.schema import (
    CandidateNonSelectionDisposition,
    GateCompositionResult,
)
from ..schema import (
    AlternativeCandidateCustodyRecord,
    GateCustodyReferenceRecord,
    InheritedLimitationCustodyRecord,
    SelectionAuthorityRequirementRecord,
    SelectionCandidateCustodyRecord,
    SelectionEligibilityStatusRecord,
    UnresolvedStateCustodyRecord,
)
from ..governed_lifecycle.schema import SelectedMeaningGovernanceBundle
from .authority import (
    DIGEST_ALGORITHM,
    SLICE41C_GOVERNING_AUTHORITY_REFS,
    SLICE41C_PERMANENT_BOUNDARIES,
    SLICE41C_PROFILE_ID,
    SLICE41C_PROFILE_KEY,
    SLICE41C_PROFILE_VERSION,
    SLICE41C_PROHIBITED_AUTHORITY,
    SLICE41C_SCHEMA_VERSION,
)


class SelectionEligibilityOutcome(str, Enum):
    ELIGIBLE_FOR_SELECTED_MEANING_CONSTRUCTION = (
        "eligible_for_selected_meaning_construction"
    )
    HELD_PENDING_AUTHORITY = "held_pending_authority"
    MATERIALLY_UNRESOLVED = "materially_unresolved"
    CLARIFICATION_DEPENDENT = "clarification_dependent"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    INDETERMINATE = "indeterminate"
    NOT_ELIGIBLE = "not_eligible"


class SelectionEligibilityFindingKind(str, Enum):
    EXACT_CANDIDATE_CUSTODY_CONFIRMED = "exact_candidate_custody_confirmed"
    EXACT_GATE_CUSTODY_CONFIRMED = "exact_gate_custody_confirmed"
    ALL_FOUR_GATE_RESULTS_CONFIRMED = "all_four_gate_results_confirmed"
    EXACT_COMPOSITION_CONFIRMED = "exact_composition_confirmed"
    EXPLICIT_CANDIDATE_SUPPORT_CONFIRMED = "explicit_candidate_support_confirmed"
    MISSING_AUTHORITY_PRESERVED = "missing_authority_preserved"
    MATERIAL_AMBIGUITY_PRESERVED = "material_ambiguity_preserved"
    CLARIFICATION_DEPENDENCY_PRESERVED = "clarification_dependency_preserved"
    UNSUPPORTED_STATE_PRESERVED = "unsupported_state_preserved"
    CONFLICT_PRESERVED = "conflict_preserved"
    REFUSAL_RELEVANCE_PRESERVED = "refusal_relevance_preserved"
    BLOCKED_PROGRESSION_PRESERVED = "blocked_progression_preserved"
    ALTERNATIVE_CUSTODY_PRESERVED = "alternative_custody_preserved"
    EXPLICIT_NOT_ELIGIBLE_PRESERVED = "explicit_not_eligible_preserved"
    INDETERMINATE_FAIL_CLOSED = "indeterminate_fail_closed"


class SelectionEligibilityValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    PROFILE_NOT_APPROVED = "profile_not_approved"
    RECORD_INVALID = "record_invalid"
    EXACT_CANDIDATE_MISMATCH = "exact_candidate_mismatch"
    GATE_CUSTODY_MISMATCH = "gate_custody_mismatch"
    FAMILY_RESULT_MISMATCH = "family_result_mismatch"
    COMPOSITION_RESULT_MISMATCH = "composition_result_mismatch"
    DISPOSITION_MISMATCH = "disposition_mismatch"
    ALTERNATIVE_CUSTODY_MISMATCH = "alternative_custody_mismatch"
    UNRESOLVED_CUSTODY_MISMATCH = "unresolved_custody_mismatch"
    LIMITATION_CUSTODY_MISMATCH = "limitation_custody_mismatch"
    AUTHORITY_REQUIREMENT_MISMATCH = "authority_requirement_mismatch"
    DUPLICATE_ID = "duplicate_id"
    IDENTITY_MISMATCH = "identity_mismatch"
    OUTCOME_MISMATCH = "outcome_mismatch"
    PROHIBITED_STRATEGY = "prohibited_strategy"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class SelectionEligibilityValidationIssue:
    path: str
    code: SelectionEligibilityValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class SelectionEligibilityValidationReport:
    issues: tuple[SelectionEligibilityValidationIssue, ...]
    schema_version: str = SLICE41C_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class SelectionEligibilityValidationError(ValueError):
    def __init__(self, report: SelectionEligibilityValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 41C eligibility validation failed")


@dataclass(frozen=True, slots=True)
class SelectionEligibilityAuthorityProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    governing_authority_refs: tuple[str, ...]
    permitted_outcomes: tuple[SelectionEligibilityOutcome, ...]
    exact_msm_candidate_required: bool
    exact_slice40h_companion_required: bool
    all_four_gate_results_required: bool
    exact_slice40g_composition_required: bool
    approved_profile_required: bool
    candidate_specific_dispositions_required: bool
    explicit_positive_support_required: bool
    unresolved_custody_required: bool
    alternative_custody_required: bool
    inherited_limitations_required: bool
    fail_closed: bool
    candidate_ranking_allowed: bool
    confidence_scoring_allowed: bool
    probability_ranking_allowed: bool
    semantic_similarity_allowed: bool
    nearest_known_substitution_allowed: bool
    language_model_allowed: bool
    hidden_classifier_allowed: bool
    automatic_only_candidate_eligibility_allowed: bool
    automatic_first_candidate_eligibility_allowed: bool
    automatic_safest_candidate_eligibility_allowed: bool
    selected_meaning_construction_allowed: bool
    msm_v1_mutation_allowed: bool
    downstream_authority_allowed: bool
    permanent_boundaries: tuple[str, ...] = SLICE41C_PERMANENT_BOUNDARIES
    prohibited_authority: tuple[str, ...] = SLICE41C_PROHIBITED_AUTHORITY
    schema_version: str = SLICE41C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectionEligibilityEvaluationInput:
    evaluation_input_id: str
    governance_bundle: SelectedMeaningGovernanceBundle
    manifest_candidate_record: CandidateMeaningRecord
    manifest_candidate_companion: CandidateMeaningManifestCompanionV1
    msm_gate_custody_companion: MsmGateCustodyCompanionV1
    gate_composition_result: GateCompositionResult
    authority_profile: SelectionEligibilityAuthorityProfile
    candidate_dispositions: tuple[CandidateNonSelectionDisposition, ...]
    explicit_positive_support_refs: tuple[str, ...]
    explicit_not_eligible_refs: tuple[str, ...]
    authority_profile_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    candidate_ranking_used: bool
    confidence_scoring_used: bool
    probability_ranking_used: bool
    semantic_similarity_used: bool
    nearest_known_substitution_used: bool
    language_model_used: bool
    hidden_classifier_used: bool
    only_candidate_automatic_eligibility_used: bool
    first_candidate_automatic_eligibility_used: bool
    safest_candidate_automatic_eligibility_used: bool
    refusal_relevance_erased: bool
    blocked_progression_erased: bool
    unresolved_alternatives_erased: bool
    understood_meaning_converted_to_permission: bool
    schema_version: str = SLICE41C_SCHEMA_VERSION

    @property
    def runtime_schema_record(self):
        return self.governance_bundle.runtime_schema_record

    @property
    def selection_candidate_custody(self) -> SelectionCandidateCustodyRecord:
        return self.runtime_schema_record.selection_candidate_custody

    @property
    def gate_custody_reference(self) -> GateCustodyReferenceRecord:
        return self.runtime_schema_record.gate_custody_reference

    @property
    def selection_authority_requirements(
        self,
    ) -> tuple[SelectionAuthorityRequirementRecord, ...]:
        return self.runtime_schema_record.selection_authority_requirements

    @property
    def alternative_candidate_custody(self) -> AlternativeCandidateCustodyRecord:
        return self.runtime_schema_record.alternative_candidate_custody

    @property
    def unresolved_state_custody(self) -> UnresolvedStateCustodyRecord:
        return self.runtime_schema_record.unresolved_state_custody

    @property
    def inherited_limitation_custody(self) -> InheritedLimitationCustodyRecord:
        return self.runtime_schema_record.inherited_limitation_custody

    @property
    def prior_eligibility_status(self) -> SelectionEligibilityStatusRecord:
        return self.runtime_schema_record.selection_eligibility_status


@dataclass(frozen=True, slots=True)
class SelectionEligibilityFinding:
    finding_id: str
    evaluation_input_ref: str
    candidate_meaning_ref: str
    finding_kind: SelectionEligibilityFindingKind
    basis_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE41C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectionEligibilityResult:
    result_id: str
    evaluation_input_ref: str
    selection_candidate_custody_ref: str
    candidate_meaning_ref: str
    candidate_lineage_ref: str
    manifest_candidate_record_ref: str
    manifest_candidate_companion_ref: str
    msm_gate_custody_companion_ref: str
    gate_composition_result_ref: str
    authority_profile_ref: str
    outcome: SelectionEligibilityOutcome
    findings: tuple[SelectionEligibilityFinding, ...]
    preserved_disposition_refs: tuple[str, ...]
    explicit_positive_support_refs: tuple[str, ...]
    explicit_not_eligible_refs: tuple[str, ...]
    material_ambiguity_refs: tuple[str, ...]
    clarification_dependency_refs: tuple[str, ...]
    unsupported_refs: tuple[str, ...]
    conflicted_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    held_refs: tuple[str, ...]
    refusal_relevant_refs: tuple[str, ...]
    blocked_progression_refs: tuple[str, ...]
    preserved_alternative_candidate_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    deterministic: bool
    candidate_specific: bool
    exact_msm_candidate_verified: bool
    exact_slice40h_companion_verified: bool
    all_four_gate_results_verified: bool
    exact_slice40g_composition_verified: bool
    approved_authority_profile_verified: bool
    explicit_candidate_support_verified: bool
    alternatives_preserved: bool
    unresolved_states_preserved: bool
    refusal_relevance_preserved: bool
    blocked_progression_preserved: bool
    inherited_limitations_preserved: bool
    eligibility_evaluated: bool
    eligible_for_selected_meaning_construction: bool
    candidate_ranked: bool
    selection_performed: bool
    selected_meaning_created: bool
    msm_v1_modified: bool
    bootstrap_integration_enabled: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    memory_written: bool
    rendered: bool
    delivered: bool
    external_resource_loaded: bool
    language_model_used: bool
    hidden_classifier_used: bool
    confidence_scoring_used: bool
    probability_ranking_used: bool
    semantic_similarity_used: bool
    nearest_known_substitution_used: bool
    only_candidate_automatic_eligibility_used: bool
    first_candidate_automatic_eligibility_used: bool
    safest_candidate_automatic_eligibility_used: bool
    refusal_relevance_erased: bool
    blocked_progression_erased: bool
    unresolved_alternatives_erased: bool
    understood_meaning_converted_to_permission: bool
    canonical_digest: str
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE41C_SCHEMA_VERSION


APPROVED_STRICT_PROFILE = SelectionEligibilityAuthorityProfile(
    profile_id=SLICE41C_PROFILE_ID,
    profile_key=SLICE41C_PROFILE_KEY,
    profile_version=SLICE41C_PROFILE_VERSION,
    governing_authority_refs=SLICE41C_GOVERNING_AUTHORITY_REFS,
    permitted_outcomes=tuple(SelectionEligibilityOutcome),
    exact_msm_candidate_required=True,
    exact_slice40h_companion_required=True,
    all_four_gate_results_required=True,
    exact_slice40g_composition_required=True,
    approved_profile_required=True,
    candidate_specific_dispositions_required=True,
    explicit_positive_support_required=True,
    unresolved_custody_required=True,
    alternative_custody_required=True,
    inherited_limitations_required=True,
    fail_closed=True,
    candidate_ranking_allowed=False,
    confidence_scoring_allowed=False,
    probability_ranking_allowed=False,
    semantic_similarity_allowed=False,
    nearest_known_substitution_allowed=False,
    language_model_allowed=False,
    hidden_classifier_allowed=False,
    automatic_only_candidate_eligibility_allowed=False,
    automatic_first_candidate_eligibility_allowed=False,
    automatic_safest_candidate_eligibility_allowed=False,
    selected_meaning_construction_allowed=False,
    msm_v1_mutation_allowed=False,
    downstream_authority_allowed=False,
)

APPROVED_SELECTION_AUTHORITY_PROFILES = (APPROVED_STRICT_PROFILE,)

__all__ = (
    "APPROVED_SELECTION_AUTHORITY_PROFILES",
    "APPROVED_STRICT_PROFILE",
    "SelectionEligibilityAuthorityProfile",
    "SelectionEligibilityEvaluationInput",
    "SelectionEligibilityFinding",
    "SelectionEligibilityFindingKind",
    "SelectionEligibilityOutcome",
    "SelectionEligibilityResult",
    "SelectionEligibilityValidationCode",
    "SelectionEligibilityValidationError",
    "SelectionEligibilityValidationIssue",
    "SelectionEligibilityValidationReport",
)
