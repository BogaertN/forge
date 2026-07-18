"""Pure validation for exact Slice 39 roadmap continuity authority."""

from __future__ import annotations

from dataclasses import dataclass

from .authority import (
    SLICE39_BOUNDARIES,
    SLICE39_PRE_GATE_REQUIRED_INCREMENTS,
    SLICE39_SEQUENCE,
    SLICE40_ENTRY_REQUIREMENT,
)


@dataclass(frozen=True, slots=True)
class RoadmapContinuityReport:
    ok: bool
    issues: tuple[str, ...]


def validate_roadmap_continuity() -> RoadmapContinuityReport:
    issues: list[str] = []
    if SLICE39_SEQUENCE != ("39A", "39B", "39C", "39D", "39E", "39F", "39G", "39H", "40"):
        issues.append("sequence mismatch")
    if SLICE39_PRE_GATE_REQUIRED_INCREMENTS != ("39F", "39G", "39H"):
        issues.append("pre-gate increments mismatch")
    if "39H" not in SLICE40_ENTRY_REQUIREMENT:
        issues.append("Slice 40 entry requirement does not name 39H")
    expected = {
        "39B": ("39A", "39C"), "39C": ("39B", "39D"),
        "39D": ("39C", "39E"), "39E": ("39D", "39F"),
        "39F": ("39E", "39G"), "39G": ("39F", "39H"),
        "39H": ("39G", "40"),
    }
    observed: set[str] = set()
    for boundary in SLICE39_BOUNDARIES:
        if boundary.slice_id in observed:
            issues.append(f"duplicate boundary {boundary.slice_id}")
        observed.add(boundary.slice_id)
        if expected.get(boundary.slice_id) != (boundary.predecessor, boundary.successor):
            issues.append(f"dependency mismatch {boundary.slice_id}")
        if not boundary.owned_authority:
            issues.append(f"empty owned authority {boundary.slice_id}")
        if not boundary.prohibited_authority:
            issues.append(f"empty prohibited authority {boundary.slice_id}")
    if observed != set(expected):
        issues.append("boundary inventory mismatch")
    return RoadmapContinuityReport(ok=not issues, issues=tuple(issues))
