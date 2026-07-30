"""Bridge validated Language Core evidence into the recommendation-only Council.

Raw source text never crosses this boundary.  The Council receives only
content identities and closed booleans from a fully validated compiler result,
Echo receipt, and exact-reference RMC evaluation.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
import hashlib
import re

from aiweb_language_core_bootstrap.schema import stable_record_id
from aiweb_language_core_bootstrap.meaning_compiler_preview import (
    meaning_compiler_preview_boundary,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (
    forge_seed_registry,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.rmc_context import (
    build_rmc_context_snapshot,
    evaluate_rmc_context,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.semantic_contract import (
    semantic_contract_for_candidate,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.schema import (
    AlgebraTraceStep,
    CandidateWording,
    EchoResult,
    EchoStatus,
    FrameCandidate,
    GateResult,
    LexicalCandidate,
    MeaningCandidate,
    MeaningCompilerPreviewResult,
    MeaningCompilerPreviewBoundary,
    MEANING_COMPILER_PREVIEW_SCHEMA_VERSION,
    PreviewReceipt,
    PreviewStatus,
    RmcContextEvaluation,
    RmcContextSnapshot,
    SourceForm,
    StageResult,
)
from aiweb_language_core_bootstrap.operator_council import (
    CouncilValidationError,
    convene_operator_council,
)
from rmc_engine_v1.rmc_exact_language_store import ExactIdentityResonance


_MAX_EXTERNAL_RESONANCES = 4096
_EXACT_MEMORY_RECORD_ID = re.compile(r"^rmc_exact_language_record:[0-9a-f]{64}$")
_GATE_RULES = {
    "expectancy": "FORGE-MEANING-GATE-AKANKSHA-V0",
    "congruity": "FORGE-MEANING-GATE-YOGYATA-V0",
    "connectedness": "FORGE-MEANING-GATE-SANNIDHI-V0",
    "purport": "FORGE-MEANING-GATE-TATPARYA-V0",
}


def _closed_boundary() -> dict[str, object]:
    return {
        "recommendation_only": True,
        "operator_decision_required": True,
        "raw_text_accepted": False,
        "tokenization_performed": False,
        "model_called": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
        "memory_write_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "decision_authority": False,
    }


def _not_convened(reason_code: str, summary: str) -> dict[str, object]:
    return {
        "status": "NOT_CONVENED",
        "reason_code": reason_code,
        "summary": summary,
        "result": None,
        "boundary": _closed_boundary(),
    }


def _held_invalid(*issues: str) -> dict[str, object]:
    codes = tuple(dict.fromkeys(item for item in issues if item))
    return {
        "status": "HELD_INVALID_EVIDENCE",
        "reason_code": "operator_council_evidence_rejected",
        "issue_codes": list(codes or ("operator_council_bridge_failed_closed",)),
        "summary": "Council rejected the structured evidence envelope.",
        "result": None,
        "boundary": _closed_boundary(),
    }


def _content_id_matches(value: object, id_field: str, namespace: str) -> bool:
    method = getattr(value, "to_dict", None)
    if not callable(method):
        return False
    body = method()
    if not isinstance(body, dict) or id_field not in body:
        return False
    supplied = body.pop(id_field)
    return type(supplied) is str and supplied == stable_record_id(namespace, body)


def _semantic_signature(candidate: MeaningCandidate) -> str:
    role_signature = tuple(
        sorted(
            (role.role_key, role.concept_ref, role.sense_ref)
            for role in candidate.roles
        )
    )
    if (
        candidate.predicate_key == "mean"
        and candidate.speech_act in {"definition_request", "definition_response"}
    ):
        body = {
            "semantic_relation": "governed_provisional_definition",
            "predicate_key": candidate.predicate_key,
            "negated": candidate.negated,
            "roles": role_signature,
        }
    else:
        body = {
            "speech_act": candidate.speech_act,
            "purport": candidate.purport,
            "predicate_key": candidate.predicate_key,
            "negated": candidate.negated,
            "roles": role_signature,
        }
    return stable_record_id("semantic_signature", body)


def _validate_candidate(
    candidate: MeaningCandidate,
    *,
    frame_by_id: Mapping[str, FrameCandidate],
    source_form_ids: frozenset[str],
    input_event_id: str,
    predicate_by_key: Mapping[str, object],
    sense_by_id: Mapping[str, object],
) -> tuple[str, ...]:
    issues: list[str] = []
    if not _content_id_matches(candidate, "meaning_candidate_id", "meaning_candidate"):
        issues.append("meaning_candidate_id_content_mismatch")
    if candidate.semantic_signature != _semantic_signature(candidate):
        issues.append("semantic_signature_content_mismatch")
    frame = frame_by_id.get(candidate.frame_candidate_ref)
    if frame is None:
        issues.append("meaning_candidate_frame_not_in_result")
    else:
        if (
            candidate.frame_key != frame.frame_key
            or candidate.speech_act != frame.speech_act
            or candidate.purport != frame.purport
            or candidate.predicate_ref != frame.predicate_ref
            or candidate.predicate_key != frame.predicate_key
            or candidate.negated is not frame.negated
        ):
            issues.append("meaning_candidate_frame_contract_mismatch")
        if len(candidate.roles) != len(frame.role_bindings):
            issues.append("meaning_candidate_role_binding_count_mismatch")
        else:
            for role, binding in zip(candidate.roles, frame.role_bindings):
                if (
                    role.role_key != binding.role_key
                    or role.source_form_refs != binding.source_form_refs
                ):
                    issues.append("meaning_candidate_role_binding_mismatch")
                    break

    predicate = predicate_by_key.get(candidate.predicate_key)
    if predicate is None or getattr(predicate, "predicate_id", None) != candidate.predicate_ref:
        issues.append("meaning_candidate_predicate_not_in_registry")
    for role in candidate.roles:
        if any(reference not in source_form_ids for reference in role.source_form_refs):
            issues.append("meaning_candidate_source_form_not_in_result")
        if bool(role.concept_ref) != bool(role.sense_ref):
            issues.append("meaning_candidate_partial_concept_sense_binding")
            continue
        if role.sense_ref:
            sense = sense_by_id.get(role.sense_ref)
            if sense is None or getattr(sense, "concept_ref", None) != role.concept_ref:
                issues.append("meaning_candidate_sense_concept_mismatch")

    expected_relations = tuple(
        sorted(
            (f"predicate:{candidate.predicate_key}",)
            + tuple(
                f"role:{role.role_key}:{role.concept_ref}"
                for role in candidate.roles
                if role.concept_ref
            )
        )
    )
    if candidate.relation_refs != expected_relations:
        issues.append("meaning_candidate_relation_refs_mismatch")
    expected_ancestry = tuple(
        sorted(
            (input_event_id,)
            + tuple(
                reference
                for role in candidate.roles
                for reference in role.source_form_refs
            )
        )
    )
    if candidate.ancestry_refs != expected_ancestry:
        issues.append("meaning_candidate_ancestry_refs_mismatch")

    if len(candidate.gates) != len(_GATE_RULES):
        issues.append("meaning_candidate_gate_count_mismatch")
    seen_gates: list[str] = []
    for gate in candidate.gates:
        if type(gate) is not GateResult:
            issues.append("meaning_gate_type_not_admitted")
            continue
        seen_gates.append(gate.gate_name)
        if not _content_id_matches(gate, "gate_id", "meaning_gate"):
            issues.append("meaning_gate_id_content_mismatch")
        if type(gate.passed) is not bool:
            issues.append("meaning_gate_passed_not_boolean")
        if _GATE_RULES.get(gate.gate_name) != gate.rule_id:
            issues.append("meaning_gate_rule_mismatch")
    if tuple(seen_gates) != tuple(_GATE_RULES):
        issues.append("meaning_gate_order_or_membership_mismatch")
    if type(candidate.all_gates_passed) is not bool or candidate.all_gates_passed != all(
        gate.passed is True for gate in candidate.gates
    ):
        issues.append("meaning_candidate_gate_aggregate_mismatch")
    if (
        candidate.provisional is not True
        or candidate.preview_only is not True
        or candidate.selection_authority is not False
    ):
        issues.append("meaning_candidate_authority_contract_violated")
    return tuple(issues)


def _expected_rmc_context(
    result: MeaningCompilerPreviewResult,
    selected: MeaningCandidate | None,
) -> RmcContextEvaluation:
    snapshot = build_rmc_context_snapshot(result.rmc_context.snapshot.records)
    base = evaluate_rmc_context(
        snapshot,
        result.meaning_candidates,
        result.frame_candidates,
    )
    if not result.rmc_context.context_used_for_selection:
        return base
    if selected is None:
        raise ValueError("selection-marked RMC context has no selected meaning")
    resonances = tuple(
        replace(
            resonance,
            used_for_selection=(
                resonance.meaning_candidate_ref == selected.meaning_candidate_id
                and bool(resonance.exact_semantic_contract_refs)
            ),
        )
        for resonance in base.resonances
    )
    body = {
        "snapshot": snapshot,
        "resonances": resonances,
        "exact_reference_resonance_only": True,
        "context_used_for_selection": True,
        "memory_read_performed": False,
        "memory_write_performed": False,
    }
    return RmcContextEvaluation(
        evaluation_id=stable_record_id("rmc_context_evaluation", body),
        **body,
    )


def _validate_compiler_result(
    result: MeaningCompilerPreviewResult,
) -> tuple[str, ...]:
    issues: list[str] = []
    if result.schema_version != MEANING_COMPILER_PREVIEW_SCHEMA_VERSION:
        issues.append("meaning_result_schema_version_mismatch")
    if type(result.source_text) is not str or type(result.status) is not PreviewStatus:
        issues.append("meaning_result_core_type_invalid")
    if type(result.boundary) is not MeaningCompilerPreviewBoundary:
        issues.append("meaning_boundary_type_not_admitted")
    elif result.boundary != meaning_compiler_preview_boundary():
        issues.append("meaning_boundary_identity_or_authority_mismatch")
    if type(result.receipt) is not PreviewReceipt:
        issues.append("meaning_receipt_type_not_admitted")
    if type(result.rmc_context) is not RmcContextEvaluation:
        issues.append("rmc_context_type_not_admitted")
    elif type(result.rmc_context.snapshot) is not RmcContextSnapshot:
        issues.append("rmc_snapshot_type_not_admitted")

    custody = result.source_custody
    if type(result.source_text) is str:
        expected_sha = hashlib.sha256(result.source_text.encode("utf-8")).hexdigest()
        if custody.source_sha256 != expected_sha:
            issues.append("source_custody_sha256_mismatch")
    for field in (
        "normalization_performed",
        "tokenization_performed",
        "model_token_stream_created",
        "subword_token_stream_created",
        "numeric_token_ids_created",
    ):
        if getattr(custody, field, None) is not False:
            issues.append("source_custody_forbidden_mechanism_enabled")
            break

    typed_collections = (
        (result.source_forms, SourceForm, "source_form_type_not_admitted"),
        (result.lexical_candidates, LexicalCandidate, "lexical_candidate_type_not_admitted"),
        (result.frame_candidates, FrameCandidate, "frame_candidate_type_not_admitted"),
        (result.algebra_trace, AlgebraTraceStep, "algebra_trace_type_not_admitted"),
        (result.meaning_candidates, MeaningCandidate, "meaning_candidate_type_not_admitted"),
        (result.stages, StageResult, "stage_type_not_admitted"),
    )
    for values, expected_type, code in typed_collections:
        if type(values) is not tuple or any(type(item) is not expected_type for item in values):
            issues.append(code)

    identity_specs = (
        (result.source_forms, "source_form_id", "source_form", "source_form_id_content_mismatch"),
        (result.lexical_candidates, "lexical_candidate_id", "lexical_candidate", "lexical_candidate_id_content_mismatch"),
        (result.frame_candidates, "frame_candidate_id", "frame_candidate", "frame_candidate_id_content_mismatch"),
        (result.algebra_trace, "trace_step_id", "meaning_algebra_step", "algebra_trace_id_content_mismatch"),
        (result.stages, "stage_id", "meaning_preview_stage", "stage_id_content_mismatch"),
    )
    for values, id_field, namespace, code in identity_specs:
        for value in values:
            if not _content_id_matches(value, id_field, namespace):
                issues.append(code)
                break
    for frame in result.frame_candidates:
        for binding in frame.role_bindings:
            if not _content_id_matches(binding, "binding_id", "role_binding"):
                issues.append("role_binding_id_content_mismatch")
                break

    id_collections = (
        tuple(item.source_form_id for item in result.source_forms),
        tuple(item.lexical_candidate_id for item in result.lexical_candidates),
        tuple(item.frame_candidate_id for item in result.frame_candidates),
        tuple(item.meaning_candidate_id for item in result.meaning_candidates),
        tuple(item.stage_id for item in result.stages),
    )
    if any(len(items) != len(set(items)) for items in id_collections):
        issues.append("meaning_result_duplicate_content_identity")

    frame_by_id = {
        item.frame_candidate_id: item for item in result.frame_candidates
    }
    source_form_ids = frozenset(item.source_form_id for item in result.source_forms)
    registry = forge_seed_registry()
    predicate_by_key = {item.predicate_key: item for item in registry.predicates}
    sense_by_id = {item.sense_id: item for item in registry.senses}
    for candidate in result.meaning_candidates:
        issues.extend(
            _validate_candidate(
                candidate,
                frame_by_id=frame_by_id,
                source_form_ids=source_form_ids,
                input_event_id=custody.input_event_id,
                predicate_by_key=predicate_by_key,
                sense_by_id=sense_by_id,
            )
        )

    selected = result.selected_meaning
    if selected is not None:
        matches = tuple(
            candidate
            for candidate in result.meaning_candidates
            if candidate.meaning_candidate_id == selected.meaning_candidate_id
        )
        if len(matches) != 1 or matches[0] != selected:
            issues.append("selected_meaning_not_exact_result_member")
        if (
            result.status is not PreviewStatus.PREVIEW_READY
            or selected.all_gates_passed is not True
            or selected.unknown_source_form_refs
            or custody.source_preserved_exactly is not True
            or custody.structural_progression_allowed is not True
        ):
            issues.append("selected_meaning_not_council_eligible")
    elif result.status is PreviewStatus.PREVIEW_READY:
        issues.append("preview_ready_without_selected_meaning")

    wording = result.candidate_wording
    if wording is not None:
        if type(wording) is not CandidateWording:
            issues.append("candidate_wording_type_not_admitted")
        else:
            if not _content_id_matches(wording, "wording_id", "candidate_wording"):
                issues.append("candidate_wording_id_content_mismatch")
            if wording.delivery_authorized is not False:
                issues.append("candidate_wording_delivery_authority_enabled")
    if selected is not None:
        if type(wording) is not CandidateWording:
            issues.append("selected_meaning_candidate_wording_required")
        elif (
            wording.meaning_candidate_ref != selected.meaning_candidate_id
            or wording.outward_semantic_signature != selected.semantic_signature
        ):
            issues.append("candidate_wording_selected_meaning_mismatch")

    echo = result.echo
    if type(echo) is not EchoResult:
        issues.append("echo_type_not_admitted")
    else:
        if not _content_id_matches(echo, "echo_id", "meaning_echo"):
            issues.append("echo_id_content_mismatch")
        if echo.delivery_authorized is not False:
            issues.append("echo_delivery_authority_enabled")
        if selected is not None:
            if (
                echo.status is not EchoStatus.PASS
                or echo.reason_code != "semantic_signature_preserved"
                or echo.meaning_candidate_ref != selected.meaning_candidate_id
                or type(wording) is not CandidateWording
                or echo.candidate_wording_ref != wording.wording_id
                or echo.inward_semantic_signature != selected.semantic_signature
                or echo.reparsed_semantic_signature != selected.semantic_signature
                or echo.exact_signature_match is not True
                or echo.reparse_performed is not True
            ):
                issues.append("echo_selected_meaning_validation_mismatch")

    if type(result.rmc_context) is RmcContextEvaluation:
        try:
            expected_context = _expected_rmc_context(result, selected)
        except (TypeError, ValueError):
            issues.append("rmc_context_validation_failed")
        else:
            if result.rmc_context != expected_context:
                issues.append("rmc_context_identity_or_membership_mismatch")

    if type(result.receipt) is PreviewReceipt:
        receipt = result.receipt
        if (
            receipt.status is not result.status
            or receipt.source_sha256 != custody.source_sha256
            or receipt.deterministic is not True
            or receipt.preview_only is not True
            or receipt.writes_performed is not False
            or receipt.action_performed is not False
            or receipt.delivery_performed is not False
        ):
            issues.append("meaning_receipt_contract_violated")

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
        expected_digest = stable_record_id("meaning_preview_digest", digest_body)
        if receipt.result_digest != expected_digest:
            issues.append("meaning_result_digest_content_mismatch")
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
        if receipt.receipt_id != stable_record_id("meaning_preview_receipt", receipt_body):
            issues.append("meaning_receipt_id_content_mismatch")
        result_body = {**digest_body, "receipt": receipt}
        if result.result_id != stable_record_id("meaning_compiler_preview_result", result_body):
            issues.append("meaning_result_id_content_mismatch")
    return tuple(dict.fromkeys(issues))


def _coerce_external_resonances(value: object) -> tuple[ExactIdentityResonance, ...]:
    if value is None or isinstance(value, (str, bytes, bytearray, Mapping)):
        raise ValueError("exact_rmc_resonances_not_admitted")
    try:
        iterator = iter(value)
    except TypeError as error:
        raise ValueError("exact_rmc_resonances_not_iterable") from error
    except Exception as error:
        raise ValueError("exact_rmc_resonance_iteration_failed") from error
    items: list[ExactIdentityResonance] = []
    try:
        for item in iterator:
            if len(items) >= _MAX_EXTERNAL_RESONANCES:
                raise ValueError("exact_rmc_resonance_limit_exceeded")
            if type(item) is not ExactIdentityResonance:
                raise ValueError("exact_rmc_resonance_type_not_admitted")
            items.append(item)
    except ValueError:
        raise
    except Exception as error:
        raise ValueError("exact_rmc_resonance_iteration_failed") from error
    if len({item.resonance_id for item in items}) != len(items):
        raise ValueError("duplicate_exact_rmc_resonance_id")
    return tuple(items)


def _validate_external_resonances(
    resonances: tuple[ExactIdentityResonance, ...],
    result: MeaningCompilerPreviewResult,
) -> tuple[str, ...]:
    issues: list[str] = []
    candidates = {
        item.meaning_candidate_id: item for item in result.meaning_candidates
    }
    context_resonances = result.rmc_context.resonances
    for resonance in resonances:
        if not _content_id_matches(
            resonance,
            "resonance_id",
            "rmc_exact_identity_resonance",
        ):
            issues.append("exact_rmc_resonance_id_content_mismatch")
        if (
            type(resonance.memory_record_ref) is not str
            or not _EXACT_MEMORY_RECORD_ID.fullmatch(resonance.memory_record_ref)
        ):
            issues.append("exact_rmc_memory_record_ref_invalid")
        candidate = candidates.get(resonance.meaning_candidate_ref)
        if candidate is None:
            issues.append("exact_rmc_resonance_candidate_not_in_result")
            continue
        ref_fields = (
            resonance.exact_semantic_contract_refs,
            resonance.exact_concept_refs,
            resonance.exact_sense_refs,
            resonance.exact_relation_refs,
            resonance.exact_role_refs,
            resonance.exact_ancestry_refs,
        )
        if any(
            type(values) is not tuple
            or values != tuple(sorted(values))
            or len(values) != len(set(values))
            for values in ref_fields
        ):
            issues.append("exact_rmc_resonance_reference_set_not_canonical")
        if (
            type(resonance.exact_identity_count) is not int
            or resonance.exact_identity_count
            != sum(len(values) for values in ref_fields)
            or resonance.approximate_match_used is not False
            or resonance.used_for_selection is not False
        ):
            issues.append("exact_rmc_resonance_contract_violated")
        candidate_concepts = {item.concept_ref for item in candidate.roles}
        candidate_senses = {item.sense_ref for item in candidate.roles}
        candidate_relations = set(candidate.relation_refs)
        candidate_ancestry = set(candidate.ancestry_refs)
        registry = forge_seed_registry()
        role_id_by_key = {item.role_key: item.role_id for item in registry.roles}
        candidate_roles = {
            role_id_by_key[item.role_key]
            for item in candidate.roles
            if item.role_key in role_id_by_key
        }
        try:
            candidate_contract = semantic_contract_for_candidate(
                candidate,
                result.frame_candidates,
            )
        except (TypeError, ValueError):
            issues.append("meaning_candidate_semantic_contract_invalid")
            continue
        if (
            not set(resonance.exact_semantic_contract_refs).issubset(
                {candidate_contract.semantic_contract_id}
            )
            or not set(resonance.exact_concept_refs).issubset(candidate_concepts)
            or not set(resonance.exact_sense_refs).issubset(candidate_senses)
            or not set(resonance.exact_relation_refs).issubset(candidate_relations)
            or not set(resonance.exact_role_refs).issubset(candidate_roles)
            or not set(resonance.exact_ancestry_refs).issubset(candidate_ancestry)
        ):
            issues.append("exact_rmc_resonance_claims_non_candidate_identity")
        if not any(
            context.meaning_candidate_ref == resonance.meaning_candidate_ref
            and context.exact_semantic_contract_refs
            == resonance.exact_semantic_contract_refs
            and context.exact_concept_refs == resonance.exact_concept_refs
            and context.exact_relation_refs == resonance.exact_relation_refs
            and context.exact_ancestry_refs == resonance.exact_ancestry_refs
            for context in context_resonances
        ):
            issues.append("exact_rmc_resonance_not_bound_to_snapshot")
    return tuple(dict.fromkeys(issues))


def _adequate_context_resonances(
    result: MeaningCompilerPreviewResult,
    selected: MeaningCandidate,
    semantic_contract_ref: str,
) -> tuple[object, ...]:
    selected_concepts = {item.concept_ref for item in selected.roles}
    selected_relations = set(selected.relation_refs)
    predicate_ref = f"predicate:{selected.predicate_key}"
    return tuple(
        resonance
        for resonance in result.rmc_context.resonances
        if resonance.meaning_candidate_ref == selected.meaning_candidate_id
        and resonance.exact_semantic_contract_refs
        == (semantic_contract_ref,)
        and set(resonance.exact_concept_refs) == selected_concepts
        and set(resonance.exact_relation_refs) == selected_relations
        and predicate_ref in resonance.exact_relation_refs
    )


def _adequate_external_resonances(
    resonances: tuple[ExactIdentityResonance, ...],
    selected: MeaningCandidate,
    adequate_context: tuple[object, ...],
    semantic_contract_ref: str,
) -> tuple[ExactIdentityResonance, ...]:
    registry = forge_seed_registry()
    role_id_by_key = {item.role_key: item.role_id for item in registry.roles}
    concepts = {item.concept_ref for item in selected.roles}
    senses = {item.sense_ref for item in selected.roles}
    relations = set(selected.relation_refs)
    roles = {
        role_id_by_key[item.role_key]
        for item in selected.roles
        if item.role_key in role_id_by_key
    }
    predicate_ref = f"predicate:{selected.predicate_key}"
    context_keys = {
        (
            item.exact_semantic_contract_refs,
            item.exact_concept_refs,
            item.exact_relation_refs,
            item.exact_ancestry_refs,
        )
        for item in adequate_context
    }
    return tuple(
        resonance
        for resonance in resonances
        if resonance.meaning_candidate_ref == selected.meaning_candidate_id
        and resonance.exact_semantic_contract_refs
        == (semantic_contract_ref,)
        and set(resonance.exact_concept_refs) == concepts
        and set(resonance.exact_sense_refs) == senses
        and set(resonance.exact_relation_refs) == relations
        and set(resonance.exact_role_refs) == roles
        and predicate_ref in resonance.exact_relation_refs
        and (
            resonance.exact_semantic_contract_refs,
            resonance.exact_concept_refs,
            resonance.exact_relation_refs,
            resonance.exact_ancestry_refs,
        )
        in context_keys
    )


def build_operator_council_preview(
    result: MeaningCompilerPreviewResult,
    *,
    exact_rmc_resonances: Iterable[object] = (),
) -> dict[str, object]:
    """Convene on validated structured evidence, or return a typed visible hold."""

    if type(result) is not MeaningCompilerPreviewResult:
        return _not_convened(
            "meaning_result_type_not_admitted",
            "Council did not receive a typed Language Core result.",
        )
    try:
        result_issues = _validate_compiler_result(result)
    except Exception:
        return _held_invalid("meaning_result_validation_failed_closed")
    if result_issues:
        return _held_invalid(*result_issues)
    selected = result.selected_meaning
    if selected is None:
        return _not_convened(
            "selected_meaning_required_before_council",
            "Council waits until Language Core selects one meaning.",
        )

    try:
        external = _coerce_external_resonances(exact_rmc_resonances)
        resonance_issues = _validate_external_resonances(external, result)
    except ValueError as error:
        return _held_invalid(str(error))
    except Exception:
        return _held_invalid("exact_rmc_resonance_validation_failed_closed")
    if resonance_issues:
        return _held_invalid(*resonance_issues)

    try:
        selected_contract = semantic_contract_for_candidate(
            selected,
            result.frame_candidates,
        )
    except (TypeError, ValueError):
        return _held_invalid("selected_meaning_semantic_contract_invalid")
    adequate_context = _adequate_context_resonances(
        result,
        selected,
        selected_contract.semantic_contract_id,
    )
    adequate_external = _adequate_external_resonances(
        external,
        selected,
        adequate_context,
        selected_contract.semantic_contract_id,
    )
    # When the exact-store audit is supplied, it must independently confirm
    # concepts, senses, predicate/relations, and role identities.  Direct
    # compiler callers without that enriched audit may rely on a complete,
    # canonical context resonance bound to the immutable snapshot.
    adequate_support = bool(adequate_context) and (
        not external or bool(adequate_external)
    )
    if adequate_support:
        rmc_evidence_refs = tuple(
            sorted(
                {
                    selected_contract.semantic_contract_id,
                    *(item.resonance_id for item in adequate_context),
                    *(item.resonance_id for item in adequate_external),
                }
            )
        )
        support_status = "EXACT_SUPPORT"
    else:
        rmc_evidence_refs = ()
        support_status = "NO_ADEQUATE_EXACT_SUPPORT"

    uncertainties: list[str] = []
    if not adequate_support:
        uncertainties.append("council_uncertainty:no_adequate_exact_rmc_support")

    envelope = {
        "selected_meaning_ref": selected.meaning_candidate_id,
        "semantic_signature": selected.semantic_signature,
        "speech_act": selected.speech_act,
        "purport": selected.purport,
        "predicate_ref": selected.predicate_ref,
        "concept_refs": sorted({item.concept_ref for item in selected.roles}),
        "relation_refs": list(selected.relation_refs),
        "ancestry_refs": list(selected.ancestry_refs),
        "gate_receipt_refs": [item.gate_id for item in selected.gates],
        "gates_passed": True,
        "echo_receipt_ref": result.echo.echo_id,
        "echo_status": EchoStatus.PASS.value,
        "rmc_snapshot_ref": result.rmc_context.snapshot.snapshot_id,
        "rmc_connection_status": result.rmc_context.snapshot.connection_status,
        "selected_meaning_support_status": support_status,
        "rmc_evidence_refs": list(rmc_evidence_refs),
        "authority_evidence_refs": [
            result.boundary.boundary_id,
            result.receipt.receipt_id,
        ],
        "contradiction_refs": [],
        "uncertainty_refs": uncertainties,
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
    try:
        council = convene_operator_council(envelope)
    except CouncilValidationError as error:
        return _held_invalid(*error.issues)
    except Exception:
        return _held_invalid("operator_council_deliberation_failed_closed")

    recommendation = council.recommendation
    return {
        "status": recommendation.disposition.value,
        "reason_code": recommendation.reason_codes[0],
        "summary": (
            "Council recommends this evidence for human operator review."
            if recommendation.disposition.value == "RECOMMEND_FOR_OPERATOR_REVIEW"
            else "Council holds this candidate until the missing evidence is supplied."
        ),
        "recommendation_only": True,
        "operator_decision_required": True,
        "result": council.to_dict(),
        "boundary": council.boundary.to_dict(),
    }


__all__ = ("build_operator_council_preview",)
