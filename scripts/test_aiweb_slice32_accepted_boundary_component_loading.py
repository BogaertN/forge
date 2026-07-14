#!/usr/bin/env python3
"""Behavior and adversarial tests for Slice 32 R1 strict identity hardening."""

from __future__ import annotations

from dataclasses import replace
import hashlib
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
from aiweb_language_core_bootstrap.component_loading.schema import (
    ComponentInterfaceContract,
    ComponentLoadingResult,
    LoadedComponentRecord,
    build_component_interface_contract,
    build_component_loading_result,
    build_loaded_component_record,
    validate_component_interface_contract,
    validate_loaded_component_record,
)
from aiweb_language_core_bootstrap.component_loading.static_interfaces import (
    ACCEPTED_PACKAGE_NAMES,
    build_interface_contracts,
)
from aiweb_language_core_bootstrap.component_registry import (
    build_component_registry_record,
)

TEST_COUNT = 0


def check(value: bool, message: str) -> None:
    global TEST_COUNT
    assert value, message
    TEST_COUNT += 1


def reidentify_contract(
    record: ComponentInterfaceContract,
    **changes: object,
) -> ComponentInterfaceContract:
    changed = replace(record, **changes)
    return replace(changed, interface_contract_id=changed.expected_id())


def reidentify_loaded(
    record: LoadedComponentRecord,
    **changes: object,
) -> LoadedComponentRecord:
    changed = replace(record, **changes)
    return replace(changed, loaded_component_id=changed.expected_id())


def reidentify_result(
    record: ComponentLoadingResult,
    **changes: object,
) -> ComponentLoadingResult:
    changed = replace(record, **changes)
    return replace(changed, loading_result_id=changed.expected_id())


