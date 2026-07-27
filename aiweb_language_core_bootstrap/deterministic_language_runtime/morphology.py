"""Deterministic morphology for the closed LC-RMC-001 English profile."""

from __future__ import annotations

from .forge_profile import (
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
from .schema import MorphologyRecord, TokenRecord


def analyze_morphology(
    tokens: tuple[TokenRecord, ...],
) -> tuple[MorphologyRecord, ...]:
    records: list[MorphologyRecord] = []
    for token in tokens:
        normalized = token.normalized
        features: tuple[str, ...] = ()
        part = "unknown"
        lemma = normalized

        if token.kind == "PUNCTUATION":
            part = "punctuation"
            features = (
                "terminal" if normalized in TERMINAL_PUNCTUATION else "separator",
            )
        elif normalized in CONTRACTION_FEATURES:
            lemma, category, polarity = CONTRACTION_FEATURES[normalized]
            part = category
            features = (polarity, "contracted")
        elif normalized in ACTION_SURFACE_TO_ROOT:
            lemma = ACTION_SURFACE_TO_ROOT[normalized]
            part = "verb"
            if normalized == lemma:
                features = ("base",)
            elif normalized.endswith("ing"):
                features = ("progressive",)
            elif normalized.endswith("ed"):
                features = ("past",)
            else:
                features = ("third_person_singular",)
        elif normalized in MODALS:
            part = "modal"
        elif normalized in AUXILIARY_BE:
            part = "auxiliary_be"
        elif normalized in AUXILIARY_DO:
            part = "auxiliary"
        elif normalized in NEGATION_FORMS:
            part = "negation"
        elif normalized in DETERMINERS:
            part = "determiner"
        elif normalized in ADJECTIVES:
            part = "adjective"
        elif normalized in SUBJECTS:
            part = "subject"
        elif normalized in POLITENESS_FORMS:
            part = "politeness"
        elif normalized in ATTACHMENT_PREPOSITIONS:
            part = "preposition"
        elif normalized in OBJECT_CONCEPT_SET or normalized in {"write", "plan"}:
            part = "noun"
        elif token.kind == "IDENTIFIER":
            part = "identifier"

        records.append(
            MorphologyRecord(
                token_index=token.index,
                lemma=lemma,
                part_of_speech=part,
                features=features,
            )
        )
    return tuple(records)


__all__ = ("analyze_morphology",)
