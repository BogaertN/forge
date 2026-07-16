"""Deterministic Slice 37C manifest and registry identity helpers."""

from __future__ import annotations

from dataclasses import replace

from .schema import (
    BuiltInConceptRegistry,
    BuiltInConceptRegistryManifest,
)


def with_expected_manifest_id(
    manifest: BuiltInConceptRegistryManifest,
) -> BuiltInConceptRegistryManifest:
    return replace(
        manifest,
        manifest_id=manifest.expected_id(),
    )


def registry_digest(
    registry: BuiltInConceptRegistry,
) -> str:
    return registry.registry_digest()
