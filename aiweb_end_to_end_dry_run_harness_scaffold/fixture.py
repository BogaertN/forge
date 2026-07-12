"""Offline deterministic fixtures for Slice 23.

The fixtures in this module are data records only. They do not read files,
write files, register routes, call tools, call models, fetch resources,
write memory, deliver output, or execute actions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final

from .authority import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    stable_record_id,
)

SAFE_DISPLAY_FIXTURE_KEY: Final[str] = "safe_display_fixture"
BLOCKED_ACTION_FIXTURE_KEY: Final[str] = "blocked_action_fixture"

ALLOWED_FIXTURE_KEYS: Final[tuple[str, ...]] = (
    SAFE_DISPLAY_FIXTURE_KEY,
    BLOCKED_ACTION_FIXTURE_KEY,
)

ALLOWED_EXPECTED_OUTCOMES: Final[tuple[str, ...]] = (
    "display_only_evidence_chain_boundary",
    "blocked_before_memory_delivery_or_action_boundary",
)


@dataclass(frozen=True, slots=True)
class DryRunFixtureRecord:
    fixture_id: str
    fixture_key: str
    input_text: str
    expected_outcome: str
    expected_gate_status: str
    expected_selection_status: str
    expected_expression_status: str
    expected_block_reason: str
    offline_only: bool
    deterministic: bool
    source_kind: str
    version_tag: str = "v1"
    live_runtime_behavior: bool = False
    live_runtime_interpretation: bool = False
    public_capability: bool = False
    fixture_as_public_capability: bool = False
    memory_write: bool = False
    memory_authority: bool = False
    external_resource_admission: bool = False
    external_resource_promotion: bool = False
    resource_fetch: bool = False
    resource_download: bool = False
    resource_ingestion: bool = False
    resource_parsing: bool = False
    resource_indexing: bool = False
    delivery_action: bool = False
    delivery_authority: bool = False
    action_authorization: bool = False
    action_execution: bool = False
    tool_routing: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    permission_grant: bool = False
    truth_decision: bool = False
    selected_meaning_finalization: bool = False
    final_meaning_selection: bool = False
    output_approval: bool = False
    user_facing_output_authorized: bool = False
    route_registration_authorized: bool = False
    ui_integration_authorized: bool = False
    config_mutation_authorized: bool = False
    network_io: bool = False
    shell_execution: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False
    similarity_authority: bool = False
    embedding_index_creation: bool = False
    rag_execution: bool = False
    gp014_import: bool = False
    gp014_call: bool = False
    gp014_wrap: bool = False
    gp014_promotion: bool = False
    gp014_supersession: bool = False
    gp015_repair: bool = False
    gp015_revival: bool = False
    production_readiness: bool = False
    release_authority: bool = False

    def canonical_body(self) -> dict[str, object]:
        return {
            "fixture_key": self.fixture_key,
            "input_text": self.input_text,
            "expected_outcome": self.expected_outcome,
            "expected_gate_status": self.expected_gate_status,
            "expected_selection_status": self.expected_selection_status,
            "expected_expression_status": self.expected_expression_status,
            "expected_block_reason": self.expected_block_reason,
            "offline_only": self.offline_only,
            "deterministic": self.deterministic,
            "source_kind": self.source_kind,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice23-fixture", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_safe_display_fixture() -> DryRunFixtureRecord:
    body = {
        "fixture_key": SAFE_DISPLAY_FIXTURE_KEY,
        "input_text": "Show the evidence chain for this dry-run fixture without changing anything.",
        "expected_outcome": "display_only_evidence_chain_boundary",
        "expected_gate_status": "display_only_gate_boundary",
        "expected_selection_status": "selected_state_candidate_boundary_recorded_not_final",
        "expected_expression_status": "unapproved_expression_preview_boundary",
        "expected_block_reason": "no_block_display_only_boundary",
        "offline_only": True,
        "deterministic": True,
        "source_kind": "local_literal_fixture",
        "version_tag": "v1",
    }
    return DryRunFixtureRecord(fixture_id=stable_record_id("slice23-fixture", body), **body)


def build_blocked_action_fixture() -> DryRunFixtureRecord:
    body = {
        "fixture_key": BLOCKED_ACTION_FIXTURE_KEY,
        "input_text": "Remember this, send it, and execute the action after the dry run.",
        "expected_outcome": "blocked_before_memory_delivery_or_action_boundary",
        "expected_gate_status": "blocked_action_gate_boundary",
        "expected_selection_status": "selection_blocked_boundary",
        "expected_expression_status": "blocked_expression_preview_boundary",
        "expected_block_reason": "memory_delivery_and_action_intent_blocked_by_slice23_boundary",
        "offline_only": True,
        "deterministic": True,
        "source_kind": "local_literal_fixture",
        "version_tag": "v1",
    }
    return DryRunFixtureRecord(fixture_id=stable_record_id("slice23-fixture", body), **body)


def build_default_fixtures() -> tuple[DryRunFixtureRecord, ...]:
    return (build_safe_display_fixture(), build_blocked_action_fixture())


def validate_fixture_record(record: DryRunFixtureRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.fixture_key not in ALLOWED_FIXTURE_KEYS:
        issues.append(ValidationIssue("fixture_key", "unsupported_fixture_key"))
    if record.expected_outcome not in ALLOWED_EXPECTED_OUTCOMES:
        issues.append(ValidationIssue("expected_outcome", "unsupported_expected_outcome"))
    if not record.input_text.strip():
        issues.append(ValidationIssue("input_text", "input_text_required"))
    if record.offline_only is not True:
        issues.append(ValidationIssue("offline_only", "fixture_must_remain_offline_only"))
    if record.deterministic is not True:
        issues.append(ValidationIssue("deterministic", "fixture_must_remain_deterministic"))
    if record.source_kind != "local_literal_fixture":
        issues.append(ValidationIssue("source_kind", "fixture_must_remain_local_literal"))
    if record.fixture_id != record.expected_id():
        issues.append(ValidationIssue("fixture_id", "stable_identifier_mismatch"))
    for field_name in DOWNSTREAM_FALSE_ONLY_FIELDS:
        if bool(getattr(record, field_name)):
            issues.append(ValidationIssue(field_name, "must_remain_false_for_fixture"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))
