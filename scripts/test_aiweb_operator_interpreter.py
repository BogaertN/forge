#!/usr/bin/env python3
"""Focused backend checks for the non-LLM Ask Forge interpreter.

The checks use only injected providers and temporary repository roots.  They
exercise the public interpreter/research contracts without calling the public
network or depending on the workstation's current candidate-memory contents.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1 import operator_interpreter  # noqa: E402
from rmc_engine_v1.operator_interpreter import (  # noqa: E402
    answer_forge_question,
    persist_possible_answer_candidate,
)
from rmc_engine_v1.research_acquisition import (  # noqa: E402
    ResearchProvider,
    acquire_research_evidence,
    capture_public_page_evidence,
)


def _held_exact_preview(_: str) -> dict[str, object]:
    """Keep non-exact route tests independent of installed promoted records."""

    return {
        "status": "HELD",
        "reason_code": "test_no_promoted_exact_answer",
        "trusted_rmc_provider": {"trusted": False},
        "rmc_exact_identity_resonances": [],
        "governed_output": None,
    }


def _trusted_exact_preview(source_text: str) -> dict[str, object]:
    """Return the minimum trusted promoted-RMC delivery evidence."""

    answer = "Forge preserved the exact promoted RMC answer."
    return {
        "status": "PREVIEW_READY",
        "source_text": source_text,
        "trusted_rmc_provider": {
            "trusted": True,
            "load_status": "TRUSTED_STRUCTURED",
        },
        "rmc_exact_identity_resonances": [
            {"memory_record_ref": "rmc_exact_language_record:test-promoted"}
        ],
        "governed_output": {
            "answer_delivery_eligible": True,
            "manifest": {
                "manifest_id": "language_output_manifest:test-promoted",
                "canonical": True,
            },
            "rendered_output": {
                "rendered_output_id": "language_render:test-promoted",
                "text": answer,
            },
            "exact_echo": {
                "echo_id": "language_echo:test-promoted",
                "status": "PASS",
                "exact_contract_match": True,
            },
        },
    }


class _CallTrap:
    """Record an unexpected provider call and fail at its exact boundary."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.calls = 0

    def no_args(self) -> dict[str, object]:
        self.calls += 1
        raise AssertionError(f"{self.label} must not be called")

    def one_arg(self, _: str) -> dict[str, object]:
        self.calls += 1
        raise AssertionError(f"{self.label} must not be called")

    def search(self, _: str) -> tuple[dict[str, object], ...]:
        self.calls += 1
        raise AssertionError(f"{self.label} must not be called")

    def capture(
        self,
        _: str,
        __: dict[str, object],
    ) -> dict[str, object]:
        self.calls += 1
        raise AssertionError(f"{self.label} must not be called")


class OperatorInterpreterTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(
            prefix="forge-operator-interpreter-test-"
        )
        self.repository_root = Path(self._temporary.name)

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def _answer_without_promoted_exact(
        self,
        source_text: str,
        **kwargs: object,
    ) -> dict[str, object]:
        with mock.patch.object(
            operator_interpreter,
            "_exact_language_attempt",
            side_effect=_held_exact_preview,
        ):
            return answer_forge_question(
                {"source_text": source_text},
                repository_root=self.repository_root,
                **kwargs,
            )

    def assert_no_repository_files(self) -> None:
        self.assertEqual(
            [path for path in self.repository_root.rglob("*") if path.is_file()],
            [],
        )

    def test_promoted_exact_rmc_short_circuits_and_preserves_source(self) -> None:
        exact_source = "  Echo ⩱ memory?\n"
        status_trap = _CallTrap("status provider")
        math_trap = _CallTrap("math provider")
        research_trap = _CallTrap("research provider")
        research_provider = ResearchProvider(
            search=research_trap.search,
            capture=research_trap.capture,
            provider_id="must-not-run",
        )

        with mock.patch.object(
            operator_interpreter,
            "_exact_language_attempt",
            side_effect=_trusted_exact_preview,
        ):
            response = answer_forge_question(
                {"source_text": exact_source},
                repository_root=self.repository_root,
                research_provider=research_provider,
                status_provider=status_trap.no_args,
                math_provider=math_trap.one_arg,
            )

        self.assertEqual(response["status"], "ANSWERED")
        self.assertEqual(response["answer_kind"], "trusted_rmc")
        self.assertEqual(response["route"], "promoted_exact_rmc")
        self.assertEqual(response["reason_code"], "promoted_exact_rmc_answer_delivered")
        self.assertEqual(response["source_text"], exact_source)
        self.assertEqual(
            "".join(str(row["exact_text"]) for row in response["source_forms"]),
            exact_source,
        )
        self.assertIsNone(response["candidate_memory_recall"])
        self.assertIsNone(response["research_acquisition"])
        self.assertIsNone(response["candidate_retention"])
        self.assertEqual(response["capability_result"]["echo"]["status"], "PASS")
        self.assertEqual(status_trap.calls, 0)
        self.assertEqual(math_trap.calls, 0)
        self.assertEqual(research_trap.calls, 0)

        custody = response["source_custody"]
        self.assertIs(custody["source_preserved_exactly"], True)
        self.assertIs(custody["token_stream_created"], False)
        boundary = response["boundary"]
        self.assertIs(boundary["source_forms_are_model_tokens"], False)
        self.assertIs(boundary["conventional_token_stream_created"], False)
        self.assertIs(boundary["model_subword_segmentation_performed"], False)
        self.assertIs(boundary["numeric_token_ids_created"], False)
        self.assertIs(boundary["calls_llm"], False)
        self.assertIs(boundary["embedding_performed"], False)
        self.assertIs(boundary["vector_retrieval_performed"], False)
        self.assert_no_repository_files()

    def test_typed_status_provider_returns_manifest_and_echo_pass(self) -> None:
        calls: list[str] = []

        def status_provider() -> dict[str, object]:
            calls.append("status")
            return {
                "status": "OK",
                "source": "injected_forge_status",
                "data": {
                    "trust": 5,
                    "cmd_count": 857,
                    "tool_count": 770,
                    "session_id": "forge_test_session",
                },
            }

        research_trap = _CallTrap("research provider")
        response = self._answer_without_promoted_exact(
            "What is Forge status?",
            status_provider=status_provider,
            research_provider=ResearchProvider(
                search=research_trap.search,
                capture=research_trap.capture,
                provider_id="must-not-run",
            ),
        )

        self.assertEqual(calls, ["status"])
        self.assertEqual(research_trap.calls, 0)
        self.assertEqual(response["status"], "ANSWERED")
        self.assertEqual(response["answer_kind"], "typed_capability")
        self.assertEqual(response["route"], "typed_forge_status_capability")
        capability = response["capability_result"]
        self.assertEqual(capability["manifest"]["result_type"], "forge_runtime_status")
        self.assertIs(capability["manifest"]["read_only"], True)
        self.assertEqual(capability["manifest"]["facts"]["forge_status"], "OK")
        self.assertEqual(capability["echo"]["status"], "PASS")
        self.assertIs(capability["echo"]["facts_preserved"], True)
        self.assertIn("857 commands", response["response_text"])
        self.assertIn("770 tools", response["response_text"])
        self.assert_no_repository_files()

    def test_typed_math_provider_returns_verified_receipt(self) -> None:
        calls: list[str] = []

        def math_provider(source_text: str) -> dict[str, object]:
            calls.append(source_text)
            return {
                "status": "ANSWERED",
                "answer_text": "4",
                "result_hash": "math_result:test-two-plus-two",
                "reasons": [],
                "input_preserved": source_text,
                "read_only": True,
            }

        research_trap = _CallTrap("research provider")
        response = self._answer_without_promoted_exact(
            "Calculate 2 + 2.",
            math_provider=math_provider,
            research_provider=ResearchProvider(
                search=research_trap.search,
                capture=research_trap.capture,
                provider_id="must-not-run",
            ),
        )

        self.assertEqual(calls, ["Calculate 2 + 2."])
        self.assertEqual(research_trap.calls, 0)
        self.assertEqual(response["status"], "ANSWERED")
        self.assertEqual(response["answer_kind"], "typed_capability")
        self.assertEqual(response["route"], "symbolic_math")
        self.assertEqual(response["response_text"], "4")
        capability = response["capability_result"]
        self.assertEqual(capability["receipt"]["result_hash"], "math_result:test-two-plus-two")
        self.assertEqual(capability["source_refs"], ["math_result:test-two-plus-two"])
        echo_stages = [
            row for row in response["stages"] if row["stage_key"] == "echo"
        ]
        self.assertEqual(len(echo_stages), 1)
        self.assertEqual(echo_stages[0]["status"], "PASS")
        self.assertIs(response["boundary"]["runs_unapproved_tools"], False)
        self.assert_no_repository_files()

    def test_build_request_returns_governed_plan_without_execution(self) -> None:
        research_trap = _CallTrap("research provider")
        response = self._answer_without_promoted_exact(
            "Build a Python API.",
            research_provider=ResearchProvider(
                search=research_trap.search,
                capture=research_trap.capture,
                provider_id="must-not-run",
            ),
            persist_candidates=False,
        )

        self.assertEqual(research_trap.calls, 0)
        self.assertEqual(response["status"], "PLANNED")
        self.assertEqual(response["answer_kind"], "governed_build_plan")
        self.assertEqual(response["route"], "software_build_request")
        plan = response["capability_result"]["plan"]
        self.assertEqual(plan["status"], "PLAN_READY_MISSING_GENERAL_CODE_RENDERER")
        self.assertIs(plan["execution_authorized"], False)
        self.assertIs(plan["patch_write_authorized"], False)
        self.assertIs(plan["operator_decision_required_before_apply"], True)
        self.assertIn("operator_approval", plan["stages"])
        self.assertIs(response["possible_answer_manifest"]["canonical"], False)
        self.assertIs(response["possible_answer_manifest"]["stable_memory"], False)
        self.assertEqual(response["echo"]["status"], "PASS")
        boundary = response["boundary"]
        self.assertIs(boundary["executes_shell"], False)
        self.assertIs(boundary["applies_code"], False)
        self.assertIs(boundary["runs_unapproved_tools"], False)
        self.assert_no_repository_files()

    def test_web_answer_is_candidate_only_and_retention_is_idempotent(self) -> None:
        calls: list[tuple[str, str]] = []

        def search(query: str) -> tuple[dict[str, object], ...]:
            calls.append(("search", query))
            return (
                {
                    "search_result_id": "web_search_result:test-france",
                    "url": "https://example.test/france",
                    "title": "France reference",
                },
            )

        def capture(
            query: str,
            search_result: dict[str, object],
        ) -> dict[str, object]:
            calls.append(("capture", query))
            self.assertEqual(
                search_result["search_result_id"],
                "web_search_result:test-france",
            )
            return {
                "source_receipt_id": "web_source_receipt:test-france",
                "requested_url": "https://example.test/france",
                "final_url": "https://example.test/france",
                "title": "France reference",
                "excerpt": "Paris is the capital and most populous city of France.",
                "excerpt_sha256": "sha256:test-france-excerpt",
                "resonance_score": 0.99,
                "evidence_rank_score": 0.99,
                "matched_source_forms": ("capital", "france"),
                "exact_excerpt_from_source": True,
                "candidate_evidence_only": True,
                "canonical": False,
            }

        response = self._answer_without_promoted_exact(
            "What is the capital of France?",
            research_provider=ResearchProvider(
                search=search,
                capture=capture,
                provider_id="injected-research-v1",
            ),
        )

        self.assertEqual(
            calls,
            [
                ("search", "What is the capital of France?"),
                ("capture", "What is the capital of France?"),
            ],
        )
        self.assertEqual(response["status"], "ANSWERED")
        self.assertEqual(response["answer_kind"], "possible_answer_candidate")
        self.assertEqual(
            response["response_text"],
            "Paris is the capital and most populous city of France.",
        )
        self.assertEqual(response["echo"]["status"], "PASS")
        self.assertIs(response["echo"]["exact_claim_or_plan_match"], True)
        self.assertIs(response["echo"]["candidate_boundary_preserved"], True)
        self.assertIs(response["research_acquisition"]["canonical"], False)
        self.assertIs(
            response["research_acquisition"]["candidate_evidence_only"],
            True,
        )

        manifest = response["possible_answer_manifest"]
        self.assertIs(manifest["possible_answer_only"], True)
        self.assertIs(manifest["stable_memory"], False)
        self.assertIs(manifest["canonical"], False)
        self.assertIs(manifest["truth_claim_finalized"], False)
        self.assertIs(
            manifest["operator_review_required_for_canonical_promotion"],
            True,
        )
        self.assertEqual(manifest["lifecycle_state"], "observed_candidate")
        self.assertIs(response["sources"][0]["canonical"], False)

        retention = response["candidate_retention"]
        self.assertIs(retention["candidate_written"], True)
        self.assertIs(retention["candidate_present"], True)
        self.assertIs(retention["writes_candidate_memory"], True)
        self.assertIs(retention["writes_stable_memory"], False)
        self.assertIs(retention["writes_canonical_memory"], False)
        expected_prefix = "memory/rmc_candidate_answers_v1/candidates/"
        self.assertTrue(str(retention["relative_path"]).startswith(expected_prefix))

        files = [
            path for path in self.repository_root.rglob("*") if path.is_file()
        ]
        self.assertEqual(len(files), 1)
        candidate_path = files[0]
        self.assertEqual(
            candidate_path.parent,
            self.repository_root
            / "memory"
            / "rmc_candidate_answers_v1"
            / "candidates",
        )
        persisted = json.loads(candidate_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["manifest_id"], manifest["manifest_id"])
        self.assertIs(persisted["canonical"], False)
        self.assertIs(persisted["stable_memory"], False)

        duplicate = persist_possible_answer_candidate(
            manifest,
            repository_root=self.repository_root,
        )
        self.assertIs(duplicate["candidate_written"], False)
        self.assertIs(duplicate["candidate_present"], True)
        self.assertIs(duplicate["writes_candidate_memory"], False)
        self.assertIs(duplicate["writes_stable_memory"], False)
        self.assertIs(duplicate["writes_canonical_memory"], False)
        self.assertEqual(
            len([path for path in self.repository_root.rglob("*") if path.is_file()]),
            1,
        )

        # A later identical question must use the retained candidate during
        # the memory-first stage instead of searching or fetching again.
        repeated = self._answer_without_promoted_exact(
            "What is the capital of France?",
            research_provider=ResearchProvider(
                search=search,
                capture=capture,
                provider_id="injected-research-v1",
            ),
        )
        self.assertEqual(len(calls), 2)
        self.assertIsNone(repeated["research_acquisition"])
        self.assertEqual(repeated["status"], "ANSWERED")
        self.assertEqual(repeated["response_text"], response["response_text"])
        self.assertIs(
            repeated["candidate_retention"]["reused_existing_candidate"],
            True,
        )
        self.assertIs(repeated["candidate_retention"]["candidate_written"], False)
        self.assertEqual(
            len([path for path in self.repository_root.rglob("*") if path.is_file()]),
            1,
        )

    def test_network_disabled_returns_needs_evidence_without_provider_call(self) -> None:
        research_trap = _CallTrap("research provider")
        response = self._answer_without_promoted_exact(
            "Who was Ada Lovelace?",
            research_provider=ResearchProvider(
                search=research_trap.search,
                capture=research_trap.capture,
                provider_id="must-not-run",
            ),
            allow_network=False,
            persist_candidates=False,
        )

        self.assertEqual(research_trap.calls, 0)
        self.assertEqual(response["status"], "NEEDS_EVIDENCE")
        self.assertEqual(response["answer_kind"], "insufficient_evidence")
        self.assertEqual(response["reason_code"], "no_governed_answer_evidence_found")
        self.assertIsNone(response["research_acquisition"])
        self.assertEqual(response["echo"]["status"], "PASS")
        research_stages = [
            row
            for row in response["stages"]
            if row["stage_key"] == "research_acquisition"
        ]
        self.assertEqual(len(research_stages), 1)
        self.assertEqual(research_stages[0]["status"], "NETWORK_DISABLED")
        self.assertIs(response["possible_answer_manifest"]["canonical"], False)
        self.assertIs(response["possible_answer_manifest"]["stable_memory"], False)
        self.assert_no_repository_files()

    def test_private_url_is_rejected_before_network_fetch(self) -> None:
        private_result = {
            "search_result_id": "web_search_result:test-private",
            "url": "http://127.0.0.1/private",
            "title": "Private target",
        }
        provider = ResearchProvider(
            search=lambda _: (private_result,),
            capture=lambda query, row: capture_public_page_evidence(query, row),
            provider_id="private-url-rejection-test",
        )

        acquisition = acquire_research_evidence(
            "What is on the private target?",
            provider=provider,
        )

        self.assertEqual(acquisition["status"], "NO_EVIDENCE_CAPTURED")
        self.assertEqual(acquisition["evidence_count"], 0)
        self.assertEqual(acquisition["error_count"], 1)
        self.assertEqual(acquisition["errors"][0]["stage"], "capture")
        self.assertEqual(acquisition["errors"][0]["reason_code"], "ValueError")
        self.assertIn(
            "research_private_or_non_global_target_blocked",
            acquisition["errors"][0]["detail"],
        )
        self.assertIs(acquisition["canonical"], False)
        self.assertIs(acquisition["candidate_evidence_only"], True)
        self.assertIs(acquisition["boundary"]["private_network_targets_blocked"], True)
        self.assertIs(acquisition["boundary"]["writes_files"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
