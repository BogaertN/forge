"""Exact, source-span-preserving tokenizer for the LC-RMC-001 profile."""

from __future__ import annotations

import re
from typing import Final

from .authority import (
    MAX_SOURCE_BYTES,
    MAX_SOURCE_CHARACTERS,
    MAX_TOKENS,
    REFUSAL_CONTROL_CHARACTER,
    REFUSAL_EMPTY_SOURCE,
    REFUSAL_SOURCE_TOO_LARGE,
    REFUSAL_TOO_MANY_TOKENS,
    REFUSAL_UNSUPPORTED_UNICODE,
    REFUSAL_UNTOKENIZABLE_SOURCE,
    LanguageRuntimeError,
)
from .schema import SourceSpan, TokenRecord, stable_id


_TOKEN_PATTERN: Final = re.compile(
    r"[A-Za-z][A-Za-z0-9]*(?:[_:][A-Za-z0-9][A-Za-z0-9_:-]*)+"
    r"|[A-Za-z]+(?:-[A-Za-z]+)*(?:'[A-Za-z]+)?"
    r"|[0-9]+"
    r"|[.,?!]"
)


def _validate_source(source_text: str) -> None:
    if type(source_text) is not str:
        raise TypeError("source_text must be an exact str")
    if not source_text.strip():
        raise LanguageRuntimeError(
            REFUSAL_EMPTY_SOURCE,
            "source expression is empty",
        )
    if len(source_text) > MAX_SOURCE_CHARACTERS:
        raise LanguageRuntimeError(
            REFUSAL_SOURCE_TOO_LARGE,
            "source expression exceeds the character limit",
        )
    if len(source_text.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise LanguageRuntimeError(
            REFUSAL_SOURCE_TOO_LARGE,
            "source expression exceeds the byte limit",
        )
    for index, char in enumerate(source_text):
        codepoint = ord(char)
        if codepoint > 0x7F:
            raise LanguageRuntimeError(
                REFUSAL_UNSUPPORTED_UNICODE,
                "the initial profile admits ASCII source only",
                index,
                index + 1,
            )
        if codepoint < 0x20 or codepoint == 0x7F:
            raise LanguageRuntimeError(
                REFUSAL_CONTROL_CHARACTER,
                "control characters are not admitted",
                index,
                index + 1,
            )


def tokenize(source_text: str) -> tuple[TokenRecord, ...]:
    """Tokenize the exact source without normalization or lossy replacement."""

    _validate_source(source_text)
    records: list[TokenRecord] = []
    cursor = 0
    for match in _TOKEN_PATTERN.finditer(source_text):
        gap = source_text[cursor : match.start()]
        if gap and not gap.isspace():
            raise LanguageRuntimeError(
                REFUSAL_UNTOKENIZABLE_SOURCE,
                "source contains an unadmitted character sequence",
                cursor,
                match.start(),
            )
        source = match.group(0)
        kind = "PUNCTUATION" if source in ".,?!" else (
            "IDENTIFIER" if "_" in source or ":" in source else "WORD"
        )
        index = len(records)
        span = SourceSpan(match.start(), match.end(), source)
        records.append(
            TokenRecord(
                index=index,
                kind=kind,
                source=source,
                normalized=source.lower(),
                span=span,
                ancestry_id=stable_id(
                    "lc_token",
                    {
                        "source": source_text,
                        "index": index,
                        "start": match.start(),
                        "end": match.end(),
                        "text": source,
                    },
                ),
            )
        )
        cursor = match.end()

    trailing = source_text[cursor:]
    if trailing and not trailing.isspace():
        raise LanguageRuntimeError(
            REFUSAL_UNTOKENIZABLE_SOURCE,
            "source contains an unadmitted trailing sequence",
            cursor,
            len(source_text),
        )
    if not records:
        raise LanguageRuntimeError(
            REFUSAL_EMPTY_SOURCE,
            "source expression contains no admitted linguistic units",
        )
    if len(records) > MAX_TOKENS:
        raise LanguageRuntimeError(
            REFUSAL_TOO_MANY_TOKENS,
            "source expression exceeds the token limit",
        )
    return tuple(records)


__all__ = ("tokenize",)
