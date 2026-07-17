"""Fail-closed validation for Slice 37G disabled integration records."""

from __future__ import annotations

from dataclasses import dataclass

from ..candidate_resonant_phase_trail import (
    CandidateResonantPhaseTrailResult,
    validate_candidate_resonant_phase_trail_result,
)
from ..deterministic_structural_derivation import (
    DeterministicStructuralDerivationResult,
    validate_deterministic_structural_derivation_result,
)
from ..input_event_custody import (
    InputEventCaptureResult,
    validate_input_event_capture_result,
)
from ..resonant_operator_candidate_binding import (
    ResonantOperatorCandidateBindingResult,
    validate_resonant_operator_candidate_binding_result,
)
from ..scope_attachment_reference_constraints import (
    ScopeAttachmentReferenceConstraintResult,
    validate_scope_attachment_reference_constraint_result,
)
from ..source_field_projection import (
    SourceFieldProjectionResult,
    validate_source_field_projection_result,
)
from ..structural_concept_candidate_proposal import (
    StructuralConceptCandidateProposalResult,
    validate_proposal_profile,
    validate_proposal_result,
)
from ..symbolic_grammar_operator_registry import (
    SymbolicGrammarOperatorRegistry,
    validate_symbolic_grammar_operator_registry,
)
from .fixtures import is_exact_accepted_fixture
from .schema import (
    PRE_SLICE37_COMMIT,
    PRE_SLICE37_TREE,
    SLICE37_ACCEPTED_CHAIN,
    SLICE37_ACCEPTED_SCOPE,
    SLICE37_DEFERRED_SCOPE,
    SLICE37_INCREMENT_LABELS,
    SLICE37_PERMANENT_BOUNDARIES,
    SLICE37F_ACCEPTED_HEAD,
    SLICE37F_ACCEPTED_TREE,
    SLICE37G_COMMIT_SUBJECT,
    DisabledStructuralConceptBootstrapResult,
    DisabledStructuralConceptBootstrapState,
    DisabledStructuralConceptFixture,
    DisabledStructuralConceptInvocation,
    IntegrationStage,
    IntegrationStageReceipt,
    IntegrationStatus,
    Slice37AcceptanceRecord,
    Slice37RollbackMetadata,
)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    issue_codes: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.issue_codes


def _report(issues: list[str]) -> ValidationReport:
    return ValidationReport(tuple(dict.fromkeys(issues)))


_STATE_TRUE = (
    "disabled_by_default",
    "explicit_invocation_required",
    "accepted_static_fixture_only",
    "offline_only",
    "standard_library_only",
    "deterministic",
    "read_only",
    "in_memory_only",
    "exact_profile_bounded",
    "source_preserving",
    "structural_ancestry_preserving",
    "registry_snapshot_preserving",
    "zero_one_many_preserving",
    "explicit_unknown_preserving",
    "explicit_unsupported_preserving",
    "rollback_safe",
)

_STATE_FALSE = (
    "automatic_activation_allowed",
    "arbitrary_text_invocation_allowed",
    "conventional_word_token_authority_allowed",
    "normalization_allowed",
    "semantic_similarity_allowed",
    "learned_model_allowed",
    "external_resource_loading_allowed",
    "filesystem_read_allowed",
    "filesystem_write_allowed",
    "network_allowed",
    "memory_read_allowed",
    "memory_write_allowed",
    "api_route_allowed",
    "capability_route_allowed",
    "tool_invocation_allowed",
    "action_allowed",
    "rendering_allowed",
    "delivery_allowed",
    "candidate_meaning_allowed",
    "selected_meaning_allowed",
    "selected_sense_allowed",
    "predicate_identity_allowed",
    "participant_role_allowed",
    "truth_allowed",
    "evidence_validity_allowed",
    "clarification_allowed",
    "permission_allowed",
    "runtime_self_acceptance_allowed",
    "release_authorized",
    "production_ready",
)


def validate_integration_state(record: object) -> ValidationReport:
    if type(record) is not DisabledStructuralConceptBootstrapState:
        return _report(["invalid_state_type"])
    issues: list[str] = []
    if record.state_id != record.expected_id():
        issues.append("state_identity_mismatch")
    if record.enabled is not record.explicit_offline_developer_enable:
        issues.append("state_enable_flag_mismatch")
    for name in _STATE_TRUE:
        if getattr(record, name) is not True:
            issues.append(f"state_{name}_must_be_true")
    for name in _STATE_FALSE:
        if getattr(record, name) is not False:
            issues.append(f"state_{name}_must_be_false")
    return _report(issues)


