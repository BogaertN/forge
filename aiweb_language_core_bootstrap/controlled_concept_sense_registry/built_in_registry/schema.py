"""Immutable Slice 37C minimal built-in concept-registry records.

The records in this package describe a closed, read-only registry of four
explicitly admitted architecture concepts.  They do not map surface language,
select a sense, construct CandidateMeaning, populate semantic classes or
relations, consume structural candidates, access memory, register routes,
invoke tools, render output, authorize delivery, or execute actions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ...schema import stable_record_id
from ..schema import ConceptNamespaceIdentity, ControlledConceptIdentity
from ..governed_lifecycle.schema import ConceptGovernanceBatch


SLICE37C_SPEC_ID: Final[str] = (
    "aiweb-slice37c-minimal-built-in-concept-registry"
)
SLICE37C_SPEC_VERSION: Final[str] = (
    "aiweb-slice37c-minimal-built-in-concept-registry-v1"
)
SLICE37C_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-minimal-built-in-concept-registry-schema-v1"
)
SLICE37C_ACCEPTED_PARENT_HEAD: Final[str] = (
    "f4cfdd0e3f20c5ff3d72ed335b6ddd155b0f36fd"
)
SLICE37C_ACCEPTED_PARENT_TREE: Final[str] = (
    "8150ddcd4264f564e83f1f8db5420a3f77d67856"
)
SLICE37C_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 37B deterministic validation identity and lifecycle law"
)
SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256: Final[str] = (
    "5933294e9de406d6c4dd37ec69c59af9ac8596f67bb8542a60f6a3fada994963"
)
SLICE37C_EXPECTED_CONCEPT_COUNT: Final[int] = 4
SLICE37C_EXPECTED_NAMESPACE_COUNT: Final[int] = 1


class BuiltInRegistryValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    MANIFEST_BOUNDARY_MISMATCH = "manifest_boundary_mismatch"
    GOVERNANCE_BATCH_INVALID = "governance_batch_invalid"
    REGISTRY_COUNT_MISMATCH = "registry_count_mismatch"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    REGISTRY_NOT_READ_ONLY = "registry_not_read_only"
    DUPLICATE_CONCEPT_ID = "duplicate_concept_id"
    DUPLICATE_CONCEPT_KEY = "duplicate_concept_key"
    NAMESPACE_MISMATCH = "namespace_mismatch"
    LIFECYCLE_STATE_MISMATCH = "lifecycle_state_mismatch"
    HISTORY_MISSING = "history_missing"
    PROVENANCE_MISMATCH = "provenance_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    PERMITTED_USE_MISMATCH = "permitted_use_mismatch"
    PROHIBITED_USE_MISMATCH = "prohibited_use_mismatch"
    AUTHORITY_LIMIT_MISMATCH = "authority_limit_mismatch"
    DEFERRED_REFERENCE_MISMATCH = "deferred_reference_mismatch"
    SURFACE_LOOKUP_PROHIBITED = "surface_lookup_prohibited"
    OCCURRENCE_MAPPING_PROHIBITED = "occurrence_mapping_prohibited"
    SENSE_AUTHORITY_PROHIBITED = "sense_authority_prohibited"
    CLASS_RELATION_AUTHORITY_PROHIBITED = "class_relation_authority_prohibited"
    STRUCTURAL_INTEGRATION_PROHIBITED = "structural_integration_prohibited"
    RUNTIME_AUTHORITY_PROHIBITED = "runtime_authority_prohibited"
    EXTERNAL_RESOURCE_PROHIBITED = "external_resource_prohibited"
    HISTORICAL_BOUNDARY_MISMATCH = "historical_boundary_mismatch"


@dataclass(frozen=True, slots=True)
class BuiltInRegistryValidationIssue:
    path: str
    code: BuiltInRegistryValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class BuiltInRegistryValidationReport:
    ok: bool
    issues: tuple[BuiltInRegistryValidationIssue, ...]
    schema_version: str = SLICE37C_SCHEMA_VERSION


class BuiltInRegistryValidationError(ValueError):
    """Raised when the Slice 37C registry fails closed."""

    def __init__(self, report: BuiltInRegistryValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            detail or "Slice 37C built-in registry validation failed"
        )


@dataclass(frozen=True, slots=True)
class BuiltInConceptRegistryManifest:
    manifest_id: str
    registry_key: str
    namespace_ref: str
    concept_refs: tuple[str, ...]
    concept_lineage_refs: tuple[str, ...]
    concept_keys: tuple[str, ...]
    source_authority_packet_sha256: str
    decision_owner_ref: str
    human_approval_ref: str
    human_approved: bool
    registry_population_authorized: bool
    read_only: bool
    closed_set: bool
    authority_limitations: tuple[str, ...]
    exact_identity_lookup_allowed: bool
    exact_internal_key_lookup_allowed: bool
    surface_form_lookup_allowed: bool
    lexical_reference_population_installed: bool
    term_mapping_installed: bool
    occurrence_interpretation_installed: bool
    sense_population_installed: bool
    sense_selection_installed: bool
    semantic_class_population_installed: bool
    semantic_relation_population_installed: bool
    structural_integration_installed: bool
    candidate_meaning_creation_installed: bool
    runtime_activation_installed: bool
    route_registration_installed: bool
    tool_activation_installed: bool
    memory_access_installed: bool
    action_execution_installed: bool
    rendering_installed: bool
    delivery_installed: bool
    external_resource_loading_installed: bool
    llm_authority_installed: bool
    semantic_class_references_deferred_to_slice37e: bool
    sense_references_deferred_to_slice37d: bool
    relation_references_deferred_to_slice37e: bool
    historical_slice8_preserved: bool
    historical_slice8_superseded: bool
    schema_version: str = SLICE37C_SCHEMA_VERSION
    spec_id: str = SLICE37C_SPEC_ID
    spec_version: str = SLICE37C_SPEC_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("manifest_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37c_built_in_concept_registry_manifest",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BuiltInConceptRegistry:
    manifest: BuiltInConceptRegistryManifest
    governance_batch: ConceptGovernanceBatch
    current_namespace: ConceptNamespaceIdentity
    admitted_concepts: tuple[ControlledConceptIdentity, ...]

    def canonical_body(self) -> dict[str, object]:
        return {
            "manifest_id": self.manifest.manifest_id,
            "governance_batch_id": self.governance_batch.batch_id,
            "current_namespace_id": self.current_namespace.namespace_id,
            "admitted_concept_ids": tuple(
                concept.concept_id
                for concept in self.admitted_concepts
            ),
        }

    def registry_digest(self) -> str:
        return stable_record_id(
            "slice37c_built_in_concept_registry",
            self.canonical_body(),
        )
