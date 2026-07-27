"""Immutable records for the token-free RSOC reference preview.

The records in this module describe exact source observations only.  They do
not bind operands, compose operators, apply an operator, assign a phase,
create meaning, infer permission, or grant memory, route, tool, action, or
delivery authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id

REFERENCE_PREVIEW_SPEC_ID: Final[str] = (
    "aiweb-rsoc-symbolic-reference-preview"
)
REFERENCE_PREVIEW_SPEC_VERSION: Final[str] = (
    "aiweb-rsoc-symbolic-reference-preview-v1"
)
REFERENCE_PREVIEW_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-rsoc-reference-preview-v1"
)
REFERENCE_RECOGNITION_RULESET_ID: Final[str] = (
    "aiweb-rsoc-exact-registry-glyph-recognition-v1"
)

DEFAULT_MAX_OPERATOR_REFERENCES: Final[int] = 256
DEFAULT_MAX_COVERAGE_SEGMENTS: Final[int] = 512
ABSOLUTE_MAX_OPERATOR_REFERENCES: Final[int] = 4_096
ABSOLUTE_MAX_COVERAGE_SEGMENTS: Final[int] = 4_096


class RsocReferencePreviewStatus(str, Enum):
    REFERENCE_PREVIEW_READY = "REFERENCE_PREVIEW_READY"
    HELD_INVALID_CUSTODY = "HELD_INVALID_CUSTODY"
    HELD_UNSUPPORTED_SOURCE = "HELD_UNSUPPORTED_SOURCE"
    HELD_INVALID_PROJECTION = "HELD_INVALID_PROJECTION"
    HELD_INVALID_REGISTRY = "HELD_INVALID_REGISTRY"
    HELD_INVALID_LIMITS = "HELD_INVALID_LIMITS"
    HELD_NO_OPERATOR_REFERENCE = "HELD_NO_OPERATOR_REFERENCE"
    HELD_UNCONSUMED_SOURCE = "HELD_UNCONSUMED_SOURCE"
    HELD_PREVIEW_LIMIT_EXCEEDED = "HELD_PREVIEW_LIMIT_EXCEEDED"


class SourceCoverageKind(str, Enum):
    OPERATOR_REFERENCE = "operator_reference"
    ASCII_SEPARATOR = "ascii_separator"
    UNRECOGNIZED = "unrecognized"
    LIMIT_REMAINDER = "limit_remainder"


@dataclass(frozen=True, slots=True)
class RsocReferencePreviewLimits:
    limits_id: str
    max_operator_references: int
    max_coverage_segments: int
    spec_id: str = REFERENCE_PREVIEW_SPEC_ID
    spec_version: str = REFERENCE_PREVIEW_SPEC_VERSION
    schema_version: str = REFERENCE_PREVIEW_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("limits_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_reference_preview_limits", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceCoverageSegment:
    segment_id: str
    ordinal: int
    kind: SourceCoverageKind
    exact_text: str
    utf8_hex: str
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    source_span_id: str
    atom_ids: tuple[str, ...]
    operator_contract_id: str
    issue_code: str
    ruleset_id: str = REFERENCE_RECOGNITION_RULESET_ID
    spec_id: str = REFERENCE_PREVIEW_SPEC_ID
    spec_version: str = REFERENCE_PREVIEW_SPEC_VERSION
    schema_version: str = REFERENCE_PREVIEW_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("segment_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_source_coverage_segment", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocOperatorReferenceNode:
    reference_id: str
    ordinal: int
    operator_key: str
    glyph: str
    canonical_name: str
    declared_arity: str
    registry_id: str
    operator_contract_id: str
    runtime_status: str
    coverage_segment_id: str
    source_span_id: str
    atom_ids: tuple[str, ...]
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    exact_glyph_recognition_performed: bool
    registry_reference_only: bool
    source_binding_performed: bool
    operator_application_performed: bool
    numeric_transform_performed: bool
    entropy_mutation_performed: bool
    phase_assignment_performed: bool
    meaning_created: bool
    permission_inferred: bool
    ruleset_id: str = REFERENCE_RECOGNITION_RULESET_ID
    spec_id: str = REFERENCE_PREVIEW_SPEC_ID
    spec_version: str = REFERENCE_PREVIEW_SPEC_VERSION
    schema_version: str = REFERENCE_PREVIEW_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("reference_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_operator_reference", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocReferenceDocument:
    document_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    registry_id: str
    coverage_segment_ids: tuple[str, ...]
    operator_reference_ids: tuple[str, ...]
    operator_reference_count: int
    separator_segment_count: int
    full_source_coverage: bool
    full_input_consumed: bool
    exact_reconstruction_proven: bool
    registry_reference_sequence_created: bool
    composition_interpreted: bool
    arguments_bound: bool
    source_binding_performed: bool
    operator_application_performed: bool
    successor_field_created: bool
    phase_assigned: bool
    meaning_created: bool
    ruleset_id: str = REFERENCE_RECOGNITION_RULESET_ID
    spec_id: str = REFERENCE_PREVIEW_SPEC_ID
    spec_version: str = REFERENCE_PREVIEW_SPEC_VERSION
    schema_version: str = REFERENCE_PREVIEW_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("document_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_reference_document", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocReferenceBoundary:
    read_only: bool
    registry_reference_only: bool
    exact_glyph_recognition_performed: bool
    natural_language_tokenization_performed: bool
    word_tokenization_performed: bool
    subword_tokenization_performed: bool
    normalization_performed: bool
    casefolding_performed: bool
    vocabulary_lookup_performed: bool
    concept_lookup_performed: bool
    predicate_binding_performed: bool
    reference_resolution_performed: bool
    authoritative_expression_grammar_installed: bool
    source_binding_performed: bool
    operator_occurrence_created: bool
    operator_application_performed: bool
    numeric_transform_performed: bool
    entropy_mutation_performed: bool
    successor_field_created: bool
    phase_assignment_performed: bool
    meaning_created: bool
    permission_inferred: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    identity_vault_write_performed: bool
    route_registration_performed: bool
    model_call_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocReferencePreviewResult:
    result_id: str
    status: RsocReferencePreviewStatus
    reason_code: str
    ready: bool
    source_event_id: str
    source_sha256: str
    projection_id: str
    registry_id: str
    unicode_database_version: str
    limits: RsocReferencePreviewLimits | None
    coverage: tuple[SourceCoverageSegment, ...]
    operator_references: tuple[RsocOperatorReferenceNode, ...]
    document: RsocReferenceDocument | None
    recognized_operator_count: int
    separator_segment_count: int
    unrecognized_segment_count: int
    unresolved_code_point_count: int
    scan_complete: bool
    full_source_coverage: bool
    exact_reconstruction_proven: bool
    validation_issue_codes: tuple[str, ...]
    boundary: RsocReferenceBoundary
    ruleset_id: str = REFERENCE_RECOGNITION_RULESET_ID
    spec_id: str = REFERENCE_PREVIEW_SPEC_ID
    spec_version: str = REFERENCE_PREVIEW_SPEC_VERSION
    schema_version: str = REFERENCE_PREVIEW_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_reference_preview_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
