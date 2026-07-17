#!/usr/bin/env python3
"""Behavior and adversarial test for Slice 38B predicate governance."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from aiweb_language_core_bootstrap.predicate_role_frame_registry import (
    PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
    with_expected_predicate_resource_id,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.governed_lifecycle import (
    PREDICATE_LIFECYCLE_TRANSITION_RULES,
    SLICE38B_ACCEPTED_PARENT_HEAD,
    SLICE38B_ACCEPTED_PARENT_SUBJECT,
    SLICE38B_ACCEPTED_PARENT_TREE,
    PredicateGovernanceBatch,
    PredicateGovernanceValidationCode,
    PredicateGovernanceValidationError,
    PredicateLifecycleAuthorityRecord,
    PredicateLifecycleTransitionKind,
    PredicateLifecycleTransitionRecord,
    active_lifecycle_states,
    assert_governance_batch,
    assert_lifecycle_transition,
    evaluate_lifecycle_transition,
    expected_resource_lineage_id,
    nonoperative_lifecycle_states,
    parse_resource_version,
    resource_id,
    transition_rule,
    validate_governance_batch,
    validate_governance_batch_shape,
    validate_governed_resource,
    validate_lifecycle_authority_record,
    validate_lifecycle_transition_record_shape,
    validate_provenance_record,
    version_advances,
    version_compatible,
    with_expected_authority_id,
    with_expected_batch_id,
    with_expected_transition_id,
    with_recomputed_resource_id,
)


checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def has_code(report, code: PredicateGovernanceValidationCode) -> bool:
    return any(issue.code is code for issue in report.issues)


def provenance() -> PredicateProvenanceReference:
    return with_expected_predicate_resource_id(
        PredicateProvenanceReference(
            provenance_id="",
            authority_document="Document 5",
            authority_section="Section 48 and canonical Slice 38B roadmap ruling",
            source_kind="architecture_authority",
            source_reference="RMC Predicate-Role Frame Registry v1",
            version="v1",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            implementation_authorized=False,
            prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def namespace(
    *,
    provenance_ref: str,
    version: str,
    state: PredicateLifecycleState,
    key: str = "aiweb:predicate:governance_test",
    scope: tuple[str, ...] = ("schema_identity", "schema_validation"),
    non_scope: tuple[str, ...] = ("runtime_lookup", "action_execution"),
    prohibited_uses: tuple[str, ...] = (
        "runtime_selection",
        "capability_routing",
    ),
) -> PredicateNamespaceIdentity:
    return with_recomputed_resource_id(
        PredicateNamespaceIdentity(
            namespace_id="",
            namespace_key=key,
            label="Synthetic governed predicate namespace",
            definition="A deterministic non-runtime namespace used only by Slice 38B tests.",
            scope=scope,
            non_scope=non_scope,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance_ref,
            permitted_uses=("schema_validation", "lifecycle_validation"),
            prohibited_uses=prohibited_uses,
            unknown_state_policy="Unknown and unsupported action-like material remains explicit and is never substituted with a nearest known root.",
            prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def action_root(
    *,
    provenance_ref: str,
    namespace_id: str,
    version: str,
    state: PredicateLifecycleState,
    key: str = "synthetic_governed_action",
    scope: tuple[str, ...] = ("identity_shape", "dependency_declaration"),
    non_scope: tuple[str, ...] = (
        "surface_matching",
        "occurrence_selection",
        "execution",
    ),
    prohibited_uses: tuple[str, ...] = (
        "command_detection",
        "tool_dispatch",
        "action_execution",
    ),
) -> ActionRootIdentity:
    return with_recomputed_resource_id(
        ActionRootIdentity(
            action_root_id="",
            namespace_id=namespace_id,
            action_root_key=key,
            preferred_label="Synthetic governed action root",
            definition="A non-runtime action-root identity used only for deterministic governance testing.",
            scope=scope,
            non_scope=non_scope,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance_ref,
            concept_identity_refs=("controlled_concept:synthetic_action",),
            frame_dependency_required=True,
            participant_role_dependency_required=True,
            speech_act_separation_required=True,
            effect_boundary_dependency_required=True,
            capability_non_invocation_required=True,
            occurrence_selection_allowed=False,
            execution_authorized=False,
            unknown_state_policy="Unknown expressions remain unknown or unsupported and are not coerced to this action root.",
            permitted_uses=("identity_validation", "lifecycle_validation"),
            prohibited_uses=prohibited_uses,
            prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def predicate(
    *,
    provenance_ref: str,
    namespace_id: str,
    action_root_id: str,
    version: str,
    state: PredicateLifecycleState,
    key: str = "synthetic_governed_predicate",
) -> PredicateIdentity:
    return with_recomputed_resource_id(
        PredicateIdentity(
            predicate_id="",
            action_root_id=action_root_id,
            namespace_id=namespace_id,
            predicate_key=key,
            preferred_label="Synthetic governed predicate",
            definition="A non-runtime predicate identity used only for deterministic governance testing.",
            scope=("predicate_identity_shape", "action_root_dependency"),
            non_scope=("participant_assignment", "frame_completion", "execution"),
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance_ref,
            concept_identity_refs=("controlled_concept:synthetic_action",),
            participant_role_schema_refs=(),
            predicate_frame_schema_refs=(),
            effect_boundary_refs=(),
            capability_family_reference_refs=(),
            participant_role_dependency_required=True,
            predicate_frame_dependency_required=True,
            speech_act_separation_required=True,
            capability_non_invocation_required=True,
            occurrence_selection_allowed=False,
            selected_for_occurrence=False,
            execution_authorized=False,
            unknown_state_policy="Unknown or unsupported predicate use remains visible, non-operative, and unselected.",
            permitted_uses=("identity_validation", "lifecycle_validation"),
            prohibited_uses=("selected_interpretation", "route_binding", "execution"),
            prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def authority(
    *,
    provenance_ref: str,
    source_id: str,
    target_id: str,
    scope: tuple[str, ...],
    conflict_review: bool = True,
    unknown_review: bool = True,
    dependency_review: bool = True,
    unresolved: tuple[str, ...] = (),
    missing: tuple[str, ...] = (),
) -> PredicateLifecycleAuthorityRecord:
    return with_expected_authority_id(
        PredicateLifecycleAuthorityRecord(
            authority_id="",
            authority_provenance_ref=provenance_ref,
            decision_owner_ref="Nicholas Jacob Bogaert / AI.Web",
            human_approval_ref="slice38b-test-explicit-human-approval",
            human_approved=True,
            reason="Synthetic deterministic lifecycle test authority.",
            scope=scope,
            affected_record_refs=(source_id, target_id),
            prohibited_uses=(
                "runtime_activation",
                "registry_population",
                "nearest_known_substitution",
                "semantic_similarity_authority",
            ),
            unresolved_dependency_refs=unresolved,
            missing_authority_refs=missing,
            conflict_review_complete=conflict_review,
            unknown_state_review_complete=unknown_review,
            later_dependency_review_complete=dependency_review,
            version_compatibility_review_complete=True,
            scope_non_scope_review_complete=True,
            provenance_review_complete=True,
            lifecycle_review_complete=True,
            non_llm_provenance=True,
            nearest_known_substitution_allowed=False,
            semantic_similarity_authority_allowed=False,
            runtime_authorized=False,
            implementation_authorized=False,
            registry_population_authorized=False,
        )
    )


def transition(
    *,
    source,
    target,
    authority_record: PredicateLifecycleAuthorityRecord,
    kind: PredicateLifecycleTransitionKind,
    quarantine_causes: tuple[str, ...] = (),
    quarantine_requirements: tuple[str, ...] = (),
    resolved_quarantine_causes: tuple[str, ...] = (),
    superseding_resource_ref: str | None = None,
    blocked_reentry_keys: tuple[str, ...] = (),
    prior_disposition_transition_ref: str | None = None,
) -> PredicateLifecycleTransitionRecord:
    return with_expected_transition_id(
        PredicateLifecycleTransitionRecord(
            transition_id="",
            lineage_id=expected_resource_lineage_id(source),
            resource_kind=source.resource_kind,
            source_resource_id=resource_id(source),
            target_resource_id=resource_id(target),
            source_version=source.version,
            target_version=target.version,
            from_state=source.lifecycle_state,
            to_state=target.lifecycle_state,
            transition_kind=kind,
            authority_record_ref=authority_record.authority_id,
            quarantine_cause_refs=quarantine_causes,
            quarantine_release_requirement_refs=quarantine_requirements,
            resolved_quarantine_cause_refs=resolved_quarantine_causes,
            superseding_resource_ref=superseding_resource_ref,
            blocked_reentry_keys=blocked_reentry_keys,
            prior_disposition_transition_ref=prior_disposition_transition_ref,
            prior_record_preserved=True,
            automatic_transition=False,
            in_place_mutation_performed=False,
            nearest_known_substitution_performed=False,
            similarity_authority_used=False,
        )
    )


prov = provenance()
provenance_by_id = {prov.provenance_id: prov}

check(SLICE38B_ACCEPTED_PARENT_HEAD == "2809966f62d172cf8660f9acb343a92813e87d2b", "parent HEAD")
check(SLICE38B_ACCEPTED_PARENT_TREE == "b02d41d21c72e7eae3c39ce04e71286b1b5bcbb0", "parent tree")
check(SLICE38B_ACCEPTED_PARENT_SUBJECT == "Slice 38A action-root and predicate-identity core schema", "parent subject")
check(validate_provenance_record(prov).ok, "provenance validates")
check(parse_resource_version("v1") == (1, 0, 0), "parse v1")
check(parse_resource_version("v1.2") == (1, 2, 0), "parse v1.2")
check(parse_resource_version("v1.2.3") == (1, 2, 3), "parse v1.2.3")
for invalid in ("1", "v01", "v1.02", "v1.2.3.4", "v-1", " v1"):
    try:
        parse_resource_version(invalid)
    except ValueError:
        check(True, f"reject version {invalid}")
    else:
        check(False, f"reject version {invalid}")
check(version_advances("v1", "v1.1"), "version advances")
check(not version_advances("v1.1", "v1.1"), "equal version rejected")
check(version_compatible("v1.2", "v1.3"), "same-major compatible")
check(not version_compatible("v1.2", "v2"), "major version rejected")
check(len(active_lifecycle_states()) == 2, "two authority-active states")
check(PredicateLifecycleState.UNKNOWN in nonoperative_lifecycle_states(), "unknown nonoperative")
check(PredicateLifecycleState.UNSUPPORTED in nonoperative_lifecycle_states(), "unsupported nonoperative")
check(len(PREDICATE_LIFECYCLE_TRANSITION_RULES) >= 45, "substantial explicit transition matrix")
check(transition_rule(PredicateLifecycleState.CANDIDATE, PredicateLifecycleState.REVIEWED) is not None, "candidate review rule")
check(transition_rule(PredicateLifecycleState.UNKNOWN, PredicateLifecycleState.ADMITTED) is None, "unknown direct admission absent")
check(transition_rule(PredicateLifecycleState.ADMITTED, PredicateLifecycleState.WITHDRAWN) is None, "admitted withdrawal absent")

ns_candidate = namespace(provenance_ref=prov.provenance_id, version="v1", state=PredicateLifecycleState.CANDIDATE)
ns_reviewed = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.REVIEWED)
ns_admitted = namespace(provenance_ref=prov.provenance_id, version="v1.2", state=PredicateLifecycleState.ADMITTED)
check(validate_governed_resource(ns_candidate, provenance_by_id=provenance_by_id).ok, "candidate namespace validates")
check(expected_resource_lineage_id(ns_candidate) == expected_resource_lineage_id(ns_reviewed), "namespace lineage stable")
check(resource_id(ns_candidate) != resource_id(ns_reviewed), "version-record identity changes")
try:
    ns_candidate.label = "mutated"  # type: ignore[misc]
except (FrozenInstanceError, AttributeError):
    check(True, "records immutable")
else:
    check(False, "records immutable")

review_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=ns_candidate.namespace_id,
    target_id=ns_reviewed.namespace_id,
    scope=ns_reviewed.scope,
)
review_transition = transition(
    source=ns_candidate,
    target=ns_reviewed,
    authority_record=review_authority,
    kind=PredicateLifecycleTransitionKind.REVIEW,
)
review_decision = evaluate_lifecycle_transition(
    ns_candidate,
    ns_reviewed,
    review_transition,
    review_authority,
    provenance_by_id=provenance_by_id,
)
check(review_decision.allowed, "candidate to reviewed allowed")
check(assert_lifecycle_transition(
    ns_candidate,
    ns_reviewed,
    review_transition,
    review_authority,
    provenance_by_id=provenance_by_id,
).allowed, "assert transition returns allowed")

admit_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=ns_reviewed.namespace_id,
    target_id=ns_admitted.namespace_id,
    scope=ns_admitted.scope,
)
admit_transition = transition(
    source=ns_reviewed,
    target=ns_admitted,
    authority_record=admit_authority,
    kind=PredicateLifecycleTransitionKind.ADMISSION,
)
check(evaluate_lifecycle_transition(
    ns_reviewed,
    ns_admitted,
    admit_transition,
    admit_authority,
    provenance_by_id=provenance_by_id,
).allowed, "reviewed to admitted allowed")

# Admission may not skip review.
direct_admit_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=ns_candidate.namespace_id,
    target_id=ns_admitted.namespace_id,
    scope=ns_admitted.scope,
)
direct_admit = transition(
    source=ns_candidate,
    target=ns_admitted,
    authority_record=direct_admit_authority,
    kind=PredicateLifecycleTransitionKind.ADMISSION,
)
report = evaluate_lifecycle_transition(
    ns_candidate,
    ns_admitted,
    direct_admit,
    direct_admit_authority,
    provenance_by_id=provenance_by_id,
)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.TRANSITION_NOT_PERMITTED), "direct admission rejected")

# Unknown and unsupported states must return through candidate review and preserve lineage.
unknown = namespace(provenance_ref=prov.provenance_id, version="v1.3", state=PredicateLifecycleState.UNKNOWN)
unknown_candidate = namespace(provenance_ref=prov.provenance_id, version="v1.4", state=PredicateLifecycleState.CANDIDATE)
unknown_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=unknown.namespace_id,
    target_id=unknown_candidate.namespace_id,
    scope=unknown_candidate.scope,
)
unknown_transition = transition(
    source=unknown,
    target=unknown_candidate,
    authority_record=unknown_authority,
    kind=PredicateLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
)
check(evaluate_lifecycle_transition(
    unknown,
    unknown_candidate,
    unknown_transition,
    unknown_authority,
    provenance_by_id=provenance_by_id,
).allowed, "unknown returns only to same-lineage candidate review")

nearest = replace(unknown_transition, nearest_known_substitution_performed=True)
nearest = replace(nearest, transition_id=nearest.expected_id())
report = evaluate_lifecycle_transition(
    unknown,
    unknown_candidate,
    nearest,
    unknown_authority,
    provenance_by_id=provenance_by_id,
)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED), "nearest-known substitution rejected")

similarity = replace(unknown_transition, similarity_authority_used=True)
similarity = replace(similarity, transition_id=similarity.expected_id())
report = evaluate_lifecycle_transition(
    unknown,
    unknown_candidate,
    similarity,
    unknown_authority,
    provenance_by_id=provenance_by_id,
)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.SIMILARITY_AUTHORITY_PROHIBITED), "similarity authority rejected")

for field, code in (
    ("automatic_transition", PredicateGovernanceValidationCode.AUTOMATIC_TRANSITION_PROHIBITED),
    ("in_place_mutation_performed", PredicateGovernanceValidationCode.IN_PLACE_MUTATION_PROHIBITED),
):
    bad = replace(review_transition, **{field: True})
    bad = replace(bad, transition_id=bad.expected_id())
    report = evaluate_lifecycle_transition(ns_candidate, ns_reviewed, bad, review_authority, provenance_by_id=provenance_by_id)
    check(not report.allowed and has_code(report, code), f"reject {field}")

same_version = replace(ns_reviewed, version="v1")
same_version = with_recomputed_resource_id(same_version)
same_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=same_version.namespace_id, scope=same_version.scope)
same_transition = transition(source=ns_candidate, target=same_version, authority_record=same_authority, kind=PredicateLifecycleTransitionKind.REVIEW)
report = evaluate_lifecycle_transition(ns_candidate, same_version, same_transition, same_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.VERSION_NOT_ADVANCING), "same version rejected")

major = replace(ns_reviewed, version="v2")
major = with_recomputed_resource_id(major)
major_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=major.namespace_id, scope=major.scope)
major_transition = transition(source=ns_candidate, target=major, authority_record=major_authority, kind=PredicateLifecycleTransitionKind.REVIEW)
report = evaluate_lifecycle_transition(ns_candidate, major, major_transition, major_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.VERSION_INCOMPATIBLE), "breaking major rejected")

expanded = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.REVIEWED, scope=("schema_identity", "schema_validation", "new_authority"))
expanded_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=expanded.namespace_id, scope=expanded.scope)
expanded_transition = transition(source=ns_candidate, target=expanded, authority_record=expanded_authority, kind=PredicateLifecycleTransitionKind.REVIEW)
report = evaluate_lifecycle_transition(ns_candidate, expanded, expanded_transition, expanded_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.SCOPE_EXPANSION), "scope expansion rejected")

narrowed_non_scope = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.REVIEWED, non_scope=("runtime_lookup",))
narrowed_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=narrowed_non_scope.namespace_id, scope=narrowed_non_scope.scope)
narrowed_transition = transition(source=ns_candidate, target=narrowed_non_scope, authority_record=narrowed_authority, kind=PredicateLifecycleTransitionKind.REVIEW)
report = evaluate_lifecycle_transition(ns_candidate, narrowed_non_scope, narrowed_transition, narrowed_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.NON_SCOPE_NARROWING), "non-scope removal rejected")

removed_prohibition = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.REVIEWED, prohibited_uses=("runtime_selection",))
removed_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=removed_prohibition.namespace_id, scope=removed_prohibition.scope)
removed_transition = transition(source=ns_candidate, target=removed_prohibition, authority_record=removed_authority, kind=PredicateLifecycleTransitionKind.REVIEW)
report = evaluate_lifecycle_transition(ns_candidate, removed_prohibition, removed_transition, removed_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.PROHIBITED_USE_REMOVED), "prohibited-use removal rejected")

mutated_lineage = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.REVIEWED, key="aiweb:predicate:different")
mutated_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=mutated_lineage.namespace_id, scope=mutated_lineage.scope)
mutated_transition = transition(source=ns_candidate, target=mutated_lineage, authority_record=mutated_authority, kind=PredicateLifecycleTransitionKind.REVIEW)
report = evaluate_lifecycle_transition(ns_candidate, mutated_lineage, mutated_transition, mutated_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.LINEAGE_MISMATCH), "lineage mutation rejected")

missing_provenance = replace(ns_candidate, provenance_ref="missing:provenance")
missing_provenance = with_recomputed_resource_id(missing_provenance)
report = validate_governed_resource(missing_provenance, provenance_by_id=provenance_by_id)
check(not report.ok and has_code(report, PredicateGovernanceValidationCode.PROVENANCE_NOT_FOUND), "missing provenance rejected")

for field, code in (
    ("human_approved", PredicateGovernanceValidationCode.HUMAN_APPROVAL_REQUIRED),
    ("non_llm_provenance", PredicateGovernanceValidationCode.NON_LLM_PROVENANCE_REQUIRED),
    ("nearest_known_substitution_allowed", PredicateGovernanceValidationCode.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED),
    ("semantic_similarity_authority_allowed", PredicateGovernanceValidationCode.SIMILARITY_AUTHORITY_PROHIBITED),
    ("runtime_authorized", PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED),
    ("implementation_authorized", PredicateGovernanceValidationCode.IMPLEMENTATION_AUTHORITY_PROHIBITED),
    ("registry_population_authorized", PredicateGovernanceValidationCode.REGISTRY_POPULATION_PROHIBITED),
):
    bad = replace(review_authority, **{field: not getattr(review_authority, field)})
    bad = replace(bad, authority_id=bad.expected_id())
    report = validate_lifecycle_authority_record(bad, provenance_by_id=provenance_by_id)
    check(not report.ok and has_code(report, code), f"authority rejects {field}")

# Withdrawal is explicit and cannot be used to erase admitted authority.
withdrawn = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.WITHDRAWN)
withdraw_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=withdrawn.namespace_id, scope=withdrawn.scope)
withdraw_transition = transition(source=ns_candidate, target=withdrawn, authority_record=withdraw_authority, kind=PredicateLifecycleTransitionKind.WITHDRAWAL)
check(evaluate_lifecycle_transition(ns_candidate, withdrawn, withdraw_transition, withdraw_authority, provenance_by_id=provenance_by_id).allowed, "candidate withdrawal allowed")

admitted_withdrawn = namespace(provenance_ref=prov.provenance_id, version="v1.3", state=PredicateLifecycleState.WITHDRAWN)
admitted_withdraw_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_admitted.namespace_id, target_id=admitted_withdrawn.namespace_id, scope=admitted_withdrawn.scope)
admitted_withdraw_transition = transition(source=ns_admitted, target=admitted_withdrawn, authority_record=admitted_withdraw_authority, kind=PredicateLifecycleTransitionKind.WITHDRAWAL)
report = evaluate_lifecycle_transition(ns_admitted, admitted_withdrawn, admitted_withdraw_transition, admitted_withdraw_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.TRANSITION_NOT_PERMITTED), "admitted withdrawal rejected")

reopened = namespace(provenance_ref=prov.provenance_id, version="v1.2", state=PredicateLifecycleState.CANDIDATE)
reopen_authority = authority(provenance_ref=prov.provenance_id, source_id=withdrawn.namespace_id, target_id=reopened.namespace_id, scope=reopened.scope)
reopen_transition = transition(source=withdrawn, target=reopened, authority_record=reopen_authority, kind=PredicateLifecycleTransitionKind.REOPEN_REVIEW)
report = evaluate_lifecycle_transition(withdrawn, reopened, reopen_transition, reopen_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED), "reopen requires disposition ancestry")
reopen_transition = transition(source=withdrawn, target=reopened, authority_record=reopen_authority, kind=PredicateLifecycleTransitionKind.REOPEN_REVIEW, prior_disposition_transition_ref=withdraw_transition.transition_id)
check(evaluate_lifecycle_transition(withdrawn, reopened, reopen_transition, reopen_authority, provenance_by_id=provenance_by_id).allowed, "withdrawn reopen with ancestry allowed")

# Quarantine, rejection, and supersession have dedicated custody requirements.
quarantined = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.QUARANTINED)
quarantine_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=quarantined.namespace_id, scope=quarantined.scope)
quarantine_transition = transition(source=ns_candidate, target=quarantined, authority_record=quarantine_authority, kind=PredicateLifecycleTransitionKind.QUARANTINE)
report = evaluate_lifecycle_transition(ns_candidate, quarantined, quarantine_transition, quarantine_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.QUARANTINE_CAUSE_REQUIRED), "quarantine cause required")
quarantine_transition = transition(source=ns_candidate, target=quarantined, authority_record=quarantine_authority, kind=PredicateLifecycleTransitionKind.QUARANTINE, quarantine_causes=("missing_authority:synthetic",), quarantine_requirements=("resolve_missing_authority",))
check(evaluate_lifecycle_transition(ns_candidate, quarantined, quarantine_transition, quarantine_authority, provenance_by_id=provenance_by_id).allowed, "bounded quarantine allowed")

rejected = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.REJECTED)
reject_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_candidate.namespace_id, target_id=rejected.namespace_id, scope=rejected.scope)
reject_transition = transition(source=ns_candidate, target=rejected, authority_record=reject_authority, kind=PredicateLifecycleTransitionKind.REJECTION)
report = evaluate_lifecycle_transition(ns_candidate, rejected, reject_transition, reject_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED), "rejection blocks equivalent reentry")

superseded = namespace(provenance_ref=prov.provenance_id, version="v1.3", state=PredicateLifecycleState.SUPERSEDED)
supersede_authority = authority(provenance_ref=prov.provenance_id, source_id=ns_admitted.namespace_id, target_id=superseded.namespace_id, scope=superseded.scope)
supersede_transition = transition(source=ns_admitted, target=superseded, authority_record=supersede_authority, kind=PredicateLifecycleTransitionKind.SUPERSESSION)
report = evaluate_lifecycle_transition(ns_admitted, superseded, supersede_transition, supersede_authority, provenance_by_id=provenance_by_id)
check(not report.allowed and has_code(report, PredicateGovernanceValidationCode.SUPERSEDING_RESOURCE_REQUIRED), "supersession successor required")

# Full valid batch: namespace observed -> candidate -> reviewed -> admitted,
# action-root candidate -> reviewed -> admitted, plus one non-operative predicate candidate.
ns_observed = namespace(provenance_ref=prov.provenance_id, version="v1", state=PredicateLifecycleState.OBSERVED)
ns_candidate_b = namespace(provenance_ref=prov.provenance_id, version="v1.1", state=PredicateLifecycleState.CANDIDATE)
ns_reviewed_b = namespace(provenance_ref=prov.provenance_id, version="v1.2", state=PredicateLifecycleState.REVIEWED)
ns_admitted_b = namespace(provenance_ref=prov.provenance_id, version="v1.3", state=PredicateLifecycleState.ADMITTED)

resources = [ns_observed, ns_candidate_b, ns_reviewed_b, ns_admitted_b]
authorities = []
transitions = []
for source, target, kind in (
    (ns_observed, ns_candidate_b, PredicateLifecycleTransitionKind.PROPOSAL),
    (ns_candidate_b, ns_reviewed_b, PredicateLifecycleTransitionKind.REVIEW),
    (ns_reviewed_b, ns_admitted_b, PredicateLifecycleTransitionKind.ADMISSION),
):
    auth = authority(provenance_ref=prov.provenance_id, source_id=resource_id(source), target_id=resource_id(target), scope=target.scope)
    tr = transition(source=source, target=target, authority_record=auth, kind=kind)
    authorities.append(auth)
    transitions.append(tr)

ar_candidate = action_root(provenance_ref=prov.provenance_id, namespace_id=ns_admitted_b.namespace_id, version="v1", state=PredicateLifecycleState.CANDIDATE)
ar_reviewed = action_root(provenance_ref=prov.provenance_id, namespace_id=ns_admitted_b.namespace_id, version="v1.1", state=PredicateLifecycleState.REVIEWED)
ar_admitted = action_root(provenance_ref=prov.provenance_id, namespace_id=ns_admitted_b.namespace_id, version="v1.2", state=PredicateLifecycleState.ADMITTED)
resources.extend((ar_candidate, ar_reviewed, ar_admitted))
for source, target, kind in (
    (ar_candidate, ar_reviewed, PredicateLifecycleTransitionKind.REVIEW),
    (ar_reviewed, ar_admitted, PredicateLifecycleTransitionKind.ADMISSION),
):
    auth = authority(provenance_ref=prov.provenance_id, source_id=resource_id(source), target_id=resource_id(target), scope=target.scope)
    tr = transition(source=source, target=target, authority_record=auth, kind=kind)
    authorities.append(auth)
    transitions.append(tr)

pred_candidate = predicate(provenance_ref=prov.provenance_id, namespace_id=ns_admitted_b.namespace_id, action_root_id=ar_admitted.action_root_id, version="v1", state=PredicateLifecycleState.CANDIDATE)
resources.append(pred_candidate)

batch = with_expected_batch_id(
    PredicateGovernanceBatch(
        batch_id="",
        provenance_records=(prov,),
        resources=tuple(resources),
        authority_records=tuple(authorities),
        transitions=tuple(transitions),
        registry_population_installed=False,
        action_root_lookup_installed=False,
        predicate_selection_installed=False,
        nearest_known_mapping_installed=False,
        semantic_similarity_installed=False,
        capability_routing_installed=False,
        runtime_activation_installed=False,
    )
)
check(validate_governance_batch_shape(batch).ok, "batch shape validates")
valid_batch_report = validate_governance_batch(batch)
if not valid_batch_report.ok:
    for issue in valid_batch_report.issues:
        print("VALID BATCH ISSUE", issue)
check(valid_batch_report.ok, "valid governance batch")
check(assert_governance_batch(batch).ok, "assert valid governance batch")
check(validate_governance_batch(batch) == validate_governance_batch(batch), "deterministic repeat report")

# Duplicate and conflict refusal.
duplicate_batch = with_expected_batch_id(replace(batch, resources=batch.resources + (batch.resources[0],)))
report = validate_governance_batch(duplicate_batch)
check(not report.ok and has_code(report, PredicateGovernanceValidationCode.EXACT_DUPLICATE_RECORD), "exact duplicate rejected")

conflicting = replace(ns_candidate_b, definition="A conflicting body at the same lineage version.")
conflicting = with_recomputed_resource_id(conflicting)
conflict_batch = with_expected_batch_id(replace(batch, resources=batch.resources + (conflicting,)))
report = validate_governance_batch(conflict_batch)
check(not report.ok and has_code(report, PredicateGovernanceValidationCode.CONFLICTING_LINEAGE_VERSION), "conflicting lineage version rejected")

broken_predicate = predicate(provenance_ref=prov.provenance_id, namespace_id=ns_admitted_b.namespace_id, action_root_id="missing:action_root", version="v1", state=PredicateLifecycleState.CANDIDATE, key="broken_predicate")
broken_batch = with_expected_batch_id(replace(batch, resources=batch.resources + (broken_predicate,)))
report = validate_governance_batch(broken_batch)
check(not report.ok and has_code(report, PredicateGovernanceValidationCode.REFERENCE_NOT_FOUND), "broken reference rejected")

for field in (
    "registry_population_installed",
    "action_root_lookup_installed",
    "predicate_selection_installed",
    "nearest_known_mapping_installed",
    "semantic_similarity_installed",
    "capability_routing_installed",
    "runtime_activation_installed",
):
    bad_batch = replace(batch, **{field: True})
    bad_batch = replace(bad_batch, batch_id=bad_batch.expected_id())
    report = validate_governance_batch_shape(bad_batch)
    check(not report.ok, f"batch rejects authority flag {field}")

try:
    assert_lifecycle_transition(
        ns_candidate,
        ns_admitted,
        direct_admit,
        direct_admit_authority,
        provenance_by_id=provenance_by_id,
    )
except PredicateGovernanceValidationError:
    check(True, "assert transition fails closed")
else:
    check(False, "assert transition fails closed")

# Additional fail-closed and ancestry-custody adversarial coverage.
permitted_expansion = replace(
    ns_reviewed,
    permitted_uses=ns_reviewed.permitted_uses + ("runtime_selection",),
)
permitted_expansion = with_recomputed_resource_id(permitted_expansion)
permitted_expansion_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=ns_candidate.namespace_id,
    target_id=permitted_expansion.namespace_id,
    scope=permitted_expansion.scope,
)
permitted_expansion_transition = transition(
    source=ns_candidate,
    target=permitted_expansion,
    authority_record=permitted_expansion_authority,
    kind=PredicateLifecycleTransitionKind.REVIEW,
)
report = evaluate_lifecycle_transition(
    ns_candidate,
    permitted_expansion,
    permitted_expansion_transition,
    permitted_expansion_authority,
    provenance_by_id=provenance_by_id,
)
check(
    not report.allowed
    and has_code(report, PredicateGovernanceValidationCode.PERMITTED_USE_ADDED),
    "permitted-use expansion rejected",
)

malformed_scope = replace(ns_candidate, scope=(["not", "text"],))
report = validate_governed_resource(
    malformed_scope,
    provenance_by_id=provenance_by_id,
)
check(
    not report.ok
    and has_code(report, PredicateGovernanceValidationCode.TYPE_MISMATCH),
    "malformed unhashable tuple member fails closed without exception",
)

malformed_transition_batch = PredicateGovernanceBatch(
    batch_id="malformed-batch",
    provenance_records=(),
    resources=(),
    authority_records=(),
    transitions=(object(),),
    registry_population_installed=False,
    action_root_lookup_installed=False,
    predicate_selection_installed=False,
    nearest_known_mapping_installed=False,
    semantic_similarity_installed=False,
    capability_routing_installed=False,
    runtime_activation_installed=False,
)
report = validate_governance_batch(malformed_transition_batch)
check(
    not report.ok
    and has_code(report, PredicateGovernanceValidationCode.TYPE_MISMATCH),
    "malformed batch member fails closed without exception",
)
check(
    not validate_lifecycle_transition_record_shape(object()).ok,
    "transition-shape validator rejects non-record input",
)

malformed_provenance = replace(prov, source_reference=object())
check(
    not validate_provenance_record(malformed_provenance).ok,
    "malformed provenance canonical body fails closed",
)
malformed_authority = replace(review_authority, reason=object())
check(
    not validate_lifecycle_authority_record(
        malformed_authority, provenance_by_id=provenance_by_id
    ).ok,
    "malformed authority canonical body fails closed",
)
malformed_batch_shape = replace(batch, resources=object())
check(
    not validate_governance_batch_shape(malformed_batch_shape).ok,
    "malformed batch collection fails closed",
)

# Every authority boolean must be an exact bool. Truthy strings and integers
# must never satisfy a mandatory review gate.
for boolean_field in (
    "conflict_review_complete",
    "unknown_state_review_complete",
    "later_dependency_review_complete",
):
    for malformed_boolean in (0, 1, "true", "false", None):
        malformed_review_authority = with_expected_authority_id(
            replace(
                review_authority,
                **{boolean_field: malformed_boolean},
            )
        )
        malformed_review_report = validate_lifecycle_authority_record(
            malformed_review_authority,
            provenance_by_id=provenance_by_id,
        )
        check(
            not malformed_review_report.ok
            and has_code(
                malformed_review_report,
                PredicateGovernanceValidationCode.TYPE_MISMATCH,
            ),
            f"authority review boolean requires exact bool: {boolean_field}={malformed_boolean!r}",
        )

check(
    not validate_governed_resource(
        ns_candidate,
        provenance_by_id=[],  # type: ignore[arg-type]
    ).ok,
    "malformed provenance index fails closed",
)

# Broad exact-dataclass malformed-field fuzzing. Public validation boundaries
# must always return a report or decision; they must never leak a Python
# exception because a field is unhashable, wrongly typed, or unserializable.
malformed_field_values = (
    None,
    object(),
    [],
    {},
    set(),
    1,
    1.5,
    True,
    b"x",
    "",
    " bad ",
    "\x00",
)
malformed_field_crashes: list[str] = []
malformed_field_cases = 0


def record_malformed_call(label: str, function, *args, **kwargs) -> None:
    global malformed_field_cases
    malformed_field_cases += 1
    try:
        function(*args, **kwargs)
    except Exception as error:  # pragma: no cover - failure detail only
        malformed_field_crashes.append(
            f"{label}:{type(error).__name__}:{error}"
        )


for record_name, record, validator, validator_kwargs in (
    ("provenance", prov, validate_provenance_record, {}),
    (
        "authority",
        review_authority,
        validate_lifecycle_authority_record,
        {"provenance_by_id": provenance_by_id},
    ),
    (
        "transition",
        review_transition,
        validate_lifecycle_transition_record_shape,
        {},
    ),
    ("batch", batch, validate_governance_batch, {}),
):
    for record_field in fields(record):
        for malformed_value in malformed_field_values:
            mutated = replace(record, **{record_field.name: malformed_value})
            record_malformed_call(
                f"{record_name}.{record_field.name}",
                validator,
                mutated,
                **validator_kwargs,
            )

for resource_position, resource in enumerate(batch.resources):
    for resource_field in fields(resource):
        for malformed_value in malformed_field_values:
            mutated_resource = replace(
                resource,
                **{resource_field.name: malformed_value},
            )
            record_malformed_call(
                f"resource[{resource_position}].{resource_field.name}.individual",
                validate_governed_resource,
                mutated_resource,
                provenance_by_id=provenance_by_id,
            )
            mutated_resources = list(batch.resources)
            mutated_resources[resource_position] = mutated_resource
            mutated_batch = replace(batch, resources=tuple(mutated_resources))
            record_malformed_call(
                f"resource[{resource_position}].{resource_field.name}.batch",
                validate_governance_batch,
                mutated_batch,
            )

for object_name, source_object, argument_position in (
    ("source", ns_candidate, 0),
    ("target", ns_reviewed, 1),
    ("transition", review_transition, 2),
    ("authority", review_authority, 3),
):
    for object_field in fields(source_object):
        for malformed_value in malformed_field_values:
            mutated_object = replace(
                source_object,
                **{object_field.name: malformed_value},
            )
            transition_arguments = [
                ns_candidate,
                ns_reviewed,
                review_transition,
                review_authority,
            ]
            transition_arguments[argument_position] = mutated_object
            record_malformed_call(
                f"evaluate.{object_name}.{object_field.name}",
                evaluate_lifecycle_transition,
                *transition_arguments,
                provenance_by_id=provenance_by_id,
            )

check(
    not malformed_field_crashes,
    "all malformed exact-dataclass fields fail closed without exception: "
    + " | ".join(malformed_field_crashes[:5]),
)


class ExplosiveEquality:
    def __eq__(self, other) -> bool:
        raise RuntimeError("malformed equality must not escape validation")


explosive_duplicate_authority = replace(
    review_authority,
    scope=(ExplosiveEquality(),),
)
explosive_duplicate_batch = replace(
    batch,
    authority_records=(review_authority, explosive_duplicate_authority),
)
try:
    explosive_duplicate_report = validate_governance_batch(
        explosive_duplicate_batch
    )
except Exception as error:  # pragma: no cover - failure detail only
    check(False, f"duplicate comparison fails closed: {error}")
else:
    check(
        not explosive_duplicate_report.ok
        and has_code(
            explosive_duplicate_report,
            PredicateGovernanceValidationCode.DUPLICATE_AUTHORITY_ID,
        ),
        "malformed duplicate equality fails closed without exception",
    )

withdrawn_for_batch = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.1",
    state=PredicateLifecycleState.WITHDRAWN,
)
withdrawn_authority_for_batch = authority(
    provenance_ref=prov.provenance_id,
    source_id=ns_candidate.namespace_id,
    target_id=withdrawn_for_batch.namespace_id,
    scope=withdrawn_for_batch.scope,
)
withdrawn_transition_for_batch = transition(
    source=ns_candidate,
    target=withdrawn_for_batch,
    authority_record=withdrawn_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.WITHDRAWAL,
)
reopened_for_batch = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.2",
    state=PredicateLifecycleState.CANDIDATE,
)
reopen_authority_for_batch = authority(
    provenance_ref=prov.provenance_id,
    source_id=withdrawn_for_batch.namespace_id,
    target_id=reopened_for_batch.namespace_id,
    scope=reopened_for_batch.scope,
)
fake_reopen_transition = transition(
    source=withdrawn_for_batch,
    target=reopened_for_batch,
    authority_record=reopen_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.REOPEN_REVIEW,
    prior_disposition_transition_ref="not-a-real-transition",
)
valid_reopen_transition = transition(
    source=withdrawn_for_batch,
    target=reopened_for_batch,
    authority_record=reopen_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.REOPEN_REVIEW,
    prior_disposition_transition_ref=withdrawn_transition_for_batch.transition_id,
)

def custody_batch(*transition_records):
    return with_expected_batch_id(
        PredicateGovernanceBatch(
            batch_id="",
            provenance_records=(prov,),
            resources=(ns_candidate, withdrawn_for_batch, reopened_for_batch),
            authority_records=(
                withdrawn_authority_for_batch,
                reopen_authority_for_batch,
            ),
            transitions=tuple(transition_records),
            registry_population_installed=False,
            action_root_lookup_installed=False,
            predicate_selection_installed=False,
            nearest_known_mapping_installed=False,
            semantic_similarity_installed=False,
            capability_routing_installed=False,
            runtime_activation_installed=False,
        )
    )

report = validate_governance_batch(
    custody_batch(withdrawn_transition_for_batch, fake_reopen_transition)
)
check(
    not report.ok
    and has_code(
        report, PredicateGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED
    ),
    "fake reopening ancestry rejected by collection validator",
)
check(
    validate_governance_batch(
        custody_batch(withdrawn_transition_for_batch, valid_reopen_transition)
    ).ok,
    "exact reopening ancestry accepted",
)

shared_reopen_authority = with_expected_authority_id(
    replace(
        withdrawn_authority_for_batch,
        reason="One authority record must not both withdraw and reopen material.",
        affected_record_refs=(
            ns_candidate.namespace_id,
            withdrawn_for_batch.namespace_id,
            reopened_for_batch.namespace_id,
        ),
    )
)
shared_withdrawal_transition = transition(
    source=ns_candidate,
    target=withdrawn_for_batch,
    authority_record=shared_reopen_authority,
    kind=PredicateLifecycleTransitionKind.WITHDRAWAL,
)
shared_reopen_transition = transition(
    source=withdrawn_for_batch,
    target=reopened_for_batch,
    authority_record=shared_reopen_authority,
    kind=PredicateLifecycleTransitionKind.REOPEN_REVIEW,
    prior_disposition_transition_ref=shared_withdrawal_transition.transition_id,
)
shared_authority_batch = with_expected_batch_id(
    PredicateGovernanceBatch(
        batch_id="",
        provenance_records=(prov,),
        resources=(ns_candidate, withdrawn_for_batch, reopened_for_batch),
        authority_records=(shared_reopen_authority,),
        transitions=(shared_withdrawal_transition, shared_reopen_transition),
        registry_population_installed=False,
        action_root_lookup_installed=False,
        predicate_selection_installed=False,
        nearest_known_mapping_installed=False,
        semantic_similarity_installed=False,
        capability_routing_installed=False,
        runtime_activation_installed=False,
    )
)
report = validate_governance_batch(shared_authority_batch)
check(
    not report.ok
    and has_code(
        report,
        PredicateGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
    ),
    "reopening requires a distinct new authority record",
)

quarantined_for_batch = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.1",
    state=PredicateLifecycleState.QUARANTINED,
)
quarantine_authority_for_batch = authority(
    provenance_ref=prov.provenance_id,
    source_id=ns_candidate.namespace_id,
    target_id=quarantined_for_batch.namespace_id,
    scope=quarantined_for_batch.scope,
)
quarantine_transition_for_batch = transition(
    source=ns_candidate,
    target=quarantined_for_batch,
    authority_record=quarantine_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.QUARANTINE,
    quarantine_causes=("cause:A",),
    quarantine_requirements=("resolve:A",),
)
released_for_batch = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.2",
    state=PredicateLifecycleState.REVIEWED,
)
release_authority_for_batch = authority(
    provenance_ref=prov.provenance_id,
    source_id=quarantined_for_batch.namespace_id,
    target_id=released_for_batch.namespace_id,
    scope=released_for_batch.scope,
)
invalid_release_transition = transition(
    source=quarantined_for_batch,
    target=released_for_batch,
    authority_record=release_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW,
    quarantine_requirements=("resolve:A",),
    resolved_quarantine_causes=("unrelated:B",),
)
valid_release_transition = transition(
    source=quarantined_for_batch,
    target=released_for_batch,
    authority_record=release_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW,
    quarantine_requirements=("resolve:A",),
    resolved_quarantine_causes=("cause:A",),
)
missing_requirement_release_transition = transition(
    source=quarantined_for_batch,
    target=released_for_batch,
    authority_record=release_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW,
    resolved_quarantine_causes=("cause:A",),
)
wrong_requirement_release_transition = transition(
    source=quarantined_for_batch,
    target=released_for_batch,
    authority_record=release_authority_for_batch,
    kind=PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW,
    quarantine_requirements=("unrelated:B",),
    resolved_quarantine_causes=("cause:A",),
)

def quarantine_custody_batch(release_transition):
    return with_expected_batch_id(
        PredicateGovernanceBatch(
            batch_id="",
            provenance_records=(prov,),
            resources=(
                ns_candidate,
                quarantined_for_batch,
                released_for_batch,
            ),
            authority_records=(
                quarantine_authority_for_batch,
                release_authority_for_batch,
            ),
            transitions=(
                quarantine_transition_for_batch,
                release_transition,
            ),
            registry_population_installed=False,
            action_root_lookup_installed=False,
            predicate_selection_installed=False,
            nearest_known_mapping_installed=False,
            semantic_similarity_installed=False,
            capability_routing_installed=False,
            runtime_activation_installed=False,
        )
    )

report = validate_governance_batch(
    quarantine_custody_batch(invalid_release_transition)
)
check(
    not report.ok
    and has_code(
        report, PredicateGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED
    ),
    "unrelated quarantine cause cannot authorize release",
)
report = evaluate_lifecycle_transition(
    quarantined_for_batch,
    released_for_batch,
    missing_requirement_release_transition,
    release_authority_for_batch,
    provenance_by_id=provenance_by_id,
)
check(
    not report.allowed
    and has_code(
        report,
        PredicateGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
    ),
    "quarantine release must identify satisfied release requirements",
)
report = validate_governance_batch(
    quarantine_custody_batch(wrong_requirement_release_transition)
)
check(
    not report.ok
    and has_code(
        report,
        PredicateGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
    ),
    "unrelated quarantine release requirement cannot authorize release",
)
check(
    validate_governance_batch(
        quarantine_custody_batch(valid_release_transition)
    ).ok,
    "exact quarantine cause resolution accepted",
)

# Rejection must block the exact lineage, not merely an arbitrary alias.
rejected_lineage_record = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.1",
    state=PredicateLifecycleState.REJECTED,
    key="aiweb:predicate:rejection_lineage",
)
rejection_source_record = namespace(
    provenance_ref=prov.provenance_id,
    version="v1",
    state=PredicateLifecycleState.CANDIDATE,
    key="aiweb:predicate:rejection_lineage",
)
rejection_lineage_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=rejection_source_record.namespace_id,
    target_id=rejected_lineage_record.namespace_id,
    scope=rejected_lineage_record.scope,
)
missing_lineage_block_transition = transition(
    source=rejection_source_record,
    target=rejected_lineage_record,
    authority_record=rejection_lineage_authority,
    kind=PredicateLifecycleTransitionKind.REJECTION,
    blocked_reentry_keys=("alias:only",),
)
report = evaluate_lifecycle_transition(
    rejection_source_record,
    rejected_lineage_record,
    missing_lineage_block_transition,
    rejection_lineage_authority,
    provenance_by_id=provenance_by_id,
)
check(
    not report.allowed
    and has_code(
        report,
        PredicateGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED,
    ),
    "rejection blocks the exact canonical lineage",
)
exact_lineage_block_transition = transition(
    source=rejection_source_record,
    target=rejected_lineage_record,
    authority_record=rejection_lineage_authority,
    kind=PredicateLifecycleTransitionKind.REJECTION,
    blocked_reentry_keys=(
        expected_resource_lineage_id(rejection_source_record),
        "alias:only",
    ),
)
check(
    evaluate_lifecycle_transition(
        rejection_source_record,
        rejected_lineage_record,
        exact_lineage_block_transition,
        rejection_lineage_authority,
        provenance_by_id=provenance_by_id,
    ).allowed,
    "rejection with exact lineage custody accepted",
)

# Supersession authority must explicitly name its admitted successor.
old_candidate = namespace(
    provenance_ref=prov.provenance_id,
    version="v1",
    state=PredicateLifecycleState.CANDIDATE,
    key="aiweb:predicate:supersession_old",
)
old_reviewed = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.1",
    state=PredicateLifecycleState.REVIEWED,
    key="aiweb:predicate:supersession_old",
)
old_admitted = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.2",
    state=PredicateLifecycleState.ADMITTED,
    key="aiweb:predicate:supersession_old",
)
old_superseded = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.3",
    state=PredicateLifecycleState.SUPERSEDED,
    key="aiweb:predicate:supersession_old",
)
new_candidate = namespace(
    provenance_ref=prov.provenance_id,
    version="v1",
    state=PredicateLifecycleState.CANDIDATE,
    key="aiweb:predicate:supersession_new",
)
new_reviewed = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.1",
    state=PredicateLifecycleState.REVIEWED,
    key="aiweb:predicate:supersession_new",
)
new_admitted = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.2",
    state=PredicateLifecycleState.ADMITTED,
    key="aiweb:predicate:supersession_new",
)
supersession_resources = (
    old_candidate,
    old_reviewed,
    old_admitted,
    old_superseded,
    new_candidate,
    new_reviewed,
    new_admitted,
)
supersession_authorities = []
supersession_transitions = []
for source, target, kind in (
    (old_candidate, old_reviewed, PredicateLifecycleTransitionKind.REVIEW),
    (old_reviewed, old_admitted, PredicateLifecycleTransitionKind.ADMISSION),
    (new_candidate, new_reviewed, PredicateLifecycleTransitionKind.REVIEW),
    (new_reviewed, new_admitted, PredicateLifecycleTransitionKind.ADMISSION),
):
    item_authority = authority(
        provenance_ref=prov.provenance_id,
        source_id=resource_id(source),
        target_id=resource_id(target),
        scope=target.scope,
    )
    item_transition = transition(
        source=source,
        target=target,
        authority_record=item_authority,
        kind=kind,
    )
    supersession_authorities.append(item_authority)
    supersession_transitions.append(item_transition)

supersession_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=old_admitted.namespace_id,
    target_id=old_superseded.namespace_id,
    scope=old_superseded.scope,
)
supersession_transition = transition(
    source=old_admitted,
    target=old_superseded,
    authority_record=supersession_authority,
    kind=PredicateLifecycleTransitionKind.SUPERSESSION,
    superseding_resource_ref=new_admitted.namespace_id,
)

def supersession_batch(authority_record, transition_record):
    return with_expected_batch_id(
        PredicateGovernanceBatch(
            batch_id="",
            provenance_records=(prov,),
            resources=supersession_resources,
            authority_records=tuple(
                supersession_authorities + [authority_record]
            ),
            transitions=tuple(
                supersession_transitions + [transition_record]
            ),
            registry_population_installed=False,
            action_root_lookup_installed=False,
            predicate_selection_installed=False,
            nearest_known_mapping_installed=False,
            semantic_similarity_installed=False,
            capability_routing_installed=False,
            runtime_activation_installed=False,
        )
    )

report = validate_governance_batch(
    supersession_batch(supersession_authority, supersession_transition)
)
check(
    not report.ok
    and has_code(
        report, PredicateGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH
    ),
    "supersession authority must name successor",
)
supersession_authority_with_successor = replace(
    supersession_authority,
    affected_record_refs=(
        *supersession_authority.affected_record_refs,
        new_admitted.namespace_id,
    ),
)
supersession_authority_with_successor = with_expected_authority_id(
    supersession_authority_with_successor
)
supersession_transition_with_successor = transition(
    source=old_admitted,
    target=old_superseded,
    authority_record=supersession_authority_with_successor,
    kind=PredicateLifecycleTransitionKind.SUPERSESSION,
    superseding_resource_ref=new_admitted.namespace_id,
)
check(
    validate_governance_batch(
        supersession_batch(
            supersession_authority_with_successor,
            supersession_transition_with_successor,
        )
    ).ok,
    "supersession with explicitly named admitted successor accepted",
)

# Active resources may not keep using an admitted dependency after that exact
# dependency version has transitioned into historical status.
ns_deprecated_b = namespace(
    provenance_ref=prov.provenance_id,
    version="v1.4",
    state=PredicateLifecycleState.DEPRECATED,
)
ns_deprecation_authority = authority(
    provenance_ref=prov.provenance_id,
    source_id=ns_admitted_b.namespace_id,
    target_id=ns_deprecated_b.namespace_id,
    scope=ns_deprecated_b.scope,
)
ns_deprecation_transition = transition(
    source=ns_admitted_b,
    target=ns_deprecated_b,
    authority_record=ns_deprecation_authority,
    kind=PredicateLifecycleTransitionKind.DEPRECATION,
)
historical_dependency_batch = with_expected_batch_id(
    replace(
        batch,
        resources=batch.resources + (ns_deprecated_b,),
        authority_records=batch.authority_records
        + (ns_deprecation_authority,),
        transitions=batch.transitions + (ns_deprecation_transition,),
    )
)
report = validate_governance_batch(historical_dependency_batch)
check(
    not report.ok
    and has_code(
        report,
        PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
    ),
    "active resource rejects historical non-current dependency version",
)

# Source static boundary: no lookup, nearest-match, routing, or effectful module calls.
package_root = REPO / "aiweb_language_core_bootstrap" / "predicate_role_frame_registry" / "governed_lifecycle"
source_files = tuple(sorted(package_root.glob("*.py")))
check(len(source_files) == 7, "exact seven governance source files")
for path in source_files:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lowered = node.name.lower()
            check("lookup" not in lowered, f"no lookup function {path.name}:{node.name}")
            check("select" not in lowered, f"no selection function {path.name}:{node.name}")
            check("route" not in lowered, f"no routing function {path.name}:{node.name}")
            check("execute" not in lowered, f"no execution function {path.name}:{node.name}")

print("AI.WEB SLICE 38B BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_field_cases={malformed_field_cases}")
print(f"transition_rules={len(PREDICATE_LIFECYCLE_TRANSITION_RULES)}")
print("admitted_action_roots=0")
print("admitted_predicates=0")
print("participant_role_registry_entries=0")
print("predicate_frame_registry_entries=0")
print("nearest_known_substitution=0")
print("semantic_similarity_authority=0")
print("registry_population_lookup_selection=0")
print("memory_routes_tools_actions_rendering_delivery=0")
