"""Immutable records for Slice 33 deterministic trace and receipt assembly.

The records in this module are in-memory, standard-library-only structures.
They do not write files, persist memory, mutate evidence, use a network,
register routes, connect UI, invoke tools, execute actions, call GP-014, or
create runtime authority.
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
    require_unique_text_tuple,
    stable_record_id,
)

TRACE_RECEIPT_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-deterministic-trace-receipt-v1"
)

MODE_DISABLED_DEFAULT: Final[str] = "disabled_default"
MODE_EXPLICIT_OFFLINE_TRACE_RECEIPT: Final[str] = (
    "explicit_offline_trace_receipt"
)

STATUS_REFUSED_DISABLED: Final[str] = (
    "refused_trace_receipt_assembly_disabled"
)
STATUS_COMPLETED: Final[str] = "completed_trace_receipt_assembly"
STATUS_HELD_INVALID_STATE: Final[str] = "held_invalid_trace_receipt_state"
STATUS_HELD_UNKNOWN_FLOW: Final[str] = "held_unknown_trace_receipt_flow"
STATUS_HELD_SOURCE_RESULT_MISMATCH: Final[str] = (
    "held_source_result_identity_mismatch"
)
STATUS_HELD_TRACE_MISMATCH: Final[str] = "held_derivation_trace_identity_mismatch"
STATUS_HELD_RECEIPT_MISMATCH: Final[str] = (
    "held_derivation_receipt_identity_mismatch"
)

VERDICT_LAWFUL_REFUSAL: Final[str] = "PASS_LAWFUL_REFUSAL"
VERDICT_COMPLETED_READ_ONLY_FLOW: Final[str] = (
    "PASS_COMPLETED_READ_ONLY_FLOW"
)

ASSEMBLY_DISABLED_REASON: Final[str] = (
    "explicit_offline_trace_receipt_enable_required"
)
ASSEMBLY_COMPLETED_REASON: Final[str] = (
    "exact_source_flow_trace_and_receipt_assembled"
)

ALLOWED_SOURCE_SLICES: Final[tuple[str, ...]] = ("Slice 31", "Slice 32")
ALLOWED_OUTCOMES: Final[tuple[str, ...]] = (
    "lawful_refusal",
    "completed_read_only_flow",
)
ALLOWED_STEP_DECISIONS: Final[tuple[str, ...]] = (
    "selected",
    "verified",
    "refused",
    "completed",
)
ALLOWED_STEP_KINDS: Final[tuple[str, ...]] = (
    "flow_spec_selected",
    "assembly_state_verified",
    "fixture_identity_verified",
    "source_state_identity_verified",
    "source_result_executed",
    "source_result_identity_verified",
    "lawful_refusal_verified",
    "observation_identity_verified",
    "slice31_prerequisite_verified",
    "bootstrap_lineage_verified",
    "loaded_component_set_verified",
    "negative_authority_verified",
)


@dataclass(frozen=True, slots=True)
class TraceReceiptAssemblyState:
    assembly_state_id: str
    enabled: bool
    disabled_by_default: bool
    explicit_offline_developer_enable: bool
    activation_mode: str
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    read_only: bool
    exact_flow_catalog_only: bool
    source_result_execution_allowed: bool
    persistent_trace_write_allowed: bool
    persistent_receipt_write_allowed: bool
    filesystem_read_allowed: bool
    filesystem_write_allowed: bool
    network_allowed: bool
    environment_lookup_allowed: bool
    main_connection_allowed: bool
    ask_forge_connection_allowed: bool
    route_connection_allowed: bool
    api_connection_allowed: bool
    ui_connection_allowed: bool
    memory_write_allowed: bool
    evidence_mutation_allowed: bool
    external_resource_allowed: bool
    delivery_allowed: bool
    tool_routing_allowed: bool
    action_allowed: bool
    component_invocation_allowed: bool
    component_verifier_invocation_allowed: bool
    gp014_import_allowed: bool
    gp014_call_allowed: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = TRACE_RECEIPT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("assembly_state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("trace_receipt_assembly_state", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AcceptedTraceFlowSpec:
    flow_spec_id: str
    flow_name: str
    source_slice: str
    source_enabled: bool
    fixture_name: str
    fixture_id: str
    source_state_id: str
    expected_source_status: str
    expected_source_reason_code: str
    expected_source_result_id: str
    expected_observation_id: str
    expected_authority_state_id: str
    expected_import_policy_id: str
    expected_bootstrap_boundary_id: str
    expected_component_registry_id: str
    expected_loaded_package_names: tuple[str, ...]
    expected_loaded_component_ids: tuple[str, ...]
    expected_loaded_component_count: int
    expected_lawful_outcome: str
    expected_receipt_verdict: str
    schema_version: str = TRACE_RECEIPT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("flow_spec_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("trace_flow_spec", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DerivationTraceStep:
    step_id: str
    step_index: int
    step_kind: str
    source_slice: str
    input_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    decision: str
    reason_code: str
    identity_verified: bool
    read_only: bool
    persistent_side_effect_performed: bool
    schema_version: str = TRACE_RECEIPT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("step_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("derivation_trace_step", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DerivationTraceRecord:
    trace_id: str
    flow_spec_id: str
    flow_name: str
    assembly_state_id: str
    source_slice: str
    source_fixture_id: str
    source_state_id: str
    source_result_id: str
    source_status: str
    source_reason_code: str
    observation_id: str
    authority_state_id: str
    import_policy_id: str
    bootstrap_boundary_id: str
    component_registry_id: str
    loaded_package_names: tuple[str, ...]
    loaded_component_ids: tuple[str, ...]
    loaded_component_count: int
    loaded_component_set_digest: str
    steps: tuple[DerivationTraceStep, ...]
    step_id_digest: str
    trace_complete: bool
    exact_identity_bound: bool
    read_only: bool
    fixture_only: bool
    offline_only: bool
    persistent_trace_write_performed: bool
    persistent_receipt_write_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    memory_write_performed: bool
    evidence_mutation_performed: bool
    external_resource_used: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    component_invocation_performed: bool
    component_verifier_invocation_performed: bool
    gp014_imported: bool
    gp014_called: bool
    runtime_connection_performed: bool
    schema_version: str = TRACE_RECEIPT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("trace_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("derivation_trace", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DerivationReceiptRecord:
    receipt_id: str
    trace_id: str
    flow_spec_id: str
    flow_name: str
    verdict: str
    source_slice: str
    source_fixture_id: str
    source_state_id: str
    source_result_id: str
    source_status: str
    source_reason_code: str
    observation_id: str
    bootstrap_boundary_id: str
    component_registry_id: str
    loaded_component_count: int
    loaded_component_set_digest: str
    step_id_digest: str
    source_version_refs: tuple[str, ...]
    exact_identity_bound: bool
    trace_complete: bool
    source_result_validated: bool
    lawful_refusal_accepted: bool
    completed_flow_accepted: bool
    read_only: bool
    fixture_only: bool
    offline_only: bool
    authority_granted: bool
    acceptance_widened: bool
    persistent_trace_write_performed: bool
    persistent_receipt_write_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    memory_write_performed: bool
    evidence_mutation_performed: bool
    external_resource_used: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    component_invocation_performed: bool
    component_verifier_invocation_performed: bool
    gp014_imported: bool
    gp014_called: bool
    runtime_connection_performed: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = TRACE_RECEIPT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("receipt_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("derivation_receipt", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TraceReceiptAssemblyResult:
    assembly_result_id: str
    flow_spec_id: str
    flow_name: str
    assembly_state_id: str
    status: str
    reason_code: str
    trace: DerivationTraceRecord | None
    receipt: DerivationReceiptRecord | None
    deterministic: bool
    fixture_only: bool
    offline_only: bool
    read_only: bool
    persistent_side_effect_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    memory_write_performed: bool
    evidence_mutation_performed: bool
    external_resource_used: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    component_invocation_performed: bool
    component_verifier_invocation_performed: bool
    gp014_imported: bool
    gp014_called: bool
    runtime_connection_performed: bool
    schema_version: str = TRACE_RECEIPT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("assembly_result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("trace_receipt_assembly_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_STATE_FALSE_FIELDS: Final[tuple[str, ...]] = (
    "persistent_trace_write_allowed",
    "persistent_receipt_write_allowed",
    "filesystem_read_allowed",
    "filesystem_write_allowed",
    "network_allowed",
    "environment_lookup_allowed",
    "main_connection_allowed",
    "ask_forge_connection_allowed",
    "route_connection_allowed",
    "api_connection_allowed",
    "ui_connection_allowed",
    "memory_write_allowed",
    "evidence_mutation_allowed",
    "external_resource_allowed",
    "delivery_allowed",
    "tool_routing_allowed",
    "action_allowed",
    "component_invocation_allowed",
    "component_verifier_invocation_allowed",
    "gp014_import_allowed",
    "gp014_call_allowed",
    "production_ready",
    "release_authorized",
)

_TRACE_FALSE_FIELDS: Final[tuple[str, ...]] = (
    "persistent_trace_write_performed",
    "persistent_receipt_write_performed",
    "filesystem_write_performed",
    "network_access_performed",
    "memory_write_performed",
    "evidence_mutation_performed",
    "external_resource_used",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "component_invocation_performed",
    "component_verifier_invocation_performed",
    "gp014_imported",
    "gp014_called",
    "runtime_connection_performed",
)

_RECEIPT_FALSE_FIELDS: Final[tuple[str, ...]] = (
    "authority_granted",
    "acceptance_widened",
    "persistent_trace_write_performed",
    "persistent_receipt_write_performed",
    "filesystem_write_performed",
    "network_access_performed",
    "memory_write_performed",
    "evidence_mutation_performed",
    "external_resource_used",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "component_invocation_performed",
    "component_verifier_invocation_performed",
    "gp014_imported",
    "gp014_called",
    "runtime_connection_performed",
    "production_ready",
    "release_authorized",
)

_RESULT_FALSE_FIELDS: Final[tuple[str, ...]] = (
    "persistent_side_effect_performed",
    "filesystem_write_performed",
    "network_access_performed",
    "memory_write_performed",
    "evidence_mutation_performed",
    "external_resource_used",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "component_invocation_performed",
    "component_verifier_invocation_performed",
    "gp014_imported",
    "gp014_called",
    "runtime_connection_performed",
)


def build_trace_receipt_assembly_state(
    *,
    explicit_offline_developer_enable: bool = False,
) -> TraceReceiptAssemblyState:
    enabled = explicit_offline_developer_enable is True
    body = {
        "enabled": enabled,
        "disabled_by_default": True,
        "explicit_offline_developer_enable": enabled,
        "activation_mode": (
            MODE_EXPLICIT_OFFLINE_TRACE_RECEIPT
            if enabled
            else MODE_DISABLED_DEFAULT
        ),
        "fixture_only": True,
        "offline_only": True,
        "deterministic": True,
        "read_only": True,
        "exact_flow_catalog_only": True,
        "source_result_execution_allowed": enabled,
        "persistent_trace_write_allowed": False,
        "persistent_receipt_write_allowed": False,
        "filesystem_read_allowed": False,
        "filesystem_write_allowed": False,
        "network_allowed": False,
        "environment_lookup_allowed": False,
        "main_connection_allowed": False,
        "ask_forge_connection_allowed": False,
        "route_connection_allowed": False,
        "api_connection_allowed": False,
        "ui_connection_allowed": False,
        "memory_write_allowed": False,
        "evidence_mutation_allowed": False,
        "external_resource_allowed": False,
        "delivery_allowed": False,
        "tool_routing_allowed": False,
        "action_allowed": False,
        "component_invocation_allowed": False,
        "component_verifier_invocation_allowed": False,
        "gp014_import_allowed": False,
        "gp014_call_allowed": False,
        "production_ready": False,
        "release_authorized": False,
        "schema_version": TRACE_RECEIPT_SCHEMA_VERSION,
    }
    return TraceReceiptAssemblyState(
        assembly_state_id=stable_record_id("trace_receipt_assembly_state", body),
        **body,
    )


def build_trace_flow_spec(**values: object) -> AcceptedTraceFlowSpec:
    body = dict(values)
    body["schema_version"] = TRACE_RECEIPT_SCHEMA_VERSION
    return AcceptedTraceFlowSpec(
        flow_spec_id=stable_record_id("trace_flow_spec", body),
        **body,
    )


def build_derivation_trace_step(**values: object) -> DerivationTraceStep:
    body = dict(values)
    body["schema_version"] = TRACE_RECEIPT_SCHEMA_VERSION
    return DerivationTraceStep(
        step_id=stable_record_id("derivation_trace_step", body),
        **body,
    )


def build_derivation_trace_record(**values: object) -> DerivationTraceRecord:
    body = dict(values)
    body["schema_version"] = TRACE_RECEIPT_SCHEMA_VERSION
    return DerivationTraceRecord(
        trace_id=stable_record_id("derivation_trace", body),
        **body,
    )


def build_derivation_receipt_record(**values: object) -> DerivationReceiptRecord:
    body = dict(values)
    body["schema_version"] = TRACE_RECEIPT_SCHEMA_VERSION
    return DerivationReceiptRecord(
        receipt_id=stable_record_id("derivation_receipt", body),
        **body,
    )


def build_trace_receipt_assembly_result(**values: object) -> TraceReceiptAssemblyResult:
    body = dict(values)
    body["schema_version"] = TRACE_RECEIPT_SCHEMA_VERSION
    return TraceReceiptAssemblyResult(
        assembly_result_id=stable_record_id("trace_receipt_assembly_result", body),
        **body,
    )


def _report(issues: list[ValidationIssue]) -> ValidationReport:
    return ValidationReport(
        schema_version=TRACE_RECEIPT_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_trace_receipt_assembly_state(
    record: TraceReceiptAssemblyState,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != TRACE_RECEIPT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "schema_version_mismatch"))
    if record.assembly_state_id != record.expected_id():
        issues.append(issue("assembly_state_id", "stable_id_mismatch"))
    require_true(field="disabled_by_default", value=record.disabled_by_default, issues=issues)
    require_true(field="fixture_only", value=record.fixture_only, issues=issues)
    require_true(field="offline_only", value=record.offline_only, issues=issues)
    require_true(field="deterministic", value=record.deterministic, issues=issues)
    require_true(field="read_only", value=record.read_only, issues=issues)
    require_true(
        field="exact_flow_catalog_only",
        value=record.exact_flow_catalog_only,
        issues=issues,
    )
    for field in _STATE_FALSE_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.enabled:
        if record.activation_mode != MODE_EXPLICIT_OFFLINE_TRACE_RECEIPT:
            issues.append(issue("activation_mode", "enabled_mode_mismatch"))
        require_true(
            field="explicit_offline_developer_enable",
            value=record.explicit_offline_developer_enable,
            issues=issues,
        )
        require_true(
            field="source_result_execution_allowed",
            value=record.source_result_execution_allowed,
            issues=issues,
        )
    else:
        if record.activation_mode != MODE_DISABLED_DEFAULT:
            issues.append(issue("activation_mode", "disabled_mode_mismatch"))
        require_false(
            field="explicit_offline_developer_enable",
            value=record.explicit_offline_developer_enable,
            issues=issues,
        )
        require_false(
            field="source_result_execution_allowed",
            value=record.source_result_execution_allowed,
            issues=issues,
        )
    expected = build_trace_receipt_assembly_state(
        explicit_offline_developer_enable=record.enabled,
    )
    if record != expected:
        issues.append(issue("assembly_state", "accepted_state_identity_mismatch"))
    return _report(issues)


def validate_trace_flow_spec(record: AcceptedTraceFlowSpec) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != TRACE_RECEIPT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "schema_version_mismatch"))
    if record.flow_spec_id != record.expected_id():
        issues.append(issue("flow_spec_id", "stable_id_mismatch"))
    require_non_empty_text(field="flow_name", value=record.flow_name, issues=issues)
    if record.source_slice not in ALLOWED_SOURCE_SLICES:
        issues.append(issue("source_slice", "source_slice_not_allowed"))
    require_non_empty_text(field="fixture_name", value=record.fixture_name, issues=issues)
    require_non_empty_text(field="fixture_id", value=record.fixture_id, issues=issues)
    require_non_empty_text(field="source_state_id", value=record.source_state_id, issues=issues)
    require_non_empty_text(
        field="expected_source_status",
        value=record.expected_source_status,
        issues=issues,
    )
    require_non_empty_text(
        field="expected_source_reason_code",
        value=record.expected_source_reason_code,
        issues=issues,
    )
    require_non_empty_text(
        field="expected_source_result_id",
        value=record.expected_source_result_id,
        issues=issues,
    )
    if record.expected_lawful_outcome not in ALLOWED_OUTCOMES:
        issues.append(issue("expected_lawful_outcome", "outcome_not_allowed"))
    if record.expected_receipt_verdict not in (
        VERDICT_LAWFUL_REFUSAL,
        VERDICT_COMPLETED_READ_ONLY_FLOW,
    ):
        issues.append(issue("expected_receipt_verdict", "verdict_not_allowed"))
    if record.expected_loaded_component_count != len(record.expected_loaded_component_ids):
        issues.append(issue("expected_loaded_component_count", "count_mismatch"))
    if len(record.expected_loaded_package_names) != len(record.expected_loaded_component_ids):
        issues.append(issue("expected_loaded_package_names", "identity_count_mismatch"))
    require_unique_text_tuple(
        field="expected_loaded_package_names",
        value=record.expected_loaded_package_names,
        issues=issues,
        allow_empty=True,
    )
    require_unique_text_tuple(
        field="expected_loaded_component_ids",
        value=record.expected_loaded_component_ids,
        issues=issues,
        allow_empty=True,
    )
    from .flow_catalog import get_trace_flow

    accepted = get_trace_flow(record.flow_name)
    if accepted is None or record != accepted:
        issues.append(issue("flow_spec", "unaccepted_trace_flow_identity"))
    return _report(issues)


def validate_derivation_trace_step(record: DerivationTraceStep) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != TRACE_RECEIPT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "schema_version_mismatch"))
    if record.step_id != record.expected_id():
        issues.append(issue("step_id", "stable_id_mismatch"))
    if record.step_index < 1:
        issues.append(issue("step_index", "must_be_positive"))
    if record.step_kind not in ALLOWED_STEP_KINDS:
        issues.append(issue("step_kind", "step_kind_not_allowed"))
    if record.source_slice not in ALLOWED_SOURCE_SLICES:
        issues.append(issue("source_slice", "source_slice_not_allowed"))
    require_unique_text_tuple(
        field="input_refs",
        value=record.input_refs,
        issues=issues,
        allow_empty=True,
    )
    require_unique_text_tuple(
        field="output_refs",
        value=record.output_refs,
        issues=issues,
        allow_empty=True,
    )
    if record.decision not in ALLOWED_STEP_DECISIONS:
        issues.append(issue("decision", "decision_not_allowed"))
    require_non_empty_text(field="reason_code", value=record.reason_code, issues=issues)
    require_true(field="identity_verified", value=record.identity_verified, issues=issues)
    require_true(field="read_only", value=record.read_only, issues=issues)
    require_false(
        field="persistent_side_effect_performed",
        value=record.persistent_side_effect_performed,
        issues=issues,
    )
    return _report(issues)


def validate_derivation_trace_record(
    record: DerivationTraceRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != TRACE_RECEIPT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "schema_version_mismatch"))
    if record.trace_id != record.expected_id():
        issues.append(issue("trace_id", "stable_id_mismatch"))
    for index, step in enumerate(record.steps, start=1):
        report = validate_derivation_trace_step(step)
        if not report.ok:
            issues.append(issue(f"steps[{index}]", "invalid_step"))
        if step.step_index != index:
            issues.append(issue(f"steps[{index}].step_index", "step_order_mismatch"))
    step_ids = tuple(step.step_id for step in record.steps)
    if len(step_ids) != len(set(step_ids)):
        issues.append(issue("steps", "duplicate_step_ids"))
    require_true(field="trace_complete", value=record.trace_complete, issues=issues)
    require_true(field="exact_identity_bound", value=record.exact_identity_bound, issues=issues)
    require_true(field="read_only", value=record.read_only, issues=issues)
    require_true(field="fixture_only", value=record.fixture_only, issues=issues)
    require_true(field="offline_only", value=record.offline_only, issues=issues)
    for field in _TRACE_FALSE_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)
    from .flow_catalog import (
        EXACT_ENABLED_ASSEMBLY_STATE_ID,
        build_expected_trace,
        get_trace_flow,
    )

    spec = get_trace_flow(record.flow_name)
    if spec is None:
        issues.append(issue("flow_name", "unknown_trace_flow"))
    else:
        if record.assembly_state_id != EXACT_ENABLED_ASSEMBLY_STATE_ID:
            issues.append(issue("assembly_state_id", "accepted_enabled_state_mismatch"))
        expected = build_expected_trace(
            spec,
            assembly_state_id=EXACT_ENABLED_ASSEMBLY_STATE_ID,
        )
        if record != expected:
            issues.append(issue("trace", "accepted_trace_identity_mismatch"))
    return _report(issues)


def validate_derivation_receipt_record(
    record: DerivationReceiptRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != TRACE_RECEIPT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "schema_version_mismatch"))
    if record.receipt_id != record.expected_id():
        issues.append(issue("receipt_id", "stable_id_mismatch"))
    require_true(field="exact_identity_bound", value=record.exact_identity_bound, issues=issues)
    require_true(field="trace_complete", value=record.trace_complete, issues=issues)
    require_true(
        field="source_result_validated",
        value=record.source_result_validated,
        issues=issues,
    )
    require_true(field="read_only", value=record.read_only, issues=issues)
    require_true(field="fixture_only", value=record.fixture_only, issues=issues)
    require_true(field="offline_only", value=record.offline_only, issues=issues)
    require_unique_text_tuple(
        field="source_version_refs",
        value=record.source_version_refs,
        issues=issues,
    )
    for field in _RECEIPT_FALSE_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)
    from .flow_catalog import build_expected_receipt, get_trace_flow

    spec = get_trace_flow(record.flow_name)
    if spec is None:
        issues.append(issue("flow_name", "unknown_trace_flow"))
    else:
        expected = build_expected_receipt(spec)
        if record != expected:
            issues.append(issue("receipt", "accepted_receipt_identity_mismatch"))
    return _report(issues)


def validate_trace_receipt_assembly_result(
    record: TraceReceiptAssemblyResult,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != TRACE_RECEIPT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "schema_version_mismatch"))
    if record.assembly_result_id != record.expected_id():
        issues.append(issue("assembly_result_id", "stable_id_mismatch"))
    require_true(field="deterministic", value=record.deterministic, issues=issues)
    require_true(field="fixture_only", value=record.fixture_only, issues=issues)
    require_true(field="offline_only", value=record.offline_only, issues=issues)
    require_true(field="read_only", value=record.read_only, issues=issues)
    for field in _RESULT_FALSE_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)

    from .flow_catalog import (
        build_expected_receipt,
        build_expected_trace,
        get_trace_flow,
    )

    spec = get_trace_flow(record.flow_name)
    if spec is None:
        if (
            record.status == STATUS_HELD_UNKNOWN_FLOW
            and record.reason_code == "flow_not_in_exact_static_catalog"
            and record.flow_spec_id == ""
            and record.trace is None
            and record.receipt is None
        ):
            require_non_empty_text(
                field="flow_name",
                value=record.flow_name,
                issues=issues,
            )
            return _report(issues)
        issues.append(issue("flow_spec_id", "unaccepted_trace_flow_identity"))
        return _report(issues)
    if spec.flow_spec_id != record.flow_spec_id:
        issues.append(issue("flow_spec_id", "unaccepted_trace_flow_identity"))
        return _report(issues)

    enabled_state = build_trace_receipt_assembly_state(
        explicit_offline_developer_enable=True,
    )
    disabled_state = build_trace_receipt_assembly_state(
        explicit_offline_developer_enable=False,
    )

    held_reasons = {
        STATUS_HELD_INVALID_STATE:
            "trace_receipt_assembly_state_validation_failed",
        STATUS_HELD_SOURCE_RESULT_MISMATCH:
            "source_fixture_flow_did_not_match_accepted_identity",
        STATUS_HELD_TRACE_MISMATCH:
            "assembled_trace_did_not_match_accepted_identity",
        STATUS_HELD_RECEIPT_MISMATCH:
            "assembled_receipt_did_not_match_accepted_identity",
    }
    if record.status in held_reasons:
        if record.reason_code != held_reasons[record.status]:
            issues.append(issue("reason_code", "held_reason_mismatch"))
        if record.trace is not None or record.receipt is not None:
            issues.append(issue("trace_receipt", "held_result_must_not_contain_proof"))
        if record.status != STATUS_HELD_INVALID_STATE and (
            record.assembly_state_id != enabled_state.assembly_state_id
        ):
            issues.append(issue("assembly_state_id", "held_enabled_state_mismatch"))
        return _report(issues)

    if record.assembly_state_id == disabled_state.assembly_state_id:
        expected = build_trace_receipt_assembly_result(
            flow_spec_id=spec.flow_spec_id,
            flow_name=spec.flow_name,
            assembly_state_id=disabled_state.assembly_state_id,
            status=STATUS_REFUSED_DISABLED,
            reason_code=ASSEMBLY_DISABLED_REASON,
            trace=None,
            receipt=None,
            deterministic=True,
            fixture_only=True,
            offline_only=True,
            read_only=True,
            persistent_side_effect_performed=False,
            filesystem_write_performed=False,
            network_access_performed=False,
            memory_write_performed=False,
            evidence_mutation_performed=False,
            external_resource_used=False,
            delivery_performed=False,
            tool_routing_performed=False,
            action_performed=False,
            component_invocation_performed=False,
            component_verifier_invocation_performed=False,
            gp014_imported=False,
            gp014_called=False,
            runtime_connection_performed=False,
        )
        if record != expected:
            issues.append(issue("result", "accepted_disabled_result_identity_mismatch"))
        return _report(issues)

    if record.assembly_state_id != enabled_state.assembly_state_id:
        issues.append(issue("assembly_state_id", "unaccepted_assembly_state_identity"))
        return _report(issues)

    if record.status != STATUS_COMPLETED or record.reason_code != ASSEMBLY_COMPLETED_REASON:
        issues.append(issue("status", "completed_result_status_mismatch"))
    if record.trace is None:
        issues.append(issue("trace", "completed_result_requires_trace"))
        return _report(issues)
    if record.receipt is None:
        issues.append(issue("receipt", "completed_result_requires_receipt"))
        return _report(issues)

    trace_report = validate_derivation_trace_record(record.trace)
    if not trace_report.ok:
        issues.append(issue("trace", "invalid_derivation_trace"))
    receipt_report = validate_derivation_receipt_record(record.receipt)
    if not receipt_report.ok:
        issues.append(issue("receipt", "invalid_derivation_receipt"))

    expected_trace = build_expected_trace(
        spec,
        assembly_state_id=enabled_state.assembly_state_id,
    )
    expected_receipt = build_expected_receipt(spec)
    expected = build_trace_receipt_assembly_result(
        flow_spec_id=spec.flow_spec_id,
        flow_name=spec.flow_name,
        assembly_state_id=enabled_state.assembly_state_id,
        status=STATUS_COMPLETED,
        reason_code=ASSEMBLY_COMPLETED_REASON,
        trace=expected_trace,
        receipt=expected_receipt,
        deterministic=True,
        fixture_only=True,
        offline_only=True,
        read_only=True,
        persistent_side_effect_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        memory_write_performed=False,
        evidence_mutation_performed=False,
        external_resource_used=False,
        delivery_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        component_invocation_performed=False,
        component_verifier_invocation_performed=False,
        gp014_imported=False,
        gp014_called=False,
        runtime_connection_performed=False,
    )
    if record != expected:
        issues.append(issue("result", "accepted_completed_result_identity_mismatch"))
    return _report(issues)
