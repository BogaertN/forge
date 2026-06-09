#!/usr/bin/env python3
"""MATH-001R1 / GP-012R1 behavior verification: computation-only symbolic kernel."""
from __future__ import annotations
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.gp012r1_symbolic_math_computation_capability import activate
from rmc_engine_v1.general_pipeline.symbolic_math_ast import SUPPORTED_OPERATION_FAMILIES
from rmc_engine_v1.general_pipeline.symbolic_math_kernel import (
    SUCCESS_STATUS, REQUIRED_DELIVERY_AUTHORITY,
    execute_symbolic_math_operation, symbolic_math_service_contract,
)
from rmc_engine_v1.general_pipeline.symbolic_math_runtime_attestation_math001r1 import canonical_attestation_manifests

checks = []
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

state = activate()
check("MATH-001R1 capability activation is exact", state["capability_id"] == "cap.math.symbolic_math.v1" and state["installation_exact"] is True)
check("SymPy remains the active engine", state["installed_versions"]["sympy"] == "1.14.0")
check("mpmath support remains exact", state["installed_versions"]["mpmath"] == "1.3.0")
check("all twenty-six families are declared", len(SUPPORTED_OPERATION_FAMILIES) == 26)
check("operation family ordering is canonical", SUPPORTED_OPERATION_FAMILIES[0] == "exact_evaluation" and SUPPORTED_OPERATION_FAMILIES[-1] == "substitution_verification")
service = symbolic_math_service_contract()
check("service is bound to symbolic capability", service["capability_id"] == "cap.math.symbolic_math.v1")
check("service is worker isolated", service["worker_policy"] == "ISOLATED_RESOURCE_LIMITS_APPLIED_BEFORE_SYMPY_IMPORT")
check("service does not add natural-language compilation", service["natural_language_compiler_added"] is False)
check("service carries SymPy dependency binding", any("sympy" in item for item in service["active_dependency_record_ids"]))
check("service is computation only", service["computation_only_capability"] is True)
check("service cannot authorize direct delivery", service["direct_user_facing_delivery_authorized"] is False and service["render_allowed"] is False)
check("service retains exclusive downstream authority", service["required_delivery_authority"] == REQUIRED_DELIVERY_AUTHORITY)
check("service denies persistence and economy effects", not any(service[key] for key in ("writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers", "ingests_corpus")))

sample = canonical_attestation_manifests()
check("canonical sample manifest count is complete", len(sample) == 26)
check("canonical samples map one-to-one to families", tuple(item.operation_family for item in sample) == SUPPORTED_OPERATION_FAMILIES)
exact = execute_symbolic_math_operation(sample[0])
check("exact arithmetic computes pending governance", exact["status"] == SUCCESS_STATUS)
check("exact arithmetic computes through SymPy", exact.get("computed_artifact", {}).get("display_text") == "7/3")
check("execution receipt binds backend", exact.get("execution_receipt", {}).get("backend") == "sympy==1.14.0")
check("pending receipt exists instead of delivery receipt", exact.get("pending_governance_receipt", {}).get("status") == "SYMBOLIC_MATH_COMPUTED_PENDING_MANIFEST_V2_ECHO" and "delivery_authorization_receipt" not in exact)
check("computed artifact is not render or delivery authorized", exact["delivery_authorized"] is False and exact["render_allowed"] is False and exact["actual_echo_invoked"] is False)
check("computed artifact retains real delivery authority requirement", exact["required_delivery_authority"] == REQUIRED_DELIVERY_AUTHORITY)
blocked = execute_symbolic_math_operation({"operation_id": "unsafe.raw", "operation_family": "simplification", "operands": {"value": {"node": "raw", "text": "x"}}})
check("untyped raw node is contained", blocked["status"] == "CONTAINED" and blocked["non_delivery_receipt"]["reason_code"] == "MANIFEST_OR_AST_BOUNDARY_REFUSED")
blocked_function = execute_symbolic_math_operation({"operation_id": "unsafe.function", "operation_family": "simplification", "operands": {"value": {"node": "function", "name": "not_allowed", "args": [{"node": "integer", "value": 1}]}}})
check("unapproved function is contained", blocked_function["status"] == "CONTAINED")
check("containment never delivers or renders", blocked_function["non_delivery_receipt"]["result_delivered"] is False and blocked_function["non_delivery_receipt"]["render_allowed"] is False)

passed = sum(1 for _, outcome in checks if outcome)
print(f"RESULT: MATH-001R1-GP-012R1-SYMBOLIC-MATHEMATICS-COMPUTATION-KERNEL_BEHAVIOR {'PASS' if passed == len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed == len(checks) else 1)
