"""Immutable records for the bounded Forge meaning-compiler preview.

The records in this module describe evidence and preview results only.  They
carry no route, model, memory, tool, action, delivery, or write authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import canonicalize, stable_record_id


MEANING_COMPILER_PREVIEW_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-meaning-compiler-preview-v0"
)


class PreviewStatus(str, Enum):
    PREVIEW_READY = "PREVIEW_READY"
    HELD = "HELD"
    UNSUPPORTED = "UNSUPPORTED"
    INVALID = "INVALID"


class SourceFormKind(str, Enum):
    WORD = "word"
    NUMBER = "number"
    WHITESPACE = "whitespace"
    PUNCTUATION = "punctuation"
    SYMBOL = "symbol"


class LexicalCandidateKind(str, Enum):
    CONCEPT_SENSE = "concept_sense"
    PREDICATE = "predicate"
    FUNCTION = "function"
    UNKNOWN = "unknown"


class EchoStatus(str, Enum):
    PASS = "PASS"
    REJECT = "REJECT"
    NOT_RUN = "NOT_RUN"


def _record_dict(value: object) -> dict[str, object]:
    return canonicalize(asdict(value))


@dataclass(frozen=True, slots=True)
class SourceCustodySummary:
    custody_result_id: str
    input_event_id: str
    custody_status: str
    reason_code: str
    source_sha256: str
    code_point_length: int | None
    utf8_byte_length: int | None
    source_preserved_exactly: bool
    structural_progression_allowed: bool
    normalization_performed: bool
    tokenization_performed: bool
    model_token_stream_created: bool
    subword_token_stream_created: bool
    numeric_token_ids_created: bool
    conditions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class SourceForm:
    source_form_id: str
    source_span_id: str
    input_event_id: str
    kind: SourceFormKind
    exact_text: str
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    source_sha256: str

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ProvisionalConcept:
    concept_id: str
    concept_key: str
    preferred_label: str
    semantic_class: str
    provisional_definition: str
    registry_owner: str
    registry_version: str
    provisional: bool
    external_reference_authority: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ProvisionalSense:
    sense_id: str
    sense_key: str
    concept_ref: str
    exact_surface_forms: tuple[tuple[str, ...], ...]
    provisional_gloss: str
    registry_owner: str
    registry_version: str
    provisional: bool
    external_reference_authority: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class PredicateDefinition:
    predicate_id: str
    predicate_key: str
    preferred_label: str
    exact_surface_forms: tuple[str, ...]
    required_roles: tuple[str, ...]
    registry_owner: str
    registry_version: str
    provisional: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class RoleDefinition:
    role_id: str
    role_key: str
    description: str
    registry_owner: str
    registry_version: str
    provisional: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ForgeSeedRegistry:
    registry_id: str
    owner: str
    version: str
    concepts: tuple[ProvisionalConcept, ...]
    senses: tuple[ProvisionalSense, ...]
    predicates: tuple[PredicateDefinition, ...]
    roles: tuple[RoleDefinition, ...]
    external_reference_authority: bool
    imported_reference_definitions_used: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class LexicalCandidate:
    lexical_candidate_id: str
    kind: LexicalCandidateKind
    exact_text: str
    source_form_refs: tuple[str, ...]
    word_ordinals: tuple[int, ...]
    ambiguity_group: str
    concept_ref: str
    sense_ref: str
    predicate_ref: str
    function_key: str
    known: bool
    provisional: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class RoleBinding:
    binding_id: str
    role_key: str
    source_form_refs: tuple[str, ...]
    word_ordinals: tuple[int, ...]
    exact_text: str

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class FrameCandidate:
    frame_candidate_id: str
    frame_key: str
    speech_act: str
    purport: str
    predicate_ref: str
    predicate_key: str
    negated: bool
    role_bindings: tuple[RoleBinding, ...]
    grammar_rule_id: str
    complete: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class GateResult:
    gate_id: str
    gate_name: str
    passed: bool
    rule_id: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class MeaningRole:
    role_key: str
    concept_ref: str
    sense_ref: str
    source_form_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class MeaningCandidate:
    meaning_candidate_id: str
    semantic_signature: str
    frame_candidate_ref: str
    frame_key: str
    speech_act: str
    purport: str
    predicate_ref: str
    predicate_key: str
    negated: bool
    roles: tuple[MeaningRole, ...]
    relation_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    unknown_source_form_refs: tuple[str, ...]
    gates: tuple[GateResult, ...]
    all_gates_passed: bool
    provisional: bool
    preview_only: bool
    selection_authority: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class SemanticContractBinding:
    """Exact reusable meaning boundary, independent of source occurrence IDs.

    A semantic signature alone is not sufficient because the governed
    definition request/response pair deliberately shares one Echo signature.
    The complete contract therefore binds communicative force, purport,
    polarity, frame, grammar rule, and predicate as well.
    """

    semantic_contract_id: str
    semantic_signature_ref: str
    speech_act: str
    purport: str
    negated: bool
    frame_key: str
    grammar_rule_ref: str
    predicate_ref: str

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("semantic_contract_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "meaning_semantic_contract",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class AlgebraTraceStep:
    trace_step_id: str
    sequence: int
    operation: str
    rule_id: str
    operands: tuple[str, ...]
    outputs: tuple[str, ...]
    note: str

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class RmcContextRecord:
    record_id: str
    semantic_contract_refs: tuple[str, ...]
    concept_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    phase_refs: tuple[str, ...]
    correction_refs: tuple[str, ...]
    echo_receipt_refs: tuple[str, ...]
    lifecycle_state: str
    exact_reference_resonance_only: bool
    raw_text_present: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class RmcContextSnapshot:
    snapshot_id: str
    records: tuple[RmcContextRecord, ...]
    connection_status: str
    reason_code: str
    record_count: int
    read_only: bool
    caller_supplied: bool
    exact_reference_resonance_only: bool
    filesystem_access_performed: bool
    raw_word_overlap_used: bool
    embedding_used: bool
    vector_used: bool
    similarity_scoring_used: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class RmcCandidateResonance:
    resonance_id: str
    meaning_candidate_ref: str
    record_ref: str
    exact_semantic_contract_refs: tuple[str, ...]
    exact_concept_refs: tuple[str, ...]
    exact_relation_refs: tuple[str, ...]
    exact_ancestry_refs: tuple[str, ...]
    resonance_count: int
    used_for_selection: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class RmcContextEvaluation:
    evaluation_id: str
    snapshot: RmcContextSnapshot
    resonances: tuple[RmcCandidateResonance, ...]
    exact_reference_resonance_only: bool
    context_used_for_selection: bool
    memory_read_performed: bool
    memory_write_performed: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class CandidateWording:
    wording_id: str
    meaning_candidate_ref: str
    template_key: str
    text: str
    outward_semantic_signature: str
    definition_concept_ref: str
    definition_sense_ref: str
    provisional: bool
    delivery_authorized: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class EchoResult:
    echo_id: str
    status: EchoStatus
    reason_code: str
    meaning_candidate_ref: str
    candidate_wording_ref: str
    inward_semantic_signature: str
    reparsed_semantic_signature: str
    exact_signature_match: bool
    reparse_performed: bool
    delivery_authorized: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class StageResult:
    stage_id: str
    sequence: int
    stage_key: str
    status: str
    input_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class MeaningCompilerPreviewBoundary:
    boundary_id: str
    preview_version: str
    preview_only: bool
    forge_owned_provisional_registry: bool
    reference_only_materials: tuple[str, ...]
    external_reference_authority: bool
    glyph_reference_authority: bool
    google_drive_reference_authority: bool
    panini_reference_authority: bool
    chomsky_reference_authority: bool
    normalization_performed: bool
    tokenization_performed: bool
    model_token_stream_created: bool
    subword_token_stream_created: bool
    numeric_token_ids_created: bool
    model_called: bool
    embedding_used: bool
    vector_used: bool
    similarity_scoring_used: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class PreviewReceipt:
    receipt_id: str
    result_digest: str
    source_sha256: str
    status: PreviewStatus
    deterministic: bool
    preview_only: bool
    writes_performed: bool
    action_performed: bool
    delivery_performed: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class MeaningCompilerPreviewResult:
    result_id: str
    schema_version: str
    status: PreviewStatus
    source_text: str
    source_custody: SourceCustodySummary
    source_forms: tuple[SourceForm, ...]
    lexical_candidates: tuple[LexicalCandidate, ...]
    frame_candidates: tuple[FrameCandidate, ...]
    algebra_trace: tuple[AlgebraTraceStep, ...]
    meaning_candidates: tuple[MeaningCandidate, ...]
    selected_meaning: MeaningCandidate | None
    rmc_context: RmcContextEvaluation
    candidate_wording: CandidateWording | None
    echo: EchoResult
    stages: tuple[StageResult, ...]
    reasons: tuple[str, ...]
    boundary: MeaningCompilerPreviewBoundary
    receipt: PreviewReceipt

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


__all__ = (
    "AlgebraTraceStep",
    "CandidateWording",
    "EchoResult",
    "EchoStatus",
    "ForgeSeedRegistry",
    "FrameCandidate",
    "GateResult",
    "LexicalCandidate",
    "LexicalCandidateKind",
    "MEANING_COMPILER_PREVIEW_SCHEMA_VERSION",
    "MeaningCandidate",
    "MeaningCompilerPreviewBoundary",
    "MeaningCompilerPreviewResult",
    "MeaningRole",
    "PredicateDefinition",
    "PreviewReceipt",
    "PreviewStatus",
    "ProvisionalConcept",
    "ProvisionalSense",
    "RmcCandidateResonance",
    "RmcContextEvaluation",
    "RmcContextRecord",
    "RmcContextSnapshot",
    "RoleBinding",
    "RoleDefinition",
    "SemanticContractBinding",
    "SourceCustodySummary",
    "SourceForm",
    "SourceFormKind",
    "StageResult",
)
