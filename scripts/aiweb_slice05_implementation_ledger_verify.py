#!/usr/bin/env python3
"""
AIWEB Slice 5R1 verifier.

Verifies that the installed Slice 5R1 scaffold is present, syntactically valid,
locally deterministic, clean of raw unsafe authority text, and bounded to the
intended Slice 5 scaffold paths.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    sys.path.insert(0, str(repo))

    from aiweb_implementation_ledger_scaffold.verify import (
        REQUIRED_FILES,
        compile_python_file,
        forbidden_authority_terms,
        git_status_is_slice05_only,
        has_forbidden_authority_phrases,
        has_forbidden_imports,
        required_files_exist,
    )
    from aiweb_implementation_ledger_scaffold import (
        LEDGER_BLOCKED_AUTHORITIES,
        build_cycle_update_record,
        build_ledger_continuity_record,
        unsafe_phrase,
        validate_cycle_update_record,
        validate_ledger_continuity_record,
    )

    passes = []
    failures = []

    def check(condition: bool, message: str) -> None:
        if condition:
            passes.append("PASS - " + message)
        else:
            failures.append("FAIL - " + message)

    print("============================================================")
    print("AIWEB SLICE 5R1 IMPLEMENTATION LEDGER SCAFFOLD VERIFIER")
    print("============================================================")
    print(f"Target repo: {repo}")

    check(str(repo) == "/home/nic/forge", "target repo is exactly /home/nic/forge")
    check(repo.is_dir(), "target repo directory exists")
    check((repo / ".git").is_dir(), "target repo is a git repository")

    ok, messages = required_files_exist(repo)
    for message in messages:
        check(message.startswith("required file exists:"), message)

    python_files = [
        "aiweb_implementation_ledger_scaffold/__init__.py",
        "aiweb_implementation_ledger_scaffold/ledger.py",
        "aiweb_implementation_ledger_scaffold/cycle.py",
        "aiweb_implementation_ledger_scaffold/verify.py",
        "scripts/test_aiweb_slice05_implementation_ledger_scaffold.py",
        "scripts/aiweb_slice05_implementation_ledger_verify.py",
    ]

    for rel in python_files:
        path = repo / rel
        if path.exists():
            valid, msg = compile_python_file(path)
            check(valid, msg)
            valid, msg = has_forbidden_imports(path)
            check(valid, msg)
            valid, msg = has_forbidden_authority_phrases(path)
            check(valid, msg)

    check(len(forbidden_authority_terms()) >= 10, "raw unsafe phrase catalog is assembled at runtime")

    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--short"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    status_lines = status.stdout.splitlines()
    valid, msg = git_status_is_slice05_only(repo, status_lines)
    check(valid, msg)

    ledger = build_ledger_continuity_record(
        ledger_name="AIWEB_IMPLEMENTATION_LEDGER_v1",
        cycle_id="AIWEB-SLICE-05R1",
        slice_id="SLICE-05R1",
        source_repo="/home/nic/forge",
        source_branch="main",
        source_commit="f4479882840935a5e916bcbec94e07f902b022e6",
        working_tree_status="clean",
        packet_identities=["source_authority_packet", "repair_design_record", "repair_patch_packet"],
        source_freshness="fresh_source_authority_packet_inspected",
        implementation_cycle_status="verified",
        inherited_tests=["slice01", "slice02", "slice03", "slice04"],
        inherited_verifiers=["slice01", "slice02", "slice03", "slice04"],
        created_utc="2026-06-16T00:00:00Z",
    )
    valid, _ = validate_ledger_continuity_record(ledger)
    check(valid, "sample ledger continuity record validates")

    check("live_ledger_write" in LEDGER_BLOCKED_AUTHORITIES, "live ledger write remains blocked")
    check("external_google_drive_update" in LEDGER_BLOCKED_AUTHORITIES, "external Google Drive update remains blocked")
    check("production_readiness" in LEDGER_BLOCKED_AUTHORITIES, "production readiness remains blocked")
    check("release_authorization" in LEDGER_BLOCKED_AUTHORITIES, "release authorization remains blocked")

    bad_ledger = dict(ledger)
    bad_ledger["writes_google_drive"] = True
    valid, _ = validate_ledger_continuity_record(bad_ledger)
    check(not valid, "bad Google Drive writing ledger record fails validation")

    bad_ledger = dict(ledger)
    bad_ledger["notes"] = unsafe_phrase("prod_dash_ready")
    valid, _ = validate_ledger_continuity_record(bad_ledger)
    check(not valid, "prod readiness ledger overclaim fails validation")

    cycle = build_cycle_update_record(
        cycle_id="AIWEB-SLICE-05R1",
        cycle_title="Implementation Ledger Continuity and Cycle Update Scaffold Repair",
        slice_id="SLICE-05R1",
        slice_name="Implementation Ledger Continuity and Cycle Update Scaffold Repair",
        cycle_status="verified_passed",
        source_commit="f4479882840935a5e916bcbec94e07f902b022e6",
        source_branch="main",
        working_tree_status="clean",
        source_packet="AIWEB_SLICE05_NARROW_SOURCE_AUTHORITY_PACKET_20260616_222506_UTC.tar.gz",
        patch_design_record="AIWEB_SLICE05R1_REPAIR_PATCH_DESIGN_RECORD_20260616_UTC.tar.gz",
        patch_packet="AIWEB_SLICE05R1_IMPLEMENTATION_LEDGER_SCAFFOLD_REPAIR_PATCH_PACKET_20260616_UTC.tar.gz",
        result_packet="AIWEB_SLICE05R1_IMPLEMENTATION_LEDGER_SCAFFOLD_REPAIR_RESULT_PACKET_PENDING.tar.gz",
        result_packet_sha256="pending_after_install",
        verifier_outputs=["slice05r1_verifier_output.txt"],
        behavior_test_outputs=["slice05r1_behavior_test_output.txt"],
        created_utc="2026-06-16T00:00:00Z",
    )
    valid, _ = validate_cycle_update_record(cycle)
    check(valid, "sample cycle update record validates")

    for mutation, description in (
        ({"claims_production_ready": True}, "prod readiness cycle claim fails"),
        ({"authorizes_release": True}, "release grant cycle claim fails"),
        ({"authorizes_public_delivery": True}, "public delivery cycle claim fails"),
        ({"updates_live_ledger": True}, "live ledger update cycle claim fails"),
        ({"cycle_status": "done"}, "uncontrolled cycle status fails"),
        ({"notes": unsafe_phrase("gp014_dash_sup")}, "GP-014 supersession text fails"),
        ({"notes": unsafe_phrase("llm_auth_on")}, "LLM authority text fails"),
    ):
        bad = dict(cycle)
        bad.update(mutation)
        valid, _ = validate_cycle_update_record(bad)
        check(not valid, description)

    print("PASSES:")
    for item in passes:
        print("  " + item)
    print("FAILURES:")
    for item in failures:
        print("  " + item)

    if failures:
        print("VERDICT: FAIL - Slice 5R1 implementation ledger scaffold verifier failed")
        return 1

    print("VERDICT: PASS - Slice 5R1 implementation ledger scaffold verifier passed within repair scope")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
