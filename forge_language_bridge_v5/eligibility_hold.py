"""Bridge 5: exact gate custody and eligibility evaluation hold.

This bridge extends an explicitly nominated Bridge 4 candidate through the
real Slice 40C-F gate families, Slice 40G composition, Slice 40H MSM gate
custody, and Slice 41C eligibility evaluation. It never calls Slice 41D or
Slice 41E, never selects meaning, never routes a tool, never executes an
action, never writes source or memory, and never calls a language model.

LLM use remains an EchoForge deliberation concern. EchoForge output is not
Forge meaning, permission, proof, routing, or execution authority.
"""
from __future__ import annotations

from typing import Any, Final

from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.source_field_projection import project_source_field
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    bind_resonant_operator_candidates,
)
from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import (
    construct_candidate_resonant_phase_trails,
)
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import (
    apply_scope_attachment_reference_constraints,
)
from aiweb_language_core_bootstrap.deterministic_structural_derivation import (
    derive_deterministic_structural_analysis,
)
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import (
    propose_structural_concept_candidates,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    build_compatibility_snapshot,
    build_exact_compatibility_rule,
    propose_predicate_role_frame_candidates,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.deterministic_constructor import (
    CandidateMeaningConstructorInput,
    construct_candidate_meanings,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.manifest_candidate_integration import (
    integrate_candidate_meanings_into_manifest,
)
from forge_language_bridge_v4 import (
    STATUS_CANDIDATE_CUSTODY,
    candidate_custody_decision,
)
from forge_language_bridge_v4 import bridge_status as bridge4_status
from .runtime_builders import build_gate_and_eligibility

BRIDGE_VERSION: Final[str] = "forge_language_bridge_v5"
BRIDGE_MODE: Final[str] = "exact_gate_custody_selection_eligibility_hold"

STATUS_ELIGIBILITY_EVALUATED_HELD: Final[str] = "ELIGIBILITY_EVALUATED_HELD"
STATUS_PREDICATE_FRAME_NOMINATION_REQUIRED: Final[str] = (
    "PREDICATE_FRAME_NOMINATION_REQUIRED"
)
STATUS_INVALID_PREDICATE_FRAME_NOMINATION: Final[str] = (
    "INVALID_PREDICATE_FRAME_NOMINATION"
)
STATUS_GATE_EVALUATION_HELD: Final[str] = "GATE_EVALUATION_HELD"
STATUS_INVALID_INPUT: Final[str] = "INVALID_INPUT"
STATUS_INVALID_CANDIDATE_NOMINATION: Final[str] = (
    "INVALID_CANDIDATE_NOMINATION"
)

_ALLOWED_ACTION_ROOT_FRAMES: Final[dict[str, str]] = {
    "inspect": "inspect_read_only",
    "report": "report_attributed_content",
    "request": "request_non_authorizing",
}

_REMAINING_FORGE_LLM_LANES: Final[tuple[str, ...]] = (
    "diagnostic_output_analysis",
    "forge_command_implementation_generation",
    "forge_self_suggestion_generation",
    "engine_review_generation",
    "generic_repair_draft_generation",
    "generic_repair_candidate_review",
    "tool_wrapper_generation",
)

_BLOCKED_DOWNSTREAM: Final[tuple[str, ...]] = (
    "slice41d_selected_meaning_construction",
    "slice41e_msm_selected_meaning_integration",
    "truth_decision",
    "evidence_validation",
    "permission_grant",
    "tool_routing",
    "tool_invocation",
    "action_execution",
    "memory_write",
    "rendering",
    "delivery",
)


def _value(value: object) -> str:
    return str(getattr(value, "value", value))


def _base(
    request: object,
    *,
    action_root: str,
    surface: str,
) -> dict[str, Any]:
    text = request if type(request) is str else ""
    return {
        "schema_version": "forge-language-bridge-v5",
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "surface": surface,
        "normalized_text": text.strip(),
        "action_root": action_root,
        "handled": True,
        "route": "",
        "args": "",
        "action_class": "none",
        "approval_required": False,
        "approval_gate": "",
        "calls_llm": False,
        "executes_command": False,
        "executes_shell": False,
        "executes_simulation": False,
        "writes_files": False,
        "writes_memory": False,
        "grants_permission": False,
        "selected_meaning": False,
        "meaning_selection_authority": False,
        "candidate_ranking_used": False,
        "confidence_scoring_used": False,
        "semantic_similarity_used": False,
        "tool_routing_authority": False,
        "action_authority": False,
        "delivery_authority": False,
        "echo_forge_llm_invoked": False,
        "echo_forge_output_used_as_forge_authority": False,
    }


def _held(
    request: object,
    *,
    action_root: str,
    surface: str,
    status: str,
    response_text: str,
    reasons: tuple[str, ...],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    value = {
        **_base(request, action_root=action_root, surface=surface),
        "status": status,
        "intent": "selection_eligibility_hold",
        "response_text": response_text,
        "gate_evaluation": {
            "executed": False,
            "family_results": {},
            "composition_executed": False,
            "msm_gate_custody_created": False,
        },
        "selection_boundary": {
            "nomination_recorded": False,
            "predicate_frame_pair_recorded": False,
            "eligibility_evaluated": False,
            "eligible_for_selected_meaning_construction": False,
            "selected_meaning_constructed": False,
            "msm_selected_meaning_integrated": False,
            "slice41d_called": False,
            "slice41e_called": False,
        },
        "blocked_downstream": _BLOCKED_DOWNSTREAM,
        "reasons": reasons,
    }
    if extra:
        value.update(extra)
    return value


def _build_candidate_artifacts(
    request: str,
    *,
    action_root: str,
) -> dict[str, Any]:
    root = action_root.strip().lower()
    frame_key = _ALLOWED_ACTION_ROOT_FRAMES[root]

    custody = capture_input_event(
        request,
        source_id="forge.language.bridge.v4",
        channel_id="forge.language.bridge.v4.explicit_candidate_custody",
        sequence_number=0,
    )
    projection = project_source_field(custody.event)
    binding = bind_resonant_operator_candidates(projection)
    trails = construct_candidate_resonant_phase_trails(projection, binding)
    constraints = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
    )
    structural = derive_deterministic_structural_analysis(
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
    slice37 = propose_structural_concept_candidates(
        custody,
        projection,
        structural,
    )

    compatibility_rules = []
    for concept_index, concept in enumerate(slice37.concept_candidates):
        for sense_index, sense in enumerate(slice37.sense_candidates):
            if sense.concept_id != concept.concept_id:
                continue
            compatibility_rules.append(
                build_exact_compatibility_rule(
                    rule_key=(
                        f"forge.language.bridge.v4.{root}."
                        f"{concept_index}.{sense_index}"
                    ),
                    action_root_key=root,
                    concept_id=concept.concept_id,
                    sense_id=sense.sense_id,
                    allowed_frame_keys=(frame_key,),
                )
            )

    if not compatibility_rules:
        raise ValueError("no exact concept/sense compatibility pair")

    snapshot = build_compatibility_snapshot(
        rules=tuple(compatibility_rules),
        registry_key=f"forge.language.bridge.v4.{root}",
    )
    slice38 = propose_predicate_role_frame_candidates(
        slice37,
        compatibility_snapshot=snapshot,
    )
    constructor_input = CandidateMeaningConstructorInput(
        custody=custody,
        projection=projection,
        binding=binding,
        trails=trails,
        constraints=constraints,
        structural=structural,
        slice37=slice37,
        slice38=slice38,
    )
    constructor_result = construct_candidate_meanings((constructor_input,))
    integration_result = integrate_candidate_meanings_into_manifest(
        constructor_result
    )
    manifest = integration_result.manifest
    companions = tuple(integration_result.companions)
    constructed_records = tuple(constructor_result.constructed_records)

    constructed_by_id = {}
    for record in constructed_records:
        identity = record.candidate_meaning_state.identity
        constructed_by_id[identity.candidate_meaning_id] = record

    manifest_records = {
        record.record_id: record
        for record in tuple(manifest.candidate_meanings)
    }

    return {
        "custody": custody,
        "projection": projection,
        "binding": binding,
        "trails": trails,
        "constraints": constraints,
        "structural": structural,
        "slice37": slice37,
        "slice38": slice38,
        "constructor_result": constructor_result,
        "integration_result": integration_result,
        "manifest": manifest,
        "companions": companions,
        "constructed_records": constructed_records,
        "constructed_by_id": constructed_by_id,
        "manifest_records": manifest_records,
        "all_candidate_ids": tuple(
            companion.candidate_meaning_id
            for companion in companions
        ),
    }


def _linked_pair_options(
    artifacts: dict[str, Any],
    constructed_record: object,
) -> tuple[dict[str, Any], ...]:
    content = constructed_record.candidate_meaning_state.content
    predicate_refs = set(content.action_root_predicate_candidate_refs)
    layout_refs = set(content.role_layout_candidate_refs)

    predicates = {
        item.candidate_id: item
        for item in tuple(artifacts["slice38"].action_predicate_candidates)
        if item.candidate_id in predicate_refs
    }
    layouts = {
        item.candidate_id: item
        for item in tuple(artifacts["slice38"].role_layout_candidates)
        if item.candidate_id in layout_refs
    }

    options: list[dict[str, Any]] = []
    for predicate_candidate_id in sorted(predicates):
        predicate = predicates[predicate_candidate_id]
        for layout_candidate_id in sorted(layouts):
            layout = layouts[layout_candidate_id]
            exact_link = (
                layout.predicate_id == predicate.predicate_id
                and layout.action_root_id == predicate.action_root_id
                and (layout.frame_id, layout.frame_version)
                in predicate.frame_ids_and_versions
                and layout_candidate_id in predicate.role_layout_candidate_ids
            )
            if not exact_link:
                continue
            options.append(
                {
                    "predicate_candidate_id": predicate.candidate_id,
                    "predicate_id": predicate.predicate_id,
                    "predicate_version": predicate.predicate_version,
                    "role_layout_candidate_id": layout.candidate_id,
                    "frame_id": layout.frame_id,
                    "frame_version": layout.frame_version,
                    "action_root_id": predicate.action_root_id,
                    "action_root_version": predicate.action_root_version,
                    "_predicate": predicate,
                    "_layout": layout,
                }
            )
    return tuple(options)


def eligibility_hold_decision(
    request: object,
    *,
    action_root: str,
    nominated_candidate_id: str,
    predicate_candidate_id: str = "",
    role_layout_candidate_id: str = "",
    surface: str,
    reason: str,
) -> dict[str, Any]:
    text = request if type(request) is str else ""
    root = str(action_root or "").strip().lower()
    nominated = str(nominated_candidate_id or "").strip()
    predicate_nomination = str(predicate_candidate_id or "").strip()
    layout_nomination = str(role_layout_candidate_id or "").strip()

    if not text.strip():
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_INVALID_INPUT,
            response_text="Eligibility evaluation requires a non-empty source request.",
            reasons=("non_empty_source_request_required",),
        )

    if root not in _ALLOWED_ACTION_ROOT_FRAMES:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_INVALID_INPUT,
            response_text=(
                "Eligibility evaluation requires an explicit accepted action root: "
                "inspect, report, or request."
            ),
            reasons=(
                "explicit_action_root_required",
                "hidden_action_root_inference_prohibited",
            ),
        )

    custody_preview = candidate_custody_decision(
        text,
        action_root=root,
        surface=surface,
        reason=reason,
    )
    if custody_preview.get("status") != STATUS_CANDIDATE_CUSTODY:
        return {
            **custody_preview,
            "bridge_version": BRIDGE_VERSION,
            "bridge_mode": BRIDGE_MODE,
        }

    exact_ids = tuple(
        custody_preview.get("candidate_custody", {}).get("candidate_ids", ())
    )
    if not nominated or nominated not in exact_ids:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_INVALID_CANDIDATE_NOMINATION,
            response_text=(
                "The supplied candidate identifier does not exactly match a candidate "
                "generated from this source and action root."
            ),
            reasons=(
                "exact_candidate_id_required",
                "candidate_substitution_prohibited",
            ),
            extra={
                "candidate_custody": custody_preview.get("candidate_custody", {}),
                "nominated_candidate_id": nominated,
            },
        )

    try:
        artifacts = _build_candidate_artifacts(
            text,
            action_root=root,
        )
    except Exception as error:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_GATE_EVALUATION_HELD,
            response_text=(
                "The deterministic candidate chain stopped safely before gate "
                "evaluation, selection, routing, or action."
            ),
            reasons=(
                "candidate_artifact_chain_failed_closed",
                f"exception_type:{type(error).__name__}",
            ),
        )

    if tuple(artifacts["all_candidate_ids"]) != exact_ids:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_GATE_EVALUATION_HELD,
            response_text=(
                "The Bridge 5 artifact chain did not reproduce the exact Bridge 4 "
                "candidate set. Evaluation was blocked."
            ),
            reasons=("candidate_set_reproduction_mismatch",),
        )

    companion = next(
        value
        for value in artifacts["companions"]
        if value.candidate_meaning_id == nominated
    )
    constructed_record = artifacts["constructed_by_id"].get(nominated)
    if constructed_record is None:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_GATE_EVALUATION_HELD,
            response_text=(
                "The exact candidate companion was present but its constructed record "
                "was unavailable. Evaluation was blocked."
            ),
            reasons=("exact_constructed_candidate_record_required",),
        )
    manifest_candidate = artifacts["manifest_records"].get(
        companion.manifest_candidate_record_id
    )
    if manifest_candidate is None:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_GATE_EVALUATION_HELD,
            response_text=(
                "The exact MSM candidate record was unavailable. Evaluation was blocked."
            ),
            reasons=("exact_manifest_candidate_record_required",),
        )

    options = _linked_pair_options(artifacts, constructed_record)
    public_options = tuple(
        {
            key: value
            for key, value in option.items()
            if not key.startswith("_")
        }
        for option in options
    )

    if not predicate_nomination and not layout_nomination:
        if len(options) != 1:
            return _held(
                request,
                action_root=root,
                surface=surface,
                status=STATUS_PREDICATE_FRAME_NOMINATION_REQUIRED,
                response_text=(
                    "The nominated CandidateMeaning preserves more than one exact "
                    "predicate/frame path. Supply one exact predicate-candidate ID and "
                    "one exact role-layout-candidate ID. Nothing was evaluated or selected."
                ),
                reasons=(
                    "predicate_frame_plurality_preserved",
                    "automatic_first_pair_selection_prohibited",
                ),
                extra={
                    "candidate_custody": custody_preview["candidate_custody"],
                    "nominated_candidate_id": nominated,
                    "predicate_frame_options": public_options,
                },
            )
        selected_option = options[0]
    else:
        selected_option = next(
            (
                option
                for option in options
                if option["predicate_candidate_id"] == predicate_nomination
                and option["role_layout_candidate_id"] == layout_nomination
            ),
            None,
        )
        if selected_option is None:
            return _held(
                request,
                action_root=root,
                surface=surface,
                status=STATUS_INVALID_PREDICATE_FRAME_NOMINATION,
                response_text=(
                    "The supplied predicate and role-layout candidate identifiers do not "
                    "form an exact linked pair inside the nominated CandidateMeaning."
                ),
                reasons=(
                    "exact_predicate_frame_pair_required",
                    "cross_predicate_frame_pair_prohibited",
                ),
                extra={
                    "candidate_custody": custody_preview["candidate_custody"],
                    "nominated_candidate_id": nominated,
                    "predicate_frame_options": public_options,
                },
            )

    artifacts.update(
        {
            "manifest_companion": companion,
            "manifest_candidate": manifest_candidate,
            "constructed_record": constructed_record,
            "predicate_candidate": selected_option["_predicate"],
            "role_layout_candidate": selected_option["_layout"],
        }
    )

    try:
        runtime = build_gate_and_eligibility(artifacts)
    except Exception as error:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_GATE_EVALUATION_HELD,
            response_text=(
                "The real gate or eligibility chain failed closed. No selected meaning, "
                "route, action, memory write, or LLM call occurred."
            ),
            reasons=(
                "gate_or_eligibility_chain_failed_closed",
                f"exception_type:{type(error).__name__}",
            ),
            extra={
                "candidate_custody": custody_preview["candidate_custody"],
                "nominated_candidate_id": nominated,
                "predicate_frame_options": public_options,
            },
        )

    expectancy = runtime["expectancy_result"]
    congruity = runtime["congruity_result"]
    connectedness = runtime["connectedness_result"]
    purpose = runtime["purpose_result"]
    composition = runtime["composition_result"]
    gate_integration = runtime["gate_integration"]
    eligibility = runtime["eligibility_result"]

    forbidden = (
        eligibility.selected_meaning_created,
        eligibility.selection_performed,
        eligibility.msm_v1_modified,
        eligibility.route_created,
        eligibility.tool_invoked,
        eligibility.action_performed,
        eligibility.memory_written,
        eligibility.language_model_used,
        eligibility.hidden_classifier_used,
        gate_integration.selected_meaning_created,
    )
    if any(forbidden):
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_GATE_EVALUATION_HELD,
            response_text=(
                "A prohibited downstream-authority flag appeared. Bridge 5 failed closed."
            ),
            reasons=("prohibited_downstream_authority_flag_detected",),
        )

    outcome = _value(eligibility.outcome)
    eligible = bool(
        eligibility.eligible_for_selected_meaning_construction
    )
    return {
        **_base(request, action_root=root, surface=surface),
        "status": STATUS_ELIGIBILITY_EVALUATED_HELD,
        "intent": "exact_candidate_gate_and_eligibility_evaluation_hold",
        "response_text": (
            f"{reason} The exact nominated candidate and predicate/frame pair passed "
            "through the real Slice 40C-F, 40G, 40H, and 41C chain. "
            f"Eligibility outcome: {outcome}. Progression remains held before Slice "
            "41D selected-meaning construction."
        ),
        "candidate_custody": custody_preview["candidate_custody"],
        "nominated_candidate_id": nominated,
        "predicate_frame_pair": {
            key: value
            for key, value in selected_option.items()
            if not key.startswith("_")
        },
        "gate_evaluation": {
            "executed": True,
            "candidate_input_ref": expectancy.candidate_input_ref,
            "family_results": {
                "expectancy": {
                    "result_id": expectancy.result_id,
                    "state": _value(expectancy.overall_state),
                },
                "congruity": {
                    "result_id": congruity.result_id,
                    "state": _value(congruity.overall_state),
                },
                "connectedness": {
                    "result_id": connectedness.result_id,
                    "state": _value(connectedness.overall_state),
                },
                "recoverable_purpose": {
                    "result_id": purpose.result_id,
                    "state": _value(purpose.overall_state),
                },
            },
            "composition_executed": True,
            "composition_result_id": composition.result_id,
            "composition_status": _value(composition.composition_status),
            "composition_disposition_count": len(composition.dispositions),
            "msm_gate_custody_created": True,
            "msm_gate_custody_companion_id": (
                gate_integration.companion.companion_id
            ),
            "all_family_results_preserved": bool(
                gate_integration.companion.family_results_preserved
            ),
            "language_model_used": False,
        },
        "selection_boundary": {
            "nomination_recorded": True,
            "predicate_frame_pair_recorded": True,
            "eligibility_evaluated": True,
            "eligibility_result_id": eligibility.result_id,
            "eligibility_outcome": outcome,
            "eligible_for_selected_meaning_construction": eligible,
            "selected_meaning_constructed": False,
            "msm_selected_meaning_integrated": False,
            "slice41d_called": False,
            "slice41e_called": False,
            "hold_reason": (
                "bridge5_stops_before_slice41d_even_if_eligible"
                if eligible
                else "eligibility_outcome_does_not_authorize_slice41d"
            ),
        },
        "blocked_downstream": _BLOCKED_DOWNSTREAM,
        "reasons": (
            "exact_candidate_nomination_verified",
            "exact_predicate_frame_pair_verified",
            "current_slice38_version_custody_verified",
            "four_real_gate_family_results_created",
            "slice40g_composition_created",
            "slice40h_msm_gate_custody_created",
            "slice41c_eligibility_evaluated",
            "slice41d_not_called",
            "echo_forge_llm_not_invoked",
            "no_tool_route_no_action",
        ),
    }


