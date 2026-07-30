"""Ask Forge adapter for the response-only Language Core meaning preview."""

from __future__ import annotations

from collections.abc import Mapping

from aiweb_language_core_bootstrap.meaning_compiler_preview import (
    GovernedClarificationRequest,
    build_governed_clarification_request,
    compile_meaning_preview,
    meaning_compiler_preview_boundary,
    validate_governed_clarification_request,
)
from aiweb_language_core_bootstrap.governed_output_delivery import (
    ClarificationReentryStatus,
    ExactEchoStatus,
    OutputPurpose,
    build_clarification_reentry,
    build_exact_output_echo,
    build_governed_output_manifest,
    render_governed_output,
    validate_clarification_reentry_result,
    validate_exact_output_echo,
    validate_governed_output_manifest,
    validate_rendered_output_candidate,
)
from aiweb_language_core_bootstrap.operator_council import (
    OperatorCouncilResult,
    convene_operator_council,
)
from aiweb_language_core_bootstrap.schema import stable_record_id
from rmc_engine_v1.rmc_exact_language_store import (
    evaluate_exact_identity_resonance,
    load_trusted_rmc_language_store,
)
from rmc_engine_v1.operator_council_preview import (
    build_operator_council_preview,
)


API_CONTRACT = "forge_operator_console_api_v1"
ENDPOINT = "/api/operator/ask-forge/language-core-preview"
CLARIFICATION_REENTRY_REQUEST_SCHEMA = (
    "aiweb-forge-clarification-reentry-request-v1"
)

# The provider is loaded once at the trusted Python boundary.  HTTP callers
# cannot replace or refresh this immutable snapshot.  A governed runtime may
# restart or explicitly reload the adapter after approved memory promotion.
_TRUSTED_RMC_PROVIDER = load_trusted_rmc_language_store()


def _surface_boundary() -> dict[str, object]:
    boundary = meaning_compiler_preview_boundary().to_dict()
    compiler_boundary_id = str(boundary.pop("boundary_id", ""))
    boundary.update(
        {
            "compiler_boundary_id": compiler_boundary_id,
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
            "filesystem_read_performed": (
                _TRUSTED_RMC_PROVIDER.filesystem_read_performed
            ),
            "memory_read_performed": _TRUSTED_RMC_PROVIDER.memory_read_performed,
            "rmc_memory_read_performed": _TRUSTED_RMC_PROVIDER.memory_read_performed,
            "rmc_memory_write_performed": False,
            "trusted_rmc_provider_configured": True,
            "trusted_rmc_provider": _TRUSTED_RMC_PROVIDER.trusted,
            "rmc_provider_load_status": _TRUSTED_RMC_PROVIDER.load_status,
            "public_rmc_snapshot_injection_allowed": False,
            "rmc_exact_identity_resonance_only": True,
        }
    )
    return {
        "boundary_id": stable_record_id(
            "ask_forge_language_core_surface_boundary",
            boundary,
        ),
        **boundary,
    }


