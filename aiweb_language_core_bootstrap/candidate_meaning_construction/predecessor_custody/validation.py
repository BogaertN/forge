"""Fail-closed validation for Slice 39C predecessor custody."""

from __future__ import annotations

from enum import Enum
import re
from typing import Any, Callable

from ..governed_lifecycle.identity import expected_provenance_id
from ..schema import CandidateMeaningProvenance
from .authority import SLICE39C_REQUIRED_STAGES
from .identity import (
    expected_binding_result_id,
    expected_custody_digest,
    expected_custody_id,
    expected_lineage_id,
    expected_operator_reference_id,
    expected_profile_id,
    expected_receipt_id,
    expected_registry_resource_reference_id,
    expected_source_span_reference_id,
    expected_structural_rule_reference_id,
)
from .schema import (
    DIGEST_ALGORITHM,
    SLICE39C_PROFILE_VERSION,
    SLICE39C_SCHEMA_VERSION,
    SLICE39C_SPEC_ID,
    SLICE39C_SPEC_VERSION,
    CandidateMeaningConstructionProfileIdentity,
    CandidateMeaningPredecessorBindingResult,
    CandidateMeaningPredecessorCustody,
    OperatorCustodyReference,
    PredecessorCustodyReceipt,
    PredecessorCustodyStage,
    PredecessorCustodyStatus,
    PredecessorCustodyValidationCode,
    PredecessorCustodyValidationIssue,
    PredecessorCustodyValidationReport,
    RegistryResourceCustodyReference,
    RegistryResourceKind,
    SourceSpanCustodyReference,
    StructuralRuleCustodyReference,
)


_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]*\Z")
_VERSION_RE = re.compile(
    r"v?(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){0,2}\Z"
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_FALSE_FIELDS = (
    "semantic_payload_constructed",
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
_REQUIRED_RESOURCE_KINDS = frozenset(
    (
        RegistryResourceKind.CONCEPT,
        RegistryResourceKind.SENSE,
        RegistryResourceKind.ACTION_ROOT,
        RegistryResourceKind.PREDICATE,
        RegistryResourceKind.PARTICIPANT_ROLE,
        RegistryResourceKind.PREDICATE_FRAME,
        RegistryResourceKind.EFFECT_BOUNDARY,
        RegistryResourceKind.FRAME_EFFECT_REFERENCE,
    )
)


def _issue(
    issues: list[PredecessorCustodyValidationIssue],
    path: str,
    code: PredecessorCustodyValidationCode,
    detail: str,
) -> None:
    issues.append(
        PredecessorCustodyValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def _report(
    issues: list[PredecessorCustodyValidationIssue],
) -> PredecessorCustodyValidationReport:
    return PredecessorCustodyValidationReport(issues=tuple(issues))


def _text(
    value: Any,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
) -> bool:
    if type(value) is not str:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "expected exact str",
        )
        return False
    if not value or value != value.strip():
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.REQUIRED_VALUE_MISSING,
            "expected non-empty trimmed text",
        )
        return False
    return True


def _identifier(
    value: Any,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
) -> bool:
    if not _text(value, path=path, issues=issues):
        return False
    if _IDENTIFIER_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.INVALID_IDENTIFIER,
            "unsupported identifier characters",
        )
        return False
    return True


def _version(
    value: Any,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
) -> bool:
    if not _text(value, path=path, issues=issues):
        return False
    if _VERSION_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.INVALID_VERSION,
            "expected canonical N, N.N, N.N.N or v-prefixed equivalent",
        )
        return False
    return True


def _sha256(
    value: Any,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
) -> bool:
    if type(value) is not str or _SHA256_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.INVALID_SHA256,
            "expected 64 lower-case hexadecimal characters",
        )
        return False
    return True


def _exact_bool(
    value: Any,
    expected: bool,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
    code: PredecessorCustodyValidationCode = (
        PredecessorCustodyValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
    ),
) -> bool:
    if type(value) is not bool:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "expected exact bool",
        )
        return False
    if value is not expected:
        _issue(issues, path, code, f"expected {expected!r}")
        return False
    return True


def _integer(
    value: Any,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
    minimum: int = 0,
) -> bool:
    if type(value) is not int:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "expected exact int",
        )
        return False
    if value < minimum:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.REQUIRED_VALUE_MISSING,
            f"expected integer >= {minimum}",
        )
        return False
    return True


def _tuple(
    value: Any,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
    nonempty: bool = False,
) -> tuple[Any, ...]:
    if type(value) is not tuple:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.INVALID_TUPLE,
            "expected exact tuple",
        )
        return ()
    if nonempty and not value:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE,
            "required predecessor tuple is empty",
        )
    return value


