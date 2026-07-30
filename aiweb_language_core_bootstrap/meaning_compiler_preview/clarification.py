"""Governed clarification previews for genuinely ambiguous meanings.

This module projects an already-held compiler result into one deterministic
operator-facing clarification *preview*.  Exposing that preview is recorded
explicitly; it does not start a live clarification session, consume a
clarification response, select an alternative, call a model, route a tool,
authorize an action, deliver an answer, or write memory.  Successful compiler
selections and every non-ambiguity hold return ``None`` unchanged.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from typing import Final

from ..schema import canonicalize, stable_record_id
from .registry import forge_seed_registry
from .schema import (
    EchoStatus,
    MeaningCompilerPreviewResult,
    MeaningRole,
    PreviewStatus,
)
from .semantic_contract import semantic_contract_for_candidate


GOVERNED_CLARIFICATION_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-governed-clarification-preview-v1"
)
CLARIFICATION_REASON: Final[str] = "ambiguous_meaning_requires_clarification"


def _record_dict(value: object) -> dict[str, object]:
    return canonicalize(asdict(value))


@dataclass(frozen=True, slots=True)
class ClarificationRoleOption:
    """One exact role/sense projection retained inside an alternative."""

    role_key: str
    concept_ref: str
    sense_ref: str
    preferred_label: str
    provisional_definition: str

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ClarificationOption:
    """One admitted meaning offered without selection authority."""

    option_id: str
    meaning_candidate_ref: str
    semantic_contract_ref: str
    semantic_signature_ref: str
    frame_candidate_ref: str
    option_label: str
    roles: tuple[ClarificationRoleOption, ...]
    provisional: bool
    selection_authority: bool

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("option_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "governed_clarification_option",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class GovernedClarificationRequest:
    """An identity-bound question preview that preserves every alternative."""

    clarification_request_id: str
    schema_version: str
    status: str
    reason_code: str
    compiler_result_ref: str
    compiler_receipt_ref: str
    source_custody_ref: str
    source_sha256: str
    rmc_context_ref: str
    candidate_wording_id: str
    candidate_wording: str
    alternative_meaning_refs: tuple[str, ...]
    alternative_count: int
    options: tuple[ClarificationOption, ...]
    resolution_required: str
    all_admitted_alternatives_preserved: bool
    preview_only: bool
    recommendation_only: bool
    operator_response_required: bool
    operator_preview_exposed: bool
    clarification_question_preview_exposed: bool
    live_clarification_session_started: bool
    clarification_response_consumed: bool
    selection_performed: bool
    delivery_authorized: bool
    delivery_performed: bool
    answer_delivery_performed: bool
    action_authorized: bool
    tool_routing_authorized: bool
    memory_write_authorized: bool
    memory_write_performed: bool

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("clarification_request_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "governed_clarification_request",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


def _role_option(role: MeaningRole) -> ClarificationRoleOption:
    registry = forge_seed_registry()
    concepts = {item.concept_id: item for item in registry.concepts}
    senses = {item.sense_id: item for item in registry.senses}
    concept = concepts.get(role.concept_ref)
    sense = senses.get(role.sense_ref)
    if (
        concept is None
        or sense is None
        or sense.concept_ref != concept.concept_id
    ):
        raise ValueError("clarification_role_registry_membership_invalid")
    return ClarificationRoleOption(
        role_key=role.role_key,
        concept_ref=concept.concept_id,
        sense_ref=sense.sense_id,
        preferred_label=concept.preferred_label,
        provisional_definition=concept.provisional_definition,
    )


def _option_label(roles: tuple[ClarificationRoleOption, ...]) -> str:
    if len(roles) == 1:
        return roles[0].preferred_label
    return "; ".join(
        f"{role.role_key}: {role.preferred_label}"
        for role in roles
    )


def _distinguish_option_labels(
    base_labels: tuple[str, ...],
    candidates: tuple[object, ...],
    contracts: tuple[object, ...],
) -> tuple[str, ...]:
    """Keep question labels usable even when human labels collide.

    Ordinarily a distinguishing concept/sense produces distinct preferred
    labels.  If two future contracts share that wording, append their exact
    communicative contract and candidate identities instead of emitting an
    unusable ``X or X`` question.  The IDs are long only in this exceptional
    collision lane and make the alternatives deterministically distinct.
    """

    counts = {label: base_labels.count(label) for label in set(base_labels)}
    labels: list[str] = []
    for base, candidate, contract in zip(base_labels, candidates, contracts):
        if counts.get(base, 0) == 1:
            labels.append(base)
            continue
        speech_act = str(candidate.speech_act).replace("_", " ")
        purport = str(candidate.purport).replace("_", " ")
        polarity = "negated" if candidate.negated else "affirmative"
        frame = str(candidate.frame_key).replace("_", " ")
        labels.append(
            f"{base} — {speech_act}; {purport}; {polarity}; {frame} "
            f"[{contract.semantic_contract_id}; {candidate.meaning_candidate_id}]"
        )
    if len(labels) != len(set(labels)):
        raise ValueError("clarification_option_labels_not_distinguishing")
    return tuple(labels)


def _clarification_wording(options: tuple[ClarificationOption, ...]) -> str:
    labels = tuple(item.option_label for item in options)
    if len(labels) == 2:
        joined = f"{labels[0]} or {labels[1]}"
    else:
        joined = ", ".join(labels[:-1]) + f", or {labels[-1]}"
    return f"Please clarify the intended meaning: {joined}?"


def _eligible_alternatives(
    result: MeaningCompilerPreviewResult,
) -> tuple[object, ...]:
    if (
        result.status is not PreviewStatus.HELD
        or result.selected_meaning is not None
        or result.candidate_wording is not None
        or result.reasons != (CLARIFICATION_REASON,)
        or result.echo.status is not EchoStatus.NOT_RUN
        or result.rmc_context.context_used_for_selection is not False
    ):
        return ()
    return tuple(
        item for item in result.meaning_candidates if item.all_gates_passed
    )


def _compiler_result_validation_issues(
    result: object,
) -> tuple[str, ...]:
    """Authenticate the complete compiler result by deterministic replay.

    Replaying through the canonical compiler is intentionally stricter than
    copying a subset of its private validators.  Exact dataclass equality
    covers source custody and source-form identities, registry membership,
    frames, the four gates, candidate identities and authority flags, RMC
    evaluation, Echo, stages, boundary, digest, receipt, and final result ID.
    The explicit checks below also keep the no-effect contract visible at this
    boundary and provide stable diagnostics for authority regressions.
    """

    if type(result) is not MeaningCompilerPreviewResult:
        return ("compiler_result_type_not_admitted",)

    try:
        # Function-local import avoids the package-initialization cycle while
        # retaining one canonical compiler implementation.
        from .compiler import compile_meaning_preview

        replayed = compile_meaning_preview(
            result.source_text,
            rmc_snapshot=result.rmc_context.snapshot,
        )
    except Exception:
        return ("compiler_result_replay_failed",)
    if replayed != result:
        return ("compiler_result_not_exact_deterministic_replay",)

    # Exact replay proves the nested runtime types before the explicit
    # authority assertions below are inspected.
    issues: list[str] = []
    if type(result.source_text) is not str:
        issues.append("compiler_source_text_type_invalid")
    else:
        source_sha256 = hashlib.sha256(
            result.source_text.encode("utf-8")
        ).hexdigest()
        if result.source_custody.source_sha256 != source_sha256:
            issues.append("compiler_source_sha256_mismatch")
    custody = result.source_custody
    if (
        custody.normalization_performed is not False
        or custody.tokenization_performed is not False
        or custody.model_token_stream_created is not False
        or custody.subword_token_stream_created is not False
        or custody.numeric_token_ids_created is not False
    ):
        issues.append("compiler_source_custody_boundary_invalid")

    for candidate in result.meaning_candidates:
        actual_all_gates_passed = bool(candidate.gates) and all(
            gate.passed is True for gate in candidate.gates
        )
        if candidate.all_gates_passed is not actual_all_gates_passed:
            issues.append("compiler_candidate_gate_aggregate_mismatch")
        if (
            candidate.preview_only is not True
            or candidate.selection_authority is not False
        ):
            issues.append("compiler_candidate_authority_invalid")

    rmc = result.rmc_context
    snapshot = rmc.snapshot
    if (
        rmc.exact_reference_resonance_only is not True
        or rmc.memory_read_performed is not False
        or rmc.memory_write_performed is not False
        or snapshot.read_only is not True
        or snapshot.exact_reference_resonance_only is not True
        or snapshot.filesystem_access_performed is not False
        or snapshot.raw_word_overlap_used is not False
        or snapshot.embedding_used is not False
        or snapshot.vector_used is not False
        or snapshot.similarity_scoring_used is not False
    ):
        issues.append("compiler_rmc_boundary_invalid")
    if any(
        record.exact_reference_resonance_only is not True
        or record.raw_text_present is not False
        for record in snapshot.records
    ):
        issues.append("compiler_rmc_record_boundary_invalid")

    if result.echo.delivery_authorized is not False:
        issues.append("compiler_echo_delivery_authority_invalid")

    boundary = result.boundary
    if boundary.preview_only is not True:
        issues.append("compiler_preview_boundary_disabled")
    boundary_false_fields = (
        "external_reference_authority",
        "glyph_reference_authority",
        "google_drive_reference_authority",
        "panini_reference_authority",
        "chomsky_reference_authority",
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
        "delivery_performed",
    )
    if any(getattr(boundary, field) is not False for field in boundary_false_fields):
        issues.append("compiler_effect_boundary_invalid")

    receipt = result.receipt
    if (
        receipt.source_sha256 != custody.source_sha256
        or receipt.status is not result.status
        or receipt.deterministic is not True
        or receipt.preview_only is not True
        or receipt.writes_performed is not False
        or receipt.action_performed is not False
        or receipt.delivery_performed is not False
    ):
        issues.append("compiler_receipt_boundary_invalid")

    return tuple(sorted(set(issues)))


def _build_unchecked(
    result: MeaningCompilerPreviewResult,
) -> GovernedClarificationRequest | None:
    admitted = _eligible_alternatives(result)
    if len(admitted) < 2:
        return None

    prepared: list[tuple[object, object, tuple[ClarificationRoleOption, ...]]] = []
    for candidate in admitted:
        contract = semantic_contract_for_candidate(
            candidate,
            result.frame_candidates,
        )
        roles = tuple(
            sorted(
                (_role_option(role) for role in candidate.roles),
                key=lambda item: (
                    item.role_key,
                    item.concept_ref,
                    item.sense_ref,
                ),
            )
        )
        prepared.append((candidate, contract, roles))

    role_keys = {
        role.role_key
        for _candidate, _contract, roles in prepared
        for role in roles
    }
    distinguishing_role_keys = {
        role_key
        for role_key in role_keys
        if len(
            {
                (role.concept_ref, role.sense_ref)
                for _candidate, _contract, roles in prepared
                for role in roles
                if role.role_key == role_key
            }
        )
        > 1
    }

    base_labels = tuple(
        _option_label(
            tuple(
                role
                for role in roles
                if role.role_key in distinguishing_role_keys
            )
            or roles
        )
        for _candidate, _contract, roles in prepared
    )
    option_labels = _distinguish_option_labels(
        base_labels,
        tuple(candidate for candidate, _contract, _roles in prepared),
        tuple(contract for _candidate, contract, _roles in prepared),
    )

    built_options: list[ClarificationOption] = []
    for (candidate, contract, roles), option_label in zip(
        prepared,
        option_labels,
    ):
        option_body = {
            "meaning_candidate_ref": candidate.meaning_candidate_id,
            "semantic_contract_ref": contract.semantic_contract_id,
            "semantic_signature_ref": candidate.semantic_signature,
            "frame_candidate_ref": candidate.frame_candidate_ref,
            "option_label": option_label,
            "roles": roles,
            "provisional": True,
            "selection_authority": False,
        }
        built_options.append(
            ClarificationOption(
                option_id=stable_record_id(
                    "governed_clarification_option",
                    option_body,
                ),
                **option_body,
            )
        )
    options = tuple(
        sorted(
            built_options,
            key=lambda item: (
                item.option_label.casefold(),
                item.meaning_candidate_ref,
            ),
        )
    )
    # Multiple source derivations of the same complete semantic contract do
    # not create a genuine meaning choice and must not provoke a question.
    if len({item.semantic_contract_ref for item in options}) < 2:
        return None

    wording = _clarification_wording(options)
    wording_body = {
        "compiler_result_ref": result.result_id,
        "compiler_receipt_ref": result.receipt.receipt_id,
        "source_custody_ref": result.source_custody.custody_result_id,
        "rmc_context_ref": result.rmc_context.evaluation_id,
        "alternative_option_refs": tuple(item.option_id for item in options),
        "text": wording,
        "delivery_authorized": False,
    }
    request_body = {
        "schema_version": GOVERNED_CLARIFICATION_SCHEMA_VERSION,
        "status": "CLARIFICATION_REQUIRED",
        "reason_code": CLARIFICATION_REASON,
        "compiler_result_ref": result.result_id,
        "compiler_receipt_ref": result.receipt.receipt_id,
        "source_custody_ref": result.source_custody.custody_result_id,
        "source_sha256": result.source_custody.source_sha256,
        "rmc_context_ref": result.rmc_context.evaluation_id,
        "candidate_wording_id": stable_record_id(
            "governed_clarification_candidate_wording",
            wording_body,
        ),
        "candidate_wording": wording,
        "alternative_meaning_refs": tuple(
            item.meaning_candidate_ref for item in options
        ),
        "alternative_count": len(options),
        "options": options,
        "resolution_required": "operator_clarification",
        "all_admitted_alternatives_preserved": True,
        "preview_only": True,
        "recommendation_only": True,
        "operator_response_required": True,
        "operator_preview_exposed": True,
        "clarification_question_preview_exposed": True,
        "live_clarification_session_started": False,
        "clarification_response_consumed": False,
        "selection_performed": False,
        "delivery_authorized": False,
        "delivery_performed": False,
        "answer_delivery_performed": False,
        "action_authorized": False,
        "tool_routing_authorized": False,
        "memory_write_authorized": False,
        "memory_write_performed": False,
    }
    return GovernedClarificationRequest(
        clarification_request_id=stable_record_id(
            "governed_clarification_request",
            request_body,
        ),
        **request_body,
    )


def _validate_exact_projection(
    request: GovernedClarificationRequest,
    compiler_result: MeaningCompilerPreviewResult,
) -> tuple[str, ...]:
    """Validate a request after its compiler result has been authenticated."""

    issues: list[str] = []
    if request.clarification_request_id != request.expected_id():
        issues.append("clarification_request_id_content_mismatch")
    if any(item.option_id != item.expected_id() for item in request.options):
        issues.append("clarification_option_id_content_mismatch")
    expected = _build_unchecked(compiler_result)
    if expected is None:
        issues.append("compiler_result_not_clarification_eligible")
    elif request != expected:
        issues.append("clarification_request_not_exact_compiler_projection")
    forbidden_true = (
        request.live_clarification_session_started,
        request.clarification_response_consumed,
        request.selection_performed,
        request.delivery_authorized,
        request.delivery_performed,
        request.answer_delivery_performed,
        request.action_authorized,
        request.tool_routing_authorized,
        request.memory_write_authorized,
        request.memory_write_performed,
    )
    if any(forbidden_true):
        issues.append("clarification_authority_or_effect_enabled")
    if (
        request.preview_only is not True
        or request.recommendation_only is not True
        or request.operator_response_required is not True
        or request.operator_preview_exposed is not True
        or request.clarification_question_preview_exposed is not True
        or request.all_admitted_alternatives_preserved is not True
    ):
        issues.append("clarification_required_boundary_disabled")
    return tuple(sorted(set(issues)))


def validate_governed_clarification_request(
    request: object,
    compiler_result: object,
) -> tuple[str, ...]:
    """Validate exact membership, identities, and the no-authority boundary."""

    if type(request) is not GovernedClarificationRequest:
        return ("clarification_request_type_not_admitted",)
    if type(compiler_result) is not MeaningCompilerPreviewResult:
        return ("compiler_result_type_not_admitted",)
    compiler_issues = _compiler_result_validation_issues(compiler_result)
    if compiler_issues:
        return compiler_issues
    return _validate_exact_projection(request, compiler_result)


def build_governed_clarification_request(
    compiler_result: object,
) -> GovernedClarificationRequest | None:
    """Build a question preview only for a held, materially ambiguous result."""

    if type(compiler_result) is not MeaningCompilerPreviewResult:
        raise TypeError("compiler_result_must_be_meaning_preview_result")
    compiler_issues = _compiler_result_validation_issues(compiler_result)
    if compiler_issues:
        raise ValueError(compiler_issues[0])
    request = _build_unchecked(compiler_result)
    if request is None:
        return None
    issues = _validate_exact_projection(request, compiler_result)
    if issues:
        raise ValueError(issues[0])
    return request


__all__ = (
    "CLARIFICATION_REASON",
    "GOVERNED_CLARIFICATION_SCHEMA_VERSION",
    "ClarificationOption",
    "ClarificationRoleOption",
    "GovernedClarificationRequest",
    "build_governed_clarification_request",
    "validate_governed_clarification_request",
)
