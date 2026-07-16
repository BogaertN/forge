"""Fail-closed validation for Slice 37F records."""

from __future__ import annotations

from dataclasses import dataclass

from .schema import (
    SLICE37F_NON_AUTHORITY_BOUNDARIES,
    ConceptCandidateProposal,
    ExactLexicalOccurrenceProposal,
    LexicalOccurrenceDisposition,
    ProposalResultStatus,
    RegistrySnapshotIdentity,
    SenseCandidateProposal,
    StructuralCandidateAncestry,
    StructuralConceptCandidateProposalResult,
    StructuralConceptProposalProfile,
)


@dataclass(frozen=True, slots=True)
class ProposalValidationReport:
    issue_codes: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.issue_codes


def _report(issues: list[str]) -> ProposalValidationReport:
    return ProposalValidationReport(tuple(dict.fromkeys(issues)))


def validate_proposal_profile(record: object) -> ProposalValidationReport:
    issues: list[str] = []
    if type(record) is not StructuralConceptProposalProfile:
        return _report(["invalid_profile_type"])
    if record.profile_id != record.expected_id():
        issues.append("profile_identity_mismatch")
    true_fields = (
        "explicit_invocation_required", "offline_only", "standard_library_only",
        "deterministic", "immutable_records", "exact_source_preservation_required",
        "exact_case_sensitive_matching", "ascii_identifier_boundary_profile",
        "structural_result_consumption_allowed", "exact_term_lookup_allowed",
        "concept_candidate_proposal_allowed", "sense_candidate_proposal_allowed",
        "preserve_zero_one_many", "preserve_unresolved_alternatives",
        "explicit_unknown_required", "explicit_unsupported_required",
    )
    false_fields = (
        "normalization_allowed", "casefolding_allowed", "spelling_correction_allowed",
        "stemming_allowed", "synonym_expansion_allowed", "nearest_match_allowed",
        "frequency_ranking_allowed", "semantic_similarity_allowed",
        "model_inference_allowed", "dictionary_fallback_allowed",
        "candidate_meaning_creation_allowed", "selected_meaning_allowed",
        "selected_sense_allowed", "predicate_identity_allowed",
        "participant_role_assignment_allowed", "truth_determination_allowed",
        "evidence_validity_determination_allowed", "clarification_allowed",
        "permission_inference_allowed", "capability_routing_allowed",
        "tool_invocation_allowed", "action_execution_allowed", "memory_read_allowed",
        "memory_write_allowed", "outward_rendering_allowed", "delivery_allowed",
    )
    for name in true_fields:
        if getattr(record, name) is not True:
            issues.append(f"profile_{name}_must_be_true")
    for name in false_fields:
        if getattr(record, name) is not False:
            issues.append(f"profile_{name}_must_be_false")
    if not record.language_tags or not all(type(item) is str and item for item in record.language_tags):
        issues.append("profile_language_tags_invalid")
    if not record.namespace_id or not record.namespace_scope or not record.domain_scope:
        issues.append("profile_scope_missing")
    if record.non_authority_boundaries != SLICE37F_NON_AUTHORITY_BOUNDARIES:
        issues.append("profile_non_authority_boundary_mismatch")
    return _report(issues)


def validate_registry_snapshot(record: object) -> ProposalValidationReport:
    issues: list[str] = []
    if type(record) is not RegistrySnapshotIdentity:
        return _report(["invalid_registry_snapshot_type"])
    if record.snapshot_id != record.expected_id():
        issues.append("snapshot_identity_mismatch")
    for name in (
        "concept_registry_manifest_id", "concept_registry_digest",
        "sense_mapping_manifest_id", "sense_mapping_registry_digest",
        "semantic_class_relation_manifest_id", "semantic_class_relation_registry_digest",
        "namespace_id", "namespace_version",
    ):
        if not getattr(record, name):
            issues.append(f"snapshot_{name}_missing")
    for name in (
        "concept_count", "sense_count", "lexical_reference_count", "mapping_count",
        "semantic_class_count", "relation_family_count", "relation_type_count",
        "relation_instance_count",
    ):
        value = getattr(record, name)
        if type(value) is not int or value < 0:
            issues.append(f"snapshot_{name}_invalid")
    if record.exact_snapshot is not True:
        issues.append("snapshot_must_be_exact")
    if record.external_resources_loaded is not False:
        issues.append("snapshot_external_resource_loading_prohibited")
    if record.runtime_mutation_allowed is not False:
        issues.append("snapshot_runtime_mutation_prohibited")
    if record.relation_instance_count != 0:
        issues.append("snapshot_relation_instances_prohibited")
    return _report(issues)


