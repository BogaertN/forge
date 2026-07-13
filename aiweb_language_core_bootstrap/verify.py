"""In-memory verification for the isolated bootstrap boundary."""

from __future__ import annotations

from .boundary import (
    BootstrapBoundaryBundle,
    build_bootstrap_boundary_bundle,
    validate_bootstrap_boundary_record,
)
from .schema import SCHEMA_VERSION, ValidationIssue, ValidationReport, issue


def verify_bootstrap_boundary_bundle(
    bundle: BootstrapBoundaryBundle | None = None,
) -> ValidationReport:
    candidate = bundle or build_bootstrap_boundary_bundle()
    issues: list[ValidationIssue] = []

    boundary_report = validate_bootstrap_boundary_record(
        candidate.boundary,
        authority=candidate.authority,
        registry=candidate.registry,
        import_policy=candidate.import_policy,
    )
    issues.extend(boundary_report.issues)

    second = build_bootstrap_boundary_bundle()
    if candidate != second:
        issues.append(issue("bundle", "non_deterministic_bundle"))

    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )
