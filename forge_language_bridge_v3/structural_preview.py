"""Bridge 3: real deterministic language-core structural preview.

This bridge connects Forge's unsupported ordinary-request path to the already
accepted source-custody through deterministic-structural-derivation chain. It
never selects meaning, routes a tool, executes a command, writes memory, or
calls a language model. Explicit maker/review model lanes remain separately
governed and visible.
"""
from __future__ import annotations
import hashlib
from typing import Any, Final
from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.source_field_projection import project_source_field
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import bind_resonant_operator_candidates
from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import construct_candidate_resonant_phase_trails
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import apply_scope_attachment_reference_constraints
from aiweb_language_core_bootstrap.deterministic_structural_derivation import derive_deterministic_structural_analysis
from forge_language_bridge_v2 import bridge_status as bridge2_status

BRIDGE_VERSION: Final[str] = "forge_language_bridge_v3"
BRIDGE_MODE: Final[str] = "deterministic_structural_preview_no_selection"
STATUS_STRUCTURAL_PREVIEW: Final[str] = "STRUCTURAL_PREVIEW"
STATUS_BOUNDARY_BLOCKED: Final[str] = "BOUNDARY_BLOCKED"
_REMAINING_EXPLICIT_LLM_LANES: Final[tuple[str, ...]] = (
    "diagnostic_output_analysis", "forge_command_implementation_generation",
    "forge_self_suggestion_generation", "engine_review_generation",
    "generic_repair_draft_generation", "generic_repair_candidate_review",
    "tool_wrapper_generation",
)

def _value(value: object) -> object:
    return getattr(value, "value", value)

def _stage(name: str, result: object) -> dict[str, Any]:
    return {
        "stage": name,
        "result_id": str(getattr(result, "result_id", "")),
        "status": str(_value(getattr(result, "status", ""))),
        "reason_code": str(getattr(result, "reason_code", "")),
        "filesystem_read_performed": bool(getattr(result, "filesystem_read_performed", False)),
        "filesystem_write_performed": bool(getattr(result, "filesystem_write_performed", False)),
        "network_access_performed": bool(getattr(result, "network_access_performed", False)),
        "memory_read_performed": bool(getattr(result, "memory_read_performed", False)),
        "memory_write_performed": bool(getattr(result, "memory_write_performed", False)),
        "tool_routing_performed": bool(getattr(result, "tool_routing_performed", False)),
        "action_performed": bool(getattr(result, "action_performed", False)),
        "delivery_performed": bool(getattr(result, "delivery_performed", False)),
    }

def _request_id(surface: str, source_sha256: str, text: str) -> str:
    return "flb3_" + hashlib.sha256((surface + "\0" + source_sha256 + "\0" + text).encode("utf-8")).hexdigest()[:18]

