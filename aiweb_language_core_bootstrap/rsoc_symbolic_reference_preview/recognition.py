"""Exact registry-glyph recognition over validated source-field atoms."""

from __future__ import annotations

from ..input_event_custody import (
    InputCustodyStatus,
    InputEventCaptureResult,
    build_source_span,
    validate_input_event_capture_result,
)
from ..resonant_language_operator_contract import (
    RsocLanguageOperatorRegistry,
    build_default_rsoc_operator_registry,
    validate_rsoc_language_operator_registry,
)
from ..schema import stable_record_id
from ..source_field_projection import (
    SourceFieldProjectionResult,
    SourceFieldProjectionStatus,
    validate_source_field_projection_result,
)
from .schema import (
    ABSOLUTE_MAX_COVERAGE_SEGMENTS,
    ABSOLUTE_MAX_OPERATOR_REFERENCES,
    DEFAULT_MAX_COVERAGE_SEGMENTS,
    DEFAULT_MAX_OPERATOR_REFERENCES,
    REFERENCE_PREVIEW_SCHEMA_VERSION,
    REFERENCE_PREVIEW_SPEC_ID,
    REFERENCE_PREVIEW_SPEC_VERSION,
    REFERENCE_RECOGNITION_RULESET_ID,
    RsocOperatorReferenceNode,
    RsocReferenceBoundary,
    RsocReferenceDocument,
    RsocReferencePreviewLimits,
    RsocReferencePreviewResult,
    RsocReferencePreviewStatus,
    SourceCoverageKind,
    SourceCoverageSegment,
)

_ASCII_SEPARATORS = frozenset((" ", "\t", "\r", "\n"))


def build_reference_preview_limits(
    *,
    max_operator_references: object = DEFAULT_MAX_OPERATOR_REFERENCES,
    max_coverage_segments: object = DEFAULT_MAX_COVERAGE_SEGMENTS,
) -> RsocReferencePreviewLimits | None:
    if type(max_operator_references) is not int:
        return None
    if type(max_coverage_segments) is not int:
        return None
    if not 1 <= max_operator_references <= ABSOLUTE_MAX_OPERATOR_REFERENCES:
        return None
    if not 1 <= max_coverage_segments <= ABSOLUTE_MAX_COVERAGE_SEGMENTS:
        return None
    body = {
        "max_operator_references": max_operator_references,
        "max_coverage_segments": max_coverage_segments,
        "spec_id": REFERENCE_PREVIEW_SPEC_ID,
        "spec_version": REFERENCE_PREVIEW_SPEC_VERSION,
        "schema_version": REFERENCE_PREVIEW_SCHEMA_VERSION,
    }
    return RsocReferencePreviewLimits(
        limits_id=stable_record_id("rsoc_reference_preview_limits", body),
        **body,
    )


def default_reference_preview_limits() -> RsocReferencePreviewLimits:
    limits = build_reference_preview_limits()
    assert limits is not None
    return limits


def build_reference_boundary(
    *,
    recognition_performed: bool = True,
) -> RsocReferenceBoundary:
    return RsocReferenceBoundary(
        read_only=True,
        registry_reference_only=True,
        exact_glyph_recognition_performed=recognition_performed,
        natural_language_tokenization_performed=False,
        word_tokenization_performed=False,
        subword_tokenization_performed=False,
        normalization_performed=False,
        casefolding_performed=False,
        vocabulary_lookup_performed=False,
        concept_lookup_performed=False,
        predicate_binding_performed=False,
        reference_resolution_performed=False,
        authoritative_expression_grammar_installed=False,
        source_binding_performed=False,
        operator_occurrence_created=False,
        operator_application_performed=False,
        numeric_transform_performed=False,
        entropy_mutation_performed=False,
        successor_field_created=False,
        phase_assignment_performed=False,
        meaning_created=False,
        permission_inferred=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        environment_access_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        identity_vault_write_performed=False,
        route_registration_performed=False,
        model_call_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        delivery_performed=False,
    )


