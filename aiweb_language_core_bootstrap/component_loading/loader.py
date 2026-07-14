"""Explicit Slice 32 component-loading flow.

The flow first requires the exact successful Slice 31 boundary-inspection
fixture. It then imports the 15 registered packages through the static source
allowlist and returns records only. It does not invoke component functions.
"""

from __future__ import annotations

import sys

from ..boundary import build_bootstrap_boundary_bundle
from ..bootstrap_adapter import (
    FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
    STATUS_COMPLETED_INSPECTION,
    build_bootstrap_adapter_state,
    get_bootstrap_fixture,
    run_bootstrap_fixture,
    validate_bootstrap_adapter_result,
)
from .fixtures import is_exact_component_loading_fixture
from .schema import (
    MODE_DISABLED_DEFAULT,
    MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING,
    STATUS_COMPLETED_STATIC_LOADING,
    STATUS_HELD_BOUNDARY_INSPECTION_FAILED,
    STATUS_HELD_FIXTURE_NOT_ACCEPTED,
    STATUS_HELD_INTERFACE_MISMATCH,
    STATUS_HELD_INVALID_FIXTURE,
    STATUS_HELD_INVALID_STATE,
    STATUS_HELD_PREEXISTING_UNREGISTERED_COMPONENT,
    STATUS_HELD_STATIC_IMPORT_FAILED,
    STATUS_HELD_UNREGISTERED_COMPONENT,
    STATUS_REFUSED_DISABLED,
    ComponentLoadingFixtureRecord,
    ComponentLoadingResult,
    ComponentLoadingState,
    build_component_loading_result,
    build_loaded_component_record,
    validate_component_loading_fixture_record,
    validate_component_loading_result,
    validate_component_loading_state,
)
from .static_interfaces import (
    ACCEPTED_PACKAGE_NAMES,
    StaticComponentImportFailure,
    build_interface_contracts,
    export_digest,
    load_static_component_modules,
)

_ALLOWED_PROJECT_ROOTS = frozenset(
    ACCEPTED_PACKAGE_NAMES + ("aiweb_language_core_bootstrap",)
)


def _project_roots() -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                name.split(".", 1)[0]
                for name in sys.modules
                if name.startswith("aiweb_")
            }
        )
    )


