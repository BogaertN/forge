"""Exact legacy-or-registry predicate/frame version custody for Slice 40 gates.

Slice 40C through 40F were admitted with frozen v1.0.0 fixtures before the
current Slice 38 registries advanced admitted predicate identities to v1.3.0
and predicate-frame identities to v1.1.0.  This module preserves the frozen
legacy path while admitting only an exact current registry ID/version pair.
It performs no occurrence interpretation, candidate selection, gate outcome,
permission grant, route creation, tool invocation, action, memory operation,
or language-model call.
"""

from __future__ import annotations

from typing import Final

from ..predicate_role_frame_registry.built_in_action_root_registry.registry import (
    predicate_by_id,
)
from ..predicate_role_frame_registry.predicate_frame_registry.registry import (
    frame_by_id,
)


LEGACY_GATE_PREDICATE_VERSION: Final[str] = "v1.0.0"
LEGACY_GATE_FRAME_VERSION: Final[str] = "v1.0.0"


def invalid_predicate_frame_version_fields(
    *,
    predicate_id: object,
    predicate_version: object,
    frame_id: object,
    frame_version: object,
) -> tuple[str, ...]:
    """Return the exact version fields that fail closed custody validation.

    The original Slice 40 v1.0.0 fixture pair remains accepted exactly as it
    was before this compatibility correction.  Any non-legacy pair must resolve
    by exact identity in the current admitted Slice 38 registries, carry the
    exact registered versions, and preserve the frame-to-predicate link.
    """

    if (
        predicate_version == LEGACY_GATE_PREDICATE_VERSION
        and frame_version == LEGACY_GATE_FRAME_VERSION
    ):
        return ()

    invalid: list[str] = []
    predicate = None
    frame = None

    try:
        predicate = predicate_by_id(predicate_id)  # type: ignore[arg-type]
    except (KeyError, TypeError):
        invalid.append("predicate_version")

    try:
        frame = frame_by_id(frame_id)  # type: ignore[arg-type]
    except (KeyError, TypeError):
        invalid.append("frame_version")

    if predicate is not None and predicate.version != predicate_version:
        invalid.append("predicate_version")

    if frame is not None and frame.version != frame_version:
        invalid.append("frame_version")

    if (
        predicate is not None
        and frame is not None
        and frame.linked_predicate_id != predicate.predicate_id
    ):
        invalid.extend(("predicate_version", "frame_version"))

    return tuple(dict.fromkeys(invalid))


__all__ = (
    "LEGACY_GATE_FRAME_VERSION",
    "LEGACY_GATE_PREDICATE_VERSION",
    "invalid_predicate_frame_version_fields",
)
