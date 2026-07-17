"""Construct the closed immutable Slice 38F reference registry."""

from __future__ import annotations

from dataclasses import replace
from typing import Final

from ...schema import stable_record_id
from ..predicate_frame_registry import PREDICATE_FRAME_REGISTRY
from ..predicate_frame_registry.schema import FrameEffectClassification
from .authority import (
    ADMITTED_CAPABILITY_FAMILY_KEYS,
    ADMITTED_EFFECT_BOUNDARY_KEYS,
    CAPABILITY_FAMILY_DEFINITIONS,
    DEFERRED_CAPABILITY_FAMILY_KEYS,
    EFFECT_BOUNDARY_DEFINITIONS,
    FRAME_CAPABILITY_DEFINITIONS,
    FRAME_EFFECT_DEFINITIONS,
    FRAMES_WITHOUT_CAPABILITY_REFERENCE,
    SLICE38F_AUTHORITY_LIMITATIONS,
    UNBOUND_CAPABILITY_FAMILY_KEYS,
)
from .identity import expected_lineage_id, with_expected_id
from .schema import (
    CapabilityAvailabilityStatus,
    CapabilityEffectCompatibilityRecord,
    CapabilityFamilyIdentity,
    CapabilityFamilyReferenceRegistry,
    CapabilityFamilyReferenceRegistryManifest,
    CapabilityReferenceLifecycleAuthorityRecord,
    CapabilityReferenceLifecycleState,
    CapabilityReferenceLifecycleTransitionRecord,
    CapabilityReferenceNamespaceIdentity,
    CapabilityReferenceProvenanceReference,
    CapabilityReferenceTransitionKind,
    EffectBoundaryIdentity,
    FrameCapabilityFamilyReference,
    FrameEffectBoundaryReference,
)


_FRAME_BY_KEY = {
    frame.frame_key: frame
    for frame in PREDICATE_FRAME_REGISTRY.admitted_frames
}

_EXPECTED_FRAME_EFFECT_MAP: Final[dict[str, FrameEffectClassification]] = {
    "inspect_read_only": FrameEffectClassification.READ_ONLY,
    "report_attributed_content": FrameEffectClassification.COMMUNICATIVE_ONLY,
    "request_non_authorizing": FrameEffectClassification.NO_ACTION,
    "verify_bounded_review": FrameEffectClassification.VERIFICATION_REVIEW_ONLY,
    "simulate_non_live": FrameEffectClassification.SIMULATION_ONLY,
}

if set(_FRAME_BY_KEY) != set(_EXPECTED_FRAME_EFFECT_MAP):
    raise RuntimeError("Slice 38F requires the exact admitted Slice 38E frame set")

for _frame_key, _expected_effect in _EXPECTED_FRAME_EFFECT_MAP.items():
    if _FRAME_BY_KEY[_frame_key].effect_classification is not _expected_effect:
        raise RuntimeError(f"Slice 38E effect mismatch for {_frame_key}")


PROVENANCE_RECORDS: Final[tuple[CapabilityReferenceProvenanceReference, ...]] = tuple(
    with_expected_id(record)
    for record in (
        CapabilityReferenceProvenanceReference(
            provenance_id="",
            authority_document="AI.Web Forge Canonical Production Roadmap v1.0",
            authority_section=(
                "Slice 38F — Capability-Family References and Effect Boundaries"
            ),
            source_kind="canonical_roadmap",
            source_reference=(
                "Google Drive canonical roadmap inspected before Slice 38F patch construction"
            ),
            version="v1.0.0",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=True,
            prohibited_authorities=SLICE38F_AUTHORITY_LIMITATIONS,
        ),
        CapabilityReferenceProvenanceReference(
            provenance_id="",
            authority_document="RMC Predicate–Role Frame Registry v1",
            authority_section="Sections 43, 44 and 45",
            source_kind="permanent_architecture_authority",
            source_reference=(
                "Document 5 effect-boundary classification, capability-family binding-reference, "
                "capability-effect mode, non-invocation, provenance, versioning, safe-failure and "
                "implementation-deferral law"
            ),
            version="v1.0.0",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=True,
            prohibited_authorities=SLICE38F_AUTHORITY_LIMITATIONS,
        ),
        CapabilityReferenceProvenanceReference(
            provenance_id="",
            authority_document="Accepted live Forge predecessor chain",
            authority_section="Slices 38C, 38D and 38E",
            source_kind="committed_predecessor_source",
            source_reference=(
                "Exact admitted action-root, predicate, participant-role and predicate-frame "
                "identities from the protected Slice 38E parent tree"
            ),
            version="v1.0.0",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=True,
            prohibited_authorities=SLICE38F_AUTHORITY_LIMITATIONS,
        ),
        CapabilityReferenceProvenanceReference(
            provenance_id="",
            authority_document="Accepted GP-014 preservation boundary",
            authority_section="Slice 18 and protected predecessor state",
            source_kind="accepted_bounded_baseline",
            source_reference=(
                "GP-014 remains protected only as the bounded mathematical-output expression baseline; "
                "no general-language, routing, proof or supersession authority is imported"
            ),
            version="v1.0.0",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=True,
            prohibited_authorities=SLICE38F_AUTHORITY_LIMITATIONS,
        ),
    )
)

