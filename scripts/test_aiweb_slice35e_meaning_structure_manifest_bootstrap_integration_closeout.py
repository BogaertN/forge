#!/usr/bin/env python3
"""Behavior, containment, determinism, and adversarial proof for Slice 35E."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import replace
import builtins
import os
from pathlib import Path
import socket
import subprocess
import sys
from unittest.mock import patch
import urllib.request

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

MODULE_NAME = (
    "aiweb_language_core_bootstrap.meaning_structure_manifest."
    "bootstrap_integration"
)

before_modules = set(sys.modules)
import aiweb_language_core_bootstrap as bootstrap_root
import aiweb_language_core_bootstrap.meaning_structure_manifest as msm_root

assert MODULE_NAME not in sys.modules
assert "bootstrap_integration" not in bootstrap_root.__dict__
assert "bootstrap_integration" not in msm_root.__dict__

from aiweb_language_core_bootstrap.meaning_structure_manifest import (
    MeaningStructureManifestV1,
)
from aiweb_language_core_bootstrap.meaning_structure_manifest.bootstrap_integration import (
    INTEGRATION_SCHEMA_VERSION,
    STATUS_COMPLETED,
    STATUS_HELD_INVALID_FIXTURE,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
    build_msm_bootstrap_integration_state,
    build_synthetic_msm_bootstrap_fixture,
    run_msm_bootstrap_integration,
    validate_msm_bootstrap_fixture,
    validate_msm_bootstrap_integration_result,
    validate_msm_bootstrap_integration_state,
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(label)


def reid_state(state):
    return replace(state, state_id=state.expected_id())


def reid_fixture(fixture):
    return replace(fixture, fixture_id=fixture.expected_id())


def reid_result(result):
    return replace(result, result_id=result.expected_id())


# Explicit import must not import any of the accepted Phase B component packages.
accepted_components = (
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
new_modules = set(sys.modules) - before_modules
for component in accepted_components:
    check(
        not any(
            name == component or name.startswith(component + ".")
            for name in new_modules
        ),
        f"integration import loaded accepted component: {component}",
    )

# State and fixture identities are deterministic and immutable.
disabled_state = build_msm_bootstrap_integration_state()
enabled_state = build_msm_bootstrap_integration_state(
    explicit_offline_developer_enable=True
)
fixture_a = build_synthetic_msm_bootstrap_fixture()
fixture_b = build_synthetic_msm_bootstrap_fixture()
check(disabled_state == build_msm_bootstrap_integration_state(), "disabled state deterministic")
check(enabled_state == build_msm_bootstrap_integration_state(explicit_offline_developer_enable=True), "enabled state deterministic")
check(fixture_a == fixture_b, "fixture deterministic")
check(type(fixture_a.manifest) is MeaningStructureManifestV1, "exact manifest type")
check(validate_msm_bootstrap_integration_state(disabled_state).ok, "disabled state valid")
check(validate_msm_bootstrap_integration_state(enabled_state).ok, "enabled state valid")
check(validate_msm_bootstrap_fixture(fixture_a).ok, "fixture valid")
check(disabled_state.enabled is False, "disabled by default")
check(enabled_state.enabled is True, "explicit enable required")
check(disabled_state.schema_version == INTEGRATION_SCHEMA_VERSION, "schema version exact")

for state in (disabled_state, enabled_state):
    for field_name in (
        "runtime_connected",
        "component_loading_allowed",
        "route_allowed",
        "api_allowed",
        "ui_allowed",
        "network_allowed",
        "filesystem_read_allowed",
        "filesystem_write_allowed",
        "environment_backend_selection_allowed",
        "dynamic_loading_allowed",
        "external_resource_allowed",
        "memory_read_allowed",
        "memory_write_allowed",
        "evidence_mutation_allowed",
        "delivery_allowed",
        "tool_routing_allowed",
        "action_allowed",
        "gp014_import_allowed",
        "gp014_call_allowed",
        "llm_authority_allowed",
        "vector_authority_allowed",
        "embedding_authority_allowed",
        "rag_authority_allowed",
        "release_authorized",
        "production_ready",
    ):
        check(getattr(state, field_name) is False, f"state boundary false: {field_name}")

# Default execution refuses and grants no consequence.
default_result = run_msm_bootstrap_integration(
    fixture=fixture_a,
    integration_state=disabled_state,
)
check(validate_msm_bootstrap_integration_result(default_result).ok, "default result valid")
check(default_result.status == STATUS_REFUSED_DISABLED, "default refusal exact")
check(default_result.bounded_integration_completed is False, "default not completed")
check(default_result.canonical_byte_count == 0, "default no serialization")

# Enabled execution must remain side-effect free.
def forbidden(*args, **kwargs):
    raise AssertionError("forbidden runtime side effect attempted")

with ExitStack() as stack:
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "read_bytes", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(os, "system", forbidden))
    stack.enter_context(patch.object(subprocess, "run", forbidden))
    stack.enter_context(patch.object(subprocess, "Popen", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    enabled_result_a = run_msm_bootstrap_integration(
        fixture=fixture_a,
        integration_state=enabled_state,
    )
    enabled_result_b = run_msm_bootstrap_integration(
        fixture=fixture_b,
        integration_state=enabled_state,
    )

check(enabled_result_a == enabled_result_b, "enabled result deterministic")
check(validate_msm_bootstrap_integration_result(enabled_result_a).ok, "enabled result valid")
check(enabled_result_a.status == STATUS_COMPLETED, "enabled status completed")
check(enabled_result_a.bounded_integration_completed is True, "integration completed")
check(enabled_result_a.manifest_validation_passed is True, "manifest validated")
check(enabled_result_a.round_trip_equal is True, "round trip exact")
check(enabled_result_a.canonical_byte_count > 0, "canonical bytes produced")
check(len(enabled_result_a.canonical_sha256) == 64, "canonical digest exact length")
check(enabled_result_a.canonical_sha256 == fixture_a.expected_canonical_sha256, "fixture digest preserved")

for field_name in (
    "runtime_connection_performed",
    "component_loading_performed",
    "route_registration_performed",
    "api_registration_performed",
    "ui_connection_performed",
    "network_access_performed",
    "filesystem_read_performed",
    "filesystem_write_performed",
    "environment_backend_selected",
    "dynamic_loading_performed",
    "external_resource_used",
    "memory_read_performed",
    "memory_write_performed",
    "evidence_mutation_performed",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "gp014_imported",
    "gp014_called",
    "llm_authority_used",
    "vector_authority_used",
    "embedding_authority_used",
    "rag_authority_used",
    "technical_acceptance_granted_by_runtime",
    "release_authorized",
    "production_ready",
):
    check(getattr(enabled_result_a, field_name) is False, f"result boundary false: {field_name}")

# Fail closed on state, fixture, manifest and result tampering.
bad_state = reid_state(replace(enabled_state, route_allowed=True))
bad_state_result = run_msm_bootstrap_integration(
    fixture=fixture_a,
    integration_state=bad_state,
)
check(bad_state_result.status == STATUS_HELD_INVALID_STATE, "invalid state held")

bad_fixture = reid_fixture(replace(fixture_a, accepted_fixture=False))
bad_fixture_result = run_msm_bootstrap_integration(
    fixture=bad_fixture,
    integration_state=enabled_state,
)
check(bad_fixture_result.status == STATUS_HELD_INVALID_FIXTURE, "invalid fixture held")

bad_manifest = replace(fixture_a.manifest, manifest_id="")
bad_manifest_fixture = reid_fixture(
    replace(
        fixture_a,
        manifest=bad_manifest,
        expected_manifest_id="",
    )
)
check(not validate_msm_bootstrap_fixture(bad_manifest_fixture).ok, "invalid manifest fixture rejected")

for field_name in (
    "network_access_performed",
    "filesystem_write_performed",
    "memory_write_performed",
    "evidence_mutation_performed",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "technical_acceptance_granted_by_runtime",
    "release_authorized",
    "production_ready",
):
    altered = reid_result(replace(enabled_result_a, **{field_name: True}))
    check(
        not validate_msm_bootstrap_integration_result(altered).ok,
        f"result escalation rejected: {field_name}",
    )

# Frozen records must reject mutation.
try:
    enabled_result_a.status = "tampered"  # type: ignore[misc]
except Exception:
    pass
else:
    raise AssertionError("result record is mutable")

print("SLICE 35E BEHAVIOR TEST: PASS")
print(f"checks={checks}")
print(f"fixture_id={fixture_a.fixture_id}")
print(f"canonical_bytes={enabled_result_a.canonical_byte_count}")
print(f"canonical_sha256={enabled_result_a.canonical_sha256}")
print("runtime_network_memory_delivery_tool_action_attempts=0")
