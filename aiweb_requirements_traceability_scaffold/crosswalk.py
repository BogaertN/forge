from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    _canonicalize,
    check_false_only,
    issue,
    stable_traceability_id,
    tuple_of_text,
)

ALLOWED_TEST_CLASSES = (
    "behavior_test",
    "verifier_gate",
    "authority_boundary_test",
    "negative_test",
    "rollback_trigger_test",
    "result_packet_evidence_test",
    "accepted_scope_test",
)

ALLOWED_TRACEABILITY_STATUS = (
    "traceability_represented_only",
    "mapped_not_accepted",
    "mapped_pending_result_packet",
    "mapped_pending_decision_record",
)


@dataclass(frozen=True)
class RequirementTestCrosswalkRecord:
    crosswalk_id: str
    requirement_ref: str
    slice_ref: str
    test_class_refs: Tuple[str, ...]
    behavior_test_ref: str
    verifier_gate_ref: str
    authority_boundary_test_refs: Tuple[str, ...]
    negative_test_refs: Tuple[str, ...]
    traceability_status: str = "traceability_represented_only"
    version_tag: str = "v1"
    live_runtime_behavior: bool = False
    capability_acceptance: bool = False
    verifier_gate_replacement: bool = False
    result_packet_bypass: bool = False
    accepted_scope_widening: bool = False
    release_authority: bool = False
    production_readiness: bool = False
    delivery_action: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False
    final_meaning_selection: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    live_clarification: bool = False
    user_facing_question_emission: bool = False
    gp014_supersession: bool = False
    gp015_repair: bool = False
    gp015r1_installation: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "requirement_ref": self.requirement_ref,
            "slice_ref": self.slice_ref,
            "test_class_refs": self.test_class_refs,
            "behavior_test_ref": self.behavior_test_ref,
            "verifier_gate_ref": self.verifier_gate_ref,
            "authority_boundary_test_refs": self.authority_boundary_test_refs,
            "negative_test_refs": self.negative_test_refs,
            "traceability_status": self.traceability_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_traceability_id("requirement_test_crosswalk", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["crosswalk_id"] = self.crosswalk_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_requirement_test_crosswalk_record(
    *,
    requirement_ref: str,
    slice_ref: str,
    test_class_refs: Tuple[str, ...],
    behavior_test_ref: str,
    verifier_gate_ref: str,
    authority_boundary_test_refs: Tuple[str, ...],
    negative_test_refs: Tuple[str, ...],
    traceability_status: str = "traceability_represented_only",
    version_tag: str = "v1",
) -> RequirementTestCrosswalkRecord:
    body = {
        "requirement_ref": requirement_ref,
        "slice_ref": slice_ref,
        "test_class_refs": test_class_refs,
        "behavior_test_ref": behavior_test_ref,
        "verifier_gate_ref": verifier_gate_ref,
        "authority_boundary_test_refs": authority_boundary_test_refs,
        "negative_test_refs": negative_test_refs,
        "traceability_status": traceability_status,
        "version_tag": version_tag,
    }
    return RequirementTestCrosswalkRecord(
        crosswalk_id=stable_traceability_id("requirement_test_crosswalk", body),
        **body,
    )


def validate_requirement_test_crosswalk_record(record: RequirementTestCrosswalkRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record.requirement_ref, str) or not record.requirement_ref.strip():
        issues.append(issue("requirement_ref", "required_non_empty_text"))
    if not isinstance(record.slice_ref, str) or not record.slice_ref.strip():
        issues.append(issue("slice_ref", "required_non_empty_text"))
    if not tuple_of_text(record.test_class_refs, allow_empty=False):
        issues.append(issue("test_class_refs", "required_non_empty_text_tuple"))
    elif not all(item in ALLOWED_TEST_CLASSES for item in record.test_class_refs):
        issues.append(issue("test_class_refs", "unsupported_test_class"))
    if not isinstance(record.behavior_test_ref, str) or not record.behavior_test_ref.strip():
        issues.append(issue("behavior_test_ref", "required_non_empty_text"))
    if not isinstance(record.verifier_gate_ref, str) or not record.verifier_gate_ref.strip():
        issues.append(issue("verifier_gate_ref", "required_non_empty_text"))
    if not tuple_of_text(record.authority_boundary_test_refs, allow_empty=False):
        issues.append(issue("authority_boundary_test_refs", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.negative_test_refs, allow_empty=True):
        issues.append(issue("negative_test_refs", "text_tuple_required"))
    if record.traceability_status not in ALLOWED_TRACEABILITY_STATUS:
        issues.append(issue("traceability_status", "unsupported_traceability_status"))
    if record.crosswalk_id != record.expected_id():
        issues.append(issue("crosswalk_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "requirement_test_crosswalk")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_requirement_test_crosswalk_record() -> RequirementTestCrosswalkRecord:
    return build_requirement_test_crosswalk_record(
        requirement_ref="requirement_identity:demo-slice13",
        slice_ref="Slice13",
        test_class_refs=("behavior_test", "verifier_gate", "authority_boundary_test", "negative_test", "result_packet_evidence_test"),
        behavior_test_ref="scripts/test_aiweb_slice13_requirements_traceability_scaffold.py",
        verifier_gate_ref="scripts/aiweb_slice13_requirements_traceability_verify.py",
        authority_boundary_test_refs=("scope_blocks_downstream_authority", "frozen_paths_untouched"),
        negative_test_refs=("reject_result_packet_bypass", "reject_scope_widening", "reject_capability_acceptance"),
    )