def _plan(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "goal": (
            "Evaluate exact candidate-specific gate custody and selection eligibility "
            "without selecting meaning or creating an executable route."
        ),
        "impossible": True,
        "reason": decision.get(
            "response_text",
            "Eligibility evaluation held.",
        ),
        "steps": [],
        "_language_bridge": decision,
    }


def parse_explicit_plan(
    request: object,
    *,
    surface: str,
) -> dict[str, Any] | None:
    if type(request) is not str:
        return None

    text = request.strip()
    lowered = text.lower()
    prefix = "forge-language-eligibility-hold "
    if not lowered.startswith(prefix):
        return None

    payload = text[len(prefix):]
    parts = [part.strip() for part in payload.split("::")]
    if len(parts) == 3:
        action_root, candidate_id, source = parts
        predicate_candidate_id = ""
        role_layout_candidate_id = ""
    elif len(parts) == 5:
        (
            action_root,
            candidate_id,
            predicate_candidate_id,
            role_layout_candidate_id,
            source,
        ) = parts
    else:
        return _plan(
            _held(
                request,
                action_root="",
                surface=surface,
                status=STATUS_INVALID_INPUT,
                response_text=(
                    "Usage: forge-language-eligibility-hold "
                    "<inspect|report|request> :: <exact-candidate-id> "
                    "[:: <exact-predicate-candidate-id> "
                    ":: <exact-role-layout-candidate-id>] "
                    ":: <source request>"
                ),
                reasons=("explicit_bridge5_syntax_required",),
            )
        )

    return _plan(
        eligibility_hold_decision(
            source,
            action_root=action_root,
            nominated_candidate_id=candidate_id,
            predicate_candidate_id=predicate_candidate_id,
            role_layout_candidate_id=role_layout_candidate_id,
            surface=surface,
            reason="Explicit Bridge 5 eligibility-hold request received.",
        )
    )


