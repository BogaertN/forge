"""Fail-closed validation for Slice 39D candidate semantic content."""

from __future__ import annotations

import re
from typing import Any, Iterable

from ..governed_lifecycle import validate_content_record
from ..predecessor_custody import validate_custody
from .identity import (
    expected_assembly_digest,
    expected_assembly_id,
    expected_communicative_purpose_id,
    expected_distinction_id,
    expected_payload_id,
    expected_profile_id,
    expected_referent_id,
    expected_requested_act_id,
    expected_result_id,
    expected_semantic_relation_reference_id,
)
from .schema import (
    DIGEST_ALGORITHM,
    SLICE39D_PROFILE_VERSION,
    SLICE39D_SCHEMA_VERSION,
    SLICE39D_SPEC_ID,
    SLICE39D_SPEC_VERSION,
    CandidateCommunicativePurpose,
    CandidateReferentReference,
    CandidateRequestedActDescription,
    CandidateSemanticContentAssembly,
    CandidateSemanticContentAssemblyResult,
    CandidateSemanticContentPayload,
    CandidateSemanticContentProfileIdentity,
    CandidateSemanticContentStatus,
    CandidateSemanticContentValidationCode,
    CandidateSemanticContentValidationError,
    CandidateSemanticContentValidationIssue,
    CandidateSemanticContentValidationReport,
    CandidateSemanticDistinction,
    CandidateSemanticRelationReference,
    CommunicativeForceCandidate,
    ReferentCandidateKind,
    SemanticDistinctionKind,
)

_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]*\Z")
_VERSION_RE = re.compile(r"v?(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){0,2}\Z")
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")

_DOWNSTREAM_FALSE_FIELDS = (
    "participant_assignments_created",
    "referents_resolved",
    "clarification_question_emitted",
    "candidate_ranked",
    "candidate_selected",
    "gate_progression_created",
    "truth_determined",
    "evidence_validated",
    "permission_granted",
    "route_created",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
)


def _issue(issues: list[CandidateSemanticContentValidationIssue], path: str,
           code: CandidateSemanticContentValidationCode, detail: str) -> None:
    issues.append(CandidateSemanticContentValidationIssue(path, code, detail))


def _report(issues: list[CandidateSemanticContentValidationIssue]) -> CandidateSemanticContentValidationReport:
    return CandidateSemanticContentValidationReport(tuple(issues))


def _text(value: Any, path: str, issues: list[CandidateSemanticContentValidationIssue], *, allow_empty: bool = False) -> bool:
    if type(value) is not str:
        _issue(issues, path, CandidateSemanticContentValidationCode.TYPE_MISMATCH, "expected exact str")
        return False
    if not allow_empty and (not value or value != value.strip()):
        _issue(issues, path, CandidateSemanticContentValidationCode.REQUIRED_VALUE_MISSING, "expected non-empty trimmed text")
        return False
    return True


def _identifier(value: Any, path: str, issues: list[CandidateSemanticContentValidationIssue]) -> bool:
    if not _text(value, path, issues):
        return False
    if _IDENTIFIER_RE.fullmatch(value) is None:
        _issue(issues, path, CandidateSemanticContentValidationCode.INVALID_IDENTIFIER, "unsupported identifier characters")
        return False
    return True


def _version(value: Any, path: str, issues: list[CandidateSemanticContentValidationIssue]) -> bool:
    if not _text(value, path, issues):
        return False
    if _VERSION_RE.fullmatch(value) is None:
        _issue(issues, path, CandidateSemanticContentValidationCode.INVALID_VERSION, "expected N, N.N, N.N.N or v-prefixed equivalent")
        return False
    return True


def _sha(value: Any, path: str, issues: list[CandidateSemanticContentValidationIssue]) -> bool:
    if type(value) is not str or _SHA256_RE.fullmatch(value) is None:
        _issue(issues, path, CandidateSemanticContentValidationCode.INVALID_SHA256, "expected 64 lower-case hexadecimal characters")
        return False
    return True


def _tuple(value: Any, path: str, issues: list[CandidateSemanticContentValidationIssue], *, nonempty: bool = False) -> tuple[Any, ...]:
    if type(value) is not tuple:
        _issue(issues, path, CandidateSemanticContentValidationCode.INVALID_TUPLE, "expected exact tuple")
        return ()
    if nonempty and not value:
        _issue(issues, path, CandidateSemanticContentValidationCode.REQUIRED_VALUE_MISSING, "required tuple is empty")
    return value


