#!/usr/bin/env python3
"""Static and live verification for GP-005 capability service contracts.

Run:
    .venv/bin/python scripts/general_pipeline_capability_services_build_gp005_verify.py --forge-root "$HOME/forge"

Verification is read-only: imports and answers occur in memory; source is scanned
for forbidden writes and for execution-boundary enforcement.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()
    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

    gp_dir = forge_root / "rmc_engine_v1" / "general_pipeline"
    required = [
        "capability_registry.py",
        "capability_services.py",
        "domains.py",
        "source_compiler.py",
        "manifest_builder.py",
        "governed_gate.py",
        "pipeline.py",
        "gp004_production_reground.py",
        "gp005_capability_services.py",
    ]

    passed = 0
    failed = 0
    out = []

    def check(name: str, condition: bool) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            out.append(f"PASS  {name}")
        else:
            failed += 1
            out.append(f"FAIL  {name}")

    for filename in required:
        check(f"module present: rmc_engine_v1/general_pipeline/{filename}", (gp_dir / filename).is_file())

    try:
        from rmc_engine_v1.general_pipeline import learn_and_answer
        from rmc_engine_v1.general_pipeline import gp005_capability_services as gp5
        from rmc_engine_v1.general_pipeline.capability_services import (
            all_service_contracts,
            service_boundary_contract,
            service_registry_hash,
        )
        state = gp5.activate()
        imported = True
    except Exception as exc:
        imported = False
        out.append(f"FAIL  imports + GP-005 activation against real engine ({exc})")
        failed += 1
    else:
        check("imports + GP-005 activation against real MEA engine", imported)

    if imported:
        services = all_service_contracts()
        check("four service contracts available", len(services) == 4)
        check("service registry hash stable", state["service_registry_hash"] == service_registry_hash())
        check("services are bound to registered capability hashes", all(bool(s.capability_contract_hash) for s in services))
        check("services are Forge-owned", all(s.authority_owner == "forge" for s in services))
        check("services cannot write or mint", all(not s.memory_write_allowed and not s.identity_write_allowed and not s.contribution_economy_write_allowed and not s.ct_mint_allowed for s in services))
        check("services cannot render or Echo-approve", all(not s.render_output_allowed and not s.echo_approval_allowed for s in services))

        algebra = "Elementary algebra equation solve unknown variable both sides isolate."
        solved = learn_and_answer(algebra, "a", "solve 11x + 17 = 105 for x")
        check("service-mediated equation answers", solved.status == "ANSWERED" and "8" in (solved.answer_text or ""))
        check("trace stores service contract", "capability_service_contract" in solved.trace)
        check("trace stores canonical request", "capability_invocation_request" in solved.trace)
        check("trace stores execution receipt", "capability_execution_receipt" in solved.trace)
        check("execution receipt precedes existing Echo approval", solved.trace.get("capability_execution_receipt", {}).get("execution_status") == "VERIFIED_EXECUTION_COMPLETE" and solved.trace.get("echo", {}).get("approved_output") is True)
        open_facts = solved.trace["open_manifest"]["known_facts"]
        check("MEA open manifest identifies service boundary", any(str(f).startswith("capability_service = svc.forge.") for f in open_facts))
        check("MEA open manifest retains Forge invocation policy", "execution_authority = forge_pipeline_bound_request_only" in open_facts)

        boundary = service_boundary_contract()
        check("boundary: in memory only", boundary["in_memory_only"] is True)
        check("boundary: no memory write", boundary["writes_memory"] is False)
        check("boundary: no Identity Vault write", boundary["writes_identity_vault"] is False)
        check("boundary: no Contribution Economy write", boundary["writes_contribution_economy"] is False)
        check("boundary: no CT mint", boundary["mints_ct"] is False)
        check("boundary: no corpus ingestion", boundary["adds_corpus_ingestion"] is False)
        check("boundary: no new problem domain", boundary["adds_new_domain"] is False)
        check("boundary: GP-005 historical no-dependency origin retained", boundary["third_party_dependencies_added_during_original_gp005"] == [])
        check("boundary: authorized active equation and capacity tools truthfully declared", boundary["third_party_dependencies_added"] == ["lark==1.3.1", "sympy==1.14.0", "mpmath==1.3.0", "Pint==0.25.3", "flexcache==0.3", "flexparser==0.4", "platformdirs==4.10.0"] and boundary["third_party_parser_imported"] is True and boundary["third_party_solver_imported"] is True)

    combined = "\n".join((gp_dir / name).read_text(encoding="utf-8") for name in required)
    forbidden_runtime_tokens = [
        "@app.route",
        "import flask",
        "from flask",
        "import chromadb",
        "chromadb.",
        ".add_documents(",
        "requests.post",
        "requests.get",
        "subprocess.",
        "os.system",
        "open(",
        "Path.write_text",
        "Path.write_bytes",
    ]
    for token in forbidden_runtime_tokens:
        check(f"boundary source has no forbidden runtime token {token!r}", token not in combined)

    pipeline_text = (gp_dir / "pipeline.py").read_text(encoding="utf-8")
    service_text = (gp_dir / "capability_services.py").read_text(encoding="utf-8")
    source_text = (gp_dir / "source_compiler.py").read_text(encoding="utf-8")
    check("answering pipeline invokes Forge-owned service boundary", "execute_registered_capability(parsed)" in pipeline_text)
    check("answering pipeline does not directly call domain executor", "domain.execute(parsed)" not in pipeline_text)
    check("service boundary is the controlled executor callsite", "solution = domain.execute(parsed)" in service_text)
    check("source compiler cannot create service authority", "CapabilityServiceContract" not in source_text and "service_contract" not in source_text)

    print("\n".join(out))
    total = passed + failed
    result_status = "PASS" if failed == 0 else "FAIL"
    print("\nBUILD_ID: GENERAL-PIPELINE-CAPABILITY-SERVICE-CONTRACTS-BUILD-GP-005")
    print("SCHEMA_VERSION: general_pipeline_capability_services_v1_build_gp005")
    print(f"RESULT: GENERAL-PIPELINE-CAPABILITY-SERVICE-CONTRACTS-BUILD-GP-005_VERIFY {result_status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
