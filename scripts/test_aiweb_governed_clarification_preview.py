#!/usr/bin/env python3
"""Behavior and adversarial checks for governed ambiguity clarification."""

from __future__ import annotations

import argparse
import builtins
from contextlib import ExitStack
from dataclasses import replace
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
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
                message += ": " + repr(detail)[:1400]
            self.failures.append(message)
            print("FAIL - " + message)


def _forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("forbidden external effect attempted")


def _all_keys(value: object) -> set[str]:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if isinstance(value, dict):
        return {str(key) for key in value} | {
            nested_key
            for nested in value.values()
            for nested_key in _all_keys(nested)
        }
    if isinstance(value, (tuple, list)):
        return {
            nested_key
            for nested in value
            for nested_key in _all_keys(nested)
        }
    return set()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))
    ledger = Ledger()

    from aiweb_language_core_bootstrap.meaning_compiler_preview import (
        CLARIFICATION_REASON,
        GOVERNED_CLARIFICATION_SCHEMA_VERSION,
        build_governed_clarification_request,
        build_rmc_context_record,
        build_rmc_context_snapshot,
        compile_meaning_preview,
        semantic_contract_for_candidate,
        validate_governed_clarification_request,
    )
    from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (
        forge_seed_registry,
    )
    from rmc_engine_v1.rmc_exact_language_store import (
        load_trusted_rmc_language_store,
    )
    import aiweb_language_core_bootstrap.meaning_compiler_preview.clarification as clarification_module
    import rmc_engine_v1.meaning_compiler_preview as adapter

    import_order = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from aiweb_language_core_bootstrap.meaning_compiler_preview.clarification "
                "import build_governed_clarification_request; "
                "from aiweb_language_core_bootstrap.meaning_compiler_preview.compiler "
                "import compile_meaning_preview; "
                "assert build_governed_clarification_request("
                "compile_meaning_preview('What is core?')) is not None; "
                "import rmc_engine_v1.operator_council_preview"
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
        "clarification-first import order has no cycle",
        import_order.stdout,
    )

    # Empty exact context leaves the deliberately polysemous surface ``core``
    # unresolved.  The compiler remains held and does not manufacture an
    # answer; the separate clarification projector preserves both candidates.
    source = "What is core?"
    result = compile_meaning_preview(source)
    request = build_governed_clarification_request(result)
    ledger.check(result.status.value == "HELD", "ambiguous compiler result held", result)
    ledger.check(
        CLARIFICATION_REASON in result.reasons,
        "ambiguity reason exact",
        result.reasons,
    )
    ledger.check(result.selected_meaning is None, "clarification does not select meaning")
    ledger.check(result.candidate_wording is None, "clarification does not create answer wording")
    ledger.check(request is not None, "governed clarification request created")
    if request is None:
        print("RESULT=FAIL")
        return 1

    ledger.check(
        request.schema_version == GOVERNED_CLARIFICATION_SCHEMA_VERSION,
        "clarification schema exact",
        request.to_dict(),
    )
    ledger.check(request.status == "CLARIFICATION_REQUIRED", "clarification status exact")
    ledger.check(request.reason_code == CLARIFICATION_REASON, "clarification reason exact")
    ledger.check(
        request.candidate_wording
        == "Please clarify the intended meaning: Forge Core or Language Core?",
        "bounded clarification wording exact",
        request.candidate_wording,
    )
    ledger.check(request.alternative_count == 2, "two alternatives retained")
    ledger.check(
        tuple(item.option_label for item in request.options)
        == ("Forge Core", "Language Core"),
        "governed option labels exact and deterministic",
        request.options,
    )

    admitted = tuple(
        item for item in result.meaning_candidates if item.all_gates_passed
    )
    ledger.check(len(admitted) == 2, "fixture has two admitted meanings")
    ledger.check(
        set(request.alternative_meaning_refs)
        == {item.meaning_candidate_id for item in admitted},
        "every admitted alternative preserved exactly",
        request.alternative_meaning_refs,
    )
    ledger.check(
        len(request.options) == len(request.alternative_meaning_refs)
        == request.alternative_count,
        "option counts agree",
    )
    registry = forge_seed_registry()
    concepts = {item.concept_id: item for item in registry.concepts}
    senses = {item.sense_id: item for item in registry.senses}
    admitted_by_id = {item.meaning_candidate_id: item for item in admitted}
    for option in request.options:
        candidate = admitted_by_id.get(option.meaning_candidate_ref)
        ledger.check(candidate is not None, "option cites admitted candidate", option)
        if candidate is None:
            continue
        contract = semantic_contract_for_candidate(candidate, result.frame_candidates)
        ledger.check(
            option.semantic_contract_ref == contract.semantic_contract_id,
            "option cites exact semantic contract",
            option,
        )
        ledger.check(
            option.semantic_signature_ref == candidate.semantic_signature,
            "option cites exact semantic signature",
            option,
        )
        ledger.check(
            option.frame_candidate_ref == candidate.frame_candidate_ref,
            "option cites exact frame",
            option,
        )
        ledger.check(option.option_id == option.expected_id(), "option identity content-addressed")
        ledger.check(option.selection_authority is False, "option grants no selection authority")
        ledger.check(bool(option.roles), "option preserves role/sense grounding")
        for role in option.roles:
            concept = concepts.get(role.concept_ref)
            sense = senses.get(role.sense_ref)
            ledger.check(
                concept is not None
                and sense is not None
                and sense.concept_ref == concept.concept_id,
                "clarification role has exact registry membership",
                role,
            )
            if concept is not None:
                ledger.check(
                    role.preferred_label == concept.preferred_label
                    and role.provisional_definition == concept.provisional_definition,
                    "clarification role wording is registry-owned",
                    role,
                )

    ledger.check(
        request.clarification_request_id == request.expected_id(),
        "clarification request identity content-addressed",
    )
    ledger.check(
        request.compiler_result_ref == result.result_id
        and request.compiler_receipt_ref == result.receipt.receipt_id,
        "clarification binds exact compiler result and receipt",
    )
    ledger.check(
        request.source_custody_ref == result.source_custody.custody_result_id
        and request.source_sha256 == result.source_custody.source_sha256,
        "clarification binds exact source custody",
    )
    ledger.check(
        request.rmc_context_ref == result.rmc_context.evaluation_id,
        "clarification binds insufficient exact context",
    )
    ledger.check(
        request.all_admitted_alternatives_preserved is True,
        "alternative-preservation assertion true",
    )
    ledger.check(request.preview_only is True, "clarification preview only")
    ledger.check(request.recommendation_only is True, "clarification recommendation only")
    ledger.check(request.operator_response_required is True, "operator response required")
    ledger.check(request.operator_preview_exposed is True, "operator preview exposure recorded")
    ledger.check(
        request.clarification_question_preview_exposed is True,
        "question preview exposure recorded",
    )
    ledger.check(request.resolution_required == "operator_clarification", "resolution is operator clarification")
    for field in (
        "live_clarification_session_started",
        "clarification_response_consumed",
        "selection_performed",
        "delivery_authorized",
        "delivery_performed",
        "answer_delivery_performed",
        "action_authorized",
        "tool_routing_authorized",
        "memory_write_authorized",
        "memory_write_performed",
    ):
        ledger.check(getattr(request, field) is False, "clarification false " + field)
    ledger.check(
        validate_governed_clarification_request(request, result) == (),
        "clarification validates",
    )
    ledger.check(
        build_governed_clarification_request(result) == request,
        "clarification replay deterministic",
    )
    for composed_ambiguity in (
        "Core is a system.",
        "Compare core and memory.",
        "Please inspect core.",
    ):
        composed_result = compile_meaning_preview(composed_ambiguity)
        composed_request = build_governed_clarification_request(composed_result)
        ledger.check(
            composed_request is not None
            and composed_request.candidate_wording
            == "Please clarify the intended meaning: Forge Core or Language Core?",
            "clarification wording isolates only the distinguishing sense: "
            + composed_ambiguity,
            composed_request,
        )

    # If future semantic contracts share one human label, their exact
    # contract/candidate identities must distinguish the question instead of
    # producing an unusable ``Core or Core`` choice.
    admitted_contracts = tuple(
        semantic_contract_for_candidate(candidate, result.frame_candidates)
        for candidate in admitted
    )
    collision_labels = clarification_module._distinguish_option_labels(
        ("Core", "Core"),
        admitted,
        admitted_contracts,
    )
    ledger.check(
        len(collision_labels) == len(set(collision_labels)) == 2,
        "same human labels receive deterministic semantic distinctions",
        collision_labels,
    )
    ledger.check(
        all(contract.semantic_contract_id in label for contract, label in zip(admitted_contracts, collision_labels)),
        "collision labels retain exact semantic contract identities",
        collision_labels,
    )
    ledger.check(
        json.dumps(
            json.loads(json.dumps(request.to_dict(), sort_keys=True)),
            sort_keys=True,
            separators=(",", ":"),
        )
        == json.dumps(
            request.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        ),
        "clarification JSON round trip deterministic",
    )
    forbidden_stream_fields = {
        "tokens",
        "token_ids",
        "model_tokens",
        "subword_tokens",
        "embeddings",
        "vectors",
        "similarity_score",
        "similarity_scores",
    }
    ledger.check(
        forbidden_stream_fields.isdisjoint(_all_keys(request)),
        "clarification contains no token/vector/similarity stream",
        forbidden_stream_fields.intersection(_all_keys(request)),
    )

    # Only material ambiguity is clarification-eligible.  Unknown forms,
    # unsupported grammar, held composition, and successful selections remain
    # exactly in their existing lanes.
    for non_clarification_source in (
        "",
        "What does bank mean?",
        "purple quickly maybe",
        "Please inspect the active manifest.",
        "What does language core mean?",
        "Forge uses RMC memory.",
    ):
        other = compile_meaning_preview(non_clarification_source)
        ledger.check(
            build_governed_clarification_request(other) is None,
            "non-ambiguity result gets no clarification: " + non_clarification_source,
            other,
        )

    # One complete semantic-contract witness still resolves the ambiguity by
    # the existing exact-RMC rule.  The clarification layer cannot override it.
    target = admitted[0]
    target_contract = semantic_contract_for_candidate(
        target,
        result.frame_candidates,
    )
    support = build_rmc_context_record(
        semantic_contract_refs=(target_contract.semantic_contract_id,),
        concept_refs=tuple(sorted({role.concept_ref for role in target.roles})),
        relation_refs=target.relation_refs,
        ancestry_refs=(),
    )
    supported = compile_meaning_preview(
        source,
        rmc_snapshot=build_rmc_context_snapshot(records=(support,)),
    )
    ledger.check(supported.status.value == "PREVIEW_READY", "exact RMC selection unchanged")
    ledger.check(
        supported.selected_meaning is not None
        and supported.selected_meaning.semantic_signature == target.semantic_signature,
        "exact RMC selects the witnessed meaning",
        supported,
    )
    ledger.check(
        build_governed_clarification_request(supported) is None,
        "exact-RMC selection suppresses clarification",
    )

    # Verify the user's currently promoted eight-record provider as a separate
    # integration pair when it is installed.  ``What does core mean?`` has an
    # exact promoted contract; the copular variant does not, so it must still
    # ask instead of borrowing partial identity overlap.
    promoted_provider = load_trusted_rmc_language_store()
    promoted_pair_verified = False
    if (
        promoted_provider.load_status == "TRUSTED_STRUCTURED"
        and promoted_provider.stable_record_count
        + promoted_provider.live_record_count
        >= 8
    ):
        live_ambiguous = compile_meaning_preview(
            "What is core?",
            rmc_snapshot=promoted_provider.snapshot,
        )
        live_clarification = build_governed_clarification_request(live_ambiguous)
        live_resolved = compile_meaning_preview(
            "What does core mean?",
            rmc_snapshot=promoted_provider.snapshot,
        )
        ledger.check(
            live_ambiguous.status.value == "HELD"
            and live_clarification is not None
            and live_clarification.alternative_count == 2,
            "promoted provider retains unsupported copular core ambiguity",
            live_ambiguous,
        )
        ledger.check(
            live_resolved.status.value == "PREVIEW_READY"
            and "unique_exact_rmc_resonance" in live_resolved.reasons
            and build_governed_clarification_request(live_resolved) is None,
            "promoted provider resolves only the exact supported core contract",
            live_resolved,
        )
        live_surface_ambiguous = adapter.build_language_core_preview_response(
            {"source_text": "What is core?"}
        )
        live_surface_resolved = adapter.build_language_core_preview_response(
            {"source_text": "What does core mean?"}
        )
        ledger.check(
            live_surface_ambiguous.get("status") == "HELD"
            and (live_surface_ambiguous.get("clarification_request") or {}).get(
                "status"
            )
            == "CLARIFICATION_REQUIRED",
            "actual promoted Ask Forge surface exposes clarification",
            live_surface_ambiguous,
        )
        ledger.check(
            live_surface_resolved.get("status") == "PREVIEW_READY"
            and live_surface_resolved.get("reason_code")
            == "unique_exact_rmc_resonance"
            and live_surface_resolved.get("clarification_request") is None,
            "actual promoted Ask Forge surface preserves exact resolution",
            live_surface_resolved,
        )
        promoted_pair_verified = True

    # Tampering is detectable and cannot convert a held projection into
    # authority or remove an alternative while retaining a valid identity.
    tampered_id = replace(request, clarification_request_id="governed_clarification_request:tampered")
    ledger.check(
        "clarification_request_id_content_mismatch"
        in validate_governed_clarification_request(tampered_id, result),
        "tampered request identity rejected",
    )
    dropped = replace(
        request,
        options=request.options[:-1],
        alternative_meaning_refs=request.alternative_meaning_refs[:-1],
        alternative_count=1,
    )
    ledger.check(
        bool(validate_governed_clarification_request(dropped, result)),
        "dropped alternative rejected",
    )
    authority = replace(request, action_authorized=True)
    ledger.check(
        "clarification_authority_or_effect_enabled"
        in validate_governed_clarification_request(authority, result),
        "authority escalation rejected",
    )
    altered_wording = replace(request, candidate_wording="Choose Forge Core.")
    ledger.check(
        bool(validate_governed_clarification_request(altered_wording, result)),
        "selection-biased wording rejected",
    )
    ledger.check(
        validate_governed_clarification_request(request, supported)
        == ("compiler_result_not_clarification_eligible",),
        "clarification cannot be rebound to selected result",
    )

    # A typed dataclass is not automatically trusted.  Every upstream custody,
    # gate, authority, RMC, Echo, boundary, receipt, and result-identity
    # mutation must fail deterministic replay before a safe-looking
    # clarification can mask it.
    first_candidate = result.meaning_candidates[0]
    tampered_compiler_results = {
        "candidate selection authority": replace(
            result,
            meaning_candidates=(
                replace(first_candidate, selection_authority=True),
                *result.meaning_candidates[1:],
            ),
        ),
        "candidate preview boundary": replace(
            result,
            meaning_candidates=(
                replace(first_candidate, preview_only=False),
                *result.meaning_candidates[1:],
            ),
        ),
        "failed gate hidden by aggregate": replace(
            result,
            meaning_candidates=(
                replace(
                    first_candidate,
                    gates=(
                        replace(first_candidate.gates[0], passed=False),
                        *first_candidate.gates[1:],
                    ),
                ),
                *result.meaning_candidates[1:],
            ),
        ),
        "RMC memory write": replace(
            result,
            rmc_context=replace(result.rmc_context, memory_write_performed=True),
        ),
        "wrong nested RMC type": replace(result, rmc_context=None),
        "wrong nested custody type": replace(result, source_custody=None),
        "Echo delivery authority": replace(
            result,
            echo=replace(result.echo, delivery_authorized=True),
        ),
        "compiler boundary action": replace(
            result,
            boundary=replace(result.boundary, action_performed=True),
        ),
        "receipt delivery": replace(
            result,
            receipt=replace(result.receipt, delivery_performed=True),
        ),
        "receipt identity": replace(
            result,
            receipt=replace(result.receipt, receipt_id="meaning_preview_receipt:tampered"),
        ),
        "result identity": replace(
            result,
            result_id="meaning_compiler_preview_result:tampered",
        ),
        "source text": replace(result, source_text="What is tampered?"),
        "source SHA": replace(
            result,
            source_custody=replace(result.source_custody, source_sha256="0" * 64),
        ),
        "source custody identity": replace(
            result,
            source_custody=replace(
                result.source_custody,
                custody_result_id="input_event_capture_result:tampered",
            ),
        ),
        "source custody mechanisms": replace(
            result,
            source_custody=replace(
                result.source_custody,
                tokenization_performed=True,
            ),
        ),
        "source preservation assertion": replace(
            result,
            source_custody=replace(
                result.source_custody,
                source_preserved_exactly=False,
            ),
        ),
    }
    for label, tampered_result in tampered_compiler_results.items():
        rejected = False
        try:
            build_governed_clarification_request(tampered_result)
        except (TypeError, ValueError):
            rejected = True
        ledger.check(rejected, "tampered compiler result rejected: " + label)
        ledger.check(
            bool(validate_governed_clarification_request(request, tampered_result)),
            "tampered compiler result does not validate: " + label,
        )

    # The public Ask Forge adapter exposes the structured request and binds it
    # into its integrated receipt while keeping answer fields empty.
    with tempfile.TemporaryDirectory(prefix="forge-clarification-test-", dir="/tmp") as temporary:
        empty_provider = load_trusted_rmc_language_store(temporary)
        ledger.check(empty_provider.load_status == "TRUSTED_EMPTY", "empty provider trusted")
        with patch.object(adapter, "_TRUSTED_RMC_PROVIDER", empty_provider):
            first = adapter.build_language_core_preview_response({"source_text": source})
            second = adapter.build_language_core_preview_response({"source_text": source})
            unique = adapter.build_language_core_preview_response(
                {"source_text": "What does language core mean?"}
            )
    public = first.get("clarification_request") or {}
    ledger.check(first == second, "public clarification response deterministic")
    ledger.check(first.get("status") == "HELD", "public compiler status remains held")
    ledger.check(first.get("reason_code") == CLARIFICATION_REASON, "public reason exact")
    ledger.check(first.get("selected_meaning") is None, "public ambiguity has no selected meaning")
    ledger.check(first.get("candidate_wording") is None, "public ambiguity has no answer wording")
    ledger.check(public == request.to_dict(), "public clarification is exact compiler projection", public)
    ledger.check(public.get("status") == "CLARIFICATION_REQUIRED", "public clarification status exact")
    ledger.check(
        (first.get("receipt") or {}).get("clarification_request_ref")
        == public.get("clarification_request_id"),
        "integrated receipt binds clarification request",
        first.get("receipt"),
    )
    ledger.check(
        (first.get("receipt") or {}).get("operator_preview_exposed") is True
        and (first.get("receipt") or {}).get(
            "clarification_question_preview_exposed"
        )
        is True
        and (first.get("receipt") or {}).get(
            "live_clarification_session_started"
        )
        is False
        and (first.get("receipt") or {}).get("clarification_response_consumed")
        is False
        and (first.get("receipt") or {}).get("answer_delivery_performed") is False,
        "integrated receipt distinguishes preview exposure from live delivery",
        first.get("receipt"),
    )
    stages = tuple(first.get("stages", ()))
    clarification_stages = tuple(
        item
        for item in stages
        if item.get("label") == "Governed clarification preview"
    )
    ledger.check(len(clarification_stages) == 1, "one clarification trace stage exposed")
    ledger.check(
        (clarification_stages[0].get("evidence") or {}).get("selection_performed")
        is False,
        "clarification trace records no selection",
    )
    ledger.check(
        unique.get("status") == "PREVIEW_READY"
        and unique.get("clarification_request") is None,
        "successful public preview remains free of clarification",
        unique,
    )
    ledger.check(
        "clarification_request_ref" not in (unique.get("receipt") or {}),
        "successful receipt shape is not changed by null clarification",
    )

    # Once imported and supplied a compiler result, projection performs no
    # filesystem, network, subprocess, environment, or write operation.
    with ExitStack() as stack:
        stack.enter_context(patch.object(builtins, "open", _forbidden))
        stack.enter_context(patch.object(Path, "open", _forbidden))
        stack.enter_context(patch.object(Path, "read_text", _forbidden))
        stack.enter_context(patch.object(Path, "read_bytes", _forbidden))
        stack.enter_context(patch.object(Path, "write_text", _forbidden))
        stack.enter_context(patch.object(Path, "write_bytes", _forbidden))
        stack.enter_context(patch.object(socket, "socket", _forbidden))
        stack.enter_context(patch.object(socket, "create_connection", _forbidden))
        stack.enter_context(patch.object(subprocess, "run", _forbidden))
        stack.enter_context(patch.object(subprocess, "Popen", _forbidden))
        stack.enter_context(patch.object(urllib.request, "urlopen", _forbidden))
        stack.enter_context(patch.object(os, "getenv", _forbidden))
        trapped = build_governed_clarification_request(result)
    ledger.check(trapped == request, "clarification runs under external-effect traps")

    with patch.object(
        adapter,
        "build_governed_clarification_request",
        side_effect=ValueError("forced"),
    ):
        contained = adapter.build_language_core_preview_response(
            {"source_text": "What does language core mean?"}
        )
    ledger.check(contained.get("status") == "ERROR", "clarification exception contained")
    ledger.check(
        contained.get("reason_code")
        == "governed_clarification_preview_failed_closed",
        "clarification failure reason typed",
        contained,
    )
    for malformed in ({}, object()):
        with patch.object(
            adapter,
            "build_governed_clarification_request",
            return_value=malformed,
        ):
            malformed_contained = adapter.build_language_core_preview_response(
                {"source_text": "What is core?"}
            )
        ledger.check(
            malformed_contained.get("status") == "ERROR"
            and malformed_contained.get("reason_code")
            == "governed_clarification_preview_failed_closed",
            "malformed clarification return contained: " + type(malformed).__name__,
            malformed_contained,
        )
    with patch.object(
        adapter,
        "compile_meaning_preview",
        return_value=tampered_compiler_results["result identity"],
    ):
        tampered_compile_contained = adapter.build_language_core_preview_response(
            {"source_text": source}
        )
    ledger.check(
        tampered_compile_contained.get("status") == "ERROR"
        and tampered_compile_contained.get("reason_code")
        == "governed_clarification_preview_failed_closed",
        "adapter rejects tampered compiler result before clarification exposure",
        tampered_compile_contained,
    )

    print("AI.WEB GOVERNED CLARIFICATION PREVIEW")
    print(f"checks={ledger.checks}")
    print(f"failures={len(ledger.failures)}")
    print("ambiguous_source=" + source)
    print("clarification_status=CLARIFICATION_REQUIRED")
    print("promoted_provider_pair_verified=" + str(int(promoted_pair_verified)))
    print("selection_action_delivery_memory_write=0")
    print("RESULT=" + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
