"""Slice 39B-E roadmap-continuity correction authority."""

from .authority import (
    SLICE39B_E_PERMANENT_BOUNDARIES,
    SLICE39_BOUNDARIES,
    SLICE39_PRE_GATE_REQUIRED_INCREMENTS,
    SLICE39_SEQUENCE,
    SLICE40_ENTRY_REQUIREMENT,
    SliceRoadmapBoundary,
)
from .validation import RoadmapContinuityReport, validate_roadmap_continuity

__all__ = (
    "RoadmapContinuityReport",
    "SLICE39B_E_PERMANENT_BOUNDARIES",
    "SLICE39_BOUNDARIES",
    "SLICE39_PRE_GATE_REQUIRED_INCREMENTS",
    "SLICE39_SEQUENCE",
    "SLICE40_ENTRY_REQUIREMENT",
    "SliceRoadmapBoundary",
    "validate_roadmap_continuity",
)
