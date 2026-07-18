"""Deterministic validation for Slice 39G candidate-manifest integration."""

from __future__ import annotations

from collections import Counter

from ...meaning_structure_manifest import (
    ExternalAuthorityReferenceRecord,
    MeaningStructureManifestV1,
    SemanticLifecycleState,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.validation import validate_manifest
from .authority import (
    SLICE39G_ADAPTER_DECISION,
    SLICE39G_ADAPTER_DECISION_REASONS,
    SLICE39G_COMPANION_VERSION,
    SLICE39G_PERMANENT_BOUNDARIES,
    SLICE39G_PROFILE_VERSION,
    SLICE39G_PROHIBITED_AUTHORITY,
    SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS,
    SLICE39G_REQUIRED_PATH,
    SLICE39G_SCHEMA_VERSION,
)
from .identity import (
    expected_alternative_relationship_id,
    expected_companion_id,
    expected_limitation_reference_id,
    expected_profile_id,
    expected_provenance_reference_id,
    expected_result_digest,
    expected_result_id,
    expected_trace_reference_id,
)
from .schema import (
    CandidateAlternativeRelationshipV1,
    CandidateConstructionTraceReferenceV1,
    CandidateLimitationReferenceV1,
    CandidateMeaningManifestCompanionV1,
    CandidateProvenanceReferenceV1,
    ManifestCandidateIntegrationProfile,
    ManifestCandidateIntegrationResult,
    ManifestCandidateIntegrationStatus,
    ManifestCandidateIntegrationValidationCode,
    ManifestCandidateIntegrationValidationError,
    ManifestCandidateIntegrationValidationIssue,
    ManifestCandidateIntegrationValidationReport,
)


def _issue(
    path: str,
    code: ManifestCandidateIntegrationValidationCode,
    detail: str,
) -> ManifestCandidateIntegrationValidationIssue:
    return ManifestCandidateIntegrationValidationIssue(
        path=path,
        code=code,
        detail=detail,
    )


def validate_profile(
    profile: object,
) -> ManifestCandidateIntegrationValidationReport:
    issues: list[ManifestCandidateIntegrationValidationIssue] = []
    if type(profile) is not ManifestCandidateIntegrationProfile:
        return ManifestCandidateIntegrationValidationReport(
            (
                _issue(
                    "profile",
                    ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                    "expected ManifestCandidateIntegrationProfile",
                ),
            )
        )
    expected_true = (
        "explicitly_invoked",
        "exact_slice39f_result_required",
        "exact_msm_v1_schema_required",
        "versioned_companion_required",
        "candidate_side_only",
        "offline_only",
        "standard_library_only",
        "read_only",
        "deterministic",
        "in_memory_only",
        "source_preserving",
        "fail_closed",
    )
    expected_false = (
        "existing_msm_schema_modification_allowed",
        "automatic_migration_allowed",
        "gate_outcome_allowed",
        "selected_meaning_allowed",
        "governed_result_allowed",
        "outward_meaning_allowed",
        "expression_validation_delivery_allowed",
        "bootstrap_integration_allowed",
        "slice39_closeout_allowed",
        "truth_evidence_permission_allowed",
        "route_action_memory_rendering_delivery_allowed",
    )
    for name in expected_true:
        if getattr(profile, name) is not True:
            issues.append(
                _issue(
                    f"profile.{name}",
                    ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                    "required profile flag must be true",
                )
            )
    for name in expected_false:
        if getattr(profile, name) is not False:
            issues.append(
                _issue(
                    f"profile.{name}",
                    ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                    "prohibited profile flag must be false",
                )
            )
    if profile.profile_version != SLICE39G_PROFILE_VERSION:
        issues.append(
            _issue(
                "profile.profile_version",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "profile version mismatch",
            )
        )
    if profile.adapter_decision != SLICE39G_ADAPTER_DECISION:
        issues.append(
            _issue(
                "profile.adapter_decision",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "adapter decision mismatch",
            )
        )
    if profile.adapter_decision_reasons != SLICE39G_ADAPTER_DECISION_REASONS:
        issues.append(
            _issue(
                "profile.adapter_decision_reasons",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "adapter decision reasons mismatch",
            )
        )
    if profile.required_path != SLICE39G_REQUIRED_PATH:
        issues.append(
            _issue(
                "profile.required_path",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "required path mismatch",
            )
        )
    if (
        profile.required_empty_manifest_sections
        != SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS
    ):
        issues.append(
            _issue(
                "profile.required_empty_manifest_sections",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "required empty sections mismatch",
            )
        )
    if profile.permanent_boundaries != SLICE39G_PERMANENT_BOUNDARIES:
        issues.append(
            _issue(
                "profile.permanent_boundaries",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "permanent boundary inventory mismatch",
            )
        )
    if profile.prohibited_authority != SLICE39G_PROHIBITED_AUTHORITY:
        issues.append(
            _issue(
                "profile.prohibited_authority",
                ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
                "prohibited authority inventory mismatch",
            )
        )
    if profile.schema_version != SLICE39G_SCHEMA_VERSION:
        issues.append(
            _issue(
                "profile.schema_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "schema version mismatch",
            )
        )
    if profile.profile_id != expected_profile_id(profile):
        issues.append(
            _issue(
                "profile.profile_id",
                ManifestCandidateIntegrationValidationCode.IDENTITY_MISMATCH,
                "profile identity mismatch",
            )
        )
    return ManifestCandidateIntegrationValidationReport(tuple(issues))


def _validate_trace_reference(
    record: object,
    index: int,
) -> tuple[ManifestCandidateIntegrationValidationIssue, ...]:
    if type(record) is not CandidateConstructionTraceReferenceV1:
        return (
            _issue(
                f"construction_trace_references[{index}]",
                ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                "expected CandidateConstructionTraceReferenceV1",
            ),
        )
    issues = []
    if record.trace_reference_id != expected_trace_reference_id(record):
        issues.append(
            _issue(
                f"construction_trace_references[{index}].trace_reference_id",
                ManifestCandidateIntegrationValidationCode.IDENTITY_MISMATCH,
                "trace reference identity mismatch",
            )
        )
    if (
        record.deterministic_position < 1
        or record.duplicate_occurrence_count < 1
    ):
        issues.append(
            _issue(
                f"construction_trace_references[{index}]",
                ManifestCandidateIntegrationValidationCode.COUNT_MISMATCH,
                "positions and duplicate counts must be positive",
            )
        )
    for name in (
        "exact_typed_predecessors_verified",
        "exact_ancestry_verified",
        "exact_snapshots_verified",
        "source_preserved",
    ):
        if getattr(record, name) is not True:
            issues.append(
                _issue(
                    f"construction_trace_references[{index}].{name}",
                    ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                    "exact custody flag must be true",
                )
            )
    if record.schema_version != SLICE39G_SCHEMA_VERSION:
        issues.append(
            _issue(
                f"construction_trace_references[{index}].schema_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "schema version mismatch",
            )
        )
    return tuple(issues)


def _validate_provenance_reference(
    record: object,
    index: int,
) -> tuple[ManifestCandidateIntegrationValidationIssue, ...]:
    if type(record) is not CandidateProvenanceReferenceV1:
        return (
            _issue(
                f"provenance_references[{index}]",
                ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                "expected CandidateProvenanceReferenceV1",
            ),
        )
    issues = []
    if (
        record.provenance_reference_id
        != expected_provenance_reference_id(record)
    ):
        issues.append(
            _issue(
                f"provenance_references[{index}].provenance_reference_id",
                ManifestCandidateIntegrationValidationCode.IDENTITY_MISMATCH,
                "provenance reference identity mismatch",
            )
        )
    for name in (
        "exact_ancestry_verified",
        "exact_snapshots_verified",
        "source_preserved",
    ):
        if getattr(record, name) is not True:
            issues.append(
                _issue(
                    f"provenance_references[{index}].{name}",
                    ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                    "exact custody flag must be true",
                )
            )
    for name in (
        "predecessor_result_ids",
        "predecessor_receipt_ids",
        "source_span_reference_ids",
        "structural_rule_reference_ids",
        "operator_reference_ids",
        "registry_resource_reference_ids",
    ):
        value = getattr(record, name)
        if type(value) is not tuple or len(value) != len(set(value)):
            issues.append(
                _issue(
                    f"provenance_references[{index}].{name}",
                    ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                    "exact unique tuple required",
                )
            )
    if record.schema_version != SLICE39G_SCHEMA_VERSION:
        issues.append(
            _issue(
                f"provenance_references[{index}].schema_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "schema version mismatch",
            )
        )
    return tuple(issues)


def _validate_limitation_reference(
    record: object,
    index: int,
) -> tuple[ManifestCandidateIntegrationValidationIssue, ...]:
    if type(record) is not CandidateLimitationReferenceV1:
        return (
            _issue(
                f"limitation_references[{index}]",
                ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                "expected CandidateLimitationReferenceV1",
            ),
        )
    issues = []
    if (
        record.limitation_reference_id
        != expected_limitation_reference_id(record)
    ):
        issues.append(
            _issue(
                f"limitation_references[{index}].limitation_reference_id",
                ManifestCandidateIntegrationValidationCode.IDENTITY_MISMATCH,
                "limitation reference identity mismatch",
            )
        )
    if record.candidate_only is not True:
        issues.append(
            _issue(
                f"limitation_references[{index}].candidate_only",
                ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                "limitation custody must remain candidate only",
            )
        )
    for name in (
        "clarification_required_created",
        "ambiguity_outcome_created",
        "refusal_created",
    ):
        if getattr(record, name) is not False:
            issues.append(
                _issue(
                    f"limitation_references[{index}].{name}",
                    ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                    "limitation custody cannot create a gate outcome",
                )
            )
    if record.schema_version != SLICE39G_SCHEMA_VERSION:
        issues.append(
            _issue(
                f"limitation_references[{index}].schema_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "schema version mismatch",
            )
        )
    return tuple(issues)


def _validate_alternative_relationship(
    record: object,
    index: int,
) -> tuple[ManifestCandidateIntegrationValidationIssue, ...]:
    if type(record) is not CandidateAlternativeRelationshipV1:
        return (
            _issue(
                f"alternative_relationships[{index}]",
                ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                "expected CandidateAlternativeRelationshipV1",
            ),
        )
    issues = []
    if record.relationship_id != expected_alternative_relationship_id(record):
        issues.append(
            _issue(
                f"alternative_relationships[{index}].relationship_id",
                ManifestCandidateIntegrationValidationCode.IDENTITY_MISMATCH,
                "alternative relationship identity mismatch",
            )
        )
    if record.candidate_only is not True:
        issues.append(
            _issue(
                f"alternative_relationships[{index}].candidate_only",
                ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                "alternative relationship must remain candidate only",
            )
        )
    for name in (
        "ranking_assigned",
        "preferred_candidate_assigned",
        "selected_alternative",
        "ambiguous_gate_disposition_created",
    ):
        if getattr(record, name) is not False:
            issues.append(
                _issue(
                    f"alternative_relationships[{index}].{name}",
                    ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                    "alternative relationship cannot select or resolve ambiguity",
                )
            )
    if record.schema_version != SLICE39G_SCHEMA_VERSION:
        issues.append(
            _issue(
                f"alternative_relationships[{index}].schema_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "schema version mismatch",
            )
        )
    return tuple(issues)


def _validate_companion(
    record: object,
    index: int,
) -> tuple[ManifestCandidateIntegrationValidationIssue, ...]:
    if type(record) is not CandidateMeaningManifestCompanionV1:
        return (
            _issue(
                f"companions[{index}]",
                ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                "expected CandidateMeaningManifestCompanionV1",
            ),
        )
    issues = []
    if record.companion_id != expected_companion_id(record):
        issues.append(
            _issue(
                f"companions[{index}].companion_id",
                ManifestCandidateIntegrationValidationCode.IDENTITY_MISMATCH,
                "companion identity mismatch",
            )
        )
    if record.companion_version != SLICE39G_COMPANION_VERSION:
        issues.append(
            _issue(
                f"companions[{index}].companion_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "companion version mismatch",
            )
        )
    for name in (
        "exact_adapter",
        "lossless_custody",
        "candidate_side_only",
    ):
        if getattr(record, name) is not True:
            issues.append(
                _issue(
                    f"companions[{index}].{name}",
                    ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                    "required companion custody flag must be true",
                )
            )
    for name in ("selected_meaning_created", "gate_outcome_created"):
        if getattr(record, name) is not False:
            issues.append(
                _issue(
                    f"companions[{index}].{name}",
                    ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                    "companion cannot create downstream authority",
                )
            )
    if record.schema_version != SLICE39G_SCHEMA_VERSION:
        issues.append(
            _issue(
                f"companions[{index}].schema_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "schema version mismatch",
            )
        )
    return tuple(issues)


def validate_integration_result(
    record: object,
) -> ManifestCandidateIntegrationValidationReport:
    issues: list[ManifestCandidateIntegrationValidationIssue] = []
    if type(record) is not ManifestCandidateIntegrationResult:
        return ManifestCandidateIntegrationValidationReport(
            (
                _issue(
                    "result",
                    ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                    "expected ManifestCandidateIntegrationResult",
                ),
            )
        )
    issues.extend(validate_profile(record.profile).issues)
    if record.schema_version != SLICE39G_SCHEMA_VERSION:
        issues.append(
            _issue(
                "result.schema_version",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "schema version mismatch",
            )
        )
    if record.status is ManifestCandidateIntegrationStatus.REJECTED:
        if record.manifest is not None:
            issues.append(
                _issue(
                    "result.manifest",
                    ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                    "rejected result cannot contain a manifest",
                )
            )
        for name in (
            "companions",
            "construction_trace_references",
            "provenance_references",
            "limitation_references",
            "alternative_relationships",
        ):
            if getattr(record, name):
                issues.append(
                    _issue(
                        f"result.{name}",
                        ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                        "rejected result cannot contain integrated custody records",
                    )
                )
        if not record.issues:
            issues.append(
                _issue(
                    "result.issues",
                    ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                    "rejected result requires explicit issues",
                )
            )
    else:
        if record.issues:
            issues.append(
                _issue(
                    "result.issues",
                    ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                    "accepted result cannot carry rejection issues",
                )
            )

    manifest = record.manifest
    if manifest is not None:
        if type(manifest) is not MeaningStructureManifestV1:
            issues.append(
                _issue(
                    "result.manifest",
                    ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
                    "expected MeaningStructureManifestV1",
                )
            )
        else:
            manifest_report = validate_manifest(manifest)
            if not manifest_report.ok:
                issues.append(
                    _issue(
                        "result.manifest",
                        ManifestCandidateIntegrationValidationCode.MANIFEST_INVALID,
                        "MSM-v1 validation failed",
                    )
                )
            for name in SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS:
                if getattr(manifest, name):
                    issues.append(
                        _issue(
                            f"result.manifest.{name}",
                            ManifestCandidateIntegrationValidationCode.REQUIRED_SECTION_NOT_EMPTY,
                            "Slice 39G requires this manifest section to remain empty",
                        )
                    )
    elif record.status is ManifestCandidateIntegrationStatus.INTEGRATED:
        issues.append(
            _issue(
                "result.manifest",
                ManifestCandidateIntegrationValidationCode.MANIFEST_INVALID,
                "integrated status requires a manifest",
            )
        )

    for index, item in enumerate(record.construction_trace_references):
        issues.extend(_validate_trace_reference(item, index))
    for index, item in enumerate(record.provenance_references):
        issues.extend(_validate_provenance_reference(item, index))
    for index, item in enumerate(record.limitation_references):
        issues.extend(_validate_limitation_reference(item, index))
    for index, item in enumerate(record.alternative_relationships):
        issues.extend(_validate_alternative_relationship(item, index))
    for index, item in enumerate(record.companions):
        issues.extend(_validate_companion(item, index))

    if manifest is not None:
        candidate_ids = {item.record_id for item in manifest.candidate_meanings}
        companion_candidate_ids = {
            item.manifest_candidate_record_id for item in record.companions
        }
        if record.status is ManifestCandidateIntegrationStatus.INTEGRATED:
            if candidate_ids != companion_candidate_ids:
                issues.append(
                    _issue(
                        "result.companions",
                        ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                        "every manifest candidate requires exactly one companion",
                    )
                )
            expected_count = len(manifest.candidate_meanings)
            if not (
                len(record.companions)
                == len(record.construction_trace_references)
                == len(record.provenance_references)
                == len(record.limitation_references)
                == expected_count
                == record.input_candidate_count
                == record.manifest_candidate_count
            ):
                issues.append(
                    _issue(
                        "result.counts",
                        ManifestCandidateIntegrationValidationCode.COUNT_MISMATCH,
                        "candidate, companion, trace, provenance and limitation counts must match",
                    )
                )
        if record.status is ManifestCandidateIntegrationStatus.ZERO_CANDIDATES:
            if manifest.candidate_meanings or record.companions:
                issues.append(
                    _issue(
                        "result.zero_candidates",
                        ManifestCandidateIntegrationValidationCode.COUNT_MISMATCH,
                        "zero-candidate manifest must contain no candidate records",
                    )
                )

        trace_ids = {
            item.trace_reference_id
            for item in record.construction_trace_references
        }
        provenance_ids = {
            item.provenance_reference_id for item in record.provenance_references
        }
        limitation_ids = {
            item.limitation_reference_id for item in record.limitation_references
        }
        relationship_ids = {
            item.relationship_id for item in record.alternative_relationships
        }
        for index, companion in enumerate(record.companions):
            if companion.construction_trace_reference_id not in trace_ids:
                issues.append(
                    _issue(
                        f"result.companions[{index}].construction_trace_reference_id",
                        ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                        "companion trace reference is unresolved",
                    )
                )
            if companion.provenance_reference_id not in provenance_ids:
                issues.append(
                    _issue(
                        f"result.companions[{index}].provenance_reference_id",
                        ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                        "companion provenance reference is unresolved",
                    )
                )
            if companion.limitation_reference_id not in limitation_ids:
                issues.append(
                    _issue(
                        f"result.companions[{index}].limitation_reference_id",
                        ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                        "companion limitation reference is unresolved",
                    )
                )
            if not set(companion.alternative_relationship_ids).issubset(
                relationship_ids
            ):
                issues.append(
                    _issue(
                        f"result.companions[{index}].alternative_relationship_ids",
                        ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                        "companion alternative relationship is unresolved",
                    )
                )

        external_refs = {
            item.external_object_ref
            for item in manifest.external_authority_references
            if type(item) is ExternalAuthorityReferenceRecord
        }
        required_external_refs = (
            trace_ids | provenance_ids | limitation_ids | relationship_ids
        )
        if external_refs != required_external_refs:
            issues.append(
                _issue(
                    "result.manifest.external_authority_references",
                    ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                    "manifest external-reference custody must exactly match companion references",
                )
            )

        transition_targets = Counter(
            item.to_record_ref
            for item in manifest.semantic_transition_traces
            if type(item) is SemanticTransitionTraceRecord
        )
        for candidate_id in candidate_ids:
            if transition_targets[candidate_id] != 1:
                issues.append(
                    _issue(
                        "result.manifest.semantic_transition_traces",
                        ManifestCandidateIntegrationValidationCode.REFERENCE_MISMATCH,
                        "each candidate requires one construction ancestry trace",
                    )
                )
        for trace in manifest.semantic_transition_traces:
            if trace.to_state is not SemanticLifecycleState.CANDIDATE_MEANING:
                issues.append(
                    _issue(
                        "result.manifest.semantic_transition_traces",
                        ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                        "Slice 39G trace may terminate only at candidate meaning",
                    )
                )

    if record.manifest_candidate_count != (
        len(manifest.candidate_meanings) if manifest is not None else 0
    ):
        issues.append(
            _issue(
                "result.manifest_candidate_count",
                ManifestCandidateIntegrationValidationCode.COUNT_MISMATCH,
                "manifest candidate count mismatch",
            )
        )

    required_true = ("explicitly_invoked", "candidate_side_only")
    if record.status is not ManifestCandidateIntegrationStatus.REJECTED:
        required_true = required_true + ("exact_constructor_result_verified",)
    for name in required_true:
        if getattr(record, name) is not True:
            issues.append(
                _issue(
                    f"result.{name}",
                    ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                    "required integration boundary flag must be true",
                )
            )
    if manifest is not None:
        for name in ("exact_msm_v1_verified", "manifest_integrated"):
            if getattr(record, name) is not True:
                issues.append(
                    _issue(
                        f"result.{name}",
                        ManifestCandidateIntegrationValidationCode.MANIFEST_INVALID,
                        "manifest-backed result requires verified integration",
                    )
                )
    if record.companions:
        for name in ("versioned_companion_used", "lossless_companion_custody"):
            if getattr(record, name) is not True:
                issues.append(
                    _issue(
                        f"result.{name}",
                        ManifestCandidateIntegrationValidationCode.COMPANION_INVALID,
                        "candidate integration requires lossless versioned companion custody",
                    )
                )

    required_false = (
        "existing_msm_schema_modified",
        "automatic_migration_performed",
        "non_selection_outcome_created",
        "selected_governed_meaning_created",
        "governed_result_reference_created",
        "governed_outward_meaning_created",
        "expression_link_created",
        "validation_link_created",
        "delivery_link_created",
        "gate_outcome_created",
        "selected_meaning_created",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "route_created",
        "action_performed",
        "memory_accessed",
        "rendered",
        "delivered",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
        "bootstrap_integrated",
        "slice39_closeout_created",
    )
    for name in required_false:
        if getattr(record, name) is not False:
            issues.append(
                _issue(
                    f"result.{name}",
                    ManifestCandidateIntegrationValidationCode.DOWNSTREAM_AUTHORITY,
                    "prohibited authority flag must be false",
                )
            )

    if record.canonical_digest != expected_result_digest(record):
        issues.append(
            _issue(
                "result.canonical_digest",
                ManifestCandidateIntegrationValidationCode.CANONICAL_MISMATCH,
                "result digest mismatch",
            )
        )
    if record.result_id != expected_result_id(record):
        issues.append(
            _issue(
                "result.result_id",
                ManifestCandidateIntegrationValidationCode.IDENTITY_MISMATCH,
                "result identity mismatch",
            )
        )
    return ManifestCandidateIntegrationValidationReport(tuple(issues))


def assert_valid_integration_result(record: object) -> None:
    report = validate_integration_result(record)
    if not report.ok:
        raise ManifestCandidateIntegrationValidationError(report)


__all__ = (
    "assert_valid_integration_result",
    "validate_integration_result",
    "validate_profile",
)
