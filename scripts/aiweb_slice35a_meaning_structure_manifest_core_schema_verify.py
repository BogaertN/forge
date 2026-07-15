#!/usr/bin/env python3
"""Independent verifier for Slice 35A core schema contract."""

from __future__ import annotations

import ast
from dataclasses import fields, is_dataclass
import importlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = "aiweb_language_core_bootstrap.meaning_structure_manifest"
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
PACKAGE_DIR = REPO / "aiweb_language_core_bootstrap" / "meaning_structure_manifest"
TEST_PATH = REPO / "scripts" / "test_aiweb_slice35a_meaning_structure_manifest_core_schema.py"
EXPECTED_FILES = (
    "__init__.py",
    "_enums.py",
    "_identity.py",
    "_records.py",
)
PROHIBITED_IMPORT_ROOTS = {
    "aiohttp",
    "chromadb",
    "fastapi",
    "flask",
    "httpx",
    "json",
    "ollama",
    "openai",
    "pathlib",
    "pickle",
    "requests",
    "socket",
    "sqlite3",
    "subprocess",
    "urllib",
}
PROHIBITED_CALL_NAMES = {
    "open",
    "compile",
    "eval",
    "exec",
    "input",
    "print",
}

def fail(message: str) -> None:
    raise AssertionError(message)


