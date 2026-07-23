"""Immutable proof records for Slice 46."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .authority import SLICE46_SCHEMA_VERSION
from .canonical import canonical_value, stable_identifier


@dataclass(frozen=True, slots=True)
class EquivalenceFixture:
    fixture_id: str
    label: str
    question: str
    expected_class: str
    expected_source_status: str
    expected_operation_family: str | None
    schema_version: str = SLICE46_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice46_fixture", self, excluded_fields=("fixture_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class DimensionResult:
    dimension: str
    direct_value_digest: str
    adapter_value_digest: str
    equivalent: bool
    schema_version: str = SLICE46_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class EquivalenceCaseResult:
    case_id: str
    fixture_id: str
    expected_class: str
    direct_status: str
    adapter_status: str
    operation_family: str | None
    direct_result_hash: str
    adapter_source_result_hash: str
    dimension_results: tuple[DimensionResult, ...]
    dimension_count: int
    all_dimensions_equivalent: bool
    direct_replay_deterministic: bool
    adapter_replay_deterministic: bool
    request_forwarded_byte_for_byte: bool
    adapter_source_returned_unchanged: bool
    adapter_added_authority: bool
    gp014_modified: bool
    gp014_superseded: bool
    gp015_used: bool
    delivery_equivalent_within_source_scope: bool
    schema_version: str = SLICE46_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice46_equivalence_case", self, excluded_fields=("case_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class BoundaryFailureResult:
    failure_id: str
    label: str
    adapter_status: str
    reason_code: str
    expected_status: str
    raw_marker: str
    raw_marker_exposed: bool
    raw_exception_exposed_flag: bool
    gp014_called: bool
    source_result_present: bool
    deterministic_replay: bool
    passed: bool
    schema_version: str = SLICE46_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice46_boundary_failure", self, excluded_fields=("failure_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class EquivalenceProofReport:
    report_id: str
    accepted_parent_head: str
    accepted_parent_tree: str
    direct_binding_module: str
    adapter_binding_module: str
    gp014_imported_before_explicit_enable: bool
    gp015_loaded_before: bool
    gp015_loaded_after: bool
    disabled_adapter_status: str
    disabled_adapter_called_gp014: bool
    invalid_request_status: str
    invalid_request_called_gp014: bool
    cases: tuple[EquivalenceCaseResult, ...]
    boundary_failures: tuple[BoundaryFailureResult, ...]
    positive_case_count: int
    negative_case_count: int
    total_case_count: int
    all_cases_equivalent: bool
    all_replays_deterministic: bool
    all_boundary_failures_contained: bool
    accepted_input_equivalent: bool
    computation_equivalent: bool
    expression_equivalent: bool
    validation_equivalent: bool
    accepted_failure_behavior_equivalent: bool
    no_gp014_modification: bool
    no_gp014_supersession: bool
    no_gp015_reuse: bool
    no_route_api_ui_authority: bool
    no_memory_tool_action_resource_authority: bool
    no_adapter_delivery_authority: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = SLICE46_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice46_equivalence_report", self, excluded_fields=("report_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


__all__ = (
    "EquivalenceFixture", "DimensionResult", "EquivalenceCaseResult",
    "BoundaryFailureResult", "EquivalenceProofReport",
)
