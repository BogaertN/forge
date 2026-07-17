"""Construct the closed immutable Slice 38E predicate-frame registry."""

from __future__ import annotations

from dataclasses import replace
from typing import Final

from ...controlled_concept_sense_registry.semantic_class_relation_registry import (
    SEMANTIC_CLASS_RELATION_REGISTRY,
)
from ..built_in_action_root_registry import BUILT_IN_ACTION_ROOT_REGISTRY
from ..participant_role_registry import PARTICIPANT_ROLE_REGISTRY
from .authority import (
    ADMITTED_PREDICATE_FRAME_KEYS,
    FRAME_DEFINITIONS,
    SLICE38E_AUTHORITY_LIMITATIONS,
    STRUCTURAL_STATE_DEFINITIONS,
)
from .identity import expected_lineage_id, with_expected_id
from .schema import (
    FrameCapabilityReferenceStatus,
    FrameRoleRequirement,
    FrameStructuralStatePolicy,
    PredicateFrameIdentity,
    PredicateFrameLifecycleAuthorityRecord,
    PredicateFrameLifecycleState,
    PredicateFrameLifecycleTransitionRecord,
    PredicateFrameNamespaceIdentity,
    PredicateFrameProvenanceReference,
    PredicateFrameRegistry,
    PredicateFrameRegistryManifest,
    PredicateFrameStructuralState,
    PredicateFrameTransitionKind,
    RoleConceptCompatibilityMode,
    RoleConceptCompatibilityRule,
    FrameRoleConstraint,
)


_ACTION_ROOT_BY_KEY = {
    item.action_root_key: item
    for item in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_action_roots
}
_PREDICATE_BY_KEY = {
    item.predicate_key: item
    for item in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates
}
_ROLE_BY_KEY = {
    item.role_key: item
    for item in PARTICIPANT_ROLE_REGISTRY.admitted_roles
}
_CLASS_BY_KEY = {
    item.class_key: item
    for item in SEMANTIC_CLASS_RELATION_REGISTRY.semantic_classes
}


PROVENANCE_RECORDS: Final[tuple[PredicateFrameProvenanceReference, ...]] = tuple(
    with_expected_id(record)
    for record in (
        PredicateFrameProvenanceReference(
            provenance_id="",
            authority_document="AI.Web Forge Canonical Production Roadmap v1.0",
            authority_section="Slice 38E — Predicate-Frame Constraints and Role Compatibility",
            source_kind="canonical_roadmap",
            source_reference="Google Drive canonical roadmap inspected before patch construction",
            version="v1.0.0",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=True,
            prohibited_authorities=SLICE38E_AUTHORITY_LIMITATIONS,
        ),
        PredicateFrameProvenanceReference(
            provenance_id="",
            authority_document="RMC Predicate–Role Frame Registry v1",
            authority_section="Sections 39, 41, 42 and 43",
            source_kind="permanent_architecture_authority",
            source_reference=(
                "Document 5 frame-role relationship, frame identity, speech-act, effect-boundary, "
                "unknown-state, versioning, provenance and non-permission law"
            ),
            version="v1.0.0",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=True,
            prohibited_authorities=SLICE38E_AUTHORITY_LIMITATIONS,
        ),
        PredicateFrameProvenanceReference(
            provenance_id="",
            authority_document="Accepted live Forge predecessor chain",
            authority_section="Slices 37E, 38C and 38D",
            source_kind="committed_predecessor_source",
            source_reference=(
                "Exact admitted semantic classes, action roots, predicate identities and participant-role identities "
                "from the protected parent tree"
            ),
            version="v1.0.0",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=True,
            prohibited_authorities=SLICE38E_AUTHORITY_LIMITATIONS,
        ),
    )
)
PROVENANCE_REFS: Final[tuple[str, ...]] = tuple(item.provenance_id for item in PROVENANCE_RECORDS)


