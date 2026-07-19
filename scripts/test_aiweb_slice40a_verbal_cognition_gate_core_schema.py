#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 40A verbal-cognition gate core schema."""

from __future__ import annotations

import argparse
import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass
from enum import Enum
import importlib
import inspect
from pathlib import Path
import sys


PACKAGE = "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
EXPECTED_EXPORTS = ('ACCEPTED_PARENT_HEAD', 'ACCEPTED_PARENT_SUBJECT', 'ACCEPTED_PARENT_TREE', 'CANDIDATE_INPUT_REFERENCE_SCHEMA_ID', 'DEFERRED_SLICE40_RUNTIME_AUTHORITY', 'GATE_FAMILY_VALUES', 'GATE_IDENTITY_SCHEMA_ID', 'GATE_PROFILE_SCHEMA_ID', 'GateCandidateInputReference', 'GateEvaluationState', 'GateLimitationReference', 'GateProvenanceReference', 'GateReasonGround', 'GateRequirementReference', 'GateTraceReference', 'LIMITATION_REFERENCE_SCHEMA_ID', 'MSM_GATE_CUSTODY_DECISION', 'MSM_V1_AUTOMATIC_MIGRATION_ALLOWED', 'MSM_V1_SCHEMA_MODIFICATION_ALLOWED', 'PACKAGE_ID', 'PACKAGE_NAME', 'PERMANENT_GATE_CORE_BOUNDARIES', 'POSITIVE_DISPOSITION_NAMING_DECISION', 'PROHIBITED_AUTHORITY_PATHS', 'PROVENANCE_REFERENCE_SCHEMA_ID', 'REASON_GROUND_SCHEMA_ID', 'RECOVERABLE_PURPOSE_ARCHITECTURE_ALIASES', 'REQUIREMENT_REFERENCE_SCHEMA_ID', 'REVIEW_RECORD_SCHEMA_ID', 'SCHEMA_ABBREVIATION', 'SCHEMA_NAME', 'SCHEMA_ONLY_EVALUATION_STATE_VALUES', 'SCHEMA_VERSION', 'SPEC_ID', 'SPEC_VERSION', 'TRACE_REFERENCE_SCHEMA_ID', 'VerbalCognitionGateFamily', 'VerbalCognitionGateIdentity', 'VerbalCognitionGateProfileIdentity', 'VerbalCognitionGateReviewRecord')
EXPECTED_FAMILIES = (
    "expectancy",
    "congruity",
    "connectedness",
    "recoverable_purpose",
)
EXPECTED_STATES = (
    "not_evaluated",
    "ready_for_later_evaluation",
    "evaluation_deferred",
    "evaluation_unavailable",
)
FORBIDDEN_OUTCOME_VALUES = (
    "accepted",
    "approved",
    "passed",
    "failed",
    "selected_meaning",
    "candidate_accepted",
    "candidate_rejected",
    "ambiguity_disposition",
    "clarification_required",
    "unsupported",
    "refusal_relevant",
    "held",
    "blocked_progression",
    "selection_eligible",
    "gate_satisfied",
)
FORBIDDEN_FUNCTION_PREFIXES = (
    "build_",
    "calculate_",
    "canonical_",
    "compose_",
    "create_",
    "evaluate_",
    "select_",
    "validate_",
    "assert_valid",
    "resolve_",
    "route_",
    "invoke_",
    "render_",
    "deliver_",
)
PROHIBITED_IMPORT_ROOTS = {
    "anthropic", "chromadb", "faiss", "httpx", "keras", "langchain",
    "llama_index", "nltk", "numpy", "ollama", "openai", "pandas",
    "pathlib", "requests", "scipy", "sentence_transformers", "sklearn",
    "socket", "spacy", "subprocess", "tensorflow", "torch", "transformers",
    "urllib",
}
PROHIBITED_SOURCE_TOKENS = (
    "@app.route", "@router.", "FastAPI(", "Flask(", "requests.",
    "urlopen(", "socket.socket(", "os.system(", "subprocess.", "open(",
    "Path(", "read_text(", "write_text(", "semantic_similarity(",
    "embedding(", "aiweb_verbal_cognition_gate_boundary_scaffold",
    "meaning_structure_manifest import",
)


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


