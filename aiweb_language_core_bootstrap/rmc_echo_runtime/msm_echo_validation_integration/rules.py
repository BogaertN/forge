"""Exact Slice 43G source-chain and custody rules."""

from __future__ import annotations

from typing import Iterable

from ..echo_disposition import EchoDisposition
from .authority import VALIDATION_DISPOSITIONS


def unique(values: Iterable[str]) -> tuple[str, ...]:
    ordered: dict[str, None] = {}
    for value in values:
        ordered.setdefault(value, None)
    return tuple(ordered)


def exact_disposition(value) -> EchoDisposition:
    disposition = value.source_43f_disposition_result.disposition
    if disposition is None or disposition.value not in VALIDATION_DISPOSITIONS:
        raise ValueError("exact decided Echo disposition required")
    return disposition


def source_disposition_package(value):
    package = value.source_43f_disposition_result.disposition_package
    if package is None:
        raise ValueError("exact Slice 43F disposition package required")
    return package


def source_disposition_record(value):
    return source_disposition_package(value).disposition_record


def source_expression_link(value):
    return value.source_42g_result.expression_link_record


def source_expression_candidate_ref(value) -> str:
    return source_expression_link(value).expression_candidate_ref


def classification_trace_refs(value) -> tuple[str, ...]:
    package = value.source_43e_classification_result.classification_package
    if package is None:
        return ()
    return unique(
        trace
        for finding in package.drift_findings
        for trace in finding.comparison_trace_refs
    )


def classification_evidence_refs(value) -> tuple[str, ...]:
    package = value.source_43e_classification_result.classification_package
    if package is None:
        return ()
    return unique(
        evidence
        for finding in package.drift_findings
        for evidence in finding.comparison_evidence_refs
    )


def exact_chain_is_proved(value) -> bool:
    expression = source_expression_link(value)
    candidate_ref = source_expression_candidate_ref(value)
    traces = set(classification_trace_refs(value))
    evidence = set(classification_evidence_refs(value))
    disposition_result = value.source_43f_disposition_result
    return (
        disposition_result.classification_result_ref
        == value.source_43e_classification_result.classification_result_id
        and expression.record_id in evidence
        and candidate_ref in evidence
        and value.source_42g_result.outward_to_expression_trace.record_id in traces
    )


def authorized_trace_refs(value) -> tuple[str, ...]:
    package = source_disposition_package(value)
    record = package.disposition_record
    refs = [
        value.source_42g_result.selected_to_outward_trace.record_id,
        value.source_42g_result.outward_to_expression_trace.record_id,
        value.source_42g_result.receipt.receipt_id,
        value.source_43e_classification_result.classification_result_id,
        value.source_43f_disposition_result.disposition_result_id,
        package.disposition_package_id,
        record.disposition_id,
    ]
    if package.rejection_record is not None:
        refs.append(package.rejection_record.rejection_id)
    if package.containment_record is not None:
        refs.append(package.containment_record.containment_id)
    return unique(refs)


def rejection_record_ref(value) -> str | None:
    record = source_disposition_package(value).rejection_record
    return None if record is None else record.rejection_id


def containment_record_ref(value) -> str | None:
    record = source_disposition_package(value).containment_record
    return None if record is None else record.containment_id


__all__ = tuple(name for name in globals() if not name.startswith("_"))
