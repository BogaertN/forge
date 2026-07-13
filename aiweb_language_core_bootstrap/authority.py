"""Disabled authority-state record for the isolated bootstrap boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .schema import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    require_true,
    stable_record_id,
)


@dataclass(frozen=True, slots=True)
class BootstrapAuthorityState:
    authority_state_id: str
    enabled: bool
    disabled_by_default: bool
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    runtime_connected: bool
    components_loaded: bool
    main_registered: bool
    route_registered: bool
    ui_connected: bool
    network_allowed: bool
    filesystem_write_allowed: bool
    environment_selected_backend: bool
    dynamic_loading_allowed: bool
    external_resource_allowed: bool
    memory_write_allowed: bool
    evidence_mutation_allowed: bool
    delivery_allowed: bool
    tool_routing_allowed: bool
    action_allowed: bool
    gp014_imported: bool
    gp014_called: bool
    gp014_superseded: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("authority_state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("bootstrap_authority", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_FALSE_ONLY_FIELDS = (
    "enabled",
    "runtime_connected",
    "components_loaded",
    "main_registered",
    "route_registered",
    "ui_connected",
    "network_allowed",
    "filesystem_write_allowed",
    "environment_selected_backend",
    "dynamic_loading_allowed",
    "external_resource_allowed",
    "memory_write_allowed",
    "evidence_mutation_allowed",
    "delivery_allowed",
    "tool_routing_allowed",
    "action_allowed",
    "gp014_imported",
    "gp014_called",
    "gp014_superseded",
    "production_ready",
    "release_authorized",
)

_TRUE_ONLY_FIELDS = (
    "disabled_by_default",
    "fixture_only",
    "offline_only",
    "deterministic",
)


def build_bootstrap_authority_state() -> BootstrapAuthorityState:
    body = {
        "enabled": False,
        "disabled_by_default": True,
        "fixture_only": True,
        "offline_only": True,
        "deterministic": True,
        "runtime_connected": False,
        "components_loaded": False,
        "main_registered": False,
        "route_registered": False,
        "ui_connected": False,
        "network_allowed": False,
        "filesystem_write_allowed": False,
        "environment_selected_backend": False,
        "dynamic_loading_allowed": False,
        "external_resource_allowed": False,
        "memory_write_allowed": False,
        "evidence_mutation_allowed": False,
        "delivery_allowed": False,
        "tool_routing_allowed": False,
        "action_allowed": False,
        "gp014_imported": False,
        "gp014_called": False,
        "gp014_superseded": False,
        "production_ready": False,
        "release_authorized": False,
        "schema_version": SCHEMA_VERSION,
    }
    return BootstrapAuthorityState(
        authority_state_id=stable_record_id("bootstrap_authority", body),
        **body,
    )


def validate_bootstrap_authority_state(
    record: BootstrapAuthorityState,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    if record.schema_version != SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))

    if record.authority_state_id != record.expected_id():
        issues.append(issue("authority_state_id", "stable_identifier_mismatch"))

    for field in _FALSE_ONLY_FIELDS:
        require_false(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    for field in _TRUE_ONLY_FIELDS:
        require_true(
            field=field,
            value=getattr(record, field),
            issues=issues,
        )

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )
