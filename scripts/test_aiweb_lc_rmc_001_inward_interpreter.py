#!/usr/bin/env python3
"""LC-RMC-001 behavior and integration tests.

``--mode isolated`` runs against the bounded source-authority reconstruction.
``--mode live`` additionally executes the existing complete RMC trace and
candidate path. The live mode is the acceptance mode for /home/nic/forge.
"""

from __future__ import annotations

import argparse
import ast
import copy
from dataclasses import FrozenInstanceError
import json
import locale
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aiweb_language_core_bootstrap.deterministic_language_runtime import (
    interpret_source,
    runtime_authority_boundary,
)
from aiweb_language_core_bootstrap.deterministic_language_runtime.authority import (
    MAX_SOURCE_CHARACTERS,
    REFUSAL_CONTROL_CHARACTER,
    REFUSAL_METADATA_AUTHORITY,
    REFUSAL_SOURCE_AUTHORITY_IDENTIFIER,
    REFUSAL_SOURCE_TOO_LARGE,
    REFUSAL_UNSUPPORTED_FORM,
    REFUSAL_UNSUPPORTED_PREDICATE,
    REFUSAL_UNSUPPORTED_UNICODE,
)
from rmc_engine_v1.phase_parser import parse_phase, phase_parser_boundary


LIVE_MODE = False


def _candidate(source: str):
    result = interpret_source(source)
    if not result.candidates:
        raise AssertionError(result.to_dict())
    return result, result.candidates[0]


