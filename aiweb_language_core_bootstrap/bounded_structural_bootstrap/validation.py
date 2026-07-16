"""Deterministic validators for Slice 36H bounded bootstrap records."""

from __future__ import annotations

from ..bootstrap_adapter import (
    BootstrapAdapterState,
    validate_bootstrap_adapter_state,
)
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
from ..schema import (
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    require_non_empty_text,
    require_true,
    require_unique_text_tuple,
)
from ..source_field_projection import (
    SourceFieldProjectionResult,
    validate_source_field_projection_result,
)
from ..symbolic_grammar_operator_registry import (
    SymbolicGrammarOperatorRegistry,
    validate_symbolic_grammar_operator_registry,
)
from .fixtures import is_exact_accepted_bounded_structural_fixture
from .schema import (
    PRE_SLICE36_COMMIT,
    PRE_SLICE36_TREE,
    SLICE36_ACCEPTED_CHAIN,
    SLICE36_ACCEPTED_SCOPE,
    SLICE36_DEFERRED_SCOPE,
    SLICE36_INCREMENT_LABELS,
    SLICE36_MATHEMATICAL_DIRECTION,
    SLICE36_PERMANENT_BOUNDARIES,
    SLICE36G_ACCEPTED_HEAD,
    SLICE36G_ACCEPTED_TREE,
    SLICE36H_COMMIT_SUBJECT,
    SLICE36H_SCHEMA_VERSION,
    SLICE36H_SPEC_ID,
    SLICE36H_SPEC_VERSION,
    BootstrapIntegrationStatus,
    BootstrapInvocationKind,
    BootstrapStage,
    BootstrapStageReceipt,
    BootstrapStageStatus,
    BoundedStructuralBootstrapInvocation,
    BoundedStructuralBootstrapResult,
    BoundedStructuralBootstrapState,
    BoundedStructuralFixtureRecord,
    Slice36AcceptanceRecord,
    Slice36RollbackMetadata,
    source_sha256,
)


_STATE_TRUE_FIELDS = (
    "disabled_by_default",
    "explicit_invocation_required",
    "accepted_fixture_only",
    "approved_caller_path_defined",
    "offline_only",
    "standard_library_only",
    "deterministic",
    "read_only",
    "in_memory_only",
    "source_preserving",
    "operator_trace_preserving",
    "phase_trace_preserving",
    "bounded_supported_profile_only",
    "non_llm",
    "rollback_safe",
)

_STATE_FALSE_FIELDS = (
    "approved_caller_catalog_installed",
    "raw_text_alone_allowed",
    "arbitrary_input_allowed",
    "automatic_activation_allowed",
    "hidden_fallback_parser_allowed",
    "conventional_nlp_authority_allowed",
    "external_linguistic_resource_loading_allowed",
    "filesystem_search_allowed",
    "filesystem_read_allowed",
    "filesystem_write_allowed",
    "repository_history_search_allowed",
    "network_allowed",
    "web_access_allowed",
    "environment_lookup_allowed",
    "memory_read_allowed",
    "memory_write_allowed",
    "protected_memory_retrieval_allowed",
    "llm_allowed",
    "embedding_allowed",
    "vector_database_allowed",
    "semantic_similarity_allowed",
    "learned_parser_allowed",
    "neural_classifier_allowed",
    "rag_allowed",
    "main_connection_allowed",
    "api_route_allowed",
    "capability_route_allowed",
    "tool_activation_allowed",
    "action_execution_allowed",
    "outward_rendering_allowed",
    "evidence_validation_allowed",
    "delivery_authorization_allowed",
    "candidate_meaning_allowed",
    "selected_meaning_allowed",
    "concept_resolution_allowed",
    "predicate_authority_allowed",
    "participant_role_authority_allowed",
    "permission_inference_allowed",
    "capability_authority_allowed",
    "release_authorized",
    "production_ready",
)

_FIXTURE_TRUE_FIELDS = (
    "synthetic",
    "accepted_fixture",
    "explicit_invocation_only",
    "offline_only",
    "in_memory_only",
)

_FIXTURE_FALSE_FIELDS = (
    "external_context_required",
    "external_resource_allowed",
    "memory_allowed",
    "route_allowed",
    "action_allowed",
    "rendering_allowed",
    "delivery_allowed",
    "selected_meaning_allowed",
)

