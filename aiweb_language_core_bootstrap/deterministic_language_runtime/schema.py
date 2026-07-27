"""Immutable LC-RMC-001 source, grammar, and interpretation records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

from .authority import (
    PROFILE_ID,
    PROFILE_VERSION,
    RUNTIME_VERSION,
    SCHEMA_VERSION,
    runtime_authority_boundary,
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_id(prefix: str, value: Any, length: int = 24) -> str:
    digest = sha256_text(canonical_json(value))
    return f"{prefix}_{digest[:length]}"


@dataclass(frozen=True, slots=True)
class SourceSpan:
    start: int
    end: int
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TokenRecord:
    index: int
    kind: str
    source: str
    normalized: str
    span: SourceSpan
    ancestry_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "kind": self.kind,
            "source": self.source,
            "normalized": self.normalized,
            "span": self.span.to_dict(),
            "ancestry_id": self.ancestry_id,
        }


@dataclass(frozen=True, slots=True)
class MorphologyRecord:
    token_index: int
    lemma: str
    part_of_speech: str
    features: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "token_index": self.token_index,
            "lemma": self.lemma,
            "part_of_speech": self.part_of_speech,
            "features": list(self.features),
        }


@dataclass(frozen=True, slots=True)
class ObjectMeaning:
    source_text: str
    span: SourceSpan
    concept_keys: tuple[str, ...]
    determiners: tuple[str, ...]
    modifiers: tuple[str, ...]
    semantic_class_keys: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_text": self.source_text,
            "span": self.span.to_dict(),
            "concept_keys": list(self.concept_keys),
            "determiners": list(self.determiners),
            "modifiers": list(self.modifiers),
            "semantic_class_keys": list(self.semantic_class_keys),
        }


@dataclass(frozen=True, slots=True)
class ParticipantBinding:
    role_key: str
    role_id: str
    value_kind: str
    source_span: SourceSpan | None
    concept_keys: tuple[str, ...]
    implicit: bool
    authority_satisfied: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "role_key": self.role_key,
            "role_id": self.role_id,
            "value_kind": self.value_kind,
            "source_span": (
                self.source_span.to_dict() if self.source_span is not None else None
            ),
            "concept_keys": list(self.concept_keys),
            "implicit": self.implicit,
            "authority_satisfied": self.authority_satisfied,
        }


@dataclass(frozen=True, slots=True)
class ClauseDerivation:
    communicative_form: str
    speech_act: str
    predicate_token_index: int
    action_root_key: str
    negated: bool
    subject_token_indexes: tuple[int, ...]
    object_token_indexes: tuple[int, ...]
    modifier_token_indexes: tuple[int, ...]
    consumed_token_indexes: tuple[int, ...]
    attachment_kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "communicative_form": self.communicative_form,
            "speech_act": self.speech_act,
            "predicate_token_index": self.predicate_token_index,
            "action_root_key": self.action_root_key,
            "negated": self.negated,
            "subject_token_indexes": list(self.subject_token_indexes),
            "object_token_indexes": list(self.object_token_indexes),
            "modifier_token_indexes": list(self.modifier_token_indexes),
            "consumed_token_indexes": list(self.consumed_token_indexes),
            "attachment_kind": self.attachment_kind,
        }


@dataclass(frozen=True, slots=True)
class InterpretationCandidate:
    candidate_id: str
    action_root_key: str
    action_root_id: str
    predicate_id: str
    frame_key: str
    frame_id: str
    communicative_form: str
    speech_act: str
    negated: bool
    participants: tuple[ParticipantBinding, ...]
    object_meaning: ObjectMeaning
    attachment_kind: str
    consumed_token_indexes: tuple[int, ...]
    source_spans: tuple[SourceSpan, ...]
    semantic_signature: str
    selected: bool = False
    permission_granted: bool = False
    execution_authorized: bool = False
    output_authorized: bool = False
    memory_write_authorized: bool = False

    def body_dict(self) -> dict[str, Any]:
        return {
            "action_root_key": self.action_root_key,
            "action_root_id": self.action_root_id,
            "predicate_id": self.predicate_id,
            "frame_key": self.frame_key,
            "frame_id": self.frame_id,
            "communicative_form": self.communicative_form,
            "speech_act": self.speech_act,
            "negated": self.negated,
            "participants": [item.to_dict() for item in self.participants],
            "object_meaning": self.object_meaning.to_dict(),
            "attachment_kind": self.attachment_kind,
            "consumed_token_indexes": list(self.consumed_token_indexes),
            "source_spans": [item.to_dict() for item in self.source_spans],
            "selected": self.selected,
            "permission_granted": self.permission_granted,
            "execution_authorized": self.execution_authorized,
            "output_authorized": self.output_authorized,
            "memory_write_authorized": self.memory_write_authorized,
        }

    def to_dict(self) -> dict[str, Any]:
        value = self.body_dict()
        value["candidate_id"] = self.candidate_id
        value["semantic_signature"] = self.semantic_signature
        return value


@dataclass(frozen=True, slots=True)
class InterpretationEnvelope:
    status: str
    source_text: str
    source_sha256: str
    source_byte_length: int
    tokens: tuple[TokenRecord, ...]
    morphology: tuple[MorphologyRecord, ...]
    candidates: tuple[InterpretationCandidate, ...]
    refusal_code: str | None
    refusal_detail: str | None
    unresolved_conditions: tuple[str, ...]
    ambiguity_preserved: bool
    coverage_complete: bool
    metadata_authority_attempted: bool
    metadata_authority_used: bool
    semantic_signature: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_VERSION,
            "runtime_version": RUNTIME_VERSION,
            "profile_id": PROFILE_ID,
            "profile_version": PROFILE_VERSION,
            "status": self.status,
            "source_text": self.source_text,
            "source_sha256": self.source_sha256,
            "source_byte_length": self.source_byte_length,
            "tokens": [item.to_dict() for item in self.tokens],
            "morphology": [item.to_dict() for item in self.morphology],
            "candidates": [item.to_dict() for item in self.candidates],
            "candidate_count": len(self.candidates),
            "refusal_code": self.refusal_code,
            "refusal_detail": self.refusal_detail,
            "unresolved_conditions": list(self.unresolved_conditions),
            "ambiguity_preserved": self.ambiguity_preserved,
            "coverage_complete": self.coverage_complete,
            "metadata_authority_attempted": self.metadata_authority_attempted,
            "metadata_authority_used": self.metadata_authority_used,
            "semantic_signature": self.semantic_signature,
            "authority_boundary": runtime_authority_boundary(),
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json(self.to_dict()).encode("utf-8")


def make_candidate(
    *,
    action_root_key: str,
    action_root_id: str,
    predicate_id: str,
    frame_key: str,
    frame_id: str,
    communicative_form: str,
    speech_act: str,
    negated: bool,
    participants: tuple[ParticipantBinding, ...],
    object_meaning: ObjectMeaning,
    attachment_kind: str,
    consumed_token_indexes: tuple[int, ...],
    source_spans: tuple[SourceSpan, ...],
) -> InterpretationCandidate:
    provisional = InterpretationCandidate(
        candidate_id="",
        action_root_key=action_root_key,
        action_root_id=action_root_id,
        predicate_id=predicate_id,
        frame_key=frame_key,
        frame_id=frame_id,
        communicative_form=communicative_form,
        speech_act=speech_act,
        negated=negated,
        participants=participants,
        object_meaning=object_meaning,
        attachment_kind=attachment_kind,
        consumed_token_indexes=consumed_token_indexes,
        source_spans=source_spans,
        semantic_signature="",
    )
    body = provisional.body_dict()
    signature = sha256_text(canonical_json(body))
    return InterpretationCandidate(
        candidate_id=stable_id("lc_candidate", body),
        action_root_key=action_root_key,
        action_root_id=action_root_id,
        predicate_id=predicate_id,
        frame_key=frame_key,
        frame_id=frame_id,
        communicative_form=communicative_form,
        speech_act=speech_act,
        negated=negated,
        participants=participants,
        object_meaning=object_meaning,
        attachment_kind=attachment_kind,
        consumed_token_indexes=consumed_token_indexes,
        source_spans=source_spans,
        semantic_signature=signature,
    )


__all__ = (
    "ClauseDerivation",
    "InterpretationCandidate",
    "InterpretationEnvelope",
    "MorphologyRecord",
    "ObjectMeaning",
    "ParticipantBinding",
    "SourceSpan",
    "TokenRecord",
    "canonical_json",
    "make_candidate",
    "sha256_text",
    "stable_id",
)