def _unique(
    values: tuple[Any, ...],
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
) -> None:
    try:
        duplicate = len(values) != len(set(values))
    except Exception:
        duplicate = True
    if duplicate:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.DUPLICATE_VALUE,
            "duplicate values are prohibited",
        )


def _schema(
    value: Any,
    *,
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
) -> None:
    if value != SLICE39C_SCHEMA_VERSION:
        _issue(
            issues,
            path,
            PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH,
            "Slice 39C schema version mismatch",
        )


def validate_construction_profile(
    record: Any,
) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not CandidateMeaningConstructionProfileIdentity:
        _issue(
            issues,
            "profile",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact CandidateMeaningConstructionProfileIdentity required",
        )
        return _report(issues)
    _identifier(record.profile_id, path="profile.profile_id", issues=issues)
    _text(record.profile_key, path="profile.profile_key", issues=issues)
    _version(record.profile_version, path="profile.profile_version", issues=issues)
    stages = _tuple(
        record.required_stages,
        path="profile.required_stages",
        issues=issues,
        nonempty=True,
    )
    if stages != SLICE39C_REQUIRED_STAGES:
        _issue(
            issues,
            "profile.required_stages",
            PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH,
            "exact Slice 39C predecessor stage order required",
        )
    for name in (
        "exact_source_event_required",
        "exact_source_checksum_required",
        "exact_source_span_reconstruction_required",
        "exact_structural_rule_ancestry_required",
        "exact_operator_ancestry_required",
        "exact_phase_trail_ancestry_required",
        "exact_scope_attachment_reference_ancestry_required",
        "exact_registry_snapshot_required",
        "exact_resource_version_required",
        "zero_one_many_preservation_required",
    ):
        _exact_bool(
            getattr(record, name),
            True,
            path=f"profile.{name}",
            issues=issues,
            code=PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH,
        )
    for name in (
        "cross_lineage_merge_allowed",
        "generated_substitute_ancestry_allowed",
        "semantic_payload_construction_allowed",
        "candidate_ranking_allowed",
        "candidate_selection_allowed",
        "gate_progression_allowed",
        "truth_evidence_permission_allowed",
        "route_action_memory_rendering_delivery_allowed",
    ):
        _exact_bool(
            getattr(record, name),
            False,
            path=f"profile.{name}",
            issues=issues,
            code=(
                PredecessorCustodyValidationCode.GENERATED_SUBSTITUTE_ANCESTRY
                if name == "generated_substitute_ancestry_allowed"
                else PredecessorCustodyValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            ),
        )
    if record.profile_version != SLICE39C_PROFILE_VERSION:
        _issue(
            issues,
            "profile.profile_version",
            PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH,
            "canonical Slice 39C profile version required",
        )
    if record.spec_id != SLICE39C_SPEC_ID:
        _issue(
            issues,
            "profile.spec_id",
            PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH,
            "spec id mismatch",
        )
    if record.spec_version != SLICE39C_SPEC_VERSION:
        _issue(
            issues,
            "profile.spec_version",
            PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH,
            "spec version mismatch",
        )
    _schema(record.schema_version, path="profile.schema_version", issues=issues)
    try:
        expected = expected_profile_id(record)
    except Exception:
        expected = None
    if record.profile_id != expected:
        _issue(
            issues,
            "profile.profile_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "profile identity does not match canonical body",
        )
    return _report(issues)


def validate_source_span_reference(
    record: Any,
) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not SourceSpanCustodyReference:
        _issue(
            issues,
            "source_span_reference",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact SourceSpanCustodyReference required",
        )
        return _report(issues)
    for name in ("reference_id", "span_id", "input_event_id"):
        _identifier(getattr(record, name), path=f"source_span.{name}", issues=issues)
    _sha256(record.source_sha256, path="source_span.source_sha256", issues=issues)
    _sha256(record.span_sha256, path="source_span.span_sha256", issues=issues)
    for name in (
        "code_point_start",
        "code_point_end",
        "utf8_byte_start",
        "utf8_byte_end",
    ):
        _integer(getattr(record, name), path=f"source_span.{name}", issues=issues)
    if record.code_point_end <= record.code_point_start:
        _issue(
            issues,
            "source_span.code_point_end",
            PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
            "source span must have positive code-point length",
        )
    if record.utf8_byte_end <= record.utf8_byte_start:
        _issue(
            issues,
            "source_span.utf8_byte_end",
            PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
            "source span must have positive UTF-8 byte length",
        )
    if type(record.is_root_span) is not bool:
        _issue(
            issues,
            "source_span.is_root_span",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "is_root_span must be exact bool",
        )
    observed = _tuple(
        record.observed_in_record_ids,
        path="source_span.observed_in_record_ids",
        issues=issues,
        nonempty=True,
    )
    for index, value in enumerate(observed):
        _identifier(
            value,
            path=f"source_span.observed_in_record_ids[{index}]",
            issues=issues,
        )
    _unique(observed, path="source_span.observed_in_record_ids", issues=issues)
    _schema(record.schema_version, path="source_span.schema_version", issues=issues)
    try:
        expected = expected_source_span_reference_id(record)
    except Exception:
        expected = None
    if record.reference_id != expected:
        _issue(
            issues,
            "source_span.reference_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "source-span custody identity mismatch",
        )
    return _report(issues)


