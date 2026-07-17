"""Immutable Slice 38C minimal built-in action-root registry records.

The records define a closed read-only registry of five explicitly admitted
Forge-owned action roots and their one-to-one predicate identities.  They do
not map surface text, select an occurrence, infer intent, assign participant
roles, complete frames, bind capabilities, invoke routes, execute actions,
validate evidence, access memory, render output, deliver messages, or release
software.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ...schema import stable_record_id
from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateNamespaceIdentity,
)
from ..governed_lifecycle.schema import PredicateGovernanceBatch


SLICE38C_SPEC_ID: Final[str] = (
    "aiweb-slice38c-minimal-built-in-action-root-registry"
)
SLICE38C_SPEC_VERSION: Final[str] = (
    "aiweb-slice38c-minimal-built-in-action-root-registry-v1"
)
SLICE38C_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-minimal-built-in-action-root-registry-schema-v1"
)
SLICE38C_ACCEPTED_PARENT_HEAD: Final[str] = (
    "c502b74ada70ed0bc551fb591c49fd119191f52f"
)
SLICE38C_ACCEPTED_PARENT_TREE: Final[str] = (
    "77d349f51a617eab98d1fddeef7ba9e57f52dec6"
)
SLICE38C_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 38B deterministic validation identity versioning lifecycle"
)
SLICE38C_SOURCE_AUTHORITY_PACKET_SHA256: Final[str] = (
    "1e9d44dfbe256f2438baa24357b65741462b294b0ef120021a0cd73e8a59ee3e"
)
SLICE38C_EXPECTED_NAMESPACE_COUNT: Final[int] = 1
SLICE38C_EXPECTED_ACTION_ROOT_COUNT: Final[int] = 5
SLICE38C_EXPECTED_PREDICATE_COUNT: Final[int] = 5


class BuiltInActionRootRegistryValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    MANIFEST_BOUNDARY_MISMATCH = "manifest_boundary_mismatch"
    GOVERNANCE_BATCH_INVALID = "governance_batch_invalid"
    REGISTRY_COUNT_MISMATCH = "registry_count_mismatch"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    REGISTRY_NOT_READ_ONLY = "registry_not_read_only"
    DUPLICATE_ACTION_ROOT_ID = "duplicate_action_root_id"
    DUPLICATE_ACTION_ROOT_KEY = "duplicate_action_root_key"
    DUPLICATE_PREDICATE_ID = "duplicate_predicate_id"
    DUPLICATE_PREDICATE_KEY = "duplicate_predicate_key"
    NAMESPACE_MISMATCH = "namespace_mismatch"
    ACTION_ROOT_LINK_MISMATCH = "action_root_link_mismatch"
    LIFECYCLE_STATE_MISMATCH = "lifecycle_state_mismatch"
    HISTORY_MISSING = "history_missing"
    PROVENANCE_MISMATCH = "provenance_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    NON_SCOPE_MISMATCH = "non_scope_mismatch"
    PERMITTED_USE_MISMATCH = "permitted_use_mismatch"
    PROHIBITED_USE_MISMATCH = "prohibited_use_mismatch"
    AUTHORITY_LIMIT_MISMATCH = "authority_limit_mismatch"
    DEFERRED_REFERENCE_MISMATCH = "deferred_reference_mismatch"
    SURFACE_LOOKUP_PROHIBITED = "surface_lookup_prohibited"
    OCCURRENCE_SELECTION_PROHIBITED = "occurrence_selection_prohibited"
    NEAREST_MAPPING_PROHIBITED = "nearest_mapping_prohibited"
    SIMILARITY_AUTHORITY_PROHIBITED = "similarity_authority_prohibited"
    ROLE_FRAME_AUTHORITY_PROHIBITED = "role_frame_authority_prohibited"
    CAPABILITY_AUTHORITY_PROHIBITED = "capability_authority_prohibited"
    EVIDENCE_AUTHORITY_PROHIBITED = "evidence_authority_prohibited"
    MEMORY_AUTHORITY_PROHIBITED = "memory_authority_prohibited"
    RUNTIME_AUTHORITY_PROHIBITED = "runtime_authority_prohibited"
    EXTERNAL_RESOURCE_PROHIBITED = "external_resource_prohibited"
    LLM_AUTHORITY_PROHIBITED = "llm_authority_prohibited"
    PREDECESSOR_BOUNDARY_MISMATCH = "predecessor_boundary_mismatch"


@dataclass(frozen=True, slots=True)
class BuiltInActionRootRegistryValidationIssue:
    path: str
    code: BuiltInActionRootRegistryValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class BuiltInActionRootRegistryValidationReport:
    ok: bool
    issues: tuple[BuiltInActionRootRegistryValidationIssue, ...]
    schema_version: str = SLICE38C_SCHEMA_VERSION


class BuiltInActionRootRegistryValidationError(ValueError):
    """Raised when the Slice 38C registry fails closed."""

    def __init__(
        self,
        report: BuiltInActionRootRegistryValidationReport,
    ) -> None:
        self.report = report
        detail = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            detail or "Slice 38C built-in action-root registry validation failed"
        )


@dataclass(frozen=True, slots=True)
class BuiltInActionRootRegistryManifest:
    manifest_id: str
    registry_key: str
    namespace_ref: str
    action_root_refs: tuple[str, ...]
    action_root_lineage_refs: tuple[str, ...]
    action_root_keys: tuple[str, ...]
    predicate_refs: tuple[str, ...]
    predicate_lineage_refs: tuple[str, ...]
    predicate_keys: tuple[str, ...]
    source_authority_packet_sha256: str
    decision_owner_ref: str
    human_approval_ref: str
    human_approved: bool
    registry_population_authorized: bool
    read_only: bool
    closed_set: bool
    authority_limitations: tuple[str, ...]
    deferred_higher_consequence_families: tuple[str, ...]
    exact_identity_lookup_allowed: bool
    exact_internal_key_lookup_allowed: bool
    exact_action_root_to_predicate_link_allowed: bool
    surface_form_lookup_allowed: bool
    surface_normalization_allowed: bool
    occurrence_interpretation_installed: bool
    predicate_selection_installed: bool
    nearest_known_mapping_installed: bool
    semantic_similarity_installed: bool
    concept_to_predicate_conversion_installed: bool
    participant_role_population_installed: bool
    role_assignment_installed: bool
    predicate_frame_population_installed: bool
    frame_completion_installed: bool
    effect_boundary_population_installed: bool
    capability_reference_population_installed: bool
    capability_routing_installed: bool
    route_registration_installed: bool
    tool_activation_installed: bool
    action_execution_installed: bool
    evidence_validation_installed: bool
    memory_access_installed: bool
    rendering_installed: bool
    delivery_installed: bool
    external_resource_loading_installed: bool
    llm_authority_installed: bool
    participant_roles_deferred_to_slice38d: bool
    predicate_frames_deferred_to_slice38e: bool
    effect_and_capability_references_deferred_to_slice38f: bool
    occurrence_candidate_proposal_deferred_to_slice38g: bool
    disabled_integration_deferred_to_slice38h: bool
    slice38a_preserved: bool
    slice38b_preserved: bool
    slice38a_superseded: bool
    slice38b_superseded: bool
    schema_version: str = SLICE38C_SCHEMA_VERSION
    spec_id: str = SLICE38C_SPEC_ID
    spec_version: str = SLICE38C_SPEC_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("manifest_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice38c_built_in_action_root_registry_manifest",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BuiltInActionRootRegistry:
    manifest: BuiltInActionRootRegistryManifest
    governance_batch: PredicateGovernanceBatch
    current_namespace: PredicateNamespaceIdentity
    admitted_action_roots: tuple[ActionRootIdentity, ...]
    admitted_predicates: tuple[PredicateIdentity, ...]

    def canonical_body(self) -> dict[str, object]:
        return {
            "manifest_id": self.manifest.manifest_id,
            "governance_batch_id": self.governance_batch.batch_id,
            "current_namespace_id": self.current_namespace.namespace_id,
            "admitted_action_root_ids": tuple(
                record.action_root_id for record in self.admitted_action_roots
            ),
            "admitted_predicate_ids": tuple(
                record.predicate_id for record in self.admitted_predicates
            ),
        }

    def registry_digest(self) -> str:
        return stable_record_id(
            "slice38c_built_in_action_root_registry",
            self.canonical_body(),
        )
