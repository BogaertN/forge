#!/usr/bin/env python3
"""Behavior test for Slice 6 scanner scaffold."""

from __future__ import annotations

import sys
from pathlib import Path


def _add_repo_to_path(repo: Path) -> None:
    repo_text = str(repo.resolve())
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)


def _join(parts):
    return "".join(parts)


def main() -> int:
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    _add_repo_to_path(repo)

    from aiweb_authority_scanner_scaffold.catalog import (
        assembled_unsafe_catalog,
        safe_demo_text,
        scanner_scope_record,
        unsafe_demo_text,
    )
    from aiweb_authority_scanner_scaffold.scanner import scan_paths, scan_text
    from aiweb_authority_scanner_scaffold.verify import verify_slice06

    passes = []
    failures = []

    def check(name: str, condition: bool) -> None:
        if condition:
            passes.append(name)
        else:
            failures.append(name)

    scope = scanner_scope_record()
    check("scope is scanner-only", scope.get("scanner_only") is True)
    check("scope has no runtime effect", scope.get("runtime_effect") == "none")
    check("scope has no dependency change", scope.get("dependency_change") == "none")

    catalog = assembled_unsafe_catalog()
    check("unsafe catalog has entries", len(catalog) >= 20)
    check("unsafe catalog assembled at runtime", any(item.phrase == _join(("production", "-", "ready")) for item in catalog))

    safe_report = scan_text(safe_demo_text(), path_label="safe_demo")
    check("safe demo passes scanner", safe_report.passed)

    unsafe_report = scan_text(unsafe_demo_text(), path_label="unsafe_demo")
    categories = {finding.category for finding in unsafe_report.findings}
    check("unsafe demo produces findings", unsafe_report.finding_count >= 5)
    check("public claim overreach detected", "public_claim_overreach" in categories)
    check("baseline failure-path overclaim detected", "baseline_failure_path_overclaim" in categories)
    check("model or opaque authority detected", "model_or_opaque_authority" in categories)
    check("retrieval or similarity authority detected", "retrieval_or_similarity_authority" in categories)
    check("stored material or action overreach detected", "stored_material_or_action_overreach" in categories)

    sample_one = _join(("release", " ", "authorized"))
    sample_two = _join(("semantic", " ", "similarity", " ", "authority"))
    combined_report = scan_text(f"{sample_one}\\n{sample_two}", path_label="combined")
    check("multi-line unsafe sample detects two findings", combined_report.finding_count == 2)

    source_report = scan_paths([
        repo / "aiweb_authority_scanner_scaffold/__init__.py",
        repo / "aiweb_authority_scanner_scaffold/catalog.py",
        repo / "aiweb_authority_scanner_scaffold/scanner.py",
        repo / "aiweb_authority_scanner_scaffold/verify.py",
        repo / "scripts/test_aiweb_slice06_authority_scanner_scaffold.py",
        repo / "scripts/aiweb_slice06_authority_scanner_verify.py",
        repo / "scripts/README_aiweb_slice06_authority_scanner_scaffold.md",
    ])
    check("scanner does not flag Slice 6 committed source", source_report.finding_count == 0)

    verifier_passes, verifier_failures = verify_slice06(repo)
    check("verifier sample checks pass", len(verifier_failures) == 0 and len(verifier_passes) > 0)

    print("=" * 60)
    print("AIWEB SLICE 6 UNIFIED AUTHORITY SCANNER SCAFFOLD BEHAVIOR TEST")
    print("=" * 60)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")

    if failures:
        print("VERDICT: FAIL - behavior test failed")
        return 1

    print("VERDICT: PASS - behavior test passed within Slice 6 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
