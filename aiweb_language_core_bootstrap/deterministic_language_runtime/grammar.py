"""Bounded deterministic clause and argument derivation for LC-RMC-001."""

from __future__ import annotations

from dataclasses import dataclass

from .authority import (
    MAX_CANDIDATES,
    MAX_NOUN_CONCEPTS,
    REFUSAL_INCOMPLETE_SOURCE_COVERAGE,
    REFUSAL_UNSUPPORTED_FORM,
    REFUSAL_UNSUPPORTED_PREDICATE,
    REFUSAL_UNSUPPORTED_TERM,
    LanguageRuntimeError,
)
from .forge_profile import (
    ACTION_BY_ROOT,
    ACTION_SURFACE_TO_ROOT,
    ADJECTIVES,
    ATTACHMENT_PREPOSITIONS,
    AUXILIARY_BE,
    AUXILIARY_DO,
    CONTRACTION_FEATURES,
    DETERMINERS,
    MODALS,
    NEGATION_FORMS,
    OBJECT_CONCEPT_SET,
    POLITENESS_FORMS,
    SUBJECTS,
    TERMINAL_PUNCTUATION,
)
from .schema import ClauseDerivation, MorphologyRecord, TokenRecord


@dataclass(frozen=True, slots=True)
class ParsedNounPhrase:
    token_indexes: tuple[int, ...]
    concept_keys: tuple[str, ...]
    determiners: tuple[str, ...]
    modifiers: tuple[str, ...]


def _morphology_by_index(
    morphology: tuple[MorphologyRecord, ...],
) -> dict[int, MorphologyRecord]:
    return {item.token_index: item for item in morphology}


def _parse_noun_phrase(
    indexes: tuple[int, ...],
    tokens: tuple[TokenRecord, ...],
) -> ParsedNounPhrase:
    if not indexes:
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "the admitted predicate requires a bounded object phrase",
        )

    concepts: list[str] = []
    determiners: list[str] = []
    modifiers: list[str] = []
    position = 0
    while position < len(indexes):
        token = tokens[indexes[position]]
        word = token.normalized
        if word in DETERMINERS:
            if position != 0 or determiners:
                raise LanguageRuntimeError(
                    REFUSAL_UNSUPPORTED_FORM,
                    "determiner must occur once at the start of the noun phrase",
                    token.span.start,
                    token.span.end,
                )
            determiners.append(word)
            position += 1
            continue
        if word in ADJECTIVES:
            if concepts:
                raise LanguageRuntimeError(
                    REFUSAL_UNSUPPORTED_FORM,
                    "admitted noun-phrase modifiers must precede concepts",
                    token.span.start,
                    token.span.end,
                )
            modifiers.append(word)
            position += 1
            continue
        if (
            word == "write"
            and position + 1 < len(indexes)
            and tokens[indexes[position + 1]].normalized == "plan"
        ):
            concepts.append("write_plan")
            position += 2
            continue
        if word in OBJECT_CONCEPT_SET:
            concepts.append(word)
            position += 1
            continue
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_TERM,
            "noun phrase contains an unadmitted term",
            token.span.start,
            token.span.end,
        )

    if not concepts:
        token = tokens[indexes[-1]]
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_TERM,
            "noun phrase contains no admitted Forge object concept",
            token.span.start,
            token.span.end,
        )
    if len(concepts) > MAX_NOUN_CONCEPTS:
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "noun phrase exceeds the concept limit",
        )
    return ParsedNounPhrase(
        token_indexes=indexes,
        concept_keys=tuple(concepts),
        determiners=tuple(determiners),
        modifiers=tuple(modifiers),
    )


def parse_noun_phrase(
    indexes: tuple[int, ...],
    tokens: tuple[TokenRecord, ...],
) -> ParsedNounPhrase:
    return _parse_noun_phrase(indexes, tokens)


