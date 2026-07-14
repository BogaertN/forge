"""Slice 31 disabled-by-default offline bootstrap adapter.

The subpackage exports typed in-memory fixture records and deterministic
builders only. Importing it does not enable the adapter or run a fixture.
"""

from .adapter import run_bootstrap_fixture
from .fixtures import (
    FIXTURE_DISABLED_DEFAULT,
    FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
    get_bootstrap_fixture,
    is_exact_accepted_fixture,
    list_bootstrap_fixtures,
)
from .schema import (
    ADAPTER_SCHEMA_VERSION,
    MODE_DISABLED_DEFAULT,
    MODE_EXPLICIT_OFFLINE_FIXTURE,
    STATUS_COMPLETED_INSPECTION,
    STATUS_HELD_ADAPTER_MODE_MISMATCH,
    STATUS_HELD_FIXTURE_NOT_ACCEPTED,
    STATUS_HELD_INVALID_BOUNDARY,
    STATUS_HELD_INVALID_FIXTURE,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
    BootstrapAdapterResult,
    BootstrapAdapterState,
    BootstrapFixtureObservation,
    BootstrapFixtureRecord,
    FixtureProvenanceRecord,
    build_bootstrap_adapter_state,
    validate_bootstrap_adapter_result,
    validate_bootstrap_adapter_state,
    validate_bootstrap_fixture_observation,
    validate_bootstrap_fixture_record,
    validate_fixture_provenance_record,
)

__all__ = (
    "ADAPTER_SCHEMA_VERSION",
    "BootstrapAdapterResult",
    "BootstrapAdapterState",
    "BootstrapFixtureObservation",
    "BootstrapFixtureRecord",
    "FIXTURE_DISABLED_DEFAULT",
    "FIXTURE_EXPLICIT_OFFLINE_INSPECTION",
    "FixtureProvenanceRecord",
    "MODE_DISABLED_DEFAULT",
    "MODE_EXPLICIT_OFFLINE_FIXTURE",
    "STATUS_COMPLETED_INSPECTION",
    "STATUS_HELD_ADAPTER_MODE_MISMATCH",
    "STATUS_HELD_FIXTURE_NOT_ACCEPTED",
    "STATUS_HELD_INVALID_BOUNDARY",
    "STATUS_HELD_INVALID_FIXTURE",
    "STATUS_HELD_INVALID_STATE",
    "STATUS_REFUSED_DISABLED",
    "build_bootstrap_adapter_state",
    "get_bootstrap_fixture",
    "is_exact_accepted_fixture",
    "list_bootstrap_fixtures",
    "run_bootstrap_fixture",
    "validate_bootstrap_adapter_result",
    "validate_bootstrap_adapter_state",
    "validate_bootstrap_fixture_observation",
    "validate_bootstrap_fixture_record",
    "validate_fixture_provenance_record",
)