PROVENANCE_REFS: Final[tuple[str, ...]] = tuple(
    record.provenance_id
    for record in PROVENANCE_RECORDS
)


CURRENT_NAMESPACE: Final[CapabilityReferenceNamespaceIdentity] = with_expected_id(
    CapabilityReferenceNamespaceIdentity(
        namespace_id="",
        namespace_key="aiweb_capability_family_reference_registry",
        preferred_label="AI.Web Capability-Family Reference Registry",
        definition=(
            "The closed Forge-owned namespace for architecture-only effect boundaries, capability-family "
            "identities, frame effect references, and non-operational capability relevance references."
        ),
        scope=(
            "namespace:aiweb:language-core:predicate-role-frame:capability-family-reference-registry",
            "slice:38f",
            "layer:architecture-only",
            "identity:exact-and-versioned",
        ),
        non_scope=(
            "capability availability registry",
            "route registry",
            "invocation registry",
            "argument construction",
            "tool binding",
            "execution",
            "evidence validation",
            "memory operations",
            "delivery",
            "external-resource admission",
            "implementation",
        ),
        version="v1.1.0",
        lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
        provenance_refs=PROVENANCE_REFS,
        permitted_uses=(
            "exact effect-boundary identity lookup",
            "exact capability-family identity lookup",
            "inspection of static frame effect and capability relevance references",
            "inspection of explicit non-operational authority dependencies",
        ),
        prohibited_uses=SLICE38F_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown, unsupported, ambiguous, conflicted or deferred capability relevance remains explicit "
            "and cannot be replaced by the nearest known family, a default route, or a guessed invocation."
        ),
    )
)


EFFECT_BOUNDARY_HISTORIES_LIST: list[tuple[EffectBoundaryIdentity, ...]] = []
CURRENT_EFFECT_BOUNDARIES_LIST: list[EffectBoundaryIdentity] = []

for definition in EFFECT_BOUNDARY_DEFINITIONS:
    current = with_expected_id(
        EffectBoundaryIdentity(
            effect_boundary_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            effect_boundary_key=definition.key,
            preferred_label=definition.label,
            effect_class=definition.effect_class,
            definition=definition.definition,
            scope=definition.scope,
            non_scope=definition.non_scope,
            allowed_consequence_descriptions=definition.allowed_consequence_descriptions,
            prohibited_escalations=definition.prohibited_escalations,
            authority_dependencies=definition.authority_dependencies,
            unknown_state_policy=definition.unknown_state_policy,
            version="v1.1.0",
            lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            provenance_refs=PROVENANCE_REFS,
            permission_satisfied=False,
            capability_available=False,
            route_resolved=False,
            capability_invoked=False,
            execution_performed=False,
            evidence_validated=False,
            memory_authority_supplied=False,
            delivery_authorized=False,
            external_resource_admitted=False,
            implementation_performed=False,
        )
    )
    candidate = with_expected_id(
        replace(
            current,
            effect_boundary_id="",
            version="v1.0.0",
            lifecycle_state=CapabilityReferenceLifecycleState.CANDIDATE,
        )
    )
    EFFECT_BOUNDARY_HISTORIES_LIST.append((candidate, current))
    CURRENT_EFFECT_BOUNDARIES_LIST.append(current)