def validate_structural_ancestry(record: object) -> ProposalValidationReport:
    issues: list[str] = []
    if type(record) is not StructuralCandidateAncestry:
        return _report(["invalid_structural_ancestry_type"])
    if record.ancestry_id != record.expected_id():
        issues.append("ancestry_identity_mismatch")
    for name in (
        "lexical_occurrence_id", "structural_result_id", "structural_set_id",
        "structural_candidate_id", "source_event_id", "source_sha256",
        "root_source_span_id", "projection_id", "constrained_trail_id",
        "phase_trail_id", "operator_graph_id", "source_coverage_proof_id",
    ):
        if not getattr(record, name):
            issues.append(f"ancestry_{name}_missing")
    if record.exact_ancestry_complete is not True:
        issues.append("ancestry_exact_ancestry_required")
    if record.source_reconstruction_proven is not True:
        issues.append("ancestry_source_reconstruction_required")
    if record.candidate_only is not True or record.selected_structure is not False:
        issues.append("ancestry_candidate_only_boundary_violation")
    return _report(issues)


def validate_lexical_occurrence(record: object) -> ProposalValidationReport:
    issues: list[str] = []
    if type(record) is not ExactLexicalOccurrenceProposal:
        return _report(["invalid_lexical_occurrence_type"])
    if record.occurrence_id != record.expected_id():
        issues.append("occurrence_identity_mismatch")
    if not (0 <= record.code_point_start < record.code_point_end):
        issues.append("occurrence_code_point_range_invalid")
    if not (0 <= record.utf8_byte_start < record.utf8_byte_end):
        issues.append("occurrence_utf8_range_invalid")
    if not record.exact_source_text or not record.source_span_ids:
        issues.append("occurrence_exact_source_ancestry_missing")
    if not record.lexical_reference_id or not record.lexical_reference_version:
        issues.append("occurrence_lexical_identity_missing")
    if not record.lookup_request_id or not record.lookup_result_id:
        issues.append("occurrence_lookup_identity_missing")
    if record.exact_match is not True:
        issues.append("occurrence_exact_match_required")
    if record.candidate_order_is_ranked is not False:
        issues.append("occurrence_ranking_prohibited")
    if record.selected_concept_id is not None or record.selected_sense_id is not None:
        issues.append("occurrence_selection_prohibited")
    if record.disposition is LexicalOccurrenceDisposition.UNMAPPED:
        if record.explicit_unknown is not True or record.explicit_unsupported is not False:
            issues.append("occurrence_unknown_flags_invalid")
    elif record.disposition is LexicalOccurrenceDisposition.UNSUPPORTED:
        if record.explicit_unsupported is not True or record.explicit_unknown is not False:
            issues.append("occurrence_unsupported_flags_invalid")
    elif record.explicit_unknown or record.explicit_unsupported:
        issues.append("occurrence_mapped_flags_invalid")
    if record.non_authority_boundaries != SLICE37F_NON_AUTHORITY_BOUNDARIES:
        issues.append("occurrence_non_authority_boundary_mismatch")
    return _report(issues)


def _candidate_boundary_issues(record: object) -> list[str]:
    issues: list[str] = []
    for name in (
        "selected", "candidate_meaning_created", "truth_determined",
        "evidence_validity_determined", "permission_inferred",
        "capability_route_created", "tool_invoked", "action_performed",
        "memory_accessed", "outward_rendered", "delivered",
    ):
        if getattr(record, name) is not False:
            issues.append(f"candidate_{name}_must_be_false")
    if getattr(record, "candidate_only") is not True:
        issues.append("candidate_candidate_only_must_be_true")
    if record.non_authority_boundaries != SLICE37F_NON_AUTHORITY_BOUNDARIES:
        issues.append("candidate_non_authority_boundary_mismatch")
    return issues


def validate_concept_candidate(record: object) -> ProposalValidationReport:
    if type(record) is not ConceptCandidateProposal:
        return _report(["invalid_concept_candidate_type"])
    issues = _candidate_boundary_issues(record)
    if record.proposal_id != record.expected_id():
        issues.append("concept_candidate_identity_mismatch")
    for name in (
        "lexical_occurrence_id", "structural_result_id", "profile_id",
        "registry_snapshot_id", "exact_matched_lexical_reference_id",
        "exact_matched_lexical_reference_version", "concept_id", "concept_key",
        "concept_version", "concept_lifecycle_state", "concept_provenance_ref",
    ):
        if not getattr(record, name):
            issues.append(f"concept_candidate_{name}_missing")
    return _report(issues)


def validate_sense_candidate(record: object) -> ProposalValidationReport:
    if type(record) is not SenseCandidateProposal:
        return _report(["invalid_sense_candidate_type"])
    issues = _candidate_boundary_issues(record)
    if record.proposal_id != record.expected_id():
        issues.append("sense_candidate_identity_mismatch")
    for name in (
        "selected_sense_created", "predicate_identity_created",
        "participant_roles_assigned", "clarification_asked",
    ):
        if getattr(record, name) is not False:
            issues.append(f"sense_candidate_{name}_must_be_false")
    for name in (
        "lexical_occurrence_id", "structural_result_id", "profile_id",
        "registry_snapshot_id", "exact_matched_lexical_reference_id",
        "exact_matched_lexical_reference_version", "concept_id", "sense_id",
        "sense_key", "sense_version", "sense_lifecycle_state", "sense_provenance_ref",
    ):
        if not getattr(record, name):
            issues.append(f"sense_candidate_{name}_missing")
    return _report(issues)


