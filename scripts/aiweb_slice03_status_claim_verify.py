#!/usr/bin/env python3
"""Repository verifier for AI.Web Slice 3 controlled status/claim scaffold."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: aiweb_slice03_status_claim_verify.py /home/nic/forge")
        return 2

    repo = Path(sys.argv[1]).resolve()
    passes = []
    failures = []

    def check(name: str, condition: bool) -> None:
        if condition:
            passes.append(name)
        else:
            failures.append(name)

    check("target repo is exactly /home/nic/forge", str(repo) == "/home/nic/forge")
    check("target repo directory exists", repo.is_dir())
    check("target repo is a git repository", (repo / ".git").is_dir())

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    try:
        from aiweb_status_claim_scaffold.verify import (
            REQUIRED_RELATIVE_FILES,
            forbidden_imports_in_file,
            git_status_is_slice03_only,
            required_files_present,
            sample_claim_checks_ok,
            syntax_error_for_file,
            vocabulary_shape_ok,
        )
    except Exception as exc:
        failures.append(f"could not import Slice 3 verifier helpers: {exc}")
        REQUIRED_RELATIVE_FILES = ()

    if REQUIRED_RELATIVE_FILES:
        missing = required_files_present(repo)
        for rel in REQUIRED_RELATIVE_FILES:
            check(f"required file exists: {rel}", rel not in missing)

        for rel in REQUIRED_RELATIVE_FILES:
            path = repo / rel
            if not path.is_file():
                continue
            if path.suffix == ".py":
                syntax_error = syntax_error_for_file(path)
                check(f"python syntax valid: {rel}", syntax_error == "")
                if syntax_error:
                    failures.append(syntax_error)

                try:
                    imports = forbidden_imports_in_file(path)
                except Exception as exc:
                    imports = (f"import scan error: {exc}",)
                check(f"no forbidden active model/network imports: {rel}", not imports)
                for item in imports:
                    failures.append(f"forbidden import in {rel}: {item}")

        try:
            status_output = subprocess.check_output(
                ["git", "-C", str(repo), "status", "--short"],
                text=True,
                stderr=subprocess.STDOUT,
            )
            unexpected = git_status_is_slice03_only(status_output.splitlines())
            check("git status contains only Slice 3 scaffold paths", not unexpected)
            for line in unexpected:
                failures.append(f"unexpected git status line: {line}")
        except Exception as exc:
            failures.append(f"could not read git status: {exc}")

        check("controlled status vocabulary shape is valid", vocabulary_shape_ok())
        check("sample claim validations pass", sample_claim_checks_ok())

    print("============================================================")
    print("AIWEB SLICE 3 STATUS CLAIM SCAFFOLD VERIFIER")
    print("============================================================")
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")

    if failures:
        print("VERDICT: FAIL - Slice 3 status claim scaffold verifier failed within Slice 3 scope")
        return 1

    print("VERDICT: PASS - Slice 3 status claim scaffold verifier passed within Slice 3 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
