#!/usr/bin/env python3
"""Behavior and adversarial tests for Slice 36B0."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import builtins
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.input_event_custody import (
    InputCustodyStatus,
    capture_input_event,
)
from aiweb_language_core_bootstrap.resonant_language_operator_contract import (
    CONTRACT_SCHEMA_VERSION,
    CONTRACT_SPEC_ID,
    CONTRACT_SPEC_VERSION,
    EXPECTED_RSOC_OPERATOR_COUNT,
    FIELD_SCHEMA_ID,
    LEGACY_ISOLATION_SCHEMA_ID,
    OPERATOR_SCHEMA_ID,
    REGISTRY_SCHEMA_ID,
    FieldEnvelopeBuildStatus,
    FieldPhaseStatus,
    FieldProjectionStatus,
    FieldSupportStatus,
    LegacySurfaceCategory,
    LegacySurfaceDisposition,
    LineageIdentityHandling,
    OperatorApplicationStatus,
    OperatorArity,
    OperatorRuntimeStatus,
    build_default_legacy_isolation_catalog,
    build_default_rsoc_operator_registry,
    build_unprojected_language_field,
    evaluate_operator_application,
    isolation_record_for_surface,
    operator_contract_for_glyph,
    operator_contract_for_key,
    validate_field_envelope_build_result,
    validate_legacy_isolation_catalog,
    validate_legacy_isolation_record,
    validate_operator_application_decision,
    validate_resonant_language_field,
    validate_rsoc_language_operator_registry,
    validate_rsoc_operator_contract,
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1


def forbidden(*args, **kwargs):
    raise AssertionError("forbidden external side effect attempted")


check(CONTRACT_SPEC_ID == "aiweb-rsoc-fbsc-language-operator-contract", "spec id exact")
check(CONTRACT_SPEC_VERSION.endswith("-v1"), "spec version exact")
check(CONTRACT_SCHEMA_VERSION.endswith("-v1"), "schema version exact")
check(FIELD_SCHEMA_ID.endswith("-v1"), "field schema exact")
check(OPERATOR_SCHEMA_ID.endswith("-v1"), "operator schema exact")
check(REGISTRY_SCHEMA_ID.endswith("-v1"), "registry schema exact")
check(LEGACY_ISOLATION_SCHEMA_ID.endswith("-v1"), "isolation schema exact")
check(EXPECTED_RSOC_OPERATOR_COUNT == 10, "operator count exact")

registry_a = build_default_rsoc_operator_registry()
registry_b = build_default_rsoc_operator_registry()
check(registry_a == registry_b, "registry deterministic")
check(registry_a.registry_id == registry_a.expected_id(), "registry id stable")
check(validate_rsoc_language_operator_registry(registry_a).ok, "registry validates")
check(len(registry_a.operators) == 10, "registry length exact")
check(registry_a.exact_operator_count == 10, "declared count exact")
check(registry_a.default_runtime_enabled is False, "registry disabled")
check(registry_a.operator_application_available is False, "application unavailable")
check(registry_a.source_binding_available is False, "source binding unavailable")
check(registry_a.phase_assignment_available is False, "phase assignment unavailable")
check(registry_a.legacy_imports_allowed is False, "legacy imports disabled")
check(registry_a.mea_substitution_allowed is False, "MEA substitution disabled")
check(registry_a.hidden_fallback_allowed is False, "hidden fallback disabled")

expected = (
    ("resonance_merge", "⟁", "Resonance Merge", OperatorArity.BINARY),
    ("resonance_severance", "⧧", "Resonance Severance", OperatorArity.BINARY),
    ("recursive_amplification", "⧒", "Recursive Amplification", OperatorArity.UNARY),
    ("symbolic_discharge", "⧀", "Symbolic Discharge / Collapse", OperatorArity.UNARY),
    ("recursive_lock", "⧙", "Recursive Lock / Fusion", OperatorArity.BINARY),
    ("recursive_memory_integral", "⧜", "Recursive Integration / Memory", OperatorArity.UNARY),
    ("christ_function", "χ(t)", "Christ Function / Grace Override", OperatorArity.UNARY),
    ("resurrection_reload", "R̂", "Resurrection Reload", OperatorArity.UNARY),
    ("controlled_archival", "Ĉ", "Controlled Archival", OperatorArity.UNARY),
    ("echo_validation", "Ê", "Echo Validation", OperatorArity.UNARY),
)
check(tuple((x.operator_key, x.glyph, x.canonical_name, x.arity) for x in registry_a.operators) == expected, "operator catalog exact")
check(len({x.operator_key for x in registry_a.operators}) == 10, "operator keys unique")
check(len({x.glyph for x in registry_a.operators}) == 10, "glyphs unique")
check(len({x.contract_id for x in registry_a.operators}) == 10, "contract ids unique")
check(sum(x.may_decrease_entropy for x in registry_a.operators) == 1, "entropy decrease exclusive")

for item in registry_a.operators:
    check(item.contract_id == item.expected_id(), f"stable operator id {item.operator_key}")
    check(validate_rsoc_operator_contract(item).ok, f"operator validates {item.operator_key}")
    check(item.runtime_status is OperatorRuntimeStatus.CONTRACT_ONLY_DISABLED, f"contract only {item.operator_key}")
    check(item.domain_schema_id == FIELD_SCHEMA_ID, f"domain exact {item.operator_key}")
    check(item.range_schema_id == FIELD_SCHEMA_ID, f"range exact {item.operator_key}")
    check(item.runtime_enabled is False, f"runtime false {item.operator_key}")
    check(item.application_implemented is False, f"application false {item.operator_key}")
    check(item.automatic_trigger_authorized is False, f"trigger false {item.operator_key}")
    check(item.source_binding_authorized is False, f"source binding false {item.operator_key}")
    check(item.phase_assignment_authorized is False, f"phase false {item.operator_key}")
    check(item.meaning_authorized is False, f"meaning false {item.operator_key}")
    check(item.memory_authorized is False, f"memory false {item.operator_key}")
    check(item.route_authorized is False, f"route false {item.operator_key}")
    check(item.tool_authorized is False, f"tool false {item.operator_key}")
    check(item.action_authorized is False, f"action false {item.operator_key}")
    check(item.delivery_authorized is False, f"delivery false {item.operator_key}")
    check(item.entropy_thresholds_installed is False, f"threshold false {item.operator_key}")
    check(item.commutation_table_installed is False, f"commutation false {item.operator_key}")
    check(item.numeric_transform_installed is False, f"numeric transform false {item.operator_key}")
    check(bool(item.source_authority_refs), f"authority refs present {item.operator_key}")
    check(bool(item.hard_boundaries), f"hard boundary present {item.operator_key}")

christ = operator_contract_for_key("christ_function", registry_a)
check(christ is not None, "christ found")
check(christ.glyph == "χ(t)", "christ glyph")
check(christ.may_decrease_entropy is True, "christ exclusive entropy permission")
check(christ.identity_handling is LineageIdentityHandling.CONTROLLED_MASK_ONLY_UNDER_LATER_AUTHORITY, "christ identity handling")
archival = operator_contract_for_glyph("Ĉ", registry_a)
check(archival is not None, "archival found")
check(archival.identity_handling is LineageIdentityHandling.CONTROLLED_MASK_ONLY_UNDER_LATER_AUTHORITY, "archival identity handling")
for item in registry_a.operators:
    if item.operator_key not in {"christ_function", "controlled_archival"}:
        check(item.identity_handling is LineageIdentityHandling.COPY_UNCHANGED, f"identity copied {item.operator_key}")
        check(item.may_decrease_entropy is False, f"entropy decrease denied {item.operator_key}")
check(operator_contract_for_key("missing", registry_a) is None, "unknown key none")
check(operator_contract_for_key(1, registry_a) is None, "non-text key none")
check(operator_contract_for_glyph("?", registry_a) is None, "unknown glyph none")
check(operator_contract_for_glyph(None, registry_a) is None, "non-text glyph none")

capture = capture_input_event(
    "  Do not install it.\r\n",
    source_id="fixture.user",
    channel_id="fixture.chat",
    sequence_number=36,
    correlation_id="slice36b0:field",
)
check(capture.status is InputCustodyStatus.CAPTURED_SUPPORTED, "fixture custody supported")
field_result_a = build_unprojected_language_field(capture.event)
field_result_b = build_unprojected_language_field(capture.event)
check(field_result_a == field_result_b, "field build deterministic")
check(field_result_a.status is FieldEnvelopeBuildStatus.CREATED_UNPROJECTED, "field build status")
check(field_result_a.envelope_created is True, "field created")
check(field_result_a.structural_progression_allowed is False, "field progression held")
check(field_result_a.result_id == field_result_a.expected_id(), "field result id stable")
check(validate_field_envelope_build_result(field_result_a).ok, "field result valid")
field = field_result_a.field
check(field is not None, "field present")
check(field.field_id == field.expected_id(), "field id stable")
check(validate_resonant_language_field(field).ok, "field valid")
check(field.source_event_id == capture.event.input_event_id, "source event linked")
check(field.source_sha256 == capture.event.source_sha256, "source hash linked")
check(field.source_utf8_byte_length == capture.event.utf8_byte_length, "byte length linked")
check(field.source_code_point_length == capture.event.code_point_length, "code point length linked")
check(field.root_source_span_id == capture.event.root_source_span_id, "root span linked")
check(field.projection_status is FieldProjectionStatus.UNPROJECTED, "field unprojected")
check(field.phase_status is FieldPhaseStatus.UNASSIGNED, "phase unassigned")
check(field.support_status is FieldSupportStatus.UNASSESSED, "support unassessed")
check(field.covered_source_span_ids == (), "no covered spans")
check(field.unresolved_source_span_ids == (capture.event.root_source_span_id,), "root unresolved")
check(field.predecessor_field_id is None, "no predecessor")
check(field.applied_operator_trace_ids == (), "no operator ancestry")
check(not hasattr(field, "exact_received_text"), "field does not copy source text")
for name in (
    "rsoc_lineage_identity_assigned",
    "source_text_copied_or_replaced",
    "tokenization_performed",
    "operator_binding_performed",
    "operator_application_performed",
    "phase_assignment_performed",
    "concept_lookup_performed",
    "predicate_binding_performed",
    "meaning_created",
    "reference_resolution_performed",
    "legacy_runtime_consulted",
    "filesystem_read_performed",
    "filesystem_write_performed",
    "network_access_performed",
    "environment_access_performed",
    "memory_read_performed",
    "memory_write_performed",
    "route_registration_performed",
    "tool_routing_performed",
    "action_performed",
    "delivery_performed",
):
    check(getattr(field, name) is False, f"field consequence false {name}")

unsupported_capture = capture_input_event(
    "supported\ue000held",
    source_id="fixture.user",
    channel_id="fixture.chat",
    sequence_number=37,
)
check(unsupported_capture.status is InputCustodyStatus.CAPTURED_UNSUPPORTED, "unsupported fixture held by 36A")
unsupported_field = build_unprojected_language_field(unsupported_capture.event)
check(unsupported_field.status is FieldEnvelopeBuildStatus.HELD_UNSUPPORTED_INPUT, "unsupported held")
check(unsupported_field.envelope_created is False, "unsupported no envelope")
check(unsupported_field.field is None, "unsupported field absent")
check(validate_field_envelope_build_result(unsupported_field).ok, "unsupported result valid")
invalid_field = build_unprojected_language_field("not an event")
check(invalid_field.status is FieldEnvelopeBuildStatus.REJECTED_INVALID_INPUT_EVENT, "invalid type rejected")
check(invalid_field.field is None, "invalid field absent")
check(validate_field_envelope_build_result(invalid_field).ok, "invalid result valid")
tampered_event = replace(capture.event, source_sha256="0" * 64)
tampered_field = build_unprojected_language_field(tampered_event)
check(tampered_field.status is FieldEnvelopeBuildStatus.REJECTED_INVALID_INPUT_EVENT, "tampered event rejected")
check(tampered_field.validation_issue_codes, "tampered typed issues")

for item in registry_a.operators:
    decision = evaluate_operator_application(field, item.operator_key)
    check(decision.status is OperatorApplicationStatus.REFUSED_CONTRACT_ONLY, f"application refused {item.operator_key}")
    check(decision.operator_found is True, f"operator found {item.operator_key}")
    check(decision.application_performed is False, f"no application {item.operator_key}")
    check(decision.successor_field_created is False, f"no successor {item.operator_key}")
    check(decision.phase_assigned is False, f"no phase {item.operator_key}")
    check(decision.meaning_created is False, f"no meaning {item.operator_key}")
    check(decision.decision_id == decision.expected_id(), f"decision id stable {item.operator_key}")
    check(validate_operator_application_decision(decision).ok, f"decision validates {item.operator_key}")
unknown_decision = evaluate_operator_application(field, "unknown")
check(unknown_decision.status is OperatorApplicationStatus.REFUSED_UNKNOWN_OPERATOR, "unknown operator typed")
check(unknown_decision.operator_found is False, "unknown not found")
invalid_decision = evaluate_operator_application(object(), "resonance_merge")
check(invalid_decision.status is OperatorApplicationStatus.REFUSED_INVALID_FIELD, "invalid field typed")
check(validate_operator_application_decision(invalid_decision).ok, "invalid decision valid")

catalog_a = build_default_legacy_isolation_catalog()
catalog_b = build_default_legacy_isolation_catalog()
check(catalog_a == catalog_b, "isolation deterministic")
check(catalog_a.catalog_id == catalog_a.expected_id(), "catalog id stable")
check(validate_legacy_isolation_catalog(catalog_a).ok, "catalog validates")
check(len(catalog_a.records) == 14, "isolation record count")
check(len({x.surface_path for x in catalog_a.records}) == 14, "isolation paths unique")
check(catalog_a.legacy_imports_allowed is False, "catalog imports false")
check(catalog_a.legacy_calls_allowed is False, "catalog calls false")
check(catalog_a.legacy_language_authority_allowed is False, "catalog language authority false")
check(catalog_a.mea_substitution_allowed is False, "catalog mea substitution false")
check(catalog_a.static_reference_only is True, "catalog static reference true")
for record in catalog_a.records:
    check(record.isolation_id == record.expected_id(), f"isolation id stable {record.surface_path}")
    check(validate_legacy_isolation_record(record).ok, f"isolation validates {record.surface_path}")
    check(record.import_allowed is False, f"import false {record.surface_path}")
    check(record.call_allowed is False, f"call false {record.surface_path}")
    check(record.language_authority_allowed is False, f"language authority false {record.surface_path}")
    check(record.semantic_authority_allowed is False, f"semantic authority false {record.surface_path}")
    check(record.runtime_substitution_allowed is False, f"substitution false {record.surface_path}")
phase_parser_isolation = isolation_record_for_surface("rmc_engine_v1.phase_parser", catalog_a)
check(phase_parser_isolation.category is LegacySurfaceCategory.WITHDRAWN_LEGACY_LANGUAGE, "phase parser category")
check(phase_parser_isolation.disposition is LegacySurfaceDisposition.ISOLATED_NO_IMPORT_OR_CALL, "phase parser disposition")
mea_isolation = isolation_record_for_surface("rmc_engine_v1.mea.operator_engine", catalog_a)
check(mea_isolation.category is LegacySurfaceCategory.SEPARATE_DOMAIN_NOT_LANGUAGE_AUTHORITY, "mea category")
check(mea_isolation.disposition is LegacySurfaceDisposition.SEPARATE_DOMAIN_NO_SUBSTITUTION, "mea disposition")
check(isolation_record_for_surface("missing", catalog_a) is None, "missing isolation none")
check(isolation_record_for_surface(3, catalog_a) is None, "non-text isolation none")

# Frozen records and validation escalation checks.
try:
    registry_a.default_runtime_enabled = True  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("registry is mutable")
try:
    field.meaning_created = True  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("field is mutable")
check(not validate_rsoc_language_operator_registry(replace(registry_a, hidden_fallback_allowed=True)).ok, "fallback escalation rejected")
check(not validate_rsoc_operator_contract(replace(christ, automatic_trigger_authorized=True)).ok, "automatic trigger rejected")
check(not validate_rsoc_operator_contract(replace(christ, entropy_thresholds_installed=True)).ok, "threshold escalation rejected")
merge = operator_contract_for_key("resonance_merge", registry_a)
check(not validate_rsoc_operator_contract(replace(merge, may_decrease_entropy=True)).ok, "non-christ entropy decrease rejected")
check(not validate_resonant_language_field(replace(field, phase_assignment_performed=True)).ok, "phase escalation rejected")
check(not validate_resonant_language_field(replace(field, legacy_runtime_consulted=True)).ok, "legacy consultation rejected")
check(not validate_legacy_isolation_catalog(replace(catalog_a, mea_substitution_allowed=True)).ok, "mea substitution escalation rejected")

# Explicit import must not load legacy RMC modules.
legacy_before = {name for name in sys.modules if name == "rmc_engine_v1" or name.startswith("rmc_engine_v1.")}
import aiweb_language_core_bootstrap.resonant_language_operator_contract as explicit_package
legacy_after = {name for name in sys.modules if name == "rmc_engine_v1" or name.startswith("rmc_engine_v1.")}
check(legacy_before == legacy_after, "explicit package import loads no legacy RMC")
check(len(explicit_package.__all__) == 44, "export count exact")

# Runtime paths remain in-memory and offline under booby-trapped external APIs.
with ExitStack() as stack:
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "read_bytes", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(os, "getenv", forbidden))
    stack.enter_context(patch.object(os, "system", forbidden))
    stack.enter_context(patch.object(subprocess, "run", forbidden))
    stack.enter_context(patch.object(subprocess, "Popen", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    trapped_registry = build_default_rsoc_operator_registry()
    trapped_catalog = build_default_legacy_isolation_catalog()
    trapped_field = build_unprojected_language_field(capture.event)
    trapped_decision = evaluate_operator_application(trapped_field.field, "resonance_merge")
check(validate_rsoc_language_operator_registry(trapped_registry).ok, "trapped registry valid")
check(validate_legacy_isolation_catalog(trapped_catalog).ok, "trapped catalog valid")
check(validate_field_envelope_build_result(trapped_field).ok, "trapped field valid")
check(validate_operator_application_decision(trapped_decision).ok, "trapped decision valid")

print("SLICE 36B0 BEHAVIOR TEST: PASS")
print(f"checks={checks}")
print(f"registry_id={registry_a.registry_id}")
print(f"operator_count={len(registry_a.operators)}")
print(f"legacy_isolation_records={len(catalog_a.records)}")
print(f"field_id={field.field_id}")
print("operator_phase_meaning_memory_route_tool_action_delivery_effects=0")
