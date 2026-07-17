"""Deterministic identity and version helpers for Slice 38F records."""

from __future__ import annotations

from dataclasses import replace
import re
from typing import TypeVar

from .schema import (
    CapabilityEffectCompatibilityRecord,
    CapabilityFamilyIdentity,
    CapabilityFamilyReferenceRegistryManifest,
    CapabilityReferenceGovernedResource,
    CapabilityReferenceLifecycleAuthorityRecord,
    CapabilityReferenceLifecycleTransitionRecord,
    CapabilityReferenceNamespaceIdentity,
    CapabilityReferenceProvenanceReference,
    EffectBoundaryIdentity,
    FrameCapabilityFamilyReference,
    FrameEffectBoundaryReference,
)


_VERSION = re.compile(r"^v([0-9]+)\.([0-9]+)\.([0-9]+)$")
T = TypeVar("T")


def parse_version(value: object) -> tuple[int, int, int]:
    if type(value) is not str:
        raise TypeError("version must be an exact str")
    match = _VERSION.fullmatch(value)
    if match is None:
        raise ValueError("version must match vMAJOR.MINOR.PATCH")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def version_advances(source: object, target: object) -> bool:
    try:
        return parse_version(target) > parse_version(source)
    except (TypeError, ValueError):
        return False


def record_id(record: object) -> str:
    expected = getattr(record, "expected_id", None)
    if not callable(expected):
        raise TypeError("record must expose expected_id()")
    value = expected()
    if type(value) is not str or not value:
        raise ValueError("expected_id() must return a non-empty str")
    return value


def with_expected_id(record: T) -> T:
    field_by_type = {
        CapabilityReferenceProvenanceReference: "provenance_id",
        CapabilityReferenceNamespaceIdentity: "namespace_id",
        EffectBoundaryIdentity: "effect_boundary_id",
        CapabilityFamilyIdentity: "capability_family_id",
        FrameEffectBoundaryReference: "frame_effect_reference_id",
        FrameCapabilityFamilyReference: "frame_capability_reference_id",
        CapabilityEffectCompatibilityRecord: "compatibility_id",
        CapabilityReferenceLifecycleAuthorityRecord: "authority_id",
        CapabilityReferenceLifecycleTransitionRecord: "transition_id",
        CapabilityFamilyReferenceRegistryManifest: "manifest_id",
    }
    field_name = field_by_type.get(type(record))
    if field_name is None:
        raise TypeError("unsupported Slice 38F record type")
    return replace(record, **{field_name: record_id(record)})


def resource_lineage_body(
    record: CapabilityReferenceGovernedResource,
) -> dict[str, object]:
    body = record.canonical_body()
    body.pop("version", None)
    body.pop("lifecycle_state", None)
    body.pop("provenance_refs", None)
    return body


def expected_lineage_id(record: CapabilityReferenceGovernedResource) -> str:
    from ...schema import stable_record_id

    return stable_record_id(
        "slice38f_capability_reference_lineage",
        resource_lineage_body(record),
    )
