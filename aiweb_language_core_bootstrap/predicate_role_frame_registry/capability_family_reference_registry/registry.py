"""Exact read-only accessors for the Slice 38F registry."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from .records import CAPABILITY_FAMILY_REFERENCE_REGISTRY
from .schema import (
    CapabilityEffectCompatibilityRecord,
    CapabilityFamilyIdentity,
    CapabilityFamilyReferenceRegistry,
    CapabilityFamilyReferenceRegistryManifest,
    EffectBoundaryIdentity,
    FrameCapabilityFamilyReference,
    FrameEffectBoundaryReference,
)


_EFFECT_BY_ID: Final = MappingProxyType(
    {
        item.effect_boundary_id: item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.effect_boundaries
    }
)
_EFFECT_BY_KEY: Final = MappingProxyType(
    {
        (
            CAPABILITY_FAMILY_REFERENCE_REGISTRY.current_namespace.namespace_id,
            item.effect_boundary_key,
        ): item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.effect_boundaries
    }
)
_CAPABILITY_BY_ID: Final = MappingProxyType(
    {
        item.capability_family_id: item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.capability_families
    }
)
_CAPABILITY_BY_KEY: Final = MappingProxyType(
    {
        (
            CAPABILITY_FAMILY_REFERENCE_REGISTRY.current_namespace.namespace_id,
            item.capability_family_key,
        ): item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.capability_families
    }
)
_FRAME_EFFECT_BY_ID: Final = MappingProxyType(
    {
        item.frame_effect_reference_id: item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.frame_effect_references
    }
)
_FRAME_EFFECT_BY_FRAME_ID: Final = MappingProxyType(
    {
        item.frame_id: item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.frame_effect_references
    }
)
_FRAME_CAPABILITY_BY_ID: Final = MappingProxyType(
    {
        item.frame_capability_reference_id: item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.frame_capability_references
    }
)
_FRAME_CAPABILITIES_BY_FRAME_ID: Final = MappingProxyType(
    {
        frame_id: tuple(
            item
            for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.frame_capability_references
            if item.frame_id == frame_id
        )
        for frame_id in {
            item.frame_id
            for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.frame_effect_references
        }
    }
)
_COMPATIBILITY_BY_ID: Final = MappingProxyType(
    {
        item.compatibility_id: item
        for item in CAPABILITY_FAMILY_REFERENCE_REGISTRY.compatibility_records
    }
)


def capability_family_reference_registry() -> CapabilityFamilyReferenceRegistry:
    return CAPABILITY_FAMILY_REFERENCE_REGISTRY


def registry_manifest() -> CapabilityFamilyReferenceRegistryManifest:
    return CAPABILITY_FAMILY_REFERENCE_REGISTRY.manifest


def all_effect_boundaries() -> tuple[EffectBoundaryIdentity, ...]:
    return CAPABILITY_FAMILY_REFERENCE_REGISTRY.effect_boundaries


def all_capability_families() -> tuple[CapabilityFamilyIdentity, ...]:
    return CAPABILITY_FAMILY_REFERENCE_REGISTRY.capability_families


def all_frame_effect_references() -> tuple[FrameEffectBoundaryReference, ...]:
    return CAPABILITY_FAMILY_REFERENCE_REGISTRY.frame_effect_references


def all_frame_capability_references() -> tuple[FrameCapabilityFamilyReference, ...]:
    return CAPABILITY_FAMILY_REFERENCE_REGISTRY.frame_capability_references


def all_compatibility_records() -> tuple[CapabilityEffectCompatibilityRecord, ...]:
    return CAPABILITY_FAMILY_REFERENCE_REGISTRY.compatibility_records


def contains_effect_boundary_id(effect_boundary_id: object) -> bool:
    return type(effect_boundary_id) is str and effect_boundary_id in _EFFECT_BY_ID


def effect_boundary_by_id(effect_boundary_id: str) -> EffectBoundaryIdentity | None:
    if type(effect_boundary_id) is not str:
        return None
    return _EFFECT_BY_ID.get(effect_boundary_id)


def effect_boundary_by_key(
    namespace_id: str,
    effect_boundary_key: str,
) -> EffectBoundaryIdentity | None:
    if type(namespace_id) is not str or type(effect_boundary_key) is not str:
        return None
    return _EFFECT_BY_KEY.get((namespace_id, effect_boundary_key))


def contains_capability_family_id(capability_family_id: object) -> bool:
    return (
        type(capability_family_id) is str
        and capability_family_id in _CAPABILITY_BY_ID
    )


def capability_family_by_id(
    capability_family_id: str,
) -> CapabilityFamilyIdentity | None:
    if type(capability_family_id) is not str:
        return None
    return _CAPABILITY_BY_ID.get(capability_family_id)


def capability_family_by_key(
    namespace_id: str,
    capability_family_key: str,
) -> CapabilityFamilyIdentity | None:
    if type(namespace_id) is not str or type(capability_family_key) is not str:
        return None
    return _CAPABILITY_BY_KEY.get((namespace_id, capability_family_key))


def frame_effect_reference_by_id(
    reference_id: str,
) -> FrameEffectBoundaryReference | None:
    if type(reference_id) is not str:
        return None
    return _FRAME_EFFECT_BY_ID.get(reference_id)


def frame_effect_reference_for_frame(
    frame_id: str,
) -> FrameEffectBoundaryReference | None:
    if type(frame_id) is not str:
        return None
    return _FRAME_EFFECT_BY_FRAME_ID.get(frame_id)


def frame_capability_reference_by_id(
    reference_id: str,
) -> FrameCapabilityFamilyReference | None:
    if type(reference_id) is not str:
        return None
    return _FRAME_CAPABILITY_BY_ID.get(reference_id)


def frame_capability_references_for_frame(
    frame_id: str,
) -> tuple[FrameCapabilityFamilyReference, ...]:
    if type(frame_id) is not str:
        return ()
    return _FRAME_CAPABILITIES_BY_FRAME_ID.get(frame_id, ())


def compatibility_by_id(
    compatibility_id: str,
) -> CapabilityEffectCompatibilityRecord | None:
    if type(compatibility_id) is not str:
        return None
    return _COMPATIBILITY_BY_ID.get(compatibility_id)
