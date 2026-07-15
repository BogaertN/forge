"""Disabled-by-default in-memory MSM-v1 bootstrap integration for Slice 35E.

This module connects the accepted MeaningStructureManifest v1 schema to the
isolated language-core bootstrap boundary only through an explicit offline,
synthetic-fixture path. Importing the module performs no work. The default
execution path refuses. The enabled path validates the bootstrap boundary,
validates one synthetic in-memory manifest, performs canonical serialization
and strict deserialization, and returns an immutable result record.

It does not register routes, APIs, UI, memory, evidence mutation, external
resources, delivery, tools, actions, GP-014, network access, filesystem I/O,
production authority, or release authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final

from ..boundary import build_bootstrap_boundary_bundle
from ..schema import (
    SCHEMA_VERSION as BOOTSTRAP_SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    require_non_empty_text,
    require_true,
    stable_record_id,
)
from ..verify import verify_bootstrap_boundary_bundle
from ._enums import (
    DeliveryContainmentKind,
    ExternalAuthorityKind,
    LineageOriginKind,
    NonSelectionOutcomeKind,
    SemanticDirection,
    SemanticPreservationClass,
    SemanticTransitionKind,
)
from ._records import (
    CandidateMeaningRecord,
    DeliveryContainmentLinkRecord,
    ExpressionLinkRecord,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    GovernedResultReferenceRecord,
    LineageRootRecord,
    MeaningStructureManifestV1,
    NonSelectionOutcomeRecord,
    SelectedGovernedMeaningRecord,
    ValidationLinkRecord,
)
from .lifecycle import append_lifecycle_successor
from .serialization import (
    CanonicalSerializationError,
    canonical_manifest_sha256,
    deserialize_manifest,
    serialize_manifest,
)
from .validation import validate_manifest

INTEGRATION_SPEC_ID: Final[str] = "aiweb-msm-v1-bootstrap-integration"
INTEGRATION_SPEC_VERSION: Final[str] = "aiweb-msm-v1-bootstrap-integration-v1"
INTEGRATION_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-msm-bootstrap-integration-v1"
)

STATUS_REFUSED_DISABLED: Final[str] = "refused_msm_bootstrap_integration_disabled"
STATUS_HELD_INVALID_STATE: Final[str] = "held_invalid_msm_bootstrap_state"
STATUS_HELD_INVALID_FIXTURE: Final[str] = "held_invalid_msm_bootstrap_fixture"
STATUS_HELD_INVALID_BOOTSTRAP: Final[str] = "held_invalid_bootstrap_boundary"
STATUS_HELD_INVALID_MANIFEST: Final[str] = "held_invalid_meaning_structure_manifest"
STATUS_HELD_SERIALIZATION_FAILURE: Final[str] = "held_canonical_serialization_failure"
STATUS_HELD_ROUND_TRIP_MISMATCH: Final[str] = "held_canonical_round_trip_mismatch"
STATUS_COMPLETED: Final[str] = "completed_bounded_msm_bootstrap_integration"

REASON_DISABLED: Final[str] = "explicit_offline_msm_bootstrap_enable_required"
REASON_COMPLETED: Final[str] = (
    "validated_manifest_round_tripped_inside_disabled_bootstrap_boundary"
)

_FALSE_ONLY_STATE_FIELDS: Final[tuple[str, ...]] = (
    "runtime_connected",
    "component_loading_allowed",
    "route_allowed",
    "api_allowed",
    "ui_allowed",
    "network_allowed",
    "filesystem_read_allowed",
    "filesystem_write_allowed",
    "environment_backend_selection_allowed",
    "dynamic_loading_allowed",
    "external_resource_allowed",
    "memory_read_allowed",
    "memory_write_allowed",
    "evidence_mutation_allowed",
    "delivery_allowed",
    "tool_routing_allowed",
    "action_allowed",
    "gp014_import_allowed",
    "gp014_call_allowed",
    "llm_authority_allowed",
    "vector_authority_allowed",
    "embedding_authority_allowed",
    "rag_authority_allowed",
    "release_authorized",
    "production_ready",
)

_TRUE_ONLY_STATE_FIELDS: Final[tuple[str, ...]] = (
    "disabled_by_default",
    "fixture_only",
    "offline_only",
    "read_only",
    "in_memory_only",
    "deterministic",
)

_FALSE_ONLY_RESULT_FIELDS: Final[tuple[str, ...]] = (
    "runtime_connection_performed",
    "component_loading_performed",
    "route_registration_performed",
    "api_registration_performed",
    "ui_connection_performed",
    "network_access_performed",
    "filesystem_read_performed",
    "filesystem_write_performed",
    "environment_backend_selected",
    "dynamic_loading_performed",
    "external_resource_used",
    "memory_read_performed",
    "memory_write_performed",
    "evidence_mutation_performed",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "gp014_imported",
    "gp014_called",
    "llm_authority_used",
    "vector_authority_used",
    "embedding_authority_used",
    "rag_authority_used",
    "technical_acceptance_granted_by_runtime",
    "release_authorized",
    "production_ready",
)


@dataclass(frozen=True, slots=True)
class MsmBootstrapIntegrationState:
    state_id: str
    enabled: bool
    explicit_offline_developer_enable: bool
    disabled_by_default: bool
    fixture_only: bool
    offline_only: bool
    read_only: bool
    in_memory_only: bool
    deterministic: bool
    runtime_connected: bool
    component_loading_allowed: bool
    route_allowed: bool
    api_allowed: bool
    ui_allowed: bool
    network_allowed: bool
    filesystem_read_allowed: bool
    filesystem_write_allowed: bool
    environment_backend_selection_allowed: bool
    dynamic_loading_allowed: bool
    external_resource_allowed: bool
    memory_read_allowed: bool
    memory_write_allowed: bool
    evidence_mutation_allowed: bool
    delivery_allowed: bool
    tool_routing_allowed: bool
    action_allowed: bool
    gp014_import_allowed: bool
    gp014_call_allowed: bool
    llm_authority_allowed: bool
    vector_authority_allowed: bool
    embedding_authority_allowed: bool
    rag_authority_allowed: bool
    release_authorized: bool
    production_ready: bool
    integration_spec_id: str = INTEGRATION_SPEC_ID
    integration_spec_version: str = INTEGRATION_SPEC_VERSION
    schema_version: str = INTEGRATION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("msm_bootstrap_integration_state", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MsmBootstrapFixtureRecord:
    fixture_id: str
    fixture_name: str
    source_classification: str
    expected_manifest_id: str
    expected_canonical_sha256: str
    manifest: MeaningStructureManifestV1
    synthetic: bool
    accepted_fixture: bool
    offline_only: bool
    in_memory_only: bool
    schema_version: str = INTEGRATION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        return {
            "fixture_name": self.fixture_name,
            "source_classification": self.source_classification,
            "expected_manifest_id": self.expected_manifest_id,
            "expected_canonical_sha256": self.expected_canonical_sha256,
            "synthetic": self.synthetic,
            "accepted_fixture": self.accepted_fixture,
            "offline_only": self.offline_only,
            "in_memory_only": self.in_memory_only,
            "schema_version": self.schema_version,
        }

    def expected_id(self) -> str:
        return stable_record_id("msm_bootstrap_fixture", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        body = self.canonical_body()
        body["fixture_id"] = self.fixture_id
        return body


@dataclass(frozen=True, slots=True)
class MsmBootstrapIntegrationResult:
    result_id: str
    state_id: str
    fixture_id: str
    status: str
    reason_code: str
    bootstrap_schema_version: str
    bootstrap_authority_state_id: str
    bootstrap_boundary_id: str
    component_registry_id: str
    import_policy_id: str
    manifest_id: str
    canonical_sha256: str
    canonical_byte_count: int
    manifest_validation_passed: bool
    round_trip_equal: bool
    bounded_integration_completed: bool
    deterministic: bool
    fixture_only: bool
    offline_only: bool
    read_only: bool
    in_memory_only: bool
    runtime_connection_performed: bool
    component_loading_performed: bool
    route_registration_performed: bool
    api_registration_performed: bool
    ui_connection_performed: bool
    network_access_performed: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    environment_backend_selected: bool
    dynamic_loading_performed: bool
    external_resource_used: bool
    memory_read_performed: bool
    memory_write_performed: bool
    evidence_mutation_performed: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    gp014_imported: bool
    gp014_called: bool
    llm_authority_used: bool
    vector_authority_used: bool
    embedding_authority_used: bool
    rag_authority_used: bool
    technical_acceptance_granted_by_runtime: bool
    release_authorized: bool
    production_ready: bool
    integration_spec_id: str = INTEGRATION_SPEC_ID
    integration_spec_version: str = INTEGRATION_SPEC_VERSION
    schema_version: str = INTEGRATION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("msm_bootstrap_integration_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_msm_bootstrap_integration_state(
    *, explicit_offline_developer_enable: bool = False
) -> MsmBootstrapIntegrationState:
    enabled = explicit_offline_developer_enable is True
    body = {
        "enabled": enabled,
        "explicit_offline_developer_enable": enabled,
        "disabled_by_default": True,
        "fixture_only": True,
        "offline_only": True,
        "read_only": True,
        "in_memory_only": True,
        "deterministic": True,
        "runtime_connected": False,
        "component_loading_allowed": False,
        "route_allowed": False,
        "api_allowed": False,
        "ui_allowed": False,
        "network_allowed": False,
        "filesystem_read_allowed": False,
        "filesystem_write_allowed": False,
        "environment_backend_selection_allowed": False,
        "dynamic_loading_allowed": False,
        "external_resource_allowed": False,
        "memory_read_allowed": False,
        "memory_write_allowed": False,
        "evidence_mutation_allowed": False,
        "delivery_allowed": False,
        "tool_routing_allowed": False,
        "action_allowed": False,
        "gp014_import_allowed": False,
        "gp014_call_allowed": False,
        "llm_authority_allowed": False,
        "vector_authority_allowed": False,
        "embedding_authority_allowed": False,
        "rag_authority_allowed": False,
        "release_authorized": False,
        "production_ready": False,
        "integration_spec_id": INTEGRATION_SPEC_ID,
        "integration_spec_version": INTEGRATION_SPEC_VERSION,
        "schema_version": INTEGRATION_SCHEMA_VERSION,
    }
    return MsmBootstrapIntegrationState(
        state_id=stable_record_id("msm_bootstrap_integration_state", body),
        **body,
    )


def _authority(
    record_id: str,
    external_object_ref: str,
    authority_kind: ExternalAuthorityKind,
) -> ExternalAuthorityReferenceRecord:
    return ExternalAuthorityReferenceRecord(
        record_id=record_id,
        lineage_id="slice35e-lineage-001",
        authority_kind=authority_kind,
        external_object_ref=external_object_ref,
        semantic_relevance=f"bounds_{record_id}",
    )


def build_synthetic_msm_bootstrap_fixture() -> MsmBootstrapFixtureRecord:
    """Build the one deterministic synthetic fixture accepted by Slice 35E."""

    preservation = (
        SemanticPreservationClass.NEGATION,
        SemanticPreservationClass.UNCERTAINTY_AND_CLAIM_STRENGTH,
        SemanticPreservationClass.NON_LLM_PROVENANCE,
    )
    root = LineageRootRecord(
        lineage_id="slice35e-lineage-001",
        origin_kind=LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION,
        origin_ref="slice35e-source-event-001",
        direction=SemanticDirection.INWARD,
    )
    candidate = CandidateMeaningRecord(
        record_id="slice35e-candidate-001",
        lineage_id=root.lineage_id,
        source_expression_ref=root.origin_ref,
        communicative_act="bounded_bootstrap_fixture_inspection",
        concept_refs=("concept-msm-bootstrap",),
        relation_refs=("relation-bounded-integration",),
        meaning_modifiers=("fixture_only", "offline_only", "read_only"),
        ambiguity_reasons=(),
        unresolved_referents=(),
        authority_sensitive_implications=("meaning_not_action",),
        preservation_classes=preservation,
    )
    authorities = (
        _authority(
            "slice35e-authority-gate",
            "slice35e-gate-receipt-001",
            ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
        _authority(
            "slice35e-authority-result",
            "slice35e-result-receipt-001",
            ExternalAuthorityKind.INVOCATION_EXECUTION_OR_VERIFICATION_RECEIPT,
        ),
        _authority(
            "slice35e-authority-outward",
            "slice35e-outward-authority-001",
            ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
        _authority(
            "slice35e-authority-render",
            "slice35e-render-candidate-001",
            ExternalAuthorityKind.RENDER_PREVIEW_OR_OUTPUT_OBJECT,
        ),
        _authority(
            "slice35e-authority-echo",
            "slice35e-echo-receipt-001",
            ExternalAuthorityKind.RMC_ECHO_VALIDATOR_RECEIPT,
        ),
        _authority(
            "slice35e-authority-containment",
            "slice35e-containment-receipt-001",
            ExternalAuthorityKind.DELIVERY_OR_CONTAINMENT_RECEIPT,
        ),
        _authority(
            "slice35e-authority-unresolved",
            "slice35e-unresolved-receipt-001",
            ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
    )
    unresolved = NonSelectionOutcomeRecord(
        record_id="slice35e-outcome-unresolved-001",
        lineage_id=root.lineage_id,
        outcome_kind=NonSelectionOutcomeKind.UNRESOLVED,
        candidate_refs=(candidate.record_id,),
        reasons=("preserved_non_selected_alternative",),
        required_clarifications=(),
        external_authority_refs=("slice35e-authority-unresolved",),
    )
    manifest = MeaningStructureManifestV1(
        manifest_id="slice35e-msm-fixture-001",
        lineage_root=root,
        candidate_meanings=(candidate,),
        non_selection_outcomes=(unresolved,),
        selected_governed_meanings=(),
        governed_result_references=(),
        governed_outward_meanings=(),
        expression_links=(),
        validation_links=(),
        delivery_or_containment_links=(),
        external_authority_references=authorities,
        semantic_transition_traces=(),
    )
    selected = SelectedGovernedMeaningRecord(
        record_id="slice35e-selected-001",
        lineage_id=root.lineage_id,
        selected_candidate_ref=candidate.record_id,
        selection_authority_ref="slice35e-gate-receipt-001",
        communicative_act=candidate.communicative_act,
        concept_refs=candidate.concept_refs,
        relation_refs=candidate.relation_refs,
        meaning_modifiers=candidate.meaning_modifiers,
        inherited_limitations=("fixture_scope_only",),
        authority_sensitive_distinctions=("selected_not_authorized",),
        preservation_classes=preservation,
    )
    step1 = append_lifecycle_successor(
        manifest,
        trace_record_id="slice35e-trace-001",
        from_record_ref=candidate.record_id,
        successor=selected,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason="deterministic_fixture_gate_selection",
        authority_reference_ref="slice35e-authority-gate",
    )
    result_reference = GovernedResultReferenceRecord(
        record_id="slice35e-result-001",
        lineage_id=root.lineage_id,
        selected_meaning_ref=selected.record_id,
        external_authority_ref="slice35e-authority-result",
        semantic_relevance="bounded_fixture_result",
    )
    step2 = append_lifecycle_successor(
        step1.manifest,
        trace_record_id="slice35e-trace-002",
        from_record_ref=selected.record_id,
        successor=result_reference,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason="fixture_result_reference_linked",
        authority_reference_ref="slice35e-authority-result",
    )
    outward = GovernedOutwardMeaningRecord(
        record_id="slice35e-outward-001",
        lineage_id=root.lineage_id,
        outward_basis_refs=(result_reference.record_id, "slice35e-authority-outward"),
        prior_selected_meaning_ref=selected.record_id,
        permitted_claims=("bounded_fixture_round_trip_completed",),
        required_qualifications=("offline_fixture_scope_only",),
        prohibited_enlargements=("live_runtime_authority", "production_readiness"),
        external_dependency_refs=("slice35e-authority-outward",),
        preservation_classes=preservation,
    )
    step3 = append_lifecycle_successor(
        step2.manifest,
        trace_record_id="slice35e-trace-003",
        from_record_ref=result_reference.record_id,
        successor=outward,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason="fixture_outward_meaning_bounded",
        authority_reference_ref="slice35e-authority-outward",
    )
    expression = ExpressionLinkRecord(
        record_id="slice35e-expression-001",
        lineage_id=root.lineage_id,
        governed_outward_meaning_ref=outward.record_id,
        expression_candidate_ref="slice35e-render-candidate-001",
    )
    step4 = append_lifecycle_successor(
        step3.manifest,
        trace_record_id="slice35e-trace-004",
        from_record_ref=outward.record_id,
        successor=expression,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason="fixture_expression_linked",
        authority_reference_ref="slice35e-authority-render",
    )
    validation = ValidationLinkRecord(
        record_id="slice35e-validation-001",
        lineage_id=root.lineage_id,
        expression_link_ref=expression.record_id,
        external_validation_receipt_ref="slice35e-echo-receipt-001",
        external_validation_disposition="accepted_within_fixture_scope",
    )
    step5 = append_lifecycle_successor(
        step4.manifest,
        trace_record_id="slice35e-trace-005",
        from_record_ref=expression.record_id,
        successor=validation,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason="fixture_validation_receipt_linked",
        authority_reference_ref="slice35e-authority-echo",
    )
    containment = DeliveryContainmentLinkRecord(
        record_id="slice35e-containment-001",
        lineage_id=root.lineage_id,
        prior_link_ref=validation.record_id,
        disposition=DeliveryContainmentKind.CONTAINMENT_LINKED,
        external_receipt_ref="slice35e-containment-receipt-001",
    )
    step6 = append_lifecycle_successor(
        step5.manifest,
        trace_record_id="slice35e-trace-006",
        from_record_ref=validation.record_id,
        successor=containment,
        transition_kind=SemanticTransitionKind.CONTAINMENT,
        reason="fixture_is_contained_not_delivered",
        authority_reference_ref="slice35e-authority-containment",
    )
    completed_manifest = step6.manifest
    digest = canonical_manifest_sha256(completed_manifest)
    body = {
        "fixture_name": "slice35e-synthetic-msm-bootstrap-round-trip-v1",
        "source_classification": "synthetic_in_memory_msm_fixture",
        "expected_manifest_id": completed_manifest.manifest_id,
        "expected_canonical_sha256": digest,
        "synthetic": True,
        "accepted_fixture": True,
        "offline_only": True,
        "in_memory_only": True,
        "schema_version": INTEGRATION_SCHEMA_VERSION,
    }
    return MsmBootstrapFixtureRecord(
        fixture_id=stable_record_id("msm_bootstrap_fixture", body),
        manifest=completed_manifest,
        **body,
    )


def validate_msm_bootstrap_integration_state(
    record: MsmBootstrapIntegrationState,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not MsmBootstrapIntegrationState:
        return ValidationReport(
            schema_version=INTEGRATION_SCHEMA_VERSION,
            ok=False,
            issues=(issue("state", "exact_state_type_required"),),
        )
    if record.schema_version != INTEGRATION_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.integration_spec_id != INTEGRATION_SPEC_ID:
        issues.append(issue("integration_spec_id", "integration_spec_mismatch"))
    if record.integration_spec_version != INTEGRATION_SPEC_VERSION:
        issues.append(issue("integration_spec_version", "integration_spec_version_mismatch"))
    if record.state_id != record.expected_id():
        issues.append(issue("state_id", "stable_identifier_mismatch"))
    if record.enabled is not record.explicit_offline_developer_enable:
        issues.append(issue("enabled", "explicit_enable_state_mismatch"))
    for field_name in _TRUE_ONLY_STATE_FIELDS:
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    for field_name in _FALSE_ONLY_STATE_FIELDS:
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)
    return ValidationReport(
        schema_version=INTEGRATION_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_msm_bootstrap_fixture(
    record: MsmBootstrapFixtureRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not MsmBootstrapFixtureRecord:
        return ValidationReport(
            schema_version=INTEGRATION_SCHEMA_VERSION,
            ok=False,
            issues=(issue("fixture", "exact_fixture_type_required"),),
        )
    if record.schema_version != INTEGRATION_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.fixture_id != record.expected_id():
        issues.append(issue("fixture_id", "stable_identifier_mismatch"))
    require_non_empty_text(field="fixture_name", value=record.fixture_name, issues=issues)
    if record.source_classification != "synthetic_in_memory_msm_fixture":
        issues.append(issue("source_classification", "unsupported_fixture_source"))
    for field_name in ("synthetic", "accepted_fixture", "offline_only", "in_memory_only"):
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    if type(record.manifest) is not MeaningStructureManifestV1:
        issues.append(issue("manifest", "exact_manifest_type_required"))
    else:
        if record.manifest.manifest_id != record.expected_manifest_id:
            issues.append(issue("expected_manifest_id", "manifest_identity_mismatch"))
        manifest_report = validate_manifest(record.manifest)
        if not manifest_report.ok:
            issues.append(issue("manifest", "manifest_validation_failed"))
        try:
            actual_digest = canonical_manifest_sha256(record.manifest)
        except CanonicalSerializationError:
            issues.append(issue("manifest", "canonical_serialization_failed"))
        else:
            if actual_digest != record.expected_canonical_sha256:
                issues.append(issue("expected_canonical_sha256", "canonical_digest_mismatch"))
    return ValidationReport(
        schema_version=INTEGRATION_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def _result(
    *,
    state: MsmBootstrapIntegrationState,
    fixture_id: str = "",
    status: str,
    reason_code: str,
    bootstrap_authority_state_id: str = "",
    bootstrap_boundary_id: str = "",
    component_registry_id: str = "",
    import_policy_id: str = "",
    manifest_id: str = "",
    canonical_sha256: str = "",
    canonical_byte_count: int = 0,
    manifest_validation_passed: bool = False,
    round_trip_equal: bool = False,
    bounded_integration_completed: bool = False,
) -> MsmBootstrapIntegrationResult:
    body = {
        "state_id": state.state_id,
        "fixture_id": fixture_id,
        "status": status,
        "reason_code": reason_code,
        "bootstrap_schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "bootstrap_authority_state_id": bootstrap_authority_state_id,
        "bootstrap_boundary_id": bootstrap_boundary_id,
        "component_registry_id": component_registry_id,
        "import_policy_id": import_policy_id,
        "manifest_id": manifest_id,
        "canonical_sha256": canonical_sha256,
        "canonical_byte_count": canonical_byte_count,
        "manifest_validation_passed": manifest_validation_passed,
        "round_trip_equal": round_trip_equal,
        "bounded_integration_completed": bounded_integration_completed,
        "deterministic": True,
        "fixture_only": True,
        "offline_only": True,
        "read_only": True,
        "in_memory_only": True,
        "runtime_connection_performed": False,
        "component_loading_performed": False,
        "route_registration_performed": False,
        "api_registration_performed": False,
        "ui_connection_performed": False,
        "network_access_performed": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "environment_backend_selected": False,
        "dynamic_loading_performed": False,
        "external_resource_used": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "evidence_mutation_performed": False,
        "delivery_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "gp014_imported": False,
        "gp014_called": False,
        "llm_authority_used": False,
        "vector_authority_used": False,
        "embedding_authority_used": False,
        "rag_authority_used": False,
        "technical_acceptance_granted_by_runtime": False,
        "release_authorized": False,
        "production_ready": False,
        "integration_spec_id": INTEGRATION_SPEC_ID,
        "integration_spec_version": INTEGRATION_SPEC_VERSION,
        "schema_version": INTEGRATION_SCHEMA_VERSION,
    }
    return MsmBootstrapIntegrationResult(
        result_id=stable_record_id("msm_bootstrap_integration_result", body),
        **body,
    )


def validate_msm_bootstrap_integration_result(
    record: MsmBootstrapIntegrationResult,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not MsmBootstrapIntegrationResult:
        return ValidationReport(
            schema_version=INTEGRATION_SCHEMA_VERSION,
            ok=False,
            issues=(issue("result", "exact_result_type_required"),),
        )
    if record.schema_version != INTEGRATION_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.integration_spec_id != INTEGRATION_SPEC_ID:
        issues.append(issue("integration_spec_id", "integration_spec_mismatch"))
    if record.integration_spec_version != INTEGRATION_SPEC_VERSION:
        issues.append(issue("integration_spec_version", "integration_spec_version_mismatch"))
    if record.result_id != record.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))
    for field_name in ("deterministic", "fixture_only", "offline_only", "read_only", "in_memory_only"):
        require_true(field=field_name, value=getattr(record, field_name), issues=issues)
    for field_name in _FALSE_ONLY_RESULT_FIELDS:
        require_false(field=field_name, value=getattr(record, field_name), issues=issues)
    if record.status == STATUS_COMPLETED:
        if record.reason_code != REASON_COMPLETED:
            issues.append(issue("reason_code", "completed_reason_mismatch"))
        for field_name in (
            "manifest_validation_passed",
            "round_trip_equal",
            "bounded_integration_completed",
        ):
            require_true(field=field_name, value=getattr(record, field_name), issues=issues)
        for field_name in (
            "fixture_id",
            "bootstrap_authority_state_id",
            "bootstrap_boundary_id",
            "component_registry_id",
            "import_policy_id",
            "manifest_id",
            "canonical_sha256",
        ):
            require_non_empty_text(field=field_name, value=getattr(record, field_name), issues=issues)
        if record.canonical_byte_count <= 0:
            issues.append(issue("canonical_byte_count", "positive_byte_count_required"))
    elif record.bounded_integration_completed:
        issues.append(issue("bounded_integration_completed", "completion_requires_completed_status"))
    return ValidationReport(
        schema_version=INTEGRATION_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def run_msm_bootstrap_integration(
    *,
    fixture: MsmBootstrapFixtureRecord | None = None,
    integration_state: MsmBootstrapIntegrationState | None = None,
) -> MsmBootstrapIntegrationResult:
    """Run the bounded integration path, refusing unless explicitly enabled."""

    state = integration_state or build_msm_bootstrap_integration_state()
    if not validate_msm_bootstrap_integration_state(state).ok:
        return _result(
            state=state,
            fixture_id=getattr(fixture, "fixture_id", ""),
            status=STATUS_HELD_INVALID_STATE,
            reason_code="msm_bootstrap_state_validation_failed",
        )
    if not state.enabled:
        return _result(
            state=state,
            fixture_id=getattr(fixture, "fixture_id", ""),
            status=STATUS_REFUSED_DISABLED,
            reason_code=REASON_DISABLED,
        )
    if fixture is None or not validate_msm_bootstrap_fixture(fixture).ok:
        return _result(
            state=state,
            fixture_id=getattr(fixture, "fixture_id", ""),
            status=STATUS_HELD_INVALID_FIXTURE,
            reason_code="accepted_synthetic_msm_fixture_required",
        )

    bundle = build_bootstrap_boundary_bundle()
    bootstrap_report = verify_bootstrap_boundary_bundle(bundle)
    if (
        not bootstrap_report.ok
        or bundle.authority.enabled
        or not bundle.authority.disabled_by_default
        or not bundle.authority.fixture_only
        or not bundle.authority.offline_only
        or not bundle.authority.deterministic
        or bundle.authority.runtime_connected
        or bundle.authority.components_loaded
        or bundle.boundary.component_loading
        or bundle.boundary.main_connection
        or bundle.boundary.route_connection
        or bundle.boundary.ui_connection
        or bundle.boundary.persistent_side_effect
    ):
        return _result(
            state=state,
            fixture_id=fixture.fixture_id,
            status=STATUS_HELD_INVALID_BOOTSTRAP,
            reason_code="isolated_bootstrap_boundary_validation_failed",
        )

    manifest_report = validate_manifest(fixture.manifest)
    if not manifest_report.ok:
        return _result(
            state=state,
            fixture_id=fixture.fixture_id,
            status=STATUS_HELD_INVALID_MANIFEST,
            reason_code="meaning_structure_manifest_validation_failed",
            bootstrap_authority_state_id=bundle.authority.authority_state_id,
            bootstrap_boundary_id=bundle.boundary.bootstrap_boundary_id,
            component_registry_id=bundle.registry.registry_id,
            import_policy_id=bundle.import_policy.import_policy_id,
            manifest_id=fixture.manifest.manifest_id,
        )

    try:
        canonical = serialize_manifest(fixture.manifest)
        decoded = deserialize_manifest(canonical)
        digest = canonical_manifest_sha256(fixture.manifest)
    except CanonicalSerializationError:
        return _result(
            state=state,
            fixture_id=fixture.fixture_id,
            status=STATUS_HELD_SERIALIZATION_FAILURE,
            reason_code="strict_canonical_round_trip_failed",
            bootstrap_authority_state_id=bundle.authority.authority_state_id,
            bootstrap_boundary_id=bundle.boundary.bootstrap_boundary_id,
            component_registry_id=bundle.registry.registry_id,
            import_policy_id=bundle.import_policy.import_policy_id,
            manifest_id=fixture.manifest.manifest_id,
            manifest_validation_passed=True,
        )

    if (
        decoded != fixture.manifest
        or digest != fixture.expected_canonical_sha256
        or serialize_manifest(decoded) != canonical
    ):
        return _result(
            state=state,
            fixture_id=fixture.fixture_id,
            status=STATUS_HELD_ROUND_TRIP_MISMATCH,
            reason_code="canonical_round_trip_identity_mismatch",
            bootstrap_authority_state_id=bundle.authority.authority_state_id,
            bootstrap_boundary_id=bundle.boundary.bootstrap_boundary_id,
            component_registry_id=bundle.registry.registry_id,
            import_policy_id=bundle.import_policy.import_policy_id,
            manifest_id=fixture.manifest.manifest_id,
            canonical_sha256=digest,
            canonical_byte_count=len(canonical),
            manifest_validation_passed=True,
        )

    return _result(
        state=state,
        fixture_id=fixture.fixture_id,
        status=STATUS_COMPLETED,
        reason_code=REASON_COMPLETED,
        bootstrap_authority_state_id=bundle.authority.authority_state_id,
        bootstrap_boundary_id=bundle.boundary.bootstrap_boundary_id,
        component_registry_id=bundle.registry.registry_id,
        import_policy_id=bundle.import_policy.import_policy_id,
        manifest_id=fixture.manifest.manifest_id,
        canonical_sha256=digest,
        canonical_byte_count=len(canonical),
        manifest_validation_passed=True,
        round_trip_equal=True,
        bounded_integration_completed=True,
    )


__all__ = (
    "INTEGRATION_SCHEMA_VERSION",
    "INTEGRATION_SPEC_ID",
    "INTEGRATION_SPEC_VERSION",
    "MsmBootstrapFixtureRecord",
    "MsmBootstrapIntegrationResult",
    "MsmBootstrapIntegrationState",
    "REASON_COMPLETED",
    "REASON_DISABLED",
    "STATUS_COMPLETED",
    "STATUS_HELD_INVALID_BOOTSTRAP",
    "STATUS_HELD_INVALID_FIXTURE",
    "STATUS_HELD_INVALID_MANIFEST",
    "STATUS_HELD_INVALID_STATE",
    "STATUS_HELD_ROUND_TRIP_MISMATCH",
    "STATUS_HELD_SERIALIZATION_FAILURE",
    "STATUS_REFUSED_DISABLED",
    "build_msm_bootstrap_integration_state",
    "build_synthetic_msm_bootstrap_fixture",
    "run_msm_bootstrap_integration",
    "validate_msm_bootstrap_fixture",
    "validate_msm_bootstrap_integration_result",
    "validate_msm_bootstrap_integration_state",
)
