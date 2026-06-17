"""Speech-act boundary records for Slice 9."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Tuple

from .predicate_frame import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    _issue,
    _namespace_ok,
    _nonempty,
    stable_boundary_id,
)

ALLOWED_ACT_TYPES = frozenset({
    "claim_boundary",
    "question_boundary",
    "request_boundary",
    "command_boundary",
    "draft_request_boundary",
    "comparison_boundary",
    "evidence_review_boundary",
    "memory_request_boundary",
    "implementation_request_boundary",
    "refusal_boundary",
    "clarification_boundary",
    "unknown_speech_act_boundary",
})

ALLOWED_SPEECH_UNKNOWN_STATES = frozenset({
    "known_boundary",
    "unknown_boundary",
    "ambiguous_boundary",
    "quarantined_boundary",
})

SPEECH_FALSE_ONLY_FIELDS = (
    "request_permission",
    "command_permission",
    "send_permission",
    "memory_write_permission",
    "tool_invocation_permission",
    "delivery_permission",
    "official_record_permission",
    "economic_action_permission",
    "identity_action_permission",
    "execution_authority",
)


@dataclass(frozen=True)
class SpeechActBoundaryRecord:
    speech_act_key: str
    act_type: str
    namespace: str
    source_ref: str
    provenance_tag: str
    version_tag: str
    unknown_state: str = "known_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    request_permission: bool = False
    command_permission: bool = False
    send_permission: bool = False
    memory_write_permission: bool = False
    tool_invocation_permission: bool = False
    delivery_permission: bool = False
    official_record_permission: bool = False
    economic_action_permission: bool = False
    identity_action_permission: bool = False
    execution_authority: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "speech_act",
            self.namespace,
            self.speech_act_key,
            self.act_type,
            self.source_ref,
            self.unknown_state,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def validate_speech_act_record(record: SpeechActBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in ("speech_act_key", "act_type", "namespace", "source_ref", "provenance_tag", "version_tag"):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.act_type not in ALLOWED_ACT_TYPES:
        issues.append(_issue("act_type", "unsupported_act_type"))
    if record.unknown_state not in ALLOWED_SPEECH_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    for field_name in SPEECH_FALSE_ONLY_FIELDS:
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_remain_false_in_slice9"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_speech_act_record() -> SpeechActBoundaryRecord:
    return SpeechActBoundaryRecord(
        speech_act_key="draft_request_boundary",
        act_type="draft_request_boundary",
        namespace="aiweb:core",
        source_ref="slice9_demo_input_boundary",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        notes=("recognized draft shape only",),
    )


def demo_memory_request_speech_act_record() -> SpeechActBoundaryRecord:
    return SpeechActBoundaryRecord(
        speech_act_key="memory_request_boundary",
        act_type="memory_request_boundary",
        namespace="aiweb:core",
        source_ref="slice9_demo_input_boundary",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
    )


def demo_implementation_request_speech_act_record() -> SpeechActBoundaryRecord:
    return SpeechActBoundaryRecord(
        speech_act_key="implementation_request_boundary",
        act_type="implementation_request_boundary",
        namespace="aiweb:core",
        source_ref="slice9_demo_input_boundary",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
    )


def demo_command_speech_act_record() -> SpeechActBoundaryRecord:
    return SpeechActBoundaryRecord(
        speech_act_key="command_boundary",
        act_type="command_boundary",
        namespace="aiweb:core",
        source_ref="slice9_demo_input_boundary",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
    )