def expect_type_error(ledger: Ledger, label: str, function, *args, **kwargs) -> None:
    try:
        function(*args, **kwargs)
    except TypeError:
        ledger.malformed(True, label)
    except Exception as error:
        ledger.malformed(False, f"{label}:wrong_exception:{type(error).__name__}")
    else:
        ledger.malformed(False, f"{label}:accepted")


def expect_value_error(ledger: Ledger, label: str, function, *args) -> None:
    try:
        function(*args)
    except ValueError:
        ledger.malformed(True, label)
    except Exception as error:
        ledger.malformed(False, f"{label}:wrong_exception:{type(error).__name__}")
    else:
        ledger.malformed(False, f"{label}:accepted")


def fixtures(module, family):
    profile = module.VerbalCognitionGateProfileIdentity(
        profile_id=f"gate_profile:{family.value}:v1",
        profile_key=f"{family.value}_default_profile",
        profile_version="v1.0.0",
        gate_family=family,
        governing_authority_refs=("document6:verbal_cognition_gate_engine:v1",),
        required_schema_refs=("slice39g:manifest_candidate_integration:v1",),
        exact_profile_only=True,
    )
    identity = module.VerbalCognitionGateIdentity(
        gate_id=f"gate:{family.value}:demo",
        gate_key=f"{family.value}_gate",
        gate_version="v1.0.0",
        gate_family=family,
        gate_profile_ref=profile.profile_id,
    )
    candidate = module.GateCandidateInputReference(
        candidate_input_ref_id=f"gate_candidate_input:{family.value}:demo",
        candidate_meaning_id="candidate_meaning:demo",
        candidate_state_id="candidate_state:demo",
        candidate_lineage_id="lineage:demo",
        candidate_identity_ref="candidate_meaning:demo",
        candidate_content_ref="candidate_content:demo",
        candidate_provenance_ref="candidate_provenance:demo",
        construction_receipt_ref="candidate_receipt:demo",
        manifest_candidate_record_ref="msm_candidate:demo",
        manifest_companion_ref="manifest_companion:demo",
        construction_trace_ref="construction_trace:demo",
        limitation_reference_ref="candidate_limitation:demo",
        alternative_relationship_refs=("candidate_alternative:demo",),
    )
    requirement = module.GateRequirementReference(
        requirement_reference_id=f"gate_requirement:{family.value}:demo",
        gate_family=family,
        requirement_key=f"{family.value}_requirement",
        requirement_version="v1.0.0",
        candidate_input_ref=candidate.candidate_input_ref_id,
        subject_record_refs=(candidate.candidate_meaning_id,),
        required_authority_refs=("document6:verbal_cognition_gate_engine:v1",),
        required_record_refs=("candidate_record:demo",),
        required_relation_refs=("candidate_relation:demo",),
        limitation_refs=("gate_limitation:demo",),
    )
    reason = module.GateReasonGround(
        reason_ground_id=f"gate_reason:{family.value}:demo",
        gate_family=family,
        reason_key=f"{family.value}_reason_ground",
        candidate_input_ref=candidate.candidate_input_ref_id,
        requirement_reference_ids=(requirement.requirement_reference_id,),
        supporting_record_refs=("supporting_record:demo",),
        conflicting_record_refs=(),
        missing_record_refs=(),
        unknown_record_refs=(),
        authority_refs=("document6:verbal_cognition_gate_engine:v1",),
        limitation_refs=("gate_limitation:demo",),
    )
    trace = module.GateTraceReference(
        trace_reference_id=f"gate_trace:{family.value}:demo",
        candidate_input_ref=candidate.candidate_input_ref_id,
        source_span_refs=("source_span:demo",),
        candidate_trace_refs=("candidate_trace:demo",),
        construction_trace_refs=("construction_trace:demo",),
        structural_trace_refs=("structural_trace:demo",),
        concept_sense_trace_refs=("concept_sense_trace:demo",),
        predicate_role_frame_trace_refs=("predicate_frame_trace:demo",),
        alternative_relationship_refs=("candidate_alternative:demo",),
        predecessor_receipt_refs=("slice39h_receipt:demo",),
    )
    provenance = module.GateProvenanceReference(
        provenance_reference_id=f"gate_provenance:{family.value}:demo",
        candidate_input_ref=candidate.candidate_input_ref_id,
        source_event_id="source_event:demo",
        source_sha256="0" * 64,
        candidate_provenance_ref="candidate_provenance:demo",
        gate_profile_ref=profile.profile_id,
        governing_document_refs=("document6:verbal_cognition_gate_engine:v1",),
        authority_version_refs=(("document6", "v1"),),
        schema_version_refs=(("slice39g", "v1"),),
        external_resource_refs=(),
    )
    limitation = module.GateLimitationReference(
        limitation_reference_id=f"gate_limitation:{family.value}:demo",
        candidate_input_ref=candidate.candidate_input_ref_id,
        limitation_key="schema_only",
        reason_refs=("slice40a_no_evaluation",),
        affected_requirement_refs=(requirement.requirement_reference_id,),
        later_authority_refs=("slice40b_validation", f"slice40_{family.value}_runtime"),
    )
    review = module.VerbalCognitionGateReviewRecord(
        review_record_id=f"gate_review:{family.value}:demo",
        identity=identity,
        profile=profile,
        candidate_input=candidate,
        requirement_references=(requirement,),
        reason_grounds=(reason,),
        evaluation_state=module.GateEvaluationState.NOT_EVALUATED,
        trace_references=(trace,),
        provenance_reference=provenance,
        limitation_references=(limitation,),
    )
    return (identity, profile, candidate, requirement, reason, trace, provenance, limitation, review)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    ledger = Ledger()
    module = importlib.import_module(PACKAGE)
    package_modules = tuple(
        importlib.import_module(f"{PACKAGE}.{name}")
        for name in ("authority", "identity", "schema")
    )

    ledger.check(tuple(module.__all__) == EXPECTED_EXPORTS, "exact public exports")
    ledger.check(len(module.__all__) == len(set(module.__all__)), "exports unique")
    for name in EXPECTED_EXPORTS:
        ledger.check(hasattr(module, name), f"export exists {name}")

    families = tuple(item.value for item in module.VerbalCognitionGateFamily)
    states = tuple(item.value for item in module.GateEvaluationState)
    ledger.check(families == EXPECTED_FAMILIES, "exact gate families")
    ledger.check(states == EXPECTED_STATES, "exact schema evaluation states")
    ledger.check(tuple(module.GATE_FAMILY_VALUES) == families, "family authority matches enum")
    ledger.check(
        tuple(module.SCHEMA_ONLY_EVALUATION_STATE_VALUES) == states,
        "evaluation-state authority matches enum",
    )
    ledger.check(set(states).isdisjoint(FORBIDDEN_OUTCOME_VALUES), "states exclude outcomes")
    for item in (*module.VerbalCognitionGateFamily, *module.GateEvaluationState):
        ledger.check(isinstance(item, str), f"string enum {item.value}")
        ledger.check(isinstance(item, Enum), f"enum member {item.value}")

    ledger.check(module.ACCEPTED_PARENT_HEAD == "643686b8664fe938b8e87e6335cf6ecc3c87e1d3", "accepted parent head")
    ledger.check(module.ACCEPTED_PARENT_TREE == "a83b0561ff7858d0ea69db0f92ed6494fcde26aa", "accepted parent tree")
    ledger.check(module.ACCEPTED_PARENT_SUBJECT == "Slice 39H disabled bootstrap integration closeout", "accepted parent subject")
    ledger.check(module.MSM_GATE_CUSTODY_DECISION == "versioned_companion_required", "companion decision")
    ledger.check(module.MSM_V1_SCHEMA_MODIFICATION_ALLOWED is False, "MSM modification false")
    ledger.check(module.MSM_V1_AUTOMATIC_MIGRATION_ALLOWED is False, "MSM migration false")
    ledger.check(
        module.POSITIVE_DISPOSITION_NAMING_DECISION
        == "deferred_to_slice40g_source_and_document6_decision",
        "positive disposition name deferred",
    )
    ledger.check(
        tuple(module.RECOVERABLE_PURPOSE_ARCHITECTURE_ALIASES)
        == ("intended_purport", "recoverable_purpose"),
        "recoverable-purpose architecture aliases",
    )

    record_types = (
        module.VerbalCognitionGateIdentity,
        module.VerbalCognitionGateProfileIdentity,
        module.GateCandidateInputReference,
        module.GateRequirementReference,
        module.GateReasonGround,
        module.GateTraceReference,
        module.GateProvenanceReference,
        module.GateLimitationReference,
        module.VerbalCognitionGateReviewRecord,
    )
    all_instances = []
    for family in module.VerbalCognitionGateFamily:
        instances = fixtures(module, family)
        all_instances.extend(instances)
        review = instances[-1]
        ledger.check(review.identity.gate_family is family, f"identity family {family.value}")
        ledger.check(review.profile.gate_family is family, f"profile family {family.value}")
        ledger.check(review.requirement_references[0].gate_family is family, f"requirement family {family.value}")
        ledger.check(review.reason_grounds[0].gate_family is family, f"reason family {family.value}")
        ledger.check(review.evaluation_state is module.GateEvaluationState.NOT_EVALUATED, f"not evaluated {family.value}")
        ledger.check(hash(review) == hash(review), f"stable in-process hash {family.value}")
        ledger.check(review == fixtures(module, family)[-1], f"deterministic equality {family.value}")

    for record_type in record_types:
        ledger.check(is_dataclass(record_type), f"dataclass {record_type.__name__}")
        ledger.check(getattr(record_type, "__dataclass_params__").frozen is True, f"frozen {record_type.__name__}")
        ledger.check(hasattr(record_type, "__slots__"), f"slots {record_type.__name__}")
        sample = next(item for item in all_instances if isinstance(item, record_type))
        ledger.check(not hasattr(sample, "__dict__"), f"no dict {record_type.__name__}")
        ledger.check(record_type.__module__ == f"{PACKAGE}.schema", f"module {record_type.__name__}")
        init_fields = [item for item in fields(record_type) if item.init]
        kwargs = {item.name: getattr(sample, item.name) for item in init_fields}
        ledger.check(record_type(**kwargs) == sample, f"roundtrip constructor {record_type.__name__}")
        expect_type_error(ledger, f"extra field {record_type.__name__}", record_type, **kwargs, unexpected=True)
        if init_fields:
            missing = dict(kwargs)
            missing.pop(init_fields[0].name)
            expect_type_error(ledger, f"missing field {record_type.__name__}", record_type, **missing)
        fixed = next((item for item in fields(record_type) if not item.init), None)
        if fixed is not None:
            expect_type_error(ledger, f"fixed field constructor {record_type.__name__}", record_type, **kwargs, **{fixed.name: getattr(sample, fixed.name)})
        for item in fields(record_type):
            try:
                setattr(sample, item.name, getattr(sample, item.name))
            except (FrozenInstanceError, AttributeError):
                ledger.check(True, f"immutable {record_type.__name__}.{item.name}")
            except Exception as error:
                ledger.check(False, f"immutability wrong error {record_type.__name__}.{item.name}:{type(error).__name__}")
            else:
                ledger.check(False, f"mutable {record_type.__name__}.{item.name}")

    expect_value_error(ledger, "invalid gate family", module.VerbalCognitionGateFamily, "unknown")
    expect_value_error(ledger, "invalid evaluation state", module.GateEvaluationState, "passed")

    review = fixtures(module, module.VerbalCognitionGateFamily.EXPECTANCY)[-1]
    fixed_true = ("schema_only", "versioned_companion")
    fixed_false = (
        "runtime_evaluator_installed", "identity_calculated", "validation_performed",
        "lifecycle_transition_performed", "gate_evaluation_performed",
        "expectancy_result_created", "congruity_result_created",
        "connectedness_result_created", "recoverable_purpose_result_created",
        "gate_pass_created", "gate_failure_created", "gate_outcome_created",
        "ambiguity_disposition_created", "clarification_required_created",
        "unsupported_disposition_created", "refusal_relevant_disposition_created",
        "held_disposition_created", "blocked_progression_created",
        "positive_selection_review_disposition_created", "candidate_accepted",
        "candidate_rejected", "candidate_clarified", "selected_meaning_created",
        "truth_determined", "evidence_validated", "permission_granted",
        "execution_authorized", "capability_availability_created", "route_created",
        "tool_invoked", "action_performed", "memory_accessed", "rendered",
        "delivered", "external_resource_loaded", "language_model_used",
        "embedding_used", "vector_used", "rag_used", "semantic_similarity_used",
    )
    for name in fixed_true:
        ledger.check(getattr(review, name) is True, f"review fixed true {name}")
    for name in fixed_false:
        ledger.check(getattr(review, name) is False, f"review fixed false {name}")

    candidate = review.candidate_input
    for name in ("accepted_candidate", "selected_candidate"):
        ledger.check(getattr(candidate, name) is False, f"candidate fixed false {name}")
    requirement = review.requirement_references[0]
    for name in ("requirement_satisfied", "requirement_failed"):
        ledger.check(getattr(requirement, name) is False, f"requirement fixed false {name}")
    reason = review.reason_grounds[0]
    for name in ("reason_validated", "outcome_created"):
        ledger.check(getattr(reason, name) is False, f"reason fixed false {name}")
    ledger.check(review.trace_references[0].trace_validated is False, "trace validation false")
    ledger.check(review.provenance_reference.provenance_validated is False, "provenance validation false")
    ledger.check(review.provenance_reference.external_resource_loaded is False, "provenance external load false")
    ledger.check(review.limitation_references[0].clarification_created is False, "limitation clarification false")
    ledger.check(review.limitation_references[0].blocked_progression_created is False, "limitation block false")

    ledger.check(len(module.PERMANENT_GATE_CORE_BOUNDARIES) == 32, "permanent boundary count")
    ledger.check(len(module.PROHIBITED_AUTHORITY_PATHS) == 22, "prohibited authority count")
    ledger.check(len(module.DEFERRED_SLICE40_RUNTIME_AUTHORITY) == 19, "deferred authority count")

    for package_module in package_modules:
        functions = tuple(
            name for name, value in inspect.getmembers(package_module, inspect.isfunction)
            if value.__module__ == package_module.__name__
        )
        ledger.check(not functions, f"no runtime functions {package_module.__name__}")
        for name in dir(package_module):
            ledger.check(not name.startswith(FORBIDDEN_FUNCTION_PREFIXES), f"no function prefix {package_module.__name__}.{name}")

    package_path = repository / "aiweb_language_core_bootstrap" / "verbal_cognition_gate_runtime"
    expected_files = ("__init__.py", "authority.py", "identity.py", "schema.py")
    actual_files = tuple(path.name for path in sorted(package_path.glob("*.py")))
    ledger.check(actual_files == expected_files, "exact package files")
    for path in sorted(package_path.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ledger.check(False, f"no functions in package {path.name}:{node.name}")
        ledger.check(not (roots & PROHIBITED_IMPORT_ROOTS), f"no prohibited imports {path.name}")
        for token in PROHIBITED_SOURCE_TOKENS:
            ledger.check(token not in text, f"no prohibited token {path.name}:{token}")

    print("AI.WEB SLICE 40A BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_constructor_cases={ledger.malformed_cases}")
    print(f"record_types={len(record_types)}")
    print(f"gate_family_count={len(families)}")
    print(f"schema_evaluation_state_count={len(states)}")
    print(f"permanent_boundaries={len(module.PERMANENT_GATE_CORE_BOUNDARIES)}")
    print("versioned_companion_required=1")
    print("msm_v1_modified=0")
    print("positive_disposition_name_deferred=1")
    print("runtime_evaluator_installed=0")
    print("gate_evaluation_performed=0")
    print("gate_outcome_created=0")
    print("candidate_accepted_rejected_clarified_selected=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print(f"FAIL: {failure}")
    if ledger.failures:
        print("AI.WEB SLICE 40A BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 40A BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
