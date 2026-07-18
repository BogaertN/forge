"""Fail-closed Slice 39C complete predecessor-custody binding.

This module accepts only already-built, exact Slice 36, 37 and 38 records.  It
reconstructs every claimed source span from the original input event, checks
all stage-to-stage identities, checks admitted registry resources by exact ID,
key and version, and emits only custody/provenance records.  It constructs no
semantic payload and grants no downstream authority.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from typing import Any, Callable, Iterable

from aiweb_language_core_bootstrap.input_event_custody import (
    InputEventCaptureResult,
    build_source_span,
    validate_input_event_capture_result,
    validate_source_span,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    SourceFieldProjectionResult,
    validate_source_field_projection_result,
)
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    ResonantOperatorCandidateBindingResult,
    validate_resonant_operator_candidate_binding_result,
)
from aiweb_language_core_bootstrap.symbolic_grammar_operator_registry import (
    build_default_symbolic_grammar_operator_registry,
)
from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import (
    CandidateResonantPhaseTrailResult,
    validate_candidate_resonant_phase_trail_result,
)
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import (
    ScopeAttachmentReferenceConstraintResult,
    validate_scope_attachment_reference_constraint_result,
)
from aiweb_language_core_bootstrap.deterministic_structural_derivation import (
    DeterministicStructuralDerivationResult,
    validate_deterministic_structural_derivation_result,
)
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import (
    StructuralConceptCandidateProposalResult,
    validate_proposal_result,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    PredicateRoleFrameCandidateProposalResult,
    validate_result as validate_slice38_candidate_result,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.built_in_registry import (
    concept_by_id,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.sense_term_mapping_registry import (
    sense_by_id,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.built_in_action_root_registry import (
    action_root_by_id,
    predicate_by_id,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.participant_role_registry import (
    role_by_id,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_frame_registry import (
    frame_by_id,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.capability_family_reference_registry import (
    capability_family_by_id,
    effect_boundary_by_id,
    frame_capability_reference_by_id,
    frame_effect_reference_by_id,
)

from ..governed_lifecycle.identity import with_expected_provenance_id
from ..schema import CandidateMeaningProvenance
from .authority import SLICE39C_REQUIRED_STAGES
from .identity import expected_lineage_id, with_expected_id
from .schema import (
    CandidateMeaningConstructionProfileIdentity,
    CandidateMeaningPredecessorBindingResult,
    CandidateMeaningPredecessorCustody,
    OperatorCustodyReference,
    PredecessorCustodyReceipt,
    PredecessorCustodyStage,
    PredecessorCustodyStatus,
    PredecessorCustodyValidationCode,
    PredecessorCustodyValidationIssue,
    RegistryResourceCustodyReference,
    RegistryResourceKind,
    SourceSpanCustodyReference,
    StructuralRuleCustodyReference,
    SLICE39C_PROFILE_VERSION,
)
from .validation import (
    validate_binding_result,
    validate_construction_profile,
    validate_custody,
)


_FALSE_AUTHORITY_FIELDS = (
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


def _profile() -> CandidateMeaningConstructionProfileIdentity:
    record = CandidateMeaningConstructionProfileIdentity(
        profile_id="pending",
        profile_key="complete_predecessor_custody",
        profile_version=SLICE39C_PROFILE_VERSION,
        required_stages=SLICE39C_REQUIRED_STAGES,
        exact_source_event_required=True,
        exact_source_checksum_required=True,
        exact_source_span_reconstruction_required=True,
        exact_structural_rule_ancestry_required=True,
        exact_operator_ancestry_required=True,
        exact_phase_trail_ancestry_required=True,
        exact_scope_attachment_reference_ancestry_required=True,
        exact_registry_snapshot_required=True,
        exact_resource_version_required=True,
        zero_one_many_preservation_required=True,
        cross_lineage_merge_allowed=False,
        generated_substitute_ancestry_allowed=False,
        semantic_payload_construction_allowed=False,
        candidate_ranking_allowed=False,
        candidate_selection_allowed=False,
        gate_progression_allowed=False,
        truth_evidence_permission_allowed=False,
        route_action_memory_rendering_delivery_allowed=False,
    )
    result = with_expected_id(record)
    report = validate_construction_profile(result)
    if not report.ok:
        raise RuntimeError("canonical Slice 39C construction profile is invalid")
    return result


DEFAULT_CONSTRUCTION_PROFILE = _profile()


def _issue(
    path: str,
    code: PredecessorCustodyValidationCode,
    detail: str,
) -> PredecessorCustodyValidationIssue:
    return PredecessorCustodyValidationIssue(path=path, code=code, detail=detail)


def _empty_result(
    *,
    status: PredecessorCustodyStatus,
    reason_code: str,
    issues: tuple[PredecessorCustodyValidationIssue, ...],
    source_event_id: str = "unknown:source_event",
    source_sha256: str = "0" * 64,
    slice37_result_id: str = "unknown:slice37_result",
    slice38_result_id: str = "unknown:slice38_result",
) -> CandidateMeaningPredecessorBindingResult:
    result = CandidateMeaningPredecessorBindingResult(
        result_id="pending",
        status=status,
        reason_code=reason_code,
        custody=None,
        issues=issues,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        slice37_result_id=slice37_result_id,
        slice38_result_id=slice38_result_id,
        source_span_reference_count=0,
        structural_rule_reference_count=0,
        operator_reference_count=0,
        registry_resource_reference_count=0,
        stage_receipt_count=0,
        semantic_payload_constructed=False,
        candidate_ranked=False,
        candidate_selected=False,
        gate_progression_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        route_created=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        semantic_similarity_used=False,
    )
    return with_expected_id(result)


def _rejected(
    issues: Iterable[PredecessorCustodyValidationIssue],
    *,
    source_event_id: str = "unknown:source_event",
    source_sha256: str = "0" * 64,
    slice37_result_id: str = "unknown:slice37_result",
    slice38_result_id: str = "unknown:slice38_result",
) -> CandidateMeaningPredecessorBindingResult:
    issue_tuple = tuple(issues)
    if not issue_tuple:
        issue_tuple = (
            _issue(
                "predecessors",
                PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
                "predecessor custody rejected",
            ),
        )
    return _empty_result(
        status=PredecessorCustodyStatus.PREDECESSOR_REJECTED,
        reason_code=issue_tuple[0].code.value,
        issues=issue_tuple,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        slice37_result_id=slice37_result_id,
        slice38_result_id=slice38_result_id,
    )


def _report_ok(report: object) -> bool:
    return getattr(report, "ok", False) is True


def _validate_predecessor(
    value: object,
    validator: Callable[[object], object],
    path: str,
    issues: list[PredecessorCustodyValidationIssue],
) -> None:
    try:
        report = validator(value)
    except Exception as exc:
        issues.append(
            _issue(
                path,
                PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
                f"validator raised {type(exc).__name__}",
            )
        )
        return
    if not _report_ok(report):
        issues.append(
            _issue(
                path,
                PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED,
                "accepted predecessor validator rejected record",
            )
        )


def _require_equal(
    actual: object,
    expected: object,
    path: str,
    code: PredecessorCustodyValidationCode,
    issues: list[PredecessorCustodyValidationIssue],
) -> None:
    if actual != expected:
        issues.append(_issue(path, code, "exact predecessor value mismatch"))


def _pairs(values: Iterable[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(set(values)))


def _ids(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _collect_source_spans(
    custody: InputEventCaptureResult,
    binding: ResonantOperatorCandidateBindingResult,
    trails: CandidateResonantPhaseTrailResult,
    constraints: ScopeAttachmentReferenceConstraintResult,
    structural: DeterministicStructuralDerivationResult,
    slice37: StructuralConceptCandidateProposalResult,
    issues: list[PredecessorCustodyValidationIssue],
) -> tuple[SourceSpanCustodyReference, ...]:
    event = custody.event
    root = custody.root_span
    if event is None or root is None:
        issues.append(
            _issue(
                "input_event_custody",
                PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE,
                "custody event and root span are required",
            )
        )
        return ()

    claims: dict[str, tuple[int, int]] = {}
    observed: dict[str, set[str]] = defaultdict(set)

    def add(span_id: str, cp_range: tuple[int, int], record_id: str) -> None:
        if type(span_id) is not str or type(cp_range) is not tuple or len(cp_range) != 2:
            issues.append(
                _issue(
                    "source_span_claim",
                    PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED,
                    "malformed source-span claim",
                )
            )
            return
        start, end = cp_range
        if type(start) is not int or type(end) is not int:
            issues.append(
                _issue(
                    f"source_span_claim.{span_id}",
                    PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
                    "source-span range must use exact integers",
                )
            )
            return
        prior = claims.get(span_id)
        if prior is not None and prior != cp_range:
            issues.append(
                _issue(
                    f"source_span_claim.{span_id}",
                    PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
                    "same span identity claimed with different ranges",
                )
            )
            return
        claims[span_id] = cp_range
        observed[span_id].add(record_id)

    add(root.span_id, (root.code_point_start, root.code_point_end), custody.result_id)

    binding_set = binding.binding_set
    if binding_set is not None:
        for candidate in binding_set.candidates:
            if not (
                len(candidate.source_span_ids)
                == len(candidate.code_point_ranges)
                == len(candidate.utf8_byte_ranges)
                == len(candidate.exact_source_fragments)
            ):
                issues.append(
                    _issue(
                        f"binding.{candidate.candidate_binding_id}.source_spans",
                        PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
                        "binding source-span vectors differ in length",
                    )
                )
                continue
            for span_id, cp_range in zip(
                candidate.source_span_ids, candidate.code_point_ranges
            ):
                add(span_id, cp_range, candidate.candidate_binding_id)

    trail_set = trails.phase_trail_set
    if trail_set is not None:
        for trail in trail_set.trails:
            for application in trail.applications:
                for span_id in application.source_span_ids:
                    observed[span_id].add(application.application_id)

    constraint_set = constraints.constraint_set
    if constraint_set is not None:
        for constrained in constraint_set.constrained_trails:
            for occurrence in constrained.scope_occurrences:
                if len(occurrence.exact_source_span_ids) != len(
                    occurrence.exact_code_point_ranges
                ):
                    issues.append(
                        _issue(
                            f"scope.{occurrence.occurrence_id}.source_spans",
                            PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
                            "scope occurrence source-span vectors differ in length",
                        )
                    )
                else:
                    for span_id, cp_range in zip(
                        occurrence.exact_source_span_ids,
                        occurrence.exact_code_point_ranges,
                    ):
                        add(span_id, cp_range, occurrence.occurrence_id)
                for governed in occurrence.possible_governed_spans:
                    if len(governed.source_span_ids) != len(governed.code_point_ranges):
                        issues.append(
                            _issue(
                                f"scope.{governed.governed_span_id}.source_spans",
                                PredecessorCustodyValidationCode.SOURCE_SPAN_RANGE_MISMATCH,
                                "governed-span vectors differ in length",
                            )
                        )
                    else:
                        for span_id, cp_range in zip(
                            governed.source_span_ids, governed.code_point_ranges
                        ):
                            add(span_id, cp_range, governed.governed_span_id)
            for analysis in constrained.reference_analyses:
                for span_id in analysis.source_span_ids:
                    observed[span_id].add(analysis.analysis_id)
                for candidate in analysis.candidates:
                    for span_id in candidate.source_span_ids:
                        observed[span_id].add(candidate.reference_candidate_id)

    structural_set = structural.structural_set
    if structural_set is not None:
        for candidate in structural_set.candidates:
            for trace in candidate.rule_application_traces:
                for span_id in trace.source_span_ids:
                    observed[span_id].add(trace.trace_id)
            coverage = candidate.source_coverage
            for span_ids, ranges, label in (
                (
                    coverage.consumed_source_span_ids,
                    coverage.consumed_code_point_ranges,
                    "consumed",
                ),
                (
                    coverage.unconsumed_source_span_ids,
                    coverage.unconsumed_code_point_ranges,
                    "unconsumed",
                ),
            ):
                if len(span_ids) == len(ranges):
                    for span_id, cp_range in zip(span_ids, ranges):
                        add(span_id, cp_range, coverage.coverage_proof_id)
                else:
                    for span_id in span_ids:
                        observed[span_id].add(coverage.coverage_proof_id)

    for occurrence in slice37.lexical_occurrences:
        for span_id in occurrence.source_span_ids:
            observed[span_id].add(occurrence.occurrence_id)

    missing_ranges = sorted(set(observed) - set(claims))
    for span_id in missing_ranges:
        issues.append(
            _issue(
                f"source_spans.{span_id}",
                PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE,
                "source span is referenced but no exact predecessor range exists",
            )
        )

    references: list[SourceSpanCustodyReference] = []
    for span_id in sorted(claims):
        start, end = claims[span_id]
        try:
            built = build_source_span(
                event,
                code_point_start=start,
                code_point_end=end,
            )
        except Exception as exc:
            issues.append(
                _issue(
                    f"source_spans.{span_id}",
                    PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED,
                    f"source-span reconstruction raised {type(exc).__name__}",
                )
            )
            continue
        if not built.ok or built.span is None:
            issues.append(
                _issue(
                    f"source_spans.{span_id}",
                    PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED,
                    "source-span reconstruction failed",
                )
            )
            continue
        span = built.span
        if span.span_id != span_id:
            issues.append(
                _issue(
                    f"source_spans.{span_id}",
                    PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED,
                    "claimed span identity differs from exact reconstruction",
                )
            )
            continue
        span_report = validate_source_span(span, event=event)
        if not span_report.ok:
            issues.append(
                _issue(
                    f"source_spans.{span_id}",
                    PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED,
                    "reconstructed span failed accepted validator",
                )
            )
            continue
        reference = SourceSpanCustodyReference(
            reference_id="pending",
            span_id=span.span_id,
            input_event_id=span.input_event_id,
            source_sha256=span.source_sha256,
            code_point_start=span.code_point_start,
            code_point_end=span.code_point_end,
            utf8_byte_start=span.utf8_byte_start,
            utf8_byte_end=span.utf8_byte_end,
            span_sha256=span.span_sha256,
            is_root_span=span.is_root_span,
            observed_in_record_ids=_ids(observed[span_id] | ({custody.result_id} if span_id == root.span_id else set())),
        )
        references.append(with_expected_id(reference))
    return tuple(sorted(references, key=lambda item: (item.code_point_start, item.code_point_end, item.span_id)))


def _collect_structural_rules(
    structural: DeterministicStructuralDerivationResult,
) -> tuple[StructuralRuleCustodyReference, ...]:
    references: list[StructuralRuleCustodyReference] = []
    structural_set = structural.structural_set
    if structural_set is None:
        return ()
    for candidate in structural_set.candidates:
        for trace in candidate.rule_application_traces:
            source_pairs = tuple(zip(trace.source_rule_ids, trace.source_rule_versions))
            record = StructuralRuleCustodyReference(
                reference_id="pending",
                trace_id=trace.trace_id,
                structural_candidate_id=candidate.structural_candidate_id,
                derivation_rule_id=trace.derivation_rule_id,
                derivation_rule_key=trace.derivation_rule_key,
                derivation_rule_version=trace.derivation_rule_version,
                source_rule_ids_and_versions=_pairs(source_pairs),
                input_record_ids=_ids(trace.input_record_ids),
                output_record_ids=_ids(trace.output_record_ids),
                source_span_ids=_ids(trace.source_span_ids),
            )
            references.append(with_expected_id(record))
    return tuple(sorted(references, key=lambda item: item.trace_id))


def _collect_operators(
    binding: ResonantOperatorCandidateBindingResult,
    trails: CandidateResonantPhaseTrailResult,
) -> tuple[OperatorCustodyReference, ...]:
    binding_set = binding.binding_set
    trail_set = trails.phase_trail_set
    if binding_set is None or trail_set is None:
        return ()
    trail_ids: dict[str, set[str]] = defaultdict(set)
    application_ids: dict[str, set[str]] = defaultdict(set)
    for trail in trail_set.trails:
        for binding_id in trail.participating_binding_ids:
            trail_ids[binding_id].add(trail.phase_trail_id)
        for application in trail.applications:
            application_ids[application.candidate_binding_id].add(application.application_id)
            trail_ids[application.candidate_binding_id].add(trail.phase_trail_id)
    records: list[OperatorCustodyReference] = []
    for candidate in binding_set.candidates:
        record = OperatorCustodyReference(
            reference_id="pending",
            candidate_binding_id=candidate.candidate_binding_id,
            operator_definition_id=candidate.candidate_operator_definition_id,
            operator_key=candidate.candidate_operator_key,
            operator_version=candidate.candidate_operator_version,
            grammar_registry_id=candidate.grammar_registry_id,
            grammar_registry_version=candidate.grammar_registry_version,
            proposal_rule_id=candidate.proposal_rule_id,
            proposal_rule_version=candidate.proposal_rule_version,
            source_span_ids=_ids(candidate.source_span_ids),
            phase_trail_ids=_ids(trail_ids[candidate.candidate_binding_id]),
            application_ids=_ids(application_ids[candidate.candidate_binding_id]),
        )
        records.append(with_expected_id(record))
    return tuple(sorted(records, key=lambda item: item.candidate_binding_id))


def _resource_record(
    *,
    kind: RegistryResourceKind,
    resource_id: str,
    resource_key: str,
    resource_version: str,
    snapshot_id: str,
    source_candidate_ids: Iterable[str],
    parent_resource_ids: Iterable[str] = (),
    relation_reference_ids: Iterable[str] = (),
) -> RegistryResourceCustodyReference:
    return with_expected_id(
        RegistryResourceCustodyReference(
            reference_id="pending",
            resource_kind=kind,
            resource_id=resource_id,
            resource_key=resource_key,
            resource_version=resource_version,
            registry_snapshot_id=snapshot_id,
            source_candidate_ids=_ids(source_candidate_ids),
            parent_resource_ids=_ids(parent_resource_ids),
            relation_reference_ids=_ids(relation_reference_ids),
        )
    )


def _exact_static_resource(
    *,
    lookup: Callable[[str], object],
    resource_id: str,
    expected_key: str,
    expected_version: str,
    id_field: str,
    key_field: str,
    path: str,
    fabricated_code: PredecessorCustodyValidationCode,
    issues: list[PredecessorCustodyValidationIssue],
) -> object | None:
    try:
        record = lookup(resource_id)
    except Exception:
        record = None
    if record is None:
        issues.append(_issue(path, fabricated_code, "resource ID is not admitted"))
        return None
    if getattr(record, id_field, None) != resource_id:
        issues.append(_issue(path, fabricated_code, "registry returned different resource identity"))
        return None
    if getattr(record, key_field, None) != expected_key:
        issues.append(_issue(path, fabricated_code, "resource key differs from admitted registry"))
    if getattr(record, "version", None) != expected_version:
        issues.append(
            _issue(
                path,
                PredecessorCustodyValidationCode.RESOURCE_VERSION_MISMATCH,
                "resource version differs from admitted registry",
            )
        )
    expected_id_method = getattr(record, "expected_id", None)
    if callable(expected_id_method):
        try:
            if expected_id_method() != resource_id:
                issues.append(_issue(path, fabricated_code, "admitted resource identity is internally invalid"))
        except Exception:
            issues.append(_issue(path, fabricated_code, "resource identity verification raised"))
    return record


def _collect_registry_resources(
    slice37: StructuralConceptCandidateProposalResult,
    slice38: PredicateRoleFrameCandidateProposalResult,
    issues: list[PredecessorCustodyValidationIssue],
) -> tuple[RegistryResourceCustodyReference, ...]:
    records: dict[tuple[RegistryResourceKind, str], RegistryResourceCustodyReference] = {}
    snap37 = slice37.registry_snapshot.snapshot_id
    snap38 = slice38.slice38_registry_snapshot.snapshot_id

    def put(record: RegistryResourceCustodyReference) -> None:
        key = (record.resource_kind, record.resource_id)
        previous = records.get(key)
        if previous is None:
            records[key] = record
            return

        fixed_fields_match = (
            previous.resource_key == record.resource_key
            and previous.resource_version == record.resource_version
            and previous.registry_snapshot_id == record.registry_snapshot_id
            and previous.schema_version == record.schema_version
        )
        if not fixed_fields_match:
            issues.append(
                _issue(
                    f"registry_resources.{record.resource_id}",
                    PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE,
                    "same resource identity arrived with incompatible key, version, snapshot, or schema ancestry",
                )
            )
            return

        merged = replace(
            previous,
            reference_id="pending",
            source_candidate_ids=_ids(
                previous.source_candidate_ids + record.source_candidate_ids
            ),
            parent_resource_ids=_ids(
                previous.parent_resource_ids + record.parent_resource_ids
            ),
            relation_reference_ids=_ids(
                previous.relation_reference_ids + record.relation_reference_ids
            ),
        )
        records[key] = with_expected_id(merged)

    concept_candidates = {item.proposal_id: item for item in slice37.concept_candidates}
    sense_candidates = {item.proposal_id: item for item in slice37.sense_candidates}

    for candidate in slice37.concept_candidates:
        _exact_static_resource(
            lookup=concept_by_id,
            resource_id=candidate.concept_id,
            expected_key=candidate.concept_key,
            expected_version=candidate.concept_version,
            id_field="concept_id",
            key_field="concept_key",
            path=f"concept.{candidate.proposal_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        put(
            _resource_record(
                kind=RegistryResourceKind.CONCEPT,
                resource_id=candidate.concept_id,
                resource_key=candidate.concept_key,
                resource_version=candidate.concept_version,
                snapshot_id=snap37,
                source_candidate_ids=(candidate.proposal_id,),
                relation_reference_ids=candidate.related_sense_candidate_ids,
            )
        )

    for candidate in slice37.sense_candidates:
        admitted = _exact_static_resource(
            lookup=sense_by_id,
            resource_id=candidate.sense_id,
            expected_key=candidate.sense_key,
            expected_version=candidate.sense_version,
            id_field="sense_id",
            key_field="sense_key",
            path=f"sense.{candidate.proposal_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        if admitted is not None and getattr(admitted, "concept_id", None) != candidate.concept_id:
            issues.append(
                _issue(
                    f"sense.{candidate.proposal_id}.concept_id",
                    PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE,
                    "sense belongs to a different admitted concept",
                )
            )
        put(
            _resource_record(
                kind=RegistryResourceKind.SENSE,
                resource_id=candidate.sense_id,
                resource_key=candidate.sense_key,
                resource_version=candidate.sense_version,
                snapshot_id=snap37,
                source_candidate_ids=(candidate.proposal_id,),
                parent_resource_ids=(candidate.concept_id,),
            )
        )

    layout_by_id = {item.candidate_id: item for item in slice38.role_layout_candidates}
    capability_by_id = {item.candidate_id: item for item in slice38.capability_reference_candidates}

    for candidate in slice38.action_predicate_candidates:
        for source_id in candidate.source_concept_candidate_proposal_ids:
            if source_id not in concept_candidates:
                issues.append(_issue(f"action.{candidate.candidate_id}.concept_sources", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, "action candidate references foreign concept candidate"))
        for source_id in candidate.source_sense_candidate_proposal_ids:
            if source_id not in sense_candidates:
                issues.append(_issue(f"action.{candidate.candidate_id}.sense_sources", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, "action candidate references foreign sense candidate"))
        _exact_static_resource(
            lookup=action_root_by_id,
            resource_id=candidate.action_root_id,
            expected_key=candidate.action_root_key,
            expected_version=candidate.action_root_version,
            id_field="action_root_id",
            key_field="action_root_key",
            path=f"action_root.{candidate.candidate_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        predicate = _exact_static_resource(
            lookup=predicate_by_id,
            resource_id=candidate.predicate_id,
            expected_key=candidate.predicate_key,
            expected_version=candidate.predicate_version,
            id_field="predicate_id",
            key_field="predicate_key",
            path=f"predicate.{candidate.candidate_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        if predicate is not None and getattr(predicate, "action_root_id", None) != candidate.action_root_id:
            issues.append(_issue(f"predicate.{candidate.candidate_id}.action_root_id", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, "predicate belongs to a different action root"))
        put(_resource_record(kind=RegistryResourceKind.ACTION_ROOT, resource_id=candidate.action_root_id, resource_key=candidate.action_root_key, resource_version=candidate.action_root_version, snapshot_id=snap38, source_candidate_ids=(candidate.candidate_id,), relation_reference_ids=candidate.role_layout_candidate_ids))
        put(_resource_record(kind=RegistryResourceKind.PREDICATE, resource_id=candidate.predicate_id, resource_key=candidate.predicate_key, resource_version=candidate.predicate_version, snapshot_id=snap38, source_candidate_ids=(candidate.candidate_id,), parent_resource_ids=(candidate.action_root_id,), relation_reference_ids=tuple(item[0] for item in candidate.frame_ids_and_versions)))
        for layout_id in candidate.role_layout_candidate_ids:
            if layout_id not in layout_by_id:
                issues.append(_issue(f"action.{candidate.candidate_id}.role_layouts", PredecessorCustodyValidationCode.ROLE_IDENTITY_FABRICATED, "action candidate references missing role-layout candidate"))
        for capability_id in candidate.capability_reference_candidate_ids:
            if capability_id not in capability_by_id:
                issues.append(_issue(f"action.{candidate.candidate_id}.capabilities", PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED, "action candidate references missing capability candidate"))

    for layout in slice38.role_layout_candidates:
        frame = _exact_static_resource(
            lookup=frame_by_id,
            resource_id=layout.frame_id,
            expected_key=layout.frame_key,
            expected_version=layout.frame_version,
            id_field="frame_id",
            key_field="frame_key",
            path=f"frame.{layout.candidate_id}",
            fabricated_code=PredecessorCustodyValidationCode.FRAME_IDENTITY_FABRICATED,
            issues=issues,
        )
        if frame is not None:
            if getattr(frame, "linked_action_root_id", None) != layout.action_root_id or getattr(frame, "linked_predicate_id", None) != layout.predicate_id:
                issues.append(_issue(f"frame.{layout.candidate_id}.lineage", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, "frame belongs to a different action-root/predicate lineage"))
        put(_resource_record(kind=RegistryResourceKind.PREDICATE_FRAME, resource_id=layout.frame_id, resource_key=layout.frame_key, resource_version=layout.frame_version, snapshot_id=snap38, source_candidate_ids=(layout.candidate_id,), parent_resource_ids=(layout.action_root_id, layout.predicate_id), relation_reference_ids=(layout.frame_effect_reference_id,) + layout.capability_reference_candidate_ids))

        role_triples = layout.required_roles + layout.optional_roles + layout.prohibited_roles + layout.conditional_roles
        for role_id_value, role_key, role_version in role_triples:
            _exact_static_resource(
                lookup=role_by_id,
                resource_id=role_id_value,
                expected_key=role_key,
                expected_version=role_version,
                id_field="role_id",
                key_field="role_key",
                path=f"role.{layout.candidate_id}.{role_id_value}",
                fabricated_code=PredecessorCustodyValidationCode.ROLE_IDENTITY_FABRICATED,
                issues=issues,
            )
            put(_resource_record(kind=RegistryResourceKind.PARTICIPANT_ROLE, resource_id=role_id_value, resource_key=role_key, resource_version=role_version, snapshot_id=snap38, source_candidate_ids=(layout.candidate_id,), parent_resource_ids=(layout.frame_id,)))

        _exact_static_resource(
            lookup=effect_boundary_by_id,
            resource_id=layout.effect_boundary_id,
            expected_key=layout.effect_boundary_key,
            expected_version=layout.effect_boundary_version,
            id_field="effect_boundary_id",
            key_field="effect_boundary_key",
            path=f"effect_boundary.{layout.candidate_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        put(_resource_record(kind=RegistryResourceKind.EFFECT_BOUNDARY, resource_id=layout.effect_boundary_id, resource_key=layout.effect_boundary_key, resource_version=layout.effect_boundary_version, snapshot_id=snap38, source_candidate_ids=(layout.candidate_id,), parent_resource_ids=(layout.frame_id,)))

        effect_ref = _exact_static_resource(
            lookup=frame_effect_reference_by_id,
            resource_id=layout.frame_effect_reference_id,
            expected_key=layout.frame_key,
            expected_version=layout.frame_effect_reference_version,
            id_field="frame_effect_reference_id",
            key_field="frame_key",
            path=f"frame_effect_reference.{layout.candidate_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        if effect_ref is not None and (getattr(effect_ref, "frame_id", None) != layout.frame_id or getattr(effect_ref, "effect_boundary_id", None) != layout.effect_boundary_id):
            issues.append(_issue(f"frame_effect_reference.{layout.candidate_id}.lineage", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, "frame-effect reference belongs to different frame/effect lineage"))
        put(_resource_record(kind=RegistryResourceKind.FRAME_EFFECT_REFERENCE, resource_id=layout.frame_effect_reference_id, resource_key=layout.frame_key, resource_version=layout.frame_effect_reference_version, snapshot_id=snap38, source_candidate_ids=(layout.candidate_id,), parent_resource_ids=(layout.frame_id, layout.effect_boundary_id)))

    for candidate in slice38.capability_reference_candidates:
        capability = _exact_static_resource(
            lookup=capability_family_by_id,
            resource_id=candidate.capability_family_id,
            expected_key=candidate.capability_family_key,
            expected_version=candidate.capability_family_version,
            id_field="capability_family_id",
            key_field="capability_family_key",
            path=f"capability.{candidate.candidate_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        if capability is not None and candidate.effect_boundary_id not in getattr(capability, "supported_effect_boundary_refs", ()):
            issues.append(_issue(f"capability.{candidate.candidate_id}.effect_boundary", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, "capability does not admit claimed effect boundary"))
        put(_resource_record(kind=RegistryResourceKind.CAPABILITY_FAMILY, resource_id=candidate.capability_family_id, resource_key=candidate.capability_family_key, resource_version=candidate.capability_family_version, snapshot_id=snap38, source_candidate_ids=(candidate.candidate_id,), parent_resource_ids=(candidate.effect_boundary_id,)))

        frame_cap = _exact_static_resource(
            lookup=frame_capability_reference_by_id,
            resource_id=candidate.frame_capability_reference_id,
            expected_key=candidate.frame_key,
            expected_version=candidate.frame_capability_reference_version,
            id_field="frame_capability_reference_id",
            key_field="frame_key",
            path=f"frame_capability_reference.{candidate.candidate_id}",
            fabricated_code=PredecessorCustodyValidationCode.RESOURCE_IDENTITY_FABRICATED,
            issues=issues,
        )
        if frame_cap is not None and (
            getattr(frame_cap, "frame_id", None) != candidate.frame_id
            or getattr(frame_cap, "capability_family_id", None) != candidate.capability_family_id
            or getattr(frame_cap, "effect_boundary_id", None) != candidate.effect_boundary_id
        ):
            issues.append(_issue(f"frame_capability_reference.{candidate.candidate_id}.lineage", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, "frame-capability reference belongs to a different lineage"))
        put(_resource_record(kind=RegistryResourceKind.FRAME_CAPABILITY_REFERENCE, resource_id=candidate.frame_capability_reference_id, resource_key=candidate.frame_key, resource_version=candidate.frame_capability_reference_version, snapshot_id=snap38, source_candidate_ids=(candidate.candidate_id,), parent_resource_ids=(candidate.frame_id, candidate.capability_family_id, candidate.effect_boundary_id)))

    return tuple(sorted(records.values(), key=lambda item: (item.resource_kind.value, item.resource_id)))


def _receipts(
    *,
    source_event_id: str,
    source_sha256: str,
    stages: tuple[tuple[PredecessorCustodyStage, tuple[str, ...], str, str], ...],
) -> tuple[PredecessorCustodyReceipt, ...]:
    result: list[PredecessorCustodyReceipt] = []
    for ordinal, (stage, predecessor_ids, output_id, output_schema) in enumerate(stages, start=1):
        exact_predecessors = () if not result else (result[-1].output_record_id, result[-1].receipt_id)
        record = PredecessorCustodyReceipt(
            receipt_id="pending",
            stage_ordinal=ordinal,
            stage=stage,
            predecessor_record_ids=exact_predecessors,
            output_record_id=output_id,
            output_schema_version=output_schema,
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            exact_validation_passed=True,
            exact_lineage_preserved=True,
            generated_substitute_ancestry_used=False,
            semantic_payload_constructed=False,
            candidate_ranked=False,
            candidate_selected=False,
            gate_progression_created=False,
            truth_determined=False,
            evidence_validated=False,
            permission_granted=False,
            route_created=False,
            action_performed=False,
            memory_accessed=False,
            rendered=False,
            delivered=False,
        )
        result.append(with_expected_id(record))
    return tuple(result)


def bind_complete_predecessor_custody(
    custody: object,
    projection: object,
    binding: object,
    trails: object,
    constraints: object,
    structural: object,
    slice37: object,
    slice38: object,
    *,
    construction_profile: object = DEFAULT_CONSTRUCTION_PROFILE,
) -> CandidateMeaningPredecessorBindingResult:
    """Bind the exact accepted predecessor chain without semantic construction."""

    issues: list[PredecessorCustodyValidationIssue] = []
    exact_types = (
        (custody, InputEventCaptureResult, "custody"),
        (projection, SourceFieldProjectionResult, "projection"),
        (binding, ResonantOperatorCandidateBindingResult, "binding"),
        (trails, CandidateResonantPhaseTrailResult, "trails"),
        (constraints, ScopeAttachmentReferenceConstraintResult, "constraints"),
        (structural, DeterministicStructuralDerivationResult, "structural"),
        (slice37, StructuralConceptCandidateProposalResult, "slice37"),
        (slice38, PredicateRoleFrameCandidateProposalResult, "slice38"),
        (construction_profile, CandidateMeaningConstructionProfileIdentity, "construction_profile"),
    )
    for value, expected_type, path in exact_types:
        if type(value) is not expected_type:
            issues.append(_issue(path, PredecessorCustodyValidationCode.TYPE_MISMATCH, f"exact {expected_type.__name__} required"))
    if issues:
        return _rejected(issues)

    assert isinstance(custody, InputEventCaptureResult)
    assert isinstance(projection, SourceFieldProjectionResult)
    assert isinstance(binding, ResonantOperatorCandidateBindingResult)
    assert isinstance(trails, CandidateResonantPhaseTrailResult)
    assert isinstance(constraints, ScopeAttachmentReferenceConstraintResult)
    assert isinstance(structural, DeterministicStructuralDerivationResult)
    assert isinstance(slice37, StructuralConceptCandidateProposalResult)
    assert isinstance(slice38, PredicateRoleFrameCandidateProposalResult)
    assert isinstance(construction_profile, CandidateMeaningConstructionProfileIdentity)

    source_event_id = custody.event.input_event_id if custody.event is not None else "unknown:source_event"
    source_sha256 = custody.event.source_sha256 if custody.event is not None else "0" * 64

    _validate_predecessor(custody, validate_input_event_capture_result, "custody", issues)
    _validate_predecessor(projection, validate_source_field_projection_result, "projection", issues)
    _validate_predecessor(binding, validate_resonant_operator_candidate_binding_result, "binding", issues)
    try:
        trail_report = validate_candidate_resonant_phase_trail_result(
            trails, projection, binding, build_default_symbolic_grammar_operator_registry()
        )
        if not trail_report.ok:
            issues.append(_issue("trails", PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED, "accepted predecessor validator rejected record"))
    except Exception as exc:
        issues.append(_issue("trails", PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED, f"validator raised {type(exc).__name__}"))
    try:
        constraint_report = validate_scope_attachment_reference_constraint_result(
            constraints, projection, binding, trails
        )
        if not constraint_report.ok:
            issues.append(_issue("constraints", PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED, "accepted predecessor validator rejected record"))
    except Exception as exc:
        issues.append(_issue("constraints", PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED, f"validator raised {type(exc).__name__}"))
    try:
        structural_report = validate_deterministic_structural_derivation_result(
            structural, custody, projection, binding, trails, constraints
        )
        if not structural_report.ok:
            issues.append(_issue("structural", PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED, "accepted predecessor validator rejected record"))
    except Exception as exc:
        issues.append(_issue("structural", PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED, f"validator raised {type(exc).__name__}"))
    _validate_predecessor(slice37, validate_proposal_result, "slice37", issues)
    _validate_predecessor(slice38, validate_slice38_candidate_result, "slice38", issues)
    profile_report = validate_construction_profile(construction_profile)
    if not profile_report.ok or construction_profile != DEFAULT_CONSTRUCTION_PROFILE:
        issues.append(_issue("construction_profile", PredecessorCustodyValidationCode.CONSTRUCTION_PROFILE_MISMATCH, "exact canonical Slice 39C profile required"))

    if custody.event is None or custody.root_span is None or projection.projection is None or binding.binding_set is None or trails.phase_trail_set is None or constraints.constraint_set is None or structural.structural_set is None or slice37.registry_snapshot is None or slice38.slice38_registry_snapshot is None or slice38.compatibility_registry_snapshot is None:
        issues.append(_issue("predecessors", PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE, "complete accepted predecessor records are required"))

    if issues:
        return _rejected(issues, source_event_id=source_event_id, source_sha256=source_sha256, slice37_result_id=slice37.result_id, slice38_result_id=slice38.result_id)

    event = custody.event
    root = custody.root_span
    projection_record = projection.projection
    binding_set = binding.binding_set
    trail_set = trails.phase_trail_set
    constraint_set = constraints.constraint_set
    structural_set = structural.structural_set
    assert event is not None and root is not None and projection_record is not None
    assert binding_set is not None and trail_set is not None and constraint_set is not None and structural_set is not None

    for path, actual in (
        ("projection.source_event_id", projection.source_event_id),
        ("binding.source_event_id", binding.source_event_id),
        ("trails.source_event_id", trails.source_event_id),
        ("constraints.source_event_id", constraints.source_event_id),
        ("structural.source_event_id", structural.source_event_id),
        ("slice37.source_event_id", slice37.source_event_id),
        ("slice38.source_event_id", slice38.source_event_id),
    ):
        _require_equal(actual, event.input_event_id, path, PredecessorCustodyValidationCode.SOURCE_EVENT_MISMATCH, issues)
    for path, actual in (
        ("projection.source_sha256", projection.source_sha256),
        ("binding.source_sha256", binding.source_sha256),
        ("trails.source_sha256", trails.source_sha256),
        ("constraints.source_sha256", constraints.source_sha256),
        ("structural.source_sha256", structural.source_sha256),
        ("slice37.source_sha256", slice37.source_sha256),
        ("slice38.source_sha256", slice38.source_sha256),
    ):
        _require_equal(actual, event.source_sha256, path, PredecessorCustodyValidationCode.SOURCE_CHECKSUM_MISMATCH, issues)

    _require_equal(root.span_id, event.root_source_span_id, "custody.root_source_span_id", PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED, issues)
    _require_equal(projection_record.root_source_span_id, root.span_id, "projection.root_source_span_id", PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED, issues)
    _require_equal(binding.projection_id, projection_record.projection_id, "binding.projection_id", PredecessorCustodyValidationCode.STRUCTURAL_ANCESTRY_MISMATCH, issues)
    _require_equal(trails.projection_id, projection_record.projection_id, "trails.projection_id", PredecessorCustodyValidationCode.PHASE_TRAIL_ANCESTRY_MISMATCH, issues)
    _require_equal(trails.binding_set_id, binding_set.binding_set_id, "trails.binding_set_id", PredecessorCustodyValidationCode.OPERATOR_ANCESTRY_MISMATCH, issues)
    _require_equal(constraints.phase_trail_set_id, trail_set.phase_trail_set_id, "constraints.phase_trail_set_id", PredecessorCustodyValidationCode.SCOPE_ANCESTRY_MISMATCH, issues)
    _require_equal(structural.constraint_set_id, constraint_set.constraint_set_id, "structural.constraint_set_id", PredecessorCustodyValidationCode.STRUCTURAL_ANCESTRY_MISMATCH, issues)
    _require_equal(slice37.structural_result_id, structural.result_id, "slice37.structural_result_id", PredecessorCustodyValidationCode.STRUCTURAL_ANCESTRY_MISMATCH, issues)
    _require_equal(slice37.structural_set_id, structural_set.structural_set_id, "slice37.structural_set_id", PredecessorCustodyValidationCode.STRUCTURAL_ANCESTRY_MISMATCH, issues)
    _require_equal(slice38.source_slice37_result_id, slice37.result_id, "slice38.source_slice37_result_id", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, issues)
    _require_equal(slice38.slice37_registry_snapshot_id, slice37.registry_snapshot.snapshot_id, "slice38.slice37_registry_snapshot_id", PredecessorCustodyValidationCode.REGISTRY_SNAPSHOT_MISMATCH, issues)

    expected_structural_ids = _ids(item.structural_candidate_id for item in structural_set.candidates)
    _require_equal(_ids(item.structural_candidate_id for item in slice37.structural_ancestries), expected_structural_ids, "slice37.structural_candidate_ids", PredecessorCustodyValidationCode.STRUCTURAL_ANCESTRY_MISMATCH, issues)
    _require_equal(_ids(slice38.structural_ancestry_ids), _ids(item.ancestry_id for item in slice37.structural_ancestries), "slice38.structural_ancestry_ids", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, issues)
    _require_equal(_ids(slice38.concept_candidate_proposal_ids), _ids(item.proposal_id for item in slice37.concept_candidates), "slice38.concept_candidate_proposal_ids", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, issues)
    _require_equal(_ids(slice38.sense_candidate_proposal_ids), _ids(item.proposal_id for item in slice37.sense_candidates), "slice38.sense_candidate_proposal_ids", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, issues)

    for ancestry in slice37.structural_ancestries:
        _require_equal(ancestry.source_event_id, event.input_event_id, f"slice37.ancestry.{ancestry.ancestry_id}.source_event_id", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, issues)
        _require_equal(ancestry.source_sha256, event.source_sha256, f"slice37.ancestry.{ancestry.ancestry_id}.source_sha256", PredecessorCustodyValidationCode.CROSS_LINEAGE_CANDIDATE_MERGE, issues)
        _require_equal(ancestry.root_source_span_id, root.span_id, f"slice37.ancestry.{ancestry.ancestry_id}.root_source_span_id", PredecessorCustodyValidationCode.SOURCE_SPAN_FABRICATED, issues)
        if not ancestry.exact_ancestry_complete or not ancestry.source_reconstruction_proven:
            issues.append(_issue(f"slice37.ancestry.{ancestry.ancestry_id}", PredecessorCustodyValidationCode.GENERATED_SUBSTITUTE_ANCESTRY, "exact accepted ancestry proof is required"))

    if slice38.action_predicate_candidate_count == 0:
        if issues:
            return _rejected(issues, source_event_id=event.input_event_id, source_sha256=event.source_sha256, slice37_result_id=slice37.result_id, slice38_result_id=slice38.result_id)
        result = _empty_result(
            status=PredecessorCustodyStatus.NO_CANDIDATE_PREDECESSOR,
            reason_code="no_slice38_candidate_predecessor",
            issues=(),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            slice37_result_id=slice37.result_id,
            slice38_result_id=slice38.result_id,
        )
        if not validate_binding_result(result).ok:
            return _rejected((_issue("binding_result", PredecessorCustodyValidationCode.PREDECESSOR_VALIDATION_FAILED, "empty result failed Slice 39C validator"),), source_event_id=event.input_event_id, source_sha256=event.source_sha256, slice37_result_id=slice37.result_id, slice38_result_id=slice38.result_id)
        return result

    source_spans = _collect_source_spans(custody, binding, trails, constraints, structural, slice37, issues)
    structural_rules = _collect_structural_rules(structural)
    operators = _collect_operators(binding, trails)
    resources = _collect_registry_resources(slice37, slice38, issues)

    if not source_spans:
        issues.append(_issue("source_spans", PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE, "at least one reconstructed source span is required"))
    if not structural_rules:
        issues.append(_issue("structural_rules", PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE, "structural-rule ancestry is required"))
    if not operators:
        issues.append(_issue("operators", PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE, "operator ancestry is required"))
    if not resources:
        issues.append(_issue("registry_resources", PredecessorCustodyValidationCode.MISSING_PREDECESSOR_REFERENCE, "registry-resource ancestry is required"))

    stages = (
        (PredecessorCustodyStage.INPUT_EVENT_CUSTODY, (), custody.result_id, custody.schema_version),
        (PredecessorCustodyStage.SOURCE_FIELD_PROJECTION, (custody.result_id,), projection.result_id, projection.schema_version),
        (PredecessorCustodyStage.OPERATOR_CANDIDATE_BINDING, (projection.result_id,), binding.result_id, binding.schema_version),
        (PredecessorCustodyStage.CANDIDATE_PHASE_TRAILS, (binding.result_id,), trails.result_id, trails.schema_version),
        (PredecessorCustodyStage.SCOPE_ATTACHMENT_REFERENCE_CONSTRAINTS, (trails.result_id,), constraints.result_id, constraints.schema_version),
        (PredecessorCustodyStage.DETERMINISTIC_STRUCTURAL_DERIVATION, (constraints.result_id,), structural.result_id, structural.schema_version),
        (PredecessorCustodyStage.SLICE37_CONCEPT_SENSE_CANDIDATES, (structural.result_id,), slice37.result_id, slice37.schema_version),
        (PredecessorCustodyStage.SLICE38_PREDICATE_ROLE_FRAME_CANDIDATES, (slice37.result_id,), slice38.result_id, slice38.schema_version),
    )
    receipts = _receipts(source_event_id=event.input_event_id, source_sha256=event.source_sha256, stages=stages)

    provenance = CandidateMeaningProvenance(
        provenance_id="pending",
        source_event_id=event.input_event_id,
        source_sha256=event.source_sha256,
        input_event_id=event.input_event_id,
        root_source_span_id=root.span_id,
        source_span_ids=tuple(item.span_id for item in source_spans),
        projection_id=projection_record.projection_id,
        structural_result_id=structural.result_id,
        structural_set_id=structural_set.structural_set_id,
        structural_candidate_ids=tuple(item.structural_candidate_id for item in structural_set.candidates),
        structural_ancestry_ids=tuple(item.ancestry_id for item in slice37.structural_ancestries),
        constrained_trail_ids=slice38.constrained_trail_ids,
        phase_trail_ids=slice38.phase_trail_ids,
        operator_graph_ids=slice38.operator_graph_ids,
        operator_node_ids=slice38.operator_node_ids,
        operator_definition_ids=slice38.operator_definition_ids,
        operator_keys_and_versions=slice38.operator_keys_and_versions,
        scope_occurrence_ids=slice38.scope_occurrence_ids,
        attachment_candidate_ids=slice38.attachment_candidate_ids,
        reference_analysis_ids=slice38.reference_analysis_ids,
        reference_candidate_ids=slice38.reference_candidate_ids,
        slice37_result_id=slice37.result_id,
        slice37_registry_snapshot_id=slice37.registry_snapshot.snapshot_id,
        concept_candidate_proposal_ids=tuple(item.proposal_id for item in slice37.concept_candidates),
        sense_candidate_proposal_ids=tuple(item.proposal_id for item in slice37.sense_candidates),
        concept_ids_and_versions=tuple((item.concept_id, item.concept_version) for item in slice37.concept_candidates),
        sense_ids_and_versions=tuple((item.sense_id, item.sense_version) for item in slice37.sense_candidates),
        slice38_result_id=slice38.result_id,
        slice38_registry_snapshot_id=slice38.slice38_registry_snapshot.snapshot_id,
        compatibility_registry_snapshot_id=slice38.compatibility_registry_snapshot.snapshot_id,
        action_predicate_candidate_ids=tuple(item.candidate_id for item in slice38.action_predicate_candidates),
        role_layout_candidate_ids=tuple(item.candidate_id for item in slice38.role_layout_candidates),
        capability_reference_candidate_ids=tuple(item.candidate_id for item in slice38.capability_reference_candidates),
        predecessor_receipt_ids=tuple(item.receipt_id for item in receipts),
        source_ancestry_preserved=True,
        operator_ancestry_preserved=True,
        phase_trail_ancestry_preserved=True,
        scope_attachment_ancestry_preserved=True,
        registry_snapshots_preserved=True,
    )
    provenance = with_expected_provenance_id(provenance)

    lineage_id = expected_lineage_id(
        source_event_id=event.input_event_id,
        source_sha256=event.source_sha256,
        slice37_registry_snapshot_id=slice37.registry_snapshot.snapshot_id,
        slice38_registry_snapshot_id=slice38.slice38_registry_snapshot.snapshot_id,
        compatibility_registry_snapshot_id=slice38.compatibility_registry_snapshot.snapshot_id,
        construction_profile_id=construction_profile.profile_id,
        construction_profile_version=construction_profile.profile_version,
    )
    predecessor_ids = tuple(stage[2] for stage in stages)
    custody_record = CandidateMeaningPredecessorCustody(
        custody_id="pending",
        lineage_id=lineage_id,
        provenance=provenance,
        construction_profile=construction_profile,
        source_span_references=source_spans,
        structural_rule_references=structural_rules,
        operator_references=operators,
        registry_resource_references=resources,
        stage_receipts=receipts,
        predecessor_result_ids=predecessor_ids,
        exact_source_event_match=True,
        exact_source_checksum_match=True,
        exact_source_spans_verified=True,
        exact_structural_ancestry_verified=True,
        exact_operator_ancestry_verified=True,
        exact_phase_trail_ancestry_verified=True,
        exact_scope_attachment_reference_ancestry_verified=True,
        exact_registry_snapshots_verified=True,
        exact_resource_versions_verified=True,
        zero_one_many_preserved=True,
        cross_lineage_candidate_merge_performed=False,
        generated_substitute_ancestry_used=False,
        semantic_payload_constructed=False,
        candidate_ranked=False,
        candidate_selected=False,
        gate_progression_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        route_created=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        canonical_digest="pending",
    )
    custody_record = with_expected_id(custody_record)
    custody_report = validate_custody(custody_record)
    if not custody_report.ok:
        issues.extend(custody_report.issues)

    if issues:
        return _rejected(issues, source_event_id=event.input_event_id, source_sha256=event.source_sha256, slice37_result_id=slice37.result_id, slice38_result_id=slice38.result_id)

    result = CandidateMeaningPredecessorBindingResult(
        result_id="pending",
        status=PredecessorCustodyStatus.BOUND,
        reason_code="complete_predecessor_custody_bound",
        custody=custody_record,
        issues=(),
        source_event_id=event.input_event_id,
        source_sha256=event.source_sha256,
        slice37_result_id=slice37.result_id,
        slice38_result_id=slice38.result_id,
        source_span_reference_count=len(source_spans),
        structural_rule_reference_count=len(structural_rules),
        operator_reference_count=len(operators),
        registry_resource_reference_count=len(resources),
        stage_receipt_count=len(receipts),
        semantic_payload_constructed=False,
        candidate_ranked=False,
        candidate_selected=False,
        gate_progression_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        route_created=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        semantic_similarity_used=False,
    )
    result = with_expected_id(result)
    final_report = validate_binding_result(result)
    if not final_report.ok:
        return _rejected(final_report.issues, source_event_id=event.input_event_id, source_sha256=event.source_sha256, slice37_result_id=slice37.result_id, slice38_result_id=slice38.result_id)
    return result


__all__ = (
    "DEFAULT_CONSTRUCTION_PROFILE",
    "bind_complete_predecessor_custody",
)
