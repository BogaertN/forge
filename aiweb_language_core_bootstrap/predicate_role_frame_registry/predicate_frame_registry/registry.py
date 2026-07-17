"""Exact read-only accessors for the Slice 38E predicate-frame registry."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from .records import PREDICATE_FRAME_REGISTRY
from .schema import (
    FrameRoleConstraint,
    FrameStructuralStatePolicy,
    PredicateFrameIdentity,
    PredicateFrameRegistry,
    PredicateFrameRegistryManifest,
    RoleConceptCompatibilityRule,
)


_FRAME_BY_ID: Final = MappingProxyType({item.frame_id: item for item in PREDICATE_FRAME_REGISTRY.admitted_frames})
_FRAME_BY_KEY: Final = MappingProxyType({item.frame_key: item for item in PREDICATE_FRAME_REGISTRY.admitted_frames})
_CONSTRAINT_BY_ID: Final = MappingProxyType({item.constraint_id: item for item in PREDICATE_FRAME_REGISTRY.role_constraints})
_COMPATIBILITY_BY_ID: Final = MappingProxyType({item.compatibility_id: item for item in PREDICATE_FRAME_REGISTRY.compatibility_rules})
_STATE_POLICY_BY_STATE: Final = MappingProxyType({item.state: item for item in PREDICATE_FRAME_REGISTRY.structural_state_policies})


def predicate_frame_registry() -> PredicateFrameRegistry:
    return PREDICATE_FRAME_REGISTRY


def registry_manifest() -> PredicateFrameRegistryManifest:
    return PREDICATE_FRAME_REGISTRY.manifest


def all_admitted_frames() -> tuple[PredicateFrameIdentity, ...]:
    return PREDICATE_FRAME_REGISTRY.admitted_frames


def all_role_constraints() -> tuple[FrameRoleConstraint, ...]:
    return PREDICATE_FRAME_REGISTRY.role_constraints


def all_compatibility_rules() -> tuple[RoleConceptCompatibilityRule, ...]:
    return PREDICATE_FRAME_REGISTRY.compatibility_rules


def all_structural_state_policies() -> tuple[FrameStructuralStatePolicy, ...]:
    return PREDICATE_FRAME_REGISTRY.structural_state_policies


def contains_frame_id(frame_id: object) -> bool:
    if type(frame_id) is not str:
        return False
    return frame_id in _FRAME_BY_ID


def frame_by_id(frame_id: str) -> PredicateFrameIdentity:
    if type(frame_id) is not str:
        raise TypeError("frame_id must be an exact str")
    return _FRAME_BY_ID[frame_id]


def frame_by_key(namespace_id: str, frame_key: str) -> PredicateFrameIdentity:
    if type(namespace_id) is not str or type(frame_key) is not str:
        raise TypeError("namespace_id and frame_key must be exact str values")
    if namespace_id != PREDICATE_FRAME_REGISTRY.current_namespace.namespace_id:
        raise KeyError((namespace_id, frame_key))
    return _FRAME_BY_KEY[frame_key]


def constraint_by_id(constraint_id: str) -> FrameRoleConstraint:
    if type(constraint_id) is not str:
        raise TypeError("constraint_id must be an exact str")
    return _CONSTRAINT_BY_ID[constraint_id]


def compatibility_by_id(compatibility_id: str) -> RoleConceptCompatibilityRule:
    if type(compatibility_id) is not str:
        raise TypeError("compatibility_id must be an exact str")
    return _COMPATIBILITY_BY_ID[compatibility_id]


def structural_state_policy(state: object) -> FrameStructuralStatePolicy:
    return _STATE_POLICY_BY_STATE[state]
