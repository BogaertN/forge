"""Typed records for the disabled-by-default Slice 31 bootstrap adapter.

This module is standard-library only. It creates deterministic in-memory test
records. It does not load registered components or create network, filesystem,
environment, route, UI, memory, evidence, delivery, tool, action, GP-014,
release, or production authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from ..schema import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    require_non_empty_text,
    require_true,
    require_unique_text_tuple,
    stable_record_id,
)

ADAPTER_SCHEMA_VERSION = "aiweb-language-core-bootstrap-adapter-v1"

STATUS_REFUSED_DISABLED = "refused_adapter_disabled"
STATUS_COMPLETED_INSPECTION = "completed_fixture_inspection"
STATUS_HELD_FIXTURE_NOT_ACCEPTED = "held_fixture_not_accepted"
STATUS_HELD_ADAPTER_MODE_MISMATCH = "held_adapter_mode_mismatch"
STATUS_HELD_INVALID_STATE = "held_invalid_adapter_state"
STATUS_HELD_INVALID_FIXTURE = "held_invalid_fixture"
STATUS_HELD_INVALID_BOUNDARY = "held_invalid_bootstrap_boundary"

MODE_DISABLED_DEFAULT = "disabled_default"
MODE_EXPLICIT_OFFLINE_FIXTURE = "explicit_offline_fixture"

OPERATION_PROBE_DISABLED = "probe_disabled_boundary"
OPERATION_INSPECT_BOUNDARY = "inspect_bootstrap_boundary"


@dataclass(frozen=True, slots=True)
class BootstrapAdapterState:
    adapter_state_id: str
    enabled: bool
    disabled_by_default: bool
    explicit_offline_developer_enable: bool
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    known_fixture_only: bool
    activation_mode: str
    arbitrary_input_allowed: bool
    external_file_input_allowed: bool
    component_loading_allowed: bool
    dynamic_loading_allowed: bool
    plugin_discovery_allowed: bool
    network_allowed: bool
    filesystem_read_allowed: bool
    filesystem_write_allowed: bool
    environment_lookup_allowed: bool
    runtime_connected: bool
    main_connected: bool
    route_connected: bool
    ui_connected: bool
    external_resource_allowed: bool
    memory_write_allowed: bool
    evidence_mutation_allowed: bool
    delivery_allowed: bool
    tool_routing_allowed: bool
    action_allowed: bool
    gp014_import_allowed: bool
    gp014_call_allowed: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = ADAPTER_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("adapter_state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_adapter_state", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FixtureProvenanceRecord:
    provenance_id: str
    source_class: str
    creator: str
    test_purpose: str
    expected_lawful_outcome: str
    prohibited_outcomes: tuple[str, ...]
    rights_status: str
    privacy_status: str
    external_resource_status: str
    data_safety_status: str
    synthetic: bool
    approved_document_derived: bool
    external_resource_derived: bool
    private_source_derived: bool
    trace_derived: bool
    memory_derived: bool
    generated: bool
    copied: bool
    transformed: bool
    redacted: bool
    paraphrased: bool
    public: bool
    internal_only: bool
    package_safe: bool
    redistribution_safe: bool
    runtime_prohibited: bool
    evidence: bool
    memory: bool
    runtime_corpus: bool
    production_data: bool
    external_resource_permission: bool
    public_output: bool
    contains_sensitive_data: bool
    contains_live_secret: bool
    contains_real_personal_data: bool
    contains_real_system_path: bool
    contains_executable_command: bool
    contains_tool_invocation: bool
    schema_version: str = ADAPTER_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("provenance_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_fixture_provenance", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BootstrapFixtureRecord:
    fixture_id: str
    fixture_name: str
    fixture_kind: str
    operation: str
    required_adapter_mode: str
    expected_result_status: str
    fixture_status: str
    provenance: FixtureProvenanceRecord
    schema_version: str = ADAPTER_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("fixture_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_fixture", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BootstrapFixtureObservation:
    observation_id: str
    fixture_id: str
    adapter_state_id: str
    bootstrap_schema_version: str
    bootstrap_boundary_id: str
    authority_state_id: str
    component_registry_id: str
    import_policy_id: str
    component_count: int
    boundary_kind: str
    integration_state: str
    registry_state: str
    runtime_effect: str
    dependency_effect: str
    adapter_enabled: bool
    component_loading_performed: bool
    runtime_connection_performed: bool
    persistent_side_effect_performed: bool
    schema_version: str = ADAPTER_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("observation_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_fixture_observation", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BootstrapAdapterResult:
    result_id: str
    fixture_id: str
    adapter_state_id: str
    status: str
    reason_code: str
    observation: BootstrapFixtureObservation | None
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    side_effects_performed: bool
    component_loading_performed: bool
    external_resource_used: bool
    memory_write_performed: bool
    evidence_mutation_performed: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    runtime_connection_performed: bool
    schema_version: str = ADAPTER_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_adapter_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_ADAPTER_FALSE_ONLY_FIELDS = (
    "arbitrary_input_allowed",
    "external_file_input_allowed",
    "component_loading_allowed",
    "dynamic_loading_allowed",
    "plugin_discovery_allowed",
    "network_allowed",
    "filesystem_read_allowed",
    "filesystem_write_allowed",
    "environment_lookup_allowed",
    "runtime_connected",
    "main_connected",
    "route_connected",
    "ui_connected",
    "external_resource_allowed",
    "memory_write_allowed",
    "evidence_mutation_allowed",
    "delivery_allowed",
    "tool_routing_allowed",
    "action_allowed",
    "gp014_import_allowed",
    "gp014_call_allowed",
    "production_ready",
    "release_authorized",
)

_PROVENANCE_FALSE_ONLY_FIELDS = (
    "approved_document_derived",
    "external_resource_derived",
    "private_source_derived",
    "trace_derived",
    "memory_derived",
    "copied",
    "transformed",
    "redacted",
    "paraphrased",
    "public",
    "evidence",
    "memory",
    "runtime_corpus",
    "production_data",
    "external_resource_permission",
    "public_output",
    "contains_sensitive_data",
    "contains_live_secret",
    "contains_real_personal_data",
    "contains_real_system_path",
    "contains_executable_command",
    "contains_tool_invocation",
)

_RESULT_FALSE_ONLY_FIELDS = (
    "side_effects_performed",
    "component_loading_performed",
    "external_resource_used",
    "memory_write_performed",
    "evidence_mutation_performed",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "runtime_connection_performed",
)


def build_bootstrap_adapter_state(
    *,
    explicit_offline_developer_enable: bool = False,
) -> BootstrapAdapterState:
    enabled = explicit_offline_developer_enable is True
    body = {
        "enabled": enabled,
        "disabled_by_default": True,
        "explicit_offline_developer_enable": enabled,
        "fixture_only": True,
        "offline_only": True,
        "deterministic": True,
        "known_fixture_only": True,
        "activation_mode": (
            MODE_EXPLICIT_OFFLINE_FIXTURE if enabled else MODE_DISABLED_DEFAULT
        ),
        "arbitrary_input_allowed": False,
        "external_file_input_allowed": False,
        "component_loading_allowed": False,
        "dynamic_loading_allowed": False,
        "plugin_discovery_allowed": False,
        "network_allowed": False,
        "filesystem_read_allowed": False,
        "filesystem_write_allowed": False,
        "environment_lookup_allowed": False,
        "runtime_connected": False,
        "main_connected": False,
        "route_connected": False,
        "ui_connected": False,
        "external_resource_allowed": False,
        "memory_write_allowed": False,
        "evidence_mutation_allowed": False,
        "delivery_allowed": False,
        "tool_routing_allowed": False,
        "action_allowed": False,
        "gp014_import_allowed": False,
        "gp014_call_allowed": False,
        "production_ready": False,
        "release_authorized": False,
        "schema_version": ADAPTER_SCHEMA_VERSION,
    }
    return BootstrapAdapterState(
        adapter_state_id=stable_record_id("bootstrap_adapter_state", body),
        **body,
    )


def build_synthetic_fixture_provenance(
    *,
    creator: str,
    test_purpose: str,
    expected_lawful_outcome: str,
    prohibited_outcomes: tuple[str, ...],
) -> FixtureProvenanceRecord:
    body = {
        "source_class": "synthetic",
        "creator": creator,
        "test_purpose": test_purpose,
        "expected_lawful_outcome": expected_lawful_outcome,
        "prohibited_outcomes": tuple(prohibited_outcomes),
        "rights_status": "forge_owned_synthetic",
        "privacy_status": "no_personal_or_private_data",
        "external_resource_status": "none",
        "data_safety_status": "safe_internal_synthetic_fixture",
        "synthetic": True,
        "approved_document_derived": False,
        "external_resource_derived": False,
        "private_source_derived": False,
        "trace_derived": False,
        "memory_derived": False,
        "generated": True,
        "copied": False,
        "transformed": False,
        "redacted": False,
        "paraphrased": False,
        "public": False,
        "internal_only": True,
        "package_safe": True,
        "redistribution_safe": True,
        "runtime_prohibited": True,
        "evidence": False,
        "memory": False,
        "runtime_corpus": False,
        "production_data": False,
        "external_resource_permission": False,
        "public_output": False,
        "contains_sensitive_data": False,
        "contains_live_secret": False,
        "contains_real_personal_data": False,
        "contains_real_system_path": False,
        "contains_executable_command": False,
        "contains_tool_invocation": False,
        "schema_version": ADAPTER_SCHEMA_VERSION,
    }
    return FixtureProvenanceRecord(
        provenance_id=stable_record_id("bootstrap_fixture_provenance", body),
        **body,
    )


def build_bootstrap_fixture_record(
    *,
    fixture_name: str,
    fixture_kind: str,
    operation: str,
    required_adapter_mode: str,
    expected_result_status: str,
    provenance: FixtureProvenanceRecord,
) -> BootstrapFixtureRecord:
    body = {
        "fixture_name": fixture_name,
        "fixture_kind": fixture_kind,
        "operation": operation,
        "required_adapter_mode": required_adapter_mode,
        "expected_result_status": expected_result_status,
        "fixture_status": "accepted_test_fixture",
        "provenance": provenance,
        "schema_version": ADAPTER_SCHEMA_VERSION,
    }
    return BootstrapFixtureRecord(
        fixture_id=stable_record_id("bootstrap_fixture", body),
        **body,
    )


def build_bootstrap_fixture_observation(
    *,
    fixture_id: str,
    adapter_state_id: str,
    bootstrap_schema_version: str,
    bootstrap_boundary_id: str,
    authority_state_id: str,
    component_registry_id: str,
    import_policy_id: str,
    component_count: int,
    boundary_kind: str,
    integration_state: str,
    registry_state: str,
    runtime_effect: str,
    dependency_effect: str,
    adapter_enabled: bool,
) -> BootstrapFixtureObservation:
    body = {
        "fixture_id": fixture_id,
        "adapter_state_id": adapter_state_id,
        "bootstrap_schema_version": bootstrap_schema_version,
        "bootstrap_boundary_id": bootstrap_boundary_id,
        "authority_state_id": authority_state_id,
        "component_registry_id": component_registry_id,
        "import_policy_id": import_policy_id,
        "component_count": component_count,
        "boundary_kind": boundary_kind,
        "integration_state": integration_state,
        "registry_state": registry_state,
        "runtime_effect": runtime_effect,
        "dependency_effect": dependency_effect,
        "adapter_enabled": adapter_enabled,
        "component_loading_performed": False,
        "runtime_connection_performed": False,
        "persistent_side_effect_performed": False,
        "schema_version": ADAPTER_SCHEMA_VERSION,
    }
    return BootstrapFixtureObservation(
        observation_id=stable_record_id("bootstrap_fixture_observation", body),
        **body,
    )


def build_bootstrap_adapter_result(
    *,
    fixture_id: str,
    adapter_state_id: str,
    status: str,
    reason_code: str,
    observation: BootstrapFixtureObservation | None = None,
) -> BootstrapAdapterResult:
    body = {
        "fixture_id": fixture_id,
        "adapter_state_id": adapter_state_id,
        "status": status,
        "reason_code": reason_code,
        "observation": observation,
        "fixture_only": True,
        "offline_only": True,
        "deterministic": True,
        "side_effects_performed": False,
        "component_loading_performed": False,
        "external_resource_used": False,
        "memory_write_performed": False,
        "evidence_mutation_performed": False,
        "delivery_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "runtime_connection_performed": False,
        "schema_version": ADAPTER_SCHEMA_VERSION,
    }
    return BootstrapAdapterResult(
        result_id=stable_record_id("bootstrap_adapter_result", body),
        **body,
    )


def validate_bootstrap_adapter_state(
    record: BootstrapAdapterState,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != ADAPTER_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_adapter_schema_version"))
    if record.adapter_state_id != record.expected_id():
        issues.append(issue("adapter_state_id", "stable_identifier_mismatch"))

    for field in (
        "disabled_by_default",
        "fixture_only",
        "offline_only",
        "deterministic",
        "known_fixture_only",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)

    for field in _ADAPTER_FALSE_ONLY_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)

    if record.enabled is not record.explicit_offline_developer_enable:
        issues.append(issue("enabled", "explicit_enable_state_mismatch"))

    expected_mode = (
        MODE_EXPLICIT_OFFLINE_FIXTURE
        if record.explicit_offline_developer_enable
        else MODE_DISABLED_DEFAULT
    )
    if record.activation_mode != expected_mode:
        issues.append(issue("activation_mode", "activation_mode_mismatch"))

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_fixture_provenance_record(
    record: FixtureProvenanceRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != ADAPTER_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_adapter_schema_version"))
    if record.provenance_id != record.expected_id():
        issues.append(issue("provenance_id", "stable_identifier_mismatch"))

    for field in (
        "source_class",
        "creator",
        "test_purpose",
        "expected_lawful_outcome",
        "rights_status",
        "privacy_status",
        "external_resource_status",
        "data_safety_status",
    ):
        require_non_empty_text(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    require_unique_text_tuple(
        field="prohibited_outcomes",
        value=record.prohibited_outcomes,
        issues=issues,
    )

    if record.source_class != "synthetic":
        issues.append(issue("source_class", "only_synthetic_fixture_allowed"))
    for field in (
        "synthetic",
        "generated",
        "internal_only",
        "package_safe",
        "redistribution_safe",
        "runtime_prohibited",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)

    for field in _PROVENANCE_FALSE_ONLY_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)

    if record.rights_status != "forge_owned_synthetic":
        issues.append(issue("rights_status", "rights_status_mismatch"))
    if record.privacy_status != "no_personal_or_private_data":
        issues.append(issue("privacy_status", "privacy_status_mismatch"))
    if record.external_resource_status != "none":
        issues.append(
            issue("external_resource_status", "external_resource_fixture_forbidden")
        )
    if record.data_safety_status != "safe_internal_synthetic_fixture":
        issues.append(issue("data_safety_status", "data_safety_status_mismatch"))

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_bootstrap_fixture_record(
    record: BootstrapFixtureRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != ADAPTER_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_adapter_schema_version"))
    if record.fixture_id != record.expected_id():
        issues.append(issue("fixture_id", "stable_identifier_mismatch"))

    for field in (
        "fixture_name",
        "fixture_kind",
        "operation",
        "required_adapter_mode",
        "expected_result_status",
        "fixture_status",
    ):
        require_non_empty_text(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    if record.operation not in (
        OPERATION_PROBE_DISABLED,
        OPERATION_INSPECT_BOUNDARY,
    ):
        issues.append(issue("operation", "unsupported_fixture_operation"))
    if record.required_adapter_mode not in (
        MODE_DISABLED_DEFAULT,
        MODE_EXPLICIT_OFFLINE_FIXTURE,
    ):
        issues.append(issue("required_adapter_mode", "unsupported_adapter_mode"))
    if record.fixture_status != "accepted_test_fixture":
        issues.append(issue("fixture_status", "fixture_not_accepted"))

    provenance_report = validate_fixture_provenance_record(record.provenance)
    for nested in provenance_report.issues:
        issues.append(
            issue(
                f"provenance.{nested.field}",
                nested.code,
                nested.detail,
            )
        )

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_bootstrap_fixture_observation(
    record: BootstrapFixtureObservation,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != ADAPTER_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_adapter_schema_version"))
    if record.observation_id != record.expected_id():
        issues.append(issue("observation_id", "stable_identifier_mismatch"))

    for field in (
        "fixture_id",
        "adapter_state_id",
        "bootstrap_schema_version",
        "bootstrap_boundary_id",
        "authority_state_id",
        "component_registry_id",
        "import_policy_id",
        "boundary_kind",
        "integration_state",
        "registry_state",
        "runtime_effect",
        "dependency_effect",
    ):
        require_non_empty_text(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    if record.component_count != 15:
        issues.append(issue("component_count", "component_count_mismatch"))
    require_true(
        field="adapter_enabled",
        value=record.adapter_enabled,
        issues=issues,
    )
    for field in (
        "component_loading_performed",
        "runtime_connection_performed",
        "persistent_side_effect_performed",
    ):
        require_false(field=field, value=getattr(record, field), issues=issues)

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_bootstrap_adapter_result(
    record: BootstrapAdapterResult,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != ADAPTER_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_adapter_schema_version"))
    if record.result_id != record.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))

    for field in (
        "fixture_id",
        "adapter_state_id",
        "status",
        "reason_code",
    ):
        require_non_empty_text(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    for field in (
        "fixture_only",
        "offline_only",
        "deterministic",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)

    for field in _RESULT_FALSE_ONLY_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)

    allowed_statuses = (
        STATUS_REFUSED_DISABLED,
        STATUS_COMPLETED_INSPECTION,
        STATUS_HELD_FIXTURE_NOT_ACCEPTED,
        STATUS_HELD_ADAPTER_MODE_MISMATCH,
        STATUS_HELD_INVALID_STATE,
        STATUS_HELD_INVALID_FIXTURE,
        STATUS_HELD_INVALID_BOUNDARY,
    )
    if record.status not in allowed_statuses:
        issues.append(issue("status", "unsupported_result_status"))

    if record.status == STATUS_COMPLETED_INSPECTION:
        if record.observation is None:
            issues.append(issue("observation", "completed_result_requires_observation"))
        else:
            observation_report = validate_bootstrap_fixture_observation(
                record.observation
            )
            for nested in observation_report.issues:
                issues.append(
                    issue(
                        f"observation.{nested.field}",
                        nested.code,
                        nested.detail,
                    )
                )
    elif record.observation is not None:
        issues.append(issue("observation", "noncompleted_result_forbids_observation"))

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )
