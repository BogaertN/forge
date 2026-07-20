"""Immutable Slice 41D selected-meaning construction records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...candidate_meaning_construction.manifest_candidate_integration.schema import (
    CandidateMeaningManifestCompanionV1,
)
from ...meaning_structure_manifest import (
    CandidateMeaningRecord,
    SelectedGovernedMeaningRecord,
)
from ..eligibility_evaluation.schema import (
    SelectionEligibilityEvaluationInput,
    SelectionEligibilityResult,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE41D_GOVERNING_AUTHORITY_REFS,
    SLICE41D_PERMANENT_BOUNDARIES,
    SLICE41D_PROFILE_ID,
    SLICE41D_PROFILE_KEY,
    SLICE41D_PROFILE_VERSION,
    SLICE41D_PROHIBITED_AUTHORITY,
    SLICE41D_SCHEMA_VERSION,
)


class PreservedAlternativeKind(str, Enum):
    NON_SELECTED = "non_selected"
    UNRESOLVED = "unresolved"
    MATERIAL_AMBIGUITY = "material_ambiguity"
    CLARIFICATION_DEPENDENT = "clarification_dependent"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    HELD = "held"
    REFUSAL_RELEVANT = "refusal_relevant"
    BLOCKED_PROGRESSION = "blocked_progression"
    EXACT_DUPLICATE = "exact_duplicate"
    OTHER_PRESERVED = "other_preserved"


class SelectedMeaningConstructionValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    PROFILE_NOT_APPROVED = "profile_not_approved"
    ELIGIBILITY_NOT_SUCCESSFUL = "eligibility_not_successful"
    ELIGIBILITY_MISMATCH = "eligibility_mismatch"
    CANDIDATE_MISMATCH = "candidate_mismatch"
    LINEAGE_MISMATCH = "lineage_mismatch"
    SEMANTIC_CONTENT_MISMATCH = "semantic_content_mismatch"
    SEMANTIC_ENRICHMENT = "semantic_enrichment"
    SEMANTIC_DELETION = "semantic_deletion"
    LIMITATION_CUSTODY_MISMATCH = "limitation_custody_mismatch"
    ALTERNATIVE_CUSTODY_MISMATCH = "alternative_custody_mismatch"
    ALTERNATIVE_ERASED = "alternative_erased"
    UNRESOLVED_CUSTODY_MISMATCH = "unresolved_custody_mismatch"
    AMBIGUITY_ANCESTRY_MISMATCH = "ambiguity_ancestry_mismatch"
    CLARIFICATION_ANCESTRY_MISMATCH = "clarification_ancestry_mismatch"
    TRACE_MISMATCH = "trace_mismatch"
    RECEIPT_MISMATCH = "receipt_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    DUPLICATE_ID = "duplicate_id"
    PROHIBITED_STRATEGY = "prohibited_strategy"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class SelectedMeaningConstructionValidationIssue:
    path: str
    code: SelectedMeaningConstructionValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class SelectedMeaningConstructionValidationReport:
    issues: tuple[SelectedMeaningConstructionValidationIssue, ...]
    schema_version: str = SLICE41D_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class SelectedMeaningConstructionValidationError(ValueError):
    def __init__(self, report: SelectedMeaningConstructionValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 41D selected-meaning validation failed")


@dataclass(frozen=True, slots=True)
class SelectedMeaningConstructionAuthorityProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    governing_authority_refs: tuple[str, ...]
    exact_successful_eligibility_required: bool
    exact_selected_candidate_required: bool
    exact_candidate_lineage_required: bool
    exact_semantic_copy_required: bool
    exact_candidate_companion_required: bool
    inherited_limitations_required: bool
    blocked_consequence_markers_required: bool
    authority_sensitive_distinctions_required: bool
    every_non_selected_candidate_required: bool
    unresolved_alternatives_separate_required: bool
    ambiguity_ancestry_required: bool
    clarification_ancestry_required: bool
    deterministic_trace_required: bool
    deterministic_receipt_required: bool
    fail_closed: bool
    candidate_ranking_allowed: bool
    confidence_scoring_allowed: bool
    probability_ranking_allowed: bool
    semantic_similarity_allowed: bool
    nearest_known_substitution_allowed: bool
    language_model_allowed: bool
    hidden_classifier_allowed: bool
    automatic_only_candidate_selection_allowed: bool
    automatic_first_candidate_selection_allowed: bool
    automatic_safest_candidate_selection_allowed: bool
    msm_v1_mutation_allowed: bool
    outward_meaning_allowed: bool
    truth_evidence_permission_execution_allowed: bool
    route_tool_action_memory_rendering_delivery_allowed: bool
    permanent_boundaries: tuple[str, ...] = SLICE41D_PERMANENT_BOUNDARIES
    prohibited_authority: tuple[str, ...] = SLICE41D_PROHIBITED_AUTHORITY
    schema_version: str = SLICE41D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningConstructionInput:
    construction_input_id: str
    eligibility_evaluation_input: SelectionEligibilityEvaluationInput
    eligibility_result: SelectionEligibilityResult
    authority_profile: SelectedMeaningConstructionAuthorityProfile
    selection_reason_refs: tuple[str, ...]
    ambiguity_ancestry_refs: tuple[str, ...]
    clarification_ancestry_refs: tuple[str, ...]
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
    only_candidate_automatic_selection_used: bool
    first_candidate_automatic_selection_used: bool
    safest_candidate_automatic_selection_used: bool
    alternative_erasure_requested: bool
    unresolved_alternative_erasure_requested: bool
    ambiguity_ancestry_erasure_requested: bool
    clarification_ancestry_erasure_requested: bool
    refusal_relevance_erasure_requested: bool
    blocked_progression_erasure_requested: bool
    msm_v1_mutation_requested: bool
    outward_meaning_requested: bool
    downstream_authority_requested: bool
    schema_version: str = SLICE41D_SCHEMA_VERSION

    @property
    def selected_candidate_record(self) -> CandidateMeaningRecord:
        return self.eligibility_evaluation_input.manifest_candidate_record

    @property
    def selected_candidate_companion(self) -> CandidateMeaningManifestCompanionV1:
        return self.eligibility_evaluation_input.manifest_candidate_companion


@dataclass(frozen=True, slots=True)
class SelectedMeaningDecisionRecord:
    decision_id: str
    construction_input_ref: str
    eligibility_result_ref: str
    selected_candidate_ref: str
    selected_candidate_lineage_ref: str
    selected_manifest_candidate_record_ref: str
    selected_manifest_candidate_companion_ref: str
    selection_authority_profile_ref: str
    selection_reason_refs: tuple[str, ...]
    non_selected_candidate_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    ambiguity_ancestry_refs: tuple[str, ...]
    clarification_ancestry_refs: tuple[str, ...]
    decision_performed: bool
    candidate_ranked: bool
    only_candidate_claimed: bool
    historical_candidate_exhaustiveness_claimed: bool
    schema_version: str = SLICE41D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class PreservedAlternativeCandidateRecord:
    preservation_id: str
    construction_input_ref: str
    selected_candidate_ref: str
    alternative_candidate_ref: str
    preservation_kinds: tuple[PreservedAlternativeKind, ...]
    alternative_relationship_refs: tuple[str, ...]
    disposition_refs: tuple[str, ...]
    unresolved_reason_refs: tuple[str, ...]
    ambiguity_ancestry_refs: tuple[str, ...]
    clarification_ancestry_refs: tuple[str, ...]
    shared_ancestry_refs: tuple[str, ...]
    exact_duplicate_group_refs: tuple[str, ...]
    preserved_by_exact_reference: bool
    selected: bool
    deleted: bool
    ranked: bool
    confidence_scored: bool
    schema_version: str = SLICE41D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningContentProof:
    proof_id: str
    construction_input_ref: str
    selected_candidate_ref: str
    selected_meaning_ref: str
    candidate_semantic_digest: str
    selected_semantic_digest: str
    communicative_act_exact: bool
    concept_refs_exact: bool
    relation_refs_exact: bool
    meaning_modifiers_exact: bool
    preservation_classes_exact: bool
    candidate_identity_exact: bool
    candidate_lineage_exact: bool
    added_concept_refs: tuple[str, ...]
    removed_concept_refs: tuple[str, ...]
    added_relation_refs: tuple[str, ...]
    removed_relation_refs: tuple[str, ...]
    added_meaning_modifiers: tuple[str, ...]
    removed_meaning_modifiers: tuple[str, ...]
    added_preservation_classes: tuple[str, ...]
    removed_preservation_classes: tuple[str, ...]
    semantic_content_exact: bool
    semantic_enrichment_detected: bool
    semantic_deletion_detected: bool
    schema_version: str = SLICE41D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningSelectionTraceRecord:
    trace_id: str
    construction_input_ref: str
    decision_ref: str
    eligibility_result_ref: str
    selected_candidate_ref: str
    selected_meaning_ref: str
    gate_custody_ref: str
    gate_composition_result_ref: str
    authority_profile_ref: str
    content_proof_ref: str
    preserved_alternative_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    blocked_consequence_refs: tuple[str, ...]
    refusal_relevant_refs: tuple[str, ...]
    ambiguity_ancestry_refs: tuple[str, ...]
    clarification_ancestry_refs: tuple[str, ...]
    predecessor_trace_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    deterministic: bool
    candidate_ranked: bool
    alternatives_erased: bool
    schema_version: str = SLICE41D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningSelectionReceiptRecord:
    receipt_id: str
    construction_input_ref: str
    decision_ref: str
    selected_meaning_ref: str
    content_proof_ref: str
    trace_ref: str
    eligibility_result_ref: str
    selected_candidate_ref: str
    preserved_alternative_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    required_law_refs: tuple[str, ...]
    prohibited_consequence_refs: tuple[str, ...]
    deterministic: bool
    selected_meaning_constructed: bool
    msm_v1_modified: bool
    outward_meaning_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE41D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningConstructionPackage:
    package_id: str
    package_digest: str
    construction_input_ref: str
    authority_profile_ref: str
    eligibility_result_ref: str
    selected_candidate_record: CandidateMeaningRecord
    selected_candidate_companion: CandidateMeaningManifestCompanionV1
    decision_record: SelectedMeaningDecisionRecord
    selected_meaning_record: SelectedGovernedMeaningRecord
    content_proof: SelectedMeaningContentProof
    preserved_alternatives: tuple[PreservedAlternativeCandidateRecord, ...]
    unresolved_alternative_refs: tuple[str, ...]
    ambiguity_ancestry_refs: tuple[str, ...]
    clarification_ancestry_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    blocked_consequence_refs: tuple[str, ...]
    refusal_relevant_refs: tuple[str, ...]
    authority_sensitive_distinction_refs: tuple[str, ...]
    selection_trace: SelectedMeaningSelectionTraceRecord
    selection_receipt: SelectedMeaningSelectionReceiptRecord
    deterministic: bool
    exact_candidate_identity_preserved: bool
    exact_candidate_lineage_preserved: bool
    exact_semantic_content_preserved: bool
    every_non_selected_candidate_preserved: bool
    unresolved_alternatives_preserved_separately: bool
    ambiguity_ancestry_preserved: bool
    clarification_ancestry_preserved: bool
    inherited_limitations_preserved: bool
    blocked_consequences_preserved: bool
    refusal_relevance_preserved: bool
    selected_meaning_created: bool
    candidate_ranked: bool
    alternatives_erased: bool
    msm_v1_modified: bool
    governed_outward_meaning_created: bool
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
    bootstrap_integration_enabled: bool
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE41D_SCHEMA_VERSION


APPROVED_STRICT_PROFILE = SelectedMeaningConstructionAuthorityProfile(
    profile_id=SLICE41D_PROFILE_ID,
    profile_key=SLICE41D_PROFILE_KEY,
    profile_version=SLICE41D_PROFILE_VERSION,
    governing_authority_refs=SLICE41D_GOVERNING_AUTHORITY_REFS,
    exact_successful_eligibility_required=True,
    exact_selected_candidate_required=True,
    exact_candidate_lineage_required=True,
    exact_semantic_copy_required=True,
    exact_candidate_companion_required=True,
    inherited_limitations_required=True,
    blocked_consequence_markers_required=True,
    authority_sensitive_distinctions_required=True,
    every_non_selected_candidate_required=True,
    unresolved_alternatives_separate_required=True,
    ambiguity_ancestry_required=True,
    clarification_ancestry_required=True,
    deterministic_trace_required=True,
    deterministic_receipt_required=True,
    fail_closed=True,
    candidate_ranking_allowed=False,
    confidence_scoring_allowed=False,
    probability_ranking_allowed=False,
    semantic_similarity_allowed=False,
    nearest_known_substitution_allowed=False,
    language_model_allowed=False,
    hidden_classifier_allowed=False,
    automatic_only_candidate_selection_allowed=False,
    automatic_first_candidate_selection_allowed=False,
    automatic_safest_candidate_selection_allowed=False,
    msm_v1_mutation_allowed=False,
    outward_meaning_allowed=False,
    truth_evidence_permission_execution_allowed=False,
    route_tool_action_memory_rendering_delivery_allowed=False,
)

APPROVED_SELECTED_MEANING_CONSTRUCTION_PROFILES = (APPROVED_STRICT_PROFILE,)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
