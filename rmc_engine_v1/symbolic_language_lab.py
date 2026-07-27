"""Read-only Forge adapter for imported RSOC reference inspection.

The imported names and glyphs are evidence about an earlier design.  They do
not define the Forge meaning algebra and cannot become language authority.
"""

from __future__ import annotations

from aiweb_language_core_bootstrap.input_event_custody import (
    build_input_custody_limits,
    capture_input_event,
)
from aiweb_language_core_bootstrap.resonant_language_operator_contract import (
    build_default_rsoc_operator_registry,
)
from aiweb_language_core_bootstrap.rsoc_symbolic_reference_preview import (
    build_reference_boundary,
    preview_rsoc_operator_references,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    build_source_field_projection_limits,
    project_source_field,
    reconstruct_source_field,
)

API_CONTRACT = "forge_operator_console_api_v1"
ENDPOINT = "/api/rmc/symbolic-language-preview"
MAX_SOURCE_CODE_POINTS = 4_096
MAX_SOURCE_UTF8_BYTES = 16_384


def _operator_catalog(registry) -> list[dict[str, object]]:
    return [
        {
            "operator_key": item.operator_key,
            "glyph": item.glyph,
            "canonical_name": item.canonical_name,
            "authority_status": "REFERENCE_ONLY",
            "forge_meaning_authority": False,
            "declared_arity": item.arity.value,
            "contract_id": item.contract_id,
            "runtime_status": item.runtime_status.value,
            "runtime_enabled": item.runtime_enabled,
            "source_binding_authorized": item.source_binding_authorized,
            "application_implemented": item.application_implemented,
            "meaning_authorized": item.meaning_authorized,
            "memory_authorized": item.memory_authorized,
            "delivery_authorized": item.delivery_authorized,
        }
        for item in registry.operators
    ]


def _grammar_boundary() -> dict[str, object]:
    return {
        "authoritative_expression_grammar_installed": False,
        "accepted_preview_document": (
            "exact registered glyph references, adjacent or separated only by "
            "ASCII space, tab, carriage return, or line feed"
        ),
        "operand_syntax_installed": False,
        "precedence_installed": False,
        "composition_law_installed": False,
        "compatibility_table_installed": False,
        "numeric_transform_installed": False,
        "phase_transition_executor_installed": False,
        "reference_sources_only": True,
        "drive_definitions_required_before_transition_law": False,
        "forge_owned_meaning_algebra_separate": True,
    }


def _invalid_request(reason_code: str, registry) -> dict[str, object]:
    return {
        "status": "ERROR",
        "reason_code": reason_code,
        "api_contract": API_CONTRACT,
        "endpoint": ENDPOINT,
        "read_only": True,
        "reference_authority": "REFERENCE_ONLY",
        "operator_catalog": _operator_catalog(registry),
        "grammar_boundary": _grammar_boundary(),
        "boundary": build_reference_boundary(
            recognition_performed=False,
        ).to_dict(),
    }


def build_symbolic_language_preview_response(request: object) -> dict[str, object]:
    """Return one deterministic response and perform no external side effects."""

    registry = build_default_rsoc_operator_registry()
    if type(request) is not dict:
        return _invalid_request("request_must_be_json_object", registry)
    if set(request) != {"source_text"}:
        return _invalid_request("request_requires_exact_source_text_field_only", registry)
    source_text = request.get("source_text")
    if type(source_text) is not str:
        return _invalid_request("source_text_must_be_string", registry)

    custody_limits = build_input_custody_limits(
        max_utf8_bytes=MAX_SOURCE_UTF8_BYTES,
        max_code_points=MAX_SOURCE_CODE_POINTS,
        max_recorded_conditions=256,
        allow_empty=False,
    )
    projection_limits = build_source_field_projection_limits(
        max_code_points=MAX_SOURCE_CODE_POINTS,
        max_observations=16_384,
    )
    assert custody_limits is not None
    assert projection_limits is not None

    custody = capture_input_event(
        source_text,
        source_id="forge.operator_console.symbolic_language_lab",
        channel_id="api.rmc.symbolic_language_preview",
        correlation_id="rsoc-symbolic-reference-preview-v1",
        limits=custody_limits,
    )
    projection = project_source_field(custody.event, limits=projection_limits)
    preview = preview_rsoc_operator_references(custody, projection, registry)

    reconstruction = None
    if projection.projection is not None:
        reconstruction = reconstruct_source_field(projection.projection)

    encoded = b""
    try:
        encoded = source_text.encode("utf-8", "strict")
    except UnicodeError:
        pass

    return {
        "status": "OK" if preview.ready else "HELD",
        "reason_code": preview.reason_code,
        "api_contract": API_CONTRACT,
        "endpoint": ENDPOINT,
        "mode": "exact_rsoc_operator_reference_preview",
        "read_only": True,
        "reference_authority": "REFERENCE_ONLY",
        "source": {
            "exact_text": source_text,
            "utf8_hex": encoded.hex(),
            "source_sha256": custody.observed_source_sha256,
            "code_point_length": custody.observed_code_point_length,
            "utf8_byte_length": custody.observed_utf8_byte_length,
            "normalization_performed": False,
            "tokenization_performed": False,
        },
        "custody": {
            "status": custody.status.value,
            "reason_code": custody.reason_code,
            "result_id": custody.result_id,
            "source_event_id": custody.event.input_event_id if custody.event else "",
            "source_preserved_exactly": bool(
                custody.event and custody.event.source_preserved_exactly
            ),
            "structural_progression_allowed": custody.structural_progression_allowed,
            "condition_codes": [condition.code.value for condition in custody.conditions],
        },
        "projection": {
            "status": projection.status.value,
            "reason_code": projection.reason_code,
            "result_id": projection.result_id,
            "projection_id": projection.projection.projection_id if projection.projection else "",
            "exact_reconstruction_proven": bool(
                projection.projection and projection.projection.exact_reconstruction_proven
            ),
            "normalization_performed": bool(
                projection.projection and projection.projection.normalization_performed
            ),
            "tokenization_performed": bool(
                projection.projection and projection.projection.tokenization_performed
            ),
        },
        "reconstruction": reconstruction.to_dict() if reconstruction else None,
        "registry": {
            "registry_id": registry.registry_id,
            "operator_count": len(registry.operators),
            "runtime_enabled": registry.default_runtime_enabled,
            "operator_application_available": registry.operator_application_available,
            "source_binding_available": registry.source_binding_available,
            "phase_assignment_available": registry.phase_assignment_available,
            "reference_only": True,
            "creates_forge_meaning_authority": False,
        },
        "operator_catalog": _operator_catalog(registry),
        "reference_preview": preview.to_dict(),
        "grammar_boundary": _grammar_boundary(),
        "boundary": preview.boundary.to_dict(),
    }