CURRENT_NAMESPACE: Final[PredicateFrameNamespaceIdentity] = with_expected_id(
    PredicateFrameNamespaceIdentity(
        namespace_id="",
        namespace_key="aiweb_predicate_frame_registry",
        preferred_label="AI.Web Predicate-Frame Registry",
        definition=(
            "The closed Forge-owned namespace for architecture-level predicate frames, frame-role "
            "constraints, exact concept-compatibility requirements, and structural-state policies."
        ),
        scope=(
            "namespace:aiweb:language-core:predicate-role-frame:predicate-frame-registry",
            "slice:38e",
            "layer:architecture-only",
            "identity:exact-and-versioned",
        ),
        non_scope=(
            "source-term lookup", "occurrence interpretation", "role assignment", "frame selection",
            "gate outcome", "capability reference population", "route registration", "execution",
            "evidence validation", "memory", "rendering", "delivery",
        ),
        version="v1.1.0",
        lifecycle_state=PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
        provenance_refs=PROVENANCE_REFS,
        permitted_uses=(
            "exact frame identity lookup",
            "inspection of static frame-role constraints",
            "inspection of structural-state and concept-compatibility policy",
        ),
        prohibited_uses=SLICE38E_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown or unsupported frame material remains explicit and cannot be converted to the nearest admitted frame."
        ),
    )
)


COMPATIBILITY_RULES_LIST: list[RoleConceptCompatibilityRule] = []
ROLE_CONSTRAINTS_LIST: list[FrameRoleConstraint] = []
FRAME_HISTORIES_LIST: list[tuple[PredicateFrameIdentity, ...]] = []
CURRENT_FRAMES_LIST: list[PredicateFrameIdentity] = []

