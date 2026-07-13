#!/usr/bin/env python3
"""Behavior tests for Slice 30 isolated language-core package boundary."""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ACCEPTED_COMPONENT_PREFIXES = (
    "aiweb_meaning_law_trace_scaffold",
    "aiweb_concept_boundary_scaffold",
    "aiweb_predicate_role_boundary_scaffold",
    "aiweb_verbal_cognition_gate_boundary_scaffold",
    "aiweb_candidate_meaning_boundary_scaffold",
    "aiweb_ambiguity_clarification_boundary_scaffold",
    "aiweb_requirements_traceability_scaffold",
    "aiweb_external_resource_quarantine_scaffold",
    "aiweb_corpus_evidence_memory_trace_scaffold",
    "aiweb_selected_meaning_boundary_scaffold",
    "aiweb_output_expression_boundary_scaffold",
    "aiweb_gp014_preservation_decision_scaffold",
    "aiweb_rmc_echo_boundary_scaffold",
    "aiweb_delivery_action_tool_routing_boundary_scaffold",
    "aiweb_read_only_inspection_surface_scaffold",
)

before_modules = set(sys.modules)

from aiweb_language_core_bootstrap import (
    build_bootstrap_authority_state,
    build_bootstrap_boundary_bundle,
    build_component_registration_record,
    build_component_registry_record,
    build_import_policy_record,
    canonical_json,
    validate_bootstrap_authority_state,
    validate_bootstrap_boundary_record,
    validate_component_registration_record,
    validate_component_registry_record,
    validate_import_policy_record,
)
from aiweb_language_core_bootstrap.component_registry import (
    PROHIBITED_RUNTIME_COMPONENTS,
)


def assert_invalid(report, code: str) -> None:
    assert not report.ok
    assert any(issue.code == code for issue in report.issues), report.issues


def test_import_loads_no_accepted_component() -> None:
    newly_loaded = set(sys.modules) - before_modules
    for prefix in ACCEPTED_COMPONENT_PREFIXES:
        assert not any(
            module == prefix or module.startswith(f"{prefix}.")
            for module in newly_loaded
        ), prefix


def test_default_bundle_is_valid_and_deterministic() -> None:
    first = build_bootstrap_boundary_bundle()
    second = build_bootstrap_boundary_bundle()
    assert first == second
    assert first.boundary.bootstrap_boundary_id == second.boundary.bootstrap_boundary_id
    assert canonical_json(first) == canonical_json(second)

    assert validate_bootstrap_authority_state(first.authority).ok
    assert validate_component_registry_record(first.registry).ok
    assert validate_import_policy_record(first.import_policy).ok
    assert validate_bootstrap_boundary_record(
        first.boundary,
        authority=first.authority,
        registry=first.registry,
        import_policy=first.import_policy,
    ).ok


def test_default_authority_grants_nothing() -> None:
    authority = build_bootstrap_authority_state()
    assert authority.disabled_by_default is True
    assert authority.fixture_only is True
    assert authority.offline_only is True
    assert authority.deterministic is True

    for field in (
        "enabled",
        "runtime_connected",
        "components_loaded",
        "main_registered",
        "route_registered",
        "ui_connected",
        "network_allowed",
        "filesystem_write_allowed",
        "environment_selected_backend",
        "dynamic_loading_allowed",
        "external_resource_allowed",
        "memory_write_allowed",
        "evidence_mutation_allowed",
        "delivery_allowed",
        "tool_routing_allowed",
        "action_allowed",
        "gp014_imported",
        "gp014_called",
        "gp014_superseded",
        "production_ready",
        "release_authorized",
    ):
        assert getattr(authority, field) is False, field


def test_registry_is_exact_and_not_loaded() -> None:
    registry = build_component_registry_record()
    assert registry.component_count == 15
    assert len(registry.components) == 15
    assert registry.registry_state == "registered_not_loaded"
    assert registry.components_loaded is False
    assert registry.dynamic_discovery_allowed is False
    assert len({item.package_name for item in registry.components}) == 15
    assert not set(PROHIBITED_RUNTIME_COMPONENTS).intersection(
        item.package_name for item in registry.components
    )
    for item in registry.components:
        assert item.registry_state == "registered_not_loaded"
        assert item.runtime_import_authorized is False
        assert item.component_loaded is False
        assert len(item.package_digest) == 64


def test_authority_escalation_is_rejected() -> None:
    base = build_bootstrap_authority_state()
    for field in (
        "enabled",
        "runtime_connected",
        "components_loaded",
        "main_registered",
        "route_registered",
        "ui_connected",
        "network_allowed",
        "filesystem_write_allowed",
        "environment_selected_backend",
        "dynamic_loading_allowed",
        "external_resource_allowed",
        "memory_write_allowed",
        "evidence_mutation_allowed",
        "delivery_allowed",
        "tool_routing_allowed",
        "action_allowed",
        "gp014_imported",
        "gp014_called",
        "gp014_superseded",
        "production_ready",
        "release_authorized",
    ):
        altered = replace(base, **{field: True})
        assert_invalid(
            validate_bootstrap_authority_state(altered),
            "must_remain_false",
        )


