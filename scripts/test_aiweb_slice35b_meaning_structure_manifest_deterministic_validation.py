#!/usr/bin/env python3
"""Behavior tests for Slice 35B MSM-v1 deterministic validation."""

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
VALIDATION_MODULE = f"{PACKAGE}.validation"
EXPECTED_VALIDATION_EXPORTS = (
    "ManifestValidationCode",
    "ManifestValidationIssue",
    "ManifestValidationReport",
    "MeaningStructureManifestValidationError",
    "assert_valid_manifest",
    "validate_manifest",
    "validate_record",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def import_probe(statement: str) -> None:
    with tempfile.TemporaryDirectory(prefix="aiweb_slice35b_import_") as tmp:
        before = tuple(sorted(Path(tmp).iterdir()))
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
        after = tuple(sorted(Path(tmp).iterdir()))
        require(completed.returncode == 0, completed.stderr)
        require(before == after, "validation import created files or runtime state")


def make_manifest(package):
    preservation = (
        package.SemanticPreservationClass.NEGATION,
        package.SemanticPreservationClass.NON_LLM_PROVENANCE,
    )
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
        meaning_modifiers=("not_yet_verified",),
        ambiguity_reasons=(),
        unresolved_referents=(),
        authority_sensitive_implications=("explanation_not_execution",),
        preservation_classes=preservation,
    )
    outcome = package.NonSelectionOutcomeRecord(
        record_id="outcome-001",
        lineage_id=root.lineage_id,
        outcome_kind=package.NonSelectionOutcomeKind.CLARIFICATION_REQUIRED,
        candidate_refs=(candidate.record_id,),
        reasons=("missing_referent",),
        required_clarifications=("identify_the_source",),
        external_authority_refs=(),
    )
    authority = package.ExternalAuthorityReferenceRecord(
        record_id="authority-ref-001",
        lineage_id=root.lineage_id,
        authority_kind=package.ExternalAuthorityKind.EVIDENCE_OR_CLAIM_STATUS,
        external_object_ref="verification-receipt-001",
        semantic_relevance="bounds_claim_strength",
    )
    selected = package.SelectedGovernedMeaningRecord(
        record_id="selected-001",
        lineage_id=root.lineage_id,
        selected_candidate_ref=candidate.record_id,
        selection_authority_ref="gate-receipt-001",
        communicative_act=candidate.communicative_act,
        concept_refs=candidate.concept_refs,
        relation_refs=candidate.relation_refs,
        meaning_modifiers=candidate.meaning_modifiers,
        inherited_limitations=("explanation_only",),
        authority_sensitive_distinctions=("selected_not_authorized",),
        preservation_classes=preservation,
    )
    result_ref = package.GovernedResultReferenceRecord(
        record_id="result-ref-001",
        lineage_id=root.lineage_id,
        selected_meaning_ref=selected.record_id,
        external_authority_ref=authority.record_id,
        semantic_relevance="verified_status_is_externally_owned",
    )
    outward = package.GovernedOutwardMeaningRecord(
        record_id="outward-001",
        lineage_id=root.lineage_id,
        outward_basis_refs=(result_ref.record_id,),
        prior_selected_meaning_ref=selected.record_id,
        permitted_claims=("the_bounded_check_passed",),
        required_qualifications=("within_tested_scope",),
        prohibited_enlargements=("production_ready",),
        external_dependency_refs=(authority.record_id,),
        preservation_classes=preservation,
    )
    expression = package.ExpressionLinkRecord(
        record_id="expression-link-001",
        lineage_id=root.lineage_id,
        governed_outward_meaning_ref=outward.record_id,
        expression_candidate_ref="render-candidate-001",
    )
    validation = package.ValidationLinkRecord(
        record_id="validation-link-001",
        lineage_id=root.lineage_id,
        expression_link_ref=expression.record_id,
        external_validation_receipt_ref="echo-receipt-001",
        external_validation_disposition="accepted_within_scope",
    )
    delivery = package.DeliveryContainmentLinkRecord(
        record_id="delivery-link-001",
        lineage_id=root.lineage_id,
        prior_link_ref=validation.record_id,
        disposition=package.DeliveryContainmentKind.CONTAINMENT_LINKED,
        external_receipt_ref="containment-receipt-001",
    )
    transition = package.SemanticTransitionTraceRecord(
        record_id="transition-001",
        lineage_id=root.lineage_id,
        from_record_ref=candidate.record_id,
        to_record_ref=selected.record_id,
        from_state=package.SemanticLifecycleState.CANDIDATE_MEANING,
        to_state=package.SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="later_gate_selection_reference",
        authority_reference_ref="gate-receipt-001",
    )
    return package.MeaningStructureManifestV1(
        manifest_id="msm-001",
        lineage_root=root,
        candidate_meanings=(candidate,),
        non_selection_outcomes=(outcome,),
        selected_governed_meanings=(selected,),
        governed_result_references=(result_ref,),
        governed_outward_meanings=(outward,),
        expression_links=(expression,),
        validation_links=(validation,),
        delivery_or_containment_links=(delivery,),
        external_authority_references=(authority,),
        semantic_transition_traces=(transition,),
    )


