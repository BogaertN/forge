#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 39A candidate-meaning core schema."""

from __future__ import annotations

import argparse
import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass
from enum import Enum
import importlib
import inspect
from pathlib import Path
import sys


PACKAGE = "aiweb_language_core_bootstrap.candidate_meaning_construction"
EXPECTED_EXPORTS = (
    "ACCEPTED_PARENT_HEAD",
    "ACCEPTED_PARENT_SUBJECT",
    "ACCEPTED_PARENT_TREE",
    "ALTERNATIVE_REFERENCE_SCHEMA_ID",
    "CONSTRUCTION_ONLY_STATUS_VALUES",
    "CONSTRUCTION_RECEIPT_SCHEMA_ID",
    "CONTENT_SCHEMA_ID",
    "CandidateMeaningAlternativeReference",
    "CandidateMeaningConstructionReceipt",
    "CandidateMeaningConstructionStatus",
    "CandidateMeaningContent",
    "CandidateMeaningIdentity",
    "CandidateMeaningProvenance",
    "CandidateMeaningState",
    "DEFERRED_SLICE40_GATE_OUTCOMES",
    "IDENTITY_SCHEMA_ID",
    "PACKAGE_ID",
    "PACKAGE_NAME",
    "PERMANENT_CANDIDATE_MEANING_BOUNDARIES",
    "PROHIBITED_AUTHORITY_PATHS",
    "PROVENANCE_SCHEMA_ID",
    "SCHEMA_ABBREVIATION",
    "SCHEMA_NAME",
    "SCHEMA_VERSION",
    "SPEC_ID",
    "SPEC_VERSION",
    "STATE_SCHEMA_ID",
)
EXPECTED_STATUSES = (
    "constructed",
    "construction_incomplete",
    "construction_unknown",
    "construction_unsupported",
    "construction_conflicted",
    "predecessor_invalid",
)
FORBIDDEN_GATE_VALUES = (
    "accepted_meaning",
    "selected_meaning",
    "ambiguous_gate_disposition",
    "clarification_required",
    "refusal",
    "blocked_progression",
    "rejection",
    "unsupported_language_disposition",
    "gate_pass",
    "gate_fail",
    "ambiguity_resolved",
    "clarification_asked",
)
FORBIDDEN_SCHEMA_FUNCTION_PREFIXES = (
    "build_",
    "construct_",
    "create_",
    "select_",
    "validate_",
    "assert_valid",
    "rank_",
    "resolve_",
    "route_",
    "invoke_",
    "render_",
    "deliver_",
)
PROHIBITED_IMPORT_ROOTS = {
    "anthropic",
    "chromadb",
    "faiss",
    "httpx",
    "keras",
    "langchain",
    "llama_index",
    "nltk",
    "numpy",
    "openai",
    "pandas",
    "requests",
    "scipy",
    "sentence_transformers",
    "sklearn",
    "spacy",
    "tensorflow",
    "torch",
    "transformers",
}
PROHIBITED_SOURCE_TOKENS = (
    "@app.route",
    "@router.",
    "FastAPI(",
    "Flask(",
    "requests.",
    "urlopen(",
    "socket.socket(",
    "os.system(",
    "subprocess.",
    "open(",
    "Path(",
    "read_text(",
    "write_text(",
    "semantic_similarity(",
    "embedding(",
)


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []
        self.malformed_cases = 0

    def check(self, condition: bool, label: str) -> None:
        self.check_count += 1
        if not condition:
            self.failures.append(label)

    def malformed(self, condition: bool, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)


def _expect_type_error(ledger: Ledger, label: str, function, *args, **kwargs) -> None:
    try:
        function(*args, **kwargs)
    except TypeError:
        ledger.malformed(True, label)
    except Exception as error:
        ledger.malformed(False, f"{label}:wrong_exception:{type(error).__name__}")
    else:
        ledger.malformed(False, f"{label}:accepted")


