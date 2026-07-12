"""Authority separation records for Slice 23.

Slice 23 is an end-to-end dry-run harness scaffold. It represents an
offline fixture path only. It does not create a live runtime, public
capability, memory event, resource promotion, delivery, tool route, action,
model authority, release authority, route, UI, or config change.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Final, Mapping
import hashlib
import json

SLICE_ID: Final[str] = "Slice 23"
SLICE_TITLE: Final[str] = "End-to-End Dry-Run Harness Scaffold"
SCAFFOLD_VERSION: Final[str] = "1.0.0"
SCHEMA_VERSION: Final[str] = "aiweb-end-to-end-dry-run-harness-scaffold-v1"

REQUIRED_BASE_HEAD_FOR_APPLICATION: Final[str] = "ecbf8c18946f8551d6f78a88b8cd29abe7aacdfc"
REQUIRED_BASE_SUBJECT_FOR_APPLICATION: Final[str] = "Slice 21 read-only inspection surface scaffold"
REQUIRED_BASE_PARENT_FOR_APPLICATION: Final[str] = "9f687f3ffa350cfe40e1e1ad4530a0e757dc262c"
EXPECTED_COMMIT_SUBJECT: Final[str] = "Slice 23 end-to-end dry-run harness scaffold"

RUNTIME_EFFECT: Final[str] = "none"
DEPENDENCY_CHANGE: Final[str] = "none"
INTEGRATION_STATE: Final[str] = "offline_scaffold_only_not_registered_not_live"

REQUIRED_DRY_RUN_STEP_ORDER: Final[tuple[str, ...]] = (
    "input_text_fixture",
    "candidate_meaning_boundary",
    "concept_boundary",
    "predicate_frame_boundary",
    "verbal_gate_boundary",
    "selected_state_candidate_boundary",
    "expression_boundary",
    "read_only_inspection_reference",
)

REQUIRED_DRY_RUN_LAWS: Final[tuple[str, ...]] = (
    "dry_run_is_not_live_runtime",
    "fixture_pass_is_not_public_capability",
    "dry_run_does_not_write_memory",
    "dry_run_does_not_promote_external_resources",
    "dry_run_does_not_deliver_output",
    "dry_run_does_not_execute_actions",
    "dry_run_does_not_route_or_invoke_tools",
    "dry_run_does_not_grant_permission",
    "dry_run_does_not_finalize_selected_meaning",
    "dry_run_does_not_decide_truth",
    "dry_run_does_not_register_routes",
    "dry_run_does_not_modify_config",
    "dry_run_does_not_integrate_ui",
    "dry_run_does_not_call_llm",
    "dry_run_does_not_create_embeddings",
    "dry_run_does_not_run_retrieval_or_rag",
    "dry_run_does_not_import_call_wrap_or_promote_gp014",
    "dry_run_does_not_repair_or_revive_gp015",
)

DOWNSTREAM_FALSE_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "live_runtime_behavior",
    "live_runtime_interpretation",
    "public_capability",
    "fixture_as_public_capability",
    "memory_write",
    "memory_authority",
    "external_resource_admission",
    "external_resource_promotion",
    "resource_fetch",
    "resource_download",
    "resource_ingestion",
    "resource_parsing",
    "resource_indexing",
    "delivery_action",
    "delivery_authority",
    "action_authorization",
    "action_execution",
    "tool_routing",
    "tool_invocation",
    "capability_route",
    "permission_grant",
    "truth_decision",
    "selected_meaning_finalization",
    "final_meaning_selection",
    "output_approval",
    "user_facing_output_authorized",
    "route_registration_authorized",
    "ui_integration_authorized",
    "config_mutation_authorized",
    "network_io",
    "shell_execution",
    "model_authority",
    "vector_authority",
    "retrieval_authority",
    "similarity_authority",
    "embedding_index_creation",
    "rag_execution",
    "gp014_import",
    "gp014_call",
    "gp014_wrap",
    "gp014_promotion",
    "gp014_supersession",
    "gp015_repair",
    "gp015_revival",
    "production_readiness",
    "release_authority",
)

REQUIRED_PRIOR_BOUNDARIES: Final[tuple[str, ...]] = (
    "slice7_meaning_law_trace_boundary",
    "slice8_concept_boundary",
    "slice9_predicate_role_boundary",
    "slice10_verbal_cognition_gate_boundary",
    "slice11_candidate_meaning_boundary",
    "slice12_ambiguity_clarification_boundary",
    "slice13_requirements_traceability_boundary",
    "slice14_external_resource_quarantine_boundary",
    "slice15_corpus_evidence_memory_trace_boundary",
    "slice16_selected_meaning_boundary",
    "slice17_output_expression_boundary",
    "slice20_delivery_action_tool_routing_boundary",
    "slice21_read_only_inspection_surface_boundary",
)


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "to_dict"):
        return _canonicalize(value.to_dict())
    return str(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    """Return deterministic JSON for local records."""

    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    """Return a SHA-256 digest for UTF-8 text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_record_id(prefix: str, *parts: Any) -> str:
    body = {"prefix": prefix, "parts": [_canonicalize(part) for part in parts]}
    return f"{prefix}:{sha256_text(canonical_json(body))[:16]}"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    field: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    schema_version: str
    passed: bool
    issues: tuple[ValidationIssue, ...]

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "passed": self.passed,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True, slots=True)
class AuthoritySeparationRecord:
    slice_id: str
    title: str
    schema_version: str
    scaffold_version: str
    integration_state: str
    runtime_effect: str
    dependency_change: str
    dry_run_step_order: tuple[str, ...]
    dry_run_laws: tuple[str, ...]
    prior_boundaries: tuple[str, ...]
    false_only_fields: tuple[str, ...]
    authority_record_id: str
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
            "slice_id": self.slice_id,
            "title": self.title,
            "schema_version": self.schema_version,
            "scaffold_version": self.scaffold_version,
            "integration_state": self.integration_state,
            "runtime_effect": self.runtime_effect,
            "dependency_change": self.dependency_change,
            "dry_run_step_order": self.dry_run_step_order,
            "dry_run_laws": self.dry_run_laws,
            "prior_boundaries": self.prior_boundaries,
            "false_only_fields": self.false_only_fields,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice23-authority-separation", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_authority_separation_record() -> AuthoritySeparationRecord:
    body = {
        "slice_id": SLICE_ID,
        "title": SLICE_TITLE,
        "schema_version": SCHEMA_VERSION,
        "scaffold_version": SCAFFOLD_VERSION,
        "integration_state": INTEGRATION_STATE,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "dry_run_step_order": REQUIRED_DRY_RUN_STEP_ORDER,
        "dry_run_laws": REQUIRED_DRY_RUN_LAWS,
        "prior_boundaries": REQUIRED_PRIOR_BOUNDARIES,
        "false_only_fields": DOWNSTREAM_FALSE_ONLY_FIELDS,
    }
    return AuthoritySeparationRecord(
        authority_record_id=stable_record_id("slice23-authority-separation", body),
        **body,
    )