def _integrated_result_and_receipt(
    *,
    compiler_result: object,
    exact_resonances: tuple[object, ...],
    council_exact_resonances: tuple[object, ...],
    operator_council: dict[str, object],
    boundary: dict[str, object],
    clarification_request: object = None,
    clarification_reentry_result: object = None,
    governed_output: dict[str, object] | None = None,
) -> tuple[str, dict[str, object]]:
    council_result = operator_council.get("result")
    council_result_ref = (
        str(council_result.get("result_id", ""))
        if isinstance(council_result, Mapping)
        else ""
    )
    body = {
        "compiler_result_ref": compiler_result.result_id,
        "compiler_receipt_ref": compiler_result.receipt.receipt_id,
        "rmc_provider_result_ref": _TRUSTED_RMC_PROVIDER.provider_result_id,
        "rmc_snapshot_ref": compiler_result.rmc_context.snapshot.snapshot_id,
        "rmc_exact_resonance_refs": tuple(
            item.resonance_id for item in exact_resonances
        ),
        "rmc_exact_resonance_count": len(exact_resonances),
        "operator_council_admitted_rmc_exact_resonance_refs": tuple(
            item.resonance_id for item in council_exact_resonances
        ),
        "operator_council_admitted_rmc_exact_resonance_count": len(
            council_exact_resonances
        ),
        "operator_council_result_ref": council_result_ref,
        "operator_council_status": str(operator_council.get("status", "")),
        "surface_boundary_ref": boundary["boundary_id"],
        "deterministic": True,
        "read_only": True,
        "recommendation_only": True,
        "writes_performed": False,
        "action_performed": False,
        "delivery_performed": False,
    }
    clarification_ref = getattr(
        clarification_request,
        "clarification_request_id",
        "",
    )
    if clarification_ref:
        body.update(
            {
                "clarification_request_ref": clarification_ref,
                "operator_preview_exposed": True,
                "clarification_question_preview_exposed": True,
                "live_clarification_session_started": False,
                "clarification_response_consumed": False,
                "answer_delivery_performed": False,
            }
        )
    reentry_result_ref = getattr(
        clarification_reentry_result,
        "result_id",
        "",
    )
    if reentry_result_ref:
        reentry_receipt = getattr(
            clarification_reentry_result,
            "receipt",
            None,
        )
        body.update(
            {
                "clarification_reentry_result_ref": reentry_result_ref,
                "clarification_reentry_status": getattr(
                    getattr(clarification_reentry_result, "status", None),
                    "value",
                    "",
                ),
                "clarification_reentry_receipt_ref": getattr(
                    reentry_receipt,
                    "receipt_id",
                    "",
                ),
                "clarification_response_consumed": True,
                "operator_option_selection_performed": False,
            }
        )
    if governed_output is not None:
        manifest = governed_output.get("manifest")
        rendered = governed_output.get("rendered_output")
        exact_echo = governed_output.get("exact_echo")
        if not all(type(item) is dict for item in (manifest, rendered, exact_echo)):
            raise ValueError("governed_output_receipt_projection_invalid")
        body.update(
            {
                "governed_output_status": governed_output.get("status"),
                "governed_output_purpose": governed_output.get("output_purpose"),
                "governed_output_manifest_ref": manifest.get("manifest_id"),
                "governed_rendered_output_ref": rendered.get(
                    "rendered_output_id"
                ),
                "governed_exact_echo_ref": exact_echo.get("echo_id"),
                "answer_delivery_eligible": governed_output.get(
                    "answer_delivery_eligible"
                ),
                "answer_delivery_authorized": False,
                "answer_delivery_performed": False,
            }
        )
    result_id = stable_record_id("ask_forge_language_core_surface_result", body)
    receipt_body = {
        "integrated_result_ref": result_id,
        **body,
    }
    return result_id, {
        "receipt_id": stable_record_id(
            "ask_forge_language_core_surface_receipt",
            receipt_body,
        ),
        **receipt_body,
    }


def _snapshot_bound_council_resonances(
    compiler_result: object,
    exact_resonances: tuple[object, ...],
) -> tuple[object, ...]:
    """Admit only exact-store rows independently bound to compiler context.

    The exact-store evaluator intentionally returns every non-empty exact-ID
    intersection for audit.  Some rows can therefore contain only a shared
    sense or role identity.  The compiler snapshot does not claim those rows
    as semantic evidence, so forwarding them to Council would correctly make
    Council reject the entire supplied set.  Keep the complete evaluator
    output on the surface, but pass Council only rows whose candidate,
    semantic-contract, concept, relation, and ancestry tuple is represented by
    the immutable compiler snapshot.
    """

    context = compiler_result.rmc_context.resonances
    snapshot_keys = {
        (
            item.meaning_candidate_ref,
            item.exact_semantic_contract_refs,
            item.exact_concept_refs,
            item.exact_relation_refs,
            item.exact_ancestry_refs,
        )
        for item in context
    }
    return tuple(
        item
        for item in exact_resonances
        if (
            item.meaning_candidate_ref,
            item.exact_semantic_contract_refs,
            item.exact_concept_refs,
            item.exact_relation_refs,
            item.exact_ancestry_refs,
        )
        in snapshot_keys
    )