_RECEIPT_FALSE_FIELDS = (
    "stage_skipped",
    "interpretation_performed",
    "semantic_classification_performed",
    "core_rsoc_operator_application_performed",
    "selected_meaning_created",
    "evidence_validation_performed",
    "filesystem_search_performed",
    "filesystem_read_performed",
    "filesystem_write_performed",
    "repository_history_search_performed",
    "network_access_performed",
    "web_access_performed",
    "memory_read_performed",
    "memory_write_performed",
    "route_registration_performed",
    "capability_route_performed",
    "tool_activation_performed",
    "action_performed",
    "outward_rendering_performed",
    "delivery_authorized",
)

_RESULT_TRUE_FIELDS = (
    "disabled_by_default",
    "fixture_only",
    "offline_only",
    "standard_library_only",
    "deterministic",
    "read_only",
    "in_memory_only",
)

_RESULT_FALSE_FIELDS = (
    "raw_text_alone_activated",
    "hidden_fallback_parser_used",
    "conventional_nlp_authority_used",
    "external_linguistic_resource_loaded",
    "filesystem_search_performed",
    "filesystem_read_performed",
    "filesystem_write_performed",
    "repository_history_search_performed",
    "network_access_performed",
    "web_access_performed",
    "environment_lookup_performed",
    "memory_read_performed",
    "memory_write_performed",
    "protected_memory_retrieval_performed",
    "llm_used",
    "embedding_used",
    "vector_database_used",
    "semantic_similarity_used",
    "learned_parser_used",
    "neural_classifier_used",
    "rag_used",
    "api_route_activated",
    "capability_route_activated",
    "tool_activated",
    "action_executed",
    "outward_rendering_performed",
    "evidence_validation_performed",
    "candidate_meaning_created",
    "selected_meaning_created",
    "concept_resolved",
    "predicate_identity_created",
    "participant_roles_assigned",
    "permission_inferred",
    "capability_authorized",
    "delivery_authorized",
    "technical_acceptance_granted_by_runtime",
    "release_authorized",
    "production_ready",
)

_STAGE_ORDER = (
    BootstrapStage.INPUT_CUSTODY,
    BootstrapStage.SOURCE_FIELD_PROJECTION,
    BootstrapStage.OPERATOR_REGISTRY,
    BootstrapStage.OPERATOR_CANDIDATE_BINDING,
    BootstrapStage.PHASE_TRAIL_CONSTRUCTION,
    BootstrapStage.SCOPE_REFERENCE_CONSTRAINTS,
    BootstrapStage.STRUCTURAL_DERIVATION,
)