def validate_proposal_result(record: object) -> ProposalValidationReport:
    issues: list[str] = []
    if type(record) is not StructuralConceptCandidateProposalResult:
        return _report(["invalid_proposal_result_type"])
    if record.result_id != record.expected_id():
        issues.append("result_identity_mismatch")
    issues.extend(validate_proposal_profile(record.profile).issue_codes)
    issues.extend(validate_registry_snapshot(record.registry_snapshot).issue_codes)
    if record.status is ProposalResultStatus.EXPLICIT_UNKNOWN and not record.lexical_occurrences:
        if not record.unmatched_exact_source_fragments:
            issues.append("unknown_result_unmatched_source_missing")
        if not record.unmatched_source_span_ids:
            issues.append("unknown_result_unmatched_span_ancestry_missing")
        if not record.unmatched_code_point_ranges:
            issues.append("unknown_result_unmatched_range_missing")
    if record.lexical_occurrence_count != len(record.lexical_occurrences):
        issues.append("result_lexical_occurrence_count_mismatch")
    if record.structural_ancestry_count != len(record.structural_ancestries):
        issues.append("result_structural_ancestry_count_mismatch")
    if record.concept_candidate_count != len(record.concept_candidates):
        issues.append("result_concept_candidate_count_mismatch")
    if record.sense_candidate_count != len(record.sense_candidates):
        issues.append("result_sense_candidate_count_mismatch")
    for item in record.lexical_occurrences:
        issues.extend(validate_lexical_occurrence(item).issue_codes)
    for item in record.structural_ancestries:
        issues.extend(validate_structural_ancestry(item).issue_codes)
    for item in record.concept_candidates:
        issues.extend(validate_concept_candidate(item).issue_codes)
    for item in record.sense_candidates:
        issues.extend(validate_sense_candidate(item).issue_codes)
    occurrence_ids = {item.occurrence_id for item in record.lexical_occurrences}
    ancestry_ids = {item.ancestry_id for item in record.structural_ancestries}
    concept_ids = {item.proposal_id for item in record.concept_candidates}
    sense_ids = {item.proposal_id for item in record.sense_candidates}
    for item in record.lexical_occurrences:
        if not set(item.structural_ancestry_ids).issubset(ancestry_ids):
            issues.append("result_occurrence_ancestry_reference_missing")
        if not set(item.concept_candidate_proposal_ids).issubset(concept_ids):
            issues.append("result_occurrence_concept_reference_missing")
        if not set(item.sense_candidate_proposal_ids).issubset(sense_ids):
            issues.append("result_occurrence_sense_reference_missing")
    for item in record.structural_ancestries:
        if item.lexical_occurrence_id not in occurrence_ids:
            issues.append("result_ancestry_occurrence_reference_missing")
    for item in (*record.concept_candidates, *record.sense_candidates):
        if item.lexical_occurrence_id not in occurrence_ids:
            issues.append("result_candidate_occurrence_reference_missing")
        if not set(item.structural_ancestry_ids).issubset(ancestry_ids):
            issues.append("result_candidate_ancestry_reference_missing")
    if record.status is ProposalResultStatus.PREDECESSOR_REJECTED:
        if record.lexical_occurrences or record.concept_candidates or record.sense_candidates:
            issues.append("rejected_result_must_not_create_candidates")
    for name in (
        "zero_one_many_preserved", "structural_plurality_preserved",
        "source_ancestry_preserved", "operator_ancestry_preserved",
        "scope_attachment_ancestry_preserved", "exact_registry_lookup_only",
    ):
        if getattr(record, name) is not True:
            issues.append(f"result_{name}_must_be_true")
    for name in (
        "candidate_order_is_ranked", "candidate_meaning_created",
        "selected_meaning_created", "selected_sense_created",
        "predicate_identity_created", "participant_roles_assigned",
        "truth_determined", "evidence_validity_determined", "clarification_asked",
        "permission_inferred", "capability_route_created", "tool_invoked",
        "action_performed", "memory_read_performed", "memory_write_performed",
        "outward_rendered", "delivered", "filesystem_read_performed",
        "filesystem_write_performed", "network_access_performed",
        "external_resource_loaded", "language_model_used", "embedding_used",
        "semantic_similarity_used",
    ):
        if getattr(record, name) is not False:
            issues.append(f"result_{name}_must_be_false")
    if record.non_authority_boundaries != SLICE37F_NON_AUTHORITY_BOUNDARIES:
        issues.append("result_non_authority_boundary_mismatch")
    return _report(issues)


def assert_proposal_profile(record: StructuralConceptProposalProfile) -> StructuralConceptProposalProfile:
    report = validate_proposal_profile(record)
    if not report.ok:
        raise ValueError(report.issue_codes)
    return record


def assert_proposal_result(record: StructuralConceptCandidateProposalResult) -> StructuralConceptCandidateProposalResult:
    report = validate_proposal_result(record)
    if not report.ok:
        raise ValueError(report.issue_codes)
    return record
