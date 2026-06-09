#!/usr/bin/env python3
"""NL-MATH-001 / GP-013 behavior verification: natural-language math through actual Echo delivery."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.symbolic_math_language_compiler import compile_symbolic_math_request
from rmc_engine_v1.general_pipeline.symbolic_math_language_vertical_slice import (
    answer_symbolic_math_language_request,
    attest_natural_language_symbolic_math_vertical_slice,
    natural_language_symbolic_math_vertical_slice_boundary,
)

checks = []
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

# One production attestation run executes all eight language-enabled operation
# families through typed MATH-001R1 evidence, MEA seal, RMC meaning, actual Echo
# and DeliveryAuthorizationReceiptV2.
attestation = attest_natural_language_symbolic_math_vertical_slice()
rows = attestation["rows"]
families = {row["operation_family"] for row in rows}
expected_families = {
    "simplification", "expansion", "factoring", "trigonometric_simplification",
    "trigonometric_expansion", "differentiation", "integration", "limits",
}
check("attestation delivers eight supported cases", attestation["supported_attestation_count"] == 8)
check("attestation covers every language-enabled family exactly once", families == expected_families and len(rows) == len(families))
check("attestation contains unsupported mixed language", attestation["unsupported_mixed_language_contained"] is True)
check("attestation adds no corpus, LLM or side effects", not any(attestation[key] for key in ("corpus_used", "llm_used", "writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers")))
for family in sorted(expected_families):
    row = next((item for item in rows if item["operation_family"] == family), None)
    check(f"{family} has a sealed Echo-delivery attestation row", row is not None and len(row["delivery_authorization_v2_hash"]) == 64)
    check(f"{family} records declared verification strength", row is not None and row["verification_strength"] in {"EXACT_SYMBOLIC_EQUIVALENCE", "EXACT_SUBSTITUTION_VERIFICATION", "DETERMINISTIC_ENGINE_REPLAY", "STRUCTURAL_SYMBOLIC_RECEIPT"})

# Natural phrasing compiles without launching a duplicate computation.
natural_compiled = compile_symbolic_math_request("Find the derivative of x cubed plus 4 x with respect to x.")
check("natural word-form derivative compiles safely", natural_compiled.operation_family == "differentiation")
check("natural word-form derivative emits typed AST manifest", natural_compiled.operation_manifest.manifest_hash() == natural_compiled.compiler_receipt.operation_manifest_hash)

# These are refused before any typed computation is allowed.
negative = (
    "Explain quantum gravity and then factor x^2 - 9.",
    "Differentiate os.system(x) with respect to x.",
    "Compute a matrix eigen analysis of [[1,2],[3,4]].",
    "Differentiate x^2 with respect to x and publish it.",
    "Factor x^2 - 9 and publish it.",
)
for question in negative:
    result = answer_symbolic_math_language_request(question)
    check(f"unsupported or unsafe language remains contained: {question[:24]}", result.status == "REFUSED_UNLEARNED")
    check(f"contained result cannot deliver: {question[:24]}", "delivery_authorization_v2" not in result.trace)

compiled = compile_symbolic_math_request("Factor x^2 - 9.")
check("language compiler emits typed operation manifest", compiled.operation_manifest.capability_id == "cap.math.symbolic_math.v1")
check("language compiler attests full input", compiled.compiler_receipt.full_input_consumed is True)
check("language compiler never sends raw text to SymPy", compiled.compiler_receipt.raw_text_sent_to_sympy is False)
check("language compiler adds no corpus or LLM", compiled.compiler_receipt.corpus_used is False and compiled.compiler_receipt.llm_used is False)

boundary = natural_language_symbolic_math_vertical_slice_boundary()
check("boundary uses actual delivery spine", boundary["actual_echo_and_delivery_authorization_v2_required"] is True)
check("boundary does not repurpose preview renderer", boundary["repurposes_historical_renderer_preview_lane"] is False)
check("boundary adds no corpus or writes", not any(boundary[key] for key in ("corpus_ingestion_added", "calls_llm", "writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers")))

attestation_output = os.environ.get("NLMATH001_GP013_ATTESTATION_OUTPUT", "").strip()
if attestation_output:
    output_path = Path(attestation_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(attestation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    check("requested live attestation evidence file written", output_path.is_file())

passed = sum(1 for _, value in checks if value)
print(f"RESULT: NL-MATH-001-GP-013-NATURAL-LANGUAGE-SYMBOLIC-EXPRESSION-TO-ECHO_VERTICAL_SLICE_BEHAVIOR {'PASS' if passed == len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed == len(checks) else 1)
