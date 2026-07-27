"""LC-RMC-001 deterministic inward Language Core runtime."""

from .authority import (
    PROFILE_ID,
    PROFILE_VERSION,
    RUNTIME_VERSION,
    SCHEMA_VERSION,
    runtime_authority_boundary,
)
from .forge_profile import profile_manifest
from .interpreter import interpret_source, interpret_to_dict
from .schema import (
    InterpretationCandidate,
    InterpretationEnvelope,
    MorphologyRecord,
    ObjectMeaning,
    ParticipantBinding,
    SourceSpan,
    TokenRecord,
    canonical_json,
)

__all__ = (
    "InterpretationCandidate",
    "InterpretationEnvelope",
    "MorphologyRecord",
    "ObjectMeaning",
    "PROFILE_ID",
    "PROFILE_VERSION",
    "ParticipantBinding",
    "RUNTIME_VERSION",
    "SCHEMA_VERSION",
    "SourceSpan",
    "TokenRecord",
    "canonical_json",
    "interpret_source",
    "interpret_to_dict",
    "profile_manifest",
    "runtime_authority_boundary",
)
