"""Typed records for Slice 32 static component loading.

The records describe an explicit, offline, fixture-only import event. They do
not grant runtime, route, UI, memory, resource, delivery, tool, action, or
GP-014 authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

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

LOADING_SCHEMA_VERSION = "aiweb-language-core-component-loading-v1"

MODE_DISABLED_DEFAULT = "disabled_default"
MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING = "explicit_offline_component_loading"

STATUS_REFUSED_DISABLED = "refused_component_loading_disabled"
STATUS_HELD_INVALID_STATE = "held_invalid_component_loading_state"
STATUS_HELD_INVALID_FIXTURE = "held_invalid_component_loading_fixture"
STATUS_HELD_FIXTURE_NOT_ACCEPTED = "held_component_loading_fixture_not_accepted"
STATUS_HELD_BOUNDARY_INSPECTION_FAILED = "held_slice31_boundary_inspection_failed"
STATUS_HELD_PREEXISTING_UNREGISTERED_COMPONENT = (
    "held_preexisting_unregistered_project_component"
)
STATUS_HELD_STATIC_IMPORT_FAILED = "held_static_component_import_failed"
STATUS_HELD_INTERFACE_MISMATCH = "held_component_interface_mismatch"
STATUS_HELD_UNREGISTERED_COMPONENT = "held_unregistered_project_component"
STATUS_COMPLETED_STATIC_LOADING = "completed_static_component_loading"

OPERATION_LOAD_ACCEPTED_COMPONENTS = "load_accepted_boundary_components"


@dataclass(frozen=True, slots=True)
class ComponentLoadingState:
    loading_state_id: str
    enabled: bool
    activation_mode: str
    disabled_by_default: bool
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    static_allowlist_only: bool
    component_loading_authorized: bool
    python_module_import_read_only: bool
    dynamic_loading_allowed: bool
    plugin_discovery_allowed: bool
    hidden_fallback_allowed: bool
    environment_selected_backend: bool
    main_connection_allowed: bool
    route_connection_allowed: bool
    api_connection_allowed: bool
    ui_connection_allowed: bool
    network_allowed: bool
    external_data_filesystem_read_allowed: bool
    filesystem_write_allowed: bool
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
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("loading_state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_loading_state", self.canonical_body())


@dataclass(frozen=True, slots=True)
class ComponentLoadingFixtureRecord:
    fixture_id: str
    fixture_name: str
    operation: str
    required_activation_mode: str
    required_slice31_fixture_name: str
    expected_result_status: str
    synthetic: bool
    forge_owned: bool
    internal_only: bool
    fixture_only: bool
    offline_only: bool
    runtime_prohibited: bool
    evidence: bool
    memory: bool
    runtime_corpus: bool
    production_data: bool
    public_output: bool
    external_resource_derived: bool
    memory_derived: bool
    trace_derived: bool
    contains_real_personal_data: bool
    contains_live_secret: bool
    contains_executable_command: bool
    contains_tool_invocation: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("fixture_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_loading_fixture", self.canonical_body())


@dataclass(frozen=True, slots=True)
class ComponentInterfaceContract:
    interface_contract_id: str
    slice_ref: str
    component_registration_id: str
    package_name: str
    package_digest: str
    file_count: int
    accepted_scope: str
    expected_exports: tuple[str, ...]
    export_count: int
    export_digest: str
    static_import_required: bool
    component_invocation_allowed: bool
    verifier_invocation_allowed: bool
    runtime_authority_allowed: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("interface_contract_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_interface", self.canonical_body())


@dataclass(frozen=True, slots=True)
class LoadedComponentRecord:
    loaded_component_id: str
    interface_contract_id: str
    component_registration_id: str
    package_name: str
    module_name: str
    load_order: int
    export_count: int
    export_digest: str
    module_loaded: bool
    interface_verified: bool
    component_invoked: bool
    verifier_invoked: bool
    runtime_authority_granted: bool
    persistent_side_effect_performed: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("loaded_component_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("loaded_component", self.canonical_body())


@dataclass(frozen=True, slots=True)
class ComponentLoadingResult:
    loading_result_id: str
    fixture_id: str
    loading_state_id: str
    slice31_result_id: str
    bootstrap_boundary_id: str
    component_registry_id: str
    status: str
    reason_code: str
    loaded_components: tuple[LoadedComponentRecord, ...]
    loaded_component_count: int
    accepted_component_count: int
    failed_package_name: str
    unregistered_project_roots: tuple[str, ...]
    deterministic: bool
    fixture_only: bool
    offline_only: bool
    static_allowlist_only: bool
    dynamic_discovery_performed: bool
    hidden_fallback_used: bool
    component_invocation_performed: bool
    verifier_invocation_performed: bool
    runtime_connection_performed: bool
    network_access_performed: bool
    external_data_filesystem_read_performed: bool
    filesystem_write_performed: bool
    external_resource_used: bool
    memory_write_performed: bool
    evidence_mutation_performed: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    gp014_imported: bool
    gp014_called: bool
    persistent_side_effect_performed: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("loading_result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_loading_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_FALSE_ONLY_STATE_FIELDS = (
    "dynamic_loading_allowed",
    "plugin_discovery_allowed",
    "hidden_fallback_allowed",
    "environment_selected_backend",
    "main_connection_allowed",
    "route_connection_allowed",
    "api_connection_allowed",
    "ui_connection_allowed",
    "network_allowed",
    "external_data_filesystem_read_allowed",
    "filesystem_write_allowed",
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

_FALSE_ONLY_RESULT_FIELDS = (
    "dynamic_discovery_performed",
    "hidden_fallback_used",
    "component_invocation_performed",
    "verifier_invocation_performed",
    "runtime_connection_performed",
    "network_access_performed",
    "external_data_filesystem_read_performed",
    "filesystem_write_performed",
    "external_resource_used",
    "memory_write_performed",
    "evidence_mutation_performed",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "gp014_imported",
    "gp014_called",
    "persistent_side_effect_performed",
)


def build_component_loading_state(*, enabled: bool = False) -> ComponentLoadingState:
    body = {
        "enabled": enabled,
        "activation_mode": (
            MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING
            if enabled
            else MODE_DISABLED_DEFAULT
        ),
        "disabled_by_default": True,
        "fixture_only": True,
        "offline_only": True,
        "deterministic": True,
        "static_allowlist_only": True,
        "component_loading_authorized": enabled,
        "python_module_import_read_only": True,
        "dynamic_loading_allowed": False,
        "plugin_discovery_allowed": False,
        "hidden_fallback_allowed": False,
        "environment_selected_backend": False,
        "main_connection_allowed": False,
        "route_connection_allowed": False,
        "api_connection_allowed": False,
        "ui_connection_allowed": False,
        "network_allowed": False,
        "external_data_filesystem_read_allowed": False,
        "filesystem_write_allowed": False,
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
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return ComponentLoadingState(
        loading_state_id=stable_record_id("component_loading_state", body),
        **body,
    )


def build_component_loading_fixture_record(**values: object) -> ComponentLoadingFixtureRecord:
    body = dict(values)
    body["schema_version"] = LOADING_SCHEMA_VERSION
    return ComponentLoadingFixtureRecord(
        fixture_id=stable_record_id("component_loading_fixture", body),
        **body,
    )


def build_component_interface_contract(
    *,
    slice_ref: str,
    component_registration_id: str,
    package_name: str,
    package_digest: str,
    file_count: int,
    accepted_scope: str,
    expected_exports: tuple[str, ...],
    export_digest: str,
) -> ComponentInterfaceContract:
    body = {
        "slice_ref": slice_ref,
        "component_registration_id": component_registration_id,
        "package_name": package_name,
        "package_digest": package_digest,
        "file_count": file_count,
        "accepted_scope": accepted_scope,
        "expected_exports": expected_exports,
        "export_count": len(expected_exports),
        "export_digest": export_digest,
        "static_import_required": True,
        "component_invocation_allowed": False,
        "verifier_invocation_allowed": False,
        "runtime_authority_allowed": False,
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return ComponentInterfaceContract(
        interface_contract_id=stable_record_id("component_interface", body),
        **body,
    )


def build_loaded_component_record(
    *,
    contract: ComponentInterfaceContract,
    module_name: str,
    load_order: int,
) -> LoadedComponentRecord:
    body = {
        "interface_contract_id": contract.interface_contract_id,
        "component_registration_id": contract.component_registration_id,
        "package_name": contract.package_name,
        "module_name": module_name,
        "load_order": load_order,
        "export_count": contract.export_count,
        "export_digest": contract.export_digest,
        "module_loaded": True,
        "interface_verified": True,
        "component_invoked": False,
        "verifier_invoked": False,
        "runtime_authority_granted": False,
        "persistent_side_effect_performed": False,
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return LoadedComponentRecord(
        loaded_component_id=stable_record_id("loaded_component", body),
        **body,
    )


def build_component_loading_result(
    *,
    fixture_id: str,
    loading_state_id: str,
    status: str,
    reason_code: str,
    slice31_result_id: str = "",
    bootstrap_boundary_id: str = "",
    component_registry_id: str = "",
    loaded_components: tuple[LoadedComponentRecord, ...] = (),
    accepted_component_count: int = 15,
    failed_package_name: str = "",
    unregistered_project_roots: tuple[str, ...] = (),
) -> ComponentLoadingResult:
    body = {
        "fixture_id": fixture_id,
        "loading_state_id": loading_state_id,
        "slice31_result_id": slice31_result_id,
        "bootstrap_boundary_id": bootstrap_boundary_id,
        "component_registry_id": component_registry_id,
        "status": status,
        "reason_code": reason_code,
        "loaded_components": loaded_components,
        "loaded_component_count": len(loaded_components),
        "accepted_component_count": accepted_component_count,
        "failed_package_name": failed_package_name,
        "unregistered_project_roots": unregistered_project_roots,
        "deterministic": True,
        "fixture_only": True,
        "offline_only": True,
        "static_allowlist_only": True,
        "dynamic_discovery_performed": False,
        "hidden_fallback_used": False,
        "component_invocation_performed": False,
        "verifier_invocation_performed": False,
        "runtime_connection_performed": False,
        "network_access_performed": False,
        "external_data_filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "external_resource_used": False,
        "memory_write_performed": False,
        "evidence_mutation_performed": False,
        "delivery_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "gp014_imported": False,
        "gp014_called": False,
        "persistent_side_effect_performed": False,
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return ComponentLoadingResult(
        loading_result_id=stable_record_id("component_loading_result", body),
        **body,
    )


def validate_component_loading_state(record: ComponentLoadingState) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.activation_mode not in (
        MODE_DISABLED_DEFAULT,
        MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING,
    ):
        issues.append(issue("activation_mode", "unsupported_activation_mode"))
    if record.enabled != record.component_loading_authorized:
        issues.append(issue("component_loading_authorized", "state_mismatch"))
    if record.enabled and record.activation_mode != MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING:
        issues.append(issue("activation_mode", "enabled_mode_mismatch"))
    if not record.enabled and record.activation_mode != MODE_DISABLED_DEFAULT:
        issues.append(issue("activation_mode", "disabled_mode_mismatch"))
    for field in (
        "disabled_by_default",
        "fixture_only",
        "offline_only",
        "deterministic",
        "static_allowlist_only",
        "python_module_import_read_only",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in _FALSE_ONLY_STATE_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.loading_state_id != record.expected_id():
        issues.append(issue("loading_state_id", "stable_identifier_mismatch"))
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_component_loading_fixture_record(
    record: ComponentLoadingFixtureRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in (
        "fixture_name",
        "operation",
        "required_activation_mode",
        "required_slice31_fixture_name",
        "expected_result_status",
    ):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.operation != OPERATION_LOAD_ACCEPTED_COMPONENTS:
        issues.append(issue("operation", "unsupported_operation"))
    if record.required_activation_mode != MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING:
        issues.append(issue("required_activation_mode", "mode_mismatch"))
    if record.expected_result_status != STATUS_COMPLETED_STATIC_LOADING:
        issues.append(issue("expected_result_status", "status_mismatch"))
    for field in (
        "synthetic",
        "forge_owned",
        "internal_only",
        "fixture_only",
        "offline_only",
        "runtime_prohibited",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in (
        "evidence",
        "memory",
        "runtime_corpus",
        "production_data",
        "public_output",
        "external_resource_derived",
        "memory_derived",
        "trace_derived",
        "contains_real_personal_data",
        "contains_live_secret",
        "contains_executable_command",
        "contains_tool_invocation",
    ):
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.fixture_id != record.expected_id():
        issues.append(issue("fixture_id", "stable_identifier_mismatch"))
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_component_interface_contract(
    record: ComponentInterfaceContract,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in (
        "slice_ref",
        "component_registration_id",
        "package_name",
        "package_digest",
        "accepted_scope",
        "export_digest",
    ):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    require_unique_text_tuple(
        field="expected_exports",
        value=record.expected_exports,
        issues=issues,
    )
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.file_count <= 0:
        issues.append(issue("file_count", "required_positive_integer"))
    if record.export_count != len(record.expected_exports):
        issues.append(issue("export_count", "export_count_mismatch"))
    if len(record.package_digest) != 64 or any(c not in "0123456789abcdef" for c in record.package_digest):
        issues.append(issue("package_digest", "invalid_sha256"))
    if len(record.export_digest) != 64 or any(c not in "0123456789abcdef" for c in record.export_digest):
        issues.append(issue("export_digest", "invalid_sha256"))
    require_true(
        field="static_import_required",
        value=record.static_import_required,
        issues=issues,
    )
    for field in (
        "component_invocation_allowed",
        "verifier_invocation_allowed",
        "runtime_authority_allowed",
    ):
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.interface_contract_id != record.expected_id():
        issues.append(issue("interface_contract_id", "stable_identifier_mismatch"))
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_loaded_component_record(record: LoadedComponentRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in (
        "interface_contract_id",
        "component_registration_id",
        "package_name",
        "module_name",
        "export_digest",
    ):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.load_order <= 0:
        issues.append(issue("load_order", "required_positive_integer"))
    if record.export_count <= 0:
        issues.append(issue("export_count", "required_positive_integer"))
    for field in ("module_loaded", "interface_verified"):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in (
        "component_invoked",
        "verifier_invoked",
        "runtime_authority_granted",
        "persistent_side_effect_performed",
    ):
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.package_name != record.module_name:
        issues.append(issue("module_name", "module_name_mismatch"))
    if record.loaded_component_id != record.expected_id():
        issues.append(issue("loaded_component_id", "stable_identifier_mismatch"))
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_component_loading_result(record: ComponentLoadingResult) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in ("fixture_id", "loading_state_id", "status", "reason_code"):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.loaded_component_count != len(record.loaded_components):
        issues.append(issue("loaded_component_count", "count_mismatch"))
    if record.accepted_component_count != 15:
        issues.append(issue("accepted_component_count", "accepted_count_mismatch"))
    for field in ("deterministic", "fixture_only", "offline_only", "static_allowlist_only"):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in _FALSE_ONLY_RESULT_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)
    require_unique_text_tuple(
        field="unregistered_project_roots",
        value=record.unregistered_project_roots,
        issues=issues,
        allow_empty=True,
    )
    for loaded in record.loaded_components:
        report = validate_loaded_component_record(loaded)
        for nested in report.issues:
            issues.append(issue(f"loaded.{loaded.package_name}.{nested.field}", nested.code, nested.detail))
    if record.status == STATUS_COMPLETED_STATIC_LOADING:
        if record.loaded_component_count != record.accepted_component_count:
            issues.append(issue("loaded_component_count", "completion_count_mismatch"))
        if not record.slice31_result_id or not record.bootstrap_boundary_id or not record.component_registry_id:
            issues.append(issue("references", "completion_references_required"))
        if record.failed_package_name or record.unregistered_project_roots:
            issues.append(issue("completion", "failure_fields_must_be_empty"))
    elif record.loaded_component_count:
        issues.append(issue("loaded_components", "noncompletion_must_not_claim_loaded_components"))
    if record.loading_result_id != record.expected_id():
        issues.append(issue("loading_result_id", "stable_identifier_mismatch"))
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))
