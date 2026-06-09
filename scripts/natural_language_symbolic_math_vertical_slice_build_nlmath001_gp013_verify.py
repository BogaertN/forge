#!/usr/bin/env python3
"""NL-MATH-001 / GP-013 structural/governance verification."""
from __future__ import annotations
from pathlib import Path
import sys

FORGE = Path(__file__).resolve().parents[1]
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.gp013_natural_language_symbolic_math_vertical_slice import activate
from rmc_engine_v1.general_pipeline.manifest_contract_v2 import (
    SYMBOLIC_MATH_TOOL_EVIDENCE_VERIFICATION,
    manifest_contract_v2_boundary,
)

checks = []
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

required = (
    "rmc_engine_v1/general_pipeline/symbolic_math_language_compiler.py",
    "rmc_engine_v1/general_pipeline/symbolic_math_mea_evidence_bridge.py",
    "rmc_engine_v1/general_pipeline/symbolic_math_rmc_delivery.py",
    "rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py",
    "rmc_engine_v1/general_pipeline/gp013_natural_language_symbolic_math_vertical_slice.py",
    "scripts/test_natural_language_symbolic_math_vertical_slice_build_nlmath001_gp013.py",
    "scripts/natural_language_symbolic_math_vertical_slice_build_nlmath001_gp013_verify.py",
    "scripts/README_natural_language_symbolic_math_vertical_slice_build_nlmath001_gp013.md",
    "scripts/MEA_NATURAL_LANGUAGE_SYMBOLIC_MATH_VERTICAL_SLICE_BUILD_NLMATH001_GP013_DELIVERY_MANIFEST.json",
)
for rel in required:
    check(f"module present: {rel}", (FORGE / rel).is_file())

state = activate()
check("activation identifies the vertical slice", state["active"] is True and "NL-MATH-001-GP-013" in state["build_id"])
check("activation retains actual Echo delivery requirement", state["actual_echo_delivery_required"] is True)
check("activation adds no corpus/LLM/write/economy authority", not any(state[key] for key in ("corpus_ingestion_added", "calls_llm", "writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers")))

boundary = state["vertical_slice"]
check("language layer covers coherent first eight-family slice", boundary["supported_language_operation_family_count"] == 8)
check("installed 26-family computation kernel remains underlying tool", boundary["underlying_math_kernel_operation_family_count"] == 26)
check("new slice does not mutate legacy router", boundary["registers_legacy_domain_router_change"] is False)
check("new slice does not add route or UI", boundary["adds_route_or_ui"] is False)
check("new slice sends no raw user text to SymPy", boundary["raw_user_text_sent_to_sympy"] is False)

manifest_boundary = manifest_contract_v2_boundary()
check("Manifest Contract v2 declares symbolic tool evidence support", manifest_boundary["symbolic_math_verified_tool_evidence_supported"] is True)
check("Manifest Contract v2 still requires actual Echo", manifest_boundary["symbolic_math_delivery_requires_actual_echo"] is True)
check("symbolic verification method has explicit identity", SYMBOLIC_MATH_TOOL_EVIDENCE_VERIFICATION == "symbolic_math_typed_ast_verified_tool_evidence")

production_files = [
    FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_language_compiler.py",
    FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_mea_evidence_bridge.py",
    FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_rmc_delivery.py",
    FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py",
    FORGE / "rmc_engine_v1/general_pipeline/gp013_natural_language_symbolic_math_vertical_slice.py",
]
combined = "\n".join(path.read_text(encoding="utf-8") for path in production_files)
for forbidden in (
    "eval(", "exec(", "sympify", "parse_expr", "requests.", "subprocess.", "os.system",
    "sqlite3.connect", "chromadb", ".write_text(", ".write_bytes(", "open(",
):
    check(f"new production layer contains no prohibited executable token {forbidden!r}", forbidden not in combined)
check("production language compiler calls typed manifest not SymPy", "SymbolicMathOperationManifest(" in (FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_language_compiler.py").read_text(encoding="utf-8"))
check("delivery layer calls installed actual Echo", "validate_and_approve_v2(" in (FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_rmc_delivery.py").read_text(encoding="utf-8"))
check("vertical slice calls installed final delivery receipt", "finalize_echo_delivery(" in (FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py").read_text(encoding="utf-8"))

vertical_source = (FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py").read_text(encoding="utf-8")
delivery_source = (FORGE / "rmc_engine_v1/general_pipeline/symbolic_math_rmc_delivery.py").read_text(encoding="utf-8")
check("vertical source binds kernel evidence before MEA seal", "compute_symbolic_math_evidence(compiled, open_manifest)" in vertical_source and "seal_symbolic_math_problem_manifest(open_manifest, solution, evidence, gate)" in vertical_source)
check("vertical source compiles RMC meaning only after MEA seal", vertical_source.index("seal_symbolic_math_problem_manifest") < vertical_source.index("compile_symbolic_math_meaning"))
execution_body = vertical_source[vertical_source.index("def answer_symbolic_math_language_request"):]
check("vertical source reaches actual delivery receipt after Echo", execution_body.index("validate_symbolic_math_echo_v2") < execution_body.index("finalize_echo_delivery"))
check("renderer source invokes actual existing Echo validation", "validate_and_approve_v2(meaning, rendered_text, contract)" in delivery_source)
check("renderer source prevents corpus or LLM additions", '"corpus_ingestion_added": False' in delivery_source and '"calls_llm": False' in delivery_source)

passed = sum(1 for _, value in checks if value)
print(f"RESULT: NL-MATH-001-GP-013-NATURAL-LANGUAGE-SYMBOLIC-EXPRESSION-TO-ECHO_VERTICAL_SLICE_VERIFY {'PASS' if passed == len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed == len(checks) else 1)
