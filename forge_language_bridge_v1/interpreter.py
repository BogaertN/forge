"""Bounded deterministic interpreter for the Forge workshop.

Bridge 1 intentionally handles a small fixed request family before the
historical Qwen/Ollama path. It preserves the existing Forge command functions
and approval gates. Unsupported requests remain eligible for the historical
fallback until later replacement bridges are accepted.

This module:
- uses accepted input-event custody in memory;
- performs exact deterministic phrase/regular-expression matching;
- returns an existing Forge route or an explicit hold;
- creates only a non-authoritative recursive-manifest preview;
- performs no network, shell, filesystem, memory, tool, or simulation action.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any, Final

from aiweb_language_core_bootstrap.input_event_custody.capture import (
    capture_input_event,
)

from .schema import BridgeDecision, SCHEMA_VERSION


BRIDGE_VERSION: Final[str] = "forge_language_bridge_v1"
BRIDGE_MODE: Final[str] = "bounded_deterministic_interpreter"
UNSUPPORTED_FALLBACK: Final[str] = "historical_qwen_ollama_fallback"

_ALLOWED_ROUTES: Final[tuple[str, ...]] = (
    "status",
    "audit",
    "forge-capabilities",
    "forge-protoforge-status",
    "forge-protoforge-simulation-plan",
    "forge-protoforge-result-show",
)

_CAPABILITY_PHRASES: Final[frozenset[str]] = frozenset({
    "what can forge do",
    "what can you do",
    "show forge capabilities",
    "show me forge capabilities",
    "forge capabilities",
    "list forge capabilities",
})

_STATUS_PHRASES: Final[frozenset[str]] = frozenset({
    "show forge status",
    "check forge status",
    "forge status",
    "what is forge status",
    "what is the forge status",
})

_AUDIT_PHRASES: Final[frozenset[str]] = frozenset({
    "check audit",
    "verify audit",
    "check audit chain",
    "verify audit chain",
    "verify the audit chain",
})

_PROTOFORGE_STATUS_PHRASES: Final[frozenset[str]] = frozenset({
    "check protoforge status",
    "show protoforge status",
    "protoforge status",
    "is protoforge running",
    "is protoforge working",
})

_RUN_SIMULATION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:run|execute|launch|start)\b.*\b(?:simulation|sim)\b"
)

_SYMBOLIC_SIMULATION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:build|create|make|prepare|plan|design)\b"
    r".*\b(?:symbolic|frequency|harmonic)\b"
    r".*\b(?:simulation|sim|probe)\b"
)

_CUBE_SIMULATION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:build|create|make|prepare|plan|design)\b"
    r".*\b(?:falling\s+cube|cube|pybullet)\b"
    r".*\b(?:simulation|sim)?\b"
)

_RESULT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:show|display|read|inspect)\b"
    r".*\b(?:simulation|protoforge)\b"
    r".*\b(?:result|results|output)\b"
    r"(?:.*\b(simreq_[A-Za-z0-9]+)\b)?"
)


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.casefold().strip()
    normalized = re.sub(r"[^\w\s?_-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip(" ?")


def _custody_summary(source_text: object, surface: str) -> dict[str, Any]:
    result = capture_input_event(
        source_text,
        source_id="forge.language.bridge.v1",
        channel_id=surface if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}", surface) else "forge_bridge",
        sequence_number=0,
    )
    status_value = getattr(result.status, "value", str(result.status))
    return {
        "result_id": result.result_id,
        "status": status_value,
        "reason_code": result.reason_code,
        "custody_created": result.custody_created,
        "structural_progression_allowed": result.structural_progression_allowed,
        "malformed_input": result.malformed_input,
        "unsupported_input": result.unsupported_input,
        "observed_utf8_byte_length": result.observed_utf8_byte_length,
        "observed_code_point_length": result.observed_code_point_length,
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


def _manifest_preview(
    *,
    source_sha256: str,
    intent: str,
    route: str,
    args: str,
    status: str,
    approval_gate: str,
) -> dict[str, Any]:
    body = {
        "manifest_kind": "bounded_recursive_manifest_preview",
        "manifest_status": "preview_only_not_compiled_mu_t",
        "source_sha256": source_sha256,
        "candidate_intent": intent,
        "candidate_route": route,
        "candidate_args": args,
        "decision_status": status,
        "approval_gate": approval_gate,
        "trace": (
            "input_event_custody",
            "deterministic_phrase_or_pattern_match",
            "fixed_route_allowlist_check",
            "route_preview_or_hold",
        ),
        "rmc_authority": False,
        "selected_meaning_authority": False,
        "output_rendering_authority": False,
        "permission_authority": False,
        "execution_authority": False,
        "memory_write_allowed": False,
        "canonical_reference_write_allowed": False,
    }
    stable = repr(sorted(body.items())).encode("utf-8")
    return {
        **body,
        "preview_id": "rmcpreview_" + hashlib.sha256(stable).hexdigest()[:18],
    }


def _decision(
    *,
    source_text: str,
    normalized: str,
    surface: str,
    custody: dict[str, Any],
    handled: bool,
    status: str,
    intent: str = "",
    route: str = "",
    args: str = "",
    response_text: str = "",
    action_class: str = "none",
    approval_required: bool = False,
    approval_gate: str = "",
    reasons: tuple[str, ...] = (),
) -> dict[str, Any]:
    source_sha256 = str(custody.get("observed_source_sha256") or "")
    request_id = "flb1_" + hashlib.sha256(
        (surface + "\0" + source_sha256 + "\0" + normalized).encode("utf-8")
    ).hexdigest()[:18]
    manifest = _manifest_preview(
        source_sha256=source_sha256,
        intent=intent,
        route=route,
        args=args,
        status=status,
        approval_gate=approval_gate,
    )
    record = BridgeDecision(
        schema_version=SCHEMA_VERSION,
        bridge_version=BRIDGE_VERSION,
        bridge_mode=BRIDGE_MODE,
        request_id=request_id,
        surface=surface,
        source_text_sha256=source_sha256,
        normalized_text=normalized,
        handled=handled,
        status=status,
        intent=intent,
        route=route,
        args=args,
        response_text=response_text,
        action_class=action_class,
        approval_required=approval_required,
        approval_gate=approval_gate,
        calls_llm=False,
        executes_command=False,
        executes_shell=False,
        executes_simulation=False,
        writes_files=False,
        writes_memory=False,
        grants_permission=False,
        input_custody=custody,
        recursive_manifest_preview=manifest,
        reasons=reasons,
    )
    return record.to_dict()


def interpret_request(request: object, *, surface: str = "forge_cli") -> dict[str, Any]:
    """Interpret one request against the bounded Bridge 1 route table."""

    custody = _custody_summary(request, surface)
    if type(request) is not str:
        return _decision(
            source_text="",
            normalized="",
            surface=surface,
            custody=custody,
            handled=True,
            status="INVALID_INPUT",
            response_text="Forge requires one text request. Nothing was executed.",
            reasons=("input_event_custody_rejected_non_text",),
        )

    normalized = _normalize(request)

    if (
        not custody.get("custody_created")
        or not custody.get("structural_progression_allowed")
        or not normalized
    ):
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="INVALID_INPUT",
            response_text=(
                "Forge preserved the exact input custody record but held "
                "interpretation because the input was empty, malformed, or unsupported. "
                "Nothing was executed."
            ),
            reasons=("input_custody_did_not_allow_structural_progression",),
        )

    if normalized in _CAPABILITY_PHRASES:
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="ROUTED",
            intent="inspect_forge_capabilities",
            route="forge-capabilities",
            response_text=(
                "Forge mapped this request to its installed capability report. "
                "The deterministic bridge did not call a model."
            ),
            action_class="read_only_existing_forge_command",
            reasons=("exact_capability_phrase",),
        )

    if normalized in _STATUS_PHRASES:
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="ROUTED",
            intent="inspect_forge_status",
            route="status",
            response_text=(
                "Forge mapped this request to its current status command. "
                "The deterministic bridge did not call a model."
            ),
            action_class="read_only_existing_forge_command",
            reasons=("exact_status_phrase",),
        )

    if normalized in _AUDIT_PHRASES:
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="ROUTED",
            intent="verify_audit_chain",
            route="audit",
            response_text=(
                "Forge mapped this request to audit-chain verification. "
                "The deterministic bridge did not call a model."
            ),
            action_class="read_only_existing_forge_command",
            reasons=("exact_audit_phrase",),
        )

    if normalized in _PROTOFORGE_STATUS_PHRASES:
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="ROUTED",
            intent="inspect_protoforge_status",
            route="forge-protoforge-status",
            response_text=(
                "Forge mapped this request to the existing read-only ProtoForge "
                "status route. No simulation was requested or executed."
            ),
            action_class="read_only_existing_forge_command",
            reasons=("exact_protoforge_status_phrase",),
        )

    if _RUN_SIMULATION_PATTERN.search(normalized):
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="APPROVAL_REQUIRED",
            intent="execute_protoforge_simulation",
            response_text=(
                "Forge understood this as a request to execute the latest "
                "ProtoForge plan. Execution was not performed. Use the existing "
                "`forge-protoforge-simulation-run-approved` route and provide "
                "the `RUN-PROTOFORGE` approval gate in the Operator Console."
            ),
            action_class="held_execution_request",
            approval_required=True,
            approval_gate="RUN-PROTOFORGE",
            reasons=("simulation_execution_requires_existing_gate",),
        )

    result_match = _RESULT_PATTERN.search(normalized)
    if result_match:
        run_id = result_match.group(1) or ""
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="ROUTED",
            intent="inspect_protoforge_result",
            route="forge-protoforge-result-show",
            args=run_id,
            response_text=(
                "Forge mapped this request to its existing read-only ProtoForge "
                "result display route. No simulation was executed."
            ),
            action_class="read_only_existing_forge_command",
            reasons=("protoforge_result_pattern",),
        )

    if _SYMBOLIC_SIMULATION_PATTERN.search(normalized):
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="ROUTED",
            intent="plan_symbolic_frequency_simulation",
            route="forge-protoforge-simulation-plan",
            args="symbolic_frequency_probe",
            response_text=(
                "Forge mapped this request to creation of the existing "
                "symbolic-frequency ProtoForge plan. Planning does not run the "
                "simulation."
            ),
            action_class="bounded_runtime_plan_write",
            reasons=("symbolic_frequency_simulation_pattern",),
        )

    if _CUBE_SIMULATION_PATTERN.search(normalized):
        return _decision(
            source_text=request,
            normalized=normalized,
            surface=surface,
            custody=custody,
            handled=True,
            status="ROUTED",
            intent="plan_falling_cube_simulation",
            route="forge-protoforge-simulation-plan",
            args="pybullet_fixed_falling_cube",
            response_text=(
                "Forge mapped this request to creation of the existing falling-"
                "cube ProtoForge plan. Planning does not run the simulation."
            ),
            action_class="bounded_runtime_plan_write",
            reasons=("falling_cube_simulation_pattern",),
        )

    return _decision(
        source_text=request,
        normalized=normalized,
        surface=surface,
        custody=custody,
        handled=False,
        status="UNSUPPORTED",
        response_text=(
            "Bridge 1 has no deterministic route for this request. The historical "
            "Qwen/Ollama fallback remains available until later replacement "
            "bridges are accepted."
        ),
        reasons=("no_fixed_deterministic_route",),
    )


def decision_to_plan(decision: dict[str, Any]) -> dict[str, Any]:
    """Convert one handled decision to the existing Patch-199 plan shape."""

    if not decision.get("handled"):
        raise ValueError("unsupported decisions cannot become deterministic plans")

    status = str(decision.get("status") or "")
    route = str(decision.get("route") or "")
    args = str(decision.get("args") or "")
    intent = str(decision.get("intent") or "deterministic Forge request")
    response_text = str(decision.get("response_text") or "")

    metadata = {
        "handled": True,
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "request_id": decision.get("request_id"),
        "status": status,
        "intent": intent,
        "route": route,
        "args": args,
        "response_text": response_text,
        "calls_llm": False,
        "executes_command": False,
        "executes_simulation": False,
        "writes_files": False,
        "writes_memory": False,
        "approval_required": bool(decision.get("approval_required")),
        "approval_gate": str(decision.get("approval_gate") or ""),
        "recursive_manifest_preview": decision.get("recursive_manifest_preview"),
    }

    if status == "ROUTED":
        gate = None
        return {
            "goal": intent.replace("_", " "),
            "impossible": False,
            "reason": "",
            "steps": [{
                "cmd": route,
                "args": args,
                "description": response_text,
                "gate": gate,
            }],
            "_language_bridge": metadata,
        }

    return {
        "goal": intent.replace("_", " "),
        "impossible": True,
        "reason": response_text,
        "steps": [],
        "_language_bridge": metadata,
    }


def bridge_status() -> dict[str, Any]:
    """Return a read-only status record for the installed first bridge."""

    return {
        "schema_version": SCHEMA_VERSION,
        "bridge_version": BRIDGE_VERSION,
        "bridge_mode": BRIDGE_MODE,
        "installed": True,
        "deterministic_routes_active": True,
        "covered_route_count": len(_ALLOWED_ROUTES),
        "covered_routes": list(_ALLOWED_ROUTES),
        "input_event_custody_connected": True,
        "selected_meaning_runtime_connected": False,
        "recursive_manifest_state": "preview_only_not_compiled_mu_t",
        "rmc_memory_write_allowed": False,
        "tool_authority_added": False,
        "action_authority_added": False,
        "simulation_authority_added": False,
        "model_called_for_covered_requests": False,
        "unsupported_request_fallback": UNSUPPORTED_FALLBACK,
        "unsupported_request_fallback_enabled": True,
        "full_qwen_ollama_replacement_complete": False,
        "forge_replaced": False,
    }
