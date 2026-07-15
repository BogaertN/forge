#!/usr/bin/env python3
"""Behavior tests for Slice 35A MeaningStructureManifest core schema."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
import importlib
import inspect
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = "aiweb_language_core_bootstrap.meaning_structure_manifest"
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

EXPECTED_EXPORTS = (
    "AUTHORITY_DOCUMENT",
    "CandidateMeaningRecord",
    "DeliveryContainmentKind",
    "DeliveryContainmentLinkRecord",
    "ExpressionLinkRecord",
    "ExternalAuthorityKind",
    "ExternalAuthorityReferenceRecord",
    "GovernedOutwardMeaningRecord",
    "GovernedResultReferenceRecord",
    "LineageOriginKind",
    "LineageRootRecord",
    "MeaningStructureManifestV1",
    "NonSelectionOutcomeKind",
    "NonSelectionOutcomeRecord",
    "PACKAGE_ID",
    "PACKAGE_NAME",
    "SCHEMA_ABBREVIATION",
    "SCHEMA_ID",
    "SCHEMA_NAME",
    "SCHEMA_VERSION",
    "SelectedGovernedMeaningRecord",
    "SemanticDirection",
    "SemanticLifecycleState",
    "SemanticPreservationClass",
    "SemanticRecordKind",
    "SemanticTransitionKind",
    "SemanticTransitionTraceRecord",
    "ValidationLinkRecord",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_import_probe(statement: str) -> None:
    with tempfile.TemporaryDirectory(prefix="aiweb_slice35a_import_") as tmp:
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
        require(
            completed.returncode == 0,
            f"import probe failed: {statement!r}\n{completed.stderr}",
        )
        require(before == after, "import created files or runtime state")


def make_records(package):
    preservation = (
        package.SemanticPreservationClass.NEGATION,
        package.SemanticPreservationClass.NON_LLM_PROVENANCE,
    )
    root = package.LineageRootRecord(
        lineage_id="lineage-001",
        origin_kind=(
            package.LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION
        ),
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
        outcome_kind=(
            package.NonSelectionOutcomeKind.CLARIFICATION_REQUIRED
        ),
        candidate_refs=(candidate.record_id,),
        reasons=("missing_referent",),
        required_clarifications=("identify_the_source",),
        external_authority_refs=(),
    )
    authority = package.ExternalAuthorityReferenceRecord(
        record_id="authority-ref-001",
        lineage_id=root.lineage_id,
        authority_kind=(
            package.ExternalAuthorityKind.EVIDENCE_OR_CLAIM_STATUS
        ),
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
        to_state=(
            package.SemanticLifecycleState.SELECTED_GOVERNED_MEANING
        ),
        transition_kind=package.SemanticTransitionKind.ANCESTRY,
        reason="later_gate_selection_reference",
        authority_reference_ref="gate-receipt-001",
    )
    manifest = package.MeaningStructureManifestV1(
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
    return (
        root,
        candidate,
        outcome,
        authority,
        selected,
        result_ref,
        outward,
        expression,
        validation,
        delivery,
        transition,
        manifest,
    )


def main() -> int:
    run_import_probe(f"import {PACKAGE}")
    run_import_probe(f"from {PACKAGE} import *")

    package = importlib.import_module(PACKAGE)
    require(package.__all__ == EXPECTED_EXPORTS, "unexpected __all__")

    public_names = tuple(
        sorted(name for name in vars(package) if not name.startswith("_"))
    )
    require(
        public_names == tuple(sorted(EXPECTED_EXPORTS)),
        f"undocumented public exports: {public_names}",
    )

    star_namespace: dict[str, object] = {}
    exec(f"from {PACKAGE} import *", star_namespace, star_namespace)
    star_names = tuple(sorted(name for name in star_namespace if name != "__builtins__"))
    require(star_names == tuple(sorted(EXPECTED_EXPORTS)), "star import mismatch")
    for name in EXPECTED_EXPORTS:
        require(hasattr(package, name), f"missing export: {name}")
        require(
            star_namespace[name] is getattr(package, name),
            f"star export identity mismatch: {name}",
        )

    records = make_records(package)
    record_classes = tuple(type(record) for record in records)
    for record, record_class in zip(records, record_classes):
        require(is_dataclass(record), f"not a dataclass: {record_class.__name__}")
        require(
            record_class.__dataclass_params__.frozen,
            f"not frozen: {record_class.__name__}",
        )
        require(hasattr(record_class, "__slots__"), f"not slotted: {record_class.__name__}")
        require(hash(record) == hash(record), f"unstable hash: {record_class.__name__}")
        try:
            first_field = next(iter(record_class.__dataclass_fields__))
            setattr(record, first_field, "changed")
        except (FrozenInstanceError, AttributeError):
            pass
        else:
            raise AssertionError(f"mutable record: {record_class.__name__}")

        constructor_values = {
            item.name: getattr(record, item.name)
            for item in fields(record_class)
            if item.init
        }
        try:
            record_class(**constructor_values, unsupported_field="must_fail")
        except TypeError:
            pass
        else:
            raise AssertionError(
                f"unsupported field accepted: {record_class.__name__}"
            )

    manifest_a = records[-1]
    manifest_b = make_records(package)[-1]
    require(manifest_a == manifest_b, "deterministic equality failed")
    require(hash(manifest_a) == hash(manifest_b), "deterministic hashing failed")



    forbidden_members = {
        "serialize",
        "deserialize",
        "to_dict",
        "from_dict",
        "validate",
        "transition",
        "save",
        "load",
        "write",
        "read",
        "migrate",
    }
    for record_class in set(record_classes):
        present = forbidden_members.intersection(vars(record_class))
        require(
            not present,
            f"forbidden behavior on {record_class.__name__}: {sorted(present)}",
        )

    print("SLICE 35A BEHAVIOR TEST: PASS")
    print(f"package={PACKAGE}")
    print(f"exports={len(EXPECTED_EXPORTS)}")
    print(f"record_instances={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
