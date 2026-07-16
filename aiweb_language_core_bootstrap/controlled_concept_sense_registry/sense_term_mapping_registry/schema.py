"""Immutable Slice 37D controlled-sense and exact term-mapping records.

This package provides a closed, read-only, deterministic registry over the four
Slice 37C concepts. It may expose exact lexical references and zero, one, or
multiple concept/sense candidates. It never interprets a source occurrence,
selects a sense, ranks candidates, expands a term, consumes Slice 36 output,
constructs CandidateMeaning, renders language, authorizes delivery, or performs
runtime action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ...schema import stable_record_id
from ..governed_lifecycle.schema import ConceptGovernanceBatch
from ..schema import (
    ControlledLexicalReference,
    ControlledSenseIdentity,
    TermConceptMappingIdentity,
)
from ..built_in_registry.schema import BuiltInConceptRegistry


SLICE37D_SPEC_ID: Final[str] = (
    "aiweb-slice37d-controlled-sense-exact-term-mapping-registry"
)
SLICE37D_SPEC_VERSION: Final[str] = (
    "aiweb-slice37d-controlled-sense-exact-term-mapping-registry-v1"
)
SLICE37D_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-controlled-sense-exact-term-mapping-registry-schema-v1"
)
SLICE37D_ACCEPTED_PARENT_HEAD: Final[str] = (
    "02c36cbaa99a9dfaef5b0753169b3ff692a68bea"
)
SLICE37D_ACCEPTED_PARENT_TREE: Final[str] = (
    "6943984372930849fcdca3d999c525b0afe0bae3"
)
SLICE37D_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 37C minimal built-in concept registry"
)
SLICE37D_SOURCE_AUTHORITY_PACKET_SHA256: Final[str] = (
    "e0da6836a590675552b49f4859019c899292ac5c174f43d4ffd9ca1b2d0a482c"
)

SLICE37D_EXPECTED_SENSE_COUNT: Final[int] = 5
SLICE37D_EXPECTED_LEXICAL_REFERENCE_COUNT: Final[int] = 11
SLICE37D_EXPECTED_MAPPING_COUNT: Final[int] = 10
SLICE37D_EXPECTED_OUTWARD_ELIGIBILITY_COUNT: Final[int] = 4


class MappingMultiplicity(str, Enum):
    ZERO = "zero"
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"


class ExactTermLookupState(str, Enum):
    NO_EXACT_LEXICAL_REFERENCE = "no_exact_lexical_reference"
    UNMAPPED_TERM = "unmapped_term"
    MAPPED_ONE_TO_ONE = "mapped_one_to_one"
    MAPPED_ONE_TO_MANY = "mapped_one_to_many"
    AMBIGUOUS_MAPPING = "ambiguous_mapping"
    UNSUPPORTED_MAPPING = "unsupported_mapping"


class ProhibitedExpansionKind(str, Enum):
    CASE_FOLD = "case_fold"
    SPELLING_CORRECTION = "spelling_correction"
    STEMMING = "stemming"
    SYNONYM_EXPANSION = "synonym_expansion"
    NEAREST_MATCH = "nearest_match"
    FREQUENCY_RANKING = "frequency_ranking"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    EMBEDDING = "embedding"
    MODEL_INFERENCE = "model_inference"
    ORDINARY_DICTIONARY_FALLBACK = "ordinary_dictionary_fallback"


class OutwardExpressionEligibilityState(str, Enum):
    ELIGIBLE_REFERENCE_ONLY = "eligible_reference_only"
    INELIGIBLE = "ineligible"


class SenseTermMappingValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_LANGUAGE_TAG = "invalid_language_tag"
    INVALID_SCOPE = "invalid_scope"
    DUPLICATE_VALUE = "duplicate_value"
    REFERENCE_NOT_FOUND = "reference_not_found"
    REFERENCE_KIND_MISMATCH = "reference_kind_mismatch"
    REGISTRY_COUNT_MISMATCH = "registry_count_mismatch"
    REGISTRY_NOT_CLOSED = "registry_not_closed"
    REGISTRY_NOT_READ_ONLY = "registry_not_read_only"
    GOVERNANCE_BATCH_INVALID = "governance_batch_invalid"
    CONCEPT_REGISTRY_MISMATCH = "concept_registry_mismatch"
    MAPPING_MULTIPLICITY_MISMATCH = "mapping_multiplicity_mismatch"
    MAPPING_STATE_MISMATCH = "mapping_state_mismatch"
    CANDIDATE_ORDER_MISMATCH = "candidate_order_mismatch"
    OUTWARD_ELIGIBILITY_MISMATCH = "outward_eligibility_mismatch"
    OCCURRENCE_SELECTION_PROHIBITED = "occurrence_selection_prohibited"
    EXPANSION_AUTHORITY_PROHIBITED = "expansion_authority_prohibited"
    RUNTIME_AUTHORITY_PROHIBITED = "runtime_authority_prohibited"
    EXTERNAL_RESOURCE_PROHIBITED = "external_resource_prohibited"


@dataclass(frozen=True, slots=True)
class SenseTermMappingValidationIssue:
    path: str
    code: SenseTermMappingValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class SenseTermMappingValidationReport:
    ok: bool
    issues: tuple[SenseTermMappingValidationIssue, ...]
    schema_version: str = SLICE37D_SCHEMA_VERSION


class SenseTermMappingValidationError(ValueError):
    """Raised when the Slice 37D registry fails closed."""

    def __init__(self, report: SenseTermMappingValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(
            detail or "Slice 37D sense and term-mapping validation failed"
        )


@dataclass(frozen=True, slots=True)
class OutwardExpressionEligibilityReference:
    eligibility_id: str
    lexical_reference_id: str
    concept_ref: str
    sense_ref: str
    eligibility_state: OutwardExpressionEligibilityState
    reason: str
    version: str
    provenance_ref: str
    rendering_authorized: bool
    delivery_authorized: bool
    runtime_authorized: bool
    prohibited_authorities: tuple[str, ...]
    schema_version: str = SLICE37D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("eligibility_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37d_outward_expression_eligibility",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MappingExpansionRefusal:
    refusal_id: str
    expansion_kind: ProhibitedExpansionKind
    allowed: bool
    reason: str
    prohibited_authorities: tuple[str, ...]
    schema_version: str = SLICE37D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("refusal_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37d_mapping_expansion_refusal",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExactTermLookupRequest:
    request_id: str
    exact_form: str
    language_tag: str
    namespace_id: str
    namespace_scope: tuple[str, ...]
    domain_scope: tuple[str, ...]
    schema_version: str = SLICE37D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("request_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37d_exact_term_lookup_request",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExactTermLookupResult:
    result_id: str
    request_ref: str
    state: ExactTermLookupState
    multiplicity: MappingMultiplicity
    lexical_reference_refs: tuple[str, ...]
    mapping_refs: tuple[str, ...]
    concept_candidate_refs: tuple[str, ...]
    sense_candidate_refs: tuple[str, ...]
    outward_eligibility_refs: tuple[str, ...]
    exact_match: bool
    candidate_order_is_ranked: bool
    occurrence_interpretation_selected: bool
    selected_concept_ref: str | None
    selected_sense_ref: str | None
    reason: str
    prohibited_authorities: tuple[str, ...]
    schema_version: str = SLICE37D_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37d_exact_term_lookup_result",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SenseTermMappingRegistryManifest:
    manifest_id: str
    registry_key: str
    source_authority_packet_sha256: str
    decision_owner_ref: str
    human_approval_ref: str
    human_approved: bool
    read_only: bool
    closed_set: bool
    authority_limitations: tuple[str, ...]
    sense_refs: tuple[str, ...]
    lexical_reference_refs: tuple[str, ...]
    mapping_refs: tuple[str, ...]
    outward_eligibility_refs: tuple[str, ...]
    prohibited_expansion_refusal_refs: tuple[str, ...]
    exact_term_lookup_allowed: bool
    exact_reference_id_lookup_allowed: bool
    exact_sense_id_lookup_allowed: bool
    exact_mapping_id_lookup_allowed: bool
    registry_population_authorized: bool
    sense_population_authorized: bool
    lexical_reference_population_authorized: bool
    mapping_population_authorized: bool
    outward_eligibility_reference_population_authorized: bool
    occurrence_interpretation_installed: bool
    sense_selection_installed: bool
    candidate_meaning_creation_installed: bool
    structural_integration_installed: bool
    case_fold_expansion_installed: bool
    spelling_correction_installed: bool
    stemming_installed: bool
    synonym_expansion_installed: bool
    nearest_match_installed: bool
    frequency_ranking_installed: bool
    semantic_similarity_installed: bool
    embedding_installed: bool
    model_inference_installed: bool
    ordinary_dictionary_fallback_installed: bool
    external_resource_loading_installed: bool
    runtime_activation_installed: bool
    route_registration_installed: bool
    tool_activation_installed: bool
    memory_access_installed: bool
    action_execution_installed: bool
    rendering_installed: bool
    delivery_installed: bool
    semantic_classes_deferred_to_slice37e: bool
    semantic_relations_deferred_to_slice37e: bool
    structural_candidate_integration_deferred_to_slice37f: bool
    schema_version: str = SLICE37D_SCHEMA_VERSION
    spec_id: str = SLICE37D_SPEC_ID
    spec_version: str = SLICE37D_SPEC_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("manifest_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37d_sense_term_mapping_registry_manifest",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SenseTermMappingRegistry:
    manifest: SenseTermMappingRegistryManifest
    concept_registry: BuiltInConceptRegistry
    governance_batch: ConceptGovernanceBatch
    senses: tuple[ControlledSenseIdentity, ...]
    lexical_references: tuple[ControlledLexicalReference, ...]
    mappings: tuple[TermConceptMappingIdentity, ...]
    outward_eligibility_references: tuple[
        OutwardExpressionEligibilityReference, ...
    ]
    prohibited_expansion_refusals: tuple[MappingExpansionRefusal, ...]

    def canonical_body(self) -> dict[str, object]:
        return {
            "manifest_id": self.manifest.manifest_id,
            "concept_registry_digest": self.concept_registry.registry_digest(),
            "governance_batch_id": self.governance_batch.batch_id,
            "sense_ids": tuple(item.sense_id for item in self.senses),
            "lexical_reference_ids": tuple(
                item.lexical_reference_id
                for item in self.lexical_references
            ),
            "mapping_ids": tuple(item.mapping_id for item in self.mappings),
            "outward_eligibility_ids": tuple(
                item.eligibility_id
                for item in self.outward_eligibility_references
            ),
            "prohibited_expansion_refusal_ids": tuple(
                item.refusal_id
                for item in self.prohibited_expansion_refusals
            ),
        }

    def registry_digest(self) -> str:
        return stable_record_id(
            "slice37d_sense_term_mapping_registry",
            self.canonical_body(),
        )
