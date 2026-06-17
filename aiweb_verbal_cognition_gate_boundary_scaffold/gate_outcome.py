"""Gate outcome boundary records for Slice 10."""

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

ALLOWED_OUTCOME_TYPES = frozenset({
    "recognized_boundary",
    "held_boundary",
    "clarification_required_boundary",
    "unsupported_language_boundary",
    "unsupported_capability_boundary",
    "ambiguous_boundary",
    "blocked_action_boundary",
    "deferred_boundary",
    "no_action_boundary",
    "unknown_outcome_boundary",
})

ALLOWED_OUTCOME_UNKNOWN_STATES = frozenset({
    "known_boundary",
    "unknown_boundary",
    "ambiguous_boundary",
    "unsupported_boundary",
    "quarantined_boundary",
})

OUTCOME_FALSE_ONLY_FIELDS = (
    "selected_meaning",
    "final_meaning_selection",
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
    "production_readiness",
    "release_authority",
)


@dataclass(frozen=True)
class GateOutcomeBoundaryRecord:
    outcome_key: str
    gate_key: str
    outcome_type: str
    namespace: str
    reason_boundary_refs: Tuple[str, ...]
    required_next_boundary: str
    provenance_tag: str
    version_tag: str
    unknown_state: str = "known_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    selected_meaning: bool = False
    final_meaning_selection: bool = False
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
    production_readiness: bool = False
    release_authority: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "gate_outcome",
            self.namespace,
            self.gate_key,
            self.outcome_key,
            self.outcome_type,
            self.reason_boundary_refs,
            self.required_next_boundary,
            self.unknown_state,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def validate_gate_outcome_record(record: GateOutcomeBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in (
        "outcome_key",
        "gate_key",
        "outcome_type",
        "namespace",
        "required_next_boundary",
        "provenance_tag",
        "version_tag",
    ):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.outcome_type not in ALLOWED_OUTCOME_TYPES:
        issues.append(_issue("outcome_type", "unsupported_outcome_type"))
    if record.unknown_state not in ALLOWED_OUTCOME_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    if not isinstance(record.reason_boundary_refs, tuple):
        issues.append(_issue("reason_boundary_refs", "must_be_tuple_boundary_refs"))
    _check_false_only(record, OUTCOME_FALSE_ONLY_FIELDS, issues, "slice10")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_gate_outcome_record() -> GateOutcomeBoundaryRecord:
    return GateOutcomeBoundaryRecord(
        outcome_key="draft_request_held_boundary",
        gate_key="draft_request_gate_boundary",
        outcome_type="held_boundary",
        namespace="aiweb:core",
        reason_boundary_refs=("expectancy_present_boundary", "connectedness_present_boundary"),
        required_next_boundary="candidate_meaning_boundary_if_later_supported",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
        notes=("held outcome shape only",),
    )


def demo_clarification_required_outcome_record() -> GateOutcomeBoundaryRecord:
    return GateOutcomeBoundaryRecord(
        outcome_key="recipient_clarification_required_boundary",
        gate_key="draft_request_gate_boundary",
        outcome_type="clarification_required_boundary",
        namespace="aiweb:core",
        reason_boundary_refs=("missing_recipient_boundary",),
        required_next_boundary="clarification_state_boundary",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_blocked_action_outcome_record() -> GateOutcomeBoundaryRecord:
    return GateOutcomeBoundaryRecord(
        outcome_key="unsafe_command_blocked_boundary",
        gate_key="command_gate_boundary",
        outcome_type="blocked_action_boundary",
        namespace="aiweb:core",
        reason_boundary_refs=("action_boundary_without_authority",),
        required_next_boundary="no_action_boundary",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_unknown_gate_outcome_record() -> GateOutcomeBoundaryRecord:
    return GateOutcomeBoundaryRecord(
        outcome_key="unknown_outcome_boundary",
        gate_key="unknown_gate_boundary",
        outcome_type="unknown_outcome_boundary",
        namespace="aiweb:core",
        reason_boundary_refs=("unknown_reason_boundary",),
        required_next_boundary="hold_boundary",
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
        unknown_state="unknown_boundary",
    )