def validate_structural_rule_reference(
    record: Any,
) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not StructuralRuleCustodyReference:
        _issue(
            issues,
            "structural_rule_reference",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact StructuralRuleCustodyReference required",
        )
        return _report(issues)
    for name in (
        "reference_id",
        "trace_id",
        "structural_candidate_id",
        "derivation_rule_id",
    ):
        _identifier(getattr(record, name), path=f"structural_rule.{name}", issues=issues)
    _text(
        record.derivation_rule_key,
        path="structural_rule.derivation_rule_key",
        issues=issues,
    )
    _version(
        record.derivation_rule_version,
        path="structural_rule.derivation_rule_version",
        issues=issues,
    )
    pairs = _tuple(
        record.source_rule_ids_and_versions,
        path="structural_rule.source_rule_ids_and_versions",
        issues=issues,
    )
    for index, pair in enumerate(pairs):
        if type(pair) is not tuple or len(pair) != 2:
            _issue(
                issues,
                f"structural_rule.source_rule_ids_and_versions[{index}]",
                PredecessorCustodyValidationCode.TYPE_MISMATCH,
                "expected exact (id, version) pair",
            )
            continue
        _identifier(pair[0], path=f"structural_rule.source_rules[{index}].id", issues=issues)
        _identifier(pair[1], path=f"structural_rule.source_rules[{index}].version", issues=issues)
    for name in ("input_record_ids", "output_record_ids", "source_span_ids"):
        values = _tuple(
            getattr(record, name),
            path=f"structural_rule.{name}",
            issues=issues,
            nonempty=False,
        )
        for index, value in enumerate(values):
            _identifier(value, path=f"structural_rule.{name}[{index}]", issues=issues)
        _unique(values, path=f"structural_rule.{name}", issues=issues)
    _schema(record.schema_version, path="structural_rule.schema_version", issues=issues)
    try:
        expected = expected_structural_rule_reference_id(record)
    except Exception:
        expected = None
    if record.reference_id != expected:
        _issue(
            issues,
            "structural_rule.reference_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "structural-rule custody identity mismatch",
        )
    return _report(issues)


def validate_operator_reference(
    record: Any,
) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not OperatorCustodyReference:
        _issue(
            issues,
            "operator_reference",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact OperatorCustodyReference required",
        )
        return _report(issues)
    for name in (
        "reference_id",
        "candidate_binding_id",
        "operator_definition_id",
        "grammar_registry_id",
        "proposal_rule_id",
    ):
        _identifier(getattr(record, name), path=f"operator.{name}", issues=issues)
    _text(record.operator_key, path="operator.operator_key", issues=issues)
    for name in (
        "operator_version",
        "grammar_registry_version",
        "proposal_rule_version",
    ):
        _version(getattr(record, name), path=f"operator.{name}", issues=issues)
    for name in ("source_span_ids", "phase_trail_ids", "application_ids"):
        values = _tuple(
            getattr(record, name),
            path=f"operator.{name}",
            issues=issues,
            nonempty=True,
        )
        for index, value in enumerate(values):
            _identifier(value, path=f"operator.{name}[{index}]", issues=issues)
        _unique(values, path=f"operator.{name}", issues=issues)
    _schema(record.schema_version, path="operator.schema_version", issues=issues)
    try:
        expected = expected_operator_reference_id(record)
    except Exception:
        expected = None
    if record.reference_id != expected:
        _issue(
            issues,
            "operator.reference_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "operator custody identity mismatch",
        )
    return _report(issues)


def validate_registry_resource_reference(
    record: Any,
) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not RegistryResourceCustodyReference:
        _issue(
            issues,
            "registry_resource_reference",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact RegistryResourceCustodyReference required",
        )
        return _report(issues)
    _identifier(record.reference_id, path="resource.reference_id", issues=issues)
    if not isinstance(record.resource_kind, RegistryResourceKind):
        _issue(
            issues,
            "resource.resource_kind",
            PredecessorCustodyValidationCode.INVALID_ENUM,
            "RegistryResourceKind required",
        )
    _identifier(record.resource_id, path="resource.resource_id", issues=issues)
    _text(record.resource_key, path="resource.resource_key", issues=issues)
    _version(record.resource_version, path="resource.resource_version", issues=issues)
    _identifier(
        record.registry_snapshot_id,
        path="resource.registry_snapshot_id",
        issues=issues,
    )
    for name in (
        "source_candidate_ids",
        "parent_resource_ids",
        "relation_reference_ids",
    ):
        values = _tuple(
            getattr(record, name),
            path=f"resource.{name}",
            issues=issues,
            nonempty=(name == "source_candidate_ids"),
        )
        for index, value in enumerate(values):
            _identifier(value, path=f"resource.{name}[{index}]", issues=issues)
        _unique(values, path=f"resource.{name}", issues=issues)
    _schema(record.schema_version, path="resource.schema_version", issues=issues)
    try:
        expected = expected_registry_resource_reference_id(record)
    except Exception:
        expected = None
    if record.reference_id != expected:
        _issue(
            issues,
            "resource.reference_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "registry-resource custody identity mismatch",
        )
    return _report(issues)


def validate_receipt(record: Any) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not PredecessorCustodyReceipt:
        _issue(
            issues,
            "receipt",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact PredecessorCustodyReceipt required",
        )
        return _report(issues)
    _identifier(record.receipt_id, path="receipt.receipt_id", issues=issues)
    _integer(record.stage_ordinal, path="receipt.stage_ordinal", issues=issues, minimum=1)
    if not isinstance(record.stage, PredecessorCustodyStage):
        _issue(
            issues,
            "receipt.stage",
            PredecessorCustodyValidationCode.INVALID_ENUM,
            "PredecessorCustodyStage required",
        )
    predecessors = _tuple(
        record.predecessor_record_ids,
        path="receipt.predecessor_record_ids",
        issues=issues,
    )
    for index, value in enumerate(predecessors):
        _identifier(value, path=f"receipt.predecessor_record_ids[{index}]", issues=issues)
    _unique(predecessors, path="receipt.predecessor_record_ids", issues=issues)
    for name in ("output_record_id", "source_event_id"):
        _identifier(getattr(record, name), path=f"receipt.{name}", issues=issues)
    _text(
        record.output_schema_version,
        path="receipt.output_schema_version",
        issues=issues,
    )
    _sha256(record.source_sha256, path="receipt.source_sha256", issues=issues)
    _exact_bool(
        record.exact_validation_passed,
        True,
        path="receipt.exact_validation_passed",
        issues=issues,
        code=PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
    )
    _exact_bool(
        record.exact_lineage_preserved,
        True,
        path="receipt.exact_lineage_preserved",
        issues=issues,
        code=PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE,
    )
    _exact_bool(
        record.generated_substitute_ancestry_used,
        False,
        path="receipt.generated_substitute_ancestry_used",
        issues=issues,
        code=PredecessorCustodyValidationCode.GENERATED_SUBSTITUTE_ANCESTRY,
    )
    for name in _FALSE_FIELDS:
        _exact_bool(
            getattr(record, name),
            False,
            path=f"receipt.{name}",
            issues=issues,
        )
    _schema(record.schema_version, path="receipt.schema_version", issues=issues)
    try:
        expected = expected_receipt_id(record)
    except Exception:
        expected = None
    if record.receipt_id != expected:
        _issue(
            issues,
            "receipt.receipt_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "receipt identity mismatch",
        )
    return _report(issues)


def _extend(
    issues: list[PredecessorCustodyValidationIssue],
    report: PredecessorCustodyValidationReport,
    prefix: str,
) -> None:
    for item in report.issues:
        issues.append(
            PredecessorCustodyValidationIssue(
                path=f"{prefix}.{item.path}",
                code=item.code,
                detail=item.detail,
            )
        )



