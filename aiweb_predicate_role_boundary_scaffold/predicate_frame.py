"""Deterministic predicate-frame boundary records for Slice 9.

This package is deliberately inert. It represents action-shaped meaning,
participant slots, speech-act shape, and effect categories without granting
downstream power. It performs no file writes, no stored-material mutation,
no external lookup, no tool call, no delivery, no expression rendering, and
no selected-meaning or gate-selection decision.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Dict, List, Tuple

SCHEMA_VERSION = "aiweb-predicate-role-boundary-scaffold-v1"
SCOPE_STATUS = "predicate_role_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"

ALLOWED_FRAME_KINDS = frozenset({
    "action_boundary",
    "event_boundary",
    "process_boundary",
    "state_change_boundary",
    "communicative_act_boundary",
    "comparison_boundary",
    "evidence_review_boundary",
    "memory_request_boundary",
    "implementation_request_boundary",
    "unknown_frame_boundary",
})

ALLOWED_UNKNOWN_STATES = frozenset({
    "known_boundary",
    "unknown_boundary",
    "missing_required_role_boundary",
    "ambiguous_boundary",
    "quarantined_boundary",
})

PREDICATE_FALSE_ONLY_FIELDS = (
    "execution_authority",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "memory_write",
    "evidence_validation",
    "gate_selection",
    "selected_meaning",
    "expression_rendering",
    "external_resource_admission",
    "corpus_material",
)


def _canonical_payload(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_boundary_id(prefix: str, *parts: object) -> str:
    """Create a deterministic local boundary identifier.

    The identifier uses canonical JSON plus SHA256. It does not use random
    values or timestamps.
    """
    digest = hashlib.sha256(_canonical_payload(parts).encode("utf-8")).hexdigest()[:16]
    clean = prefix.strip().lower().replace(" ", "_")
    return f"{clean}_{digest}"


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    passed: bool
    issues: Tuple[ValidationIssue, ...]

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "passed": self.passed,
            "issues": [asdict(item) for item in self.issues],
        }


@dataclass(frozen=True)
class PredicateFrameBoundaryRecord:
    predicate_key: str
    action_root: str
    frame_kind: str
    namespace: str
    role_keys: Tuple[str, ...]
    speech_act_key: str
    effect_boundary_key: str
    provenance_tag: str
    version_tag: str
    unknown_state: str = "known_boundary"
    domain_markers: Tuple[str, ...] = field(default_factory=tuple)
    notes: Tuple[str, ...] = field(default_factory=tuple)
    execution_authority: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    gate_selection: bool = False
    selected_meaning: bool = False
    expression_rendering: bool = False
    external_resource_admission: bool = False
    corpus_material: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "predicate_frame",
            self.namespace,
            self.predicate_key,
            self.action_root,
            self.frame_kind,
            self.role_keys,
            self.speech_act_key,
            self.effect_boundary_key,
            self.version_tag,
            self.unknown_state,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def predicate_role_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "predicate_resolution": False,
        "role_resolution": False,
        "speech_act_permission": False,
        "effect_authorization": False,
        "selected_meaning": False,
        "gate_selection": False,
        "expression_rendering": False,
        "tool_invocation": False,
        "capability_route": False,
        "action_route": False,
        "memory_write": False,
        "evidence_validation": False,
        "external_resource_admission": False,
        "delivery_action": False,
        "production_readiness": False,
        "release_authority": False,
        "sanskrit_wordnet_status": "hold_unadmitted",
    }


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _namespace_ok(namespace: str) -> bool:
    return namespace.startswith("aiweb:") and len(namespace.split(":")) >= 2


def _issue(field: str, message: str) -> ValidationIssue:
    return ValidationIssue(field=field, message=message)


def _check_false_only(record: object, field_names: Tuple[str, ...], issues: List[ValidationIssue]) -> None:
    for field_name in field_names:
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_remain_false_in_slice9"))


def validate_predicate_frame_record(record: PredicateFrameBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in (
        "predicate_key",
        "action_root",
        "frame_kind",
        "namespace",
        "speech_act_key",
        "effect_boundary_key",
        "provenance_tag",
        "version_tag",
    ):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.frame_kind not in ALLOWED_FRAME_KINDS:
        issues.append(_issue("frame_kind", "unsupported_frame_kind"))
    if record.unknown_state not in ALLOWED_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    if not isinstance(record.role_keys, tuple):
        issues.append(_issue("role_keys", "must_be_tuple"))
    _check_false_only(record, PREDICATE_FALSE_ONLY_FIELDS, issues)
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_predicate_frame_record() -> PredicateFrameBoundaryRecord:
    return PredicateFrameBoundaryRecord(
        predicate_key="draft_boundary",
        action_root="draft",
        frame_kind="communicative_act_boundary",
        namespace="aiweb:core",
        role_keys=("agent_boundary", "content_boundary", "recipient_boundary_missing"),
        speech_act_key="draft_request_boundary",
        effect_boundary_key="draft_effect_boundary",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        notes=("boundary example only",),
    )


def demo_unknown_predicate_frame_record() -> PredicateFrameBoundaryRecord:
    return PredicateFrameBoundaryRecord(
        predicate_key="unknown_predicate_boundary",
        action_root="unknown",
        frame_kind="unknown_frame_boundary",
        namespace="aiweb:core",
        role_keys=("unknown_role_boundary",),
        speech_act_key="unknown_speech_act_boundary",
        effect_boundary_key="unknown_effect_boundary",
        provenance_tag="slice9_demo_boundary",
        version_tag="v1",
        unknown_state="unknown_boundary",
    )