def run_component_loading_fixture(
    fixture: ComponentLoadingFixtureRecord,
    *,
    loading_state: ComponentLoadingState,
) -> ComponentLoadingResult:
    state_report = validate_component_loading_state(loading_state)
    if not state_report.ok:
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_INVALID_STATE,
            reason_code="component_loading_state_validation_failed",
        )

    fixture_report = validate_component_loading_fixture_record(fixture)
    if not fixture_report.ok:
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_INVALID_FIXTURE,
            reason_code="component_loading_fixture_validation_failed",
        )

    if not is_exact_component_loading_fixture(fixture):
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_FIXTURE_NOT_ACCEPTED,
            reason_code="fixture_not_in_exact_static_catalog",
        )

    if (
        not loading_state.enabled
        or loading_state.activation_mode == MODE_DISABLED_DEFAULT
        or not loading_state.component_loading_authorized
    ):
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_REFUSED_DISABLED,
            reason_code="explicit_component_loading_enable_required",
        )

    if loading_state.activation_mode != MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING:
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_INVALID_STATE,
            reason_code="component_loading_activation_mode_mismatch",
        )

    preexisting_unregistered = tuple(
        root for root in _project_roots() if root not in _ALLOWED_PROJECT_ROOTS
    )
    if preexisting_unregistered:
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_PREEXISTING_UNREGISTERED_COMPONENT,
            reason_code="unregistered_project_component_already_loaded",
            unregistered_project_roots=preexisting_unregistered,
        )

    boundary_bundle = build_bootstrap_boundary_bundle()
    slice31_fixture = get_bootstrap_fixture(FIXTURE_EXPLICIT_OFFLINE_INSPECTION)
    slice31_state = build_bootstrap_adapter_state(explicit_offline_developer_enable=True)
    slice31_result = run_bootstrap_fixture(
        slice31_fixture,
        adapter_state=slice31_state,
        boundary_bundle=boundary_bundle,
    )
    slice31_report = validate_bootstrap_adapter_result(slice31_result)
    if (
        not slice31_report.ok
        or slice31_result.status != STATUS_COMPLETED_INSPECTION
        or slice31_result.observation is None
        or slice31_result.observation.bootstrap_boundary_id
        != boundary_bundle.boundary.bootstrap_boundary_id
        or slice31_result.observation.component_registry_id
        != boundary_bundle.registry.registry_id
    ):
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_BOUNDARY_INSPECTION_FAILED,
            reason_code="slice31_boundary_inspection_not_accepted",
            slice31_result_id=slice31_result.result_id,
            bootstrap_boundary_id=boundary_bundle.boundary.bootstrap_boundary_id,
            component_registry_id=boundary_bundle.registry.registry_id,
        )

    contracts = build_interface_contracts(boundary_bundle.registry)
    try:
        loaded_modules = load_static_component_modules()
    except StaticComponentImportFailure as exc:
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_STATIC_IMPORT_FAILED,
            reason_code="static_component_import_failed_no_fallback",
            slice31_result_id=slice31_result.result_id,
            bootstrap_boundary_id=boundary_bundle.boundary.bootstrap_boundary_id,
            component_registry_id=boundary_bundle.registry.registry_id,
            failed_package_name=exc.package_name,
        )

    unregistered = tuple(
        root for root in _project_roots() if root not in _ALLOWED_PROJECT_ROOTS
    )
    if unregistered:
        return build_component_loading_result(
            fixture_id=fixture.fixture_id,
            loading_state_id=loading_state.loading_state_id,
            status=STATUS_HELD_UNREGISTERED_COMPONENT,
            reason_code="unregistered_project_component_loaded",
            slice31_result_id=slice31_result.result_id,
            bootstrap_boundary_id=boundary_bundle.boundary.bootstrap_boundary_id,
            component_registry_id=boundary_bundle.registry.registry_id,
            unregistered_project_roots=unregistered,
        )

    loaded_records = []
    for index, (contract, loaded_pair) in enumerate(
        zip(contracts, loaded_modules, strict=True),
        start=1,
    ):
        package_name, module = loaded_pair
        module_name = getattr(module, "__name__", "")
        exports = tuple(getattr(module, "__all__", ()))
        if (
            package_name != contract.package_name
            or module_name != contract.package_name
            or exports != contract.expected_exports
            or export_digest(exports) != contract.export_digest
            or any(not hasattr(module, name) for name in exports)
        ):
            return build_component_loading_result(
                fixture_id=fixture.fixture_id,
                loading_state_id=loading_state.loading_state_id,
                status=STATUS_HELD_INTERFACE_MISMATCH,
                reason_code="loaded_component_interface_mismatch",
                slice31_result_id=slice31_result.result_id,
                bootstrap_boundary_id=boundary_bundle.boundary.bootstrap_boundary_id,
                component_registry_id=boundary_bundle.registry.registry_id,
                failed_package_name=contract.package_name,
            )
        loaded_records.append(
            build_loaded_component_record(
                contract=contract,
                module_name=module_name,
                load_order=index,
            )
        )

    result = build_component_loading_result(
        fixture_id=fixture.fixture_id,
        loading_state_id=loading_state.loading_state_id,
        status=STATUS_COMPLETED_STATIC_LOADING,
        reason_code="all_registered_components_loaded_through_static_interfaces",
        slice31_result_id=slice31_result.result_id,
        bootstrap_boundary_id=boundary_bundle.boundary.bootstrap_boundary_id,
        component_registry_id=boundary_bundle.registry.registry_id,
        loaded_components=tuple(loaded_records),
    )
    if validate_component_loading_result(result).ok:
        return result
    return build_component_loading_result(
        fixture_id=fixture.fixture_id,
        loading_state_id=loading_state.loading_state_id,
        status=STATUS_HELD_INTERFACE_MISMATCH,
        reason_code="component_loading_result_validation_failed",
        slice31_result_id=slice31_result.result_id,
        bootstrap_boundary_id=boundary_bundle.boundary.bootstrap_boundary_id,
        component_registry_id=boundary_bundle.registry.registry_id,
    )