EFFECT_BOUNDARY_HISTORIES: Final[
    tuple[tuple[EffectBoundaryIdentity, ...], ...]
] = tuple(EFFECT_BOUNDARY_HISTORIES_LIST)

EFFECT_BOUNDARIES: Final[tuple[EffectBoundaryIdentity, ...]] = tuple(
    CURRENT_EFFECT_BOUNDARIES_LIST
)

_EFFECT_BY_KEY = {
    boundary.effect_boundary_key: boundary
    for boundary in EFFECT_BOUNDARIES
}

if tuple(_EFFECT_BY_KEY) != ADMITTED_EFFECT_BOUNDARY_KEYS:
    raise RuntimeError("Slice 38F effect-boundary definition order mismatch")


CAPABILITY_FAMILY_HISTORIES_LIST: list[tuple[CapabilityFamilyIdentity, ...]] = []
CURRENT_CAPABILITY_FAMILIES_LIST: list[CapabilityFamilyIdentity] = []

for definition in CAPABILITY_FAMILY_DEFINITIONS:
    current = with_expected_id(
        CapabilityFamilyIdentity(
            capability_family_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            capability_family_key=definition.key,
            preferred_label=definition.label,
            definition=definition.definition,
            scope=definition.scope,
            non_scope=definition.non_scope,
            supported_effect_boundary_refs=tuple(
                _EFFECT_BY_KEY[key].effect_boundary_id
                for key in definition.effect_boundary_keys
            ),
            permitted_reference_modes=definition.reference_modes,
            authority_dependencies=definition.authority_dependencies,
            availability_proof_dependencies=definition.availability_proof_dependencies,
            route_proof_dependencies=definition.route_proof_dependencies,
            invocation_proof_dependencies=definition.invocation_proof_dependencies,
            prohibited_uses=definition.prohibited_uses,
            unknown_state_policy=definition.unknown_state_policy,
            version="v1.1.0",
            lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            provenance_refs=PROVENANCE_REFS,
            installed=False,
            available=False,
            route_registered=False,
            invocation_contract_installed=False,
            runtime_loaded=False,
            tool_bound=False,
            external_resource_loaded=False,
            implementation_authorized=False,
        )
    )
    candidate = with_expected_id(
        replace(
            current,
            capability_family_id="",
            version="v1.0.0",
            lifecycle_state=CapabilityReferenceLifecycleState.CANDIDATE,
        )
    )
    CAPABILITY_FAMILY_HISTORIES_LIST.append((candidate, current))
    CURRENT_CAPABILITY_FAMILIES_LIST.append(current)

CAPABILITY_FAMILY_HISTORIES: Final[
    tuple[tuple[CapabilityFamilyIdentity, ...], ...]
] = tuple(CAPABILITY_FAMILY_HISTORIES_LIST)

CAPABILITY_FAMILIES: Final[tuple[CapabilityFamilyIdentity, ...]] = tuple(
    CURRENT_CAPABILITY_FAMILIES_LIST
)

_CAPABILITY_BY_KEY = {
    family.capability_family_key: family
    for family in CAPABILITY_FAMILIES
}

if tuple(_CAPABILITY_BY_KEY) != ADMITTED_CAPABILITY_FAMILY_KEYS:
    raise RuntimeError("Slice 38F capability-family definition order mismatch")


COMPATIBILITY_HISTORIES_LIST: list[
    tuple[CapabilityEffectCompatibilityRecord, ...]
] = []
CURRENT_COMPATIBILITY_LIST: list[CapabilityEffectCompatibilityRecord] = []

