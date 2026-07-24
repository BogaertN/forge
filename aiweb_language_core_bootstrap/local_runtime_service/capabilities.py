"""Deterministic capability-state reporting for Slice 48."""
from __future__ import annotations

from .authority import NEXT_LAWFUL_SLICE, PROHIBITED_AUTHORITIES
from .schema import CapabilityState
from .validation import validate_capability_state


def _state(capability_id: str, state: str, authority: bool, detail: str) -> CapabilityState:
    value = CapabilityState(capability_id, state, authority, detail)
    issues = validate_capability_state(value)
    if issues:
        raise ValueError("invalid_capability_state:" + ",".join(issues))
    return value


def capability_states() -> tuple[CapabilityState, ...]:
    values = (
        _state(
            "local_runtime_service.lifecycle",
            "ENABLED",
            True,
            "Explicit local start, stop, status, and process-identity custody are enabled.",
        ),
        _state(
            "local_runtime_service.health",
            "ENABLED",
            True,
            "Local health reporting is available through the owner-only Unix socket.",
        ),
        _state(
            "local_runtime_service.version",
            "ENABLED",
            True,
            "Static build, schema, protocol, and service-version reporting is enabled.",
        ),
        _state(
            "local_runtime_service.capability_state",
            "ENABLED",
            True,
            "Capability-state reporting describes accepted boundaries and grants no new capability.",
        ),
        _state(
            "local_runtime_service.transport",
            "ENABLED",
            True,
            "AF_UNIX owner-only transport is enabled; TCP, UDP, HTTP, and remote access are absent.",
        ),
        _state(
            "language.inspection_api",
            "DEFERRED",
            False,
            f"Read-only language inspection is deferred to Slice {NEXT_LAWFUL_SLICE}.",
        ),
        _state(
            "general_language.interpretation",
            "NOT_AUTHORIZED",
            False,
            "Slice 48 does not interpret natural language or select meaning.",
        ),
        _state(
            "memory.write",
            "NOT_AUTHORIZED",
            False,
            "No memory write, evidence mutation, or trace mutation is authorized.",
        ),
        _state(
            "external_resource.ingestion",
            "NOT_AUTHORIZED",
            False,
            "No external resource retrieval, admission, or transformation is authorized.",
        ),
        _state(
            "tool_action_delivery.execution",
            "NOT_AUTHORIZED",
            False,
            "No tool invocation, action execution, or message delivery is authorized.",
        ),
        _state(
            "gp014.bounded_lane",
            "PRESERVED",
            False,
            "GP-014 remains an unchanged protected bounded lane and is not superseded.",
        ),
        _state(
            "operator_console.connection",
            "DEFERRED",
            False,
            "The Slice 22 display-only operator-console connection remains deferred to Slice 52.",
        ),
        _state(
            "production.release",
            "NOT_AUTHORIZED",
            False,
            "A local service boundary is not production packaging, release, or Forge 1.0 acceptance.",
        ),
    )
    if tuple(sorted(item.capability_id for item in values)) != tuple(item.capability_id for item in sorted(values, key=lambda item: item.capability_id)):
        raise AssertionError("capability_ordering_failure")
    return tuple(sorted(values, key=lambda item: item.capability_id))


def build_capability_report(service_running: bool) -> dict[str, object]:
    states = capability_states()
    return {
        "service_running": bool(service_running),
        "capabilities": [item.to_dict() for item in states],
        "prohibited_authorities": {name: False for name in PROHIBITED_AUTHORITIES},
        "next_lawful_slice": NEXT_LAWFUL_SLICE,
    }
