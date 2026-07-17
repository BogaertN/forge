"""Deterministic exact snapshot of accepted Slice 38 registries."""

from __future__ import annotations

from ..built_in_action_root_registry import built_in_action_root_registry
from ..capability_family_reference_registry import (
    capability_family_reference_registry,
)
from ..participant_role_registry import participant_role_registry
from ..predicate_frame_registry import predicate_frame_registry
from .identity import with_expected_id
from .schema import Slice38RegistrySnapshotIdentity


def _manifest_version(manifest: object) -> str:
    for name in ("version", "spec_version", "schema_version"):
        value = getattr(manifest, name, None)
        if type(value) is str and value:
            return value
    raise ValueError("registry manifest has no exact version identity")


def build_slice38_registry_snapshot() -> Slice38RegistrySnapshotIdentity:
    action_registry = built_in_action_root_registry()
    role_registry = participant_role_registry()
    frame_registry = predicate_frame_registry()
    capability_registry = capability_family_reference_registry()

    raw = Slice38RegistrySnapshotIdentity(
        snapshot_id="",
        action_root_manifest_id=action_registry.manifest.manifest_id,
        action_root_registry_version=_manifest_version(action_registry.manifest),
        action_root_count=len(action_registry.admitted_action_roots),
        predicate_count=len(action_registry.admitted_predicates),
        participant_role_manifest_id=role_registry.manifest.manifest_id,
        participant_role_registry_version=_manifest_version(role_registry.manifest),
        participant_role_count=len(role_registry.admitted_roles),
        predicate_frame_manifest_id=frame_registry.manifest.manifest_id,
        predicate_frame_registry_version=_manifest_version(frame_registry.manifest),
        predicate_frame_count=len(frame_registry.admitted_frames),
        frame_role_constraint_count=len(frame_registry.role_constraints),
        frame_role_concept_compatibility_count=len(frame_registry.compatibility_rules),
        capability_reference_manifest_id=capability_registry.manifest.manifest_id,
        capability_reference_registry_version=_manifest_version(
            capability_registry.manifest
        ),
        effect_boundary_count=len(capability_registry.effect_boundaries),
        capability_family_count=len(capability_registry.capability_families),
        frame_effect_reference_count=len(
            capability_registry.frame_effect_references
        ),
        frame_capability_reference_count=len(
            capability_registry.frame_capability_references
        ),
        exact_snapshot=True,
        external_resources_loaded=False,
        runtime_mutation_allowed=False,
    )
    return with_expected_id(raw, "snapshot_id")
