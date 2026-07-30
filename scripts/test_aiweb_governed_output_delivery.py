#!/usr/bin/env python3
"""Focused behavior and adversarial checks for governed output delivery evidence."""

from __future__ import annotations

import argparse
import builtins
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request
from unittest.mock import patch


class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str, detail: object = "") -> None:
        self.checks += 1
        if condition is not True:
            message = label
            if detail not in (None, ""):
                message += ": " + repr(detail)[:1200]
            self.failures.append(message)
            print("FAIL - " + message)


def _forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("forbidden external effect attempted")


def _reidentify(value: object, field: str) -> object:
    pending = replace(value, **{field: "pending"})
    return replace(pending, **{field: pending.expected_id()})


def _all_items(value: object):
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key), nested
            yield from _all_items(nested)
    elif isinstance(value, (tuple, list)):
        for nested in value:
            yield from _all_items(nested)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))
    ledger = Ledger()

    from aiweb_language_core_bootstrap.governed_output_delivery import (
        CONTROLLED_RESTATEMENT_TRANSITION,
        DEFINITION_RESPONSE_TRANSITION,
        ClarificationReentryStatus,
        ExactEchoStatus,
        GovernedOutputValidationError,
        OutputPurpose,
        build_clarification_reentry,
        build_exact_output_echo,
        build_governed_output_manifest,
        render_governed_output,
        validate_clarification_reentry_receipt,
        validate_clarification_reentry_result,
        validate_exact_output_echo,
        validate_governed_output_manifest,
        validate_rendered_output_candidate,
    )
    import aiweb_language_core_bootstrap.governed_output_delivery as public_api
    import aiweb_language_core_bootstrap.governed_output_delivery.exact_echo as echo_module
    from aiweb_language_core_bootstrap.governed_semantic_charter import (
        proposed_semantic_charter,
    )
    from aiweb_language_core_bootstrap.meaning_compiler_preview import (
        build_governed_clarification_request,
        build_rmc_context_record,
        build_rmc_context_snapshot,
        compile_meaning_preview,
        semantic_contract_for_candidate,
        validate_candidate_wording,
        validate_governed_clarification_request,
    )
    from aiweb_language_core_bootstrap.operator_council import (
        convene_operator_council,
    )

    import_order = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from aiweb_language_core_bootstrap.governed_output_delivery "
                "import build_clarification_reentry, build_exact_output_echo; "
                "from aiweb_language_core_bootstrap.meaning_compiler_preview "
                "import compile_meaning_preview, build_governed_clarification_request; "
                "r=compile_meaning_preview('What is core?'); "
                "assert build_governed_clarification_request(r) is not None"
            ),
        ],
        cwd=repository,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    ledger.check(
        import_order.returncode == 0,
        "governed-output-first import order has no cycle",
        import_order.stdout,
    )

    def supported_result(source_text: str):
        initial = compile_meaning_preview(source_text)
        selected = initial.selected_meaning
        if selected is None:
            raise AssertionError("fixture did not produce a unique initial meaning")
        contract = semantic_contract_for_candidate(
            selected,
            initial.frame_candidates,
        )
        record = build_rmc_context_record(
            semantic_contract_refs=(contract.semantic_contract_id,),
            concept_refs=tuple(sorted({role.concept_ref for role in selected.roles})),
            relation_refs=selected.relation_refs,
            ancestry_refs=selected.ancestry_refs,
        )
        result = compile_meaning_preview(
            source_text,
            rmc_snapshot=build_rmc_context_snapshot((record,)),
        )
        selected = result.selected_meaning
        if selected is None:
            raise AssertionError("supported fixture did not select")
        contract = semantic_contract_for_candidate(
            selected,
            result.frame_candidates,
        )
        resonances = tuple(
            resonance
            for resonance in result.rmc_context.resonances
            if resonance.meaning_candidate_ref == selected.meaning_candidate_id
            and resonance.exact_semantic_contract_refs
            == (contract.semantic_contract_id,)
            and set(resonance.exact_concept_refs)
            == {role.concept_ref for role in selected.roles}
            and set(resonance.exact_relation_refs) == set(selected.relation_refs)
        )
        if not resonances:
            raise AssertionError("fixture lacks exact structured resonance")
        evidence = {
            "selected_meaning_ref": selected.meaning_candidate_id,
            "semantic_signature": selected.semantic_signature,
            "speech_act": selected.speech_act,
            "purport": selected.purport,
            "predicate_ref": selected.predicate_ref,
            "concept_refs": tuple(
                sorted({role.concept_ref for role in selected.roles})
            ),
            "relation_refs": selected.relation_refs,
            "ancestry_refs": selected.ancestry_refs,
            "gate_receipt_refs": tuple(gate.gate_id for gate in selected.gates),
            "gates_passed": True,
            "echo_receipt_ref": result.echo.echo_id,
            "echo_status": "PASS",
            "rmc_snapshot_ref": result.rmc_context.snapshot.snapshot_id,
            "rmc_connection_status": (
                result.rmc_context.snapshot.connection_status
            ),
            "selected_meaning_support_status": "EXACT_SUPPORT",
            "rmc_evidence_refs": tuple(
                sorted(
                    (contract.semantic_contract_id,)
                    + tuple(item.resonance_id for item in resonances)
                )
            ),
            "authority_evidence_refs": tuple(
                sorted((result.boundary.boundary_id, result.receipt.receipt_id))
            ),
            "contradiction_refs": (),
            "uncertainty_refs": (),
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
        council = convene_operator_council(evidence)
        return result, council

    expected_outputs = {
        "define_language_core": (
            "Language Core means the provisional Forge component that compiles "
            "source forms into symbolic meaning candidates."
        ),
        "define_rmc": (
            "RMC Memory means the read-only resonance context layer identified "
            "as RMC in this preview."
        ),
        "inspect_manifest": "Please inspect the manifest.",
        "report_status": "Can Forge report the status?",
        "forge_uses_rmc": "Forge uses RMC Memory.",
        "forge_does_not_use_vector_memory": (
            "Forge does not use the vector Memory."
        ),
        "forge_is_system": "Forge is a system.",
        "compare_rmc_and_vector_memory": (
            "Compare RMC Memory and vector Memory."
        ),
    }
    answer_fixtures = {"define_language_core", "define_rmc"}
    charter = proposed_semantic_charter()
    ledger.check(len(charter.replay_fixtures) == 8, "charter exposes eight fixtures")
    ledger.check(
        {fixture.fixture_key for fixture in charter.replay_fixtures}
        == set(expected_outputs),
        "fixture matrix exact",
    )
    built: dict[str, tuple[object, object, object, object, object]] = {}
    for fixture in charter.replay_fixtures:
        key = fixture.fixture_key
        compiled, council = supported_result(fixture.exact_source_text)
        manifest = build_governed_output_manifest(compiled, council)
        rendered = render_governed_output(manifest, compiled, council)
        echo = build_exact_output_echo(rendered, manifest, compiled, council)
        built[key] = (compiled, council, manifest, rendered, echo)
        expected_answer = key in answer_fixtures
        expected_purpose = (
            OutputPurpose.DEFINITION_ANSWER
            if expected_answer
            else OutputPurpose.CONTROLLED_RESTATEMENT_PREVIEW
        )
        ledger.check(manifest.manifest_id == manifest.expected_id(), key + " manifest ID")
        ledger.check(manifest.output_purpose is expected_purpose, key + " purpose")
        ledger.check(
            manifest.answer_delivery_eligible is expected_answer,
            key + " manifest answer eligibility",
        )
        ledger.check(
            manifest.transition_rule_ref
            == (
                DEFINITION_RESPONSE_TRANSITION
                if expected_answer
                else CONTROLLED_RESTATEMENT_TRANSITION
            ),
            key + " transition rule",
        )
        ledger.check(
            validate_governed_output_manifest(manifest, compiled, council) == (),
            key + " manifest validates",
        )
        ledger.check(
            rendered.text == expected_outputs[key],
            key + " exact deterministic output",
            rendered.text,
        )
        ledger.check(
            rendered.text_sha256
            == hashlib.sha256(rendered.text.encode("utf-8")).hexdigest(),
            key + " output hash",
        )
        ledger.check(
            rendered.code_point_length == len(rendered.text)
            and rendered.utf8_byte_length == len(rendered.text.encode("utf-8")),
            key + " output lengths",
        )
        ledger.check(
            validate_rendered_output_candidate(
                rendered,
                manifest,
                compiled,
                council,
            )
            == (),
            key + " renderer validates",
        )
        ledger.check(echo.status is ExactEchoStatus.PASS, key + " exact Echo passes")
        ledger.check(echo.transition_admitted is True, key + " transition admitted")
        ledger.check(echo.exact_contract_match is True, key + " contract exact")
        ledger.check(echo.exact_role_match is True, key + " roles exact")
        ledger.check(echo.exact_relation_match is True, key + " relations exact")
        ledger.check(
            echo.answer_delivery_eligible is expected_answer,
            key + " Echo answer eligibility",
        )
        ledger.check(
            echo.answer_delivery_authorized is False
            and echo.answer_delivery_performed is False,
            key + " Echo grants no delivery authority",
        )
        ledger.check(
            validate_exact_output_echo(
                echo,
                rendered,
                manifest,
                compiled,
                council,
            )
            == (),
            key + " exact Echo validates",
        )
        replay_manifest = build_governed_output_manifest(compiled, council)
        replay_rendered = render_governed_output(
            replay_manifest,
            compiled,
            council,
        )
        replay_echo = build_exact_output_echo(
            replay_rendered,
            replay_manifest,
            compiled,
            council,
        )
        ledger.check(
            (replay_manifest, replay_rendered, replay_echo)
            == (manifest, rendered, echo),
            key + " full chain deterministic replay",
        )
        for field_name, field_value in _all_items((manifest, rendered, echo)):
            if field_name in {
                "normalization_performed",
                "tokenization_performed",
                "model_token_stream_created",
                "subword_token_stream_created",
                "numeric_token_ids_created",
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
                "answer_delivery_authorized",
                "answer_delivery_performed",
                "delivery_authorized",
                "delivery_performed",
            }:
                ledger.check(
                    field_value is False,
                    key + " forbidden capability remains false: " + field_name,
                    field_value,
                )

    definition_compiled, definition_council, definition_manifest, definition_rendered, definition_echo = built[
        "define_language_core"
    ]
    tampered_manifest = replace(
        definition_manifest,
        output_purpose=OutputPurpose.CONTROLLED_RESTATEMENT_PREVIEW,
        answer_delivery_eligible=False,
    )
    tampered_manifest = _reidentify(tampered_manifest, "manifest_id")
    ledger.check(
        bool(
            validate_governed_output_manifest(
                tampered_manifest,
                definition_compiled,
                definition_council,
            )
        ),
        "reidentified manifest purpose tamper rejected",
    )
    reordered_manifest = replace(
        definition_manifest,
        compiler_stage_refs=tuple(reversed(definition_manifest.compiler_stage_refs)),
    )
    reordered_manifest = _reidentify(reordered_manifest, "manifest_id")
    ledger.check(
        bool(
            validate_governed_output_manifest(
                reordered_manifest,
                definition_compiled,
                definition_council,
            )
        ),
        "reidentified compiler stage reorder rejected",
    )
    altered_source_contract = replace(
        definition_manifest.source_semantic_contract,
        speech_act="statement",
    )
    altered_source_contract = _reidentify(
        altered_source_contract,
        "semantic_contract_id",
    )
    nested_manifest = replace(
        definition_manifest,
        source_semantic_contract=altered_source_contract,
    )
    nested_manifest = _reidentify(nested_manifest, "manifest_id")
    ledger.check(
        bool(
            validate_governed_output_manifest(
                nested_manifest,
                definition_compiled,
                definition_council,
            )
        ),
        "reidentified nested semantic contract tamper rejected",
    )

    altered_text = definition_rendered.text + " "
    altered_render = replace(
        definition_rendered,
        text=altered_text,
        text_sha256=hashlib.sha256(altered_text.encode("utf-8")).hexdigest(),
        code_point_length=len(altered_text),
        utf8_byte_length=len(altered_text.encode("utf-8")),
    )
    altered_render = _reidentify(altered_render, "rendered_output_id")
    ledger.check(
        bool(
            validate_rendered_output_candidate(
                altered_render,
                definition_manifest,
                definition_compiled,
                definition_council,
            )
        ),
        "reidentified output text tamper rejected",
    )
    altered_echo = replace(definition_echo, transition_admitted=False)
    altered_echo = _reidentify(altered_echo, "echo_id")
    ledger.check(
        bool(
            validate_exact_output_echo(
                altered_echo,
                definition_rendered,
                definition_manifest,
                definition_compiled,
                definition_council,
            )
        ),
        "reidentified Echo transition tamper rejected",
    )

    # The legacy signature-only validator admits this request as equivalent to
    # the input definition request.  Full-contract Echo must reject it because
    # it is still a request, not the declared definition response.
    selected_definition = definition_compiled.selected_meaning
    ledger.check(selected_definition is not None, "definition candidate selected")
    if selected_definition is not None:
        wrong_question = "What is language core?"
        legacy_echo = validate_candidate_wording(
            meaning_candidate=selected_definition,
            wording_text=wrong_question,
        )
        ledger.check(
            legacy_echo.status.value == "PASS",
            "regression fixture demonstrates signature-only collision",
        )
        encoded = wrong_question.encode("utf-8")
        wrong_render = replace(
            definition_rendered,
            text=wrong_question,
            text_sha256=hashlib.sha256(encoded).hexdigest(),
            code_point_length=len(wrong_question),
            utf8_byte_length=len(encoded),
        )
        wrong_render = _reidentify(wrong_render, "rendered_output_id")
        full_echo = echo_module._expected_echo(
            wrong_render,
            definition_manifest,
        )
        ledger.check(full_echo.status is ExactEchoStatus.REJECT, "full Echo rejects request/request collision")
        ledger.check(full_echo.exact_contract_match is False, "full Echo detects speech-act contract mismatch")
        ledger.check(full_echo.transition_admitted is False, "full Echo rejects undeclared transition")
        ledger.check(
            full_echo.answer_delivery_eligible is False
            and full_echo.answer_delivery_authorized is False,
            "failed Echo cannot become answer eligible",
        )

        for bad_text, label in (
            (
                "Language Core does not mean the provisional Forge component that "
                "compiles source forms into symbolic meaning candidates.",
                "negation change",
            ),
            (
                "Languаge Core means the provisional Forge component that compiles "
                "source forms into symbolic meaning candidates.",
                "Unicode confusable",
            ),
        ):
            bad_encoded = bad_text.encode("utf-8")
            bad_render = replace(
                definition_rendered,
                text=bad_text,
                text_sha256=hashlib.sha256(bad_encoded).hexdigest(),
                code_point_length=len(bad_text),
                utf8_byte_length=len(bad_encoded),
            )
            bad_render = _reidentify(bad_render, "rendered_output_id")
            bad_echo = echo_module._expected_echo(bad_render, definition_manifest)
            ledger.check(bad_echo.status is ExactEchoStatus.REJECT, label + " rejected")
            ledger.check(bad_echo.answer_delivery_eligible is False, label + " not eligible")

    original = compile_meaning_preview("What is core?")
    clarification = build_governed_clarification_request(original)
    ledger.check(clarification is not None, "ambiguous source creates clarification")
    if clarification is not None:
        ledger.check(
            validate_governed_clarification_request(clarification, original) == (),
            "original clarification validates",
        )
        accepted_receipts = []
        for clarified_text, expected_label in (
            ("What is Forge Core?", "Forge Core"),
            ("What is language core?", "Language Core"),
        ):
            reentry = build_clarification_reentry(
                original,
                clarification,
                clarified_text,
            )
            ledger.check(
                reentry.status is ClarificationReentryStatus.ACCEPTED,
                clarified_text + " accepted",
                reentry.reason_codes,
            )
            ledger.check(reentry.receipt is not None, clarified_text + " receipt created")
            ledger.check(
                validate_clarification_reentry_result(
                    reentry,
                    original,
                    clarification,
                )
                == (),
                clarified_text + " re-entry validates",
            )
            if reentry.receipt is not None:
                accepted_receipts.append(reentry.receipt)
                option = next(
                    item
                    for item in clarification.options
                    if item.option_id == reentry.receipt.matched_option_ref
                )
                ledger.check(option.option_label == expected_label, clarified_text + " matched exact option")
                ledger.check(
                    reentry.receipt.original_option_refs
                    == tuple(item.option_id for item in clarification.options),
                    clarified_text + " preserves every original option",
                )
                ledger.check(
                    validate_clarification_reentry_receipt(
                        reentry.receipt,
                        original,
                        clarification,
                        reentry.clarified_compiler_result,
                    )
                    == (),
                    clarified_text + " receipt validates",
                )
                ledger.check(
                    reentry.receipt.operator_option_selection_performed is False
                    and reentry.receipt.answer_delivery_authorized is False
                    and reentry.receipt.memory_write_performed is False,
                    clarified_text + " receipt grants no authority",
                )
        for held_text, expected_reason in (
            ("What is RMC?", "clarified_meaning_not_original_alternative"),
            ("What is core?", "clarified_meaning_not_preview_ready"),
            ("Language Core", "clarified_meaning_not_preview_ready"),
        ):
            held = build_clarification_reentry(
                original,
                clarification,
                held_text,
            )
            ledger.check(held.status is ClarificationReentryStatus.HELD, held_text + " held")
            ledger.check(held.receipt is None, held_text + " creates no receipt")
            ledger.check(expected_reason in held.reason_codes, held_text + " reason exact")
            ledger.check(
                held.compiler_selection_performed is False
                and held.operator_option_selection_performed is False,
                held_text + " performs no selection",
            )
            ledger.check(
                validate_clarification_reentry_result(
                    held,
                    original,
                    clarification,
                )
                == (),
                held_text + " held result validates",
            )

        if accepted_receipts:
            accepted = build_clarification_reentry(
                original,
                clarification,
                "What is language core?",
            )
            receipt = accepted.receipt
            assert receipt is not None
            other_option = next(
                item
                for item in clarification.options
                if item.option_id != receipt.matched_option_ref
            )
            tampered_receipt = replace(
                receipt,
                matched_option_ref=other_option.option_id,
                matched_original_meaning_ref=other_option.meaning_candidate_ref,
                matched_semantic_contract_ref=other_option.semantic_contract_ref,
            )
            tampered_receipt = _reidentify(tampered_receipt, "receipt_id")
            ledger.check(
                bool(
                    validate_clarification_reentry_receipt(
                        tampered_receipt,
                        original,
                        clarification,
                        accepted.clarified_compiler_result,
                    )
                ),
                "reidentified matched-option receipt tamper rejected",
            )
            reordered_receipt = replace(
                receipt,
                original_option_refs=tuple(reversed(receipt.original_option_refs)),
            )
            reordered_receipt = _reidentify(reordered_receipt, "receipt_id")
            ledger.check(
                bool(
                    validate_clarification_reentry_receipt(
                        reordered_receipt,
                        original,
                        clarification,
                        accepted.clarified_compiler_result,
                    )
                ),
                "reidentified alternative order tamper rejected",
            )
            changed_initial = compile_meaning_preview("What is language core?")
            changed_selected = changed_initial.selected_meaning
            assert changed_selected is not None
            changed_contract = semantic_contract_for_candidate(
                changed_selected,
                changed_initial.frame_candidates,
            )
            changed_record = build_rmc_context_record(
                semantic_contract_refs=(changed_contract.semantic_contract_id,),
                concept_refs=tuple(
                    sorted({role.concept_ref for role in changed_selected.roles})
                ),
                relation_refs=changed_selected.relation_refs,
                ancestry_refs=changed_selected.ancestry_refs,
            )
            changed_result = compile_meaning_preview(
                "What is language core?",
                rmc_snapshot=build_rmc_context_snapshot((changed_record,)),
            )
            ledger.check(
                bool(
                    validate_clarification_reentry_receipt(
                        receipt,
                        original,
                        clarification,
                        changed_result,
                    )
                ),
                "changed RMC snapshot rejects clarification receipt",
            )
        truncated_request = replace(
            clarification,
            options=clarification.options[:-1],
            alternative_meaning_refs=clarification.alternative_meaning_refs[:-1],
            alternative_count=clarification.alternative_count - 1,
        )
        truncated_request = _reidentify(
            truncated_request,
            "clarification_request_id",
        )
        ledger.check(
            bool(validate_governed_clarification_request(truncated_request, original)),
            "reidentified dropped clarification alternative rejected",
        )
        try:
            build_clarification_reentry(original, truncated_request, "What is Forge Core?")
        except GovernedOutputValidationError:
            ledger.check(True, "tampered clarification fails closed")
        else:
            ledger.check(False, "tampered clarification fails closed")

    # Frozen records must not permit in-place mutation.
    try:
        definition_manifest.status = "MUTATED"
    except (FrozenInstanceError, AttributeError):
        ledger.check(True, "manifest is immutable")
    else:
        ledger.check(False, "manifest is immutable")

    # The package deliberately exports no action that approves, delivers,
    # writes, promotes, or registers a route.
    forbidden_public_prefixes = ("approve", "deliver", "write", "promote", "route")
    ledger.check(
        not any(
            name.lower().startswith(forbidden_public_prefixes)
            for name in public_api.__all__
        ),
        "public API exposes no authority action",
        public_api.__all__,
    )

    # Re-run representative pure builders with external-effect entry points
    # trapped after all imports and subprocess checks are complete.
    with ExitStack() as stack:
        stack.enter_context(patch.object(builtins, "open", _forbidden))
        stack.enter_context(patch.object(os, "open", _forbidden))
        stack.enter_context(patch.object(os, "getenv", _forbidden))
        stack.enter_context(patch.object(socket, "create_connection", _forbidden))
        stack.enter_context(patch.object(subprocess, "run", _forbidden))
        stack.enter_context(patch.object(urllib.request, "urlopen", _forbidden))
        stack.enter_context(patch.object(Path, "open", _forbidden))
        stack.enter_context(patch.object(Path, "read_text", _forbidden))
        stack.enter_context(patch.object(Path, "write_text", _forbidden))
        try:
            pure_manifest = build_governed_output_manifest(
                definition_compiled,
                definition_council,
            )
            pure_rendered = render_governed_output(
                pure_manifest,
                definition_compiled,
                definition_council,
            )
            pure_echo = build_exact_output_echo(
                pure_rendered,
                pure_manifest,
                definition_compiled,
                definition_council,
            )
            pure_reentry = build_clarification_reentry(
                original,
                clarification,
                "What is Forge Core?",
            ) if clarification is not None else None
        except Exception as error:
            ledger.check(False, "pure package avoids external effects", error)
        else:
            ledger.check(
                pure_echo.status is ExactEchoStatus.PASS
                and pure_reentry is not None
                and pure_reentry.status is ClarificationReentryStatus.ACCEPTED,
                "pure package avoids external effects",
            )

    print(f"checks={ledger.checks}")
    if ledger.failures:
        print(f"failures={len(ledger.failures)}")
        print("RESULT=FAIL")
        return 1
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
