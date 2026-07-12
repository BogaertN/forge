"""Core constants for Slice 19.

The constants in this file define a boundary scaffold only. They must not be
interpreted as a runnable Echo validator, a delivery gate, a renderer, a public
release decision, or output approval.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping

SLICE_ID = "Slice 19"
SLICE_TITLE = "RMC Echo Boundary Scaffold"
SCAFFOLD_VERSION = "1.0.0"

EXPECTED_BASE_HEAD = "9af49a428c9fd87f16a1a03b98947aada6c55b6c"
EXPECTED_BASE_SUBJECT = "Slice 18R1 verifier context correction"
EXPECTED_COMMIT_SUBJECT = "Slice 19 RMC Echo boundary scaffold"

IMPLEMENTATION_STATE = "not_implemented"
ECHO_RELATIONSHIP = "separate_later_authority_layer"

@dataclass(frozen=True, slots=True)
class BoundaryItem:
    """A single locked Slice 19 boundary statement."""

    key: str
    allowed: bool
    statement: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def frozen_mapping(items: Mapping[str, Any]) -> dict[str, Any]:
    """Return a JSON-friendly shallow copy.

    This helper intentionally does not create runtime authority. It only makes
    deterministic reports easier to inspect and test.
    """

    return dict(items)
