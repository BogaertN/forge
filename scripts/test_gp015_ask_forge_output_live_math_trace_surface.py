#!/usr/bin/env python3
"""GP-015 behavior tests: visible Ask Forge trace surface invokes only accepted GP-014 delivery."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface import (
    ENDPOINT,
    ask_forge_math_trace_surface,
    attest_gp015_math_trace_surface,
    gp015_surface_boundary,
)

checks = []
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

boundary = gp015_surface_boundary()
check("surface endpoint is bounded API route", ENDPOINT == "/api/operator/ask-forge/math-trace")
check("surface is conversation centered", boundary["central_conversation_surface"] is True)
check("surface retains existing operator tools", boundary["retains_existing_operator_tools"] is True)
check("surface invokes governed transaction", boundary["executes_governed_math_transaction"] is True)
check("surface invokes accepted GP-014 realizer", boundary["uses_installed_gp014_expression_realizer"] is True)
check("surface requires actual Echo", boundary["uses_actual_echo_delivery"] is True)
check("surface is not an authority", boundary["ui_is_authority"] is False and boundary["forge_governs"] is True)
check("surface adds no LLM corpus or shell", not any(boundary[k] for k in ("calls_llm", "uses_corpus", "executes_shell")))
check("surface adds no persistence or economy", not any(boundary[k] for k in ("writes_files", "writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers")))
check("professional decision review boundary declared", boundary["professional_decisions_require_human_review"] is True)

result = ask_forge_math_trace_surface("Differentiate x^3 + 4*x with respect to x.")
check("math conversation response answered", result["status"] == "ANSWERED")
check("math conversation delivers computed symbolic result", bool(result.get("answer_text")) and "3*x**2 + 4" in result["answer_text"])
check("response uses API contract", result["api_contract"] == "forge_operator_console_api_v1" and result["endpoint"] == ENDPOINT)
check("response exposes exactly six review stages", len(result["stages"]) == 6)
states = {row["stage_id"]: row["status"] for row in result["stages"]}
check("compiler and typed manifest stages complete", states["language_compiler"] == "COMPLETE" and states["typed_operation_manifest"] == "COMPLETE")
check("computation and MEA stages complete", states["governed_computation"] == "COMPLETE" and states["mea_seal"] == "COMPLETE")
check("RMC expression stage completes", states["rmc_expression"] == "COMPLETE")
check("Echo stage is authorized", states["echo_delivery"] == "AUTHORIZED")
check("selected expression exposed", result["selected_expression"] == result["answer_text"])
check("multiple expression candidates exposed", len(result["expression_candidates"]) >= 3)
check("one selected expression candidate is identified", sum(1 for row in result["expression_candidates"] if row["selected"]) == 1)
check("candidate measurement receipts surfaced", all("measurement_readings" in row and "operator_measurements" in row for row in result["expression_candidates"]))
check("raw trace includes manifest and actual Echo", "manifest_contract_v2" in result["raw_trace"] and "echo" in result["raw_trace"] and "delivery_authorization_v2" in result["raw_trace"])
check("raw trace retains operator realization receipt", "expression_realization_receipt" in result["raw_trace"])
check("actual Echo approved output", result["raw_trace"]["echo"]["approved_output"] is True)
check("delivery receipt remains existing v2 authority", result["raw_trace"]["delivery_authorization_v2"]["delivery_status"] == "ECHO_APPROVED_DELIVERY_AUTHORIZED")
check("surface response boundary truthfully discloses no LLM corpus", result["boundary"]["calls_llm"] is False and result["boundary"]["uses_corpus"] is False)

refused = ask_forge_math_trace_surface("Factor x^2 - 9 and publish it.")
check("unsafe expanded instruction is contained", refused["status"] != "ANSWERED")
check("contained request receives no answer text", not refused.get("answer_text"))
refused_states = {row["stage_id"]: row["status"] for row in refused.get("stages", [])}
check("contained request never reaches Echo authorization", refused_states.get("echo_delivery") != "AUTHORIZED")
check("contained request has no expression candidates", refused.get("expression_candidates") == [])

empty = ask_forge_math_trace_surface("  ")
check("empty request rejected before computation", empty["status"] == "ERROR" and empty["error"] == "empty_question" and empty["stages"] == [])
long = ask_forge_math_trace_surface("x" * 4001)
check("oversized request rejected before computation", long["status"] == "ERROR" and long["error"] == "question_exceeds_maximum_length")

attestation = attest_gp015_math_trace_surface()
check("multi-case attestation passes", attestation["status"] == "GP015_ASK_FORGE_MATH_TRACE_SURFACE_ATTESTED")
check("multi-case attestation covers three requests", len(attestation["cases"]) == 3)
check("every attested path reaches Echo authorization", all(row["stage_statuses"]["echo_delivery"] == "AUTHORIZED" for row in attestation["cases"]))

output = os.environ.get("GP015_ASK_FORGE_TRACE_ATTESTATION_OUTPUT", "").strip()
if output:
    Path(output).write_text(json.dumps(attestation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    check("attestation JSON written when requested", Path(output).is_file())

passed = sum(1 for _, ok in checks if ok)
print(f"RESULT: GP-015-ASK-FORGE-OUTPUT-LIVE-MATH-TRACE-SURFACE_BEHAVIOR {'PASS' if passed == len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed == len(checks) else 1)
