"""Closed exact Slice 37-to-Slice 38 compatibility snapshot construction."""

from __future__ import annotations

from typing import Iterable

from ...controlled_concept_sense_registry.built_in_registry import (
    built_in_registry,
)
from ...controlled_concept_sense_registry.sense_term_mapping_registry import (
    sense_term_mapping_registry,
)
from ..built_in_action_root_registry import built_in_action_root_registry
from ..predicate_frame_registry import predicate_frame_registry
from .authority import CANONICAL_PROVENANCE_REFS
from .identity import with_expected_id
from .schema import (
    ActionRootCompatibilityConflict,
    ActionRootCompatibilityRule,
    CompatibilityLifecycleState,
    CompatibilityMatchMode,
    CompatibilityRegistrySnapshot,
)


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _concept_by_id(concept_id: str):
    for item in built_in_registry().admitted_concepts:
        if item.concept_id == concept_id:
            return item
    return None


def _sense_by_id(sense_id: str):
    for item in sense_term_mapping_registry().senses:
        if item.sense_id == sense_id:
            return item
    return None


def _root_by_key(action_root_key: str):
    for item in built_in_action_root_registry().admitted_action_roots:
        if item.action_root_key == action_root_key:
            return item
    return None


def _predicate_for_root_id(action_root_id: str):
    for item in built_in_action_root_registry().admitted_predicates:
        if item.action_root_id == action_root_id:
            return item
    return None


def _frames_for_root_id(action_root_id: str):
    return tuple(
        item
        for item in predicate_frame_registry().admitted_frames
        if item.linked_action_root_id == action_root_id
    )


def build_exact_compatibility_rule(
    *,
    rule_key: str,
    action_root_key: str,
    concept_id: str | None = None,
    sense_id: str | None = None,
    allowed_frame_keys: tuple[str, ...] = (),
    scope_tags: tuple[str, ...] = ("slice38g:candidate-proposal",),
    provenance_refs: tuple[str, ...] = CANONICAL_PROVENANCE_REFS,
    conflict_refs: tuple[str, ...] = (),
    version: str = "v1.0.0",
    lifecycle_state: CompatibilityLifecycleState = (
        CompatibilityLifecycleState.ARCHITECTURE_ADMITTED
    ),
) -> ActionRootCompatibilityRule:
    """Build one exact candidate-only compatibility rule.

    This helper resolves only exact governed identities.  It does not perform
    surface matching, semantic similarity, ranking, selection, or authority.
    Validation remains mandatory before a snapshot can be consumed.
    """

    concept = _concept_by_id(concept_id) if concept_id is not None else None
    sense = _sense_by_id(sense_id) if sense_id is not None else None
    root = _root_by_key(action_root_key)

    if root is None:
        raise ValueError(f"unknown admitted action-root key: {action_root_key}")

    predicate = _predicate_for_root_id(root.action_root_id)
    if predicate is None:
        raise ValueError("admitted action root has no exact predicate identity")

    if concept_id is not None and concept is None:
        raise ValueError(f"unknown admitted concept id: {concept_id}")
    if sense_id is not None and sense is None:
        raise ValueError(f"unknown admitted sense id: {sense_id}")
    if concept is None and sense is None:
        raise ValueError("an exact concept id, exact sense id, or both are required")
    if concept is not None and sense is not None and sense.concept_id != concept.concept_id:
        raise ValueError("sense does not belong to the supplied concept")

    if concept is not None and sense is not None:
        match_mode = CompatibilityMatchMode.EXACT_CONCEPT_AND_SENSE
    elif sense is not None:
        match_mode = CompatibilityMatchMode.EXACT_SENSE
    else:
        match_mode = CompatibilityMatchMode.EXACT_CONCEPT

    frames = _frames_for_root_id(root.action_root_id)
    if allowed_frame_keys:
        requested = set(allowed_frame_keys)
        selected = tuple(item for item in frames if item.frame_key in requested)
        if set(item.frame_key for item in selected) != requested:
            raise ValueError("allowed_frame_keys contains an unknown or incompatible frame")
    else:
        selected = frames

    raw = ActionRootCompatibilityRule(
        rule_id="",
        rule_key=rule_key,
        match_mode=match_mode,
        concept_id=concept.concept_id if concept is not None else None,
        concept_version=concept.version if concept is not None else None,
        sense_id=sense.sense_id if sense is not None else None,
        sense_version=sense.version if sense is not None else None,
        action_root_id=root.action_root_id,
        action_root_key=root.action_root_key,
        action_root_version=root.version,
        predicate_id=predicate.predicate_id,
        predicate_key=predicate.predicate_key,
        predicate_version=predicate.version,
        allowed_frame_ids=tuple(item.frame_id for item in selected),
        scope_tags=_unique(scope_tags),
        provenance_refs=_unique(provenance_refs),
        conflict_refs=_unique(conflict_refs),
        version=version,
        lifecycle_state=lifecycle_state,
        candidate_only=True,
        selection_authority=False,
        permission_authority=False,
        route_authority=False,
        execution_authority=False,
    )
    return with_expected_id(raw, "rule_id")


