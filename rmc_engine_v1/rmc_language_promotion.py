"""Governed prepare -> approve -> promote workflow for Language Core RMC.

Only the eight exact fixtures in the first Forge semantic-charter proposal can
enter this workflow.  Preparation is response-only.  Approval persists
content-addressed source and operator-decision receipts.  Promotion requires a
second, one-time confirmation and creates one immutable v2 exact-language
record in the stable store.  Ordinary Ask Forge requests never call this
module and retain no write authority.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import secrets
import stat
import tempfile
import threading
import time
from typing import Final, Iterator, Mapping

from aiweb_language_core_bootstrap.governed_semantic_charter import (
    SemanticReplayFixture,
    assert_valid_semantic_charter,
    proposed_semantic_charter,
    replay_semantic_charter,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview import (
    EchoStatus,
    PreviewStatus,
    build_rmc_context_snapshot,
    compile_meaning_preview,
    forge_seed_registry,
    semantic_contract_for_candidate,
)
from aiweb_language_core_bootstrap.schema import canonicalize, stable_record_id

from rmc_engine_v1.rmc_exact_language_store import (
    ExactLanguageMemoryRecord,
    build_exact_language_memory_record,
    language_memory_root,
    load_trusted_rmc_language_store,
)
from rmc_engine_v1.rmc_language_receipts import (
    APPROVAL_RECEIPT_DIRECTORY,
    APPROVAL_TOKEN,
    PROMOTION_RECEIPT_DIRECTORY,
    PROMOTION_TOKEN,
    SOURCE_RECEIPT_DIRECTORY,
    LanguageOperatorApprovalReceipt,
    LanguagePromotionReceipt,
    LanguageReceiptError,
    LanguageSourceReceipt,
    approval_confirmation_phrase,
    build_language_operator_approval_receipt,
    build_language_promotion_receipt,
    build_language_source_receipt,
    governance_root,
    language_record_draft_ref,
    promotion_confirmation_phrase,
    verify_language_record_receipts,
)


LANGUAGE_PROMOTION_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-governed-language-memory-promotion-v1"
)
LANGUAGE_PROMOTION_VERSION: Final[str] = (
    "forge-language-memory-prepare-approve-promote-v1"
)
NONCE_TTL_SECONDS: Final[int] = 10 * 60
MAX_REQUEST_FIELDS: Final[int] = 8
DEFAULT_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_PLACEHOLDER_APPROVAL_REF: Final[str] = (
    "operator_approval_receipt:" + ("0" * 64)
)


class LanguagePromotionError(ValueError):
    def __init__(self, reason_code: str, http_status: int = 422) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code
        self.http_status = http_status


@dataclass(frozen=True, slots=True)
class PreparedLanguageMemory:
    fixture: SemanticReplayFixture
    proposal_id: str
    record_draft_ref: str
    semantic_contract_ref: str
    source_receipt: LanguageSourceReceipt
    approval_receipt: LanguageOperatorApprovalReceipt
    record: ExactLanguageMemoryRecord
    approval_phrase: str
    promotion_phrase: str


@dataclass(frozen=True, slots=True)
class _NonceGrant:
    stage: str
    fixture_id: str
    proposal_id: str
    record_id: str
    approval_receipt_id: str
    expires_at_monotonic: float


_NONCE_LOCK = threading.Lock()
_NONCES: dict[str, _NonceGrant] = {}


def _boundary(*, stage: str, writes_files: bool, writes_memory: bool) -> dict[str, object]:
    return {
        "stage": stage,
        "forge_governs": True,
        "ui_is_authority": False,
        "ask_forge_write_authority": False,
        "explicit_operator_confirmation_required": stage in {"approve", "promote"},
        "local_same_origin_required": stage in {"prepare", "approve", "promote"},
        "one_time_action_nonce_required": stage in {"approve", "promote"},
        "charter_fixture_allowlist_only": True,
        "exact_semantic_contract_required": True,
        "stable_store_only": True,
        "automatic_approval": False,
        "automatic_promotion": False,
        "raw_text_written_to_memory": False,
        "tokenization_performed": False,
        "model_called": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
        "filesystem_write_performed": writes_files,
        "memory_write_performed": writes_memory,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "general_runtime_authority_granted": False,
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
        "schema_version": LANGUAGE_PROMOTION_SCHEMA_VERSION,
        "workflow_version": LANGUAGE_PROMOTION_VERSION,
        "writes_performed": False,
        "written_refs": [],
        "restart_required": False,
        "boundary": _boundary(
            stage=stage,
            writes_files=False,
            writes_memory=False,
        ),
    }


def _repo(repository_root: Path | str | None) -> Path:
    root = (
        DEFAULT_REPOSITORY_ROOT
        if repository_root is None
        else Path(repository_root).resolve()
    )
    root = root.resolve()
    default = DEFAULT_REPOSITORY_ROOT.resolve()
    temporary = Path(tempfile.gettempdir()).resolve()
    if root == default or (root != temporary and temporary in root.parents):
        return root
    raise LanguagePromotionError("repository_root_not_admitted", 403)


def _strict_request(value: object, fields: frozenset[str]) -> dict[str, object]:
    if type(value) is not dict:
        raise LanguagePromotionError("request_must_be_json_object", 400)
    if len(value) > MAX_REQUEST_FIELDS or set(value) != fields:
        raise LanguagePromotionError("request_fields_not_exact", 400)
    return value


def _fixture_by_id(fixture_id: object) -> SemanticReplayFixture:
    if type(fixture_id) is not str:
        raise LanguagePromotionError("fixture_id_must_be_string", 400)
    charter = assert_valid_semantic_charter(proposed_semantic_charter())
    matches = tuple(
        fixture
        for fixture in charter.replay_fixtures
        if fixture.fixture_id == fixture_id
    )
    if len(matches) != 1:
        raise LanguagePromotionError("fixture_not_in_proposed_charter", 404)
    return matches[0]


def _prepared_for_fixture(fixture: SemanticReplayFixture) -> PreparedLanguageMemory:
    charter = assert_valid_semantic_charter(proposed_semantic_charter())
    replay = replay_semantic_charter(charter)
    if replay.status.value != "PASS":
        raise LanguagePromotionError("semantic_charter_replay_not_ready", 409)
    construction_matches = tuple(
        item
        for item in charter.constructions
        if item.construction_id == fixture.construction_ref
    )
    if len(construction_matches) != 1:
        raise LanguagePromotionError("fixture_construction_not_unique", 409)
    construction = construction_matches[0]

    result = compile_meaning_preview(
        fixture.exact_source_text,
        rmc_snapshot=build_rmc_context_snapshot(),
    )
    selected = result.selected_meaning
    if (
        result.status is not PreviewStatus.PREVIEW_READY
        or selected is None
        or result.echo.status is not EchoStatus.PASS
        or result.echo.exact_signature_match is not True
        or selected.meaning_candidate_id != fixture.expected_meaning_candidate_ref
        or selected.semantic_signature != fixture.expected_semantic_signature
        or selected.predicate_ref != fixture.expected_predicate_ref
        or selected.negated is not fixture.expected_negated
        or tuple(item.role_key for item in selected.roles)
        != fixture.expected_role_keys
        or tuple(sorted({item.concept_ref for item in selected.roles}))
        != fixture.expected_concept_refs
        or tuple(sorted({item.sense_ref for item in selected.roles}))
        != fixture.expected_sense_refs
        or selected.relation_refs != fixture.expected_relation_refs
    ):
        raise LanguagePromotionError("fixture_compiler_replay_mismatch", 409)

    contract = semantic_contract_for_candidate(selected, result.frame_candidates)
    if (
        contract.semantic_signature_ref != fixture.expected_semantic_signature
        or contract.speech_act != construction.speech_act
        or contract.purport != construction.purport
        or contract.negated is not construction.negated
        or contract.frame_key != construction.frame_key
        or contract.grammar_rule_ref != construction.grammar_rule_id
        or contract.predicate_ref != construction.predicate_ref
    ):
        raise LanguagePromotionError("fixture_semantic_contract_mismatch", 409)

    registry = forge_seed_registry()
    role_ref_by_key = {item.role_key: item.role_id for item in registry.roles}
    role_refs = tuple(
        sorted({role_ref_by_key[item.role_key] for item in selected.roles})
    )
    source_form_refs = tuple(
        sorted(
            {
                reference
                for role in selected.roles
                for reference in role.source_form_refs
            }
        )
    )
    source_receipt = build_language_source_receipt(
        charter_ref=charter.charter_id,
        charter_entry_ref=fixture.fixture_id,
        registry_ref=registry.registry_id,
        compiler_result_ref=result.result_id,
        selected_meaning_ref=selected.meaning_candidate_id,
        semantic_contract_ref=contract.semantic_contract_id,
        source_sha256=result.source_custody.source_sha256,
        input_event_ref=result.source_custody.input_event_id,
        source_form_refs=source_form_refs,
        concept_refs=fixture.expected_concept_refs,
        sense_refs=fixture.expected_sense_refs,
        relation_refs=fixture.expected_relation_refs,
        role_refs=role_refs,
        ancestry_refs=selected.ancestry_refs,
        echo_receipt_ref=result.echo.echo_id,
    )

    record_args = {
        "store_class": "stable",
        "lifecycle_state": "accepted_stable",
        "registry_ref": registry.registry_id,
        "semantic_contract_ref": contract.semantic_contract_id,
        "semantic_signature_ref": contract.semantic_signature_ref,
        "speech_act": contract.speech_act,
        "purport": contract.purport,
        "negated": contract.negated,
        "frame_key": contract.frame_key,
        "grammar_rule_ref": contract.grammar_rule_ref,
        "predicate_ref": contract.predicate_ref,
        "concept_refs": fixture.expected_concept_refs,
        "sense_refs": fixture.expected_sense_refs,
        "relation_refs": fixture.expected_relation_refs,
        "role_refs": role_refs,
        "ancestry_refs": selected.ancestry_refs,
        "source_receipt_ref": source_receipt.source_receipt_id,
    }
    placeholder = build_exact_language_memory_record(
        **record_args,
        approval_receipt_ref=_PLACEHOLDER_APPROVAL_REF,
    )
    draft_ref = language_record_draft_ref(placeholder)
    proposal_body = {
        "schema_version": LANGUAGE_PROMOTION_SCHEMA_VERSION,
        "workflow_version": LANGUAGE_PROMOTION_VERSION,
        "charter_ref": charter.charter_id,
        "charter_entry_ref": fixture.fixture_id,
        "registry_ref": registry.registry_id,
        "semantic_contract_ref": contract.semantic_contract_id,
        "source_receipt_ref": source_receipt.source_receipt_id,
        "record_draft_ref": draft_ref,
        "store_class": "stable",
        "automatic_selection": False,
        "operator_approval_required": True,
    }
    proposal_id = stable_record_id("language_memory_proposal", proposal_body)
    approval_receipt = build_language_operator_approval_receipt(
        proposal_ref=proposal_id,
        charter_ref=charter.charter_id,
        charter_entry_ref=fixture.fixture_id,
        registry_ref=registry.registry_id,
        source_receipt_ref=source_receipt.source_receipt_id,
        semantic_contract_ref=contract.semantic_contract_id,
        record_draft_ref=draft_ref,
        store_class="stable",
    )
    record = build_exact_language_memory_record(
        **record_args,
        approval_receipt_ref=approval_receipt.approval_receipt_id,
    )
    if language_record_draft_ref(record) != draft_ref:
        raise LanguagePromotionError("final_record_draft_binding_mismatch", 409)
    return PreparedLanguageMemory(
        fixture=fixture,
        proposal_id=proposal_id,
        record_draft_ref=draft_ref,
        semantic_contract_ref=contract.semantic_contract_id,
        source_receipt=source_receipt,
        approval_receipt=approval_receipt,
        record=record,
        approval_phrase=approval_confirmation_phrase(proposal_id, draft_ref),
        promotion_phrase=promotion_confirmation_phrase(
            record.record_id,
            approval_receipt.approval_receipt_id,
        ),
    )


def _issue_nonce(stage: str, prepared: PreparedLanguageMemory) -> str:
    token = secrets.token_urlsafe(32)
    grant = _NonceGrant(
        stage=stage,
        fixture_id=prepared.fixture.fixture_id,
        proposal_id=prepared.proposal_id,
        record_id=prepared.record.record_id,
        approval_receipt_id=prepared.approval_receipt.approval_receipt_id,
        expires_at_monotonic=time.monotonic() + NONCE_TTL_SECONDS,
    )
    with _NONCE_LOCK:
        now = time.monotonic()
        expired = tuple(
            key
            for key, value in _NONCES.items()
            if value.expires_at_monotonic <= now
        )
        for key in expired:
            _NONCES.pop(key, None)
        _NONCES[token] = grant
    return token


def _peek_nonce(token: object, stage: str) -> _NonceGrant:
    if type(token) is not str or not token:
        raise LanguagePromotionError("action_nonce_required", 403)
    with _NONCE_LOCK:
        grant = _NONCES.get(token)
    if grant is None or grant.stage != stage:
        raise LanguagePromotionError("action_nonce_invalid", 403)
    if grant.expires_at_monotonic <= time.monotonic():
        with _NONCE_LOCK:
            _NONCES.pop(token, None)
        raise LanguagePromotionError("action_nonce_expired", 403)
    return grant


def _consume_nonce(token: str, expected: _NonceGrant) -> None:
    with _NONCE_LOCK:
        actual = _NONCES.pop(token, None)
    if actual != expected or actual.expires_at_monotonic <= time.monotonic():
        raise LanguagePromotionError("action_nonce_replayed_or_stale", 403)


def _validate_directory(path: Path, *, create: bool = False) -> None:
    if create and not os.path.lexists(path):
        path.mkdir(mode=0o700, parents=False, exist_ok=False)
    try:
        metadata = path.lstat()
    except OSError as error:
        raise LanguagePromotionError("governed_directory_unreadable", 409) from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise LanguagePromotionError("governed_directory_not_trusted", 409)
    if metadata.st_uid != os.geteuid() or metadata.st_mode & 0o022:
        raise LanguagePromotionError("governed_directory_permissions_rejected", 409)


def _ensure_roots(repository: Path) -> None:
    memory = repository / "memory"
    if not os.path.lexists(memory):
        memory.mkdir(mode=0o700, parents=False, exist_ok=False)
    _validate_directory(memory)
    governance = governance_root(repository)
    if not os.path.lexists(governance):
        governance.mkdir(mode=0o700, parents=False, exist_ok=False)
    _validate_directory(governance)
    for name in (
        SOURCE_RECEIPT_DIRECTORY,
        APPROVAL_RECEIPT_DIRECTORY,
        PROMOTION_RECEIPT_DIRECTORY,
    ):
        directory = governance / name
        _validate_directory(directory, create=True)


@contextmanager
def _promotion_lock(repository: Path) -> Iterator[None]:
    memory = repository / "memory"
    if not os.path.lexists(memory):
        memory.mkdir(mode=0o700, parents=False, exist_ok=False)
    _validate_directory(memory)
    lock_path = memory / ".rmc_language_core_promotion.lock"
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(lock_path, flags, 0o600)
    try:
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.geteuid()
            or metadata.st_nlink != 1
            or metadata.st_mode & 0o077
        ):
            raise LanguagePromotionError("promotion_lock_not_trusted", 409)
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _encoded_json(payload: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            canonicalize(dict(payload)),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _secure_existing_bytes(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.geteuid()
            or metadata.st_nlink != 1
            or metadata.st_mode & 0o022
            or metadata.st_size <= 0
            or metadata.st_size > 64 * 1024
        ):
            raise LanguagePromotionError("existing_artifact_not_trusted", 409)
        chunks: list[bytes] = []
        remaining = metadata.st_size
        while remaining:
            chunk = os.read(descriptor, min(8192, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) != metadata.st_size:
            raise LanguagePromotionError("existing_artifact_changed_during_read", 409)
        return payload
    finally:
        os.close(descriptor)


def _atomic_create_or_verify(path: Path, payload: Mapping[str, object]) -> bool:
    expected = _encoded_json(payload)
    if os.path.lexists(path):
        try:
            actual = _secure_existing_bytes(path)
        except OSError as error:
            raise LanguagePromotionError("existing_artifact_open_rejected", 409) from error
        if actual != expected:
            raise LanguagePromotionError("existing_artifact_content_conflict", 409)
        return False
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(expected)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if _secure_existing_bytes(path) != expected:
                raise LanguagePromotionError("concurrent_artifact_content_conflict", 409)
            return False
        finally:
            temporary.unlink(missing_ok=True)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return True
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)


def _receipt_path(repository: Path, directory: str, reference: str) -> Path:
    return governance_root(repository) / directory / (
        reference.split(":", 1)[1] + ".json"
    )


def _record_path(repository: Path, record: ExactLanguageMemoryRecord) -> Path:
    return language_memory_root(repository) / "stable" / (
        record.record_id.split(":", 1)[1] + ".json"
    )


def _provider_allows(prepared: PreparedLanguageMemory, repository: Path) -> tuple[bool, str]:
    provider = load_trusted_rmc_language_store(repository)
    if not provider.trusted or provider.load_status == "REJECTED":
        return False, "trusted_rmc_language_store_rejected"
    conflicts = tuple(
        record
        for record in provider.records
        if record.semantic_contract_ref == prepared.semantic_contract_ref
        and record.record_id != prepared.record.record_id
    )
    if conflicts:
        return False, "semantic_contract_already_bound_to_different_record"
    return True, "provider_ready"


def language_charter_status(
    *, repository_root: Path | str | None = None
) -> dict[str, object]:
    try:
        repository = _repo(repository_root)
        charter = assert_valid_semantic_charter(proposed_semantic_charter())
        replay = replay_semantic_charter(charter)
        provider = load_trusted_rmc_language_store(repository)
        entries: list[dict[str, object]] = []
        approved_count = 0
        promoted_count = 0
        for fixture in charter.replay_fixtures:
            prepared = _prepared_for_fixture(fixture)
            approved = False
            try:
                verify_language_record_receipts(repository, prepared.record)
                approved = True
            except (LanguageReceiptError, OSError):
                approved = False
            exact_records = tuple(
                record
                for record in provider.records
                if record.record_id == prepared.record.record_id
            )
            contract_conflict = any(
                record.semantic_contract_ref == prepared.semantic_contract_ref
                and record.record_id != prepared.record.record_id
                for record in provider.records
            )
            promoted = len(exact_records) == 1
            approved_count += int(approved)
            promoted_count += int(promoted)
            state = (
                "CONFLICT"
                if contract_conflict
                else "PROMOTED"
                if promoted
                else "APPROVED_NOT_PROMOTED"
                if approved
                else "PROPOSED"
            )
            entries.append(
                {
                    "fixture_id": fixture.fixture_id,
                    "fixture_key": fixture.fixture_key,
                    "exact_source_text": fixture.exact_source_text,
                    "construction_ref": fixture.construction_ref,
                    "semantic_contract_ref": prepared.semantic_contract_ref,
                    "record_id": prepared.record.record_id,
                    "state": state,
                    "operator_approval_required": not approved,
                    # Approval persists evidence only.  No runtime-visible
                    # memory changes until the separate promotion commit.
                    "restart_required": False,
                }
            )
        state = (
            "FULLY_PROMOTED"
            if promoted_count == len(entries)
            else "PARTIALLY_PROMOTED"
            if promoted_count
            else "APPROVALS_PENDING"
        )
        return {
            "status": "OK" if replay.status.value == "PASS" and provider.trusted else "HELD",
            "reason_code": "governed_language_charter_status",
            "http_status": 200,
            "schema_version": LANGUAGE_PROMOTION_SCHEMA_VERSION,
            "workflow_version": LANGUAGE_PROMOTION_VERSION,
            "charter_id": charter.charter_id,
            "charter_status": charter.status.value,
            "activation_state": state,
            "registry_ref": charter.registry_ref,
            "entry_count": len(entries),
            "approved_count": approved_count,
            "promoted_count": promoted_count,
            "provider": provider.public_receipt(),
            "entries": entries,
            "writes_performed": False,
            "restart_required": False,
            "boundary": _boundary(
                stage="status", writes_files=False, writes_memory=False
            ),
        }
    except Exception:
        return _reject(
            "language_charter_status_failed_closed",
            stage="status",
            http_status=409,
        )


def prepare_language_memory(
    request: object,
    *,
    repository_root: Path | str | None = None,
    local_request_verified: bool = False,
) -> dict[str, object]:
    try:
        if local_request_verified is not True:
            raise LanguagePromotionError("local_same_origin_request_required", 403)
        req = _strict_request(request, frozenset({"fixture_id"}))
        repository = _repo(repository_root)
        prepared = _prepared_for_fixture(_fixture_by_id(req.get("fixture_id")))
        allowed, reason = _provider_allows(prepared, repository)
        if not allowed:
            raise LanguagePromotionError(reason, 409)
        nonce = _issue_nonce("approve", prepared)
        return {
            "status": "PREPARED",
            "reason_code": "exact_language_memory_proposal_prepared",
            "http_status": 200,
            "schema_version": LANGUAGE_PROMOTION_SCHEMA_VERSION,
            "workflow_version": LANGUAGE_PROMOTION_VERSION,
            "fixture_id": prepared.fixture.fixture_id,
            "fixture_key": prepared.fixture.fixture_key,
            "exact_source_text": prepared.fixture.exact_source_text,
            "proposal_id": prepared.proposal_id,
            "semantic_contract_ref": prepared.semantic_contract_ref,
            "record_draft_ref": prepared.record_draft_ref,
            "record_id": prepared.record.record_id,
            "source_receipt_id": prepared.source_receipt.source_receipt_id,
            "approval_receipt_id": prepared.approval_receipt.approval_receipt_id,
            "record_preview": prepared.record.to_dict(),
            "source_receipt_preview": prepared.source_receipt.to_dict(),
            "approval_receipt_preview": prepared.approval_receipt.to_dict(),
            "approval_token": APPROVAL_TOKEN,
            "approval_confirmation_phrase": prepared.approval_phrase,
            "approval_action_nonce": nonce,
            "action_nonce_expires_in_seconds": NONCE_TTL_SECONDS,
            "writes_performed": False,
            "written_refs": [],
            "restart_required": False,
            "boundary": _boundary(
                stage="prepare", writes_files=False, writes_memory=False
            ),
        }
    except LanguagePromotionError as error:
        return _reject(
            error.reason_code, stage="prepare", http_status=error.http_status
        )
    except Exception:
        return _reject(
            "language_memory_prepare_failed_closed",
            stage="prepare",
            http_status=409,
        )


def approve_language_memory(
    request: object,
    *,
    action_nonce: object,
    repository_root: Path | str | None = None,
    local_request_verified: bool = False,
) -> dict[str, object]:
    try:
        if local_request_verified is not True:
            raise LanguagePromotionError("local_same_origin_request_required", 403)
        req = _strict_request(
            request,
            frozenset(
                {
                    "proposal_id",
                    "record_id",
                    "approval_token",
                    "approval_confirmation_phrase",
                }
            ),
        )
        grant = _peek_nonce(action_nonce, "approve")
        prepared = _prepared_for_fixture(_fixture_by_id(grant.fixture_id))
        if (
            req.get("proposal_id") != prepared.proposal_id
            or req.get("record_id") != prepared.record.record_id
            or req.get("approval_token") != APPROVAL_TOKEN
            or req.get("approval_confirmation_phrase") != prepared.approval_phrase
            or grant.proposal_id != prepared.proposal_id
            or grant.record_id != prepared.record.record_id
            or grant.approval_receipt_id
            != prepared.approval_receipt.approval_receipt_id
        ):
            raise LanguagePromotionError("approval_binding_or_confirmation_mismatch", 403)
        _consume_nonce(str(action_nonce), grant)
        repository = _repo(repository_root)
        written: list[str] = []
        with _promotion_lock(repository):
            # Recompute the complete deterministic record/receipt packet while
            # holding the same lock that guards the visibility transition.
            locked_prepared = _prepared_for_fixture(
                _fixture_by_id(grant.fixture_id)
            )
            if locked_prepared != prepared:
                raise LanguagePromotionError(
                    "approval_packet_changed_before_locked_commit",
                    409,
                )
            prepared = locked_prepared
            allowed, reason = _provider_allows(prepared, repository)
            if not allowed:
                raise LanguagePromotionError(reason, 409)
            _ensure_roots(repository)
            source_path = _receipt_path(
                repository,
                SOURCE_RECEIPT_DIRECTORY,
                prepared.source_receipt.source_receipt_id,
            )
            approval_path = _receipt_path(
                repository,
                APPROVAL_RECEIPT_DIRECTORY,
                prepared.approval_receipt.approval_receipt_id,
            )
            if _atomic_create_or_verify(source_path, prepared.source_receipt.to_dict()):
                written.append(
                    f"memory/{governance_root(repository).name}/{SOURCE_RECEIPT_DIRECTORY}/{source_path.name}"
                )
            if _atomic_create_or_verify(
                approval_path, prepared.approval_receipt.to_dict()
            ):
                written.append(
                    f"memory/{governance_root(repository).name}/{APPROVAL_RECEIPT_DIRECTORY}/{approval_path.name}"
                )
            verify_language_record_receipts(repository, prepared.record)
        promotion_nonce = _issue_nonce("promote", prepared)
        return {
            "status": "APPROVED",
            "reason_code": "one_exact_language_record_approved",
            "http_status": 200,
            "schema_version": LANGUAGE_PROMOTION_SCHEMA_VERSION,
            "workflow_version": LANGUAGE_PROMOTION_VERSION,
            "fixture_id": prepared.fixture.fixture_id,
            "proposal_id": prepared.proposal_id,
            "record_id": prepared.record.record_id,
            "source_receipt_id": prepared.source_receipt.source_receipt_id,
            "approval_receipt_id": prepared.approval_receipt.approval_receipt_id,
            "promotion_token": PROMOTION_TOKEN,
            "promotion_confirmation_phrase": prepared.promotion_phrase,
            "promotion_action_nonce": promotion_nonce,
            "action_nonce_expires_in_seconds": NONCE_TTL_SECONDS,
            "writes_performed": bool(written),
            "written_refs": written,
            "memory_record_written": False,
            "restart_required": False,
            "boundary": _boundary(
                stage="approve",
                writes_files=bool(written),
                writes_memory=False,
            ),
        }
    except LanguagePromotionError as error:
        return _reject(
            error.reason_code, stage="approve", http_status=error.http_status
        )
    except (LanguageReceiptError, OSError):
        return _reject(
            "language_memory_approval_receipt_failed_closed",
            stage="approve",
            http_status=409,
        )
    except Exception:
        return _reject(
            "language_memory_approve_failed_closed",
            stage="approve",
            http_status=409,
        )


def promote_language_memory(
    request: object,
    *,
    action_nonce: object,
    repository_root: Path | str | None = None,
    local_request_verified: bool = False,
) -> dict[str, object]:
    try:
        if local_request_verified is not True:
            raise LanguagePromotionError("local_same_origin_request_required", 403)
        req = _strict_request(
            request,
            frozenset(
                {
                    "proposal_id",
                    "record_id",
                    "approval_receipt_id",
                    "promotion_token",
                    "promotion_confirmation_phrase",
                }
            ),
        )
        grant = _peek_nonce(action_nonce, "promote")
        prepared = _prepared_for_fixture(_fixture_by_id(grant.fixture_id))
        if (
            req.get("proposal_id") != prepared.proposal_id
            or req.get("record_id") != prepared.record.record_id
            or req.get("approval_receipt_id")
            != prepared.approval_receipt.approval_receipt_id
            or req.get("promotion_token") != PROMOTION_TOKEN
            or req.get("promotion_confirmation_phrase") != prepared.promotion_phrase
            or grant.proposal_id != prepared.proposal_id
            or grant.record_id != prepared.record.record_id
            or grant.approval_receipt_id
            != prepared.approval_receipt.approval_receipt_id
        ):
            raise LanguagePromotionError("promotion_binding_or_confirmation_mismatch", 403)
        _consume_nonce(str(action_nonce), grant)
        repository = _repo(repository_root)
        written: list[str] = []
        with _promotion_lock(repository):
            # Recompute the complete deterministic record/receipt packet while
            # holding the same lock that guards the stable-store commit.
            locked_prepared = _prepared_for_fixture(
                _fixture_by_id(grant.fixture_id)
            )
            if locked_prepared != prepared:
                raise LanguagePromotionError(
                    "promotion_packet_changed_before_locked_commit",
                    409,
                )
            prepared = locked_prepared
            allowed, reason = _provider_allows(prepared, repository)
            if not allowed:
                raise LanguagePromotionError(reason, 409)
            _ensure_roots(repository)
            verify_language_record_receipts(repository, prepared.record)
            store_root = language_memory_root(repository)
            if not os.path.lexists(store_root):
                store_root.mkdir(mode=0o700, parents=False, exist_ok=False)
            _validate_directory(store_root)
            stable = store_root / "stable"
            _validate_directory(stable, create=True)
            target = _record_path(repository, prepared.record)
            target_ref = (
                f"memory/{store_root.name}/stable/{target.name}"
            )
            promotion_receipt = build_language_promotion_receipt(
                proposal_ref=prepared.proposal_id,
                charter_ref=proposed_semantic_charter().charter_id,
                charter_entry_ref=prepared.fixture.fixture_id,
                registry_ref=forge_seed_registry().registry_id,
                source_receipt_ref=prepared.source_receipt.source_receipt_id,
                approval_receipt_ref=prepared.approval_receipt.approval_receipt_id,
                record_ref=prepared.record.record_id,
                target_ref=target_ref,
            )
            promotion_path = _receipt_path(
                repository,
                PROMOTION_RECEIPT_DIRECTORY,
                promotion_receipt.promotion_receipt_id,
            )
            # A newly created promotion receipt may only witness an absent
            # target.  When both artifacts already exist, this is an
            # idempotent verification of the original transition rather than
            # a new claim that the current target is absent.
            if os.path.lexists(target) and not os.path.lexists(promotion_path):
                raise LanguagePromotionError(
                    "promotion_receipt_missing_for_existing_target",
                    409,
                )
            if _atomic_create_or_verify(
                promotion_path, promotion_receipt.to_dict()
            ):
                written.append(
                    f"memory/{governance_root(repository).name}/{PROMOTION_RECEIPT_DIRECTORY}/{promotion_path.name}"
                )
            record_created = _atomic_create_or_verify(
                target, prepared.record.to_dict()
            )
            if record_created:
                written.append(target_ref)
            reloaded = load_trusted_rmc_language_store(repository)
            if (
                not reloaded.trusted
                or reloaded.load_status != "TRUSTED_STRUCTURED"
                or not any(
                    item.record_id == prepared.record.record_id
                    for item in reloaded.records
                )
            ):
                raise LanguagePromotionError(
                    "promoted_record_failed_provider_reload", 409
                )
        return {
            "status": "PROMOTED" if record_created else "ALREADY_PROMOTED",
            "reason_code": (
                "one_exact_stable_language_record_promoted"
                if record_created
                else "exact_language_record_already_present"
            ),
            "http_status": 200,
            "schema_version": LANGUAGE_PROMOTION_SCHEMA_VERSION,
            "workflow_version": LANGUAGE_PROMOTION_VERSION,
            "fixture_id": prepared.fixture.fixture_id,
            "proposal_id": prepared.proposal_id,
            "record_id": prepared.record.record_id,
            "source_receipt_id": prepared.source_receipt.source_receipt_id,
            "approval_receipt_id": prepared.approval_receipt.approval_receipt_id,
            "promotion_receipt_id": promotion_receipt.promotion_receipt_id,
            "writes_performed": bool(written),
            "written_refs": written,
            "memory_record_written": record_created,
            "restart_required": True,
            "restart_reason": "Ask Forge loads the trusted RMC snapshot at process start.",
            "boundary": _boundary(
                stage="promote",
                writes_files=bool(written),
                writes_memory=record_created,
            ),
        }
    except LanguagePromotionError as error:
        return _reject(
            error.reason_code, stage="promote", http_status=error.http_status
        )
    except (LanguageReceiptError, OSError):
        return _reject(
            "language_memory_promotion_receipt_failed_closed",
            stage="promote",
            http_status=409,
        )
    except Exception:
        return _reject(
            "language_memory_promote_failed_closed",
            stage="promote",
            http_status=409,
        )


__all__ = (
    "APPROVAL_TOKEN",
    "LANGUAGE_PROMOTION_SCHEMA_VERSION",
    "LANGUAGE_PROMOTION_VERSION",
    "PROMOTION_TOKEN",
    "approve_language_memory",
    "language_charter_status",
    "prepare_language_memory",
    "promote_language_memory",
)