def _validate_provenance_39c(record: Any) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not CandidateMeaningProvenance:
        _issue(issues, "provenance", PredecessorCustodyValidationCode.TYPE_MISMATCH, "exact CandidateMeaningProvenance required")
        return _report(issues)
    for name in (
        "provenance_id", "source_event_id", "input_event_id", "root_source_span_id",
        "projection_id", "structural_result_id", "structural_set_id",
        "slice37_result_id", "slice37_registry_snapshot_id", "slice38_result_id",
        "slice38_registry_snapshot_id", "compatibility_registry_snapshot_id",
    ):
        _identifier(getattr(record, name), path=f"provenance.{name}", issues=issues)
    _sha256(record.source_sha256, path="provenance.source_sha256", issues=issues)
    tuple_fields = (
        "source_span_ids", "structural_candidate_ids", "structural_ancestry_ids",
        "constrained_trail_ids", "phase_trail_ids", "operator_graph_ids",
        "operator_node_ids", "operator_definition_ids", "scope_occurrence_ids",
        "attachment_candidate_ids", "reference_analysis_ids", "reference_candidate_ids",
        "concept_candidate_proposal_ids", "sense_candidate_proposal_ids",
        "action_predicate_candidate_ids", "role_layout_candidate_ids",
        "capability_reference_candidate_ids", "predecessor_receipt_ids",
    )
    required = frozenset((
        "source_span_ids", "structural_candidate_ids", "structural_ancestry_ids",
        "constrained_trail_ids", "phase_trail_ids", "operator_graph_ids",
        "operator_node_ids", "operator_definition_ids",
        "concept_candidate_proposal_ids", "sense_candidate_proposal_ids",
        "action_predicate_candidate_ids", "role_layout_candidate_ids",
        "predecessor_receipt_ids",
    ))
    for name in tuple_fields:
        values = _tuple(getattr(record, name), path=f"provenance.{name}", issues=issues, nonempty=name in required)
        for index, value in enumerate(values):
            _identifier(value, path=f"provenance.{name}[{index}]", issues=issues)
        _unique(values, path=f"provenance.{name}", issues=issues)
    for name in ("operator_keys_and_versions", "concept_ids_and_versions", "sense_ids_and_versions"):
        values = _tuple(getattr(record, name), path=f"provenance.{name}", issues=issues, nonempty=True)
        for index, pair in enumerate(values):
            if type(pair) is not tuple or len(pair) != 2:
                _issue(issues, f"provenance.{name}[{index}]", PredecessorCustodyValidationCode.TYPE_MISMATCH, "exact two-item identity/version pair required")
                continue
            if name == "operator_keys_and_versions":
                _text(pair[0], path=f"provenance.{name}[{index}][0]", issues=issues)
            else:
                _identifier(pair[0], path=f"provenance.{name}[{index}][0]", issues=issues)
            _version(pair[1], path=f"provenance.{name}[{index}][1]", issues=issues)
        _unique(values, path=f"provenance.{name}", issues=issues)
    for name in (
        "source_ancestry_preserved", "operator_ancestry_preserved",
        "phase_trail_ancestry_preserved", "scope_attachment_ancestry_preserved",
        "registry_snapshots_preserved", "candidate_only",
    ):
        _exact_bool(getattr(record, name), True, path=f"provenance.{name}", issues=issues, code=PredecessorCustodyValidationCode.PROVENANCE_MISMATCH)
    for name in ("selected_ancestry", "external_resource_loaded"):
        _exact_bool(getattr(record, name), False, path=f"provenance.{name}", issues=issues, code=PredecessorCustodyValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED)
    if record.provenance_id != expected_provenance_id(record):
        _issue(issues, "provenance.provenance_id", PredecessorCustodyValidationCode.IDENTITY_MISMATCH, "provenance identity mismatch")
    return _report(issues)


