"""Content-addressed evidence receipts for governed Language Core memory.

The exact RMC record store contains references, not prose.  This module gives
those references an independently persisted meaning and verifies that a
record's source, operator-approval, and final promotion receipts actually
exist, are immutable, and bind the same exact semantic identities and commit
target.

Verification deterministically replays only the exact installed charter
fixture named by a receipt.  It does not accept arbitrary source text, call a
model, perform similarity search, or grant general Forge authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Final, Mapping

from aiweb_language_core_bootstrap.schema import canonicalize, stable_record_id


LANGUAGE_GOVERNANCE_DIRECTORY: Final[str] = "rmc_language_core_governance_v1"
SOURCE_RECEIPT_DIRECTORY: Final[str] = "source_receipts"
APPROVAL_RECEIPT_DIRECTORY: Final[str] = "approval_receipts"
PROMOTION_RECEIPT_DIRECTORY: Final[str] = "promotion_receipts"

SOURCE_RECEIPT_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-language-source-receipt-v1"
)
APPROVAL_RECEIPT_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-language-operator-approval-receipt-v1"
)
PROMOTION_RECEIPT_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-language-promotion-receipt-v1"
)
APPROVAL_TOKEN: Final[str] = "APPROVE_LANGUAGE_MEMORY"
PROMOTION_TOKEN: Final[str] = "PROMOTE_LANGUAGE_MEMORY"
MAX_RECEIPT_BYTES: Final[int] = 64 * 1024

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CONTENT_REF = re.compile(r"^[a-z][a-z0-9_]*:[0-9a-f]{64}$")
_SOURCE_RECEIPT_REF = re.compile(r"^source_receipt:[0-9a-f]{64}$")
_APPROVAL_RECEIPT_REF = re.compile(
    r"^operator_approval_receipt:[0-9a-f]{64}$"
)
_PROMOTION_RECEIPT_REF = re.compile(
    r"^rmc_language_promotion_receipt:[0-9a-f]{64}$"
)
_SEMANTIC_CONTRACT_REF = re.compile(
    r"^meaning_semantic_contract:[0-9a-f]{64}$"
)
_INPUT_EVENT_REF = re.compile(r"^input_event:[0-9a-f]{64}$")
_SOURCE_FORM_REF = re.compile(r"^source_form:[0-9a-f]{64}$")
_CHARTER_REF = re.compile(r"^governed_semantic_charter:[0-9a-f]{64}$")
_CHARTER_ENTRY_REF = re.compile(
    r"^semantic_charter_replay_fixture:[0-9a-f]{64}$"
)
_REGISTRY_REF = re.compile(r"^forge_preview_registry:[0-9a-f]{64}$")
_COMPILER_RESULT_REF = re.compile(
    r"^meaning_compiler_preview_result:[0-9a-f]{64}$"
)
_MEANING_CANDIDATE_REF = re.compile(r"^meaning_candidate:[0-9a-f]{64}$")
_ECHO_RECEIPT_REF = re.compile(r"^meaning_echo:[0-9a-f]{64}$")
_PROPOSAL_REF = re.compile(r"^language_memory_proposal:[0-9a-f]{64}$")
_RECORD_DRAFT_REF = re.compile(
    r"^rmc_exact_language_record_draft:[0-9a-f]{64}$"
)
_EXACT_RECORD_REF = re.compile(r"^rmc_exact_language_record:[0-9a-f]{64}$")
_STABLE_TARGET_REF = re.compile(
    r"^memory/rmc_language_core_v1/stable/([0-9a-f]{64})\.json$"
)


class LanguageReceiptError(ValueError):
    """Typed fail-closed receipt rejection without raw evidence disclosure."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


def _record_dict(value: object) -> dict[str, object]:
    return canonicalize(asdict(value))


