"""Deterministic fixture-only orchestrator for the Slice 30 boundary.

Slice 31 does not load registered boundary components. It only proves that an
explicit offline fixture can pass through a typed adapter and inspect the inert
Slice 30 package-boundary record.
"""

from __future__ import annotations

from ..boundary import (
    BootstrapBoundaryBundle,
    build_bootstrap_boundary_bundle,
    validate_bootstrap_boundary_record,
)
from ..authority import validate_bootstrap_authority_state
from ..component_registry import validate_component_registry_record
from ..import_policy import validate_import_policy_record
from .fixtures import is_exact_accepted_fixture
from .schema import (
    MODE_DISABLED_DEFAULT,
    MODE_EXPLICIT_OFFLINE_FIXTURE,
    OPERATION_INSPECT_BOUNDARY,
    OPERATION_PROBE_DISABLED,
    STATUS_COMPLETED_INSPECTION,
    STATUS_HELD_ADAPTER_MODE_MISMATCH,
    STATUS_HELD_FIXTURE_NOT_ACCEPTED,
    STATUS_HELD_INVALID_BOUNDARY,
    STATUS_HELD_INVALID_FIXTURE,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
    BootstrapAdapterResult,
    BootstrapAdapterState,
    BootstrapFixtureRecord,
    build_bootstrap_adapter_result,
    build_bootstrap_fixture_observation,
    validate_bootstrap_adapter_result,
    validate_bootstrap_adapter_state,
    validate_bootstrap_fixture_record,
)


def _boundary_is_valid(bundle: BootstrapBoundaryBundle) -> bool:
    reports = (
        validate_bootstrap_authority_state(bundle.authority),
        validate_component_registry_record(bundle.registry),
        validate_import_policy_record(bundle.import_policy),
        validate_bootstrap_boundary_record(
            bundle.boundary,
            authority=bundle.authority,
            registry=bundle.registry,
            import_policy=bundle.import_policy,
        ),
    )
    return all(report.ok for report in reports)


def run_bootstrap_fixture(
    fixture: BootstrapFixtureRecord,
    *,
    adapter_state: BootstrapAdapterState,
    boundary_bundle: BootstrapBoundaryBundle | None = None,
) -> BootstrapAdapterResult:
    state_report = validate_bootstrap_adapter_state(adapter_state)
    if not state_report.ok:
        return build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_HELD_INVALID_STATE,
            reason_code="adapter_state_validation_failed",
        )

    fixture_report = validate_bootstrap_fixture_record(fixture)
    if not fixture_report.ok:
        return build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_HELD_INVALID_FIXTURE,
            reason_code="fixture_validation_failed",
        )

    if not is_exact_accepted_fixture(fixture):
        return build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_HELD_FIXTURE_NOT_ACCEPTED,
            reason_code="fixture_not_in_exact_static_catalog",
        )

    bundle = boundary_bundle or build_bootstrap_boundary_bundle()
    if not _boundary_is_valid(bundle):
        return build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_HELD_INVALID_BOUNDARY,
            reason_code="bootstrap_boundary_validation_failed",
        )

    if adapter_state.activation_mode != fixture.required_adapter_mode:
        if adapter_state.activation_mode == MODE_DISABLED_DEFAULT:
            return build_bootstrap_adapter_result(
                fixture_id=fixture.fixture_id,
                adapter_state_id=adapter_state.adapter_state_id,
                status=STATUS_REFUSED_DISABLED,
                reason_code="explicit_offline_fixture_enable_required",
            )
        return build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_HELD_ADAPTER_MODE_MISMATCH,
            reason_code="fixture_adapter_mode_mismatch",
        )

    if fixture.operation == OPERATION_PROBE_DISABLED:
        return build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_REFUSED_DISABLED,
            reason_code="adapter_remains_disabled_by_default",
        )

    if (
        fixture.operation == OPERATION_INSPECT_BOUNDARY
        and adapter_state.activation_mode == MODE_EXPLICIT_OFFLINE_FIXTURE
        and adapter_state.enabled
    ):
        observation = build_bootstrap_fixture_observation(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            bootstrap_schema_version=bundle.boundary.schema_version,
            bootstrap_boundary_id=bundle.boundary.bootstrap_boundary_id,
            authority_state_id=bundle.authority.authority_state_id,
            component_registry_id=bundle.registry.registry_id,
            import_policy_id=bundle.import_policy.import_policy_id,
            component_count=bundle.registry.component_count,
            boundary_kind=bundle.boundary.boundary_kind,
            integration_state=bundle.boundary.integration_state,
            registry_state=bundle.registry.registry_state,
            runtime_effect=bundle.boundary.runtime_effect,
            dependency_effect=bundle.boundary.dependency_effect,
            adapter_enabled=adapter_state.enabled,
        )
        result = build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_COMPLETED_INSPECTION,
            reason_code="explicit_offline_fixture_inspection_completed",
            observation=observation,
        )
        report = validate_bootstrap_adapter_result(result)
        if report.ok:
            return result
        return build_bootstrap_adapter_result(
            fixture_id=fixture.fixture_id,
            adapter_state_id=adapter_state.adapter_state_id,
            status=STATUS_HELD_INVALID_BOUNDARY,
            reason_code="adapter_result_validation_failed",
        )

    return build_bootstrap_adapter_result(
        fixture_id=fixture.fixture_id,
        adapter_state_id=adapter_state.adapter_state_id,
        status=STATUS_HELD_ADAPTER_MODE_MISMATCH,
        reason_code="unsupported_fixture_adapter_combination",
    )
