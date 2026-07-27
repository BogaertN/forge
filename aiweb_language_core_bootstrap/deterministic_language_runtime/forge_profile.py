"""Closed, versioned initial Forge English profile for LC-RMC-001."""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Final

from .authority import (
    PROFILE_ID,
    PROFILE_VERSION,
    REFUSAL_INTERNAL_PROFILE_ERROR,
    LanguageRuntimeError,
)


@dataclass(frozen=True, slots=True)
class ActionProfile:
    root: str
    frame_key: str
    object_role_key: str
    phase_primary: str
    speech_act_default: str
    forms: tuple[str, ...]


ACTION_PROFILES: Final[tuple[ActionProfile, ...]] = (
    ActionProfile(
        root="inspect",
        frame_key="inspect_read_only",
        object_role_key="action_subject",
        phase_primary="Φ6",
        speech_act_default="DIRECTIVE",
        forms=("inspect", "inspects", "inspected", "inspecting"),
    ),
    ActionProfile(
        root="report",
        frame_key="report_attributed_content",
        object_role_key="content",
        phase_primary="Φ8",
        speech_act_default="REPORT_REQUEST",
        forms=("report", "reports", "reported", "reporting"),
    ),
    ActionProfile(
        root="request",
        frame_key="request_non_authorizing",
        object_role_key="content",
        phase_primary="Φ3",
        speech_act_default="REQUEST",
        forms=("request", "requests", "requested", "requesting"),
    ),
    ActionProfile(
        root="verify",
        frame_key="verify_bounded_review",
        object_role_key="action_subject",
        phase_primary="Φ6",
        speech_act_default="DIRECTIVE",
        forms=("verify", "verifies", "verified", "verifying"),
    ),
    ActionProfile(
        root="simulate",
        frame_key="simulate_non_live",
        object_role_key="action_subject",
        phase_primary="Φ3",
        speech_act_default="HYPOTHETICAL_REQUEST",
        forms=("simulate", "simulates", "simulated", "simulating"),
    ),
)

ACTION_BY_ROOT: Final = MappingProxyType({item.root: item for item in ACTION_PROFILES})
ACTION_SURFACE_TO_ROOT: Final = MappingProxyType(
    {form: item.root for item in ACTION_PROFILES for form in item.forms}
)

OBJECT_CONCEPTS: Final[tuple[str, ...]] = (
    "build",
    "repository",
    "state",
    "status",
    "test",
    "packet",
    "checksum",
    "manifest",
    "trace",
    "memory",
    "write_plan",
    "audit",
    "result",
)
OBJECT_CONCEPT_SET: Final = frozenset(OBJECT_CONCEPTS)

DETERMINERS: Final = frozenset(("a", "an", "the", "this", "that"))
ADJECTIVES: Final = frozenset(
    (
        "active",
        "applied",
        "current",
        "existing",
        "governed",
        "local",
        "read-only",
        "sealed",
    )
)
SUBJECTS: Final = frozenset(("forge", "i", "operator", "system", "user", "we", "you"))
MODALS: Final = frozenset(("can", "could", "may", "might", "should", "will", "would"))
AUXILIARY_DO: Final = frozenset(("do", "does", "did"))
AUXILIARY_BE: Final = frozenset(("am", "are", "is", "was", "were"))
NEGATION_FORMS: Final = frozenset(("not", "never"))
POLITENESS_FORMS: Final = frozenset(("please",))
TERMINAL_PUNCTUATION: Final = frozenset((".", "?", "!"))
ATTACHMENT_PREPOSITIONS: Final = frozenset(("with",))

CONTRACTION_FEATURES: Final = MappingProxyType(
    {
        "can't": ("can", "modal", "negative"),
        "cannot": ("can", "modal", "negative"),
        "couldn't": ("could", "modal", "negative"),
        "shouldn't": ("should", "modal", "negative"),
        "won't": ("will", "modal", "negative"),
        "wouldn't": ("would", "modal", "negative"),
        "don't": ("do", "auxiliary", "negative"),
        "doesn't": ("does", "auxiliary", "negative"),
        "didn't": ("did", "auxiliary", "negative"),
    }
)

AUTHORITY_IDENTIFIER_PATTERN: Final = re.compile(
    r"(?i)^(?:cand(?:idate)?|meaning|selection)[_:-][a-z0-9][a-z0-9_:-]*$"
)

SEMANTIC_CLASS_BY_CONCEPT: Final = MappingProxyType(
    {
        "build": ("type_or_category_concept",),
        "repository": ("type_or_category_concept",),
        "state": ("state_or_condition_concept",),
        "status": ("state_or_condition_concept",),
        "test": ("type_or_category_concept",),
        "packet": ("expression_representation_communication_concept",),
        "checksum": ("expression_representation_communication_concept",),
        "manifest": ("expression_representation_communication_concept",),
        "trace": ("expression_representation_communication_concept",),
        "memory": ("type_or_category_concept",),
        "write_plan": ("expression_representation_communication_concept",),
        "audit": ("occurrence_event_or_change_concept",),
        "result": ("state_or_condition_concept",),
    }
)


