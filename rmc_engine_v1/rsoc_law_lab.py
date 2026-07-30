"""Strict read-only adapter for the Forge-owned typed RSOC law laboratory.

The public request contains an exact registered glyph plus fully structured
symbolic-field operands.  It accepts no prose, expression, source-text, field
identity, persistence, runtime, tool, action, or delivery instruction.
"""

from __future__ import annotations

from aiweb_language_core_bootstrap.rsoc_symbolic_law_lab import (
    RsocLawBoundary,
    SymbolicFieldState,
    build_symbolic_field_state,
    law_for_glyph,
    preview_rsoc_law,
    rsoc_law_registry,
)


API_CONTRACT = "forge_operator_console_api_v1"
ENDPOINT = "/api/rmc/rsoc-law-lab/preview"
ROUTE_KEY = "rsoc_law_lab_preview"

_BASE_REQUEST_FIELDS = frozenset({"glyph", "operands"})
_ECHO_REQUEST_FIELDS = frozenset(
    {"glyph", "operands", "expected_ancestry_ref"}
)
_OPERAND_FIELDS = frozenset(
    {
        "identity_refs",
        "phase_index",
        "recursion_depth",
        "drift_micro",
        "resonance_micro",
        "memory_charge_micro",
        "entropy_micro",
        "loop_ref",
        "echo_ancestry_refs",
        "lineage_refs",
        "locked",
        "archived",
        "grace_used",
        "revision",
    }
)
_REFERENCE_FIELDS = (
    "identity_refs",
    "echo_ancestry_refs",
    "lineage_refs",
)
_MAX_REFERENCES_PER_FIELD = 64
_MAX_REFERENCE_CODE_POINTS = 256


def _catalog() -> list[dict[str, object]]:
    return [
        {
            "law_id": law.law_id,
            "operator_key": law.operator_key,
            "glyph": law.glyph,
            "forge_provisional_name": law.forge_provisional_name,
            "declared_arity": law.declared_arity,
            "admitted_preview_operation": law.admitted_preview_operation,
            "reference_conflict_codes": list(law.reference_conflict_codes),
            "forge_owned": law.forge_owned,
            "provisional": law.provisional,
            "external_reference_authority": law.external_reference_authority,
            "runtime_enabled": law.runtime_enabled,
        }
        for law in rsoc_law_registry()
    ]


def _surface_boundary() -> dict[str, object]:
    boundary = RsocLawBoundary().to_dict()
    boundary.update(
        {
            "read_only": True,
            "structured_field_operands_required": True,
            "exact_registered_glyph_required": True,
            "caller_supplied_field_identity_allowed": False,
            "free_text_interpretation_performed": False,
            "normalization_performed": False,
            "persistence_performed": False,
            "runtime_invocation_performed": False,
            "operator_council_invoked": False,
            "ui_is_authority": False,
            "forge_governs": True,
        }
    )
    return boundary


def _request_contract() -> dict[str, object]:
    return {
        "request_fields": ["glyph", "operands"],
        "echo_additional_field": "expected_ancestry_ref",
        "operand_fields": sorted(_OPERAND_FIELDS),
        "operand_kind": "symbolic_field_state",
        "field_id_derived_by_forge": True,
        "free_text_fields": [],
        "maximum_operands": 2,
        "maximum_references_per_field": _MAX_REFERENCES_PER_FIELD,
        "maximum_reference_code_points": _MAX_REFERENCE_CODE_POINTS,
    }


def _invalid_response(reason_code: str) -> dict[str, object]:
    return {
        "status": "ERROR",
        "reason_code": reason_code,
        "api_contract": API_CONTRACT,
        "endpoint": ENDPOINT,
        "route_key": ROUTE_KEY,
        "mode": "forge_owned_typed_rsoc_law_preview",
        "read_only": True,
        "law_catalog": _catalog(),
        "request_contract": _request_contract(),
        "input_fields": [],
        "result": None,
        "output_fields": [],
        "echo_valid": None,
        "issue_codes": [reason_code],
        "trace": [],
        "boundary": _surface_boundary(),
        "receipt": None,
    }


def _bounded_references(value: object) -> bool:
    return (
        isinstance(value, (tuple, list))
        and len(value) <= _MAX_REFERENCES_PER_FIELD
        and all(
            type(item) is str
            and bool(item)
            and len(item) <= _MAX_REFERENCE_CODE_POINTS
            for item in value
        )
    )


