#!/usr/bin/env python3
"""Behavior, Unicode, boundary, and route tests for the symbolic reference lab."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import builtins
import json
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
    build_default_rsoc_operator_registry,
)
from aiweb_language_core_bootstrap.rsoc_symbolic_reference_preview import (
    RsocReferencePreviewStatus,
    SourceCoverageKind,
    build_reference_preview_limits,
    preview_rsoc_operator_references,
    validate_reference_preview_result,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    project_source_field,
    reconstruct_source_field,
)
from rmc_engine_v1.symbolic_language_lab import (
    build_symbolic_language_preview_response,
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1


def forbidden(*args, **kwargs):
    raise AssertionError("forbidden external side effect attempted")


def source_records(text: str):
    custody = capture_input_event(
        text,
        source_id="test.symbolic_lab",
        channel_id="test",
        correlation_id="test-rsoc-reference-preview",
    )
    projection = project_source_field(custody.event)
    return custody, projection


registry = build_default_rsoc_operator_registry()
expected = tuple(
    (item.operator_key, item.glyph, item.canonical_name, item.arity.value)
    for item in registry.operators
)
all_source = " ".join(item.glyph for item in registry.operators)
custody, projection = source_records(all_source)
result_a = preview_rsoc_operator_references(custody, projection, registry)
result_b = preview_rsoc_operator_references(custody, projection, registry)

check(custody.status is InputCustodyStatus.CAPTURED_SUPPORTED, "all glyphs pass custody")
check(projection.projection is not None, "all glyphs project")
check(result_a == result_b, "preview deterministic")
check(result_a.result_id == result_a.expected_id(), "result stable id")
check(result_a.status is RsocReferencePreviewStatus.REFERENCE_PREVIEW_READY, "all glyphs ready")
check(result_a.ready is True, "ready flag true")
check(result_a.recognized_operator_count == 10, "ten references recognized")
check(result_a.unrecognized_segment_count == 0, "no unrecognized source")
check(result_a.unresolved_code_point_count == 0, "no unresolved code points")
check(result_a.scan_complete is True, "scan complete")
check(result_a.full_source_coverage is True, "full source coverage")
check(result_a.exact_reconstruction_proven is True, "reconstruction proof carried")
check(result_a.document is not None, "reference document created")
check(result_a.document.document_id == result_a.document.expected_id(), "document stable id")
check(result_a.document.full_input_consumed is True, "document consumes exact input")
check(result_a.document.composition_interpreted is False, "no composition inferred")
check(result_a.document.arguments_bound is False, "no operands bound")
check(result_a.document.operator_application_performed is False, "no application")
check(result_a.document.meaning_created is False, "no meaning")
check(validate_reference_preview_result(result_a).ok, "result validates")
check(
    tuple(
        (node.operator_key, node.glyph, node.canonical_name, node.declared_arity)
        for node in result_a.operator_references
    ) == expected,
    "registry identity and arity preserved",
)

for segment in result_a.coverage:
    check(segment.segment_id == segment.expected_id(), f"segment stable {segment.ordinal}")
    check(
        segment.exact_text == all_source[segment.code_point_start:segment.code_point_end],
        f"segment exact slice {segment.ordinal}",
    )
for node in result_a.operator_references:
    check(node.reference_id == node.expected_id(), f"reference stable {node.operator_key}")
    check(node.registry_reference_only is True, f"reference-only {node.operator_key}")
    for false_name in (
        "source_binding_performed",
        "operator_application_performed",
        "numeric_transform_performed",
        "entropy_mutation_performed",
        "phase_assignment_performed",
        "meaning_created",
        "permission_inferred",
    ):
        check(getattr(node, false_name) is False, f"{false_name} false {node.operator_key}")

chi = next(node for node in result_a.operator_references if node.glyph == "χ(t)")
reload_ref = next(node for node in result_a.operator_references if node.glyph == "R̂")
check(chi.code_point_end - chi.code_point_start == 4, "chi atomic four code points")
check(chi.utf8_byte_end - chi.utf8_byte_start == len("χ(t)".encode("utf-8")), "chi exact byte span")
check(len(chi.atom_ids) == 4, "chi linked to four source atoms")
check(reload_ref.code_point_end - reload_ref.code_point_start == 2, "reload atomic two code points")
check(reload_ref.utf8_byte_end - reload_ref.utf8_byte_start == len("R̂".encode("utf-8")), "reload exact byte span")
check(len(reload_ref.atom_ids) == 2, "reload linked to two source atoms")

reconstruction = reconstruct_source_field(projection.projection)
check(reconstruction.ok, "source reconstructs")
check(reconstruction.reconstructed_text == all_source, "reconstruction exact text")
check(reconstruction.reconstructed_utf8_hex == all_source.encode("utf-8").hex(), "reconstruction exact bytes")

adjacent_custody, adjacent_projection = source_records("⟁⧧ÊÊ")
adjacent = preview_rsoc_operator_references(adjacent_custody, adjacent_projection)
check(adjacent.ready, "adjacent references accepted")
check(tuple(node.glyph for node in adjacent.operator_references) == ("⟁", "⧧", "Ê", "Ê"), "adjacent order exact")
check(all(segment.kind is SourceCoverageKind.OPERATOR_REFERENCE for segment in adjacent.coverage), "adjacent has no invented separators")

for exact in ("Ĉ", "Ê", "R̂", "χ(t)"):
    exact_custody, exact_projection = source_records(exact)
    exact_result = preview_rsoc_operator_references(exact_custody, exact_projection)
    check(exact_result.ready, f"canonical exact form accepted {exact}")
    check(exact_result.operator_references[0].glyph == exact, f"canonical exact glyph returned {exact}")

for noncanonical in (
    "Ĉ",
    "Ê",
    "R^",
    "Rˆ",
    "chi(t)",
    "x(t)",
    "Χ(t)",
    "х(t)",
    "χ (t)",
    "χ(τ)",
    "†",
    "‡",
):
    held_custody, held_projection = source_records(noncanonical)
    held = preview_rsoc_operator_references(held_custody, held_projection)
    check(not held.ready, f"spoof held {noncanonical!r}")
    check(held.document is None, f"spoof has no document {noncanonical!r}")
    check(held.recognized_operator_count == 0, f"spoof not recognized {noncanonical!r}")
    check(held.boundary.normalization_performed is False, f"spoof not normalized {noncanonical!r}")

mixed_custody, mixed_projection = source_records("Please Ê this")
mixed = preview_rsoc_operator_references(mixed_custody, mixed_projection)
check(mixed.status is RsocReferencePreviewStatus.HELD_UNCONSUMED_SOURCE, "natural text held")
check(mixed.recognized_operator_count == 1, "reference remains observable in held text")
check(mixed.document is None, "partial source creates no document")
check(mixed.full_source_coverage is True, "held text still receives exact coverage")
check(mixed.unresolved_code_point_count == len("Please") + len("this"), "unresolved count exact")

whitespace_custody, whitespace_projection = source_records(" \t\r\n")
whitespace = preview_rsoc_operator_references(whitespace_custody, whitespace_projection)
check(whitespace.status is RsocReferencePreviewStatus.HELD_NO_OPERATOR_REFERENCE, "separator-only held")
check(whitespace.full_source_coverage, "separator-only coverage exact")
check(whitespace.separator_segment_count == 1, "separators grouped")

unsupported_custody, unsupported_projection = source_records("Ê\u200b")
unsupported = preview_rsoc_operator_references(unsupported_custody, unsupported_projection)
check(unsupported.status is RsocReferencePreviewStatus.HELD_UNSUPPORTED_SOURCE, "format control held before scan")
check(unsupported.recognized_operator_count == 0, "unsupported input not partially advanced")

tampered_projection_record = replace(projection.projection, source_sha256="0" * 64)
tampered_projection = replace(projection, projection=tampered_projection_record)
tampered_projection_result = preview_rsoc_operator_references(custody, tampered_projection, registry)
check(tampered_projection_result.status is RsocReferencePreviewStatus.HELD_INVALID_PROJECTION, "tampered projection held")

tampered_registry = replace(registry, exact_operator_count=11)
tampered_registry_result = preview_rsoc_operator_references(custody, projection, tampered_registry)
check(tampered_registry_result.status is RsocReferencePreviewStatus.HELD_INVALID_REGISTRY, "tampered registry held")

small_limits = build_reference_preview_limits(max_operator_references=1, max_coverage_segments=4)
check(small_limits is not None, "small limits build")
limited = preview_rsoc_operator_references(adjacent_custody, adjacent_projection, limits=small_limits)
check(limited.status is RsocReferencePreviewStatus.HELD_PREVIEW_LIMIT_EXCEEDED, "reference limit held")
check(limited.document is None, "limit creates no document")
check(limited.scan_complete is False, "limited scan marked incomplete")
check(limited.coverage[-1].kind is SourceCoverageKind.LIMIT_REMAINDER, "limit remainder exact")

try:
    result_a.status = RsocReferencePreviewStatus.HELD_INVALID_CUSTODY
    raise AssertionError("result unexpectedly mutable")
except (FrozenInstanceError, AttributeError):
    check(True, "result frozen")

boundary = result_a.boundary.to_dict()
for true_name in ("read_only", "registry_reference_only", "exact_glyph_recognition_performed"):
    check(boundary[true_name] is True, f"boundary true {true_name}")
for false_name, state in boundary.items():
    if false_name not in {"read_only", "registry_reference_only", "exact_glyph_recognition_performed"}:
        check(state is False, f"boundary false {false_name}")

response_a = build_symbolic_language_preview_response({"source_text": all_source})
response_b = build_symbolic_language_preview_response({"source_text": all_source})
check(response_a == response_b, "API response deterministic")
check(response_a["status"] == "OK", "API ready")
check(response_a["endpoint"] == "/api/rmc/symbolic-language-preview", "API endpoint exact")
check(response_a["source"]["exact_text"] == all_source, "API exact source echo")
check(response_a["source"]["tokenization_performed"] is False, "API no tokenization")
check(response_a["source"]["normalization_performed"] is False, "API no normalization")
check(response_a["reconstruction"]["reconstructed_text"] == all_source, "API reconstruction exact")
check(response_a["registry"]["operator_count"] == 10, "API catalog count")
check(response_a["registry"]["operator_application_available"] is False, "API application unavailable")
check(response_a["grammar_boundary"]["authoritative_expression_grammar_installed"] is False, "API grammar boundary visible")
check(response_a["grammar_boundary"]["drive_definitions_required_before_transition_law"] is False, "API Drive references do not gate Forge law")
check(response_a["grammar_boundary"]["reference_sources_only"] is True, "API imported sources remain reference-only")
check(response_a["reference_authority"] == "REFERENCE_ONLY", "API refuses imported language authority")
check(len(response_a["operator_catalog"]) == 10, "API ten catalog entries")
round_tripped_response = json.loads(json.dumps(response_a, ensure_ascii=False))
check(round_tripped_response["source"]["exact_text"] == all_source, "API JSON preserves exact Unicode source")
check(round_tripped_response["reference_preview"]["recognized_operator_count"] == 10, "API JSON preserves preview")

for bad_request in (None, [], {}, {"source_text": "Ê", "extra": True}, {"source_text": 1}):
    bad = build_symbolic_language_preview_response(bad_request)
    check(bad["status"] == "ERROR", f"invalid API request rejected {bad_request!r}")
    check(bad["read_only"] is True, f"invalid API request remains read only {bad_request!r}")

empty_response = build_symbolic_language_preview_response({"source_text": ""})
check(empty_response["status"] == "HELD", "empty source held")
check(empty_response["reference_preview"]["ready"] is False, "empty source no preview document")
oversized_response = build_symbolic_language_preview_response({"source_text": "Ê" * 4_097})
check(oversized_response["status"] == "HELD", "oversized source held")
check(oversized_response["reference_preview"]["recognized_operator_count"] == 0, "oversized source not scanned")

with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(Path, "open", forbidden))
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(socket, "create_connection", forbidden))
    stack.enter_context(patch.object(subprocess, "run", forbidden))
    stack.enter_context(patch.object(subprocess, "Popen", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(os, "getenv", forbidden))
    trapped = build_symbolic_language_preview_response({"source_text": "Ê ⧒ χ(t)"})
check(trapped["status"] == "OK", "API works under external-side-effect traps")

main_source = (REPO_ROOT / "main.py").read_text(encoding="utf-8")
check('"route_key":"symbolic_language_preview"' in main_source, "route manifest entry installed")
check('"method":"POST","path":"/api/rmc/symbolic-language-preview"' in main_source, "POST path manifest exact")
check('if _p281_req_path == "/api/rmc/symbolic-language-preview":' in main_source, "POST handler installed")
check("_gp015_ask_forge_math_trace_surface_v1" in main_source, "existing GP-015 helper retained")
check('elif self.path == "/api/operator/ask-forge/math-trace":' in main_source, "existing math route retained")

pure_sources = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((REPO_ROOT / "aiweb_language_core_bootstrap" / "rsoc_symbolic_reference_preview").glob("*.py"))
)
for forbidden_import in (
    "rmc_engine_v1",
    "fbsc_operator_crosswalk",
    "chi_correction_gate",
    "symbolic_math_operator_language_realizer",
):
    check(forbidden_import not in pure_sources, f"pure package isolates {forbidden_import}")

print(f"RSOC symbolic reference preview: {checks} checks passed")
