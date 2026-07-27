"""End-to-end bounded deterministic inward interpreter for LC-RMC-001."""

from __future__ import annotations

from typing import Any

from .authority import (
    REFUSAL_METADATA_AUTHORITY,
    REFUSAL_SOURCE_AUTHORITY_IDENTIFIER,
    RUNTIME_VERSION,
    SEMANTIC_METADATA_KEYS,
    STATUS_AMBIGUOUS,
    STATUS_INTERPRETED,
    STATUS_REFUSED,
    LanguageRuntimeError,
)
from .forge_profile import (
    AUTHORITY_IDENTIFIER_PATTERN,
    action_profile,
    concept_classes,
    resolve_registry_identities,
)
from .grammar import ParsedNounPhrase, derive_clauses, parse_noun_phrase
from .morphology import analyze_morphology
from .schema import (
    ClauseDerivation,
    InterpretationCandidate,
    InterpretationEnvelope,
    ObjectMeaning,
    ParticipantBinding,
    SourceSpan,
    canonical_json,
    make_candidate,
    sha256_text,
)
from .tokenization import tokenize


def _span_for_indexes(
    source_text: str,
    indexes: tuple[int, ...],
    tokens,
) -> SourceSpan:
    start = tokens[indexes[0]].span.start
    end = tokens[indexes[-1]].span.end
    return SourceSpan(start=start, end=end, text=source_text[start:end])


def _object_meaning(
    source_text: str,
    phrase: ParsedNounPhrase,
    modifier: ParsedNounPhrase | None,
    *,
    include_modifier_in_object: bool,
    tokens,
) -> ObjectMeaning:
    concept_keys = phrase.concept_keys
    determiners = phrase.determiners
    modifiers = phrase.modifiers
    indexes = phrase.token_indexes
    if include_modifier_in_object and modifier is not None:
        concept_keys = (*concept_keys, *modifier.concept_keys)
        determiners = (*determiners, *modifier.determiners)
        modifiers = (*modifiers, *modifier.modifiers)
        indexes = (*indexes, *modifier.token_indexes)
    span = _span_for_indexes(source_text, tuple(sorted(indexes)), tokens)
    return ObjectMeaning(
        source_text=span.text,
        span=span,
        concept_keys=tuple(concept_keys),
        determiners=tuple(determiners),
        modifiers=tuple(modifiers),
        semantic_class_keys=concept_classes(tuple(concept_keys)),
    )


def _subject_participant(
    source_text: str,
    derivation: ClauseDerivation,
    identities: dict[str, str],
    tokens,
) -> ParticipantBinding:
    is_request = derivation.action_root_key == "request"
    role_key = "initiator" if is_request else "actor"
    role_id = (
        identities["initiator_role_id"]
        if is_request
        else identities["actor_role_id"]
    )
    if derivation.subject_token_indexes:
        span = _span_for_indexes(
            source_text,
            derivation.subject_token_indexes,
            tokens,
        )
        concepts = tuple(
            tokens[index].normalized
            for index in derivation.subject_token_indexes
            if tokens[index].normalized not in {"a", "an", "the", "this", "that"}
        )
        return ParticipantBinding(
            role_key=role_key,
            role_id=role_id,
            value_kind="explicit_grammatical_subject",
            source_span=span,
            concept_keys=concepts,
            implicit=False,
        )
    return ParticipantBinding(
        role_key=role_key,
        role_id=role_id,
        value_kind="implicit_imperative_subject",
        source_span=None,
        concept_keys=(),
        implicit=True,
    )


def _candidate_from_derivation(
    source_text: str,
    derivation: ClauseDerivation,
    tokens,
) -> InterpretationCandidate:
    profile = action_profile(derivation.action_root_key)
    identities = resolve_registry_identities(derivation.action_root_key)
    phrase = parse_noun_phrase(derivation.object_token_indexes, tokens)
    modifier = (
        parse_noun_phrase(derivation.modifier_token_indexes, tokens)
        if derivation.modifier_token_indexes
        else None
    )
    include_modifier = derivation.attachment_kind == "OBJECT_MODIFIER_ATTACHMENT"
    object_meaning = _object_meaning(
        source_text,
        phrase,
        modifier,
        include_modifier_in_object=include_modifier,
        tokens=tokens,
    )
    participants: list[ParticipantBinding] = [
        _subject_participant(source_text, derivation, identities, tokens),
        ParticipantBinding(
            role_key=identities["object_role_key"],
            role_id=identities["object_role_id"],
            value_kind="bounded_forge_object_phrase",
            source_span=object_meaning.span,
            concept_keys=object_meaning.concept_keys,
            implicit=False,
        ),
    ]
    if (
        modifier is not None
        and derivation.attachment_kind == "PREDICATE_INSTRUMENT_ATTACHMENT"
    ):
        modifier_span = _span_for_indexes(
            source_text,
            modifier.token_indexes,
            tokens,
        )
        participants.append(
            ParticipantBinding(
                role_key="instrument",
                role_id=identities["instrument_role_id"],
                value_kind="bounded_attachment_instrument_candidate",
                source_span=modifier_span,
                concept_keys=modifier.concept_keys,
                implicit=False,
            )
        )

    source_spans = tuple(
        tokens[index].span for index in derivation.consumed_token_indexes
    )
    return make_candidate(
        action_root_key=profile.root,
        action_root_id=identities["action_root_id"],
        predicate_id=identities["predicate_id"],
        frame_key=identities["frame_key"],
        frame_id=identities["frame_id"],
        communicative_form=derivation.communicative_form,
        speech_act=derivation.speech_act,
        negated=derivation.negated,
        participants=tuple(participants),
        object_meaning=object_meaning,
        attachment_kind=derivation.attachment_kind,
        consumed_token_indexes=derivation.consumed_token_indexes,
        source_spans=source_spans,
    )


