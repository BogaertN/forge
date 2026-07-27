"""Ask Forge adapter for the response-only Language Core meaning preview."""

from __future__ import annotations

from collections.abc import Mapping

from aiweb_language_core_bootstrap.meaning_compiler_preview import (
    compile_meaning_preview,
    meaning_compiler_preview_boundary,
)


API_CONTRACT = "forge_operator_console_api_v1"
ENDPOINT = "/api/operator/ask-forge/language-core-preview"


def _surface_boundary() -> dict[str, object]:
    boundary = meaning_compiler_preview_boundary().to_dict()
    boundary.update(
        {
            "read_only": True,
            "ui_is_authority": False,
            "forge_governs": True,
            "imported_references_are_authority": False,
            "llm_tokenization_performed": False,
            "model_call_performed": False,
            "calls_llm": False,
            "embedding_performed": False,
            "uses_embeddings": False,
            "vector_retrieval_performed": False,
            "uses_vectors": False,
            "rmc_memory_read_performed": False,
            "rmc_memory_write_performed": False,
        }
    )
    return boundary


def _invalid_response(reason_code: str, source_text: str = "") -> dict[str, object]:
    return {
        "status": "ERROR",
        "reason_code": reason_code,
        "schema_version": "aiweb-forge-meaning-compiler-preview-v0",
        "api_contract": API_CONTRACT,
        "endpoint": ENDPOINT,
        "mode": "forge_owned_language_core_preview",
        "source_text": source_text,
        "summary": "The Language Core request was rejected before meaning compilation.",
        "reasons": [reason_code],
        "source_custody": None,
        "source_forms": [],
        "lexical_candidates": [],
        "frame_candidates": [],
        "algebra_trace": [],
        "meaning_candidates": [],
        "selected_meaning": None,
        "rmc_context": None,
        "candidate_wording": None,
        "candidate_wording_record": None,
        "echo": None,
        "stages": [],
        "boundary": _surface_boundary(),
        "receipt": None,
    }


def _meaning_candidate_for_surface(
    candidate: object,
    selected_id: str,
) -> dict[str, object]:
    data = candidate.to_dict()
    gates = data.get("gates") if isinstance(data.get("gates"), (list, tuple)) else ()
    rejected = [
        reason
        for gate in gates
        if isinstance(gate, Mapping) and gate.get("passed") is False
        for reason in gate.get("reasons", ())
    ]
    candidate_id = str(data.get("meaning_candidate_id", ""))
    data.update(
        {
            "candidate_id": candidate_id,
            "selected": bool(selected_id and candidate_id == selected_id),
            "status": "ADMITTED" if data.get("all_gates_passed") else "HELD",
            "rejected_reasons": rejected,
        }
    )
    return data


def _stage_for_surface(stage: object) -> dict[str, object]:
    data = stage.to_dict()
    stage_key = str(data.get("stage_key", "compiler_stage"))
    labels = {
        "source_custody": "Exact source custody",
        "source_form_projection": "Character and source-form spans",
        "lexical_sense_proposal": "Provisional concept and sense candidates",
        "predicate_role_derivation": "Predicate and participant-role derivation",
        "symbolic_meaning_gates": "Symbolic meaning algebra and four gates",
        "rmc_exact_resonance": "Read-only RMC exact-reference resonance",
        "preview_selection": "Unique selection or clarification hold",
        "reverse_derivation": "Reverse expression derivation",
        "echo_comparison": "Echo meaning-preservation comparison",
    }
    return {
        "stage_id": data.get("stage_id"),
        "label": labels.get(stage_key, stage_key.replace("_", " ").title()),
        "status": data.get("status"),
        "summary": "; ".join(str(item) for item in data.get("reasons", ()))
        or "Deterministic stage receipt recorded.",
        "evidence": {
            "stage_key": stage_key,
            "input_refs": data.get("input_refs", ()),
            "output_refs": data.get("output_refs", ()),
            "reasons": data.get("reasons", ()),
        },
    }


def build_language_core_preview_response(request: object) -> dict[str, object]:
    """Return one deterministic JSON-safe preview response and no side effect."""

    if type(request) is not dict:
        return _invalid_response("request_must_be_json_object")
    if "source_text" not in request:
        return _invalid_response("source_text_field_required")
    # Browser/API callers cannot supply memory evidence.  The trusted Python
    # compiler interface accepts validated snapshots for tests and for a future
    # Forge-owned provider, but the public HTTP boundary is source text only.
    if set(request) != {"source_text"}:
        return _invalid_response("request_contains_unsupported_fields")
    source_text = request.get("source_text")
    if type(source_text) is not str:
        return _invalid_response("source_text_must_be_string")

    try:
        result = compile_meaning_preview(
            source_text,
        )
    except Exception:
        return _invalid_response("language_core_preview_failed_closed", source_text)

    selected_id = (
        result.selected_meaning.meaning_candidate_id
        if result.selected_meaning is not None
        else ""
    )
    wording_text = result.candidate_wording.text if result.candidate_wording else None
    if result.status.value == "PREVIEW_READY":
        summary = (
            "One provisional meaning passed the four gates and the Echo "
            "round-trip. Candidate wording is available but not delivered."
        )
    elif result.status.value == "HELD":
        summary = "Forge held the source for clarification or unsupported meaning evidence."
    elif result.status.value == "UNSUPPORTED":
        summary = "The exact source is outside the bounded v0 grammar."
    else:
        summary = "The exact source could not enter the bounded compiler."

    return {
        "status": result.status.value,
        "reason_code": result.reasons[0] if result.reasons else "preview_complete",
        "schema_version": result.schema_version,
        "api_contract": API_CONTRACT,
        "endpoint": ENDPOINT,
        "mode": "forge_owned_language_core_preview",
        "result_id": result.result_id,
        "source_text": result.source_text,
        "summary": summary,
        "reasons": list(result.reasons),
        "source_custody": result.source_custody.to_dict(),
        "source_forms": [item.to_dict() for item in result.source_forms],
        "lexical_candidates": [item.to_dict() for item in result.lexical_candidates],
        "frame_candidates": [item.to_dict() for item in result.frame_candidates],
        "algebra_trace": [item.to_dict() for item in result.algebra_trace],
        "meaning_candidates": [
            _meaning_candidate_for_surface(item, selected_id)
            for item in result.meaning_candidates
        ],
        "selected_meaning": result.selected_meaning.to_dict()
        if result.selected_meaning
        else None,
        "rmc_context": result.rmc_context.to_dict(),
        "candidate_wording": wording_text,
        "candidate_wording_record": result.candidate_wording.to_dict()
        if result.candidate_wording
        else None,
        "echo": result.echo.to_dict(),
        "stages": [_stage_for_surface(item) for item in result.stages],
        "boundary": _surface_boundary(),
        "receipt": result.receipt.to_dict(),
    }


__all__ = (
    "API_CONTRACT",
    "ENDPOINT",
    "build_language_core_preview_response",
)
