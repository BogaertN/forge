"""Fail-closed validators for Slice 38H immutable records."""

from __future__ import annotations

from dataclasses import fields

from ..disabled_structural_concept_bootstrap import (
    validate_integration_result as validate_slice37_result,
)
from ..predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    CandidateProposalStatus,
    validate_result as validate_slice38_result,
)
from .fixtures import is_exact_accepted_fixture
from .schema import (
    PRE_SLICE38_COMMIT,
    PRE_SLICE38_TREE,
    SLICE38_ACCEPTED_CHAIN,
    SLICE38_ACCEPTED_SCOPE,
    SLICE38_DEFERRED_SCOPE,
    SLICE38_INCREMENT_LABELS,
    SLICE38_PERMANENT_BOUNDARIES,
    SLICE38G_ACCEPTED_HEAD,
    SLICE38G_ACCEPTED_SUBJECT,
    SLICE38G_ACCEPTED_TREE,
    SLICE38H_COMMIT_SUBJECT,
    SLICE38H_SCHEMA_VERSION,
    SLICE38H_SPEC_ID,
    SLICE38H_SPEC_VERSION,
    CloseoutIntegrationStage,
    CloseoutIntegrationStatus,
    CloseoutStageReceipt,
    DisabledPredicateRoleFrameBootstrapResult,
    DisabledPredicateRoleFrameBootstrapState,
    DisabledPredicateRoleFrameFixture,
    DisabledPredicateRoleFrameInvocation,
    Slice38AcceptanceRecord,
    Slice38RollbackMetadata,
)


class ValidationReport:
    __slots__ = ("ok", "issues")

    def __init__(self, issues: tuple[str, ...]) -> None:
        self.issues = issues
        self.ok = not issues


def _report(issues: list[str]) -> ValidationReport:
    return ValidationReport(tuple(issues))


def _exact_type(value: object, expected: type, issues: list[str]) -> bool:
    if type(value) is not expected:
        issues.append(f"exact type required: {expected.__name__}")
        return False
    return True


def _stable(record: object, id_field: str, issues: list[str]) -> None:
    try:
        actual = getattr(record, id_field)
        expected = record.expected_id()
    except Exception as error:
        issues.append(f"stable identity unavailable: {type(error).__name__}")
        return
    if actual != expected:
        issues.append(f"{id_field} mismatch")


def _exact_bool(record: object, names: tuple[str, ...], expected: bool, issues: list[str]) -> None:
    for name in names:
        if getattr(record, name, None) is not expected:
            issues.append(f"{name} must be {expected}")


_STATE_TRUE = (
    "disabled_by_default", "explicit_invocation_required",
    "accepted_static_fixture_only", "offline_only", "standard_library_only",
    "deterministic", "read_only", "in_memory_only", "exact_profile_bounded",
    "source_preserving", "structural_ancestry_preserving",
    "operator_ancestry_preserving", "phase_trail_ancestry_preserving",
    "scope_attachment_ancestry_preserving", "registry_snapshot_preserving",
    "zero_one_many_preserving", "explicit_non_progress_preserving",
    "rollback_safe",
)
_STATE_FALSE = (
    "automatic_activation_allowed", "arbitrary_text_invocation_allowed",
    "normalization_allowed", "nearest_known_substitution_allowed",
    "semantic_similarity_allowed", "learned_model_allowed",
    "external_resource_loading_allowed", "filesystem_read_allowed",
    "filesystem_write_allowed", "network_allowed", "memory_read_allowed",
    "memory_write_allowed", "api_route_allowed", "capability_route_allowed",
    "invocation_allowed", "tool_allowed", "action_allowed", "rendering_allowed",
    "delivery_allowed", "selected_predicate_allowed", "selected_frame_allowed",
    "selected_participant_assignment_allowed", "candidate_meaning_allowed",
    "selected_meaning_allowed", "clarification_allowed", "refusal_allowed",
    "blocked_progression_allowed", "truth_allowed", "evidence_validity_allowed",
    "permission_allowed", "runtime_self_acceptance_allowed", "release_authorized",
    "production_ready",
)


