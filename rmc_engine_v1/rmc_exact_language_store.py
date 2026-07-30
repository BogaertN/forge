"""Trusted read-only RMC storage for Forge symbolic language records.

This module is the only filesystem-facing part of the v0 meaning preview.  It
loads content-addressed JSON records from one dedicated repository-local root:

    memory/rmc_language_core_v1/{stable,live}

Records contain typed registry and ancestry identifiers only and are admitted
only when their source, approval, and promotion receipts all verify.  Raw
language, tokens, embeddings, vectors, approximate matching, and runtime
writes are not admitted.  One invalid file rejects the complete store so
partially trusted memory can never influence meaning selection.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import stat
from typing import Final

from aiweb_language_core_bootstrap.schema import canonicalize, stable_record_id
from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (
    forge_seed_registry,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.rmc_context import (
    build_rmc_context_record,
    build_rmc_context_snapshot,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.semantic_contract import (
    build_semantic_contract_binding,
    semantic_contract_for_candidate,
)
from aiweb_language_core_bootstrap.meaning_compiler_preview.schema import (
    FrameCandidate,
    MeaningCandidate,
    RmcContextSnapshot,
)
from rmc_engine_v1.rmc_language_receipts import (
    LanguageReceiptError,
    verify_language_record_promotion_receipt,
)


EXACT_RMC_RECORD_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-rmc-exact-language-record-v2"
)
EXACT_RMC_PROVIDER_VERSION: Final[str] = "aiweb-forge-rmc-exact-provider-v2"
LANGUAGE_MEMORY_DIRECTORY: Final[str] = "rmc_language_core_v1"
STORE_CLASSES: Final[tuple[str, ...]] = ("stable", "live")
MAX_RECORD_BYTES: Final[int] = 64 * 1024
MAX_RECORD_FILES: Final[int] = 1024
MAX_STORE_BYTES: Final[int] = 16 * 1024 * 1024

_ANCESTRY_ID = re.compile(r"^(?:input_event|source_form):[0-9a-f]{64}$")
_SOURCE_RECEIPT_ID = re.compile(r"^source_receipt:[0-9a-f]{64}$")
_APPROVAL_RECEIPT_ID = re.compile(
    r"^operator_approval_receipt:[0-9a-f]{64}$"
)


class ExactRmcStoreError(ValueError):
    """Typed fail-closed storage rejection with no raw payload disclosure."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


def _record_dict(value: object) -> dict[str, object]:
    return canonicalize(asdict(value))