def test_registry_mutation_is_rejected() -> None:
    registry = build_component_registry_record()
    first = registry.components[0]

    def with_recomputed_component_id(record, **changes):
        altered = replace(record, **changes)
        return replace(
            altered,
            component_registration_id=altered.expected_id(),
        )

    def with_recomputed_registry_id(record, components):
        altered = replace(record, components=components)
        return replace(altered, registry_id=altered.expected_id())

    altered_digest = with_recomputed_component_id(
        first,
        package_digest="0" * 64,
    )
    assert_invalid(
        validate_component_registration_record(altered_digest),
        "component_identity_mismatch",
    )

    altered_slice = with_recomputed_component_id(
        first,
        slice_ref="Slice 700",
    )
    assert_invalid(
        validate_component_registration_record(altered_slice),
        "component_identity_mismatch",
    )

    altered_count = with_recomputed_component_id(
        first,
        file_count=first.file_count + 1,
    )
    assert_invalid(
        validate_component_registration_record(altered_count),
        "component_identity_mismatch",
    )

    altered_scope = with_recomputed_component_id(
        first,
        accepted_scope=f"{first.accepted_scope} altered",
    )
    assert_invalid(
        validate_component_registration_record(altered_scope),
        "component_identity_mismatch",
    )

    runtime_enabled = with_recomputed_component_id(
        first,
        runtime_import_authorized=True,
    )
    assert_invalid(
        validate_component_registration_record(runtime_enabled),
        "must_remain_false",
    )

    prohibited = build_component_registration_record(
        slice_ref="Slice 23",
        package_name="aiweb_end_to_end_dry_run_harness_scaffold",
        package_digest="1" * 64,
        file_count=1,
        accepted_scope="proof ancestry only",
    )
    assert_invalid(
        validate_component_registration_record(prohibited),
        "evidence_component_not_runtime_component",
    )

    unknown = build_component_registration_record(
        slice_ref="Slice 999",
        package_name="unauthorized_runtime_component",
        package_digest="2" * 64,
        file_count=1,
        accepted_scope="unauthorized",
    )
    assert_invalid(
        validate_component_registration_record(unknown),
        "unrecognized_component",
    )

    tampered_components = (altered_digest,) + registry.components[1:]
    tampered_registry = with_recomputed_registry_id(
        registry,
        tampered_components,
    )
    assert_invalid(
        validate_component_registry_record(tampered_registry),
        "component_identity_set_or_order_mismatch",
    )

    duplicate_components = (
        registry.components[0],
    ) + registry.components[:-1]
    duplicate_registry = with_recomputed_registry_id(
        registry,
        duplicate_components,
    )
    assert_invalid(
        validate_component_registry_record(duplicate_registry),
        "component_set_or_order_mismatch",
    )


def test_import_policy_escalation_is_rejected() -> None:
    policy = build_import_policy_record()
    assert policy.static_allowlist_required is True
    for field in (
        "dynamic_loading_allowed",
        "plugin_discovery_allowed",
        "environment_selected_backend",
        "hidden_fallback_allowed",
        "network_import_allowed",
        "model_import_allowed",
        "vector_import_allowed",
        "retrieval_import_allowed",
    ):
        altered = replace(policy, **{field: True})
        assert_invalid(
            validate_import_policy_record(altered),
            "must_remain_false",
        )


def test_boundary_escalation_is_rejected() -> None:
    bundle = build_bootstrap_boundary_bundle()
    for field in (
        "existing_file_modification",
        "component_loading",
        "main_connection",
        "route_connection",
        "ui_connection",
        "persistent_side_effect",
    ):
        altered = replace(bundle.boundary, **{field: True})
        report = validate_bootstrap_boundary_record(
            altered,
            authority=bundle.authority,
            registry=bundle.registry,
            import_policy=bundle.import_policy,
        )
        assert_invalid(report, "must_remain_false")


def test_public_api_has_no_execution_operations() -> None:
    import aiweb_language_core_bootstrap as bootstrap

    prohibited = {
        "run",
        "execute",
        "interpret",
        "render",
        "deliver",
        "route",
        "load_plugin",
        "discover",
        "call_model",
        "write_memory",
        "invoke_tool",
        "perform_action",
    }
    assert not prohibited.intersection(bootstrap.__all__)


def test_import_and_build_have_no_repository_side_effect() -> None:
    package = REPO / "aiweb_language_core_bootstrap"
    before = {
        path.relative_to(REPO).as_posix(): path.stat().st_mtime_ns
        for path in package.rglob("*")
        if path.is_file()
    }
    environment = dict(os.environ)
    build_bootstrap_boundary_bundle()
    after = {
        path.relative_to(REPO).as_posix(): path.stat().st_mtime_ns
        for path in package.rglob("*")
        if path.is_file()
    }
    assert before == after
    assert dict(os.environ) == environment


def main() -> int:
    tests = (
        test_import_loads_no_accepted_component,
        test_default_bundle_is_valid_and_deterministic,
        test_default_authority_grants_nothing,
        test_registry_is_exact_and_not_loaded,
        test_authority_escalation_is_rejected,
        test_registry_mutation_is_rejected,
        test_import_policy_escalation_is_rejected,
        test_boundary_escalation_is_rejected,
        test_public_api_has_no_execution_operations,
        test_import_and_build_have_no_repository_side_effect,
    )
    for test in tests:
        test()
    print("SLICE30_ISOLATED_LANGUAGE_CORE_PACKAGE_BOUNDARY_TEST=PASS")
    print(f"TEST_COUNT={len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
