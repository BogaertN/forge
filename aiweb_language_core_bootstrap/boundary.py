"""Isolated package-boundary record for Slice 30."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .authority import (
    BootstrapAuthorityState,
    build_bootstrap_authority_state,
    validate_bootstrap_authority_state,
)
from .component_registry import (
    ComponentRegistryRecord,
    build_component_registry_record,
    validate_component_registry_record,
)
from .import_policy import (
    ImportPolicyRecord,
    build_import_policy_record,
    validate_import_policy_record,
)
from .schema import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    stable_record_id,
)

PACKAGE_NAME = "aiweb_language_core_bootstrap"


@dataclass(frozen=True, slots=True)
class BootstrapBoundaryRecord:
    bootstrap_boundary_id: str
    package_name: str
    authority_state_id: str
    component_registry_id: str
    import_policy_id: str
    component_count: int
    boundary_kind: str
    integration_state: str
    runtime_effect: str
    dependency_effect: str
    existing_file_modification: bool
    component_loading: bool
    main_connection: bool
    route_connection: bool
    ui_connection: bool
    persistent_side_effect: bool
    schema_version: str = SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("bootstrap_boundary_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_boundary", self.canonical_body())


@dataclass(frozen=True, slots=True)
class BootstrapBoundaryBundle:
    authority: BootstrapAuthorityState
    registry: ComponentRegistryRecord
    import_policy: ImportPolicyRecord
    boundary: BootstrapBoundaryRecord


def build_bootstrap_boundary_record(
    *,
    authority: BootstrapAuthorityState,
    registry: ComponentRegistryRecord,
    import_policy: ImportPolicyRecord,
) -> BootstrapBoundaryRecord:
    body = {
        "package_name": PACKAGE_NAME,
        "authority_state_id": authority.authority_state_id,
        "component_registry_id": registry.registry_id,
        "import_policy_id": import_policy.import_policy_id,
        "component_count": registry.component_count,
        "boundary_kind": "isolated_language_core_package_boundary",
        "integration_state": "registered_not_loaded_disabled_offline",
        "runtime_effect": "none",
        "dependency_effect": "none",
        "existing_file_modification": False,
        "component_loading": False,
        "main_connection": False,
        "route_connection": False,
        "ui_connection": False,
        "persistent_side_effect": False,
        "schema_version": SCHEMA_VERSION,
    }
    return BootstrapBoundaryRecord(
        bootstrap_boundary_id=stable_record_id(
            "bootstrap_boundary",
            body,
        ),
        **body,
    )


def build_bootstrap_boundary_bundle() -> BootstrapBoundaryBundle:
    authority = build_bootstrap_authority_state()
    registry = build_component_registry_record()
    import_policy = build_import_policy_record()
    boundary = build_bootstrap_boundary_record(
        authority=authority,
        registry=registry,
        import_policy=import_policy,
    )
    return BootstrapBoundaryBundle(
        authority=authority,
        registry=registry,
        import_policy=import_policy,
        boundary=boundary,
    )


def validate_bootstrap_boundary_record(
    record: BootstrapBoundaryRecord,
    *,
    authority: BootstrapAuthorityState,
    registry: ComponentRegistryRecord,
    import_policy: ImportPolicyRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.package_name != PACKAGE_NAME:
        issues.append(issue("package_name", "package_name_mismatch"))
    if record.authority_state_id != authority.authority_state_id:
        issues.append(issue("authority_state_id", "authority_reference_mismatch"))
    if record.component_registry_id != registry.registry_id:
        issues.append(
            issue(
                "component_registry_id",
                "component_registry_reference_mismatch",
            )
        )
    if record.import_policy_id != import_policy.import_policy_id:
        issues.append(issue("import_policy_id", "import_policy_reference_mismatch"))
    if record.component_count != registry.component_count:
        issues.append(issue("component_count", "component_count_mismatch"))
    if record.boundary_kind != "isolated_language_core_package_boundary":
        issues.append(issue("boundary_kind", "boundary_kind_mismatch"))
    if record.integration_state != "registered_not_loaded_disabled_offline":
        issues.append(issue("integration_state", "integration_state_mismatch"))
    if record.runtime_effect != "none":
        issues.append(issue("runtime_effect", "runtime_effect_forbidden"))
    if record.dependency_effect != "none":
        issues.append(issue("dependency_effect", "dependency_effect_forbidden"))

    for field in (
        "existing_file_modification",
        "component_loading",
        "main_connection",
        "route_connection",
        "ui_connection",
        "persistent_side_effect",
    ):
        require_false(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    for report_name, report in (
        ("authority", validate_bootstrap_authority_state(authority)),
        ("registry", validate_component_registry_record(registry)),
        ("import_policy", validate_import_policy_record(import_policy)),
    ):
        for nested_issue in report.issues:
            issues.append(
                issue(
                    f"{report_name}.{nested_issue.field}",
                    nested_issue.code,
                    nested_issue.detail,
                )
            )

    if record.bootstrap_boundary_id != record.expected_id():
        issues.append(issue("bootstrap_boundary_id", "stable_identifier_mismatch"))

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )
