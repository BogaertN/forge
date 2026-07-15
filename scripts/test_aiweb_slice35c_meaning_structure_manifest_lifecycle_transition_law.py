#!/usr/bin/env python3
"""Behavior tests for Slice 35C MSM-v1 lifecycle transition law."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import importlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PACKAGE = "aiweb_language_core_bootstrap.meaning_structure_manifest"
LIFECYCLE_MODULE = f"{PACKAGE}.lifecycle"
EXPECTED_EXPORTS = (
    "LIFECYCLE_SPEC_ID",
    "LIFECYCLE_SPEC_VERSION",
    "LIFECYCLE_TRANSITION_RULES",
    "LifecycleAppendResult",
    "LifecycleTransitionCode",
    "LifecycleTransitionDecision",
    "LifecycleTransitionError",
    "LifecycleTransitionIssue",
    "LifecycleTransitionRule",
    "append_lifecycle_successor",
    "evaluate_lifecycle_transition",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def import_probe(statement: str) -> None:
    with tempfile.TemporaryDirectory(prefix="aiweb_slice35c_import_") as tmp:
        before = tuple(Path(tmp).iterdir())
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = str(REPO)
        completed = subprocess.run(
            [sys.executable, "-B", "-c", statement],
            cwd=tmp,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        after = tuple(Path(tmp).iterdir())
        require(completed.returncode == 0, completed.stderr)
        require(before == after, "lifecycle import created files or runtime state")


def make_authority(package, record_id: str, object_ref: str, kind):
    return package.ExternalAuthorityReferenceRecord(
        record_id=record_id,
        lineage_id="lineage-001",
        authority_kind=kind,
        external_object_ref=object_ref,
        semantic_relevance=f"authority_for_{record_id}",
    )


def make_base_manifest(package):
    root = package.LineageRootRecord(
        lineage_id="lineage-001",
        origin_kind=package.LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION,
        origin_ref="source-event-001",
        direction=package.SemanticDirection.INWARD,
    )
    candidate = package.CandidateMeaningRecord(
        record_id="candidate-001",
        lineage_id=root.lineage_id,
        source_expression_ref=root.origin_ref,
        communicative_act="request_to_explain",
        concept_refs=("concept-001",),
        relation_refs=("relation-001",),
        meaning_modifiers=("bounded_scope",),
        ambiguity_reasons=(),
        unresolved_referents=(),
        authority_sensitive_implications=("meaning_not_action",),
        preservation_classes=(
            package.SemanticPreservationClass.NEGATION,
            package.SemanticPreservationClass.NON_LLM_PROVENANCE,
        ),
    )
    authorities = (
        make_authority(
            package,
            "authority-gate",
            "gate-receipt-001",
            package.ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
        make_authority(
            package,
            "authority-result",
            "result-receipt-001",
            package.ExternalAuthorityKind.INVOCATION_EXECUTION_OR_VERIFICATION_RECEIPT,
        ),
        make_authority(
            package,
            "authority-outward",
            "outward-authority-001",
            package.ExternalAuthorityKind.MANIFEST_CONTRACT,
        ),
        make_authority(
            package,
            "authority-render",
            "render-candidate-001",
            package.ExternalAuthorityKind.RENDER_PREVIEW_OR_OUTPUT_OBJECT,
        ),
        make_authority(
            package,
            "authority-echo",
            "echo-receipt-001",
            package.ExternalAuthorityKind.RMC_ECHO_VALIDATOR_RECEIPT,
        ),
        make_authority(
            package,
            "authority-delivery",
            "delivery-receipt-001",
            package.ExternalAuthorityKind.DELIVERY_OR_CONTAINMENT_RECEIPT,
        ),
        make_authority(
            package,
            "authority-containment",
            "containment-receipt-001",
            package.ExternalAuthorityKind.DELIVERY_OR_CONTAINMENT_RECEIPT,
        ),
    )
    manifest = package.MeaningStructureManifestV1(
        manifest_id="msm-001",
        lineage_root=root,
        candidate_meanings=(candidate,),
        non_selection_outcomes=(),
        selected_governed_meanings=(),
        governed_result_references=(),
        governed_outward_meanings=(),
        expression_links=(),
        validation_links=(),
        delivery_or_containment_links=(),
        external_authority_references=authorities,
        semantic_transition_traces=(),
    )
    return manifest, candidate


def append_full_chain(package, lifecycle):
    manifest, candidate = make_base_manifest(package)
    selected = package.SelectedGovernedMeaningRecord(
        record_id="selected-001",
        lineage_id="lineage-001",
        selected_candidate_ref=candidate.record_id,
        selection_authority_ref="gate-receipt-001",
        communicative_act=candidate.communicative_act,
        concept_refs=candidate.concept_refs,
        relation_refs=candidate.relation_refs,
        meaning_modifiers=candidate.meaning_modifiers,
        inherited_limitations=("explanation_only",),
        authority_sensitive_distinctions=("selected_not_authorized",),
        preservation_classes=candidate.preservation_classes,
    )
    first = lifecycle.append_lifecycle_successor(
        manifest,
        trace_record_id="trace-001",
        from_record_ref=candidate.record_id,
        successor=selected,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="deterministic_gate_selected_candidate",
        authority_reference_ref="authority-gate",
    )
    result = package.GovernedResultReferenceRecord(
        record_id="result-001",
        lineage_id="lineage-001",
        selected_meaning_ref=selected.record_id,
        external_authority_ref="authority-result",
        semantic_relevance="bounded_external_result",
    )
    second = lifecycle.append_lifecycle_successor(
        first.manifest,
        trace_record_id="trace-002",
        from_record_ref=selected.record_id,
        successor=result,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="external_result_became_semantically_relevant",
        authority_reference_ref="authority-result",
    )
    outward = package.GovernedOutwardMeaningRecord(
        record_id="outward-001",
        lineage_id="lineage-001",
        outward_basis_refs=(result.record_id, "authority-outward"),
        prior_selected_meaning_ref=selected.record_id,
        permitted_claims=("bounded_result_exists",),
        required_qualifications=("within_external_receipt_scope",),
        prohibited_enlargements=("general_success",),
        external_dependency_refs=("authority-outward",),
        preservation_classes=candidate.preservation_classes,
    )
    third = lifecycle.append_lifecycle_successor(
        second.manifest,
        trace_record_id="trace-003",
        from_record_ref=result.record_id,
        successor=outward,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="outward_meaning_bounded_by_result",
        authority_reference_ref="authority-outward",
    )
    expression = package.ExpressionLinkRecord(
        record_id="expression-001",
        lineage_id="lineage-001",
        governed_outward_meaning_ref=outward.record_id,
        expression_candidate_ref="render-candidate-001",
    )
    fourth = lifecycle.append_lifecycle_successor(
        third.manifest,
        trace_record_id="trace-004",
        from_record_ref=outward.record_id,
        successor=expression,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="deterministic_surface_candidate_linked",
        authority_reference_ref="authority-render",
    )
    validation = package.ValidationLinkRecord(
        record_id="validation-001",
        lineage_id="lineage-001",
        expression_link_ref=expression.record_id,
        external_validation_receipt_ref="echo-receipt-001",
        external_validation_disposition="accepted_within_scope",
    )
    fifth = lifecycle.append_lifecycle_successor(
        fourth.manifest,
        trace_record_id="trace-005",
        from_record_ref=expression.record_id,
        successor=validation,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="external_echo_receipt_linked",
        authority_reference_ref="authority-echo",
    )
    delivery = package.DeliveryContainmentLinkRecord(
        record_id="delivery-001",
        lineage_id="lineage-001",
        prior_link_ref=validation.record_id,
        disposition=package.DeliveryContainmentKind.DELIVERY_LINKED,
        external_receipt_ref="delivery-receipt-001",
    )
    sixth = lifecycle.append_lifecycle_successor(
        fifth.manifest,
        trace_record_id="trace-006",
        from_record_ref=validation.record_id,
        successor=delivery,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="separate_delivery_receipt_linked",
        authority_reference_ref="authority-delivery",
    )
    return manifest, sixth.manifest, selected, expression, validation, delivery


def codes(decision):
    return tuple(issue.code.value for issue in decision.issues)


def main() -> int:
    import_probe(f"import {LIFECYCLE_MODULE}")
    import_probe(f"from {LIFECYCLE_MODULE} import *")

    package = importlib.import_module(PACKAGE)
    lifecycle = importlib.import_module(LIFECYCLE_MODULE)
    validation = importlib.import_module(f"{PACKAGE}.validation")

    require(lifecycle.__all__ == EXPECTED_EXPORTS, "lifecycle __all__ mismatch")
    star: dict[str, object] = {}
    exec(f"from {LIFECYCLE_MODULE} import *", star, star)
    star_names = tuple(sorted(name for name in star if name != "__builtins__"))
    require(star_names == tuple(sorted(EXPECTED_EXPORTS)), "star import mismatch")
    for name in EXPECTED_EXPORTS:
        require(star[name] is getattr(lifecycle, name), f"export identity mismatch: {name}")

    root_exports_before = tuple(package.__all__)
    require("append_lifecycle_successor" not in root_exports_before, "root exports expanded")

    pairs = tuple((rule.from_state, rule.to_state) for rule in lifecycle.LIFECYCLE_TRANSITION_RULES)
    require(len(pairs) == len(set(pairs)), "duplicate lifecycle rule pair")
    require(len(pairs) == 31, f"unexpected transition rule count: {len(pairs)}")
    for rule in lifecycle.LIFECYCLE_TRANSITION_RULES:
        try:
            rule.purpose = "changed"
        except (FrozenInstanceError, AttributeError):
            pass
        else:
            raise AssertionError("lifecycle rule is mutable")

    original, final_manifest, selected, expression, validation_link, delivery = append_full_chain(package, lifecycle)
    require(validation.validate_manifest(original).ok, "original manifest invalid")
    require(validation.validate_manifest(final_manifest).ok, "final manifest invalid")
    require(original.selected_governed_meanings == (), "original manifest mutated")
    require(len(final_manifest.semantic_transition_traces) == 6, "trace count mismatch")
    require(final_manifest.delivery_or_containment_links[-1] == delivery, "delivery missing")

    manifest, candidate = make_base_manifest(package)
    selected_missing_authority = replace(selected, record_id="selected-no-authority")
    denied = lifecycle.evaluate_lifecycle_transition(
        manifest,
        from_record_ref=candidate.record_id,
        successor=selected_missing_authority,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="missing_authority_test",
        authority_reference_ref=None,
    )
    require(not denied.allowed, "selection without authority was allowed")
    require("authority_required" in codes(denied), "missing authority reason absent")

    illegal_delivery = package.DeliveryContainmentLinkRecord(
        record_id="delivery-illegal",
        lineage_id="lineage-001",
        prior_link_ref=candidate.record_id,
        disposition=package.DeliveryContainmentKind.DELIVERY_LINKED,
        external_receipt_ref="delivery-receipt-001",
    )
    denied = lifecycle.evaluate_lifecycle_transition(
        manifest,
        from_record_ref=candidate.record_id,
        successor=illegal_delivery,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="skip_all_required_stages",
        authority_reference_ref="authority-delivery",
    )
    require(not denied.allowed, "candidate-to-delivery skip was allowed")
    require("transition_not_permitted" in codes(denied), "skip denial absent")

    delivery_from_expression = replace(delivery, record_id="delivery-from-expression", prior_link_ref=expression.record_id)
    chain_manifest = final_manifest
    denied = lifecycle.evaluate_lifecycle_transition(
        chain_manifest,
        from_record_ref=expression.record_id,
        successor=delivery_from_expression,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="validation_must_not_be_skipped",
        authority_reference_ref="authority-delivery",
    )
    require(not denied.allowed, "expression-to-delivery skip was allowed")

    clarification = package.NonSelectionOutcomeRecord(
        record_id="clarification-001",
        lineage_id="lineage-001",
        outcome_kind=package.NonSelectionOutcomeKind.CLARIFICATION_REQUIRED,
        candidate_refs=(candidate.record_id,),
        reasons=("missing_referent",),
        required_clarifications=("identify_source",),
        external_authority_refs=("authority-gate",),
    )
    clarification_result = lifecycle.append_lifecycle_successor(
        manifest,
        trace_record_id="trace-clarification",
        from_record_ref=candidate.record_id,
        successor=clarification,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="gate_requires_clarification",
        authority_reference_ref="authority-gate",
    )
    clarified_candidate = replace(
        candidate,
        record_id="candidate-clarified",
        ambiguity_reasons=(),
        unresolved_referents=(),
    )
    reentry = lifecycle.append_lifecycle_successor(
        clarification_result.manifest,
        trace_record_id="trace-reentry",
        from_record_ref=clarification.record_id,
        successor=clarified_candidate,
        transition_kind=package.SemanticTransitionKind.NARROWING,
        reason="clarification_answer_narrowed_candidate",
        authority_reference_ref="authority-gate",
    )
    require(reentry.trace.from_state is package.SemanticLifecycleState.CLARIFICATION_REQUIRED, "wrong re-entry source state")
    require(reentry.trace.to_state is package.SemanticLifecycleState.CANDIDATE_MEANING, "wrong re-entry target state")

    selected2 = replace(selected, record_id="selected-corrected", inherited_limitations=("explanation_only", "corrected_scope"))
    selected_manifest = lifecycle.append_lifecycle_successor(
        manifest,
        trace_record_id="trace-selected-base",
        from_record_ref=candidate.record_id,
        successor=selected,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="base_selection",
        authority_reference_ref="authority-gate",
    ).manifest
    blocked_outcome = package.NonSelectionOutcomeRecord(
        record_id="blocked-001",
        lineage_id="lineage-001",
        outcome_kind=package.NonSelectionOutcomeKind.AUTHORITY_BLOCKED,
        candidate_refs=(candidate.record_id,),
        reasons=("external_permission_absent",),
        required_clarifications=(),
        external_authority_refs=("authority-gate",),
    )
    blocked = lifecycle.append_lifecycle_successor(
        selected_manifest,
        trace_record_id="trace-blocked",
        from_record_ref=selected.record_id,
        successor=blocked_outcome,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="meaning_selected_but_external_permission_absent",
        authority_reference_ref="authority-gate",
    )
    require(
        blocked.trace.to_state is package.SemanticLifecycleState.AUTHORITY_BLOCKED,
        "selected-to-blocked transition failed",
    )

    refused_outcome = package.NonSelectionOutcomeRecord(
        record_id="refused-001",
        lineage_id="lineage-001",
        outcome_kind=package.NonSelectionOutcomeKind.REFUSED,
        candidate_refs=(candidate.record_id,),
        reasons=("requested_consequence_prohibited",),
        required_clarifications=(),
        external_authority_refs=("authority-gate",),
    )
    refused = lifecycle.append_lifecycle_successor(
        selected_manifest,
        trace_record_id="trace-refused",
        from_record_ref=selected.record_id,
        successor=refused_outcome,
        transition_kind=package.SemanticTransitionKind.REJECTION,
        reason="selected_meaning_does_not_authorize_prohibited_consequence",
        authority_reference_ref="authority-gate",
    )
    require(
        refused.trace.to_state is package.SemanticLifecycleState.REFUSED,
        "selected-to-refused transition failed",
    )

    corrected = lifecycle.append_lifecycle_successor(
        selected_manifest,
        trace_record_id="trace-correction",
        from_record_ref=selected.record_id,
        successor=selected2,
        transition_kind=package.SemanticTransitionKind.CORRECTION,
        reason="corrected_inherited_scope_without_mutation",
        authority_reference_ref="authority-gate",
    )
    require(selected_manifest.selected_governed_meanings[-1] == selected, "predecessor changed")
    require(corrected.trace.transition_kind is package.SemanticTransitionKind.CORRECTION, "correction trace missing")
    require(corrected.trace.from_state is corrected.trace.to_state, "correction changed lifecycle state")

    bad_correction = lifecycle.evaluate_lifecycle_transition(
        manifest,
        from_record_ref=candidate.record_id,
        successor=selected,
        transition_kind=package.SemanticTransitionKind.CORRECTION,
        reason="must_not_escalate_via_correction",
        authority_reference_ref="authority-gate",
    )
    require(not bad_correction.allowed, "cross-kind correction was allowed")

    containment = package.DeliveryContainmentLinkRecord(
        record_id="containment-001",
        lineage_id="lineage-001",
        prior_link_ref=expression.record_id,
        disposition=package.DeliveryContainmentKind.CONTAINMENT_LINKED,
        external_receipt_ref="containment-receipt-001",
    )
    before_validation = replace(
        final_manifest,
        validation_links=(),
        delivery_or_containment_links=(),
        semantic_transition_traces=final_manifest.semantic_transition_traces[:4],
    )
    contained = lifecycle.append_lifecycle_successor(
        before_validation,
        trace_record_id="trace-containment",
        from_record_ref=expression.record_id,
        successor=containment,
        transition_kind=package.SemanticTransitionKind.CONTAINMENT,
        reason="expression_contained_before_delivery",
        authority_reference_ref="authority-containment",
    )
    require(contained.manifest.delivery_or_containment_links[-1] == containment, "containment missing")

    require(tuple(package.__all__) == root_exports_before, "Slice 35A root exports changed")
    require(lifecycle.LIFECYCLE_SPEC_VERSION.endswith("-v1"), "spec version missing")

    print("SLICE 35C BEHAVIOR TEST: PASS")
    print(f"lifecycle_module={LIFECYCLE_MODULE}")
    print(f"transition_rules={len(lifecycle.LIFECYCLE_TRANSITION_RULES)}")
    print("full_chain_transitions=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
