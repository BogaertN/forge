"""Fail-closed validation for Slice 41E integration and custody."""
from __future__ import annotations

from typing import Any, Callable

from ...meaning_structure_manifest import (
    ExternalAuthorityKind,
    ExternalAuthorityReferenceRecord,
    MeaningStructureManifestV1,
    SelectedGovernedMeaningRecord,
    SemanticLifecycleState,
    SemanticTransitionKind,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.serialization import (
    canonical_manifest_sha256,
    deserialize_manifest,
    serialize_manifest,
)
from ...meaning_structure_manifest.validation import validate_manifest
from ...msm_gate_custody.schema import MsmGateIntegrationResult
from ...msm_gate_custody.validation import validate_result as validate_gate_result
from ..selected_meaning_construction.schema import (
    SelectedMeaningConstructionInput,
    SelectedMeaningConstructionPackage,
)
from ..selected_meaning_construction.validation import (
    validate_construction_input,
    validate_package,
)
from .authority import (
    SLICE41E_COMPANION_VERSION,
    SLICE41E_GOVERNING_AUTHORITY_REFS,
    SLICE41E_PERMANENT_BOUNDARIES,
    SLICE41E_PROFILE_KEY,
    SLICE41E_PROFILE_VERSION,
    SLICE41E_PROHIBITED_AUTHORITY,
    SLICE41E_RECEIPT_VERSION,
    SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS,
    SLICE41E_REQUIRED_PATH,
    SLICE41E_SCHEMA_VERSION,
    SLICE41E_SPEC_ID,
    SLICE41E_SPEC_VERSION,
)
from .identity import (
    expected_authority_reference_id,
    expected_companion_id,
    expected_input_id,
    expected_profile_id,
    expected_receipt_id,
    expected_result_digest,
    expected_result_id,
    expected_selected_record_id,
    expected_successor_manifest_id,
    expected_transition_trace_id,
)
from .schema import (
    MsmSelectedMeaningCustodyCompanionV1,
    MsmSelectedMeaningIntegrationAuthorityProfile,
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationReceiptV1,
    MsmSelectedMeaningIntegrationResult,
    MsmSelectedMeaningIntegrationValidationCode as Code,
    MsmSelectedMeaningIntegrationValidationError,
    MsmSelectedMeaningIntegrationValidationIssue as Issue,
    MsmSelectedMeaningIntegrationValidationReport as Report,
)


def _issue(issues: list[Issue], path: str, code: Code, detail: str) -> None:
    issues.append(Issue(path, code, detail))


def _report(issues: list[Issue]) -> Report:
    return Report(tuple(issues))


def _text(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


def _tuple_text(
    value: object,
    path: str,
    issues: list[Issue],
    *,
    allow_empty: bool = True,
) -> None:
    if type(value) is not tuple or any(not _text(item) for item in value):
        _issue(issues, path, Code.TYPE_MISMATCH, "tuple of trimmed text required")
    elif not allow_empty and not value:
        _issue(issues, path, Code.CANONICAL_MISMATCH, "non-empty tuple required")


def _false_flags(
    value: Any,
    names: tuple[str, ...],
    path: str,
    issues: list[Issue],
) -> None:
    for name in names:
        if getattr(value, name, None) is not False:
            _issue(issues, f"{path}.{name}", Code.PROHIBITED_AUTHORITY, "must be false")


def _true_flags(
    value: Any,
    names: tuple[str, ...],
    path: str,
    issues: list[Issue],
) -> None:
    for name in names:
        if getattr(value, name, None) is not True:
            _issue(issues, f"{path}.{name}", Code.CANONICAL_MISMATCH, "must be true")


def _safe_expected(
    issues: list[Issue],
    path: str,
    callback: Callable[[], object],
) -> object | None:
    try:
        return callback()
    except Exception as error:  # fail closed for deliberately malformed nested records
        _issue(issues, path, Code.CANONICAL_MISMATCH, f"deterministic calculation failed: {error}")
        return None


def validate_authority_profile(value: object) -> Report:
    issues: list[Issue] = []
    if type(value) is not MsmSelectedMeaningIntegrationAuthorityProfile:
        return Report((Issue("profile", Code.TYPE_MISMATCH, "exact profile type required"),))

    exact = {
        "profile_key": SLICE41E_PROFILE_KEY,
        "profile_version": SLICE41E_PROFILE_VERSION,
        "governing_authority_refs": SLICE41E_GOVERNING_AUTHORITY_REFS,
        "required_path": SLICE41E_REQUIRED_PATH,
        "permanent_boundaries": SLICE41E_PERMANENT_BOUNDARIES,
        "prohibited_authority": SLICE41E_PROHIBITED_AUTHORITY,
        "required_empty_successor_sections": SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS,
        "spec_id": SLICE41E_SPEC_ID,
        "spec_version": SLICE41E_SPEC_VERSION,
        "schema_version": SLICE41E_SCHEMA_VERSION,
    }
    for name, expected in exact.items():
        if getattr(value, name) != expected:
            _issue(issues, f"profile.{name}", Code.PROFILE_MISMATCH, "canonical profile field mismatch")

    _true_flags(
        value,
        (
            "exact_slice40h_result_required",
            "exact_slice40h_companion_required",
            "exact_slice41d_input_required",
            "exact_slice41d_package_required",
            "exact_selected_candidate_required",
            "exact_selection_receipt_required",
            "immutable_successor_required",
            "lawful_lifecycle_transition_required",
            "candidate_retention_required",
            "non_selection_retention_required",
            "gate_ancestry_retention_required",
            "complete_successor_validation_required",
            "versioned_companion_required",
            "deterministic_receipt_required",
            "fail_closed",
        ),
        "profile",
        issues,
    )
    _false_flags(
        value,
        (
            "msm_schema_rewrite_allowed",
            "automatic_migration_allowed",
            "candidate_deletion_allowed",
            "non_selection_deletion_allowed",
            "gate_custody_deletion_allowed",
            "governed_result_allowed",
            "outward_meaning_allowed",
            "expression_link_allowed",
            "validation_link_allowed",
            "delivery_link_allowed",
            "truth_evidence_allowed",
            "permission_execution_allowed",
            "route_tool_action_memory_rendering_delivery_allowed",
            "bootstrap_integration_allowed",
        ),
        "profile",
        issues,
    )
    expected = _safe_expected(issues, "profile.profile_id", lambda: expected_profile_id(value))
    if expected is not None and value.profile_id != expected:
        _issue(issues, "profile.profile_id", Code.IDENTITY_MISMATCH, "profile ID mismatch")
    return _report(issues)


def validate_integration_input(value: object) -> Report:
    issues: list[Issue] = []
    if type(value) is not MsmSelectedMeaningIntegrationInput:
        return Report((Issue("input", Code.TYPE_MISMATCH, "exact input type required"),))

    issues.extend(validate_authority_profile(value.authority_profile).issues)

    gate_ok = False
    if type(value.source_gate_integration_result) is not MsmGateIntegrationResult:
        _issue(issues, "input.source_gate_integration_result", Code.TYPE_MISMATCH, "exact Slice 40H result required")
    else:
        try:
            gate_report = validate_gate_result(value.source_gate_integration_result)
        except Exception as error:
            _issue(issues, "input.source_gate_integration_result", Code.SOURCE_GATE_RESULT_INVALID, f"Slice 40H validation raised: {error}")
        else:
            gate_ok = gate_report.ok
            if not gate_ok:
                _issue(issues, "input.source_gate_integration_result", Code.SOURCE_GATE_RESULT_INVALID, "Slice 40H result validation failed")

    construction_ok = False
    if type(value.selected_meaning_construction_input) is not SelectedMeaningConstructionInput:
        _issue(issues, "input.selected_meaning_construction_input", Code.TYPE_MISMATCH, "exact Slice 41D input required")
    else:
        try:
            construction_report = validate_construction_input(value.selected_meaning_construction_input)
        except Exception as error:
            _issue(issues, "input.selected_meaning_construction_input", Code.SLICE41D_INPUT_INVALID, f"Slice 41D input validation raised: {error}")
        else:
            construction_ok = construction_report.ok
            if not construction_ok:
                _issue(issues, "input.selected_meaning_construction_input", Code.SLICE41D_INPUT_INVALID, "Slice 41D input validation failed")

    package_ok = False
    if type(value.selected_meaning_package) is not SelectedMeaningConstructionPackage:
        _issue(issues, "input.selected_meaning_package", Code.TYPE_MISMATCH, "exact Slice 41D package required")
    elif type(value.selected_meaning_construction_input) is SelectedMeaningConstructionInput:
        try:
            package_report = validate_package(
                value.selected_meaning_package,
                construction_input=value.selected_meaning_construction_input,
            )
        except Exception as error:
            _issue(issues, "input.selected_meaning_package", Code.SLICE41D_PACKAGE_INVALID, f"Slice 41D package validation raised: {error}")
        else:
            package_ok = package_report.ok
            if not package_ok:
                _issue(issues, "input.selected_meaning_package", Code.SLICE41D_PACKAGE_INVALID, "Slice 41D package validation failed")

    if not _text(value.semantic_transition_reason):
        _issue(issues, "input.semantic_transition_reason", Code.TYPE_MISMATCH, "trimmed transition reason required")
    _tuple_text(value.version_refs, "input.version_refs", issues, allow_empty=False)
    _false_flags(
        value,
        (
            "msm_schema_rewrite_requested",
            "automatic_migration_requested",
            "candidate_deletion_requested",
            "non_selection_deletion_requested",
            "gate_custody_deletion_requested",
            "governed_result_requested",
            "outward_meaning_requested",
            "expression_link_requested",
            "validation_link_requested",
            "delivery_link_requested",
            "truth_claim_requested",
            "evidence_claim_requested",
            "permission_requested",
            "execution_requested",
            "route_requested",
            "tool_requested",
            "action_requested",
            "memory_access_requested",
            "memory_write_requested",
            "rendering_requested",
            "delivery_requested",
            "bootstrap_integration_requested",
        ),
        "input",
        issues,
    )

    source: MeaningStructureManifestV1 | None = None
    if type(value.source_gate_integration_result) is MsmGateIntegrationResult:
        possible_source = value.source_gate_integration_result.successor_manifest
        if type(possible_source) is not MeaningStructureManifestV1:
            _issue(issues, "input.source_manifest", Code.TYPE_MISMATCH, "exact MSM-v1 successor required")
        else:
            source = possible_source
            try:
                source_report = validate_manifest(source)
            except Exception as error:
                _issue(issues, "input.source_manifest", Code.SOURCE_MANIFEST_INVALID, f"source manifest validation raised: {error}")
            else:
                if not source_report.ok:
                    _issue(issues, "input.source_manifest", Code.SOURCE_MANIFEST_INVALID, "source successor manifest invalid")
            try:
                if deserialize_manifest(serialize_manifest(source)) != source:
                    _issue(issues, "input.source_manifest", Code.CANONICAL_MISMATCH, "source manifest canonical roundtrip failed")
            except Exception as error:
                _issue(issues, "input.source_manifest", Code.SOURCE_MANIFEST_INVALID, f"source manifest serialization failed: {error}")

            gate = value.source_gate_integration_result
            companion = gate.companion
            if gate.successor_manifest_id != source.manifest_id or companion.successor_manifest_id != source.manifest_id:
                _issue(issues, "input.source_manifest.manifest_id", Code.SLICE40H_CUSTODY_MISMATCH, "Slice 40H successor identity mismatch")
            if gate.source_manifest_id != companion.source_manifest_id or gate.manifest_candidate_ref != companion.manifest_candidate_ref:
                _issue(issues, "input.source_gate_integration_result", Code.SLICE40H_CUSTODY_MISMATCH, "Slice 40H source custody mismatch")
            if source.selected_governed_meanings:
                _issue(issues, "input.source_manifest.selected_governed_meanings", Code.RETENTION_MISMATCH, "41E requires the pre-integration selected section to be empty")
            for name in SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS:
                if getattr(source, name):
                    _issue(issues, f"input.source_manifest.{name}", Code.DOWNSTREAM_AUTHORITY, "downstream section must remain empty")

    if (
        source is not None
        and gate_ok
        and construction_ok
        and package_ok
        and type(value.selected_meaning_construction_input) is SelectedMeaningConstructionInput
        and type(value.selected_meaning_package) is SelectedMeaningConstructionPackage
    ):
        package = value.selected_meaning_package
        construction = value.selected_meaning_construction_input
        candidate = package.selected_candidate_record
        matching = tuple(item for item in source.candidate_meanings if item.record_id == candidate.record_id)
        if matching != (candidate,):
            _issue(issues, "input.source_manifest.candidate_meanings", Code.CANDIDATE_MISMATCH, "source manifest must contain the exact selected candidate once")
        if package.selected_candidate_companion != construction.selected_candidate_companion:
            _issue(issues, "input.selected_meaning_package.selected_candidate_companion", Code.CANDIDATE_MISMATCH, "candidate companion mismatch")
        if value.source_gate_integration_result.companion != construction.eligibility_evaluation_input.msm_gate_custody_companion:
            _issue(issues, "input.source_gate_integration_result.companion", Code.SLICE40H_CUSTODY_MISMATCH, "exact Slice 40H companion required by 41D input")
        if package.selection_trace.gate_custody_ref != value.source_gate_integration_result.companion.companion_id:
            _issue(issues, "input.selected_meaning_package.selection_trace.gate_custody_ref", Code.SLICE40H_CUSTODY_MISMATCH, "41D trace must bind exact Slice 40H companion")
        if package.selection_trace.gate_composition_result_ref != value.source_gate_integration_result.companion.composition_result_id:
            _issue(issues, "input.selected_meaning_package.selection_trace.gate_composition_result_ref", Code.SLICE40H_CUSTODY_MISMATCH, "41D trace must bind exact Slice 40G composition")
        if candidate.lineage_id != source.lineage_root.lineage_id:
            _issue(issues, "input.selected_meaning_package.selected_candidate_record.lineage_id", Code.LINEAGE_MISMATCH, "selected candidate lineage must match source manifest")
        if package.msm_v1_modified or package.governed_outward_meaning_created:
            _issue(issues, "input.selected_meaning_package", Code.DOWNSTREAM_AUTHORITY, "41D package must remain pre-integration and pre-outward")

    expected = _safe_expected(issues, "input.integration_input_id", lambda: expected_input_id(value))
    if expected is not None and value.integration_input_id != expected:
        _issue(issues, "input.integration_input_id", Code.IDENTITY_MISMATCH, "input ID mismatch")
    return _report(issues)


def _expected_candidate_ancestry(value: MsmSelectedMeaningIntegrationInput) -> tuple[str, ...]:
    package = value.selected_meaning_package
    companion = package.selected_candidate_companion
    return (
        package.selected_candidate_record.record_id,
        companion.companion_id,
        companion.candidate_meaning_id,
        companion.candidate_state_id,
        companion.candidate_identity_ref,
        companion.candidate_content_ref,
        companion.candidate_provenance_ref,
        companion.construction_receipt_ref,
        companion.construction_trace_reference_id,
        companion.provenance_reference_id,
        companion.limitation_reference_id,
        *companion.alternative_relationship_ids,
    )


def _expected_gate_ancestry(value: MsmSelectedMeaningIntegrationInput) -> tuple[str, ...]:
    companion = value.slice40h_companion
    package = value.selected_meaning_package
    return (
        companion.companion_id,
        *(item.custody_id for item in companion.family_custody),
        *(item.result_id for item in companion.family_custody),
        companion.composition_result_id,
        *companion.composition_disposition_refs,
        package.selection_trace.gate_custody_ref,
        package.selection_trace.gate_composition_result_ref,
    )


def validate_integration_result(
    value: object,
    *,
    integration_input: MsmSelectedMeaningIntegrationInput | None = None,
) -> Report:
    issues: list[Issue] = []
    if type(value) is not MsmSelectedMeaningIntegrationResult:
        return Report((Issue("result", Code.TYPE_MISMATCH, "exact result type required"),))
    if type(integration_input) is not MsmSelectedMeaningIntegrationInput:
        return Report((Issue("integration_input", Code.TYPE_MISMATCH, "exact integration input required"),))

    input_report = validate_integration_input(integration_input)
    issues.extend(input_report.issues)
    if not input_report.ok:
        _true_flags(
            value,
            (
                "deterministic",
                "additive_only",
                "immutable_successor_created",
                "exact_slice40h_custody_preserved",
                "exact_slice41d_package_preserved",
                "exact_selected_candidate_preserved",
                "exact_selection_receipt_bound",
                "candidate_and_gate_ancestry_preserved",
                "all_candidate_meanings_retained",
                "all_non_selection_outcomes_retained",
                "complete_successor_manifest_validated",
                "selected_meaning_integrated",
            ),
            "result",
            issues,
        )
        return _report(issues)

    source = integration_input.source_manifest
    package = integration_input.selected_meaning_package
    candidate = package.selected_candidate_record
    authority = value.authority_reference_record
    selected = value.integrated_selected_meaning_record
    trace = value.semantic_transition_trace
    successor = value.successor_manifest

    if type(value.source_manifest) is not MeaningStructureManifestV1 or value.source_manifest != source:
        _issue(issues, "result.source_manifest", Code.CANONICAL_MISMATCH, "source manifest not preserved exactly")

    authority_ok = type(authority) is ExternalAuthorityReferenceRecord
    if not authority_ok:
        _issue(issues, "result.authority_reference_record", Code.TYPE_MISMATCH, "exact authority reference type required")
    else:
        expected = _safe_expected(issues, "result.authority_reference_record.record_id", lambda: expected_authority_reference_id(authority))
        if expected is not None and authority.record_id != expected:
            _issue(issues, "result.authority_reference_record.record_id", Code.IDENTITY_MISMATCH, "authority record ID mismatch")
        if authority.lineage_id != source.lineage_root.lineage_id:
            _issue(issues, "result.authority_reference_record.lineage_id", Code.LINEAGE_MISMATCH, "authority lineage mismatch")
        if authority.authority_kind is not ExternalAuthorityKind.INVOCATION_EXECUTION_OR_VERIFICATION_RECEIPT:
            _issue(issues, "result.authority_reference_record.authority_kind", Code.SELECTION_AUTHORITY_MISMATCH, "verification-receipt authority kind required")
        if authority.external_object_ref != package.selection_receipt.receipt_id:
            _issue(issues, "result.authority_reference_record.external_object_ref", Code.SELECTION_AUTHORITY_MISMATCH, "exact Slice 41D selection receipt required")
        if authority.semantic_relevance != "slice41d_selection_authority_receipt":
            _issue(issues, "result.authority_reference_record.semantic_relevance", Code.SELECTION_AUTHORITY_MISMATCH, "selection authority relevance mismatch")

    selected_ok = type(selected) is SelectedGovernedMeaningRecord
    if not selected_ok:
        _issue(issues, "result.integrated_selected_meaning_record", Code.TYPE_MISMATCH, "exact selected record required")
    else:
        expected = _safe_expected(issues, "result.integrated_selected_meaning_record.record_id", lambda: expected_selected_record_id(selected))
        if expected is not None and selected.record_id != expected:
            _issue(issues, "result.integrated_selected_meaning_record.record_id", Code.IDENTITY_MISMATCH, "selected record ID mismatch")
        exact = {
            "lineage_id": candidate.lineage_id,
            "selected_candidate_ref": candidate.record_id,
            "selection_authority_ref": package.selection_receipt.receipt_id,
            "communicative_act": candidate.communicative_act,
            "concept_refs": candidate.concept_refs,
            "relation_refs": candidate.relation_refs,
            "meaning_modifiers": candidate.meaning_modifiers,
            "inherited_limitations": package.inherited_limitation_refs,
            "authority_sensitive_distinctions": candidate.authority_sensitive_implications,
            "preservation_classes": candidate.preservation_classes,
        }
        for name, expected_value in exact.items():
            if getattr(selected, name) != expected_value:
                code = Code.SELECTION_AUTHORITY_MISMATCH if name == "selection_authority_ref" else Code.SEMANTIC_CONTENT_MISMATCH
                _issue(issues, f"result.integrated_selected_meaning_record.{name}", code, "integrated selected field mismatch")
        dormant = package.selected_meaning_record
        for name in (
            "lineage_id",
            "selected_candidate_ref",
            "communicative_act",
            "concept_refs",
            "relation_refs",
            "meaning_modifiers",
            "inherited_limitations",
            "authority_sensitive_distinctions",
            "preservation_classes",
        ):
            if getattr(selected, name) != getattr(dormant, name):
                _issue(issues, f"result.integrated_selected_meaning_record.{name}", Code.SEMANTIC_CONTENT_MISMATCH, "41D dormant selected content changed")

    trace_ok = type(trace) is SemanticTransitionTraceRecord
    if not trace_ok:
        _issue(issues, "result.semantic_transition_trace", Code.TYPE_MISMATCH, "exact transition trace required")
    else:
        expected = _safe_expected(issues, "result.semantic_transition_trace.record_id", lambda: expected_transition_trace_id(trace))
        if expected is not None and trace.record_id != expected:
            _issue(issues, "result.semantic_transition_trace.record_id", Code.IDENTITY_MISMATCH, "trace ID mismatch")
        exact = {
            "lineage_id": source.lineage_root.lineage_id,
            "from_record_ref": candidate.record_id,
            "to_record_ref": selected.record_id if selected_ok else "",
            "from_state": SemanticLifecycleState.CANDIDATE_MEANING,
            "to_state": SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
            "transition_kind": SemanticTransitionKind.ANCESTRY,
            "reason": integration_input.semantic_transition_reason,
            "authority_reference_ref": authority.record_id if authority_ok else "",
        }
        for name, expected_value in exact.items():
            if getattr(trace, name) != expected_value:
                _issue(issues, f"result.semantic_transition_trace.{name}", Code.TRANSITION_MISMATCH, "lawful transition field mismatch")

    successor_ok = type(successor) is MeaningStructureManifestV1
    if not successor_ok:
        _issue(issues, "result.successor_manifest", Code.TYPE_MISMATCH, "exact MSM-v1 successor required")
    else:
        if selected_ok and authority_ok and trace_ok:
            expected = _safe_expected(
                issues,
                "result.successor_manifest.manifest_id",
                lambda: expected_successor_manifest_id(source, selected, authority, trace, integration_input),
            )
            if expected is not None and successor.manifest_id != expected:
                _issue(issues, "result.successor_manifest.manifest_id", Code.IDENTITY_MISMATCH, "successor manifest ID mismatch")

        exact_sections = {
            "lineage_root": source.lineage_root,
            "candidate_meanings": source.candidate_meanings,
            "non_selection_outcomes": source.non_selection_outcomes,
            "governed_result_references": source.governed_result_references,
            "governed_outward_meanings": source.governed_outward_meanings,
            "expression_links": source.expression_links,
            "validation_links": source.validation_links,
            "delivery_or_containment_links": source.delivery_or_containment_links,
        }
        for name, expected_value in exact_sections.items():
            if getattr(successor, name) != expected_value:
                _issue(issues, f"result.successor_manifest.{name}", Code.RETENTION_MISMATCH, "source section changed or was not retained")
        if selected_ok and successor.selected_governed_meanings != (*source.selected_governed_meanings, selected):
            _issue(issues, "result.successor_manifest.selected_governed_meanings", Code.RETENTION_MISMATCH, "selected record append mismatch")
        if authority_ok and successor.external_authority_references != (*source.external_authority_references, authority):
            _issue(issues, "result.successor_manifest.external_authority_references", Code.RETENTION_MISMATCH, "authority append mismatch")
        if trace_ok and successor.semantic_transition_traces != (*source.semantic_transition_traces, trace):
            _issue(issues, "result.successor_manifest.semantic_transition_traces", Code.RETENTION_MISMATCH, "transition append mismatch")
        for name in SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS:
            if getattr(successor, name):
                _issue(issues, f"result.successor_manifest.{name}", Code.DOWNSTREAM_AUTHORITY, "downstream section must remain empty")
        try:
            successor_report = validate_manifest(successor)
        except Exception as error:
            _issue(issues, "result.successor_manifest", Code.SUCCESSOR_MANIFEST_INVALID, f"successor validation raised: {error}")
        else:
            if not successor_report.ok:
                _issue(issues, "result.successor_manifest", Code.SUCCESSOR_MANIFEST_INVALID, "complete successor manifest validation failed")
        try:
            if deserialize_manifest(serialize_manifest(successor)) != successor:
                _issue(issues, "result.successor_manifest", Code.CANONICAL_MISMATCH, "successor canonical roundtrip failed")
        except Exception as error:
            _issue(issues, "result.successor_manifest", Code.SUCCESSOR_MANIFEST_INVALID, f"successor serialization failed: {error}")

    companion = value.companion
    if type(companion) is not MsmSelectedMeaningCustodyCompanionV1:
        _issue(issues, "result.companion", Code.TYPE_MISMATCH, "exact companion required")
    else:
        expected = _safe_expected(issues, "result.companion.companion_id", lambda: expected_companion_id(companion))
        if expected is not None and companion.companion_id != expected:
            _issue(issues, "result.companion.companion_id", Code.IDENTITY_MISMATCH, "companion ID mismatch")
        if successor_ok and selected_ok and authority_ok and trace_ok:
            exact = {
                "companion_version": SLICE41E_COMPANION_VERSION,
                "integration_input_ref": integration_input.integration_input_id,
                "source_manifest_id": source.manifest_id,
                "successor_manifest_id": successor.manifest_id,
                "lineage_id": source.lineage_root.lineage_id,
                "selected_candidate_ref": candidate.record_id,
                "dormant_selected_meaning_ref": package.selected_meaning_record.record_id,
                "integrated_selected_meaning_ref": selected.record_id,
                "selection_eligibility_result_ref": package.eligibility_result_ref,
                "selection_decision_ref": package.decision_record.decision_id,
                "selection_trace_ref": package.selection_trace.trace_id,
                "selection_receipt_ref": package.selection_receipt.receipt_id,
                "content_proof_ref": package.content_proof.proof_id,
                "selection_authority_reference_record_ref": authority.record_id,
                "slice40h_companion_ref": integration_input.slice40h_companion.companion_id,
                "slice40h_custody_companion": integration_input.slice40h_companion,
                "candidate_refs_before": tuple(item.record_id for item in source.candidate_meanings),
                "candidate_refs_after": tuple(item.record_id for item in successor.candidate_meanings),
                "non_selection_outcome_refs_before": tuple(item.record_id for item in source.non_selection_outcomes),
                "non_selection_outcome_refs_after": tuple(item.record_id for item in successor.non_selection_outcomes),
                "source_external_authority_refs": tuple(item.record_id for item in source.external_authority_references),
                "added_external_authority_refs": (authority.record_id,),
                "source_transition_trace_refs": tuple(item.record_id for item in source.semantic_transition_traces),
                "added_transition_trace_refs": (trace.record_id,),
                "preserved_alternative_refs": tuple(item.preservation_id for item in package.preserved_alternatives),
                "unresolved_alternative_refs": package.unresolved_alternative_refs,
                "candidate_ancestry_refs": _expected_candidate_ancestry(integration_input),
                "gate_ancestry_refs": _expected_gate_ancestry(integration_input),
            }
            for name, expected_value in exact.items():
                if getattr(companion, name) != expected_value:
                    _issue(issues, f"result.companion.{name}", Code.CANONICAL_MISMATCH, "companion custody mismatch")
        _true_flags(
            companion,
            (
                "exact_adapter",
                "lossless_custody",
                "immutable_successor",
                "selected_record_integrated",
                "selection_authority_receipt_bound",
                "candidate_ancestry_preserved",
                "gate_ancestry_preserved",
                "all_candidate_meanings_retained",
                "all_non_selection_outcomes_retained",
                "slice40h_companion_retained",
                "complete_successor_manifest_validated",
            ),
            "result.companion",
            issues,
        )
        _false_flags(companion, ("msm_schema_modified", "automatic_migration_performed"), "result.companion", issues)

    receipt = value.receipt
    if type(receipt) is not MsmSelectedMeaningIntegrationReceiptV1:
        _issue(issues, "result.receipt", Code.TYPE_MISMATCH, "exact receipt required")
    else:
        expected = _safe_expected(issues, "result.receipt.receipt_id", lambda: expected_receipt_id(receipt))
        if expected is not None and receipt.receipt_id != expected:
            _issue(issues, "result.receipt.receipt_id", Code.IDENTITY_MISMATCH, "receipt ID mismatch")
        if successor_ok and selected_ok and authority_ok and trace_ok:
            exact = {
                "receipt_version": SLICE41E_RECEIPT_VERSION,
                "integration_input_ref": integration_input.integration_input_id,
                "source_manifest_ref": source.manifest_id,
                "successor_manifest_ref": successor.manifest_id,
                "source_gate_integration_result_ref": integration_input.source_gate_integration_result.result_id,
                "slice40h_companion_ref": integration_input.slice40h_companion.companion_id,
                "slice41d_package_ref": package.package_id,
                "slice41d_selection_receipt_ref": package.selection_receipt.receipt_id,
                "selection_authority_reference_record_ref": authority.record_id,
                "selected_candidate_ref": candidate.record_id,
                "integrated_selected_meaning_ref": selected.record_id,
                "semantic_transition_trace_ref": trace.record_id,
                "candidate_count_before": len(source.candidate_meanings),
                "candidate_count_after": len(successor.candidate_meanings),
                "non_selection_count_before": len(source.non_selection_outcomes),
                "non_selection_count_after": len(successor.non_selection_outcomes),
                "selected_count_before": len(source.selected_governed_meanings),
                "selected_count_after": len(successor.selected_governed_meanings),
            }
            source_hash = _safe_expected(
                issues,
                "result.receipt.source_manifest_sha256",
                lambda: canonical_manifest_sha256(source),
            )
            successor_hash = _safe_expected(
                issues,
                "result.receipt.successor_manifest_sha256",
                lambda: canonical_manifest_sha256(successor),
            )
            if source_hash is not None:
                exact["source_manifest_sha256"] = source_hash
            if successor_hash is not None:
                exact["successor_manifest_sha256"] = successor_hash
            for name, expected_value in exact.items():
                if getattr(receipt, name) != expected_value:
                    _issue(issues, f"result.receipt.{name}", Code.CANONICAL_MISMATCH, "receipt field mismatch")
        _true_flags(
            receipt,
            (
                "deterministic",
                "immutable_successor_created",
                "selected_meaning_integrated",
                "complete_manifest_validated",
                "candidates_retained",
                "non_selection_outcomes_retained",
                "slice40h_companion_retained",
            ),
            "result.receipt",
            issues,
        )
        _false_flags(
            receipt,
            (
                "msm_schema_modified",
                "governed_outward_meaning_created",
                "expression_link_created",
                "validation_link_created",
                "delivery_link_created",
                "truth_determined",
                "evidence_validated",
                "permission_granted",
                "execution_authorized",
                "route_created",
                "tool_invoked",
                "action_performed",
                "memory_accessed",
                "memory_written",
                "rendered",
                "delivered",
            ),
            "result.receipt",
            issues,
        )

    _true_flags(
        value,
        (
            "deterministic",
            "additive_only",
            "immutable_successor_created",
            "exact_slice40h_custody_preserved",
            "exact_slice41d_package_preserved",
            "exact_selected_candidate_preserved",
            "exact_selection_receipt_bound",
            "candidate_and_gate_ancestry_preserved",
            "all_candidate_meanings_retained",
            "all_non_selection_outcomes_retained",
            "complete_successor_manifest_validated",
            "selected_meaning_integrated",
        ),
        "result",
        issues,
    )
    _false_flags(
        value,
        (
            "msm_schema_modified",
            "automatic_migration_performed",
            "candidate_deleted",
            "non_selection_outcome_deleted",
            "gate_custody_deleted",
            "governed_result_reference_created",
            "governed_outward_meaning_created",
            "expression_link_created",
            "validation_link_created",
            "delivery_link_created",
            "truth_determined",
            "evidence_validated",
            "permission_granted",
            "execution_authorized",
            "capability_availability_created",
            "route_created",
            "tool_invoked",
            "action_performed",
            "memory_accessed",
            "memory_written",
            "rendered",
            "delivered",
            "filesystem_read_performed",
            "filesystem_write_performed",
            "network_access_performed",
            "external_resource_loaded",
            "language_model_used",
            "embedding_used",
            "vector_used",
            "rag_used",
            "semantic_similarity_used",
            "bootstrap_integration_enabled",
        ),
        "result",
        issues,
    )
    expected_digest = _safe_expected(issues, "result.canonical_digest", lambda: expected_result_digest(value))
    expected_id = _safe_expected(issues, "result.result_id", lambda: expected_result_id(value))
    if expected_digest is not None and value.canonical_digest != expected_digest:
        _issue(issues, "result.canonical_digest", Code.IDENTITY_MISMATCH, "result digest mismatch")
    if expected_id is not None and value.result_id != expected_id:
        _issue(issues, "result.result_id", Code.IDENTITY_MISMATCH, "result ID mismatch")
    return _report(issues)


def assert_valid_integration_input(value: object) -> None:
    report = validate_integration_input(value)
    if not report.ok:
        raise MsmSelectedMeaningIntegrationValidationError(report)


def assert_valid_integration_result(
    value: object,
    *,
    integration_input: MsmSelectedMeaningIntegrationInput,
) -> None:
    report = validate_integration_result(value, integration_input=integration_input)
    if not report.ok:
        raise MsmSelectedMeaningIntegrationValidationError(report)


__all__ = (
    "assert_valid_integration_input",
    "assert_valid_integration_result",
    "validate_authority_profile",
    "validate_integration_input",
    "validate_integration_result",
)
