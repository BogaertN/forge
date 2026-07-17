"""Human-approved Slice 38D participant-role admission authority.

The admitted set is deliberately smaller and safer than the roadmap's review
list.  Eleven roles are admitted because they are sufficient to let the five
Slice 38C action roots receive future frame structure without confusing role
identity with role assignment, effect, permission, proof, capability, or
execution.  ``affected_entity`` and ``location`` remain deferred:

* ``affected_entity`` is too broad before Slice 38E can separate read-only
  subjects from modification, memory, runtime, delivery, and other effectful
  targets.  Slice 38D therefore admits the narrower ``action_subject`` role.
* ``location`` is deferred because a location-like value can mean physical
  place, source location, file path, route, destination, runtime target, or
  output target; those distinctions require frame and effect-boundary law.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


SLICE38D_DECISION_OWNER_REF: Final[str] = "nicholas-jacob-bogaert"
SLICE38D_HUMAN_APPROVAL_REF: Final[str] = (
    "aiweb-slice38d-decision-owner-participant-role-registry-authorization"
)
SLICE38D_NAMESPACE_KEY: Final[str] = (
    "aiweb:language-core:predicate-role-frame:participant-role-registry"
)
SLICE38D_NAMESPACE_LABEL: Final[str] = (
    "AI.Web Language-Core Participant-Role Registry"
)
SLICE38D_NAMESPACE_DEFINITION: Final[str] = (
    "The closed Forge-owned namespace for controlled participant-role identity, "
    "role dependency, role distinction, lifecycle ancestry, correction support, "
    "and conflict support. Namespace membership does not assign any role to a "
    "source span, concept candidate, grammatical position, action occurrence, "
    "person, document, system, or result."
)

SLICE38D_NAMESPACE_SCOPE: Final[tuple[str, ...]] = (
    "namespace:aiweb:language-core:predicate-role-frame:participant-role-registry",
    "domain:forge-language-core",
    "authority:participant-role-identity-only",
    "lifecycle:architecture-governance-only",
)
SLICE38D_NAMESPACE_NON_SCOPE: Final[tuple[str, ...]] = (
    "surface-language role lookup or normalization",
    "source-occurrence role assignment or participant identification",
    "concept-candidate conversion into participant role",
    "semantic-relation conversion into participant role",
    "source-span conversion into actor identity",
    "grammatical-position conversion into participant role",
    "predicate-frame population, completion, or selected meaning",
    "capability, route, tool, permission, invocation, or execution authority",
    "evidence validation, memory access, rendering, delivery, or release",
)
SLICE38D_NAMESPACE_PERMITTED_USES: Final[tuple[str, ...]] = (
    "identify exact Forge-owned participant-role identities",
    "preserve version, provenance, scope, non-scope, and lifecycle ancestry",
    "preserve explicit role dependencies and must-remain-distinct relationships",
    "support exact read-only identity and internal-key inspection",
    "support correction and conflict record validation without inventing an incident",
)

SLICE38D_COMMON_PROHIBITED_USES: Final[tuple[str, ...]] = (
    "surface word, phrase, alias, synonym, stemming, or fuzzy role lookup",
    "source-occurrence interpretation, participant identification, or role assignment",
    "concept candidate, concept identity, sense identity, or semantic relation as role assignment",
    "source span, token position, dependency label, grammatical subject, or object as role assignment",
    "nearest-known role substitution or similarity-based role inference",
    "embedding, vector, classifier, RAG, learned parser, or LLM role authority",
    "predicate-frame completion, candidate meaning selection, or selected meaning",
    "permission, consent, identity verification, authority satisfaction, or gate outcome",
    "capability-family binding, route selection, tool invocation, or execution",
    "evidence validation, proof, verified status, result certification, or receipt validation",
    "memory read, write, deletion, disclosure, correction, or persistence",
    "file access, file modification, installation, rollback, deployment, or runtime mutation",
    "outward rendering, publication, delivery, release, or production-readiness claim",
    "external linguistic resource admission, runtime loading, or direct role import",
)
SLICE38D_AUTHORITY_LIMITATIONS: Final[tuple[str, ...]] = (
    "semantic relation is not participant role",
    "concept candidate is not role assignment",
    "source span is not actor",
    "grammatical position is not participant role",
    "participant identity is not participant-role identity",
    "role identity is not role assignment",
    "role compatibility is not role assignment",
    "role presence is not frame completeness",
    "initiator is not actor, permission holder, or verified identity",
    "actor is not verified performer or execution proof",
    "action subject is not affected entity, modification target, or runtime target",
    "source is not evidence validity, proof, or authority source",
    "recipient is not delivery target or delivery authorization",
    "instrument is not capability binding, route, invocation, or execution",
    "condition is not condition satisfaction or gate outcome",
    "standard is not compliance, proof, or verified status",
    "result is not occurrence proof, receipt, or certification",
    "output target is not destination, file path, publication, or delivery authorization",
)
SLICE38D_DEFERRED_ROLE_CANDIDATES: Final[tuple[str, ...]] = (
    "affected_entity",
    "location",
    "evidence_item",
    "permission_holder",
    "authority_source",
    "memory_target",
    "runtime_target",
    "delivery_target",
    "risk_subject",
    "identity_subject",
    "economic_actor",
    "external_resource_subject",
    "receipt",
)


@dataclass(frozen=True, slots=True)
class ParticipantRoleDefinition:
    role_key: str
    preferred_label: str
    role_category_key: str
    definition: str
    explicit_exclusions: tuple[str, ...]
    authority_section: str
    source_reference: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...] = SLICE38D_COMMON_PROHIBITED_USES


ROLE_DEFINITIONS: Final[tuple[ParticipantRoleDefinition, ...]] = (
    ParticipantRoleDefinition(
        role_key="initiator",
        preferred_label="Initiator",
        role_category_key="requester_and_initiating_participant",
        definition=(
            "The participant represented as originating an action-bearing or "
            "communicative event within a future predicate frame. Initiation "
            "records structural origin only; it does not establish identity, "
            "authority, permission, authorship, performance, or execution."
        ),
        explicit_exclusions=(
            "not actor or verified performer",
            "not permission holder, authority source, or consent record",
            "not proof that a person or system originated a live event",
        ),
        authority_section="Document 5 Sections 29, 31.19, 31.32, and 38",
        source_reference="document5:participant-role:initiator",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:structural-initiation"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "authority or verified authorship"),
        permitted_uses=(
            "identify the exact Forge-owned initiator role",
            "preserve a future frame distinction between initiator and actor",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="actor",
        preferred_label="Actor",
        role_category_key="actor_and_performer",
        definition=(
            "The participant represented as performing or undertaking the "
            "action described by a future predicate frame. The role describes "
            "frame-level participant function only and does not prove identity, "
            "actual performance, capability invocation, or action occurrence."
        ),
        explicit_exclusions=(
            "not initiator by default",
            "not verified identity or verified performer",
            "not execution, action receipt, or result proof",
        ),
        authority_section="Document 5 Sections 29, 31.20, 32, 33, and 38",
        source_reference="document5:participant-role:actor",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:represented-performer"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "verified performance or identity"),
        permitted_uses=(
            "identify the exact Forge-owned actor role",
            "preserve actor versus initiator and source distinctions",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="action_subject",
        preferred_label="Action Subject",
        role_category_key="object_affected_participant_and_action_target",
        definition=(
            "The participant that a future non-executing predicate frame is "
            "structurally about or toward. This narrower role is admitted instead "
            "of the broader affected-entity candidate so read-only inspection, "
            "verification, reporting, and simulation do not imply modification "
            "or actual effect."
        ),
        explicit_exclusions=(
            "not proof that the participant was affected",
            "not modification, memory, runtime, installation, or delivery target",
            "not grammatical object or source span by position alone",
        ),
        authority_section="Document 5 Sections 29.4, 31.21, 38.66, and 46",
        source_reference="document5:participant-role:action-subject-narrowed",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:non-effectful-action-subject"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "state-changing or specialized target"),
        permitted_uses=(
            "identify the exact Forge-owned action-subject role",
            "preserve read-only subject meaning without claiming effect",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="content",
        preferred_label="Content",
        role_category_key="communicative_content",
        definition=(
            "The information or material represented as carried, requested, "
            "reported, simulated, or expressed in a future frame. Content is not "
            "automatically source, evidence, action subject, result, recipient, "
            "or output destination."
        ),
        explicit_exclusions=(
            "not source authority or evidence validity",
            "not action subject, recipient, or output target",
            "not outward rendering, publication, or delivery",
        ),
        authority_section="Document 5 Sections 31.18, 31.25, 31.29, and 39",
        source_reference="document5:participant-role:content",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:communicative-content"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "source proof or delivery"),
        permitted_uses=(
            "identify the exact Forge-owned content role",
            "preserve content versus source, subject, result, and target distinctions",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="source",
        preferred_label="Source",
        role_category_key="source_and_origin",
        definition=(
            "The participant represented as material, origin, attribution, or "
            "reference consulted by a future frame. Source participation does "
            "not establish source reliability, evidence status, proof, authority, "
            "live observation, or external-resource admission."
        ),
        explicit_exclusions=(
            "not evidence item, evidence validity, or proof",
            "not authority source or permission record",
            "not external-resource admission or live source access",
        ),
        authority_section="Document 5 Sections 29.5, 31.22, 32, 35, and 38",
        source_reference="document5:participant-role:source",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:source-material-or-origin"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "proof, reliability, or authority"),
        permitted_uses=(
            "identify the exact Forge-owned source role",
            "preserve source versus standard, content, evidence, and authority distinctions",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="recipient",
        preferred_label="Recipient",
        role_category_key="recipient_destination_and_audience",
        definition=(
            "The participant represented as the intended receiver or addressee "
            "of content in a future communicative frame. Recipient identity does "
            "not authorize delivery, establish destination, prove transmission, "
            "or identify an output target."
        ),
        explicit_exclusions=(
            "not delivery target, destination system, or output target",
            "not delivery authorization, consent, or disclosure permission",
            "not proof of transmission or receipt",
        ),
        authority_section="Document 5 Sections 29.5, 31.25, 36, 37, and 38",
        source_reference="document5:participant-role:recipient",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:intended-recipient"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "delivery or release"),
        permitted_uses=(
            "identify the exact Forge-owned recipient role",
            "preserve recipient versus output-target and delivery distinctions",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="instrument",
        preferred_label="Instrument",
        role_category_key="instrument_method_and_capability_implication",
        definition=(
            "The participant represented as a described method, tool, medium, "
            "or system involved in how an action is discussed. Instrument identity "
            "does not create a capability reference, bind a route, invoke a tool, "
            "or execute an action."
        ),
        explicit_exclusions=(
            "not capability family, capability argument, or route",
            "not tool selection, invocation, or execution",
            "not proof that a method or system was actually used",
        ),
        authority_section="Document 5 Sections 29, 31.26, 36, and 38",
        source_reference="document5:participant-role:instrument",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:described-instrument-or-method"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "capability binding or invocation"),
        permitted_uses=(
            "identify the exact Forge-owned instrument role",
            "preserve described method without capability or execution authority",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="condition",
        preferred_label="Condition",
        role_category_key="condition_constraint_and_limitation",
        definition=(
            "The participant function representing a prerequisite, constraint, "
            "limitation, exception, or dependency on an action-bearing meaning. "
            "Condition identity does not establish that the condition is true, "
            "satisfied, enforced, selected, or authorized."
        ),
        explicit_exclusions=(
            "not verified satisfaction or live status",
            "not gate outcome, permission, or runtime enforcement",
            "not grammatical subordinate clause by position alone",
        ),
        authority_section="Document 5 Sections 29, 31.30, 33, 37, and 38",
        source_reference="document5:participant-role:condition",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:semantic-condition-or-constraint"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "condition satisfaction or enforcement"),
        permitted_uses=(
            "identify the exact Forge-owned condition role",
            "preserve prerequisites and limitations without claiming satisfaction",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="standard",
        preferred_label="Standard",
        role_category_key="comparison_and_standard",
        definition=(
            "The participant represented as a criterion, rule, threshold, or "
            "reference against which a future frame may describe comparison or "
            "verification. Standard identity does not establish compliance, "
            "evidence validity, verified status, or proof."
        ),
        explicit_exclusions=(
            "not evidence, proof, or verified result",
            "not authority rule satisfaction or compliance finding",
            "not capability test execution",
        ),
        authority_section="Document 5 Sections 29, 31.24, 35, 37, and 38",
        source_reference="document5:participant-role:standard",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:comparison-or-verification-standard"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "proof, compliance, or authority"),
        permitted_uses=(
            "identify the exact Forge-owned standard role",
            "preserve standard versus source and result distinctions",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="result",
        preferred_label="Result",
        role_category_key="result_and_receipt",
        definition=(
            "The participant represented as an outcome, status, return, or "
            "purported result of an action-bearing meaning. Result identity does "
            "not prove occurrence, correctness, verification, receipt validity, "
            "delivery, memory state, or runtime state."
        ),
        explicit_exclusions=(
            "not proof that an action occurred",
            "not evidence validity, verified status, or receipt certification",
            "not delivery, memory, rollback, installation, or runtime-state proof",
        ),
        authority_section="Document 5 Sections 29, 31.35, 35, 37, and 38",
        source_reference="document5:participant-role:result",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:represented-result-or-status"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "occurrence proof or receipt validation"),
        permitted_uses=(
            "identify the exact Forge-owned result role",
            "preserve represented result without certifying occurrence or correctness",
        ),
    ),
    ParticipantRoleDefinition(
        role_key="output_target",
        preferred_label="Output Target",
        role_category_key="output_and_expression_target",
        definition=(
            "The participant represented as the intended internal expression "
            "target or output-form target of a future frame. Output-target identity "
            "does not establish recipient, destination, file path, route, rendering, "
            "publication, delivery, or release authority."
        ),
        explicit_exclusions=(
            "not recipient, delivery target, publication target, or destination system",
            "not file path, route parameter, UI field, or capability argument",
            "not rendering, validation, delivery, or release authorization",
        ),
        authority_section="Document 5 Sections 27.61, 31.25, 31.29, 36, and 38",
        source_reference="document5:participant-role:output-target",
        scope=(*SLICE38D_NAMESPACE_SCOPE, "role-scope:internal-expression-output-target"),
        non_scope=(*SLICE38D_NAMESPACE_NON_SCOPE, "destination, path, publication, or delivery"),
        permitted_uses=(
            "identify the exact Forge-owned output-target role",
            "preserve output-target versus recipient and delivery distinctions",
        ),
    ),
)

ADMITTED_PARTICIPANT_ROLE_KEYS: Final[tuple[str, ...]] = tuple(
    definition.role_key for definition in ROLE_DEFINITIONS
)


@dataclass(frozen=True, slots=True)
class RoleDistinctionDefinition:
    relationship_key: str
    left_role_key: str
    right_role_key: str
    definition: str


ROLE_DISTINCTION_DEFINITIONS: Final[tuple[RoleDistinctionDefinition, ...]] = (
    RoleDistinctionDefinition(
        relationship_key="initiator_must_remain_distinct_from_actor",
        left_role_key="initiator",
        right_role_key="actor",
        definition=(
            "Originating an action-bearing or communicative event is not the same "
            "participant function as performing the embedded action."
        ),
    ),
    RoleDistinctionDefinition(
        relationship_key="action_subject_must_remain_distinct_from_content",
        left_role_key="action_subject",
        right_role_key="content",
        definition=(
            "What an action is structurally about is not automatically the material "
            "carried, requested, reported, simulated, or expressed."
        ),
    ),
    RoleDistinctionDefinition(
        relationship_key="source_must_remain_distinct_from_standard",
        left_role_key="source",
        right_role_key="standard",
        definition=(
            "Material or origin consulted by a frame is not automatically the "
            "criterion against which a claim or result is assessed."
        ),
    ),
    RoleDistinctionDefinition(
        relationship_key="recipient_must_remain_distinct_from_output_target",
        left_role_key="recipient",
        right_role_key="output_target",
        definition=(
            "An intended receiver of content is not automatically the internal "
            "expression target, destination, route, or delivery target."
        ),
    ),
    RoleDistinctionDefinition(
        relationship_key="standard_must_remain_distinct_from_result",
        left_role_key="standard",
        right_role_key="result",
        definition=(
            "A criterion used for comparison or verification is not the outcome, "
            "status, proof, or receipt of that comparison."
        ),
    ),
)

ROLE_DEPENDENCY_REFS: Final[tuple[str, ...]] = (
    "slice38e:predicate-frame-context-required",
    "document5:action-root-context-required",
    "document4:concept-compatibility-review-required",
    "document3:speech-act-and-scope-preservation-required",
    "slice38e:effect-boundary-review-required",
)
