"""Deterministic verbal-cognition gate boundary records for Slice 10.

This package is inert. It represents gate-shaped language states without
granting downstream power. It performs no live gate evaluation, no final
meaning choice, no truth decision, no permission grant, no tool call, no
delivery step, no expression rendering, no stored-material mutation, and no
external lookup.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Dict, List, Tuple

SCHEMA_VERSION = "aiweb-verbal-cognition-gate-boundary-scaffold-v1"
SCOPE_STATUS = "verbal_cognition_gate_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"

ALLOWED_GATE_TYPES = frozenset({
    "verbal_cognition_gate_boundary",
    "expectancy_gate_boundary",
    "congruity_gate_boundary",
    "connectedness_gate_boundary",
    "recoverable_purpose_gate_boundary",
    "ambiguity_gate_boundary",
    "unsupported_state_gate_boundary",
    "clarification_required_gate_boundary",
    "blocked_action_gate_boundary",
    "deferred_gate_boundary",
    "unknown_gate_boundary",
})

ALLOWED_GATE_STAGES = frozenset({
    "pre_selection_boundary",
    "input_boundary",
    "candidate_boundary",
    "review_boundary",
    "hold_boundary",
    "defer_boundary",
    "unknown_stage_boundary",
})

ALLOWED_UNKNOWN_STATES = frozenset({
    "known_boundary",
    "unknown_boundary",
    "ambiguous_boundary",
    "unsupported_boundary",
    "quarantined_boundary",
})

GATE_FALSE_ONLY_FIELDS = (
    "live_gate_evaluation",
    "gate_resolution",
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


def _canonical_payload(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_boundary_id(prefix: str, *parts: object) -> str:
    """Create a deterministic local boundary identifier."""
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
class GateBoundaryRecord:
    gate_key: str
    gate_type: str
    gate_stage: str
    namespace: str
    gate_input_refs: Tuple[str, ...]
    predicate_frame_refs: Tuple[str, ...]
    concept_boundary_refs: Tuple[str, ...]
    provenance_tag: str
    version_tag: str
    unknown_state: str = "known_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    live_gate_evaluation: bool = False
    gate_resolution: bool = False
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
            "gate",
            self.namespace,
            self.gate_key,
            self.gate_type,
            self.gate_stage,
            self.gate_input_refs,
            self.predicate_frame_refs,
            self.concept_boundary_refs,
            self.unknown_state,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def verbal_cognition_gate_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "gate_identity_representation": True,
        "gate_input_representation": True,
        "gate_outcome_representation": True,
        "expectancy_boundary_representation": True,
        "state_boundary_representation": True,
        "live_gate_evaluation": False,
        "gate_resolution": False,
        "selected_meaning": False,
        "final_meaning_selection": False,
        "truth_decision": False,
        "permission_grant": False,
        "action_authorization": False,
        "tool_invocation": False,
        "capability_route": False,
        "delivery_action": False,
        "memory_write": False,
        "evidence_validation": False,
        "external_resource_admission": False,
        "expression_rendering": False,
        "production_readiness": False,
        "release_authority": False,
        "sanskrit_wordnet_status": "hold_unadmitted",
        "gp014_status": "protected_prior_scope",
        "gp015_status": "failed_not_repaired",
        "gp015r1_status": "not_installed",
    }


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _namespace_ok(namespace: str) -> bool:
    return namespace.startswith("aiweb:") and len(namespace.split(":")) >= 2


def _issue(field: str, message: str) -> ValidationIssue:
    return ValidationIssue(field=field, message=message)


def _check_false_only(record: object, field_names: Tuple[str, ...], issues: List[ValidationIssue], slice_label: str) -> None:
    for field_name in field_names:
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, f"must_remain_false_in_{slice_label}"))


def validate_gate_boundary_record(record: GateBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in (
        "gate_key",
        "gate_type",
        "gate_stage",
        "namespace",
        "provenance_tag",
        "version_tag",
    ):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.gate_type not in ALLOWED_GATE_TYPES:
        issues.append(_issue("gate_type", "unsupported_gate_type"))
    if record.gate_stage not in ALLOWED_GATE_STAGES:
        issues.append(_issue("gate_stage", "unsupported_gate_stage"))
    if record.unknown_state not in ALLOWED_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    for tuple_field in ("gate_input_refs", "predicate_frame_refs", "concept_boundary_refs"):
        if not isinstance(getattr(record, tuple_field), tuple):
            issues.append(_issue(tuple_field, "must_be_tuple_boundary_refs"))
    _check_false_only(record, GATE_FALSE_ONLY_FIELDS, issues, "slice10")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_gate_boundary_record() -> GateBoundaryRecord:
    return GateBoundaryRecord(
        gate_key="draft_request_gate_boundary",
        gate_type="verbal_cognition_gate_boundary",
        gate_stage="pre_selection_boundary",
        namespace="aiweb:core",
        gate_input_refs=("neutral_input_boundary",),
        predicate_frame_refs=("draft_boundary",),
        concept_boundary_refs=("concept_written_content_boundary",),
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
        notes=("boundary example only",),
    )


def demo_unknown_gate_boundary_record() -> GateBoundaryRecord:
    return GateBoundaryRecord(
        gate_key="unknown_gate_boundary",
        gate_type="unknown_gate_boundary",
        gate_stage="unknown_stage_boundary",
        namespace="aiweb:core",
        gate_input_refs=("unknown_input_boundary",),
        predicate_frame_refs=("unknown_predicate_boundary",),
        concept_boundary_refs=("unknown_concept_boundary",),
        provenance_tag="slice10_demo_boundary",
        version_tag="v1",
        unknown_state="unknown_boundary",
    )