def structural_preview_decision(request: object, *, surface: str, reason: str) -> dict[str, Any]:
    text = request if type(request) is str else ""
    custody = capture_input_event(request, source_id="forge.language.bridge.v3", channel_id=surface, sequence_number=0)
    source_sha256 = str(getattr(custody, "observed_source_sha256", "") or "")
    rid = _request_id(surface, source_sha256, text)
    common = {
        "schema_version": "forge-language-bridge-v3",
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "request_id": rid,
        "surface": surface,
        "source_text_sha256": source_sha256,
        "normalized_text": text.strip(),
        "handled": True,
        "intent": "deterministic_structural_preview",
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
        "tool_routing_authority": False,
        "action_authority": False,
        "delivery_authority": False,
    }
    if not bool(getattr(custody, "custody_created", False)) or not bool(getattr(custody, "structural_progression_allowed", False)):
        return {
            **common,
            "status": STATUS_BOUNDARY_BLOCKED,
            "response_text": "The language core preserved the input boundary but could not lawfully progress into structural analysis.",
            "structural_preview": {"custody": _stage("input_event_custody", custody), "chain_completed": False},
            "recursive_manifest_preview": {"manifest_kind": "bounded_recursive_manifest_preview", "manifest_status": "custody_boundary_blocked", "source_sha256": source_sha256, "rmc_authority": False, "memory_write_allowed": False},
            "reasons": ("input_custody_boundary_blocked",),
        }
    try:
        projection = project_source_field(custody.event)
        binding = bind_resonant_operator_candidates(projection)
        trails = construct_candidate_resonant_phase_trails(projection, binding)
        constraints = apply_scope_attachment_reference_constraints(projection, binding, trails)
        structural = derive_deterministic_structural_analysis(custody, projection, binding, trails, constraints)
    except Exception as error:
        return {
            **common,
            "status": STATUS_BOUNDARY_BLOCKED,
            "response_text": "The deterministic structural chain stopped safely before meaning selection or action.",
            "structural_preview": {"custody": _stage("input_event_custody", custody), "chain_completed": False, "error_type": type(error).__name__},
            "recursive_manifest_preview": {"manifest_kind": "bounded_recursive_manifest_preview", "manifest_status": "structural_chain_held", "source_sha256": source_sha256, "rmc_authority": False, "memory_write_allowed": False},
            "reasons": ("structural_chain_exception_held",),
        }
    binding_set = getattr(binding, "binding_set", None)
    phase_set = getattr(trails, "phase_trail_set", None)
    constraint_set = getattr(constraints, "constraint_set", None)
    structural_set = getattr(structural, "structural_set", None)
    preview = {
        "chain_completed": True,
        "custody": _stage("input_event_custody", custody),
        "projection": _stage("source_field_projection", projection),
        "binding": _stage("resonant_operator_candidate_binding", binding),
        "phase_trails": _stage("candidate_resonant_phase_trails", trails),
        "constraints": _stage("scope_attachment_reference_constraints", constraints),
        "structural_derivation": _stage("deterministic_structural_derivation", structural),
        "binding_candidate_count": int(getattr(binding_set, "candidate_count", 0) or 0),
        "phase_trail_count": int(getattr(phase_set, "trail_count", 0) or 0),
        "constrained_trail_count": int(getattr(constraint_set, "constrained_trail_count", 0) or 0),
        "structural_candidate_count": int(getattr(structural_set, "candidate_count", 0) or 0),
        "structural_status": str(_value(getattr(structural, "status", ""))),
        "structural_reason_code": str(getattr(structural, "reason_code", "")),
        "candidate_plurality_preserved": bool(getattr(structural_set, "structural_candidate_plurality_preserved", False)),
        "selected_structural_candidate_id": str(getattr(structural_set, "selected_structural_candidate_id", "") or ""),
        "selected_meaning": False,
        "language_model_used": False,
        "source_ancestry_preserved": bool(getattr(structural, "source_preserved_in_custody", False)),
    }
    response = (
        f"{reason} Structural status: {preview['structural_status']}; "
        f"candidates preserved: {preview['structural_candidate_count']}. "
        "No meaning was selected, no command was routed, and no action was executed."
    )
    return {
        **common,
        "status": STATUS_STRUCTURAL_PREVIEW,
        "response_text": response,
        "structural_preview": preview,
        "recursive_manifest_preview": {
            "manifest_kind": "bounded_recursive_manifest_preview",
            "manifest_status": "structural_preview_compiled_no_mu_t_selection",
            "source_sha256": source_sha256,
            "custody_result_id": str(getattr(custody, "result_id", "")),
            "structural_result_id": str(getattr(structural, "result_id", "")),
            "candidate_count": preview["structural_candidate_count"],
            "decision_status": STATUS_STRUCTURAL_PREVIEW,
            "rmc_authority": False,
            "selected_meaning_authority": False,
            "execution_authority": False,
            "memory_write_allowed": False,
        },
        "reasons": (
            "ordinary_interpretation_model_fallback_disabled",
            "accepted_deterministic_structural_chain_executed",
            "candidate_plurality_preserved_without_selection",
        ),
    }

def structural_preview_plan(request: object, *, surface: str, reason: str) -> dict[str, Any]:
    decision = structural_preview_decision(request, surface=surface, reason=reason)
    return {
        "goal": "Preserve the request and expose deterministic structural evidence without inventing an executable route.",
        "impossible": True,
        "reason": decision.get("response_text", reason),
        "steps": [],
        "_language_bridge": decision,
    }

def bridge_status() -> dict[str, Any]:
    return {
        "schema_version": "forge-language-bridge-status-v3",
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "bridge2": bridge2_status(),
        "ordinary_interactive_agent_ask_fallback": False,
        "patch199_planner_ollama_fallback": False,
        "operator_console_interpretation_ollama_fallback": False,
        "unsupported_requests_receive_structural_preview": True,
        "source_custody_connected": True,
        "source_field_projection_connected": True,
        "candidate_binding_connected": True,
        "phase_trail_construction_connected": True,
        "scope_constraint_connected": True,
        "deterministic_structural_derivation_connected": True,
        "selected_meaning_authority": False,
        "tool_routing_authority": False,
        "action_authority": False,
        "full_language_replacement_claimed": False,
        "forge_replaced": False,
        "agent_py_changed": False,
        "remaining_explicit_llm_lanes": _REMAINING_EXPLICIT_LLM_LANES,
    }