def build_compatibility_conflict(
    *,
    conflict_key: str,
    rules: tuple[ActionRootCompatibilityRule, ...],
    conflict_kind: str,
    reason: str,
    scope_tags: tuple[str, ...] = ("slice38g:candidate-proposal",),
    provenance_refs: tuple[str, ...] = CANONICAL_PROVENANCE_REFS,
    version: str = "v1.0.0",
) -> ActionRootCompatibilityConflict:
    if len(rules) < 2:
        raise ValueError("a conflict requires at least two exact rules")
    raw = ActionRootCompatibilityConflict(
        conflict_id="",
        conflict_key=conflict_key,
        rule_refs=tuple(item.rule_id for item in rules),
        concept_refs=_unique(
            item.concept_id for item in rules if item.concept_id is not None
        ),
        sense_refs=_unique(
            item.sense_id for item in rules if item.sense_id is not None
        ),
        action_root_refs=_unique(item.action_root_id for item in rules),
        conflict_kind=conflict_kind,
        reason=reason,
        scope_tags=_unique(scope_tags),
        provenance_refs=_unique(provenance_refs),
        version=version,
        lifecycle_state=CompatibilityLifecycleState.CONFLICTED,
        operative=False,
        resolved=False,
        selected_rule_ref=None,
    )
    return with_expected_id(raw, "conflict_id")


def build_compatibility_snapshot(
    *,
    rules: tuple[ActionRootCompatibilityRule, ...] = (),
    conflicts: tuple[ActionRootCompatibilityConflict, ...] = (),
    registry_key: str = "slice38g_exact_candidate_compatibility",
    registry_version: str = "v1.0.0",
    provenance_refs: tuple[str, ...] = CANONICAL_PROVENANCE_REFS,
) -> CompatibilityRegistrySnapshot:
    raw = CompatibilityRegistrySnapshot(
        snapshot_id="",
        registry_key=registry_key,
        registry_version=registry_version,
        rule_refs=tuple(item.rule_id for item in rules),
        conflict_refs=tuple(item.conflict_id for item in conflicts),
        rules=rules,
        conflicts=conflicts,
        rule_count=len(rules),
        conflict_count=len(conflicts),
        exact_identity_lookup_only=True,
        closed_world=True,
        runtime_mutation_allowed=False,
        automatic_mapping_allowed=False,
        nearest_known_substitution_allowed=False,
        semantic_similarity_allowed=False,
        language_model_allowed=False,
        selection_authority=False,
        permission_authority=False,
        route_authority=False,
        execution_authority=False,
        provenance_refs=_unique(provenance_refs),
    )
    return with_expected_id(raw, "snapshot_id")


CANONICAL_COMPATIBILITY_SNAPSHOT = build_compatibility_snapshot()
