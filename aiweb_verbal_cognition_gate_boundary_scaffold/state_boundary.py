"""Gate state boundary records for ambiguity, unsupported, clarification, and deferral states."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Tuple

from .gate_boundary import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    _check_false_only,
    _issue,
    _namespace_ok,
    _nonempty,
    stable_boundary_id,
)

ALLOWED_STATE_TYPES = frozenset({
    "ambiguity_state_boundary",
    "clarification_required_state_boundary",
    "unsupported_state_boundary",
    "blocked_action_state_boundary",
    "deferred_state_boundary",
    "recoverable_state_boundary",
    "hold_state_boundary",
    "unknown_state_boundary",
})

ALLOWED_STATE_SEVERITY = frozenset({
    "informational_boundary",
    "requires_future_boundary",
    "blocked_boundary",
    "held_boundary",
    "unknown_boundary",
})

STATE_FALSE_ONLY_FIELDS = (
    "state_resolution",
    "selected_meaning",
    "truth_decision",
    "permission_grant",
    "action_authorization",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
    "expression_rendering",
)


@dataclass(frozen=True)
class GateStateBoundaryRecord:
    state_key: str
    gate_key: str
    state_type: str
    namespace: str
    severity_boundary: str
    reason_boundary_refs: Tuple[str, ...]
    required_future_boundary: str
    provenance_tag: str
    version_tag: str
    notes: Tuple[str, ...] = field(default_factory=tuple)
    state_resolution: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    permission_grant: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False
    expression_rendering: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "gate_state",
            self.namespace,
            self.gate_key,
            self.state_key,
            self.state_type,
            self.severity_boundary,
            self.reason_boundary_refs,
            self.required_future_boundary,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def validate_gate_state_record(record: GateStateBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in (
        "state_key",
        "gate_key",
        "state_type",
        "namespace",
        "severity_boundary",
        "required_future_boundary",
        "provenance_tag",
        "version_tag",
    ):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.state_type not in ALLOWED_STATE_TYPES:
        issues.append(_issue("state_type", "unsupported_state_type"))
    if record.severity_boundary not in ALLOWED_STATE_SEVERITY:
        issues.append(_issue("severity_boundary", "unsupported_state_severity"))
    if not isinstance(record.reason_boundary_refs, tuple):
        issues.append(_issue("reason_boundary_refs", "must_be_tuple_boundary_refs"))
    _check_false_only(record, STATE_FALSE_ONLY_FIELDS, issues, "slice10")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_ambiguity_state_record() -> GateStateBoundaryRecord:
    return GateStateBoundaryRecord(
        state_key="recipient_ambiguity_state_boundary",
        gate_key="draft_request_gate_boundary",
        state_type="ambiguity_state_boundary",
        namespace="aiweb:core",
        severity_boundary="requires_future_boundary",
        reason_boundary_refs=("recipient_boundary_missing", "multiple_possible_recipient_boundary"),
        required_future_boundary="clarification_required_state_boundary",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_clarification_required_state_record() -> GateStateBoundaryRecord:
    return GateStateBoundaryRecord(
        state_key="recipient_clarification_state_boundary",
        gate_key="draft_request_gate_boundary",
        state_type="clarification_required_state_boundary",
        namespace="aiweb:core",
        severity_boundary="requires_future_boundary",
        reason_boundary_refs=("recipient_boundary_missing",),
        required_future_boundary="clarification_prompt_boundary_if_later_supported",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_unsupported_state_record() -> GateStateBoundaryRecord:
    return GateStateBoundaryRecord(
        state_key="unsupported_language_state_boundary",
        gate_key="unknown_gate_boundary",
        state_type="unsupported_state_boundary",
        namespace="aiweb:core",
        severity_boundary="held_boundary",
        reason_boundary_refs=("unsupported_language_boundary",),
        required_future_boundary="hold_boundary",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_blocked_action_state_record() -> GateStateBoundaryRecord:
    return GateStateBoundaryRecord(
        state_key="blocked_action_state_boundary",
        gate_key="command_gate_boundary",
        state_type="blocked_action_state_boundary",
        namespace="aiweb:core",
        severity_boundary="blocked_boundary",
        reason_boundary_refs=("command_without_authority_boundary",),
        required_future_boundary="no_action_boundary",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_deferred_state_record() -> GateStateBoundaryRecord:
    return GateStateBoundaryRecord(
        state_key="deferred_state_boundary",
        gate_key="draft_request_gate_boundary",
        state_type="deferred_state_boundary",
        namespace="aiweb:core",
        severity_boundary="held_boundary",
        reason_boundary_refs=("future_authority_required_boundary",),
        required_future_boundary="future_slice_boundary",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )
