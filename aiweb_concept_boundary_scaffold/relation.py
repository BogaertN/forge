"""Semantic relation boundary records for Slice 8.

A relation record here is a named boundary edge, not a graph engine. It cannot
traverse, resolve, assign roles, select gates, validate evidence, write memory,
admit resources, or authorize action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Tuple

from .concept import SCHEMA_VERSION, ValidationIssue, ValidationReport, stable_boundary_id

ALLOWED_RELATION_TYPES = frozenset({
    "is_a_boundary",
    "part_of_boundary",
    "associated_with_boundary",
    "domain_marker_boundary",
    "unknown_relation_boundary",
})


@dataclass(frozen=True)
class SemanticRelationBoundaryRecord:
    relation_key: str
    relation_type: str
    source_concept_key: str
    target_concept_key: str
    namespace: str
    provenance_tag: str
    version_tag: str
    unknown_state: str = "known_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    live_graph_traversal: bool = False
    external_resource_admission: bool = False
    predicate_role_assignment: bool = False
    gate_selection: bool = False
    evidence_validation: bool = False
    memory_write: bool = False
    delivery_action: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "relation",
            self.namespace,
            self.relation_key,
            self.relation_type,
            self.source_concept_key,
            self.target_concept_key,
            self.version_tag,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def relation_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "semantic_relation_boundary_scaffold_only",
        "runtime_effect": "none",
        "dependency_change": "none",
        "scaffold_only": True,
        "live_graph_traversal": False,
        "external_resource_admission": False,
        "predicate_role_assignment": False,
        "gate_selection": False,
        "evidence_validation": False,
        "memory_write": False,
        "delivery_action": False,
    }


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _namespace_ok(namespace: str) -> bool:
    return namespace.startswith("aiweb:") and len(namespace.split(":")) >= 2


def _issue(field: str, message: str) -> ValidationIssue:
    return ValidationIssue(field=field, message=message)


def validate_relation_record(record: SemanticRelationBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in (
        "relation_key",
        "relation_type",
        "source_concept_key",
        "target_concept_key",
        "namespace",
        "provenance_tag",
        "version_tag",
    ):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.relation_type not in ALLOWED_RELATION_TYPES:
        issues.append(_issue("relation_type", "unsupported_relation_type"))
    if record.unknown_state not in {"known_boundary", "unknown_boundary", "quarantined_boundary"}:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    for field_name in (
        "live_graph_traversal",
        "external_resource_admission",
        "predicate_role_assignment",
        "gate_selection",
        "evidence_validation",
        "memory_write",
        "delivery_action",
    ):
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_remain_false_in_slice8"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_relation_record() -> SemanticRelationBoundaryRecord:
    return SemanticRelationBoundaryRecord(
        relation_key="water_related_to_liquid_boundary",
        relation_type="associated_with_boundary",
        source_concept_key="water",
        target_concept_key="liquid",
        namespace="aiweb:core",
        provenance_tag="slice8_demo_boundary",
        version_tag="v1",
        notes=("boundary edge only",),
    )