def _metadata_authority_attempt(
    source_metadata: dict[str, Any],
    candidates: tuple[InterpretationCandidate, ...],
) -> bool:
    attempts = {
        key: source_metadata[key]
        for key in SEMANTIC_METADATA_KEYS
        if key in source_metadata and source_metadata[key] not in (None, "", [], {})
    }
    if not attempts:
        return False

    candidate = candidates[0]
    allowed_exact_values = {
        "action_root": candidate.action_root_key,
        "predicate": candidate.action_root_key,
        "action_root_id": candidate.action_root_id,
        "predicate_id": candidate.predicate_id,
        "predicate_frame": candidate.frame_key,
        "predicate_frame_id": candidate.frame_id,
    }
    for key, value in attempts.items():
        if key not in allowed_exact_values:
            raise LanguageRuntimeError(
                REFUSAL_METADATA_AUTHORITY,
                "metadata attempted to supply or select semantic authority",
            )
        if type(value) is not str or value != allowed_exact_values[key]:
            raise LanguageRuntimeError(
                REFUSAL_METADATA_AUTHORITY,
                "metadata conflicts with source-derived meaning",
            )
    return True


def _refused_envelope(
    source_text: str,
    error: LanguageRuntimeError,
    *,
    tokens=(),
    morphology=(),
    metadata_authority_attempted: bool = False,
) -> InterpretationEnvelope:
    source = source_text if type(source_text) is str else ""
    signature = sha256_text(
        canonical_json(
            {
                "runtime_version": RUNTIME_VERSION,
                "source_sha256": sha256_text(source),
                "refusal_code": error.code,
                "start": error.start,
                "end": error.end,
            }
        )
    )
    condition = error.code
    if error.start is not None and error.end is not None:
        condition = f"{error.code}@{error.start}:{error.end}"
    return InterpretationEnvelope(
        status=STATUS_REFUSED,
        source_text=source,
        source_sha256=sha256_text(source),
        source_byte_length=len(source.encode("utf-8")),
        tokens=tuple(tokens),
        morphology=tuple(morphology),
        candidates=(),
        refusal_code=error.code,
        refusal_detail=error.detail,
        unresolved_conditions=(condition,),
        ambiguity_preserved=False,
        coverage_complete=False,
        metadata_authority_attempted=metadata_authority_attempted,
        metadata_authority_used=False,
        semantic_signature=signature,
    )


def interpret_source(
    source_text: str,
    source_metadata: dict[str, Any] | None = None,
) -> InterpretationEnvelope:
    """Interpret one source expression under the closed initial Forge profile."""

    if source_metadata is None:
        metadata: dict[str, Any] = {}
    elif type(source_metadata) is dict:
        metadata = dict(source_metadata)
    else:
        raise TypeError("source_metadata must be a dict or None")

    tokens = ()
    morphology = ()
    attempted = any(
        key in metadata and metadata[key] not in (None, "", [], {})
        for key in SEMANTIC_METADATA_KEYS
    )
    try:
        tokens = tokenize(source_text)
        for token in tokens:
            if token.kind == "IDENTIFIER" and AUTHORITY_IDENTIFIER_PATTERN.fullmatch(
                token.normalized
            ):
                raise LanguageRuntimeError(
                    REFUSAL_SOURCE_AUTHORITY_IDENTIFIER,
                    "source-embedded candidate or selection identifiers are not authority",
                    token.span.start,
                    token.span.end,
                )
        morphology = analyze_morphology(tokens)
        derivations = derive_clauses(tokens, morphology)
        candidates = tuple(
            _candidate_from_derivation(source_text, derivation, tokens)
            for derivation in derivations
        )
        attempted = _metadata_authority_attempt(metadata, candidates)
    except LanguageRuntimeError as error:
        return _refused_envelope(
            source_text,
            error,
            tokens=tokens,
            morphology=morphology,
            metadata_authority_attempted=attempted,
        )

    candidate_signatures = [
        candidate.semantic_signature for candidate in candidates
    ]
    envelope_signature = sha256_text(
        canonical_json(
            {
                "runtime_version": RUNTIME_VERSION,
                "source_sha256": sha256_text(source_text),
                "candidate_signatures": candidate_signatures,
                "ambiguity_preserved": len(candidates) > 1,
            }
        )
    )
    status = STATUS_AMBIGUOUS if len(candidates) > 1 else STATUS_INTERPRETED
    return InterpretationEnvelope(
        status=status,
        source_text=source_text,
        source_sha256=sha256_text(source_text),
        source_byte_length=len(source_text.encode("utf-8")),
        tokens=tokens,
        morphology=morphology,
        candidates=candidates,
        refusal_code=None,
        refusal_detail=None,
        unresolved_conditions=(
            ("LC_RMC_001_ATTACHMENT_AMBIGUITY",)
            if len(candidates) > 1
            else ()
        ),
        ambiguity_preserved=len(candidates) > 1,
        coverage_complete=all(
            len(candidate.consumed_token_indexes) == len(tokens)
            for candidate in candidates
        ),
        metadata_authority_attempted=attempted,
        metadata_authority_used=False,
        semantic_signature=envelope_signature,
    )


def interpret_to_dict(
    source_text: str,
    source_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return interpret_source(source_text, source_metadata).to_dict()


__all__ = ("interpret_source", "interpret_to_dict")