for frame_definition in FRAME_DEFINITIONS:
    action_root = _ACTION_ROOT_BY_KEY[frame_definition.action_root_key]
    predicate = _PREDICATE_BY_KEY[frame_definition.action_root_key]
    frame_compatibilities: list[RoleConceptCompatibilityRule] = []
    frame_constraints: list[FrameRoleConstraint] = []

    for definition in frame_definition.role_constraints:
        role = _ROLE_BY_KEY[definition.role_key]
        compatibility = with_expected_id(
            RoleConceptCompatibilityRule(
                compatibility_id="",
                frame_key=frame_definition.frame_key,
                role_id=role.role_id,
                role_key=role.role_key,
                mode=RoleConceptCompatibilityMode.EXACT_ADMITTED_SUPPORT_REQUIRED,
                allowed_concept_refs=(),
                allowed_semantic_class_refs=tuple(
                    _CLASS_BY_KEY[key].semantic_class_id
                    for key in definition.allowed_semantic_class_keys
                ),
                prohibited_concept_refs=(),
                semantic_class_membership_sufficient=False,
                exact_concept_allowlist_required=True,
                unknown_if_exact_support_absent=True,
                external_only_support_allowed=False,
                quarantined_support_allowed=False,
                similarity_support_allowed=False,
                occurrence_assignment_allowed=False,
                scope=(
                    f"frame:{frame_definition.frame_key}",
                    f"role:{role.role_key}",
                    "compatibility:architecture-review-only",
                ),
                non_scope=(
                    "occurrence concept assignment",
                    "sense selection",
                    "semantic-class membership as sufficient compatibility",
                    "similarity fallback",
                    "external-only support",
                ),
                version="v1.1.0",
                lifecycle_state=PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
                provenance_refs=PROVENANCE_REFS,
            )
        )
        frame_compatibilities.append(compatibility)
        COMPATIBILITY_RULES_LIST.append(compatibility)

    compatibility_by_role = {
        item.role_key: item
        for item in frame_compatibilities
    }

    for definition in frame_definition.role_constraints:
        role = _ROLE_BY_KEY[definition.role_key]
        constraint = with_expected_id(
            FrameRoleConstraint(
                constraint_id="",
                frame_key=frame_definition.frame_key,
                role_id=role.role_id,
                role_key=role.role_key,
                requirement=definition.requirement,
                cardinality=definition.cardinality,
                condition_key=definition.condition_key,
                co_required_role_ids=tuple(
                    _ROLE_BY_KEY[key].role_id
                    for key in definition.co_required_role_keys
                ),
                conflicting_role_ids=tuple(
                    _ROLE_BY_KEY[key].role_id
                    for key in definition.conflicting_role_keys
                ),
                concept_compatibility_ref=compatibility_by_role[role.role_key].compatibility_id,
                scope=(
                    f"frame:{frame_definition.frame_key}",
                    f"role:{role.role_key}",
                    f"requirement:{definition.requirement.value}",
                ),
                non_scope=(
                    "occurrence role assignment",
                    "candidate meaning construction",
                    "gate outcome",
                    "capability argument",
                    "permission or execution",
                ),
                version="v1.1.0",
                lifecycle_state=PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
                provenance_refs=PROVENANCE_REFS,
                occurrence_assignment_allowed=False,
                gate_outcome_created=False,
                authority_satisfied=False,
                capability_argument_created=False,
                execution_authorized=False,
            )
        )
        frame_constraints.append(constraint)
        ROLE_CONSTRAINTS_LIST.append(constraint)

    refs_by_requirement = {
        requirement: tuple(
            item.constraint_id
            for item in frame_constraints
            if item.requirement is requirement
        )
        for requirement in FrameRoleRequirement
    }
    cardinality_refs = tuple(item.constraint_id for item in frame_constraints)
    co_refs = tuple(
        item.constraint_id
        for item in frame_constraints
        if item.co_required_role_ids
    )
    conflict_refs = tuple(
        item.constraint_id
        for item in frame_constraints
        if item.conflicting_role_ids
        or item.requirement is FrameRoleRequirement.PROHIBITED
    )
    compatibility_refs = tuple(item.compatibility_id for item in frame_compatibilities)

    candidate = with_expected_id(
        PredicateFrameIdentity(
            frame_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            frame_key=frame_definition.frame_key,
            preferred_label=frame_definition.label,
            definition=frame_definition.definition,
            linked_action_root_id=action_root.action_root_id,
            linked_action_root_key=action_root.action_root_key,
            linked_predicate_id=predicate.predicate_id,
            linked_predicate_key=predicate.predicate_key,
            purpose=frame_definition.purpose,
            scope=(
                f"frame:{frame_definition.frame_key}",
                f"action-root:{action_root.action_root_key}",
                "layer:predicate-frame-architecture",
            ),
            non_scope=frame_definition.non_scope + (
                "source occurrence frame selection",
                "occurrence role assignment",
                "gate outcome",
                "capability reference population",
                "execution",
            ),
            version="v1.0.0",
            lifecycle_state=PredicateFrameLifecycleState.CANDIDATE,
            provenance_refs=PROVENANCE_REFS,
            required_role_constraint_refs=refs_by_requirement[FrameRoleRequirement.REQUIRED],
            optional_role_constraint_refs=refs_by_requirement[FrameRoleRequirement.OPTIONAL],
            prohibited_role_constraint_refs=refs_by_requirement[FrameRoleRequirement.PROHIBITED],
            conditional_role_constraint_refs=refs_by_requirement[FrameRoleRequirement.CONDITIONAL],
            role_cardinality_constraint_refs=cardinality_refs,
            role_co_requirement_refs=co_refs,
            role_conflict_refs=conflict_refs,
            role_concept_compatibility_refs=compatibility_refs,
            permitted_speech_acts=frame_definition.permitted_speech_acts,
            scope_constraint_refs=frame_definition.scope_constraints,
            effect_classification=frame_definition.effect_classification,
            authority_dependencies=frame_definition.authority_dependencies,
            evidence_boundaries=(
                "frame identity does not validate evidence",
                "reported source or result does not become proof",
            ),
            memory_boundaries=(
                "frame identity does not read write correct delete or persist memory",
            ),
            delivery_boundaries=(
                "recipient or output target does not authorize delivery publication or release",
            ),
            runtime_boundaries=(
                "frame identity does not install modify execute simulate live or prove runtime state",
            ),
            external_resource_boundaries=(
                "external resource relevance does not admit or load an external resource",
            ),
            capability_reference_status=FrameCapabilityReferenceStatus.DEFERRED_TO_SLICE38F,
            capability_reference_refs=(),
            unknown_frame_policy="Unknown frame conditions remain explicit and non-operative.",
            incomplete_frame_policy="Missing required or triggered conditional support remains structurally incomplete.",
            ambiguous_frame_policy="Competing frame structures remain preserved without ranking or selection.",
            conflicted_frame_policy="Prohibited or incompatible structure remains conflicted without automatic refusal.",
            unsupported_frame_policy="Unsupported structure remains first-class and does not fall back to a known frame.",
            structurally_complete_is_permission=False,
            occurrence_frame_selection_allowed=False,
            occurrence_role_assignment_allowed=False,
            frame_completion_allowed=False,
            capability_binding_allowed=False,
            gate_outcome_created=False,
            execution_authorized=False,
        )
    )
    current = replace(
        candidate,
        version="v1.1.0",
        lifecycle_state=PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
    )
    current = replace(current, frame_id=current.expected_id())
    FRAME_HISTORIES_LIST.append((candidate, current))
    CURRENT_FRAMES_LIST.append(current)


