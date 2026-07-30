#!/usr/bin/env python3
"""Acceptance and adversarial tests for the bounded semantic charter."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

import aiweb_language_core_bootstrap.governed_semantic_charter as package
from aiweb_language_core_bootstrap.governed_semantic_charter import (
    CharterReplayStatus,
    CharterSourceDisposition,
    CharterStatus,
    PROPOSED_SEMANTIC_CHARTER,
    SemanticCharterValidationError,
    assert_valid_semantic_charter,
    build_proposed_semantic_charter,
    evaluate_source_against_charter,
    replay_semantic_charter,
    validate_semantic_charter,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview import (
    compile_meaning_preview,
)


EXPECTED_SOURCES = (
    "What does language core mean?",
    "What is RMC?",
    "Please inspect the manifest.",
    "Can Forge report status?",
    "Forge uses RMC memory.",
    "Forge does not use vector memory.",
    "Forge is a system.",
    "Compare RMC memory and vector memory.",
)

EXPECTED_CONCEPT_KEYS = (
    "forge",
    "language_core",
    "rmc_memory",
    "vector_memory",
    "system",
    "status",
    "manifest",
)

EXPECTED_PREDICATE_KEYS = (
    "mean",
    "inspect",
    "report",
    "use",
    "be",
    "compare",
)

EXPECTED_ROLE_KEYS = (
    "actor",
    "subject",
    "object",
    "definition_target",
    "comparison_left",
    "comparison_right",
)

EXPECTED_CONSTRUCTION_SHAPES = {
    "definition_do": (
        "FORGE-GRAMMAR-V0-DEFINITION-DO",
        "mean",
        ("definition_target",),
        False,
    ),
    "definition_copula": (
        "FORGE-GRAMMAR-V0-DEFINITION-COPULA",
        "mean",
        ("definition_target",),
        False,
    ),
    "governed_definition_response": (
        "FORGE-GRAMMAR-V0-GOVERNED-DEFINITION-RESPONSE",
        "mean",
        ("definition_target",),
        False,
    ),
    "imperative_inspect": (
        "FORGE-GRAMMAR-V0-IMPERATIVE",
        "inspect",
        ("object",),
        False,
    ),
    "modal_report": (
        "FORGE-GRAMMAR-V0-MODAL",
        "report",
        ("actor", "object"),
        False,
    ),
    "positive_use": (
        "FORGE-GRAMMAR-V0-POSITIVE",
        "use",
        ("actor", "object"),
        False,
    ),
    "negative_use": (
        "FORGE-GRAMMAR-V0-NEGATIVE-DO",
        "use",
        ("actor", "object"),
        True,
    ),
    "copula_anchor_positive": (
        "FORGE-GRAMMAR-V0-COPULA-ANCHOR",
        "be",
        ("subject", "object"),
        False,
    ),
    "compare_rmc_designs": (
        "FORGE-GRAMMAR-V0-COMPARE",
        "compare",
        ("comparison_left", "comparison_right"),
        False,
    ),
}


def _reidentify(record: object, id_field: str, **changes: object) -> object:
    pending = replace(record, **{id_field: "pending", **changes})
    return replace(pending, **{id_field: pending.expected_id()})


def _reidentify_charter(**changes: object) -> object:
    return _reidentify(PROPOSED_SEMANTIC_CHARTER, "charter_id", **changes)


def _all_keys(value: object) -> set[str]:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for nested in value.values():
            keys.update(_all_keys(nested))
        return keys
    if isinstance(value, (tuple, list)):
        keys: set[str] = set()
        for nested in value:
            keys.update(_all_keys(nested))
        return keys
    return set()


class GovernedSemanticCharterTests(unittest.TestCase):
    def test_packaged_charter_is_exact_small_proposal(self) -> None:
        charter = PROPOSED_SEMANTIC_CHARTER
        self.assertEqual(charter.status, CharterStatus.PROPOSED_FOR_OPERATOR_APPROVAL)
        self.assertEqual(
            charter.registry_ref,
            (
                "forge_preview_registry:"
                "eba54768ad3c5e10d0e370be39e41c0b77ccc41a2163c5de028b2bd77a4eb770"
            ),
        )
        self.assertEqual(
            tuple(item.concept_key for item in charter.concept_senses),
            EXPECTED_CONCEPT_KEYS,
        )
        self.assertEqual(
            tuple(item.predicate_key for item in charter.predicates),
            EXPECTED_PREDICATE_KEYS,
        )
        self.assertEqual(
            tuple(item.role_key for item in charter.roles), EXPECTED_ROLE_KEYS
        )
        self.assertNotIn("requester", {item.role_key for item in charter.roles})
        self.assertEqual(len(charter.constructions), 9)
        self.assertEqual(
            tuple(item.exact_source_text for item in charter.replay_fixtures),
            EXPECTED_SOURCES,
        )
        self.assertEqual(charter.charter_id, charter.expected_id())
        self.assertFalse(validate_semantic_charter(charter))
        self.assertIs(assert_valid_semantic_charter(charter), charter)

    def test_every_nested_record_is_content_addressed(self) -> None:
        charter = PROPOSED_SEMANTIC_CHARTER
        records = (
            *charter.concept_senses,
            *charter.predicates,
            *charter.roles,
            *charter.constructions,
            *charter.replay_fixtures,
            charter.boundary,
        )
        for record in records:
            identifiers = (
                "proposal_id",
                "construction_id",
                "fixture_id",
                "boundary_id",
            )
            actual = next(getattr(record, name) for name in identifiers if hasattr(record, name))
            self.assertEqual(actual, record.expected_id())
        self.assertEqual(
            len({item.proposal_id for item in charter.concept_senses}), 7
        )
        self.assertEqual(len({item.fixture_id for item in charter.replay_fixtures}), 8)

    def test_constructions_capture_effective_roles_not_only_predicate_minima(self) -> None:
        observed = {
            item.construction_key: (
                item.grammar_rule_id,
                item.predicate_key,
                item.effective_role_keys,
                item.negated,
            )
            for item in PROPOSED_SEMANTIC_CHARTER.constructions
        }
        self.assertEqual(observed, EXPECTED_CONSTRUCTION_SHAPES)
        modal = next(
            item
            for item in PROPOSED_SEMANTIC_CHARTER.constructions
            if item.construction_key == "modal_report"
        )
        report = next(
            item
            for item in PROPOSED_SEMANTIC_CHARTER.predicates
            if item.predicate_key == "report"
        )
        self.assertEqual(report.declared_required_role_keys, ("object",))
        self.assertEqual(modal.effective_role_keys, ("actor", "object"))
        response = next(
            item
            for item in PROPOSED_SEMANTIC_CHARTER.constructions
            if item.construction_key == "governed_definition_response"
        )
        self.assertTrue(response.echo_reparse_only)
        self.assertTrue(
            all(
                item.exact_fixture_only
                for item in PROPOSED_SEMANTIC_CHARTER.constructions
            )
        )
        self.assertTrue(
            all(
                not item.runtime_active
                for item in PROPOSED_SEMANTIC_CHARTER.constructions
            )
        )

    def test_all_eight_semantic_replays_match_exact_current_identities(self) -> None:
        replay = replay_semantic_charter()
        self.assertEqual(replay.status, CharterReplayStatus.PASS)
        self.assertEqual(len(replay.case_results), 8)
        self.assertTrue(all(item.passed for item in replay.case_results))
        self.assertTrue(all(item.construction_matched for item in replay.case_results))
        self.assertTrue(all(item.semantic_identity_matched for item in replay.case_results))
        self.assertTrue(all(item.exact_reference_sets_matched for item in replay.case_results))
        self.assertTrue(all(not item.operator_approval_granted for item in replay.case_results))
        self.assertTrue(all(not item.runtime_authority for item in replay.case_results))
        fixture_ids = {
            item.fixture_id: item.expected_meaning_candidate_ref
            for item in PROPOSED_SEMANTIC_CHARTER.replay_fixtures
        }
        self.assertEqual(
            tuple(item.observed_meaning_candidate_ref for item in replay.case_results),
            tuple(fixture_ids[item.fixture_ref] for item in replay.case_results),
        )
        self.assertEqual(replay.replay_id, replay.expected_id())

    def test_replay_is_deterministic(self) -> None:
        first = replay_semantic_charter()
        second = replay_semantic_charter()
        self.assertEqual(first, second)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(build_proposed_semantic_charter(), PROPOSED_SEMANTIC_CHARTER)

    def test_exact_fixture_match_remains_only_a_proposal_match(self) -> None:
        for source in EXPECTED_SOURCES:
            evaluation = evaluate_source_against_charter(source)
            self.assertEqual(
                evaluation.disposition,
                CharterSourceDisposition.MATCHED_PROPOSED_FIXTURE,
            )
            self.assertTrue(evaluation.proposed_match_only)
            self.assertTrue(evaluation.fixture_ref)
            self.assertFalse(evaluation.operator_approval_granted)
            self.assertFalse(evaluation.runtime_authority)
            self.assertFalse(evaluation.memory_write_performed)
            self.assertFalse(evaluation.action_performed)
            self.assertFalse(evaluation.delivery_performed)
            self.assertEqual(evaluation.evaluation_id, evaluation.expected_id())

    def test_broad_a_and_b_registry_sentences_are_outside_charter(self) -> None:
        for source in (
            "Please begin the batch.",
            "Forge balances the budget.",
        ):
            compiler = compile_meaning_preview(source)
            self.assertEqual(compiler.status.value, "PREVIEW_READY")
            evaluation = evaluate_source_against_charter(source)
            self.assertEqual(
                evaluation.disposition,
                CharterSourceDisposition.OUTSIDE_PROPOSED_CHARTER,
            )
            self.assertEqual(evaluation.compiler_status, "PREVIEW_READY")
            self.assertIn(
                "exact_source_not_in_proposed_charter",
                evaluation.compiler_reason_codes,
            )
            self.assertFalse(evaluation.proposed_match_only)
            self.assertFalse(evaluation.selected_meaning_ref == "")

    def test_case_variant_is_not_silently_added_to_exact_proposal(self) -> None:
        variant = "forge uses rmc memory."
        self.assertEqual(compile_meaning_preview(variant).status.value, "PREVIEW_READY")
        evaluation = evaluate_source_against_charter(variant)
        self.assertEqual(
            evaluation.disposition,
            CharterSourceDisposition.OUTSIDE_PROPOSED_CHARTER,
        )

    def test_core_polysemy_remains_held(self) -> None:
        evaluation = evaluate_source_against_charter("What does core mean?")
        self.assertEqual(
            evaluation.disposition, CharterSourceDisposition.HELD_AMBIGUOUS
        )
        self.assertEqual(evaluation.compiler_status, "HELD")
        self.assertEqual(evaluation.meaning_candidate_count, 2)
        self.assertFalse(evaluation.selected_meaning_ref)
        self.assertIn(
            "ambiguous_meaning_requires_clarification",
            evaluation.compiler_reason_codes,
        )

    def test_non_text_source_is_invalid_without_guessing(self) -> None:
        evaluation = evaluate_source_against_charter({"source_text": "Forge"})
        self.assertEqual(evaluation.disposition, CharterSourceDisposition.INVALID_INPUT)
        self.assertFalse(evaluation.compiler_result_ref)
        self.assertFalse(evaluation.selected_meaning_ref)

    def test_source_hashes_are_exact_utf8_hashes(self) -> None:
        for fixture in PROPOSED_SEMANTIC_CHARTER.replay_fixtures:
            self.assertEqual(
                fixture.exact_source_sha256,
                hashlib.sha256(fixture.exact_source_text.encode("utf-8")).hexdigest(),
            )

    def test_tampered_registry_reference_rejected_even_with_new_outer_id(self) -> None:
        tampered = _reidentify_charter(
            registry_ref="forge_preview_registry:" + ("0" * 64)
        )
        issues = validate_semantic_charter(tampered)
        self.assertIn(
            "charter:registry_ref_does_not_match_installed_registry", issues
        )
        self.assertIn("charter:does_not_match_packaged_proposal", issues)
        with self.assertRaises(SemanticCharterValidationError):
            replay_semantic_charter(tampered)

    def test_tampered_effective_role_shape_rejected(self) -> None:
        original = PROPOSED_SEMANTIC_CHARTER.constructions[4]
        tampered_construction = _reidentify(
            original, "construction_id", effective_role_keys=("object",)
        )
        constructions = (
            *PROPOSED_SEMANTIC_CHARTER.constructions[:4],
            tampered_construction,
            *PROPOSED_SEMANTIC_CHARTER.constructions[5:],
        )
        tampered = _reidentify_charter(constructions=constructions)
        issues = validate_semantic_charter(tampered)
        self.assertIn("charter:does_not_match_packaged_proposal", issues)
        self.assertTrue(
            any(
                "unknown_construction_ref" in issue
                or "effective_role_shape_mismatch" in issue
                for issue in issues
            ),
            issues,
        )

    def test_tampered_semantic_signature_rejected(self) -> None:
        original = PROPOSED_SEMANTIC_CHARTER.replay_fixtures[0]
        tampered_fixture = _reidentify(
            original,
            "fixture_id",
            expected_semantic_signature="semantic_signature:" + ("0" * 64),
        )
        fixtures = (
            tampered_fixture,
            *PROPOSED_SEMANTIC_CHARTER.replay_fixtures[1:],
        )
        tampered = _reidentify_charter(replay_fixtures=fixtures)
        self.assertIn(
            "charter:does_not_match_packaged_proposal",
            validate_semantic_charter(tampered),
        )

    def test_mapping_or_self_declared_active_value_is_rejected(self) -> None:
        self.assertEqual(
            validate_semantic_charter(PROPOSED_SEMANTIC_CHARTER.to_dict()),
            ("charter:must_be_exact_proposed_semantic_charter",),
        )
        tampered = _reidentify_charter(
            active=True,
            operator_approval_present=True,
            canonical_authority=True,
            runtime_authority=True,
        )
        issues = validate_semantic_charter(tampered)
        self.assertIn("charter:active_must_remain_false", issues)
        self.assertIn("charter:canonical_authority_must_remain_false", issues)
        self.assertIn("charter:runtime_authority_must_remain_false", issues)

    def test_malformed_nested_collections_fail_closed(self) -> None:
        malformed = _reidentify_charter(
            concept_senses=None,
            predicates={"mean": "forged"},
            constructions=("FORGE-GRAMMAR-V0-POSITIVE",),
            replay_fixtures=(),
            boundary={"active": True},
        )
        issues = validate_semantic_charter(malformed)
        self.assertIn("concept_senses:must_be_tuple", issues)
        self.assertIn("predicates:must_be_tuple", issues)
        self.assertIn("constructions:contains_wrong_record_type", issues)
        self.assertIn("replay_fixtures:unexpected_count", issues)
        self.assertIn("boundary:must_be_exact_semantic_charter_boundary", issues)
        with self.assertRaises(SemanticCharterValidationError):
            assert_valid_semantic_charter(malformed)

    def test_charter_and_nested_records_are_frozen(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            PROPOSED_SEMANTIC_CHARTER.active = True
        with self.assertRaises(FrozenInstanceError):
            PROPOSED_SEMANTIC_CHARTER.constructions[0].runtime_active = True

    def test_boundary_is_closed_and_no_approval_api_is_exported(self) -> None:
        charter = PROPOSED_SEMANTIC_CHARTER
        self.assertTrue(charter.boundary.forge_owned)
        self.assertTrue(charter.boundary.proposal_only)
        self.assertTrue(charter.boundary.operator_approval_required)
        false_fields = (
            "operator_approval_present",
            "active",
            "canonical_authority",
            "truth_authority",
            "selection_authority",
            "runtime_authority",
            "route_authority",
            "tool_authority",
            "action_authority",
            "delivery_authority",
            "memory_write_authority",
            "external_reference_authority",
            "tokenization_performed",
            "model_called",
            "embedding_used",
            "vector_used",
            "similarity_scoring_used",
            "filesystem_read_performed",
            "filesystem_write_performed",
            "network_access_performed",
            "environment_access_performed",
            "memory_read_performed",
            "memory_write_performed",
            "route_registration_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
        )
        self.assertTrue(all(getattr(charter.boundary, field) is False for field in false_fields))
        for name in ("approve", "activate", "promote", "write_rmc", "install_route"):
            self.assertFalse(hasattr(package, name))

    def test_records_have_no_model_token_embedding_or_vector_stream(self) -> None:
        forbidden = {
            "tokens",
            "token_ids",
            "model_tokens",
            "subword_tokens",
            "vocabulary_ids",
            "embeddings",
            "vectors",
            "next_token",
        }
        keys = _all_keys(PROPOSED_SEMANTIC_CHARTER)
        self.assertFalse(forbidden.intersection(keys), forbidden.intersection(keys))
        json.dumps(PROPOSED_SEMANTIC_CHARTER.to_dict(), ensure_ascii=False, sort_keys=True)

    def test_replay_attempts_no_io_execution_or_environment_access(self) -> None:
        with ExitStack() as stack:
            stack.enter_context(
                patch("builtins.open", side_effect=AssertionError("filesystem"))
            )
            stack.enter_context(
                patch.object(Path, "write_text", side_effect=AssertionError("write"))
            )
            stack.enter_context(
                patch.object(Path, "write_bytes", side_effect=AssertionError("write"))
            )
            stack.enter_context(
                patch.object(os, "open", side_effect=AssertionError("filesystem"))
            )
            stack.enter_context(
                patch.object(os, "getenv", side_effect=AssertionError("environment"))
            )
            stack.enter_context(
                patch.object(socket, "socket", side_effect=AssertionError("network"))
            )
            stack.enter_context(
                patch.object(subprocess, "Popen", side_effect=AssertionError("process"))
            )
            replay = replay_semantic_charter()
        self.assertEqual(replay.status, CharterReplayStatus.PASS)
        self.assertFalse(replay.filesystem_write_performed)
        self.assertFalse(replay.memory_write_performed)
        self.assertFalse(replay.route_registration_performed)
        self.assertFalse(replay.tool_routing_performed)
        self.assertFalse(replay.action_performed)
        self.assertFalse(replay.delivery_performed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
