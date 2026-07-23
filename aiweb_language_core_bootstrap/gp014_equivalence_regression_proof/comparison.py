"""Dimension-by-dimension comparison for direct GP-014 and adapter exposure."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from .authority import ANSWERED_DIMENSIONS, CONTAINED_DIMENSIONS, PROHIBITED_AUTHORITY_FLAGS
from .canonical import deterministic_digest, text_sha256
from .schema import DimensionResult, EquivalenceCaseResult, EquivalenceFixture


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def source_snapshot(result: Any) -> dict[str, Any]:
    trace = _dict(getattr(result, "trace", None))
    compiled = _dict(trace.get("compiled_request"))
    solution = _dict(trace.get("solution"))
    realization = _dict(trace.get("expression_realization_receipt"))
    candidates = realization.get("candidates") if isinstance(realization.get("candidates"), list) else []
    delivery_present = isinstance(trace.get("delivery_authorization_v2"), dict) and isinstance(trace.get("delivery_authorization_v2_hash"), str)
    result_hash = result.result_hash() if callable(getattr(result, "result_hash", None)) else ""
    reasons = getattr(result, "reasons", None)
    return {
        "status": getattr(result, "status", None),
        "question": getattr(result, "question", None),
        "question_sha256": text_sha256(getattr(result, "question", None)),
        "answer_text": getattr(result, "answer_text", None),
        "answer_text_sha256": text_sha256(getattr(result, "answer_text", None)),
        "domain": getattr(result, "domain", None),
        "build_id": getattr(result, "build_id", None),
        "schema_version": getattr(result, "schema_version", None),
        "reasons_digest": deterministic_digest(list(reasons) if isinstance(reasons, list) else reasons),
        "source_result_hash": result_hash,
        "compiled_request_hash": trace.get("compiled_request_hash"),
        "operation_family": compiled.get("operation_family"),
        "operation_manifest_hash": trace.get("symbolic_math_operation_manifest_hash"),
        "kernel_result_digest": deterministic_digest(trace.get("kernel_result")),
        "solution_digest": deterministic_digest(solution),
        "solution_answer_text": solution.get("answer_text"),
        "verification_strength": solution.get("verification_strength"),
        "meaning_hash": trace.get("meaning_hash"),
        "manifest_contract_v2_hash": trace.get("manifest_contract_v2_hash"),
        "expression_realization_receipt_hash": trace.get("expression_realization_receipt_hash"),
        "rendered_text_sha256": text_sha256(trace.get("rendered_text") if isinstance(trace.get("rendered_text"), str) else None),
        "selected_candidate_id": realization.get("selected_candidate_id"),
        "selected_candidate_hash": realization.get("selected_candidate_hash"),
        "candidate_set_digest": deterministic_digest(candidates),
        "echo_hash": trace.get("echo_hash"),
        "delivery_authorization_v2_hash": trace.get("delivery_authorization_v2_hash"),
        "non_delivery_receipt_hash": trace.get("non_delivery_receipt_hash"),
        "delivery_present": delivery_present,
    }


def compare_case(
    *,
    fixture: EquivalenceFixture,
    direct_first: Any,
    direct_second: Any,
    adapter_first: Any,
    adapter_second: Any,
) -> EquivalenceCaseResult:
    adapter_source_first = getattr(adapter_first, "source_result", None)
    adapter_source_second = getattr(adapter_second, "source_result", None)
    direct_snapshot = source_snapshot(direct_first)
    adapter_snapshot = source_snapshot(adapter_source_first)
    dimensions = ANSWERED_DIMENSIONS if fixture.expected_class == "ANSWERED" else CONTAINED_DIMENSIONS
    dimension_rows = tuple(
        DimensionResult(
            dimension=name,
            direct_value_digest=deterministic_digest(direct_snapshot.get(name)),
            adapter_value_digest=deterministic_digest(adapter_snapshot.get(name)),
            equivalent=direct_snapshot.get(name) == adapter_snapshot.get(name),
        )
        for name in dimensions
    )
    receipt = getattr(adapter_first, "receipt", None)
    prohibited = any(bool(getattr(receipt, name, False)) for name in PROHIBITED_AUTHORITY_FLAGS)
    expected_adapter_status = "COMPLETED_GP014_ANSWERED" if fixture.expected_class == "ANSWERED" else "COMPLETED_GP014_CONTAINED"
    direct_replay = (
        callable(getattr(direct_first, "result_hash", None))
        and callable(getattr(direct_second, "result_hash", None))
        and direct_first.result_hash() == direct_second.result_hash()
    )
    adapter_replay = (
        getattr(adapter_first, "result_id", None) == getattr(adapter_second, "result_id", None)
        and getattr(getattr(adapter_first, "receipt", None), "receipt_id", None)
        == getattr(getattr(adapter_second, "receipt", None), "receipt_id", None)
        and adapter_source_first is not None
        and adapter_source_second is not None
        and callable(getattr(adapter_source_first, "result_hash", None))
        and callable(getattr(adapter_source_second, "result_hash", None))
        and adapter_source_first.result_hash() == adapter_source_second.result_hash()
    )
    delivery_equivalent = direct_snapshot["delivery_present"] == adapter_snapshot["delivery_present"]
    value = EquivalenceCaseResult(
        case_id="pending",
        fixture_id=fixture.fixture_id,
        expected_class=fixture.expected_class,
        direct_status=str(direct_snapshot.get("status")),
        adapter_status=str(getattr(adapter_first, "status", "")),
        operation_family=direct_snapshot.get("operation_family"),
        direct_result_hash=str(direct_snapshot.get("source_result_hash") or ""),
        adapter_source_result_hash=str(adapter_snapshot.get("source_result_hash") or ""),
        dimension_results=dimension_rows,
        dimension_count=len(dimension_rows),
        all_dimensions_equivalent=all(row.equivalent for row in dimension_rows),
        direct_replay_deterministic=direct_replay,
        adapter_replay_deterministic=adapter_replay,
        request_forwarded_byte_for_byte=(
            getattr(receipt, "question_forwarded_byte_for_byte", False) is True
            and getattr(receipt, "source_question_sha256", None) == direct_snapshot["question_sha256"]
        ),
        adapter_source_returned_unchanged=(getattr(receipt, "source_result_returned_unchanged", False) is True),
        adapter_added_authority=prohibited,
        gp014_modified=(getattr(receipt, "gp014_modified", True) is True),
        gp014_superseded=(getattr(receipt, "gp014_superseded", True) is True),
        gp015_used=(getattr(receipt, "gp015_used", True) is True),
        delivery_equivalent_within_source_scope=delivery_equivalent,
    )
    # Keep expected statuses and fixture class inside the deterministic identity.
    if value.direct_status != fixture.expected_source_status or value.adapter_status != expected_adapter_status:
        value = replace(value, all_dimensions_equivalent=False)
    return replace(value, case_id=value.expected_id())


__all__ = ("source_snapshot", "compare_case")
