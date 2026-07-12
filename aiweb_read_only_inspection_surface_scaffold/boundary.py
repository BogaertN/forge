"""Boundary integrity checks for Slice 21."""

from __future__ import annotations

from dataclasses import dataclass

from .authority import build_authority_separation_record
from .core import (
    build_inspection_surface_record,
    get_allowed_inspection_subjects,
    get_downstream_false_only_fields,
    get_required_boundary_laws,
)


@dataclass(frozen=True, slots=True)
class BoundaryCheckResult:
    passed: bool
    failures: tuple[str, ...]

    def require_pass(self) -> None:
        if not self.passed:
            raise RuntimeError("Slice 21 read-only inspection boundary check failed: " + "; ".join(self.failures))


def check_boundary_integrity() -> BoundaryCheckResult:
    """Verify that Slice 21 remains read-only inspection visibility only."""

    record = build_inspection_surface_record()
    authority = build_authority_separation_record()
    failures: list[str] = []

    subject_keys = tuple(subject.key for subject in record.inspection_subjects)
    if subject_keys != get_allowed_inspection_subjects():
        failures.append("inspection subjects changed or reordered")

    for subject in record.inspection_subjects:
        if not subject.visible:
            failures.append("inspection subject is not visible: " + subject.key)
        if not subject.reference_only:
            failures.append("inspection subject is not reference-only: " + subject.key)
        if subject.mutation_allowed:
            failures.append("inspection subject allows mutation: " + subject.key)
        if subject.acceptance_effect:
            failures.append("inspection subject creates acceptance: " + subject.key)
        if subject.runtime_effect:
            failures.append("inspection subject creates runtime effect: " + subject.key)
        if subject.proof_effect:
            failures.append("inspection subject creates proof effect: " + subject.key)

    if tuple(record.boundary_laws) != get_required_boundary_laws():
        failures.append("required boundary laws changed or reordered")

    flag_keys = tuple(flag.key for flag in record.negative_authority_flags)
    if flag_keys != get_downstream_false_only_fields():
        failures.append("negative authority flags changed or reordered")

    for flag in record.negative_authority_flags:
        if flag.value is not False:
            failures.append("negative authority flag must remain false: " + flag.key)

    if not record.inspection_is_read_only:
        failures.append("inspection surface must be read-only")
    if record.route_registration_authorized:
        failures.append("route registration must not be authorized")
    if record.ui_integration_authorized:
        failures.append("UI integration must not be authorized")
    if record.config_mutation_authorized:
        failures.append("config mutation must not be authorized")
    if record.live_api_authorized:
        failures.append("live API must not be authorized")
    if record.runtime_effect != "none":
        failures.append("runtime effect must remain none")
    if record.dependency_change != "none":
        failures.append("dependency change must remain none")
    if record.subject_count != len(get_allowed_inspection_subjects()):
        failures.append("subject count mismatch")
    if record.law_count != len(get_required_boundary_laws()):
        failures.append("law count mismatch")
    if record.negative_authority_flag_count != len(get_downstream_false_only_fields()):
        failures.append("negative authority flag count mismatch")

    if not authority.read_only_inspection_required:
        failures.append("read-only inspection must be required")
    if not authority.mutation_forbidden:
        failures.append("mutation must remain forbidden")
    if not authority.acceptance_creation_forbidden:
        failures.append("acceptance creation must remain forbidden")
    if not authority.accepted_scope_widening_forbidden:
        failures.append("accepted-scope widening must remain forbidden")
    if not authority.candidate_promotion_forbidden:
        failures.append("candidate promotion must remain forbidden")
    if not authority.memory_write_forbidden:
        failures.append("memory write must remain forbidden")
    if not authority.tool_routing_forbidden:
        failures.append("tool routing must remain forbidden")
    if not authority.tool_invocation_forbidden:
        failures.append("tool invocation must remain forbidden")
    if not authority.delivery_forbidden:
        failures.append("delivery must remain forbidden")
    if not authority.action_execution_forbidden:
        failures.append("action execution must remain forbidden")
    if not authority.external_resource_admission_forbidden:
        failures.append("external resource admission must remain forbidden")
    if not authority.model_vector_retrieval_rag_authority_forbidden:
        failures.append("model/vector/retrieval/RAG authority must remain forbidden")
    if not authority.ui_authority_forbidden:
        failures.append("UI authority must remain forbidden")
    if authority.this_scaffold_grants_runtime_authority:
        failures.append("this scaffold must not grant runtime authority")
    if authority.this_scaffold_grants_acceptance_authority:
        failures.append("this scaffold must not grant acceptance authority")
    if authority.this_scaffold_grants_permission:
        failures.append("this scaffold must not grant permission")
    if authority.this_scaffold_registers_routes:
        failures.append("this scaffold must not register routes")
    if authority.this_scaffold_modifies_config:
        failures.append("this scaffold must not modify config")
    if authority.this_scaffold_integrates_ui:
        failures.append("this scaffold must not integrate UI")

    return BoundaryCheckResult(passed=not failures, failures=tuple(failures))