def validate_fixture(record: object) -> ValidationReport:
    if type(record) is not DisabledStructuralConceptFixture:
        return _report(["invalid_fixture_type"])
    issues: list[str] = []
    if record.fixture_id != record.expected_id():
        issues.append("fixture_identity_mismatch")
    if not is_exact_accepted_fixture(record):
        issues.append("fixture_not_in_closed_catalog")
    if not record.fixture_name or not record.exact_source_text:
        issues.append("fixture_identity_or_source_missing")
    if type(record.sequence_number) is not int or record.sequence_number <= 0:
        issues.append("fixture_sequence_invalid")
    for name in (
        "expected_lexical_occurrence_count",
        "expected_concept_candidate_count",
        "expected_sense_candidate_count",
        "expected_unknown_count",
        "expected_unsupported_count",
    ):
        value = getattr(record, name)
        if type(value) is not int or value < 0:
            issues.append(f"fixture_{name}_invalid")
    for name in (
        "accepted_fixture",
        "synthetic",
        "explicit_invocation_only",
        "offline_only",
        "in_memory_only",
        "raw_text_not_carried_by_invocation",
    ):
        if getattr(record, name) is not True:
            issues.append(f"fixture_{name}_must_be_true")
    return _report(issues)


def validate_invocation(record: object) -> ValidationReport:
    if type(record) is not DisabledStructuralConceptInvocation:
        return _report(["invalid_invocation_type"])
    issues: list[str] = []
    if record.invocation_id != record.expected_id():
        issues.append("invocation_identity_mismatch")
    if not record.fixture_name or not record.fixture_id or not record.profile_id:
        issues.append("invocation_reference_missing")
    if record.explicit_invocation is not True:
        issues.append("invocation_must_be_explicit")
    if record.requested_operation != (
        "run_disabled_structural_concept_candidate_proposal"
    ):
        issues.append("invocation_operation_mismatch")
    if record.raw_text_carried_by_invocation is not False:
        issues.append("invocation_raw_text_prohibited")
    return _report(issues)


def validate_stage_receipt(record: object) -> ValidationReport:
    if type(record) is not IntegrationStageReceipt:
        return _report(["invalid_stage_receipt_type"])
    issues: list[str] = []
    if record.receipt_id != record.expected_id():
        issues.append("stage_receipt_identity_mismatch")
    if record.stage_ordinal not in range(1, 9):
        issues.append("stage_receipt_ordinal_invalid")
    if not record.predecessor_record_ids:
        issues.append("stage_receipt_predecessor_missing")
    if not record.output_record_id or not record.output_schema_version:
        issues.append("stage_receipt_output_identity_missing")
    if record.output_validation_passed is not True:
        issues.append("stage_receipt_output_validation_required")
    if not record.source_event_id or not record.source_sha256:
        issues.append("stage_receipt_source_ancestry_missing")
    if record.source_ancestry_preserved is not True:
        issues.append("stage_receipt_source_ancestry_required")
    for name in (
        "selected_meaning_created",
        "truth_determined",
        "permission_inferred",
        "memory_accessed",
        "route_created",
        "tool_invoked",
        "action_performed",
        "rendered",
        "delivered",
    ):
        if getattr(record, name) is not False:
            issues.append(f"stage_receipt_{name}_must_be_false")
    return _report(issues)


def validate_rollback_metadata(record: object) -> ValidationReport:
    if type(record) is not Slice37RollbackMetadata:
        return _report(["invalid_rollback_type"])
    issues: list[str] = []
    if record.rollback_id != record.expected_id():
        issues.append("rollback_identity_mismatch")
    expected = {
        "pre_slice37_commit": PRE_SLICE37_COMMIT,
        "pre_slice37_tree": PRE_SLICE37_TREE,
        "accepted_parent_head": SLICE37F_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE37F_ACCEPTED_TREE,
        "expected_closeout_commit_subject": SLICE37G_COMMIT_SUBJECT,
    }
    for name, value in expected.items():
        if getattr(record, name) != value:
            issues.append(f"rollback_{name}_mismatch")
    for name in (
        "exact_commit_checkout_required",
        "exact_tree_match_required",
        "separate_recovery_clone_required",
        "git_object_verification_required",
        "rollback_proof_external_to_runtime",
    ):
        if getattr(record, name) is not True:
            issues.append(f"rollback_{name}_must_be_true")
    for name in (
        "live_repository_mutation_authorized",
        "runtime_rollback_execution_authorized",
    ):
        if getattr(record, name) is not False:
            issues.append(f"rollback_{name}_must_be_false")
    return _report(issues)


