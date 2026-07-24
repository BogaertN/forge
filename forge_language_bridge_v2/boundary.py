"""Bridge 2 boundary: remove model fallback from request interpretation.

Bridge 2 does not claim full language replacement. It closes only the ordinary
interpretation fallthroughs that previously called Qwen/Ollama when a request
was not covered by Bridge 1. Explicit generation/review commands remain visible
and separately governed for later replacement bridges.
"""

from __future__ import annotations

import hashlib
from typing import Any, Final

from aiweb_language_core_bootstrap.input_event_custody.capture import capture_input_event
from forge_language_bridge_v1 import bridge_status as bridge1_status

BRIDGE_VERSION: Final[str] = "forge_language_bridge_v2"
BRIDGE_MODE: Final[str] = "no_ordinary_interpretation_model_fallback"
STATUS_UNSUPPORTED: Final[str] = "UNSUPPORTED_HOLD"

_REMAINING_EXPLICIT_LLM_LANES: Final[tuple[str, ...]] = (
    "diagnostic_output_analysis",
    "forge_command_implementation_generation",
    "forge_self_suggestion_generation",
    "engine_review_generation",
    "generic_repair_draft_generation",
    "generic_repair_candidate_review",
    "tool_wrapper_generation",
)


def _custody(request: object, surface: str) -> dict[str, Any]:
    result = capture_input_event(
        request,
        source_id="forge.language.bridge.v2",
        channel_id=surface,
        sequence_number=0,
    )
    return {
        "result_id": result.result_id,
        "status": getattr(result.status, "value", str(result.status)),
        "reason_code": result.reason_code,
        "custody_created": result.custody_created,
        "structural_progression_allowed": result.structural_progression_allowed,
        "observed_source_sha256": result.observed_source_sha256,
        "filesystem_read_performed": result.filesystem_read_performed,
        "filesystem_write_performed": result.filesystem_write_performed,
        "network_access_performed": result.network_access_performed,
        "memory_read_performed": result.memory_read_performed,
        "memory_write_performed": result.memory_write_performed,
        "tool_routing_performed": result.tool_routing_performed,
        "action_performed": result.action_performed,
        "delivery_performed": result.delivery_performed,
    }


def unsupported_request_decision(
    request: object,
    *,
    surface: str,
    reason: str,
) -> dict[str, Any]:
    custody = _custody(request, surface)
    text = request if type(request) is str else ""
    source_sha256 = str(custody.get("observed_source_sha256") or "")
    request_id = "flb2_" + hashlib.sha256(
        (surface + "\0" + source_sha256 + "\0" + text).encode("utf-8")
    ).hexdigest()[:18]
    return {
        "schema_version": "forge-language-bridge-v2",
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "request_id": request_id,
        "surface": surface,
        "source_text_sha256": source_sha256,
        "normalized_text": text.strip(),
        "handled": True,
        "status": STATUS_UNSUPPORTED,
        "intent": "unsupported_request_hold",
        "route": "",
        "args": "",
        "response_text": reason,
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
        "input_custody": custody,
        "recursive_manifest_preview": {
            "manifest_kind": "bounded_recursive_manifest_preview",
            "manifest_status": "unsupported_hold_not_compiled_mu_t",
            "source_sha256": source_sha256,
            "decision_status": STATUS_UNSUPPORTED,
            "rmc_authority": False,
            "selected_meaning_authority": False,
            "execution_authority": False,
            "memory_write_allowed": False,
        },
        "reasons": (
            "ordinary_interpretation_model_fallback_disabled",
            "unsupported_request_preserved_without_invention",
        ),
    }


def unsupported_plan(
    request: object,
    *,
    surface: str,
    reason: str,
) -> dict[str, Any]:
    decision = unsupported_request_decision(request, surface=surface, reason=reason)
    return {
        "goal": "Preserve unsupported request without model interpretation.",
        "impossible": True,
        "reason": reason,
        "steps": [],
        "_language_bridge": decision,
    }


def bridge_status() -> dict[str, Any]:
    return {
        "schema_version": "forge-language-bridge-status-v2",
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "bridge1": bridge1_status(),
        "ordinary_interactive_agent_ask_fallback": False,
        "patch199_planner_ollama_fallback": False,
        "operator_console_interpretation_ollama_fallback": False,
        "unsupported_requests_are_held": True,
        "full_language_replacement_claimed": False,
        "forge_replaced": False,
        "agent_py_changed": False,
        "remaining_explicit_llm_lanes": _REMAINING_EXPLICIT_LLM_LANES,
    }
