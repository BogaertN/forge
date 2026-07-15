"""Deterministic validation for Slice 36B0 contract records."""

from __future__ import annotations

from ..schema import ValidationReport, issue
from .schema import (
    CONTRACT_SCHEMA_VERSION,
    CONTRACT_SPEC_ID,
    CONTRACT_SPEC_VERSION,
    EXPECTED_RSOC_OPERATOR_COUNT,
    FIELD_SCHEMA_ID,
    LEGACY_ISOLATION_SCHEMA_ID,
    OPERATOR_SCHEMA_ID,
    REGISTRY_SCHEMA_ID,
    FieldEnvelopeBuildResult,
    FieldProjectionStatus,
    FieldPhaseStatus,
    FieldSupportStatus,
    LegacyIsolationCatalog,
    LegacyIsolationRecord,
    LineageIdentityHandling,
    OperatorApplicationDecision,
    OperatorRuntimeStatus,
    ResonantLanguageFieldEnvelope,
    RsocLanguageOperatorRegistry,
    RsocOperatorContract,
)


def _report(issues: list[object]) -> ValidationReport:
    return ValidationReport(
        schema_version=CONTRACT_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def _base_issues(record: object) -> list[object]:
    issues: list[object] = []
    if getattr(record, "schema_version", None) != CONTRACT_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if getattr(record, "contract_spec_id", None) != CONTRACT_SPEC_ID:
        issues.append(issue("contract_spec_id", "contract_spec_id_mismatch"))
    if getattr(record, "contract_spec_version", None) != CONTRACT_SPEC_VERSION:
        issues.append(issue("contract_spec_version", "contract_spec_version_mismatch"))
    return issues


def validate_resonant_language_field(
    field: object,
) -> ValidationReport:
    if type(field) is not ResonantLanguageFieldEnvelope:
        return _report([issue("field", "invalid_record_type")])
    issues = _base_issues(field)
    if field.field_schema_id != FIELD_SCHEMA_ID:
        issues.append(issue("field_schema_id", "field_schema_id_mismatch"))
    if field.field_id != field.expected_id():
        issues.append(issue("field_id", "stable_identifier_mismatch"))
    if field.projection_status is not FieldProjectionStatus.UNPROJECTED:
        issues.append(issue("projection_status", "must_remain_unprojected"))
    if field.phase_status is not FieldPhaseStatus.UNASSIGNED:
        issues.append(issue("phase_status", "must_remain_unassigned"))
    if field.support_status is not FieldSupportStatus.UNASSESSED:
        issues.append(issue("support_status", "must_remain_unassessed"))
    if field.covered_source_span_ids:
        issues.append(issue("covered_source_span_ids", "must_remain_empty"))
    if len(field.unresolved_source_span_ids) != 1:
        issues.append(issue("unresolved_source_span_ids", "root_span_must_remain_unresolved"))
    if field.unresolved_source_span_ids and field.unresolved_source_span_ids[0] != field.root_source_span_id:
        issues.append(issue("unresolved_source_span_ids", "root_span_reference_mismatch"))
    for name in (
        "rsoc_lineage_identity_assigned",
        "source_text_copied_or_replaced",
        "tokenization_performed",
        "operator_binding_performed",
        "operator_application_performed",
        "phase_assignment_performed",
        "concept_lookup_performed",
        "predicate_binding_performed",
        "meaning_created",
        "reference_resolution_performed",
        "legacy_runtime_consulted",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
    ):
        if getattr(field, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    return _report(issues)


def validate_field_envelope_build_result(
    result: object,
) -> ValidationReport:
    if type(result) is not FieldEnvelopeBuildResult:
        return _report([issue("result", "invalid_record_type")])
    issues = _base_issues(result)
    if result.result_id != result.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))
    if result.envelope_created:
        field_report = validate_resonant_language_field(result.field)
        issues.extend(field_report.issues)
    elif result.field is not None:
        issues.append(issue("field", "must_be_none_when_not_created"))
    if result.structural_progression_allowed is not False:
        issues.append(issue("structural_progression_allowed", "must_remain_false"))
    for name in (
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
    ):
        if getattr(result, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    return _report(issues)


def validate_rsoc_operator_contract(
    contract: object,
) -> ValidationReport:
    if type(contract) is not RsocOperatorContract:
        return _report([issue("contract", "invalid_record_type")])
    issues = _base_issues(contract)
    if contract.operator_schema_id != OPERATOR_SCHEMA_ID:
        issues.append(issue("operator_schema_id", "operator_schema_id_mismatch"))
    if contract.contract_id != contract.expected_id():
        issues.append(issue("contract_id", "stable_identifier_mismatch"))
    if contract.runtime_status is not OperatorRuntimeStatus.CONTRACT_ONLY_DISABLED:
        issues.append(issue("runtime_status", "must_remain_contract_only_disabled"))
    if contract.domain_schema_id != FIELD_SCHEMA_ID or contract.range_schema_id != FIELD_SCHEMA_ID:
        issues.append(issue("domain_or_range", "field_schema_contract_mismatch"))
    for name in (
        "entropy_thresholds_installed",
        "commutation_table_installed",
        "numeric_transform_installed",
        "runtime_enabled",
        "application_implemented",
        "automatic_trigger_authorized",
        "source_binding_authorized",
        "phase_assignment_authorized",
        "meaning_authorized",
        "memory_authorized",
        "route_authorized",
        "tool_authorized",
        "action_authorized",
        "delivery_authorized",
    ):
        if getattr(contract, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    if contract.operator_key == "christ_function":
        if contract.may_decrease_entropy is not True:
            issues.append(issue("may_decrease_entropy", "christ_function_exclusive_permission_missing"))
        if contract.identity_handling is not LineageIdentityHandling.CONTROLLED_MASK_ONLY_UNDER_LATER_AUTHORITY:
            issues.append(issue("identity_handling", "christ_function_identity_contract_mismatch"))
    elif contract.may_decrease_entropy is not False:
        issues.append(issue("may_decrease_entropy", "non_christ_entropy_decrease_prohibited"))
    return _report(issues)


def validate_rsoc_language_operator_registry(
    registry: object,
) -> ValidationReport:
    if type(registry) is not RsocLanguageOperatorRegistry:
        return _report([issue("registry", "invalid_record_type")])
    issues = _base_issues(registry)
    if registry.registry_schema_id != REGISTRY_SCHEMA_ID:
        issues.append(issue("registry_schema_id", "registry_schema_id_mismatch"))
    if registry.registry_id != registry.expected_id():
        issues.append(issue("registry_id", "stable_identifier_mismatch"))
    if registry.exact_operator_count != EXPECTED_RSOC_OPERATOR_COUNT:
        issues.append(issue("exact_operator_count", "operator_count_contract_mismatch"))
    if len(registry.operators) != EXPECTED_RSOC_OPERATOR_COUNT:
        issues.append(issue("operators", "operator_count_mismatch"))
    keys = tuple(item.operator_key for item in registry.operators)
    glyphs = tuple(item.glyph for item in registry.operators)
    if len(set(keys)) != len(keys):
        issues.append(issue("operators", "duplicate_operator_key"))
    if len(set(glyphs)) != len(glyphs):
        issues.append(issue("operators", "duplicate_operator_glyph"))
    if sum(item.may_decrease_entropy for item in registry.operators) != 1:
        issues.append(issue("operators", "entropy_decrease_exclusivity_broken"))
    for item in registry.operators:
        issues.extend(validate_rsoc_operator_contract(item).issues)
    for name in (
        "default_runtime_enabled",
        "operator_application_available",
        "source_binding_available",
        "phase_assignment_available",
        "legacy_imports_allowed",
        "mea_substitution_allowed",
        "hidden_fallback_allowed",
    ):
        if getattr(registry, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    return _report(issues)


def validate_operator_application_decision(
    decision: object,
) -> ValidationReport:
    if type(decision) is not OperatorApplicationDecision:
        return _report([issue("decision", "invalid_record_type")])
    issues = _base_issues(decision)
    if decision.decision_id != decision.expected_id():
        issues.append(issue("decision_id", "stable_identifier_mismatch"))
    for name in (
        "application_performed",
        "successor_field_created",
        "phase_assigned",
        "meaning_created",
        "memory_read_performed",
        "memory_write_performed",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
    ):
        if getattr(decision, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    return _report(issues)


def validate_legacy_isolation_record(
    record: object,
) -> ValidationReport:
    if type(record) is not LegacyIsolationRecord:
        return _report([issue("record", "invalid_record_type")])
    issues = _base_issues(record)
    if record.isolation_schema_id != LEGACY_ISOLATION_SCHEMA_ID:
        issues.append(issue("isolation_schema_id", "isolation_schema_id_mismatch"))
    if record.isolation_id != record.expected_id():
        issues.append(issue("isolation_id", "stable_identifier_mismatch"))
    for name in (
        "import_allowed",
        "call_allowed",
        "language_authority_allowed",
        "semantic_authority_allowed",
        "runtime_substitution_allowed",
    ):
        if getattr(record, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    return _report(issues)


def validate_legacy_isolation_catalog(
    catalog: object,
) -> ValidationReport:
    if type(catalog) is not LegacyIsolationCatalog:
        return _report([issue("catalog", "invalid_record_type")])
    issues = _base_issues(catalog)
    if catalog.isolation_schema_id != LEGACY_ISOLATION_SCHEMA_ID:
        issues.append(issue("isolation_schema_id", "isolation_schema_id_mismatch"))
    if catalog.catalog_id != catalog.expected_id():
        issues.append(issue("catalog_id", "stable_identifier_mismatch"))
    paths = tuple(item.surface_path for item in catalog.records)
    if len(paths) != len(set(paths)):
        issues.append(issue("records", "duplicate_surface_path"))
    for item in catalog.records:
        issues.extend(validate_legacy_isolation_record(item).issues)
    for name in (
        "legacy_imports_allowed",
        "legacy_calls_allowed",
        "legacy_language_authority_allowed",
        "mea_substitution_allowed",
    ):
        if getattr(catalog, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    if catalog.static_reference_only is not True:
        issues.append(issue("static_reference_only", "must_remain_true"))
    return _report(issues)
