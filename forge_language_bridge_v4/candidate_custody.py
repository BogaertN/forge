"""Bridge 4: exact candidate custody and explicit selection hold.

This bridge extends the accepted Bridge 3 structural chain through the real
Slice 37 concept-candidate proposal, Slice 38 predicate/role-frame candidate
proposal, Slice 39F deterministic CandidateMeaning construction, and Slice 39G
MeaningStructureManifest candidate custody adapter.

Action-root authority must be supplied explicitly by the caller. The bridge
never infers an action root from surface text. A candidate may be explicitly
nominated only by its exact generated identifier. Nomination creates validated
Slice 16 selected-meaning boundary *hold* records because exact Slice 40H gate
custody and a successful Slice 41C eligibility result are not yet present.
Nothing here selects meaning, ranks candidates, routes a tool, executes an
action, writes memory, or calls a language model.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Final

from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.source_field_projection import project_source_field
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import bind_resonant_operator_candidates
from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import construct_candidate_resonant_phase_trails
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import apply_scope_attachment_reference_constraints
from aiweb_language_core_bootstrap.deterministic_structural_derivation import derive_deterministic_structural_analysis
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import propose_structural_concept_candidates
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
from aiweb_selected_meaning_boundary_scaffold import (
    REQUIRED_PRIOR_BOUNDARIES,
    REQUIRED_SELECTION_LAWS,
    build_candidate_selection_reference_record,
    build_selected_meaning_status_record,
    build_selection_basis_record,
    build_selection_constraint_record,
    build_selection_receipt_record,
    build_selection_trace_record,
    validate_candidate_selection_reference_record,
    validate_selected_meaning_status_record,
    validate_selection_basis_record,
    validate_selection_constraint_record,
    validate_selection_receipt_record,
    validate_selection_trace_record,
)
from forge_language_bridge_v3 import bridge_status as bridge3_status
from forge_language_bridge_v3 import structural_preview_decision

BRIDGE_VERSION: Final[str] = "forge_language_bridge_v4"
BRIDGE_MODE: Final[str] = "exact_candidate_custody_explicit_selection_hold"
STATUS_CANDIDATE_CUSTODY: Final[str] = "CANDIDATE_CUSTODY"
STATUS_CANDIDATE_CUSTODY_HELD: Final[str] = "CANDIDATE_CUSTODY_HELD"
STATUS_SELECTION_ELIGIBILITY_HELD: Final[str] = "SELECTION_ELIGIBILITY_HELD"
STATUS_INVALID_INPUT: Final[str] = "INVALID_INPUT"
STATUS_INVALID_CANDIDATE_NOMINATION: Final[str] = "INVALID_CANDIDATE_NOMINATION"

_ALLOWED_ACTION_ROOT_FRAMES: Final[dict[str, str]] = {
    "inspect": "inspect_read_only",
    "report": "report_attributed_content",
    "request": "request_non_authorizing",
}

_REMAINING_EXPLICIT_LLM_LANES: Final[tuple[str, ...]] = (
    "diagnostic_output_analysis",
    "forge_command_implementation_generation",
    "forge_self_suggestion_generation",
    "engine_review_generation",
    "generic_repair_draft_generation",
    "generic_repair_candidate_review",
    "tool_wrapper_generation",
)

_BLOCKED_DOWNSTREAM: Final[tuple[str, ...]] = (
    "truth_decision",
    "permission_grant",
    "delivery_action",
    "execution_authority",
    "memory_write",
    "evidence_validation",
    "tool_invocation",
    "route_creation",
    "action_execution",
)


def _value(value: object) -> str:
    return str(getattr(value, "value", value))


def _base(*, request: object, action_root: str, surface: str) -> dict[str, Any]:
    text = request if type(request) is str else ""
    return {
        "schema_version": "forge-language-bridge-v4",
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
    }


def _held(
    request: object,
    *,
    action_root: str,
    surface: str,
    status: str,
    reason: str,
    reasons: tuple[str, ...],
) -> dict[str, Any]:
    return {
        **_base(request=request, action_root=action_root, surface=surface),
        "status": status,
        "intent": "candidate_custody_hold",
        "response_text": reason,
        "candidate_custody": {
            "chain_completed": False,
            "candidate_meaning_count": 0,
            "manifest_candidate_count": 0,
            "candidate_ids": [],
            "selected_candidate_id": "",
        },
        "selection_boundary": {
            "nomination_recorded": False,
            "eligibility_evaluated": False,
            "selected_meaning_constructed": False,
            "msm_selected_meaning_integrated": False,
        },
        "reasons": reasons,
    }


def candidate_custody_decision(
    request: object,
    *,
    action_root: str,
    surface: str,
    reason: str,
) -> dict[str, Any]:
    """Construct exact candidate custody without selecting any candidate."""
    text = request if type(request) is str else ""
    root = str(action_root or "").strip().lower()
    base = _base(request=request, action_root=root, surface=surface)

    if not text.strip():
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_INVALID_INPUT,
            reason="Candidate custody requires a non-empty source request.",
            reasons=("non_empty_source_request_required",),
        )

    if root not in _ALLOWED_ACTION_ROOT_FRAMES:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_INVALID_INPUT,
            reason=(
                "Candidate custody requires an explicit accepted action root: "
                "inspect, report, or request. The bridge did not infer one from text."
            ),
            reasons=(
                "explicit_action_root_required",
                "hidden_action_root_inference_prohibited",
            ),
        )

    try:
        custody = capture_input_event(
            text,
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

        frame_key = _ALLOWED_ACTION_ROOT_FRAMES[root]
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
            return _held(
                request,
                action_root=root,
                surface=surface,
                status=STATUS_CANDIDATE_CUSTODY_HELD,
                reason=(
                    "The source chain produced no exact concept/sense pair that could "
                    "enter the explicit action-root compatibility boundary."
                ),
                reasons=("no_exact_concept_sense_compatibility_pair",),
            )

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
    except Exception as error:
        return _held(
            request,
            action_root=root,
            surface=surface,
            status=STATUS_CANDIDATE_CUSTODY_HELD,
            reason=(
                "The deterministic candidate chain stopped safely before selection, "
                "routing, or action."
            ),
            reasons=(
                "candidate_chain_exception_held",
                f"exception_type:{type(error).__name__}",
            ),
        )

    manifest = getattr(integration_result, "manifest", None)
    companions = tuple(getattr(integration_result, "companions", ()) or ())
    constructed_records = tuple(
        getattr(constructor_result, "constructed_records", ()) or ()
    )
    candidate_ids = tuple(
        str(getattr(companion, "candidate_meaning_id", ""))
        for companion in companions
        if str(getattr(companion, "candidate_meaning_id", ""))
    )

    if manifest is None or not companions or not candidate_ids:
        return {
            **base,
            "status": STATUS_CANDIDATE_CUSTODY_HELD,
            "intent": "candidate_custody_hold",
            "response_text": (
                "The exact candidate pipeline preserved its result but produced no "
                "candidate that could enter MSM-v1 custody. Nothing was selected."
            ),
            "candidate_custody": {
                "chain_completed": True,
                "source_event_id": str(getattr(custody.event, "event_id", "")),
                "source_sha256": str(getattr(custody, "observed_source_sha256", "")),
                "slice37_result_id": str(getattr(slice37, "result_id", "")),
                "slice37_status": _value(getattr(slice37, "status", "")),
                "slice38_result_id": str(getattr(slice38, "result_id", "")),
                "slice38_status": _value(getattr(slice38, "status", "")),
                "constructor_result_id": str(getattr(constructor_result, "result_id", "")),
                "constructor_status": _value(getattr(constructor_result, "status", "")),
                "integration_result_id": str(getattr(integration_result, "result_id", "")),
                "integration_status": _value(getattr(integration_result, "status", "")),
                "candidate_meaning_count": len(constructed_records),
                "manifest_candidate_count": int(
                    getattr(integration_result, "manifest_candidate_count", 0) or 0
                ),
                "candidate_ids": list(candidate_ids),
                "selected_candidate_id": "",
            },
            "selection_boundary": {
                "nomination_recorded": False,
                "eligibility_evaluated": False,
                "selected_meaning_constructed": False,
                "msm_selected_meaning_integrated": False,
            },
            "reasons": ("candidate_or_manifest_custody_unavailable",),
        }

    entries: list[dict[str, Any]] = []
    records_by_id = {}
    for record in constructed_records:
        state = getattr(record, "candidate_meaning_state", None)
        identity = getattr(state, "identity", None)
        candidate_id = str(getattr(identity, "candidate_meaning_id", ""))
        if candidate_id:
            records_by_id[candidate_id] = record

    manifest_records = {
        str(getattr(record, "record_id", "")): record
        for record in tuple(getattr(manifest, "candidate_meanings", ()) or ())
    }

    for companion in companions:
        candidate_id = str(getattr(companion, "candidate_meaning_id", ""))
        constructed = records_by_id.get(candidate_id)
        state = getattr(constructed, "candidate_meaning_state", None)
        manifest_record_id = str(
            getattr(companion, "manifest_candidate_record_id", "")
        )
        manifest_record = manifest_records.get(manifest_record_id)
        entries.append(
            {
                "candidate_meaning_id": candidate_id,
                "manifest_candidate_record_id": manifest_record_id,
                "manifest_companion_id": str(getattr(companion, "companion_id", "")),
                "candidate_state_id": str(getattr(companion, "candidate_state_id", "")),
                "construction_receipt_ref": str(
                    getattr(companion, "construction_receipt_ref", "")
                ),
                "source_expression_ref": str(
                    getattr(manifest_record, "source_expression_ref", "")
                ),
                "communicative_act_ref": str(
                    getattr(manifest_record, "communicative_act", "")
                ),
                "concept_ref_count": len(
                    tuple(getattr(manifest_record, "concept_refs", ()) or ())
                ),
                "ambiguity_reason_count": len(
                    tuple(getattr(manifest_record, "ambiguity_reasons", ()) or ())
                ),
                "unresolved_referent_count": len(
                    tuple(getattr(manifest_record, "unresolved_referents", ()) or ())
                ),
                "candidate_limitation_count": len(
                    tuple(getattr(state, "limitations", ()) or ())
                ),
                "candidate_only": True,
                "selected": False,
            }
        )

    return {
        **base,
        "status": STATUS_CANDIDATE_CUSTODY,
        "intent": "exact_candidate_meaning_custody_preview",
        "response_text": (
            f"{reason} Exact candidate custody completed for action root {root}; "
            f"{len(entries)} candidate record(s) entered MSM-v1 candidate custody. "
            "No candidate was ranked or selected."
        ),
        "candidate_custody": {
            "chain_completed": True,
            "source_event_id": str(getattr(custody.event, "event_id", "")),
            "source_sha256": str(getattr(custody, "observed_source_sha256", "")),
            "structural_result_id": str(getattr(structural, "result_id", "")),
            "slice37_result_id": str(getattr(slice37, "result_id", "")),
            "slice37_status": _value(getattr(slice37, "status", "")),
            "concept_candidate_count": len(tuple(slice37.concept_candidates)),
            "sense_candidate_count": len(tuple(slice37.sense_candidates)),
            "slice38_result_id": str(getattr(slice38, "result_id", "")),
            "slice38_status": _value(getattr(slice38, "status", "")),
            "predicate_candidate_count": len(
                tuple(getattr(slice38, "action_root_predicate_candidates", ()) or ())
            ),
            "role_layout_candidate_count": len(
                tuple(getattr(slice38, "role_layout_candidates", ()) or ())
            ),
            "constructor_result_id": str(getattr(constructor_result, "result_id", "")),
            "constructor_status": _value(getattr(constructor_result, "status", "")),
            "integration_result_id": str(getattr(integration_result, "result_id", "")),
            "integration_status": _value(getattr(integration_result, "status", "")),
            "manifest_id": str(getattr(manifest, "manifest_id", "")),
            "candidate_meaning_count": len(constructed_records),
            "manifest_candidate_count": len(entries),
            "candidate_ids": list(candidate_ids),
            "candidates": entries,
            "selected_candidate_id": "",
            "candidate_plurality_preserved": True,
            "language_model_used": False,
        },
        "selection_boundary": {
            "nomination_recorded": False,
            "eligibility_evaluated": False,
            "selected_meaning_constructed": False,
            "msm_selected_meaning_integrated": False,
            "exact_slice40h_gate_custody_present": False,
            "exact_slice41c_eligibility_result_present": False,
        },
        "reasons": (
            "explicit_action_root_received_without_surface_inference",
            "real_slice37_candidate_proposal_executed",
            "real_slice38_candidate_frame_proposal_executed",
            "real_slice39f_candidate_meaning_constructor_executed",
            "real_slice39g_msm_candidate_custody_executed",
            "automatic_selection_prohibited",
        ),
    }


def selection_nomination_hold_decision(
    request: object,
    *,
    action_root: str,
    nominated_candidate_id: str,
    surface: str,
    reason: str,
) -> dict[str, Any]:
    """Validate an exact nomination and create held boundary custody records."""
    custody_decision = candidate_custody_decision(
        request,
        action_root=action_root,
        surface=surface,
        reason=reason,
    )
    if custody_decision.get("status") != STATUS_CANDIDATE_CUSTODY:
        return custody_decision

    candidate_custody = custody_decision["candidate_custody"]
    exact_ids = tuple(candidate_custody.get("candidate_ids") or ())
    nominated = str(nominated_candidate_id or "").strip()
    if not nominated or nominated not in exact_ids:
        return {
            **custody_decision,
            "status": STATUS_INVALID_CANDIDATE_NOMINATION,
            "intent": "explicit_candidate_nomination_rejected",
            "response_text": (
                "The supplied candidate identifier does not exactly match a candidate "
                "generated from this source, action root, and current deterministic chain."
            ),
            "selection_boundary": {
                "nomination_recorded": False,
                "nominated_candidate_id": nominated,
                "exact_candidate_match": False,
                "eligibility_evaluated": False,
                "selected_meaning_constructed": False,
                "msm_selected_meaning_integrated": False,
            },
            "reasons": (
                "exact_candidate_id_required",
                "candidate_substitution_prohibited",
                "automatic_selection_prohibited",
            ),
        }

    candidate_entry = next(
        entry
        for entry in candidate_custody["candidates"]
        if entry["candidate_meaning_id"] == nominated
    )
    group_id = str(candidate_custody.get("manifest_id") or "")
    upstream = (
        str(candidate_custody.get("slice37_result_id") or ""),
        str(candidate_custody.get("slice38_result_id") or ""),
        str(candidate_custody.get("constructor_result_id") or ""),
        str(candidate_custody.get("integration_result_id") or ""),
        candidate_entry["manifest_candidate_record_id"],
        candidate_entry["manifest_companion_id"],
    )
    uncertainty = (
        "missing_exact_slice40h_gate_custody",
        "missing_exact_slice41c_selection_eligibility_result",
        f"slice37_status:{candidate_custody.get('slice37_status')}",
        f"slice38_status:{candidate_custody.get('slice38_status')}",
    )

    reference = build_candidate_selection_reference_record(
        candidate_meaning_id=nominated,
        candidate_group_id=group_id,
        source_expression_ref=candidate_entry["source_expression_ref"],
        candidate_role="held_candidate_reference",
        selection_reference_status="candidate_selection_held_boundary",
        upstream_boundary_refs=upstream,
        non_selected_candidate_refs=tuple(
            candidate_id for candidate_id in exact_ids if candidate_id != nominated
        ),
        selection_reason_refs=(
            "explicit_exact_candidate_nomination",
            "selection_eligibility_not_yet_satisfied",
        ),
    )
    basis = build_selection_basis_record(
        basis_key="bridge4_explicit_nomination_insufficient_gate_custody",
        selected_candidate_ref=nominated,
        basis_kind="insufficient_support_boundary",
        basis_status="basis_held_boundary",
        support_refs=(
            reference.selection_reference_id,
            candidate_entry["manifest_companion_id"],
        ),
        constraint_refs=(
            "missing_exact_slice40h_gate_custody",
            "missing_exact_slice41c_selection_eligibility_result",
        ),
        rejected_basis_refs=(),
        uncertainty_refs=uncertainty,
    )
    constraint = build_selection_constraint_record(
        constraint_key="bridge4_selected_meaning_progression_hold",
        constraint_kind="prior_boundary_dependency",
        constraint_status="constraint_blocked_boundary",
        required_prior_boundary_refs=REQUIRED_PRIOR_BOUNDARIES,
        required_law_refs=REQUIRED_SELECTION_LAWS,
        blocked_downstream_refs=_BLOCKED_DOWNSTREAM,
        enforcement_note=(
            "Exact candidate nomination is custody only. Exact Slice 40H gate custody "
            "and successful Slice 41C eligibility are required before Slice 41D."
        ),
    )
    status_record = build_selected_meaning_status_record(
        candidate_meaning_id=nominated,
        selection_reference_id=reference.selection_reference_id,
        selection_basis_id=basis.selection_basis_id,
        selection_constraint_id=constraint.selection_constraint_id,
        selected_meaning_status="selection_held_boundary",
        selection_scope="held_boundary_only",
        confidence_boundary="unknown_confidence_boundary",
        uncertainty_refs=uncertainty,
        required_law_refs=REQUIRED_SELECTION_LAWS,
    )
    trace = build_selection_trace_record(
        selected_meaning_id=status_record.selected_meaning_id,
        candidate_group_id=group_id,
        selection_step_refs=(
            reference.selection_reference_id,
            basis.selection_basis_id,
            constraint.selection_constraint_id,
            status_record.selected_meaning_id,
        ),
        comparison_refs=exact_ids,
        non_selected_candidate_refs=tuple(
            candidate_id for candidate_id in exact_ids if candidate_id != nominated
        ),
        trace_status="selection_trace_held_boundary",
        trace_scope="trace_record_only_not_delivery_not_execution",
    )
    receipt = build_selection_receipt_record(
        selected_meaning_id=status_record.selected_meaning_id,
        selection_trace_id=trace.selection_trace_id,
        receipt_status="selection_receipt_held_boundary",
        receipt_effect="held_only_no_downstream_authority",
        required_law_refs=REQUIRED_SELECTION_LAWS,
        downstream_block_refs=_BLOCKED_DOWNSTREAM,
        audit_note=(
            "Bridge 4 recorded exact nomination custody and held progression before "
            "selection eligibility, selected meaning construction, routing, or action."
        ),
    )

    validations = {
        "candidate_reference": validate_candidate_selection_reference_record(reference),
        "selection_basis": validate_selection_basis_record(basis),
        "selection_constraint": validate_selection_constraint_record(constraint),
        "selected_meaning_status": validate_selected_meaning_status_record(status_record),
        "selection_trace": validate_selection_trace_record(trace),
        "selection_receipt": validate_selection_receipt_record(receipt),
    }
    validation_ok = all(report.ok for report in validations.values())
    if not validation_ok:
        return {
            **custody_decision,
            "status": STATUS_CANDIDATE_CUSTODY_HELD,
            "intent": "selection_boundary_validation_hold",
            "response_text": (
                "The exact nomination was found, but boundary-record validation failed "
                "closed. No selected meaning was constructed."
            ),
            "selection_boundary": {
                "nomination_recorded": False,
                "nominated_candidate_id": nominated,
                "exact_candidate_match": True,
                "boundary_validation_ok": False,
                "validation_issue_counts": {
                    name: report.issue_count for name, report in validations.items()
                },
                "eligibility_evaluated": False,
                "selected_meaning_constructed": False,
                "msm_selected_meaning_integrated": False,
            },
            "reasons": ("selection_boundary_validation_failed_closed",),
        }

    return {
        **custody_decision,
        "status": STATUS_SELECTION_ELIGIBILITY_HELD,
        "intent": "explicit_candidate_nomination_custody_held_before_eligibility",
        "response_text": (
            "The exact candidate nomination was recorded in validated boundary custody. "
            "Progression is held because exact Slice 40H gate custody and a successful "
            "Slice 41C eligibility result are absent. No selected meaning was constructed."
        ),
        "selection_boundary": {
            "nomination_recorded": True,
            "nominated_candidate_id": nominated,
            "exact_candidate_match": True,
            "boundary_validation_ok": True,
            "candidate_selection_reference": asdict(reference),
            "selection_basis": asdict(basis),
            "selection_constraint": asdict(constraint),
            "selected_meaning_status_boundary": asdict(status_record),
            "selection_trace": asdict(trace),
            "selection_receipt": asdict(receipt),
            "eligibility_evaluated": False,
            "selected_meaning_constructed": False,
            "msm_selected_meaning_integrated": False,
            "exact_slice40h_gate_custody_present": False,
            "exact_slice41c_eligibility_result_present": False,
            "slice41d_called": False,
            "slice41e_called": False,
        },
        "reasons": (
            "exact_candidate_nomination_recorded",
            "validated_selected_meaning_boundary_hold_records_created",
            "exact_slice40h_gate_custody_required",
            "successful_slice41c_eligibility_required",
            "one_candidate_is_not_automatic_selection",
            "no_selected_meaning_construction",
        ),
    }


def _plan(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "goal": (
            "Expose exact deterministic candidate custody and selection-boundary "
            "evidence without creating an executable route."
        ),
        "impossible": True,
        "reason": decision.get("response_text", "Candidate custody held."),
        "steps": [],
        "_language_bridge": decision,
    }


def parse_explicit_plan(
    request: object,
    *,
    surface: str,
) -> dict[str, Any] | None:
    """Parse only explicit Bridge 4 command syntax; never infer from ordinary text."""
    if type(request) is not str:
        return None
    text = request.strip()
    lowered = text.lower()
    candidate_prefix = "forge-language-candidate "
    selection_prefix = "forge-language-selection-hold "

    if lowered.startswith(candidate_prefix):
        payload = text[len(candidate_prefix):]
        if "::" not in payload:
            return _plan(
                _held(
                    request,
                    action_root="",
                    surface=surface,
                    status=STATUS_INVALID_INPUT,
                    reason=(
                        "Usage: forge-language-candidate <inspect|report|request> "
                        ":: <source request>"
                    ),
                    reasons=("explicit_candidate_preview_syntax_required",),
                )
            )
        action_root, source = (part.strip() for part in payload.split("::", 1))
        return _plan(
            candidate_custody_decision(
                source,
                action_root=action_root,
                surface=surface,
                reason="Explicit Bridge 4 candidate-custody request received.",
            )
        )

    if lowered.startswith(selection_prefix):
        payload = text[len(selection_prefix):]
        parts = [part.strip() for part in payload.split("::", 2)]
        if len(parts) != 3:
            return _plan(
                _held(
                    request,
                    action_root="",
                    surface=surface,
                    status=STATUS_INVALID_INPUT,
                    reason=(
                        "Usage: forge-language-selection-hold "
                        "<inspect|report|request> :: <exact-candidate-id> "
                        ":: <source request>"
                    ),
                    reasons=("explicit_selection_hold_syntax_required",),
                )
            )
        action_root, candidate_id, source = parts
        return _plan(
            selection_nomination_hold_decision(
                source,
                action_root=action_root,
                nominated_candidate_id=candidate_id,
                surface=surface,
                reason="Explicit Bridge 4 candidate nomination received.",
            )
        )

    return None


def bridge_status() -> dict[str, Any]:
    return {
        "schema_version": "forge-language-bridge-status-v4",
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "bridge3": bridge3_status(),
        "ordinary_unsupported_path_remains_bridge3_structural_preview": True,
        "explicit_action_root_required": True,
        "accepted_explicit_action_roots": tuple(_ALLOWED_ACTION_ROOT_FRAMES),
        "slice37_candidate_proposal_connected": True,
        "slice38_predicate_role_candidate_proposal_connected": True,
        "slice39f_candidate_meaning_constructor_connected": True,
        "slice39g_msm_candidate_custody_connected": True,
        "selected_meaning_boundary_hold_scaffold_connected": True,
        "exact_candidate_nomination_required": True,
        "automatic_candidate_selection": False,
        "selection_eligibility_evaluation_connected": False,
        "slice40h_gate_custody_connected": False,
        "slice41c_eligibility_result_connected": False,
        "selected_meaning_construction_connected": False,
        "msm_selected_meaning_integration_connected": False,
        "meaning_selection_authority": False,
        "tool_routing_authority": False,
        "action_authority": False,
        "full_language_replacement_claimed": False,
        "forge_replaced": False,
        "agent_py_changed": False,
        "remaining_explicit_llm_lanes": _REMAINING_EXPLICIT_LLM_LANES,
    }
