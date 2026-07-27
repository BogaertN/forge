"""LC-RMC-001 authority constants and fail-closed error contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


RUNTIME_VERSION: Final[str] = "lc-rmc-001.deterministic-language-runtime.v1"
SCHEMA_VERSION: Final[str] = "aiweb.language-core.interpretation-envelope.v1"
PROFILE_ID: Final[str] = "aiweb.forge.initial-operational-english"
PROFILE_VERSION: Final[str] = "1.0.0"

MAX_SOURCE_BYTES: Final[int] = 4096
MAX_SOURCE_CHARACTERS: Final[int] = 4096
MAX_TOKENS: Final[int] = 128
MAX_CANDIDATES: Final[int] = 8
MAX_NOUN_CONCEPTS: Final[int] = 8

STATUS_INTERPRETED: Final[str] = "INTERPRETED"
STATUS_AMBIGUOUS: Final[str] = "AMBIGUOUS"
STATUS_REFUSED: Final[str] = "REFUSED"

REFUSAL_EMPTY_SOURCE: Final[str] = "LC_RMC_001_EMPTY_SOURCE"
REFUSAL_SOURCE_TOO_LARGE: Final[str] = "LC_RMC_001_SOURCE_TOO_LARGE"
REFUSAL_UNSUPPORTED_UNICODE: Final[str] = "LC_RMC_001_UNSUPPORTED_UNICODE"
REFUSAL_CONTROL_CHARACTER: Final[str] = "LC_RMC_001_CONTROL_CHARACTER"
REFUSAL_UNTOKENIZABLE_SOURCE: Final[str] = "LC_RMC_001_UNTOKENIZABLE_SOURCE"
REFUSAL_TOO_MANY_TOKENS: Final[str] = "LC_RMC_001_TOO_MANY_TOKENS"
REFUSAL_UNSUPPORTED_FORM: Final[str] = "LC_RMC_001_UNSUPPORTED_FORM"
REFUSAL_UNSUPPORTED_PREDICATE: Final[str] = "LC_RMC_001_UNSUPPORTED_PREDICATE"
REFUSAL_UNSUPPORTED_TERM: Final[str] = "LC_RMC_001_UNSUPPORTED_TERM"
REFUSAL_INCOMPLETE_SOURCE_COVERAGE: Final[str] = (
    "LC_RMC_001_INCOMPLETE_SOURCE_COVERAGE"
)
REFUSAL_METADATA_AUTHORITY: Final[str] = "LC_RMC_001_METADATA_AUTHORITY_CONFLICT"
REFUSAL_SOURCE_AUTHORITY_IDENTIFIER: Final[str] = (
    "LC_RMC_001_SOURCE_AUTHORITY_IDENTIFIER_PROHIBITED"
)
REFUSAL_INTERNAL_PROFILE_ERROR: Final[str] = (
    "LC_RMC_001_INTERNAL_PROFILE_CONTRACT_FAILURE"
)

SEMANTIC_METADATA_KEYS: Final[tuple[str, ...]] = (
    "action_root",
    "action_root_id",
    "predicate",
    "predicate_id",
    "predicate_frame",
    "predicate_frame_id",
    "candidate_id",
    "candidate_ids",
    "selected_candidate_id",
    "selected_meaning_id",
    "meaning",
    "semantic_signature",
)


@dataclass(frozen=True, slots=True)
class LanguageRuntimeError(ValueError):
    """A privacy-safe, deterministic refusal raised inside the runtime."""

    code: str
    detail: str
    start: int | None = None
    end: int | None = None

    def __str__(self) -> str:
        return self.code


def runtime_authority_boundary() -> dict[str, object]:
    """Return the immutable authority boundary for the inward interpreter."""

    return {
        "runtime_version": RUNTIME_VERSION,
        "schema_version": SCHEMA_VERSION,
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "deterministic": True,
        "standard_library_only": True,
        "network_access": False,
        "calls_llm": False,
        "uses_embeddings": False,
        "uses_vector_store": False,
        "uses_rag": False,
        "uses_semantic_similarity": False,
        "uses_learned_classifier": False,
        "uses_legacy_heuristic_fallback": False,
        "reads_files": False,
        "writes_files": False,
        "reads_memory": False,
        "writes_memory": False,
        "routes_tools": False,
        "invokes_capabilities": False,
        "executes_actions": False,
        "renders_output": False,
        "delivers_output": False,
        "grants_permission": False,
        "grants_authority": False,
        "selects_ambiguous_meaning": False,
        "metadata_can_supply_meaning": False,
    }


__all__ = (
    "LanguageRuntimeError",
    "MAX_CANDIDATES",
    "MAX_NOUN_CONCEPTS",
    "MAX_SOURCE_BYTES",
    "MAX_SOURCE_CHARACTERS",
    "MAX_TOKENS",
    "PROFILE_ID",
    "PROFILE_VERSION",
    "REFUSAL_CONTROL_CHARACTER",
    "REFUSAL_EMPTY_SOURCE",
    "REFUSAL_INCOMPLETE_SOURCE_COVERAGE",
    "REFUSAL_INTERNAL_PROFILE_ERROR",
    "REFUSAL_METADATA_AUTHORITY",
    "REFUSAL_SOURCE_AUTHORITY_IDENTIFIER",
    "REFUSAL_SOURCE_TOO_LARGE",
    "REFUSAL_TOO_MANY_TOKENS",
    "REFUSAL_UNSUPPORTED_FORM",
    "REFUSAL_UNSUPPORTED_PREDICATE",
    "REFUSAL_UNSUPPORTED_TERM",
    "REFUSAL_UNSUPPORTED_UNICODE",
    "REFUSAL_UNTOKENIZABLE_SOURCE",
    "RUNTIME_VERSION",
    "SCHEMA_VERSION",
    "SEMANTIC_METADATA_KEYS",
    "STATUS_AMBIGUOUS",
    "STATUS_INTERPRETED",
    "STATUS_REFUSED",
    "runtime_authority_boundary",
)
