from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-ambiguity-clarification-boundary-scaffold-v1"
SCOPE_STATUS = "ambiguity_clarification_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonicalize(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_boundary_id(prefix: str, *parts: Any) -> str:
    body = {"prefix": prefix, "parts": [_canonicalize(part) for part in parts]}
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    reason: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    ok: bool
    issues: Tuple[ValidationIssue, ...] = ()

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def _issue(field: str, reason: str) -> ValidationIssue:
    return ValidationIssue(field=field, reason=reason)


def _check_false_only(record: Any, fields: Tuple[str, ...], issues: list[ValidationIssue], namespace: str) -> None:
    for field_name in fields:
        if bool(getattr(record, field_name, False)):
            issues.append(_issue(field_name, f"{namespace}:{field_name}_must_remain_false"))


def _tuple_of_text(value: Tuple[str, ...], *, allow_empty: bool = True) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    return all(isinstance(item, str) and bool(item.strip()) for item in value)

ALLOWED_UNKNOWN_KINDS = (
    "unknown_concept_boundary",
    "unknown_language_boundary",
    "unknown_role_boundary",
    "unknown_gate_boundary",
    "unsupported_resource_boundary",
    "missing_support_boundary",
)

ALLOWED_UNKNOWN_STATUS = (
    "unknown_preserved_boundary",
    "unsupported_preserved_boundary",
    "missing_support_preserved_boundary",
    "held_for_authority_boundary",
    "deferred_until_authority_boundary",
)

UNKNOWN_FALSE_ONLY_FIELDS = (
    "guess_substitution",
    "silent_repair",
    "external_resource_admission",
    "concept_resolution",
    "role_resolution",
    "gate_resolution",
    "selected_meaning",
    "truth_decision",
    "tool_invocation",
    "action_authorization",
    "memory_write",
    "evidence_validation",
)


@dataclass(frozen=True)
class UnknownSupportBoundaryRecord:
    unknown_boundary_id: str
    unknown_key: str
    unknown_kind: str
    unknown_status: str
    source_ref: str
    candidate_ref: str
    authority_needed_refs: Tuple[str, ...]
    no_guess: bool = True
    uncertainty_preserved: bool = True
    provenance_tag: str = "slice12_boundary"
    version_tag: str = "v1"
    guess_substitution: bool = False
    silent_repair: bool = False
    external_resource_admission: bool = False
    concept_resolution: bool = False
    role_resolution: bool = False
    gate_resolution: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    tool_invocation: bool = False
    action_authorization: bool = False
    memory_write: bool = False
    evidence_validation: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "unknown_key": self.unknown_key,
            "unknown_kind": self.unknown_kind,
            "unknown_status": self.unknown_status,
            "source_ref": self.source_ref,
            "candidate_ref": self.candidate_ref,
            "authority_needed_refs": self.authority_needed_refs,
            "no_guess": self.no_guess,
            "uncertainty_preserved": self.uncertainty_preserved,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("unknown_support", self.canonical_body())


def build_unknown_support_record(
    *,
    unknown_key: str,
    unknown_kind: str,
    unknown_status: str,
    source_ref: str,
    candidate_ref: str,
    authority_needed_refs: Tuple[str, ...],
    provenance_tag: str = "slice12_boundary",
    version_tag: str = "v1",
) -> UnknownSupportBoundaryRecord:
    body = {
        "unknown_key": unknown_key,
        "unknown_kind": unknown_kind,
        "unknown_status": unknown_status,
        "source_ref": source_ref,
        "candidate_ref": candidate_ref,
        "authority_needed_refs": authority_needed_refs,
        "no_guess": True,
        "uncertainty_preserved": True,
        "provenance_tag": provenance_tag,
        "version_tag": version_tag,
    }
    return UnknownSupportBoundaryRecord(unknown_boundary_id=stable_boundary_id("unknown_support", body), **body)


def validate_unknown_support_record(record: UnknownSupportBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.unknown_kind not in ALLOWED_UNKNOWN_KINDS:
        issues.append(_issue("unknown_kind", "unsupported_unknown_kind"))
    if record.unknown_status not in ALLOWED_UNKNOWN_STATUS:
        issues.append(_issue("unknown_status", "unsupported_unknown_status"))
    if not record.unknown_key:
        issues.append(_issue("unknown_key", "required"))
    if not record.source_ref:
        issues.append(_issue("source_ref", "required"))
    if not record.candidate_ref:
        issues.append(_issue("candidate_ref", "required"))
    if not _tuple_of_text(record.authority_needed_refs, allow_empty=False):
        issues.append(_issue("authority_needed_refs", "at_least_one_authority_ref_required"))
    if record.no_guess is not True:
        issues.append(_issue("no_guess", "must_remain_true"))
    if record.uncertainty_preserved is not True:
        issues.append(_issue("uncertainty_preserved", "must_remain_true"))
    if record.unknown_boundary_id != record.expected_id():
        issues.append(_issue("unknown_boundary_id", "does_not_match_canonical_body"))
    _check_false_only(record, UNKNOWN_FALSE_ONLY_FIELDS, issues, "slice12")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_unknown_concept_record() -> UnknownSupportBoundaryRecord:
    return build_unknown_support_record(
        unknown_key="unknown_concept_fixture_boundary",
        unknown_kind="unknown_concept_boundary",
        unknown_status="unknown_preserved_boundary",
        source_ref="src_expr:demo",
        candidate_ref="candidate_meaning:unknown_term",
        authority_needed_refs=("concept_authority:missing",),
        provenance_tag="slice12_demo_boundary",
    )


def demo_unsupported_resource_record() -> UnknownSupportBoundaryRecord:
    return build_unknown_support_record(
        unknown_key="unsupported_resource_fixture_boundary",
        unknown_kind="unsupported_resource_boundary",
        unknown_status="held_for_authority_boundary",
        source_ref="src_expr:demo",
        candidate_ref="candidate_meaning:external_resource_needed",
        authority_needed_refs=("resource_authority:not_admitted",),
        provenance_tag="slice12_demo_boundary",
    )
