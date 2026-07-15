"""Immutable records for Slice 34 bootstrap containment evaluation.

These records describe a read-only in-memory containment proof. They do not run
full regression, write evidence, create rollback commits, or grant technical
acceptance. Those consequential proof steps remain installer/verifier duties.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final

from ..schema import (
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    require_non_empty_text,
    require_true,
    stable_record_id,
)
from .policy import (
    FLOW_IDENTITY_EXPECTATIONS,
    MODE_DISABLED_DEFAULT,
    MODE_EXPLICIT_OFFLINE_CONTAINMENT,
    ONE_COMMAND_ROLLBACK_REQUIRED,
    REASON_COMPLETED,
    REASON_DISABLED,
    REQUIRED_CONTAINMENT_GUARDS,
    REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT,
    REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT,
    REQUIRED_PRIOR_COMMAND_COUNT,
    SLICE34_SCHEMA_VERSION,
    STATUS_COMPLETED,
    STATUS_HELD_FLOW_MISMATCH,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
)


@dataclass(frozen=True, slots=True)
class BootstrapContainmentState:
    state_id: str
    enabled: bool
    disabled_by_default: bool
    explicit_offline_developer_enable: bool
    activation_mode: str
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    read_only: bool
    exact_flow_catalog_only: bool
    full_regression_execution_allowed: bool
    rollback_execution_allowed: bool
    filesystem_write_allowed: bool
    network_allowed: bool
    environment_lookup_allowed: bool
    runtime_memory_write_allowed: bool
    evidence_mutation_allowed: bool
    external_resource_ingestion_allowed: bool
    component_invocation_allowed: bool
    component_verifier_invocation_allowed: bool
    gp014_import_allowed: bool
    gp014_call_allowed: bool
    delivery_allowed: bool
    tool_routing_allowed: bool
    action_allowed: bool
    route_connection_allowed: bool
    api_connection_allowed: bool
    ui_connection_allowed: bool
    llm_authority_allowed: bool
    vector_authority_allowed: bool
    embedding_authority_allowed: bool
    rag_authority_allowed: bool
    chroma_authority_allowed: bool
    qwen_authority_allowed: bool
    ollama_authority_allowed: bool
    general_language_claim_allowed: bool
    technical_acceptance_grant_allowed: bool
    release_authorized: bool
    production_ready: bool
    schema_version: str = SLICE34_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_containment_state", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FlowContainmentProof:
    proof_id: str
    flow_name: str
    flow_spec_id: str
    assembly_result_id: str
    trace_id: str
    receipt_id: str
    verdict: str
    loaded_component_count: int
    loaded_component_set_digest: str
    source_result_validated: bool
    deterministic: bool
    fixture_only: bool
    offline_only: bool
    read_only: bool
    persistent_side_effect_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    runtime_memory_write_performed: bool
    evidence_mutation_performed: bool
    external_resource_used: bool
    component_invocation_performed: bool
    component_verifier_invocation_performed: bool
    gp014_imported: bool
    gp014_called: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    runtime_connection_performed: bool
    exact_identity_match: bool
    schema_version: str = SLICE34_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("proof_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_flow_containment_proof", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BootstrapContainmentEvaluation:
    evaluation_id: str
    state_id: str
    status: str
    reason_code: str
    flow_proofs: tuple[FlowContainmentProof, ...]
    required_flow_count: int
    validated_flow_count: int
    containment_guard_ids: tuple[str, ...]
    runtime_containment_passed: bool
    inherited_regression_required: bool
    inherited_regression_command_count: int
    phase_b_preservation_required: bool
    phase_b_preservation_command_count: int
    total_prior_command_count: int
    inherited_regression_executed_by_runtime: bool
    phase_b_preservation_executed_by_runtime: bool
    one_command_rollback_required: bool
    rollback_executed_by_runtime: bool
    technical_acceptance_granted: bool
    acceptance_widened: bool
    general_language_claim_made: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    runtime_memory_write_performed: bool
    evidence_mutation_performed: bool
    external_resource_used: bool
    component_invocation_performed: bool
    component_verifier_invocation_performed: bool
    gp014_imported: bool
    gp014_called: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    runtime_connection_performed: bool
    release_authorized: bool
    production_ready: bool
    schema_version: str = SLICE34_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("evaluation_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "bootstrap_containment_evaluation", self.canonical_body()
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_bootstrap_containment_state(
    *, explicit_offline_developer_enable: bool = False
) -> BootstrapContainmentState:
    enabled = explicit_offline_developer_enable is True
    body = {
        "enabled": enabled,
        "disabled_by_default": True,
        "explicit_offline_developer_enable": enabled,
        "activation_mode": (
            MODE_EXPLICIT_OFFLINE_CONTAINMENT if enabled else MODE_DISABLED_DEFAULT
        ),
        "fixture_only": True,
        "offline_only": True,
        "deterministic": True,
        "read_only": True,
        "exact_flow_catalog_only": True,
        "full_regression_execution_allowed": False,
        "rollback_execution_allowed": False,
        "filesystem_write_allowed": False,
        "network_allowed": False,
        "environment_lookup_allowed": False,
        "runtime_memory_write_allowed": False,
        "evidence_mutation_allowed": False,
        "external_resource_ingestion_allowed": False,
        "component_invocation_allowed": False,
        "component_verifier_invocation_allowed": False,
        "gp014_import_allowed": False,
        "gp014_call_allowed": False,
        "delivery_allowed": False,
        "tool_routing_allowed": False,
        "action_allowed": False,
        "route_connection_allowed": False,
        "api_connection_allowed": False,
        "ui_connection_allowed": False,
        "llm_authority_allowed": False,
        "vector_authority_allowed": False,
        "embedding_authority_allowed": False,
        "rag_authority_allowed": False,
        "chroma_authority_allowed": False,
        "qwen_authority_allowed": False,
        "ollama_authority_allowed": False,
        "general_language_claim_allowed": False,
        "technical_acceptance_grant_allowed": False,
        "release_authorized": False,
        "production_ready": False,
        "schema_version": SLICE34_SCHEMA_VERSION,
    }
    return BootstrapContainmentState(
        state_id=stable_record_id("bootstrap_containment_state", body), **body
    )


def build_flow_containment_proof(**values: object) -> FlowContainmentProof:
    body = dict(values)
    body["schema_version"] = SLICE34_SCHEMA_VERSION
    return FlowContainmentProof(
        proof_id=stable_record_id("bootstrap_flow_containment_proof", body),
        **body,
    )


def build_bootstrap_containment_evaluation(**values: object) -> BootstrapContainmentEvaluation:
    body = dict(values)
    body["schema_version"] = SLICE34_SCHEMA_VERSION
    return BootstrapContainmentEvaluation(
        evaluation_id=stable_record_id("bootstrap_containment_evaluation", body),
        **body,
    )


def _report(issues: list[ValidationIssue]) -> ValidationReport:
    return ValidationReport(
        schema_version=SLICE34_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_bootstrap_containment_state(
    state: BootstrapContainmentState,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if state.schema_version != SLICE34_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unexpected_schema_version"))
    if state.state_id != state.expected_id():
        issues.append(issue("state_id", "identity_mismatch"))
    require_true(field="disabled_by_default", value=state.disabled_by_default, issues=issues)
    require_true(field="fixture_only", value=state.fixture_only, issues=issues)
    require_true(field="offline_only", value=state.offline_only, issues=issues)
    require_true(field="deterministic", value=state.deterministic, issues=issues)
    require_true(field="read_only", value=state.read_only, issues=issues)
    require_true(field="exact_flow_catalog_only", value=state.exact_flow_catalog_only, issues=issues)
    expected_mode = MODE_EXPLICIT_OFFLINE_CONTAINMENT if state.enabled else MODE_DISABLED_DEFAULT
    if state.activation_mode != expected_mode:
        issues.append(issue("activation_mode", "mode_enablement_mismatch"))
    if state.explicit_offline_developer_enable is not state.enabled:
        issues.append(issue("explicit_offline_developer_enable", "enablement_mismatch"))
    false_fields = (
        "full_regression_execution_allowed", "rollback_execution_allowed",
        "filesystem_write_allowed", "network_allowed", "environment_lookup_allowed",
        "runtime_memory_write_allowed", "evidence_mutation_allowed",
        "external_resource_ingestion_allowed", "component_invocation_allowed",
        "component_verifier_invocation_allowed", "gp014_import_allowed",
        "gp014_call_allowed", "delivery_allowed", "tool_routing_allowed",
        "action_allowed", "route_connection_allowed", "api_connection_allowed",
        "ui_connection_allowed", "llm_authority_allowed", "vector_authority_allowed",
        "embedding_authority_allowed", "rag_authority_allowed", "chroma_authority_allowed",
        "qwen_authority_allowed", "ollama_authority_allowed",
        "general_language_claim_allowed", "technical_acceptance_grant_allowed",
        "release_authorized", "production_ready",
    )
    for field in false_fields:
        require_false(field=field, value=getattr(state, field), issues=issues)
    return _report(issues)


def validate_flow_containment_proof(proof: FlowContainmentProof) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if proof.schema_version != SLICE34_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unexpected_schema_version"))
    if proof.proof_id != proof.expected_id():
        issues.append(issue("proof_id", "identity_mismatch"))
    require_non_empty_text(field="flow_name", value=proof.flow_name, issues=issues)
    expected = next(
        (item for item in FLOW_IDENTITY_EXPECTATIONS if item.flow_name == proof.flow_name),
        None,
    )
    if expected is None:
        issues.append(issue("flow_name", "flow_not_in_exact_catalog"))
    else:
        exact_values = {
            "flow_spec_id": expected.flow_spec_id,
            "assembly_result_id": expected.assembly_result_id,
            "trace_id": expected.trace_id,
            "receipt_id": expected.receipt_id,
            "verdict": expected.verdict,
            "loaded_component_count": expected.loaded_component_count,
            "loaded_component_set_digest": expected.loaded_component_set_digest,
        }
        for field, expected_value in exact_values.items():
            if getattr(proof, field) != expected_value:
                issues.append(issue(field, "exact_accepted_identity_mismatch"))
    for field in (
        "source_result_validated", "deterministic", "fixture_only", "offline_only",
        "read_only", "exact_identity_match",
    ):
        require_true(field=field, value=getattr(proof, field), issues=issues)
    for field in (
        "persistent_side_effect_performed", "filesystem_write_performed",
        "network_access_performed", "runtime_memory_write_performed",
        "evidence_mutation_performed", "external_resource_used",
        "component_invocation_performed", "component_verifier_invocation_performed",
        "gp014_imported", "gp014_called", "delivery_performed",
        "tool_routing_performed", "action_performed", "runtime_connection_performed",
    ):
        require_false(field=field, value=getattr(proof, field), issues=issues)
    return _report(issues)


def validate_bootstrap_containment_evaluation(
    evaluation: BootstrapContainmentEvaluation,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if evaluation.schema_version != SLICE34_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unexpected_schema_version"))
    if evaluation.evaluation_id != evaluation.expected_id():
        issues.append(issue("evaluation_id", "identity_mismatch"))
    require_non_empty_text(field="state_id", value=evaluation.state_id, issues=issues)
    expected_names = tuple(item.flow_name for item in FLOW_IDENTITY_EXPECTATIONS)
    actual_names = tuple(proof.flow_name for proof in evaluation.flow_proofs)
    if evaluation.status == STATUS_REFUSED_DISABLED:
        if evaluation.reason_code != REASON_DISABLED:
            issues.append(issue("reason_code", "disabled_reason_mismatch"))
        if evaluation.flow_proofs:
            issues.append(issue("flow_proofs", "disabled_evaluation_must_be_empty"))
        require_false(
            field="runtime_containment_passed",
            value=evaluation.runtime_containment_passed,
            issues=issues,
        )
    elif evaluation.status == STATUS_COMPLETED:
        if evaluation.reason_code != REASON_COMPLETED:
            issues.append(issue("reason_code", "completed_reason_mismatch"))
        if actual_names != expected_names:
            issues.append(issue("flow_proofs", "exact_flow_order_mismatch"))
        for index, proof in enumerate(evaluation.flow_proofs):
            report = validate_flow_containment_proof(proof)
            for item in report.issues:
                issues.append(issue(f"flow_proofs[{index}].{item.field}", item.code, item.detail))
        require_true(
            field="runtime_containment_passed",
            value=evaluation.runtime_containment_passed,
            issues=issues,
        )
    elif evaluation.status in {STATUS_HELD_INVALID_STATE, STATUS_HELD_FLOW_MISMATCH}:
        require_false(
            field="runtime_containment_passed",
            value=evaluation.runtime_containment_passed,
            issues=issues,
        )
    else:
        issues.append(issue("status", "unexpected_status"))
    if evaluation.required_flow_count != len(FLOW_IDENTITY_EXPECTATIONS):
        issues.append(issue("required_flow_count", "required_flow_count_mismatch"))
    if evaluation.validated_flow_count != len(evaluation.flow_proofs):
        issues.append(issue("validated_flow_count", "validated_flow_count_mismatch"))
    if evaluation.containment_guard_ids != REQUIRED_CONTAINMENT_GUARDS:
        issues.append(issue("containment_guard_ids", "exact_guard_catalog_mismatch"))
    require_true(
        field="inherited_regression_required",
        value=evaluation.inherited_regression_required,
        issues=issues,
    )
    require_true(
        field="phase_b_preservation_required",
        value=evaluation.phase_b_preservation_required,
        issues=issues,
    )
    if evaluation.inherited_regression_command_count != REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT:
        issues.append(issue("inherited_regression_command_count", "command_count_mismatch"))
    if evaluation.phase_b_preservation_command_count != REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT:
        issues.append(issue("phase_b_preservation_command_count", "command_count_mismatch"))
    if evaluation.total_prior_command_count != REQUIRED_PRIOR_COMMAND_COUNT:
        issues.append(issue("total_prior_command_count", "command_count_mismatch"))
    if evaluation.one_command_rollback_required is not ONE_COMMAND_ROLLBACK_REQUIRED:
        issues.append(issue("one_command_rollback_required", "rollback_requirement_mismatch"))
    for field in (
        "inherited_regression_executed_by_runtime",
        "phase_b_preservation_executed_by_runtime",
        "rollback_executed_by_runtime", "technical_acceptance_granted",
        "acceptance_widened", "general_language_claim_made",
        "filesystem_write_performed", "network_access_performed",
        "runtime_memory_write_performed", "evidence_mutation_performed",
        "external_resource_used", "component_invocation_performed",
        "component_verifier_invocation_performed", "gp014_imported", "gp014_called",
        "delivery_performed", "tool_routing_performed", "action_performed",
        "runtime_connection_performed", "release_authorized", "production_ready",
    ):
        require_false(field=field, value=getattr(evaluation, field), issues=issues)
    return _report(issues)