def validate_custody(record: Any) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not CandidateMeaningPredecessorCustody:
        _issue(
            issues,
            "custody",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact CandidateMeaningPredecessorCustody required",
        )
        return _report(issues)
    _identifier(record.custody_id, path="custody.custody_id", issues=issues)
    _identifier(record.lineage_id, path="custody.lineage_id", issues=issues)
    _extend(issues, _validate_provenance_39c(record.provenance), "custody")
    _extend(
        issues,
        validate_construction_profile(record.construction_profile),
        "custody",
    )
    spans = _tuple(
        record.source_span_references,
        path="custody.source_span_references",
        issues=issues,
        nonempty=True,
    )
    rules = _tuple(
        record.structural_rule_references,
        path="custody.structural_rule_references",
        issues=issues,
        nonempty=True,
    )
    operators = _tuple(
        record.operator_references,
        path="custody.operator_references",
        issues=issues,
        nonempty=True,
    )
    resources = _tuple(
        record.registry_resource_references,
        path="custody.registry_resource_references",
        issues=issues,
        nonempty=True,
    )
    receipts = _tuple(
        record.stage_receipts,
        path="custody.stage_receipts",
        issues=issues,
        nonempty=True,
    )
    results = _tuple(
        record.predecessor_result_ids,
        path="custody.predecessor_result_ids",
        issues=issues,
        nonempty=True,
    )
    for index, item in enumerate(spans):
        _extend(issues, validate_source_span_reference(item), f"custody.spans[{index}]")
    for index, item in enumerate(rules):
        _extend(
            issues,
            validate_structural_rule_reference(item),
            f"custody.rules[{index}]",
        )
    for index, item in enumerate(operators):
        _extend(
            issues,
            validate_operator_reference(item),
            f"custody.operators[{index}]",
        )
    for index, item in enumerate(resources):
        _extend(
            issues,
            validate_registry_resource_reference(item),
            f"custody.resources[{index}]",
        )
    for index, item in enumerate(receipts):
        _extend(issues, validate_receipt(item), f"custody.receipts[{index}]")
    for values, path, key in (
        (spans, "custody.source_span_references", lambda item: item.span_id),
        (rules, "custody.structural_rule_references", lambda item: item.trace_id),
        (operators, "custody.operator_references", lambda item: item.candidate_binding_id),
        (
            resources,
            "custody.registry_resource_references",
            lambda item: (item.resource_kind, item.resource_id),
        ),
        (receipts, "custody.stage_receipts", lambda item: item.receipt_id),
        (results, "custody.predecessor_result_ids", lambda item: item),
    ):
        try:
            keys = tuple(key(item) for item in values)
        except Exception:
            keys = ()
        _unique(keys, path=path, issues=issues)
    if spans != tuple(
        sorted(
            spans,
            key=lambda item: (
                item.code_point_start,
                item.code_point_end,
                item.span_id,
            ),
        )
    ):
        _issue(
            issues,
            "custody.source_span_references",
            PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
            "source spans must be in canonical source order",
        )
    if rules != tuple(sorted(rules, key=lambda item: item.trace_id)):
        _issue(
            issues,
            "custody.structural_rule_references",
            PredecessorCustodyValidationCode.STRUCTURAL_ANCESTRY_MISMATCH,
            "structural rule references must be canonically ordered",
        )
    if operators != tuple(
        sorted(operators, key=lambda item: item.candidate_binding_id)
    ):
        _issue(
            issues,
            "custody.operator_references",
            PredecessorCustodyValidationCode.OPERATOR_ANCESTRY_MISMATCH,
            "operator references must be canonically ordered",
        )
    if resources != tuple(
        sorted(resources, key=lambda item: (item.resource_kind.value, item.resource_id))
    ):
        _issue(
            issues,
            "custody.registry_resource_references",
            PredecessorCustodyValidationCode.REGISTRY_SNAPSHOT_MISMATCH,
            "registry resources must be canonically ordered",
        )
    expected_stages = tuple(PredecessorCustodyStage)
    if tuple(item.stage for item in receipts) != expected_stages:
        _issue(
            issues,
            "custody.stage_receipts",
            PredecessorCustodyValidationCode.RECEIPT_CHAIN_MISMATCH,
            "exact eight-stage custody chain required",
        )
    if tuple(item.stage_ordinal for item in receipts) != tuple(
        range(1, len(expected_stages) + 1)
    ):
        _issue(
            issues,
            "custody.stage_receipts",
            PredecessorCustodyValidationCode.RECEIPT_CHAIN_MISMATCH,
            "receipt ordinals must be consecutive",
        )
    for index, receipt in enumerate(receipts):
        expected_predecessors = (
            ()
            if index == 0
            else (
                receipts[index - 1].output_record_id,
                receipts[index - 1].receipt_id,
            )
        )
        if receipt.predecessor_record_ids != expected_predecessors:
            _issue(
                issues,
                f"custody.stage_receipts[{index}].predecessor_record_ids",
                PredecessorCustodyValidationCode.RECEIPT_CHAIN_MISMATCH,
                "receipt does not preserve exact prior output and receipt",
            )
    if results != tuple(item.output_record_id for item in receipts):
        _issue(
            issues,
            "custody.predecessor_result_ids",
            PredecessorCustodyValidationCode.RECEIPT_CHAIN_MISMATCH,
            "result inventory must equal receipt output inventory",
        )
    if record.provenance.predecessor_receipt_ids != tuple(
        item.receipt_id for item in receipts
    ):
        _issue(
            issues,
            "custody.provenance.predecessor_receipt_ids",
            PredecessorCustodyValidationCode.PROVENANCE_MISMATCH,
            "provenance receipt inventory mismatch",
        )
    if record.provenance.source_span_ids != tuple(item.span_id for item in spans):
        _issue(
            issues,
            "custody.provenance.source_span_ids",
            PredecessorCustodyValidationCode.PROVENANCE_MISMATCH,
            "provenance source spans do not match verified span references",
        )
    roots = tuple(item for item in spans if item.is_root_span)
    if len(roots) != 1 or roots[0].span_id != record.provenance.root_source_span_id:
        _issue(issues, "custody.source_span_references", PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED, "exactly one reconstructed root span must match provenance")
    operator_ids = tuple(item.operator_definition_id for item in operators)
    operator_keys_versions = tuple(
        (item.operator_key, item.operator_version) for item in operators
    )
    if frozenset(record.provenance.operator_definition_ids) != frozenset(operator_ids):
        _issue(
            issues,
            "custody.provenance.operator_definition_ids",
            PredecessorCustodyValidationCode.PROVENANCE_MISMATCH,
            "operator definition ancestry mismatch",
        )
    if frozenset(record.provenance.operator_keys_and_versions) != frozenset(operator_keys_versions):
        _issue(
            issues,
            "custody.provenance.operator_keys_and_versions",
            PredecessorCustodyValidationCode.PROVENANCE_MISMATCH,
            "operator key/version ancestry mismatch",
        )
    if record.provenance.schema_version == "":
        _issue(
            issues,
            "custody.construction_profile",
            PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH,
            "provenance schema version is required",
        )
    resource_kinds = frozenset(item.resource_kind for item in resources)
    if not _REQUIRED_RESOURCE_KINDS.issubset(resource_kinds):
        _issue(
            issues,
            "custody.registry_resource_references",
            PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE,
            "complete concept/sense/action/predicate/role/frame/effect custody required; capability ancestry may be explicitly empty",
        )
    expected_lineage = expected_lineage_id(
        source_event_id=record.provenance.source_event_id,
        source_sha256=record.provenance.source_sha256,
        slice37_registry_snapshot_id=(
            record.provenance.slice37_registry_snapshot_id
        ),
        slice38_registry_snapshot_id=(
            record.provenance.slice38_registry_snapshot_id
        ),
        compatibility_registry_snapshot_id=(
            record.provenance.compatibility_registry_snapshot_id
        ),
        construction_profile_id=record.construction_profile.profile_id,
        construction_profile_version=record.construction_profile.profile_version,
    )
    if record.lineage_id != expected_lineage:
        _issue(
            issues,
            "custody.lineage_id",
            PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE,
            "lineage identity does not match exact source and snapshots",
        )
    for name in (
        "exact_source_event_match",
        "exact_source_checksum_match",
        "exact_source_spans_verified",
        "exact_structural_ancestry_verified",
        "exact_operator_ancestry_verified",
        "exact_phase_trail_ancestry_verified",
        "exact_scope_attachment_reference_ancestry_verified",
        "exact_registry_snapshots_verified",
        "exact_resource_versions_verified",
        "zero_one_many_preserved",
    ):
        _exact_bool(
            getattr(record, name),
            True,
            path=f"custody.{name}",
            issues=issues,
            code=PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
        )
    _exact_bool(
        record.cross_lineage_candidate_merge_performed,
        False,
        path="custody.cross_lineage_candidate_merge_performed",
        issues=issues,
        code=PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE,
    )
    _exact_bool(
        record.generated_substitute_ancestry_used,
        False,
        path="custody.generated_substitute_ancestry_used",
        issues=issues,
        code=PredecessorCustodyValidationCode.GENERATED_SUBSTITUTE_ANCESTRY,
    )
    for name in _FALSE_FIELDS:
        _exact_bool(
            getattr(record, name),
            False,
            path=f"custody.{name}",
            issues=issues,
        )
    if record.digest_algorithm != DIGEST_ALGORITHM:
        _issue(
            issues,
            "custody.digest_algorithm",
            PredecessorCustodyValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED,
            "SHA-256 is the only admitted custody digest",
        )
    _sha256(record.canonical_digest, path="custody.canonical_digest", issues=issues)
    _schema(record.schema_version, path="custody.schema_version", issues=issues)
    try:
        digest = expected_custody_digest(record)
        custody_id = expected_custody_id(record)
    except Exception:
        digest = None
        custody_id = None
    if record.canonical_digest != digest:
        _issue(
            issues,
            "custody.canonical_digest",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "canonical custody digest mismatch",
        )
    if record.custody_id != custody_id:
        _issue(
            issues,
            "custody.custody_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "custody identity mismatch",
        )
    return _report(issues)


