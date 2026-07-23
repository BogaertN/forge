"""Explicit in-memory Slice 46 equivalence proof runner."""
from __future__ import annotations

from dataclasses import replace
import importlib
import sys
from typing import Any, Callable

from .authority import (
    ACCEPTED_PARENT_HEAD,
    ACCEPTED_PARENT_TREE,
    ADAPTER_MODULE,
    DIRECT_SOURCE_MODULE,
    GP014_MODULE,
    GP015_MODULE,
)
from .canonical import canonical_json_bytes
from .comparison import compare_case
from .fixtures import EQUIVALENCE_FIXTURES
from .schema import BoundaryFailureResult, EquivalenceProofReport
from .validation import validate_report


def _boundary_failure(
    *,
    label: str,
    expected_status: str,
    marker: str,
    first: Any,
    second: Any,
    expected_called: bool,
    expected_source_present: bool,
) -> BoundaryFailureResult:
    first_bytes = canonical_json_bytes(first.to_dict())
    second_bytes = canonical_json_bytes(second.to_dict())
    receipt = first.receipt
    value = BoundaryFailureResult(
        failure_id="pending",
        label=label,
        adapter_status=first.status,
        reason_code=first.reason_code,
        expected_status=expected_status,
        raw_marker=marker,
        raw_marker_exposed=(bool(marker) and marker.encode("utf-8") in first_bytes),
        raw_exception_exposed_flag=receipt.raw_exception_exposed,
        gp014_called=receipt.gp014_called,
        source_result_present=first.source_result is not None,
        deterministic_replay=(first.result_id == second.result_id and first.receipt.receipt_id == second.receipt.receipt_id and first_bytes == second_bytes),
        passed=(
            first.status == expected_status
            and second.status == expected_status
            and receipt.gp014_called is expected_called
            and (first.source_result is not None) is expected_source_present
            and (not marker or marker.encode("utf-8") not in first_bytes)
            and receipt.raw_exception_exposed is False
        ),
    )
    return replace(value, failure_id=value.expected_id())