def action_profile(root: str) -> ActionProfile:
    try:
        return ACTION_BY_ROOT[root]
    except KeyError as error:
        raise LanguageRuntimeError(
            REFUSAL_INTERNAL_PROFILE_ERROR,
            "admitted action profile is unavailable",
        ) from error


def resolve_registry_identities(root: str) -> dict[str, str]:
    """Resolve exact accepted registry identities without iterative selection."""

    profile = action_profile(root)
    try:
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.built_in_action_root_registry import (
            action_root_by_key,
            current_namespace as action_namespace,
            predicate_for_action_root_id,
        )
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.participant_role_registry import (
            participant_role_registry,
            role_by_key,
        )
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_frame_registry import (
            predicate_frame_registry,
            frame_by_key,
        )

        action = action_root_by_key(action_namespace().namespace_id, profile.root)
        predicate = predicate_for_action_root_id(action.action_root_id)
        frame_registry = predicate_frame_registry()
        frame = frame_by_key(
            frame_registry.current_namespace.namespace_id,
            profile.frame_key,
        )
        role_registry = participant_role_registry()
        object_role = role_by_key(
            role_registry.current_namespace.namespace_id,
            profile.object_role_key,
        )
        initiator_role = role_by_key(
            role_registry.current_namespace.namespace_id,
            "initiator",
        )
        actor_role = role_by_key(
            role_registry.current_namespace.namespace_id,
            "actor",
        )
        instrument_role = role_by_key(
            role_registry.current_namespace.namespace_id,
            "instrument",
        )
    except (ImportError, AttributeError, KeyError, TypeError) as error:
        raise LanguageRuntimeError(
            REFUSAL_INTERNAL_PROFILE_ERROR,
            "accepted registry identities do not satisfy the LC-RMC-001 profile",
        ) from error

    if frame.linked_action_root_id != action.action_root_id:
        raise LanguageRuntimeError(
            REFUSAL_INTERNAL_PROFILE_ERROR,
            "predicate frame and action-root registry identities conflict",
        )

    return {
        "action_root_id": action.action_root_id,
        "predicate_id": predicate.predicate_id,
        "frame_id": frame.frame_id,
        "frame_key": frame.frame_key,
        "object_role_id": object_role.role_id,
        "object_role_key": object_role.role_key,
        "initiator_role_id": initiator_role.role_id,
        "actor_role_id": actor_role.role_id,
        "instrument_role_id": instrument_role.role_id,
    }


def concept_classes(concept_keys: tuple[str, ...]) -> tuple[str, ...]:
    values: list[str] = []
    for key in concept_keys:
        for semantic_class in SEMANTIC_CLASS_BY_CONCEPT[key]:
            if semantic_class not in values:
                values.append(semantic_class)
    return tuple(values)


def profile_manifest() -> dict[str, object]:
    return {
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "closed_set": True,
        "action_roots": [item.root for item in ACTION_PROFILES],
        "action_forms": {
            item.root: list(item.forms)
            for item in ACTION_PROFILES
        },
        "object_concepts": list(OBJECT_CONCEPTS),
        "determiners": sorted(DETERMINERS),
        "adjectives": sorted(ADJECTIVES),
        "subjects": sorted(SUBJECTS),
        "modals": sorted(MODALS),
        "attachment_prepositions": sorted(ATTACHMENT_PREPOSITIONS),
        "external_resources_loaded": False,
        "nearest_match_allowed": False,
        "spelling_repair_allowed": False,
        "synonym_expansion_allowed": False,
        "registry_iteration_selects_identity": False,
    }


__all__ = (
    "ACTION_BY_ROOT",
    "ACTION_PROFILES",
    "ACTION_SURFACE_TO_ROOT",
    "ADJECTIVES",
    "ATTACHMENT_PREPOSITIONS",
    "AUTHORITY_IDENTIFIER_PATTERN",
    "AUXILIARY_BE",
    "AUXILIARY_DO",
    "CONTRACTION_FEATURES",
    "DETERMINERS",
    "MODALS",
    "NEGATION_FORMS",
    "OBJECT_CONCEPTS",
    "OBJECT_CONCEPT_SET",
    "POLITENESS_FORMS",
    "SUBJECTS",
    "TERMINAL_PUNCTUATION",
    "ActionProfile",
    "action_profile",
    "concept_classes",
    "profile_manifest",
    "resolve_registry_identities",
)