def _build_operand(value: object) -> SymbolicFieldState:
    if type(value) is not dict:
        raise TypeError("operand_must_be_json_object")
    if set(value) != _OPERAND_FIELDS:
        raise ValueError("operand_requires_exact_structured_fields")
    if any(not _bounded_references(value.get(name)) for name in _REFERENCE_FIELDS):
        raise ValueError("operand_reference_list_invalid_or_unbounded")
    loop_ref = value.get("loop_ref")
    if type(loop_ref) is not str or len(loop_ref) > _MAX_REFERENCE_CODE_POINTS:
        raise ValueError("operand_loop_ref_invalid_or_unbounded")
    return build_symbolic_field_state(
        identity_refs=value["identity_refs"],
        phase_index=value["phase_index"],
        recursion_depth=value["recursion_depth"],
        drift_micro=value["drift_micro"],
        resonance_micro=value["resonance_micro"],
        memory_charge_micro=value["memory_charge_micro"],
        entropy_micro=value["entropy_micro"],
        loop_ref=loop_ref,
        echo_ancestry_refs=value["echo_ancestry_refs"],
        lineage_refs=value["lineage_refs"],
        locked=value["locked"],
        archived=value["archived"],
        grace_used=value["grace_used"],
        revision=value["revision"],
    )


def build_rsoc_law_lab_preview_response(request: object) -> dict[str, object]:
    """Return a deterministic JSON-safe law preview without side effects."""

    if type(request) is not dict:
        return _invalid_response("request_must_be_json_object")
    if not _BASE_REQUEST_FIELDS.issubset(request):
        return _invalid_response("request_requires_glyph_and_operands")
    glyph = request.get("glyph")
    if type(glyph) is not str:
        return _invalid_response("glyph_must_be_exact_text")
    law = law_for_glyph(glyph)
    if law is None:
        if set(request) != _BASE_REQUEST_FIELDS:
            return _invalid_response("request_contains_unsupported_fields")
        result = preview_rsoc_law(glyph, ())
        fields: tuple[SymbolicFieldState, ...] = ()
    else:
        expected_fields = (
            _ECHO_REQUEST_FIELDS if law.glyph == "Ê" else _BASE_REQUEST_FIELDS
        )
        if set(request) != expected_fields:
            return _invalid_response(
                "echo_requires_expected_ancestry_ref"
                if law.glyph == "Ê"
                else "request_contains_unsupported_fields"
            )
        operands = request.get("operands")
        if not isinstance(operands, (tuple, list)):
            return _invalid_response("operands_must_be_structured_array")
        if len(operands) > 2:
            return _invalid_response("operand_count_exceeds_lab_limit")
        try:
            fields = tuple(_build_operand(item) for item in operands)
        except (TypeError, ValueError) as error:
            reason = str(error)
            if reason not in {
                "operand_must_be_json_object",
                "operand_requires_exact_structured_fields",
                "operand_reference_list_invalid_or_unbounded",
                "operand_loop_ref_invalid_or_unbounded",
            }:
                reason = "operand_value_failed_closed_validation"
            return _invalid_response(reason)
        expected_ancestry_ref = request.get("expected_ancestry_ref", "")
        if law.glyph == "Ê" and (
            type(expected_ancestry_ref) is not str
            or not expected_ancestry_ref
            or len(expected_ancestry_ref) > _MAX_REFERENCE_CODE_POINTS
        ):
            return _invalid_response("expected_ancestry_ref_invalid_or_unbounded")
        result = preview_rsoc_law(
            glyph,
            fields,
            expected_ancestry_ref=expected_ancestry_ref,
        )

    result_record = result.to_dict()
    result_record["status"] = result.status.value
    return {
        "status": result.status.value,
        "reason_code": result.reason_code,
        "api_contract": API_CONTRACT,
        "endpoint": ENDPOINT,
        "route_key": ROUTE_KEY,
        "mode": "forge_owned_typed_rsoc_law_preview",
        "read_only": True,
        "law_catalog": _catalog(),
        "request_contract": _request_contract(),
        "input_fields": [field.to_dict() for field in fields],
        "result": result_record,
        "output_fields": [field.to_dict() for field in result.output_fields],
        "echo_valid": result.echo_valid,
        "issue_codes": list(result.issue_codes),
        "trace": list(result.trace),
        "boundary": _surface_boundary(),
        "receipt": {
            "result_id": result.result_id,
            "deterministic": result.deterministic,
            "preview_only": True,
            "runtime_authority": result.runtime_authority,
            "memory_authority": result.memory_authority,
            "action_authority": result.action_authority,
            "delivery_authority": result.delivery_authority,
        },
    }


__all__ = (
    "API_CONTRACT",
    "ENDPOINT",
    "ROUTE_KEY",
    "build_rsoc_law_lab_preview_response",
)