for definition in CAPABILITY_FAMILY_DEFINITIONS:
    family = _CAPABILITY_BY_KEY[definition.key]
    if len(definition.effect_boundary_keys) != 1:
        raise RuntimeError(f"Slice 38F requires one exact effect boundary for {definition.key}")
    effect = _EFFECT_BY_KEY[definition.effect_boundary_keys[0]]
    current = with_expected_id(
        CapabilityEffectCompatibilityRecord(
            compatibility_id="",
            capability_family_id=family.capability_family_id,
            capability_family_key=family.capability_family_key,
            effect_boundary_id=effect.effect_boundary_id,
            effect_boundary_key=effect.effect_boundary_key,
            permitted_reference_modes=family.permitted_reference_modes,
            compatibility_basis=(
                "exact Forge-owned capability-family identity",
                "exact Forge-owned effect-boundary identity",
                "architecture-only compatibility without availability, route or invocation",
            ),
            scope=(
                f"capability-family:{family.capability_family_key}",
                f"effect-boundary:{effect.effect_boundary_key}",
                "compatibility:architecture-only",
            ),
            non_scope=(
                "capability installation",
                "capability availability",
                "route creation",
                "invocation authorization",
                "execution",
            ),
            version="v1.1.0",
            lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            provenance_refs=PROVENANCE_REFS,
            proves_capability_availability=False,
            creates_route=False,
            authorizes_invocation=False,
            authorizes_execution=False,
            satisfies_permission=False,
        )
    )
    candidate = with_expected_id(
        replace(
            current,
            compatibility_id="",
            version="v1.0.0",
            lifecycle_state=CapabilityReferenceLifecycleState.CANDIDATE,
        )
    )
    COMPATIBILITY_HISTORIES_LIST.append((candidate, current))
    CURRENT_COMPATIBILITY_LIST.append(current)

COMPATIBILITY_HISTORIES: Final[
    tuple[tuple[CapabilityEffectCompatibilityRecord, ...], ...]
] = tuple(COMPATIBILITY_HISTORIES_LIST)

COMPATIBILITY_RECORDS: Final[
    tuple[CapabilityEffectCompatibilityRecord, ...]
] = tuple(CURRENT_COMPATIBILITY_LIST)


FRAME_EFFECT_REFERENCE_HISTORIES_LIST: list[
    tuple[FrameEffectBoundaryReference, ...]
] = []
CURRENT_FRAME_EFFECT_REFERENCES_LIST: list[FrameEffectBoundaryReference] = []

for definition in FRAME_EFFECT_DEFINITIONS:
    frame = _FRAME_BY_KEY[definition.frame_key]
    effect = _EFFECT_BY_KEY[definition.effect_boundary_key]
    current = with_expected_id(
        FrameEffectBoundaryReference(
            frame_effect_reference_id="",
            frame_id=frame.frame_id,
            frame_key=frame.frame_key,
            frame_version=frame.version,
            effect_boundary_id=effect.effect_boundary_id,
            effect_boundary_key=effect.effect_boundary_key,
            effect_boundary_version=effect.version,
            classification_basis=definition.classification_basis,
            authority_dependencies=definition.authority_dependencies,
            scope=(
                f"frame:{frame.frame_key}",
                f"effect-boundary:{effect.effect_boundary_key}",
                "reference:classification-only",
            ),
            non_scope=(
                "frame selection",
                "permission",
                "capability availability",
                "route",
                "invocation",
                "execution",
                "result proof",
            ),
            unknown_state_policy=definition.unknown_state_policy,
            version="v1.1.0",
            lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            provenance_refs=PROVENANCE_REFS,
            frame_selected=False,
            effect_permission_satisfied=False,
            capability_available=False,
            route_resolved=False,
            invocation_proposed=False,
            invocation_authorized=False,
            execution_performed=False,
            result_verified=False,
        )
    )
    candidate = with_expected_id(
        replace(
            current,
            frame_effect_reference_id="",
            version="v1.0.0",
            lifecycle_state=CapabilityReferenceLifecycleState.CANDIDATE,
        )
    )
    FRAME_EFFECT_REFERENCE_HISTORIES_LIST.append((candidate, current))
    CURRENT_FRAME_EFFECT_REFERENCES_LIST.append(current)

FRAME_EFFECT_REFERENCE_HISTORIES: Final[
    tuple[tuple[FrameEffectBoundaryReference, ...], ...]
] = tuple(FRAME_EFFECT_REFERENCE_HISTORIES_LIST)

FRAME_EFFECT_REFERENCES: Final[tuple[FrameEffectBoundaryReference, ...]] = tuple(
    CURRENT_FRAME_EFFECT_REFERENCES_LIST
)