def validate_binding_result(
    record: Any,
) -> PredecessorCustodyValidationReport:
    issues: list[PredecessorCustodyValidationIssue] = []
    if type(record) is not CandidateMeaningPredecessorBindingResult:
        _issue(
            issues,
            "binding_result",
            PredecessorCustodyValidationCode.TYPE_MISMATCH,
            "exact CandidateMeaningPredecessorBindingResult required",
        )
        return _report(issues)
    _identifier(record.result_id, path="binding_result.result_id", issues=issues)
    if not isinstance(record.status, PredecessorCustodyStatus):
        _issue(
            issues,
            "binding_result.status",
            PredecessorCustodyValidationCode.INVALID_ENUM,
            "PredecessorCustodyStatus required",
        )
    _text(record.reason_code, path="binding_result.reason_code", issues=issues)
    issue_tuple = _tuple(
        record.issues,
        path="binding_result.issues",
        issues=issues,
    )
    for item in issue_tuple:
        if type(item) is not PredecessorCustodyValidationIssue:
            _issue(
                issues,
                "binding_result.issues",
                PredecessorCustodyValidationCode.TYPE_MISMATCH,
                "exact validation issues required",
            )
            break
    for name in (
        "source_span_reference_count",
        "structural_rule_reference_count",
        "operator_reference_count",
        "registry_resource_reference_count",
        "stage_receipt_count",
    ):
        _integer(getattr(record, name), path=f"binding_result.{name}", issues=issues)
    for name in _FALSE_FIELDS + (
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "semantic_similarity_used",
    ):
        _exact_bool(
            getattr(record, name),
            False,
            path=f"binding_result.{name}",
            issues=issues,
        )
    if record.status is PredecessorCustodyStatus.BOUND:
        if record.custody is None:
            _issue(
                issues,
                "binding_result.custody",
                PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE,
                "BOUND result requires custody",
            )
        else:
            _extend(issues, validate_custody(record.custody), "binding_result")
            if record.source_event_id != record.custody.provenance.source_event_id:
                _issue(
                    issues,
                    "binding_result.source_event_id",
                    PredecessorCustodyValidationCode.SOURCE_EVENT_MISMATCH,
                    "result source event differs from custody",
                )
            if record.source_sha256 != record.custody.provenance.source_sha256:
                _issue(
                    issues,
                    "binding_result.source_sha256",
                    PredecessorCustodyValidationCode.SOURCE_CHECKSUM_MISMATCH,
                    "result source checksum differs from custody",
                )
            expected_counts = (
                len(record.custody.source_span_references),
                len(record.custody.structural_rule_references),
                len(record.custody.operator_references),
                len(record.custody.registry_resource_references),
                len(record.custody.stage_receipts),
            )
            actual_counts = (
                record.source_span_reference_count,
                record.structural_rule_reference_count,
                record.operator_reference_count,
                record.registry_resource_reference_count,
                record.stage_receipt_count,
            )
            if actual_counts != expected_counts:
                _issue(
                    issues,
                    "binding_result.counts",
                    PredecessorCustodyValidationCode.PROVENANCE_MISMATCH,
                    "binding-result counts do not match custody",
                )
        if issue_tuple:
            _issue(
                issues,
                "binding_result.issues",
                PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
                "BOUND result must have zero issues",
            )
    else:
        if record.custody is not None:
            _issue(
                issues,
                "binding_result.custody",
                PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
                "rejected or empty result must not carry custody",
            )
        if record.status is PredecessorCustodyStatus.PREDECESSOR_REJECTED and not issue_tuple:
            _issue(
                issues,
                "binding_result.issues",
                PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
                "rejected result must preserve failure issues",
            )
    _schema(record.schema_version, path="binding_result.schema_version", issues=issues)
    try:
        expected = expected_binding_result_id(record)
    except Exception:
        expected = None
    if record.result_id != expected:
        _issue(
            issues,
            "binding_result.result_id",
            PredecessorCustodyValidationCode.IDENTITY_MISMATCH,
            "binding-result identity mismatch",
        )
    return _report(issues)


def assert_valid_custody(
    record: CandidateMeaningPredecessorCustody,
) -> CandidateMeaningPredecessorCustody:
    report = validate_custody(record)
    if not report.ok:
        from .schema import PredecessorCustodyValidationError
        raise PredecessorCustodyValidationError(report)
    return record


def assert_valid_binding_result(
    record: CandidateMeaningPredecessorBindingResult,
) -> CandidateMeaningPredecessorBindingResult:
    report = validate_binding_result(record)
    if not report.ok:
        from .schema import PredecessorCustodyValidationError
        raise PredecessorCustodyValidationError(report)
    return record


__all__ = (
    "assert_valid_binding_result",
    "assert_valid_custody",
    "validate_binding_result",
    "validate_construction_profile",
    "validate_custody",
    "validate_operator_reference",
    "validate_receipt",
    "validate_registry_resource_reference",
    "validate_source_span_reference",
    "validate_structural_rule_reference",
)
