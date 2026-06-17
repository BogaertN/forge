from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-requirements-traceability-scaffold-v1"
SCOPE_STATUS = "requirements_traceability_scaffold_only"
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


def stable_traceability_id(prefix: str, *parts: Any) -> str:
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


def issue(field: str, reason: str) -> ValidationIssue:
    return ValidationIssue(field=field, reason=reason)


def tuple_of_text(value: Tuple[str, ...], *, allow_empty: bool = True) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    return all(isinstance(item, str) and bool(item.strip()) for item in value)


def check_false_only(record: Any, fields: Tuple[str, ...], issues: list[ValidationIssue], namespace: str) -> None:
    for field_name in fields:
        if bool(getattr(record, field_name, False)):
            issues.append(issue(field_name, f"{namespace}:{field_name}_must_remain_false"))


DOWNSTREAM_FALSE_ONLY_FIELDS = (
    "live_runtime_behavior",
    "capability_acceptance",
    "verifier_gate_replacement",
    "result_packet_bypass",
    "accepted_scope_widening",
    "release_authority",
    "production_readiness",
    "delivery_action",
    "action_authorization",
    "tool_invocation",
    "capability_route",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
    "final_meaning_selection",
    "selected_meaning",
    "truth_decision",
    "live_clarification",
    "user_facing_question_emission",
    "gp014_supersession",
    "gp015_repair",
    "gp015r1_installation",
    "model_authority",
    "vector_authority",
    "retrieval_authority",
)


def requirements_traceability_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "represents_requirement_identities": True,
        "represents_requirement_to_test_crosswalks": True,
        "represents_test_class_mappings": True,
        "represents_verifier_gate_references": True,
        "represents_evidence_receipt_references": True,
        "represents_rollback_trigger_references": True,
        "represents_accepted_scope_records": True,
        "represents_result_packet_references": True,
        "represents_decision_record_references": True,
        "represents_implementation_slice_traceability_status": True,
        "preserves_prior_accepted_scope_boundaries": True,
        "live_runtime_behavior": False,
        "capability_acceptance": False,
        "verifier_gate_replacement": False,
        "result_packet_bypass": False,
        "accepted_scope_widening": False,
        "release_authority": False,
        "production_readiness": False,
        "delivery_action": False,
        "action_authorization": False,
        "tool_invocation": False,
        "capability_route": False,
        "memory_write": False,
        "evidence_validation": False,
        "external_resource_admission": False,
        "final_meaning_selection": False,
        "selected_meaning": False,
        "truth_decision": False,
        "live_clarification": False,
        "user_facing_question_emission": False,
        "gp014_supersession": False,
        "gp014_status": "protected_not_superseded",
        "gp015_repair": False,
        "gp015_status": "failed_not_repaired",
        "gp015r1_installation": False,
        "gp015r1_status": "uninstalled_not_live",
        "sanskrit_wordnet_status": "hold_unadmitted",
        "model_authority": False,
        "vector_authority": False,
        "retrieval_authority": False,
    }