ROLE_CONSTRAINTS: Final[tuple[FrameRoleConstraint, ...]] = tuple(ROLE_CONSTRAINTS_LIST)
COMPATIBILITY_RULES: Final[tuple[RoleConceptCompatibilityRule, ...]] = tuple(COMPATIBILITY_RULES_LIST)
FRAME_HISTORIES: Final[tuple[tuple[PredicateFrameIdentity, ...], ...]] = tuple(FRAME_HISTORIES_LIST)
ADMITTED_FRAMES: Final[tuple[PredicateFrameIdentity, ...]] = tuple(CURRENT_FRAMES_LIST)


STRUCTURAL_STATE_POLICIES: Final[tuple[FrameStructuralStatePolicy, ...]] = tuple(
    with_expected_id(
        FrameStructuralStatePolicy(
            policy_id="",
            state=PredicateFrameStructuralState(state),
            definition=definition,
            trigger_conditions=triggers,
            preserved_obligations=(
                "preserve exact frame and role ancestry",
                "preserve speech-act scope negation condition and attribution",
                "preserve external authority dependencies",
            ),
            prohibited_consequences=prohibited,
            gate_outcome_created=False,
            permission_created=False,
            capability_binding_created=False,
            execution_authorized=False,
            version="v1.1.0",
            lifecycle_state=PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
            provenance_refs=PROVENANCE_REFS,
        )
    )
    for state, definition, triggers, prohibited in STRUCTURAL_STATE_DEFINITIONS
)


ADMISSION_AUTHORITY: Final[PredicateFrameLifecycleAuthorityRecord] = with_expected_id(
    PredicateFrameLifecycleAuthorityRecord(
        authority_id="",
        authority_key="slice38e_architecture_admission",
        decision_owner="Nicholas Jacob Bogaert / AI.Web",
        authority_basis=(
            "Canonical Slice 38E roadmap increment",
            "Document 5 Sections 39 41 42 and 43",
            "accepted Slice 38C action-root registry",
            "accepted Slice 38D participant-role registry",
        ),
        approved_scope=(
            "five closed architecture-level predicate frames",
            "static role requirement cardinality co-requirement conflict and compatibility policy",
            "six structural-state policies",
        ),
        prohibited_scope=SLICE38E_AUTHORITY_LIMITATIONS,
        human_approval=True,
        non_llm_decision=True,
        automatic_transition_allowed=False,
        implementation_authorized=True,
        capability_authorized=False,
        action_authorized=False,
        version="v1.0.0",
        lifecycle_state=PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
        provenance_refs=PROVENANCE_REFS,
    )
)