_FRAME_EFFECT_BY_FRAME_KEY = {
    reference.frame_key: reference
    for reference in FRAME_EFFECT_REFERENCES
}


FRAME_CAPABILITY_REFERENCE_HISTORIES_LIST: list[
    tuple[FrameCapabilityFamilyReference, ...]
] = []
CURRENT_FRAME_CAPABILITY_REFERENCES_LIST: list[FrameCapabilityFamilyReference] = []

for definition in FRAME_CAPABILITY_DEFINITIONS:
    frame = _FRAME_BY_KEY[definition.frame_key]
    family = _CAPABILITY_BY_KEY[definition.capability_family_key]
    effect = _EFFECT_BY_KEY[definition.effect_boundary_key]
    frame_effect = _FRAME_EFFECT_BY_FRAME_KEY[frame.frame_key]
    if frame_effect.effect_boundary_id != effect.effect_boundary_id:
        raise RuntimeError(f"frame effect mismatch for {frame.frame_key}: {frame_effect.effect_boundary_key} {frame_effect.effect_boundary_id} != {effect.effect_boundary_key} {effect.effect_boundary_id}")
    current = with_expected_id(
        FrameCapabilityFamilyReference(
            frame_capability_reference_id="",
            frame_id=frame.frame_id,
            frame_key=frame.frame_key,
            frame_version=frame.version,
            capability_family_id=family.capability_family_id,
            capability_family_key=family.capability_family_key,
            capability_family_version=family.version,
            frame_effect_reference_id=frame_effect.frame_effect_reference_id,
            effect_boundary_id=effect.effect_boundary_id,
            effect_boundary_key=effect.effect_boundary_key,
            relevance_mode=definition.relevance_mode,
            availability_status=CapabilityAvailabilityStatus.NOT_PROVEN,
            relevance_basis=definition.relevance_basis,
            authority_dependencies=definition.authority_dependencies,
            scope=(
                f"frame:{frame.frame_key}",
                f"capability-family:{family.capability_family_key}",
                f"effect-boundary:{effect.effect_boundary_key}",
                "reference:possible-relevance-only",
            ),
            non_scope=(
                "capability installation",
                "capability availability proof",
                "route identity",
                "invocation identity",
                "argument bundle",
                "permission",
                "execution",
                "result proof",
            ),
            unknown_state_policy=definition.unknown_state_policy,
            version="v1.1.0",
            lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            provenance_refs=PROVENANCE_REFS,
            capability_available=False,
            route_identity=None,
            route_available=False,
            invocation_identity=None,
            invocation_proposed=False,
            invocation_authorized=False,
            argument_bundle_id=None,
            arguments_constructed=False,
            permission_id=None,
            permission_granted=False,
            execution_receipt_id=None,
            execution_performed=False,
            result_verified=False,
            tool_bound=False,
            memory_operation_performed=False,
            delivery_performed=False,
            external_resource_admitted=False,
            implementation_performed=False,
        )
    )
    candidate = with_expected_id(
        replace(
            current,
            frame_capability_reference_id="",
            version="v1.0.0",
            lifecycle_state=CapabilityReferenceLifecycleState.CANDIDATE,
        )
    )
    FRAME_CAPABILITY_REFERENCE_HISTORIES_LIST.append((candidate, current))
    CURRENT_FRAME_CAPABILITY_REFERENCES_LIST.append(current)

FRAME_CAPABILITY_REFERENCE_HISTORIES: Final[
    tuple[tuple[FrameCapabilityFamilyReference, ...], ...]
] = tuple(FRAME_CAPABILITY_REFERENCE_HISTORIES_LIST)

FRAME_CAPABILITY_REFERENCES: Final[
    tuple[FrameCapabilityFamilyReference, ...]
] = tuple(CURRENT_FRAME_CAPABILITY_REFERENCES_LIST)


