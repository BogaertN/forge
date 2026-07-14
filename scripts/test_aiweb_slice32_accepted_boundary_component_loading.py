#!/usr/bin/env python3
"""Behavior tests for Slice 32 accepted boundary component loading."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

sys.dont_write_bytecode = True
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from aiweb_language_core_bootstrap.component_loading import (
    FIXTURE_STATIC_COMPONENT_LOADING,
    STATUS_COMPLETED_STATIC_LOADING,
    STATUS_HELD_FIXTURE_NOT_ACCEPTED,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
    build_component_loading_state,
    get_component_loading_fixture,
    list_component_loading_fixtures,
    run_component_loading_fixture,
    validate_component_loading_fixture_record,
    validate_component_loading_result,
    validate_component_loading_state,
)
from aiweb_language_core_bootstrap.component_loading.static_interfaces import (
    ACCEPTED_PACKAGE_NAMES,
)

TEST_COUNT = 0


def check(value: bool, message: str) -> None:
    global TEST_COUNT
    assert value, message
    TEST_COUNT += 1


def main() -> int:
    fixture = get_component_loading_fixture(FIXTURE_STATIC_COMPONENT_LOADING)
    check(len(list_component_loading_fixtures()) == 1, "exact fixture catalog")
    check(validate_component_loading_fixture_record(fixture).ok, "fixture validates")

    disabled_state = build_component_loading_state(enabled=False)
    check(validate_component_loading_state(disabled_state).ok, "disabled state validates")
    before_disabled = frozenset(sys.modules)
    disabled = run_component_loading_fixture(fixture, loading_state=disabled_state)
    after_disabled = frozenset(sys.modules)
    check(disabled.status == STATUS_REFUSED_DISABLED, "disabled refusal")
    check(disabled.loaded_component_count == 0, "disabled loads none")
    check(not any(name in after_disabled - before_disabled for name in ACCEPTED_PACKAGE_NAMES), "disabled path imports no component root")
    check(validate_component_loading_result(disabled).ok, "disabled result validates")

    invalid_state = replace(disabled_state, deterministic=False)
    invalid = run_component_loading_fixture(fixture, loading_state=invalid_state)
    check(invalid.status == STATUS_HELD_INVALID_STATE, "invalid state held")

    altered_fixture = replace(fixture, fixture_name="altered", fixture_id=fixture.fixture_id)
    altered = run_component_loading_fixture(altered_fixture, loading_state=disabled_state)
    check(altered.status in (STATUS_HELD_FIXTURE_NOT_ACCEPTED, "held_invalid_component_loading_fixture"), "altered fixture held")

    enabled_state = build_component_loading_state(enabled=True)
    check(validate_component_loading_state(enabled_state).ok, "enabled state validates")
    result = run_component_loading_fixture(fixture, loading_state=enabled_state)
    check(result.status == STATUS_COMPLETED_STATIC_LOADING, "loading completes")
    check(result.loaded_component_count == 15, "15 components loaded")
    check(result.accepted_component_count == 15, "15 components accepted")
    check(tuple(item.package_name for item in result.loaded_components) == ACCEPTED_PACKAGE_NAMES, "load order exact")
    check(tuple(item.load_order for item in result.loaded_components) == tuple(range(1, 16)), "load positions exact")
    check(all(item.module_loaded for item in result.loaded_components), "all module loaded flags true")
    check(all(item.interface_verified for item in result.loaded_components), "all interfaces verified")
    check(not any(item.component_invoked for item in result.loaded_components), "no component invoked")
    check(not any(item.verifier_invoked for item in result.loaded_components), "no verifier invoked")
    check(not any(item.runtime_authority_granted for item in result.loaded_components), "no runtime authority")
    check(not result.dynamic_discovery_performed, "no dynamic discovery")
    check(not result.hidden_fallback_used, "no hidden fallback")
    check(not result.runtime_connection_performed, "no runtime connection")
    check(not result.network_access_performed, "no network")
    check(not result.external_data_filesystem_read_performed, "no external data read")
    check(not result.filesystem_write_performed, "no filesystem write")
    check(not result.memory_write_performed, "no memory write")
    check(not result.evidence_mutation_performed, "no evidence mutation")
    check(not result.delivery_performed, "no delivery")
    check(not result.tool_routing_performed, "no tool routing")
    check(not result.action_performed, "no action")
    check(not result.gp014_imported and not result.gp014_called, "no GP-014 use")
    check(result.unregistered_project_roots == (), "no unregistered project component")
    check(validate_component_loading_result(result).ok, "completed result validates")

    repeated = run_component_loading_fixture(fixture, loading_state=enabled_state)
    check(repeated == result, "deterministic repeated result")

    print("SLICE32_ACCEPTED_BOUNDARY_COMPONENT_LOADING_TEST=PASS")
    print(f"TEST_COUNT={TEST_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
