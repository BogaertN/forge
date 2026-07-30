"""Fail-closed admission and identity checks for Operator Council evidence."""

from __future__ import annotations

from dataclasses import fields, replace
import re
from typing import Mapping

from .schema import (
    CouncilDissent,
    CouncilMemberPosition,
    CouncilRecommendation,
    CouncilValidationError,
    OPERATOR_COUNCIL_SCHEMA_VERSION,
    OperatorCouncilBoundary,
    OperatorCouncilDecisionReceipt,
    OperatorCouncilResult,
    SemanticRmcEvidenceEnvelope,
)


_REFERENCE = re.compile(
    r"^[A-Za-z][A-Za-z0-9_.-]{1,95}:[A-Za-z0-9_./:+-]{1,256}$"
)
_SYMBOLIC_LABEL = re.compile(r"^[a-z][a-z0-9_:-]{0,127}$")
_ECHO_STATUSES = frozenset({"PASS", "REJECT", "NOT_RUN"})
_RMC_CONNECTION_STATUSES = frozenset(
    {"CONNECTED_STRUCTURED", "CONNECTED_EMPTY"}
)
_SELECTED_MEANING_SUPPORT_STATUSES = frozenset(
    {"EXACT_SUPPORT", "NO_ADEQUATE_EXACT_SUPPORT"}
)
_BOOL_FIELDS = (
    "gates_passed",
    "selected_meaning_validated",
    "exact_reference_resonance_only",
    "read_only",
    "raw_text_present",
    "tokenization_performed",
    "model_called",
    "embedding_used",
    "vector_used",
    "similarity_scoring_used",
    "memory_write_performed",
    "tool_routing_performed",
    "action_performed",
    "delivery_performed",
)
_REFERENCE_TUPLE_FIELDS = (
    "concept_refs",
    "relation_refs",
    "ancestry_refs",
    "gate_receipt_refs",
    "rmc_evidence_refs",
    "authority_evidence_refs",
    "contradiction_refs",
    "uncertainty_refs",
)
_REQUIRED_NONEMPTY_REFERENCE_TUPLES = frozenset(
    {
        "concept_refs",
        "relation_refs",
        "ancestry_refs",
        "gate_receipt_refs",
        "authority_evidence_refs",
    }
)
_FORBIDDEN_TRUE_FIELDS = (
    "raw_text_present",
    "tokenization_performed",
    "model_called",
    "embedding_used",
    "vector_used",
    "similarity_scoring_used",
    "memory_write_performed",
    "tool_routing_performed",
    "action_performed",
    "delivery_performed",
)
_ENVELOPE_FIELD_NAMES = frozenset(
    item.name for item in fields(SemanticRmcEvidenceEnvelope)
)
_REQUIRED_MAPPING_FIELDS = _ENVELOPE_FIELD_NAMES - {"envelope_id", "schema_version"}