ADMISSION_AUTHORITY: Final[CapabilityReferenceLifecycleAuthorityRecord] = with_expected_id(
    CapabilityReferenceLifecycleAuthorityRecord(
        authority_id="",
        authority_key="slice38f_architecture_admission",
        decision_owner="Nicholas Jacob Bogaert / AI.Web",
        authority_basis=(
            "AI.Web Forge Canonical Production Roadmap v1.0 Slice 38F",
            "RMC Predicate–Role Frame Registry v1 Sections 43 through 45",
            "accepted Slice 38E parent source and live evidence",
        ),
        approved_scope=(
            "six exact effect-boundary identities",
            "six exact capability-family identities",
            "five exact frame effect references",
            "five non-operational frame capability-family relevance references",
            "six capability-effect compatibility records",
            "versioned lifecycle and provenance",
        ),
        prohibited_scope=SLICE38F_AUTHORITY_LIMITATIONS,
        human_approval=True,
        non_llm_decision=True,
        automatic_transition_allowed=False,
        implementation_authorized=False,
        capability_availability_authorized=False,
        route_authorized=False,
        invocation_authorized=False,
        action_authorized=False,
        version="v1.1.0",
        lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
        provenance_refs=PROVENANCE_REFS,
    )
)


def _transition_for_history(
    history: tuple[
        EffectBoundaryIdentity
        | CapabilityFamilyIdentity
        | FrameEffectBoundaryReference
        | FrameCapabilityFamilyReference
        | CapabilityEffectCompatibilityRecord,
        ...,
    ],
) -> CapabilityReferenceLifecycleTransitionRecord:
    source, target = history
    return with_expected_id(
        CapabilityReferenceLifecycleTransitionRecord(
            transition_id="",
            resource_lineage_id=expected_lineage_id(source),
            source_resource_id=source.expected_id(),
            target_resource_id=target.expected_id(),
            source_version=source.version,
            target_version=target.version,
            from_state=source.lifecycle_state,
            to_state=target.lifecycle_state,
            transition_kind=CapabilityReferenceTransitionKind.ARCHITECTURE_ADMIT,
            reason=(
                "Explicit Slice 38F architecture admission with prior record preservation and no "
                "capability availability, route, invocation, permission, execution or result proof."
            ),
            scope=(
                "slice:38f",
                f"resource-lineage:{expected_lineage_id(source)}",
                "transition:candidate-to-architecture-admitted",
            ),
            non_scope=(
                "automatic transition",
                "in-place mutation",
                "capability availability",
                "route creation",
                "invocation",
                "permission",
                "execution",
                "result proof",
            ),
            provenance_refs=PROVENANCE_REFS,
            authority_record_ref=ADMISSION_AUTHORITY.authority_id,
            human_approval=True,
            prior_record_preserved=True,
            automatic_transition=False,
            in_place_mutation_performed=False,
            capability_availability_created=False,
            route_created=False,
            invocation_created=False,
            permission_created=False,
            execution_created=False,
            result_proof_created=False,
        )
    )


_ALL_HISTORIES = (
    *EFFECT_BOUNDARY_HISTORIES,
    *CAPABILITY_FAMILY_HISTORIES,
    *FRAME_EFFECT_REFERENCE_HISTORIES,
    *FRAME_CAPABILITY_REFERENCE_HISTORIES,
    *COMPATIBILITY_HISTORIES,
)

TRANSITIONS: Final[tuple[CapabilityReferenceLifecycleTransitionRecord, ...]] = tuple(
    _transition_for_history(history)
    for history in _ALL_HISTORIES
)


REGISTRY_ID: Final[str] = stable_record_id(
    "slice38f_capability_family_reference_registry",
    {
        "namespace_id": CURRENT_NAMESPACE.namespace_id,
        "effect_boundary_keys": ADMITTED_EFFECT_BOUNDARY_KEYS,
        "capability_family_keys": ADMITTED_CAPABILITY_FAMILY_KEYS,
        "frame_effect_reference_ids": tuple(
            item.frame_effect_reference_id
            for item in FRAME_EFFECT_REFERENCES
        ),
        "frame_capability_reference_ids": tuple(
            item.frame_capability_reference_id
            for item in FRAME_CAPABILITY_REFERENCES
        ),
        "compatibility_ids": tuple(
            item.compatibility_id
            for item in COMPATIBILITY_RECORDS
        ),
        "version": "v1.1.0",
    },
)