def _parse_preview_request(
    request: object,
) -> tuple[str, dict[str, object] | None, str | None]:
    """Accept only exact source custody and one typed clarification link."""

    if type(request) is not dict:
        return "", None, "request_must_be_json_object"
    allowed_shapes = (
        {"source_text"},
        {"source_text", "clarification_reentry"},
    )
    if set(request) not in allowed_shapes:
        if "source_text" not in request:
            return "", None, "source_text_field_required"
        return "", None, "request_contains_unsupported_fields"
    source_text = request.get("source_text")
    if type(source_text) is not str:
        return "", None, "source_text_must_be_string"
    reentry = request.get("clarification_reentry")
    if reentry is None:
        return source_text, None, None
    if type(reentry) is not dict:
        return source_text, None, "clarification_reentry_must_be_json_object"
    if set(reentry) != {
        "schema_version",
        "original_source_text",
        "clarification_request_id",
    }:
        return source_text, None, "clarification_reentry_fields_not_exact"
    if (
        reentry.get("schema_version") != CLARIFICATION_REENTRY_REQUEST_SCHEMA
        or type(reentry.get("original_source_text")) is not str
        or type(reentry.get("clarification_request_id")) is not str
        or not reentry.get("clarification_request_id")
    ):
        return source_text, None, "clarification_reentry_contract_invalid"
    return source_text, dict(reentry), None


def _replay_typed_council_result(
    operator_council: object,
) -> OperatorCouncilResult | None:
    """Recover the exact typed Council result from its public projection."""

    if type(operator_council) is not dict:
        raise TypeError("operator_council_surface_type_not_admitted")
    if operator_council.get("status") != "RECOMMEND_FOR_OPERATOR_REVIEW":
        return None
    projected = operator_council.get("result")
    if type(projected) is not dict or type(projected.get("evidence")) is not dict:
        raise ValueError("operator_council_result_projection_missing")
    replayed = convene_operator_council(projected["evidence"])
    if type(replayed) is not OperatorCouncilResult or replayed.to_dict() != projected:
        raise ValueError("operator_council_result_projection_not_exact_replay")
    return replayed


def _build_governed_output(
    compiler_result: object,
    operator_council: object,
) -> dict[str, object] | None:
    """Run manifest → renderer → exact symbolic Echo, without delivery."""

    council_result = _replay_typed_council_result(operator_council)
    if council_result is None:
        return None
    manifest = build_governed_output_manifest(
        compiler_result,
        council_result,
    )
    if validate_governed_output_manifest(
        manifest,
        compiler_result,
        council_result,
    ):
        raise ValueError("governed_output_manifest_validation_failed")
    rendered = render_governed_output(
        manifest,
        compiler_result,
        council_result,
    )
    if validate_rendered_output_candidate(
        rendered,
        manifest,
        compiler_result,
        council_result,
    ):
        raise ValueError("governed_output_render_validation_failed")
    exact_echo = build_exact_output_echo(
        rendered,
        manifest,
        compiler_result,
        council_result,
    )
    if validate_exact_output_echo(
        exact_echo,
        rendered,
        manifest,
        compiler_result,
        council_result,
    ):
        raise ValueError("governed_output_exact_echo_validation_failed")
    if exact_echo.status is not ExactEchoStatus.PASS:
        raise ValueError("governed_output_exact_echo_not_passed")
    answer_eligible = exact_echo.answer_delivery_eligible
    if answer_eligible is not (
        manifest.output_purpose is OutputPurpose.DEFINITION_ANSWER
    ):
        raise ValueError("governed_output_answer_eligibility_mismatch")
    return {
        "status": (
            "EXACT_ECHO_PASS_PENDING_OPERATOR_APPROVAL"
            if answer_eligible
            else "CONTROLLED_RESTATEMENT_PREVIEW"
        ),
        "reason_code": (
            "definition_answer_requires_explicit_operator_approval"
            if answer_eligible
            else "typed_result_producer_required_before_answer_delivery"
        ),
        "output_purpose": manifest.output_purpose.value,
        "answer_delivery_eligible": answer_eligible,
        "operator_approval_required": True,
        "manifest": manifest.to_dict(),
        "rendered_output": rendered.to_dict(),
        "exact_echo": exact_echo.to_dict(),
        "boundary": manifest.boundary.to_dict(),
    }


