#!/usr/bin/env python3
"""Behavior, containment, determinism, and adversarial proof for Slice 34."""

from __future__ import annotations

from pathlib import Path
import sys

sys.dont_write_bytecode = True
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from contextlib import ExitStack
from dataclasses import replace
import builtins
import json
import os
import socket
import subprocess
from unittest.mock import patch
import urllib.request

from aiweb_language_core_bootstrap.regression_containment import (
    FLOW_IDENTITY_EXPECTATIONS,
    PROHIBITED_AUTHORITY_CATEGORIES,
    REQUIRED_CONTAINMENT_GUARDS,
    REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT,
    REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT,
    REQUIRED_PRIOR_COMMAND_COUNT,
    build_bootstrap_containment_state,
    run_default_containment_evaluation,
    run_explicit_offline_containment_evaluation,
    validate_bootstrap_containment_evaluation,
    validate_bootstrap_containment_state,
    validate_flow_containment_proof,
)
from aiweb_language_core_bootstrap.regression_containment.schema import (
    build_bootstrap_containment_evaluation,
    build_flow_containment_proof,
)

ACCEPTED_PACKAGE_NAMES = (
    "aiweb_meaning_law_trace_scaffold",
    "aiweb_concept_boundary_scaffold",
    "aiweb_predicate_role_boundary_scaffold",
    "aiweb_verbal_cognition_gate_boundary_scaffold",
    "aiweb_candidate_meaning_boundary_scaffold",
    "aiweb_ambiguity_clarification_boundary_scaffold",
    "aiweb_requirements_traceability_scaffold",
    "aiweb_external_resource_quarantine_scaffold",
    "aiweb_corpus_evidence_memory_trace_scaffold",
    "aiweb_selected_meaning_boundary_scaffold",
    "aiweb_output_expression_boundary_scaffold",
    "aiweb_gp014_preservation_decision_scaffold",
    "aiweb_rmc_echo_boundary_scaffold",
    "aiweb_delivery_action_tool_routing_boundary_scaffold",
    "aiweb_read_only_inspection_surface_scaffold",
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(label)


def reid_state(state):
    return replace(state, state_id=state.expected_id())


def reid_proof(proof):
    return replace(proof, proof_id=proof.expected_id())


def reid_evaluation(evaluation):
    return replace(evaluation, evaluation_id=evaluation.expected_id())


# Import alone must not load accepted components.
check(
    sum(1 for name in ACCEPTED_PACKAGE_NAMES if name in sys.modules) == 0,
    "Slice 34 import loads zero accepted components",
)

# State behavior and authority boundaries.
disabled_state = build_bootstrap_containment_state()
enabled_state = build_bootstrap_containment_state(
    explicit_offline_developer_enable=True
)
check(validate_bootstrap_containment_state(disabled_state).ok, "disabled state valid")
check(validate_bootstrap_containment_state(enabled_state).ok, "enabled state valid")
check(not disabled_state.enabled, "disabled by default")
check(enabled_state.enabled, "explicit state enabled")
for state in (disabled_state, enabled_state):
    for field in (
        "full_regression_execution_allowed", "rollback_execution_allowed",
        "filesystem_write_allowed", "network_allowed", "environment_lookup_allowed",
        "runtime_memory_write_allowed", "evidence_mutation_allowed",
        "external_resource_ingestion_allowed", "component_invocation_allowed",
        "component_verifier_invocation_allowed", "gp014_import_allowed",
        "gp014_call_allowed", "delivery_allowed", "tool_routing_allowed",
        "action_allowed", "route_connection_allowed", "api_connection_allowed",
        "ui_connection_allowed", "llm_authority_allowed", "vector_authority_allowed",
        "embedding_authority_allowed", "rag_authority_allowed", "chroma_authority_allowed",
        "qwen_authority_allowed", "ollama_authority_allowed",
        "general_language_claim_allowed", "technical_acceptance_grant_allowed",
        "release_authorized", "production_ready",
    ):
        check(getattr(state, field) is False, f"state boundary false: {field}")

# Default refusal is exact and produces no flow proof.
default_result = run_default_containment_evaluation()
check(validate_bootstrap_containment_evaluation(default_result).ok, "default result valid")
check(default_result.status == "refused_bootstrap_containment_evaluation_disabled", "default refusal status")
check(default_result.flow_proofs == (), "default refusal has no proof")
check(not default_result.runtime_containment_passed, "default refusal not passed")

# Block runtime side effects while executing the exact in-memory evaluation.
def forbidden(*args, **kwargs):
    raise AssertionError("forbidden runtime side effect attempted")

with ExitStack() as stack:
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(os, "system", forbidden))
    stack.enter_context(patch.object(subprocess, "run", forbidden))
    stack.enter_context(patch.object(subprocess, "Popen", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(socket, "create_connection", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    enabled_result = run_explicit_offline_containment_evaluation()

check(validate_bootstrap_containment_evaluation(enabled_result).ok, "enabled result valid")
check(enabled_result.runtime_containment_passed, "runtime containment passed")
check(enabled_result.validated_flow_count == 5, "five flows validated")
check(enabled_result.required_flow_count == 5, "five flows required")
check(enabled_result.containment_guard_ids == REQUIRED_CONTAINMENT_GUARDS, "guard catalog exact")
check(enabled_result.inherited_regression_command_count == REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT, "45 inherited commands required")
check(enabled_result.phase_b_preservation_command_count == REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT, "8 Phase B commands required")
check(enabled_result.total_prior_command_count == REQUIRED_PRIOR_COMMAND_COUNT, "53 prior commands required")
check(enabled_result.one_command_rollback_required, "one-command rollback required")

for proof, expectation in zip(enabled_result.flow_proofs, FLOW_IDENTITY_EXPECTATIONS):
    check(validate_flow_containment_proof(proof).ok, f"proof valid: {proof.flow_name}")
    check(proof.flow_name == expectation.flow_name, "flow name exact")
    check(proof.flow_spec_id == expectation.flow_spec_id, "flow spec exact")
    check(proof.assembly_result_id == expectation.assembly_result_id, "result exact")
    check(proof.trace_id == expectation.trace_id, "trace exact")
    check(proof.receipt_id == expectation.receipt_id, "receipt exact")
    check(proof.verdict == expectation.verdict, "verdict exact")
    check(proof.loaded_component_count == expectation.loaded_component_count, "loaded count exact")
    check(proof.loaded_component_set_digest == expectation.loaded_component_set_digest, "component digest exact")
    for field in (
        "persistent_side_effect_performed", "filesystem_write_performed",
        "network_access_performed", "runtime_memory_write_performed",
        "evidence_mutation_performed", "external_resource_used",
        "component_invocation_performed", "component_verifier_invocation_performed",
        "gp014_imported", "gp014_called", "delivery_performed",
        "tool_routing_performed", "action_performed", "runtime_connection_performed",
    ):
        check(getattr(proof, field) is False, f"proof boundary false: {field}")

for field in (
    "inherited_regression_executed_by_runtime",
    "phase_b_preservation_executed_by_runtime", "rollback_executed_by_runtime",
    "technical_acceptance_granted", "acceptance_widened",
    "general_language_claim_made", "filesystem_write_performed",
    "network_access_performed", "runtime_memory_write_performed",
    "evidence_mutation_performed", "external_resource_used",
    "component_invocation_performed", "component_verifier_invocation_performed",
    "gp014_imported", "gp014_called", "delivery_performed",
    "tool_routing_performed", "action_performed", "runtime_connection_performed",
    "release_authorized", "production_ready",
):
    check(getattr(enabled_result, field) is False, f"evaluation boundary false: {field}")

# Evaluation is deterministic across repeated execution.
repeat = run_explicit_offline_containment_evaluation()
check(enabled_result == repeat, "repeat evaluation exact")
check(
    json.dumps(enabled_result.to_dict(), sort_keys=True, separators=(",", ":"))
    == json.dumps(repeat.to_dict(), sort_keys=True, separators=(",", ":")),
    "serialized evaluation deterministic",
)
check(
    sum(1 for name in ACCEPTED_PACKAGE_NAMES if name in sys.modules) == 15,
    "exact 15 accepted components loaded by explicit flow",
)

# Re-IDed state attacks remain invalid.
state_attacks = (
    replace(enabled_state, network_allowed=True),
    replace(enabled_state, filesystem_write_allowed=True),
    replace(enabled_state, runtime_memory_write_allowed=True),
    replace(enabled_state, evidence_mutation_allowed=True),
    replace(enabled_state, external_resource_ingestion_allowed=True),
    replace(enabled_state, action_allowed=True),
    replace(enabled_state, technical_acceptance_grant_allowed=True),
    replace(enabled_state, production_ready=True),
)
for index, attack in enumerate(state_attacks, start=1):
    attack = reid_state(attack)
    check(not validate_bootstrap_containment_state(attack).ok, f"state attack {index} rejected")

# Re-IDed flow proof attacks remain invalid.
base_proof = enabled_result.flow_proofs[-1]
proof_attacks = (
    replace(base_proof, flow_spec_id="trace_flow_spec:" + "0" * 64),
    replace(base_proof, assembly_result_id="trace_receipt_assembly_result:" + "1" * 64),
    replace(base_proof, trace_id="derivation_trace:" + "2" * 64),
    replace(base_proof, receipt_id="derivation_receipt:" + "3" * 64),
    replace(base_proof, verdict="PASS_FABRICATED"),
    replace(base_proof, loaded_component_count=14),
    replace(base_proof, network_access_performed=True),
    replace(base_proof, runtime_memory_write_performed=True),
    replace(base_proof, evidence_mutation_performed=True),
    replace(base_proof, action_performed=True),
    replace(base_proof, exact_identity_match=False),
)
for index, attack in enumerate(proof_attacks, start=1):
    attack = reid_proof(attack)
    check(not validate_flow_containment_proof(attack).ok, f"proof attack {index} rejected")

# Re-IDed evaluation attacks remain invalid.
evaluation_attacks = (
    replace(enabled_result, flow_proofs=tuple(reversed(enabled_result.flow_proofs))),
    replace(enabled_result, flow_proofs=enabled_result.flow_proofs[:-1], validated_flow_count=4),
    replace(enabled_result, flow_proofs=enabled_result.flow_proofs + (enabled_result.flow_proofs[-1],), validated_flow_count=6),
    replace(enabled_result, inherited_regression_command_count=44),
    replace(enabled_result, phase_b_preservation_command_count=7),
    replace(enabled_result, total_prior_command_count=52),
    replace(enabled_result, inherited_regression_executed_by_runtime=True),
    replace(enabled_result, rollback_executed_by_runtime=True),
    replace(enabled_result, technical_acceptance_granted=True),
    replace(enabled_result, acceptance_widened=True),
    replace(enabled_result, general_language_claim_made=True),
    replace(enabled_result, network_access_performed=True),
    replace(enabled_result, runtime_memory_write_performed=True),
    replace(enabled_result, evidence_mutation_performed=True),
    replace(enabled_result, action_performed=True),
    replace(enabled_result, production_ready=True),
)
for index, attack in enumerate(evaluation_attacks, start=1):
    attack = reid_evaluation(attack)
    check(not validate_bootstrap_containment_evaluation(attack).ok, f"evaluation attack {index} rejected")

# A fully fabricated, internally self-consistent proof/evaluation remains rejected.
fake_proofs = []
for index, proof in enumerate(enabled_result.flow_proofs):
    fake = reid_proof(
        replace(
            proof,
            flow_spec_id="trace_flow_spec:" + f"{index + 10:064x}",
            assembly_result_id="trace_receipt_assembly_result:" + f"{index + 20:064x}",
            trace_id="derivation_trace:" + f"{index + 30:064x}",
            receipt_id="derivation_receipt:" + f"{index + 40:064x}",
        )
    )
    fake_proofs.append(fake)
fake_evaluation = reid_evaluation(
    replace(enabled_result, flow_proofs=tuple(fake_proofs))
)
check(fake_evaluation.evaluation_id == fake_evaluation.expected_id(), "fabricated chain fully re-IDed")
check(not validate_bootstrap_containment_evaluation(fake_evaluation).ok, "fabricated chain rejected")

check(len(REQUIRED_CONTAINMENT_GUARDS) == 20, "20 containment guards")
check(len(PROHIBITED_AUTHORITY_CATEGORIES) == 23, "23 prohibited authority categories")

print("SLICE34_BOOTSTRAP_REGRESSION_CONTAINMENT_ACCEPTANCE_TEST=PASS")
print(f"TEST_COUNT={checks}")
print("FABRICATED_RECOMPUTED_CONTAINMENT_CHAIN_REJECTED=True")
print("RUNTIME_NETWORK_WRITE_ACTION_ATTEMPTS=0")