def validate_integration_state(value: object) -> ValidationReport:
    issues: list[str] = []
    if not _exact_type(value, DisabledPredicateRoleFrameBootstrapState, issues):
        return _report(issues)
    _stable(value, "state_id", issues)
    if value.spec_id != SLICE38H_SPEC_ID:
        issues.append("spec_id mismatch")
    if value.spec_version != SLICE38H_SPEC_VERSION:
        issues.append("spec_version mismatch")
    if value.schema_version != SLICE38H_SCHEMA_VERSION:
        issues.append("schema_version mismatch")
    if value.enabled is not value.explicit_offline_developer_enable:
        issues.append("enabled state must equal explicit enable")
    _exact_bool(value, _STATE_TRUE, True, issues)
    _exact_bool(value, _STATE_FALSE, False, issues)
    return _report(issues)


def validate_fixture(value: object) -> ValidationReport:
    issues: list[str] = []
    if not _exact_type(value, DisabledPredicateRoleFrameFixture, issues):
        return _report(issues)
    _stable(value, "fixture_id", issues)
    if not is_exact_accepted_fixture(value):
        issues.append("fixture is not exact accepted catalog member")
    if value.schema_version != SLICE38H_SCHEMA_VERSION:
        issues.append("schema_version mismatch")
    if type(value.fixture_name) is not str or not value.fixture_name:
        issues.append("fixture_name required")
    if type(value.slice37_fixture_name) is not str or not value.slice37_fixture_name:
        issues.append("slice37_fixture_name required")
    if value.accepted_fixture is not True or value.synthetic is not True:
        issues.append("fixture acceptance flags invalid")
    _exact_bool(
        value,
        ("explicit_invocation_only", "offline_only", "in_memory_only", "raw_text_not_carried_by_invocation"),
        True,
        issues,
    )
    for name in (
        "expected_action_predicate_candidate_count",
        "expected_role_layout_candidate_count",
        "expected_capability_reference_candidate_count",
    ):
        if type(getattr(value, name, None)) is not int or getattr(value, name) < 0:
            issues.append(f"{name} invalid")
    return _report(issues)


def validate_invocation(value: object) -> ValidationReport:
    issues: list[str] = []
    if not _exact_type(value, DisabledPredicateRoleFrameInvocation, issues):
        return _report(issues)
    _stable(value, "invocation_id", issues)
    if value.schema_version != SLICE38H_SCHEMA_VERSION:
        issues.append("schema_version mismatch")
    fixture = None
    try:
        from .fixtures import get_disabled_predicate_role_frame_fixture
        fixture = get_disabled_predicate_role_frame_fixture(value.fixture_name)
    except Exception:
        fixture = None
    if fixture is None or value.fixture_id != fixture.fixture_id:
        issues.append("fixture identity mismatch")
    if value.explicit_invocation is not True:
        issues.append("explicit invocation required")
    if value.raw_text_carried_by_invocation is not False:
        issues.append("raw text prohibited")
    from .integration import REQUESTED_OPERATION
    if value.requested_operation != REQUESTED_OPERATION:
        issues.append("requested operation mismatch")
    from ..predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
        CANONICAL_COMPATIBILITY_SNAPSHOT,
        DEFAULT_PROPOSAL_PROFILE,
        SLICE38_REGISTRY_SNAPSHOT,
    )
    if value.proposal_profile_id != DEFAULT_PROPOSAL_PROFILE.profile_id:
        issues.append("proposal profile mismatch")
    if value.compatibility_snapshot_id != CANONICAL_COMPATIBILITY_SNAPSHOT.snapshot_id:
        issues.append("compatibility snapshot mismatch")
    if value.slice38_registry_snapshot_id != SLICE38_REGISTRY_SNAPSHOT.snapshot_id:
        issues.append("Slice 38 snapshot mismatch")
    return _report(issues)