def validate_authority_separation_record(record: AuthoritySeparationRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.slice_id != SLICE_ID:
        issues.append(ValidationIssue("slice_id", "slice_id_must_remain_slice_23"))
    if record.title != SLICE_TITLE:
        issues.append(ValidationIssue("title", "slice_title_changed"))
    if record.schema_version != SCHEMA_VERSION:
        issues.append(ValidationIssue("schema_version", "schema_version_changed"))
    if record.integration_state != INTEGRATION_STATE:
        issues.append(ValidationIssue("integration_state", "must_remain_offline_scaffold_only"))
    if record.runtime_effect != RUNTIME_EFFECT:
        issues.append(ValidationIssue("runtime_effect", "must_remain_none"))
    if record.dependency_change != DEPENDENCY_CHANGE:
        issues.append(ValidationIssue("dependency_change", "must_remain_none"))
    if record.dry_run_step_order != REQUIRED_DRY_RUN_STEP_ORDER:
        issues.append(ValidationIssue("dry_run_step_order", "step_order_changed"))
    if record.dry_run_laws != REQUIRED_DRY_RUN_LAWS:
        issues.append(ValidationIssue("dry_run_laws", "law_set_changed"))
    if record.prior_boundaries != REQUIRED_PRIOR_BOUNDARIES:
        issues.append(ValidationIssue("prior_boundaries", "prior_boundary_set_changed"))
    if record.false_only_fields != DOWNSTREAM_FALSE_ONLY_FIELDS:
        issues.append(ValidationIssue("false_only_fields", "false_only_field_set_changed"))
    if record.authority_record_id != record.expected_id():
        issues.append(ValidationIssue("authority_record_id", "stable_identifier_mismatch"))
    for field_name in DOWNSTREAM_FALSE_ONLY_FIELDS:
        if bool(getattr(record, field_name)):
            issues.append(ValidationIssue(field_name, "must_remain_false_for_slice23"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))