def _terminal_and_body(
    tokens: tuple[TokenRecord, ...],
) -> tuple[list[int], set[int]]:
    body = list(range(len(tokens)))
    consumed: set[int] = set()
    terminal_count = 0
    while body and tokens[body[-1]].normalized in TERMINAL_PUNCTUATION:
        consumed.add(body.pop())
        terminal_count += 1
    if terminal_count > 1:
        token = tokens[min(consumed)]
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "the initial profile admits one terminal punctuation mark",
            token.span.start,
            tokens[max(consumed)].span.end,
        )
    if any(tokens[index].normalized in TERMINAL_PUNCTUATION for index in body):
        token = next(
            tokens[index]
            for index in body
            if tokens[index].normalized in TERMINAL_PUNCTUATION
        )
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "terminal punctuation is admitted only at the end of the clause",
            token.span.start,
            token.span.end,
        )
    return body, consumed


def derive_clauses(
    tokens: tuple[TokenRecord, ...],
    morphology: tuple[MorphologyRecord, ...],
) -> tuple[ClauseDerivation, ...]:
    morph = _morphology_by_index(morphology)
    body, consumed = _terminal_and_body(tokens)
    if not body:
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "source contains punctuation but no clause",
        )

    cursor = 0
    polite = False
    if tokens[body[cursor]].normalized in POLITENESS_FORMS:
        polite = True
        consumed.add(body[cursor])
        cursor += 1
        if cursor < len(body) and tokens[body[cursor]].normalized == ",":
            consumed.add(body[cursor])
            cursor += 1
    if any(tokens[index].normalized == "," for index in body[cursor:]):
        token = next(tokens[index] for index in body[cursor:] if tokens[index].normalized == ",")
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "comma is admitted only after initial please",
            token.span.start,
            token.span.end,
        )
    if cursor >= len(body):
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "politeness marker has no governed clause",
        )

    communicative_form: str
    speech_act: str
    subject_indexes: tuple[int, ...] = ()
    negated = False
    progressive_required = False
    base_form_required = False
    finite_subject: str | None = None
    finite_auxiliary: str | None = None
    grammatical_subject: str | None = None
    first_index = body[cursor]
    first = tokens[first_index].normalized
    first_morph = morph[first_index]

    if first in MODALS or first_morph.part_of_speech == "modal":
        communicative_form = "MODAL_REQUEST"
        speech_act = "REQUEST"
        consumed.add(first_index)
        negated = "negative" in first_morph.features
        cursor += 1
        if cursor >= len(body) or tokens[body[cursor]].normalized not in SUBJECTS:
            raise LanguageRuntimeError(
                REFUSAL_UNSUPPORTED_FORM,
                "modal request requires an admitted explicit subject",
            )
        subject_indexes = (body[cursor],)
        consumed.add(body[cursor])
        cursor += 1
        base_form_required = True
        if cursor < len(body) and tokens[body[cursor]].normalized in NEGATION_FORMS:
            if negated:
                token = tokens[body[cursor]]
                raise LanguageRuntimeError(
                    REFUSAL_UNSUPPORTED_FORM,
                    "the initial profile admits at most one negation marker",
                    token.span.start,
                    token.span.end,
                )
            negated = True
            consumed.add(body[cursor])
            cursor += 1
    else:
        subject_start = cursor
        if first in DETERMINERS:
            if cursor + 1 < len(body) and tokens[body[cursor + 1]].normalized in SUBJECTS:
                subject_word = tokens[body[cursor + 1]].normalized
                if subject_word not in {"operator", "system", "user"}:
                    token = tokens[body[cursor + 1]]
                    raise LanguageRuntimeError(
                        REFUSAL_UNSUPPORTED_FORM,
                        "determiner cannot govern a pronoun or proper-name subject",
                        token.span.start,
                        token.span.end,
                    )
                subject_indexes = (body[cursor], body[cursor + 1])
                cursor += 2
            else:
                subject_indexes = ()
        elif first in SUBJECTS:
            subject_indexes = (first_index,)
            cursor += 1

        if subject_indexes:
            if polite:
                token = tokens[subject_indexes[0]]
                raise LanguageRuntimeError(
                    REFUSAL_UNSUPPORTED_FORM,
                    "initial please is admitted only for an imperative clause",
                    token.span.start,
                    tokens[subject_indexes[-1]].span.end,
                )
            communicative_form = "SIMPLE_ACTIVE_DECLARATIVE"
            speech_act = "DECLARATIVE"
            consumed.update(subject_indexes)
            grammatical_subject = tokens[subject_indexes[-1]].normalized
            if cursor < len(body) and (
                tokens[body[cursor]].normalized in AUXILIARY_BE
                or morph[body[cursor]].part_of_speech == "auxiliary_be"
            ):
                progressive_required = True
                finite_auxiliary = morph[body[cursor]].lemma
                consumed.add(body[cursor])
                cursor += 1
                if cursor < len(body) and tokens[body[cursor]].normalized in NEGATION_FORMS:
                    if negated:
                        token = tokens[body[cursor]]
                        raise LanguageRuntimeError(
                            REFUSAL_UNSUPPORTED_FORM,
                            "the initial profile admits at most one negation marker",
                            token.span.start,
                            token.span.end,
                        )
                    negated = True
                    consumed.add(body[cursor])
                    cursor += 1
            elif cursor < len(body) and (
                tokens[body[cursor]].normalized in AUXILIARY_DO
                or morph[body[cursor]].part_of_speech == "auxiliary"
            ):
                auxiliary = morph[body[cursor]]
                finite_auxiliary = auxiliary.lemma
                consumed.add(body[cursor])
                negated = "negative" in auxiliary.features
                cursor += 1
                if cursor < len(body) and tokens[body[cursor]].normalized in NEGATION_FORMS:
                    if negated:
                        token = tokens[body[cursor]]
                        raise LanguageRuntimeError(
                            REFUSAL_UNSUPPORTED_FORM,
                            "the initial profile admits at most one negation marker",
                            token.span.start,
                            token.span.end,
                        )
                    negated = True
                    consumed.add(body[cursor])
                    cursor += 1
                base_form_required = True
            else:
                finite_subject = tokens[subject_indexes[-1]].normalized
        else:
            cursor = subject_start
            communicative_form = (
                "POLITE_IMPERATIVE" if polite else "DIRECT_IMPERATIVE"
            )
            speech_act = "DIRECTIVE"
            base_form_required = True
            if cursor < len(body) and (
                tokens[body[cursor]].normalized in AUXILIARY_DO
                or morph[body[cursor]].part_of_speech == "auxiliary"
            ):
                auxiliary = morph[body[cursor]]
                consumed.add(body[cursor])
                negated = "negative" in auxiliary.features
                cursor += 1
                if cursor < len(body) and tokens[body[cursor]].normalized in NEGATION_FORMS:
                    if negated:
                        token = tokens[body[cursor]]
                        raise LanguageRuntimeError(
                            REFUSAL_UNSUPPORTED_FORM,
                            "the initial profile admits at most one negation marker",
                            token.span.start,
                            token.span.end,
                        )
                    negated = True
                    consumed.add(body[cursor])
                    cursor += 1

    if cursor >= len(body):
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_PREDICATE,
            "clause contains no admitted predicate",
        )
    predicate_index = body[cursor]
    predicate_surface = tokens[predicate_index].normalized
    predicate_morph = morph[predicate_index]
    action_root = (
        predicate_morph.lemma
        if predicate_morph.part_of_speech == "verb"
        else ACTION_SURFACE_TO_ROOT.get(predicate_surface)
    )
    if action_root not in ACTION_BY_ROOT:
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_PREDICATE,
            "predicate is outside the admitted action-root profile",
            tokens[predicate_index].span.start,
            tokens[predicate_index].span.end,
        )
    if progressive_required and "progressive" not in predicate_morph.features:
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "be auxiliary requires an admitted progressive action form",
            tokens[predicate_index].span.start,
            tokens[predicate_index].span.end,
        )
    if base_form_required and "base" not in predicate_morph.features:
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "modal, auxiliary-do, and imperative clauses require a base action form",
            tokens[predicate_index].span.start,
            tokens[predicate_index].span.end,
        )
    if finite_subject is not None:
        features = set(predicate_morph.features)
        singular_subjects = {"forge", "operator", "system", "user"}
        agreement_ok = (
            "past" in features
            or (
                finite_subject in singular_subjects
                and "third_person_singular" in features
            )
            or (
                finite_subject not in singular_subjects
                and "base" in features
            )
        )
        if not agreement_ok:
            raise LanguageRuntimeError(
                REFUSAL_UNSUPPORTED_FORM,
                "finite declarative action form does not agree with its subject",
                tokens[predicate_index].span.start,
                tokens[predicate_index].span.end,
            )
    if finite_auxiliary is not None and grammatical_subject is not None:
        if grammatical_subject == "i":
            admitted_be = {"am", "was"}
            admitted_do = {"do", "did"}
        elif grammatical_subject in {"we", "you"}:
            admitted_be = {"are", "were"}
            admitted_do = {"do", "did"}
        else:
            admitted_be = {"is", "was"}
            admitted_do = {"does", "did"}
        admitted_auxiliaries = (
            admitted_be if progressive_required else admitted_do
        )
        if finite_auxiliary not in admitted_auxiliaries:
            raise LanguageRuntimeError(
                REFUSAL_UNSUPPORTED_FORM,
                "finite auxiliary does not agree with its subject",
                tokens[predicate_index].span.start,
                tokens[predicate_index].span.end,
            )
    consumed.add(predicate_index)
    cursor += 1

    if cursor >= len(body):
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "predicate requires an admitted object phrase",
        )

    remainder = tuple(body[cursor:])
    preposition_positions = [
        offset
        for offset, index in enumerate(remainder)
        if tokens[index].normalized in ATTACHMENT_PREPOSITIONS
    ]
    if len(preposition_positions) > 1:
        token = tokens[remainder[preposition_positions[1]]]
        raise LanguageRuntimeError(
            REFUSAL_UNSUPPORTED_FORM,
            "the initial profile admits at most one attachment phrase",
            token.span.start,
            token.span.end,
        )

    if preposition_positions:
        split = preposition_positions[0]
        object_indexes = remainder[:split]
        preposition_index = remainder[split]
        modifier_indexes = remainder[split + 1 :]
        _parse_noun_phrase(object_indexes, tokens)
        _parse_noun_phrase(modifier_indexes, tokens)
        consumed.add(preposition_index)
        consumed.update(object_indexes)
        consumed.update(modifier_indexes)
        attachment_kinds = (
            "PREDICATE_INSTRUMENT_ATTACHMENT",
            "OBJECT_MODIFIER_ATTACHMENT",
        )
    else:
        object_indexes = remainder
        modifier_indexes = ()
        _parse_noun_phrase(object_indexes, tokens)
        consumed.update(object_indexes)
        attachment_kinds = ("NONE",)

    if len(consumed) != len(tokens):
        missing = sorted(set(range(len(tokens))) - consumed)
        token = tokens[missing[0]]
        raise LanguageRuntimeError(
            REFUSAL_INCOMPLETE_SOURCE_COVERAGE,
            "not every source token participates in the bounded derivation",
            token.span.start,
            token.span.end,
        )

    derivations = tuple(
        ClauseDerivation(
            communicative_form=communicative_form,
            speech_act=speech_act,
            predicate_token_index=predicate_index,
            action_root_key=action_root,
            negated=negated,
            subject_token_indexes=subject_indexes,
            object_token_indexes=tuple(object_indexes),
            modifier_token_indexes=tuple(modifier_indexes),
            consumed_token_indexes=tuple(sorted(consumed)),
            attachment_kind=attachment_kind,
        )
        for attachment_kind in attachment_kinds[:MAX_CANDIDATES]
    )
    return derivations


__all__ = ("ParsedNounPhrase", "derive_clauses", "parse_noun_phrase")
