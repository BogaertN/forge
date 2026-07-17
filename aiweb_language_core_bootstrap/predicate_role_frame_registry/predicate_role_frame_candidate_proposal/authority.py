"""Slice 38G authority boundaries and canonical compatibility ruling."""

from __future__ import annotations

from typing import Final


SLICE38G_NON_AUTHORITY_BOUNDARIES: Final[tuple[str, ...]] = (
    "Slice 37 concept candidate is not action-root identity",
    "Slice 37 sense candidate is not predicate identity",
    "exact compatibility rule is not selected predicate",
    "action-root candidate is not selected action root",
    "predicate candidate is not selected predicate",
    "frame candidate is not selected frame",
    "role-layout candidate is not participant assignment",
    "required-role inventory is not a filled role",
    "missing role is not clarification outcome",
    "conflict is not refusal outcome",
    "unsupported is not rejection or falsehood",
    "unknown is not permission to guess",
    "structurally complete is not selected meaning",
    "frame completion is not permission",
    "effect boundary is not permission",
    "capability-family reference is not capability availability",
    "capability availability is not route",
    "route is not invocation",
    "invocation proposal is not execution",
    "execution is not proof",
    "candidate order is deterministic custody order and carries no rank",
    "multiple candidates remain unresolved alternatives",
    "candidate selection belongs to the later Document 6 gate layer",
    "ambiguity resolution belongs to the later Document 6 gate layer",
    "clarification belongs to the later Document 6 gate layer",
    "refusal belongs to the later Document 6 gate layer",
    "blocked progression belongs to the later Document 6 gate layer",
    "CandidateMeaning is not created in Slice 38G",
    "selected meaning is not created in Slice 38G",
    "permission is not inferred in Slice 38G",
    "tool route is not created in Slice 38G",
    "action is not performed in Slice 38G",
    "memory is not accessed in Slice 38G",
    "delivery is not performed in Slice 38G",
    "evidence validity is not determined in Slice 38G",
    "truth is not determined in Slice 38G",
    "surface similarity is not compatibility",
    "nearest-known substitution is prohibited",
    "LLM inference is prohibited",
)

# The accepted Slice 37 registry presently contains controlled meta-semantic
# concepts and senses.  None is definitionally equivalent to any of the five
# admitted Slice 38C action roots.  The canonical bridge is therefore closed
# and empty rather than guessed.  The runtime supports a separately governed,
# immutable compatibility snapshot for future exact admissions.
CANONICAL_COMPATIBILITY_RULE_KEYS: Final[tuple[str, ...]] = ()
CANONICAL_COMPATIBILITY_CONFLICT_KEYS: Final[tuple[str, ...]] = ()

CANONICAL_COMPATIBILITY_RULING: Final[str] = (
    "No current Slice 37 concept or sense identity is admitted as an exact "
    "equivalent of inspect, report, request, verify, or simulate. Candidate "
    "proposal must therefore return explicit unsupported state unless an "
    "exact, immutable, provenance-bound compatibility snapshot is supplied."
)

CANONICAL_PROVENANCE_REFS: Final[tuple[str, ...]] = (
    "AI.Web Forge Canonical Production Roadmap v1.0 — Slice 38G",
    "RMC Predicate–Role Frame Registry v1 — candidate/selected boundary",
    "Slice 37F structural concept and sense candidate proposal",
    "Slice 38C minimal built-in action-root registry",
    "Slice 38D participant-role identity registry",
    "Slice 38E predicate-frame constraints and role compatibility",
    "Slice 38F capability-family references and effect boundaries",
)
