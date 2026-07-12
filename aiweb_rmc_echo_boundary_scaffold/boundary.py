"""Boundary statements for Slice 19 RMC Echo.

RMC Echo is represented here as a later, separate authority layer. This file
contains no Echo validator implementation and no delivery or release route.
"""

from __future__ import annotations

from .core import (
    BoundaryItem,
    ECHO_RELATIONSHIP,
    IMPLEMENTATION_STATE,
    SCAFFOLD_VERSION,
    SLICE_ID,
    SLICE_TITLE,
)

BOUNDARY_STATEMENTS: tuple[BoundaryItem, ...] = (
    BoundaryItem(
        key="echo_validation_not_implemented",
        allowed=False,
        statement="RMC Echo validation is not implemented by Slice 19.",
        reason="Language and expression scaffolds do not automatically create Echo validation.",
    ),
    BoundaryItem(
        key="echo_not_delivery",
        allowed=False,
        statement="Echo validation is not delivery.",
        reason="Delivery remains a separate downstream authority and transport concern.",
    ),
    BoundaryItem(
        key="echo_not_public_release",
        allowed=False,
        statement="Echo validation is not public release.",
        reason="Public release requires a later explicit release authority path.",
    ),
    BoundaryItem(
        key="echo_not_output_approval",
        allowed=False,
        statement="Echo validation is not output approval.",
        reason="A validation layer cannot approve output by existing as a scaffold.",
    ),
    BoundaryItem(
        key="echo_not_renderer_authority",
        allowed=False,
        statement="Echo validation is not renderer authority.",
        reason="Rendering remains outside this scaffold and does not become Echo validation.",
    ),
    BoundaryItem(
        key="echo_not_selected_meaning_authority",
        allowed=False,
        statement="Echo validation is not selected-meaning authority.",
        reason="Selected meaning remains bounded by prior meaning-boundary rules.",
    ),
    BoundaryItem(
        key="echo_not_source_authority",
        allowed=False,
        statement="Echo validation is not source authority.",
        reason="Sources are not made authoritative by an Echo boundary declaration.",
    ),
    BoundaryItem(
        key="echo_not_predicate_authority",
        allowed=False,
        statement="Echo validation is not predicate authority.",
        reason="Predicate authority is not granted or broadened by this scaffold.",
    ),
    BoundaryItem(
        key="echo_not_concept_authority",
        allowed=False,
        statement="Echo validation is not concept authority.",
        reason="Concept authority remains outside this boundary scaffold.",
    ),
    BoundaryItem(
        key="echo_not_gp014",
        allowed=False,
        statement="Echo validation is not GP-014.",
        reason="GP-014 remains preserved as a bounded mathematical-output expression baseline.",
    ),
    BoundaryItem(
        key="echo_not_gp015_repair",
        allowed=False,
        statement="Echo validation is not GP-015 repair.",
        reason="GP-015 remains failed unless repaired by a later explicit repair slice.",
    ),
    BoundaryItem(
        key="echo_not_production_integration",
        allowed=False,
        statement="Echo validation is not production integration.",
        reason="Production integration requires later explicit integration authorization.",
    ),
)

_ALLOWED_BOUNDARY_KEYS = {item.key for item in BOUNDARY_STATEMENTS}


def boundary_keys() -> tuple[str, ...]:
    """Return boundary keys in deterministic order."""

    return tuple(item.key for item in BOUNDARY_STATEMENTS)


def build_boundary_report() -> dict[str, object]:
    """Build a deterministic boundary report.

    The report describes a later authority layer. It does not validate, deliver,
    render, approve, release, or integrate output.
    """

    return {
        "slice": SLICE_ID,
        "title": SLICE_TITLE,
        "version": SCAFFOLD_VERSION,
        "implementation_state": IMPLEMENTATION_STATE,
        "relationship": ECHO_RELATIONSHIP,
        "boundary_statement_count": len(BOUNDARY_STATEMENTS),
        "boundary_keys": list(boundary_keys()),
        "statements": [item.to_dict() for item in BOUNDARY_STATEMENTS],
    }


def validate_boundary_report(report: dict[str, object]) -> tuple[str, ...]:
    """Return validation errors for a boundary report.

    An empty tuple means the report preserves the Slice 19 boundary.
    """

    failures: list[str] = []

    if report.get("slice") != SLICE_ID:
        failures.append("slice id mismatch")
    if report.get("title") != SLICE_TITLE:
        failures.append("slice title mismatch")
    if report.get("implementation_state") != IMPLEMENTATION_STATE:
        failures.append("implementation state mismatch")
    if report.get("relationship") != ECHO_RELATIONSHIP:
        failures.append("relationship mismatch")

    keys = report.get("boundary_keys")
    if keys != list(boundary_keys()):
        failures.append("boundary key ordering mismatch")

    statements = report.get("statements")
    if not isinstance(statements, list):
        failures.append("statements are missing")
        return tuple(failures)

    seen_keys: set[str] = set()
    for entry in statements:
        if not isinstance(entry, dict):
            failures.append("statement entry is not a dict")
            continue
        key = entry.get("key")
        seen_keys.add(str(key))
        if key not in _ALLOWED_BOUNDARY_KEYS:
            failures.append(f"unexpected boundary key: {key}")
        if entry.get("allowed") is not False:
            failures.append(f"boundary item is not denied: {key}")
        statement = str(entry.get("statement", ""))
        if "not" not in statement.lower():
            failures.append(f"boundary statement does not explicitly deny authority: {key}")

    missing = _ALLOWED_BOUNDARY_KEYS - seen_keys
    if missing:
        failures.append("missing boundary keys: " + ", ".join(sorted(missing)))

    return tuple(failures)