@dataclass(frozen=True, slots=True)
class ExactLanguageMemoryRecord:
    """One immutable, approved symbolic-language memory assertion."""

    record_id: str
    schema_version: str
    store_class: str
    lifecycle_state: str
    registry_ref: str
    semantic_contract_ref: str
    semantic_signature_ref: str
    speech_act: str
    purport: str
    negated: bool
    frame_key: str
    grammar_rule_ref: str
    predicate_ref: str
    concept_refs: tuple[str, ...]
    sense_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    role_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    source_receipt_ref: str
    approval_receipt_ref: str
    provenance_chain_ref: str
    immutable: bool
    read_only: bool
    exact_identity_resonance_only: bool
    raw_text_present: bool
    token_stream_present: bool
    embedding_present: bool
    vector_present: bool

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("record_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "rmc_exact_language_record",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ExactIdentityResonance:
    """Auditable intersections of exact IDs; never a similarity score."""

    resonance_id: str
    meaning_candidate_ref: str
    memory_record_ref: str
    exact_semantic_contract_refs: tuple[str, ...]
    exact_concept_refs: tuple[str, ...]
    exact_sense_refs: tuple[str, ...]
    exact_relation_refs: tuple[str, ...]
    exact_role_refs: tuple[str, ...]
    exact_ancestry_refs: tuple[str, ...]
    exact_identity_count: int
    approximate_match_used: bool
    used_for_selection: bool

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("resonance_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "rmc_exact_identity_resonance",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class TrustedRmcProviderResult:
    """Frozen provider result and compiler-compatible snapshot projection."""

    provider_result_id: str
    provider_version: str
    root_ref: str
    load_status: str
    reason_codes: tuple[str, ...]
    stable_record_count: int
    live_record_count: int
    rejected_record_count: int
    records: tuple[ExactLanguageMemoryRecord, ...]
    snapshot: RmcContextSnapshot
    trusted: bool
    read_only: bool
    filesystem_read_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    raw_word_overlap_used: bool
    tokenization_used: bool
    embedding_used: bool
    vector_used: bool
    similarity_scoring_used: bool

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)

    def public_receipt(self) -> dict[str, object]:
        """Return operational facts without disclosing stored ancestry sets."""

        return {
            "provider_result_id": self.provider_result_id,
            "provider_version": self.provider_version,
            "root_ref": self.root_ref,
            "load_status": self.load_status,
            "reason_codes": self.reason_codes,
            "stable_record_count": self.stable_record_count,
            "live_record_count": self.live_record_count,
            "rejected_record_count": self.rejected_record_count,
            "snapshot_id": self.snapshot.snapshot_id,
            "trusted": self.trusted,
            "read_only": self.read_only,
            "filesystem_read_performed": self.filesystem_read_performed,
            "memory_read_performed": self.memory_read_performed,
            "memory_write_performed": self.memory_write_performed,
            "raw_word_overlap_used": self.raw_word_overlap_used,
            "tokenization_used": self.tokenization_used,
            "embedding_used": self.embedding_used,
            "vector_used": self.vector_used,
            "similarity_scoring_used": self.similarity_scoring_used,
        }


def language_memory_root(repository_root: Path | str | None = None) -> Path:
    """Resolve the sole eligible root without consulting environment state."""

    repository = (
        Path(repository_root)
        if repository_root is not None
        else Path(__file__).resolve().parents[1]
    )
    return repository.resolve() / "memory" / LANGUAGE_MEMORY_DIRECTORY


def _strict_refs(value: object, field: str) -> tuple[str, ...]:
    if type(value) not in (list, tuple):
        raise ExactRmcStoreError(f"{field}_must_be_reference_sequence")
    if any(type(item) is not str or not item for item in value):
        raise ExactRmcStoreError(f"{field}_contains_invalid_id")
    refs = tuple(value)
    if refs != tuple(sorted(refs)):
        raise ExactRmcStoreError(f"{field}_must_be_canonical_order")
    if len(refs) != len(set(refs)):
        raise ExactRmcStoreError(f"{field}_contains_duplicate_id")
    return refs


def _registry_indexes() -> dict[str, object]:
    registry = forge_seed_registry()
    concepts = {item.concept_id: item for item in registry.concepts}
    senses = {item.sense_id: item for item in registry.senses}
    predicates = {item.predicate_key: item for item in registry.predicates}
    roles_by_id = {item.role_id: item for item in registry.roles}
    roles_by_key = {item.role_key: item for item in registry.roles}
    return {
        "registry": registry,
        "concepts": concepts,
        "senses": senses,
        "predicates": predicates,
        "roles_by_id": roles_by_id,
        "roles_by_key": roles_by_key,
    }


def _validate_relation_ref(
    reference: str,
    *,
    concepts: Mapping[str, object],
    predicates: Mapping[str, object],
    roles_by_key: Mapping[str, object],
) -> tuple[str, str]:
    if reference.startswith("predicate:"):
        predicate_key = reference.removeprefix("predicate:")
        if predicate_key not in predicates:
            raise ExactRmcStoreError("relation_ref_predicate_not_in_registry")
        return ("predicate", predicate_key)
    if reference.startswith("role:"):
        parts = reference.split(":", 2)
        if len(parts) != 3 or not parts[1] or not parts[2]:
            raise ExactRmcStoreError("relation_ref_role_shape_invalid")
        role_key, concept_ref = parts[1], parts[2]
        if role_key not in roles_by_key:
            raise ExactRmcStoreError("relation_ref_role_not_in_registry")
        if concept_ref not in concepts:
            raise ExactRmcStoreError("relation_ref_concept_not_in_registry")
        return ("role", role_key)
    raise ExactRmcStoreError("relation_ref_type_not_admitted")


def build_exact_language_memory_record(
    *,
    store_class: object,
    lifecycle_state: object,
    semantic_contract_ref: object,
    semantic_signature_ref: object,
    speech_act: object,
    purport: object,
    negated: object,
    frame_key: object,
    grammar_rule_ref: object,
    predicate_ref: object,
    concept_refs: object,
    sense_refs: object,
    relation_refs: object,
    role_refs: object,
    ancestry_refs: object,
    source_receipt_ref: object,
    approval_receipt_ref: object,
    registry_ref: object | None = None,
) -> ExactLanguageMemoryRecord:
    """Validate and content-address one record without writing it anywhere."""

    indexes = _registry_indexes()
    registry = indexes["registry"]
    if type(store_class) is not str or store_class not in STORE_CLASSES:
        raise ExactRmcStoreError("store_class_not_admitted")
    expected_lifecycle = {
        "stable": "accepted_stable",
        "live": "eligible_live",
    }[store_class]
    if type(lifecycle_state) is not str or lifecycle_state != expected_lifecycle:
        raise ExactRmcStoreError("lifecycle_state_not_eligible_for_store")
    expected_registry_ref = registry.registry_id
    supplied_registry_ref = (
        expected_registry_ref if registry_ref is None else registry_ref
    )
    if (
        type(supplied_registry_ref) is not str
        or supplied_registry_ref != expected_registry_ref
    ):
        raise ExactRmcStoreError("registry_ref_not_current_forge_registry")

    try:
        semantic_contract = build_semantic_contract_binding(
            semantic_signature_ref=semantic_signature_ref,
            speech_act=speech_act,
            purport=purport,
            negated=negated,
            frame_key=frame_key,
            grammar_rule_ref=grammar_rule_ref,
            predicate_ref=predicate_ref,
        )
    except (TypeError, ValueError) as error:
        raise ExactRmcStoreError("semantic_contract_fields_invalid") from error
    if (
        type(semantic_contract_ref) is not str
        or semantic_contract_ref != semantic_contract.semantic_contract_id
    ):
        raise ExactRmcStoreError("semantic_contract_ref_content_mismatch")

    concepts = _strict_refs(concept_refs, "concept_refs")
    senses = _strict_refs(sense_refs, "sense_refs")
    relations = _strict_refs(relation_refs, "relation_refs")
    roles = _strict_refs(role_refs, "role_refs")
    ancestry = _strict_refs(ancestry_refs, "ancestry_refs")
    if not concepts or not senses or not relations or not roles or not ancestry:
        raise ExactRmcStoreError("complete_typed_identity_sets_required")

    known_concepts = indexes["concepts"]
    known_senses = indexes["senses"]
    known_roles_by_id = indexes["roles_by_id"]
    known_roles_by_key = indexes["roles_by_key"]
    known_predicates = indexes["predicates"]
    contract_predicates = tuple(
        item
        for item in known_predicates.values()
        if item.predicate_id == semantic_contract.predicate_ref
    )
    if len(contract_predicates) != 1:
        raise ExactRmcStoreError("semantic_contract_predicate_not_in_registry")
    contract_predicate_relation = (
        f"predicate:{contract_predicates[0].predicate_key}"
    )
    if any(reference not in known_concepts for reference in concepts):
        raise ExactRmcStoreError("concept_ref_not_in_registry")
    if any(reference not in known_senses for reference in senses):
        raise ExactRmcStoreError("sense_ref_not_in_registry")
    if any(reference not in known_roles_by_id for reference in roles):
        raise ExactRmcStoreError("role_ref_not_in_registry")
    if any(not _ANCESTRY_ID.fullmatch(reference) for reference in ancestry):
        raise ExactRmcStoreError("ancestry_ref_shape_invalid")
    if not any(item.startswith("input_event:") for item in ancestry):
        raise ExactRmcStoreError("input_event_ancestry_required")
    if not any(item.startswith("source_form:") for item in ancestry):
        raise ExactRmcStoreError("source_form_ancestry_required")

    concept_set = set(concepts)
    for sense_ref in senses:
        sense = known_senses[sense_ref]
        if sense.concept_ref not in concept_set:
            raise ExactRmcStoreError("sense_ref_missing_its_concept_ref")

    used_role_keys: set[str] = set()
    for relation_ref in relations:
        kind, key = _validate_relation_ref(
            relation_ref,
            concepts=known_concepts,
            predicates=known_predicates,
            roles_by_key=known_roles_by_key,
        )
        if kind == "role":
            used_role_keys.add(key)
            relation_concept = relation_ref.split(":", 2)[2]
            if relation_concept not in concept_set:
                raise ExactRmcStoreError("role_relation_concept_missing_from_record")
    stored_role_keys = {known_roles_by_id[reference].role_key for reference in roles}
    if used_role_keys != stored_role_keys:
        raise ExactRmcStoreError("role_refs_do_not_match_role_relations")
    stored_predicate_relations = {
        reference for reference in relations if reference.startswith("predicate:")
    }
    if stored_predicate_relations != {contract_predicate_relation}:
        raise ExactRmcStoreError(
            "semantic_contract_predicate_relation_mismatch"
        )

    if (
        type(source_receipt_ref) is not str
        or not _SOURCE_RECEIPT_ID.fullmatch(source_receipt_ref)
    ):
        raise ExactRmcStoreError("source_receipt_ref_invalid")
    if (
        type(approval_receipt_ref) is not str
        or not _APPROVAL_RECEIPT_ID.fullmatch(approval_receipt_ref)
    ):
        raise ExactRmcStoreError("approval_receipt_ref_invalid")

    provenance_body = {
        "registry_ref": supplied_registry_ref,
        "ancestry_refs": ancestry,
        "source_receipt_ref": source_receipt_ref,
        "approval_receipt_ref": approval_receipt_ref,
    }
    provenance_chain_ref = stable_record_id(
        "rmc_exact_provenance_chain",
        provenance_body,
    )

    body = {
        "schema_version": EXACT_RMC_RECORD_SCHEMA_VERSION,
        "store_class": store_class,
        "lifecycle_state": lifecycle_state,
        "registry_ref": supplied_registry_ref,
        "semantic_contract_ref": semantic_contract.semantic_contract_id,
        "semantic_signature_ref": semantic_contract.semantic_signature_ref,
        "speech_act": semantic_contract.speech_act,
        "purport": semantic_contract.purport,
        "negated": semantic_contract.negated,
        "frame_key": semantic_contract.frame_key,
        "grammar_rule_ref": semantic_contract.grammar_rule_ref,
        "predicate_ref": semantic_contract.predicate_ref,
        "concept_refs": concepts,
        "sense_refs": senses,
        "relation_refs": relations,
        "role_refs": roles,
        "ancestry_refs": ancestry,
        "source_receipt_ref": source_receipt_ref,
        "approval_receipt_ref": approval_receipt_ref,
        "provenance_chain_ref": provenance_chain_ref,
        "immutable": True,
        "read_only": True,
        "exact_identity_resonance_only": True,
        "raw_text_present": False,
        "token_stream_present": False,
        "embedding_present": False,
        "vector_present": False,
    }
    return ExactLanguageMemoryRecord(
        record_id=stable_record_id("rmc_exact_language_record", body),
        **body,
    )


_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    field.name for field in ExactLanguageMemoryRecord.__dataclass_fields__.values()
)