def _coerce_reference_tuple(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        raise CouncilValidationError((f"{field}:must_be_reference_sequence",))
    items = tuple(value)
    issues: list[str] = []
    if field in _REQUIRED_NONEMPTY_REFERENCE_TUPLES and not items:
        issues.append(f"{field}:must_not_be_empty")
    if any(type(item) is not str or not _REFERENCE.fullmatch(item) for item in items):
        issues.append(f"{field}:contains_invalid_reference")
    if len(items) != len(set(items)):
        issues.append(f"{field}:contains_duplicate_reference")
    if issues:
        raise CouncilValidationError(tuple(issues))
    return tuple(sorted(items))


def _validate_reference(value: object, field: str) -> str:
    if type(value) is not str or not _REFERENCE.fullmatch(value):
        raise CouncilValidationError((f"{field}:invalid_reference",))
    return value


def _validate_symbolic_label(value: object, field: str) -> str:
    if type(value) is not str or not _SYMBOLIC_LABEL.fullmatch(value):
        raise CouncilValidationError((f"{field}:invalid_symbolic_label",))
    return value


def _validate_text_choice(
    value: object,
    field: str,
    choices: frozenset[str],
) -> str:
    if type(value) is not str or value not in choices:
        raise CouncilValidationError((f"{field}:unsupported",))
    return value


def _build_evidence_from_mapping(
    value: Mapping[str, object],
) -> SemanticRmcEvidenceEnvelope:
    if any(type(key) is not str for key in value):
        raise CouncilValidationError(("envelope:field_names_must_be_text",))
    unknown = tuple(sorted(set(value) - _ENVELOPE_FIELD_NAMES))
    missing = tuple(sorted(_REQUIRED_MAPPING_FIELDS - set(value)))
    issues: list[str] = []
    if unknown:
        issues.append("envelope:unsupported_fields:" + ",".join(unknown))
    if missing:
        issues.append("envelope:missing_fields:" + ",".join(missing))
    if issues:
        raise CouncilValidationError(tuple(issues))

    supplied_version = value.get(
        "schema_version", OPERATOR_COUNCIL_SCHEMA_VERSION
    )
    if supplied_version != OPERATOR_COUNCIL_SCHEMA_VERSION:
        raise CouncilValidationError(("schema_version:unsupported",))

    bool_values: dict[str, bool] = {}
    bool_issues: list[str] = []
    for field in _BOOL_FIELDS:
        raw = value[field]
        if type(raw) is not bool:
            bool_issues.append(f"{field}:must_be_boolean")
        else:
            bool_values[field] = raw
    if bool_issues:
        raise CouncilValidationError(tuple(bool_issues))

    reference_tuples = {
        field: _coerce_reference_tuple(value[field], field)
        for field in _REFERENCE_TUPLE_FIELDS
    }
    evidence = SemanticRmcEvidenceEnvelope(
        envelope_id="pending",
        selected_meaning_ref=_validate_reference(
            value["selected_meaning_ref"], "selected_meaning_ref"
        ),
        semantic_signature=_validate_reference(
            value["semantic_signature"], "semantic_signature"
        ),
        speech_act=_validate_symbolic_label(value["speech_act"], "speech_act"),
        purport=_validate_symbolic_label(value["purport"], "purport"),
        predicate_ref=_validate_reference(value["predicate_ref"], "predicate_ref"),
        concept_refs=reference_tuples["concept_refs"],
        relation_refs=reference_tuples["relation_refs"],
        ancestry_refs=reference_tuples["ancestry_refs"],
        gate_receipt_refs=reference_tuples["gate_receipt_refs"],
        gates_passed=bool_values["gates_passed"],
        echo_receipt_ref=_validate_reference(
            value["echo_receipt_ref"], "echo_receipt_ref"
        ),
        echo_status=_validate_text_choice(
            value["echo_status"], "echo_status", _ECHO_STATUSES
        ),
        rmc_snapshot_ref=_validate_reference(
            value["rmc_snapshot_ref"], "rmc_snapshot_ref"
        ),
        rmc_connection_status=_validate_text_choice(
            value["rmc_connection_status"],
            "rmc_connection_status",
            _RMC_CONNECTION_STATUSES,
        ),
        selected_meaning_support_status=_validate_text_choice(
            value["selected_meaning_support_status"],
            "selected_meaning_support_status",
            _SELECTED_MEANING_SUPPORT_STATUSES,
        ),
        rmc_evidence_refs=reference_tuples["rmc_evidence_refs"],
        authority_evidence_refs=reference_tuples["authority_evidence_refs"],
        contradiction_refs=reference_tuples["contradiction_refs"],
        uncertainty_refs=reference_tuples["uncertainty_refs"],
        selected_meaning_validated=bool_values["selected_meaning_validated"],
        exact_reference_resonance_only=bool_values[
            "exact_reference_resonance_only"
        ],
        read_only=bool_values["read_only"],
        raw_text_present=bool_values["raw_text_present"],
        tokenization_performed=bool_values["tokenization_performed"],
        model_called=bool_values["model_called"],
        embedding_used=bool_values["embedding_used"],
        vector_used=bool_values["vector_used"],
        similarity_scoring_used=bool_values["similarity_scoring_used"],
        memory_write_performed=bool_values["memory_write_performed"],
        tool_routing_performed=bool_values["tool_routing_performed"],
        action_performed=bool_values["action_performed"],
        delivery_performed=bool_values["delivery_performed"],
    )
    evidence = replace(evidence, envelope_id=evidence.expected_id())
    supplied_id = value.get("envelope_id")
    if supplied_id is not None and supplied_id != evidence.envelope_id:
        raise CouncilValidationError(("envelope_id:content_identity_mismatch",))
    return evidence


def _validate_evidence_semantics(
    evidence: SemanticRmcEvidenceEnvelope,
) -> tuple[str, ...]:
    issues: list[str] = []
    if evidence.schema_version != OPERATOR_COUNCIL_SCHEMA_VERSION:
        issues.append("schema_version:unsupported")
    if evidence.envelope_id != evidence.expected_id():
        issues.append("envelope_id:content_identity_mismatch")
    if evidence.echo_status not in _ECHO_STATUSES:
        issues.append("echo_status:unsupported")
    if evidence.rmc_connection_status not in _RMC_CONNECTION_STATUSES:
        issues.append("rmc_connection_status:unsupported")
    if (
        evidence.selected_meaning_support_status
        not in _SELECTED_MEANING_SUPPORT_STATUSES
    ):
        issues.append("selected_meaning_support_status:unsupported")
    if evidence.exact_reference_resonance_only is not True:
        issues.append("exact_reference_resonance_only:must_remain_true")
    if evidence.read_only is not True:
        issues.append("read_only:must_remain_true")
    for field in _FORBIDDEN_TRUE_FIELDS:
        if getattr(evidence, field) is not False:
            issues.append(f"{field}:must_remain_false")
    if evidence.selected_meaning_support_status == "EXACT_SUPPORT":
        if evidence.rmc_connection_status != "CONNECTED_STRUCTURED":
            issues.append("selected_meaning_support_status:requires_structured_connection")
        if not evidence.rmc_evidence_refs:
            issues.append("rmc_evidence_refs:required_for_exact_support")
    elif evidence.rmc_evidence_refs:
        issues.append("rmc_evidence_refs:contradicts_absent_exact_support")
    if (
        evidence.rmc_connection_status == "CONNECTED_EMPTY"
        and evidence.selected_meaning_support_status != "NO_ADEQUATE_EXACT_SUPPORT"
    ):
        issues.append("selected_meaning_support_status:contradicts_connected_empty")
    return tuple(issues)


def coerce_evidence_envelope(value: object) -> SemanticRmcEvidenceEnvelope:
    """Admit a closed, structured evidence envelope or reject it unchanged."""

    if type(value) is SemanticRmcEvidenceEnvelope:
        # Rebuild through the mapping path so nested types and every field are
        # checked rather than trusting a caller-created frozen dataclass.
        evidence = _build_evidence_from_mapping(value.to_dict())
    elif isinstance(value, Mapping):
        evidence = _build_evidence_from_mapping(value)
    else:
        raise CouncilValidationError(("envelope:must_be_structured_mapping",))
    issues = _validate_evidence_semantics(evidence)
    if issues:
        raise CouncilValidationError(issues)
    return evidence


def validate_result_identities(result: OperatorCouncilResult) -> tuple[str, ...]:
    """Internal fail-closed validation of the complete immutable result."""

    issues: list[str] = []
    if result.schema_version != OPERATOR_COUNCIL_SCHEMA_VERSION:
        issues.append("result:schema_version_mismatch")
    if result.evidence.envelope_id != result.evidence.expected_id():
        issues.append("result:evidence_identity_mismatch")
    for position in result.positions:
        if not isinstance(position, CouncilMemberPosition):
            issues.append("result:position_type_invalid")
        elif position.position_id != position.expected_id():
            issues.append("result:position_identity_mismatch")
    for dissent in result.dissents:
        if not isinstance(dissent, CouncilDissent):
            issues.append("result:dissent_type_invalid")
        elif dissent.dissent_id != dissent.expected_id():
            issues.append("result:dissent_identity_mismatch")
    recommendation = result.recommendation
    if not isinstance(recommendation, CouncilRecommendation):
        issues.append("result:recommendation_type_invalid")
    elif recommendation.recommendation_id != recommendation.expected_id():
        issues.append("result:recommendation_identity_mismatch")
    boundary = result.boundary
    if not isinstance(boundary, OperatorCouncilBoundary):
        issues.append("result:boundary_type_invalid")
    elif boundary.boundary_id != boundary.expected_id():
        issues.append("result:boundary_identity_mismatch")
    receipt = result.receipt
    if not isinstance(receipt, OperatorCouncilDecisionReceipt):
        issues.append("result:receipt_type_invalid")
    elif receipt.receipt_id != receipt.expected_id():
        issues.append("result:receipt_identity_mismatch")
    if result.result_id != result.expected_id():
        issues.append("result:content_identity_mismatch")
    return tuple(issues)


__all__ = (
    "coerce_evidence_envelope",
    "validate_result_identities",
)