def validate_stage_receipt(value: object) -> ValidationReport:
    issues: list[str] = []
    if not _exact_type(value, CloseoutStageReceipt, issues):
        return _report(issues)
    _stable(value, "receipt_id", issues)
    if value.schema_version != SLICE38H_SCHEMA_VERSION:
        issues.append("schema_version mismatch")
    if value.stage_ordinal not in (1, 2):
        issues.append("stage ordinal invalid")
    if type(value.stage) is not CloseoutIntegrationStage:
        issues.append("stage enum invalid")
    if not value.predecessor_record_ids:
        issues.append("predecessor identity required")
    for name in ("output_record_id", "output_schema_version", "output_exact_type", "source_event_id", "source_sha256"):
        if type(getattr(value, name, None)) is not str or not getattr(value, name):
            issues.append(f"{name} required")
    _exact_bool(value, ("output_validation_passed", "source_ancestry_preserved", "candidate_only"), True, issues)
    _exact_bool(
        value,
        (
            "selected_predicate_created", "selected_frame_created",
            "selected_participant_assignment_created", "candidate_meaning_created",
            "selected_meaning_created", "permission_inferred", "route_created",
            "invocation_proposed", "tool_invoked", "action_performed",
            "memory_accessed", "rendered", "delivered",
            "evidence_validity_determined", "truth_determined",
        ),
        False,
        issues,
    )
    return _report(issues)


def validate_rollback_metadata(value: object) -> ValidationReport:
    issues: list[str] = []
    if not _exact_type(value, Slice38RollbackMetadata, issues):
        return _report(issues)
    _stable(value, "rollback_id", issues)
    expected = {
        "pre_slice38_commit": PRE_SLICE38_COMMIT,
        "pre_slice38_tree": PRE_SLICE38_TREE,
        "accepted_parent_head": SLICE38G_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE38G_ACCEPTED_TREE,
        "accepted_parent_subject": SLICE38G_ACCEPTED_SUBJECT,
        "expected_closeout_commit_subject": SLICE38H_COMMIT_SUBJECT,
        "schema_version": SLICE38H_SCHEMA_VERSION,
    }
    for name, wanted in expected.items():
        if getattr(value, name, None) != wanted:
            issues.append(f"{name} mismatch")
    _exact_bool(
        value,
        (
            "exact_commit_checkout_required", "exact_tree_match_required",
            "separate_recovery_clone_required", "git_object_verification_required",
            "rollback_proof_external_to_runtime",
        ),
        True,
        issues,
    )
    _exact_bool(
        value,
        ("live_repository_mutation_authorized", "runtime_rollback_execution_authorized"),
        False,
        issues,
    )
    return _report(issues)


def validate_acceptance_record(value: object) -> ValidationReport:
    issues: list[str] = []
    if not _exact_type(value, Slice38AcceptanceRecord, issues):
        return _report(issues)
    _stable(value, "acceptance_record_id", issues)
    expected = {
        "decision_owner": "Nicholas Jacob Bogaert / AI.Web",
        "accepted_increment_labels": SLICE38_INCREMENT_LABELS,
        "accepted_chain": SLICE38_ACCEPTED_CHAIN,
        "permanent_boundaries": SLICE38_PERMANENT_BOUNDARIES,
        "accepted_scope": SLICE38_ACCEPTED_SCOPE,
        "deferred_scope": SLICE38_DEFERRED_SCOPE,
        "accepted_parent_head": SLICE38G_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE38G_ACCEPTED_TREE,
        "pre_slice38_commit": PRE_SLICE38_COMMIT,
        "pre_slice38_tree": PRE_SLICE38_TREE,
        "schema_version": SLICE38H_SCHEMA_VERSION,
    }
    for name, wanted in expected.items():
        if getattr(value, name, None) != wanted:
            issues.append(f"{name} mismatch")
    _exact_bool(
        value,
        (
            "disabled_by_default", "explicitly_invoked_only", "fixture_only",
            "offline_only", "deterministic", "read_only", "exact_profile_bounded",
            "source_preserving", "no_selected_predicate_authority",
            "no_selected_frame_authority", "no_selected_participant_authority",
            "no_candidate_meaning_authority", "no_selected_meaning_authority",
            "no_permission_authority", "no_route_authority", "no_action_authority",
            "no_memory_authority", "no_delivery_authority",
            "decision_owner_acceptance_required",
        ),
        True,
        issues,
    )
    _exact_bool(value, ("runtime_self_grants_acceptance", "release_authorized", "production_ready"), False, issues)
    return _report(issues)


