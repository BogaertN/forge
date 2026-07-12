"""Core dry-run harness records for Slice 23.

This module builds a deterministic, offline, end-to-end representation from
input text fixture to expression boundary. It is not a live runtime path. It
only constructs immutable records and validation reports.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping
import importlib

from .authority import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    REQUIRED_DRY_RUN_LAWS,
    REQUIRED_DRY_RUN_STEP_ORDER,
    REQUIRED_PRIOR_BOUNDARIES,
    SCHEMA_VERSION,
    AuthoritySeparationRecord,
    ValidationIssue,
    ValidationReport,
    build_authority_separation_record,
    validate_authority_separation_record,
    stable_record_id,
)
from .fixture import (
    BLOCKED_ACTION_FIXTURE_KEY,
    SAFE_DISPLAY_FIXTURE_KEY,
    DryRunFixtureRecord,
    build_default_fixtures,
    validate_fixture_record,
)

PATH_STATUS_ALLOWED: tuple[str, ...] = (
    "offline_dry_run_path_represented_only",
    "offline_dry_run_path_blocked_before_memory_delivery_or_action",
)

STEP_STATUS_ALLOWED: tuple[str, ...] = (
    "boundary_represented_only",
    "candidate_recorded_not_selected_final",
    "gate_display_only_boundary",
    "blocked_before_memory_delivery_or_action",
    "selected_state_candidate_not_final",
    "expression_preview_not_delivery",
    "read_only_reference_not_authority",
)

PRIOR_VALIDATION_SPECS: tuple[tuple[str, str, str, str], ...] = (
    (
        "candidate_meaning_boundary",
        "aiweb_candidate_meaning_boundary_scaffold.candidate",
        "demo_candidate_meaning_record",
        "validate_candidate_meaning_record",
    ),
    (
        "concept_boundary",
        "aiweb_concept_boundary_scaffold.concept",
        "demo_concept_record",
        "validate_concept_record",
    ),
    (
        "predicate_frame_boundary",
        "aiweb_predicate_role_boundary_scaffold.predicate_frame",
        "demo_predicate_frame_record",
        "validate_predicate_frame_record",
    ),
    (
        "verbal_gate_boundary",
        "aiweb_verbal_cognition_gate_boundary_scaffold.gate_boundary",
        "demo_gate_boundary_record",
        "validate_gate_boundary_record",
    ),
    (
        "selected_state_candidate_boundary",
        "aiweb_selected_meaning_boundary_scaffold.selection_status",
        "demo_selected_meaning_status_record",
        "validate_selected_meaning_status_record",
    ),
    (
        "expression_boundary",
        "aiweb_output_expression_boundary_scaffold.expression_plan",
        "demo_expression_plan_record",
        "validate_expression_plan_record",
    ),
)


@dataclass(frozen=True, slots=True)
class PriorBoundaryValidationRecord:
    stage_key: str
    module_name: str
    demo_builder_name: str
    validator_name: str
    validation_status: str
    validation_passed: bool
    boundary_reference: str
    issue_count: int
    error_text: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DryRunStepRecord:
    step_id: str
    fixture_id: str
    step_index: int
    step_key: str
    step_status: str
    input_ref: str
    output_ref: str
    boundary_kind: str
    upstream_refs: tuple[str, ...]
    downstream_refs: tuple[str, ...]
    law_refs: tuple[str, ...]
    notes: tuple[str, ...]
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
            "fixture_id": self.fixture_id,
            "step_index": self.step_index,
            "step_key": self.step_key,
            "step_status": self.step_status,
            "input_ref": self.input_ref,
            "output_ref": self.output_ref,
            "boundary_kind": self.boundary_kind,
            "upstream_refs": self.upstream_refs,
            "downstream_refs": self.downstream_refs,
            "law_refs": self.law_refs,
            "notes": self.notes,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice23-dry-run-step", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DryRunPathRecord:
    path_id: str
    fixture_id: str
    fixture_key: str
    path_status: str
    step_order: tuple[str, ...]
    steps: tuple[DryRunStepRecord, ...]
    blocked_before_memory_delivery_or_action: bool
    dry_run_only: bool
    no_runtime_effect: bool
    no_public_capability: bool
    no_memory_write: bool
    no_external_resource_promotion: bool
    no_delivery: bool
    no_action: bool
    no_tool_routing: bool
    no_tool_invocation: bool

    def canonical_body(self) -> dict[str, object]:
        return {
            "fixture_id": self.fixture_id,
            "fixture_key": self.fixture_key,
            "path_status": self.path_status,
            "step_order": self.step_order,
            "steps": tuple(step.to_dict() for step in self.steps),
            "blocked_before_memory_delivery_or_action": self.blocked_before_memory_delivery_or_action,
            "dry_run_only": self.dry_run_only,
            "no_runtime_effect": self.no_runtime_effect,
            "no_public_capability": self.no_public_capability,
            "no_memory_write": self.no_memory_write,
            "no_external_resource_promotion": self.no_external_resource_promotion,
            "no_delivery": self.no_delivery,
            "no_action": self.no_action,
            "no_tool_routing": self.no_tool_routing,
            "no_tool_invocation": self.no_tool_invocation,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice23-dry-run-path", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DryRunBoundaryCheckRecord:
    check_id: str
    fixture_id: str
    fixture_key: str
    path_id: str
    prior_validations: tuple[PriorBoundaryValidationRecord, ...]
    authority_flags_checked: tuple[str, ...]
    laws_checked: tuple[str, ...]
    result_status: str

    def canonical_body(self) -> dict[str, object]:
        return {
            "fixture_id": self.fixture_id,
            "fixture_key": self.fixture_key,
            "path_id": self.path_id,
            "prior_validations": tuple(item.to_dict() for item in self.prior_validations),
            "authority_flags_checked": self.authority_flags_checked,
            "laws_checked": self.laws_checked,
            "result_status": self.result_status,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice23-boundary-check", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DryRunHarnessRecord:
    harness_id: str
    authority_record: AuthoritySeparationRecord
    fixtures: tuple[DryRunFixtureRecord, ...]
    paths: tuple[DryRunPathRecord, ...]
    boundary_checks: tuple[DryRunBoundaryCheckRecord, ...]
    prior_boundaries: tuple[str, ...]
    dry_run_laws: tuple[str, ...]
    fixture_count: int
    path_count: int
    boundary_check_count: int
    harness_status: str
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
            "authority_record": self.authority_record.to_dict(),
            "fixtures": tuple(item.to_dict() for item in self.fixtures),
            "paths": tuple(item.to_dict() for item in self.paths),
            "boundary_checks": tuple(item.to_dict() for item in self.boundary_checks),
            "prior_boundaries": self.prior_boundaries,
            "dry_run_laws": self.dry_run_laws,
            "fixture_count": self.fixture_count,
            "path_count": self.path_count,
            "boundary_check_count": self.boundary_check_count,
            "harness_status": self.harness_status,
        }

    def expected_id(self) -> str:
        return stable_record_id("slice23-dry-run-harness", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _report_passed(report: Any) -> tuple[bool, int]:
    if hasattr(report, "ok"):
        passed = bool(report.ok)
    elif hasattr(report, "passed"):
        passed = bool(report.passed)
    else:
        passed = False
    issues = getattr(report, "issues", ())
    try:
        issue_count = len(issues)
    except TypeError:
        issue_count = 1
    return passed, issue_count


def _boundary_reference_from_record(stage_key: str, record: Any) -> str:
    for method_name in ("boundary_id", "expected_id"):
        method = getattr(record, method_name, None)
        if callable(method):
            value = method()
            if isinstance(value, str) and value:
                return value
    for attr_name in (
        "candidate_meaning_id",
        "concept_key",
        "predicate_key",
        "gate_key",
        "selected_meaning_id",
        "expression_plan_id",
    ):
        value = getattr(record, attr_name, "")
        if isinstance(value, str) and value:
            return f"{stage_key}:{value}"
    return f"{stage_key}:demo-record"


def build_prior_boundary_validation_records() -> tuple[PriorBoundaryValidationRecord, ...]:
    records: list[PriorBoundaryValidationRecord] = []
    for stage_key, module_name, builder_name, validator_name in PRIOR_VALIDATION_SPECS:
        try:
            module = importlib.import_module(module_name)
            builder = getattr(module, builder_name)
            validator = getattr(module, validator_name)
            demo_record = builder()
            validation_report = validator(demo_record)
            passed, issue_count = _report_passed(validation_report)
            status = "prior_boundary_demo_validation_passed" if passed else "prior_boundary_demo_validation_failed"
            boundary_reference = _boundary_reference_from_record(stage_key, demo_record)
            records.append(
                PriorBoundaryValidationRecord(
                    stage_key=stage_key,
                    module_name=module_name,
                    demo_builder_name=builder_name,
                    validator_name=validator_name,
                    validation_status=status,
                    validation_passed=passed,
                    boundary_reference=boundary_reference,
                    issue_count=issue_count,
                )
            )
        except Exception as exc:  # pragma: no cover - verifier reports the failure closed
            records.append(
                PriorBoundaryValidationRecord(
                    stage_key=stage_key,
                    module_name=module_name,
                    demo_builder_name=builder_name,
                    validator_name=validator_name,
                    validation_status="prior_boundary_import_or_validation_error",
                    validation_passed=False,
                    boundary_reference=f"{stage_key}:unavailable",
                    issue_count=1,
                    error_text=str(exc),
                )
            )

    for stage_key, module_name, builder_name in (
        (
            "delivery_action_tool_routing_boundary",
            "aiweb_delivery_action_tool_routing_boundary_scaffold.core",
            "build_boundary_record",
        ),
        (
            "read_only_inspection_reference",
            "aiweb_read_only_inspection_surface_scaffold.core",
            "build_inspection_surface_record",
        ),
    ):
        try:
            module = importlib.import_module(module_name)
            builder = getattr(module, builder_name)
            demo_record = builder()
            reference = stable_record_id(stage_key, _canonical_record(demo_record))
            records.append(
                PriorBoundaryValidationRecord(
                    stage_key=stage_key,
                    module_name=module_name,
                    demo_builder_name=builder_name,
                    validator_name="build_record_only",
                    validation_status="prior_boundary_record_built",
                    validation_passed=True,
                    boundary_reference=reference,
                    issue_count=0,
                )
            )
        except Exception as exc:  # pragma: no cover - verifier reports the failure closed
            records.append(
                PriorBoundaryValidationRecord(
                    stage_key=stage_key,
                    module_name=module_name,
                    demo_builder_name=builder_name,
                    validator_name="build_record_only",
                    validation_status="prior_boundary_import_or_build_error",
                    validation_passed=False,
                    boundary_reference=f"{stage_key}:unavailable",
                    issue_count=1,
                    error_text=str(exc),
                )
            )
    return tuple(records)


def _canonical_record(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, Mapping):
        return dict(value)
    return str(value)


def _step_status_for_fixture(fixture: DryRunFixtureRecord, step_key: str) -> str:
    if fixture.fixture_key == BLOCKED_ACTION_FIXTURE_KEY:
        if step_key == "verbal_gate_boundary":
            return "blocked_before_memory_delivery_or_action"
        if step_key == "selected_state_candidate_boundary":
            return "selected_state_candidate_not_final"
        if step_key == "expression_boundary":
            return "expression_preview_not_delivery"
    if step_key == "candidate_meaning_boundary":
        return "candidate_recorded_not_selected_final"
    if step_key == "verbal_gate_boundary":
        return "gate_display_only_boundary"
    if step_key == "selected_state_candidate_boundary":
        return "selected_state_candidate_not_final"
    if step_key == "expression_boundary":
        return "expression_preview_not_delivery"
    if step_key == "read_only_inspection_reference":
        return "read_only_reference_not_authority"
    return "boundary_represented_only"


def build_steps_for_fixture(fixture: DryRunFixtureRecord) -> tuple[DryRunStepRecord, ...]:
    steps: list[DryRunStepRecord] = []
    previous_ref = fixture.fixture_id
    for index, step_key in enumerate(REQUIRED_DRY_RUN_STEP_ORDER):
        output_ref = stable_record_id("slice23-step-output", fixture.fixture_id, step_key, index)
        downstream = () if index == len(REQUIRED_DRY_RUN_STEP_ORDER) - 1 else (REQUIRED_DRY_RUN_STEP_ORDER[index + 1],)
        body = {
            "fixture_id": fixture.fixture_id,
            "step_index": index,
            "step_key": step_key,
            "step_status": _step_status_for_fixture(fixture, step_key),
            "input_ref": previous_ref,
            "output_ref": output_ref,
            "boundary_kind": "offline_boundary_reference_only",
            "upstream_refs": (previous_ref,),
            "downstream_refs": downstream,
            "law_refs": REQUIRED_DRY_RUN_LAWS,
            "notes": (
                "dry_run_only_not_live_runtime",
                "no_memory_no_delivery_no_action_no_tool_route",
            ),
        }
        steps.append(DryRunStepRecord(step_id=stable_record_id("slice23-dry-run-step", body), **body))
        previous_ref = output_ref
    return tuple(steps)


def build_path_for_fixture(fixture: DryRunFixtureRecord) -> DryRunPathRecord:
    steps = build_steps_for_fixture(fixture)
    blocked = fixture.fixture_key == BLOCKED_ACTION_FIXTURE_KEY
    path_status = (
        "offline_dry_run_path_blocked_before_memory_delivery_or_action"
        if blocked
        else "offline_dry_run_path_represented_only"
    )
    id_body = {
        "fixture_id": fixture.fixture_id,
        "fixture_key": fixture.fixture_key,
        "path_status": path_status,
        "step_order": REQUIRED_DRY_RUN_STEP_ORDER,
        "steps": tuple(step.to_dict() for step in steps),
        "blocked_before_memory_delivery_or_action": blocked,
        "dry_run_only": True,
        "no_runtime_effect": True,
        "no_public_capability": True,
        "no_memory_write": True,
        "no_external_resource_promotion": True,
        "no_delivery": True,
        "no_action": True,
        "no_tool_routing": True,
        "no_tool_invocation": True,
    }
    return DryRunPathRecord(
        path_id=stable_record_id("slice23-dry-run-path", id_body),
        fixture_id=fixture.fixture_id,
        fixture_key=fixture.fixture_key,
        path_status=path_status,
        step_order=REQUIRED_DRY_RUN_STEP_ORDER,
        steps=steps,
        blocked_before_memory_delivery_or_action=blocked,
        dry_run_only=True,
        no_runtime_effect=True,
        no_public_capability=True,
        no_memory_write=True,
        no_external_resource_promotion=True,
        no_delivery=True,
        no_action=True,
        no_tool_routing=True,
        no_tool_invocation=True,
    )


def build_boundary_check_for_path(
    fixture: DryRunFixtureRecord,
    path: DryRunPathRecord,
    prior_validations: tuple[PriorBoundaryValidationRecord, ...],
) -> DryRunBoundaryCheckRecord:
    id_body = {
        "fixture_id": fixture.fixture_id,
        "fixture_key": fixture.fixture_key,
        "path_id": path.path_id,
        "prior_validations": tuple(item.to_dict() for item in prior_validations),
        "authority_flags_checked": DOWNSTREAM_FALSE_ONLY_FIELDS,
        "laws_checked": REQUIRED_DRY_RUN_LAWS,
        "result_status": "dry_run_boundary_check_passed_offline_only",
    }
    return DryRunBoundaryCheckRecord(
        check_id=stable_record_id("slice23-boundary-check", id_body),
        fixture_id=fixture.fixture_id,
        fixture_key=fixture.fixture_key,
        path_id=path.path_id,
        prior_validations=prior_validations,
        authority_flags_checked=DOWNSTREAM_FALSE_ONLY_FIELDS,
        laws_checked=REQUIRED_DRY_RUN_LAWS,
        result_status="dry_run_boundary_check_passed_offline_only",
    )


def build_demo_harness_record() -> DryRunHarnessRecord:
    authority = build_authority_separation_record()
    fixtures = build_default_fixtures()
    paths = tuple(build_path_for_fixture(fixture) for fixture in fixtures)
    prior_validations = build_prior_boundary_validation_records()
    checks = tuple(
        build_boundary_check_for_path(fixture, path, prior_validations)
        for fixture, path in zip(fixtures, paths)
    )
    id_body = {
        "authority_record": authority.to_dict(),
        "fixtures": tuple(fixture.to_dict() for fixture in fixtures),
        "paths": tuple(path.to_dict() for path in paths),
        "boundary_checks": tuple(check.to_dict() for check in checks),
        "prior_boundaries": REQUIRED_PRIOR_BOUNDARIES,
        "dry_run_laws": REQUIRED_DRY_RUN_LAWS,
        "fixture_count": len(fixtures),
        "path_count": len(paths),
        "boundary_check_count": len(checks),
        "harness_status": "offline_dry_run_harness_scaffold_passed_not_live_runtime",
    }
    return DryRunHarnessRecord(
        harness_id=stable_record_id("slice23-dry-run-harness", id_body),
        authority_record=authority,
        fixtures=fixtures,
        paths=paths,
        boundary_checks=checks,
        prior_boundaries=REQUIRED_PRIOR_BOUNDARIES,
        dry_run_laws=REQUIRED_DRY_RUN_LAWS,
        fixture_count=len(fixtures),
        path_count=len(paths),
        boundary_check_count=len(checks),
        harness_status="offline_dry_run_harness_scaffold_passed_not_live_runtime",
    )


def _check_false_only(record: Any, field_names: tuple[str, ...], issues: list[ValidationIssue], namespace: str) -> None:
    for field_name in field_names:
        if bool(getattr(record, field_name, False)):
            issues.append(ValidationIssue(field_name, f"{namespace}_must_remain_false"))


def validate_step_record(record: DryRunStepRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.step_key not in REQUIRED_DRY_RUN_STEP_ORDER:
        issues.append(ValidationIssue("step_key", "unknown_step_key"))
    elif REQUIRED_DRY_RUN_STEP_ORDER[record.step_index] != record.step_key:
        issues.append(ValidationIssue("step_index", "step_index_does_not_match_required_order"))
    if record.step_status not in STEP_STATUS_ALLOWED:
        issues.append(ValidationIssue("step_status", "unsupported_step_status"))
    if record.boundary_kind != "offline_boundary_reference_only":
        issues.append(ValidationIssue("boundary_kind", "must_remain_offline_boundary_reference_only"))
    if record.law_refs != REQUIRED_DRY_RUN_LAWS:
        issues.append(ValidationIssue("law_refs", "law_refs_changed"))
    if not record.input_ref or not record.output_ref:
        issues.append(ValidationIssue("input_output_ref", "input_and_output_refs_required"))
    if record.step_id != record.expected_id():
        issues.append(ValidationIssue("step_id", "stable_identifier_mismatch"))
    _check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "dry_run_step")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def validate_path_record(record: DryRunPathRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.path_status not in PATH_STATUS_ALLOWED:
        issues.append(ValidationIssue("path_status", "unsupported_path_status"))
    if record.step_order != REQUIRED_DRY_RUN_STEP_ORDER:
        issues.append(ValidationIssue("step_order", "required_step_order_changed"))
    if tuple(step.step_key for step in record.steps) != REQUIRED_DRY_RUN_STEP_ORDER:
        issues.append(ValidationIssue("steps", "step_records_do_not_match_required_order"))
    for step in record.steps:
        report = validate_step_record(step)
        if not report.passed:
            for issue in report.issues:
                issues.append(ValidationIssue(f"step.{step.step_key}.{issue.field}", issue.reason))
    if not record.dry_run_only:
        issues.append(ValidationIssue("dry_run_only", "path_must_remain_dry_run_only"))
    for field_name in (
        "no_runtime_effect",
        "no_public_capability",
        "no_memory_write",
        "no_external_resource_promotion",
        "no_delivery",
        "no_action",
        "no_tool_routing",
        "no_tool_invocation",
    ):
        if getattr(record, field_name) is not True:
            issues.append(ValidationIssue(field_name, "must_remain_true_boundary_proof"))
    if record.fixture_key == BLOCKED_ACTION_FIXTURE_KEY and not record.blocked_before_memory_delivery_or_action:
        issues.append(ValidationIssue("blocked_before_memory_delivery_or_action", "blocked_fixture_must_stop_before_effects"))
    if record.path_id != record.expected_id():
        issues.append(ValidationIssue("path_id", "stable_identifier_mismatch"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def validate_boundary_check_record(record: DryRunBoundaryCheckRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.authority_flags_checked != DOWNSTREAM_FALSE_ONLY_FIELDS:
        issues.append(ValidationIssue("authority_flags_checked", "false_only_fields_changed"))
    if record.laws_checked != REQUIRED_DRY_RUN_LAWS:
        issues.append(ValidationIssue("laws_checked", "law_set_changed"))
    if record.result_status != "dry_run_boundary_check_passed_offline_only":
        issues.append(ValidationIssue("result_status", "boundary_check_status_changed"))
    if not record.prior_validations:
        issues.append(ValidationIssue("prior_validations", "prior_boundary_validations_required"))
    for validation in record.prior_validations:
        if not validation.validation_passed:
            issues.append(ValidationIssue(validation.stage_key, validation.validation_status))
        if validation.issue_count != 0:
            issues.append(ValidationIssue(validation.stage_key, "prior_validation_issue_count_nonzero"))
    if record.check_id != record.expected_id():
        issues.append(ValidationIssue("check_id", "stable_identifier_mismatch"))
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def validate_dry_run_harness_record(record: DryRunHarnessRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    authority_report = validate_authority_separation_record(record.authority_record)
    if not authority_report.passed:
        issues.extend(ValidationIssue(f"authority.{issue.field}", issue.reason) for issue in authority_report.issues)
    if record.fixture_count != 2 or len(record.fixtures) != 2:
        issues.append(ValidationIssue("fixture_count", "exactly_two_fixtures_required"))
    if tuple(fixture.fixture_key for fixture in record.fixtures) != (SAFE_DISPLAY_FIXTURE_KEY, BLOCKED_ACTION_FIXTURE_KEY):
        issues.append(ValidationIssue("fixtures", "fixture_identity_or_order_changed"))
    for fixture in record.fixtures:
        report = validate_fixture_record(fixture)
        if not report.passed:
            issues.extend(ValidationIssue(f"fixture.{fixture.fixture_key}.{issue.field}", issue.reason) for issue in report.issues)
    if record.path_count != len(record.paths) or record.path_count != 2:
        issues.append(ValidationIssue("path_count", "exactly_two_paths_required"))
    for path in record.paths:
        report = validate_path_record(path)
        if not report.passed:
            issues.extend(ValidationIssue(f"path.{path.fixture_key}.{issue.field}", issue.reason) for issue in report.issues)
    if record.boundary_check_count != len(record.boundary_checks) or record.boundary_check_count != 2:
        issues.append(ValidationIssue("boundary_check_count", "exactly_two_boundary_checks_required"))
    for check in record.boundary_checks:
        report = validate_boundary_check_record(check)
        if not report.passed:
            issues.extend(ValidationIssue(f"check.{check.fixture_key}.{issue.field}", issue.reason) for issue in report.issues)
    if record.prior_boundaries != REQUIRED_PRIOR_BOUNDARIES:
        issues.append(ValidationIssue("prior_boundaries", "prior_boundaries_changed"))
    if record.dry_run_laws != REQUIRED_DRY_RUN_LAWS:
        issues.append(ValidationIssue("dry_run_laws", "law_set_changed"))
    if record.harness_status != "offline_dry_run_harness_scaffold_passed_not_live_runtime":
        issues.append(ValidationIssue("harness_status", "harness_status_changed"))
    if record.harness_id != record.expected_id():
        issues.append(ValidationIssue("harness_id", "stable_identifier_mismatch"))
    _check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "dry_run_harness")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))
