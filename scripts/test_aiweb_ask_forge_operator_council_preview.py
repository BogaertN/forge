#!/usr/bin/env python3
"""Integration checks for Language Core -> exact RMC -> Operator Council."""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import sys
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiweb_language_core_bootstrap.meaning_compiler_preview import (  # noqa: E402
    build_semantic_contract_binding,
    compile_meaning_preview,
    semantic_contract_for_candidate,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.rmc_context import (  # noqa: E402
    build_rmc_context_record,
    build_rmc_context_snapshot,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (  # noqa: E402
    forge_seed_registry,
)
from aiweb_language_core_bootstrap.schema import stable_record_id  # noqa: E402
from rmc_engine_v1.rmc_exact_language_store import (  # noqa: E402
    build_exact_language_memory_record,
    evaluate_exact_identity_resonance,
)
from rmc_engine_v1.operator_council_preview import (  # noqa: E402
    build_operator_council_preview,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _exact_record(
    candidate: object,
    frame_candidates: object,
    label: str,
    *,
    grammar_rule_ref: str | None = None,
) -> object:
    registry = forge_seed_registry()
    role_id_by_key = {item.role_key: item.role_id for item in registry.roles}
    contract = semantic_contract_for_candidate(candidate, frame_candidates)
    if grammar_rule_ref is not None:
        contract = build_semantic_contract_binding(
            semantic_signature_ref=contract.semantic_signature_ref,
            speech_act=contract.speech_act,
            purport=contract.purport,
            negated=contract.negated,
            frame_key=contract.frame_key,
            grammar_rule_ref=grammar_rule_ref,
            predicate_ref=contract.predicate_ref,
        )
    return build_exact_language_memory_record(
        store_class="stable",
        lifecycle_state="accepted_stable",
        semantic_contract_ref=contract.semantic_contract_id,
        semantic_signature_ref=contract.semantic_signature_ref,
        speech_act=contract.speech_act,
        purport=contract.purport,
        negated=contract.negated,
        frame_key=contract.frame_key,
        grammar_rule_ref=contract.grammar_rule_ref,
        predicate_ref=contract.predicate_ref,
        concept_refs=sorted({item.concept_ref for item in candidate.roles}),
        sense_refs=sorted({item.sense_ref for item in candidate.roles}),
        relation_refs=sorted(candidate.relation_refs),
        role_refs=sorted({role_id_by_key[item.role_key] for item in candidate.roles}),
        ancestry_refs=sorted(candidate.ancestry_refs),
        source_receipt_ref="source_receipt:" + _digest(label + ":source"),
        approval_receipt_ref=(
            "operator_approval_receipt:" + _digest(label + ":approval")
        ),
    )


def _snapshot_record(exact_record: object) -> object:
    return build_rmc_context_record(
        semantic_contract_refs=(exact_record.semantic_contract_ref,),
        concept_refs=exact_record.concept_refs,
        relation_refs=exact_record.relation_refs,
        ancestry_refs=exact_record.ancestry_refs,
        lifecycle_state="accepted",
    )


def _readdress_result(result: object) -> object:
    """Recompute top identities so contract tampering is not merely stale-ID tampering."""

    digest_body = {
        "schema_version": result.schema_version,
        "status": result.status,
        "source_text": result.source_text,
        "source_custody": result.source_custody,
        "source_forms": result.source_forms,
        "lexical_candidates": result.lexical_candidates,
        "frame_candidates": result.frame_candidates,
        "algebra_trace": result.algebra_trace,
        "meaning_candidates": result.meaning_candidates,
        "selected_meaning": result.selected_meaning,
        "rmc_context": result.rmc_context,
        "candidate_wording": result.candidate_wording,
        "echo": result.echo,
        "stages": result.stages,
        "reasons": result.reasons,
        "boundary": result.boundary,
    }
    result_digest = stable_record_id("meaning_preview_digest", digest_body)
    receipt = replace(result.receipt, result_digest=result_digest, receipt_id="pending")
    receipt_body = {
        "result_digest": receipt.result_digest,
        "source_sha256": receipt.source_sha256,
        "status": receipt.status,
        "deterministic": receipt.deterministic,
        "preview_only": receipt.preview_only,
        "writes_performed": receipt.writes_performed,
        "action_performed": receipt.action_performed,
        "delivery_performed": receipt.delivery_performed,
    }
    receipt = replace(
        receipt,
        receipt_id=stable_record_id("meaning_preview_receipt", receipt_body),
    )
    body = {**digest_body, "receipt": receipt}
    return replace(
        result,
        receipt=receipt,
        result_id=stable_record_id("meaning_compiler_preview_result", body),
    )


def main() -> int:
    checks = 0
    source = "Please inspect the manifest."
    connected_empty = compile_meaning_preview(source)
    held = build_operator_council_preview(connected_empty)
    assert held["status"] == "HOLD_FOR_EVIDENCE"
    assert held["recommendation_only"] is True
    assert held["operator_decision_required"] is True
    held_evidence = held["result"]["evidence"]
    assert held_evidence["rmc_connection_status"] == "CONNECTED_EMPTY"
    assert (
        held_evidence["selected_meaning_support_status"]
        == "NO_ADEQUATE_EXACT_SUPPORT"
    )
    checks += 3

    selected = connected_empty.selected_meaning
    assert selected is not None
    selected_contract = semantic_contract_for_candidate(
        selected,
        connected_empty.frame_candidates,
    )
    memory_record = build_rmc_context_record(
        semantic_contract_refs=(selected_contract.semantic_contract_id,),
        concept_refs=sorted({item.concept_ref for item in selected.roles}),
        relation_refs=selected.relation_refs,
        ancestry_refs=selected.ancestry_refs,
        lifecycle_state="accepted",
    )
    structured = compile_meaning_preview(
        source,
        rmc_snapshot=build_rmc_context_snapshot((memory_record,)),
    )
    recommended = build_operator_council_preview(structured)
    assert recommended["status"] == "RECOMMEND_FOR_OPERATOR_REVIEW"
    council = recommended["result"]
    assert isinstance(council, dict)
    assert council["recommendation"]["executable"] is False
    assert council["recommendation"]["authoritative"] is False
    assert council["receipt"]["council_decision_authorized"] is False
    assert council["receipt"]["action_performed"] is False
    assert council["receipt"]["delivery_performed"] is False
    assert all(
        position["decision_authority"] is False
        for position in council["positions"]
    )
    assert council["evidence"]["selected_meaning_support_status"] == "EXACT_SUPPORT"
    checks += 8

    # The production-strength path requires the enriched exact-store audit to
    # independently confirm all selected concepts, senses, relations, and roles.
    exact_source = compile_meaning_preview(source)
    exact_candidate = exact_source.selected_meaning
    assert exact_candidate is not None
    exact_record = _exact_record(
        exact_candidate,
        exact_source.frame_candidates,
        "complete",
    )
    exact_structured = compile_meaning_preview(
        source,
        rmc_snapshot=build_rmc_context_snapshot((_snapshot_record(exact_record),)),
    )
    exact_resonances = evaluate_exact_identity_resonance(
        (exact_record,),
        exact_structured.meaning_candidates,
        exact_structured.frame_candidates,
    )
    exact_recommended = build_operator_council_preview(
        exact_structured,
        exact_rmc_resonances=exact_resonances,
    )
    assert exact_recommended["status"] == "RECOMMEND_FOR_OPERATOR_REVIEW"
    exact_evidence = exact_recommended["result"]["evidence"]
    assert exact_evidence["rmc_connection_status"] == "CONNECTED_STRUCTURED"
    assert exact_evidence["selected_meaning_support_status"] == "EXACT_SUPPORT"
    assert len(exact_evidence["rmc_evidence_refs"]) == 3
    checks += 4

    # An object that merely looks like a resonance is not evidence, even when
    # its candidate and ID strings have superficially valid shapes.
    forged = SimpleNamespace(
        meaning_candidate_ref=connected_empty.selected_meaning.meaning_candidate_id,
        resonance_id="rmc_exact_identity_resonance:" + ("0" * 64),
    )
    forged_result = build_operator_council_preview(
        connected_empty,
        exact_rmc_resonances=(forged,),
    )
    assert forged_result["status"] == "HELD_INVALID_EVIDENCE"
    assert "exact_rmc_resonance_type_not_admitted" in forged_result["issue_codes"]
    assert forged_result["result"] is None
    checks += 3

    # A canonical resonance from another result is not a member of this
    # candidate set/snapshot and must be rejected rather than silently ignored.
    foreign_source = compile_meaning_preview("Forge reports the artifact.")
    foreign_candidate = foreign_source.selected_meaning
    assert foreign_candidate is not None
    foreign_record = _exact_record(
        foreign_candidate,
        foreign_source.frame_candidates,
        "foreign",
    )
    foreign_structured = compile_meaning_preview(
        "Forge reports the artifact.",
        rmc_snapshot=build_rmc_context_snapshot((_snapshot_record(foreign_record),)),
    )
    foreign_resonances = evaluate_exact_identity_resonance(
        (foreign_record,),
        foreign_structured.meaning_candidates,
        foreign_structured.frame_candidates,
    )
    foreign_result = build_operator_council_preview(
        exact_structured,
        exact_rmc_resonances=foreign_resonances,
    )
    assert foreign_result["status"] == "HELD_INVALID_EVIDENCE"
    assert (
        "exact_rmc_resonance_candidate_not_in_result"
        in foreign_result["issue_codes"]
    )
    checks += 2

    stale_exact = replace(
        exact_resonances[0],
        resonance_id="rmc_exact_identity_resonance:" + ("f" * 64),
    )
    stale_exact_result = build_operator_council_preview(
        exact_structured,
        exact_rmc_resonances=(stale_exact,),
    )
    assert stale_exact_result["status"] == "HELD_INVALID_EVIDENCE"
    assert (
        "exact_rmc_resonance_id_content_mismatch"
        in stale_exact_result["issue_codes"]
    )
    checks += 2

    # Exact overlap is not adequate merely because a generic actor/role ID is
    # shared. The record below has a different predicate and object.
    weak_record = foreign_record
    weak_target = compile_meaning_preview(
        "Forge inspects the manifest.",
        rmc_snapshot=build_rmc_context_snapshot((_snapshot_record(weak_record),)),
    )
    weak_resonances = evaluate_exact_identity_resonance(
        (weak_record,),
        weak_target.meaning_candidates,
        weak_target.frame_candidates,
    )
    assert weak_resonances
    assert not any(
        "predicate:inspect" in item.exact_relation_refs
        for item in weak_resonances
    )
    weak_result = build_operator_council_preview(
        weak_target,
        exact_rmc_resonances=weak_resonances,
    )
    assert weak_result["status"] == "HOLD_FOR_EVIDENCE"
    weak_evidence = weak_result["result"]["evidence"]
    assert weak_evidence["rmc_connection_status"] == "CONNECTED_STRUCTURED"
    assert (
        weak_evidence["selected_meaning_support_status"]
        == "NO_ADEQUATE_EXACT_SUPPORT"
    )
    assert weak_evidence["rmc_evidence_refs"] == ()
    checks += 6

    # Shared concepts, roles, and predicates cannot make an approved statement
    # support a proposition with opposite polarity.
    positive_source = compile_meaning_preview("Forge inspects the manifest.")
    positive_candidate = positive_source.selected_meaning
    assert positive_candidate is not None
    positive_record = _exact_record(
        positive_candidate,
        positive_source.frame_candidates,
        "positive-statement",
    )
    negative_target = compile_meaning_preview(
        "Forge does not inspect the manifest.",
        rmc_snapshot=build_rmc_context_snapshot(
            (_snapshot_record(positive_record),)
        ),
    )
    negative_resonances = evaluate_exact_identity_resonance(
        (positive_record,),
        negative_target.meaning_candidates,
        negative_target.frame_candidates,
    )
    assert negative_resonances
    assert all(
        not item.exact_semantic_contract_refs
        for item in negative_resonances
    )
    negative_council = build_operator_council_preview(
        negative_target,
        exact_rmc_resonances=negative_resonances,
    )
    assert negative_council["status"] == "HOLD_FOR_EVIDENCE"
    assert (
        negative_council["result"]["evidence"][
            "selected_meaning_support_status"
        ]
        == "NO_ADEQUATE_EXACT_SUPPORT"
    )
    checks += 4

    # The same proposition-shaped IDs cannot cross from a statement into a
    # modal request; speech act and purport are part of exact support.
    request_target = compile_meaning_preview(
        "Can Forge inspect the manifest?",
        rmc_snapshot=build_rmc_context_snapshot(
            (_snapshot_record(positive_record),)
        ),
    )
    request_resonances = evaluate_exact_identity_resonance(
        (positive_record,),
        request_target.meaning_candidates,
        request_target.frame_candidates,
    )
    assert request_resonances
    assert all(
        not item.exact_semantic_contract_refs
        for item in request_resonances
    )
    request_council = build_operator_council_preview(
        request_target,
        exact_rmc_resonances=request_resonances,
    )
    assert request_council["status"] == "HOLD_FOR_EVIDENCE"
    assert (
        request_council["result"]["evidence"][
            "selected_meaning_support_status"
        ]
        == "NO_ADEQUATE_EXACT_SUPPORT"
    )
    checks += 4

    # Even with every other semantic field held constant, a different grammar
    # rule is a different exact contract and cannot authorize support.
    grammar_record = _exact_record(
        positive_candidate,
        positive_source.frame_candidates,
        "grammar-mismatch",
        grammar_rule_ref="FORGE-GRAMMAR-V0-ADVERSARIAL-OTHER",
    )
    grammar_target = compile_meaning_preview(
        "Forge inspects the manifest.",
        rmc_snapshot=build_rmc_context_snapshot(
            (_snapshot_record(grammar_record),)
        ),
    )
    grammar_resonances = evaluate_exact_identity_resonance(
        (grammar_record,),
        grammar_target.meaning_candidates,
        grammar_target.frame_candidates,
    )
    assert grammar_resonances
    assert all(
        not item.exact_semantic_contract_refs
        for item in grammar_resonances
    )
    grammar_council = build_operator_council_preview(
        grammar_target,
        exact_rmc_resonances=grammar_resonances,
    )
    assert grammar_council["status"] == "HOLD_FOR_EVIDENCE"
    assert (
        grammar_council["result"]["evidence"][
            "selected_meaning_support_status"
        ]
        == "NO_ADEQUATE_EXACT_SUPPORT"
    )
    checks += 4

    # Canonically re-addressed authority violations remain forbidden; content
    # addressing does not turn an action/write claim into admissible evidence.
    forbidden_boundaries = (
        replace(structured.boundary, model_called=True),
        replace(structured.boundary, tokenization_performed=True),
        replace(structured.boundary, vector_used=True),
        replace(structured.boundary, memory_write_performed=True),
        replace(structured.boundary, action_performed=True),
        replace(structured.boundary, delivery_performed=True),
    )
    for bad_boundary in forbidden_boundaries:
        data = bad_boundary.to_dict()
        data.pop("boundary_id")
        bad_boundary = replace(
            bad_boundary,
            boundary_id=stable_record_id("meaning_compiler_preview_boundary", data),
        )
        bad_result = _readdress_result(replace(structured, boundary=bad_boundary))
        rejected = build_operator_council_preview(bad_result)
        assert rejected["status"] == "HELD_INVALID_EVIDENCE"
        assert "meaning_boundary_identity_or_authority_mismatch" in rejected["issue_codes"]
        checks += 2

    for field in ("writes_performed", "action_performed", "delivery_performed"):
        bad_receipt = replace(structured.receipt, **{field: True})
        bad_result = _readdress_result(replace(structured, receipt=bad_receipt))
        rejected = build_operator_council_preview(bad_result)
        assert rejected["status"] == "HELD_INVALID_EVIDENCE"
        assert "meaning_receipt_contract_violated" in rejected["issue_codes"]
        checks += 2

    bad_echo = replace(
        structured.echo,
        exact_signature_match=False,
        echo_id="pending",
    )
    echo_body = bad_echo.to_dict()
    echo_body.pop("echo_id")
    bad_echo = replace(
        bad_echo,
        echo_id=stable_record_id("meaning_echo", echo_body),
    )
    bad_echo_result = _readdress_result(replace(structured, echo=bad_echo))
    rejected_echo = build_operator_council_preview(bad_echo_result)
    assert rejected_echo["status"] == "HELD_INVALID_EVIDENCE"
    assert "echo_selected_meaning_validation_mismatch" in rejected_echo["issue_codes"]
    checks += 2

    stale_result = replace(structured, result_id="meaning_compiler_preview_result:" + ("0" * 64))
    rejected_stale = build_operator_council_preview(stale_result)
    assert rejected_stale["status"] == "HELD_INVALID_EVIDENCE"
    assert "meaning_result_id_content_mismatch" in rejected_stale["issue_codes"]
    checks += 2

    class BrokenIterable:
        def __iter__(self):
            raise RuntimeError("must not escape the bridge")

    broken = build_operator_council_preview(
        structured,
        exact_rmc_resonances=BrokenIterable(),
    )
    assert broken["status"] == "HELD_INVALID_EVIDENCE"
    assert "exact_rmc_resonance_iteration_failed" in broken["issue_codes"]
    none_iterable = build_operator_council_preview(
        structured,
        exact_rmc_resonances=None,
    )
    assert none_iterable["status"] == "HELD_INVALID_EVIDENCE"
    checks += 3

    unknown = compile_meaning_preview("purple quickly maybe")
    not_convened = build_operator_council_preview(unknown)
    assert not_convened["status"] == "NOT_CONVENED"
    assert not_convened["result"] is None
    assert not_convened["boundary"]["raw_text_accepted"] is False
    checks += 3

    print(f"Ask Forge Operator Council preview: {checks} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