def _reentry_council_hold(reason_code: str) -> dict[str, object]:
    return {
        "status": "NOT_CONVENED",
        "reason_code": reason_code,
        "summary": (
            "Council did not convene because the restated source did not "
            "resolve exactly one meaning from the prior clarification."
        ),
        "result": None,
        "recommendation_only": True,
        "operator_decision_required": True,
        "boundary": {
            "recommendation_only": True,
            "operator_decision_required": True,
            "raw_text_accepted": False,
            "tokenization_performed": False,
            "model_called": False,
            "embedding_used": False,
            "vector_used": False,
            "similarity_scoring_used": False,
            "memory_write_performed": False,
            "tool_routing_performed": False,
            "action_performed": False,
            "delivery_performed": False,
            "decision_authority": False,
        },
    }


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
        "trusted_rmc_provider": _TRUSTED_RMC_PROVIDER.public_receipt(),
        "rmc_exact_identity_resonances": [],
        "operator_council_admitted_rmc_exact_resonance_refs": [],
        "operator_council_admitted_rmc_exact_resonance_count": 0,
        "candidate_wording": None,
        "candidate_wording_record": None,
        "clarification_request": None,
        "clarification_reentry_receipt": None,
        "governed_output": None,
        "governed_output_reason_code": "compiler_result_not_available",
        "echo": None,
        "operator_council": {
            "status": "NOT_CONVENED",
            "reason_code": "valid_selected_meaning_required_before_council",
            "summary": "Council was not convened for an invalid Language Core request.",
            "result": None,
            "boundary": {
                "recommendation_only": True,
                "operator_decision_required": True,
                "raw_text_accepted": False,
                "tokenization_performed": False,
                "model_called": False,
                "embedding_used": False,
                "vector_used": False,
                "similarity_scoring_used": False,
                "memory_write_performed": False,
                "tool_routing_performed": False,
                "action_performed": False,
                "delivery_performed": False,
                "decision_authority": False,
            },
        },
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


def _clarification_reentry_stage(result: object) -> dict[str, object] | None:
    if result is None:
        return None
    status = getattr(getattr(result, "status", None), "value", "HELD")
    reason_codes = tuple(getattr(result, "reason_codes", ()))
    receipt = getattr(result, "receipt", None)
    return {
        "stage_id": getattr(result, "result_id", "clarification_reentry:held"),
        "label": "Clarification restatement re-entry",
        "status": status,
        "summary": "; ".join(str(item) for item in reason_codes)
        or "Clarification restatement was checked against the prior alternatives.",
        "evidence": {
            "clarification_request_ref": getattr(
                result,
                "clarification_request_ref",
                "",
            ),
            "receipt_ref": getattr(receipt, "receipt_id", ""),
            "clarification_response_consumed": True,
            "compiler_selection_performed": (
                status == ClarificationReentryStatus.ACCEPTED.value
            ),
            "operator_option_selection_performed": False,
            "action_authorized": False,
            "delivery_authorized": False,
            "answer_delivery_performed": False,
            "memory_write_authorized": False,
        },
    }