_MANIFEST_PLACEHOLDER = CapabilityFamilyReferenceRegistryManifest(
    manifest_id="",
    registry_id=REGISTRY_ID,
    namespace_id=CURRENT_NAMESPACE.namespace_id,
    effect_boundary_refs=tuple(item.effect_boundary_id for item in EFFECT_BOUNDARIES),
    effect_boundary_keys=tuple(item.effect_boundary_key for item in EFFECT_BOUNDARIES),
    capability_family_refs=tuple(item.capability_family_id for item in CAPABILITY_FAMILIES),
    capability_family_keys=tuple(item.capability_family_key for item in CAPABILITY_FAMILIES),
    frame_effect_reference_refs=tuple(
        item.frame_effect_reference_id
        for item in FRAME_EFFECT_REFERENCES
    ),
    frame_capability_reference_refs=tuple(
        item.frame_capability_reference_id
        for item in FRAME_CAPABILITY_REFERENCES
    ),
    compatibility_refs=tuple(item.compatibility_id for item in COMPATIBILITY_RECORDS),
    transition_refs=tuple(item.transition_id for item in TRANSITIONS),
    provenance_refs=PROVENANCE_REFS,
    frames_without_capability_reference=FRAMES_WITHOUT_CAPABILITY_REFERENCE,
    unbound_capability_family_keys=UNBOUND_CAPABILITY_FAMILY_KEYS,
    deferred_capability_family_keys=DEFERRED_CAPABILITY_FAMILY_KEYS,
    effect_boundary_count=len(EFFECT_BOUNDARIES),
    capability_family_count=len(CAPABILITY_FAMILIES),
    frame_effect_reference_count=len(FRAME_EFFECT_REFERENCES),
    frame_capability_reference_count=len(FRAME_CAPABILITY_REFERENCES),
    compatibility_count=len(COMPATIBILITY_RECORDS),
    transition_count=len(TRANSITIONS),
    active_correction_count=0,
    active_conflict_count=0,
    source_term_lookup_installed=False,
    occurrence_frame_selection_installed=False,
    occurrence_role_assignment_installed=False,
    candidate_meaning_creation_installed=False,
    selected_meaning_installed=False,
    gate_outcome_installed=False,
    capability_availability_registry_installed=False,
    route_registry_installed=False,
    invocation_registry_installed=False,
    argument_builder_installed=False,
    tool_activation_installed=False,
    action_execution_installed=False,
    evidence_validation_installed=False,
    memory_access_installed=False,
    rendering_installed=False,
    delivery_installed=False,
    external_resource_loading_installed=False,
    implementation_installed=False,
    nearest_known_substitution_installed=False,
    semantic_similarity_installed=False,
    llm_authority_installed=False,
    default_capability_reference_installed=False,
    registry_read_only=True,
    registry_closed=True,
    exact_identity_lookup_only=True,
    version="v1.1.0",
    lifecycle_state=CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
    provenance_refs_manifest=PROVENANCE_REFS,
)

MANIFEST: Final[CapabilityFamilyReferenceRegistryManifest] = with_expected_id(
    _MANIFEST_PLACEHOLDER
)


CAPABILITY_FAMILY_REFERENCE_REGISTRY: Final[CapabilityFamilyReferenceRegistry] = (
    CapabilityFamilyReferenceRegistry(
        manifest=MANIFEST,
        current_namespace=CURRENT_NAMESPACE,
        effect_boundaries=EFFECT_BOUNDARIES,
        effect_boundary_histories=EFFECT_BOUNDARY_HISTORIES,
        capability_families=CAPABILITY_FAMILIES,
        capability_family_histories=CAPABILITY_FAMILY_HISTORIES,
        frame_effect_references=FRAME_EFFECT_REFERENCES,
        frame_effect_reference_histories=FRAME_EFFECT_REFERENCE_HISTORIES,
        frame_capability_references=FRAME_CAPABILITY_REFERENCES,
        frame_capability_reference_histories=FRAME_CAPABILITY_REFERENCE_HISTORIES,
        compatibility_records=COMPATIBILITY_RECORDS,
        compatibility_histories=COMPATIBILITY_HISTORIES,
        authority_records=(ADMISSION_AUTHORITY,),
        transitions=TRANSITIONS,
        provenance_records=PROVENANCE_RECORDS,
    )
)
