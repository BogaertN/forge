"""Participant-role boundary records for Slice 9."""

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

ALLOWED_ROLE_TYPES = frozenset({
    "agent_boundary",
    "patient_boundary",
    "theme_boundary",
    "experiencer_boundary",
    "instrument_boundary",
    "recipient_boundary",
    "source_boundary",
    "target_boundary",
    "location_boundary",
    "time_boundary",
    "manner_boundary",
    "content_boundary",
    "authority_boundary",
    "condition_boundary",
    "unknown_role_boundary",
})

ALLOWED_PRESENCE_STATES = frozenset({
    "present_boundary",
    "missing_boundary",
    "optional_absent_boundary",
    "unknown_presence_boundary",
    "quarantined_boundary",
})

ALLOWED_ROLE_UNKNOWN_STATES = frozenset({
    "known_boundary",
    "unknown_boundary",
    "ambiguous_boundary",
    "quarantined_boundary",
})

ROLE_FALSE_ONLY_FIELDS = (
    "role_resolution",
    "concept_resolution",
    "live_binding",
    "memory_lookup",
    "evidence_lookup",
    "tool_invocation",
    "execution_authority",
    "delivery_action",
)


@dataclass(frozen=True)
class RoleBoundaryRecord:
    role_key: str
    frame_key: str
    role_type: str
    namespace: str
    concept_boundary_refs: Tuple[str, ...]
    provenance_tag: str
    version_tag: str
    presence_state: str = "present_boundary"
    unknown_state: str = "known_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    role_resolution: bool = False
    concept_resolution: bool = False
    live_binding: bool = False
    memory_lookup: bool = False
    evidence_lookup: bool = False
    tool_invocation: bool = False
    execution_authority: bool = False
    delivery_action: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "role",
            self.namespace,
            self.frame_key,
            self.role_key,
            self.role_type,
            self.concept_boundary_refs,
            self.presence_state,
            self.unknown_state,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def validate_role_record(record: RoleBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in ("role_key", "frame_key", "role_type", "namespace", "provenance_tag", "version_tag"):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.role_type not in ALLOWED_ROLE_TYPES:
        issues.append(_issue("role_type", "unsupported_role_type"))
    if record.presence_state not in ALLOWED_PRESENCE_STATES:
        issues.append(_issue("presence_state", "unsupported_presence_state"))
    if record.unknown_state not in ALLOWED_ROLE_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    if not isinstance(record.concept_boundary_refs, tuple):
        issues.append(_issue("concept_boundary_refs", "must_be_tuple_boundary_refs"))
    for field_name in ROLE_FALSE_ONLY_FIELDS:
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_remain_false_in_slice9"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_role_record() -> RoleBoundaryRecord:
    return RoleBoundaryRecord(
        role_key="content_boundary",
        frame_key="draft_boundary",
        role_type="content_boundary",
        namespace="aiweb:core",
        concept_boundary_refs=("concept_written_content_boundary",),
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        notes=("boundary reference only",),
    )


def demo_missing_role_record() -> RoleBoundaryRecord:
    return RoleBoundaryRecord(
        role_key="recipient_boundary_missing",
        frame_key="draft_boundary",
        role_type="recipient_boundary",
        namespace="aiweb:core",
        concept_boundary_refs=(),
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        presence_state="missing_boundary",
        notes=("missing role remains explicit",),
    )


def demo_unknown_role_record() -> RoleBoundaryRecord:
    return RoleBoundaryRecord(
        role_key="unknown_role_boundary",
        frame_key="unknown_predicate_boundary",
        role_type="unknown_role_boundary",
        namespace="aiweb:core",
        concept_boundary_refs=(),
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        presence_state="unknown_presence_boundary",
        unknown_state="unknown_boundary",
    )