TRANSITIONS: Final[tuple[PredicateFrameLifecycleTransitionRecord, ...]] = tuple(
    with_expected_id(
        PredicateFrameLifecycleTransitionRecord(
            transition_id="",
            frame_lineage_id=expected_lineage_id(history[1]),
            source_frame_id=history[0].frame_id,
            target_frame_id=history[1].frame_id,
            source_version=history[0].version,
            target_version=history[1].version,
            from_state=history[0].lifecycle_state,
            to_state=history[1].lifecycle_state,
            transition_kind=PredicateFrameTransitionKind.ARCHITECTURE_ADMIT,
            reason="Human-approved Slice 38E architecture admission within the closed frame registry.",
            scope=(f"frame:{history[1].frame_key}", "transition:architecture-admission"),
            non_scope=("runtime deployment", "frame selection", "role assignment", "capability binding", "execution"),
            provenance_refs=PROVENANCE_REFS,
            authority_record_ref=ADMISSION_AUTHORITY.authority_id,
            human_approval=True,
            prior_record_preserved=True,
            automatic_transition=False,
            in_place_mutation_performed=False,
            frame_selection_performed=False,
            role_assignment_performed=False,
            capability_binding_performed=False,
            gate_outcome_created=False,
            runtime_authority_supplied=False,
        )
    )
    for history in FRAME_HISTORIES
)


MANIFEST_PLACEHOLDER = PredicateFrameRegistryManifest(
    manifest_id="",
    registry_id="slice38e_predicate_frame_registry",
    namespace_id=CURRENT_NAMESPACE.namespace_id,
    frame_refs=tuple(item.frame_id for item in ADMITTED_FRAMES),
    frame_keys=ADMITTED_PREDICATE_FRAME_KEYS,
    role_constraint_refs=tuple(item.constraint_id for item in ROLE_CONSTRAINTS),
    compatibility_refs=tuple(item.compatibility_id for item in COMPATIBILITY_RULES),
    structural_state_policy_refs=tuple(item.policy_id for item in STRUCTURAL_STATE_POLICIES),
    transition_refs=tuple(item.transition_id for item in TRANSITIONS),
    provenance_refs=PROVENANCE_REFS,
    admitted_frame_count=len(ADMITTED_FRAMES),
    role_constraint_count=len(ROLE_CONSTRAINTS),
    compatibility_rule_count=len(COMPATIBILITY_RULES),
    structural_state_policy_count=len(STRUCTURAL_STATE_POLICIES),
    transition_count=len(TRANSITIONS),
    active_correction_count=0,
    active_conflict_count=0,
    source_term_lookup_installed=False,
    occurrence_frame_selection_installed=False,
    occurrence_role_assignment_installed=False,
    candidate_meaning_creation_installed=False,
    selected_meaning_installed=False,
    gate_outcome_installed=False,
    capability_reference_population_installed=False,
    capability_routing_installed=False,
    route_registration_installed=False,
    tool_activation_installed=False,
    action_execution_installed=False,
    evidence_validation_installed=False,
    memory_access_installed=False,
    rendering_installed=False,
    delivery_installed=False,
    external_resource_loading_installed=False,
    nearest_known_frame_substitution_installed=False,
    semantic_similarity_installed=False,
    llm_authority_installed=False,
    registry_read_only=True,
    registry_closed=True,
    exact_identity_lookup_only=True,
    version="v1.1.0",
    lifecycle_state=PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
    provenance_refs_manifest=PROVENANCE_REFS,
)
MANIFEST: Final[PredicateFrameRegistryManifest] = with_expected_id(MANIFEST_PLACEHOLDER)


PREDICATE_FRAME_REGISTRY: Final[PredicateFrameRegistry] = PredicateFrameRegistry(
    manifest=MANIFEST,
    current_namespace=CURRENT_NAMESPACE,
    admitted_frames=ADMITTED_FRAMES,
    frame_histories=FRAME_HISTORIES,
    role_constraints=ROLE_CONSTRAINTS,
    compatibility_rules=COMPATIBILITY_RULES,
    structural_state_policies=STRUCTURAL_STATE_POLICIES,
    authority_records=(ADMISSION_AUTHORITY,),
    transitions=TRANSITIONS,
    provenance_records=PROVENANCE_RECORDS,
)
