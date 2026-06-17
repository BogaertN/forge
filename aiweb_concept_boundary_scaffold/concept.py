"""Deterministic concept and sense boundary records for Slice 8.

The records here are deliberately inert. They describe identity, scope,
provenance, version tags, and unknown-state boundaries. They do not look up,
resolve, infer, traverse, admit resources, assign roles, select gates, render,
or write stored material.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

SCHEMA_VERSION = "aiweb-concept-boundary-scaffold-v1"
SCOPE_STATUS = "concept_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"

ALLOWED_UNKNOWN_STATES = frozenset({"known_boundary", "unknown_boundary", "quarantined_boundary"})
ALLOWED_SEMANTIC_CLASSES = frozenset({
    "entity",
    "process",
    "quality",
    "relation_marker",
    "domain_marker",
    "unknown_marker",
})


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
class SenseBoundaryRecord:
    sense_key: str
    concept_key: str
    label: str
    namespace: str
    provenance_tag: str
    version_tag: str
    unknown_state: str = "known_boundary"
    examples: Tuple[str, ...] = field(default_factory=tuple)
    lexical_dataset_source: str = "none"
    live_sense_resolution: bool = False
    external_resource_admission: bool = False
    corpus_material: bool = False
    evidence_material: bool = False
    memory_material: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "sense",
            self.namespace,
            self.concept_key,
            self.sense_key,
            self.version_tag,
            self.unknown_state,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ConceptBoundaryRecord:
    concept_key: str
    namespace: str
    label: str
    semantic_class: str
    sense_keys: Tuple[str, ...]
    relation_keys: Tuple[str, ...]
    provenance_tag: str
    version_tag: str
    unknown_state: str = "known_boundary"
    notes: Tuple[str, ...] = field(default_factory=tuple)
    live_concept_resolution: bool = False
    live_graph_traversal: bool = False
    external_resource_admission: bool = False
    predicate_role_assignment: bool = False
    gate_selection: bool = False
    rendering: bool = False
    memory_write: bool = False
    evidence_write: bool = False
    corpus_write: bool = False
    delivery_action: bool = False

    def boundary_id(self) -> str:
        return stable_boundary_id(
            "concept",
            self.namespace,
            self.concept_key,
            self.semantic_class,
            self.version_tag,
            self.unknown_state,
        )

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def concept_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "live_concept_resolution": False,
        "live_sense_resolution": False,
        "live_graph_traversal": False,
        "external_resource_admission": False,
        "lexical_dataset_import": False,
        "predicate_role_assignment": False,
        "gate_selection": False,
        "rendering": False,
        "ui_power": False,
        "memory_write": False,
        "evidence_write": False,
        "corpus_write": False,
        "delivery_action": False,
        "baseline_change": False,
    }


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _namespace_ok(namespace: str) -> bool:
    return namespace.startswith("aiweb:") and len(namespace.split(":")) >= 2


def _issue(field: str, message: str) -> ValidationIssue:
    return ValidationIssue(field=field, message=message)


def validate_sense_record(record: SenseBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in ("sense_key", "concept_key", "label", "namespace", "provenance_tag", "version_tag"):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.unknown_state not in ALLOWED_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    if record.lexical_dataset_source != "none":
        issues.append(_issue("lexical_dataset_source", "dataset_import_not_allowed_in_slice8"))
    for field_name in (
        "live_sense_resolution",
        "external_resource_admission",
        "corpus_material",
        "evidence_material",
        "memory_material",
    ):
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_remain_false_in_slice8"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def validate_concept_record(record: ConceptBoundaryRecord) -> ValidationReport:
    issues: List[ValidationIssue] = []
    for field_name in ("concept_key", "namespace", "label", "semantic_class", "provenance_tag", "version_tag"):
        if not _nonempty(str(getattr(record, field_name))):
            issues.append(_issue(field_name, "required_nonempty"))
    if not _namespace_ok(record.namespace):
        issues.append(_issue("namespace", "must_start_with_aiweb_namespace"))
    if record.semantic_class not in ALLOWED_SEMANTIC_CLASSES:
        issues.append(_issue("semantic_class", "unsupported_semantic_class"))
    if record.unknown_state not in ALLOWED_UNKNOWN_STATES:
        issues.append(_issue("unknown_state", "unsupported_unknown_state"))
    for field_name in (
        "live_concept_resolution",
        "live_graph_traversal",
        "external_resource_admission",
        "predicate_role_assignment",
        "gate_selection",
        "rendering",
        "memory_write",
        "evidence_write",
        "corpus_write",
        "delivery_action",
    ):
        if bool(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_remain_false_in_slice8"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_sense_record() -> SenseBoundaryRecord:
    return SenseBoundaryRecord(
        sense_key="water_basic_boundary",
        concept_key="water",
        label="water",
        namespace="aiweb:core",
        provenance_tag="slice8_demo_boundary",
        version_tag="v1",
        examples=("boundary example only",),
    )


def demo_concept_record() -> ConceptBoundaryRecord:
    return ConceptBoundaryRecord(
        concept_key="water",
        namespace="aiweb:core",
        label="water",
        semantic_class="entity",
        sense_keys=("water_basic_boundary",),
        relation_keys=("water_related_to_liquid_boundary",),
        provenance_tag="slice8_demo_boundary",
        version_tag="v1",
        notes=("neutral scaffold example",),
    )