def _governed_output_stages(
    governed_output: dict[str, object] | None,
) -> list[dict[str, object]]:
    if governed_output is None:
        return []
    manifest = governed_output["manifest"]
    rendered = governed_output["rendered_output"]
    exact_echo = governed_output["exact_echo"]
    assert type(manifest) is dict
    assert type(rendered) is dict
    assert type(exact_echo) is dict
    answer_eligible = governed_output["answer_delivery_eligible"] is True
    return [
        {
            "stage_id": manifest["manifest_id"],
            "label": "Recursive Manifest Compiler",
            "status": manifest.get("status", "READY_FOR_RENDER_PREVIEW"),
            "summary": (
                "Forge compiled the selected meaning, exact-ID RMC evidence, "
                "gates, Echo, and Council receipt into one immutable output manifest."
            ),
            "evidence": {
                "output_purpose": governed_output["output_purpose"],
                "answer_delivery_eligible": answer_eligible,
                "delivery_authorized": False,
            },
        },
        {
            "stage_id": rendered["rendered_output_id"],
            "label": "Deterministic human-language renderer",
            "status": "RENDERED_PREVIEW",
            "summary": (
                "A closed symbolic grammar rendered the manifest; no model or "
                "caller-authored answer text was used."
            ),
            "evidence": {
                "renderer_version": rendered.get("renderer_version"),
                "template_key": rendered.get("template_key"),
                "text_sha256": rendered.get("text_sha256"),
                "delivery_authorized": False,
            },
        },
        {
            "stage_id": exact_echo["echo_id"],
            "label": "Exact symbolic Echo",
            "status": exact_echo.get("status", "REJECT"),
            "summary": (
                "Forge decoded the rendered words and compared the complete "
                "semantic contract, roles, relations, transition, and source coverage."
            ),
            "evidence": {
                "transition_admitted": exact_echo.get("transition_admitted"),
                "exact_contract_match": exact_echo.get("exact_contract_match"),
                "exact_role_match": exact_echo.get("exact_role_match"),
                "exact_relation_match": exact_echo.get("exact_relation_match"),
                "unique_decode": exact_echo.get("unique_decode"),
                "full_source_coverage": exact_echo.get("full_source_coverage"),
                "delivery_authorized": False,
            },
        },
        {
            "stage_id": stable_record_id(
                "language_output_operator_delivery_pending",
                {
                    "manifest_ref": manifest["manifest_id"],
                    "exact_echo_ref": exact_echo["echo_id"],
                    "answer_delivery_eligible": answer_eligible,
                },
            ),
            "label": "Operator-approved output delivery",
            "status": (
                "OPERATOR_APPROVAL_REQUIRED"
                if answer_eligible
                else "TYPED_RESULT_PRODUCER_REQUIRED"
            ),
            "summary": (
                "The definition answer can be delivered only after an explicit "
                "one-time operator confirmation."
                if answer_eligible
                else "This controlled restatement remains preview-only until a "
                "typed Forge result producer supplies answer evidence."
            ),
            "evidence": {
                "answer_delivery_eligible": answer_eligible,
                "operator_approval_required": True,
                "delivery_performed": False,
                "answer_delivery_performed": False,
            },
        },
    ]


