"""Deterministic Slice 38C registry identity helpers."""

from __future__ import annotations

from dataclasses import replace

from .schema import BuiltInActionRootRegistryManifest


def with_expected_manifest_id(
    manifest: BuiltInActionRootRegistryManifest,
) -> BuiltInActionRootRegistryManifest:
    return replace(manifest, manifest_id=manifest.expected_id())


def registry_digest(registry: object) -> str:
    from .schema import BuiltInActionRootRegistry

    if type(registry) is not BuiltInActionRootRegistry:
        raise TypeError("exact BuiltInActionRootRegistry required")
    return registry.registry_digest()