def _report(issues: list[ValidationIssue]) -> ValidationReport:
    return ValidationReport(
        schema_version=SLICE36H_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _require_contract_fields(record: object, issues: list[ValidationIssue]) -> None:
    if getattr(record, "schema_version", None) != SLICE36H_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if getattr(record, "spec_id", SLICE36H_SPEC_ID) != SLICE36H_SPEC_ID:
        issues.append(issue("spec_id", "spec_id_mismatch"))
    if getattr(record, "spec_version", SLICE36H_SPEC_VERSION) != SLICE36H_SPEC_VERSION:
        issues.append(issue("spec_version", "spec_version_mismatch"))


def validate_bounded_structural_bootstrap_state(
    record: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not BoundedStructuralBootstrapState:
        return _report([issue("state", "exact_state_type_required")])

    _require_contract_fields(record, issues)
    if record.state_id != record.expected_id():
        issues.append(issue("state_id", "stable_identifier_mismatch"))
    if record.enabled is not record.explicit_offline_developer_enable:
        issues.append(issue("enabled", "explicit_enable_state_mismatch"))
    for field_name in _STATE_TRUE_FIELDS:
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    for field_name in _STATE_FALSE_FIELDS:
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)
    return _report(issues)


def validate_bounded_structural_fixture(
    record: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not BoundedStructuralFixtureRecord:
        return _report([issue("fixture", "exact_fixture_type_required")])

    if record.schema_version != SLICE36H_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.fixture_id != record.expected_id():
        issues.append(issue("fixture_id", "stable_identifier_mismatch"))
    for field_name in (
        "fixture_name",
        "exact_source_text",
        "source_sha256",
        "source_id",
        "channel_id",
        "correlation_id",
        "expected_custody_status",
        "expected_projection_status",
        "expected_binding_status",
        "expected_phase_trail_status",
        "expected_constraint_status",
        "expected_structural_status",
    ):
        require_non_empty_text(
            field=field_name,
            value=getattr(record, field_name),
            issues=issues,
        )
    if type(record.sequence_number) is not int or record.sequence_number <= 0:
        issues.append(issue("sequence_number", "positive_integer_required"))
    if (
        type(record.expected_structural_candidate_count) is not int
        or record.expected_structural_candidate_count < 0
    ):
        issues.append(issue("expected_structural_candidate_count", "non_negative_integer_required"))
    require_unique_text_tuple(
        field="expected_non_progress_reasons",
        value=record.expected_non_progress_reasons,
        issues=issues,
    )
    require_unique_text_tuple(
        field="requested_context_dependencies",
        value=record.requested_context_dependencies,
        issues=issues,
        allow_empty=True,
    )
    try:
        expected_digest = source_sha256(record.exact_source_text)
    except UnicodeEncodeError:
        issues.append(issue("exact_source_text", "utf8_encodable_text_required"))
    else:
        if record.source_sha256 != expected_digest:
            issues.append(issue("source_sha256", "source_digest_mismatch"))
    for field_name in _FIXTURE_TRUE_FIELDS:
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    for field_name in _FIXTURE_FALSE_FIELDS:
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)
    return _report(issues)


def validate_bounded_structural_bootstrap_invocation(
    record: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not BoundedStructuralBootstrapInvocation:
        return _report([issue("invocation", "exact_invocation_type_required")])

    if record.schema_version != SLICE36H_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.invocation_id != record.expected_id():
        issues.append(issue("invocation_id", "stable_identifier_mismatch"))
    require_true(
        field="explicit_invocation",
        value=record.explicit_invocation,
        issues=issues,
    )
    require_false(
        field="raw_text_carried_by_invocation",
        value=record.raw_text_carried_by_invocation,
        issues=issues,
    )
    if record.requested_operation != "run_bounded_structural_analysis":
        issues.append(issue("requested_operation", "unsupported_operation"))

    if record.invocation_kind is BootstrapInvocationKind.SYNTHETIC_FIXTURE:
        require_non_empty_text(field="fixture_name", value=record.fixture_name, issues=issues)
        require_non_empty_text(field="fixture_id", value=record.fixture_id, issues=issues)
        if record.approved_caller_id:
            issues.append(issue("approved_caller_id", "fixture_invocation_must_not_name_caller"))
    elif record.invocation_kind is BootstrapInvocationKind.APPROVED_CALLER:
        require_non_empty_text(
            field="approved_caller_id",
            value=record.approved_caller_id,
            issues=issues,
        )
        if record.fixture_name or record.fixture_id:
            issues.append(issue("fixture_id", "approved_caller_invocation_must_not_name_fixture"))
    else:
        issues.append(issue("invocation_kind", "unsupported_invocation_kind"))
    return _report(issues)


def validate_bootstrap_stage_receipt(
    record: object,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not BootstrapStageReceipt:
        return _report([issue("stage_receipt", "exact_receipt_type_required")])

    _require_contract_fields(record, issues)
    if record.receipt_id != record.expected_id():
        issues.append(issue("receipt_id", "stable_identifier_mismatch"))
    if type(record.stage_ordinal) is not int or not 1 <= record.stage_ordinal <= len(_STAGE_ORDER):
        issues.append(issue("stage_ordinal", "stage_ordinal_out_of_range"))
    elif record.stage is not _STAGE_ORDER[record.stage_ordinal - 1]:
        issues.append(issue("stage", "stage_order_mismatch"))
    for field_name in (
        "invocation_id",
        "state_id",
        "reason_code",
        "predecessor_stage",
        "predecessor_record_id",
        "predecessor_schema_version",
        "predecessor_exact_type",
        "expected_predecessor_schema_version",
        "output_record_id",
        "output_schema_version",
        "output_exact_type",
        "source_event_id",
        "source_sha256",
    ):
        require_non_empty_text(field=field_name, value=getattr(record, field_name), issues=issues)
    require_unique_text_tuple(
        field="supporting_record_ids",
        value=record.supporting_record_ids,
        issues=issues,
        allow_empty=True,
    )
    for field_name in (
        "predecessor_identity_verified",
        "predecessor_version_verified",
        "output_validation_passed",
        "stage_completed",
        "source_ancestry_preserved",
    ):
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    if record.stage_status is not BootstrapStageStatus.COMPLETED:
        issues.append(issue("stage_status", "only_completed_receipts_may_be_persisted"))
    for field_name in _RECEIPT_FALSE_FIELDS:
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)
    return _report(issues)


def validate_slice36_rollback_metadata(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not Slice36RollbackMetadata:
        return _report([issue("rollback", "exact_rollback_type_required")])
    if record.schema_version != SLICE36H_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.rollback_id != record.expected_id():
        issues.append(issue("rollback_id", "stable_identifier_mismatch"))
    expected_values = {
        "pre_slice36_commit": PRE_SLICE36_COMMIT,
        "pre_slice36_tree": PRE_SLICE36_TREE,
        "accepted_parent_head": SLICE36G_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE36G_ACCEPTED_TREE,
        "expected_closeout_commit_subject": SLICE36H_COMMIT_SUBJECT,
    }
    for field_name, expected in expected_values.items():
        if getattr(record, field_name) != expected:
            issues.append(issue(field_name, "rollback_identity_mismatch"))
    for field_name in (
        "exact_commit_checkout_required",
        "exact_tree_match_required",
        "separate_recovery_clone_required",
        "git_object_verification_required",
        "rollback_proof_external_to_runtime",
    ):
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    for field_name in (
        "live_repository_mutation_authorized",
        "runtime_rollback_execution_authorized",
    ):
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)
    return _report(issues)


def validate_slice36_acceptance_record(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not Slice36AcceptanceRecord:
        return _report([issue("acceptance", "exact_acceptance_type_required")])
    _require_contract_fields(record, issues)
    if record.acceptance_record_id != record.expected_id():
        issues.append(issue("acceptance_record_id", "stable_identifier_mismatch"))
    if record.decision_owner != "Nicholas Jacob Bogaert / AI.Web":
        issues.append(issue("decision_owner", "decision_owner_mismatch"))
    expected_tuples = {
        "accepted_increment_labels": SLICE36_INCREMENT_LABELS,
        "accepted_chain": SLICE36_ACCEPTED_CHAIN,
        "permanent_boundaries": SLICE36_PERMANENT_BOUNDARIES,
        "mathematical_direction": SLICE36_MATHEMATICAL_DIRECTION,
        "accepted_scope": SLICE36_ACCEPTED_SCOPE,
        "deferred_scope": SLICE36_DEFERRED_SCOPE,
    }
    for field_name, expected in expected_tuples.items():
        if getattr(record, field_name) != expected:
            issues.append(issue(field_name, "acceptance_contract_mismatch"))
    expected_ids = {
        "accepted_parent_head": SLICE36G_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE36G_ACCEPTED_TREE,
        "pre_slice36_commit": PRE_SLICE36_COMMIT,
        "pre_slice36_tree": PRE_SLICE36_TREE,
    }
    for field_name, expected in expected_ids.items():
        if getattr(record, field_name) != expected:
            issues.append(issue(field_name, "acceptance_identity_mismatch"))
    require_non_empty_text(
        field="rollback_metadata_id",
        value=record.rollback_metadata_id,
        issues=issues,
    )
    for field_name in (
        "disabled_by_default",
        "explicitly_invoked_only",
        "offline_only",
        "deterministic",
        "source_preserving",
        "no_public_runtime_authority",
        "no_selected_meaning_authority",
        "no_action_authority",
        "no_delivery_authority",
        "decision_owner_acceptance_required",
    ):
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    for field_name in (
        "runtime_self_grants_acceptance",
        "release_authorized",
        "production_ready",
    ):
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)
    return _report(issues)


def validate_bootstrap_adapter_for_slice36h(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not BootstrapAdapterState:
        return _report([issue("adapter_state", "exact_adapter_state_type_required")])
    nested = validate_bootstrap_adapter_state(record)
    issues.extend(nested.issues)
    if not record.enabled or not record.explicit_offline_developer_enable:
        issues.append(issue("enabled", "explicit_offline_adapter_enable_required"))
    for field_name in (
        "fixture_only",
        "offline_only",
        "deterministic",
        "known_fixture_only",
        "disabled_by_default",
    ):
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    return _report(issues)


def validate_bounded_structural_bootstrap_result(
    record: object,
    *,
    invocation: object | None = None,
    fixture: object | None = None,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not BoundedStructuralBootstrapResult:
        return _report([issue("result", "exact_result_type_required")])

    _require_contract_fields(record, issues)
    if record.result_id != record.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))
    if record.stage_receipt_count != len(record.stage_receipts):
        issues.append(issue("stage_receipt_count", "stage_receipt_count_mismatch"))
    if record.completed_stage_count != sum(
        receipt.stage_completed for receipt in record.stage_receipts
    ):
        issues.append(issue("completed_stage_count", "completed_stage_count_mismatch"))
    if tuple(receipt.stage_ordinal for receipt in record.stage_receipts) != tuple(
        range(1, len(record.stage_receipts) + 1)
    ):
        issues.append(issue("stage_receipts", "stage_receipts_not_contiguous"))
    for index, receipt in enumerate(record.stage_receipts):
        nested = validate_bootstrap_stage_receipt(receipt)
        for nested_issue in nested.issues:
            issues.append(
                issue(
                    f"stage_receipts[{index}].{nested_issue.field}",
                    nested_issue.code,
                    nested_issue.detail,
                )
            )
        if receipt.invocation_id != record.invocation_id:
            issues.append(issue(f"stage_receipts[{index}].invocation_id", "invocation_reference_mismatch"))
        if receipt.state_id != record.state_id:
            issues.append(issue(f"stage_receipts[{index}].state_id", "state_reference_mismatch"))

    for field_name in _RESULT_TRUE_FIELDS:
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    for field_name in _RESULT_FALSE_FIELDS:
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)

    rollback_report = validate_slice36_rollback_metadata(record.rollback_metadata)
    acceptance_report = validate_slice36_acceptance_record(record.acceptance_record)
    for prefix, nested in (
        ("rollback_metadata", rollback_report),
        ("acceptance_record", acceptance_report),
    ):
        for nested_issue in nested.issues:
            issues.append(issue(f"{prefix}.{nested_issue.field}", nested_issue.code, nested_issue.detail))
    if record.acceptance_record.rollback_metadata_id != record.rollback_metadata.rollback_id:
        issues.append(issue("acceptance_record.rollback_metadata_id", "rollback_reference_mismatch"))

    if invocation is not None:
        invocation_report = validate_bounded_structural_bootstrap_invocation(invocation)
        for nested_issue in invocation_report.issues:
            issues.append(issue(f"invocation.{nested_issue.field}", nested_issue.code, nested_issue.detail))
        if type(invocation) is BoundedStructuralBootstrapInvocation:
            if record.invocation_id != invocation.invocation_id:
                issues.append(issue("invocation_id", "invocation_reference_mismatch"))
            if record.explicitly_invoked is not invocation.explicit_invocation:
                issues.append(issue("explicitly_invoked", "explicit_invocation_mismatch"))

    completed_statuses = {
        BootstrapIntegrationStatus.COMPLETED_STRUCTURAL_CANDIDATES,
        BootstrapIntegrationStatus.COMPLETED_LAWFUL_NON_PROGRESS,
    }
    if record.status in completed_statuses:
        if record.stage_receipt_count != len(_STAGE_ORDER):
            issues.append(issue("stage_receipts", "complete_run_requires_seven_stage_receipts"))
        if not record.exact_stage_chain_complete:
            issues.append(issue("exact_stage_chain_complete", "complete_run_requires_exact_chain"))
        if not record.no_stage_skipped:
            issues.append(issue("no_stage_skipped", "complete_run_requires_no_skips"))
        if not record.source_reconstruction_proven:
            issues.append(issue("source_reconstruction_proven", "complete_run_requires_reconstruction"))
        if not record.all_predecessor_records_exact:
            issues.append(issue("all_predecessor_records_exact", "complete_run_requires_exact_predecessors"))
        if not record.all_predecessor_versions_exact:
            issues.append(issue("all_predecessor_versions_exact", "complete_run_requires_exact_versions"))
        expected_types = (
            ("custody_result", InputEventCaptureResult),
            ("projection_result", SourceFieldProjectionResult),
            ("grammar_registry", SymbolicGrammarOperatorRegistry),
            ("binding_result", ResonantOperatorCandidateBindingResult),
            ("phase_trail_result", CandidateResonantPhaseTrailResult),
            ("constraint_result", ScopeAttachmentReferenceConstraintResult),
            ("structural_result", DeterministicStructuralDerivationResult),
        )
        for field_name, expected_type in expected_types:
            if type(getattr(record, field_name)) is not expected_type:
                issues.append(issue(field_name, "exact_completed_record_type_required"))

        if all(type(getattr(record, name)) is expected for name, expected in expected_types):
            custody = record.custody_result
            projection = record.projection_result
            registry = record.grammar_registry
            binding = record.binding_result
            trails = record.phase_trail_result
            constraints = record.constraint_result
            structural = record.structural_result
            assert custody is not None
            assert projection is not None
            assert registry is not None
            assert binding is not None
            assert trails is not None
            assert constraints is not None
            assert structural is not None

            reports = (
                ("custody_result", validate_input_event_capture_result(custody)),
                ("projection_result", validate_source_field_projection_result(projection)),
                ("grammar_registry", validate_symbolic_grammar_operator_registry(registry)),
                (
                    "binding_result",
                    validate_resonant_operator_candidate_binding_result(
                        binding,
                        projection,
                        registry,
                    ),
                ),
                (
                    "phase_trail_result",
                    validate_candidate_resonant_phase_trail_result(
                        trails,
                        projection,
                        binding,
                        registry,
                    ),
                ),
                (
                    "constraint_result",
                    validate_scope_attachment_reference_constraint_result(
                        constraints,
                        projection,
                        binding,
                        trails,
                    ),
                ),
                (
                    "structural_result",
                    validate_deterministic_structural_derivation_result(
                        structural,
                        custody,
                        projection,
                        binding,
                        trails,
                        constraints,
                    ),
                ),
            )
            for prefix, nested in reports:
                for nested_issue in nested.issues:
                    issues.append(issue(f"{prefix}.{nested_issue.field}", nested_issue.code, nested_issue.detail))

            structural_set = structural.structural_set
            if structural_set is None:
                issues.append(issue("structural_result", "structural_set_required"))
            else:
                if record.final_structural_candidate_count != structural_set.candidate_count:
                    issues.append(issue("final_structural_candidate_count", "candidate_count_mismatch"))
                expected_reasons = tuple(
                    reason.value for reason in structural_set.aggregate_non_progress_reasons
                )
                if record.final_non_progress_reasons != expected_reasons:
                    issues.append(issue("final_non_progress_reasons", "non_progress_reason_mismatch"))
                if record.source_reconstruction_proven is not structural_set.all_source_reconstruction_proven:
                    issues.append(issue("source_reconstruction_proven", "reconstruction_flag_mismatch"))

        if fixture is None or not is_exact_accepted_bounded_structural_fixture(fixture):
            issues.append(issue("fixture", "exact_accepted_fixture_required_for_completed_run"))
        elif type(fixture) is BoundedStructuralFixtureRecord:
            fixture_report = validate_bounded_structural_fixture(fixture)
            for nested_issue in fixture_report.issues:
                issues.append(issue(f"fixture.{nested_issue.field}", nested_issue.code, nested_issue.detail))
            if record.fixture_id != fixture.fixture_id:
                issues.append(issue("fixture_id", "fixture_reference_mismatch"))
            if record.source_sha256 != fixture.source_sha256:
                issues.append(issue("source_sha256", "fixture_source_digest_mismatch"))
            if record.final_structural_candidate_count != fixture.expected_structural_candidate_count:
                issues.append(issue("final_structural_candidate_count", "fixture_candidate_expectation_mismatch"))
            if record.final_non_progress_reasons != fixture.expected_non_progress_reasons:
                issues.append(issue("final_non_progress_reasons", "fixture_non_progress_expectation_mismatch"))

        if record.status is BootstrapIntegrationStatus.COMPLETED_LAWFUL_NON_PROGRESS:
            if record.final_structural_candidate_count != 0:
                issues.append(issue("status", "lawful_non_progress_completion_requires_zero_candidates"))
        elif record.final_structural_candidate_count <= 0:
            issues.append(issue("status", "structural_candidate_completion_requires_candidates"))
    else:
        if record.exact_stage_chain_complete:
            issues.append(issue("exact_stage_chain_complete", "held_or_refused_result_must_not_claim_complete_chain"))
        if record.stage_receipt_count == 0 and record.completed_stage_count != 0:
            issues.append(issue("completed_stage_count", "empty_stage_set_requires_zero_completed"))

    return _report(issues)


__all__ = (
    "validate_bootstrap_adapter_for_slice36h",
    "validate_bootstrap_stage_receipt",
    "validate_bounded_structural_bootstrap_invocation",
    "validate_bounded_structural_bootstrap_result",
    "validate_bounded_structural_bootstrap_state",
    "validate_bounded_structural_fixture",
    "validate_slice36_acceptance_record",
    "validate_slice36_rollback_metadata",
)
