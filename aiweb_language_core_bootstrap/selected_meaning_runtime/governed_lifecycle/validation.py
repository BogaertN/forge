"""Fail-closed deterministic validation for Slice 41B records."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
import re
from typing import Any, Iterable

from ..authority import PERMANENT_SELECTED_MEANING_BOUNDARIES
from ..identity import (
    ALTERNATIVE_CANDIDATE_CUSTODY_SCHEMA_ID,
    GATE_CUSTODY_REFERENCE_SCHEMA_ID,
    INHERITED_LIMITATION_CUSTODY_SCHEMA_ID,
    SCHEMA_VERSION,
    SELECTED_MEANING_DECISION_STATUS_SCHEMA_ID,
    SELECTED_MEANING_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
    SELECTION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
    SELECTION_CANDIDATE_CUSTODY_SCHEMA_ID,
    SELECTION_ELIGIBILITY_STATUS_SCHEMA_ID,
    SELECTION_RECEIPT_BOUNDARY_SCHEMA_ID,
    SELECTION_TRACE_BOUNDARY_SCHEMA_ID,
    SPEC_ID,
    SPEC_VERSION,
    UNRESOLVED_STATE_CUSTODY_SCHEMA_ID,
)
from ..schema import (
    AlternativeCandidateCustodyRecord,
    GateCustodyReferenceRecord,
    InheritedLimitationCustodyRecord,
    SelectedMeaningDecisionCustodyState,
    SelectedMeaningDecisionStatusRecord,
    SelectedMeaningRuntimeSchemaRecord,
    SelectionAuthorityRequirementRecord,
    SelectionCandidateCustodyRecord,
    SelectionEligibilityCustodyState,
    SelectionEligibilityStatusRecord,
    SelectionReceiptBoundaryRecord,
    SelectionTraceBoundaryRecord,
    UnresolvedStateCustodyRecord,
)
from .canonical import (
    SelectedMeaningCanonicalizationError,
    canonical_field_order,
    canonical_record_bytes,
    canonicalize_field_pairs,
    deterministic_record_digest,
)
from .identity import (
    expected_bundle_digest,
    expected_bundle_id,
    expected_lifecycle_record_id,
    expected_lifecycle_transition_id,
    expected_record_id,
    expected_version_custody_id,
    identity_field,
)
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    DIGEST_ALGORITHM,
    SLICE41B_ACCEPTED_PARENT_HEAD,
    SLICE41B_ACCEPTED_PARENT_SUBJECT,
    SLICE41B_ACCEPTED_PARENT_TREE,
    SLICE41B_SCHEMA_VERSION,
    SUPPORTED_RUNTIME_SCHEMA_VERSIONS,
    SUPPORTED_RUNTIME_SPEC_VERSIONS,
    SelectedMeaningGovernanceBundle,
    SelectedMeaningLifecycleRecord,
    SelectedMeaningLifecycleStage,
    SelectedMeaningLifecycleTransitionRecord,
    SelectedMeaningValidationCode,
    SelectedMeaningValidationError,
    SelectedMeaningValidationIssue,
    SelectedMeaningValidationReport,
    SelectedMeaningVersionCustody,
)


_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:+/-]*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


_TRUE_FIELDS = {
    SelectionCandidateCustodyRecord: (
        "candidate_only",
        "selection_candidate_reference_only",
    ),
    GateCustodyReferenceRecord: (
        "exact_candidate_match_required",
        "all_four_gate_families_required",
        "composition_required",
        "gate_results_preserved_exactly",
    ),
    AlternativeCandidateCustodyRecord: ("alternatives_preserved",),
    UnresolvedStateCustodyRecord: ("unresolved_state_preserved",),
    InheritedLimitationCustodyRecord: ("limitations_preserved",),
    SelectionTraceBoundaryRecord: ("trace_boundary_only",),
    SelectionReceiptBoundaryRecord: ("receipt_boundary_only",),
    SelectedMeaningRuntimeSchemaRecord: ("schema_only", "versioned_companion"),
}

_FALSE_FIELDS = {
    SelectionCandidateCustodyRecord: (
        "candidate_eligibility_evaluated",
        "candidate_ranked",
        "candidate_selected",
    ),
    GateCustodyReferenceRecord: (
        "gate_results_re_evaluated",
        "composition_recomputed",
        "selection_performed",
    ),
    SelectionAuthorityRequirementRecord: (
        "requirement_satisfied",
        "requirement_failed",
        "authority_granted",
    ),
    AlternativeCandidateCustodyRecord: (
        "alternatives_ranked",
        "confidence_scores_created",
        "preferred_candidate_created",
        "alternatives_discarded",
        "ambiguity_resolved",
    ),
    UnresolvedStateCustodyRecord: (
        "unresolved_state_resolved",
        "clarification_emitted",
        "refusal_issued",
        "progression_authorized",
    ),
    InheritedLimitationCustodyRecord: (
        "limitations_released",
        "scope_enlarged",
        "authority_enlarged",
    ),
    SelectionEligibilityStatusRecord: (
        "eligibility_evaluated",
        "eligible_for_selected_meaning_construction",
        "not_eligible_determined",
        "candidate_ranked",
        "candidate_selected",
    ),
    SelectedMeaningDecisionStatusRecord: (
        "decision_performed",
        "candidate_selected",
        "selected_meaning_created",
        "msm_v1_modified",
    ),
    SelectionTraceBoundaryRecord: (
        "trace_validated",
        "selection_trace_created",
        "selection_performed",
    ),
    SelectionReceiptBoundaryRecord: (
        "receipt_validated",
        "selection_receipt_created",
        "selected_meaning_created",
    ),
    SelectedMeaningRuntimeSchemaRecord: (
        "deterministic_identity_calculated",
        "validation_performed",
        "canonical_serialization_performed",
        "lifecycle_transition_performed",
        "selection_eligibility_evaluated",
        "candidate_ranked",
        "alternatives_discarded",
        "ambiguity_resolved",
        "selection_decision_performed",
        "selected_meaning_created",
        "msm_v1_schema_modified",
        "msm_v1_automatic_migration_performed",
        "bootstrap_integration_enabled",
        "governed_outward_meaning_created",
        "truth_determined",
        "evidence_validated",
        "proof_claim_created",
        "permission_granted",
        "execution_authorized",
        "capability_availability_created",
        "route_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed",
        "memory_written",
        "rendered",
        "delivered",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
    ),
}

_STRING_FIELDS = {
    SelectionCandidateCustodyRecord: (
        "selection_candidate_custody_id", "candidate_meaning_id",
        "candidate_state_id", "candidate_lineage_id", "source_expression_ref",
        "manifest_candidate_record_ref", "manifest_candidate_companion_ref",
        "candidate_identity_ref", "candidate_content_ref",
        "candidate_provenance_ref", "candidate_construction_receipt_ref",
        "candidate_set_ref", "candidate_set_member_ref", "candidate_lifecycle_ref",
        "gate_candidate_input_ref",
    ),
    GateCustodyReferenceRecord: (
        "gate_custody_reference_id", "selection_candidate_custody_ref",
        "msm_gate_custody_companion_ref", "expectancy_family_custody_ref",
        "congruity_family_custody_ref", "connectedness_family_custody_ref",
        "recoverable_purpose_family_custody_ref", "expectancy_result_ref",
        "congruity_result_ref", "connectedness_result_ref",
        "recoverable_purpose_result_ref", "composition_result_ref",
    ),
    SelectionAuthorityRequirementRecord: (
        "selection_authority_requirement_id", "requirement_key",
        "requirement_version", "selection_candidate_custody_ref",
        "gate_custody_reference_ref",
    ),
    AlternativeCandidateCustodyRecord: (
        "alternative_candidate_custody_id", "selection_candidate_custody_ref",
        "candidate_set_ref",
    ),
    UnresolvedStateCustodyRecord: (
        "unresolved_state_custody_id", "selection_candidate_custody_ref",
    ),
    InheritedLimitationCustodyRecord: (
        "inherited_limitation_custody_id", "selection_candidate_custody_ref",
    ),
    SelectionEligibilityStatusRecord: (
        "selection_eligibility_status_id", "selection_candidate_custody_ref",
        "gate_custody_reference_ref", "alternative_candidate_custody_ref",
        "unresolved_state_custody_ref", "inherited_limitation_custody_ref",
    ),
    SelectedMeaningDecisionStatusRecord: (
        "selected_meaning_decision_status_id", "selection_candidate_custody_ref",
        "selection_eligibility_status_ref",
    ),
    SelectionTraceBoundaryRecord: (
        "selection_trace_boundary_id", "selection_candidate_custody_ref",
        "gate_custody_reference_ref", "alternative_candidate_custody_ref",
        "unresolved_state_custody_ref", "inherited_limitation_custody_ref",
        "selection_eligibility_status_ref", "selected_meaning_decision_status_ref",
    ),
    SelectionReceiptBoundaryRecord: (
        "selection_receipt_boundary_id", "selection_candidate_custody_ref",
        "selection_eligibility_status_ref", "selected_meaning_decision_status_ref",
        "selection_trace_boundary_ref",
    ),
    SelectedMeaningRuntimeSchemaRecord: (
        "selected_meaning_runtime_schema_record_id",
    ),
}

_TUPLE_IDENTIFIER_FIELDS = {
    SelectionCandidateCustodyRecord: ("predecessor_receipt_refs",),
    GateCustodyReferenceRecord: (
        "composition_disposition_refs", "candidate_specific_disposition_refs",
        "gate_profile_refs", "gate_trace_refs", "gate_provenance_refs",
        "gate_limitation_refs",
    ),
    SelectionAuthorityRequirementRecord: (
        "governing_document_refs", "required_authority_profile_refs",
        "required_candidate_state_refs", "required_gate_disposition_refs",
        "required_alternative_custody_refs", "required_unresolved_custody_refs",
        "required_limitation_custody_refs", "required_predecessor_receipt_refs",
        "deferred_authority_refs",
    ),
    AlternativeCandidateCustodyRecord: (
        "preserved_alternative_candidate_refs", "non_selected_candidate_refs",
        "alternative_relationship_refs", "alternative_disposition_refs",
        "material_ambiguity_refs", "clarification_relevant_refs",
        "shared_ancestry_refs", "exact_duplicate_group_refs",
    ),
    UnresolvedStateCustodyRecord: (
        "unresolved_candidate_refs", "unknown_refs", "unsupported_refs",
        "conflicted_refs", "clarification_dependency_refs", "held_refs",
        "blocked_progression_refs", "refusal_relevant_refs",
        "missing_authority_refs", "missing_structure_refs",
        "deferred_dependency_refs",
    ),
    InheritedLimitationCustodyRecord: (
        "source_limitation_refs", "candidate_limitation_refs", "gate_limitation_refs",
        "effect_boundary_refs", "domain_sensitive_refs",
        "authority_sensitive_distinction_refs", "evidence_boundary_refs",
        "memory_boundary_refs", "privacy_boundary_refs", "delivery_boundary_refs",
        "execution_boundary_refs", "correction_ancestry_refs",
        "supersession_ancestry_refs",
    ),
    SelectionEligibilityStatusRecord: (
        "selection_authority_requirement_refs", "status_reason_refs",
    ),
    SelectedMeaningDecisionStatusRecord: ("decision_reason_refs",),
    SelectionTraceBoundaryRecord: (
        "selection_authority_requirement_refs", "source_trace_refs",
        "candidate_trace_refs", "gate_trace_refs", "composition_trace_refs",
        "predecessor_receipt_refs",
    ),
    SelectionReceiptBoundaryRecord: (
        "required_law_refs", "prohibited_consequence_refs",
    ),
}

_SCHEMA_IDS = {
    SelectionCandidateCustodyRecord: SELECTION_CANDIDATE_CUSTODY_SCHEMA_ID,
    GateCustodyReferenceRecord: GATE_CUSTODY_REFERENCE_SCHEMA_ID,
    SelectionAuthorityRequirementRecord: SELECTION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
    AlternativeCandidateCustodyRecord: ALTERNATIVE_CANDIDATE_CUSTODY_SCHEMA_ID,
    UnresolvedStateCustodyRecord: UNRESOLVED_STATE_CUSTODY_SCHEMA_ID,
    InheritedLimitationCustodyRecord: INHERITED_LIMITATION_CUSTODY_SCHEMA_ID,
    SelectionEligibilityStatusRecord: SELECTION_ELIGIBILITY_STATUS_SCHEMA_ID,
    SelectedMeaningDecisionStatusRecord: SELECTED_MEANING_DECISION_STATUS_SCHEMA_ID,
    SelectionTraceBoundaryRecord: SELECTION_TRACE_BOUNDARY_SCHEMA_ID,
    SelectionReceiptBoundaryRecord: SELECTION_RECEIPT_BOUNDARY_SCHEMA_ID,
    SelectedMeaningRuntimeSchemaRecord: SELECTED_MEANING_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
}


def _issue(path: str, code: SelectedMeaningValidationCode, detail: str) -> SelectedMeaningValidationIssue:
    return SelectedMeaningValidationIssue(path=path, code=code, detail=detail)


def _report(issues: Iterable[SelectedMeaningValidationIssue]) -> SelectedMeaningValidationReport:
    return SelectedMeaningValidationReport(
        issues=tuple(sorted(issues, key=lambda item: (item.path, item.code.value, item.detail)))
    )


def _text(value: Any, path: str, *, identifier: bool = True) -> list[SelectedMeaningValidationIssue]:
    if type(value) is not str:
        return [_issue(path, SelectedMeaningValidationCode.TYPE_MISMATCH, "expected str")]
    if not value or value.strip() != value:
        return [_issue(path, SelectedMeaningValidationCode.REQUIRED_VALUE_MISSING, "non-empty trimmed text required")]
    if identifier and not _IDENTIFIER_RE.fullmatch(value):
        return [_issue(path, SelectedMeaningValidationCode.INVALID_IDENTIFIER, "invalid identifier token")]
    return []


def _version(value: Any, path: str) -> list[SelectedMeaningValidationIssue]:
    if type(value) is not str or not _VERSION_RE.fullmatch(value):
        return [_issue(path, SelectedMeaningValidationCode.INVALID_VERSION, "invalid version token")]
    return []


def _sha256(value: Any, path: str) -> list[SelectedMeaningValidationIssue]:
    if type(value) is not str or not _SHA256_RE.fullmatch(value):
        return [_issue(path, SelectedMeaningValidationCode.INVALID_SHA256, "expected lowercase SHA-256")]
    return []


def _identifier_tuple(value: Any, path: str, *, allow_empty: bool = True) -> list[SelectedMeaningValidationIssue]:
    issues: list[SelectedMeaningValidationIssue] = []
    if type(value) is not tuple:
        return [_issue(path, SelectedMeaningValidationCode.INVALID_TUPLE, "expected tuple")]
    if not allow_empty and not value:
        issues.append(_issue(path, SelectedMeaningValidationCode.REQUIRED_VALUE_MISSING, "tuple must not be empty"))
    seen: set[str] = set()
    for index, item in enumerate(value):
        issues.extend(_text(item, f"{path}[{index}]"))
        if isinstance(item, str):
            if item in seen:
                issues.append(_issue(f"{path}[{index}]", SelectedMeaningValidationCode.DUPLICATE_TUPLE_VALUE, f"duplicate value {item!r}"))
            seen.add(item)
    return issues


def _pair_tuple(value: Any, path: str) -> list[SelectedMeaningValidationIssue]:
    issues: list[SelectedMeaningValidationIssue] = []
    if type(value) is not tuple:
        return [_issue(path, SelectedMeaningValidationCode.INVALID_TUPLE, "expected tuple of pairs")]
    keys: set[str] = set()
    for index, pair in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(pair) is not tuple or len(pair) != 2:
            issues.append(_issue(item_path, SelectedMeaningValidationCode.INVALID_TUPLE, "expected (key, value) pair"))
            continue
        key, item = pair
        issues.extend(_text(key, f"{item_path}[0]"))
        issues.extend(_text(item, f"{item_path}[1]", identifier=False))
        if isinstance(key, str):
            if key in keys:
                issues.append(_issue(f"{item_path}[0]", SelectedMeaningValidationCode.DUPLICATE_TUPLE_VALUE, f"duplicate key {key!r}"))
            keys.add(key)
    return issues


def _fixed(record: Any, path: str) -> list[SelectedMeaningValidationIssue]:
    issues: list[SelectedMeaningValidationIssue] = []
    for name in _TRUE_FIELDS.get(type(record), ()):
        value = getattr(record, name)
        if type(value) is not bool or value is not True:
            issues.append(_issue(f"{path}.{name}", SelectedMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "must remain true as a custody boundary"))
    for name in _FALSE_FIELDS.get(type(record), ()):
        value = getattr(record, name)
        if type(value) is not bool:
            issues.append(_issue(f"{path}.{name}", SelectedMeaningValidationCode.TYPE_MISMATCH, "expected bool"))
        elif value:
            code = SelectedMeaningValidationCode.ELIGIBILITY_EVALUATION_PROHIBITED if "eligibility" in name else SelectedMeaningValidationCode.SELECTION_PROHIBITED if any(token in name for token in ("selected", "selection", "ranked", "ambiguity")) else SelectedMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            issues.append(_issue(f"{path}.{name}", code, "must remain false in Slice 41B"))
    return issues


def _validate_core_record(record: Any, expected_type: type[Any], path: str) -> list[SelectedMeaningValidationIssue]:
    if not isinstance(record, expected_type):
        return [_issue(path, SelectedMeaningValidationCode.TYPE_MISMATCH, f"expected {expected_type.__name__}")]
    issues: list[SelectedMeaningValidationIssue] = []
    for name in _STRING_FIELDS.get(expected_type, ()):
        issues.extend(_text(getattr(record, name), f"{path}.{name}"))
    for name in _TUPLE_IDENTIFIER_FIELDS.get(expected_type, ()):
        issues.extend(_identifier_tuple(getattr(record, name), f"{path}.{name}"))
    if hasattr(record, "schema_version") and record.schema_version != SCHEMA_VERSION:
        issues.append(_issue(f"{path}.schema_version", SelectedMeaningValidationCode.SCHEMA_VERSION_MISMATCH, f"expected {SCHEMA_VERSION!r}"))
    if hasattr(record, "schema_id") and record.schema_id != _SCHEMA_IDS[expected_type]:
        issues.append(_issue(f"{path}.schema_id", SelectedMeaningValidationCode.SCHEMA_VERSION_MISMATCH, f"expected {_SCHEMA_IDS[expected_type]!r}"))
    issues.extend(_fixed(record, path))
    try:
        actual_id = getattr(record, identity_field(expected_type))
        expected_id = expected_record_id(record)
        if actual_id != expected_id:
            issues.append(_issue(f"{path}.{identity_field(expected_type)}", SelectedMeaningValidationCode.IDENTITY_MISMATCH, "deterministic SHA-256 identity mismatch"))
    except (TypeError, SelectedMeaningCanonicalizationError, AttributeError) as error:
        issues.append(_issue(path, SelectedMeaningValidationCode.IDENTITY_MISMATCH, f"identity calculation failed: {error}"))
    return issues


def validate_field_pairs(record_type: type[Any], field_pairs: Iterable[tuple[str, Any]]) -> SelectedMeaningValidationReport:
    issues: list[SelectedMeaningValidationIssue] = []
    observed = tuple(field_pairs)
    expected = canonical_field_order(record_type)
    names: list[str] = []
    for index, pair in enumerate(observed):
        if type(pair) is not tuple or len(pair) != 2 or type(pair[0]) is not str:
            issues.append(_issue(f"field_pairs[{index}]", SelectedMeaningValidationCode.INVALID_TUPLE, "field pair must be (str, value)"))
            continue
        names.append(pair[0])
    for name in sorted({name for name in names if names.count(name) > 1}):
        issues.append(_issue(name, SelectedMeaningValidationCode.DUPLICATE_FIELD, "duplicate field"))
    for name in sorted(set(names).difference(expected)):
        issues.append(_issue(name, SelectedMeaningValidationCode.UNKNOWN_FIELD, "unknown field"))
    for name in expected:
        if name not in names:
            issues.append(_issue(name, SelectedMeaningValidationCode.MISSING_FIELD, "field missing"))
    if not issues and tuple(names) != expected:
        issues.append(_issue("field_pairs", SelectedMeaningValidationCode.FIELD_ORDER_MISMATCH, "fields are not in canonical order"))
    try:
        canonicalize_field_pairs(record_type, observed)
    except SelectedMeaningCanonicalizationError as error:
        if not issues:
            issues.append(_issue("field_pairs", SelectedMeaningValidationCode.FIELD_ORDER_MISMATCH, str(error)))
    return _report(issues)


def _individual_validator(expected_type: type[Any]):
    def validate(record: Any) -> SelectedMeaningValidationReport:
        return _report(_validate_core_record(record, expected_type, expected_type.__name__))
    return validate


validate_selection_candidate_custody = _individual_validator(SelectionCandidateCustodyRecord)
validate_gate_custody_reference = _individual_validator(GateCustodyReferenceRecord)
validate_selection_authority_requirement = _individual_validator(SelectionAuthorityRequirementRecord)
validate_alternative_candidate_custody = _individual_validator(AlternativeCandidateCustodyRecord)
validate_unresolved_state_custody = _individual_validator(UnresolvedStateCustodyRecord)
validate_inherited_limitation_custody = _individual_validator(InheritedLimitationCustodyRecord)
validate_selection_eligibility_status = _individual_validator(SelectionEligibilityStatusRecord)
validate_selected_meaning_decision_status = _individual_validator(SelectedMeaningDecisionStatusRecord)
validate_selection_trace_boundary = _individual_validator(SelectionTraceBoundaryRecord)
validate_selection_receipt_boundary = _individual_validator(SelectionReceiptBoundaryRecord)


def _identity_records(record: SelectedMeaningRuntimeSchemaRecord) -> tuple[Any, ...]:
    return (
        record.selection_candidate_custody,
        record.gate_custody_reference,
        *record.selection_authority_requirements,
        record.alternative_candidate_custody,
        record.unresolved_state_custody,
        record.inherited_limitation_custody,
        record.selection_eligibility_status,
        record.selected_meaning_decision_status,
        record.selection_trace_boundary,
        record.selection_receipt_boundary,
        record,
    )


def validate_identity_collection(records: Iterable[Any]) -> SelectedMeaningValidationReport:
    issues: list[SelectedMeaningValidationIssue] = []
    seen: dict[str, tuple[str, bytes]] = {}
    for index, record in enumerate(tuple(records)):
        path = f"records[{index}]"
        try:
            field_name = identity_field(type(record))
            record_id = getattr(record, field_name)
            payload = canonical_record_bytes(record, exclude_fields=(field_name,))
        except Exception as error:
            issues.append(_issue(path, SelectedMeaningValidationCode.IDENTITY_MISMATCH, f"identity collection failure: {error}"))
            continue
        previous = seen.get(record_id)
        if previous is not None:
            previous_type, previous_payload = previous
            code = SelectedMeaningValidationCode.DUPLICATE_RECORD_ID if previous_payload == payload and previous_type == type(record).__name__ else SelectedMeaningValidationCode.IDENTITY_COLLISION
            issues.append(_issue(path, code, f"record id {record_id!r} already used by {previous_type}"))
        else:
            seen[record_id] = (type(record).__name__, payload)
    return _report(issues)


def validate_runtime_schema_record(record: Any) -> SelectedMeaningValidationReport:
    if not isinstance(record, SelectedMeaningRuntimeSchemaRecord):
        return _report((_issue("record", SelectedMeaningValidationCode.TYPE_MISMATCH, "expected SelectedMeaningRuntimeSchemaRecord"),))
    issues = _validate_core_record(record, SelectedMeaningRuntimeSchemaRecord, "record")
    nested = (
        (record.selection_candidate_custody, SelectionCandidateCustodyRecord, "record.selection_candidate_custody"),
        (record.gate_custody_reference, GateCustodyReferenceRecord, "record.gate_custody_reference"),
        (record.alternative_candidate_custody, AlternativeCandidateCustodyRecord, "record.alternative_candidate_custody"),
        (record.unresolved_state_custody, UnresolvedStateCustodyRecord, "record.unresolved_state_custody"),
        (record.inherited_limitation_custody, InheritedLimitationCustodyRecord, "record.inherited_limitation_custody"),
        (record.selection_eligibility_status, SelectionEligibilityStatusRecord, "record.selection_eligibility_status"),
        (record.selected_meaning_decision_status, SelectedMeaningDecisionStatusRecord, "record.selected_meaning_decision_status"),
        (record.selection_trace_boundary, SelectionTraceBoundaryRecord, "record.selection_trace_boundary"),
        (record.selection_receipt_boundary, SelectionReceiptBoundaryRecord, "record.selection_receipt_boundary"),
    )
    for nested_record, nested_type, path in nested:
        issues.extend(_validate_core_record(nested_record, nested_type, path))
    if type(record.selection_authority_requirements) is not tuple or not record.selection_authority_requirements:
        issues.append(_issue("record.selection_authority_requirements", SelectedMeaningValidationCode.INVALID_TUPLE, "one or more authority requirement custody records required"))
    else:
        for index, requirement in enumerate(record.selection_authority_requirements):
            issues.extend(_validate_core_record(requirement, SelectionAuthorityRequirementRecord, f"record.selection_authority_requirements[{index}]"))

    candidate = record.selection_candidate_custody
    gate = record.gate_custody_reference
    alternatives = record.alternative_candidate_custody
    unresolved = record.unresolved_state_custody
    limitations = record.inherited_limitation_custody
    eligibility = record.selection_eligibility_status
    decision = record.selected_meaning_decision_status
    trace = record.selection_trace_boundary
    receipt = record.selection_receipt_boundary
    candidate_id = candidate.selection_candidate_custody_id
    requirement_ids = tuple(item.selection_authority_requirement_id for item in record.selection_authority_requirements if isinstance(item, SelectionAuthorityRequirementRecord))

    checks = (
        (gate.selection_candidate_custody_ref, candidate_id, "record.gate_custody_reference.selection_candidate_custody_ref"),
        (alternatives.selection_candidate_custody_ref, candidate_id, "record.alternative_candidate_custody.selection_candidate_custody_ref"),
        (alternatives.candidate_set_ref, candidate.candidate_set_ref, "record.alternative_candidate_custody.candidate_set_ref"),
        (unresolved.selection_candidate_custody_ref, candidate_id, "record.unresolved_state_custody.selection_candidate_custody_ref"),
        (limitations.selection_candidate_custody_ref, candidate_id, "record.inherited_limitation_custody.selection_candidate_custody_ref"),
        (eligibility.selection_candidate_custody_ref, candidate_id, "record.selection_eligibility_status.selection_candidate_custody_ref"),
        (eligibility.gate_custody_reference_ref, gate.gate_custody_reference_id, "record.selection_eligibility_status.gate_custody_reference_ref"),
        (eligibility.selection_authority_requirement_refs, requirement_ids, "record.selection_eligibility_status.selection_authority_requirement_refs"),
        (eligibility.alternative_candidate_custody_ref, alternatives.alternative_candidate_custody_id, "record.selection_eligibility_status.alternative_candidate_custody_ref"),
        (eligibility.unresolved_state_custody_ref, unresolved.unresolved_state_custody_id, "record.selection_eligibility_status.unresolved_state_custody_ref"),
        (eligibility.inherited_limitation_custody_ref, limitations.inherited_limitation_custody_id, "record.selection_eligibility_status.inherited_limitation_custody_ref"),
        (decision.selection_candidate_custody_ref, candidate_id, "record.selected_meaning_decision_status.selection_candidate_custody_ref"),
        (decision.selection_eligibility_status_ref, eligibility.selection_eligibility_status_id, "record.selected_meaning_decision_status.selection_eligibility_status_ref"),
        (trace.selection_candidate_custody_ref, candidate_id, "record.selection_trace_boundary.selection_candidate_custody_ref"),
        (trace.gate_custody_reference_ref, gate.gate_custody_reference_id, "record.selection_trace_boundary.gate_custody_reference_ref"),
        (trace.selection_authority_requirement_refs, requirement_ids, "record.selection_trace_boundary.selection_authority_requirement_refs"),
        (trace.alternative_candidate_custody_ref, alternatives.alternative_candidate_custody_id, "record.selection_trace_boundary.alternative_candidate_custody_ref"),
        (trace.unresolved_state_custody_ref, unresolved.unresolved_state_custody_id, "record.selection_trace_boundary.unresolved_state_custody_ref"),
        (trace.inherited_limitation_custody_ref, limitations.inherited_limitation_custody_id, "record.selection_trace_boundary.inherited_limitation_custody_ref"),
        (trace.selection_eligibility_status_ref, eligibility.selection_eligibility_status_id, "record.selection_trace_boundary.selection_eligibility_status_ref"),
        (trace.selected_meaning_decision_status_ref, decision.selected_meaning_decision_status_id, "record.selection_trace_boundary.selected_meaning_decision_status_ref"),
        (receipt.selection_candidate_custody_ref, candidate_id, "record.selection_receipt_boundary.selection_candidate_custody_ref"),
        (receipt.selection_eligibility_status_ref, eligibility.selection_eligibility_status_id, "record.selection_receipt_boundary.selection_eligibility_status_ref"),
        (receipt.selected_meaning_decision_status_ref, decision.selected_meaning_decision_status_id, "record.selection_receipt_boundary.selected_meaning_decision_status_ref"),
        (receipt.selection_trace_boundary_ref, trace.selection_trace_boundary_id, "record.selection_receipt_boundary.selection_trace_boundary_ref"),
    )
    for actual, expected, path in checks:
        if actual != expected:
            issues.append(_issue(path, SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, f"expected {expected!r}, received {actual!r}"))
    for index, requirement in enumerate(record.selection_authority_requirements):
        if not isinstance(requirement, SelectionAuthorityRequirementRecord):
            continue
        if requirement.selection_candidate_custody_ref != candidate_id:
            issues.append(_issue(f"record.selection_authority_requirements[{index}].selection_candidate_custody_ref", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "requirement candidate reference mismatch"))
        if requirement.gate_custody_reference_ref != gate.gate_custody_reference_id:
            issues.append(_issue(f"record.selection_authority_requirements[{index}].gate_custody_reference_ref", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "requirement gate reference mismatch"))
    if record.permanent_boundaries != PERMANENT_SELECTED_MEANING_BOUNDARIES:
        issues.append(_issue("record.permanent_boundaries", SelectedMeaningValidationCode.PREDECESSOR_REFERENCE_MISMATCH, "permanent Slice 41A boundaries must be preserved exactly"))
    if record.spec_id != SPEC_ID:
        issues.append(_issue("record.spec_id", SelectedMeaningValidationCode.SPEC_VERSION_MISMATCH, f"expected {SPEC_ID!r}"))
    if record.spec_version != SPEC_VERSION:
        issues.append(_issue("record.spec_version", SelectedMeaningValidationCode.SPEC_VERSION_MISMATCH, f"expected {SPEC_VERSION!r}"))
    issues.extend(validate_identity_collection(_identity_records(record)).issues)
    return _report(issues)


def expected_record_schema_versions(record: SelectedMeaningRuntimeSchemaRecord) -> tuple[tuple[str, str], ...]:
    versions: dict[str, str] = {}
    for item in _identity_records(record):
        versions[item.schema_id] = item.schema_version
    return tuple(sorted(versions.items()))


def expected_predecessor_references(record: SelectedMeaningRuntimeSchemaRecord) -> tuple[tuple[str, str], ...]:
    candidate = record.selection_candidate_custody
    return tuple(sorted((
        ("accepted_parent_head", SLICE41B_ACCEPTED_PARENT_HEAD),
        ("accepted_parent_tree", SLICE41B_ACCEPTED_PARENT_TREE),
        ("candidate_meaning", candidate.candidate_meaning_id),
        ("candidate_lineage", candidate.candidate_lineage_id),
        ("manifest_candidate_record", candidate.manifest_candidate_record_ref),
        ("manifest_candidate_companion", candidate.manifest_candidate_companion_ref),
        ("gate_custody_reference", record.gate_custody_reference.gate_custody_reference_id),
        ("alternative_candidate_custody", record.alternative_candidate_custody.alternative_candidate_custody_id),
        ("unresolved_state_custody", record.unresolved_state_custody.unresolved_state_custody_id),
        ("inherited_limitation_custody", record.inherited_limitation_custody.inherited_limitation_custody_id),
        ("selection_eligibility_status", record.selection_eligibility_status.selection_eligibility_status_id),
        ("selected_meaning_decision_status", record.selected_meaning_decision_status.selected_meaning_decision_status_id),
        ("selection_trace_boundary", record.selection_trace_boundary.selection_trace_boundary_id),
        ("selection_receipt_boundary", record.selection_receipt_boundary.selection_receipt_boundary_id),
    )))


def validate_version_custody(record: Any, *, runtime_record: SelectedMeaningRuntimeSchemaRecord | None = None) -> SelectedMeaningValidationReport:
    if not isinstance(record, SelectedMeaningVersionCustody):
        return _report((_issue("version_custody", SelectedMeaningValidationCode.TYPE_MISMATCH, "expected SelectedMeaningVersionCustody"),))
    issues: list[SelectedMeaningValidationIssue] = []
    for name in ("custody_id", "runtime_schema_record_id", "runtime_schema_version", "runtime_schema_id", "runtime_spec_id", "runtime_spec_version", "accepted_parent_head", "accepted_parent_tree", "accepted_parent_subject", "canonical_field_order_version", "digest_algorithm", "governance_schema_version"):
        issues.extend(_text(getattr(record, name), f"version_custody.{name}", identifier=name not in {"accepted_parent_subject"}))
    issues.extend(_pair_tuple(record.record_schema_versions, "version_custody.record_schema_versions"))
    issues.extend(_pair_tuple(record.predecessor_references, "version_custody.predecessor_references"))
    if record.runtime_schema_version not in SUPPORTED_RUNTIME_SCHEMA_VERSIONS:
        issues.append(_issue("version_custody.runtime_schema_version", SelectedMeaningValidationCode.UNKNOWN_VERSION, "runtime schema version is not admitted"))
    if record.runtime_spec_version not in SUPPORTED_RUNTIME_SPEC_VERSIONS:
        issues.append(_issue("version_custody.runtime_spec_version", SelectedMeaningValidationCode.UNKNOWN_VERSION, "runtime specification version is not admitted"))
    exacts = (
        (record.runtime_schema_id, SELECTED_MEANING_RUNTIME_SCHEMA_RECORD_SCHEMA_ID, "runtime_schema_id"),
        (record.runtime_spec_id, SPEC_ID, "runtime_spec_id"),
        (record.accepted_parent_head, SLICE41B_ACCEPTED_PARENT_HEAD, "accepted_parent_head"),
        (record.accepted_parent_tree, SLICE41B_ACCEPTED_PARENT_TREE, "accepted_parent_tree"),
        (record.accepted_parent_subject, SLICE41B_ACCEPTED_PARENT_SUBJECT, "accepted_parent_subject"),
        (record.canonical_field_order_version, CANONICAL_FIELD_ORDER_VERSION, "canonical_field_order_version"),
        (record.digest_algorithm, DIGEST_ALGORITHM, "digest_algorithm"),
        (record.governance_schema_version, SLICE41B_SCHEMA_VERSION, "governance_schema_version"),
    )
    for actual, expected, name in exacts:
        if actual != expected:
            issues.append(_issue(f"version_custody.{name}", SelectedMeaningValidationCode.SCHEMA_VERSION_MISMATCH, f"expected {expected!r}"))
    true_fields = ("non_llm_provenance",)
    false_fields = (
        "timestamps_in_identity", "randomness_in_identity", "process_identity_in_identity",
        "filesystem_state_in_identity", "environment_state_in_identity",
        "hash_table_order_in_identity", "eligibility_evaluation_authorized",
        "candidate_ranking_authorized", "selection_authorized",
        "selected_meaning_construction_authorized", "msm_v1_mutation_authorized",
        "bootstrap_integration_authorized", "truth_evidence_permission_execution_authorized",
        "route_tool_action_memory_rendering_delivery_authorized",
    )
    for name in true_fields:
        if getattr(record, name) is not True:
            issues.append(_issue(f"version_custody.{name}", SelectedMeaningValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED, "must be true"))
    for name in false_fields:
        if getattr(record, name) is not False:
            code = SelectedMeaningValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED if name.endswith("_in_identity") else SelectedMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            issues.append(_issue(f"version_custody.{name}", code, "must remain false"))
    try:
        if record.custody_id != expected_version_custody_id(record):
            issues.append(_issue("version_custody.custody_id", SelectedMeaningValidationCode.IDENTITY_MISMATCH, "deterministic custody id mismatch"))
    except Exception as error:
        issues.append(_issue("version_custody.custody_id", SelectedMeaningValidationCode.IDENTITY_MISMATCH, str(error)))
    if runtime_record is not None:
        if record.runtime_schema_record_id != runtime_record.selected_meaning_runtime_schema_record_id:
            issues.append(_issue("version_custody.runtime_schema_record_id", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "runtime schema record reference mismatch"))
        if record.record_schema_versions != expected_record_schema_versions(runtime_record):
            issues.append(_issue("version_custody.record_schema_versions", SelectedMeaningValidationCode.SCHEMA_VERSION_MISMATCH, "record schema versions do not match exact runtime records"))
        if record.predecessor_references != expected_predecessor_references(runtime_record):
            issues.append(_issue("version_custody.predecessor_references", SelectedMeaningValidationCode.PREDECESSOR_REFERENCE_MISMATCH, "predecessor references do not match exact runtime ancestry"))
    return _report(issues)


def validate_lifecycle_record(record: Any) -> SelectedMeaningValidationReport:
    if not isinstance(record, SelectedMeaningLifecycleRecord):
        return _report((_issue("lifecycle_record", SelectedMeaningValidationCode.TYPE_MISMATCH, "expected SelectedMeaningLifecycleRecord"),))
    issues: list[SelectedMeaningValidationIssue] = []
    for name in ("lifecycle_record_id", "runtime_schema_record_id", "version_custody_ref", "schema_version"):
        issues.extend(_text(getattr(record, name), f"lifecycle_record.{name}"))
    for name in ("predecessor_lifecycle_record_ids", "predecessor_reference_ids", "validation_issue_digest_refs", "reason_refs"):
        issues.extend(_identifier_tuple(getattr(record, name), f"lifecycle_record.{name}"))
    if not isinstance(record.stage, SelectedMeaningLifecycleStage):
        issues.append(_issue("lifecycle_record.stage", SelectedMeaningValidationCode.INVALID_ENUM, "invalid lifecycle stage"))
    if record.schema_version != SLICE41B_SCHEMA_VERSION:
        issues.append(_issue("lifecycle_record.schema_version", SelectedMeaningValidationCode.SCHEMA_VERSION_MISMATCH, "unknown lifecycle schema version"))
    for name in ("automatic_progression", "eligibility_evaluated", "gate_result_created", "candidate_ranked", "selection_performed", "selected_meaning_created", "msm_v1_modified", "bootstrap_integration_enabled", "truth_determined", "evidence_validated", "permission_granted", "execution_authorized", "route_created", "tool_invoked", "action_performed", "memory_written", "rendered", "delivered"):
        if getattr(record, name) is not False:
            code = SelectedMeaningValidationCode.AUTOMATIC_TRANSITION_PROHIBITED if name == "automatic_progression" else SelectedMeaningValidationCode.ELIGIBILITY_EVALUATION_PROHIBITED if name == "eligibility_evaluated" else SelectedMeaningValidationCode.SELECTION_PROHIBITED if name in {"candidate_ranked", "selection_performed", "selected_meaning_created"} else SelectedMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            issues.append(_issue(f"lifecycle_record.{name}", code, "must remain false"))
    for name in ("canonical_serialization_performed", "deterministic_identity_validated", "predecessor_references_validated", "cross_record_consistency_validated", "malformed_record_rejected", "unknown_version_rejected", "duplicate_record_rejected", "identity_collision_rejected"):
        if type(getattr(record, name)) is not bool:
            issues.append(_issue(f"lifecycle_record.{name}", SelectedMeaningValidationCode.TYPE_MISMATCH, "expected bool"))
    try:
        if record.lifecycle_record_id != expected_lifecycle_record_id(record):
            issues.append(_issue("lifecycle_record.lifecycle_record_id", SelectedMeaningValidationCode.IDENTITY_MISMATCH, "deterministic lifecycle id mismatch"))
    except Exception as error:
        issues.append(_issue("lifecycle_record.lifecycle_record_id", SelectedMeaningValidationCode.IDENTITY_MISMATCH, str(error)))
    return _report(issues)


def validate_lifecycle_transition_record(record: Any) -> SelectedMeaningValidationReport:
    if not isinstance(record, SelectedMeaningLifecycleTransitionRecord):
        return _report((_issue("transition", SelectedMeaningValidationCode.TYPE_MISMATCH, "expected SelectedMeaningLifecycleTransitionRecord"),))
    issues: list[SelectedMeaningValidationIssue] = []
    for name in ("transition_id", "runtime_schema_record_id", "source_lifecycle_record_id", "target_lifecycle_record_id", "version_custody_ref", "schema_version"):
        issues.extend(_text(getattr(record, name), f"transition.{name}"))
    for name in ("predecessor_transition_refs", "reason_refs"):
        issues.extend(_identifier_tuple(getattr(record, name), f"transition.{name}"))
    if not isinstance(record.from_stage, SelectedMeaningLifecycleStage) or not isinstance(record.to_stage, SelectedMeaningLifecycleStage):
        issues.append(_issue("transition.stage", SelectedMeaningValidationCode.INVALID_ENUM, "invalid lifecycle stage"))
    if not isinstance(record.transition_kind, Enum):
        issues.append(_issue("transition.transition_kind", SelectedMeaningValidationCode.INVALID_ENUM, "invalid transition kind"))
    if record.schema_version != SLICE41B_SCHEMA_VERSION:
        issues.append(_issue("transition.schema_version", SelectedMeaningValidationCode.SCHEMA_VERSION_MISMATCH, "unknown transition schema version"))
    for name in ("automatic_transition", "eligibility_evaluated", "candidate_ranked", "selection_performed", "selected_meaning_created", "msm_v1_modified", "bootstrap_integration_enabled", "truth_evidence_permission_execution_created", "route_tool_action_memory_rendering_delivery_created"):
        if getattr(record, name) is not False:
            code = SelectedMeaningValidationCode.AUTOMATIC_TRANSITION_PROHIBITED if name == "automatic_transition" else SelectedMeaningValidationCode.ELIGIBILITY_EVALUATION_PROHIBITED if name == "eligibility_evaluated" else SelectedMeaningValidationCode.SELECTION_PROHIBITED if name in {"candidate_ranked", "selection_performed", "selected_meaning_created"} else SelectedMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            issues.append(_issue(f"transition.{name}", code, "must remain false"))
    try:
        if record.transition_id != expected_lifecycle_transition_id(record):
            issues.append(_issue("transition.transition_id", SelectedMeaningValidationCode.IDENTITY_MISMATCH, "deterministic transition id mismatch"))
    except Exception as error:
        issues.append(_issue("transition.transition_id", SelectedMeaningValidationCode.IDENTITY_MISMATCH, str(error)))
    return _report(issues)


def validate_governance_bundle(record: Any) -> SelectedMeaningValidationReport:
    if not isinstance(record, SelectedMeaningGovernanceBundle):
        return _report((_issue("bundle", SelectedMeaningValidationCode.TYPE_MISMATCH, "expected SelectedMeaningGovernanceBundle"),))
    issues: list[SelectedMeaningValidationIssue] = []
    issues.extend(_text(record.bundle_id, "bundle.bundle_id"))
    issues.extend(_sha256(record.bundle_digest, "bundle.bundle_digest"))
    issues.extend(validate_runtime_schema_record(record.runtime_schema_record).issues)
    issues.extend(validate_version_custody(record.version_custody, runtime_record=record.runtime_schema_record).issues)
    issues.extend(validate_lifecycle_record(record.lifecycle_record).issues)
    if type(record.lifecycle_transitions) is not tuple:
        issues.append(_issue("bundle.lifecycle_transitions", SelectedMeaningValidationCode.INVALID_TUPLE, "expected tuple"))
    else:
        transition_ids: set[str] = set()
        for index, transition in enumerate(record.lifecycle_transitions):
            issues.extend(validate_lifecycle_transition_record(transition).issues)
            if isinstance(transition, SelectedMeaningLifecycleTransitionRecord):
                if transition.transition_id in transition_ids:
                    issues.append(_issue(f"bundle.lifecycle_transitions[{index}].transition_id", SelectedMeaningValidationCode.DUPLICATE_RECORD_ID, "duplicate transition id"))
                transition_ids.add(transition.transition_id)
    runtime_id = record.runtime_schema_record.selected_meaning_runtime_schema_record_id
    if record.version_custody.runtime_schema_record_id != runtime_id:
        issues.append(_issue("bundle.version_custody.runtime_schema_record_id", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "version custody runtime record mismatch"))
    if record.lifecycle_record.runtime_schema_record_id != runtime_id:
        issues.append(_issue("bundle.lifecycle_record.runtime_schema_record_id", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "lifecycle runtime record mismatch"))
    if record.lifecycle_record.version_custody_ref != record.version_custody.custody_id:
        issues.append(_issue("bundle.lifecycle_record.version_custody_ref", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "lifecycle version custody mismatch"))
    for index, transition in enumerate(record.lifecycle_transitions):
        if not isinstance(transition, SelectedMeaningLifecycleTransitionRecord):
            continue
        if transition.runtime_schema_record_id != runtime_id:
            issues.append(_issue(f"bundle.lifecycle_transitions[{index}].runtime_schema_record_id", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "transition runtime record mismatch"))
        if transition.version_custody_ref != record.version_custody.custody_id:
            issues.append(_issue(f"bundle.lifecycle_transitions[{index}].version_custody_ref", SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "transition version custody mismatch"))
    true_fields = ("validation_only", "immutable_successor_records", "exact_predecessor_references_required", "duplicate_and_collision_rejection_required", "unknown_version_rejection_required")
    false_fields = ("eligibility_evaluated", "gate_result_created", "candidate_ranked", "selection_performed", "selected_meaning_created", "msm_v1_modified", "bootstrap_integration_enabled", "truth_determined", "evidence_validated", "permission_granted", "execution_authorized", "route_created", "tool_invoked", "action_performed", "memory_written", "rendered", "delivered")
    for name in true_fields:
        if getattr(record, name) is not True:
            issues.append(_issue(f"bundle.{name}", SelectedMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "required validation boundary must be true"))
    for name in false_fields:
        if getattr(record, name) is not False:
            code = SelectedMeaningValidationCode.ELIGIBILITY_EVALUATION_PROHIBITED if name == "eligibility_evaluated" else SelectedMeaningValidationCode.SELECTION_PROHIBITED if name in {"candidate_ranked", "selection_performed", "selected_meaning_created"} else SelectedMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            issues.append(_issue(f"bundle.{name}", code, "must remain false"))
    if record.schema_version != SLICE41B_SCHEMA_VERSION:
        issues.append(_issue("bundle.schema_version", SelectedMeaningValidationCode.SCHEMA_VERSION_MISMATCH, "unknown bundle schema version"))
    try:
        if record.bundle_digest != expected_bundle_digest(record):
            issues.append(_issue("bundle.bundle_digest", SelectedMeaningValidationCode.CANONICAL_DIGEST_MISMATCH, "bundle digest mismatch"))
        if record.bundle_id != expected_bundle_id(record):
            issues.append(_issue("bundle.bundle_id", SelectedMeaningValidationCode.IDENTITY_MISMATCH, "bundle id mismatch"))
    except Exception as error:
        issues.append(_issue("bundle", SelectedMeaningValidationCode.IDENTITY_MISMATCH, f"bundle identity calculation failed: {error}"))
    return _report(issues)


def assert_valid_runtime_schema_record(record: SelectedMeaningRuntimeSchemaRecord) -> SelectedMeaningRuntimeSchemaRecord:
    report = validate_runtime_schema_record(record)
    if not report.ok:
        raise SelectedMeaningValidationError(report)
    return record


def assert_valid_version_custody(record: SelectedMeaningVersionCustody, *, runtime_record: SelectedMeaningRuntimeSchemaRecord | None = None) -> SelectedMeaningVersionCustody:
    report = validate_version_custody(record, runtime_record=runtime_record)
    if not report.ok:
        raise SelectedMeaningValidationError(report)
    return record


def assert_valid_governance_bundle(record: SelectedMeaningGovernanceBundle) -> SelectedMeaningGovernanceBundle:
    report = validate_governance_bundle(record)
    if not report.ok:
        raise SelectedMeaningValidationError(report)
    return record


__all__ = (
    "assert_valid_governance_bundle",
    "assert_valid_runtime_schema_record",
    "assert_valid_version_custody",
    "expected_predecessor_references",
    "expected_record_schema_versions",
    "validate_alternative_candidate_custody",
    "validate_field_pairs",
    "validate_gate_custody_reference",
    "validate_governance_bundle",
    "validate_identity_collection",
    "validate_inherited_limitation_custody",
    "validate_lifecycle_record",
    "validate_lifecycle_transition_record",
    "validate_runtime_schema_record",
    "validate_selected_meaning_decision_status",
    "validate_selection_authority_requirement",
    "validate_selection_candidate_custody",
    "validate_selection_eligibility_status",
    "validate_selection_receipt_boundary",
    "validate_selection_trace_boundary",
    "validate_unresolved_state_custody",
    "validate_version_custody",
)