def _result(
    *,
    status: RsocReferencePreviewStatus,
    reason_code: str,
    source_event_id: str = "",
    source_sha256: str = "",
    projection_id: str = "",
    registry_id: str = "",
    unicode_database_version: str = "",
    limits: RsocReferencePreviewLimits | None = None,
    coverage: tuple[SourceCoverageSegment, ...] = (),
    references: tuple[RsocOperatorReferenceNode, ...] = (),
    document: RsocReferenceDocument | None = None,
    separator_segment_count: int = 0,
    unrecognized_segment_count: int = 0,
    unresolved_code_point_count: int = 0,
    scan_complete: bool = False,
    full_source_coverage: bool = False,
    exact_reconstruction_proven: bool = False,
    validation_issue_codes: tuple[str, ...] = (),
    recognition_performed: bool = False,
) -> RsocReferencePreviewResult:
    boundary = build_reference_boundary(
        recognition_performed=recognition_performed,
    )
    body = {
        "status": status,
        "reason_code": reason_code,
        "ready": status is RsocReferencePreviewStatus.REFERENCE_PREVIEW_READY,
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "projection_id": projection_id,
        "registry_id": registry_id,
        "unicode_database_version": unicode_database_version,
        "limits": limits,
        "coverage": coverage,
        "operator_references": references,
        "document": document,
        "recognized_operator_count": len(references),
        "separator_segment_count": separator_segment_count,
        "unrecognized_segment_count": unrecognized_segment_count,
        "unresolved_code_point_count": unresolved_code_point_count,
        "scan_complete": scan_complete,
        "full_source_coverage": full_source_coverage,
        "exact_reconstruction_proven": exact_reconstruction_proven,
        "validation_issue_codes": validation_issue_codes,
        "boundary": boundary,
        "ruleset_id": REFERENCE_RECOGNITION_RULESET_ID,
        "spec_id": REFERENCE_PREVIEW_SPEC_ID,
        "spec_version": REFERENCE_PREVIEW_SPEC_VERSION,
        "schema_version": REFERENCE_PREVIEW_SCHEMA_VERSION,
    }
    return RsocReferencePreviewResult(
        result_id=stable_record_id("rsoc_reference_preview_result", body),
        **body,
    )


def _segment(
    *,
    ordinal: int,
    kind: SourceCoverageKind,
    start: int,
    end: int,
    event,
    atoms,
    operator_contract_id: str = "",
    issue_code: str = "",
) -> SourceCoverageSegment:
    span_result = build_source_span(
        event,
        code_point_start=start,
        code_point_end=end,
    )
    if not span_result.ok or span_result.span is None:
        raise ValueError("source_span_build_failed")
    span = span_result.span
    body = {
        "ordinal": ordinal,
        "kind": kind,
        "exact_text": event.exact_received_text[start:end],
        "utf8_hex": event.exact_received_text[start:end].encode("utf-8").hex(),
        "code_point_start": start,
        "code_point_end": end,
        "utf8_byte_start": span.utf8_byte_start,
        "utf8_byte_end": span.utf8_byte_end,
        "source_span_id": span.span_id,
        "atom_ids": tuple(atom.atom_id for atom in atoms[start:end]),
        "operator_contract_id": operator_contract_id,
        "issue_code": issue_code,
        "ruleset_id": REFERENCE_RECOGNITION_RULESET_ID,
        "spec_id": REFERENCE_PREVIEW_SPEC_ID,
        "spec_version": REFERENCE_PREVIEW_SPEC_VERSION,
        "schema_version": REFERENCE_PREVIEW_SCHEMA_VERSION,
    }
    return SourceCoverageSegment(
        segment_id=stable_record_id("rsoc_source_coverage_segment", body),
        **body,
    )


def _matches(atoms, start: int, glyph_code_points: tuple[str, ...]) -> bool:
    end = start + len(glyph_code_points)
    if end > len(atoms):
        return False
    return tuple(atom.exact_text for atom in atoms[start:end]) == glyph_code_points


def _operator_at(atoms, start: int, ordered_operators):
    for contract, glyph_code_points in ordered_operators:
        if _matches(atoms, start, glyph_code_points):
            return contract, glyph_code_points
    return None


