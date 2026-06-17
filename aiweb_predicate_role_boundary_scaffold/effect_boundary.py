"""Effect-category boundary records for Slice 9."""

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

ALLOWED_EFFECT_TYPES = frozenset({
    "no_effect_boundary",
    "informational_effect_boundary",
    "draft_effect_boundary",
    "memory_related_effect_boundary",
    "tool_related_effect_boundary",
    "delivery_related_effect_boundary",
    "file_write_related_effect_boundary",
    "economic_related_effect_boundary",
    "identity_related_effect_boundary",
    "official_record_related_effect_boundary",
    "medical_sensitive_effect_boundary",
    "legal_sensitive_effect_boundary",
    "unknown_effect_boundary",
})

ALLOWED_EFFECT_UNKNOWN_STATES = frozenset({
    "known_boundary",
    "unknown_boundary",
    "ambiguous_boundary",
    "quarantined_boundary",
})

EFFECT_FALSE_ONLY_FIELDS = (
    "effect_authorized",
    "side_effect_allowed",
    "file_write_allowed",
    "memory_write_allowed",
    "evidence_validation_allowed",
    "delivery_allowed",
    "action_route_allowed",
    "tool_invocation_allowed",
    "external_resource_allowed",
)


@dataclass(frozen=True)
class EffectBoundaryRecord:
    effect_key: str
    effect_type: str
    namespace: str
    provenance_tag: str
    version_tag: str
    required_future_authority: str = "none"
    unknown_state: str = "known_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    effect_authorized: bool = False
    side_effect_allowed: bool = False
    file_write_allowed: bool = False
    memory_write_allowed: bool = False
    evidence_validation_allowed: bool = False
    delivery_allowed: bool = False
    action_route_allowed: bool = False
    tool_invocation_allowed: bool = False
    external_resource_allowed: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "effect",
            self.namespace,
            self.effect_key,
            self.effect_type,
            self.required_future_authority,
            self.unknown_state,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def validate_effect_boundary_record(record: EffectBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in ("effect_key", "effect_type", "namespace", "provenance_tag", "version_tag", "required_future_authority"):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.effect_type not in ALLOWED_EFFECT_TYPES:
        issues.append(_issue("effect_type", "unsupported_effect_type"))
    if record.unknown_state not in ALLOWED_EFFECT_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    for field_name in EFFECT_FALSE_ONLY_FIELDS:
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_remain_false_in_slice9"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_effect_boundary_record() -> EffectBoundaryRecord:
    return EffectBoundaryRecord(
        effect_key="draft_effect_boundary",
        effect_type="draft_effect_boundary",
        namespace="aiweb:core",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        required_future_authority="send_or_delivery_authority_if_later_needed",
        notes=("effect category only",),
    )


def demo_unknown_effect_boundary_record() -> EffectBoundaryRecord:
    return EffectBoundaryRecord(
        effect_key="unknown_effect_boundary",
        effect_type="unknown_effect_boundary",
        namespace="aiweb:core",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        unknown_state="unknown_boundary",
    )