def run_equivalence_proof() -> EquivalenceProofReport:
    adapter_module = importlib.import_module(ADAPTER_MODULE)
    gp014_before = GP014_MODULE in sys.modules
    gp015_before = GP015_MODULE in sys.modules

    first_fixture = EQUIVALENCE_FIXTURES[0]
    disabled_request = adapter_module.build_gp014_adapter_request(first_fixture.question)
    disabled = adapter_module.run_gp014_adapter(disabled_request)
    gp014_imported_before_enable = (GP014_MODULE in sys.modules) and not gp014_before

    tampered = replace(disabled_request, question_sha256="0" * 64)
    enabled_state = adapter_module.build_gp014_adapter_state(explicit_offline_developer_enable=True)
    invalid_request = adapter_module.run_gp014_adapter(tampered, state=enabled_state)

    direct_module = importlib.import_module(DIRECT_SOURCE_MODULE)
    direct_answer: Callable[[str], Any] = getattr(direct_module, "answer_symbolic_math_language_request")

    cases = []
    for fixture in EQUIVALENCE_FIXTURES:
        direct_first = direct_answer(fixture.question)
        direct_second = direct_answer(fixture.question)
        request = adapter_module.build_gp014_adapter_request(fixture.question)
        adapter_first = adapter_module.run_gp014_adapter(request, state=enabled_state)
        adapter_second = adapter_module.run_gp014_adapter(request, state=enabled_state)
        cases.append(compare_case(
            fixture=fixture,
            direct_first=direct_first,
            direct_second=direct_second,
            adapter_first=adapter_first,
            adapter_second=adapter_second,
        ))

    original_loader = adapter_module.load_gp014_runtime_binding
    failures = []
    try:
        marker = "SLICE46_BINDING_SECRET"
        def binding_failure() -> Any:
            raise RuntimeError(marker)
        adapter_module.load_gp014_runtime_binding = binding_failure
        request = adapter_module.build_gp014_adapter_request(first_fixture.question)
        first = adapter_module.run_gp014_adapter(request, state=enabled_state)
        second = adapter_module.run_gp014_adapter(request, state=enabled_state)
        failures.append(_boundary_failure(
            label="binding_identity_failure",
            expected_status=adapter_module.STATUS_HELD_GP014_IDENTITY,
            marker=marker,
            first=first,
            second=second,
            expected_called=False,
            expected_source_present=False,
        ))

        real_binding = original_loader()
        marker = "SLICE46_SOURCE_SECRET"
        def source_failure(_: str) -> Any:
            raise RuntimeError(marker)
        binding_type = type(real_binding)
        failing_binding = binding_type(identity=real_binding.identity, answer=source_failure)
        adapter_module.load_gp014_runtime_binding = lambda: failing_binding
        first = adapter_module.run_gp014_adapter(request, state=enabled_state)
        second = adapter_module.run_gp014_adapter(request, state=enabled_state)
        failures.append(_boundary_failure(
            label="source_exception_failure",
            expected_status=adapter_module.STATUS_CONTAINED_SOURCE_FAILURE,
            marker=marker,
            first=first,
            second=second,
            expected_called=True,
            expected_source_present=False,
        ))

        marker = ""
        class InvalidSourceResult:
            status = "ANSWERED"
            question = first_fixture.question
            answer_text = marker
            trace: dict[str, Any] = {}
            def to_dict(self) -> dict[str, Any]:
                return {"status": self.status, "question": self.question, "answer_text": self.answer_text, "trace": self.trace}
            def result_hash(self) -> str:
                return "1" * 64
        invalid_binding = binding_type(identity=real_binding.identity, answer=lambda _: InvalidSourceResult())
        adapter_module.load_gp014_runtime_binding = lambda: invalid_binding
        first = adapter_module.run_gp014_adapter(request, state=enabled_state)
        second = adapter_module.run_gp014_adapter(request, state=enabled_state)
        failures.append(_boundary_failure(
            label="invalid_source_result_failure",
            expected_status=adapter_module.STATUS_HELD_GP014_RESULT,
            marker=marker,
            first=first,
            second=second,
            expected_called=True,
            expected_source_present=True,
        ))
    finally:
        adapter_module.load_gp014_runtime_binding = original_loader

    gp015_after = GP015_MODULE in sys.modules
    case_tuple = tuple(cases)
    failure_tuple = tuple(failures)
    positive = tuple(item for item in case_tuple if item.expected_class == "ANSWERED")
    negative = tuple(item for item in case_tuple if item.expected_class == "CONTAINED")

    all_equivalent = all(item.all_dimensions_equivalent for item in case_tuple)
    all_replay = all(item.direct_replay_deterministic and item.adapter_replay_deterministic for item in case_tuple)
    no_authority = all(not item.adapter_added_authority for item in case_tuple)
    value = EquivalenceProofReport(
        report_id="pending",
        accepted_parent_head=ACCEPTED_PARENT_HEAD,
        accepted_parent_tree=ACCEPTED_PARENT_TREE,
        direct_binding_module=DIRECT_SOURCE_MODULE,
        adapter_binding_module=ADAPTER_MODULE,
        gp014_imported_before_explicit_enable=gp014_imported_before_enable,
        gp015_loaded_before=gp015_before,
        gp015_loaded_after=gp015_after,
        disabled_adapter_status=disabled.status,
        disabled_adapter_called_gp014=disabled.receipt.gp014_called,
        invalid_request_status=invalid_request.status,
        invalid_request_called_gp014=invalid_request.receipt.gp014_called,
        cases=case_tuple,
        boundary_failures=failure_tuple,
        positive_case_count=len(positive),
        negative_case_count=len(negative),
        total_case_count=len(case_tuple),
        all_cases_equivalent=all_equivalent,
        all_replays_deterministic=all_replay,
        all_boundary_failures_contained=all(item.passed for item in failure_tuple),
        accepted_input_equivalent=all(item.request_forwarded_byte_for_byte for item in case_tuple),
        computation_equivalent=all(item.all_dimensions_equivalent for item in positive),
        expression_equivalent=all(item.all_dimensions_equivalent for item in positive),
        validation_equivalent=all(item.all_dimensions_equivalent for item in positive),
        accepted_failure_behavior_equivalent=all(item.all_dimensions_equivalent for item in negative),
        no_gp014_modification=all(not item.gp014_modified for item in case_tuple),
        no_gp014_supersession=all(not item.gp014_superseded for item in case_tuple),
        no_gp015_reuse=(not gp015_after or gp015_before) and all(not item.gp015_used for item in case_tuple),
        no_route_api_ui_authority=no_authority,
        no_memory_tool_action_resource_authority=no_authority,
        no_adapter_delivery_authority=no_authority,
        production_ready=False,
        release_authorized=False,
    )
    value = replace(value, report_id=value.expected_id())
    report = validate_report(value)
    if not report.ok:
        details = "; ".join(f"{issue.path}:{issue.code.value}:{issue.detail}" for issue in report.issues)
        raise RuntimeError("slice46_equivalence_proof_invalid: " + details)
    return value


__all__ = ("run_equivalence_proof",)