def _expect_value_error(ledger: Ledger, label: str, function, *args) -> None:
    try:
        function(*args)
    except ValueError:
        ledger.malformed(True, label)
    except Exception as error:
        ledger.malformed(False, f"{label}:wrong_exception:{type(error).__name__}")
    else:
        ledger.malformed(False, f"{label}:accepted")


def _fixture_kwargs(module) -> dict[type, dict[str, object]]:
    identity = module.CandidateMeaningIdentity(
        candidate_meaning_id="candidate_meaning:demo",
        candidate_key="demo_candidate",
        candidate_version="v1.0.0",
        lineage_id="lineage:demo",
        construction_profile_id="candidate_profile:demo",
        construction_profile_version="v1.0.0",
    )
    content = module.CandidateMeaningContent(
        content_id="candidate_content:demo",
        communicative_act_candidate="report_candidate",
        concept_candidate_refs=("concept_candidate:demo",),
        sense_candidate_refs=("sense_candidate:demo",),
        semantic_relation_candidate_refs=("relation_candidate:demo",),
        action_root_predicate_candidate_refs=("action_predicate_candidate:demo",),
        frame_candidate_refs=("frame_candidate:demo",),
        role_layout_candidate_refs=("role_layout_candidate:demo",),
        referent_candidate_refs=("referent_candidate:demo",),
        capability_reference_candidate_refs=("capability_candidate:demo",),
        effect_boundary_refs=("effect_boundary:communicative_only:v1",),
        meaning_modifiers=("qualified",),
        limitations=("candidate_only",),
        unresolved_referent_refs=("referent_candidate:demo",),
        missing_role_refs=(),
        conflicting_role_refs=(),
        unsupported_reason_refs=(),
        unknown_reason_refs=(),
        authority_sensitive_implications=("report_is_not_evidence",),
        preservation_class_refs=("non_llm_provenance",),
    )
    provenance = module.CandidateMeaningProvenance(
        provenance_id="candidate_provenance:demo",
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
        attachment_candidate_ids=("attachment_candidate:demo",),
        reference_analysis_ids=("reference_analysis:demo",),
        reference_candidate_ids=("reference_candidate:demo",),
        slice37_result_id="slice37_result:demo",
        slice37_registry_snapshot_id="slice37_snapshot:demo",
        concept_candidate_proposal_ids=("concept_candidate:demo",),
        sense_candidate_proposal_ids=("sense_candidate:demo",),
        concept_ids_and_versions=(("concept.demo", "v1"),),
        sense_ids_and_versions=(("sense.demo", "v1"),),
        slice38_result_id="slice38_result:demo",
        slice38_registry_snapshot_id="slice38_snapshot:demo",
        compatibility_registry_snapshot_id="compatibility_snapshot:demo",
        action_predicate_candidate_ids=("action_predicate_candidate:demo",),
        role_layout_candidate_ids=("role_layout_candidate:demo",),
        capability_reference_candidate_ids=("capability_candidate:demo",),
        predecessor_receipt_ids=("slice38h_receipt:demo",),
        source_ancestry_preserved=True,
        operator_ancestry_preserved=True,
        phase_trail_ancestry_preserved=True,
        scope_attachment_ancestry_preserved=True,
        registry_snapshots_preserved=True,
    )
    alternative = module.CandidateMeaningAlternativeReference(
        alternative_reference_id="candidate_alternative:demo",
        source_candidate_meaning_id="candidate_meaning:demo",
        alternative_candidate_meaning_id="candidate_meaning:alternative",
        alternative_kind="unresolved_alternative",
        shared_ancestry_refs=("candidate_provenance:demo",),
        differing_content_refs=("candidate_content:alternative",),
        unresolved_reason_refs=("alternative_not_ranked",),
    )
    receipt = module.CandidateMeaningConstructionReceipt(
        receipt_id="candidate_receipt:demo",
        candidate_meaning_id="candidate_meaning:demo",
        identity_ref="candidate_meaning:demo",
        content_ref="candidate_content:demo",
        provenance_ref="candidate_provenance:demo",
        alternative_reference_ids=("candidate_alternative:demo",),
        predecessor_record_ids=("slice37_result:demo", "slice38_result:demo"),
        construction_profile_id="candidate_profile:demo",
        construction_profile_version="v1.0.0",
        status=module.CandidateMeaningConstructionStatus.CONSTRUCTED,
        status_reason_refs=("exact_predecessor_shape_available",),
        deterministic_construction_required=True,
        source_preservation_required=True,
        immutable_record_set_required=True,
    )
    state = module.CandidateMeaningState(
        state_id="candidate_state:demo",
        identity=identity,
        content=content,
        provenance=provenance,
        alternative_references=(alternative,),
        construction_status=module.CandidateMeaningConstructionStatus.CONSTRUCTED,
        construction_receipt=receipt,
        status_reason_refs=("schema_fixture",),
        unresolved_alternative_refs=("candidate_meaning:alternative",),
        missing_role_refs=(),
        conflicting_role_refs=(),
        limitations=("schema_only",),
    )
    return {
        module.CandidateMeaningIdentity: {
            item.name: getattr(identity, item.name)
            for item in fields(identity)
            if item.init
        },
        module.CandidateMeaningContent: {
            item.name: getattr(content, item.name)
            for item in fields(content)
            if item.init
        },
        module.CandidateMeaningProvenance: {
            item.name: getattr(provenance, item.name)
            for item in fields(provenance)
            if item.init
        },
        module.CandidateMeaningAlternativeReference: {
            item.name: getattr(alternative, item.name)
            for item in fields(alternative)
            if item.init
        },
        module.CandidateMeaningConstructionReceipt: {
            item.name: getattr(receipt, item.name)
            for item in fields(receipt)
            if item.init
        },
        module.CandidateMeaningState: {
            item.name: getattr(state, item.name)
            for item in fields(state)
            if item.init
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    ledger = Ledger()
    module = importlib.import_module(PACKAGE)
    schema_module = importlib.import_module(f"{PACKAGE}.schema")
    identity_module = importlib.import_module(f"{PACKAGE}.identity")
    authority_module = importlib.import_module(f"{PACKAGE}.authority")

    ledger.check(tuple(module.__all__) == EXPECTED_EXPORTS, "exact public exports")
    ledger.check(len(module.__all__) == len(set(module.__all__)), "exports unique")
    for name in EXPECTED_EXPORTS:
        ledger.check(hasattr(module, name), f"export exists {name}")

    statuses = tuple(item.value for item in module.CandidateMeaningConstructionStatus)
    ledger.check(statuses == EXPECTED_STATUSES, "exact construction statuses")
    ledger.check(
        tuple(module.CONSTRUCTION_ONLY_STATUS_VALUES) == EXPECTED_STATUSES,
        "authority status tuple matches enum",
    )
    ledger.check(
        set(statuses).isdisjoint(FORBIDDEN_GATE_VALUES),
        "construction statuses exclude gate outcomes",
    )
    for status in module.CandidateMeaningConstructionStatus:
        ledger.check(isinstance(status, str), f"status is str {status.value}")
        ledger.check(isinstance(status, Enum), f"status is enum {status.value}")

    record_types = (
        module.CandidateMeaningIdentity,
        module.CandidateMeaningContent,
        module.CandidateMeaningProvenance,
        module.CandidateMeaningAlternativeReference,
        module.CandidateMeaningConstructionReceipt,
        module.CandidateMeaningState,
    )
    fixture_kwargs = _fixture_kwargs(module)
    instances = tuple(record_type(**fixture_kwargs[record_type]) for record_type in record_types)

    for record_type, instance in zip(record_types, instances):
        ledger.check(is_dataclass(record_type), f"dataclass {record_type.__name__}")
        ledger.check(
            getattr(record_type, "__dataclass_params__").frozen is True,
            f"frozen {record_type.__name__}",
        )
        ledger.check(hasattr(record_type, "__slots__"), f"slots {record_type.__name__}")
        ledger.check(not hasattr(instance, "__dict__"), f"no dict {record_type.__name__}")
        ledger.check(
            record_type.__module__ == f"{PACKAGE}.schema",
            f"exact module {record_type.__name__}",
        )
        for item in fields(record_type):
            ledger.check(bool(item.name), f"field named {record_type.__name__}.{item.name}")
            ledger.check(
                item.name not in {"accepted", "selected"},
                f"no generic authority field {record_type.__name__}.{item.name}",
            )
            try:
                setattr(instance, item.name, getattr(instance, item.name))
            except (FrozenInstanceError, AttributeError):
                ledger.check(True, f"immutable {record_type.__name__}.{item.name}")
            except Exception as error:
                ledger.check(
                    False,
                    f"immutability wrong error {record_type.__name__}.{item.name}:{type(error).__name__}",
                )
            else:
                ledger.check(False, f"mutable {record_type.__name__}.{item.name}")

    state = instances[-1]
    fixed_true = ("schema_only", "candidate_only")
    fixed_false = (
        "runtime_constructor_installed",
        "accepted_meaning",
        "selected_meaning",
        "selected_sense",
        "selected_predicate",
        "selected_frame",
        "participant_assignment",
        "resolved_referent",
        "ambiguous_gate_disposition",
        "clarification_required",
        "refusal",
        "blocked_progression",
        "rejection",
        "evidence_validity",
        "truth",
        "verified_status",
        "permission",
        "capability_availability",
        "route",
        "invocation",
        "action",
        "memory_access",
        "rendering",
        "delivery",
        "external_resource_loading",
        "language_model_authority",
        "embedding_authority",
        "semantic_similarity_authority",
    )
    for name in fixed_true:
        ledger.check(getattr(state, name) is True, f"state fixed true {name}")
    for name in fixed_false:
        ledger.check(getattr(state, name) is False, f"state fixed false {name}")

    receipt = instances[-2]
    receipt_false = (
        "accepted_meaning_created",
        "selected_meaning_created",
        "gate_outcome_created",
        "evidence_validity_determined",
        "truth_determined",
        "permission_inferred",
        "capability_availability_created",
        "route_created",
        "invocation_proposed",
        "tool_invoked",
        "action_performed",
        "memory_accessed",
        "rendered",
        "delivered",
    )
    ledger.check(receipt.candidate_only is True, "receipt candidate only")
    for name in receipt_false:
        ledger.check(getattr(receipt, name) is False, f"receipt fixed false {name}")

    alternative = instances[3]
    for name in (
        "ranking_assigned",
        "preferred_candidate_assigned",
        "selected_alternative",
        "ambiguous_gate_disposition_created",
    ):
        ledger.check(getattr(alternative, name) is False, f"alternative fixed false {name}")

    content = instances[1]
    ledger.check(content.candidate_only is True, "content candidate only")
    for name in (
        "selected_content",
        "evidence_validity_determined",
        "truth_determined",
        "permission_inferred",
    ):
        ledger.check(getattr(content, name) is False, f"content fixed false {name}")

    provenance = instances[2]
    ledger.check(provenance.candidate_only is True, "provenance candidate only")
    ledger.check(provenance.selected_ancestry is False, "provenance not selected")
    ledger.check(
        provenance.external_resource_loaded is False,
        "provenance external resource zero",
    )

    ledger.check(
        len(module.PERMANENT_CANDIDATE_MEANING_BOUNDARIES) == 26,
        "permanent boundary count",
    )
    ledger.check(
        len(module.PROHIBITED_AUTHORITY_PATHS) == 20,
        "prohibited authority count",
    )
    ledger.check(
        len(module.DEFERRED_SLICE40_GATE_OUTCOMES) == 8,
        "deferred gate outcome count",
    )
    ledger.check(
        set(module.PERMANENT_CANDIDATE_MEANING_BOUNDARIES)
        .isdisjoint(module.PROHIBITED_AUTHORITY_PATHS),
        "boundary collections distinct",
    )

    # The accepted MSM-v1 record remains untouched and separate.
    msm_records = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest._records"
    )
    msm_candidate = msm_records.CandidateMeaningRecord
    expected_msm_fields = (
        "record_id",
        "lineage_id",
        "source_expression_ref",
        "communicative_act",
        "concept_refs",
        "relation_refs",
        "meaning_modifiers",
        "ambiguity_reasons",
        "unresolved_referents",
        "authority_sensitive_implications",
        "preservation_classes",
        "record_kind",
        "lifecycle_state",
        "schema_version",
    )
    ledger.check(
        tuple(item.name for item in fields(msm_candidate)) == expected_msm_fields,
        "accepted MSM candidate shape unchanged",
    )
    ledger.check(
        not issubclass(module.CandidateMeaningState, msm_candidate),
        "companion state does not subclass MSM candidate",
    )
    ledger.check(
        not issubclass(module.CandidateMeaningContent, msm_candidate),
        "companion content does not subclass MSM candidate",
    )
    ledger.check(
        module.CandidateMeaningState is not msm_candidate,
        "companion state is distinct",
    )

    package_dir = repository / "aiweb_language_core_bootstrap" / "candidate_meaning_construction"
    package_files = tuple(sorted(package_dir.glob("*.py")))
    ledger.check(len(package_files) == 4, "schema package file count")
    expected_file_names = ("__init__.py", "authority.py", "identity.py", "schema.py")
    ledger.check(
        tuple(path.name for path in package_files) == expected_file_names,
        "schema package exact files",
    )

    for path in package_files:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        roots: set[str] = set()
        functions: list[str] = []
        async_functions: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                async_functions.append(node.name)
        ledger.check(
            not (roots & PROHIBITED_IMPORT_ROOTS),
            f"standard-library-only imports {path.name}",
        )
        ledger.check(not async_functions, f"no async functions {path.name}")
        for function in functions:
            ledger.check(
                not function.startswith(FORBIDDEN_SCHEMA_FUNCTION_PREFIXES),
                f"no runtime function {path.name}:{function}",
            )
        if path.name in {"schema.py", "authority.py", "identity.py"}:
            ledger.check(not functions, f"no functions in schema contract {path.name}")
        for token in PROHIBITED_SOURCE_TOKENS:
            ledger.check(token not in text, f"prohibited token absent {path.name}:{token}")

    ledger.check(
        not hasattr(schema_module, "validate_candidate_meaning"),
        "validation absent",
    )
    ledger.check(
        not hasattr(schema_module, "construct_candidate_meaning"),
        "constructor absent",
    )
    ledger.check(
        not hasattr(schema_module, "select_candidate_meaning"),
        "selection absent",
    )
    ledger.check(
        not hasattr(schema_module, "adapt_to_meaning_structure_manifest"),
        "MSM adapter absent",
    )

    for name in (
        "ACCEPTED_PARENT_HEAD",
        "ACCEPTED_PARENT_TREE",
        "ACCEPTED_PARENT_SUBJECT",
        "PACKAGE_ID",
        "SCHEMA_VERSION",
        "SPEC_ID",
        "SPEC_VERSION",
    ):
        value = getattr(identity_module, name)
        ledger.check(isinstance(value, str) and bool(value), f"identity text {name}")
    ledger.check(
        identity_module.ACCEPTED_PARENT_HEAD
        == "bb22f0fff6b64deaeeae8285dfabdbdd586d8473",
        "accepted parent HEAD",
    )
    ledger.check(
        identity_module.ACCEPTED_PARENT_TREE
        == "12131cc607c1dd293b3e741443d42ad69ba83063",
        "accepted parent tree",
    )
    ledger.check(
        identity_module.ACCEPTED_PARENT_SUBJECT
        == "Slice 38H disabled bootstrap integration and Slice 38 closeout",
        "accepted parent subject",
    )

    # Malformed constructor shapes: missing required fields, forbidden fixed
    # fields, unknown keywords, and non-construction statuses all fail closed.
    for record_type in record_types:
        kwargs = dict(fixture_kwargs[record_type])
        for field_name in tuple(kwargs):
            reduced = dict(kwargs)
            reduced.pop(field_name)
            _expect_type_error(
                ledger,
                f"missing required {record_type.__name__}.{field_name}",
                record_type,
                **reduced,
            )
        for item in fields(record_type):
            if not item.init:
                attempt = dict(kwargs)
                attempt[item.name] = getattr(instances[record_types.index(record_type)], item.name)
                _expect_type_error(
                    ledger,
                    f"fixed field rejected {record_type.__name__}.{item.name}",
                    record_type,
                    **attempt,
                )
        for index in range(64):
            attempt = dict(kwargs)
            attempt[f"unknown_field_{index:02d}"] = "not_admitted"
            _expect_type_error(
                ledger,
                f"unknown field rejected {record_type.__name__}.{index}",
                record_type,
                **attempt,
            )

    invalid_status_values = (
        *FORBIDDEN_GATE_VALUES,
        *module.DEFERRED_SLICE40_GATE_OUTCOMES,
        *module.PROHIBITED_AUTHORITY_PATHS,
        *(f"unknown_status_{index:03d}" for index in range(128)),
    )
    for value in invalid_status_values:
        _expect_value_error(
            ledger,
            f"invalid status rejected {value}",
            module.CandidateMeaningConstructionStatus,
            value,
        )

    # Fixed downstream fields cannot be supplied to state or receipt.
    for field_name in (*fixed_true, *fixed_false):
        attempt = dict(fixture_kwargs[module.CandidateMeaningState])
        attempt[field_name] = not getattr(state, field_name)
        _expect_type_error(
            ledger,
            f"state downstream field rejected {field_name}",
            module.CandidateMeaningState,
            **attempt,
        )
    for field_name in ("candidate_only", *receipt_false):
        attempt = dict(fixture_kwargs[module.CandidateMeaningConstructionReceipt])
        attempt[field_name] = not getattr(receipt, field_name)
        _expect_type_error(
            ledger,
            f"receipt downstream field rejected {field_name}",
            module.CandidateMeaningConstructionReceipt,
            **attempt,
        )

    print("AI.WEB SLICE 39A BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_constructor_cases={ledger.malformed_cases}")
    print(f"record_types={len(record_types)}")
    print(f"construction_statuses={len(EXPECTED_STATUSES)}")
    print(f"permanent_boundaries={len(module.PERMANENT_CANDIDATE_MEANING_BOUNDARIES)}")
    print(f"prohibited_authority_paths={len(module.PROHIBITED_AUTHORITY_PATHS)}")
    print("runtime_constructor_installed=0")
    print("validator_installed=0")
    print("identity_calculation_installed=0")
    print("lifecycle_transition_authority=0")
    print("msm_v1_modified=0")
    print("msm_adapter_installed=0")
    print("selected_meaning=0")
    print("gate_outcome=0")
    print("truth_evidence_permission=0")
    print("route_invocation_action_memory_rendering_delivery=0")
    print("llm_embedding_vector_rag_similarity_authority=0")
    if ledger.failures:
        print(f"failure_count={len(ledger.failures)}")
        for failure in ledger.failures:
            print(f"FAIL: {failure}")
        print("AI.WEB SLICE 39A BEHAVIOR TEST: FAIL")
        return 1
    print("failure_count=0")
    print("AI.WEB SLICE 39A BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