def _unique(values: tuple[Any, ...], path: str, issues: list[CandidateSemanticContentValidationIssue]) -> None:
    try:
        if len(values) != len(set(values)):
            _issue(issues, path, CandidateSemanticContentValidationCode.DUPLICATE_VALUE, "duplicate tuple value")
    except TypeError:
        _issue(issues, path, CandidateSemanticContentValidationCode.TYPE_MISMATCH, "tuple values must be hashable")


def _identifiers(values: Any, path: str, issues: list[CandidateSemanticContentValidationIssue], *, nonempty: bool = False) -> tuple[str, ...]:
    result = _tuple(values, path, issues, nonempty=nonempty)
    for index, value in enumerate(result):
        _identifier(value, f"{path}[{index}]", issues)
    _unique(result, path, issues)
    return result


def _pairs(values: Any, path: str, issues: list[CandidateSemanticContentValidationIssue]) -> tuple[tuple[str, str], ...]:
    result = _tuple(values, path, issues)
    for index, pair in enumerate(result):
        if type(pair) is not tuple or len(pair) != 2:
            _issue(issues, f"{path}[{index}]", CandidateSemanticContentValidationCode.INVALID_TUPLE, "expected exact (identifier, version) pair")
            continue
        _identifier(pair[0], f"{path}[{index}][0]", issues)
        _version(pair[1], f"{path}[{index}][1]", issues)
    _unique(result, path, issues)
    return result


def _exact_bool(value: Any, expected: bool, path: str,
                issues: list[CandidateSemanticContentValidationIssue],
                code: CandidateSemanticContentValidationCode = CandidateSemanticContentValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED) -> None:
    if type(value) is not bool:
        _issue(issues, path, CandidateSemanticContentValidationCode.TYPE_MISMATCH, "expected exact bool")
    elif value is not expected:
        _issue(issues, path, code, f"expected {expected!r}")


def _schema(record: Any, issues: list[CandidateSemanticContentValidationIssue], path: str) -> None:
    if getattr(record, "schema_version", None) != SLICE39D_SCHEMA_VERSION:
        _issue(issues, f"{path}.schema_version", CandidateSemanticContentValidationCode.INVALID_VERSION, "Slice 39D schema version mismatch")


