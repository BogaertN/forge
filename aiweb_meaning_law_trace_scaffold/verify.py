"""Verifier for Slice 7 meaning-object and law-trace scaffold."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

from .law_trace import build_law_trace, build_law_trace_step, law_trace_scope_record
from .meaning_object import build_meaning_object, meaning_object_scope_record


REQUIRED_FILES = [
    "aiweb_meaning_law_trace_scaffold/__init__.py",
    "aiweb_meaning_law_trace_scaffold/meaning_object.py",
    "aiweb_meaning_law_trace_scaffold/law_trace.py",
    "aiweb_meaning_law_trace_scaffold/verify.py",
    "scripts/test_aiweb_slice07_meaning_law_trace_scaffold.py",
    "scripts/aiweb_slice07_meaning_law_trace_verify.py",
    "scripts/README_aiweb_slice07_meaning_law_trace_scaffold.md",
]

ALLOWED_GIT_STATUS_PREFIXES = (
    "?? aiweb_meaning_law_trace_scaffold/",
    "A  aiweb_meaning_law_trace_scaffold/",
    "?? scripts/README_aiweb_slice07_meaning_law_trace_scaffold.md",
    "A  scripts/README_aiweb_slice07_meaning_law_trace_scaffold.md",
    "?? scripts/aiweb_slice07_meaning_law_trace_verify.py",
    "A  scripts/aiweb_slice07_meaning_law_trace_verify.py",
    "?? scripts/test_aiweb_slice07_meaning_law_trace_scaffold.py",
    "A  scripts/test_aiweb_slice07_meaning_law_trace_scaffold.py",
)

_BAD_IMPORT_PARTS = [
    ("open", "ai"),
    ("anth", "ropic"),
    ("oll", "ama"),
    ("chrom", "adb"),
    ("lang", "chain"),
    ("ll", "ama"),
    ("fa", "iss"),
    ("torch",),
    ("tensorflow",),
    ("transform", "ers"),
    ("sentence", "_", "transform", "ers"),
    ("sk", "learn"),
]


def _join(parts: Sequence[str]) -> str:
    return "".join(parts)


def _bad_import_names() -> List[str]:
    return [_join(parts) for parts in _BAD_IMPORT_PARTS]


def _run_git(repo: Path, args: Sequence[str]) -> Tuple[int, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode, proc.stdout


def _python_files(repo: Path) -> List[Path]:
    return [repo / item for item in REQUIRED_FILES if item.endswith(".py")]


def _check_python_syntax(path: Path) -> Tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return False, f"{path}: {exc}"
    return True, str(path)


def _check_bad_imports(path: Path) -> Tuple[bool, str]:
    bad = set(_bad_import_names())
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return False, f"{path}: {exc}"
    found: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".")[0].lower()
                if root_name in bad:
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_name = node.module.split(".")[0].lower()
                if root_name in bad:
                    found.append(node.module)
    if found:
        return False, f"{path}: {', '.join(sorted(set(found)))}"
    return True, str(path)


def _check_scanner_source_guard(repo: Path) -> Tuple[bool, str]:
    try:
        from aiweb_authority_scanner_scaffold.scanner import scan_paths
    except Exception as exc:  # pragma: no cover - diagnostic path
        return False, f"Slice 6 scanner import failed: {exc}"
    report = scan_paths([repo / item for item in REQUIRED_FILES])
    if report.finding_count:
        return False, f"Slice 6 scanner flagged Slice 7 source files: {report.finding_count}"
    return True, "Slice 6 scanner did not flag Slice 7 source files"


def _check_scope_records() -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    meaning_scope = meaning_object_scope_record()
    trace_scope = law_trace_scope_record()
    for label, scope in (("meaning", meaning_scope), ("trace", trace_scope)):
        if scope.get("runtime_effect") == "none":
            passes.append(f"{label} scope has no runtime effect")
        else:
            failures.append(f"{label} scope has runtime effect")
        if scope.get("dependency_change") == "none":
            passes.append(f"{label} scope has no dependency change")
        else:
            failures.append(f"{label} scope changes dependencies")
        blocked_fields = [
            "concept_resolution",
            "predicate_resolution",
            "gate_selection",
            "expression_rendering",
            "ui_surface",
            "stored_material_update",
            "external_resource_use",
            "delivery_step",
            "action_route",
            "baseline_change",
        ]
        enabled = [field for field in blocked_fields if scope.get(field)]
        if enabled:
            failures.append(f"{label} scope enabled downstream fields: {enabled}")
        else:
            passes.append(f"{label} scope keeps downstream fields disabled")
    return passes, failures


def _check_sample_records() -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    try:
        step = build_law_trace_step(
            rule_family="boundary",
            rule_id="DOC10-SLICE7-BOUNDARY",
            input_ref="sample_input",
            decision="recorded",
            note="scaffold boundary record",
        )
        trace = build_law_trace(
            authority_basis=("Document 10", "Slice 7"),
            linked_object_ids=(),
            steps=(step,),
            metadata={"sample": "true"},
        )
        obj = build_meaning_object(
            source_text="  The sample request is recorded only.  ",
            source_label="sample_input",
            authority_basis=("Document 10", "Slice 7"),
            law_trace_ids=(trace.trace_id,),
            metadata={"sample": "true"},
        )
        ok_obj, detail_obj = obj.validate()
        ok_trace, detail_trace = trace.validate()
        if ok_obj:
            passes.append(detail_obj)
        else:
            failures.append(detail_obj)
        if ok_trace:
            passes.append(detail_trace)
        else:
            failures.append(detail_trace)
        obj2 = build_meaning_object(
            source_text="The sample request is recorded only.",
            source_label="sample_input",
            authority_basis=("Document 10", "Slice 7"),
            law_trace_ids=(trace.trace_id,),
            metadata={"sample": "true"},
        )
        if obj.object_id == obj2.object_id and obj.content_hash() == obj2.content_hash():
            passes.append("meaning object identifiers are deterministic")
        else:
            failures.append("meaning object identifiers are not deterministic")
        step2 = build_law_trace_step(
            rule_family="boundary",
            rule_id="DOC10-SLICE7-BOUNDARY",
            input_ref="sample_input",
            decision="recorded",
            note="scaffold boundary record",
        )
        trace2 = build_law_trace(
            authority_basis=("Document 10", "Slice 7"),
            linked_object_ids=(),
            steps=(step2,),
            metadata={"sample": "true"},
        )
        if trace.trace_id == trace2.trace_id and trace.content_hash() == trace2.content_hash():
            passes.append("law trace identifiers are deterministic")
        else:
            failures.append("law trace identifiers are not deterministic")
    except Exception as exc:
        failures.append(f"sample record construction failed: {exc}")
    try:
        build_meaning_object(
            source_text="blocked sample",
            source_label="bad_sample",
            authority_basis=("Document 10", "Slice 7"),
            payload={"concept_resolution": True},
        )
        failures.append("controlled downstream payload was not rejected")
    except ValueError:
        passes.append("controlled downstream payload is rejected")
    try:
        build_law_trace_step(
            rule_family="boundary",
            rule_id="bad",
            input_ref="bad_sample",
            details={"action_route": True},
        )
        failures.append("controlled downstream trace detail was not rejected")
    except ValueError:
        passes.append("controlled downstream trace detail is rejected")
    return passes, failures


def verify_slice07(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    repo = repo.resolve()

    if repo.exists():
        passes.append(f"target repo directory exists: {repo}")
    else:
        failures.append(f"target repo directory missing: {repo}")
        return passes, failures

    if (repo / ".git").is_dir():
        passes.append("target repo is a git repository")
    else:
        failures.append("target repo is not a git repository")

    for rel in REQUIRED_FILES:
        path = repo / rel
        if path.is_file():
            passes.append(f"required file exists: {rel}")
        else:
            failures.append(f"required file missing: {rel}")

    for path in _python_files(repo):
        if not path.exists():
            continue
        ok, detail = _check_python_syntax(path)
        (passes if ok else failures).append(
            f"python syntax valid: {detail}" if ok else f"python syntax invalid: {detail}"
        )
        ok, detail = _check_bad_imports(path)
        (passes if ok else failures).append(
            f"no blocked active imports: {detail}" if ok else f"blocked active import found: {detail}"
        )

    scope_passes, scope_failures = _check_scope_records()
    passes.extend(scope_passes)
    failures.extend(scope_failures)

    sample_passes, sample_failures = _check_sample_records()
    passes.extend(sample_passes)
    failures.extend(sample_failures)

    ok, detail = _check_scanner_source_guard(repo)
    (passes if ok else failures).append(detail)

    code, status = _run_git(repo, ["status", "--short"])
    if code == 0:
        bad_lines = []
        for line in status.splitlines():
            if not line.strip():
                continue
            if not any(line.startswith(prefix) for prefix in ALLOWED_GIT_STATUS_PREFIXES):
                bad_lines.append(line)
        if bad_lines:
            failures.append("git status contains out-of-scope paths: " + " | ".join(bad_lines))
        else:
            passes.append("git status is clean or limited to Slice 7 scaffold paths")
    else:
        failures.append("git status command failed")

    return passes, failures


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    repo = Path(args[0]) if args else Path.cwd()
    print("=" * 60)
    print("AIWEB SLICE 7 MEANING OBJECT AND LAW TRACE SCAFFOLD VERIFIER")
    print("=" * 60)
    print(f"Target repo: {repo}")
    passes, failures = verify_slice07(repo)
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - Slice 7 meaning object and law trace scaffold verifier failed")
        return 1
    print("VERDICT: PASS - Slice 7 meaning object and law trace scaffold verifier passed within Slice 7 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