def _canonical_json(value: object) -> str:
    return json.dumps(
        canonicalize(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _strict_ref(value: object, field: str, pattern: re.Pattern[str] = _CONTENT_REF) -> str:
    if type(value) is not str or not pattern.fullmatch(value):
        raise LanguageReceiptError(f"{field}_invalid")
    return value


def _strict_refs(value: object, field: str) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        raise LanguageReceiptError(f"{field}_must_be_reference_sequence")
    refs = tuple(value)
    if any(type(item) is not str or not _CONTENT_REF.fullmatch(item) for item in refs):
        raise LanguageReceiptError(f"{field}_contains_invalid_reference")
    if refs != tuple(sorted(refs)):
        raise LanguageReceiptError(f"{field}_must_be_canonical_order")
    if len(refs) != len(set(refs)):
        raise LanguageReceiptError(f"{field}_contains_duplicate_reference")
    return refs


def _strict_relation_refs(value: object) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        raise LanguageReceiptError("relation_refs_must_be_reference_sequence")
    refs = tuple(value)
    if any(
        type(item) is not str
        or not item
        or not (
            item.startswith("predicate:")
            or item.startswith("role:")
        )
        for item in refs
    ):
        raise LanguageReceiptError("relation_refs_contains_invalid_reference")
    if refs != tuple(sorted(refs)):
        raise LanguageReceiptError("relation_refs_must_be_canonical_order")
    if len(refs) != len(set(refs)):
        raise LanguageReceiptError("relation_refs_contains_duplicate_reference")
    return refs


def governance_root(repository_root: Path | str | None = None) -> Path:
    repository = (
        Path(repository_root)
        if repository_root is not None
        else Path(__file__).resolve().parents[1]
    )
    return repository.resolve() / "memory" / LANGUAGE_GOVERNANCE_DIRECTORY


@dataclass(frozen=True, slots=True)
class LanguageSourceReceipt:
    source_receipt_id: str
    schema_version: str
    charter_ref: str
    charter_entry_ref: str
    registry_ref: str
    compiler_result_ref: str
    selected_meaning_ref: str
    semantic_contract_ref: str
    source_sha256: str
    input_event_ref: str
    source_form_refs: tuple[str, ...]
    concept_refs: tuple[str, ...]
    sense_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    role_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    echo_receipt_ref: str
    echo_status: str
    source_replay_verified: bool
    exact_identity_binding_verified: bool
    raw_text_stored: bool
    token_stream_stored: bool
    embedding_stored: bool
    vector_stored: bool
    writes_memory: bool
    grants_runtime_authority: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class LanguageOperatorApprovalReceipt:
    approval_receipt_id: str
    schema_version: str
    proposal_ref: str
    charter_ref: str
    charter_entry_ref: str
    registry_ref: str
    source_receipt_ref: str
    semantic_contract_ref: str
    record_draft_ref: str
    store_class: str
    decision: str
    approval_token_contract: str
    confirmation_phrase_sha256: str
    explicit_operator_confirmation_observed: bool
    local_same_origin_request_verified: bool
    operator_identity_authenticated: bool
    scope_limited_to_one_record: bool
    automatic_approval: bool
    raw_text_stored: bool
    tokenization_performed: bool
    embedding_used: bool
    vector_used: bool
    similarity_scoring_used: bool
    writes_memory: bool
    grants_general_runtime_authority: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class LanguagePromotionReceipt:
    promotion_receipt_id: str
    schema_version: str
    proposal_ref: str
    charter_ref: str
    charter_entry_ref: str
    registry_ref: str
    source_receipt_ref: str
    approval_receipt_ref: str
    record_ref: str
    store_class: str
    target_ref: str
    promotion_token_contract: str
    confirmation_phrase_sha256: str
    explicit_operator_confirmation_observed: bool
    source_and_approval_receipts_verified: bool
    exact_record_recomputed_under_lock: bool
    target_absent_before_commit: bool
    record_presence_is_commit_point: bool
    automatic_promotion: bool
    writes_one_exact_record: bool
    writes_other_memory: bool
    calls_model: bool
    embedding_used: bool
    vector_used: bool
    similarity_scoring_used: bool
    grants_general_runtime_authority: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


def approval_confirmation_phrase(proposal_ref: str, record_draft_ref: str) -> str:
    _strict_ref(proposal_ref, "proposal_ref", _PROPOSAL_REF)
    _strict_ref(record_draft_ref, "record_draft_ref", _RECORD_DRAFT_REF)
    return f"APPROVE {record_draft_ref} FROM {proposal_ref}"


def promotion_confirmation_phrase(record_ref: str, approval_receipt_ref: str) -> str:
    _strict_ref(record_ref, "record_ref", _EXACT_RECORD_REF)
    _strict_ref(
        approval_receipt_ref,
        "approval_receipt_ref",
        _APPROVAL_RECEIPT_REF,
    )
    return f"PROMOTE {record_ref} WITH {approval_receipt_ref}"


def _phrase_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_language_source_receipt(
    *,
    charter_ref: object,
    charter_entry_ref: object,
    registry_ref: object,
    compiler_result_ref: object,
    selected_meaning_ref: object,
    semantic_contract_ref: object,
    source_sha256: object,
    input_event_ref: object,
    source_form_refs: object,
    concept_refs: object,
    sense_refs: object,
    relation_refs: object,
    role_refs: object,
    ancestry_refs: object,
    echo_receipt_ref: object,
) -> LanguageSourceReceipt:
    semantic_contract = _strict_ref(
        semantic_contract_ref,
        "semantic_contract_ref",
        _SEMANTIC_CONTRACT_REF,
    )
    input_event = _strict_ref(
        input_event_ref,
        "input_event_ref",
        _INPUT_EVENT_REF,
    )
    source_forms = _strict_refs(source_form_refs, "source_form_refs")
    if not source_forms or any(
        _SOURCE_FORM_REF.fullmatch(reference) is None
        for reference in source_forms
    ):
        raise LanguageReceiptError("source_form_refs_invalid")
    concepts = _strict_refs(concept_refs, "concept_refs")
    senses = _strict_refs(sense_refs, "sense_refs")
    relations = _strict_relation_refs(relation_refs)
    roles = _strict_refs(role_refs, "role_refs")
    ancestry = _strict_refs(ancestry_refs, "ancestry_refs")
    expected_ancestry = tuple(sorted((input_event, *source_forms)))
    if ancestry != expected_ancestry:
        raise LanguageReceiptError("source_ancestry_binding_mismatch")
    if not concepts or not senses or not relations or not roles:
        raise LanguageReceiptError("source_exact_identity_sets_required")
    body = {
        "schema_version": SOURCE_RECEIPT_SCHEMA_VERSION,
        "charter_ref": _strict_ref(
            charter_ref, "charter_ref", _CHARTER_REF
        ),
        "charter_entry_ref": _strict_ref(
            charter_entry_ref, "charter_entry_ref", _CHARTER_ENTRY_REF
        ),
        "registry_ref": _strict_ref(
            registry_ref, "registry_ref", _REGISTRY_REF
        ),
        "compiler_result_ref": _strict_ref(
            compiler_result_ref,
            "compiler_result_ref",
            _COMPILER_RESULT_REF,
        ),
        "selected_meaning_ref": _strict_ref(
            selected_meaning_ref,
            "selected_meaning_ref",
            _MEANING_CANDIDATE_REF,
        ),
        "semantic_contract_ref": semantic_contract,
        "source_sha256": source_sha256,
        "input_event_ref": input_event,
        "source_form_refs": source_forms,
        "concept_refs": concepts,
        "sense_refs": senses,
        "relation_refs": relations,
        "role_refs": roles,
        "ancestry_refs": ancestry,
        "echo_receipt_ref": _strict_ref(
            echo_receipt_ref,
            "echo_receipt_ref",
            _ECHO_RECEIPT_REF,
        ),
        "echo_status": "PASS",
        "source_replay_verified": True,
        "exact_identity_binding_verified": True,
        "raw_text_stored": False,
        "token_stream_stored": False,
        "embedding_stored": False,
        "vector_stored": False,
        "writes_memory": False,
        "grants_runtime_authority": False,
    }
    if type(source_sha256) is not str or not _SHA256.fullmatch(source_sha256):
        raise LanguageReceiptError("source_sha256_invalid")
    return LanguageSourceReceipt(
        source_receipt_id=stable_record_id("source_receipt", body),
        **body,
    )


_RECORD_DRAFT_FIELDS: Final[tuple[str, ...]] = (
    "schema_version",
    "store_class",
    "lifecycle_state",
    "registry_ref",
    "semantic_contract_ref",
    "semantic_signature_ref",
    "speech_act",
    "purport",
    "negated",
    "frame_key",
    "grammar_rule_ref",
    "predicate_ref",
    "concept_refs",
    "sense_refs",
    "relation_refs",
    "role_refs",
    "ancestry_refs",
    "source_receipt_ref",
    "immutable",
    "read_only",
    "exact_identity_resonance_only",
    "raw_text_present",
    "token_stream_present",
    "embedding_present",
    "vector_present",
)


def language_record_draft_ref(record: object) -> str:
    method = getattr(record, "to_dict", None)
    value = method() if callable(method) else record
    if not isinstance(value, Mapping):
        raise LanguageReceiptError("record_draft_not_mapping")
    missing = tuple(field for field in _RECORD_DRAFT_FIELDS if field not in value)
    if missing:
        raise LanguageReceiptError("record_draft_fields_missing")
    body = {field: value[field] for field in _RECORD_DRAFT_FIELDS}
    return stable_record_id("rmc_exact_language_record_draft", body)


def build_language_operator_approval_receipt(
    *,
    proposal_ref: object,
    charter_ref: object,
    charter_entry_ref: object,
    registry_ref: object,
    source_receipt_ref: object,
    semantic_contract_ref: object,
    record_draft_ref: object,
    store_class: object,
) -> LanguageOperatorApprovalReceipt:
    proposal = _strict_ref(proposal_ref, "proposal_ref", _PROPOSAL_REF)
    draft = _strict_ref(
        record_draft_ref,
        "record_draft_ref",
        _RECORD_DRAFT_REF,
    )
    phrase = approval_confirmation_phrase(proposal, draft)
    if store_class != "stable":
        raise LanguageReceiptError("approval_store_class_not_admitted")
    body = {
        "schema_version": APPROVAL_RECEIPT_SCHEMA_VERSION,
        "proposal_ref": proposal,
        "charter_ref": _strict_ref(
            charter_ref, "charter_ref", _CHARTER_REF
        ),
        "charter_entry_ref": _strict_ref(
            charter_entry_ref, "charter_entry_ref", _CHARTER_ENTRY_REF
        ),
        "registry_ref": _strict_ref(
            registry_ref, "registry_ref", _REGISTRY_REF
        ),
        "source_receipt_ref": _strict_ref(
            source_receipt_ref, "source_receipt_ref", _SOURCE_RECEIPT_REF
        ),
        "semantic_contract_ref": _strict_ref(
            semantic_contract_ref,
            "semantic_contract_ref",
            _SEMANTIC_CONTRACT_REF,
        ),
        "record_draft_ref": draft,
        "store_class": store_class,
        "decision": "APPROVED_FOR_ONE_EXACT_RECORD_PROMOTION",
        "approval_token_contract": APPROVAL_TOKEN,
        "confirmation_phrase_sha256": _phrase_sha256(phrase),
        "explicit_operator_confirmation_observed": True,
        "local_same_origin_request_verified": True,
        "operator_identity_authenticated": False,
        "scope_limited_to_one_record": True,
        "automatic_approval": False,
        "raw_text_stored": False,
        "tokenization_performed": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
        "writes_memory": False,
        "grants_general_runtime_authority": False,
    }
    return LanguageOperatorApprovalReceipt(
        approval_receipt_id=stable_record_id("operator_approval_receipt", body),
        **body,
    )


def build_language_promotion_receipt(
    *,
    proposal_ref: object,
    charter_ref: object,
    charter_entry_ref: object,
    registry_ref: object,
    source_receipt_ref: object,
    approval_receipt_ref: object,
    record_ref: object,
    target_ref: object,
) -> LanguagePromotionReceipt:
    record = _strict_ref(record_ref, "record_ref", _EXACT_RECORD_REF)
    approval = _strict_ref(
        approval_receipt_ref, "approval_receipt_ref", _APPROVAL_RECEIPT_REF
    )
    phrase = promotion_confirmation_phrase(record, approval)
    target_match = (
        _STABLE_TARGET_REF.fullmatch(target_ref)
        if type(target_ref) is str
        else None
    )
    if (
        target_match is None
        or target_match.group(1) != record.split(":", 1)[1]
    ):
        raise LanguageReceiptError("promotion_target_ref_not_admitted")
    body = {
        "schema_version": PROMOTION_RECEIPT_SCHEMA_VERSION,
        "proposal_ref": _strict_ref(
            proposal_ref, "proposal_ref", _PROPOSAL_REF
        ),
        "charter_ref": _strict_ref(
            charter_ref, "charter_ref", _CHARTER_REF
        ),
        "charter_entry_ref": _strict_ref(
            charter_entry_ref, "charter_entry_ref", _CHARTER_ENTRY_REF
        ),
        "registry_ref": _strict_ref(
            registry_ref, "registry_ref", _REGISTRY_REF
        ),
        "source_receipt_ref": _strict_ref(
            source_receipt_ref, "source_receipt_ref", _SOURCE_RECEIPT_REF
        ),
        "approval_receipt_ref": approval,
        "record_ref": record,
        "store_class": "stable",
        "target_ref": target_ref,
        "promotion_token_contract": PROMOTION_TOKEN,
        "confirmation_phrase_sha256": _phrase_sha256(phrase),
        "explicit_operator_confirmation_observed": True,
        "source_and_approval_receipts_verified": True,
        "exact_record_recomputed_under_lock": True,
        "target_absent_before_commit": True,
        "record_presence_is_commit_point": True,
        "automatic_promotion": False,
        "writes_one_exact_record": True,
        "writes_other_memory": False,
        "calls_model": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
        "grants_general_runtime_authority": False,
    }
    return LanguagePromotionReceipt(
        promotion_receipt_id=stable_record_id("rmc_language_promotion_receipt", body),
        **body,
    )


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise LanguageReceiptError("receipt_json_duplicate_key")
        value[key] = item
    return value


def _secure_read_json(path: Path) -> dict[str, object]:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise LanguageReceiptError("receipt_file_open_rejected") from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise LanguageReceiptError("receipt_path_not_regular_file")
        if metadata.st_nlink != 1:
            raise LanguageReceiptError("receipt_file_hardlink_rejected")
        if metadata.st_uid != os.geteuid():
            raise LanguageReceiptError("receipt_file_owner_not_forge_user")
        if metadata.st_mode & 0o022:
            raise LanguageReceiptError("receipt_file_is_group_or_world_writable")
        if metadata.st_size <= 0 or metadata.st_size > MAX_RECEIPT_BYTES:
            raise LanguageReceiptError("receipt_file_size_not_admitted")
        chunks: list[bytes] = []
        remaining = MAX_RECEIPT_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(8192, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) != metadata.st_size or len(payload) > MAX_RECEIPT_BYTES:
            raise LanguageReceiptError("receipt_file_changed_during_read")
    finally:
        os.close(descriptor)
    try:
        decoded = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except LanguageReceiptError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LanguageReceiptError("receipt_json_invalid") from error
    if type(decoded) is not dict:
        raise LanguageReceiptError("receipt_must_be_json_object")
    return decoded


def _validate_directory(path: Path) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise LanguageReceiptError("receipt_directory_unreadable") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise LanguageReceiptError("receipt_directory_not_trusted")
    if metadata.st_uid != os.geteuid():
        raise LanguageReceiptError("receipt_directory_owner_not_forge_user")
    if metadata.st_mode & 0o022:
        raise LanguageReceiptError("receipt_directory_is_group_or_world_writable")


def _load_receipt(
    repository_root: Path | str,
    directory_name: str,
    reference: str,
) -> dict[str, object]:
    root = governance_root(repository_root)
    directory = root / directory_name
    _validate_directory(root.parent)
    _validate_directory(root)
    _validate_directory(directory)
    digest = reference.split(":", 1)[1]
    return _secure_read_json(directory / f"{digest}.json")


def _coerce_source_receipt(value: dict[str, object]) -> LanguageSourceReceipt:
    fields = set(LanguageSourceReceipt.__dataclass_fields__)
    if set(value) != fields:
        raise LanguageReceiptError("source_receipt_fields_not_exact")
    try:
        receipt = build_language_source_receipt(
            charter_ref=value.get("charter_ref"),
            charter_entry_ref=value.get("charter_entry_ref"),
            registry_ref=value.get("registry_ref"),
            compiler_result_ref=value.get("compiler_result_ref"),
            selected_meaning_ref=value.get("selected_meaning_ref"),
            semantic_contract_ref=value.get("semantic_contract_ref"),
            source_sha256=value.get("source_sha256"),
            input_event_ref=value.get("input_event_ref"),
            source_form_refs=value.get("source_form_refs"),
            concept_refs=value.get("concept_refs"),
            sense_refs=value.get("sense_refs"),
            relation_refs=value.get("relation_refs"),
            role_refs=value.get("role_refs"),
            ancestry_refs=value.get("ancestry_refs"),
            echo_receipt_ref=value.get("echo_receipt_ref"),
        )
    except (TypeError, LanguageReceiptError) as error:
        raise LanguageReceiptError("source_receipt_type_invalid") from error
    if _canonical_json(receipt.to_dict()) != _canonical_json(value):
        raise LanguageReceiptError("source_receipt_content_mismatch")
    return receipt


def _coerce_approval_receipt(
    value: dict[str, object],
) -> LanguageOperatorApprovalReceipt:
    fields = set(LanguageOperatorApprovalReceipt.__dataclass_fields__)
    if set(value) != fields:
        raise LanguageReceiptError("approval_receipt_fields_not_exact")
    try:
        receipt = build_language_operator_approval_receipt(
            proposal_ref=value.get("proposal_ref"),
            charter_ref=value.get("charter_ref"),
            charter_entry_ref=value.get("charter_entry_ref"),
            registry_ref=value.get("registry_ref"),
            source_receipt_ref=value.get("source_receipt_ref"),
            semantic_contract_ref=value.get("semantic_contract_ref"),
            record_draft_ref=value.get("record_draft_ref"),
            store_class=value.get("store_class"),
        )
    except (TypeError, LanguageReceiptError) as error:
        raise LanguageReceiptError("approval_receipt_type_invalid") from error
    if _canonical_json(receipt.to_dict()) != _canonical_json(value):
        raise LanguageReceiptError("approval_receipt_content_mismatch")
    return receipt


def _coerce_promotion_receipt(
    value: dict[str, object],
) -> LanguagePromotionReceipt:
    fields = set(LanguagePromotionReceipt.__dataclass_fields__)
    if set(value) != fields:
        raise LanguageReceiptError("promotion_receipt_fields_not_exact")
    try:
        receipt = build_language_promotion_receipt(
            proposal_ref=value.get("proposal_ref"),
            charter_ref=value.get("charter_ref"),
            charter_entry_ref=value.get("charter_entry_ref"),
            registry_ref=value.get("registry_ref"),
            source_receipt_ref=value.get("source_receipt_ref"),
            approval_receipt_ref=value.get("approval_receipt_ref"),
            record_ref=value.get("record_ref"),
            target_ref=value.get("target_ref"),
        )
    except (TypeError, LanguageReceiptError) as error:
        raise LanguageReceiptError("promotion_receipt_type_invalid") from error
    if _canonical_json(receipt.to_dict()) != _canonical_json(value):
        raise LanguageReceiptError("promotion_receipt_content_mismatch")
    return receipt


def _verify_installed_charter_binding(source: LanguageSourceReceipt) -> None:
    """Bind a source receipt to one exact fixture in the installed charter."""

    try:
        from aiweb_language_core_bootstrap.governed_semantic_charter import (
            PROPOSED_SEMANTIC_CHARTER,
            assert_valid_semantic_charter,
        )
        from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (
            forge_seed_registry,
        )
        from aiweb_language_core_bootstrap.meaning_compiler_preview import (
            compile_meaning_preview,
        )
        from aiweb_language_core_bootstrap.meaning_compiler_preview.semantic_contract import (
            build_semantic_contract_binding,
        )

        charter = assert_valid_semantic_charter(PROPOSED_SEMANTIC_CHARTER)
        fixtures = tuple(
            item
            for item in charter.replay_fixtures
            if item.fixture_id == source.charter_entry_ref
        )
        if len(fixtures) != 1:
            raise LanguageReceiptError("source_receipt_fixture_not_installed")
        fixture = fixtures[0]
        constructions = tuple(
            item
            for item in charter.constructions
            if item.construction_id == fixture.construction_ref
        )
        if len(constructions) != 1:
            raise LanguageReceiptError(
                "source_receipt_fixture_construction_not_installed"
            )
        construction = constructions[0]
        semantic_contract = build_semantic_contract_binding(
            semantic_signature_ref=fixture.expected_semantic_signature,
            speech_act=construction.speech_act,
            purport=construction.purport,
            negated=fixture.expected_negated,
            frame_key=construction.frame_key,
            grammar_rule_ref=construction.grammar_rule_id,
            predicate_ref=fixture.expected_predicate_ref,
        )
        registry = forge_seed_registry()
        role_id_by_key = {item.role_key: item.role_id for item in registry.roles}
        expected_role_refs = tuple(
            sorted(role_id_by_key[item] for item in fixture.expected_role_keys)
        )
        replay = compile_meaning_preview(fixture.exact_source_text)
        selected = replay.selected_meaning
        if (
            selected is None
            or selected.meaning_candidate_id
            != fixture.expected_meaning_candidate_ref
        ):
            raise LanguageReceiptError(
                "source_receipt_fixture_replay_not_selected"
            )
        replay_ancestry = tuple(selected.ancestry_refs)
        replay_source_forms = tuple(
            item
            for item in replay_ancestry
            if item.startswith("source_form:")
        )
    except LanguageReceiptError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise LanguageReceiptError(
            "installed_semantic_charter_binding_invalid"
        ) from error

    expected_pairs = (
        (source.charter_ref, charter.charter_id),
        (source.registry_ref, charter.registry_ref),
        (source.source_sha256, fixture.exact_source_sha256),
        (source.selected_meaning_ref, fixture.expected_meaning_candidate_ref),
        (source.semantic_contract_ref, semantic_contract.semantic_contract_id),
        (source.concept_refs, fixture.expected_concept_refs),
        (source.sense_refs, fixture.expected_sense_refs),
        (source.relation_refs, fixture.expected_relation_refs),
        (source.role_refs, expected_role_refs),
        (source.input_event_ref, replay.source_custody.input_event_id),
        (source.source_form_refs, replay_source_forms),
        (source.ancestry_refs, replay_ancestry),
        (source.echo_receipt_ref, replay.echo.echo_id),
    )
    if any(left != right for left, right in expected_pairs):
        raise LanguageReceiptError(
            "source_receipt_installed_charter_binding_mismatch"
        )


def verify_language_record_receipts(
    repository_root: Path | str,
    record: object,
) -> tuple[LanguageSourceReceipt, LanguageOperatorApprovalReceipt]:
    """Verify source and approval evidence without asserting promotion."""

    method = getattr(record, "to_dict", None)
    value = method() if callable(method) else record
    if not isinstance(value, Mapping):
        raise LanguageReceiptError("language_record_not_mapping")
    source_ref = _strict_ref(
        value.get("source_receipt_ref"), "source_receipt_ref", _SOURCE_RECEIPT_REF
    )
    approval_ref = _strict_ref(
        value.get("approval_receipt_ref"),
        "approval_receipt_ref",
        _APPROVAL_RECEIPT_REF,
    )
    source = _coerce_source_receipt(
        _load_receipt(repository_root, SOURCE_RECEIPT_DIRECTORY, source_ref)
    )
    approval = _coerce_approval_receipt(
        _load_receipt(repository_root, APPROVAL_RECEIPT_DIRECTORY, approval_ref)
    )
    if source.source_receipt_id != source_ref:
        raise LanguageReceiptError("source_receipt_reference_mismatch")
    if approval.approval_receipt_id != approval_ref:
        raise LanguageReceiptError("approval_receipt_reference_mismatch")
    _verify_installed_charter_binding(source)

    exact_pairs = (
        (source.registry_ref, value.get("registry_ref")),
        (source.semantic_contract_ref, value.get("semantic_contract_ref")),
        (source.concept_refs, tuple(value.get("concept_refs", ()))),
        (source.sense_refs, tuple(value.get("sense_refs", ()))),
        (source.relation_refs, tuple(value.get("relation_refs", ()))),
        (source.role_refs, tuple(value.get("role_refs", ()))),
        (source.ancestry_refs, tuple(value.get("ancestry_refs", ()))),
        (approval.registry_ref, value.get("registry_ref")),
        (approval.charter_ref, source.charter_ref),
        (approval.charter_entry_ref, source.charter_entry_ref),
        (approval.source_receipt_ref, source_ref),
        (approval.semantic_contract_ref, value.get("semantic_contract_ref")),
        (approval.store_class, value.get("store_class")),
        (approval.record_draft_ref, language_record_draft_ref(value)),
    )
    if any(left != right for left, right in exact_pairs):
        raise LanguageReceiptError("language_receipt_record_binding_mismatch")
    required_source_flags = (
        source.echo_status == "PASS",
        source.source_replay_verified is True,
        source.exact_identity_binding_verified is True,
        source.raw_text_stored is False,
        source.token_stream_stored is False,
        source.embedding_stored is False,
        source.vector_stored is False,
        source.writes_memory is False,
        source.grants_runtime_authority is False,
    )
    required_approval_flags = (
        approval.decision == "APPROVED_FOR_ONE_EXACT_RECORD_PROMOTION",
        approval.approval_token_contract == APPROVAL_TOKEN,
        approval.explicit_operator_confirmation_observed is True,
        approval.local_same_origin_request_verified is True,
        approval.operator_identity_authenticated is False,
        approval.scope_limited_to_one_record is True,
        approval.automatic_approval is False,
        approval.raw_text_stored is False,
        approval.tokenization_performed is False,
        approval.embedding_used is False,
        approval.vector_used is False,
        approval.similarity_scoring_used is False,
        approval.writes_memory is False,
        approval.grants_general_runtime_authority is False,
    )
    if not all(required_source_flags):
        raise LanguageReceiptError("source_receipt_authority_contract_violated")
    if not all(required_approval_flags):
        raise LanguageReceiptError("approval_receipt_authority_contract_violated")
    return source, approval


def verify_language_record_promotion_receipt(
    repository_root: Path | str,
    record: object,
) -> LanguagePromotionReceipt:
    """Require the distinct second-stage receipt before runtime admission.

    Approval evidence remains independently verifiable before this point via
    ``verify_language_record_receipts``.  Because adding a promotion reference
    to the record would create a content-addressing cycle, the exact expected
    promotion receipt identity and filename are derived from the already
    approved record and its two persisted receipts.
    """

    method = getattr(record, "to_dict", None)
    value = method() if callable(method) else record
    if not isinstance(value, Mapping):
        raise LanguageReceiptError("language_record_not_mapping")
    if value.get("store_class") != "stable":
        raise LanguageReceiptError("promotion_receipt_store_class_not_admitted")
    record_ref = _strict_ref(
        value.get("record_id"),
        "record_ref",
        _EXACT_RECORD_REF,
    )
    source, approval = verify_language_record_receipts(
        repository_root,
        record,
    )
    target_ref = (
        "memory/rmc_language_core_v1/stable/"
        + record_ref.split(":", 1)[1]
        + ".json"
    )
    expected = build_language_promotion_receipt(
        proposal_ref=approval.proposal_ref,
        charter_ref=source.charter_ref,
        charter_entry_ref=source.charter_entry_ref,
        registry_ref=source.registry_ref,
        source_receipt_ref=source.source_receipt_id,
        approval_receipt_ref=approval.approval_receipt_id,
        record_ref=record_ref,
        target_ref=target_ref,
    )
    expected_ref = _strict_ref(
        expected.promotion_receipt_id,
        "promotion_receipt_ref",
        _PROMOTION_RECEIPT_REF,
    )
    persisted = _coerce_promotion_receipt(
        _load_receipt(
            repository_root,
            PROMOTION_RECEIPT_DIRECTORY,
            expected_ref,
        )
    )
    if persisted.promotion_receipt_id != expected_ref:
        raise LanguageReceiptError("promotion_receipt_reference_mismatch")
    if _canonical_json(persisted.to_dict()) != _canonical_json(expected.to_dict()):
        raise LanguageReceiptError("promotion_receipt_record_binding_mismatch")

    required_flags = (
        persisted.store_class == "stable",
        persisted.promotion_token_contract == PROMOTION_TOKEN,
        persisted.explicit_operator_confirmation_observed is True,
        persisted.source_and_approval_receipts_verified is True,
        persisted.exact_record_recomputed_under_lock is True,
        persisted.target_absent_before_commit is True,
        persisted.record_presence_is_commit_point is True,
        persisted.automatic_promotion is False,
        persisted.writes_one_exact_record is True,
        persisted.writes_other_memory is False,
        persisted.calls_model is False,
        persisted.embedding_used is False,
        persisted.vector_used is False,
        persisted.similarity_scoring_used is False,
        persisted.grants_general_runtime_authority is False,
    )
    if not all(required_flags):
        raise LanguageReceiptError(
            "promotion_receipt_authority_contract_violated"
        )
    return persisted


__all__ = (
    "APPROVAL_RECEIPT_DIRECTORY",
    "APPROVAL_TOKEN",
    "LanguageOperatorApprovalReceipt",
    "LanguagePromotionReceipt",
    "LanguageReceiptError",
    "LanguageSourceReceipt",
    "PROMOTION_RECEIPT_DIRECTORY",
    "PROMOTION_TOKEN",
    "SOURCE_RECEIPT_DIRECTORY",
    "approval_confirmation_phrase",
    "build_language_operator_approval_receipt",
    "build_language_promotion_receipt",
    "build_language_source_receipt",
    "governance_root",
    "language_record_draft_ref",
    "promotion_confirmation_phrase",
    "verify_language_record_promotion_receipt",
    "verify_language_record_receipts",
)
