"""Core immutable records for Slice 21.

Slice 21 defines a read-only inspection surface boundary. The records in
this module are intentionally data-only. They do not register routes, read
live runtime state, write memory, widen accepted scope, promote candidates,
invoke tools, approve delivery, expose UI authority, fetch resources, or
call model/vector/RAG systems.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Final, Mapping

SLICE_ID: Final[str] = "Slice 21"
SLICE_TITLE: Final[str] = "Read-Only API / Inspection Surface Boundary Scaffold"
SCAFFOLD_VERSION: Final[str] = "1.0.0"
SCHEMA_VERSION: Final[str] = "aiweb-read-only-inspection-surface-scaffold-v1"

REQUIRED_BASE_HEAD_FOR_APPLICATION: Final[str] = "9f687f3ffa350cfe40e1e1ad4530a0e757dc262c"
REQUIRED_BASE_SUBJECT_FOR_APPLICATION: Final[str] = "Slice 20 delivery action tool-routing boundary scaffold"
REQUIRED_BASE_PARENT_FOR_APPLICATION: Final[str] = "ba50a5147acd098a28772c2cb9b5101f37c3f57f"
EXPECTED_COMMIT_SUBJECT: Final[str] = "Slice 21 read-only inspection surface scaffold"

RUNTIME_EFFECT: Final[str] = "none"
DEPENDENCY_CHANGE: Final[str] = "none"
INTEGRATION_STATE: Final[str] = "boundary_scaffold_only_not_registered_as_live_api"

ALLOWED_INSPECTION_SUBJECTS: Final[tuple[str, ...]] = (
    "meaning_records",
    "law_traces",
    "concept_boundaries",
    "predicate_frames",
    "gate_records",
    "receipts",
    "accepted_scope_status",
)

REQUIRED_BOUNDARY_LAWS: Final[tuple[str, ...]] = (
    "read_only_inspection_is_not_runtime_authority",
    "api_visibility_is_not_acceptance",
    "ui_visibility_is_not_proof",
    "inspection_surface_does_not_modify_state",
    "inspection_surface_does_not_widen_scope",
    "inspection_surface_does_not_create_acceptance",
    "inspection_surface_does_not_promote_candidates",
    "inspection_surface_does_not_write_memory",
    "inspection_surface_does_not_route_tools",
    "inspection_surface_does_not_invoke_tools",
    "inspection_surface_does_not_execute_actions",
    "inspection_surface_does_not_deliver_output",
    "inspection_surface_does_not_approve_output",
    "inspection_surface_does_not_grant_renderer_authority",
    "inspection_surface_does_not_admit_external_resources",
    "inspection_surface_does_not_fetch_resources",
    "inspection_surface_does_not_download_resources",
    "inspection_surface_does_not_ingest_resources",
    "inspection_surface_does_not_index_resources",
    "inspection_surface_does_not_call_llm",
    "inspection_surface_does_not_create_embeddings",
    "inspection_surface_does_not_run_retrieval",
    "inspection_surface_does_not_run_rag",
    "inspection_surface_does_not_wrap_or_call_gp014",
    "inspection_surface_does_not_repair_gp015",
)

DOWNSTREAM_FALSE_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "live_runtime_behavior",
    "runtime_authority",
    "runtime_interpretation",
    "api_availability_as_acceptance",
    "ui_visibility_as_proof",
    "state_modification",
    "accepted_scope_widening",
    "acceptance_creation",
    "candidate_promotion",
    "selected_meaning_finalization",
    "truth_decision",
    "permission_grant",
    "action_authorization",
    "tool_routing",
    "tool_invocation",
    "delivery_authority",
    "transport_authority",
    "output_approval",
    "renderer_authority",
    "memory_write",
    "memory_authority",
    "evidence_validation",
    "corpus_authority",
    "external_resource_admission",
    "resource_fetch",
    "resource_download",
    "resource_ingestion",
    "resource_parsing",
    "resource_indexing",
    "network_io",
    "shell_execution",
    "code_execution",
    "model_authority",
    "vector_authority",
    "retrieval_authority",
    "similarity_authority",
    "embedding_index_creation",
    "rag_execution",
    "training_authority",
    "gp014_modification",
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
    "slice18_gp014_preservation_decision_boundary",
    "slice19_rmc_echo_boundary",
    "slice20_delivery_action_tool_routing_boundary",
)


@dataclass(frozen=True, slots=True)
class InspectionSubject:
    """A visible inspection category that grants no authority."""

    key: str
    display_label: str
    visible: bool
    reference_only: bool
    authority_role: str
    mutation_allowed: bool
    acceptance_effect: bool
    runtime_effect: bool
    proof_effect: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class NegativeAuthorityFlag:
    """A false-only downstream authority flag."""

    key: str
    value: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InspectionSurfaceRecord:
    """Canonical Slice 21 inspection-surface boundary record."""

    slice_id: str
    title: str
    schema_version: str
    scaffold_version: str
    integration_state: str
    runtime_effect: str
    dependency_change: str
    inspection_subjects: tuple[InspectionSubject, ...]
    boundary_laws: tuple[str, ...]
    prior_boundaries: tuple[str, ...]
    negative_authority_flags: tuple[NegativeAuthorityFlag, ...]
    inspection_is_read_only: bool
    route_registration_authorized: bool
    ui_integration_authorized: bool
    config_mutation_authorized: bool
    live_api_authorized: bool
    subject_count: int
    law_count: int
    negative_authority_flag_count: int

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
    if hasattr(value, "to_dict"):
        return _canonicalize(value.to_dict())
    return str(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    """Return deterministic JSON for receipts and stable IDs."""

    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    """Return a SHA-256 digest for UTF-8 text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_record_id(prefix: str, *parts: Any) -> str:
    """Build a deterministic short ID without reading or writing external state."""

    body = {"prefix": prefix, "parts": [_canonicalize(part) for part in parts]}
    return f"{prefix}:{sha256_text(canonical_json(body))[:16]}"


