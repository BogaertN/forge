"""Expectancy, congruity, connectedness, and recoverable-purpose boundaries."""

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

ALLOWED_EXPECTANCY_TYPES = frozenset({
    "expectancy_present_boundary",
    "expectancy_missing_boundary",
    "expectancy_mismatch_boundary",
    "congruity_boundary",
    "incongruity_boundary",
    "connectedness_boundary",
    "disconnected_boundary",
    "recoverable_purpose_boundary",
    "unrecoverable_purpose_boundary",
    "unknown_expectancy_boundary",
})

ALLOWED_EXPECTANCY_STATES = frozenset({
    "represented_boundary",
    "missing_boundary",
    "ambiguous_boundary",
    "unsupported_boundary",
    "unknown_boundary",
    "quarantined_boundary",
})

EXPECTANCY_FALSE_ONLY_FIELDS = (
    "expectancy_decision",
    "congruity_decision",
    "connectedness_decision",
    "purpose_recovery_decision",
    "selected_meaning",
    "truth_decision",
    "permission_grant",
    "action_authorization",
    "tool_invocation",
    "delivery_action",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
)


@dataclass(frozen=True)
class ExpectancyBoundaryRecord:
    expectancy_key: str
    gate_key: str
    expectancy_type: str
    namespace: str
    input_boundary_refs: Tuple[str, ...]
    reason_boundary_refs: Tuple[str, ...]
    provenance_tag: str
    version_tag: str
    expectancy_state: str = "represented_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    expectancy_decision: bool = False
    congruity_decision: bool = False
    connectedness_decision: bool = False
    purpose_recovery_decision: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    permission_grant: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    delivery_action: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "expectancy",
            self.namespace,
            self.gate_key,
            self.expectancy_key,
            self.expectancy_type,
            self.input_boundary_refs,
            self.reason_boundary_refs,
            self.expectancy_state,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def validate_expectancy_record(record: ExpectancyBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in (
        "expectancy_key",
        "gate_key",
        "expectancy_type",
        "namespace",
        "provenance_tag",
        "version_tag",
    ):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.expectancy_type not in ALLOWED_EXPECTANCY_TYPES:
        issues.append(_issue("expectancy_type", "unsupported_expectancy_type"))
    if record.expectancy_state not in ALLOWED_EXPECTANCY_STATES:
        issues.append(_issue("expectancy_state", "unsupported_expectancy_state"))
    for tuple_field in ("input_boundary_refs", "reason_boundary_refs"):
        if not isinstance(getattr(record, tuple_field), tuple):
            issues.append(_issue(tuple_field, "must_be_tuple_boundary_refs"))
    _check_false_only(record, EXPECTANCY_FALSE_ONLY_FIELDS, issues, "slice10")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_expectancy_record() -> ExpectancyBoundaryRecord:
    return ExpectancyBoundaryRecord(
        expectancy_key="draft_request_expectancy_boundary",
        gate_key="draft_request_gate_boundary",
        expectancy_type="expectancy_present_boundary",
        namespace="aiweb:core",
        input_boundary_refs=("draft_request_boundary",),
        reason_boundary_refs=("communicative_act_shape_boundary",),
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
        notes=("expectancy represented only",),
    )


def demo_congruity_record() -> ExpectancyBoundaryRecord:
    return ExpectancyBoundaryRecord(
        expectancy_key="draft_request_congruity_boundary",
        gate_key="draft_request_gate_boundary",
        expectancy_type="congruity_boundary",
        namespace="aiweb:core",
        input_boundary_refs=("draft_request_boundary", "draft_effect_boundary"),
        reason_boundary_refs=("speech_act_effect_pair_boundary",),
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_connectedness_record() -> ExpectancyBoundaryRecord:
    return ExpectancyBoundaryRecord(
        expectancy_key="draft_request_connectedness_boundary",
        gate_key="draft_request_gate_boundary",
        expectancy_type="connectedness_boundary",
        namespace="aiweb:core",
        input_boundary_refs=("predicate_frame_boundary", "role_boundary"),
        reason_boundary_refs=("role_frame_reference_boundary",),
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_recoverable_purpose_record() -> ExpectancyBoundaryRecord:
    return ExpectancyBoundaryRecord(
        expectancy_key="draft_request_recoverable_purpose_boundary",
        gate_key="draft_request_gate_boundary",
        expectancy_type="recoverable_purpose_boundary",
        namespace="aiweb:core",
        input_boundary_refs=("draft_request_boundary",),
        reason_boundary_refs=("purpose_shape_present_boundary",),
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
    )


def demo_unknown_expectancy_record() -> ExpectancyBoundaryRecord:
    return ExpectancyBoundaryRecord(
        expectancy_key="unknown_expectancy_boundary",
        gate_key="unknown_gate_boundary",
        expectancy_type="unknown_expectancy_boundary",
        namespace="aiweb:core",
        input_boundary_refs=("unknown_input_boundary",),
        reason_boundary_refs=("unknown_reason_boundary",),
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
        expectancy_state="unknown_boundary",
    )