def validate_integration_result(value: object) -> ValidationReport:
    issues: list[str] = []
    if not _exact_type(value, DisabledPredicateRoleFrameBootstrapResult, issues):
        return _report(issues)
    _stable(value, "result_id", issues)
    if value.schema_version != SLICE38H_SCHEMA_VERSION:
        issues.append("schema_version mismatch")
    if type(value.status) is not CloseoutIntegrationStatus:
        issues.append("status enum invalid")
    if type(value.reason_code) is not str or not value.reason_code:
        issues.append("reason_code required")
    if value.stage_receipt_count != len(value.stage_receipts):
        issues.append("stage receipt count mismatch")
    for receipt in value.stage_receipts:
        if not validate_stage_receipt(receipt).ok:
            issues.append("invalid stage receipt")
    if not validate_rollback_metadata(value.rollback_metadata).ok:
        issues.append("invalid rollback metadata")
    if not validate_acceptance_record(value.acceptance_record).ok:
        issues.append("invalid acceptance record")
    if value.acceptance_record.rollback_metadata_id != value.rollback_metadata.rollback_id:
        issues.append("acceptance rollback identity mismatch")

    completed = value.status in (
        CloseoutIntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN,
        CloseoutIntegrationStatus.COMPLETED_EXPLICIT_UNSUPPORTED,
    )
    if completed:
        if not validate_slice37_result(value.slice37_result).ok:
            issues.append("invalid Slice 37 result")
        if not validate_slice38_result(value.slice38_result).ok:
            issues.append("invalid Slice 38 result")
        if value.stage_receipt_count != 2 or value.exact_stage_chain_complete is not True:
            issues.append("completed result requires exact two-stage chain")
        if not value.source_event_id or not value.source_sha256:
            issues.append("completed result requires source identity")
        if value.stage_receipts and (
            value.stage_receipts[0].stage is not CloseoutIntegrationStage.SLICE37_DISABLED_BOOTSTRAP
            or value.stage_receipts[1].stage is not CloseoutIntegrationStage.SLICE38_CANDIDATE_PROPOSAL
        ):
            issues.append("stage order mismatch")
        if value.slice38_result is not None:
            if value.action_predicate_candidate_count != value.slice38_result.action_predicate_candidate_count:
                issues.append("action candidate count mismatch")
            if value.role_layout_candidate_count != value.slice38_result.role_layout_candidate_count:
                issues.append("role layout count mismatch")
            if value.capability_reference_candidate_count != value.slice38_result.capability_reference_candidate_count:
                issues.append("capability candidate count mismatch")
            allowed = {
                CandidateProposalStatus.EXPLICIT_UNKNOWN,
                CandidateProposalStatus.EXPLICIT_UNSUPPORTED,
            }
            if value.slice38_result.status not in allowed:
                issues.append("canonical closeout result must preserve explicit non-progress")

    _exact_bool(
        value,
        (
            "disabled_by_default", "fixture_only", "offline_only",
            "standard_library_only", "deterministic", "read_only",
            "in_memory_only", "exact_profile_bounded",
        ),
        True,
        issues,
    )
    if completed:
        _exact_bool(
            value,
            (
                "explicitly_invoked", "source_preserved",
                "structural_ancestry_preserved", "operator_ancestry_preserved",
                "phase_trail_ancestry_preserved", "scope_attachment_ancestry_preserved",
                "registry_snapshots_preserved", "zero_one_many_preserved",
            ),
            True,
            issues,
        )
    _exact_bool(
        value,
        (
            "selected_predicate_created", "selected_frame_created",
            "selected_participant_assignment_created", "candidate_meaning_created",
            "selected_meaning_created", "clarification_outcome_created",
            "refusal_outcome_created", "blocked_progression_outcome_created",
            "permission_inferred", "capability_availability_created", "route_created",
            "invocation_proposed", "tool_invoked", "action_performed",
            "memory_read_performed", "memory_write_performed", "outward_rendered",
            "delivered", "evidence_validity_determined", "truth_determined",
            "filesystem_read_performed", "filesystem_write_performed",
            "network_access_performed", "external_resource_loaded",
            "language_model_used", "embedding_used", "semantic_similarity_used",
            "technical_acceptance_granted_by_runtime", "release_authorized",
            "production_ready",
        ),
        False,
        issues,
    )
    return _report(issues)


PUBLIC_VALIDATORS = (
    validate_acceptance_record,
    validate_fixture,
    validate_integration_result,
    validate_integration_state,
    validate_invocation,
    validate_rollback_metadata,
    validate_stage_receipt,
)