def preview_rsoc_operator_references(
    custody: object,
    projection: object,
    registry: object = None,
    *,
    limits: object = None,
) -> RsocReferencePreviewResult:
    """Recognize exact registered glyph sequences without applying them."""

    selected_limits = default_reference_preview_limits() if limits is None else limits
    if (
        type(selected_limits) is not RsocReferencePreviewLimits
        or selected_limits.limits_id != selected_limits.expected_id()
        or not 1 <= selected_limits.max_operator_references <= ABSOLUTE_MAX_OPERATOR_REFERENCES
        or not 1 <= selected_limits.max_coverage_segments <= ABSOLUTE_MAX_COVERAGE_SEGMENTS
    ):
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_LIMITS,
            reason_code="invalid_reference_preview_limits",
            validation_issue_codes=("invalid_reference_preview_limits",),
        )

    if type(custody) is not InputEventCaptureResult:
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_CUSTODY,
            reason_code="invalid_custody_result_type",
            limits=selected_limits,
            validation_issue_codes=("invalid_custody_result_type",),
        )
    custody_report = validate_input_event_capture_result(custody)
    if not custody_report.ok or custody.event is None:
        custody_issue_codes = tuple(
            issue.code for issue in custody_report.issues
        ) or (custody.reason_code,)
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_CUSTODY,
            reason_code="invalid_or_missing_custody_event",
            limits=selected_limits,
            validation_issue_codes=custody_issue_codes,
        )
    if custody.status is InputCustodyStatus.CAPTURED_UNSUPPORTED:
        return _result(
            status=RsocReferencePreviewStatus.HELD_UNSUPPORTED_SOURCE,
            reason_code="unsupported_source_preserved_but_not_scanned",
            source_event_id=custody.event.input_event_id,
            source_sha256=custody.event.source_sha256,
            unicode_database_version=custody.event.unicode_database_version,
            limits=selected_limits,
            validation_issue_codes=tuple(condition.code.value for condition in custody.conditions),
        )
    if custody.status is not InputCustodyStatus.CAPTURED_SUPPORTED:
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_CUSTODY,
            reason_code="custody_not_supported_for_scan",
            limits=selected_limits,
            validation_issue_codes=(custody.reason_code,),
        )

    if type(projection) is not SourceFieldProjectionResult:
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_PROJECTION,
            reason_code="invalid_projection_result_type",
            source_event_id=custody.event.input_event_id,
            source_sha256=custody.event.source_sha256,
            unicode_database_version=custody.event.unicode_database_version,
            limits=selected_limits,
            validation_issue_codes=("invalid_projection_result_type",),
        )
    projection_report = validate_source_field_projection_result(projection)
    if (
        not projection_report.ok
        or projection.projection is None
        or projection.status is not SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED
    ):
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_PROJECTION,
            reason_code="projection_not_valid_supported_source",
            source_event_id=custody.event.input_event_id,
            source_sha256=custody.event.source_sha256,
            unicode_database_version=custody.event.unicode_database_version,
            limits=selected_limits,
            validation_issue_codes=(
                tuple(issue.code for issue in projection_report.issues)
                or (projection.reason_code,)
            ),
        )
    projected = projection.projection
    if (
        projected.source_event_id != custody.event.input_event_id
        or projected.source_sha256 != custody.event.source_sha256
        or not projected.exact_reconstruction_proven
    ):
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_PROJECTION,
            reason_code="projection_source_binding_mismatch",
            source_event_id=custody.event.input_event_id,
            source_sha256=custody.event.source_sha256,
            projection_id=projected.projection_id,
            unicode_database_version=custody.event.unicode_database_version,
            limits=selected_limits,
            validation_issue_codes=("projection_source_binding_mismatch",),
        )

    selected_registry = (
        build_default_rsoc_operator_registry() if registry is None else registry
    )
    if type(selected_registry) is not RsocLanguageOperatorRegistry:
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_REGISTRY,
            reason_code="invalid_operator_registry_type",
            source_event_id=custody.event.input_event_id,
            source_sha256=custody.event.source_sha256,
            projection_id=projected.projection_id,
            unicode_database_version=custody.event.unicode_database_version,
            limits=selected_limits,
            validation_issue_codes=("invalid_operator_registry_type",),
        )
    registry_report = validate_rsoc_language_operator_registry(selected_registry)
    if not registry_report.ok:
        return _result(
            status=RsocReferencePreviewStatus.HELD_INVALID_REGISTRY,
            reason_code="invalid_operator_registry",
            source_event_id=custody.event.input_event_id,
            source_sha256=custody.event.source_sha256,
            projection_id=projected.projection_id,
            registry_id=selected_registry.registry_id,
            unicode_database_version=custody.event.unicode_database_version,
            limits=selected_limits,
            validation_issue_codes=tuple(issue.code for issue in registry_report.issues),
        )

    atoms = projected.code_points
    ordered_operators = tuple(
        sorted(
            (
                (contract, tuple(contract.glyph))
                for contract in selected_registry.operators
            ),
            key=lambda item: (-len(item[1]), item[0].operator_key),
        )
    )
    coverage: list[SourceCoverageSegment] = []
    references: list[RsocOperatorReferenceNode] = []
    index = 0
    separator_count = 0
    unrecognized_count = 0
    unresolved_code_points = 0
    scan_complete = True

    while index < len(atoms):
        if (
            len(coverage) >= selected_limits.max_coverage_segments - 1
            and index < len(atoms)
        ):
            coverage.append(
                _segment(
                    ordinal=len(coverage),
                    kind=SourceCoverageKind.LIMIT_REMAINDER,
                    start=index,
                    end=len(atoms),
                    event=custody.event,
                    atoms=atoms,
                    issue_code="coverage_segment_limit_exceeded",
                )
            )
            unresolved_code_points += len(atoms) - index
            scan_complete = False
            index = len(atoms)
            break

        matched = _operator_at(atoms, index, ordered_operators)
        if matched is not None:
            contract, glyph_code_points = matched
            if len(references) >= selected_limits.max_operator_references:
                coverage.append(
                    _segment(
                        ordinal=len(coverage),
                        kind=SourceCoverageKind.LIMIT_REMAINDER,
                        start=index,
                        end=len(atoms),
                        event=custody.event,
                        atoms=atoms,
                        issue_code="operator_reference_limit_exceeded",
                    )
                )
                unresolved_code_points += len(atoms) - index
                scan_complete = False
                index = len(atoms)
                break
            end = index + len(glyph_code_points)
            segment = _segment(
                ordinal=len(coverage),
                kind=SourceCoverageKind.OPERATOR_REFERENCE,
                start=index,
                end=end,
                event=custody.event,
                atoms=atoms,
                operator_contract_id=contract.contract_id,
            )
            coverage.append(segment)
            node_body = {
                "ordinal": len(references),
                "operator_key": contract.operator_key,
                "glyph": contract.glyph,
                "canonical_name": contract.canonical_name,
                "declared_arity": contract.arity.value,
                "registry_id": selected_registry.registry_id,
                "operator_contract_id": contract.contract_id,
                "runtime_status": contract.runtime_status.value,
                "coverage_segment_id": segment.segment_id,
                "source_span_id": segment.source_span_id,
                "atom_ids": segment.atom_ids,
                "code_point_start": segment.code_point_start,
                "code_point_end": segment.code_point_end,
                "utf8_byte_start": segment.utf8_byte_start,
                "utf8_byte_end": segment.utf8_byte_end,
                "exact_glyph_recognition_performed": True,
                "registry_reference_only": True,
                "source_binding_performed": False,
                "operator_application_performed": False,
                "numeric_transform_performed": False,
                "entropy_mutation_performed": False,
                "phase_assignment_performed": False,
                "meaning_created": False,
                "permission_inferred": False,
                "ruleset_id": REFERENCE_RECOGNITION_RULESET_ID,
                "spec_id": REFERENCE_PREVIEW_SPEC_ID,
                "spec_version": REFERENCE_PREVIEW_SPEC_VERSION,
                "schema_version": REFERENCE_PREVIEW_SCHEMA_VERSION,
            }
            references.append(
                RsocOperatorReferenceNode(
                    reference_id=stable_record_id("rsoc_operator_reference", node_body),
                    **node_body,
                )
            )
            index = end
            continue

        if atoms[index].exact_text in _ASCII_SEPARATORS:
            end = index + 1
            while end < len(atoms) and atoms[end].exact_text in _ASCII_SEPARATORS:
                end += 1
            coverage.append(
                _segment(
                    ordinal=len(coverage),
                    kind=SourceCoverageKind.ASCII_SEPARATOR,
                    start=index,
                    end=end,
                    event=custody.event,
                    atoms=atoms,
                )
            )
            separator_count += 1
            index = end
            continue

        end = index + 1
        while end < len(atoms):
            if atoms[end].exact_text in _ASCII_SEPARATORS:
                break
            if _operator_at(atoms, end, ordered_operators) is not None:
                break
            end += 1
        coverage.append(
            _segment(
                ordinal=len(coverage),
                kind=SourceCoverageKind.UNRECOGNIZED,
                start=index,
                end=end,
                event=custody.event,
                atoms=atoms,
                issue_code="unrecognized_exact_source_material",
            )
        )
        unrecognized_count += 1
        unresolved_code_points += end - index
        index = end

    full_coverage = bool(coverage) and coverage[0].code_point_start == 0
    expected_start = 0
    for segment in coverage:
        if segment.code_point_start != expected_start:
            full_coverage = False
            break
        expected_start = segment.code_point_end
    full_coverage = full_coverage and expected_start == len(atoms)

    common = {
        "source_event_id": custody.event.input_event_id,
        "source_sha256": custody.event.source_sha256,
        "projection_id": projected.projection_id,
        "registry_id": selected_registry.registry_id,
        "unicode_database_version": projected.unicode_database_version,
        "limits": selected_limits,
        "coverage": tuple(coverage),
        "references": tuple(references),
        "separator_segment_count": separator_count,
        "unrecognized_segment_count": unrecognized_count,
        "unresolved_code_point_count": unresolved_code_points,
        "scan_complete": scan_complete,
        "full_source_coverage": full_coverage,
        "exact_reconstruction_proven": projected.exact_reconstruction_proven,
        "recognition_performed": True,
    }
    if not scan_complete:
        return _result(
            status=RsocReferencePreviewStatus.HELD_PREVIEW_LIMIT_EXCEEDED,
            reason_code="reference_preview_limit_exceeded",
            validation_issue_codes=("reference_preview_limit_exceeded",),
            **common,
        )
    if not references:
        return _result(
            status=RsocReferencePreviewStatus.HELD_NO_OPERATOR_REFERENCE,
            reason_code="no_exact_registered_operator_reference",
            validation_issue_codes=("no_exact_registered_operator_reference",),
            **common,
        )
    if unrecognized_count:
        return _result(
            status=RsocReferencePreviewStatus.HELD_UNCONSUMED_SOURCE,
            reason_code="unrecognized_source_material_held",
            validation_issue_codes=("unrecognized_exact_source_material",),
            **common,
        )

    document_body = {
        "source_event_id": custody.event.input_event_id,
        "source_sha256": custody.event.source_sha256,
        "projection_id": projected.projection_id,
        "registry_id": selected_registry.registry_id,
        "coverage_segment_ids": tuple(item.segment_id for item in coverage),
        "operator_reference_ids": tuple(item.reference_id for item in references),
        "operator_reference_count": len(references),
        "separator_segment_count": separator_count,
        "full_source_coverage": full_coverage,
        "full_input_consumed": full_coverage,
        "exact_reconstruction_proven": projected.exact_reconstruction_proven,
        "registry_reference_sequence_created": True,
        "composition_interpreted": False,
        "arguments_bound": False,
        "source_binding_performed": False,
        "operator_application_performed": False,
        "successor_field_created": False,
        "phase_assigned": False,
        "meaning_created": False,
        "ruleset_id": REFERENCE_RECOGNITION_RULESET_ID,
        "spec_id": REFERENCE_PREVIEW_SPEC_ID,
        "spec_version": REFERENCE_PREVIEW_SPEC_VERSION,
        "schema_version": REFERENCE_PREVIEW_SCHEMA_VERSION,
    }
    document = RsocReferenceDocument(
        document_id=stable_record_id("rsoc_reference_document", document_body),
        **document_body,
    )
    return _result(
        status=RsocReferencePreviewStatus.REFERENCE_PREVIEW_READY,
        reason_code="exact_registered_operator_references_recognized",
        document=document,
        validation_issue_codes=(),
        **common,
    )
