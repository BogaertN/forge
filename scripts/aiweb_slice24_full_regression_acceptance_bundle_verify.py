#!/usr/bin/env python3
"""CLI verifier for Slice 24 full regression acceptance bundle scaffold."""

from pathlib import Path
import argparse
import json

# Ensure direct script execution can import the repo-root package.
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_full_regression_acceptance_bundle_scaffold.runner import run_acceptance_bundle
from aiweb_full_regression_acceptance_bundle_scaffold.verify import verify_slice24_boundary


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Slice 24 full regression acceptance bundle scaffold.")
    parser.add_argument("repo", nargs="?", default=".", help="Forge repository root")
    parser.add_argument("--run-acceptance", action="store_true", help="Execute the required active Slice 1-23 command matrix. Requires clean context for acceptance.")
    parser.add_argument("--result-dir", default="", help="Directory where command/result records should be written when --run-acceptance is used.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    result = verify_slice24_boundary(repo)

    print("AIWEB SLICE 24 FULL REGRESSION ACCEPTANCE BUNDLE VERIFIER")
    print("slice=Slice 24")
    print("title=Full Regression and Acceptance Bundle Scaffold")
    print(f"context_label={result.context_label}")
    print(f"checked_file_count={len(result.checked_files)}")

    if result.failures:
        print("FAILURES:")
        for failure in result.failures:
            print(f"- {failure}")
        print("VERDICT: FAIL")
        return 1

    if args.run_acceptance:
        target_result_dir = Path(args.result_dir).resolve() if args.result_dir else repo / "slice24_acceptance_results"
        acceptance = run_acceptance_bundle(repo, result_dir=target_result_dir, require_clean_context=True, execute_required_commands=True)
        print(f"acceptance_result_path={target_result_dir / 'slice24_acceptance_result.json'}")
        print(f"required_command_count={acceptance['summary']['required_command_count']}")
        print(f"executed_command_count={acceptance['summary']['executed_command_count']}")
        print(f"passed_command_count={acceptance['summary']['passed_command_count']}")
        print(f"failed_command_count={acceptance['summary']['failed_command_count']}")
        print(f"source_guard_passed={acceptance['summary']['source_guard_passed']}")
        print(f"external_context_passed={acceptance['summary']['external_context_passed']}")
        print(f"accepted={acceptance['accepted']}")
        print(f"receipt_id={acceptance['receipt']['receipt_id']}")
        print(f"receipt_verdict={acceptance['receipt']['verdict']}")
        if not acceptance["accepted"]:
            print("VERDICT: FAIL_CLOSED")
            return 2
        print("VERDICT: PASS_FULL_ACCEPTANCE")
        return 0

    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
