from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-candidate-meaning-boundary-scaffold-v1"
SCOPE_STATUS = "candidate_meaning_boundary_scaffold_only"
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

ALLOWED_SOURCE_KINDS = (
    "user_expression_boundary",
    "system_expression_boundary",
    "test_fixture_expression_boundary",
    "unknown_expression_boundary",
)

ALLOWED_CUSTODY_STATUS = (
    "source_preserved_boundary",
    "source_redacted_boundary",
    "source_unknown_boundary",
)

SOURCE_FALSE_ONLY_FIELDS = (
    "live_runtime_interpretation",
    "source_rewrite_authority",
    "semantic_selection",
    "truth_decision",
    "action_authorization",
    "tool_invocation",
    "delivery_action",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
)


@dataclass(frozen=True)
class SourceExpressionCustodyRecord:
    source_expression_id: str
    source_ref: str
    source_kind: str
    source_text_boundary: str
    source_hash: str
    normalized_preview_boundary: str
    custody_status: str = "source_preserved_boundary"
    provenance_tag: str = "slice11_boundary"
    version_tag: str = "v1"
    live_runtime_interpretation: bool = False
    source_rewrite_authority: bool = False
    semantic_selection: bool = False
    truth_decision: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    delivery_action: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "source_ref": self.source_ref,
            "source_kind": self.source_kind,
            "source_text_boundary": self.source_text_boundary,
            "source_hash": self.source_hash,
            "normalized_preview_boundary": self.normalized_preview_boundary,
            "custody_status": self.custody_status,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("src_expr", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["source_expression_id"] = self.source_expression_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def _source_hash(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def _preview(text: str, limit: int = 96) -> str:
    clean = " ".join(str(text).split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


def build_source_expression_custody_record(
    *,
    source_ref: str,
    source_kind: str,
    source_text_boundary: str,
    custody_status: str = "source_preserved_boundary",
    provenance_tag: str = "slice11_boundary",
    version_tag: str = "v1",
) -> SourceExpressionCustodyRecord:
    body = {
        "source_ref": source_ref,
        "source_kind": source_kind,
        "source_text_boundary": source_text_boundary,
        "source_hash": _source_hash(source_text_boundary),
        "normalized_preview_boundary": _preview(source_text_boundary),
        "custody_status": custody_status,
        "provenance_tag": provenance_tag,
        "version_tag": version_tag,
    }
    return SourceExpressionCustodyRecord(source_expression_id=stable_boundary_id("src_expr", body), **body)


def validate_source_expression_custody_record(record: SourceExpressionCustodyRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.source_kind not in ALLOWED_SOURCE_KINDS:
        issues.append(_issue("source_kind", "unsupported_source_kind"))
    if record.custody_status not in ALLOWED_CUSTODY_STATUS:
        issues.append(_issue("custody_status", "unsupported_custody_status"))
    if not record.source_ref:
        issues.append(_issue("source_ref", "required"))
    if not isinstance(record.source_text_boundary, str):
        issues.append(_issue("source_text_boundary", "must_be_text_boundary"))
    if record.source_hash != _source_hash(record.source_text_boundary):
        issues.append(_issue("source_hash", "does_not_match_source_text_boundary"))
    if record.source_expression_id != record.expected_id():
        issues.append(_issue("source_expression_id", "does_not_match_canonical_body"))
    _check_false_only(record, SOURCE_FALSE_ONLY_FIELDS, issues, "slice11")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_source_expression_custody_record() -> SourceExpressionCustodyRecord:
    return build_source_expression_custody_record(
        source_ref="fixture:ask_forge_001",
        source_kind="test_fixture_expression_boundary",
        source_text_boundary="Draft a reply asking for the missing appointment time.",
        provenance_tag="slice11_demo_boundary",
    )
