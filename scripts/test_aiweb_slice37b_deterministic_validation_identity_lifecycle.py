#!/usr/bin/env python3
"""Behavior tests for Slice 37B deterministic validation and lifecycle law."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from aiweb_language_core_bootstrap.controlled_concept_sense_registry.schema import (  # noqa: E402
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.governed_lifecycle import (  # noqa: E402
    CONCEPT_LIFECYCLE_TRANSITION_RULES,
    ConceptGovernanceBatch,
    ConceptGovernanceValidationCode,
    ConceptGovernanceValidationError,
    ConceptLifecycleAuthorityRecord,
    ConceptLifecycleTransitionKind,
    ConceptLifecycleTransitionRecord,
    assert_governance_batch,
    assert_lifecycle_transition,
    evaluate_lifecycle_transition,
    expected_resource_lineage_id,
    parse_resource_version,
    recompute_resource_id,
    resource_id,
    transition_rule,
    validate_governance_batch,
    validate_governed_resource,
    validate_lifecycle_authority_record,
    validate_namespace_key,
    validate_provenance_record,
    version_advances,
    with_expected_authority_id,
    with_expected_batch_id,
    with_expected_transition_id,
    with_recomputed_resource_id,
)


CHECKS = 0


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def codes(report) -> set[ConceptGovernanceValidationCode]:
    return {issue.code for issue in report.issues}


def make_provenance() -> ConceptProvenanceReference:
    provisional = ConceptProvenanceReference(
        provenance_id="",
        authority_document="RMC Concept Lexicon and Semantic Relation Graph v1",
        authority_section="Part IX Sections 50-51",
        source_kind="permanent_architecture_authority",
        source_reference="document4:part9:sections50-51",
        version="v1",
        non_llm_provenance=True,
        external_resource_admitted=False,
        runtime_loaded=False,
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
    return replace(provisional, provenance_id=provisional.expected_id())


def make_namespace(
    provenance: ConceptProvenanceReference,
    *,
    version: str,
    state: ConceptLifecycleState,
    label: str = "AI.Web Core",
    namespace_key: str = "aiweb:core",
    scope: tuple[str, ...] = ("domain:core",),
) -> ConceptNamespaceIdentity:
    provisional = ConceptNamespaceIdentity(
        namespace_id="",
        namespace_key=namespace_key,
        label=label,
        definition="Bounded synthetic namespace used only by Slice 37B tests.",
        version=version,
        lifecycle_state=state,
        provenance_ref=provenance.provenance_id,
        scope_tags=scope,
        permitted_uses=("validation-fixture-only",),
        prohibited_uses=("runtime-use", "registry-population"),
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
    return with_recomputed_resource_id(provisional)


def make_authority(
    provenance: ConceptProvenanceReference,
    source: ConceptNamespaceIdentity,
    target: ConceptNamespaceIdentity,
    *,
    conflict: bool = False,
    unknown: bool = False,
    dependency: bool = False,
    unresolved: tuple[str, ...] = (),
    missing: tuple[str, ...] = (),
    scope: tuple[str, ...] | None = None,
) -> ConceptLifecycleAuthorityRecord:
    provisional = ConceptLifecycleAuthorityRecord(
        authority_id="",
        authority_provenance_ref=provenance.provenance_id,
        decision_owner_ref="nicholas-jacob-bogaert",
        human_approval_ref=f"approval:{source.version}:{target.version}",
        human_approved=True,
        reason=f"Governed transition from {source.lifecycle_state.value} to {target.lifecycle_state.value}.",
        scope=scope or target.scope_tags,
        affected_record_refs=(source.namespace_id, target.namespace_id),
        prohibited_uses=("runtime-activation", "silent-authority-expansion"),
        unresolved_dependency_refs=unresolved,
        missing_authority_refs=missing,
        conflict_review_complete=conflict,
        unknown_state_review_complete=unknown,
        later_dependency_review_complete=dependency,
        non_llm_provenance=True,
        external_resource_decision_ref=None,
        runtime_authorized=False,
        implementation_authorized=False,
        registry_population_authorized=False,
    )
    return with_expected_authority_id(provisional)


def make_transition(
    source: ConceptNamespaceIdentity,
    target: ConceptNamespaceIdentity,
    authority: ConceptLifecycleAuthorityRecord,
    kind: ConceptLifecycleTransitionKind,
    *,
    quarantine_causes: tuple[str, ...] = (),
    quarantine_requirements: tuple[str, ...] = (),
    resolved_causes: tuple[str, ...] = (),
    successor: str | None = None,
    blocked_reentry: tuple[str, ...] = (),
    verified_scope: tuple[str, ...] = (),
    prior_disposition: str | None = None,
    historical_only: bool = False,
) -> ConceptLifecycleTransitionRecord:
    provisional = ConceptLifecycleTransitionRecord(
        transition_id="",
        lineage_id=expected_resource_lineage_id(source),
        resource_kind=source.resource_kind,
        source_resource_id=source.namespace_id,
        target_resource_id=target.namespace_id,
        source_version=source.version,
        target_version=target.version,
        from_state=source.lifecycle_state,
        to_state=target.lifecycle_state,
        transition_kind=kind,
        authority_record_ref=authority.authority_id,
        quarantine_cause_refs=quarantine_causes,
        quarantine_release_requirement_refs=quarantine_requirements,
        resolved_quarantine_cause_refs=resolved_causes,
        superseding_resource_ref=successor,
        blocked_reentry_keys=blocked_reentry,
        verified_scope_refs=verified_scope,
        prior_disposition_transition_ref=prior_disposition,
        historical_only_after_transition=historical_only,
        prior_record_preserved=True,
        automatic_transition=False,
    )
    return with_expected_transition_id(provisional)


def make_batch(
    provenance: ConceptProvenanceReference,
    resources: tuple[ConceptNamespaceIdentity, ...],
    authorities: tuple[ConceptLifecycleAuthorityRecord, ...],
    transitions: tuple[ConceptLifecycleTransitionRecord, ...],
) -> ConceptGovernanceBatch:
    provisional = ConceptGovernanceBatch(
        batch_id="",
        provenance_records=(provenance,),
        resources=resources,
        authority_records=authorities,
        transitions=transitions,
        registry_population_installed=False,
        lookup_installed=False,
        occurrence_mapping_installed=False,
        sense_selection_installed=False,
        relation_instance_population_installed=False,
        structural_integration_installed=False,
        runtime_activation_installed=False,
    )
    return with_expected_batch_id(provisional)


def main() -> None:
    provenance = make_provenance()
    observed = make_namespace(
        provenance,
        version="v1",
        state=ConceptLifecycleState.OBSERVED,
    )
    candidate = make_namespace(
        provenance,
        version="v2",
        state=ConceptLifecycleState.CANDIDATE,
    )
    admitted = make_namespace(
        provenance,
        version="v3",
        state=ConceptLifecycleState.ADMITTED,
    )

    observation_authority = make_authority(
        provenance,
        observed,
        candidate,
        missing=("concept-admission-review",),
    )
    observation_transition = make_transition(
        observed,
        candidate,
        observation_authority,
        ConceptLifecycleTransitionKind.OBSERVATION_REVIEW,
    )

    admission_authority = make_authority(
        provenance,
        candidate,
        admitted,
        conflict=True,
        unknown=True,
        dependency=True,
    )
    admission_transition = make_transition(
        candidate,
        admitted,
        admission_authority,
        ConceptLifecycleTransitionKind.ADMISSION,
    )

    valid_batch = make_batch(
        provenance,
        (observed, candidate, admitted),
        (observation_authority, admission_authority),
        (observation_transition, admission_transition),
    )

    # Identity, namespace, version, provenance, and immutable schema law.
    check(validate_provenance_record(provenance).ok, "provenance must validate")
    check(validate_namespace_key("aiweb:core").ok, "canonical namespace must validate")
    check(not validate_namespace_key("AIWeb Core").ok, "noncanonical namespace must fail")
    check(parse_resource_version("v1") == (1, 0, 0), "v1 parsing")
    check(parse_resource_version("v2.3") == (2, 3, 0), "v2.3 parsing")
    check(parse_resource_version("v2.3.4") == (2, 3, 4), "v2.3.4 parsing")
    for invalid in ("1", "V1", "v01", "v1.02", "v1.2.3.4", "v1-beta"):
        try:
            parse_resource_version(invalid)
        except ValueError:
            check(True, f"invalid version rejected: {invalid}")
        else:
            check(False, f"invalid version accepted: {invalid}")
    check(version_advances("v1", "v2"), "version must advance")
    check(not version_advances("v2", "v2"), "equal version cannot advance")
    check(not version_advances("v3", "v2"), "version cannot go backward")
    check(resource_id(observed) == observed.namespace_id, "resource identity accessor")
    check(recompute_resource_id(observed) == observed.namespace_id, "identity recomputation")
    check(expected_resource_lineage_id(observed) == expected_resource_lineage_id(admitted), "lineage stable across versions")
    check(validate_governed_resource(observed, provenance_by_id={provenance.provenance_id: provenance}).ok, "observed resource validates")
    tampered = replace(observed, label="Tampered")
    check(ConceptGovernanceValidationCode.IDENTITY_MISMATCH in codes(validate_governed_resource(tampered, provenance_by_id={provenance.provenance_id: provenance})), "tampered identity rejected")
    invalid_namespace = with_recomputed_resource_id(replace(observed, namespace_key="AIWeb Core"))
    check(ConceptGovernanceValidationCode.INVALID_NAMESPACE in codes(validate_governed_resource(invalid_namespace, provenance_by_id={provenance.provenance_id: provenance})), "namespace format enforced")
    invalid_version = with_recomputed_resource_id(replace(observed, version="v01"))
    check(ConceptGovernanceValidationCode.INVALID_VERSION in codes(validate_governed_resource(invalid_version, provenance_by_id={provenance.provenance_id: provenance})), "strict version enforced")
    check(ConceptGovernanceValidationCode.PROVENANCE_NOT_FOUND in codes(validate_governed_resource(observed, provenance_by_id={})), "missing provenance blocked")

    # Positive transition law.
    check(validate_lifecycle_authority_record(observation_authority, provenance_by_id={provenance.provenance_id: provenance}).ok, "observation authority validates")
    observation_decision = evaluate_lifecycle_transition(observed, candidate, observation_transition, observation_authority, provenance_by_id={provenance.provenance_id: provenance})
    check(observation_decision.allowed, "observed to candidate allowed")
    admission_decision = assert_lifecycle_transition(candidate, admitted, admission_transition, admission_authority, provenance_by_id={provenance.provenance_id: provenance})
    check(admission_decision.allowed, "candidate to admitted allowed")
    check(transition_rule(ConceptLifecycleState.UNKNOWN, ConceptLifecycleState.ADMITTED) is None, "unknown cannot jump to admitted")
    check(len(CONCEPT_LIFECYCLE_TRANSITION_RULES) == 48, "exact bounded transition matrix")
    pairs = {(rule.from_state, rule.to_state) for rule in CONCEPT_LIFECYCLE_TRANSITION_RULES}
    check(len(pairs) == len(CONCEPT_LIFECYCLE_TRANSITION_RULES), "transition state pairs are unique")
    for rule in CONCEPT_LIFECYCLE_TRANSITION_RULES:
        check(bool(rule.allowed_kinds), "every transition rule names an allowed kind")
        check(bool(rule.purpose.strip()), "every transition rule has a governing purpose")
        check(rule.authority_required is True, "every transition requires authority")
        check(rule.human_approval_required is True, "every transition requires human approval")

    wrong_source_decision = evaluate_lifecycle_transition(
        object(),
        candidate,
        observation_transition,
        observation_authority,
        provenance_by_id={provenance.provenance_id: provenance},
    )
    check(not wrong_source_decision.allowed, "unsupported source type fails closed")
    check(ConceptGovernanceValidationCode.TYPE_MISMATCH in {item.code for item in wrong_source_decision.issues}, "unsupported source reports type mismatch")

    corrected = make_namespace(provenance, version="v4", state=ConceptLifecycleState.ADMITTED, label="AI.Web Core Corrected")
    correction_authority = make_authority(provenance, admitted, corrected, conflict=True, unknown=True, dependency=True)
    correction_transition = make_transition(admitted, corrected, correction_authority, ConceptLifecycleTransitionKind.CORRECTION)
    check(assert_lifecycle_transition(admitted, corrected, correction_transition, correction_authority, provenance_by_id={provenance.provenance_id: provenance}).allowed, "admitted correction preserves state and ancestry")

    deprecated = make_namespace(provenance, version="v4", state=ConceptLifecycleState.DEPRECATED)
    deprecation_authority = make_authority(provenance, admitted, deprecated, conflict=True)
    deprecation_transition = make_transition(admitted, deprecated, deprecation_authority, ConceptLifecycleTransitionKind.DEPRECATION)
    check(assert_lifecycle_transition(admitted, deprecated, deprecation_transition, deprecation_authority, provenance_by_id={provenance.provenance_id: provenance}).allowed, "admitted to deprecated allowed")

    rejected = make_namespace(provenance, version="v3", state=ConceptLifecycleState.REJECTED)
    rejection_authority = make_authority(provenance, candidate, rejected, conflict=True)
    rejection_transition = make_transition(candidate, rejected, rejection_authority, ConceptLifecycleTransitionKind.REJECTION, blocked_reentry=("aiweb:core", "equivalent-core-namespace"))
    check(assert_lifecycle_transition(candidate, rejected, rejection_transition, rejection_authority, provenance_by_id={provenance.provenance_id: provenance}).allowed, "candidate rejection records blocked reentry")

    quarantined = make_namespace(provenance, version="v3", state=ConceptLifecycleState.QUARANTINED)
    quarantine_authority = make_authority(provenance, candidate, quarantined, conflict=True, dependency=True, missing=("license-review",))
    quarantine_transition = make_transition(candidate, quarantined, quarantine_authority, ConceptLifecycleTransitionKind.QUARANTINE, quarantine_causes=("cause:license-unresolved",), quarantine_requirements=("requirement:license-cleared",))
    check(assert_lifecycle_transition(candidate, quarantined, quarantine_transition, quarantine_authority, provenance_by_id={provenance.provenance_id: provenance}).allowed, "candidate quarantine allowed with causes")

    released = make_namespace(provenance, version="v4", state=ConceptLifecycleState.ADMITTED)
    release_authority = make_authority(provenance, quarantined, released, conflict=True, unknown=True, dependency=True)
    release_transition = make_transition(quarantined, released, release_authority, ConceptLifecycleTransitionKind.RELEASE_FROM_QUARANTINE, resolved_causes=("cause:license-unresolved",))
    check(assert_lifecycle_transition(quarantined, released, release_transition, release_authority, provenance_by_id={provenance.provenance_id: provenance}).allowed, "quarantine release requires full review")

    reopened = make_namespace(provenance, version="v4", state=ConceptLifecycleState.CANDIDATE)
    reopen_authority = make_authority(provenance, rejected, reopened, conflict=True, unknown=True, dependency=True)
    reopen_transition = make_transition(rejected, reopened, reopen_authority, ConceptLifecycleTransitionKind.REOPEN_REVIEW, prior_disposition=rejection_transition.transition_id)
    check(assert_lifecycle_transition(rejected, reopened, reopen_transition, reopen_authority, provenance_by_id={provenance.provenance_id: provenance}).allowed, "rejected material requires explicit reopen ancestry")

    # Fail-closed transition mutations.
    wrong_kind = with_expected_transition_id(replace(admission_transition, transition_kind=ConceptLifecycleTransitionKind.REJECTION))
    check(ConceptGovernanceValidationCode.TRANSITION_KIND_MISMATCH in {i.code for i in evaluate_lifecycle_transition(candidate, admitted, wrong_kind, admission_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "wrong transition kind blocked")
    direct_admission = make_transition(observed, admitted, admission_authority, ConceptLifecycleTransitionKind.ADMISSION)
    check(ConceptGovernanceValidationCode.TRANSITION_NOT_PERMITTED in {i.code for i in evaluate_lifecycle_transition(observed, admitted, direct_admission, admission_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "observed cannot jump to admitted")
    same_version_target = with_recomputed_resource_id(replace(candidate, lifecycle_state=ConceptLifecycleState.ADMITTED))
    same_version_authority = make_authority(provenance, candidate, same_version_target, conflict=True, unknown=True, dependency=True)
    same_version_transition = make_transition(candidate, same_version_target, same_version_authority, ConceptLifecycleTransitionKind.ADMISSION)
    check(ConceptGovernanceValidationCode.VERSION_NOT_ADVANCING in {i.code for i in evaluate_lifecycle_transition(candidate, same_version_target, same_version_transition, same_version_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "same version transition blocked")
    no_review_authority = make_authority(provenance, candidate, admitted)
    no_review_transition = make_transition(candidate, admitted, no_review_authority, ConceptLifecycleTransitionKind.ADMISSION)
    check(ConceptGovernanceValidationCode.REVIEW_INCOMPLETE in {i.code for i in evaluate_lifecycle_transition(candidate, admitted, no_review_transition, no_review_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "admission review enforced")
    unresolved_authority = make_authority(provenance, candidate, admitted, conflict=True, unknown=True, dependency=True, unresolved=("dependency:pending",))
    unresolved_transition = make_transition(candidate, admitted, unresolved_authority, ConceptLifecycleTransitionKind.ADMISSION)
    check(ConceptGovernanceValidationCode.UNRESOLVED_DEPENDENCY in {i.code for i in evaluate_lifecycle_transition(candidate, admitted, unresolved_transition, unresolved_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "unresolved dependency blocks admission")
    narrow_authority = make_authority(provenance, candidate, admitted, conflict=True, unknown=True, dependency=True, scope=("domain:other",))
    narrow_transition = make_transition(candidate, admitted, narrow_authority, ConceptLifecycleTransitionKind.ADMISSION)
    check(ConceptGovernanceValidationCode.SCOPE_EXPANSION in {i.code for i in evaluate_lifecycle_transition(candidate, admitted, narrow_transition, narrow_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "scope expansion blocked")
    automatic = with_expected_transition_id(replace(admission_transition, automatic_transition=True))
    check(ConceptGovernanceValidationCode.AUTOMATIC_TRANSITION_PROHIBITED in {i.code for i in evaluate_lifecycle_transition(candidate, admitted, automatic, admission_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "automatic transition blocked")
    erased = with_expected_transition_id(replace(admission_transition, prior_record_preserved=False))
    check(ConceptGovernanceValidationCode.PRIOR_RECORD_NOT_PRESERVED in {i.code for i in evaluate_lifecycle_transition(candidate, admitted, erased, admission_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "record erasure blocked")
    no_quarantine_cause = make_transition(candidate, quarantined, quarantine_authority, ConceptLifecycleTransitionKind.QUARANTINE)
    check(ConceptGovernanceValidationCode.QUARANTINE_CAUSE_REQUIRED in {i.code for i in evaluate_lifecycle_transition(candidate, quarantined, no_quarantine_cause, quarantine_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "quarantine reason enforced")
    no_blocked_reentry = make_transition(candidate, rejected, rejection_authority, ConceptLifecycleTransitionKind.REJECTION)
    check(ConceptGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED in {i.code for i in evaluate_lifecycle_transition(candidate, rejected, no_blocked_reentry, rejection_authority, provenance_by_id={provenance.provenance_id: provenance}).issues}, "rejection negative authority enforced")
    unapproved = with_expected_authority_id(replace(admission_authority, human_approved=False))
    check(ConceptGovernanceValidationCode.HUMAN_APPROVAL_REQUIRED in codes(validate_lifecycle_authority_record(unapproved, provenance_by_id={provenance.provenance_id: provenance})), "human approval enforced")
    runtime_authority = with_expected_authority_id(replace(admission_authority, runtime_authorized=True))
    check(ConceptGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED in codes(validate_lifecycle_authority_record(runtime_authority, provenance_by_id={provenance.provenance_id: provenance})), "runtime authority blocked")
    external_authority = with_expected_authority_id(replace(admission_authority, external_resource_decision_ref="document8:decision"))
    check(ConceptGovernanceValidationCode.EXTERNAL_RESOURCE_AUTHORITY_PROHIBITED in codes(validate_lifecycle_authority_record(external_authority, provenance_by_id={provenance.provenance_id: provenance})), "Document 8 decisions deferred")

    # Collection-level ancestry, conflict, duplicate, and no-effect law.
    valid_report = validate_governance_batch(valid_batch)
    if not valid_report.ok:
        for issue in valid_report.issues:
            print(issue)
    check(valid_report.ok, "valid governance batch must pass")
    check(assert_governance_batch(valid_batch) is valid_batch, "assert returns exact immutable batch")
    check(valid_batch.registry_population_installed is False, "no registry population")
    check(valid_batch.lookup_installed is False, "no lookup")
    check(valid_batch.occurrence_mapping_installed is False, "no occurrence mapping")
    check(valid_batch.sense_selection_installed is False, "no sense selection")
    check(valid_batch.relation_instance_population_installed is False, "no relation instances")
    check(valid_batch.structural_integration_installed is False, "no Slice 36 integration")
    check(valid_batch.runtime_activation_installed is False, "no runtime activation")

    duplicate_batch = make_batch(provenance, (observed, observed, candidate, admitted), (observation_authority, admission_authority), (observation_transition, admission_transition))
    check(ConceptGovernanceValidationCode.EXACT_DUPLICATE_RECORD in codes(validate_governance_batch(duplicate_batch)), "exact duplicate resource rejected")
    conflicting_candidate = make_namespace(provenance, version="v2", state=ConceptLifecycleState.CANDIDATE, label="Conflicting Candidate")
    conflict_batch = make_batch(provenance, (observed, candidate, conflicting_candidate), (observation_authority,), (observation_transition,))
    check(ConceptGovernanceValidationCode.CONFLICTING_LINEAGE_VERSION in codes(validate_governance_batch(conflict_batch)), "conflicting lineage/version rejected")
    orphan_batch = make_batch(provenance, (observed, admitted), (), ())
    check(ConceptGovernanceValidationCode.ORPHAN_RESOURCE_VERSION in codes(validate_governance_batch(orphan_batch)), "orphan version rejected")
    active_initial_batch = make_batch(provenance, (admitted,), (), ())
    check(ConceptGovernanceValidationCode.ADMISSION_HISTORY_REQUIRED in codes(validate_governance_batch(active_initial_batch)), "active resource requires admission history")
    effect_batch = with_expected_batch_id(replace(valid_batch, lookup_installed=True))
    check(ConceptGovernanceValidationCode.REGISTRY_POPULATION_PROHIBITED in codes(validate_governance_batch(effect_batch)), "lookup installation blocked")

    release_batch = make_batch(
        provenance,
        (observed, candidate, quarantined, released),
        (observation_authority, quarantine_authority, release_authority),
        (observation_transition, quarantine_transition, release_transition),
    )
    check(validate_governance_batch(release_batch).ok, "full quarantine ancestry and release pass")
    partial_release = with_expected_transition_id(replace(release_transition, resolved_quarantine_cause_refs=("cause:other",)))
    partial_release_batch = make_batch(
        provenance,
        (observed, candidate, quarantined, released),
        (observation_authority, quarantine_authority, release_authority),
        (observation_transition, quarantine_transition, partial_release),
    )
    check(ConceptGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED in codes(validate_governance_batch(partial_release_batch)), "unresolved quarantine cause blocks release")

    try:
        assert_governance_batch(orphan_batch)
    except ConceptGovernanceValidationError:
        check(True, "assertion fails closed")
    else:
        check(False, "invalid batch did not fail closed")

    # Repeated validation is deterministic and does not mutate records.
    first = validate_governance_batch(valid_batch)
    second = validate_governance_batch(valid_batch)
    check(first == second, "validation replay deterministic")
    check(valid_batch == make_batch(provenance, (observed, candidate, admitted), (observation_authority, admission_authority), (observation_transition, admission_transition)), "fixture reconstruction deterministic")

    print("AI.WEB SLICE 37B BEHAVIOR TEST: PASS")
    print(f"check_count={CHECKS}")
    print(f"transition_rules={len(CONCEPT_LIFECYCLE_TRANSITION_RULES)}")
    print("registry_entries=0")
    print("concept_lookup_functions=0")
    print("selected_sense_authority=0")
    print("external_resources_loaded=0")
    print("routes_tools_actions_renderings_deliveries=0")


if __name__ == "__main__":
    main()