class InterpreterBehaviorTests(unittest.TestCase):
    def test_positive_operational_examples(self) -> None:
        examples = {
            "Inspect the current build status.": "inspect",
            "Please verify the packet checksum.": "verify",
            "Report the repository state.": "report",
            "Can you request a read-only audit?": "request",
            "Simulate the memory write plan.": "simulate",
        }
        for source, expected_root in examples.items():
            with self.subTest(source=source):
                envelope, candidate = _candidate(source)
                self.assertEqual(envelope.status, "INTERPRETED")
                self.assertTrue(envelope.coverage_complete)
                self.assertEqual(candidate.action_root_key, expected_root)
                self.assertFalse(candidate.selected)
                self.assertFalse(candidate.permission_granted)
                self.assertFalse(candidate.execution_authorized)
                self.assertFalse(candidate.output_authorized)
                self.assertFalse(candidate.memory_write_authorized)

    def test_communicative_forms(self) -> None:
        expected = {
            "Inspect the build.": "DIRECT_IMPERATIVE",
            "Please inspect the build.": "POLITE_IMPERATIVE",
            "Could you inspect the build?": "MODAL_REQUEST",
            "Forge inspects the build.": "SIMPLE_ACTIVE_DECLARATIVE",
        }
        for source, form in expected.items():
            with self.subTest(source=source):
                _, candidate = _candidate(source)
                self.assertEqual(candidate.communicative_form, form)

    def test_declared_morphology(self) -> None:
        for source in (
            "Forge inspects the build.",
            "Forge inspected the build.",
            "Forge is inspecting the build.",
        ):
            with self.subTest(source=source):
                _, candidate = _candidate(source)
                self.assertEqual(candidate.action_root_key, "inspect")

    def test_malformed_action_forms_and_noun_order_fail_closed(self) -> None:
        for source in (
            "Can you inspected the build?",
            "Can you inspects the build?",
            "Can you inspecting the build?",
            "Inspected the build.",
            "Inspects the build.",
            "Inspecting the build.",
            "Please inspecting the build.",
            "Please Forge inspects the build.",
            "Forge inspect the build.",
            "We inspects the build.",
            "Do not inspected the build.",
            "Forge does not inspects the build.",
            "Forge are inspecting the build.",
            "Forge were inspecting the build.",
            "We is inspecting the build.",
            "We was inspecting the build.",
            "I is inspecting the build.",
            "I are inspecting the build.",
            "System am inspecting the build.",
            "Forge do inspect the build.",
            "Forge don't inspect the build.",
            "We does inspect the build.",
            "We doesn't inspect the build.",
            "Don't not inspect the build.",
            "Forge doesn't never inspect the build.",
            "Can't you not inspect the build?",
            "Cannot you not inspect the build.",
            "The i inspect the build.",
            "A we inspect the build.",
            "Verify build the.",
            "Verify build current.",
            "Verify the the build.",
            "Verify current the build.",
            "Verify the build current.",
        ):
            with self.subTest(source=source):
                result = interpret_source(source)
                self.assertEqual(result.status, "REFUSED")
                self.assertEqual(
                    result.refusal_code, REFUSAL_UNSUPPORTED_FORM
                )
                self.assertFalse(result.candidates)

    def test_auxiliary_and_subject_agreement_forms(self) -> None:
        for source in (
            "Forge does inspect the build.",
            "Forge did inspect the build.",
            "Forge doesn't inspect the build.",
            "Forge is inspecting the build.",
            "Forge was inspecting the build.",
            "I am inspecting the build.",
            "I was inspecting the build.",
            "We inspect the build.",
            "We are inspecting the build.",
            "We were inspecting the build.",
            "We do inspect the build.",
            "We didn't inspect the build.",
            "Do not inspect the build.",
            "Don't inspect the build.",
            "Forge does not inspect the build.",
            "Could you not inspect the build?",
            "Can't you inspect the build?",
            "The operator inspects the build.",
            "Could you inspect the build?",
        ):
            with self.subTest(source=source):
                result, candidate = _candidate(source)
                self.assertEqual(result.status, "INTERPRETED")
                self.assertEqual(candidate.action_root_key, "inspect")

    def test_negation_survives_signature(self) -> None:
        positive, positive_candidate = _candidate(
            "Verify the packet checksum."
        )
        negative, negative_candidate = _candidate(
            "Do not verify the packet checksum."
        )
        self.assertFalse(positive_candidate.negated)
        self.assertTrue(negative_candidate.negated)
        self.assertNotEqual(
            positive.semantic_signature,
            negative.semantic_signature,
        )

    def test_contracted_negation(self) -> None:
        _, candidate = _candidate("Don't simulate the memory write plan.")
        self.assertTrue(candidate.negated)

    def test_exact_source_spans(self) -> None:
        source = "Please verify the packet checksum."
        envelope, candidate = _candidate(source)
        for token in envelope.tokens:
            self.assertEqual(
                source[token.span.start : token.span.end],
                token.source,
            )
        self.assertEqual(
            set(candidate.consumed_token_indexes),
            set(range(len(envelope.tokens))),
        )

    def test_attachment_ambiguity_is_preserved_without_selection(self) -> None:
        result = interpret_source(
            "Inspect the repository with the audit."
        )
        self.assertEqual(result.status, "AMBIGUOUS")
        self.assertTrue(result.ambiguity_preserved)
        self.assertEqual(len(result.candidates), 2)
        self.assertEqual(
            {item.attachment_kind for item in result.candidates},
            {
                "OBJECT_MODIFIER_ATTACHMENT",
                "PREDICATE_INSTRUMENT_ATTACHMENT",
            },
        )
        self.assertTrue(all(not item.selected for item in result.candidates))
        self.assertEqual(
            len({item.semantic_signature for item in result.candidates}),
            2,
        )

    def test_unsupported_predicate_fails_closed(self) -> None:
        result = interpret_source("Delete the repository.")
        self.assertEqual(result.status, "REFUSED")
        self.assertEqual(
            result.refusal_code,
            REFUSAL_UNSUPPORTED_PREDICATE,
        )
        self.assertFalse(result.candidates)

    def test_partial_source_consumption_fails_closed(self) -> None:
        result = interpret_source("Verify the packet checksum / now.")
        self.assertEqual(result.status, "REFUSED")
        self.assertFalse(result.coverage_complete)
        self.assertFalse(result.candidates)

    def test_conflicting_metadata_is_rejected(self) -> None:
        result = interpret_source(
            "Verify the packet checksum.",
            {"action_root": "delete"},
        )
        self.assertEqual(result.status, "REFUSED")
        self.assertEqual(result.refusal_code, REFUSAL_METADATA_AUTHORITY)
        self.assertTrue(result.metadata_authority_attempted)
        self.assertFalse(result.metadata_authority_used)

    def test_matching_metadata_is_ignored_not_used(self) -> None:
        result = interpret_source(
            "Verify the packet checksum.",
            {"action_root": "verify"},
        )
        self.assertEqual(result.status, "INTERPRETED")
        self.assertTrue(result.metadata_authority_attempted)
        self.assertFalse(result.metadata_authority_used)

    def test_source_candidate_identifier_is_not_authority(self) -> None:
        result = interpret_source("Inspect candidate_deadbeef.")
        self.assertEqual(result.status, "REFUSED")
        self.assertEqual(
            result.refusal_code,
            REFUSAL_SOURCE_AUTHORITY_IDENTIFIER,
        )

    def test_size_limit_is_typed(self) -> None:
        result = interpret_source("a" * (MAX_SOURCE_CHARACTERS + 1))
        self.assertEqual(result.status, "REFUSED")
        self.assertEqual(result.refusal_code, REFUSAL_SOURCE_TOO_LARGE)

    def test_unicode_and_control_policy_is_typed(self) -> None:
        unicode_result = interpret_source("Verify the packet checksum Ω.")
        control_result = interpret_source("Verify\nthe packet checksum.")
        self.assertEqual(
            unicode_result.refusal_code,
            REFUSAL_UNSUPPORTED_UNICODE,
        )
        self.assertEqual(
            control_result.refusal_code,
            REFUSAL_CONTROL_CHARACTER,
        )

    def test_deterministic_replay_and_environment_independence(self) -> None:
        source = "Please verify the sealed packet checksum."
        first = interpret_source(source)
        old_lc_all = os.environ.get("LC_ALL")
        old_tz = os.environ.get("TZ")
        try:
            os.environ["LC_ALL"] = "C"
            os.environ["TZ"] = "Pacific/Honolulu"
            try:
                locale.setlocale(locale.LC_ALL, "C")
            except locale.Error:
                pass
            second = interpret_source(source)
        finally:
            if old_lc_all is None:
                os.environ.pop("LC_ALL", None)
            else:
                os.environ["LC_ALL"] = old_lc_all
            if old_tz is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = old_tz
        self.assertEqual(first.semantic_signature, second.semantic_signature)
        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())

    def test_records_are_immutable(self) -> None:
        result, candidate = _candidate("Inspect the build.")
        with self.assertRaises(FrozenInstanceError):
            candidate.action_root_key = "delete"
        with self.assertRaises(FrozenInstanceError):
            result.status = "SELECTED"

    def test_phase_adapter_preserves_entrypoint_and_authority_boundary(self) -> None:
        report = parse_phase("Please verify the packet checksum.")
        self.assertEqual(report["status"], "OK")
        self.assertEqual(report["phase_state"]["action_root_key"], "verify")
        self.assertTrue(report["phase_state"]["interpretation_complete"])
        self.assertFalse(report["phase_state"]["selected_meaning_created"])
        self.assertFalse(report["fallback_performed"])
        for key in (
            "approved_output",
            "permission_granted",
            "route_authorized",
            "tool_authorized",
            "execution_authorized",
            "delivery_authorized",
        ):
            self.assertFalse(report[key], key)

    def test_phase_refusal_has_no_legacy_fallback(self) -> None:
        report = parse_phase("Delete the repository.")
        self.assertEqual(report["status"], "UNRESOLVED")
        self.assertIsNone(report["phase_state"]["phase_primary"])
        self.assertFalse(report["phase_state"]["interpretation_complete"])
        self.assertEqual(
            report["phase_state"]["routing"],
            ["stop_before_rmc_meaning_admission"],
        )
        self.assertFalse(report["fallback_performed"])

    def test_boundaries_prohibit_side_effects_and_model_authority(self) -> None:
        combined = {
            **runtime_authority_boundary(),
            **phase_parser_boundary(),
        }
        for key in (
            "calls_llm",
            "queries_chroma",
            "writes_files",
            "writes_rmc_memory",
            "writes_identity_vault",
            "route_authority",
            "tool_authority",
            "execution_authority",
            "output_authority",
            "delivery_authority",
        ):
            self.assertFalse(combined.get(key, False), key)

    def test_static_trace_call_spine_remains_connected(self) -> None:
        memory_source = (ROOT / "rmc_engine_v1/memory_recaller.py").read_text(
            encoding="utf-8"
        )
        candidate_source = (
            ROOT / "rmc_engine_v1/candidate_generator.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "from rmc_engine_v1.phase_parser import parse_phase",
            memory_source,
        )
        self.assertIn(
            "phase_report = parse_phase(source_text, source_metadata)",
            memory_source,
        )
        self.assertIn("def generate_candidates(", candidate_source)

    def test_live_trace_and_candidate_path(self) -> None:
        if not LIVE_MODE:
            self.skipTest(
                "live RMC dependencies are intentionally absent from source packet"
            )
        from rmc_engine_v1.candidate_generator import generate_candidates
        from rmc_engine_v1.memory_recaller import build_trace_spine

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "forge"
            for relative in (
                "memory/context_library_v1/receipts",
                "memory/context_library_v1/manifests",
                "memory/context_library_v1/symbolic_maps",
                "memory/rmc_dataset_v1",
            ):
                (root / relative).mkdir(parents=True, exist_ok=True)
            before = sorted(
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
            )
            trace = build_trace_spine(
                "Inspect the current build status.",
                {"source_kind": "lc_rmc_001_live_test"},
                root=root,
            )
            self.assertEqual(trace.get("status"), "OK")
            self.assertTrue(
                trace.get("language_core_admission", {}).get("admitted")
            )
            phase_report = trace.get("phase_report", {})
            self.assertEqual(
                phase_report.get("phase_state", {}).get("action_root_key"),
                "inspect",
            )
            self.assertEqual(
                phase_report.get("language_core_interpretation", {})
                .get("candidates", [{}])[0]
                .get("action_root_key"),
                "inspect",
            )
            linguistic = phase_report.get(
                "language_core_interpretation", {}
            )
            symbolic_phase = trace.get("symbolic_trace", {}).get("Φ_t", {})
            self.assertTrue(symbolic_phase.get("language_core_admitted"))
            self.assertEqual(
                symbolic_phase.get("linguistic_candidate_ids"),
                [linguistic.get("candidates", [{}])[0].get("candidate_id")],
            )
            self.assertEqual(
                symbolic_phase.get("semantic_signature"),
                linguistic.get("semantic_signature"),
            )
            self.assertEqual(symbolic_phase.get("action_root_key"), "inspect")
            self.assertFalse(symbolic_phase.get("negated"))
            generated = generate_candidates(trace)
            self.assertEqual(generated.get("status"), "OK")
            self.assertTrue(generated.get("candidate_set"))
            self.assertTrue(
                all(
                    item.get("projection_allowed") is False
                    and item.get("memory_write_allowed") is False
                    and item.get("approved_output") is False
                    for item in generated.get("candidate_set", [])
                )
            )

            missing_custody = generate_candidates({
                "status": "OK",
                "symbolic_trace": {
                    "trace_id": "rmctrace_missing_language_core",
                    "Φ_t": {"phase_primary": "Φ6"},
                },
            })
            self.assertEqual(missing_custody.get("status"), "BLOCKED")
            self.assertEqual(
                missing_custody.get("reason_code"),
                "LC_RMC_001_LANGUAGE_CORE_CUSTODY_MISSING",
            )
            self.assertEqual(missing_custody.get("candidate_set"), [])

            tampered_phase = copy.deepcopy(trace)
            tampered_phase["symbolic_trace"]["Φ_t"][
                "phase_primary"
            ] = "Φ8"
            tampered_phase["symbolic_trace"]["Φ_t"][
                "phase_path_hypothesis"
            ] = ["Φ8"]
            tampered_ids = copy.deepcopy(trace)
            tampered_ids["symbolic_trace"]["Φ_t"][
                "linguistic_candidate_ids"
            ] = []
            tampered_action = copy.deepcopy(trace)
            tampered_action["phase_report"]["phase_state"][
                "action_root_key"
            ] = "report"
            tampered_path = copy.deepcopy(trace)
            tampered_path["phase_report"]["phase_state"][
                "phase_path_hypothesis"
            ] = ["Φ6", "Φ8"]
            tampered_path["symbolic_trace"]["Φ_t"][
                "phase_path_hypothesis"
            ] = ["Φ6", "Φ8"]
            tampered_source = copy.deepcopy(trace)
            for event in (
                tampered_source["input_event"],
                tampered_source["symbolic_trace"]["I_t"],
            ):
                event["raw_input_preview"] = "projection"
                event["raw_input_sha256"] = "tampered_source_sha256"
                event["raw_input_length"] = len("projection")
            tampered_authority = copy.deepcopy(trace)
            tampered_authority["phase_report"][
                "language_core_interpretation"
            ]["candidates"][0]["permission_granted"] = True
            tampered_coverage = copy.deepcopy(trace)
            tampered_coverage["phase_report"][
                "language_core_interpretation"
            ]["coverage_complete"] = False
            tampered_confidence = copy.deepcopy(trace)
            tampered_confidence["symbolic_trace"]["Φ_t"][
                "confidence"
            ] = 0.0
            coordinated_confidence = copy.deepcopy(trace)
            coordinated_confidence["symbolic_trace"]["Φ_t"][
                "confidence"
            ] = 0.0
            coordinated_confidence["phase_report"]["phase_state"][
                "confidence"
            ] = 0.0
            tampered_phase_authority = copy.deepcopy(trace)
            tampered_phase_authority["phase_report"][
                "permission_granted"
            ] = True
            tampered_phase_fallback = copy.deepcopy(trace)
            tampered_phase_fallback["phase_report"][
                "fallback_performed"
            ] = True
            tampered_trace_fallback = copy.deepcopy(trace)
            tampered_trace_fallback["fallback_performed"] = True
            tampered_trace_id = copy.deepcopy(trace)
            tampered_trace_id["symbolic_trace"][
                "trace_id"
            ] = "rmctrace_tampered"
            for name, altered in (
                ("phase", tampered_phase),
                ("candidate_ids", tampered_ids),
                ("action_root", tampered_action),
                ("coordinated_phase_path", tampered_path),
                ("source_event", tampered_source),
                ("authority_flag", tampered_authority),
                ("coverage", tampered_coverage),
                ("symbolic_confidence", tampered_confidence),
                ("coordinated_confidence", coordinated_confidence),
                ("phase_authority", tampered_phase_authority),
                ("phase_fallback", tampered_phase_fallback),
                ("trace_fallback", tampered_trace_fallback),
                ("trace_id", tampered_trace_id),
            ):
                with self.subTest(custody_tamper=name):
                    held = generate_candidates(altered)
                    self.assertEqual(held.get("status"), "BLOCKED")
                    self.assertEqual(
                        held.get("reason_code"),
                        "LC_RMC_001_LANGUAGE_CORE_CUSTODY_MISMATCH",
                    )
                    self.assertEqual(held.get("candidate_set"), [])
                    self.assertIsNone(
                        held.get("selected_candidate_preview")
                    )
            after = sorted(
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
            )
            self.assertEqual(before, after)

    def test_live_held_meanings_stop_before_rmc_candidates(self) -> None:
        if not LIVE_MODE:
            self.skipTest(
                "live RMC dependencies are intentionally absent from source packet"
            )
        from rmc_engine_v1.candidate_generator import generate_candidates
        from rmc_engine_v1.memory_recaller import build_trace_spine

        cases = (
            (
                "Delete the repository.",
                "LC_RMC_001_UNSUPPORTED_PREDICATE",
                "REFUSED",
                0,
                False,
            ),
            (
                "Inspect the repository with the audit.",
                "LC_RMC_001_AMBIGUOUS_MEANING_HELD",
                "AMBIGUOUS",
                2,
                False,
            ),
            (
                "Do not verify the packet checksum.",
                "LC_RMC_001_NEGATED_ACTION_HELD",
                "INTERPRETED",
                1,
                True,
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "forge"
            for relative in (
                "memory/context_library_v1/receipts",
                "memory/context_library_v1/manifests",
                "memory/context_library_v1/symbolic_maps",
                "memory/rmc_dataset_v1",
            ):
                (root / relative).mkdir(parents=True, exist_ok=True)
            before = sorted(
                path.relative_to(root).as_posix() for path in root.rglob("*")
            )

            for source, reason, status, count, negated in cases:
                with self.subTest(source=source):
                    phase = parse_phase(source)
                    self.assertEqual(phase.get("status"), "UNRESOLVED")
                    self.assertEqual(phase.get("reason_code"), reason)
                    self.assertFalse(phase.get("language_core_admitted"))
                    self.assertFalse(phase.get("candidate_pipeline_eligible"))
                    self.assertIsNone(
                        phase.get("phase_state", {}).get("phase_primary")
                    )
                    interpretation = phase.get(
                        "language_core_interpretation", {}
                    )
                    self.assertEqual(interpretation.get("status"), status)
                    self.assertEqual(
                        len(interpretation.get("candidates", [])), count
                    )

                    trace = build_trace_spine(source, root=root)
                    self.assertEqual(trace.get("status"), "BLOCKED")
                    self.assertEqual(trace.get("reason_code"), reason)
                    self.assertFalse(
                        trace.get("language_core_admission", {}).get(
                            "admitted"
                        )
                    )
                    self.assertEqual(
                        trace.get("memory_recall", {}).get("status"),
                        "NOT_RUN_LANGUAGE_CORE_HOLD",
                    )
                    self.assertEqual(
                        trace.get("drift_report", {}).get("status"),
                        "NOT_RUN_LANGUAGE_CORE_HOLD",
                    )
                    symbolic_phase = trace.get("symbolic_trace", {}).get(
                        "Φ_t", {}
                    )
                    self.assertEqual(
                        symbolic_phase.get("linguistic_candidate_ids"),
                        [
                            candidate.get("candidate_id")
                            for candidate in interpretation.get(
                                "candidates", []
                            )
                        ],
                    )
                    self.assertEqual(symbolic_phase.get("negated"), negated)

                    generated = generate_candidates(trace)
                    self.assertEqual(generated.get("status"), "BLOCKED")
                    self.assertEqual(generated.get("reason_code"), reason)
                    self.assertFalse(generated.get("C_t_present"))
                    self.assertEqual(generated.get("candidate_set"), [])
                    self.assertIsNone(
                        generated.get("selected_candidate_preview")
                    )

            after = sorted(
                path.relative_to(root).as_posix() for path in root.rglob("*")
            )
            self.assertEqual(before, after)

    def test_live_forge_phase_api_propagates_language_core_status(self) -> None:
        if not LIVE_MODE:
            self.skipTest("main.py adapter is a live Forge integration")

        main_path = ROOT / "main.py"
        syntax = ast.parse(main_path.read_text(encoding="utf-8"))
        wanted = {
            "_p262f_resolve_source",
            "_p262f_rmc_phase_parser_v1",
            "_p262h_rmc_candidate_conclusion_v1",
        }
        functions = [
            node
            for node in syntax.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted
        ]
        self.assertEqual({node.name for node in functions}, wanted)
        namespace: dict[str, object] = {}
        exec(
            compile(
                ast.Module(body=functions, type_ignores=[]),
                str(main_path),
                "exec",
            ),
            namespace,
        )

        rejected = namespace["_p262f_rmc_phase_parser_v1"](
            "/api/rmc/phase-parser?input=Delete+the+repository."
        )
        self.assertEqual(rejected.get("status"), "UNRESOLVED")
        self.assertEqual(
            rejected.get("reason_code"),
            "LC_RMC_001_UNSUPPORTED_PREDICATE",
        )
        self.assertFalse(rejected.get("language_core_admitted"))
        self.assertFalse(rejected.get("candidate_pipeline_eligible"))
        self.assertEqual(
            rejected.get("language_core_interpretation", {}).get("status"),
            "REFUSED",
        )
        self.assertFalse(rejected.get("fallback_performed"))

        namespace["_p262b6_rmc_trace_spine_v1"] = lambda _path: {
            "status": "BLOCKED",
            "reason_code": "TEST_LANGUAGE_CORE_HOLD",
            "symbolic_trace": {"Φ_t": {}},
        }
        held_candidates = namespace[
            "_p262h_rmc_candidate_conclusion_v1"
        ]("/api/rmc/candidate-conclusion")
        self.assertEqual(held_candidates.get("status"), "BLOCKED")
        self.assertEqual(
            held_candidates.get("reason_code"), "TEST_LANGUAGE_CORE_HOLD"
        )
        self.assertEqual(
            held_candidates.get("C_t", {}).get("status"),
            "BLOCKED_LANGUAGE_CORE_OR_TRACE_HOLD",
        )
        self.assertEqual(held_candidates.get("candidate_set"), [])
        self.assertIsNone(
            held_candidates.get("selected_candidate_preview")
        )

        namespace["_p262a_rmc_memory_object_view_v1"] = lambda _path: {
            "object_kind": "test_memory_object",
            "status": "OK",
            "manifest_trace": "Please\nverify",
            "selected_symbolic_entry": "the packet checksum.",
        }
        source, _metadata = namespace["_p262f_resolve_source"](
            "/api/rmc/phase-parser?selector=test"
        )
        self.assertEqual(source, "Please verify the packet checksum.")
        self.assertNotIn("\n", source)


def main() -> int:
    global LIVE_MODE
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("isolated", "live"),
        default="live",
    )
    args = parser.parse_args()
    LIVE_MODE = args.mode == "live"
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        InterpreterBehaviorTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {
        "mode": args.mode,
        "run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "successful": result.wasSuccessful(),
    }
    print("LC_RMC_001_TEST_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
