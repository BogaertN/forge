"""Slice 32 accepted boundary component loading.

Importing this subpackage does not load any registered component. Component
loading occurs only when the explicit fixture function is called with an
enabled offline loading state.
"""

from .fixtures import (
    FIXTURE_STATIC_COMPONENT_LOADING,
    get_component_loading_fixture,
    is_exact_component_loading_fixture,
    list_component_loading_fixtures,
)
from .loader import run_component_loading_fixture
from .schema import (
    LOADING_SCHEMA_VERSION,
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
    ComponentInterfaceContract,
    ComponentLoadingFixtureRecord,
    ComponentLoadingResult,
    ComponentLoadingState,
    LoadedComponentRecord,
    build_component_loading_state,
    validate_component_interface_contract,
    validate_component_loading_fixture_record,
    validate_component_loading_result,
    validate_component_loading_state,
    validate_loaded_component_record,
)

__all__ = (
    "LOADING_SCHEMA_VERSION",
    "MODE_DISABLED_DEFAULT",
    "MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING",
    "STATUS_COMPLETED_STATIC_LOADING",
    "STATUS_HELD_BOUNDARY_INSPECTION_FAILED",
    "STATUS_HELD_FIXTURE_NOT_ACCEPTED",
    "STATUS_HELD_INTERFACE_MISMATCH",
    "STATUS_HELD_INVALID_FIXTURE",
    "STATUS_HELD_INVALID_STATE",
    "STATUS_HELD_PREEXISTING_UNREGISTERED_COMPONENT",
    "STATUS_HELD_STATIC_IMPORT_FAILED",
    "STATUS_HELD_UNREGISTERED_COMPONENT",
    "STATUS_REFUSED_DISABLED",
    "ComponentInterfaceContract",
    "ComponentLoadingFixtureRecord",
    "ComponentLoadingResult",
    "ComponentLoadingState",
    "LoadedComponentRecord",
    "FIXTURE_STATIC_COMPONENT_LOADING",
    "build_component_loading_state",
    "get_component_loading_fixture",
    "is_exact_component_loading_fixture",
    "list_component_loading_fixtures",
    "run_component_loading_fixture",
    "validate_component_interface_contract",
    "validate_component_loading_fixture_record",
    "validate_component_loading_result",
    "validate_component_loading_state",
    "validate_loaded_component_record",
)
