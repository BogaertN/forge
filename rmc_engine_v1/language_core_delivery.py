"""One-time operator approval for exact Language Core definition output.

The deterministic Ask Forge preview remains the source of every semantic and
rendering object.  This module never accepts caller-authored answer text.  It
replays the complete preview, binds the trace/manifest/render/Echo/Council
identities to one short-lived local-session nonce, and returns the already
validated text only after exact operator confirmation.

No file, RMC memory, Identity Vault, contribution-economy, tool, shell, model,
token, embedding, vector, or similarity authority exists here.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
import hashlib
import secrets
import threading
import time
from typing import Final

from aiweb_language_core_bootstrap.schema import canonicalize, stable_record_id


DELIVERY_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-operator-approved-language-output-delivery-v1"
)
DELIVERY_WORKFLOW_VERSION: Final[str] = (
    "forge-language-output-prepare-approve-v1"
)
PREPARE_ENDPOINT: Final[str] = (
    "/api/operator/ask-forge/language-core-delivery/prepare"
)
APPROVE_ENDPOINT: Final[str] = (
    "/api/operator/ask-forge/language-core-delivery/approve"
)
APPROVAL_TOKEN: Final[str] = "APPROVE_LANGUAGE_OUTPUT"
NONCE_TTL_SECONDS: Final[int] = 10 * 60

_PREPARE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "preview_request",
        "integrated_result_id",
        "integrated_receipt_id",
        "compiler_result_id",
        "compiler_receipt_id",
        "manifest_id",
        "rendered_output_id",
        "exact_echo_id",
        "operator_council_result_id",
    }
)
_APPROVE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        *_PREPARE_FIELDS,
        "delivery_proposal_id",
        "approval_token",
        "approval_confirmation_phrase",
    }
)


class LanguageCoreDeliveryError(ValueError):
    """Typed fail-closed refusal without raw evidence disclosure."""

    def __init__(self, reason_code: str, http_status: int = 422) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code
        self.http_status = http_status


@dataclass(frozen=True, slots=True)
class _DeliveryEvidence:
    preview_request_ref: str
    integrated_result_id: str
    integrated_receipt_id: str
    compiler_result_id: str
    compiler_receipt_id: str
    manifest_id: str
    rendered_output_id: str
    exact_echo_id: str
    operator_council_result_id: str
    rendered_text: str
    rendered_text_sha256: str

    def reference_payload(self) -> dict[str, object]:
        value = canonicalize(asdict(self))
        value.pop("rendered_text", None)
        return value


@dataclass(frozen=True, slots=True)
class _DeliveryGrant:
    session_ref: str
    delivery_proposal_id: str
    evidence: _DeliveryEvidence
    confirmation_phrase: str
    expires_at_monotonic: float


@dataclass(frozen=True, slots=True)
class OperatorApprovedLanguageDeliveryReceipt:
    receipt_id: str
    schema_version: str
    delivery_proposal_ref: str
    session_ref: str
    preview_request_ref: str
    integrated_result_ref: str
    integrated_receipt_ref: str
    compiler_result_ref: str
    compiler_receipt_ref: str
    manifest_ref: str
    rendered_output_ref: str
    exact_echo_ref: str
    operator_council_result_ref: str
    rendered_text_sha256: str
    approval_token_ref: str
    action_nonce_ref: str
    same_origin_operator_confirmation: bool
    operator_identity_authenticated: bool
    exact_echo_passed: bool
    delivery_status: str
    delivery_performed: bool
    answer_delivery_performed: bool
    filesystem_write_performed: bool
    memory_write_performed: bool
    action_performed: bool
    tool_routing_performed: bool

    def identity_payload(self) -> dict[str, object]:
        value = canonicalize(asdict(self))
        value.pop("receipt_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "operator_approved_language_delivery_receipt",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return canonicalize(asdict(self))


_NONCE_LOCK = threading.Lock()
_NONCES: dict[str, _DeliveryGrant] = {}


def _boundary(*, stage: str, delivered: bool) -> dict[str, object]:
    return {
        "stage": stage,
        "forge_governs": True,
        "ui_is_authority": False,
        "local_same_origin_required": True,
        "explicit_operator_confirmation_required": True,
        "one_time_action_nonce_required": stage == "approve",
        "definition_answers_only": True,
        "controlled_restatement_delivery_allowed": False,
        "caller_supplied_answer_text_allowed": False,
        "operator_identity_authenticated": False,
        "tokenization_performed": False,
        "model_called": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "memory_write_performed": False,
        "identity_write_performed": False,
        "contribution_economy_write_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": delivered,
        "answer_delivery_performed": delivered,
    }


def _reject(
    reason_code: str,
    *,
    stage: str,
    http_status: int = 422,
) -> dict[str, object]:
    return {
        "status": "REJECTED",
        "reason_code": reason_code,
        "http_status": http_status,
        "schema_version": DELIVERY_SCHEMA_VERSION,
        "workflow_version": DELIVERY_WORKFLOW_VERSION,
        "delivery_performed": False,
        "answer_delivery_performed": False,
        "writes_performed": False,
        "written_refs": [],
        "restart_required": False,
        "boundary": _boundary(stage=stage, delivered=False),
    }


def _strict_request(
    request: object,
    expected_fields: frozenset[str],
) -> dict[str, object]:
    if type(request) is not dict:
        raise LanguageCoreDeliveryError("delivery_request_must_be_json_object", 400)
    if set(request) != expected_fields:
        raise LanguageCoreDeliveryError("delivery_request_fields_not_exact", 400)
    if len(request) != len(expected_fields):
        raise LanguageCoreDeliveryError("delivery_request_fields_not_unique", 400)
    return request


def _non_empty_text(value: object, reason: str) -> str:
    if type(value) is not str or not value:
        raise LanguageCoreDeliveryError(reason, 400)
    return value


def _session_ref(session_id: object) -> str:
    value = _non_empty_text(session_id, "forge_session_required")
    if len(value) > 512:
        raise LanguageCoreDeliveryError("forge_session_invalid", 403)
    return stable_record_id("forge_operator_session", value)


def _record(value: object, reason: str) -> dict[str, object]:
    if type(value) is not dict:
        raise LanguageCoreDeliveryError(reason, 409)
    return value


def _record_id(
    value: Mapping[str, object],
    reason: str,
    *keys: str,
) -> str:
    for key in keys:
        candidate = value.get(key)
        if type(candidate) is str and candidate:
            return candidate
    raise LanguageCoreDeliveryError(reason, 409)


def _preview_request(value: object) -> dict[str, object]:
    if type(value) is not dict:
        raise LanguageCoreDeliveryError("preview_request_must_be_json_object", 400)
    if set(value) not in (
        {"source_text"},
        {"source_text", "clarification_reentry"},
    ):
        raise LanguageCoreDeliveryError("preview_request_fields_not_exact", 400)
    if type(value.get("source_text")) is not str:
        raise LanguageCoreDeliveryError("preview_source_text_must_be_string", 400)
    return value


def _effect_boundary_is_closed(boundary: Mapping[str, object]) -> bool:
    return all(
        boundary.get(field) is not True
        for field in (
            "model_called",
            "calls_llm",
            "tokenization_performed",
            "llm_tokenization_performed",
            "embedding_used",
            "uses_embeddings",
            "vector_used",
            "uses_vectors",
            "similarity_scoring_used",
            "filesystem_write_performed",
            "memory_write_performed",
            "rmc_memory_write_performed",
            "identity_write_performed",
            "contribution_economy_write_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
            "answer_delivery_authorized",
            "answer_delivery_performed",
        )
    )


def _recompute_evidence(preview_request: dict[str, object]) -> _DeliveryEvidence:
    # Function-local import keeps the deterministic preview independent from
    # this nonce-bearing delivery layer.
    from rmc_engine_v1.meaning_compiler_preview import (
        build_language_core_preview_response,
    )

    preview = build_language_core_preview_response(preview_request)
    if preview.get("status") != "PREVIEW_READY":
        raise LanguageCoreDeliveryError("preview_not_ready_for_delivery", 409)
    if preview.get("clarification_request") is not None:
        raise LanguageCoreDeliveryError("clarification_cannot_enter_delivery", 409)

    governed = _record(
        preview.get("governed_output"),
        "governed_output_manifest_missing",
    )
    if governed.get("answer_delivery_eligible") is not True:
        raise LanguageCoreDeliveryError("output_not_answer_delivery_eligible", 409)
    if governed.get("output_purpose") != "definition_answer":
        raise LanguageCoreDeliveryError("only_definition_answers_are_deliverable", 409)

    manifest = _record(
        governed.get("manifest"),
        "language_output_manifest_missing",
    )
    rendered = _record(
        governed.get("rendered_output"),
        "rendered_language_output_missing",
    )
    exact_echo = _record(
        governed.get("exact_echo"),
        "exact_language_echo_missing",
    )
    if exact_echo.get("status") != "PASS":
        raise LanguageCoreDeliveryError("exact_language_echo_not_passed", 409)
    exact_contract = exact_echo.get("exact_contract_match")
    exact_echo_checks = (
        exact_echo.get("transition_admitted"),
        exact_contract,
        exact_echo.get("exact_role_match"),
        exact_echo.get("exact_relation_match"),
        exact_echo.get("unique_decode"),
        exact_echo.get("full_source_coverage"),
    )
    if not all(value is True for value in exact_echo_checks):
        checks = exact_echo.get("checks")
        if type(checks) is not dict or not checks or not all(
            value is True for value in checks.values()
        ):
            raise LanguageCoreDeliveryError(
                "exact_language_echo_contract_not_preserved",
                409,
            )

    council = _record(
        preview.get("operator_council"),
        "operator_council_missing",
    )
    council_result = _record(
        council.get("result"),
        "operator_council_result_missing",
    )
    recommendation = _record(
        council_result.get("recommendation"),
        "operator_council_recommendation_missing",
    )
    if (
        council.get("status") != "RECOMMEND_FOR_OPERATOR_REVIEW"
        or council.get("recommendation_only") is not True
        or recommendation.get("executable") is not False
        or recommendation.get("authoritative") is not False
    ):
        raise LanguageCoreDeliveryError(
            "operator_council_did_not_recommend_human_review",
            409,
        )
    if preview.get("operator_council_admitted_rmc_exact_resonance_count", 0) < 1:
        raise LanguageCoreDeliveryError("trusted_exact_rmc_support_required", 409)
    provider = _record(
        preview.get("trusted_rmc_provider"),
        "trusted_rmc_provider_missing",
    )
    if provider.get("load_status") != "TRUSTED_STRUCTURED":
        raise LanguageCoreDeliveryError("trusted_structured_rmc_required", 409)

    for value in (
        _record(preview.get("boundary"), "preview_boundary_missing"),
        _record(governed.get("boundary"), "governed_output_boundary_missing"),
        _record(manifest.get("boundary"), "manifest_boundary_missing"),
        _record(rendered.get("boundary"), "rendered_output_boundary_missing"),
        _record(exact_echo.get("boundary"), "exact_echo_boundary_missing"),
    ):
        if not _effect_boundary_is_closed(value):
            raise LanguageCoreDeliveryError(
                "pre_delivery_effect_boundary_not_closed",
                409,
            )

    rendered_text = rendered.get("text", rendered.get("rendered_text"))
    rendered_text = _non_empty_text(
        rendered_text,
        "rendered_language_text_missing",
    )
    if preview.get("candidate_wording") != rendered_text:
        raise LanguageCoreDeliveryError(
            "rendered_language_differs_from_compiler_projection",
            409,
        )

    receipt = _record(preview.get("receipt"), "integrated_receipt_missing")
    compiler_receipt = _record(
        preview.get("compiler_receipt"),
        "compiler_receipt_missing",
    )
    preview_request_ref = stable_record_id(
        "language_core_preview_request",
        preview_request,
    )
    return _DeliveryEvidence(
        preview_request_ref=preview_request_ref,
        integrated_result_id=_record_id(
            preview,
            "integrated_result_id_missing",
            "result_id",
        ),
        integrated_receipt_id=_record_id(
            receipt,
            "integrated_receipt_id_missing",
            "receipt_id",
        ),
        compiler_result_id=_record_id(
            preview,
            "compiler_result_id_missing",
            "compiler_result_id",
        ),
        compiler_receipt_id=_record_id(
            compiler_receipt,
            "compiler_receipt_id_missing",
            "receipt_id",
        ),
        manifest_id=_record_id(
            manifest,
            "language_output_manifest_id_missing",
            "manifest_id",
        ),
        rendered_output_id=_record_id(
            rendered,
            "rendered_output_id_missing",
            "rendered_output_id",
            "output_id",
        ),
        exact_echo_id=_record_id(
            exact_echo,
            "exact_echo_id_missing",
            "echo_validation_id",
            "echo_id",
        ),
        operator_council_result_id=_record_id(
            council_result,
            "operator_council_result_id_missing",
            "result_id",
        ),
        rendered_text=rendered_text,
        rendered_text_sha256=hashlib.sha256(
            rendered_text.encode("utf-8")
        ).hexdigest(),
    )


def _assert_request_bindings(
    request: Mapping[str, object],
    evidence: _DeliveryEvidence,
) -> None:
    expected = {
        "integrated_result_id": evidence.integrated_result_id,
        "integrated_receipt_id": evidence.integrated_receipt_id,
        "compiler_result_id": evidence.compiler_result_id,
        "compiler_receipt_id": evidence.compiler_receipt_id,
        "manifest_id": evidence.manifest_id,
        "rendered_output_id": evidence.rendered_output_id,
        "exact_echo_id": evidence.exact_echo_id,
        "operator_council_result_id": evidence.operator_council_result_id,
    }
    if any(request.get(field) != value for field, value in expected.items()):
        raise LanguageCoreDeliveryError(
            "delivery_evidence_binding_mismatch",
            403,
        )


def _proposal_id(session_ref: str, evidence: _DeliveryEvidence) -> str:
    return stable_record_id(
        "language_output_delivery_proposal",
        {
            "schema_version": DELIVERY_SCHEMA_VERSION,
            "session_ref": session_ref,
            **evidence.reference_payload(),
        },
    )


def _confirmation_phrase(evidence: _DeliveryEvidence) -> str:
    return (
        f"APPROVE {evidence.rendered_output_id} FROM "
        f"{evidence.manifest_id} WITH {evidence.exact_echo_id}"
    )


def _issue_nonce(grant: _DeliveryGrant) -> str:
    token = secrets.token_urlsafe(32)
    with _NONCE_LOCK:
        now = time.monotonic()
        for key, value in tuple(_NONCES.items()):
            if (
                value.expires_at_monotonic <= now
                or value.session_ref == grant.session_ref
            ):
                _NONCES.pop(key, None)
        _NONCES[token] = grant
    return token


def _peek_nonce(token: object, session_ref: str) -> _DeliveryGrant:
    if type(token) is not str or not token:
        raise LanguageCoreDeliveryError("delivery_action_nonce_required", 403)
    with _NONCE_LOCK:
        grant = _NONCES.get(token)
    if grant is None:
        raise LanguageCoreDeliveryError("delivery_action_nonce_invalid", 403)
    if grant.session_ref != session_ref:
        raise LanguageCoreDeliveryError("delivery_action_nonce_session_mismatch", 403)
    if grant.expires_at_monotonic <= time.monotonic():
        with _NONCE_LOCK:
            _NONCES.pop(token, None)
        raise LanguageCoreDeliveryError("delivery_action_nonce_expired", 403)
    return grant


def _consume_nonce(token: str, expected: _DeliveryGrant) -> None:
    with _NONCE_LOCK:
        actual = _NONCES.pop(token, None)
    if actual != expected or actual.expires_at_monotonic <= time.monotonic():
        raise LanguageCoreDeliveryError(
            "delivery_action_nonce_replayed_or_stale",
            403,
        )


def prepare_language_core_delivery(
    request: object,
    *,
    session_id: object,
    local_request_verified: bool = False,
) -> dict[str, object]:
    """Prepare one definition answer for exact operator approval."""

    try:
        if local_request_verified is not True:
            raise LanguageCoreDeliveryError(
                "local_same_origin_request_required",
                403,
            )
        req = _strict_request(request, _PREPARE_FIELDS)
        preview_request = _preview_request(req.get("preview_request"))
        session_ref = _session_ref(session_id)
        evidence = _recompute_evidence(preview_request)
        _assert_request_bindings(req, evidence)
        proposal_id = _proposal_id(session_ref, evidence)
        phrase = _confirmation_phrase(evidence)
        grant = _DeliveryGrant(
            session_ref=session_ref,
            delivery_proposal_id=proposal_id,
            evidence=evidence,
            confirmation_phrase=phrase,
            expires_at_monotonic=time.monotonic() + NONCE_TTL_SECONDS,
        )
        nonce = _issue_nonce(grant)
        return {
            "status": "PREPARED",
            "reason_code": "exact_language_output_delivery_prepared",
            "http_status": 200,
            "schema_version": DELIVERY_SCHEMA_VERSION,
            "workflow_version": DELIVERY_WORKFLOW_VERSION,
            "delivery_proposal_id": proposal_id,
            **evidence.reference_payload(),
            "approval_token": APPROVAL_TOKEN,
            "approval_confirmation_phrase": phrase,
            "delivery_action_nonce": nonce,
            "action_nonce_expires_in_seconds": NONCE_TTL_SECONDS,
            "delivery_performed": False,
            "answer_delivery_performed": False,
            "writes_performed": False,
            "written_refs": [],
            "restart_required": False,
            "boundary": _boundary(stage="prepare", delivered=False),
        }
    except LanguageCoreDeliveryError as error:
        return _reject(
            error.reason_code,
            stage="prepare",
            http_status=error.http_status,
        )
    except Exception:
        return _reject(
            "language_output_delivery_prepare_failed_closed",
            stage="prepare",
            http_status=409,
        )


def approve_language_core_delivery(
    request: object,
    *,
    session_id: object,
    action_nonce: object,
    local_request_verified: bool = False,
) -> dict[str, object]:
    """Consume one exact nonce and return only the bound definition answer."""

    try:
        if local_request_verified is not True:
            raise LanguageCoreDeliveryError(
                "local_same_origin_request_required",
                403,
            )
        req = _strict_request(request, _APPROVE_FIELDS)
        preview_request = _preview_request(req.get("preview_request"))
        session_ref = _session_ref(session_id)
        grant = _peek_nonce(action_nonce, session_ref)
        evidence = _recompute_evidence(preview_request)
        _assert_request_bindings(req, evidence)
        proposal_id = _proposal_id(session_ref, evidence)
        phrase = _confirmation_phrase(evidence)
        if (
            req.get("delivery_proposal_id") != proposal_id
            or req.get("approval_token") != APPROVAL_TOKEN
            or req.get("approval_confirmation_phrase") != phrase
            or grant.delivery_proposal_id != proposal_id
            or grant.evidence != evidence
            or grant.confirmation_phrase != phrase
        ):
            raise LanguageCoreDeliveryError(
                "delivery_approval_binding_or_confirmation_mismatch",
                403,
            )
        _consume_nonce(str(action_nonce), grant)
        nonce_ref = stable_record_id(
            "language_output_delivery_action_nonce",
            str(action_nonce),
        )
        token_ref = stable_record_id(
            "language_output_delivery_approval_token",
            APPROVAL_TOKEN,
        )
        body = {
            "schema_version": DELIVERY_SCHEMA_VERSION,
            "delivery_proposal_ref": proposal_id,
            "session_ref": session_ref,
            "preview_request_ref": evidence.preview_request_ref,
            "integrated_result_ref": evidence.integrated_result_id,
            "integrated_receipt_ref": evidence.integrated_receipt_id,
            "compiler_result_ref": evidence.compiler_result_id,
            "compiler_receipt_ref": evidence.compiler_receipt_id,
            "manifest_ref": evidence.manifest_id,
            "rendered_output_ref": evidence.rendered_output_id,
            "exact_echo_ref": evidence.exact_echo_id,
            "operator_council_result_ref": (
                evidence.operator_council_result_id
            ),
            "rendered_text_sha256": evidence.rendered_text_sha256,
            "approval_token_ref": token_ref,
            "action_nonce_ref": nonce_ref,
            "same_origin_operator_confirmation": True,
            "operator_identity_authenticated": False,
            "exact_echo_passed": True,
            "delivery_status": "OPERATOR_APPROVED_LANGUAGE_OUTPUT_DELIVERED",
            "delivery_performed": True,
            "answer_delivery_performed": True,
            "filesystem_write_performed": False,
            "memory_write_performed": False,
            "action_performed": False,
            "tool_routing_performed": False,
        }
        receipt = OperatorApprovedLanguageDeliveryReceipt(
            receipt_id=stable_record_id(
                "operator_approved_language_delivery_receipt",
                body,
            ),
            **body,
        )
        if receipt.receipt_id != receipt.expected_id():
            raise LanguageCoreDeliveryError(
                "delivery_receipt_identity_mismatch",
                409,
            )
        return {
            "status": "DELIVERED",
            "reason_code": "operator_approved_exact_language_output_delivered",
            "http_status": 200,
            "schema_version": DELIVERY_SCHEMA_VERSION,
            "workflow_version": DELIVERY_WORKFLOW_VERSION,
            "delivery_proposal_id": proposal_id,
            "delivered_text": evidence.rendered_text,
            "delivery_receipt": receipt.to_dict(),
            "delivery_performed": True,
            "answer_delivery_performed": True,
            "writes_performed": False,
            "written_refs": [],
            "restart_required": False,
            "boundary": _boundary(stage="approve", delivered=True),
        }
    except LanguageCoreDeliveryError as error:
        return _reject(
            error.reason_code,
            stage="approve",
            http_status=error.http_status,
        )
    except Exception:
        return _reject(
            "language_output_delivery_approve_failed_closed",
            stage="approve",
            http_status=409,
        )


__all__ = (
    "APPROVAL_TOKEN",
    "APPROVE_ENDPOINT",
    "DELIVERY_SCHEMA_VERSION",
    "DELIVERY_WORKFLOW_VERSION",
    "NONCE_TTL_SECONDS",
    "OperatorApprovedLanguageDeliveryReceipt",
    "PREPARE_ENDPOINT",
    "approve_language_core_delivery",
    "prepare_language_core_delivery",
)
