"""Exact synthetic fixture catalog for Slice 32."""

from __future__ import annotations

from .schema import (
    MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING,
    OPERATION_LOAD_ACCEPTED_COMPONENTS,
    STATUS_COMPLETED_STATIC_LOADING,
    ComponentLoadingFixtureRecord,
    build_component_loading_fixture_record,
)

FIXTURE_STATIC_COMPONENT_LOADING = "slice32-explicit-static-component-loading-v1"
SLICE31_REQUIRED_FIXTURE = "slice31-explicit-offline-boundary-inspection-v1"


def _build_fixture() -> ComponentLoadingFixtureRecord:
    return build_component_loading_fixture_record(
        fixture_name=FIXTURE_STATIC_COMPONENT_LOADING,
        operation=OPERATION_LOAD_ACCEPTED_COMPONENTS,
        required_activation_mode=MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING,
        required_slice31_fixture_name=SLICE31_REQUIRED_FIXTURE,
        expected_result_status=STATUS_COMPLETED_STATIC_LOADING,
        synthetic=True,
        forge_owned=True,
        internal_only=True,
        fixture_only=True,
        offline_only=True,
        runtime_prohibited=True,
        evidence=False,
        memory=False,
        runtime_corpus=False,
        production_data=False,
        public_output=False,
        external_resource_derived=False,
        memory_derived=False,
        trace_derived=False,
        contains_real_personal_data=False,
        contains_live_secret=False,
        contains_executable_command=False,
        contains_tool_invocation=False,
    )


_FIXTURE = _build_fixture()


def get_component_loading_fixture(name: str) -> ComponentLoadingFixtureRecord:
    if name != FIXTURE_STATIC_COMPONENT_LOADING:
        raise KeyError(name)
    return _FIXTURE


def list_component_loading_fixtures() -> tuple[ComponentLoadingFixtureRecord, ...]:
    return (_FIXTURE,)


def is_exact_component_loading_fixture(record: ComponentLoadingFixtureRecord) -> bool:
    return record == _FIXTURE