def validate_profile(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateSemanticContentProfileIdentity:
        _issue(issues, "profile", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateSemanticContentProfileIdentity required")
        return _report(issues)
    _identifier(record.profile_id, "profile.profile_id", issues)
    _identifier(record.profile_key, "profile.profile_key", issues)
    _version(record.profile_version, "profile.profile_version", issues)
    if record.profile_version != SLICE39D_PROFILE_VERSION:
        _issue(issues, "profile.profile_version", CandidateSemanticContentValidationCode.PROFILE_MISMATCH, "canonical Slice 39D profile version required")
    for name in (
        "exact_predecessor_custody_required", "exact_candidate_identity_required",
        "exact_registry_identity_required", "exact_source_span_support_required",
        "zero_one_many_preservation_required", "communicative_force_plurality_allowed",
        "semantic_relation_candidate_references_allowed",
    ):
        _exact_bool(getattr(record, name), True, f"profile.{name}", issues, CandidateSemanticContentValidationCode.PROFILE_MISMATCH)
    for name in (
        "role_assignment_allowed", "referent_resolution_allowed",
        "clarification_question_emission_allowed", "candidate_ranking_allowed",
        "candidate_selection_allowed", "gate_progression_allowed",
        "truth_evidence_permission_allowed",
        "route_action_memory_rendering_delivery_allowed",
    ):
        _exact_bool(getattr(record, name), False, f"profile.{name}", issues, CandidateSemanticContentValidationCode.PROFILE_MISMATCH)
    if record.spec_id != SLICE39D_SPEC_ID or record.spec_version != SLICE39D_SPEC_VERSION:
        _issue(issues, "profile.spec", CandidateSemanticContentValidationCode.PROFILE_MISMATCH, "Slice 39D spec identity mismatch")
    _schema(record, issues, "profile")
    if record.profile_id != expected_profile_id(record):
        _issue(issues, "profile.profile_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "deterministic profile identity mismatch")
    return _report(issues)


def validate_communicative_purpose(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateCommunicativePurpose:
        _issue(issues, "purpose", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateCommunicativePurpose required")
        return _report(issues)
    _identifier(record.purpose_id, "purpose.purpose_id", issues)
    keys = _identifiers(record.purpose_keys, "purpose.purpose_keys", issues, nonempty=True)
    forces = _tuple(record.force_candidates, "purpose.force_candidates", issues, nonempty=True)
    for index, force in enumerate(forces):
        if type(force) is not CommunicativeForceCandidate:
            _issue(issues, f"purpose.force_candidates[{index}]", CandidateSemanticContentValidationCode.INVALID_ENUM, "closed communicative force required")
    _unique(forces, "purpose.force_candidates", issues)
    _identifiers(record.source_action_predicate_candidate_ids, "purpose.source_action_predicate_candidate_ids", issues)
    _identifiers(record.source_scope_occurrence_ids, "purpose.source_scope_occurrence_ids", issues)
    _identifiers(record.source_span_ids, "purpose.source_span_ids", issues, nonempty=True)
    _exact_bool(record.candidate_only, True, "purpose.candidate_only", issues)
    _exact_bool(record.force_selected, False, "purpose.force_selected", issues)
    _exact_bool(record.gate_disposition_created, False, "purpose.gate_disposition_created", issues)
    _schema(record, issues, "purpose")
    if record.purpose_id != expected_communicative_purpose_id(record):
        _issue(issues, "purpose.purpose_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "deterministic purpose identity mismatch")
    return _report(issues)


def validate_requested_act(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateRequestedActDescription:
        _issue(issues, "requested_act", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateRequestedActDescription required")
        return _report(issues)
    for name in ("requested_act_id", "action_predicate_candidate_id", "action_root_id", "action_root_key", "predicate_id", "predicate_key"):
        _identifier(getattr(record, name), f"requested_act.{name}", issues)
    _version(record.action_root_version, "requested_act.action_root_version", issues)
    _version(record.predicate_version, "requested_act.predicate_version", issues)
    _pairs(record.frame_ids_and_versions, "requested_act.frame_ids_and_versions", issues)
    _identifiers(record.role_layout_candidate_ids, "requested_act.role_layout_candidate_ids", issues)
    _pairs(record.effect_boundary_ids_and_versions, "requested_act.effect_boundary_ids_and_versions", issues)
    _identifiers(record.capability_reference_candidate_ids, "requested_act.capability_reference_candidate_ids", issues)
    _identifiers(record.source_concept_candidate_ids, "requested_act.source_concept_candidate_ids", issues, nonempty=True)
    _identifiers(record.source_sense_candidate_ids, "requested_act.source_sense_candidate_ids", issues, nonempty=True)
    _identifiers(record.source_span_ids, "requested_act.source_span_ids", issues, nonempty=True)
    _exact_bool(record.candidate_only, True, "requested_act.candidate_only", issues)
    for name in ("permission_granted", "route_created", "invocation_proposed", "execution_performed"):
        _exact_bool(getattr(record, name), False, f"requested_act.{name}", issues)
    _schema(record, issues, "requested_act")
    if record.requested_act_id != expected_requested_act_id(record):
        _issue(issues, "requested_act.requested_act_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "deterministic requested-act identity mismatch")
    return _report(issues)


def validate_semantic_relation_reference(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateSemanticRelationReference:
        _issue(issues, "relation", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateSemanticRelationReference required")
        return _report(issues)
    for name in ("reference_id", "relation_type_id", "relation_type_key", "relation_family_id"):
        _identifier(getattr(record, name), f"relation.{name}", issues)
    _version(record.relation_type_version, "relation.relation_type_version", issues)
    _identifiers(record.source_concept_candidate_ids, "relation.source_concept_candidate_ids", issues, nonempty=True)
    _identifiers(record.target_concept_candidate_ids, "relation.target_concept_candidate_ids", issues, nonempty=True)
    _identifiers(record.source_record_ids, "relation.source_record_ids", issues, nonempty=True)
    _identifiers(record.source_span_ids, "relation.source_span_ids", issues, nonempty=True)
    _exact_bool(record.candidate_only, True, "relation.candidate_only", issues)
    _exact_bool(record.relation_instance_asserted, False, "relation.relation_instance_asserted", issues, CandidateSemanticContentValidationCode.RELATION_FACT_PROHIBITED)
    _exact_bool(record.truth_determined, False, "relation.truth_determined", issues)
    _exact_bool(record.evidence_validated, False, "relation.evidence_validated", issues)
    _schema(record, issues, "relation")
    if record.reference_id != expected_semantic_relation_reference_id(record):
        _issue(issues, "relation.reference_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "deterministic relation-reference identity mismatch")
    return _report(issues)


def validate_referent_reference(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateReferentReference:
        _issue(issues, "referent", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateReferentReference required")
        return _report(issues)
    _identifier(record.referent_id, "referent.referent_id", issues)
    if type(record.kind) is not ReferentCandidateKind:
        _issue(issues, "referent.kind", CandidateSemanticContentValidationCode.INVALID_ENUM, "closed referent kind required")
    _identifier(record.reference_analysis_id, "referent.reference_analysis_id", issues)
    if record.reference_candidate_id is not None:
        _identifier(record.reference_candidate_id, "referent.reference_candidate_id", issues)
    if record.context_object_id is not None:
        _identifier(record.context_object_id, "referent.context_object_id", issues)
    _text(record.exact_reference_form, "referent.exact_reference_form", issues)
    _identifiers(record.source_span_ids, "referent.source_span_ids", issues, nonempty=True)
    _exact_bool(record.candidate_only, True, "referent.candidate_only", issues)
    _exact_bool(record.referent_resolved, False, "referent.referent_resolved", issues)
    _exact_bool(record.selected, False, "referent.selected", issues)
    _schema(record, issues, "referent")
    if record.referent_id != expected_referent_id(record):
        _issue(issues, "referent.referent_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "deterministic referent identity mismatch")
    return _report(issues)


def validate_distinction(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateSemanticDistinction:
        _issue(issues, "distinction", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateSemanticDistinction required")
        return _report(issues)
    _identifier(record.distinction_id, "distinction.distinction_id", issues)
    if type(record.kind) is not SemanticDistinctionKind:
        _issue(issues, "distinction.kind", CandidateSemanticContentValidationCode.INVALID_ENUM, "closed distinction kind required")
    _identifier(record.distinction_code, "distinction.distinction_code", issues)
    _identifiers(record.source_record_ids, "distinction.source_record_ids", issues, nonempty=True)
    _identifiers(record.source_span_ids, "distinction.source_span_ids", issues)
    fragments = _tuple(record.exact_source_fragments, "distinction.exact_source_fragments", issues)
    for index, value in enumerate(fragments):
        _text(value, f"distinction.exact_source_fragments[{index}]", issues)
    _exact_bool(record.candidate_only, True, "distinction.candidate_only", issues)
    _exact_bool(record.selected, False, "distinction.selected", issues)
    _exact_bool(record.outcome_created, False, "distinction.outcome_created", issues)
    _schema(record, issues, "distinction")
    if record.distinction_id != expected_distinction_id(record):
        _issue(issues, "distinction.distinction_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "deterministic distinction identity mismatch")
    return _report(issues)


def validate_payload(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateSemanticContentPayload:
        _issue(issues, "payload", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateSemanticContentPayload required")
        return _report(issues)
    for name in ("payload_id", "lineage_id", "communicative_purpose_ref"):
        _identifier(getattr(record, name), f"payload.{name}", issues)
    forces = _tuple(record.communicative_force_candidates, "payload.communicative_force_candidates", issues, nonempty=True)
    for index, force in enumerate(forces):
        if type(force) is not CommunicativeForceCandidate:
            _issue(issues, f"payload.communicative_force_candidates[{index}]", CandidateSemanticContentValidationCode.INVALID_ENUM, "closed force candidate required")
    _unique(forces, "payload.communicative_force_candidates", issues)
    tuple_fields = (
        "requested_act_description_refs", "concept_candidate_refs", "sense_candidate_refs",
        "semantic_relation_candidate_refs", "action_root_candidate_refs", "predicate_candidate_refs",
        "frame_candidate_refs", "role_layout_candidate_refs", "referent_candidate_refs",
        "source_reference_refs", "comparison_target_reference_refs", "condition_refs",
        "negation_refs", "qualification_refs", "temporal_distinction_refs",
        "status_distinction_refs", "scope_refs", "attachment_refs", "limitation_refs",
        "missing_information_refs", "conflicting_information_refs",
        "authority_sensitive_implication_refs", "effect_boundary_refs",
        "capability_family_reference_refs",
    )
    for name in tuple_fields:
        _identifiers(getattr(record, name), f"payload.{name}", issues)
    _exact_bool(record.candidate_only, True, "payload.candidate_only", issues)
    _exact_bool(record.selected_content, False, "payload.selected_content", issues)
    _exact_bool(record.participant_assignments_created, False, "payload.participant_assignments_created", issues, CandidateSemanticContentValidationCode.ROLE_ASSIGNMENT_PROHIBITED)
    _exact_bool(record.referents_resolved, False, "payload.referents_resolved", issues)
    _exact_bool(record.clarification_question_emitted, False, "payload.clarification_question_emitted", issues, CandidateSemanticContentValidationCode.CLARIFICATION_EMISSION_PROHIBITED)
    _schema(record, issues, "payload")
    if record.payload_id != expected_payload_id(record):
        _issue(issues, "payload.payload_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "deterministic payload identity mismatch")
    return _report(issues)


def _extend(issues: list[CandidateSemanticContentValidationIssue], report: Any, prefix: str) -> None:
    if getattr(report, "ok", False):
        return
    for item in getattr(report, "issues", ()):
        code = item.code if type(item.code) is CandidateSemanticContentValidationCode else CandidateSemanticContentValidationCode.TYPE_MISMATCH
        issues.append(CandidateSemanticContentValidationIssue(f"{prefix}.{item.path}", code, item.detail))


def validate_assembly(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateSemanticContentAssembly:
        _issue(issues, "assembly", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateSemanticContentAssembly required")
        return _report(issues)
    _identifier(record.assembly_id, "assembly.assembly_id", issues)
    _identifier(record.lineage_id, "assembly.lineage_id", issues)
    custody_report = validate_custody(record.predecessor_custody)
    if not custody_report.ok:
        _issue(issues, "assembly.predecessor_custody", CandidateSemanticContentValidationCode.PREDECESSOR_CUSTODY_INVALID, "accepted Slice 39C custody required")
    if record.lineage_id != record.predecessor_custody.lineage_id:
        _issue(issues, "assembly.lineage_id", CandidateSemanticContentValidationCode.LINEAGE_MISMATCH, "assembly lineage must equal custody lineage")
    _extend(issues, validate_profile(record.profile), "assembly.profile")
    _extend(issues, validate_communicative_purpose(record.communicative_purpose), "assembly.communicative_purpose")
    for index, item in enumerate(_tuple(record.requested_act_descriptions, "assembly.requested_act_descriptions", issues)):
        _extend(issues, validate_requested_act(item), f"assembly.requested_act_descriptions[{index}]")
    for index, item in enumerate(_tuple(record.semantic_relation_references, "assembly.semantic_relation_references", issues)):
        _extend(issues, validate_semantic_relation_reference(item), f"assembly.semantic_relation_references[{index}]")
    for index, item in enumerate(_tuple(record.referent_references, "assembly.referent_references", issues)):
        _extend(issues, validate_referent_reference(item), f"assembly.referent_references[{index}]")
    for index, item in enumerate(_tuple(record.distinctions, "assembly.distinctions", issues)):
        _extend(issues, validate_distinction(item), f"assembly.distinctions[{index}]")
    _extend(issues, validate_payload(record.payload), "assembly.payload")
    content_report = validate_content_record(record.candidate_meaning_content)
    if not content_report.ok:
        _issue(issues, "assembly.candidate_meaning_content", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "Slice 39B CandidateMeaningContent validation failed")

    provenance = record.predecessor_custody.provenance
    source_span_ids = set(provenance.source_span_ids)
    concept_ids = set(provenance.concept_candidate_proposal_ids)
    sense_ids = set(provenance.sense_candidate_proposal_ids)
    action_ids = set(provenance.action_predicate_candidate_ids)
    role_ids = set(provenance.role_layout_candidate_ids)
    capability_ids = set(provenance.capability_reference_candidate_ids)

    purpose = record.communicative_purpose
    if not set(purpose.source_action_predicate_candidate_ids).issubset(action_ids):
        _issue(issues, "assembly.communicative_purpose", CandidateSemanticContentValidationCode.ACTION_ROOT_REFERENCE_FABRICATED, "purpose references foreign action/predicate candidate")
    if not set(purpose.source_span_ids).issubset(source_span_ids):
        _issue(issues, "assembly.communicative_purpose.source_span_ids", CandidateSemanticContentValidationCode.SOURCE_SPAN_MISMATCH, "purpose source span not in custody")

    requested_ids = tuple(item.requested_act_id for item in record.requested_act_descriptions)
    relation_ids = tuple(item.reference_id for item in record.semantic_relation_references)
    referent_ids = tuple(item.referent_id for item in record.referent_references)
    distinction_ids = {item.distinction_id for item in record.distinctions}
    distinction_by_kind = {
        kind: tuple(item.distinction_id for item in record.distinctions if item.kind is kind)
        for kind in SemanticDistinctionKind
    }

    for index, item in enumerate(record.requested_act_descriptions):
        if item.action_predicate_candidate_id not in action_ids:
            _issue(issues, f"assembly.requested_act_descriptions[{index}]", CandidateSemanticContentValidationCode.ACTION_ROOT_REFERENCE_FABRICATED, "foreign action/predicate candidate")
        if not set(item.role_layout_candidate_ids).issubset(role_ids):
            _issue(issues, f"assembly.requested_act_descriptions[{index}].role_layout_candidate_ids", CandidateSemanticContentValidationCode.ROLE_LAYOUT_REFERENCE_FABRICATED, "foreign role-layout candidate")
        if not set(item.capability_reference_candidate_ids).issubset(capability_ids):
            _issue(issues, f"assembly.requested_act_descriptions[{index}].capability_reference_candidate_ids", CandidateSemanticContentValidationCode.CAPABILITY_REFERENCE_FABRICATED, "foreign capability candidate")
        if not set(item.source_concept_candidate_ids).issubset(concept_ids):
            _issue(issues, f"assembly.requested_act_descriptions[{index}].source_concept_candidate_ids", CandidateSemanticContentValidationCode.CONCEPT_REFERENCE_FABRICATED, "foreign concept candidate")
        if not set(item.source_sense_candidate_ids).issubset(sense_ids):
            _issue(issues, f"assembly.requested_act_descriptions[{index}].source_sense_candidate_ids", CandidateSemanticContentValidationCode.SENSE_REFERENCE_FABRICATED, "foreign sense candidate")
        if not set(item.source_span_ids).issubset(source_span_ids):
            _issue(issues, f"assembly.requested_act_descriptions[{index}].source_span_ids", CandidateSemanticContentValidationCode.SOURCE_SPAN_MISMATCH, "foreign source span")

    for index, item in enumerate(record.semantic_relation_references):
        if not set(item.source_concept_candidate_ids).issubset(concept_ids) or not set(item.target_concept_candidate_ids).issubset(concept_ids):
            _issue(issues, f"assembly.semantic_relation_references[{index}]", CandidateSemanticContentValidationCode.SEMANTIC_RELATION_REFERENCE_FABRICATED, "relation endpoint is not an exact concept candidate")
        if not set(item.source_span_ids).issubset(source_span_ids):
            _issue(issues, f"assembly.semantic_relation_references[{index}].source_span_ids", CandidateSemanticContentValidationCode.SOURCE_SPAN_MISMATCH, "foreign source span")

    for index, item in enumerate(record.referent_references):
        if item.reference_analysis_id not in provenance.reference_analysis_ids:
            _issue(issues, f"assembly.referent_references[{index}].reference_analysis_id", CandidateSemanticContentValidationCode.REFERENT_REFERENCE_FABRICATED, "foreign reference analysis")
        if item.reference_candidate_id is not None and item.reference_candidate_id not in provenance.reference_candidate_ids:
            _issue(issues, f"assembly.referent_references[{index}].reference_candidate_id", CandidateSemanticContentValidationCode.REFERENT_REFERENCE_FABRICATED, "foreign reference candidate")
        if not set(item.source_span_ids).issubset(source_span_ids):
            _issue(issues, f"assembly.referent_references[{index}].source_span_ids", CandidateSemanticContentValidationCode.SOURCE_SPAN_MISMATCH, "foreign source span")

    for index, item in enumerate(record.distinctions):
        if not set(item.source_span_ids).issubset(source_span_ids):
            _issue(issues, f"assembly.distinctions[{index}].source_span_ids", CandidateSemanticContentValidationCode.SOURCE_SPAN_MISMATCH, "foreign source span")

    p = record.payload
    expected_payload = {
        "communicative_purpose_ref": purpose.purpose_id,
        "communicative_force_candidates": purpose.force_candidates,
        "requested_act_description_refs": requested_ids,
        "concept_candidate_refs": provenance.concept_candidate_proposal_ids,
        "sense_candidate_refs": provenance.sense_candidate_proposal_ids,
        "semantic_relation_candidate_refs": relation_ids,
        "action_root_candidate_refs": provenance.action_predicate_candidate_ids,
        "predicate_candidate_refs": provenance.action_predicate_candidate_ids,
        "role_layout_candidate_refs": provenance.role_layout_candidate_ids,
        "referent_candidate_refs": referent_ids,
        "condition_refs": distinction_by_kind[SemanticDistinctionKind.CONDITION],
        "negation_refs": distinction_by_kind[SemanticDistinctionKind.NEGATION],
        "qualification_refs": distinction_by_kind[SemanticDistinctionKind.QUALIFICATION],
        "temporal_distinction_refs": distinction_by_kind[SemanticDistinctionKind.TEMPORAL],
        "status_distinction_refs": distinction_by_kind[SemanticDistinctionKind.STATUS],
        "scope_refs": distinction_by_kind[SemanticDistinctionKind.SCOPE],
        "attachment_refs": distinction_by_kind[SemanticDistinctionKind.ATTACHMENT],
        "limitation_refs": distinction_by_kind[SemanticDistinctionKind.LIMITATION],
        "missing_information_refs": distinction_by_kind[SemanticDistinctionKind.MISSING_INFORMATION],
        "conflicting_information_refs": distinction_by_kind[SemanticDistinctionKind.CONFLICTING_INFORMATION],
        "authority_sensitive_implication_refs": distinction_by_kind[SemanticDistinctionKind.AUTHORITY_SENSITIVE_IMPLICATION],
        "capability_family_reference_refs": provenance.capability_reference_candidate_ids,
    }
    for name, expected in expected_payload.items():
        if getattr(p, name) != expected:
            _issue(issues, f"assembly.payload.{name}", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "payload does not exactly map assembled candidate records")
    if p.lineage_id != record.lineage_id:
        _issue(issues, "assembly.payload.lineage_id", CandidateSemanticContentValidationCode.LINEAGE_MISMATCH, "payload lineage mismatch")

    c = record.candidate_meaning_content
    if c.communicative_act_candidate != purpose.purpose_id:
        _issue(issues, "assembly.candidate_meaning_content.communicative_act_candidate", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "purpose mapping mismatch")
    exact_content_fields = {
        "concept_candidate_refs": p.concept_candidate_refs,
        "sense_candidate_refs": p.sense_candidate_refs,
        "semantic_relation_candidate_refs": p.semantic_relation_candidate_refs,
        "action_root_predicate_candidate_refs": p.action_root_candidate_refs,
        "frame_candidate_refs": p.frame_candidate_refs,
        "role_layout_candidate_refs": p.role_layout_candidate_refs,
        "referent_candidate_refs": p.referent_candidate_refs,
        "capability_reference_candidate_refs": p.capability_family_reference_refs,
        "effect_boundary_refs": p.effect_boundary_refs,
        "limitations": p.limitation_refs,
        "unresolved_referent_refs": tuple(item.referent_id for item in record.referent_references if item.kind is ReferentCandidateKind.UNRESOLVED),
        "missing_role_refs": p.missing_information_refs,
        "conflicting_role_refs": p.conflicting_information_refs,
        "authority_sensitive_implications": p.authority_sensitive_implication_refs,
    }
    for name, expected in exact_content_fields.items():
        if getattr(c, name) != expected:
            _issue(issues, f"assembly.candidate_meaning_content.{name}", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "CandidateMeaningContent mapping mismatch")

    for name in (
        "exact_predecessor_custody_verified", "exact_candidate_references_verified",
        "exact_registry_references_verified", "exact_source_span_support_verified",
        "zero_one_many_preserved", "candidate_semantic_content_assembled",
    ):
        _exact_bool(getattr(record, name), True, f"assembly.{name}", issues)
    for name in _DOWNSTREAM_FALSE_FIELDS:
        _exact_bool(getattr(record, name), False, f"assembly.{name}", issues,
                    CandidateSemanticContentValidationCode.CLARIFICATION_EMISSION_PROHIBITED if name == "clarification_question_emitted" else CandidateSemanticContentValidationCode.ROLE_ASSIGNMENT_PROHIBITED if name == "participant_assignments_created" else CandidateSemanticContentValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED)
    if record.digest_algorithm != DIGEST_ALGORITHM:
        _issue(issues, "assembly.digest_algorithm", CandidateSemanticContentValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED, "sha256 required")
    _sha(record.canonical_digest, "assembly.canonical_digest", issues)
    _schema(record, issues, "assembly")
    if record.canonical_digest != expected_assembly_digest(record):
        _issue(issues, "assembly.canonical_digest", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "assembly digest mismatch")
    if record.assembly_id != expected_assembly_id(record):
        _issue(issues, "assembly.assembly_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "assembly identity mismatch")
    return _report(issues)


def validate_assembly_result(record: Any) -> CandidateSemanticContentValidationReport:
    issues: list[CandidateSemanticContentValidationIssue] = []
    if type(record) is not CandidateSemanticContentAssemblyResult:
        _issue(issues, "result", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "exact CandidateSemanticContentAssemblyResult required")
        return _report(issues)
    _identifier(record.result_id, "result.result_id", issues)
    if type(record.status) is not CandidateSemanticContentStatus:
        _issue(issues, "result.status", CandidateSemanticContentValidationCode.INVALID_ENUM, "closed result status required")
    _identifier(record.reason_code, "result.reason_code", issues)
    if type(record.issues) is not tuple:
        _issue(issues, "result.issues", CandidateSemanticContentValidationCode.INVALID_TUPLE, "exact issue tuple required")
    for name in ("source_event_id", "lineage_id"):
        _identifier(getattr(record, name), f"result.{name}", issues)
    _sha(record.source_sha256, "result.source_sha256", issues)
    for name in (
        "communicative_force_candidate_count", "requested_act_description_count",
        "semantic_relation_reference_count", "referent_reference_count", "distinction_count",
    ):
        value = getattr(record, name)
        if type(value) is not int or value < 0:
            _issue(issues, f"result.{name}", CandidateSemanticContentValidationCode.TYPE_MISMATCH, "non-negative exact int required")
    if record.status is CandidateSemanticContentStatus.ASSEMBLED:
        if record.assembly is None:
            _issue(issues, "result.assembly", CandidateSemanticContentValidationCode.REQUIRED_VALUE_MISSING, "assembled result requires assembly")
        else:
            report = validate_assembly(record.assembly)
            if not report.ok:
                _issue(issues, "result.assembly", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "assembly validation failed")
            if record.source_event_id != record.assembly.predecessor_custody.provenance.source_event_id or record.source_sha256 != record.assembly.predecessor_custody.provenance.source_sha256 or record.lineage_id != record.assembly.lineage_id:
                _issue(issues, "result.lineage", CandidateSemanticContentValidationCode.LINEAGE_MISMATCH, "result lineage/source mismatch")
            expected_counts = (
                len(record.assembly.communicative_purpose.force_candidates),
                len(record.assembly.requested_act_descriptions),
                len(record.assembly.semantic_relation_references),
                len(record.assembly.referent_references),
                len(record.assembly.distinctions),
            )
            actual_counts = (
                record.communicative_force_candidate_count,
                record.requested_act_description_count,
                record.semantic_relation_reference_count,
                record.referent_reference_count,
                record.distinction_count,
            )
            if actual_counts != expected_counts:
                _issue(issues, "result.counts", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "result counts mismatch")
        _exact_bool(record.candidate_semantic_content_assembled, True, "result.candidate_semantic_content_assembled", issues)
        if record.issues:
            _issue(issues, "result.issues", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "assembled result must not carry issues")
    else:
        if record.assembly is not None:
            _issue(issues, "result.assembly", CandidateSemanticContentValidationCode.CONTENT_MAPPING_MISMATCH, "non-assembled result must not carry assembly")
        _exact_bool(record.candidate_semantic_content_assembled, False, "result.candidate_semantic_content_assembled", issues)
    for name in _DOWNSTREAM_FALSE_FIELDS:
        _exact_bool(getattr(record, name), False, f"result.{name}", issues,
                    CandidateSemanticContentValidationCode.CLARIFICATION_EMISSION_PROHIBITED if name == "clarification_question_emitted" else CandidateSemanticContentValidationCode.ROLE_ASSIGNMENT_PROHIBITED if name == "participant_assignments_created" else CandidateSemanticContentValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED)
    for name in (
        "filesystem_read_performed", "filesystem_write_performed", "network_access_performed",
        "external_resource_loaded", "language_model_used", "embedding_used", "semantic_similarity_used",
    ):
        _exact_bool(getattr(record, name), False, f"result.{name}", issues)
    _schema(record, issues, "result")
    if record.result_id != expected_result_id(record):
        _issue(issues, "result.result_id", CandidateSemanticContentValidationCode.IDENTITY_MISMATCH, "result identity mismatch")
    return _report(issues)


def assert_valid_assembly(record: CandidateSemanticContentAssembly) -> None:
    report = validate_assembly(record)
    if not report.ok:
        raise CandidateSemanticContentValidationError(report)


def assert_valid_assembly_result(record: CandidateSemanticContentAssemblyResult) -> None:
    report = validate_assembly_result(record)
    if not report.ok:
        raise CandidateSemanticContentValidationError(report)


__all__ = (
    "assert_valid_assembly",
    "assert_valid_assembly_result",
    "validate_assembly",
    "validate_assembly_result",
    "validate_communicative_purpose",
    "validate_distinction",
    "validate_payload",
    "validate_profile",
    "validate_referent_reference",
    "validate_requested_act",
    "validate_semantic_relation_reference",
)