def bridge_status() -> dict[str, Any]:
    return {
        "schema_version": "forge-language-bridge-status-v5",
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "bridge4": bridge4_status(),
        "explicit_action_root_required": True,
        "exact_candidate_nomination_required": True,
        "exact_predicate_frame_pair_required_when_plural": True,
        "automatic_first_pair_selection": False,
        "slice40c_expectancy_connected": True,
        "slice40d_congruity_connected": True,
        "slice40e_connectedness_connected": True,
        "slice40f_recoverable_purpose_connected": True,
        "slice40g_gate_composition_connected": True,
        "slice40h_msm_gate_custody_connected": True,
        "slice41c_eligibility_evaluation_connected": True,
        "slice41d_selected_meaning_construction_connected": False,
        "slice41e_msm_selected_meaning_integration_connected": False,
        "meaning_selection_authority": False,
        "tool_routing_authority": False,
        "action_authority": False,
        "forge_interpretation_llm_authority": False,
        "echo_forge_llm_boundary_preserved": True,
        "echo_forge_output_is_forge_authority": False,
        "remaining_forge_explicit_llm_lanes": _REMAINING_FORGE_LLM_LANES,
        "full_forge_echo_authority_separation_completed": False,
        "full_language_replacement_claimed": False,
        "forge_replaced": False,
        "agent_py_changed": False,
    }
