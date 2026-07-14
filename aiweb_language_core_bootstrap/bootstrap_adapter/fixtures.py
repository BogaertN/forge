"""Governed synthetic fixture catalog for the Slice 31 adapter."""

from __future__ import annotations

from .schema import (
    MODE_DISABLED_DEFAULT,
    MODE_EXPLICIT_OFFLINE_FIXTURE,
    OPERATION_INSPECT_BOUNDARY,
    OPERATION_PROBE_DISABLED,
    STATUS_COMPLETED_INSPECTION,
    STATUS_REFUSED_DISABLED,
    BootstrapFixtureRecord,
    build_bootstrap_fixture_record,
    build_synthetic_fixture_provenance,
)

FIXTURE_DISABLED_DEFAULT = "slice31-disabled-default-probe-v1"
FIXTURE_EXPLICIT_OFFLINE_INSPECTION = (
    "slice31-explicit-offline-boundary-inspection-v1"
)


def _build_disabled_default_fixture() -> BootstrapFixtureRecord:
    provenance = build_synthetic_fixture_provenance(
        creator="AI.Web Slice 31 governed fixture builder",
        test_purpose=(
            "Prove that the bootstrap adapter refuses operation while in its "
            "default disabled state."
        ),
        expected_lawful_outcome=STATUS_REFUSED_DISABLED,
        prohibited_outcomes=(
            "component_loading",
            "runtime_connection",
            "network_access",
            "filesystem_access",
            "memory_write",
            "evidence_mutation",
            "delivery",
            "tool_routing",
            "action",
        ),
    )
    return build_bootstrap_fixture_record(
        fixture_name=FIXTURE_DISABLED_DEFAULT,
        fixture_kind="synthetic_disabled_default_probe",
        operation=OPERATION_PROBE_DISABLED,
        required_adapter_mode=MODE_DISABLED_DEFAULT,
        expected_result_status=STATUS_REFUSED_DISABLED,
        provenance=provenance,
    )


def _build_explicit_offline_fixture() -> BootstrapFixtureRecord:
    provenance = build_synthetic_fixture_provenance(
        creator="AI.Web Slice 31 governed fixture builder",
        test_purpose=(
            "Inspect the inert Slice 30 bootstrap boundary through an explicit "
            "offline fixture-only adapter without loading a component."
        ),
        expected_lawful_outcome=STATUS_COMPLETED_INSPECTION,
        prohibited_outcomes=(
            "general_language_interpretation",
            "component_loading",
            "runtime_connection",
            "network_access",
            "filesystem_access",
            "memory_write",
            "evidence_mutation",
            "delivery",
            "tool_routing",
            "action",
            "gp014_import_or_call",
        ),
    )
    return build_bootstrap_fixture_record(
        fixture_name=FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
        fixture_kind="synthetic_bootstrap_boundary_inspection",
        operation=OPERATION_INSPECT_BOUNDARY,
        required_adapter_mode=MODE_EXPLICIT_OFFLINE_FIXTURE,
        expected_result_status=STATUS_COMPLETED_INSPECTION,
        provenance=provenance,
    )


_FIXTURES = (
    _build_disabled_default_fixture(),
    _build_explicit_offline_fixture(),
)

_FIXTURES_BY_NAME = {
    fixture.fixture_name: fixture
    for fixture in _FIXTURES
}


def list_bootstrap_fixtures() -> tuple[BootstrapFixtureRecord, ...]:
    return _FIXTURES


def get_bootstrap_fixture(
    fixture_name: str,
) -> BootstrapFixtureRecord | None:
    return _FIXTURES_BY_NAME.get(fixture_name)


def is_exact_accepted_fixture(
    fixture: BootstrapFixtureRecord,
) -> bool:
    accepted = _FIXTURES_BY_NAME.get(fixture.fixture_name)
    return accepted is not None and fixture == accepted