def validate_acceptance_record(record: object) -> ValidationReport:
    if type(record) is not Slice37AcceptanceRecord:
        return _report(["invalid_acceptance_type"])
    issues: list[str] = []
    if record.acceptance_record_id != record.expected_id():
        issues.append("acceptance_identity_mismatch")
    expected = {
        "accepted_increment_labels": SLICE37_INCREMENT_LABELS,
        "accepted_chain": SLICE37_ACCEPTED_CHAIN,
        "permanent_boundaries": SLICE37_PERMANENT_BOUNDARIES,
        "accepted_scope": SLICE37_ACCEPTED_SCOPE,
        "deferred_scope": SLICE37_DEFERRED_SCOPE,
        "accepted_parent_head": SLICE37F_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE37F_ACCEPTED_TREE,
        "pre_slice37_commit": PRE_SLICE37_COMMIT,
        "pre_slice37_tree": PRE_SLICE37_TREE,
    }
    for name, value in expected.items():
        if getattr(record, name) != value:
            issues.append(f"acceptance_{name}_mismatch")
    for name in (
        "disabled_by_default",
        "explicitly_invoked_only",
        "offline_only",
        "deterministic",
        "read_only",
        "exact_profile_bounded",
        "source_preserving",
        "no_public_runtime_authority",
        "no_selected_meaning_authority",
        "no_action_authority",
        "no_memory_authority",
        "no_route_authority",
        "no_delivery_authority",
        "decision_owner_acceptance_required",
    ):
        if getattr(record, name) is not True:
            issues.append(f"acceptance_{name}_must_be_true")
    for name in (
        "runtime_self_grants_acceptance",
        "release_authorized",
        "production_ready",
    ):
        if getattr(record, name) is not False:
            issues.append(f"acceptance_{name}_must_be_false")
    return _report(issues)


_COMPLETED_STATUSES = {
    IntegrationStatus.COMPLETED_CANDIDATES,
    IntegrationStatus.COMPLETED_UNRESOLVED,
    IntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN,
    IntegrationStatus.COMPLETED_EXPLICIT_UNSUPPORTED,
}


def validate_integration_result(record: object) -> ValidationReport:
    if type(record) is not DisabledStructuralConceptBootstrapResult:
        return _report(["invalid_result_type"])
    issues: list[str] = []
    if record.result_id != record.expected_id():
        issues.append("result_identity_mismatch")
    if record.stage_receipt_count != len(record.stage_receipts):
        issues.append("result_stage_receipt_count_mismatch")
    if tuple(item.stage_ordinal for item in record.stage_receipts) != tuple(
        range(1, len(record.stage_receipts) + 1)
    ):
        issues.append("result_stage_receipts_not_contiguous")
    for item in record.stage_receipts:
        issues.extend(validate_stage_receipt(item).issue_codes)
        if item.state_id != record.state_id:
            issues.append("result_stage_state_reference_mismatch")
        if item.invocation_id != record.invocation_id:
            issues.append("result_stage_invocation_reference_mismatch")
        if item.fixture_id != record.fixture_id:
            issues.append("result_stage_fixture_reference_mismatch")
    issues.extend(validate_proposal_profile(record.profile).issue_codes)
    issues.extend(validate_acceptance_record(record.acceptance_record).issue_codes)
    issues.extend(validate_rollback_metadata(record.rollback_metadata).issue_codes)
    if (
        record.acceptance_record.rollback_metadata_id
        != record.rollback_metadata.rollback_id
    ):
        issues.append("result_acceptance_rollback_reference_mismatch")

    for name in (
        "disabled_by_default",
        "offline_only",
        "standard_library_only",
        "deterministic",
        "read_only",
        "in_memory_only",
        "exact_profile_bounded",
        "source_preserved",
        "structural_ancestry_preserved",
    ):
        if getattr(record, name) is not True:
            issues.append(f"result_{name}_must_be_true")
    for name in (
        "candidate_meaning_created",
        "selected_meaning_created",
        "selected_sense_created",
        "predicate_identity_created",
        "participant_roles_assigned",
        "truth_determined",
        "evidence_validity_determined",
        "clarification_asked",
        "permission_inferred",
        "memory_read_performed",
        "memory_write_performed",
        "api_route_created",
        "capability_route_created",
        "tool_invoked",
        "action_performed",
        "outward_rendered",
        "delivered",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "semantic_similarity_used",
        "technical_acceptance_granted_by_runtime",
        "release_authorized",
        "production_ready",
    ):
        if getattr(record, name) is not False:
            issues.append(f"result_{name}_must_be_false")

    if record.status in _COMPLETED_STATUSES:
        if record.stage_receipt_count != 8:
            issues.append("completed_result_requires_eight_stages")
        if record.exact_stage_chain_complete is not True:
            issues.append("completed_result_requires_exact_stage_chain")
        if record.registry_snapshot_preserved is not True:
            issues.append("completed_result_requires_registry_snapshot")
        if record.zero_one_many_preserved is not True:
            issues.append("completed_result_requires_zero_one_many")
        expected_types = (
            (record.custody_result, InputEventCaptureResult),
            (record.projection_result, SourceFieldProjectionResult),
            (record.grammar_registry, SymbolicGrammarOperatorRegistry),
            (record.binding_result, ResonantOperatorCandidateBindingResult),
            (record.phase_trail_result, CandidateResonantPhaseTrailResult),
            (record.constraint_result, ScopeAttachmentReferenceConstraintResult),
            (record.structural_result, DeterministicStructuralDerivationResult),
            (record.proposal_result, StructuralConceptCandidateProposalResult),
        )
        if any(type(value) is not expected for value, expected in expected_types):
            issues.append("completed_result_exact_predecessor_type_mismatch")
        else:
            custody = record.custody_result
            projection = record.projection_result
            registry = record.grammar_registry
            binding = record.binding_result
            trails = record.phase_trail_result
            constraints = record.constraint_result
            structural = record.structural_result
            proposal = record.proposal_result
            assert custody is not None
            assert projection is not None
            assert registry is not None
            assert binding is not None
            assert trails is not None
            assert constraints is not None
            assert structural is not None
            assert proposal is not None
            nested = (
                validate_input_event_capture_result(custody),
                validate_source_field_projection_result(projection),
                validate_symbolic_grammar_operator_registry(registry),
                validate_resonant_operator_candidate_binding_result(
                    binding,
                    projection,
                    registry,
                ),
                validate_candidate_resonant_phase_trail_result(
                    trails,
                    projection,
                    binding,
                    registry,
                ),
                validate_scope_attachment_reference_constraint_result(
                    constraints,
                    projection,
                    binding,
                    trails,
                ),
                validate_deterministic_structural_derivation_result(
                    structural,
                    custody,
                    projection,
                    binding,
                    trails,
                    constraints,
                ),
                validate_proposal_result(proposal),
            )
            if any(not report.ok for report in nested):
                issues.append("completed_result_nested_validation_failed")
            if record.proposal_profile_id != proposal.profile.profile_id:
                issues.append("result_profile_reference_mismatch")
            if record.registry_snapshot_id != proposal.registry_snapshot.snapshot_id:
                issues.append("result_registry_snapshot_reference_mismatch")
            if record.lexical_occurrence_count != proposal.lexical_occurrence_count:
                issues.append("result_lexical_count_mismatch")
            if record.concept_candidate_count != proposal.concept_candidate_count:
                issues.append("result_concept_count_mismatch")
            if record.sense_candidate_count != proposal.sense_candidate_count:
                issues.append("result_sense_count_mismatch")
            if record.explicit_unknown_count != proposal.explicit_unknown_count:
                issues.append("result_unknown_count_mismatch")
            if (
                record.explicit_unsupported_count
                != proposal.explicit_unsupported_count
            ):
                issues.append("result_unsupported_count_mismatch")
    else:
        if record.exact_stage_chain_complete:
            issues.append("held_result_must_not_claim_complete_chain")

    return _report(issues)


__all__ = (
    "ValidationReport",
    "validate_acceptance_record",
    "validate_fixture",
    "validate_integration_result",
    "validate_integration_state",
    "validate_invocation",
    "validate_rollback_metadata",
    "validate_stage_receipt",
)
