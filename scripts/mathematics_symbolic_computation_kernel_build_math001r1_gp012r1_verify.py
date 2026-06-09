#!/usr/bin/env python3
"""MATH-001R1 / GP-012R1 structural and governance verifier."""
from __future__ import annotations
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.dependency_registry import active_runtime_dependency_ids, dependency_boundary_contract
from rmc_engine_v1.general_pipeline.symbolic_math_ast import SUPPORTED_OPERATION_FAMILIES, symbolic_math_ast_boundary
from rmc_engine_v1.general_pipeline.symbolic_math_kernel import REQUIRED_DELIVERY_AUTHORITY, symbolic_math_kernel_boundary
from rmc_engine_v1.general_pipeline.symbolic_math_runtime_attestation_math001r1 import attest_symbolic_math_kernel

checks = []
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

gp = FORGE / "rmc_engine_v1" / "general_pipeline"
required = ["symbolic_math_ast.py", "symbolic_math_worker.py", "symbolic_math_kernel.py", "symbolic_math_runtime_attestation_math001r1.py", "gp012r1_symbolic_math_computation_capability.py"]
check("all corrected symbolic runtime modules exist", all((gp / name).is_file() for name in required))
worker = (gp / "symbolic_math_worker.py").read_text(encoding="utf-8")
kernel = (gp / "symbolic_math_kernel.py").read_text(encoding="utf-8")
ast_text = (gp / "symbolic_math_ast.py").read_text(encoding="utf-8")
check("worker imports backend only after resource-limit application", worker.index("_apply_resource_limits(policy)") < worker.index("import sympy as sp"))
check("worker invokes CPU resource policy", "resource.RLIMIT_CPU" in worker)
check("worker invokes memory resource policy", "resource.RLIMIT_AS" in worker)
check("worker invokes output resource policy", "resource.RLIMIT_FSIZE" in worker)
check("kernel invokes isolated worker subprocess", "subprocess.run" in kernel and "symbolic_math_worker.py" in kernel)
check("AST boundary uses no free-form mathematical input", 'raw_mathematical_source_accepted": False' in ast_text)
for token in ("eval" + "(", "exec" + "(", "symp" + "ify(", "parse_" + "expr("):
    check(f"operational source excludes forbidden callable {token}", token not in (worker + kernel + ast_text))
check("kernel contains no rejected substitute Echo authority", "ECHO_STYLE_SYMBOLIC_DELIVERY_AUTHORIZED" not in kernel and "SymbolicMathDeliveryAuthorizationReceipt" not in kernel)
check("kernel cannot return delivered status", '"status": "DELIVERED"' not in kernel)
check("kernel expressly holds computation pending governance", "COMPUTED_VERIFIED_PENDING_DOWNSTREAM_GOVERNANCE" in kernel and "SYMBOLIC_MATH_COMPUTED_PENDING_MANIFEST_V2_ECHO" in kernel)

deps = active_runtime_dependency_ids("symbolic_math")
check("symbolic math dependency path is bounded", len(deps) == 4)
check("symbolic math dependency path binds SymPy", any("sympy" in item for item in deps))
dep_boundary = dependency_boundary_contract()
check("dependency boundary reports safe computation socket", dep_boundary["manifest_first_symbolic_math_capability_active"] is True and dep_boundary["symbolic_math_safe_ast_only"] is True and dep_boundary["symbolic_math_computation_only"] is True)
check("dependency boundary denies parallel delivery authority", dep_boundary["symbolic_math_delivery_authority_added"] is False and dep_boundary["symbolic_math_actual_echo_substitution_added"] is False)
ast_boundary = symbolic_math_ast_boundary()
check("AST boundary declares twenty-six families", ast_boundary["supported_operation_family_count"] == 26)
check("AST boundary declares no side effects", not any(ast_boundary[key] for key in ("writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers", "ingests_corpus")))
kernel_boundary = symbolic_math_kernel_boundary()
check("kernel reports pre-import resource limits", kernel_boundary["resource_limits_applied_before_backend_import"] is True)
check("kernel reports no language compiler or raw source", kernel_boundary["natural_language_compiler_added"] is False and kernel_boundary["raw_mathematical_source_accepted"] is False)
check("kernel reports computation only and no delivery", kernel_boundary["computation_only_capability"] is True and kernel_boundary["direct_user_facing_delivery_authorized"] is False and kernel_boundary["render_allowed"] is False)
check("kernel retains existing downstream authority", kernel_boundary["required_delivery_authority"] == REQUIRED_DELIVERY_AUTHORITY)
attestation = attest_symbolic_math_kernel()
receipt = attestation["attestation_receipt"]
check("full computation attestation passed", attestation["status"] == "MATH001R1_SYMBOLIC_COMPUTATION_KERNEL_ATTESTED_26_OF_26_PENDING_GOVERNANCE")
check("full computation attestation covered all families", tuple(receipt["computed_operation_families"]) == SUPPORTED_OPERATION_FAMILIES)
check("full computation attestation bound all execution receipts", len(receipt["execution_receipt_hashes"]) == 26 and all(len(value) == 64 for value in receipt["execution_receipt_hashes"]))
check("full computation attestation bound all pending receipts", len(receipt["pending_governance_receipt_hashes"]) == 26 and all(len(value) == 64 for value in receipt["pending_governance_receipt_hashes"]))
check("attestation never claims Echo or delivery", receipt["delivery_authorized"] is False and receipt["actual_echo_invoked"] is False)
check("attestation remains side-effect-free", not any(receipt[key] for key in ("writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers", "ingests_corpus")))

passed = sum(1 for _, outcome in checks if outcome)
print(f"RESULT: MATH-001R1-GP-012R1-SYMBOLIC-MATHEMATICS-COMPUTATION-KERNEL_VERIFY {'PASS' if passed == len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed == len(checks) else 1)