def verify_source() -> None:
    actual = tuple(sorted(path.name for path in PACKAGE_DIR.iterdir() if path.is_file()))
    if actual != EXPECTED_FILES:
        fail(f"unexpected package files: {actual}")

    for path in sorted(PACKAGE_DIR.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in PROHIBITED_IMPORT_ROOTS:
                        fail(f"prohibited import {alias.name!r} in {path.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".", 1)[0]
                    if root in PROHIBITED_IMPORT_ROOTS:
                        fail(f"prohibited import {node.module!r} in {path.name}")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in PROHIBITED_CALL_NAMES:
                    fail(f"prohibited call {node.func.id!r} in {path.name}")



def verify_runtime_surface() -> None:
    package = importlib.import_module(PACKAGE)
    if package.PACKAGE_NAME != PACKAGE:
        fail("package identity mismatch")
    if package.PACKAGE_ID != "aiweb-forge-meaning-structure-manifest":
        fail("package id mismatch")
    if package.SCHEMA_NAME != "MeaningStructureManifest":
        fail("schema name mismatch")
    if package.SCHEMA_ABBREVIATION != "MSM-v1":
        fail("schema abbreviation mismatch")
    if package.SCHEMA_VERSION != "MSM-v1":
        fail("schema version mismatch")

    enum_expectations = {
        package.SemanticRecordKind: {
            "lineage_root",
            "candidate_meaning",
            "non_selection_outcome",
            "selected_governed_meaning",
            "governed_result_reference",
            "governed_outward_meaning",
            "expression_link",
            "validation_link",
            "delivery_or_containment_link",
            "external_authority_reference",
            "semantic_transition_trace",
            "meaning_structure_manifest",
        },
        package.SemanticDirection: {"inward", "outward"},
        package.LineageOriginKind: {
            "source_bound_human_expression",
            "authorized_outward_expression_purpose",
        },
        package.SemanticLifecycleState: {
            "lineage_origin",
            "candidate_meaning",
            "unresolved",
            "clarification_required",
            "refused",
            "unsupported",
            "authority_blocked",
            "selected_governed_meaning",
            "governed_result_referenced",
            "governed_outward_meaning",
            "expression_linked",
            "validation_linked",
            "delivery_linked",
            "containment_linked",
            "corrected",
            "superseded",
        },
        package.NonSelectionOutcomeKind: {
            "unresolved",
            "clarification_required",
            "refused",
            "unsupported",
            "authority_blocked",
        },
        package.DeliveryContainmentKind: {
            "delivery_linked",
            "containment_linked",
        },
        package.SemanticTransitionKind: {
            "ancestry",
            "correction",
            "supersession",
            "rejection",
            "containment",
            "narrowing",
            "broadening",
        },
        package.ExternalAuthorityKind: {
            "raw_source_or_input_event",
            "parsed_question_or_typed_input",
            "source_custody",
            "evidence_or_claim_status",
            "mea_problem_state",
            "existing_rmc_meaning_or_render_artifact",
            "manifest_contract",
            "capability_contract_or_routing_admission",
            "invocation_execution_or_verification_receipt",
            "render_preview_or_output_object",
            "rmc_echo_validator_receipt",
            "delivery_or_containment_receipt",
            "memory_authorization_or_event_receipt",
            "identity_access_consent_or_user_authority",
            "contribution_economy_or_ledger",
            "rollback_patch_runtime_or_containment",
            "licensing_provenance_or_resource_admission",
        },
        package.SemanticPreservationClass: {
            "negation",
            "uncertainty_and_claim_strength",
            "modality_and_conditional_scope",
            "time_and_operational_status",
            "evidence_boundary",
            "action_proposal_simulation_and_observation",
            "permission_versus_request",
            "privacy_and_identity_boundary",
            "refusal_and_containment_boundary",
            "unresolved_ambiguity",
            "memory_boundary",
            "economic_and_ledger_boundary",
            "non_llm_provenance",
        },
    }
    for enum_class, expected_values in enum_expectations.items():
        actual_values = {member.value for member in enum_class}
        if actual_values != expected_values:
            fail(f"enum mismatch for {enum_class.__name__}: {actual_values}")

    record_names = (
        "LineageRootRecord",
        "CandidateMeaningRecord",
        "NonSelectionOutcomeRecord",
        "SelectedGovernedMeaningRecord",
        "GovernedResultReferenceRecord",
        "GovernedOutwardMeaningRecord",
        "ExpressionLinkRecord",
        "ValidationLinkRecord",
        "DeliveryContainmentLinkRecord",
        "ExternalAuthorityReferenceRecord",
        "SemanticTransitionTraceRecord",
        "MeaningStructureManifestV1",
    )
    expected_fields = {
        "LineageRootRecord": (
            "lineage_id", "origin_kind", "origin_ref", "direction",
            "record_kind", "lifecycle_state", "schema_version",
        ),
        "CandidateMeaningRecord": (
            "record_id", "lineage_id", "source_expression_ref",
            "communicative_act", "concept_refs", "relation_refs",
            "meaning_modifiers", "ambiguity_reasons",
            "unresolved_referents", "authority_sensitive_implications",
            "preservation_classes", "record_kind", "lifecycle_state",
            "schema_version",
        ),
        "NonSelectionOutcomeRecord": (
            "record_id", "lineage_id", "outcome_kind", "candidate_refs",
            "reasons", "required_clarifications",
            "external_authority_refs", "record_kind", "schema_version",
        ),
        "SelectedGovernedMeaningRecord": (
            "record_id", "lineage_id", "selected_candidate_ref",
            "selection_authority_ref", "communicative_act",
            "concept_refs", "relation_refs", "meaning_modifiers",
            "inherited_limitations", "authority_sensitive_distinctions",
            "preservation_classes", "record_kind", "lifecycle_state",
            "schema_version",
        ),
        "GovernedResultReferenceRecord": (
            "record_id", "lineage_id", "selected_meaning_ref",
            "external_authority_ref", "semantic_relevance",
            "record_kind", "lifecycle_state", "schema_version",
        ),
        "GovernedOutwardMeaningRecord": (
            "record_id", "lineage_id", "outward_basis_refs",
            "prior_selected_meaning_ref", "permitted_claims",
            "required_qualifications", "prohibited_enlargements",
            "external_dependency_refs", "preservation_classes",
            "record_kind", "lifecycle_state", "schema_version",
        ),
        "ExpressionLinkRecord": (
            "record_id", "lineage_id",
            "governed_outward_meaning_ref",
            "expression_candidate_ref", "record_kind",
            "lifecycle_state", "schema_version",
        ),
        "ValidationLinkRecord": (
            "record_id", "lineage_id", "expression_link_ref",
            "external_validation_receipt_ref",
            "external_validation_disposition", "record_kind",
            "lifecycle_state", "schema_version",
        ),
        "DeliveryContainmentLinkRecord": (
            "record_id", "lineage_id", "prior_link_ref",
            "disposition", "external_receipt_ref", "record_kind",
            "schema_version",
        ),
        "ExternalAuthorityReferenceRecord": (
            "record_id", "lineage_id", "authority_kind",
            "external_object_ref", "semantic_relevance",
            "record_kind", "schema_version",
        ),
        "SemanticTransitionTraceRecord": (
            "record_id", "lineage_id", "from_record_ref",
            "to_record_ref", "from_state", "to_state",
            "transition_kind", "reason", "authority_reference_ref",
            "record_kind", "schema_version",
        ),
        "MeaningStructureManifestV1": (
            "manifest_id", "lineage_root", "candidate_meanings",
            "non_selection_outcomes", "selected_governed_meanings",
            "governed_result_references", "governed_outward_meanings",
            "expression_links", "validation_links",
            "delivery_or_containment_links",
            "external_authority_references",
            "semantic_transition_traces", "record_kind", "package_id",
            "schema_id", "schema_version",
        ),
    }

    for name in record_names:
        record_class = getattr(package, name)
        if not is_dataclass(record_class):
            fail(f"not a dataclass: {name}")
        if not record_class.__dataclass_params__.frozen:
            fail(f"not frozen: {name}")
        if not hasattr(record_class, "__slots__"):
            fail(f"not slotted: {name}")
        actual_fields = tuple(item.name for item in fields(record_class))
        if actual_fields != expected_fields[name]:
            fail(f"record field mismatch for {name}: {actual_fields}")


def verify_import_side_effects() -> None:
    statements = (
        f"import {PACKAGE}",
        f"from {PACKAGE} import *",
    )
    for statement in statements:
        with tempfile.TemporaryDirectory(prefix="aiweb_slice35a_verify_") as tmp:
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["PYTHONPATH"] = str(REPO)
            before = tuple(Path(tmp).iterdir())
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
            if completed.returncode != 0:
                fail(f"import failed: {statement}\n{completed.stderr}")
            if before != after:
                fail(f"import side effect detected: {statement}")


def verify_behavior_test() -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-B", str(TEST_PATH)],
        cwd=REPO,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        fail(f"behavior test failed\n{completed.stdout}\n{completed.stderr}")
    if "SLICE 35A BEHAVIOR TEST: PASS" not in completed.stdout:
        fail("behavior test did not report PASS")


def main() -> int:
    verify_source()
    verify_runtime_surface()
    verify_import_side_effects()
    verify_behavior_test()
    print("SLICE 35A INDEPENDENT VERIFIER: PASS")
    print(f"package={PACKAGE}")
    print(f"package_files={len(EXPECTED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