def build_language_core_preview_response(request: object) -> dict[str, object]:
    """Return one deterministic JSON-safe preview response and no side effect."""

    source_text, reentry_request, request_issue = _parse_preview_request(request)
    if request_issue is not None:
        return _invalid_response(request_issue, source_text)
    if not _TRUSTED_RMC_PROVIDER.trusted:
        return _invalid_response("trusted_rmc_language_store_rejected", source_text)

    clarification_reentry_result = None
    try:
        if reentry_request is None:
            result = compile_meaning_preview(
                source_text,
                rmc_snapshot=_TRUSTED_RMC_PROVIDER.snapshot,
            )
        else:
            original_result = compile_meaning_preview(
                reentry_request["original_source_text"],
                rmc_snapshot=_TRUSTED_RMC_PROVIDER.snapshot,
            )
            original_clarification = build_governed_clarification_request(
                original_result
            )
            if (
                original_clarification is None
                or original_clarification.clarification_request_id
                != reentry_request["clarification_request_id"]
                or validate_governed_clarification_request(
                    original_clarification,
                    original_result,
                )
            ):
                return _invalid_response(
                    "clarification_reentry_request_not_exact_prior_preview",
                    source_text,
                )
            clarification_reentry_result = build_clarification_reentry(
                original_result,
                original_clarification,
                source_text,
            )
            if validate_clarification_reentry_result(
                clarification_reentry_result,
                original_result,
                original_clarification,
            ):
                raise ValueError("clarification_reentry_result_invalid")
            result = clarification_reentry_result.clarified_compiler_result
    except Exception:
        return _invalid_response("language_core_preview_failed_closed", source_text)

    reentry_accepted = (
        clarification_reentry_result is None
        or clarification_reentry_result.status
        is ClarificationReentryStatus.ACCEPTED
    )

    selected_id = (
        result.selected_meaning.meaning_candidate_id
        if result.selected_meaning is not None
        else ""
    )
    wording_text = result.candidate_wording.text if result.candidate_wording else None
    try:
        exact_resonances = evaluate_exact_identity_resonance(
            _TRUSTED_RMC_PROVIDER.records,
            result.meaning_candidates,
            result.frame_candidates,
        )
        council_exact_resonances = _snapshot_bound_council_resonances(
            result,
            exact_resonances,
        )
    except Exception:
        return _invalid_response("rmc_exact_resonance_failed_closed", source_text)
    try:
        if reentry_accepted:
            operator_council = build_operator_council_preview(
                result,
                exact_rmc_resonances=council_exact_resonances,
            )
        else:
            reentry_reason = (
                clarification_reentry_result.reason_codes[0]
                if clarification_reentry_result.reason_codes
                else "clarification_reentry_held"
            )
            operator_council = _reentry_council_hold(reentry_reason)
    except Exception:
        return _invalid_response("operator_council_preview_failed_closed", source_text)
    if type(operator_council) is not dict:
        return _invalid_response("operator_council_preview_invalid_result", source_text)
    try:
        clarification_request = build_governed_clarification_request(result)
        if clarification_request is not None:
            if type(clarification_request) is not GovernedClarificationRequest:
                raise TypeError("clarification_request_type_not_admitted")
            clarification_issues = validate_governed_clarification_request(
                clarification_request,
                result,
            )
            if clarification_issues:
                raise ValueError(clarification_issues[0])
            clarification_payload = clarification_request.to_dict()
        else:
            clarification_payload = None
    except Exception:
        return _invalid_response("governed_clarification_preview_failed_closed", source_text)
    governed_output = None
    governed_output_reason_code = "compiler_or_council_not_ready_for_render"
    if result.status.value == "PREVIEW_READY" and reentry_accepted:
        try:
            governed_output = _build_governed_output(result, operator_council)
            governed_output_reason_code = (
                str(governed_output.get("reason_code", "governed_output_ready"))
                if governed_output is not None
                else "operator_council_not_ready_for_render"
            )
        except Exception:
            governed_output = None
            governed_output_reason_code = "governed_output_preview_failed_closed"
    try:
        boundary = _surface_boundary()
        integrated_result_id, integrated_receipt = _integrated_result_and_receipt(
            compiler_result=result,
            exact_resonances=exact_resonances,
            council_exact_resonances=council_exact_resonances,
            operator_council=operator_council,
            boundary=boundary,
            clarification_request=clarification_request,
            clarification_reentry_result=clarification_reentry_result,
            governed_output=governed_output,
        )
    except Exception:
        return _invalid_response("language_core_surface_receipt_failed_closed", source_text)
    if not reentry_accepted:
        surface_status = "HELD"
        surface_reason = (
            clarification_reentry_result.reason_codes[0]
            if clarification_reentry_result.reason_codes
            else "clarification_reentry_held"
        )
        summary = (
            "Forge compiled the restated words but held them because they did "
            "not resolve exactly one meaning from the immediately prior "
            "clarification. No Council recommendation, rendering, or answer "
            "delivery occurred."
        )
    elif result.status.value == "PREVIEW_READY":
        surface_status = result.status.value
        surface_reason = (
            result.reasons[0] if result.reasons else "preview_complete"
        )
        summary = (
            "One provisional meaning passed the four gates, exact-ID RMC and "
            "Council review. Its output manifest and exact symbolic Echo are "
            "available; any eligible answer still requires operator approval."
            if governed_output is not None
            else "One provisional meaning passed the compiler gates. Candidate "
            "wording remains a non-delivered preview because the governed "
            "output chain is not ready."
        )
    elif result.status.value == "HELD":
        surface_status = result.status.value
        surface_reason = (
            result.reasons[0] if result.reasons else "preview_complete"
        )
        if clarification_request is not None:
            summary = (
                "Forge preserved every admitted meaning alternative and prepared "
                "a clarification question for operator review. No meaning was "
                "selected and the question was not delivered."
            )
        else:
            summary = "Forge held the source for clarification or unsupported meaning evidence."
    elif result.status.value == "UNSUPPORTED":
        surface_status = result.status.value
        surface_reason = (
            result.reasons[0] if result.reasons else "preview_complete"
        )
        summary = "The exact source is outside the bounded v0 grammar."
    else:
        surface_status = result.status.value
        surface_reason = (
            result.reasons[0] if result.reasons else "preview_complete"
        )
        summary = "The exact source could not enter the bounded compiler."

    reentry_stage = _clarification_reentry_stage(
        clarification_reentry_result
    )
    reentry_receipt = getattr(
        clarification_reentry_result,
        "receipt",
        None,
    )

    return {
        "status": surface_status,
        "reason_code": surface_reason,
        "schema_version": result.schema_version,
        "api_contract": API_CONTRACT,
        "endpoint": ENDPOINT,
        "mode": "forge_owned_language_core_preview",
        "result_id": integrated_result_id,
        "compiler_result_id": result.result_id,
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
        "trusted_rmc_provider": _TRUSTED_RMC_PROVIDER.public_receipt(),
        "rmc_exact_identity_resonances": [
            item.to_dict() for item in exact_resonances
        ],
        "operator_council_admitted_rmc_exact_resonance_refs": [
            item.resonance_id for item in council_exact_resonances
        ],
        "operator_council_admitted_rmc_exact_resonance_count": len(
            council_exact_resonances
        ),
        "candidate_wording": wording_text,
        "candidate_wording_record": result.candidate_wording.to_dict()
        if result.candidate_wording
        else None,
        "clarification_request": clarification_payload,
        "clarification_reentry_receipt": (
            reentry_receipt.to_dict() if reentry_receipt is not None else None
        ),
        "governed_output": governed_output,
        "governed_output_reason_code": governed_output_reason_code,
        "echo": result.echo.to_dict(),
        "operator_council": operator_council,
        "stages": [
            *[_stage_for_surface(item) for item in result.stages],
            *(
                [
                    {
                        "stage_id": clarification_request.clarification_request_id,
                        "label": "Governed clarification preview",
                        "status": "CLARIFICATION_REQUIRED",
                        "summary": clarification_request.candidate_wording,
                        "evidence": {
                            "reason_code": clarification_request.reason_code,
                            "alternative_meaning_refs": (
                                clarification_request.alternative_meaning_refs
                            ),
                            "all_admitted_alternatives_preserved": True,
                            "recommendation_only": True,
                            "operator_preview_exposed": True,
                            "clarification_question_preview_exposed": True,
                            "live_clarification_session_started": False,
                            "clarification_response_consumed": False,
                            "selection_performed": False,
                            "action_authorized": False,
                            "delivery_authorized": False,
                            "answer_delivery_performed": False,
                            "memory_write_authorized": False,
                        },
                    }
                ]
                if clarification_request is not None
                else []
            ),
            *([reentry_stage] if reentry_stage is not None else []),
            {
                "stage_id": (
                    operator_council.get("result", {}).get("result_id")
                    if isinstance(operator_council.get("result"), dict)
                    else "operator_council:not_convened"
                ),
                "label": "Operator Council recommendation",
                "status": operator_council.get("status", "NOT_CONVENED"),
                "summary": operator_council.get("summary", "Council stage recorded."),
                "evidence": {
                    "reason_code": operator_council.get("reason_code"),
                    "recommendation_only": True,
                    "operator_decision_required": True,
                    "action_authorized": False,
                    "delivery_authorized": False,
                },
            },
            *_governed_output_stages(governed_output),
        ],
        "boundary": boundary,
        "compiler_receipt": result.receipt.to_dict(),
        "receipt": integrated_receipt,
    }


__all__ = (
    "API_CONTRACT",
    "ENDPOINT",
    "build_language_core_preview_response",
)
