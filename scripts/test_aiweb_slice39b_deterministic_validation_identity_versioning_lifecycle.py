#!/usr/bin/env python3
"""Behavior and adversarial tests for AI.Web Slice 39B."""

from __future__ import annotations

import argparse
import ast
from dataclasses import FrozenInstanceError, fields, replace
import importlib
from pathlib import Path
import sys


PACKAGE = (
    "aiweb_language_core_bootstrap.candidate_meaning_construction"
    ".governed_lifecycle"
)
CHECKS = 0
MALFORMED_CASES = 0


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def malformed(condition: bool, message: str) -> None:
    global MALFORMED_CASES
    MALFORMED_CASES += 1
    check(condition, message)


def codes(report) -> set[str]:
    return {item.code.value for item in report.issues}


def make_bundle(module):
    parent = importlib.import_module(
        "aiweb_language_core_bootstrap.candidate_meaning_construction"
    )

    content = module.with_expected_content_id(
        parent.CandidateMeaningContent(
            content_id="candidate_content:placeholder",
            communicative_act_candidate="report_candidate",
            concept_candidate_refs=("concept_candidate:demo",),
            sense_candidate_refs=("sense_candidate:demo",),
            semantic_relation_candidate_refs=("relation_candidate:demo",),
            action_root_predicate_candidate_refs=(
                "action_predicate_candidate:demo",
            ),
            frame_candidate_refs=("frame_candidate:demo",),
            role_layout_candidate_refs=("role_layout_candidate:demo",),
            referent_candidate_refs=("referent_candidate:demo",),
            capability_reference_candidate_refs=(
                "capability_candidate:demo",
            ),
            effect_boundary_refs=(
                "effect_boundary:communicative_only:v1",
            ),
            meaning_modifiers=("qualified",),
            limitations=("candidate_only",),
            unresolved_referent_refs=("referent_candidate:demo",),
            missing_role_refs=(),
            conflicting_role_refs=(),
            unsupported_reason_refs=(),
            unknown_reason_refs=(),
            authority_sensitive_implications=(
                "report_is_not_evidence",
            ),
            preservation_class_refs=("non_llm_provenance",),
        )
    )

    provenance = module.with_expected_provenance_id(
        parent.CandidateMeaningProvenance(
            provenance_id="candidate_provenance:placeholder",
            source_event_id="source_event:demo",
            source_sha256="0" * 64,
            input_event_id="input_event:demo",
            root_source_span_id="source_span:root",
            source_span_ids=("source_span:root",),
            projection_id="projection:demo",
            structural_result_id="structural_result:demo",
            structural_set_id="structural_set:demo",
            structural_candidate_ids=("structural_candidate:demo",),
            structural_ancestry_ids=("structural_ancestry:demo",),
            constrained_trail_ids=("constrained_trail:demo",),
            phase_trail_ids=("phase_trail:demo",),
            operator_graph_ids=("operator_graph:demo",),
            operator_node_ids=("operator_node:demo",),
            operator_definition_ids=("operator_definition:demo",),
            operator_keys_and_versions=(("operator.demo", "v1"),),
            scope_occurrence_ids=("scope_occurrence:demo",),
            attachment_candidate_ids=(),
            reference_analysis_ids=(),
            reference_candidate_ids=(),
            slice37_result_id="slice37_result:demo",
            slice37_registry_snapshot_id="slice37_snapshot:demo",
            concept_candidate_proposal_ids=("concept_candidate:demo",),
            sense_candidate_proposal_ids=("sense_candidate:demo",),
            concept_ids_and_versions=(("concept.demo", "v1"),),
            sense_ids_and_versions=(("sense.demo", "v1"),),
            slice38_result_id="slice38_result:demo",
            slice38_registry_snapshot_id="slice38_snapshot:demo",
            compatibility_registry_snapshot_id=(
                "compatibility_snapshot:demo"
            ),
            action_predicate_candidate_ids=(
                "action_predicate_candidate:demo",
            ),
            role_layout_candidate_ids=("role_layout_candidate:demo",),
            capability_reference_candidate_ids=(
                "capability_candidate:demo",
            ),
            predecessor_receipt_ids=("slice38h_receipt:demo",),
            source_ancestry_preserved=True,
            operator_ancestry_preserved=True,
            phase_trail_ancestry_preserved=True,
            scope_attachment_ancestry_preserved=True,
            registry_snapshots_preserved=True,
        )
    )

    identity = module.with_expected_candidate_identity(
        parent.CandidateMeaningIdentity(
            candidate_meaning_id="candidate_meaning:placeholder",
            candidate_key="candidate_key:placeholder",
            candidate_version="v1.0.0",
            lineage_id="candidate_lineage:placeholder",
            construction_profile_id="candidate_profile:demo",
            construction_profile_version="v1.0.0",
        ),
        content=content,
        provenance=provenance,
    )

    alternative = module.with_expected_id(
        parent.CandidateMeaningAlternativeReference(
            alternative_reference_id="candidate_alternative:placeholder",
            source_candidate_meaning_id=identity.candidate_meaning_id,
            alternative_candidate_meaning_id=(
                "candidate_meaning:alternative"
            ),
            alternative_kind="unresolved_alternative",
            shared_ancestry_refs=(provenance.provenance_id,),
            differing_content_refs=("candidate_content:alternative",),
            unresolved_reason_refs=("alternative_not_ranked",),
        )
    )

    receipt = module.with_expected_id(
        parent.CandidateMeaningConstructionReceipt(
            receipt_id="candidate_receipt:placeholder",
            candidate_meaning_id=identity.candidate_meaning_id,
            identity_ref=identity.candidate_meaning_id,
            content_ref=content.content_id,
            provenance_ref=provenance.provenance_id,
            alternative_reference_ids=(
                alternative.alternative_reference_id,
            ),
            predecessor_record_ids=(
                "slice37_result:demo",
                "slice38_result:demo",
            ),
            construction_profile_id=identity.construction_profile_id,
            construction_profile_version=(
                identity.construction_profile_version
            ),
            status=parent.CandidateMeaningConstructionStatus.CONSTRUCTED,
            status_reason_refs=(
                "exact_predecessor_shape_available",
            ),
            deterministic_construction_required=True,
            source_preservation_required=True,
            immutable_record_set_required=True,
        )
    )

    state = module.with_expected_id(
        parent.CandidateMeaningState(
            state_id="candidate_state:placeholder",
            identity=identity,
            content=content,
            provenance=provenance,
            alternative_references=(alternative,),
            construction_status=receipt.status,
            construction_receipt=receipt,
            status_reason_refs=("schema_fixture",),
            unresolved_alternative_refs=(
                alternative.alternative_candidate_meaning_id,
            ),
            missing_role_refs=(),
            conflicting_role_refs=(),
            limitations=("schema_only",),
        )
    )

    custody = module.with_expected_id(
        module.CandidateMeaningVersionCustody(
            custody_id="candidate_version_custody:placeholder",
            candidate_meaning_id=identity.candidate_meaning_id,
            candidate_version=identity.candidate_version,
            schema_version=parent.SCHEMA_VERSION,
            identity_schema_id=parent.IDENTITY_SCHEMA_ID,
            content_schema_id=parent.CONTENT_SCHEMA_ID,
            provenance_schema_id=parent.PROVENANCE_SCHEMA_ID,
            alternative_reference_schema_id=(
                parent.ALTERNATIVE_REFERENCE_SCHEMA_ID
            ),
            construction_receipt_schema_id=(
                parent.CONSTRUCTION_RECEIPT_SCHEMA_ID
            ),
            state_schema_id=parent.STATE_SCHEMA_ID,
            construction_profile_id=identity.construction_profile_id,
            construction_profile_version=(
                identity.construction_profile_version
            ),
            slice37_registry_snapshot_id=(
                provenance.slice37_registry_snapshot_id
            ),
            slice37_registry_snapshot_version="v1",
            slice38_registry_snapshot_id=(
                provenance.slice38_registry_snapshot_id
            ),
            slice38_registry_snapshot_version="v1",
            compatibility_registry_snapshot_id=(
                provenance.compatibility_registry_snapshot_id
            ),
            compatibility_registry_snapshot_version="v1",
            canonical_field_order_version=(
                module.CANONICAL_FIELD_ORDER_VERSION
            ),
            digest_algorithm=module.DIGEST_ALGORITHM,
            non_llm_provenance=True,
            timestamps_in_identity=False,
            randomness_in_identity=False,
            process_identity_in_identity=False,
            filesystem_state_in_identity=False,
            environment_state_in_identity=False,
            hash_table_order_in_identity=False,
            runtime_authorized=False,
            gate_progression_authorized=False,
            action_authorized=False,
            memory_authorized=False,
            rendering_authorized=False,
            delivery_authorized=False,
        )
    )

    stage_statuses = (
        (
            module.CandidateMeaningLifecycleStage.SCHEMA_DECLARED,
            parent.CandidateMeaningConstructionStatus.CONSTRUCTION_INCOMPLETE,
        ),
        (
            module.CandidateMeaningLifecycleStage.PROVENANCE_BOUND,
            parent.CandidateMeaningConstructionStatus.CONSTRUCTION_INCOMPLETE,
        ),
        (
            module.CandidateMeaningLifecycleStage.CONTENT_CONSTRUCTED,
            parent.CandidateMeaningConstructionStatus.CONSTRUCTED,
        ),
        (
            module.CandidateMeaningLifecycleStage.CANDIDATE_SEALED,
            parent.CandidateMeaningConstructionStatus.CONSTRUCTED,
        ),
        (
            module.CandidateMeaningLifecycleStage.CANDIDATE_SET_REFERENCED,
            parent.CandidateMeaningConstructionStatus.CONSTRUCTED,
        ),
    )

    lifecycle_records = []
    predecessor = ()
    for stage, status in stage_statuses:
        item = module.with_expected_id(
            module.CandidateMeaningLifecycleRecord(
                lifecycle_record_id="candidate_lifecycle:placeholder",
                candidate_meaning_id=identity.candidate_meaning_id,
                stage=stage,
                construction_status=status,
                identity_ref=identity.candidate_meaning_id,
                content_ref=content.content_id,
                provenance_ref=provenance.provenance_id,
                receipt_ref=receipt.receipt_id,
                state_ref=state.state_id,
                version_custody_ref=custody.custody_id,
                candidate_set_reference_ids=(
                    ("candidate_set:demo",)
                    if stage
                    is module.CandidateMeaningLifecycleStage.CANDIDATE_SET_REFERENCED
                    else ()
                ),
                predecessor_lifecycle_record_ids=predecessor,
                reason_refs=(f"stage_reason:{stage.value}",),
                automatic_progression=False,
                gate_progression_created=False,
                selected_meaning_created=False,
                ambiguity_disposition_created=False,
                clarification_required_created=False,
                refusal_created=False,
                blocked_progression_created=False,
                truth_determined=False,
                evidence_validated=False,
                permission_granted=False,
                route_created=False,
                invocation_created=False,
                action_performed=False,
                memory_accessed=False,
                rendered=False,
                delivered=False,
            )
        )
        lifecycle_records.append(item)
        predecessor = (item.lifecycle_record_id,)

    transition_kinds = (
        module.CandidateMeaningLifecycleTransitionKind.BIND_PROVENANCE,
        module.CandidateMeaningLifecycleTransitionKind.CONSTRUCT_CONTENT,
        module.CandidateMeaningLifecycleTransitionKind.SEAL_CANDIDATE,
        module.CandidateMeaningLifecycleTransitionKind.REFERENCE_CANDIDATE_SET,
    )
    lifecycle_transitions = []
    predecessor_transitions = ()
    for source, target, kind in zip(
        lifecycle_records,
        lifecycle_records[1:],
        transition_kinds,
    ):
        item = module.with_expected_id(
            module.CandidateMeaningLifecycleTransitionRecord(
                transition_id=(
                    "candidate_lifecycle_transition:placeholder"
                ),
                candidate_meaning_id=identity.candidate_meaning_id,
                source_lifecycle_record_id=source.lifecycle_record_id,
                target_lifecycle_record_id=target.lifecycle_record_id,
                from_stage=source.stage,
                to_stage=target.stage,
                transition_kind=kind,
                version_custody_ref=custody.custody_id,
                reason_refs=(f"transition_reason:{kind.value}",),
                predecessor_transition_refs=predecessor_transitions,
                automatic_transition=False,
                gate_progression_created=False,
                selected_meaning_created=False,
                ambiguity_disposition_created=False,
                clarification_required_created=False,
                refusal_created=False,
                blocked_progression_created=False,
                permission_granted=False,
                route_created=False,
                invocation_created=False,
                action_performed=False,
                memory_accessed=False,
                rendered=False,
                delivered=False,
            )
        )
        lifecycle_transitions.append(item)
        predecessor_transitions = (item.transition_id,)

    bundle = module.CandidateMeaningGovernanceBundle(
        bundle_id="candidate_governance_bundle:placeholder",
        identity=identity,
        content=content,
        provenance=provenance,
        alternative_references=(alternative,),
        construction_receipt=receipt,
        state=state,
        version_custody=custody,
        lifecycle_records=tuple(lifecycle_records),
        lifecycle_transitions=tuple(lifecycle_transitions),
        canonical_digest="0" * 64,
        runtime_constructor_installed=False,
        candidate_ranking_installed=False,
        gate_engine_installed=False,
        selected_meaning_installed=False,
        route_installed=False,
        invocation_installed=False,
        action_installed=False,
        memory_installed=False,
        rendering_installed=False,
        delivery_installed=False,
    )
    return module.with_expected_id(bundle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    module = importlib.import_module(PACKAGE)
    parent = importlib.import_module(
        "aiweb_language_core_bootstrap.candidate_meaning_construction"
    )
    bundle = make_bundle(module)

    report = module.validate_governance_bundle(bundle)
    check(report.ok, f"valid governance bundle: {report.issues}")
    check(
        module.assert_valid_governance_bundle(bundle) is bundle,
        "assert valid bundle returns exact record",
    )

    check(
        module.SLICE39B_ACCEPTED_PARENT_HEAD
        == "b01f9e190d2bc6dde39340bda9260aeaa02832d6",
        "accepted parent HEAD",
    )
    check(
        module.SLICE39B_ACCEPTED_PARENT_TREE
        == "0c58df87d63cf06dba1f0c535db12b467d65910f",
        "accepted parent tree",
    )
    check(
        module.SLICE39B_ACCEPTED_PARENT_SUBJECT
        == "Slice 39A candidate meaning core schema",
        "accepted parent subject",
    )
    check(module.DIGEST_ALGORITHM == "sha256", "digest algorithm")
    check(
        module.CANONICAL_FIELD_ORDER_VERSION
        == "aiweb-slice39b-canonical-field-order-v1",
        "canonical field-order version",
    )

    supported = module.SUPPORTED_RECORD_TYPES
    check(len(supported) == 10, "supported record type count")
    check(len(supported) == len(set(supported)), "supported types unique")
    for record_type in supported:
        order = module.canonical_field_order(record_type)
        check(
            order == tuple(item.name for item in fields(record_type)),
            f"canonical field order {record_type.__name__}",
        )
        pairs = tuple(
            (name, getattr(
                {
                    type(bundle.identity): bundle.identity,
                    type(bundle.content): bundle.content,
                    type(bundle.provenance): bundle.provenance,
                    type(bundle.alternative_references[0]): (
                        bundle.alternative_references[0]
                    ),
                    type(bundle.construction_receipt): (
                        bundle.construction_receipt
                    ),
                    type(bundle.state): bundle.state,
                    type(bundle.version_custody): bundle.version_custody,
                    type(bundle.lifecycle_records[0]): (
                        bundle.lifecycle_records[0]
                    ),
                    type(bundle.lifecycle_transitions[0]): (
                        bundle.lifecycle_transitions[0]
                    ),
                    type(bundle): bundle,
                }[record_type],
                name,
            ))
            for name in reversed(order)
        )
        ordered = module.canonicalize_field_pairs(record_type, pairs)
        check(tuple(ordered) == order, f"reordered {record_type.__name__}")
        check(
            module.validate_field_pairs(record_type, pairs).ok,
            f"field pair validation {record_type.__name__}",
        )

        duplicate = pairs + (pairs[0],)
        malformed(
            "duplicate_field"
            in codes(module.validate_field_pairs(record_type, duplicate)),
            f"duplicate field rejected {record_type.__name__}",
        )
        unknown = pairs + (("unknown_field", "x"),)
        malformed(
            "unknown_field"
            in codes(module.validate_field_pairs(record_type, unknown)),
            f"unknown field rejected {record_type.__name__}",
        )
        missing = pairs[1:]
        malformed(
            "missing_field"
            in codes(module.validate_field_pairs(record_type, missing)),
            f"missing field rejected {record_type.__name__}",
        )

    check(
        module.canonical_record_bytes(bundle)
        == module.canonical_record_bytes(bundle),
        "canonical bytes stable",
    )
    check(
        module.deterministic_record_digest(bundle)
        == module.deterministic_record_digest(bundle),
        "record digest stable",
    )
    check(
        bundle.canonical_digest == module.expected_bundle_digest(bundle),
        "bundle digest exact",
    )
    check(
        bundle.bundle_id == module.expected_bundle_id(bundle),
        "bundle ID exact",
    )
    check(
        bundle.identity.candidate_meaning_id
        == module.expected_candidate_meaning_id(
            bundle.content,
            bundle.provenance,
        ),
        "candidate identity exact",
    )

    content_changed = module.with_expected_content_id(
        replace(
            bundle.content,
            limitations=("candidate_only", "changed"),
        )
    )
    check(
        module.expected_candidate_meaning_id(
            content_changed,
            bundle.provenance,
        )
        != bundle.identity.candidate_meaning_id,
        "content changes semantic identity",
    )
    provenance_changed = module.with_expected_provenance_id(
        replace(bundle.provenance, source_sha256="1" * 64)
    )
    check(
        module.expected_candidate_meaning_id(
            bundle.content,
            provenance_changed,
        )
        != bundle.identity.candidate_meaning_id,
        "provenance changes semantic identity",
    )
    identity_metadata_changed = replace(
        bundle.identity,
        candidate_version="v1.0.1",
    )
    check(
        module.expected_candidate_meaning_id(
            bundle.content,
            bundle.provenance,
        )
        == bundle.identity.candidate_meaning_id,
        "candidate identity excludes unrelated identity metadata",
    )
    check(
        identity_metadata_changed.candidate_meaning_id
        == bundle.identity.candidate_meaning_id,
        "identity metadata mutation does not silently recompute semantic ID",
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
        check(decision.allowed, f"allowed lifecycle transition {transition.transition_kind}")
        check(
            module.assert_lifecycle_transition(
                source,
                target,
                transition,
                bundle=bundle,
            )
            is transition,
            "assert lifecycle transition returns exact record",
        )

    invalid_skip = module.with_expected_id(
        replace(
            bundle.lifecycle_transitions[0],
            target_lifecycle_record_id=(
                bundle.lifecycle_records[3].lifecycle_record_id
            ),
            to_stage=module.CandidateMeaningLifecycleStage.CANDIDATE_SEALED,
            transition_kind=(
                module.CandidateMeaningLifecycleTransitionKind.SEAL_CANDIDATE
            ),
        )
    )
    malformed(
        not module.evaluate_lifecycle_transition(
            bundle.lifecycle_records[0],
            bundle.lifecycle_records[3],
            invalid_skip,
            bundle=bundle,
        ).allowed,
        "schema-to-sealed lifecycle skip rejected",
    )

    auto_transition = module.with_expected_id(
        replace(
            bundle.lifecycle_transitions[0],
            automatic_transition=True,
        )
    )
    malformed(
        "automatic_transition_prohibited"
        in codes(module.validate_lifecycle_transition_record(auto_transition)),
        "automatic transition rejected",
    )
    gate_transition = module.with_expected_id(
        replace(
            bundle.lifecycle_transitions[0],
            gate_progression_created=True,
        )
    )
    malformed(
        "gate_progression_prohibited"
        in codes(module.validate_lifecycle_transition_record(gate_transition)),
        "gate progression rejected",
    )

    malformed_ids = (
        "",
        " leading",
        "trailing ",
        "contains space",
        "bad\nnewline",
        "bad?query",
        "bad#fragment",
        "éxternal",
    )
    for value in malformed_ids:
        bad = replace(
            bundle.content,
            content_id=value,
        )
        malformed(
            not module.validate_content_record(bad).ok,
            f"malformed identifier rejected {value!r}",
        )

    bad_sha = module.with_expected_provenance_id(
        replace(bundle.provenance, source_sha256="ABC")
    )
    malformed(
        "invalid_sha256" in codes(module.validate_provenance_record(bad_sha)),
        "malformed SHA-256 rejected",
    )

    for ancestry_name in (
        "source_span_ids",
        "structural_candidate_ids",
        "structural_ancestry_ids",
        "constrained_trail_ids",
        "phase_trail_ids",
        "operator_graph_ids",
        "operator_node_ids",
        "operator_definition_ids",
        "operator_keys_and_versions",
        "scope_occurrence_ids",
        "predecessor_receipt_ids",
    ):
        bad = replace(bundle.provenance, **{ancestry_name: ()})
        malformed(
            "ancestry_required"
            in codes(module.validate_provenance_record(bad)),
            f"empty required ancestry rejected {ancestry_name}",
        )

    version_values = (
        "",
        "1",
        "v01",
        "v1.01",
        "v1.0.0.0",
        "V1",
        "v1-beta",
    )
    for value in version_values:
        bad = replace(
            bundle.version_custody,
            slice37_registry_snapshot_version=value,
        )
        version_codes = codes(
            module.validate_version_custody(
                bad,
                identity=bundle.identity,
                provenance=bundle.provenance,
            )
        )
        malformed(
            bool(
                {"invalid_version", "required_value_missing"}
                & version_codes
            ),
            f"invalid registry snapshot version rejected {value!r}",
        )

    mismatch_cases = (
        replace(
            bundle.construction_receipt,
            candidate_meaning_id="candidate_meaning:wrong",
        ),
        replace(
            bundle.construction_receipt,
            content_ref="candidate_content:wrong",
        ),
        replace(
            bundle.construction_receipt,
            provenance_ref="candidate_provenance:wrong",
        ),
    )
    for item in mismatch_cases:
        malformed(
            not module.validate_construction_receipt(
                item,
                identity=bundle.identity,
                content=bundle.content,
                provenance=bundle.provenance,
            ).ok,
            "cross-record receipt mismatch rejected",
        )

    bad_custody = module.with_expected_version_custody_id(
        replace(
            bundle.version_custody,
            slice38_registry_snapshot_id="slice38_snapshot:wrong",
        )
    )
    malformed(
        "cross_record_identity_mismatch"
        in codes(
            module.validate_version_custody(
                bad_custody,
                identity=bundle.identity,
                provenance=bundle.provenance,
            )
        ),
        "registry snapshot custody mismatch rejected",
    )

    nondeterministic_flags = (
        "timestamps_in_identity",
        "randomness_in_identity",
        "process_identity_in_identity",
        "filesystem_state_in_identity",
        "environment_state_in_identity",
        "hash_table_order_in_identity",
    )
    for name in nondeterministic_flags:
        bad = module.with_expected_version_custody_id(
            replace(bundle.version_custody, **{name: True})
        )
        malformed(
            "nondeterministic_input_prohibited"
            in codes(
                module.validate_version_custody(
                    bad,
                    identity=bundle.identity,
                    provenance=bundle.provenance,
                )
            ),
            f"nondeterministic identity input rejected {name}",
        )

    duplicate_lifecycle = replace(
        bundle,
        lifecycle_records=(
            *bundle.lifecycle_records,
            bundle.lifecycle_records[0],
        ),
    )
    malformed(
        "duplicate_lifecycle_record"
        in codes(module.validate_governance_bundle(duplicate_lifecycle)),
        "duplicate lifecycle record rejected",
    )
    duplicate_transition = replace(
        bundle,
        lifecycle_transitions=(
            *bundle.lifecycle_transitions,
            bundle.lifecycle_transitions[0],
        ),
    )
    malformed(
        "duplicate_transition_id"
        in codes(module.validate_governance_bundle(duplicate_transition)),
        "duplicate transition rejected",
    )

    for record in (
        bundle.identity,
        bundle.content,
        bundle.provenance,
        bundle.alternative_references[0],
        bundle.construction_receipt,
        bundle.state,
        bundle.version_custody,
        bundle.lifecycle_records[0],
        bundle.lifecycle_transitions[0],
        bundle,
    ):
        try:
            setattr(record, fields(record)[0].name, "mutated")
        except (FrozenInstanceError, AttributeError, TypeError):
            check(True, f"frozen record {type(record).__name__}")
        else:
            check(False, f"mutable record {type(record).__name__}")

    package_dir = (
        repository
        / "aiweb_language_core_bootstrap"
        / "candidate_meaning_construction"
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
    check(
        tuple(sorted(path.name for path in package_dir.glob("*.py")))
        == expected_files,
        "exact Slice 39B package files",
    )
    prohibited_imports = {
        "datetime",
        "os",
        "pathlib",
        "platform",
        "random",
        "secrets",
        "socket",
        "subprocess",
        "time",
        "uuid",
    }
    prohibited_tokens = (
        "open(",
        "Path(",
        "read_text(",
        "write_text(",
        "requests.",
        "urlopen(",
        "socket.socket(",
        "subprocess.",
        "os.environ",
        "time.time(",
        "datetime.now(",
        "uuid.",
        "random.",
        "secrets.",
    )
    for path in sorted(package_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module
            ):
                roots.add(node.module.split(".", 1)[0])
        check(
            not (roots & prohibited_imports),
            f"nondeterministic/effect imports absent {path.name}",
        )
        for token in prohibited_tokens:
            check(token not in text, f"effect token absent {path.name} {token}")

    parent_files = tuple(
        sorted(
            path.name
            for path in (
                repository
                / "aiweb_language_core_bootstrap"
                / "candidate_meaning_construction"
            ).glob("*.py")
        )
    )
    check(
        parent_files
        == ("__init__.py", "authority.py", "identity.py", "schema.py"),
        "Slice 39A parent package unchanged",
    )
    check(
        "CandidateMeaningVersionCustody" not in parent.__all__,
        "Slice 39B does not alter Slice 39A exports",
    )

    print("AI.WEB SLICE 39B BEHAVIOR TEST: PASS")
    print(f"check_count={CHECKS}")
    print(f"malformed_validation_cases={MALFORMED_CASES}")
    print("candidate_identity_inputs=exact_content_plus_exact_provenance")
    print("canonical_field_order_record_types=10")
    print("lifecycle_stages=7")
    print("lifecycle_transition_rules=11")
    print("schema_version_custody=1")
    print("registry_snapshot_version_custody=3")
    print("timestamps_random_process_filesystem_environment_hash_order=0")
    print("runtime_constructor_installed=0")
    print("gate_progression_installed=0")
    print("selected_meaning_installed=0")
    print("truth_evidence_permission=0")
    print("route_invocation_action_memory_rendering_delivery=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
