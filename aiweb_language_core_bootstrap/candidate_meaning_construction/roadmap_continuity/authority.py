"""Exact Slice 39 roadmap continuity authority.

This module records build-order custody only. It does not construct candidate
meaning, integrate a manifest, connect the bootstrap, evaluate a gate, or
create any consequence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class SliceRoadmapBoundary:
    slice_id: str
    predecessor: str
    successor: str
    owned_authority: str
    prohibited_authority: tuple[str, ...]


SLICE39_SEQUENCE: Final[tuple[str, ...]] = (
    "39A", "39B", "39C", "39D", "39E", "39F", "39G", "39H", "40",
)

SLICE39_PRE_GATE_REQUIRED_INCREMENTS: Final[tuple[str, ...]] = (
    "39F", "39G", "39H",
)

SLICE40_ENTRY_REQUIREMENT: Final[str] = (
    "accepted Slice 39H disabled-bootstrap integration and Slice 39 closeout"
)

_COMMON_PROHIBITED: Final[tuple[str, ...]] = (
    "ranking", "confidence scoring", "candidate selection", "gate outcome",
    "selected meaning", "truth determination", "evidence validation",
    "permission", "capability availability", "route", "invocation", "action",
    "memory access", "rendering", "delivery", "LLM authority",
    "embedding authority", "semantic-similarity authority",
)

SLICE39_BOUNDARIES: Final[tuple[SliceRoadmapBoundary, ...]] = (
    SliceRoadmapBoundary("39B", "39A", "39C", "validation identity versioning lifecycle", _COMMON_PROHIBITED + ("complete provenance binding", "semantic content assembly", "actual runtime constructor", "MSM integration", "bootstrap integration", "Slice 39 closeout")),
    SliceRoadmapBoundary("39C", "39B", "39D", "complete provenance and predecessor custody", _COMMON_PROHIBITED + ("semantic content assembly", "candidate-set preservation", "actual runtime constructor", "MSM integration", "bootstrap integration", "Slice 39 closeout")),
    SliceRoadmapBoundary("39D", "39C", "39E", "candidate semantic-content assembly", _COMMON_PROHIBITED + ("candidate-set preservation", "actual runtime constructor", "MSM integration", "bootstrap integration", "Slice 39 closeout")),
    SliceRoadmapBoundary("39E", "39D", "39F", "candidate-set and alternative preservation", _COMMON_PROHIBITED + ("actual runtime constructor", "MSM integration", "bootstrap integration", "Slice 39 closeout")),
    SliceRoadmapBoundary("39F", "39E", "39G", "deterministic in-memory CandidateMeaning construction and construction receipt", _COMMON_PROHIBITED + ("MSM integration", "bootstrap integration", "Slice 39 closeout")),
    SliceRoadmapBoundary("39G", "39F", "39H", "candidate-side MeaningStructureManifestV1 custody integration", _COMMON_PROHIBITED + ("bootstrap integration", "Slice 39 closeout")),
    SliceRoadmapBoundary("39H", "39G", "40", "disabled bootstrap integration and final Slice 39 closeout", _COMMON_PROHIBITED),
)

SLICE39B_E_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "source text is not candidate meaning",
    "structural candidate is not candidate meaning",
    "concept candidate is not accepted concept occurrence",
    "sense candidate is not selected sense",
    "predicate candidate is not selected predicate",
    "frame candidate is not selected frame",
    "role-layout candidate is not participant assignment",
    "referent candidate is not resolved referent",
    "multiple candidates are not an ambiguous gate outcome",
    "missing role is not clarification-required outcome",
    "unsupported construction is not refusal",
    "complete candidate is not gate pass",
    "complete candidate is not selected meaning",
    "candidate meaning is not truth, evidence, permission, or execution",
)