def build_inspection_subjects() -> tuple[InspectionSubject, ...]:
    labels = {
        "meaning_records": "Meaning records",
        "law_traces": "Law traces",
        "concept_boundaries": "Concept boundaries",
        "predicate_frames": "Predicate frames",
        "gate_records": "Gate records",
        "receipts": "Receipts",
        "accepted_scope_status": "Accepted-scope status",
    }
    return tuple(
        InspectionSubject(
            key=key,
            display_label=labels[key],
            visible=True,
            reference_only=True,
            authority_role="inspection_visibility_only_not_runtime_authority",
            mutation_allowed=False,
            acceptance_effect=False,
            runtime_effect=False,
            proof_effect=False,
        )
        for key in ALLOWED_INSPECTION_SUBJECTS
    )


def build_negative_authority_flags() -> tuple[NegativeAuthorityFlag, ...]:
    return tuple(
        NegativeAuthorityFlag(
            key=field,
            value=False,
            reason="slice21_read_only_inspection_surface_grants_no_downstream_authority",
        )
        for field in DOWNSTREAM_FALSE_ONLY_FIELDS
    )


def build_inspection_surface_record() -> InspectionSurfaceRecord:
    subjects = build_inspection_subjects()
    flags = build_negative_authority_flags()
    return InspectionSurfaceRecord(
        slice_id=SLICE_ID,
        title=SLICE_TITLE,
        schema_version=SCHEMA_VERSION,
        scaffold_version=SCAFFOLD_VERSION,
        integration_state=INTEGRATION_STATE,
        runtime_effect=RUNTIME_EFFECT,
        dependency_change=DEPENDENCY_CHANGE,
        inspection_subjects=subjects,
        boundary_laws=REQUIRED_BOUNDARY_LAWS,
        prior_boundaries=REQUIRED_PRIOR_BOUNDARIES,
        negative_authority_flags=flags,
        inspection_is_read_only=True,
        route_registration_authorized=False,
        ui_integration_authorized=False,
        config_mutation_authorized=False,
        live_api_authorized=False,
        subject_count=len(subjects),
        law_count=len(REQUIRED_BOUNDARY_LAWS),
        negative_authority_flag_count=len(flags),
    )


def get_inspection_surface_record() -> Mapping[str, object]:
    return build_inspection_surface_record().to_dict()


def get_allowed_inspection_subjects() -> tuple[str, ...]:
    return ALLOWED_INSPECTION_SUBJECTS


def get_required_boundary_laws() -> tuple[str, ...]:
    return REQUIRED_BOUNDARY_LAWS


def get_downstream_false_only_fields() -> tuple[str, ...]:
    return DOWNSTREAM_FALSE_ONLY_FIELDS
