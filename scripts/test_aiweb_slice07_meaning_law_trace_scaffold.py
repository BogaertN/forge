#!/usr/bin/env python3
"""Behavior test for Slice 7 neutral object and trace scaffold."""

from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
sys.path.insert(0, str(REPO))

from aiweb_meaning_law_trace_scaffold.law_trace import (
    build_law_trace,
    build_law_trace_step,
    law_trace_scope_record,
)
from aiweb_meaning_law_trace_scaffold.meaning_object import (
    build_meaning_object,
    meaning_object_scope_record,
)
from aiweb_meaning_law_trace_scaffold.verify import verify_slice07


def require(condition: bool, label: str, passes: list[str], failures: list[str]) -> None:
    if condition:
        passes.append(label)
    else:
        failures.append(label)


def main() -> int:
    print("=" * 60)
    print("AIWEB SLICE 7 MEANING OBJECT AND LAW TRACE SCAFFOLD BEHAVIOR TEST")
    print("=" * 60)
    print(f"Target repo: {REPO}")
    passes: list[str] = []
    failures: list[str] = []

    meaning_scope = meaning_object_scope_record()
    trace_scope = law_trace_scope_record()
    require(meaning_scope["object_scaffold_only"] is True, "meaning object scope is scaffold-only", passes, failures)
    require(trace_scope["trace_scaffold_only"] is True, "law trace scope is scaffold-only", passes, failures)
    require(meaning_scope["runtime_effect"] == "none", "meaning object has no runtime effect", passes, failures)
    require(trace_scope["runtime_effect"] == "none", "law trace has no runtime effect", passes, failures)
    require(meaning_scope["dependency_change"] == "none", "meaning object changes no dependency", passes, failures)
    require(trace_scope["dependency_change"] == "none", "law trace changes no dependency", passes, failures)

    step = build_law_trace_step(
        rule_family="boundary",
        rule_id="DOC10-SLICE7-SAMPLE",
        input_ref="sample",
        decision="recorded",
        note="neutral trace sample",
    )
    trace = build_law_trace(
        authority_basis=("Document 10", "Slice 7"),
        steps=(step,),
        metadata={"test": "true"},
    )
    obj = build_meaning_object(
        source_text="Example    request   held as neutral scaffold.",
        source_label="sample",
        authority_basis=("Document 10", "Slice 7"),
        law_trace_ids=(trace.trace_id,),
        metadata={"test": "true"},
    )
    ok_obj, _ = obj.validate()
    ok_trace, _ = trace.validate()
    require(ok_obj, "meaning object validates", passes, failures)
    require(ok_trace, "law trace validates", passes, failures)
    require(obj.object_id.startswith("mo_"), "meaning object id has expected prefix", passes, failures)
    require(trace.trace_id.startswith("lt_"), "law trace id has expected prefix", passes, failures)
    require(step.step_id.startswith("lts_"), "law trace step id has expected prefix", passes, failures)
    require(trace.trace_id in obj.law_trace_ids, "meaning object links to law trace id", passes, failures)

    same_obj = build_meaning_object(
        source_text="Example request held as neutral scaffold.",
        source_label="sample",
        authority_basis=("Document 10", "Slice 7"),
        law_trace_ids=(trace.trace_id,),
        metadata={"test": "true"},
    )
    require(obj.object_id == same_obj.object_id, "meaning object normalization is deterministic", passes, failures)

    try:
        build_meaning_object(
            source_text="bad",
            source_label="bad",
            authority_basis=("Document 10",),
            payload={"gate_selection": True},
        )
        failures.append("downstream object payload was not blocked")
    except ValueError:
        passes.append("downstream object payload is blocked")

    try:
        build_law_trace_step(
            rule_family="boundary",
            rule_id="bad",
            input_ref="bad",
            details={"expression_rendering": True},
        )
        failures.append("downstream trace detail was not blocked")
    except ValueError:
        passes.append("downstream trace detail is blocked")

    verifier_passes, verifier_failures = verify_slice07(REPO)
    require(not verifier_failures, "verifier sample checks pass", passes, failures)
    if verifier_failures:
        failures.extend(verifier_failures)

    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - behavior test failed")
        return 1
    print("VERDICT: PASS - behavior test passed within Slice 7 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
