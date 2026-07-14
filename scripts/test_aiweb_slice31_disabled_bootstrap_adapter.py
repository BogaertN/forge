#!/usr/bin/env python3
"""Behavior tests for Slice 31 disabled-by-default bootstrap adapter."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

sys.dont_write_bytecode = True

REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from aiweb_language_core_bootstrap import build_bootstrap_boundary_bundle
from aiweb_language_core_bootstrap.bootstrap_adapter import (
    FIXTURE_DISABLED_DEFAULT,
    FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
    MODE_DISABLED_DEFAULT,
    MODE_EXPLICIT_OFFLINE_FIXTURE,
    STATUS_COMPLETED_INSPECTION,
    STATUS_HELD_FIXTURE_NOT_ACCEPTED,
    STATUS_HELD_INVALID_FIXTURE,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
    build_bootstrap_adapter_state,
    get_bootstrap_fixture,
    list_bootstrap_fixtures,
    run_bootstrap_fixture,
    validate_bootstrap_adapter_result,
    validate_bootstrap_adapter_state,
    validate_bootstrap_fixture_record,
    validate_fixture_provenance_record,
)
from aiweb_language_core_bootstrap.schema import stable_record_id


TEST_COUNT = 0


def check(condition: bool, message: str) -> None:
    global TEST_COUNT
    TEST_COUNT += 1
    if not condition:
        raise AssertionError(message)


def reidentify(record, namespace: str, id_field: str):
    body = record.canonical_body()
    return replace(
        record,
        **{id_field: stable_record_id(namespace, body)},
    )


def main() -> int:
    fixtures = list_bootstrap_fixtures()
    check(len(fixtures) == 2, "fixture catalog must contain exactly two fixtures")
    check(
        tuple(item.fixture_name for item in fixtures)
        == (
            FIXTURE_DISABLED_DEFAULT,
            FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
        ),
        "fixture catalog order or identity mismatch",
    )

    default_state = build_bootstrap_adapter_state()
    explicit_state = build_bootstrap_adapter_state(
        explicit_offline_developer_enable=True
    )
    check(
        validate_bootstrap_adapter_state(default_state).ok
        and default_state.enabled is False
        and default_state.activation_mode == MODE_DISABLED_DEFAULT,
        "default adapter state must validate and remain disabled",
    )
    check(
        validate_bootstrap_adapter_state(explicit_state).ok
        and explicit_state.enabled is True
        and explicit_state.activation_mode == MODE_EXPLICIT_OFFLINE_FIXTURE,
        "explicit offline fixture state must validate",
    )

    for fixture in fixtures:
        check(
            validate_bootstrap_fixture_record(fixture).ok
            and validate_fixture_provenance_record(fixture.provenance).ok,
            f"fixture must validate: {fixture.fixture_name}",
        )
        check(
            fixture.provenance.synthetic
            and fixture.provenance.internal_only
            and fixture.provenance.runtime_prohibited
            and not fixture.provenance.evidence
            and not fixture.provenance.memory
            and not fixture.provenance.runtime_corpus
            and not fixture.provenance.public_output,
            f"fixture category separation failed: {fixture.fixture_name}",
        )

    disabled_fixture = get_bootstrap_fixture(FIXTURE_DISABLED_DEFAULT)
    explicit_fixture = get_bootstrap_fixture(
        FIXTURE_EXPLICIT_OFFLINE_INSPECTION
    )
    assert disabled_fixture is not None
    assert explicit_fixture is not None

    disabled_result = run_bootstrap_fixture(
        disabled_fixture,
        adapter_state=default_state,
    )
    check(
        disabled_result.status == STATUS_REFUSED_DISABLED
        and disabled_result.observation is None
        and validate_bootstrap_adapter_result(disabled_result).ok,
        "disabled fixture must produce a valid refusal",
    )

    explicit_without_enable = run_bootstrap_fixture(
        explicit_fixture,
        adapter_state=default_state,
    )
    check(
        explicit_without_enable.status == STATUS_REFUSED_DISABLED
        and explicit_without_enable.observation is None,
        "explicit fixture must refuse without explicit offline enable",
    )

    explicit_result = run_bootstrap_fixture(
        explicit_fixture,
        adapter_state=explicit_state,
    )
    check(
        explicit_result.status == STATUS_COMPLETED_INSPECTION
        and explicit_result.observation is not None
        and validate_bootstrap_adapter_result(explicit_result).ok,
        "explicit fixture inspection must complete and validate",
    )

    repeat_result = run_bootstrap_fixture(
        explicit_fixture,
        adapter_state=explicit_state,
    )
    check(
        explicit_result == repeat_result
        and explicit_result.result_id == repeat_result.result_id,
        "adapter result must be deterministic",
    )

    bundle = build_bootstrap_boundary_bundle()
    observation = explicit_result.observation
    assert observation is not None
    check(
        observation.bootstrap_boundary_id
        == bundle.boundary.bootstrap_boundary_id
        and observation.authority_state_id
        == bundle.authority.authority_state_id
        and observation.component_registry_id
        == bundle.registry.registry_id
        and observation.import_policy_id
        == bundle.import_policy.import_policy_id
        and observation.component_count == 15,
        "observation must preserve exact Slice 30 boundary identities",
    )
    check(
        all(
            not component.component_loaded
            and not component.runtime_import_authorized
            for component in bundle.registry.components
        ),
        "Slice 31 must not load or import-authorize registered components",
    )

    unknown = replace(
        explicit_fixture,
        fixture_name="slice31-unknown-but-well-shaped-v1",
    )
    unknown = reidentify(unknown, "bootstrap_fixture", "fixture_id")
    unknown_result = run_bootstrap_fixture(
        unknown,
        adapter_state=explicit_state,
    )
    check(
        unknown_result.status == STATUS_HELD_FIXTURE_NOT_ACCEPTED,
        "well-shaped unregistered fixture must be held",
    )

    unsafe_provenance = replace(
        explicit_fixture.provenance,
        external_resource_derived=True,
        external_resource_status="unapproved",
    )
    unsafe_provenance = reidentify(
        unsafe_provenance,
        "bootstrap_fixture_provenance",
        "provenance_id",
    )
    unsafe_fixture = replace(
        explicit_fixture,
        provenance=unsafe_provenance,
    )
    unsafe_fixture = reidentify(
        unsafe_fixture,
        "bootstrap_fixture",
        "fixture_id",
    )
    unsafe_result = run_bootstrap_fixture(
        unsafe_fixture,
        adapter_state=explicit_state,
    )
    check(
        unsafe_result.status == STATUS_HELD_INVALID_FIXTURE,
        "unsafe external-resource-derived fixture must be held",
    )

    unsafe_state = replace(
        explicit_state,
        network_allowed=True,
    )
    unsafe_state = reidentify(
        unsafe_state,
        "bootstrap_adapter_state",
        "adapter_state_id",
    )
    unsafe_state_result = run_bootstrap_fixture(
        explicit_fixture,
        adapter_state=unsafe_state,
    )
    check(
        unsafe_state_result.status == STATUS_HELD_INVALID_STATE,
        "network-enabled adapter state must be held",
    )

    write_state = replace(
        explicit_state,
        filesystem_write_allowed=True,
    )
    write_state = reidentify(
        write_state,
        "bootstrap_adapter_state",
        "adapter_state_id",
    )
    write_state_result = run_bootstrap_fixture(
        explicit_fixture,
        adapter_state=write_state,
    )
    check(
        write_state_result.status == STATUS_HELD_INVALID_STATE,
        "filesystem-write-enabled adapter state must be held",
    )

    check(
        all(
            value is False
            for value in (
                explicit_result.side_effects_performed,
                explicit_result.component_loading_performed,
                explicit_result.external_resource_used,
                explicit_result.memory_write_performed,
                explicit_result.evidence_mutation_performed,
                explicit_result.delivery_performed,
                explicit_result.tool_routing_performed,
                explicit_result.action_performed,
                explicit_result.runtime_connection_performed,
            )
        ),
        "completed fixture result must preserve all non-authority flags",
    )

    check(
        bundle.authority.enabled is False
        and bundle.authority.components_loaded is False
        and bundle.boundary.component_loading is False
        and bundle.boundary.runtime_effect == "none",
        "Slice 30 bootstrap boundary must remain inert",
    )

    print("SLICE31_DISABLED_BOOTSTRAP_ADAPTER_TEST=PASS")
    print(f"TEST_COUNT={TEST_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
