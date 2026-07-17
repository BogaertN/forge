"""Human-approved Slice 38C action-root selection authority.

The five definitions in this module are admitted because together they prove
five materially different Document 5 authority boundaries while remaining
small enough to audit as a closed set:

* inspect — read-only examination is not modification;
* report — a report is not observation, evidence, or proof;
* request — asking for action is not permission or execution;
* verify — verification meaning is not verified status or proof;
* simulate — hypothetical modeling is not live execution.

Higher-consequence candidates such as approve, install, send, remember, and
rollback remain deferred until participant roles, frames, effect boundaries,
and capability-reference law exist in Slices 38D through 38F.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..schema import PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES


SLICE38C_DECISION_OWNER_REF: Final[str] = "nicholas-jacob-bogaert"
SLICE38C_HUMAN_APPROVAL_REF: Final[str] = (
    "aiweb-slice38c-decision-owner-minimal-action-root-registry-authorization"
)
SLICE38C_NAMESPACE_KEY: Final[str] = (
    "aiweb:language-core:predicate-role-frame:action-root-registry"
)
SLICE38C_NAMESPACE_LABEL: Final[str] = (
    "AI.Web Language-Core Built-In Action-Root Registry"
)
SLICE38C_NAMESPACE_DEFINITION: Final[str] = (
    "The closed internal namespace for the first five Forge-owned action-root "
    "identities admitted under Document 5. Namespace membership supplies only "
    "controlled predicate identity and exact read-only registry reference. It "
    "does not supply surface-language mapping, occurrence interpretation, "
    "speech-act force, participant roles, frames, capabilities, routes, "
    "permission, execution, evidence, memory, rendering, or delivery authority."
)

SLICE38C_NAMESPACE_SCOPE: Final[tuple[str, ...]] = (
    "namespace:aiweb:language-core:predicate-role-frame:action-root-registry",
    "domain:forge-language-core",
    "authority:controlled-action-root-identity-only",
)
SLICE38C_NAMESPACE_NON_SCOPE: Final[tuple[str, ...]] = (
    "surface-language lookup or normalization",
    "source-occurrence interpretation or predicate selection",
    "speech-act, participant-role, predicate-frame, or effect-boundary completion",
    "capability, route, tool, permission, invocation, or execution authority",
    "evidence validation, memory access, rendering, delivery, or release",
)
SLICE38C_NAMESPACE_PERMITTED_USES: Final[tuple[str, ...]] = (
    "identify the exact internal namespace of Slice 38C action-root resources",
    "support deterministic read-only identity and internal-key inspection",
    "support provenance, version, lifecycle, and closed-set verification",
)
SLICE38C_COMMON_PROHIBITED_USES: Final[tuple[str, ...]] = (
    "surface verb, phrase, alias, synonym, or fuzzy lookup",
    "source-occurrence interpretation, intent inference, or predicate selection",
    "nearest-known action-root substitution",
    "semantic-similarity, embedding, vector, classifier, RAG, or LLM authority",
    "concept-to-predicate conversion",
    "speech-act inference or completion",
    "participant-role assignment or frame completion",
    "effect-boundary satisfaction or authority satisfaction",
    "capability-family availability, routing, dispatch, invocation, or execution",
    "evidence validation, proof, verified-status, or result certification",
    "memory read, write, deletion, disclosure, or persistence",
    "file modification, software installation, rollback, or runtime mutation",
    "outward rendering, publication, delivery, release, or production-readiness claim",
    "external linguistic resource admission or runtime loading",
)
SLICE38C_PROHIBITED_AUTHORITIES: Final[tuple[str, ...]] = (
    PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES
)
SLICE38C_ADDITIONAL_AUTHORITY_LIMITATIONS: Final[tuple[str, ...]] = (
    "registry membership is not source-expression applicability",
    "exact internal key lookup is not lexical or occurrence lookup",
    "admitted action root is not a selected predicate for any occurrence",
    "action-root identity is not speech-act force",
    "action-root identity is not participant-role or predicate-frame completeness",
    "action-root identity is not capability availability, route, invocation, or execution",
    "report identity is not report truth, live observation, evidence, or proof",
    "request identity is not permission, authorization, or execution",
    "verify identity is not verified status, evidence validity, or proof",
    "simulate identity is not live execution or implementation",
    "inspect identity is read-only meaning and not modification authority",
)
SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES: Final[tuple[str, ...]] = (
    "approve",
    "install",
    "send",
    "remember",
    "rollback",
)


@dataclass(frozen=True, slots=True)
class BuiltInActionRootDefinition:
    action_root_key: str
    predicate_key: str
    preferred_label: str
    definition: str
    explicit_exclusions: tuple[str, ...]
    authority_document: str
    authority_section: str
    source_reference: str
    scope: tuple[str, ...]
    non_scope: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    prohibited_authorities: tuple[str, ...] = SLICE38C_PROHIBITED_AUTHORITIES


BUILT_IN_ACTION_ROOT_DEFINITIONS: Final[
    tuple[BuiltInActionRootDefinition, ...]
] = (
    BuiltInActionRootDefinition(
        action_root_key="inspect",
        predicate_key="inspect",
        preferred_label="Inspect",
        definition=(
            "The controlled action meaning of bounded read-only examination of "
            "an identified subject or source without changing it. The root does "
            "not identify a source occurrence, complete participant roles, "
            "authorize access, perform examination, modify content, or certify a result."
        ),
        explicit_exclusions=(
            "not modification, write, install, delete, repair, or rollback",
            "not proof that inspection occurred or that a reported result is correct",
            "not permission to access a file, source, runtime, memory, or external resource",
        ),
        authority_document="Document 5 — RMC Predicate–Role Frame Registry v1",
        authority_section="Sections 1, 24, 25, and 46",
        source_reference="document5:action-root:inspect:read-only-boundary",
        scope=(*SLICE38C_NAMESPACE_SCOPE, "action-root-scope:read-only-inspection"),
        non_scope=(*SLICE38C_NAMESPACE_NON_SCOPE, "modification or state change"),
        permitted_uses=(
            "represent the exact controlled action-root identity for read-only inspection meaning",
            "support exact internal identity and key inspection",
            "anchor future role and frame work only after separately authorized later slices",
        ),
        prohibited_uses=SLICE38C_COMMON_PROHIBITED_USES,
    ),
    BuiltInActionRootDefinition(
        action_root_key="report",
        predicate_key="report",
        preferred_label="Report",
        definition=(
            "The controlled communicative action meaning of presenting a claim, "
            "status, account, or purported result as attributed content. The root "
            "does not establish that the report is true, observed live, supported "
            "by evidence, verified, accepted, rendered, or delivered."
        ),
        explicit_exclusions=(
            "not live observation, evidence, verified status, proof, or receipt",
            "not outward rendering, publication, delivery, or release authorization",
            "not the embedded action described by the report",
        ),
        authority_document="Document 5 — RMC Predicate–Role Frame Registry v1",
        authority_section="Sections 1, 20, 24, and 25",
        source_reference="document5:action-root:report:claim-not-proof-boundary",
        scope=(*SLICE38C_NAMESPACE_SCOPE, "action-root-scope:communicative-report"),
        non_scope=(*SLICE38C_NAMESPACE_NON_SCOPE, "truth, evidence, proof, or delivery"),
        permitted_uses=(
            "represent the exact controlled action-root identity for reporting meaning",
            "preserve that reported content remains attributed rather than proven",
            "anchor future speech-act and frame work only after separately authorized later slices",
        ),
        prohibited_uses=SLICE38C_COMMON_PROHIBITED_USES,
    ),
    BuiltInActionRootDefinition(
        action_root_key="request",
        predicate_key="request",
        preferred_label="Request",
        definition=(
            "The controlled communicative action meaning of asking that an action, "
            "review, response, or later consideration occur. The root records only "
            "request-type action meaning and does not prove requester authority, "
            "supply permission, complete the embedded action, or authorize execution."
        ),
        explicit_exclusions=(
            "not permission, authorization, approval, capability availability, or execution",
            "not proof that the requester controls the target or has required authority",
            "not selection of the embedded requested action for a source occurrence",
        ),
        authority_document="Document 5 — RMC Predicate–Role Frame Registry v1",
        authority_section="Sections 1, 15, 18, 19, 24, and 25",
        source_reference="document5:action-root:request:request-not-authority-boundary",
        scope=(*SLICE38C_NAMESPACE_SCOPE, "action-root-scope:communicative-request"),
        non_scope=(*SLICE38C_NAMESPACE_NON_SCOPE, "permission or execution"),
        permitted_uses=(
            "represent the exact controlled action-root identity for request meaning",
            "preserve that a request remains separate from authority and consequence",
            "anchor future speech-act and frame work only after separately authorized later slices",
        ),
        prohibited_uses=SLICE38C_COMMON_PROHIBITED_USES,
    ),
    BuiltInActionRootDefinition(
        action_root_key="verify",
        predicate_key="verify",
        preferred_label="Verify",
        definition=(
            "The controlled action meaning of checking an identified claim, record, "
            "condition, artifact, or result against an identified standard or proof "
            "requirement. The root does not perform the check, validate evidence, "
            "establish proof, or confer verified status."
        ),
        explicit_exclusions=(
            "not evidence validation, proof, authentication, certification, or verified status",
            "not live execution of a verifier, test suite, command, route, or capability",
            "not authority to rely on a source, report, receipt, or claimed result",
        ),
        authority_document="Document 5 — RMC Predicate–Role Frame Registry v1",
        authority_section="Sections 1, 20, 24, 25, and 46",
        source_reference="document5:action-root:verify:verification-not-proof-boundary",
        scope=(*SLICE38C_NAMESPACE_SCOPE, "action-root-scope:bounded-verification-meaning"),
        non_scope=(*SLICE38C_NAMESPACE_NON_SCOPE, "evidence validation or proof"),
        permitted_uses=(
            "represent the exact controlled action-root identity for bounded verification meaning",
            "preserve the distinction between verification meaning and verified result",
            "anchor future evidence-sensitive frame work only after separately authorized later slices",
        ),
        prohibited_uses=SLICE38C_COMMON_PROHIBITED_USES,
    ),
    BuiltInActionRootDefinition(
        action_root_key="simulate",
        predicate_key="simulate",
        preferred_label="Simulate",
        definition=(
            "The controlled action meaning of bounded hypothetical, modeled, or "
            "non-live representation of possible behavior or outcome. The root "
            "does not run a live target, apply code, invoke a capability, change "
            "state, establish real-world occurrence, or certify predictive truth."
        ),
        explicit_exclusions=(
            "not live execution, installation, invocation, application, or state change",
            "not proof that a modeled outcome will occur or that a real action occurred",
            "not permission to access or operate a runtime, tool, route, capability, or external system",
        ),
        authority_document="Document 5 — RMC Predicate–Role Frame Registry v1",
        authority_section="Sections 1, 15, 18, 24, 25, 45, and 46",
        source_reference="document5:action-root:simulate:hypothetical-not-execution-boundary",
        scope=(*SLICE38C_NAMESPACE_SCOPE, "action-root-scope:bounded-simulation-meaning"),
        non_scope=(*SLICE38C_NAMESPACE_NON_SCOPE, "live execution or implementation"),
        permitted_uses=(
            "represent the exact controlled action-root identity for bounded simulation meaning",
            "preserve that simulation remains hypothetical and non-live",
            "anchor future simulation frame work only after separately authorized later slices",
        ),
        prohibited_uses=SLICE38C_COMMON_PROHIBITED_USES,
    ),
)

BUILT_IN_ACTION_ROOT_KEYS: Final[tuple[str, ...]] = tuple(
    definition.action_root_key for definition in BUILT_IN_ACTION_ROOT_DEFINITIONS
)
BUILT_IN_PREDICATE_KEYS: Final[tuple[str, ...]] = tuple(
    definition.predicate_key for definition in BUILT_IN_ACTION_ROOT_DEFINITIONS
)
