"""Closed Slice 38F capability-family and effect-boundary definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .schema import (
    CapabilityReferenceMode,
    EffectBoundaryClass,
)


SLICE38F_AUTHORITY_LIMITATIONS: Final[tuple[str, ...]] = (
    "capability reference is not capability availability",
    "capability availability is not route existence",
    "route existence is not invocation",
    "invocation proposal is not execution",
    "frame completion is not permission",
    "effect boundary is not permission",
    "effect boundary is not execution",
    "effect boundary is not evidence",
    "effect boundary is not gate outcome",
    "effect boundary is not capability family",
    "capability family identity is not installed capability",
    "capability family compatibility is not a wire",
    "capability family relevance is not argument construction",
    "capability family relevance is not tool binding",
    "capability family relevance is not memory authority",
    "capability family relevance is not delivery authority",
    "capability family relevance is not external-resource admission",
    "capability family relevance is not implementation authority",
    "read-only relevance is not source-access authority",
    "source-comparison relevance is not evidence validation",
    "draft relevance is not delivery",
    "verification-review relevance is not verified status or proof",
    "simulation relevance is not live execution",
    "protected mathematical relevance does not supersede GP-014",
    "unknown capability relevance is not nearest known capability family",
    "unsupported capability relevance is not automatic refusal",
    "deferred capability relevance is not capability absence proof",
    "registry lookup is exact identity lookup only",
    "registry is not a route registry",
    "registry is not an invocation registry",
    "registry is not a tool registry",
    "registry is not an action authority",
    "registry is not an evidence authority",
    "registry is not a memory authority",
    "registry is not rendering or delivery authority",
)

ADMITTED_EFFECT_BOUNDARY_KEYS: Final[tuple[str, ...]] = (
    "no_action",
    "read_only",
    "communicative_only",
    "verification_review_only",
    "simulation_only",
    "protected_mathematical_output_only",
)

ADMITTED_CAPABILITY_FAMILY_KEYS: Final[tuple[str, ...]] = (
    "read_only_inspection",
    "source_comparison",
    "draft_preparation",
    "verification_review",
    "non_live_simulation",
    "protected_mathematical_operation",
)

DEFERRED_CAPABILITY_FAMILY_KEYS: Final[tuple[str, ...]] = (
    "memory_request",
    "software_change_proposal",
    "delivery_request",
)

FRAMES_WITHOUT_CAPABILITY_REFERENCE: Final[tuple[str, ...]] = (
    "request_non_authorizing",
)

UNBOUND_CAPABILITY_FAMILY_KEYS: Final[tuple[str, ...]] = (
    "protected_mathematical_operation",
)


@dataclass(frozen=True, slots=True)
class EffectBoundaryDefinition:
    key: str
    label: str
    effect_class: EffectBoundaryClass
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    allowed_consequence_descriptions: tuple[str, ...]
    prohibited_escalations: tuple[str, ...]
    authority_dependencies: tuple[str, ...]
    unknown_state_policy: str


@dataclass(frozen=True, slots=True)
class CapabilityFamilyDefinition:
    key: str
    label: str
    definition: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    effect_boundary_keys: tuple[str, ...]
    reference_modes: tuple[CapabilityReferenceMode, ...]
    authority_dependencies: tuple[str, ...]
    availability_proof_dependencies: tuple[str, ...]
    route_proof_dependencies: tuple[str, ...]
    invocation_proof_dependencies: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unknown_state_policy: str


@dataclass(frozen=True, slots=True)
class FrameEffectDefinition:
    frame_key: str
    effect_boundary_key: str
    classification_basis: tuple[str, ...]
    authority_dependencies: tuple[str, ...]
    unknown_state_policy: str


@dataclass(frozen=True, slots=True)
class FrameCapabilityDefinition:
    frame_key: str
    capability_family_key: str
    effect_boundary_key: str
    relevance_mode: CapabilityReferenceMode
    relevance_basis: tuple[str, ...]
    authority_dependencies: tuple[str, ...]
    unknown_state_policy: str


EFFECT_BOUNDARY_DEFINITIONS: Final[tuple[EffectBoundaryDefinition, ...]] = (
    EffectBoundaryDefinition(
        key="no_action",
        label="No-Action Effect Boundary",
        effect_class=EffectBoundaryClass.NO_ACTION,
        definition=(
            "A controlled effect classification stating that the represented frame does not itself "
            "create a state-changing consequence, capability route, invocation, permission, or result."
        ),
        scope=(
            "effect:non-operative",
            "consequence:none-created-by-this-layer",
            "frame:request_non_authorizing",
        ),
        non_scope=(
            "refusal outcome",
            "capability impossibility",
            "permission decision",
            "action decision",
        ),
        allowed_consequence_descriptions=(
            "architecture-level non-operative classification",
            "explicit preservation of unsatisfied authority dependencies",
        ),
        prohibited_escalations=(
            "no-action to refusal",
            "no-action to permission",
            "no-action to route",
            "no-action to execution",
        ),
        authority_dependencies=(
            "Document 6 selected-meaning and gate authority",
            "separate permission and action authority",
            "Document 10 implementation authority",
        ),
        unknown_state_policy=(
            "If consequence cannot be classified, preserve unknown or unresolved state rather than defaulting to no-action."
        ),
    ),
    EffectBoundaryDefinition(
        key="read_only",
        label="Read-Only Effect Boundary",
        effect_class=EffectBoundaryClass.READ_ONLY,
        definition=(
            "A controlled effect classification for examination, review, or comparison that must not "
            "write, modify, install, delete, persist, send, publish, or otherwise change the inspected state."
        ),
        scope=(
            "effect:read-only",
            "frame:inspect_read_only",
            "future-capability-relevance:inspection-or-comparison",
        ),
        non_scope=(
            "source access grant",
            "write",
            "runtime modification",
            "evidence validation",
        ),
        allowed_consequence_descriptions=(
            "future authorized inspection",
            "future authorized comparison",
            "non-state-changing review",
        ),
        prohibited_escalations=(
            "read-only to write",
            "inspection to modification",
            "comparison to approval",
            "source review to proof",
        ),
        authority_dependencies=(
            "source access privacy and identity authority where material",
            "Document 7 evidence authority where observations become evidence",
            "later live capability availability proof",
            "Document 10 implementation authority",
        ),
        unknown_state_policy=(
            "Missing access, effect, or source authority remains explicit and does not become implied read access."
        ),
    ),
    EffectBoundaryDefinition(
        key="communicative_only",
        label="Communicative-Only Effect Boundary",
        effect_class=EffectBoundaryClass.COMMUNICATIVE_ONLY,
        definition=(
            "A controlled effect classification for preparing or representing attributed communicative "
            "content without sending, publishing, persisting, or proving that content."
        ),
        scope=(
            "effect:communicative-only",
            "frame:report_attributed_content",
            "future-capability-relevance:draft-preparation",
        ),
        non_scope=(
            "delivery",
            "publication",
            "memory persistence",
            "evidence proof",
        ),
        allowed_consequence_descriptions=(
            "future authorized draft preparation",
            "attributed content organization",
            "non-delivered communicative preparation",
        ),
        prohibited_escalations=(
            "draft to send",
            "draft to publication",
            "report to evidence",
            "recipient presence to delivery authorization",
        ),
        authority_dependencies=(
            "Document 7 source attribution and evidence boundaries",
            "delivery and privacy authority where materially implicated",
            "later live capability availability proof",
            "Document 10 implementation authority",
        ),
        unknown_state_policy=(
            "Unknown delivery, attribution, or privacy status remains unresolved and cannot be repaired by assuming draft-only safety."
        ),
    ),
    EffectBoundaryDefinition(
        key="verification_review_only",
        label="Verification-Review-Only Effect Boundary",
        effect_class=EffectBoundaryClass.VERIFICATION_REVIEW_ONLY,
        definition=(
            "A controlled effect classification for reviewing a subject against a standard without "
            "validating evidence, certifying a result, or converting review into proof."
        ),
        scope=(
            "effect:verification-review-only",
            "frame:verify_bounded_review",
            "future-capability-relevance:verification-review",
        ),
        non_scope=(
            "verified status",
            "proof",
            "certification",
            "evidence validation",
        ),
        allowed_consequence_descriptions=(
            "future authorized bounded verification review",
            "standard comparison",
            "explicit unresolved result status",
        ),
        prohibited_escalations=(
            "review to verified status",
            "comparison to proof",
            "reported result to verified result",
            "standard reference to certification authority",
        ),
        authority_dependencies=(
            "Document 7 evidence and verification-result governance",
            "standard-specific authority where material",
            "later live capability availability proof",
            "Document 9 verification authority",
            "Document 10 implementation authority",
        ),
        unknown_state_policy=(
            "Unknown evidence, standard, or result status remains explicit and cannot be converted to verified status."
        ),
    ),
    EffectBoundaryDefinition(
        key="simulation_only",
        label="Simulation-Only Effect Boundary",
        effect_class=EffectBoundaryClass.SIMULATION_ONLY,
        definition=(
            "A controlled effect classification for hypothetical, assumption-bound modeling that must "
            "not create live arguments, mutate runtime, persist memory, deliver output, or prove occurrence."
        ),
        scope=(
            "effect:simulation-only",
            "frame:simulate_non_live",
            "future-capability-relevance:non-live-simulation",
        ),
        non_scope=(
            "live execution",
            "runtime mutation",
            "real-world occurrence",
            "live result",
        ),
        allowed_consequence_descriptions=(
            "future authorized non-live modeling",
            "assumption-bound hypothetical result",
            "dry-run-like non-operative analysis",
        ),
        prohibited_escalations=(
            "simulation to execution",
            "modeled result to observed fact",
            "simulation input to live argument bundle",
            "hypothetical state to runtime state",
        ),
        authority_dependencies=(
            "explicit assumption and hypothetical-status custody",
            "separate runtime memory delivery and economic authority",
            "later live capability availability proof",
            "Document 10 implementation authority",
        ),
        unknown_state_policy=(
            "Unknown assumptions, inputs, or effect consequences preserve non-operative unresolved state."
        ),
    ),
    EffectBoundaryDefinition(
        key="protected_mathematical_output_only",
        label="Protected Mathematical-Output-Only Effect Boundary",
        effect_class=EffectBoundaryClass.PROTECTED_MATHEMATICAL_OUTPUT_ONLY,
        definition=(
            "A controlled effect classification preserving GP-014 as the bounded mathematical-output "
            "expression baseline without broadening it into general language, routing, execution, or proof authority."
        ),
        scope=(
            "effect:protected-mathematical-output-only",
            "baseline:gp-014",
            "future-capability-relevance:protected-mathematical-operation",
        ),
        non_scope=(
            "general language",
            "general predicate authority",
            "general capability route",
            "full RMC",
        ),
        allowed_consequence_descriptions=(
            "preservation of bounded mathematical-output reference",
            "future separately authorized protected mathematical relevance",
        ),
        prohibited_escalations=(
            "GP-014 to general language authority",
            "mathematical relevance to tool invocation",
            "expression result to proof",
            "protected baseline to supersession",
        ),
        authority_dependencies=(
            "accepted GP-014 preservation boundary",
            "separate mathematical capability availability proof",
            "Document 9 verification authority",
            "Document 10 implementation authority",
        ),
        unknown_state_policy=(
            "Any unsupported or non-GP-014 mathematical request remains outside this boundary rather than being approximated."
        ),
    ),
)


CAPABILITY_FAMILY_DEFINITIONS: Final[tuple[CapabilityFamilyDefinition, ...]] = (
    CapabilityFamilyDefinition(
        key="read_only_inspection",
        label="Read-Only Inspection Capability Family",
        definition=(
            "An architecture-only family identity for possible future non-state-changing inspection. "
            "It does not prove access, installation, availability, route, invocation, or result."
        ),
        scope=(
            "capability-family:read-only-inspection",
            "possible-relevance:inspect_read_only",
            "effect-boundary:read_only",
        ),
        non_scope=("write", "modify", "install", "evidence validation", "source access grant"),
        effect_boundary_keys=("read_only",),
        reference_modes=(CapabilityReferenceMode.READ_ONLY_POSSIBLE,),
        authority_dependencies=(
            "source access privacy and identity authority where material",
            "later live capability registry",
            "route proof",
            "invocation authorization",
            "Document 10 implementation authority",
        ),
        availability_proof_dependencies=(
            "installed read-only capability identity",
            "verified live availability record",
        ),
        route_proof_dependencies=(
            "separately admitted route identity",
            "route scope and effect compatibility proof",
        ),
        invocation_proof_dependencies=(
            "separate invocation proposal",
            "permission and gate proof",
            "argument validation",
        ),
        prohibited_uses=SLICE38F_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown inspection capability state remains not proven and cannot default to an available reader."
        ),
    ),
    CapabilityFamilyDefinition(
        key="source_comparison",
        label="Source Comparison Capability Family",
        definition=(
            "An architecture-only family identity for possible future comparison of already lawfully "
            "available sources. Comparison relevance does not grant access, validate evidence, or approve a conclusion."
        ),
        scope=(
            "capability-family:source-comparison",
            "possible-relevance:inspect_read_only",
            "effect-boundary:read_only",
        ),
        non_scope=("source access grant", "evidence validation", "approval", "proof"),
        effect_boundary_keys=("read_only",),
        reference_modes=(CapabilityReferenceMode.COMPARISON_POSSIBLE,),
        authority_dependencies=(
            "lawful source availability",
            "Document 7 source and evidence custody",
            "later live capability registry",
            "route proof",
            "Document 10 implementation authority",
        ),
        availability_proof_dependencies=(
            "installed comparison capability identity",
            "verified live availability record",
        ),
        route_proof_dependencies=(
            "separately admitted route identity",
            "source-scope compatibility proof",
        ),
        invocation_proof_dependencies=(
            "separate invocation proposal",
            "permission and gate proof",
            "argument validation",
        ),
        prohibited_uses=SLICE38F_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown source, access, or comparison support remains unresolved rather than silently selecting a comparator."
        ),
    ),
    CapabilityFamilyDefinition(
        key="draft_preparation",
        label="Draft Preparation Capability Family",
        definition=(
            "An architecture-only family identity for possible future preparation of non-delivered draft "
            "content. A draft reference is not sending, publication, persistence, or proof."
        ),
        scope=(
            "capability-family:draft-preparation",
            "possible-relevance:report_attributed_content",
            "effect-boundary:communicative_only",
        ),
        non_scope=("send", "publish", "persist", "memory write", "evidence proof"),
        effect_boundary_keys=("communicative_only",),
        reference_modes=(CapabilityReferenceMode.DRAFT_POSSIBLE,),
        authority_dependencies=(
            "source attribution and privacy boundaries",
            "later live capability registry",
            "delivery authority remains unsatisfied",
            "route proof",
            "Document 10 implementation authority",
        ),
        availability_proof_dependencies=(
            "installed drafting capability identity",
            "verified live availability record",
        ),
        route_proof_dependencies=(
            "separately admitted draft route identity",
            "non-delivery route proof",
        ),
        invocation_proof_dependencies=(
            "separate invocation proposal",
            "permission and gate proof",
            "content and target validation",
        ),
        prohibited_uses=SLICE38F_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown drafting support remains not proven and cannot become an implicit message sender."
        ),
    ),
    CapabilityFamilyDefinition(
        key="verification_review",
        label="Verification Review Capability Family",
        definition=(
            "An architecture-only family identity for possible future bounded review against an explicit "
            "standard. It does not validate evidence, certify a result, or prove a claim."
        ),
        scope=(
            "capability-family:verification-review",
            "possible-relevance:verify_bounded_review",
            "effect-boundary:verification_review_only",
        ),
        non_scope=("verified status", "proof", "certification", "evidence validation"),
        effect_boundary_keys=("verification_review_only",),
        reference_modes=(CapabilityReferenceMode.VERIFICATION_REVIEW_POSSIBLE,),
        authority_dependencies=(
            "Document 7 evidence and verification-result governance",
            "standard-specific authority",
            "later live capability registry",
            "route proof",
            "Document 9 verification authority",
            "Document 10 implementation authority",
        ),
        availability_proof_dependencies=(
            "installed verification-review capability identity",
            "verified live availability record",
        ),
        route_proof_dependencies=(
            "separately admitted verification-review route identity",
            "standard and effect compatibility proof",
        ),
        invocation_proof_dependencies=(
            "separate invocation proposal",
            "permission and gate proof",
            "evidence and standard argument validation",
        ),
        prohibited_uses=SLICE38F_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown evidence, standard, or capability state remains unresolved and cannot become verified status."
        ),
    ),
    CapabilityFamilyDefinition(
        key="non_live_simulation",
        label="Non-Live Simulation Capability Family",
        definition=(
            "An architecture-only family identity for possible future assumption-bound non-live modeling. "
            "It does not construct live arguments, execute, mutate runtime, or prove real occurrence."
        ),
        scope=(
            "capability-family:non-live-simulation",
            "possible-relevance:simulate_non_live",
            "effect-boundary:simulation_only",
        ),
        non_scope=("live execution", "runtime mutation", "memory write", "delivery", "real result"),
        effect_boundary_keys=("simulation_only",),
        reference_modes=(CapabilityReferenceMode.SIMULATION_POSSIBLE,),
        authority_dependencies=(
            "explicit assumption and hypothetical-status custody",
            "later live capability registry",
            "route proof",
            "separate runtime authority",
            "Document 10 implementation authority",
        ),
        availability_proof_dependencies=(
            "installed simulation capability identity",
            "verified live availability record",
        ),
        route_proof_dependencies=(
            "separately admitted simulation route identity",
            "non-live effect compatibility proof",
        ),
        invocation_proof_dependencies=(
            "separate invocation proposal",
            "permission and gate proof",
            "assumption and input validation",
        ),
        prohibited_uses=SLICE38F_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown simulation support remains not proven and cannot be substituted with live execution."
        ),
    ),
    CapabilityFamilyDefinition(
        key="protected_mathematical_operation",
        label="Protected Mathematical Operation Capability Family",
        definition=(
            "An architecture-only family identity preserving possible relevance to the accepted GP-014 "
            "bounded mathematical-output baseline. It is intentionally unbound to the Slice 38E frames."
        ),
        scope=(
            "capability-family:protected-mathematical-operation",
            "baseline:gp-014",
            "effect-boundary:protected_mathematical_output_only",
        ),
        non_scope=("general language", "general predicate authority", "general route", "GP-014 supersession"),
        effect_boundary_keys=("protected_mathematical_output_only",),
        reference_modes=(CapabilityReferenceMode.PROTECTED_MATHEMATICAL_POSSIBLE,),
        authority_dependencies=(
            "accepted GP-014 preservation boundary",
            "separate compatible frame admission",
            "later live capability registry",
            "route proof",
            "Document 9 verification authority",
            "Document 10 implementation authority",
        ),
        availability_proof_dependencies=(
            "verified GP-014-compatible installed capability identity",
            "verified live availability record",
        ),
        route_proof_dependencies=(
            "separately admitted protected mathematical route identity",
            "GP-014 scope compatibility proof",
        ),
        invocation_proof_dependencies=(
            "separate invocation proposal",
            "permission and gate proof",
            "bounded mathematical argument validation",
        ),
        prohibited_uses=SLICE38F_AUTHORITY_LIMITATIONS,
        unknown_state_policy=(
            "Unknown or out-of-scope mathematical material remains unsupported rather than broadening GP-014."
        ),
    ),
)


FRAME_EFFECT_DEFINITIONS: Final[tuple[FrameEffectDefinition, ...]] = (
    FrameEffectDefinition(
        frame_key="inspect_read_only",
        effect_boundary_key="read_only",
        classification_basis=(
            "Slice 38E frame effect classification is read_only",
            "inspection must remain non-state-changing",
        ),
        authority_dependencies=(
            "Slice 38E exact frame identity",
            "Document 6 selected-meaning and gate authority",
            "source access authority where material",
        ),
        unknown_state_policy=(
            "If the frame or effect reference is not exact, preserve unknown rather than defaulting to read-only."
        ),
    ),
    FrameEffectDefinition(
        frame_key="report_attributed_content",
        effect_boundary_key="communicative_only",
        classification_basis=(
            "Slice 38E frame effect classification is communicative_only",
            "reported material remains attributed and undelivered",
        ),
        authority_dependencies=(
            "Slice 38E exact frame identity",
            "Document 7 source attribution boundary",
            "delivery authority remains unsatisfied",
        ),
        unknown_state_policy=(
            "Unknown attribution or delivery status remains unresolved and does not become communicative permission."
        ),
    ),
    FrameEffectDefinition(
        frame_key="request_non_authorizing",
        effect_boundary_key="no_action",
        classification_basis=(
            "Slice 38E frame effect classification is no_action",
            "request is not authorization or completion",
        ),
        authority_dependencies=(
            "Slice 38E exact frame identity",
            "Document 6 speech-act and gate authority",
            "separate permission and action authority",
        ),
        unknown_state_policy=(
            "Unknown requested capability relevance remains absent rather than being inferred from request form."
        ),
    ),
    FrameEffectDefinition(
        frame_key="verify_bounded_review",
        effect_boundary_key="verification_review_only",
        classification_basis=(
            "Slice 38E frame effect classification is verification_review_only",
            "review does not create verified status or proof",
        ),
        authority_dependencies=(
            "Slice 38E exact frame identity",
            "Document 7 evidence and verification-result governance",
            "Document 9 verification authority",
        ),
        unknown_state_policy=(
            "Unknown evidence or standard status remains unresolved and does not become verified."
        ),
    ),
    FrameEffectDefinition(
        frame_key="simulate_non_live",
        effect_boundary_key="simulation_only",
        classification_basis=(
            "Slice 38E frame effect classification is simulation_only",
            "simulation remains hypothetical and non-live",
        ),
        authority_dependencies=(
            "Slice 38E exact frame identity",
            "assumption and hypothetical-status custody",
            "separate runtime authority",
        ),
        unknown_state_policy=(
            "Unknown simulation assumptions or effects remain unresolved and non-operative."
        ),
    ),
)


FRAME_CAPABILITY_DEFINITIONS: Final[tuple[FrameCapabilityDefinition, ...]] = (
    FrameCapabilityDefinition(
        frame_key="inspect_read_only",
        capability_family_key="read_only_inspection",
        effect_boundary_key="read_only",
        relevance_mode=CapabilityReferenceMode.READ_ONLY_POSSIBLE,
        relevance_basis=(
            "read-only inspection may later require a governed inspection capability family",
            "reference remains non-operational",
        ),
        authority_dependencies=(
            "exact frame and effect-boundary identity",
            "later capability availability proof",
            "separate route and invocation authority",
        ),
        unknown_state_policy=(
            "Missing capability proof remains not_proven and does not create a reader."
        ),
    ),
    FrameCapabilityDefinition(
        frame_key="inspect_read_only",
        capability_family_key="source_comparison",
        effect_boundary_key="read_only",
        relevance_mode=CapabilityReferenceMode.COMPARISON_POSSIBLE,
        relevance_basis=(
            "read-only inspection may later compare lawfully available sources",
            "comparison relevance does not validate evidence",
        ),
        authority_dependencies=(
            "exact frame and effect-boundary identity",
            "lawful source availability",
            "later capability availability proof",
            "separate route and invocation authority",
        ),
        unknown_state_policy=(
            "Missing source or comparison proof remains unresolved and does not create a comparator."
        ),
    ),
    FrameCapabilityDefinition(
        frame_key="report_attributed_content",
        capability_family_key="draft_preparation",
        effect_boundary_key="communicative_only",
        relevance_mode=CapabilityReferenceMode.DRAFT_POSSIBLE,
        relevance_basis=(
            "an attributed report may later require non-delivered draft preparation",
            "draft relevance does not authorize delivery",
        ),
        authority_dependencies=(
            "exact frame and effect-boundary identity",
            "source attribution and privacy boundaries",
            "later capability availability proof",
            "delivery authority remains unsatisfied",
        ),
        unknown_state_policy=(
            "Missing drafting proof remains not_proven and cannot become sending or publication."
        ),
    ),
    FrameCapabilityDefinition(
        frame_key="verify_bounded_review",
        capability_family_key="verification_review",
        effect_boundary_key="verification_review_only",
        relevance_mode=CapabilityReferenceMode.VERIFICATION_REVIEW_POSSIBLE,
        relevance_basis=(
            "bounded review may later require a governed verification-review capability family",
            "reference does not create verified status or proof",
        ),
        authority_dependencies=(
            "exact frame and effect-boundary identity",
            "evidence and standard authority",
            "later capability availability proof",
            "separate route and invocation authority",
        ),
        unknown_state_policy=(
            "Missing verification capability proof remains not_proven and cannot certify a result."
        ),
    ),
    FrameCapabilityDefinition(
        frame_key="simulate_non_live",
        capability_family_key="non_live_simulation",
        effect_boundary_key="simulation_only",
        relevance_mode=CapabilityReferenceMode.SIMULATION_POSSIBLE,
        relevance_basis=(
            "a non-live simulation frame may later require a governed simulation capability family",
            "reference does not construct live arguments or execute",
        ),
        authority_dependencies=(
            "exact frame and effect-boundary identity",
            "assumption and hypothetical-status custody",
            "later capability availability proof",
            "separate route and invocation authority",
        ),
        unknown_state_policy=(
            "Missing simulation capability proof remains not_proven and cannot become live execution."
        ),
    ),
)
