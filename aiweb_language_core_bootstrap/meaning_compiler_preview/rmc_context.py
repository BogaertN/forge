"""Read-only structured RMC context for the meaning-compiler preview.

Resonance here means exact shared identifiers only.  The module never reads a
memory directory, raw text, vector store, embedding, or legacy RMC payload.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from ..schema import stable_record_id
from .semantic_contract import semantic_contract_for_candidate
from .schema import (
    FrameCandidate,
    MeaningCandidate,
    RmcCandidateResonance,
    RmcContextEvaluation,
    RmcContextRecord,
    RmcContextSnapshot,
)


_ELIGIBLE_LIFECYCLE_STATES = frozenset(
    {"accepted", "eligible_structured_language_record"}
)


def _require_prefixes(
    references: tuple[str, ...],
    field: str,
    prefixes: tuple[str, ...],
) -> None:
    if any(not reference.startswith(prefixes) for reference in references):
        raise ValueError(f"{field} contains an unsupported reference type")


def _refs(value: object, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (tuple, list)):
        raise TypeError(f"{field} must be a tuple or list of text references")
    items = tuple(value)
    if any(type(item) is not str or not item.strip() for item in items):
        raise ValueError(f"{field} contains an invalid reference")
    if len(items) != len(set(items)):
        raise ValueError(f"{field} contains duplicate references")
    return tuple(sorted(items))


def build_rmc_context_record(
    *,
    semantic_contract_refs: object = (),
    concept_refs: object = (),
    relation_refs: object = (),
    ancestry_refs: object = (),
    phase_refs: object = (),
    correction_refs: object = (),
    echo_receipt_refs: object = (),
    lifecycle_state: object = "eligible_structured_language_record",
) -> RmcContextRecord:
    """Build one immutable context record containing identifiers, never text."""

    if (
        type(lifecycle_state) is not str
        or lifecycle_state not in _ELIGIBLE_LIFECYCLE_STATES
    ):
        raise ValueError("lifecycle_state is not eligible for language context")
    semantic_contracts = _refs(
        semantic_contract_refs,
        "semantic_contract_refs",
    )
    concepts = _refs(concept_refs, "concept_refs")
    relations = _refs(relation_refs, "relation_refs")
    ancestry = _refs(ancestry_refs, "ancestry_refs")
    phases = _refs(phase_refs, "phase_refs")
    corrections = _refs(correction_refs, "correction_refs")
    echo_receipts = _refs(echo_receipt_refs, "echo_receipt_refs")
    _require_prefixes(
        semantic_contracts,
        "semantic_contract_refs",
        ("meaning_semantic_contract:",),
    )
    _require_prefixes(
        concepts,
        "concept_refs",
        ("forge_preview_concept:", "concept:"),
    )
    _require_prefixes(
        relations,
        "relation_refs",
        ("predicate:", "role:", "relation:"),
    )
    _require_prefixes(
        ancestry,
        "ancestry_refs",
        ("input_event:", "source_form:", "ancestry:"),
    )
    if not (semantic_contracts or concepts or relations or ancestry):
        raise ValueError("RMC context record has no eligible semantic references")
    if phases or corrections or echo_receipts:
        raise ValueError(
            "phase, correction, and Echo control references are not admitted in v0"
        )
    body = {
        "semantic_contract_refs": semantic_contracts,
        "concept_refs": concepts,
        "relation_refs": relations,
        "ancestry_refs": ancestry,
        "phase_refs": phases,
        "correction_refs": corrections,
        "echo_receipt_refs": echo_receipts,
        "lifecycle_state": lifecycle_state,
        "exact_reference_resonance_only": True,
        "raw_text_present": False,
    }
    return RmcContextRecord(
        record_id=stable_record_id("rmc_context_record", body),
        **body,
    )


def _coerce_record(value: object) -> RmcContextRecord:
    if type(value) is RmcContextRecord:
        rebuilt = build_rmc_context_record(
            semantic_contract_refs=value.semantic_contract_refs,
            concept_refs=value.concept_refs,
            relation_refs=value.relation_refs,
            ancestry_refs=value.ancestry_refs,
            phase_refs=value.phase_refs,
            correction_refs=value.correction_refs,
            echo_receipt_refs=value.echo_receipt_refs,
            lifecycle_state=value.lifecycle_state,
        )
        if value != rebuilt:
            raise ValueError("RMC context record does not match its content identity")
        return rebuilt
    if not isinstance(value, Mapping):
        raise TypeError("each RMC snapshot record must be structured")
    permitted = {
        "record_id",
        "semantic_contract_refs",
        "concept_refs",
        "relation_refs",
        "ancestry_refs",
        "phase_refs",
        "correction_refs",
        "echo_receipt_refs",
        "lifecycle_state",
        "exact_reference_resonance_only",
        "raw_text_present",
    }
    if set(value) - permitted:
        raise ValueError("RMC context record contains unsupported fields")
    if value.get("raw_text_present", False) is not False:
        raise ValueError("raw text is not eligible for this RMC preview")
    if value.get("exact_reference_resonance_only", True) is not True:
        raise ValueError("RMC context must use exact reference resonance")
    built = build_rmc_context_record(
        semantic_contract_refs=value.get("semantic_contract_refs", ()),
        concept_refs=value.get("concept_refs", ()),
        relation_refs=value.get("relation_refs", ()),
        ancestry_refs=value.get("ancestry_refs", ()),
        phase_refs=value.get("phase_refs", ()),
        correction_refs=value.get("correction_refs", ()),
        echo_receipt_refs=value.get("echo_receipt_refs", ()),
        lifecycle_state=value.get(
            "lifecycle_state", "eligible_structured_language_record"
        ),
    )
    supplied_id = value.get("record_id")
    if supplied_id is not None and supplied_id != built.record_id:
        raise ValueError("RMC context record_id does not match its content")
    return built


def build_rmc_context_snapshot(
    records: object = (),
) -> RmcContextSnapshot:
    """Build an immutable caller-supplied snapshot, or connected-empty default."""

    if not isinstance(records, (tuple, list)):
        raise TypeError("records must be a tuple or list")
    coerced = tuple(sorted((_coerce_record(item) for item in records), key=lambda item: item.record_id))
    if len(coerced) != len({record.record_id for record in coerced}):
        raise ValueError("RMC snapshot contains duplicate records")
    semantic_keys = tuple(
        (
            record.semantic_contract_refs,
            record.concept_refs,
            record.relation_refs,
            record.ancestry_refs,
        )
        for record in coerced
    )
    if len(semantic_keys) != len(set(semantic_keys)):
        raise ValueError("RMC snapshot contains duplicate semantic support")
    connected_empty = not coerced
    body = {
        "records": coerced,
        "connection_status": (
            "CONNECTED_EMPTY" if connected_empty else "CONNECTED_STRUCTURED"
        ),
        "reason_code": (
            "no_eligible_structured_language_records"
            if connected_empty
            else "eligible_structured_language_records_supplied"
        ),
        "record_count": len(coerced),
        "read_only": True,
        "caller_supplied": bool(coerced),
        "exact_reference_resonance_only": True,
        "filesystem_access_performed": False,
        "raw_word_overlap_used": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
    }
    return RmcContextSnapshot(
        snapshot_id=stable_record_id("rmc_context_snapshot", body),
        **body,
    )


def coerce_rmc_context_snapshot(value: object) -> RmcContextSnapshot:
    if value is None:
        return build_rmc_context_snapshot()
    if type(value) is RmcContextSnapshot:
        rebuilt = build_rmc_context_snapshot(value.records)
        if value != rebuilt:
            raise ValueError("RMC snapshot does not match its record identities")
        return rebuilt
    if not isinstance(value, Mapping):
        raise TypeError("rmc_snapshot must be a structured object")
    permitted = {
        "snapshot_id",
        "records",
        "connection_status",
        "reason_code",
        "record_count",
        "read_only",
        "caller_supplied",
        "exact_reference_resonance_only",
        "filesystem_access_performed",
        "raw_word_overlap_used",
        "embedding_used",
        "vector_used",
        "similarity_scoring_used",
    }
    if set(value) - permitted:
        raise ValueError("rmc_snapshot contains unsupported fields")
    built = build_rmc_context_snapshot(value.get("records", ()))
    supplied_id = value.get("snapshot_id")
    if supplied_id is not None and supplied_id != built.snapshot_id:
        raise ValueError("rmc_snapshot snapshot_id does not match its records")
    for false_field in (
        "filesystem_access_performed",
        "raw_word_overlap_used",
        "embedding_used",
        "vector_used",
        "similarity_scoring_used",
    ):
        if value.get(false_field, False) is not False:
            raise ValueError("rmc_snapshot requests a forbidden mechanism")
    if value.get("read_only", True) is not True:
        raise ValueError("rmc_snapshot must be read-only")
    for field in (
        "connection_status",
        "reason_code",
        "record_count",
        "caller_supplied",
        "exact_reference_resonance_only",
    ):
        if field in value:
            expected = getattr(built, field)
            supplied = value[field]
            if type(supplied) is not type(expected) or supplied != expected:
                raise ValueError(f"rmc_snapshot {field} contradicts its records")
    return built


def evaluate_rmc_context(
    snapshot: RmcContextSnapshot,
    meaning_candidates: Iterable[MeaningCandidate],
    frame_candidates: Iterable[FrameCandidate],
) -> RmcContextEvaluation:
    resonances: list[RmcCandidateResonance] = []
    frames = tuple(frame_candidates)
    for meaning in meaning_candidates:
        semantic_contract = semantic_contract_for_candidate(meaning, frames)
        semantic_contract_refs = {semantic_contract.semantic_contract_id}
        concept_refs = {role.concept_ref for role in meaning.roles if role.concept_ref}
        relation_refs = set(meaning.relation_refs)
        ancestry_refs = set(meaning.ancestry_refs)
        for record in snapshot.records:
            exact_semantic_contracts = tuple(
                sorted(
                    semantic_contract_refs.intersection(
                        record.semantic_contract_refs
                    )
                )
            )
            exact_concepts = tuple(sorted(concept_refs.intersection(record.concept_refs)))
            exact_relations = tuple(sorted(relation_refs.intersection(record.relation_refs)))
            exact_ancestry = tuple(sorted(ancestry_refs.intersection(record.ancestry_refs)))
            count = (
                len(exact_semantic_contracts)
                + len(exact_concepts)
                + len(exact_relations)
                + len(exact_ancestry)
            )
            if count == 0:
                continue
            body = {
                "meaning_candidate_ref": meaning.meaning_candidate_id,
                "record_ref": record.record_id,
                "exact_semantic_contract_refs": exact_semantic_contracts,
                "exact_concept_refs": exact_concepts,
                "exact_relation_refs": exact_relations,
                "exact_ancestry_refs": exact_ancestry,
                "resonance_count": count,
                "used_for_selection": False,
            }
            resonances.append(
                RmcCandidateResonance(
                    resonance_id=stable_record_id("rmc_exact_resonance", body),
                    **body,
                )
            )
    resonances.sort(key=lambda item: item.resonance_id)
    body = {
        "snapshot": snapshot,
        "resonances": tuple(resonances),
        "exact_reference_resonance_only": True,
        "context_used_for_selection": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
    }
    return RmcContextEvaluation(
        evaluation_id=stable_record_id("rmc_context_evaluation", body),
        **body,
    )


__all__ = (
    "build_rmc_context_record",
    "build_rmc_context_snapshot",
    "coerce_rmc_context_snapshot",
    "evaluate_rmc_context",
)
