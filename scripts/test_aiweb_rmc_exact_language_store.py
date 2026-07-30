#!/usr/bin/env python3
"""Focused tests for the trusted exact-ID RMC language memory provider."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch


class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str, detail: object = "") -> None:
        self.checks += 1
        if condition is not True:
            message = label + (
                (": " + repr(detail)[:1000]) if detail not in (None, "") else ""
            )
            self.failures.append(message)
            print("FAIL - " + message)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _bundle_from_result(
    result: object,
    *,
    label: str,
    build_record: object,
    build_source_receipt: object,
    build_approval_receipt: object,
    build_promotion_receipt: object,
    draft_ref: object,
    registry: object,
) -> tuple[object, object, object, object]:
    candidate = result.meaning_candidates[0]
    role_id_by_key = {item.role_key: item.role_id for item in registry.roles}
    from aiweb_language_core_bootstrap.meaning_compiler_preview import (
        semantic_contract_for_candidate,
    )
    from aiweb_language_core_bootstrap.governed_semantic_charter import (
        PROPOSED_SEMANTIC_CHARTER,
    )

    contract = semantic_contract_for_candidate(candidate, result.frame_candidates)
    concepts = sorted({item.concept_ref for item in candidate.roles})
    senses = sorted({item.sense_ref for item in candidate.roles})
    relations = sorted(candidate.relation_refs)
    roles = sorted({role_id_by_key[item.role_key] for item in candidate.roles})
    ancestry = sorted(candidate.ancestry_refs)
    input_event_ref = next(
        item for item in ancestry if item.startswith("input_event:")
    )
    source_form_refs = tuple(
        item for item in ancestry if item.startswith("source_form:")
    )
    fixture = next(
        item
        for item in PROPOSED_SEMANTIC_CHARTER.replay_fixtures
        if item.expected_meaning_candidate_ref == candidate.meaning_candidate_id
        and item.exact_source_sha256 == result.source_custody.source_sha256
    )
    charter_ref = PROPOSED_SEMANTIC_CHARTER.charter_id
    charter_entry_ref = fixture.fixture_id
    source_receipt = build_source_receipt(
        charter_ref=charter_ref,
        charter_entry_ref=charter_entry_ref,
        registry_ref=registry.registry_id,
        compiler_result_ref=result.result_id,
        selected_meaning_ref=candidate.meaning_candidate_id,
        semantic_contract_ref=contract.semantic_contract_id,
        source_sha256=result.source_custody.source_sha256,
        input_event_ref=input_event_ref,
        source_form_refs=source_form_refs,
        concept_refs=concepts,
        sense_refs=senses,
        relation_refs=relations,
        role_refs=roles,
        ancestry_refs=ancestry,
        echo_receipt_ref=result.echo.echo_id,
    )

    record_arguments = {
        "store_class": "stable",
        "lifecycle_state": "accepted_stable",
        "semantic_contract_ref": contract.semantic_contract_id,
        "semantic_signature_ref": contract.semantic_signature_ref,
        "speech_act": contract.speech_act,
        "purport": contract.purport,
        "negated": contract.negated,
        "frame_key": contract.frame_key,
        "grammar_rule_ref": contract.grammar_rule_ref,
        "predicate_ref": contract.predicate_ref,
        "concept_refs": concepts,
        "sense_refs": senses,
        "relation_refs": relations,
        "role_refs": roles,
        "ancestry_refs": ancestry,
        "source_receipt_ref": source_receipt.source_receipt_id,
    }
    provisional = build_record(
        **record_arguments,
        approval_receipt_ref=(
            "operator_approval_receipt:" + _digest(label + ":pending-approval")
        ),
    )
    record_draft_ref = draft_ref(provisional)
    approval_receipt = build_approval_receipt(
        proposal_ref="language_memory_proposal:" + _digest(label + ":proposal"),
        charter_ref=charter_ref,
        charter_entry_ref=charter_entry_ref,
        registry_ref=registry.registry_id,
        source_receipt_ref=source_receipt.source_receipt_id,
        semantic_contract_ref=contract.semantic_contract_id,
        record_draft_ref=record_draft_ref,
        store_class="stable",
    )
    record = build_record(
        **record_arguments,
        approval_receipt_ref=approval_receipt.approval_receipt_id,
    )
    if draft_ref(record) != record_draft_ref:
        raise AssertionError("approval changed exact record draft identity")
    promotion_receipt = build_promotion_receipt(
        proposal_ref=approval_receipt.proposal_ref,
        charter_ref=charter_ref,
        charter_entry_ref=charter_entry_ref,
        registry_ref=registry.registry_id,
        source_receipt_ref=source_receipt.source_receipt_id,
        approval_receipt_ref=approval_receipt.approval_receipt_id,
        record_ref=record.record_id,
        target_ref=(
            "memory/rmc_language_core_v1/stable/"
            + record.record_id.split(":", 1)[1]
            + ".json"
        ),
    )
    return record, source_receipt, approval_receipt, promotion_receipt


def _write_record(root: Path, record: object) -> Path:
    directory = root / "memory" / "rmc_language_core_v1" / record.store_class
    directory.mkdir(parents=True, exist_ok=True)
    directory.parent.chmod(0o755)
    directory.chmod(0o755)
    path = directory / (record.record_id.split(":", 1)[1] + ".json")
    path.write_text(
        json.dumps(record.to_dict(), sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    path.chmod(0o644)
    return path


def _write_receipts(
    root: Path,
    source_receipt: object,
    approval_receipt: object,
) -> tuple[Path, Path]:
    governance = root / "memory" / "rmc_language_core_governance_v1"
    source_directory = governance / "source_receipts"
    approval_directory = governance / "approval_receipts"
    promotion_directory = governance / "promotion_receipts"
    source_directory.mkdir(parents=True, exist_ok=True)
    approval_directory.mkdir(parents=True, exist_ok=True)
    promotion_directory.mkdir(parents=True, exist_ok=True)
    for directory in (
        governance.parent,
        governance,
        source_directory,
        approval_directory,
        promotion_directory,
    ):
        directory.chmod(0o755)
    source_path = source_directory / (
        source_receipt.source_receipt_id.split(":", 1)[1] + ".json"
    )
    approval_path = approval_directory / (
        approval_receipt.approval_receipt_id.split(":", 1)[1] + ".json"
    )
    source_path.write_text(
        json.dumps(source_receipt.to_dict(), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    approval_path.write_text(
        json.dumps(approval_receipt.to_dict(), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    source_path.chmod(0o644)
    approval_path.chmod(0o644)
    return source_path, approval_path


def _write_promotion_receipt(root: Path, promotion_receipt: object) -> Path:
    directory = (
        root
        / "memory"
        / "rmc_language_core_governance_v1"
        / "promotion_receipts"
    )
    directory.mkdir(parents=True, exist_ok=True)
    directory.chmod(0o755)
    path = directory / (
        promotion_receipt.promotion_receipt_id.split(":", 1)[1] + ".json"
    )
    path.write_text(
        json.dumps(promotion_receipt.to_dict(), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    path.chmod(0o644)
    return path


def _rewrite_json(path: Path, updates: dict[str, object]) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(updates)
    path.write_text(
        json.dumps(data, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _record_arguments(record: object) -> dict[str, object]:
    return {
        field: getattr(record, field)
        for field in (
            "store_class",
            "lifecycle_state",
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
        )
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))
    ledger = Ledger()

    from aiweb_language_core_bootstrap.meaning_compiler_preview import (
        compile_meaning_preview,
    )
    from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (
        forge_seed_registry,
    )
    from rmc_engine_v1.rmc_exact_language_store import (
        EXACT_RMC_PROVIDER_VERSION,
        EXACT_RMC_RECORD_SCHEMA_VERSION,
        build_exact_language_memory_record,
        evaluate_exact_identity_resonance,
        language_memory_root,
        load_trusted_rmc_language_store,
    )
    from rmc_engine_v1.rmc_language_receipts import (
        LanguageReceiptError,
        build_language_operator_approval_receipt,
        build_language_promotion_receipt,
        build_language_source_receipt,
        language_record_draft_ref,
        verify_language_record_promotion_receipt,
        verify_language_record_receipts,
    )
    from rmc_engine_v1.meaning_compiler_preview import (
        build_language_core_preview_response,
    )
    import rmc_engine_v1.meaning_compiler_preview as preview_adapter
    import rmc_engine_v1.rmc_exact_language_store as store_module

    ledger.check(
        language_memory_root() == repository / "memory" / "rmc_language_core_v1",
        "production root is the dedicated repository memory root",
        language_memory_root(),
    )
    ledger.check(
        EXACT_RMC_RECORD_SCHEMA_VERSION.endswith("-v2"),
        "record schema is explicitly versioned",
    )
    ledger.check(
        EXACT_RMC_PROVIDER_VERSION.endswith("-v2"),
        "provider is explicitly versioned",
    )

    inspect_result = compile_meaning_preview("Please inspect the manifest.")
    report_result = compile_meaning_preview("Can Forge report status?")
    ledger.check(bool(inspect_result.meaning_candidates), "inspect meaning available")
    ledger.check(bool(report_result.meaning_candidates), "report meaning available")
    inspect_candidate = inspect_result.meaning_candidates[0]
    report_candidate = report_result.meaning_candidates[0]
    registry = forge_seed_registry()
    (
        stable_record,
        stable_source_receipt,
        stable_approval_receipt,
        stable_promotion_receipt,
    ) = (
        _bundle_from_result(
            inspect_result,
            label="inspect-stable",
            build_record=build_exact_language_memory_record,
            build_source_receipt=build_language_source_receipt,
            build_approval_receipt=build_language_operator_approval_receipt,
            build_promotion_receipt=build_language_promotion_receipt,
            draft_ref=language_record_draft_ref,
            registry=registry,
        )
    )
    (
        report_record,
        report_source_receipt,
        report_approval_receipt,
        report_promotion_receipt,
    ) = (
        _bundle_from_result(
            report_result,
            label="report-stable",
            build_record=build_exact_language_memory_record,
            build_source_receipt=build_language_source_receipt,
            build_approval_receipt=build_language_operator_approval_receipt,
            build_promotion_receipt=build_language_promotion_receipt,
            draft_ref=language_record_draft_ref,
            registry=registry,
        )
    )
    ledger.check(stable_record.immutable is True, "record immutable")
    ledger.check(stable_record.record_id == stable_record.expected_id(), "record content identity canonical")
    ledger.check(stable_record.read_only is True, "record read only")
    ledger.check(stable_record.raw_text_present is False, "record excludes raw text")
    ledger.check(stable_record.token_stream_present is False, "record excludes tokens")
    ledger.check(stable_record.embedding_present is False, "record excludes embeddings")
    ledger.check(stable_record.vector_present is False, "record excludes vectors")
    ledger.check(bool(stable_record.concept_refs), "record has exact concept IDs")
    ledger.check(bool(stable_record.sense_refs), "record has exact sense IDs")
    ledger.check(bool(stable_record.relation_refs), "record has exact relation IDs")
    ledger.check(bool(stable_record.role_refs), "record has exact role IDs")
    ledger.check(bool(stable_record.ancestry_refs), "record has exact ancestry IDs")
    ledger.check(
        stable_record.semantic_contract_ref.startswith(
            "meaning_semantic_contract:"
        ),
        "record has exact semantic contract ID",
    )
    ledger.check(
        stable_record.semantic_signature_ref
        == inspect_candidate.semantic_signature,
        "record binds the selected semantic signature",
    )
    ledger.check(
        stable_record.negated is inspect_candidate.negated,
        "record binds exact polarity",
    )
    ledger.check(
        stable_record.registry_ref == registry.registry_id,
        "record binds the current Forge registry identity",
    )
    ledger.check(
        stable_record.provenance_chain_ref.startswith("rmc_exact_provenance_chain:"),
        "record carries content-addressed provenance chain",
    )

    with tempfile.TemporaryDirectory(prefix="forge_rmc_exact_") as temporary:
        test_repository = Path(temporary)
        _write_record(test_repository, stable_record)
        _write_record(test_repository, report_record)
        _write_receipts(
            test_repository,
            stable_source_receipt,
            stable_approval_receipt,
        )
        _write_receipts(
            test_repository,
            report_source_receipt,
            report_approval_receipt,
        )
        _write_promotion_receipt(
            test_repository,
            stable_promotion_receipt,
        )
        _write_promotion_receipt(
            test_repository,
            report_promotion_receipt,
        )
        verified_source, verified_approval = verify_language_record_receipts(
            test_repository,
            stable_record,
        )
        ledger.check(
            verified_source == stable_source_receipt,
            "persisted source receipt verifies canonically",
        )
        ledger.check(
            verified_approval == stable_approval_receipt,
            "persisted approval receipt verifies canonically",
        )
        verified_promotion = verify_language_record_promotion_receipt(
            test_repository,
            stable_record,
        )
        ledger.check(
            verified_promotion == stable_promotion_receipt,
            "persisted promotion receipt verifies canonically",
        )
        loaded = load_trusted_rmc_language_store(test_repository)
        ledger.check(loaded.trusted is True, "structured provider remains trusted", loaded)
        ledger.check(
            loaded.load_status == "TRUSTED_STRUCTURED",
            "structured provider status",
            loaded,
        )
        ledger.check(loaded.stable_record_count == 2, "stable store included", loaded)
        ledger.check(loaded.live_record_count == 0, "unapproved live store absent", loaded)
        ledger.check(len(loaded.records) == 2, "approved records loaded", loaded)
        ledger.check(loaded.snapshot.record_count == 2, "compiler snapshot projected", loaded)
        ledger.check(
            loaded.snapshot.connection_status == "CONNECTED_STRUCTURED",
            "compiler snapshot connected",
            loaded.snapshot,
        )
        ledger.check(loaded.memory_read_performed is True, "memory read disclosed")
        ledger.check(loaded.memory_write_performed is False, "provider performs no write")
        ledger.check(loaded.raw_word_overlap_used is False, "no raw-word overlap")
        ledger.check(loaded.tokenization_used is False, "no tokenization")
        ledger.check(loaded.embedding_used is False, "no embedding")
        ledger.check(loaded.vector_used is False, "no vectors")
        ledger.check(loaded.similarity_scoring_used is False, "no similarity score")
        repeated = load_trusted_rmc_language_store(test_repository)
        ledger.check(loaded == repeated, "provider snapshot deterministic")

        resonances = evaluate_exact_identity_resonance(
            loaded.records,
            inspect_result.meaning_candidates,
            inspect_result.frame_candidates,
        )
        exact = next(
            item for item in resonances if item.memory_record_ref == stable_record.record_id
        )
        ledger.check(
            exact.exact_concept_refs == stable_record.concept_refs,
            "concept IDs intersect exactly",
        )
        ledger.check(
            exact.exact_sense_refs == stable_record.sense_refs,
            "sense IDs intersect exactly",
        )
        ledger.check(
            exact.exact_relation_refs == stable_record.relation_refs,
            "relation IDs intersect exactly",
        )
        ledger.check(
            exact.exact_role_refs == stable_record.role_refs,
            "role IDs intersect exactly",
        )
        ledger.check(
            exact.exact_ancestry_refs == stable_record.ancestry_refs,
            "ancestry IDs intersect exactly",
        )
        ledger.check(
            exact.exact_semantic_contract_refs
            == (stable_record.semantic_contract_ref,),
            "semantic contract intersects exactly",
        )
        ledger.check(
            exact.approximate_match_used is False,
            "exact resonance uses no approximation",
        )
        ledger.check(exact.resonance_id == exact.expected_id(), "exact resonance content identity canonical")
        ledger.check(exact.used_for_selection is False, "typed audit does not silently select")

        with patch.object(
            store_module,
            "load_trusted_rmc_language_store",
            return_value=loaded,
        ):
            preview_adapter = importlib.reload(preview_adapter)
            connected = preview_adapter.build_language_core_preview_response(
                {"source_text": "Please inspect the manifest."}
            )
        ledger.check(
            connected.get("status") == "PREVIEW_READY",
            "Ask Forge compiles through trusted structured RMC",
            connected,
        )
        provider_receipt = connected.get("trusted_rmc_provider", {})
        ledger.check(
            provider_receipt.get("load_status") == "TRUSTED_STRUCTURED",
            "Ask Forge discloses trusted structured provider",
            provider_receipt,
        )
        context = connected.get("rmc_context", {})
        snapshot = context.get("snapshot", {}) if isinstance(context, dict) else {}
        ledger.check(
            snapshot.get("record_count") == 2,
            "Ask Forge receives internal frozen snapshot",
            snapshot,
        )
        adapter_resonances = connected.get("rmc_exact_identity_resonances", [])
        ledger.check(
            bool(adapter_resonances),
            "Ask Forge exposes exact identity resonance audit",
            adapter_resonances,
        )
        ledger.check(
            any(item.get("exact_sense_refs") for item in adapter_resonances),
            "Ask Forge resonance includes exact sense IDs",
            adapter_resonances,
        )
        ledger.check(
            any(item.get("exact_role_refs") for item in adapter_resonances),
            "Ask Forge resonance includes exact role IDs",
            adapter_resonances,
        )
        preview_adapter = importlib.reload(preview_adapter)

    # A record is never trusted merely because its receipt references have the
    # right shape: both referenced receipt objects must exist on disk.
    with tempfile.TemporaryDirectory(prefix="forge_rmc_receipts_missing_") as temporary:
        test_repository = Path(temporary)
        _write_record(test_repository, stable_record)
        missing = load_trusted_rmc_language_store(test_repository)
        ledger.check(missing.trusted is False, "missing governance receipts reject record")
        ledger.check(missing.load_status == "REJECTED", "missing receipts typed rejection")
        ledger.check(missing.records == (), "missing receipts expose no records")

    # Approval is intentionally useful before promotion, but cannot make a
    # manually injected stable record runtime-readable without stage two.
    with tempfile.TemporaryDirectory(prefix="forge_rmc_approved_injection_") as temporary:
        test_repository = Path(temporary)
        _write_record(test_repository, stable_record)
        _write_receipts(
            test_repository,
            stable_source_receipt,
            stable_approval_receipt,
        )
        verified_source, verified_approval = verify_language_record_receipts(
            test_repository,
            stable_record,
        )
        ledger.check(
            verified_source == stable_source_receipt
            and verified_approval == stable_approval_receipt,
            "approval-stage verification remains valid before promotion",
        )
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(
            rejected.trusted is False,
            "approved-but-not-promoted record injection rejects",
            rejected,
        )
        ledger.check(
            rejected.reason_codes == ("receipt_file_open_rejected",),
            "missing promotion receipt has typed rejection",
            rejected,
        )
        ledger.check(rejected.records == (), "approved injection exposes no records")

    for label, updates in (
        (
            "tampered_promotion_receipt",
            {"target_absent_before_commit": False},
        ),
        (
            "numeric_promotion_boolean",
            {"explicit_operator_confirmation_observed": 1},
        ),
    ):
        with tempfile.TemporaryDirectory(prefix="forge_rmc_promotion_tamper_") as temporary:
            test_repository = Path(temporary)
            _write_record(test_repository, stable_record)
            _write_receipts(
                test_repository,
                stable_source_receipt,
                stable_approval_receipt,
            )
            promotion_path = _write_promotion_receipt(
                test_repository,
                stable_promotion_receipt,
            )
            _rewrite_json(promotion_path, updates)
            rejected = load_trusted_rmc_language_store(test_repository)
            ledger.check(rejected.trusted is False, label + " rejects store", rejected)
            ledger.check(rejected.records == (), label + " exposes no records")

    with tempfile.TemporaryDirectory(prefix="forge_rmc_promotion_mismatch_") as temporary:
        test_repository = Path(temporary)
        _write_record(test_repository, stable_record)
        _write_receipts(
            test_repository,
            stable_source_receipt,
            stable_approval_receipt,
        )
        expected_path = _write_promotion_receipt(
            test_repository,
            stable_promotion_receipt,
        )
        expected_path.write_text(
            json.dumps(report_promotion_receipt.to_dict(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "mismatched promotion receipt rejects store")
        ledger.check(rejected.records == (), "mismatched promotion exposes no records")

    for label, mutate in (
        ("symlinked_promotion_receipt", "symlink"),
        ("hardlinked_promotion_receipt", "hardlink"),
        ("world_writable_promotion_receipt", "writable"),
    ):
        with tempfile.TemporaryDirectory(prefix="forge_rmc_promotion_file_") as temporary:
            test_repository = Path(temporary)
            _write_record(test_repository, stable_record)
            _write_receipts(
                test_repository,
                stable_source_receipt,
                stable_approval_receipt,
            )
            promotion_path = _write_promotion_receipt(
                test_repository,
                stable_promotion_receipt,
            )
            outside = test_repository / "outside-promotion-receipt.json"
            if mutate == "symlink":
                promotion_path.rename(outside)
                promotion_path.symlink_to(outside)
            elif mutate == "hardlink":
                outside.hardlink_to(promotion_path)
            else:
                promotion_path.chmod(0o666)
            rejected = load_trusted_rmc_language_store(test_repository)
            ledger.check(rejected.trusted is False, label + " rejects store", rejected)
            ledger.check(rejected.records == (), label + " exposes no records")

    receipt_faults = {
        "missing_source_receipt": lambda source_path, approval_path: source_path.unlink(),
        "missing_approval_receipt": lambda source_path, approval_path: approval_path.unlink(),
        "world_writable_source_receipt": lambda source_path, approval_path: source_path.chmod(0o666),
        "world_writable_approval_directory": lambda source_path, approval_path: approval_path.parent.chmod(0o777),
        "world_writable_memory_parent": lambda source_path, approval_path: source_path.parents[2].chmod(0o777),
    }
    for label, mutate in receipt_faults.items():
        with tempfile.TemporaryDirectory(prefix="forge_rmc_receipt_fault_") as temporary:
            test_repository = Path(temporary)
            _write_record(test_repository, stable_record)
            source_path, approval_path = _write_receipts(
                test_repository,
                stable_source_receipt,
                stable_approval_receipt,
            )
            mutate(source_path, approval_path)
            rejected = load_trusted_rmc_language_store(test_repository)
            ledger.check(rejected.trusted is False, label + " rejects store", rejected)
            ledger.check(rejected.load_status == "REJECTED", label + " typed rejection")
            ledger.check(rejected.records == (), label + " exposes no records")

    for label, receipt_kind in (
        ("tampered_source_receipt", "source"),
        ("tampered_approval_receipt", "approval"),
    ):
        with tempfile.TemporaryDirectory(prefix="forge_rmc_receipt_tamper_") as temporary:
            test_repository = Path(temporary)
            _write_record(test_repository, stable_record)
            source_path, approval_path = _write_receipts(
                test_repository,
                stable_source_receipt,
                stable_approval_receipt,
            )
            path = source_path if receipt_kind == "source" else approval_path
            data = json.loads(path.read_text(encoding="utf-8"))
            data["semantic_contract_ref"] = (
                "meaning_semantic_contract:" + ("0" * 64)
            )
            path.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
            rejected = load_trusted_rmc_language_store(test_repository)
            ledger.check(rejected.trusted is False, label + " rejects store", rejected)
            ledger.check(rejected.records == (), label + " exposes no records")

    for label, receipt_kind, field in (
        ("numeric_source_boolean", "source", "source_replay_verified"),
        (
            "numeric_approval_boolean",
            "approval",
            "explicit_operator_confirmation_observed",
        ),
    ):
        with tempfile.TemporaryDirectory(prefix="forge_rmc_receipt_type_") as temporary:
            test_repository = Path(temporary)
            _write_record(test_repository, stable_record)
            source_path, approval_path = _write_receipts(
                test_repository,
                stable_source_receipt,
                stable_approval_receipt,
            )
            path = source_path if receipt_kind == "source" else approval_path
            data = json.loads(path.read_text(encoding="utf-8"))
            data[field] = 1
            path.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
            rejected = load_trusted_rmc_language_store(test_repository)
            ledger.check(rejected.trusted is False, label + " rejects store", rejected)
            ledger.check(rejected.records == (), label + " exposes no records")

    with tempfile.TemporaryDirectory(prefix="forge_rmc_receipt_fifo_") as temporary:
        test_repository = Path(temporary)
        _write_record(test_repository, stable_record)
        source_path, _ = _write_receipts(
            test_repository,
            stable_source_receipt,
            stable_approval_receipt,
        )
        source_path.unlink()
        os.mkfifo(source_path, mode=0o644)
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "receipt FIFO rejects without blocking")
        ledger.check(rejected.records == (), "receipt FIFO exposes no records")

    for label, link_kind in (
        ("symlinked_source_receipt", "symlink"),
        ("hardlinked_source_receipt", "hardlink"),
    ):
        with tempfile.TemporaryDirectory(prefix="forge_rmc_receipt_link_") as temporary:
            test_repository = Path(temporary)
            _write_record(test_repository, stable_record)
            source_path, _ = _write_receipts(
                test_repository,
                stable_source_receipt,
                stable_approval_receipt,
            )
            outside = test_repository / "outside-source-receipt.json"
            if link_kind == "symlink":
                source_path.rename(outside)
                source_path.symlink_to(outside)
            else:
                outside.hardlink_to(source_path)
            rejected = load_trusted_rmc_language_store(test_repository)
            ledger.check(rejected.trusted is False, label + " rejects store", rejected)
            ledger.check(rejected.records == (), label + " exposes no records")

    with tempfile.TemporaryDirectory(prefix="forge_rmc_memory_symlink_") as temporary:
        test_repository = Path(temporary)
        _write_record(test_repository, stable_record)
        _write_receipts(
            test_repository,
            stable_source_receipt,
            stable_approval_receipt,
        )
        memory = test_repository / "memory"
        outside_memory = test_repository / "outside-memory"
        memory.rename(outside_memory)
        memory.symlink_to(outside_memory, target_is_directory=True)
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "symlinked memory parent rejects store")
        ledger.check(rejected.records == (), "symlinked memory parent exposes no records")

    # Independently valid receipts still fail when their semantic or charter
    # bindings do not describe the exact record that references them.
    with tempfile.TemporaryDirectory(prefix="forge_rmc_receipt_binding_") as temporary:
        test_repository = Path(temporary)
        mismatched_arguments = _record_arguments(stable_record)
        mismatched_arguments["source_receipt_ref"] = (
            report_source_receipt.source_receipt_id
        )
        provisional = build_exact_language_memory_record(
            **mismatched_arguments,
            approval_receipt_ref="operator_approval_receipt:"
            + _digest("binding-pending"),
        )
        mismatched_approval = build_language_operator_approval_receipt(
            proposal_ref="language_memory_proposal:" + _digest("binding-proposal"),
            charter_ref=report_source_receipt.charter_ref,
            charter_entry_ref=report_source_receipt.charter_entry_ref,
            registry_ref=stable_record.registry_ref,
            source_receipt_ref=report_source_receipt.source_receipt_id,
            semantic_contract_ref=stable_record.semantic_contract_ref,
            record_draft_ref=language_record_draft_ref(provisional),
            store_class="stable",
        )
        mismatched_record = build_exact_language_memory_record(
            **mismatched_arguments,
            approval_receipt_ref=mismatched_approval.approval_receipt_id,
        )
        _write_record(test_repository, mismatched_record)
        _write_receipts(
            test_repository,
            report_source_receipt,
            mismatched_approval,
        )
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "source semantic binding mismatch rejects")
        ledger.check(
            rejected.reason_codes == ("language_receipt_record_binding_mismatch",),
            "source binding mismatch has typed reason",
            rejected,
        )

    with tempfile.TemporaryDirectory(prefix="forge_rmc_receipt_charter_") as temporary:
        test_repository = Path(temporary)
        arguments = _record_arguments(stable_record)
        provisional = build_exact_language_memory_record(
            **arguments,
            approval_receipt_ref="operator_approval_receipt:"
            + _digest("charter-pending"),
        )
        mismatched_approval = build_language_operator_approval_receipt(
            proposal_ref="language_memory_proposal:" + _digest("charter-proposal"),
            charter_ref="governed_semantic_charter:" + _digest("other-charter"),
            charter_entry_ref=stable_source_receipt.charter_entry_ref,
            registry_ref=stable_record.registry_ref,
            source_receipt_ref=stable_source_receipt.source_receipt_id,
            semantic_contract_ref=stable_record.semantic_contract_ref,
            record_draft_ref=language_record_draft_ref(provisional),
            store_class="stable",
        )
        mismatched_record = build_exact_language_memory_record(
            **arguments,
            approval_receipt_ref=mismatched_approval.approval_receipt_id,
        )
        _write_record(test_repository, mismatched_record)
        _write_receipts(
            test_repository,
            stable_source_receipt,
            mismatched_approval,
        )
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "approval charter binding mismatch rejects")
        ledger.check(
            rejected.reason_codes == ("language_receipt_record_binding_mismatch",),
            "approval charter mismatch has typed reason",
            rejected,
        )

    # The current approval schema is deliberately stable-only. A live record
    # cannot borrow a stable approval receipt and enter the trusted snapshot.
    with tempfile.TemporaryDirectory(prefix="forge_rmc_live_unapproved_") as temporary:
        test_repository = Path(temporary)
        live_arguments = _record_arguments(stable_record)
        live_arguments["store_class"] = "live"
        live_arguments["lifecycle_state"] = "eligible_live"
        live_record = build_exact_language_memory_record(
            **live_arguments,
            approval_receipt_ref=stable_approval_receipt.approval_receipt_id,
        )
        _write_record(test_repository, live_record)
        _write_receipts(
            test_repository,
            stable_source_receipt,
            stable_approval_receipt,
        )
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "stable approval cannot admit live record")
        ledger.check(rejected.records == (), "unapproved live record exposes no records")

    # The content-addressed record digest, not caller-controlled path text,
    # determines the only admitted stable promotion target.
    try:
        build_language_promotion_receipt(
            proposal_ref=stable_approval_receipt.proposal_ref,
            charter_ref=stable_approval_receipt.charter_ref,
            charter_entry_ref=stable_approval_receipt.charter_entry_ref,
            registry_ref=stable_record.registry_ref,
            source_receipt_ref=stable_record.source_receipt_ref,
            approval_receipt_ref=stable_record.approval_receipt_ref,
            record_ref=stable_record.record_id,
            target_ref="memory/rmc_language_core_v1/stable/../escape.json",
        )
        traversal_rejected = False
    except LanguageReceiptError:
        traversal_rejected = True
    ledger.check(traversal_rejected, "promotion receipt rejects target traversal")

    # A hostile governance tree is irrelevant while the record root is absent;
    # connected-empty must remain the first and deterministic outcome.
    with tempfile.TemporaryDirectory(prefix="forge_rmc_no_record_root_") as temporary:
        test_repository = Path(temporary)
        hostile_governance = (
            test_repository / "memory" / "rmc_language_core_governance_v1"
        )
        hostile_governance.mkdir(parents=True)
        hostile_governance.chmod(0o777)
        empty = load_trusted_rmc_language_store(test_repository)
        ledger.check(empty.trusted is True, "no record root ignores governance tree")
        ledger.check(empty.load_status == "TRUSTED_EMPTY", "no record root remains empty")
        ledger.check(empty.filesystem_read_performed is False, "no record root performs no read")

    mutation_cases = {
        "tampered_record_id": lambda data: data.update(
            {"record_id": "rmc_exact_language_record:" + ("0" * 64)}
        ),
        "raw_text_flag": lambda data: data.update({"raw_text_present": True}),
        "vector_flag": lambda data: data.update({"vector_present": True}),
        "tampered_semantic_contract_ref": lambda data: data.update(
            {"semantic_contract_ref": "meaning_semantic_contract:" + ("0" * 64)}
        ),
        "tampered_semantic_signature": lambda data: data.update(
            {"semantic_signature_ref": "semantic_signature:" + ("0" * 64)}
        ),
        "tampered_polarity": lambda data: data.update(
            {"negated": not data["negated"]}
        ),
        "tampered_grammar_rule": lambda data: data.update(
            {"grammar_rule_ref": "FORGE-GRAMMAR-V0-TAMPERED"}
        ),
        "unknown_concept": lambda data: data.update(
            {"concept_refs": ["forge_preview_concept:" + ("f" * 64)]}
        ),
        "wrong_store_class": lambda data: data.update(
            {"store_class": "live", "lifecycle_state": "eligible_live"}
        ),
        "unsupported_field": lambda data: data.update({"raw_word": "manifest"}),
    }
    tampered_provider = None
    for label, mutate in mutation_cases.items():
        with tempfile.TemporaryDirectory(prefix="forge_rmc_reject_") as temporary:
            test_repository = Path(temporary)
            path = _write_record(test_repository, stable_record)
            _write_receipts(
                test_repository,
                stable_source_receipt,
                stable_approval_receipt,
            )
            data = stable_record.to_dict()
            mutate(data)
            path.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
            rejected = load_trusted_rmc_language_store(test_repository)
            if tampered_provider is None:
                tampered_provider = rejected
            ledger.check(rejected.trusted is False, label + " rejects entire store", rejected)
            ledger.check(
                rejected.load_status == "REJECTED",
                label + " typed rejected status",
                rejected,
            )
            ledger.check(
                rejected.records == (),
                label + " exposes no partial records",
                rejected,
            )
            ledger.check(
                rejected.snapshot.record_count == 0,
                label + " projects empty snapshot",
                rejected,
            )

    with patch.object(
        store_module,
        "load_trusted_rmc_language_store",
        return_value=tampered_provider,
    ):
        preview_adapter = importlib.reload(preview_adapter)
        rejected_response = preview_adapter.build_language_core_preview_response(
            {"source_text": "Please inspect the manifest."}
        )
    ledger.check(
        rejected_response.get("status") == "ERROR",
        "Ask Forge fails closed when trusted store is rejected",
        rejected_response,
    )
    ledger.check(
        rejected_response.get("reason_code")
        == "trusted_rmc_language_store_rejected",
        "Ask Forge store rejection is typed",
        rejected_response,
    )
    preview_adapter = importlib.reload(preview_adapter)

    with tempfile.TemporaryDirectory(prefix="forge_rmc_unexpected_") as temporary:
        test_repository = Path(temporary)
        root = test_repository / "memory" / "rmc_language_core_v1"
        root.mkdir(parents=True)
        root.chmod(0o755)
        (root / "notes.txt").write_text("not eligible", encoding="utf-8")
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "unexpected root entry rejected")
        ledger.check(rejected.snapshot.record_count == 0, "unexpected root entry fails closed")

    with tempfile.TemporaryDirectory(prefix="forge_rmc_symlink_") as temporary:
        test_repository = Path(temporary)
        stable_dir = test_repository / "memory" / "rmc_language_core_v1" / "stable"
        stable_dir.mkdir(parents=True)
        stable_dir.parent.chmod(0o755)
        stable_dir.chmod(0o755)
        target = test_repository / "outside.json"
        target.write_text(json.dumps(stable_record.to_dict()), encoding="utf-8")
        link = stable_dir / (stable_record.record_id.split(":", 1)[1] + ".json")
        link.symlink_to(target)
        rejected = load_trusted_rmc_language_store(test_repository)
        ledger.check(rejected.trusted is False, "symlinked record rejected")
        ledger.check(rejected.records == (), "symlink rejection fails closed")

    with tempfile.TemporaryDirectory(prefix="forge_rmc_empty_") as temporary:
        empty = load_trusted_rmc_language_store(Path(temporary))
        ledger.check(empty.trusted is True, "missing dedicated root is safe")
        ledger.check(empty.load_status == "TRUSTED_EMPTY", "missing root is connected-empty")
        ledger.check(empty.snapshot.record_count == 0, "missing root has no records")

    injection = build_language_core_preview_response(
        {
            "source_text": "What does core mean?",
            "rmc_snapshot": stable_record.to_dict(),
        }
    )
    ledger.check(injection.get("status") == "ERROR", "HTTP caller cannot inject RMC")
    ledger.check(
        injection.get("reason_code") == "request_contains_unsupported_fields",
        "HTTP RMC injection has typed rejection",
        injection,
    )

    provider_source = (
        repository
        / "rmc_engine_v1/rmc_exact_language_store.py"
    ).read_text(encoding="utf-8")
    ledger.check("write_text(" not in provider_source, "provider contains no Path write")
    ledger.check("write_bytes(" not in provider_source, "provider contains no byte write")
    ledger.check("os.write(" not in provider_source, "provider contains no OS write")

    print("AI.WEB RMC EXACT LANGUAGE STORE")
    print(f"checks={ledger.checks}")
    print(f"failures={len(ledger.failures)}")
    print("dedicated_root=memory/rmc_language_core_v1/{stable,live}")
    print("exact_ids=concept,sense,relation,role,ancestry")
    print("raw_words_tokens_embeddings_vectors_similarity=0")
    print("runtime_writes=0")
    print("RESULT=" + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