def codes(report) -> tuple[str, ...]:
    return tuple(item.code.value for item in report.issues)


def main() -> int:
    import_probe(f"import {VALIDATION_MODULE}")
    import_probe(f"from {VALIDATION_MODULE} import *")

    package = importlib.import_module(PACKAGE)
    validation = importlib.import_module(VALIDATION_MODULE)
    require(validation.__all__ == EXPECTED_VALIDATION_EXPORTS, "validation __all__ mismatch")

    star: dict[str, object] = {}
    exec(f"from {VALIDATION_MODULE} import *", star, star)
    star_names = tuple(sorted(name for name in star if name != "__builtins__"))
    require(star_names == tuple(sorted(EXPECTED_VALIDATION_EXPORTS)), "validation star import mismatch")
    for name in EXPECTED_VALIDATION_EXPORTS:
        require(star[name] is getattr(validation, name), f"validation export mismatch: {name}")

    root_before = tuple(package.__all__)
    require("validate_manifest" not in root_before, "Slice 35A root exports were expanded")

    manifest = make_manifest(package)
    report_a = validation.validate_manifest(manifest)
    report_b = validation.validate_manifest(manifest)
    require(report_a.ok, f"valid manifest rejected: {report_a.issues}")
    require(report_a == report_b, "validation report is not deterministic")
    validation.assert_valid_manifest(manifest)
    require(validation.validate_record(manifest.lineage_root).ok, "valid record rejected")

    try:
        report_a.issues = ()
    except (FrozenInstanceError, AttributeError):
        pass
    else:
        raise AssertionError("validation report is mutable")

    invalid_identifier = replace(manifest, manifest_id="bad id")
    require("invalid_identifier" in codes(validation.validate_manifest(invalid_identifier)), "invalid identifier not rejected")

    wrong_direction_root = replace(manifest.lineage_root, direction=package.SemanticDirection.OUTWARD)
    wrong_direction = replace(manifest, lineage_root=wrong_direction_root)
    require("origin_direction_mismatch" in codes(validation.validate_manifest(wrong_direction)), "origin-direction mismatch not rejected")

    wrong_lineage_candidate = replace(manifest.candidate_meanings[0], lineage_id="lineage-999")
    wrong_lineage = replace(manifest, candidate_meanings=(wrong_lineage_candidate,))
    require("lineage_mismatch" in codes(validation.validate_manifest(wrong_lineage)), "lineage mismatch not rejected")

    duplicate_candidate = replace(manifest.candidate_meanings[0])
    duplicate_id = replace(manifest, candidate_meanings=(manifest.candidate_meanings[0], duplicate_candidate))
    require("duplicate_record_id" in codes(validation.validate_manifest(duplicate_id)), "duplicate record id not rejected")

    unresolved_selected = replace(manifest.selected_governed_meanings[0], selected_candidate_ref="candidate-missing")
    unresolved = replace(manifest, selected_governed_meanings=(unresolved_selected,))
    require("unresolved_reference" in codes(validation.validate_manifest(unresolved)), "unresolved reference not rejected")

    wrong_kind_result = replace(manifest.governed_result_references[0], external_authority_ref=manifest.candidate_meanings[0].record_id)
    wrong_kind = replace(manifest, governed_result_references=(wrong_kind_result,))
    require("reference_kind_mismatch" in codes(validation.validate_manifest(wrong_kind)), "reference kind mismatch not rejected")

    empty_reason = replace(manifest.non_selection_outcomes[0], reasons=())
    empty_reason_manifest = replace(manifest, non_selection_outcomes=(empty_reason,))
    require("required_value_missing" in codes(validation.validate_manifest(empty_reason_manifest)), "missing reason not rejected")

    wrong_tuple_candidate = replace(manifest.candidate_meanings[0], concept_refs=["concept-001"])
    wrong_tuple = replace(manifest, candidate_meanings=(wrong_tuple_candidate,))
    require("invalid_tuple" in codes(validation.validate_manifest(wrong_tuple)), "list accepted where tuple required")

    tampered = make_manifest(package)
    object.__setattr__(
        tampered.candidate_meanings[0],
        "lifecycle_state",
        package.SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
    )
    require("lifecycle_state_mismatch" in codes(validation.validate_manifest(tampered)), "state tampering not rejected")

    try:
        validation.assert_valid_manifest(unresolved)
    except validation.MeaningStructureManifestValidationError as exc:
        require(exc.report == validation.validate_manifest(unresolved), "raised report mismatch")
    else:
        raise AssertionError("assert_valid_manifest did not fail closed")

    require(tuple(package.__all__) == root_before, "validation changed Slice 35A root exports")

    print("SLICE 35B BEHAVIOR TEST: PASS")
    print(f"validation_module={VALIDATION_MODULE}")
    print(f"validation_exports={len(EXPECTED_VALIDATION_EXPORTS)}")
    print("valid_manifest_issues=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
