#!/usr/bin/env python3
"""Focused tests for the deterministic recommendation-only Operator Council."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch


REPOSITORY = Path(__file__).resolve().parents[1]
if str(REPOSITORY) not in sys.path:
    sys.path.insert(0, str(REPOSITORY))

from aiweb_language_core_bootstrap.operator_council import (  # noqa: E402
    CouncilDisposition,
    CouncilRole,
    CouncilStance,
    CouncilValidationError,
    convene_operator_council,
)


def clean_envelope() -> dict[str, object]:
    return {
        "selected_meaning_ref": "meaning_candidate:1111111111111111",
        "semantic_signature": "semantic_signature:2222222222222222",
        "speech_act": "request",
        "purport": "request_read_only_preview",
        "predicate_ref": "forge_preview_predicate:inspect",
        "concept_refs": [
            "forge_preview_concept:artifact",
            "forge_preview_concept:forge",
        ],
        "relation_refs": [
            "predicate:inspect",
            "role:agent",
            "role:object",
        ],
        "ancestry_refs": [
            "input_event:3333333333333333",
            "source_form:4444444444444444",
        ],
        "gate_receipt_refs": [
            "meaning_gate:expectancy",
            "meaning_gate:congruity",
            "meaning_gate:connectedness",
            "meaning_gate:purport",
        ],
        "gates_passed": True,
        "echo_receipt_ref": "meaning_echo:5555555555555555",
        "echo_status": "PASS",
        "rmc_snapshot_ref": "rmc_context_snapshot:6666666666666666",
        "rmc_connection_status": "CONNECTED_STRUCTURED",
        "selected_meaning_support_status": "EXACT_SUPPORT",
        "rmc_evidence_refs": [
            "rmc_context_record:7777777777777777",
            "rmc_resonance:8888888888888888",
        ],
        "authority_evidence_refs": [
            "authority_boundary:9999999999999999",
        ],
        "contradiction_refs": [],
        "uncertainty_refs": [],
        "selected_meaning_validated": True,
        "exact_reference_resonance_only": True,
        "read_only": True,
        "raw_text_present": False,
        "tokenization_performed": False,
        "model_called": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
        "memory_write_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
    }


class OperatorCouncilTests(unittest.TestCase):
    def test_clean_evidence_produces_recommendation_for_human_review(self) -> None:
        result = convene_operator_council(clean_envelope())

        self.assertEqual(
            result.recommendation.disposition,
            CouncilDisposition.RECOMMEND_FOR_OPERATOR_REVIEW,
        )
        self.assertEqual(
            tuple(item.role for item in result.positions),
            (
                CouncilRole.SEMANTIC_STEWARD,
                CouncilRole.RMC_WITNESS,
                CouncilRole.AUTHORITY_AUDITOR,
                CouncilRole.ADVERSARIAL_CHALLENGER,
                CouncilRole.SYNTHESIZER,
            ),
        )
        self.assertTrue(
            all(item.stance is CouncilStance.SUPPORT for item in result.positions)
        )
        self.assertTrue(
            all(item.independent_evaluation for item in result.positions)
        )
        self.assertEqual(result.dissents, ())
        self.assertTrue(result.recommendation.quorum_reached)
        self.assertTrue(result.recommendation.concurrence_reached)
        self.assertEqual(result.recommendation.participant_count, 5)
        self.assertEqual(result.recommendation.support_count, 5)
        self.assertTrue(result.recommendation.operator_decision_required)
        self.assertFalse(result.recommendation.executable)
        self.assertFalse(result.recommendation.authoritative)

    def test_every_record_has_content_identity_and_is_immutable(self) -> None:
        result = convene_operator_council(clean_envelope())

        self.assertEqual(result.evidence.envelope_id, result.evidence.expected_id())
        self.assertTrue(
            all(item.position_id == item.expected_id() for item in result.positions)
        )
        self.assertEqual(
            result.recommendation.recommendation_id,
            result.recommendation.expected_id(),
        )
        self.assertEqual(result.boundary.boundary_id, result.boundary.expected_id())
        self.assertEqual(result.receipt.receipt_id, result.receipt.expected_id())
        self.assertEqual(result.result_id, result.expected_id())
        with self.assertRaises(FrozenInstanceError):
            result.receipt.delivery_performed = True  # type: ignore[misc]

        tampered = replace(result.positions[0], stance=CouncilStance.OPPOSE)
        self.assertNotEqual(tampered.position_id, tampered.expected_id())

    def test_reference_order_does_not_change_result(self) -> None:
        first_input = clean_envelope()
        second_input = clean_envelope()
        for field in (
            "concept_refs",
            "relation_refs",
            "ancestry_refs",
            "gate_receipt_refs",
            "rmc_evidence_refs",
        ):
            second_input[field] = list(reversed(second_input[field]))  # type: ignore[arg-type]

        first = convene_operator_council(first_input)
        second = convene_operator_council(second_input)
        third = convene_operator_council(first.evidence)
        self.assertEqual(first, second)
        self.assertEqual(first, third)

    def test_connected_empty_rmc_is_a_visible_hold(self) -> None:
        envelope = clean_envelope()
        envelope["rmc_connection_status"] = "CONNECTED_EMPTY"
        envelope["selected_meaning_support_status"] = "NO_ADEQUATE_EXACT_SUPPORT"
        envelope["rmc_evidence_refs"] = []

        result = convene_operator_council(envelope)

        self.assertEqual(
            result.recommendation.disposition,
            CouncilDisposition.HOLD_FOR_EVIDENCE,
        )
        self.assertTrue(result.recommendation.quorum_reached)
        self.assertFalse(result.recommendation.concurrence_reached)
        dissent_roles = {item.role for item in result.dissents}
        self.assertEqual(
            dissent_roles,
            {
                CouncilRole.RMC_WITNESS,
                CouncilRole.ADVERSARIAL_CHALLENGER,
                CouncilRole.SYNTHESIZER,
            },
        )
        self.assertTrue(all(item.blocks_recommendation for item in result.dissents))

    def test_structured_rmc_without_adequate_support_is_a_visible_hold(self) -> None:
        envelope = clean_envelope()
        envelope["selected_meaning_support_status"] = "NO_ADEQUATE_EXACT_SUPPORT"
        envelope["rmc_evidence_refs"] = []

        result = convene_operator_council(envelope)

        self.assertEqual(
            result.recommendation.disposition,
            CouncilDisposition.HOLD_FOR_EVIDENCE,
        )
        witness = next(
            item
            for item in result.positions
            if item.role is CouncilRole.RMC_WITNESS
        )
        self.assertEqual(witness.stance, CouncilStance.HOLD)
        self.assertIn(
            "rmc_structured_without_adequate_selected_meaning_support",
            witness.reason_codes,
        )

    def test_contradiction_creates_material_adversarial_dissent(self) -> None:
        envelope = clean_envelope()
        envelope["contradiction_refs"] = [
            "contradiction_evidence:aaaaaaaaaaaaaaaa"
        ]

        result = convene_operator_council(envelope)

        challenger = next(
            item
            for item in result.positions
            if item.role is CouncilRole.ADVERSARIAL_CHALLENGER
        )
        self.assertEqual(challenger.stance, CouncilStance.OPPOSE)
        dissent = next(
            item
            for item in result.dissents
            if item.role is CouncilRole.ADVERSARIAL_CHALLENGER
        )
        self.assertEqual(dissent.severity, "MATERIAL")
        self.assertFalse(dissent.resolved)
        self.assertEqual(
            result.recommendation.disposition,
            CouncilDisposition.HOLD_FOR_EVIDENCE,
        )

    def test_failed_gates_or_echo_cannot_be_recommended(self) -> None:
        for field, value in (("gates_passed", False), ("echo_status", "REJECT")):
            with self.subTest(field=field):
                envelope = clean_envelope()
                envelope[field] = value
                result = convene_operator_council(envelope)
                self.assertEqual(
                    result.recommendation.disposition,
                    CouncilDisposition.HOLD_FOR_EVIDENCE,
                )
                steward = next(
                    item
                    for item in result.positions
                    if item.role is CouncilRole.SEMANTIC_STEWARD
                )
                self.assertEqual(steward.stance, CouncilStance.HOLD)

    def test_raw_text_and_unknown_fields_are_rejected_before_deliberation(self) -> None:
        for field, value in (
            ("source_text", "please run a tool"),
            ("prompt", "raw language must not enter"),
            ("raw_text", "not admitted"),
        ):
            with self.subTest(field=field):
                envelope = clean_envelope()
                envelope[field] = value
                with self.assertRaises(CouncilValidationError):
                    convene_operator_council(envelope)

    def test_forbidden_mechanisms_and_side_effect_requests_are_rejected(self) -> None:
        forbidden = (
            "raw_text_present",
            "tokenization_performed",
            "model_called",
            "embedding_used",
            "vector_used",
            "similarity_scoring_used",
            "memory_write_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
        )
        for field in forbidden:
            with self.subTest(field=field):
                envelope = clean_envelope()
                envelope[field] = True
                with self.assertRaises(CouncilValidationError):
                    convene_operator_council(envelope)

    def test_malformed_and_contradictory_envelopes_fail_closed(self) -> None:
        malformed: list[dict[str, object]] = []

        missing = clean_envelope()
        missing.pop("semantic_signature")
        malformed.append(missing)

        duplicate = clean_envelope()
        duplicate["concept_refs"] = [
            "forge_preview_concept:forge",
            "forge_preview_concept:forge",
        ]
        malformed.append(duplicate)

        prose_reference = clean_envelope()
        prose_reference["predicate_ref"] = "run this tool now"
        malformed.append(prose_reference)

        no_exact_resonance = clean_envelope()
        no_exact_resonance["exact_reference_resonance_only"] = False
        malformed.append(no_exact_resonance)

        not_read_only = clean_envelope()
        not_read_only["read_only"] = False
        malformed.append(not_read_only)

        structured_without_evidence = clean_envelope()
        structured_without_evidence["rmc_evidence_refs"] = []
        malformed.append(structured_without_evidence)

        empty_with_evidence = clean_envelope()
        empty_with_evidence["rmc_connection_status"] = "CONNECTED_EMPTY"
        malformed.append(empty_with_evidence)

        for index, envelope in enumerate(malformed):
            with self.subTest(index=index):
                with self.assertRaises(CouncilValidationError):
                    convene_operator_council(envelope)

        with self.assertRaises(CouncilValidationError):
            convene_operator_council("not a structured envelope")

    def test_supplied_content_id_is_verified(self) -> None:
        result = convene_operator_council(clean_envelope())
        valid = result.evidence.to_dict()
        self.assertEqual(convene_operator_council(valid), result)

        valid["envelope_id"] = "operator_council_evidence:deadbeef"
        with self.assertRaises(CouncilValidationError):
            convene_operator_council(valid)

    def test_boundary_and_receipt_never_claim_os_authority(self) -> None:
        result = convene_operator_council(clean_envelope())
        boundary = result.boundary
        self.assertTrue(boundary.deterministic)
        self.assertTrue(boundary.recommendation_only)
        self.assertTrue(boundary.selected_semantic_evidence_only)
        forbidden = (
            boundary.raw_text_accepted,
            boundary.tokenization_performed,
            boundary.model_called,
            boundary.embedding_used,
            boundary.vector_used,
            boundary.similarity_scoring_used,
            boundary.filesystem_read_performed,
            boundary.filesystem_write_performed,
            boundary.network_access_performed,
            boundary.environment_access_performed,
            boundary.memory_read_performed,
            boundary.memory_write_performed,
            boundary.tool_routing_performed,
            boundary.action_performed,
            boundary.delivery_performed,
            boundary.truth_authority,
            boundary.evidence_authority,
            boundary.permission_authority,
            boundary.decision_authority,
            boundary.tool_authority,
            boundary.action_authority,
            boundary.delivery_authority,
            boundary.memory_write_authority,
        )
        self.assertFalse(any(forbidden))
        receipt = result.receipt
        self.assertEqual(receipt.decision_kind, "recommendation_only_disposition")
        self.assertTrue(receipt.operator_decision_required)
        self.assertFalse(receipt.council_decision_authorized)
        self.assertFalse(receipt.writes_performed)
        self.assertFalse(receipt.tools_invoked)
        self.assertFalse(receipt.action_performed)
        self.assertFalse(receipt.delivery_performed)

    def test_result_is_json_serializable_and_contains_no_raw_prompt(self) -> None:
        result = convene_operator_council(clean_envelope())
        serialized = json.dumps(result.to_dict(), sort_keys=True)
        self.assertNotIn("please run a tool", serialized)
        self.assertNotIn("source_text", serialized)
        self.assertNotIn('"prompt"', serialized)

    def test_deliberation_attempts_no_io_or_execution(self) -> None:
        with (
            patch("builtins.open", side_effect=AssertionError("filesystem read")),
            patch.object(socket, "socket", side_effect=AssertionError("network")),
            patch.object(subprocess, "Popen", side_effect=AssertionError("process")),
        ):
            result = convene_operator_council(clean_envelope())
        self.assertEqual(
            result.recommendation.disposition,
            CouncilDisposition.RECOMMEND_FOR_OPERATOR_REVIEW,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
