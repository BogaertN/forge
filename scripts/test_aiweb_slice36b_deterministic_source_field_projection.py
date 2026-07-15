#!/usr/bin/env python3
"""Behavior and adversarial tests for Slice 36B."""

from __future__ import annotations

import builtins
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import os
from pathlib import Path
import socket
import subprocess
import sys
import unicodedata
import urllib.request
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.input_event_custody import (
    InputCustodyStatus,
    build_input_custody_limits,
    capture_input_event,
)
from aiweb_language_core_bootstrap.resonant_language_operator_contract import (
    OperatorApplicationStatus,
    build_unprojected_language_field,
    evaluate_operator_application,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    ABSOLUTE_MAX_PROJECTION_CODE_POINTS,
    GraphemeBoundaryStatus,
    GraphemeProfileStatus,
    SourceFieldProjectionLimits,
    SourceFieldProjectionStatus,
    SourceFieldSupportStatus,
    SourceObservationKind,
    build_source_field_projection_limits,
    default_source_field_projection_limits,
    project_source_field,
    reconstruct_source_field,
    validate_source_boundary_record,
    validate_source_code_point_record,
    validate_source_field_projection,
    validate_source_field_projection_limits,
    validate_source_field_projection_result,
    validate_source_field_reconstruction_result,
    validate_source_observation_record,
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("external side effect attempted")


def capture(text: str, sequence: int = 1):
    result = capture_input_event(
        text,
        source_id="fixture.user",
        channel_id="fixture.chat",
        sequence_number=sequence,
    )
    check(result.event is not None, "fixture custody event created")
    return result


# Deterministic limits and typed invalid-limit handling.
limits_a = default_source_field_projection_limits()
limits_b = default_source_field_projection_limits()
check(limits_a == limits_b, "default limits deterministic")
check(limits_a.limits_id == limits_a.expected_id(), "default limits stable id")
check(validate_source_field_projection_limits(limits_a).ok, "limits validate")
custom_limits = build_source_field_projection_limits(
    max_code_points=128,
    max_observations=512,
)
check(custom_limits is not None, "custom limits built")
check(validate_source_field_projection_limits(custom_limits).ok, "custom limits valid")
check(build_source_field_projection_limits(max_code_points=True) is None, "bool limit refused")
check(
    build_source_field_projection_limits(
        max_code_points=ABSOLUTE_MAX_PROJECTION_CODE_POINTS + 1
    )
    is None,
    "absolute limit refused",
)
invalid_limits_result = project_source_field(capture("x", 2).event, limits=object())
check(
    invalid_limits_result.status
    is SourceFieldProjectionStatus.SOURCE_FIELD_MALFORMED,
    "invalid limits typed malformed",
)
check(not invalid_limits_result.projection_created, "invalid limits no projection")
check(validate_source_field_projection_result(invalid_limits_result).ok, "invalid limits result valid")

# Exact ASCII source projection and complete reversibility.
source = "Do not install it.\t  [x] + y\r\n\r\nNext"
custody = capture(source, 3)
check(custody.status is InputCustodyStatus.CAPTURED_SUPPORTED, "source supported")
result_a = project_source_field(custody.event)
result_b = project_source_field(custody.event)
check(result_a == result_b, "projection deterministic")
check(
    result_a.status is SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED,
    "supported status",
)
check(result_a.projection_created, "projection created")
check(result_a.structural_progression_allowed, "supported progression allowed")
check(result_a.source_preserved_in_custody, "custody preserved")
check(result_a.result_id == result_a.expected_id(), "result stable id")
check(validate_source_field_projection_result(result_a).ok, "result validates")
projection = result_a.projection
assert projection is not None
check(projection.projection_id == projection.expected_id(), "projection stable id")
check(validate_source_field_projection(projection).ok, "projection validates")
check(projection.source_event_id == custody.event.input_event_id, "event identity preserved")
check(projection.source_sha256 == custody.event.source_sha256, "source hash preserved")
check(projection.root_source_span_id == custody.event.root_source_span_id, "root span preserved")
check(projection.predecessor_field_envelope_id is not None, "36B0 predecessor linked")
check(projection.code_point_count == len(source), "code point count exact")
check(projection.boundary_count == len(source) + 1, "boundary count exact")
check(projection.source_utf8_byte_length == len(source.encode("utf-8")), "byte length exact")
check(projection.source_coverage_complete, "coverage complete")
check(projection.source_ordering_complete, "ordering complete")
check(projection.source_adjacency_complete, "adjacency complete")
check(projection.exact_reconstruction_proven, "reconstruction proven")
check(projection.grapheme_profile_status is GraphemeProfileStatus.COMPLETE_EXACT_ASCII_PROFILE, "ASCII grapheme profile complete")

reconstruction = reconstruct_source_field(projection)
check(reconstruction.ok, "reconstruction succeeds")
check(reconstruction.reconstructed_text == source, "text reconstructed exactly")
check(bytes.fromhex(reconstruction.reconstructed_utf8_hex) == source.encode("utf-8"), "bytes reconstructed exactly")
check(reconstruction.reconstructed_source_sha256 == custody.event.source_sha256, "reconstruction hash exact")
check(reconstruction.result_id == reconstruction.expected_id(), "reconstruction stable id")
check(validate_source_field_reconstruction_result(reconstruction).ok, "reconstruction result valid")

# Per-code-point identity, coordinates, ordering, adjacency and UTF-8 bytes.
for index, atom in enumerate(projection.code_points):
    check(atom.ordinal == index, f"atom ordinal {index}")
    check(atom.exact_text == source[index], f"atom exact text {index}")
    check(atom.unicode_code_point == f"U+{ord(source[index]):04X}", f"atom scalar {index}")
    check(bytes.fromhex(atom.utf8_hex) == source[index].encode("utf-8"), f"atom bytes {index}")
    check(atom.code_point_start == index and atom.code_point_end == index + 1, f"atom cp offsets {index}")
    check(atom.utf8_byte_start == custody.event.utf8_boundary_offsets[index], f"atom byte start {index}")
    check(atom.utf8_byte_end == custody.event.utf8_boundary_offsets[index + 1], f"atom byte end {index}")
    check(atom.atom_id == atom.expected_id(), f"atom stable id {index}")
    check(validate_source_code_point_record(atom).ok, f"atom validates {index}")
    expected_previous = projection.code_points[index - 1].atom_id if index else None
    expected_next = projection.code_points[index + 1].atom_id if index + 1 < len(source) else None
    check(atom.previous_atom_id == expected_previous, f"atom previous {index}")
    check(atom.next_atom_id == expected_next, f"atom next {index}")

for index, boundary in enumerate(projection.boundaries):
    check(boundary.ordinal == index, f"boundary ordinal {index}")
    check(boundary.code_point_offset == index, f"boundary cp offset {index}")
    check(boundary.utf8_byte_offset == custody.event.utf8_boundary_offsets[index], f"boundary byte offset {index}")
    check(boundary.boundary_id == boundary.expected_id(), f"boundary stable id {index}")
    check(validate_source_boundary_record(boundary).ok, f"boundary validates {index}")

crlf_index = source.index("\r\n") + 1
check(
    projection.boundaries[crlf_index].grapheme_boundary_status
    is GraphemeBoundaryStatus.EXACT_NON_BOUNDARY,
    "CRLF exact non-boundary",
)

# Closed visible observation classes, including overlapping surface facts.
kinds = tuple(item.kind for item in projection.observations)
for required_kind in (
    SourceObservationKind.GRAPHEME_CLUSTER,
    SourceObservationKind.VISIBLE_WHITESPACE,
    SourceObservationKind.REPEATED_WHITESPACE,
    SourceObservationKind.TAB,
    SourceObservationKind.LINE_BREAK,
    SourceObservationKind.PARAGRAPH_BOUNDARY,
    SourceObservationKind.PUNCTUATION_MARK,
    SourceObservationKind.DELIMITER_MARK,
    SourceObservationKind.OPERATOR_LIKE_SYMBOL,
    SourceObservationKind.CONTROL_CHARACTER,
):
    check(required_kind in kinds, f"observation kind present {required_kind.value}")
for observation in projection.observations:
    check(observation.observation_id == observation.expected_id(), "observation stable id")
    check(validate_source_observation_record(observation).ok, "observation validates")
    check(observation.exact_text == source[observation.code_point_start:observation.code_point_end], "observation source exact")
    check(observation.semantic_authority is False, "observation no semantic authority")
    check(observation.operator_binding_authority is False, "observation no operator authority")

# Visible words remain only ordered code points; no word token or semantic type exists.
install_start = source.index("install")
install_end = install_start + len("install")
check(
    not any(
        item.code_point_start == install_start
        and item.code_point_end == install_end
        for item in projection.observations
    ),
    "install not grouped as token",
)
for forbidden_field in (
    "noun",
    "verb",
    "adjective",
    "command",
    "request",
    "question",
    "concept",
    "predicate",
    "participant",
    "target",
    "prohibition",
    "permission",
    "phase",
    "operator",
    "intention",
    "meaning",
):
    check(not hasattr(projection, forbidden_field), f"no semantic field {forbidden_field}")

for flag in (
    "operator_application_available",
    "source_text_replaced",
    "normalization_performed",
    "casefolding_performed",
    "whitespace_collapse_performed",
    "transliteration_performed",
    "tokenization_performed",
    "vocabulary_lookup_performed",
    "part_of_speech_tagging_performed",
    "concept_lookup_performed",
    "predicate_binding_performed",
    "reference_resolution_performed",
    "operator_binding_performed",
    "operator_application_performed",
    "phase_assignment_performed",
    "intention_inference_performed",
    "meaning_created",
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
    check(getattr(projection, flag) is False, f"projection consequence false {flag}")

# Non-ASCII source remains exact while grapheme authority is conservatively held.
unicode_source = "caf\u00e9 / cafe\u0301 / \U0001f642 / \u4e2d\u6587"
unicode_custody = capture(unicode_source, 4)
unicode_result = project_source_field(unicode_custody.event)
check(unicode_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED, "Unicode supported")
unicode_projection = unicode_result.projection
assert unicode_projection is not None
check(unicode_projection.grapheme_profile_status is GraphemeProfileStatus.PARTIAL_CODE_POINT_FALLBACK, "Unicode grapheme fallback explicit")
check(any(item.grapheme_boundary_status is GraphemeBoundaryStatus.UNAVAILABLE for item in unicode_projection.boundaries), "unavailable grapheme boundaries visible")
check(reconstruct_source_field(unicode_projection).reconstructed_text == unicode_source, "Unicode exact reconstruction")
check(validate_source_field_projection(unicode_projection).ok, "Unicode projection validates")

# Canonically equivalent source forms remain distinct and are never normalized.
nfc = capture("\u00e9", 5)
nfd = capture("e\u0301", 6)
nfc_projection = project_source_field(nfc.event).projection
nfd_projection = project_source_field(nfd.event).projection
assert nfc_projection is not None and nfd_projection is not None
check(nfc.event.source_sha256 != nfd.event.source_sha256, "NFC and NFD custody hashes distinct")
check(nfc_projection.projection_id != nfd_projection.projection_id, "NFC and NFD projections distinct")
check(reconstruct_source_field(nfc_projection).reconstructed_text == "\u00e9", "NFC preserved")
check(reconstruct_source_field(nfd_projection).reconstructed_text == "e\u0301", "NFD preserved")

# Unsupported material remains visible and held from progression.
unsupported_text = "A\ue000B\u200dC\x01D\ufdd0"
unsupported_custody = capture(unsupported_text, 7)
check(unsupported_custody.status is InputCustodyStatus.CAPTURED_UNSUPPORTED, "unsupported custody captured")
unsupported_result = project_source_field(unsupported_custody.event)
check(unsupported_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED, "partial unsupported status")
check(unsupported_result.projection_created, "unsupported projection created")
check(not unsupported_result.structural_progression_allowed, "unsupported progression held")
unsupported_projection = unsupported_result.projection
assert unsupported_projection is not None
check(unsupported_projection.predecessor_field_envelope_id is None, "unsupported predecessor envelope held")
check(unsupported_projection.unsupported_code_point_count == 4, "all unsupported code points counted")
check(sum(atom.support_status is SourceFieldSupportStatus.UNSUPPORTED for atom in unsupported_projection.code_points) == 4, "unsupported atoms visible")
check(sum(item.kind is SourceObservationKind.UNSUPPORTED_CODE_POINT for item in unsupported_projection.observations) == 4, "unsupported observations visible")
check(reconstruct_source_field(unsupported_projection).reconstructed_text == unsupported_text, "unsupported exact reconstruction")
check(validate_source_field_projection_result(unsupported_result).ok, "unsupported result valid")

# Empty source is lawful only when 36A custody explicitly allowed it.
empty_custody_limits = build_input_custody_limits(allow_empty=True)
check(empty_custody_limits is not None, "empty custody limits built")
empty_capture = capture_input_event(
    "",
    source_id="fixture.user",
    channel_id="fixture.chat",
    sequence_number=8,
    limits=empty_custody_limits,
)
check(empty_capture.event is not None, "empty event captured")
empty_projection_result = project_source_field(empty_capture.event)
check(empty_projection_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED, "empty source supported")
empty_projection = empty_projection_result.projection
assert empty_projection is not None
check(empty_projection.code_point_count == 0, "empty atom count")
check(empty_projection.boundary_count == 1, "empty boundary count")
check(empty_projection.observation_count == 0, "empty observation count")
check(reconstruct_source_field(empty_projection).reconstructed_text == "", "empty reconstructed")

# Typed malformed, limit, and projection-failure dispositions.
invalid_event_result = project_source_field("not an input event")
check(invalid_event_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_MALFORMED, "invalid event typed malformed")
check(not invalid_event_result.projection_created, "invalid event no projection")
tampered_event = replace(custody.event, source_sha256="0" * 64)
tampered_result = project_source_field(tampered_event)
check(tampered_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_MALFORMED, "tampered event malformed")
small_limits = build_source_field_projection_limits(max_code_points=2, max_observations=50)
assert small_limits is not None
limited_result = project_source_field(custody.event, limits=small_limits)
check(limited_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_LIMIT_EXCEEDED, "code point limit typed")
observation_limits = build_source_field_projection_limits(max_code_points=100, max_observations=1)
assert observation_limits is not None
observation_limited = project_source_field(custody.event, limits=observation_limits)
check(observation_limited.status is SourceFieldProjectionStatus.SOURCE_FIELD_LIMIT_EXCEEDED, "observation limit typed")
unicode_version_tamper = replace(custody.event, unicode_database_version="0.0.0")
unicode_version_result = project_source_field(unicode_version_tamper)
check(unicode_version_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_MALFORMED, "tampered Unicode event rejected by custody validation")

# Reconstruction detects tampering without raising raw exceptions.
tampered_atom = replace(projection.code_points[0], utf8_hex="ff")
tampered_projection = replace(projection, code_points=(tampered_atom,) + projection.code_points[1:])
tampered_reconstruction = reconstruct_source_field(tampered_projection)
check(not tampered_reconstruction.ok, "tampered reconstruction fails typed")
check(tampered_reconstruction.validation_issue_codes, "tampered reconstruction issue codes")
check(not validate_source_field_projection(tampered_projection).ok, "tampered projection invalid")
check(not reconstruct_source_field(object()).ok, "invalid reconstruction type typed")

# Records are immutable.
try:
    projection.meaning_created = True  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("projection is mutable")
try:
    projection.code_points[0].exact_text = "X"  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("atom is mutable")

# 36B does not activate the 36B0 operator registry.
predecessor = build_unprojected_language_field(custody.event)
check(predecessor.field is not None, "predecessor field exists")
decision = evaluate_operator_application(predecessor.field, "resonance_merge")
check(decision.status is OperatorApplicationStatus.REFUSED_CONTRACT_ONLY, "operator remains disabled")
check(decision.application_performed is False, "operator not applied")

# Explicit import loads no legacy RMC modules.
legacy_before = {
    name
    for name in sys.modules
    if name == "rmc_engine_v1" or name.startswith("rmc_engine_v1.")
}
import aiweb_language_core_bootstrap.source_field_projection as explicit_package
legacy_after = {
    name
    for name in sys.modules
    if name == "rmc_engine_v1" or name.startswith("rmc_engine_v1.")
}
check(legacy_before == legacy_after, "explicit import loads no legacy RMC")
check(len(explicit_package.__all__) == 35, "export count exact")

# Projection remains in-memory and offline under booby-trapped external APIs.
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
    trapped_result = project_source_field(custody.event)
    trapped_reconstruction = reconstruct_source_field(trapped_result.projection)
check(validate_source_field_projection_result(trapped_result).ok, "trapped projection valid")
check(trapped_reconstruction.ok, "trapped reconstruction valid")

print("SLICE 36B BEHAVIOR TEST: PASS")
print(f"checks={checks}")
print(f"projection_id={projection.projection_id}")
print(f"code_points={projection.code_point_count}")
print(f"boundaries={projection.boundary_count}")
print(f"observations={projection.observation_count}")
print("token_concept_predicate_operator_phase_meaning_effects=0")
print("filesystem_network_memory_route_tool_action_delivery_effects=0")
