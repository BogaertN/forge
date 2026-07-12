"""Deterministic receipt for the Slice 23 dry-run harness scaffold."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .authority import (
    REQUIRED_DRY_RUN_LAWS,
    SCHEMA_VERSION,
    SLICE_ID,
    SLICE_TITLE,
    canonical_json,
    sha256_text,
    stable_record_id,
)
from .core import DryRunHarnessRecord, build_demo_harness_record, validate_dry_run_harness_record


@dataclass(frozen=True, slots=True)
class Slice23DryRunReceipt:
    receipt_id: str
    slice_id: str
    title: str
    schema_version: str
    harness_id: str
    harness_digest: str
    verdict: str
    runtime_effect: str
    production_effect: str
    dry_run_laws: tuple[str, ...]
    fixture_count: int
    path_count: int
    boundary_check_count: int
    no_memory_write: bool
    no_external_resource_promotion: bool
    no_delivery: bool
    no_action: bool
    no_tool_route_or_invocation: bool
    no_public_capability: bool

    def canonical_body(self) -> dict[str, object]:
        return {
            "slice_id": self.slice_id,
            "title": self.title,
            "schema_version": self.schema_version,
            "harness_id": self.harness_id,
            "harness_digest": self.harness_digest,
            "verdict": self.verdict,
            "runtime_effect": self.runtime_effect,
            "production_effect": self.production_effect,
            "dry_run_laws": self.dry_run_laws,
            "fixture_count": self.fixture_count,
            "path_count": self.path_count,
            "boundary_check_count": self.boundary_check_count,
            "no_memory_write": self.no_memory_write,
            "no_external_resource_promotion": self.no_external_resource_promotion,
            "no_delivery": self.no_delivery,
            "no_action": self.no_action,
            "no_tool_route_or_invocation": self.no_tool_route_or_invocation,
            "no_public_capability": self.no_public_capability,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice23-dry-run-receipt", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def harness_digest(record: DryRunHarnessRecord) -> str:
    return sha256_text(canonical_json(_canonicalize(record.to_dict())))


def build_receipt(harness: DryRunHarnessRecord | None = None) -> Slice23DryRunReceipt:
    record = harness if harness is not None else build_demo_harness_record()
    validation = validate_dry_run_harness_record(record)
    verdict = "PASS" if validation.passed else "FAIL"
    body = {
        "slice_id": SLICE_ID,
        "title": SLICE_TITLE,
        "schema_version": SCHEMA_VERSION,
        "harness_id": record.harness_id,
        "harness_digest": harness_digest(record),
        "verdict": verdict,
        "runtime_effect": "no_live_runtime_no_state_change_no_memory_write_no_resource_promotion_no_delivery_no_action",
        "production_effect": "no_public_capability_no_route_registration_no_ui_no_config_change_no_deployment",
        "dry_run_laws": REQUIRED_DRY_RUN_LAWS,
        "fixture_count": record.fixture_count,
        "path_count": record.path_count,
        "boundary_check_count": record.boundary_check_count,
        "no_memory_write": True,
        "no_external_resource_promotion": True,
        "no_delivery": True,
        "no_action": True,
        "no_tool_route_or_invocation": True,
        "no_public_capability": True,
    }
    return Slice23DryRunReceipt(receipt_id=stable_record_id("slice23-dry-run-receipt", body), **body)


def validate_receipt(receipt: Slice23DryRunReceipt) -> tuple[str, ...]:
    failures: list[str] = []
    if receipt.slice_id != SLICE_ID:
        failures.append("receipt slice id changed")
    if receipt.title != SLICE_TITLE:
        failures.append("receipt title changed")
    if receipt.schema_version != SCHEMA_VERSION:
        failures.append("receipt schema changed")
    if receipt.verdict != "PASS":
        failures.append("receipt verdict was not PASS")
    if receipt.runtime_effect != "no_live_runtime_no_state_change_no_memory_write_no_resource_promotion_no_delivery_no_action":
        failures.append("receipt runtime effect changed")
    if receipt.production_effect != "no_public_capability_no_route_registration_no_ui_no_config_change_no_deployment":
        failures.append("receipt production effect changed")
    if receipt.dry_run_laws != REQUIRED_DRY_RUN_LAWS:
        failures.append("receipt law set changed")
    for field_name in (
        "no_memory_write",
        "no_external_resource_promotion",
        "no_delivery",
        "no_action",
        "no_tool_route_or_invocation",
        "no_public_capability",
    ):
        if getattr(receipt, field_name) is not True:
            failures.append(field_name + " receipt proof changed")
    if receipt.receipt_id != receipt.expected_id():
        failures.append("receipt stable identifier mismatch")
    return tuple(failures)