def _coerce_record(value: object, expected_store_class: str) -> ExactLanguageMemoryRecord:
    if not isinstance(value, Mapping) or type(value) is not dict:
        raise ExactRmcStoreError("record_must_be_json_object")
    if set(value) != _RECORD_FIELDS:
        raise ExactRmcStoreError("record_fields_not_exact")
    if value.get("schema_version") != EXACT_RMC_RECORD_SCHEMA_VERSION:
        raise ExactRmcStoreError("record_schema_version_not_supported")
    strict_constants = {
        "immutable": True,
        "read_only": True,
        "exact_identity_resonance_only": True,
        "raw_text_present": False,
        "token_stream_present": False,
        "embedding_present": False,
        "vector_present": False,
    }
    for field, expected in strict_constants.items():
        supplied = value.get(field)
        if type(supplied) is not type(expected) or supplied is not expected:
            raise ExactRmcStoreError(f"record_{field}_contract_violated")
    if value.get("store_class") != expected_store_class:
        raise ExactRmcStoreError("record_store_class_directory_mismatch")
    for field in (
        "concept_refs",
        "sense_refs",
        "relation_refs",
        "role_refs",
        "ancestry_refs",
    ):
        if type(value.get(field)) is not list:
            raise ExactRmcStoreError(f"record_{field}_must_be_json_array")
    built = build_exact_language_memory_record(
        store_class=value.get("store_class"),
        lifecycle_state=value.get("lifecycle_state"),
        registry_ref=value.get("registry_ref"),
        semantic_contract_ref=value.get("semantic_contract_ref"),
        semantic_signature_ref=value.get("semantic_signature_ref"),
        speech_act=value.get("speech_act"),
        purport=value.get("purport"),
        negated=value.get("negated"),
        frame_key=value.get("frame_key"),
        grammar_rule_ref=value.get("grammar_rule_ref"),
        predicate_ref=value.get("predicate_ref"),
        concept_refs=value.get("concept_refs"),
        sense_refs=value.get("sense_refs"),
        relation_refs=value.get("relation_refs"),
        role_refs=value.get("role_refs"),
        ancestry_refs=value.get("ancestry_refs"),
        source_receipt_ref=value.get("source_receipt_ref"),
        approval_receipt_ref=value.get("approval_receipt_ref"),
    )
    supplied_id = value.get("record_id")
    if type(supplied_id) is not str or supplied_id != built.record_id:
        raise ExactRmcStoreError("record_id_content_identity_mismatch")
    if value.get("provenance_chain_ref") != built.provenance_chain_ref:
        raise ExactRmcStoreError("record_provenance_chain_identity_mismatch")
    return built


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ExactRmcStoreError("record_json_duplicate_key")
        result[key] = value
    return result


