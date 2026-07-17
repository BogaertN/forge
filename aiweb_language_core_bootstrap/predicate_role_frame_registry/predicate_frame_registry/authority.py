"""Closed Slice 38E frame definitions and authority boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .schema import (
    FrameEffectClassification as Effect,
    FrameRoleCardinality as Cardinality,
    FrameRoleRequirement as Requirement,
    FrameSpeechAct as SpeechAct,
)


SLICE38E_AUTHORITY_LIMITATIONS: Final[tuple[str, ...]] = (
    "predicate-frame identity is not selected frame",
    "frame membership is not occurrence interpretation",
    "role constraint is not occurrence role assignment",
    "role compatibility is not concept assignment",
    "structural completeness is not gate passage",
    "structural completeness is not permission",
    "request frame is not authorization",
    "report frame is not evidence",
    "verify frame is not verified status or proof",
    "simulate frame is not live execution",
    "read-only frame is not source-access authority",
    "speech-act compatibility is not speech-act selection",
    "effect classification is not capability availability",
    "capability reference is deferred to Slice 38F",
    "unknown frame is not nearest known frame",
    "ambiguous frame is not probability-ranked frame",
    "conflicted frame is not automatic refusal",
    "unsupported frame is not automatic refusal",
    "frame registry is not route registry",
    "frame registry is not tool registry",
    "frame registry is not action authority",
    "frame registry is not evidence authority",
    "frame registry is not memory authority",
    "frame registry is not rendering or delivery authority",
)

ADMITTED_PREDICATE_FRAME_KEYS: Final[tuple[str, ...]] = (
    "inspect_read_only",
    "report_attributed_content",
    "request_non_authorizing",
    "verify_bounded_review",
    "simulate_non_live",
)

SLICE38E_DEFERRED_FRAME_FAMILIES: Final[tuple[str, ...]] = (
    "approval and authorization frames",
    "installation and runtime-mutation frames",
    "delivery and publication frames",
    "memory read write correction and deletion frames",
    "rollback execution frames",
    "external-resource admission frames",
    "economic consequence frames",
    "identity verification frames",
)

ALL_SPEECH_ACT_CONTEXTS: Final[tuple[SpeechAct, ...]] = (
    SpeechAct.REQUEST,
    SpeechAct.QUESTION,
    SpeechAct.REPORT,
    SpeechAct.PROPOSAL,
    SpeechAct.PROHIBITION,
    SpeechAct.REFUSAL,
    SpeechAct.HYPOTHETICAL,
    SpeechAct.CONDITIONAL,
    SpeechAct.QUOTED,
)


@dataclass(frozen=True, slots=True)
class RoleConstraintDefinition:
    role_key: str
    requirement: Requirement
    cardinality: Cardinality
    condition_key: str | None = None
    co_required_role_keys: tuple[str, ...] = ()
    conflicting_role_keys: tuple[str, ...] = ()
    allowed_semantic_class_keys: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FrameDefinition:
    frame_key: str
    action_root_key: str
    label: str
    definition: str
    purpose: str
    role_constraints: tuple[RoleConstraintDefinition, ...]
    permitted_speech_acts: tuple[SpeechAct, ...]
    effect_classification: Effect
    authority_dependencies: tuple[str, ...]
    scope_constraints: tuple[str, ...]
    non_scope: tuple[str, ...]


TYPE_CLASS = "type_or_category_concept"
EXPRESSION_CLASS = "expression_representation_communication_concept"
EVENT_CLASS = "occurrence_event_or_change_concept"
STATE_CLASS = "state_or_condition_concept"


def rc(
    role_key: str,
    requirement: Requirement,
    cardinality: Cardinality,
    *,
    condition_key: str | None = None,
    co: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
    classes: tuple[str, ...] = (),
) -> RoleConstraintDefinition:
    return RoleConstraintDefinition(
        role_key=role_key,
        requirement=requirement,
        cardinality=cardinality,
        condition_key=condition_key,
        co_required_role_keys=co,
        conflicting_role_keys=conflicts,
        allowed_semantic_class_keys=classes,
    )


FRAME_DEFINITIONS: Final[tuple[FrameDefinition, ...]] = (
    FrameDefinition(
        frame_key="inspect_read_only",
        action_root_key="inspect",
        label="Read-Only Inspection Frame",
        definition=(
            "A controlled predicate frame for representing non-state-changing examination of an "
            "action subject. It may preserve sources, methods, conditions, standards, purported "
            "results, and internal output targets without granting source access, validating truth, "
            "modifying the inspected subject, or invoking any capability."
        ),
        purpose="Represent bounded read-only inspection meaning without modification or proof.",
        role_constraints=(
            rc("initiator", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("actor", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("action_subject", Requirement.REQUIRED, Cardinality.ONE_OR_MORE, classes=(TYPE_CLASS, EXPRESSION_CLASS)),
            rc("content", Requirement.PROHIBITED, Cardinality.ZERO_OR_ONE, conflicts=("action_subject",), classes=(EXPRESSION_CLASS,)),
            rc("source", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
            rc("recipient", Requirement.PROHIBITED, Cardinality.ZERO_OR_ONE, conflicts=("output_target",), classes=(TYPE_CLASS,)),
            rc("instrument", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("condition", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(STATE_CLASS,)),
            rc("standard", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS, STATE_CLASS)),
            rc("result", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(EVENT_CLASS, STATE_CLASS)),
            rc("output_target", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
        ),
        permitted_speech_acts=ALL_SPEECH_ACT_CONTEXTS,
        effect_classification=Effect.READ_ONLY,
        authority_dependencies=(
            "Document 6 selected-meaning and gate authority",
            "source access privacy and identity authority where material",
            "Document 7 evidence boundary where observations are treated as evidence",
            "Slice 38F effect-boundary and capability-reference authority",
            "Document 9 verification before implementation acceptance",
            "Document 10 implementation authority",
        ),
        scope_constraints=(
            "inspection must remain non-state-changing",
            "inspection observations must remain distinct from verified status",
            "source access must remain external and unsatisfied",
        ),
        non_scope=("modification", "installation", "proof", "delivery", "memory write"),
    ),
    FrameDefinition(
        frame_key="report_attributed_content",
        action_root_key="report",
        label="Attributed Content Report Frame",
        definition=(
            "A controlled predicate frame for representing attributed report content and related "
            "participants. It preserves the distinction between reported material, source material, "
            "purported results, addressees, and internal output targets without treating a report as "
            "live observation, evidence, proof, delivery, or memory persistence."
        ),
        purpose="Represent attributed report meaning without evidence or delivery authority.",
        role_constraints=(
            rc("initiator", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("actor", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("action_subject", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(TYPE_CLASS, EXPRESSION_CLASS)),
            rc("content", Requirement.REQUIRED, Cardinality.ONE_OR_MORE, classes=(EXPRESSION_CLASS, EVENT_CLASS, STATE_CLASS)),
            rc("source", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
            rc("recipient", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(TYPE_CLASS,)),
            rc("instrument", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("condition", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(STATE_CLASS,)),
            rc("standard", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS, STATE_CLASS)),
            rc("result", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(EVENT_CLASS, STATE_CLASS)),
            rc("output_target", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
        ),
        permitted_speech_acts=ALL_SPEECH_ACT_CONTEXTS,
        effect_classification=Effect.COMMUNICATIVE_ONLY,
        authority_dependencies=(
            "Document 6 selected-meaning and speech-act authority",
            "Document 7 source attribution evidence and privacy governance",
            "delivery authorization where a recipient is materially implicated",
            "Slice 38F effect-boundary and capability-reference authority",
            "Document 9 verification before implementation acceptance",
            "Document 10 implementation authority",
        ),
        scope_constraints=(
            "reported content must remain attributed rather than proven",
            "recipient presence must not become delivery authorization",
            "purported result must remain distinct from verified result",
        ),
        non_scope=("live observation", "evidence validation", "proof", "delivery", "memory persistence"),
    ),
    FrameDefinition(
        frame_key="request_non_authorizing",
        action_root_key="request",
        label="Non-Authorizing Request Frame",
        definition=(
            "A controlled predicate frame for representing that an initiator communicates requested "
            "content or a requested action subject. The frame may preserve a requested actor, an "
            "explicitly directed recipient, conditions, standards, methods, sources, and internal "
            "output targets without creating permission, action authority, completion, or result."
        ),
        purpose="Represent request meaning while preserving request is not authorization.",
        role_constraints=(
            rc("initiator", Requirement.REQUIRED, Cardinality.EXACTLY_ONE, co=("content",), classes=(TYPE_CLASS,)),
            rc("actor", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("action_subject", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(TYPE_CLASS, EXPRESSION_CLASS)),
            rc("content", Requirement.REQUIRED, Cardinality.ONE_OR_MORE, co=("initiator",), classes=(EXPRESSION_CLASS, EVENT_CLASS)),
            rc("source", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
            rc("recipient", Requirement.CONDITIONAL, Cardinality.ZERO_OR_ONE, condition_key="explicit_directed_recipient_context", classes=(TYPE_CLASS,)),
            rc("instrument", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("condition", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(STATE_CLASS,)),
            rc("standard", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS, STATE_CLASS)),
            rc("result", Requirement.PROHIBITED, Cardinality.ZERO_OR_ONE, conflicts=("content",), classes=(EVENT_CLASS, STATE_CLASS)),
            rc("output_target", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
        ),
        permitted_speech_acts=ALL_SPEECH_ACT_CONTEXTS,
        effect_classification=Effect.NO_ACTION,
        authority_dependencies=(
            "Document 6 selected-meaning speech-act and gate authority",
            "separate permission and action authority",
            "recipient and delivery authority where materially implicated",
            "Slice 38F effect-boundary and capability-reference authority",
            "Document 9 verification before implementation acceptance",
            "Document 10 implementation authority",
        ),
        scope_constraints=(
            "request origin and requested content must remain structurally distinct",
            "directed recipient requirement is conditional and explicit",
            "result role is prohibited because a request does not establish completion",
        ),
        non_scope=("permission", "authorization", "execution", "completion", "verified result"),
    ),
    FrameDefinition(
        frame_key="verify_bounded_review",
        action_root_key="verify",
        label="Bounded Verification-Review Frame",
        definition=(
            "A controlled predicate frame for representing verification-oriented review of an action "
            "subject against a stated standard. Source material may become conditionally required "
            "when the verification basis depends on source evidence. The frame does not validate "
            "evidence, certify a result, establish proof, or invoke a verification capability."
        ),
        purpose="Represent bounded verification-review structure without verified-status authority.",
        role_constraints=(
            rc("initiator", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("actor", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("action_subject", Requirement.REQUIRED, Cardinality.ONE_OR_MORE, co=("standard",), classes=(TYPE_CLASS, EXPRESSION_CLASS, EVENT_CLASS, STATE_CLASS)),
            rc("content", Requirement.PROHIBITED, Cardinality.ZERO_OR_ONE, conflicts=("action_subject",), classes=(EXPRESSION_CLASS,)),
            rc("source", Requirement.CONDITIONAL, Cardinality.ONE_OR_MORE, condition_key="verification_basis_requires_source_material", classes=(EXPRESSION_CLASS, TYPE_CLASS)),
            rc("recipient", Requirement.PROHIBITED, Cardinality.ZERO_OR_ONE, conflicts=("output_target",), classes=(TYPE_CLASS,)),
            rc("instrument", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("condition", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(STATE_CLASS,)),
            rc("standard", Requirement.REQUIRED, Cardinality.EXACTLY_ONE, co=("action_subject",), classes=(TYPE_CLASS, STATE_CLASS)),
            rc("result", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(EVENT_CLASS, STATE_CLASS)),
            rc("output_target", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
        ),
        permitted_speech_acts=ALL_SPEECH_ACT_CONTEXTS,
        effect_classification=Effect.VERIFICATION_REVIEW_ONLY,
        authority_dependencies=(
            "Document 6 selected-meaning and gate authority",
            "Document 7 evidence source and verification-result governance",
            "standard-specific authority where material",
            "Slice 38F effect-boundary and capability-reference authority",
            "Document 9 verification before implementation acceptance",
            "Document 10 implementation authority",
        ),
        scope_constraints=(
            "verification subject and standard are co-required",
            "source material is conditionally required only under explicit source-basis condition",
            "purported result must not become verified status or proof",
        ),
        non_scope=("evidence validation", "proof", "certification", "capability invocation", "delivery"),
    ),
    FrameDefinition(
        frame_key="simulate_non_live",
        action_root_key="simulate",
        label="Non-Live Simulation Frame",
        definition=(
            "A controlled predicate frame for representing hypothetical modeling of an action subject "
            "under explicit conditions or assumptions. It may preserve modeled sources, methods, "
            "standards, results, and output targets while prohibiting live execution, runtime mutation, "
            "delivery, memory persistence, and treatment of simulated results as observed facts."
        ),
        purpose="Represent simulation meaning with an explicit assumption boundary and no live effect.",
        role_constraints=(
            rc("initiator", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("actor", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("action_subject", Requirement.REQUIRED, Cardinality.ONE_OR_MORE, co=("condition",), classes=(TYPE_CLASS, EXPRESSION_CLASS, EVENT_CLASS, STATE_CLASS)),
            rc("content", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(EXPRESSION_CLASS, EVENT_CLASS)),
            rc("source", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
            rc("recipient", Requirement.PROHIBITED, Cardinality.ZERO_OR_ONE, conflicts=("output_target",), classes=(TYPE_CLASS,)),
            rc("instrument", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(TYPE_CLASS,)),
            rc("condition", Requirement.REQUIRED, Cardinality.ONE_OR_MORE, co=("action_subject",), classes=(STATE_CLASS,)),
            rc("standard", Requirement.CONDITIONAL, Cardinality.ZERO_OR_ONE, condition_key="simulation_comparison_or_evaluation_context", classes=(TYPE_CLASS, STATE_CLASS)),
            rc("result", Requirement.OPTIONAL, Cardinality.ZERO_OR_MORE, classes=(EVENT_CLASS, STATE_CLASS)),
            rc("output_target", Requirement.OPTIONAL, Cardinality.ZERO_OR_ONE, classes=(EXPRESSION_CLASS, TYPE_CLASS)),
        ),
        permitted_speech_acts=ALL_SPEECH_ACT_CONTEXTS,
        effect_classification=Effect.SIMULATION_ONLY,
        authority_dependencies=(
            "Document 6 selected-meaning and gate authority",
            "explicit assumption and hypothetical-status custody",
            "separate live runtime memory delivery and economic authority",
            "Slice 38F effect-boundary and capability-reference authority",
            "Document 9 verification before implementation acceptance",
            "Document 10 implementation authority",
        ),
        scope_constraints=(
            "action subject and condition are co-required",
            "simulated result must remain modeled and non-live",
            "simulation inputs must not become execution arguments",
        ),
        non_scope=("live execution", "runtime mutation", "memory write", "delivery", "observed-result proof"),
    ),
)


STRUCTURAL_STATE_DEFINITIONS: Final[tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...]] = (
    (
        "structurally_complete",
        "All required and triggered conditional roles are represented, prohibited roles are absent, role conflicts are absent, and exact concept compatibility is supported within frame scope. This state remains architecture-only and is not permission.",
        (
            "required roles satisfied under exact frame constraints",
            "triggered conditional roles satisfied",
            "no prohibited or conflicting role functions",
            "exact concept compatibility supported",
            "scope and speech-act constraints preserved",
        ),
        (
            "permission", "gate passage", "selected meaning", "capability binding", "execution",
        ),
    ),
    (
        "structurally_incomplete",
        "One or more required, triggered conditional, concept, scope, or co-requirement conditions remain missing or unresolved.",
        (
            "required role missing", "conditional role missing after explicit trigger",
            "co-required role missing", "exact concept support absent", "scope condition unresolved",
        ),
        (
            "default filling", "clarification by this layer", "refusal by this layer", "capability routing", "execution",
        ),
    ),
    (
        "ambiguous",
        "Multiple materially distinct frame or role-constraint structures remain supportable and none may be selected by convenience or similarity.",
        ("multiple frame identities remain possible", "material role function remains multiply supportable"),
        ("ranking", "nearest-frame substitution", "LLM resolution", "automatic clarification", "execution"),
    ),
    (
        "conflicted",
        "Frame requirements, prohibited roles, mutually exclusive role functions, concept constraints, scope conditions, or effect boundaries cannot coexist safely.",
        ("prohibited role present", "conflicting roles co-present", "effect-boundary conflict", "scope contradiction"),
        ("silent dropping", "automatic refusal", "automatic correction", "capability routing", "execution"),
    ),
    (
        "unsupported",
        "No admitted frame structure, role identity, concept compatibility, or required dependency lawfully supports the represented action meaning.",
        ("no admitted frame support", "required role category unsupported", "concept support unsupported"),
        ("fallback", "nearest-frame substitution", "automatic refusal", "capability routing", "execution"),
    ),
    (
        "unknown",
        "The material action-bearing structure cannot be identified under admitted frame, role, speech-act, scope, or concept authority.",
        ("unknown action-root relation", "unknown frame relation", "unknown role structure", "unknown concept support"),
        ("guessing", "similarity substitution", "selection", "capability routing", "execution"),
    ),
)
