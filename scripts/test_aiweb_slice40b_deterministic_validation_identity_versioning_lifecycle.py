#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 40B gate governance."""

from __future__ import annotations

import argparse
import ast
from dataclasses import FrozenInstanceError, fields, replace
import importlib
from pathlib import Path
import sys


CORE_PACKAGE = "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
PACKAGE = f"{CORE_PACKAGE}.governed_lifecycle"


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []
        self.malformed_cases = 0

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)


def codes(report) -> set[str]:
    return {item.code.value for item in report.issues}


def make_bundle(core, module, family):
    profile = module.with_expected_id(
        core.VerbalCognitionGateProfileIdentity(
            profile_id="gate_profile:placeholder",
            profile_key=f"{family.value}_default_profile",
            profile_version="v1.0.0",
            gate_family=family,
            governing_authority_refs=(
                "canonical_roadmap:slice40b",
                "document6:verbal_cognition_gate_engine:v1",
            ),
            required_schema_refs=(
                "slice39g:manifest_candidate_integration:v1",
                core.SCHEMA_VERSION,
            ),
            exact_profile_only=True,
        )
    )
    identity = module.with_expected_id(
        core.VerbalCognitionGateIdentity(
            gate_id="gate:placeholder",
            gate_key=f"{family.value}_gate",
            gate_version="v1.0.0",
            gate_family=family,
            gate_profile_ref=profile.profile_id,
        )
    )
    candidate = module.with_expected_id(
        core.GateCandidateInputReference(
            candidate_input_ref_id="gate_candidate_input:placeholder",
            candidate_meaning_id=f"candidate_meaning:{family.value}:demo",
            candidate_state_id=f"candidate_state:{family.value}:demo",
            candidate_lineage_id=f"candidate_lineage:{family.value}:demo",
            candidate_identity_ref=f"candidate_identity:{family.value}:demo",
            candidate_content_ref=f"candidate_content:{family.value}:demo",
            candidate_provenance_ref=f"candidate_provenance:{family.value}:demo",
            construction_receipt_ref=f"candidate_receipt:{family.value}:demo",
            manifest_candidate_record_ref=f"msm_candidate:{family.value}:demo",
            manifest_companion_ref=f"manifest_companion:{family.value}:demo",
            construction_trace_ref=f"construction_trace:{family.value}:demo",
            limitation_reference_ref=f"candidate_limitation:{family.value}:demo",
            alternative_relationship_refs=(
                f"candidate_alternative:{family.value}:demo",
            ),
        )
    )
    requirement = module.with_expected_id(
        core.GateRequirementReference(
            requirement_reference_id="gate_requirement:placeholder",
            gate_family=family,
            requirement_key=f"{family.value}_requirement",
            requirement_version="v1.0.0",
            candidate_input_ref=candidate.candidate_input_ref_id,
            subject_record_refs=(candidate.candidate_meaning_id,),
            required_authority_refs=(
                "document6:verbal_cognition_gate_engine:v1",
            ),
            required_record_refs=(f"candidate_record:{family.value}:demo",),
            required_relation_refs=(f"candidate_relation:{family.value}:demo",),
            limitation_refs=(f"gate_limitation:{family.value}:declared",),
        )
    )
    reason = module.with_expected_id(
        core.GateReasonGround(
            reason_ground_id="gate_reason:placeholder",
            gate_family=family,
            reason_key=f"{family.value}_validation_ground",
            candidate_input_ref=candidate.candidate_input_ref_id,
            requirement_reference_ids=(requirement.requirement_reference_id,),
            supporting_record_refs=(f"supporting_record:{family.value}:demo",),
            conflicting_record_refs=(),
            missing_record_refs=(),
            unknown_record_refs=(),
            authority_refs=(
                "document6:verbal_cognition_gate_engine:v1",
            ),
            limitation_refs=(f"gate_limitation:{family.value}:declared",),
        )
    )
    trace = module.with_expected_id(
        core.GateTraceReference(
            trace_reference_id="gate_trace:placeholder",
            candidate_input_ref=candidate.candidate_input_ref_id,
            source_span_refs=(f"source_span:{family.value}:demo",),
            candidate_trace_refs=(f"candidate_trace:{family.value}:demo",),
            construction_trace_refs=(f"construction_trace:{family.value}:demo",),
            structural_trace_refs=(f"structural_trace:{family.value}:demo",),
            concept_sense_trace_refs=(f"concept_trace:{family.value}:demo",),
            predicate_role_frame_trace_refs=(f"predicate_trace:{family.value}:demo",),
            alternative_relationship_refs=candidate.alternative_relationship_refs,
            predecessor_receipt_refs=(f"slice39h_receipt:{family.value}:demo",),
        )
    )
    provenance = module.with_expected_id(
        core.GateProvenanceReference(
            provenance_reference_id="gate_provenance:placeholder",
            candidate_input_ref=candidate.candidate_input_ref_id,
            source_event_id=f"source_event:{family.value}:demo",
            source_sha256="0" * 64,
            candidate_provenance_ref=candidate.candidate_provenance_ref,
            gate_profile_ref=profile.profile_id,
            governing_document_refs=(
                "canonical_roadmap:slice40b",
                "document6:verbal_cognition_gate_engine:v1",
            ),
            authority_version_refs=(
                ("canonical_roadmap", "2026-07-12"),
                ("document6", "v1"),
            ),
            schema_version_refs=(
                ("slice39g", "v1"),
                ("slice40a", "v1"),
            ),
            external_resource_refs=(),
        )
    )
    limitation = module.with_expected_id(
        core.GateLimitationReference(
            limitation_reference_id="gate_limitation:placeholder",
            candidate_input_ref=candidate.candidate_input_ref_id,
            limitation_key="validation_only_no_gate_evaluation",
            reason_refs=("slice40b_no_evaluator",),
            affected_requirement_refs=(requirement.requirement_reference_id,),
            later_authority_refs=(
                f"slice40_{family.value}_runtime",
                "slice40g_gate_composition",
            ),
        )
    )
    review = module.with_expected_id(
        core.VerbalCognitionGateReviewRecord(
            review_record_id="gate_review:placeholder",
            identity=identity,
            profile=profile,
            candidate_input=candidate,
            requirement_references=(requirement,),
            reason_grounds=(reason,),
            evaluation_state=core.GateEvaluationState.NOT_EVALUATED,
            trace_references=(trace,),
            provenance_reference=provenance,
            limitation_references=(limitation,),
        )
    )
    custody = module.with_expected_id(
        module.GateVersionCustody(
            custody_id="gate_version_custody:placeholder",
            review_record_id=review.review_record_id,
            gate_id=identity.gate_id,
            gate_version=identity.gate_version,
            gate_profile_id=profile.profile_id,
            gate_profile_version=profile.profile_version,
            gate_family=family,
            core_schema_version=core.SCHEMA_VERSION,
            core_spec_version=core.SPEC_VERSION,
            identity_schema_id=core.GATE_IDENTITY_SCHEMA_ID,
            profile_schema_id=core.GATE_PROFILE_SCHEMA_ID,
            candidate_input_schema_id=core.CANDIDATE_INPUT_REFERENCE_SCHEMA_ID,
            requirement_schema_id=core.REQUIREMENT_REFERENCE_SCHEMA_ID,
            reason_ground_schema_id=core.REASON_GROUND_SCHEMA_ID,
            trace_schema_id=core.TRACE_REFERENCE_SCHEMA_ID,
            provenance_schema_id=core.PROVENANCE_REFERENCE_SCHEMA_ID,
            limitation_schema_id=core.LIMITATION_REFERENCE_SCHEMA_ID,
            review_record_schema_id=core.REVIEW_RECORD_SCHEMA_ID,
            governing_authority_versions=(
                ("canonical_roadmap", "2026-07-12"),
                ("document6", "v1"),
            ),
            predecessor_schema_versions=(
                (core.GATE_IDENTITY_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.GATE_PROFILE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.CANDIDATE_INPUT_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.REQUIREMENT_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.REASON_GROUND_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.TRACE_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.PROVENANCE_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.LIMITATION_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.REVIEW_RECORD_SCHEMA_ID, core.SCHEMA_VERSION),
            ),
            canonical_field_order_version=module.CANONICAL_FIELD_ORDER_VERSION,
            digest_algorithm=module.DIGEST_ALGORITHM,
            non_llm_provenance=True,
            timestamps_in_identity=False,
            randomness_in_identity=False,
            process_identity_in_identity=False,
            filesystem_state_in_identity=False,
            environment_state_in_identity=False,
            hash_table_order_in_identity=False,
            runtime_evaluator_authorized=False,
            gate_evaluation_authorized=False,
            gate_outcome_authorized=False,
            selected_meaning_authorized=False,
            route_authorized=False,
            tool_authorized=False,
            action_authorized=False,
            memory_authorized=False,
            rendering_authorized=False,
            delivery_authorized=False,
        )
    )

    stages = (
        module.GateLifecycleStage.SCHEMA_DECLARED,
        module.GateLifecycleStage.PROFILE_VERSION_BOUND,
        module.GateLifecycleStage.CANDIDATE_REFERENCE_BOUND,
        module.GateLifecycleStage.PROVENANCE_VALIDATED,
        module.GateLifecycleStage.RECORD_VALIDATED,
        module.GateLifecycleStage.RECORD_SEALED,
    )
    lifecycle_records = []
    predecessor = ()
    for stage in stages:
        item = module.with_expected_id(
            module.GateLifecycleRecord(
                lifecycle_record_id="gate_lifecycle:placeholder",
                review_record_id=review.review_record_id,
                gate_id=identity.gate_id,
                gate_profile_id=profile.profile_id,
                candidate_input_ref=candidate.candidate_input_ref_id,
                provenance_reference_id=provenance.provenance_reference_id,
                stage=stage,
                version_custody_ref=custody.custody_id,
                predecessor_lifecycle_record_ids=predecessor,
                reason_refs=(f"lifecycle_reason:{stage.value}",),
                automatic_progression=False,
                validation_performed=stage in (
                    module.GateLifecycleStage.RECORD_VALIDATED,
                    module.GateLifecycleStage.RECORD_SEALED,
                ),
                provenance_validation_performed=stage in (
                    module.GateLifecycleStage.PROVENANCE_VALIDATED,
                    module.GateLifecycleStage.RECORD_VALIDATED,
                    module.GateLifecycleStage.RECORD_SEALED,
                ),
                gate_evaluation_created=False,
                gate_outcome_created=False,
                candidate_disposition_created=False,
                selected_meaning_created=False,
                truth_determined=False,
                evidence_validated=False,
                permission_granted=False,
                execution_authorized=False,
                route_created=False,
                tool_invoked=False,
                action_performed=False,
                memory_accessed=False,
                rendered=False,
                delivered=False,
                external_resource_loaded=False,
            )
        )
        lifecycle_records.append(item)
        predecessor = (item.lifecycle_record_id,)

    kinds = (
        module.GateLifecycleTransitionKind.BIND_PROFILE_VERSION,
        module.GateLifecycleTransitionKind.BIND_CANDIDATE_REFERENCE,
        module.GateLifecycleTransitionKind.VALIDATE_PROVENANCE,
        module.GateLifecycleTransitionKind.VALIDATE_RECORD,
        module.GateLifecycleTransitionKind.SEAL_RECORD,
    )
    lifecycle_transitions = []
    predecessor_transitions = ()
    for source, target, kind in zip(
        lifecycle_records,
        lifecycle_records[1:],
        kinds,
    ):
        item = module.with_expected_id(
            module.GateLifecycleTransitionRecord(
                transition_id="gate_lifecycle_transition:placeholder",
                review_record_id=review.review_record_id,
                source_lifecycle_record_id=source.lifecycle_record_id,
                target_lifecycle_record_id=target.lifecycle_record_id,
                from_stage=source.stage,
                to_stage=target.stage,
                transition_kind=kind,
                version_custody_ref=custody.custody_id,
                reason_refs=(f"transition_reason:{kind.value}",),
                predecessor_transition_refs=predecessor_transitions,
                automatic_transition=False,
                gate_evaluation_created=False,
                gate_outcome_created=False,
                candidate_disposition_created=False,
                selected_meaning_created=False,
                permission_granted=False,
                execution_authorized=False,
                route_created=False,
                tool_invoked=False,
                action_performed=False,
                memory_accessed=False,
                rendered=False,
                delivered=False,
            )
        )
        lifecycle_transitions.append(item)
        predecessor_transitions = (item.transition_id,)

    bundle = module.GateGovernanceBundle(
        bundle_id="gate_governance_bundle:placeholder",
        review_record=review,
        version_custody=custody,
        lifecycle_records=tuple(lifecycle_records),
        lifecycle_transitions=tuple(lifecycle_transitions),
        canonical_digest="0" * 64,
        validation_complete=True,
        provenance_validation_complete=True,
        schema_versions_known=True,
        gate_profile_version_known=True,
        runtime_evaluator_installed=False,
        gate_evaluation_performed=False,
        gate_outcome_created=False,
        candidate_disposition_created=False,
        selected_meaning_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        external_resource_loaded=False,
    )
    return module.with_expected_id(bundle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    core = importlib.import_module(CORE_PACKAGE)
    module = importlib.import_module(PACKAGE)
    ledger = Ledger()

    families = tuple(core.VerbalCognitionGateFamily)
    bundles = tuple(make_bundle(core, module, family) for family in families)

    ledger.check(
        module.SLICE40B_ACCEPTED_PARENT_HEAD
        == "09a0d20c91994b72edcd63c15780592d56394225",
        "accepted parent head",
    )
    ledger.check(
        module.SLICE40B_ACCEPTED_PARENT_TREE
        == "435de181f15b94824d1204a45d3f4c7d7f244f7b",
        "accepted parent tree",
    )
    ledger.check(
        module.SLICE40B_ACCEPTED_PARENT_SUBJECT
        == "Slice 40A verbal cognition gate core schema",
        "accepted parent subject",
    )
    ledger.check(module.DIGEST_ALGORITHM == "sha256", "digest algorithm")
    ledger.check(len(module.SUPPORTED_RECORD_TYPES) == 13, "record type count")
    ledger.check(
        len(module.GATE_LIFECYCLE_TRANSITION_RULES) == 29,
        "transition rule count",
    )
    ledger.check(
        tuple(item.value for item in module.GateLifecycleStage)
        == (
            "schema_declared",
            "profile_version_bound",
            "candidate_reference_bound",
            "provenance_validated",
            "record_validated",
            "record_sealed",
            "validation_incomplete",
            "unknown_version_blocked",
            "malformed_record_blocked",
            "provenance_invalid_blocked",
        ),
        "lifecycle stage vocabulary",
    )

    for bundle in bundles:
        report = module.validate_governance_bundle(bundle)
        ledger.check(report.ok, f"valid bundle {bundle.review_record.identity.gate_family}: {report.issues}")
        ledger.check(
            module.assert_valid_governance_bundle(bundle) is bundle,
            "assert valid bundle returns exact record",
        )
        ledger.check(
            module.validate_review_record(bundle.review_record).ok,
            "valid review record",
        )
        ledger.check(
            module.validate_version_custody(
                bundle.version_custody,
                review_record=bundle.review_record,
            ).ok,
            "valid exact version custody",
        )
        ledger.check(
            module.canonical_record_bytes(bundle)
            == module.canonical_record_bytes(bundle),
            "canonical bytes stable",
        )
        ledger.check(
            module.deterministic_record_digest(bundle)
            == module.deterministic_record_digest(bundle),
            "record digest stable",
        )
        ledger.check(
            bundle.canonical_digest == module.expected_bundle_digest(bundle),
            "bundle digest exact",
        )
        ledger.check(
            bundle.bundle_id == module.expected_bundle_id(bundle),
            "bundle identity exact",
        )

        for record_type in module.SUPPORTED_RECORD_TYPES:
            order = module.canonical_field_order(record_type)
            ledger.check(
                order == tuple(item.name for item in fields(record_type)),
                f"canonical field order {record_type.__name__}",
            )

        records_by_type = {
            type(bundle.review_record.identity): bundle.review_record.identity,
            type(bundle.review_record.profile): bundle.review_record.profile,
            type(bundle.review_record.candidate_input): bundle.review_record.candidate_input,
            type(bundle.review_record.requirement_references[0]): bundle.review_record.requirement_references[0],
            type(bundle.review_record.reason_grounds[0]): bundle.review_record.reason_grounds[0],
            type(bundle.review_record.trace_references[0]): bundle.review_record.trace_references[0],
            type(bundle.review_record.provenance_reference): bundle.review_record.provenance_reference,
            type(bundle.review_record.limitation_references[0]): bundle.review_record.limitation_references[0],
            type(bundle.review_record): bundle.review_record,
            type(bundle.version_custody): bundle.version_custody,
            type(bundle.lifecycle_records[0]): bundle.lifecycle_records[0],
            type(bundle.lifecycle_transitions[0]): bundle.lifecycle_transitions[0],
            type(bundle): bundle,
        }
        for record_type, record in records_by_type.items():
            pairs = tuple(
                (name, getattr(record, name))
                for name in reversed(module.canonical_field_order(record_type))
            )
            ledger.check(
                module.validate_field_pairs(record_type, pairs).ok,
                f"field pairs reorder {record_type.__name__}",
            )
            ledger.malformed(
                "duplicate_field"
                in codes(module.validate_field_pairs(record_type, pairs + (pairs[0],))),
                f"duplicate field rejected {record_type.__name__}",
            )
            ledger.malformed(
                "unknown_field"
                in codes(module.validate_field_pairs(record_type, pairs + (("unknown_field", "x"),))),
                f"unknown field rejected {record_type.__name__}",
            )
            ledger.malformed(
                "missing_field"
                in codes(module.validate_field_pairs(record_type, pairs[1:])),
                f"missing field rejected {record_type.__name__}",
            )

        for source, target, transition in zip(
            bundle.lifecycle_records,
            bundle.lifecycle_records[1:],
            bundle.lifecycle_transitions,
        ):
            decision = module.evaluate_lifecycle_transition(
                source,
                target,
                transition,
                bundle=bundle,
            )
            ledger.check(decision.allowed, f"allowed lifecycle {transition.transition_kind}")
            ledger.check(
                module.assert_lifecycle_transition(
                    source,
                    target,
                    transition,
                    bundle=bundle,
                )
                is transition,
                "assert lifecycle returns exact transition",
            )

    bundle = bundles[0]

    identity_changed = module.with_expected_id(
        replace(bundle.review_record.identity, gate_key="expectancy_gate_changed")
    )
    ledger.check(
        identity_changed.gate_id != bundle.review_record.identity.gate_id,
        "material identity content changes gate ID",
    )
    profile_changed = module.with_expected_id(
        replace(bundle.review_record.profile, profile_key="expectancy_profile_changed")
    )
    ledger.check(
        profile_changed.profile_id != bundle.review_record.profile.profile_id,
        "material profile content changes profile ID",
    )
    provenance_changed = module.with_expected_id(
        replace(bundle.review_record.provenance_reference, source_sha256="1" * 64)
    )
    ledger.check(
        provenance_changed.provenance_reference_id
        != bundle.review_record.provenance_reference.provenance_reference_id,
        "source provenance changes provenance ID",
    )

    unknown_identity = module.with_expected_id(
        replace(bundle.review_record.identity, gate_version="v2.0.0")
    )
    ledger.malformed(
        "unknown_version" in codes(module.validate_gate_identity(unknown_identity)),
        "unknown gate version rejected",
    )
    malformed_identity = module.with_expected_id(
        replace(bundle.review_record.identity, gate_version="1.0")
    )
    ledger.malformed(
        "invalid_version" in codes(module.validate_gate_identity(malformed_identity)),
        "malformed gate version rejected",
    )
    unknown_profile = module.with_expected_id(
        replace(bundle.review_record.profile, profile_version="v9.0.0")
    )
    ledger.malformed(
        "unknown_version" in codes(module.validate_gate_profile(unknown_profile)),
        "unknown profile version rejected",
    )
    malformed_sha = module.with_expected_id(
        replace(bundle.review_record.provenance_reference, source_sha256="ABC")
    )
    ledger.malformed(
        "invalid_sha256"
        in codes(module.validate_provenance_reference(malformed_sha)),
        "malformed provenance SHA rejected",
    )

    bad_provenance = module.with_expected_id(
        replace(
            bundle.review_record.provenance_reference,
            candidate_input_ref="gate_candidate_input:wrong",
        )
    )
    bad_review = module.with_expected_id(
        replace(bundle.review_record, provenance_reference=bad_provenance)
    )
    ledger.malformed(
        "provenance_mismatch" in codes(module.validate_review_record(bad_review)),
        "exact provenance cross-reference mismatch rejected",
    )

    bad_family_requirement = module.with_expected_id(
        replace(
            bundle.review_record.requirement_references[0],
            gate_family=core.VerbalCognitionGateFamily.CONGRUITY,
        )
    )
    bad_review = module.with_expected_id(
        replace(bundle.review_record, requirement_references=(bad_family_requirement,))
    )
    ledger.malformed(
        "cross_record_identity_mismatch"
        in codes(module.validate_review_record(bad_review)),
        "requirement family mismatch rejected",
    )

    unknown_custody = module.with_expected_id(
        replace(bundle.version_custody, gate_profile_version="v2.0.0")
    )
    ledger.malformed(
        "unknown_version"
        in codes(
            module.validate_version_custody(
                unknown_custody,
                review_record=bundle.review_record,
            )
        ),
        "unknown custody profile version rejected",
    )
    mismatch_custody = module.with_expected_id(
        replace(bundle.version_custody, gate_id="gate:wrong")
    )
    ledger.malformed(
        "cross_record_identity_mismatch"
        in codes(
            module.validate_version_custody(
                mismatch_custody,
                review_record=bundle.review_record,
            )
        ),
        "custody gate identity mismatch rejected",
    )

    for name in (
        "timestamps_in_identity",
        "randomness_in_identity",
        "process_identity_in_identity",
        "filesystem_state_in_identity",
        "environment_state_in_identity",
        "hash_table_order_in_identity",
    ):
        bad = module.with_expected_id(
            replace(bundle.version_custody, **{name: True})
        )
        ledger.malformed(
            "nondeterministic_input_prohibited"
            in codes(module.validate_version_custody(bad)),
            f"nondeterministic identity input rejected {name}",
        )

    for name in (
        "runtime_evaluator_authorized",
        "gate_evaluation_authorized",
        "gate_outcome_authorized",
        "selected_meaning_authorized",
        "route_authorized",
        "tool_authorized",
        "action_authorized",
        "memory_authorized",
        "rendering_authorized",
        "delivery_authorized",
    ):
        bad = module.with_expected_id(
            replace(bundle.version_custody, **{name: True})
        )
        ledger.malformed(
            not module.validate_version_custody(bad).ok,
            f"forbidden custody authority rejected {name}",
        )

    invalid_skip_target = module.with_expected_id(
        replace(
            bundle.lifecycle_records[-1],
            predecessor_lifecycle_record_ids=(
                bundle.lifecycle_records[0].lifecycle_record_id,
            ),
        )
    )
    invalid_skip = module.with_expected_id(
        replace(
            bundle.lifecycle_transitions[0],
            target_lifecycle_record_id=invalid_skip_target.lifecycle_record_id,
            to_stage=module.GateLifecycleStage.RECORD_SEALED,
            transition_kind=module.GateLifecycleTransitionKind.SEAL_RECORD,
        )
    )
    ledger.malformed(
        not module.evaluate_lifecycle_transition(
            bundle.lifecycle_records[0],
            invalid_skip_target,
            invalid_skip,
            bundle=bundle,
        ).allowed,
        "schema-to-sealed lifecycle skip rejected",
    )

    automatic = module.with_expected_id(
        replace(bundle.lifecycle_transitions[0], automatic_transition=True)
    )
    ledger.malformed(
        "automatic_transition_prohibited"
        in codes(module.validate_lifecycle_transition_record(automatic)),
        "automatic transition rejected",
    )
    outcome_transition = module.with_expected_id(
        replace(bundle.lifecycle_transitions[0], gate_outcome_created=True)
    )
    ledger.malformed(
        "gate_outcome_prohibited"
        in codes(module.validate_lifecycle_transition_record(outcome_transition)),
        "gate outcome transition rejected",
    )
    evaluation_lifecycle = module.with_expected_id(
        replace(bundle.lifecycle_records[0], gate_evaluation_created=True)
    )
    ledger.malformed(
        "gate_evaluation_prohibited"
        in codes(module.validate_lifecycle_record(evaluation_lifecycle)),
        "gate evaluation lifecycle claim rejected",
    )

    duplicate_lifecycle = module.with_expected_id(
        replace(
            bundle,
            lifecycle_records=(
                *bundle.lifecycle_records,
                bundle.lifecycle_records[0],
            ),
        )
    )
    ledger.malformed(
        "duplicate_lifecycle_record"
        in codes(module.validate_governance_bundle(duplicate_lifecycle)),
        "duplicate lifecycle record rejected",
    )
    duplicate_transition = module.with_expected_id(
        replace(
            bundle,
            lifecycle_transitions=(
                *bundle.lifecycle_transitions,
                bundle.lifecycle_transitions[0],
            ),
        )
    )
    ledger.malformed(
        "duplicate_transition_id"
        in codes(module.validate_governance_bundle(duplicate_transition)),
        "duplicate transition rejected",
    )

    incomplete_bundle = module.with_expected_id(
        replace(
            bundle,
            lifecycle_records=bundle.lifecycle_records[:-1],
            lifecycle_transitions=bundle.lifecycle_transitions[:-1],
            validation_complete=True,
            provenance_validation_complete=True,
        )
    )
    ledger.malformed(
        "lifecycle_stage_invalid"
        in codes(module.validate_governance_bundle(incomplete_bundle)),
        "false validation-complete claim rejected",
    )

    for record in (
        bundle.review_record.identity,
        bundle.review_record.profile,
        bundle.review_record.candidate_input,
        bundle.review_record.requirement_references[0],
        bundle.review_record.reason_grounds[0],
        bundle.review_record.trace_references[0],
        bundle.review_record.provenance_reference,
        bundle.review_record.limitation_references[0],
        bundle.review_record,
        bundle.version_custody,
        bundle.lifecycle_records[0],
        bundle.lifecycle_transitions[0],
        bundle,
    ):
        try:
            setattr(record, fields(record)[0].name, "mutated")
        except (FrozenInstanceError, AttributeError, TypeError):
            ledger.check(True, f"frozen record {type(record).__name__}")
        else:
            ledger.check(False, f"mutable record {type(record).__name__}")

    package_dir = (
        repository
        / "aiweb_language_core_bootstrap"
        / "verbal_cognition_gate_runtime"
        / "governed_lifecycle"
    )
    expected_files = (
        "__init__.py",
        "canonical.py",
        "identity.py",
        "lifecycle.py",
        "rules.py",
        "schema.py",
        "validation.py",
    )
    ledger.check(
        tuple(sorted(path.name for path in package_dir.glob("*.py")))
        == expected_files,
        "exact Slice 40B package files",
    )
    prohibited_imports = {
        "anthropic", "chromadb", "faiss", "httpx", "keras", "langchain",
        "llama_index", "nltk", "numpy", "ollama", "openai", "pandas",
        "pathlib", "random", "requests", "scipy", "sentence_transformers",
        "sklearn", "socket", "spacy", "subprocess", "tensorflow", "time",
        "torch", "transformers", "urllib", "uuid",
    }
    prohibited_tokens = (
        "evaluate_expectancy",
        "evaluate_congruity",
        "evaluate_connectedness",
        "evaluate_recoverable_purpose",
        "select_meaning",
        "nearest_known",
        "requests.",
        "urlopen(",
        "socket.socket(",
        "subprocess.",
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
    )
    for path in sorted(package_dir.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split(".", 1)[0])
        ledger.check(
            not (roots & prohibited_imports),
            f"no prohibited imports {path.name}",
        )
        lowered = source.lower()
        for token in prohibited_tokens:
            ledger.check(
                token.lower() not in lowered,
                f"no prohibited source token {path.name}:{token}",
            )

    print("AI.WEB SLICE 40B BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"record_types={len(module.SUPPORTED_RECORD_TYPES)}")
    print(f"gate_family_count={len(families)}")
    print(f"lifecycle_stage_count={len(tuple(module.GateLifecycleStage))}")
    print(f"lifecycle_transition_rules={len(module.GATE_LIFECYCLE_TRANSITION_RULES)}")
    print(f"supported_gate_versions={len(module.SUPPORTED_GATE_VERSIONS)}")
    print(f"supported_gate_profile_versions={len(module.SUPPORTED_GATE_PROFILE_VERSIONS)}")
    print("canonical_serialization=1")
    print("deterministic_identifiers=1")
    print("schema_version_custody=1")
    print("gate_profile_version_custody=1")
    print("immutable_successor_records=1")
    print("explicit_lifecycle_transitions=1")
    print("unknown_version_rejection=1")
    print("malformed_record_rejection=1")
    print("exact_provenance_validation=1")
    print("valid_record_is_valid_candidate_meaning=0")
    print("valid_record_is_successful_gate_result=0")
    print("lifecycle_is_selected_meaning_progression=0")
    print("runtime_evaluator_installed=0")
    print("gate_evaluation_performed=0")
    print("gate_outcome_created=0")
    print("candidate_disposition_created=0")
    print("selected_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print(f"FAIL: {failure}")
    if ledger.failures:
        print("AI.WEB SLICE 40B BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 40B BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