def _secure_read(path: Path) -> bytes:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ExactRmcStoreError("record_file_open_rejected") from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ExactRmcStoreError("record_path_not_regular_file")
        if metadata.st_nlink != 1:
            raise ExactRmcStoreError("record_file_hardlink_rejected")
        if metadata.st_uid != os.geteuid():
            raise ExactRmcStoreError("record_file_owner_not_forge_user")
        if metadata.st_mode & 0o022:
            raise ExactRmcStoreError("record_file_is_group_or_world_writable")
        if metadata.st_size <= 0 or metadata.st_size > MAX_RECORD_BYTES:
            raise ExactRmcStoreError("record_file_size_not_admitted")
        chunks: list[bytes] = []
        remaining = MAX_RECORD_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(8192, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) != metadata.st_size or len(payload) > MAX_RECORD_BYTES:
            raise ExactRmcStoreError("record_file_changed_during_read")
        return payload
    finally:
        os.close(descriptor)


def _validate_directory(path: Path, reason_prefix: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise ExactRmcStoreError(f"{reason_prefix}_directory_unreadable") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ExactRmcStoreError(f"{reason_prefix}_directory_not_trusted")
    if metadata.st_uid != os.geteuid():
        raise ExactRmcStoreError(f"{reason_prefix}_directory_owner_not_forge_user")
    if metadata.st_mode & 0o022:
        raise ExactRmcStoreError(
            f"{reason_prefix}_directory_is_group_or_world_writable"
        )


def _load_store_directory(path: Path, store_class: str) -> tuple[ExactLanguageMemoryRecord, ...]:
    if not os.path.lexists(path):
        return ()
    _validate_directory(path, store_class)
    try:
        entries = tuple(sorted(path.iterdir(), key=lambda item: item.name))
    except OSError as error:
        raise ExactRmcStoreError(f"{store_class}_directory_listing_failed") from error
    records: list[ExactLanguageMemoryRecord] = []
    for entry in entries:
        if entry.suffix != ".json" or entry.name.startswith("."):
            raise ExactRmcStoreError("unexpected_file_in_language_memory_store")
        payload = _secure_read(entry)
        try:
            decoded = payload.decode("utf-8", errors="strict")
            value = json.loads(decoded, object_pairs_hook=_reject_duplicate_json_keys)
        except ExactRmcStoreError:
            raise
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ExactRmcStoreError("record_json_invalid") from error
        record = _coerce_record(value, store_class)
        expected_filename = record.record_id.split(":", 1)[1] + ".json"
        if entry.name != expected_filename:
            raise ExactRmcStoreError("record_filename_identity_mismatch")
        records.append(record)
    return tuple(records)


def _project_snapshot(
    records: Iterable[ExactLanguageMemoryRecord],
) -> RmcContextSnapshot:
    projected = tuple(
        build_rmc_context_record(
            semantic_contract_refs=(record.semantic_contract_ref,),
            concept_refs=record.concept_refs,
            relation_refs=record.relation_refs,
            ancestry_refs=record.ancestry_refs,
            lifecycle_state="accepted",
        )
        for record in records
    )
    return build_rmc_context_snapshot(projected)


def _provider_result(
    *,
    root: Path,
    load_status: str,
    reason_codes: tuple[str, ...],
    stable_records: tuple[ExactLanguageMemoryRecord, ...] = (),
    live_records: tuple[ExactLanguageMemoryRecord, ...] = (),
    rejected_record_count: int = 0,
    trusted: bool,
    filesystem_read_performed: bool,
    memory_read_performed: bool,
) -> TrustedRmcProviderResult:
    records = tuple(sorted((*stable_records, *live_records), key=lambda item: item.record_id))
    try:
        snapshot = _project_snapshot(records) if trusted else build_rmc_context_snapshot()
    except (TypeError, ValueError):
        records = ()
        stable_records = ()
        live_records = ()
        snapshot = build_rmc_context_snapshot()
        load_status = "REJECTED"
        reason_codes = ("projected_snapshot_rejected",)
        rejected_record_count = max(1, rejected_record_count)
        trusted = False
    body = {
        "provider_version": EXACT_RMC_PROVIDER_VERSION,
        "root_ref": f"memory/{LANGUAGE_MEMORY_DIRECTORY}",
        "load_status": load_status,
        "reason_codes": reason_codes,
        "stable_record_count": len(stable_records),
        "live_record_count": len(live_records),
        "rejected_record_count": rejected_record_count,
        "record_refs": tuple(item.record_id for item in records),
        "snapshot_ref": snapshot.snapshot_id,
        "trusted": trusted,
        "read_only": True,
        "filesystem_read_performed": filesystem_read_performed,
        "memory_read_performed": memory_read_performed,
        "memory_write_performed": False,
        "raw_word_overlap_used": False,
        "tokenization_used": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
    }
    return TrustedRmcProviderResult(
        provider_result_id=stable_record_id("rmc_exact_provider_result", body),
        provider_version=EXACT_RMC_PROVIDER_VERSION,
        root_ref=f"memory/{LANGUAGE_MEMORY_DIRECTORY}",
        load_status=load_status,
        reason_codes=reason_codes,
        stable_record_count=len(stable_records),
        live_record_count=len(live_records),
        rejected_record_count=rejected_record_count,
        records=records,
        snapshot=snapshot,
        trusted=trusted,
        read_only=True,
        filesystem_read_performed=filesystem_read_performed,
        memory_read_performed=memory_read_performed,
        memory_write_performed=False,
        raw_word_overlap_used=False,
        tokenization_used=False,
        embedding_used=False,
        vector_used=False,
        similarity_scoring_used=False,
    )


def load_trusted_rmc_language_store(
    repository_root: Path | str | None = None,
) -> TrustedRmcProviderResult:
    """Load one complete immutable snapshot, rejecting any partial trust."""

    repository = (
        Path(repository_root).resolve()
        if repository_root is not None
        else Path(__file__).resolve().parents[1]
    )
    root = language_memory_root(repository)
    if not os.path.lexists(root):
        return _provider_result(
            root=root,
            load_status="TRUSTED_EMPTY",
            reason_codes=("dedicated_language_memory_root_not_present",),
            trusted=True,
            filesystem_read_performed=False,
            memory_read_performed=False,
        )
    try:
        _validate_directory(root.parent, "language_memory_parent")
        _validate_directory(root, "language_memory_root")
        allowed_names = set(STORE_CLASSES)
        root_entries = tuple(root.iterdir())
        if any(entry.name not in allowed_names for entry in root_entries):
            raise ExactRmcStoreError("unexpected_entry_in_language_memory_root")
        stable_records = _load_store_directory(root / "stable", "stable")
        live_records = _load_store_directory(root / "live", "live")
        records = (*stable_records, *live_records)
        if len(records) > MAX_RECORD_FILES:
            raise ExactRmcStoreError("language_memory_record_limit_exceeded")
        if len({item.record_id for item in records}) != len(records):
            raise ExactRmcStoreError("duplicate_language_memory_record_id")
        for record in records:
            verify_language_record_promotion_receipt(repository, record)
        total_bytes = 0
        for store_class in STORE_CLASSES:
            directory = root / store_class
            if os.path.lexists(directory):
                total_bytes += sum(item.stat().st_size for item in directory.iterdir())
        if total_bytes > MAX_STORE_BYTES:
            raise ExactRmcStoreError("language_memory_store_size_limit_exceeded")
        return _provider_result(
            root=root,
            load_status="TRUSTED_STRUCTURED" if records else "TRUSTED_EMPTY",
            reason_codes=(
                "eligible_exact_language_records_loaded"
                if records
                else "no_eligible_exact_language_records"
            ,),
            stable_records=stable_records,
            live_records=live_records,
            trusted=True,
            filesystem_read_performed=True,
            memory_read_performed=bool(records),
        )
    except (ExactRmcStoreError, LanguageReceiptError, OSError) as error:
        reason_code = (
            error.reason_code
            if isinstance(error, (ExactRmcStoreError, LanguageReceiptError))
            else "language_memory_filesystem_rejected"
        )
        return _provider_result(
            root=root,
            load_status="REJECTED",
            reason_codes=(reason_code,),
            rejected_record_count=1,
            trusted=False,
            filesystem_read_performed=True,
            memory_read_performed=False,
        )


def evaluate_exact_identity_resonance(
    records: Iterable[ExactLanguageMemoryRecord],
    meaning_candidates: Iterable[MeaningCandidate],
    frame_candidates: Iterable[FrameCandidate],
) -> tuple[ExactIdentityResonance, ...]:
    """Intersect typed identities exactly, without ranks or similarity scores."""

    registry = forge_seed_registry()
    role_id_by_key = {item.role_key: item.role_id for item in registry.roles}
    frames = tuple(frame_candidates)
    resonances: list[ExactIdentityResonance] = []
    for candidate in meaning_candidates:
        semantic_contract = semantic_contract_for_candidate(candidate, frames)
        candidate_semantic_contracts = {semantic_contract.semantic_contract_id}
        candidate_concepts = {item.concept_ref for item in candidate.roles}
        candidate_senses = {item.sense_ref for item in candidate.roles}
        candidate_relations = set(candidate.relation_refs)
        candidate_roles = {
            role_id_by_key[item.role_key]
            for item in candidate.roles
            if item.role_key in role_id_by_key
        }
        candidate_ancestry = set(candidate.ancestry_refs)
        for record in records:
            semantic_contracts = tuple(
                sorted(
                    candidate_semantic_contracts.intersection(
                        (record.semantic_contract_ref,)
                    )
                )
            )
            concepts = tuple(sorted(candidate_concepts.intersection(record.concept_refs)))
            senses = tuple(sorted(candidate_senses.intersection(record.sense_refs)))
            relations = tuple(sorted(candidate_relations.intersection(record.relation_refs)))
            roles = tuple(sorted(candidate_roles.intersection(record.role_refs)))
            ancestry = tuple(sorted(candidate_ancestry.intersection(record.ancestry_refs)))
            count = (
                len(semantic_contracts)
                + len(concepts)
                + len(senses)
                + len(relations)
                + len(roles)
                + len(ancestry)
            )
            if not count:
                continue
            body = {
                "meaning_candidate_ref": candidate.meaning_candidate_id,
                "memory_record_ref": record.record_id,
                "exact_semantic_contract_refs": semantic_contracts,
                "exact_concept_refs": concepts,
                "exact_sense_refs": senses,
                "exact_relation_refs": relations,
                "exact_role_refs": roles,
                "exact_ancestry_refs": ancestry,
                "exact_identity_count": count,
                "approximate_match_used": False,
                "used_for_selection": False,
            }
            resonances.append(
                ExactIdentityResonance(
                    resonance_id=stable_record_id("rmc_exact_identity_resonance", body),
                    **body,
                )
            )
    return tuple(sorted(resonances, key=lambda item: item.resonance_id))


__all__ = (
    "EXACT_RMC_PROVIDER_VERSION",
    "EXACT_RMC_RECORD_SCHEMA_VERSION",
    "ExactIdentityResonance",
    "ExactLanguageMemoryRecord",
    "ExactRmcStoreError",
    "TrustedRmcProviderResult",
    "build_exact_language_memory_record",
    "evaluate_exact_identity_resonance",
    "language_memory_root",
    "load_trusted_rmc_language_store",
)