def fake_digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def main() -> int:
    fixture = get_component_loading_fixture(FIXTURE_STATIC_COMPONENT_LOADING)
    check(len(list_component_loading_fixtures()) == 1, "exact fixture catalog")
    check(validate_component_loading_fixture_record(fixture).ok, "fixture validates")

    altered_fixture = replace(fixture, required_slice31_fixture_name="altered")
    altered_fixture = replace(altered_fixture, fixture_id=altered_fixture.expected_id())
    check(
        not validate_component_loading_fixture_record(altered_fixture).ok,
        "reidentified altered fixture rejected",
    )

    disabled_state = build_component_loading_state(enabled=False)
    check(validate_component_loading_state(disabled_state).ok, "disabled state validates")
    before_disabled = frozenset(sys.modules)
    disabled = run_component_loading_fixture(fixture, loading_state=disabled_state)
    after_disabled = frozenset(sys.modules)
    check(disabled.status == STATUS_REFUSED_DISABLED, "disabled refusal")
    check(disabled.loaded_component_count == 0, "disabled loads none")
    check(
        not any(name in after_disabled - before_disabled for name in ACCEPTED_PACKAGE_NAMES),
        "disabled path imports no component root",
    )
    check(validate_component_loading_result(disabled).ok, "disabled result validates")

    altered_disabled = reidentify_result(
        disabled,
        loading_state_id=build_component_loading_state(enabled=True).loading_state_id,
    )
    check(
        not validate_component_loading_result(altered_disabled).ok,
        "reidentified altered disabled result rejected",
    )

    invalid_state = replace(disabled_state, deterministic=False)
    invalid_state = replace(invalid_state, loading_state_id=invalid_state.expected_id())
    check(not validate_component_loading_state(invalid_state).ok, "reidentified invalid state rejected")
    invalid = run_component_loading_fixture(fixture, loading_state=invalid_state)
    check(invalid.status == STATUS_HELD_INVALID_STATE, "invalid state held")

    altered = run_component_loading_fixture(altered_fixture, loading_state=disabled_state)
    check(
        altered.status in (
            STATUS_HELD_FIXTURE_NOT_ACCEPTED,
            "held_invalid_component_loading_fixture",
        ),
        "altered fixture held",
    )

    enabled_state = build_component_loading_state(enabled=True)
    check(validate_component_loading_state(enabled_state).ok, "enabled state validates")
    result = run_component_loading_fixture(fixture, loading_state=enabled_state)
    check(result.status == STATUS_COMPLETED_STATIC_LOADING, "loading completes")
    check(result.loaded_component_count == 15, "15 components loaded")
    check(result.accepted_component_count == 15, "15 components accepted")
    check(
        tuple(item.package_name for item in result.loaded_components)
        == ACCEPTED_PACKAGE_NAMES,
        "load order exact",
    )
    check(
        tuple(item.load_order for item in result.loaded_components)
        == tuple(range(1, 16)),
        "load positions exact",
    )
    check(all(item.module_loaded for item in result.loaded_components), "all modules loaded")
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
    check(result.unregistered_project_roots == (), "no unregistered component")
    check(validate_component_loading_result(result).ok, "completed result validates")

    registry = build_component_registry_record()
    contracts = build_interface_contracts(registry)
    check(len(contracts) == 15, "exact accepted contract count")
    check(all(validate_component_interface_contract(item).ok for item in contracts), "all exact contracts validate")
    check(all(validate_loaded_component_record(item).ok for item in result.loaded_components), "all exact loaded records validate")

    first_contract = contracts[0]
    contract_mutations = (
        {"slice_ref": "Slice X"},
        {"component_registration_id": "bootstrap_component:" + "0" * 64},
        {"package_name": "aiweb_fake_component"},
        {"package_digest": fake_digest("altered-package")},
        {"file_count": first_contract.file_count + 1},
        {"accepted_scope": "altered scope"},
        {"expected_exports": first_contract.expected_exports + ("fake_export",), "export_count": first_contract.export_count + 1},
        {"export_digest": fake_digest("altered-exports")},
    )
    for index, changes in enumerate(contract_mutations, start=1):
        mutated = reidentify_contract(first_contract, **changes)
        check(
            not validate_component_interface_contract(mutated).ok,
            f"contract mutation {index} rejected after reidentification",
        )

    first_loaded = result.loaded_components[0]
    loaded_mutations = (
        {"interface_contract_id": "component_interface:" + "0" * 64},
        {"component_registration_id": "bootstrap_component:" + "1" * 64},
        {"package_name": "aiweb_fake_component", "module_name": "aiweb_fake_component"},
        {"module_name": "aiweb_fake_module"},
        {"load_order": 2},
        {"export_count": first_loaded.export_count + 1},
        {"export_digest": fake_digest("fake-loaded-exports")},
    )
    for index, changes in enumerate(loaded_mutations, start=1):
        mutated = reidentify_loaded(first_loaded, **changes)
        check(
            not validate_loaded_component_record(mutated).ok,
            f"loaded-record mutation {index} rejected after reidentification",
        )

    fake_contracts = []
    fake_loaded = []
    for index, real_contract in enumerate(contracts, start=1):
        fake_contract = build_component_interface_contract(
            slice_ref=f"Fake Slice {index}",
            component_registration_id=f"bootstrap_component:{fake_digest(f'reg-{index}')}",
            package_name=f"aiweb_fake_component_{index:02d}",
            package_digest=fake_digest(f"package-{index}"),
            file_count=index,
            accepted_scope=f"fake accepted scope {index}",
            expected_exports=(f"fake_export_{index}",),
            export_digest=fake_digest(f"exports-{index}"),
        )
        fake_contracts.append(fake_contract)
        fake_loaded.append(
            build_loaded_component_record(
                contract=fake_contract,
                module_name=fake_contract.package_name,
                load_order=index,
            )
        )
        check(
            not validate_component_interface_contract(fake_contract).ok,
            f"fictitious contract {index} rejected",
        )
        check(
            not validate_loaded_component_record(fake_loaded[-1]).ok,
            f"fictitious loaded record {index} rejected",
        )

    fake_result = build_component_loading_result(
        fixture_id=result.fixture_id,
        loading_state_id=result.loading_state_id,
        status=result.status,
        reason_code=result.reason_code,
        slice31_result_id=result.slice31_result_id,
        bootstrap_boundary_id=result.bootstrap_boundary_id,
        component_registry_id=result.component_registry_id,
        loaded_components=tuple(fake_loaded),
    )
    check(
        not validate_component_loading_result(fake_result).ok,
        "fictitious recomputed 15-component success result rejected",
    )

    result_mutations = (
        {"fixture_id": "component_loading_fixture:" + "0" * 64},
        {"loading_state_id": "component_loading_state:" + "0" * 64},
        {"slice31_result_id": "bootstrap_adapter_result:" + "0" * 64},
        {"bootstrap_boundary_id": "bootstrap_boundary:" + "0" * 64},
        {"component_registry_id": "bootstrap_registry:" + "0" * 64},
        {"reason_code": "altered_success_reason"},
        {"loaded_components": tuple(reversed(result.loaded_components))},
        {"loaded_components": (result.loaded_components[0],) + result.loaded_components[:-1]},
        {"loaded_components": result.loaded_components[:-1], "loaded_component_count": 14},
        {"loaded_components": tuple(fake_loaded)},
    )
    for index, changes in enumerate(result_mutations, start=1):
        mutated = reidentify_result(result, **changes)
        check(
            not validate_component_loading_result(mutated).ok,
            f"success-result mutation {index} rejected after reidentification",
        )

    repeated = run_component_loading_fixture(fixture, loading_state=enabled_state)
    check(repeated == result, "deterministic repeated result")

    print("SLICE32_R1_STRICT_LOADED_COMPONENT_IDENTITY_TEST=PASS")
    print(f"TEST_COUNT={TEST_COUNT}")
    print("FICTITIOUS_RECOMPUTED_RESULT_REJECTED=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
