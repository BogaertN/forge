#!/usr/bin/env python3
"""Behavior and adversarial tests for governed Language Core promotion."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import threading


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiweb_language_core_bootstrap.meaning_compiler_preview import (
    compile_meaning_preview,
)
from rmc_engine_v1.operator_council_preview import (
    build_operator_council_preview,
)
from rmc_engine_v1.rmc_exact_language_store import (
    evaluate_exact_identity_resonance,
    load_trusted_rmc_language_store,
)
from rmc_engine_v1.rmc_language_promotion import (
    approve_language_memory,
    language_charter_status,
    prepare_language_memory,
    promote_language_memory,
)


checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    if not condition:
        raise AssertionError(message)
    checks += 1


def approval_request(prepared: dict[str, object]) -> dict[str, object]:
    return {
        "proposal_id": prepared["proposal_id"],
        "record_id": prepared["record_id"],
        "approval_token": prepared["approval_token"],
        "approval_confirmation_phrase": prepared["approval_confirmation_phrase"],
    }


def promotion_request(approved: dict[str, object]) -> dict[str, object]:
    return {
        "proposal_id": approved["proposal_id"],
        "record_id": approved["record_id"],
        "approval_receipt_id": approved["approval_receipt_id"],
        "promotion_token": approved["promotion_token"],
        "promotion_confirmation_phrase": approved["promotion_confirmation_phrase"],
    }


def prepare(root: Path, fixture_id: str) -> dict[str, object]:
    return prepare_language_memory(
        {"fixture_id": fixture_id},
        repository_root=root,
        local_request_verified=True,
    )


def approve(root: Path, prepared: dict[str, object]) -> dict[str, object]:
    return approve_language_memory(
        approval_request(prepared),
        action_nonce=prepared["approval_action_nonce"],
        repository_root=root,
        local_request_verified=True,
    )


def promote(root: Path, approved: dict[str, object]) -> dict[str, object]:
    return promote_language_memory(
        promotion_request(approved),
        action_nonce=approved["promotion_action_nonce"],
        repository_root=root,
        local_request_verified=True,
    )


def test_three_stage_transaction() -> None:
    with tempfile.TemporaryDirectory(prefix="forge_language_promotion_") as temporary:
        root = Path(temporary) / "repository"
        root.mkdir()
        before = tuple(root.rglob("*"))
        status = language_charter_status(repository_root=root)
        check(status["status"] == "OK", "empty charter status must be readable")
        check(status["entry_count"] == 8, "only eight charter fixtures admitted")
        check(status["approved_count"] == 0, "no approval may be fabricated")
        check(status["promoted_count"] == 0, "no record may be fabricated")
        check(tuple(root.rglob("*")) == before, "status must not write")

        fixture = next(
            item
            for item in status["entries"]
            if item["fixture_key"] == "forge_uses_rmc"
        )
        prepared = prepare(root, fixture["fixture_id"])
        check(prepared["status"] == "PREPARED", "fixture must prepare")
        check(prepared["writes_performed"] is False, "prepare must not write")
        check(tuple(root.rglob("*")) == before, "prepare filesystem must remain clean")
        check(prepared["record_preview"]["raw_text_present"] is False, "record has no raw text")
        check(prepared["record_preview"]["token_stream_present"] is False, "record has no token stream")
        check(prepared["record_preview"]["embedding_present"] is False, "record has no embedding")
        check(prepared["record_preview"]["vector_present"] is False, "record has no vector")

        bad_approval = dict(approval_request(prepared))
        bad_approval["approval_token"] = "APPROVE_EVERYTHING"
        refused = approve_language_memory(
            bad_approval,
            action_nonce=prepared["approval_action_nonce"],
            repository_root=root,
            local_request_verified=True,
        )
        check(refused["status"] == "REJECTED", "wrong approval token rejected")
        check(refused["writes_performed"] is False, "refused approval cannot write")

        approved = approve(root, prepared)
        check(approved["status"] == "APPROVED", "exact approval must succeed")
        check(approved["memory_record_written"] is False, "approval cannot write RMC record")
        check(len(approved["written_refs"]) == 2, "source and approval receipts written")
        provider_before = load_trusted_rmc_language_store(root)
        check(provider_before.load_status == "TRUSTED_EMPTY", "approval alone leaves RMC empty")
        approved_status = language_charter_status(repository_root=root)
        approved_entry = next(
            item
            for item in approved_status["entries"]
            if item["fixture_id"] == fixture["fixture_id"]
        )
        check(
            approved_entry["state"] == "APPROVED_NOT_PROMOTED",
            "status distinguishes approval from promotion",
        )
        check(
            approved_entry["restart_required"] is False,
            "approval-only evidence does not require restart",
        )

        # Even a correctly approved record cannot be made live by manually
        # placing its preview JSON in the stable directory.  The independent
        # promotion receipt is the second-stage runtime admission gate.
        stable = root / "memory" / "rmc_language_core_v1" / "stable"
        stable.mkdir(parents=True)
        stable.parent.chmod(0o700)
        stable.chmod(0o700)
        injected = stable / (prepared["record_id"].split(":", 1)[1] + ".json")
        injected.write_text(
            json.dumps(prepared["record_preview"], sort_keys=True) + "\n",
            encoding="utf-8",
        )
        injected.chmod(0o600)
        injected_provider = load_trusted_rmc_language_store(root)
        check(
            injected_provider.load_status == "REJECTED",
            "approved-but-not-promoted record injection is rejected",
        )
        check(
            injected_provider.reason_codes == ("receipt_file_open_rejected",),
            "missing promotion receipt has a typed rejection",
        )
        check(
            injected_provider.records == (),
            "approved injection exposes no partial runtime record",
        )
        injected.unlink()
        replayed_approval = approve_language_memory(
            approval_request(prepared),
            action_nonce=prepared["approval_action_nonce"],
            repository_root=root,
            local_request_verified=True,
        )
        check(replayed_approval["status"] == "REJECTED", "approval nonce is one-time")

        bad_promotion = dict(promotion_request(approved))
        bad_promotion["promotion_confirmation_phrase"] += " tampered"
        refused_promotion = promote_language_memory(
            bad_promotion,
            action_nonce=approved["promotion_action_nonce"],
            repository_root=root,
            local_request_verified=True,
        )
        check(refused_promotion["status"] == "REJECTED", "wrong promotion phrase rejected")
        promoted = promote(root, approved)
        check(promoted["status"] == "PROMOTED", "exact promotion must succeed")
        check(promoted["memory_record_written"] is True, "one exact record is commit point")
        check(promoted["restart_required"] is True, "runtime restart must be explicit")
        check(len(promoted["written_refs"]) == 2, "promotion receipt and record written")
        replayed_promotion = promote_language_memory(
            promotion_request(approved),
            action_nonce=approved["promotion_action_nonce"],
            repository_root=root,
            local_request_verified=True,
        )
        check(replayed_promotion["status"] == "REJECTED", "promotion nonce is one-time")

        provider = load_trusted_rmc_language_store(root)
        check(provider.load_status == "TRUSTED_STRUCTURED", "provider loads promoted record")
        check(len(provider.records) == 1, "only one stable record exists")
        check(provider.records[0].record_id == promoted["record_id"], "record identity preserved")
        stable_files = tuple((root / "memory" / "rmc_language_core_v1" / "stable").glob("*.json"))
        check(len(stable_files) == 1, "stable store contains exactly one file")
        check(
            fixture["exact_source_text"] not in stable_files[0].read_text(encoding="utf-8"),
            "stable record must not persist raw charter source",
        )
        after_status = language_charter_status(repository_root=root)
        check(after_status["promoted_count"] == 1, "status sees one promoted fixture")
        promoted_entry = next(
            item for item in after_status["entries"] if item["fixture_id"] == fixture["fixture_id"]
        )
        check(promoted_entry["state"] == "PROMOTED", "entry state must be promoted")

        compiled = compile_meaning_preview(
            fixture["exact_source_text"],
            rmc_snapshot=provider.snapshot,
        )
        resonance = evaluate_exact_identity_resonance(
            provider.records,
            compiled.meaning_candidates,
            compiled.frame_candidates,
        )
        council = build_operator_council_preview(
            compiled,
            exact_rmc_resonances=resonance,
        )
        check(
            council["status"] == "RECOMMEND_FOR_OPERATOR_REVIEW",
            "exact promoted semantic contract may be recommended for human review",
        )
        check(council["recommendation_only"] is True, "Council remains recommendation-only")

        opposite = compile_meaning_preview(
            "Forge does not use RMC memory.",
            rmc_snapshot=provider.snapshot,
        )
        opposite_resonance = evaluate_exact_identity_resonance(
            provider.records,
            opposite.meaning_candidates,
            opposite.frame_candidates,
        )
        opposite_council = build_operator_council_preview(
            opposite,
            exact_rmc_resonances=opposite_resonance,
        )
        check(
            opposite_council["status"] == "HOLD_FOR_EVIDENCE",
            "positive memory cannot support a negated proposition",
        )


def test_rejections_and_idempotency() -> None:
    with tempfile.TemporaryDirectory(prefix="forge_language_rejections_") as temporary:
        root = Path(temporary) / "repository"
        root.mkdir()
        status = language_charter_status(repository_root=root)
        fixture_id = status["entries"][0]["fixture_id"]
        rejected = prepare_language_memory(
            {"fixture_id": fixture_id, "source_text": "caller injection"},
            repository_root=root,
            local_request_verified=True,
        )
        check(rejected["status"] == "REJECTED", "raw caller source field rejected")
        rejected = prepare_language_memory(
            {"fixture_id": fixture_id},
            repository_root=root,
            local_request_verified=False,
        )
        check(rejected["reason_code"] == "local_same_origin_request_required", "local gate required")
        rejected = prepare_language_memory(
            {"fixture_id": "semantic_charter_replay_fixture:" + "0" * 64},
            repository_root=root,
            local_request_verified=True,
        )
        check(rejected["reason_code"] == "fixture_not_in_proposed_charter", "unknown fixture rejected")

        prepared = prepare(root, fixture_id)
        approved = approve(root, prepared)
        promoted = promote(root, approved)
        check(promoted["status"] == "PROMOTED", "first promotion succeeds")
        prepared_again = prepare(root, fixture_id)
        approved_again = approve(root, prepared_again)
        check(approved_again["writes_performed"] is False, "same receipts are idempotent")
        promoted_again = promote(root, approved_again)
        check(promoted_again["status"] == "ALREADY_PROMOTED", "same record is idempotent")
        check(promoted_again["writes_performed"] is False, "idempotent promotion writes nothing")


def test_concurrent_commit_is_single_record() -> None:
    with tempfile.TemporaryDirectory(prefix="forge_language_concurrent_") as temporary:
        root = Path(temporary) / "repository"
        root.mkdir()
        status = language_charter_status(repository_root=root)
        fixture_id = status["entries"][1]["fixture_id"]
        approved: list[dict[str, object]] = []
        for _index in range(2):
            approved.append(approve(root, prepare(root, fixture_id)))
        results: list[dict[str, object]] = []
        result_lock = threading.Lock()

        def worker(item: dict[str, object]) -> None:
            value = promote(root, item)
            with result_lock:
                results.append(value)

        threads = tuple(threading.Thread(target=worker, args=(item,)) for item in approved)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        check(len(results) == 2, "both concurrent requests returned")
        check(
            sorted(item["status"] for item in results) == ["ALREADY_PROMOTED", "PROMOTED"],
            "lock permits one commit and one idempotent observation",
        )
        provider = load_trusted_rmc_language_store(root)
        check(len(provider.records) == 1, "concurrency creates one record only")


def test_promotion_receipt_tamper_and_mismatch() -> None:
    with tempfile.TemporaryDirectory(prefix="forge_language_promotion_receipt_") as temporary:
        root = Path(temporary) / "repository"
        root.mkdir()
        fixture_id = language_charter_status(repository_root=root)["entries"][2][
            "fixture_id"
        ]
        promoted = promote(root, approve(root, prepare(root, fixture_id)))
        check(promoted["status"] == "PROMOTED", "tamper fixture first promotes")
        promotion_directory = (
            root
            / "memory"
            / "rmc_language_core_governance_v1"
            / "promotion_receipts"
        )
        promotion_path = next(promotion_directory.glob("*.json"))
        data = json.loads(promotion_path.read_text(encoding="utf-8"))
        data["exact_record_recomputed_under_lock"] = False
        promotion_path.write_text(
            json.dumps(data, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tampered = load_trusted_rmc_language_store(root)
        check(tampered.load_status == "REJECTED", "tampered promotion receipt rejected")
        check(tampered.records == (), "tampered promotion exposes no record")

    with tempfile.TemporaryDirectory(prefix="forge_language_promotion_swap_") as temporary:
        root = Path(temporary) / "repository"
        root.mkdir()
        entries = language_charter_status(repository_root=root)["entries"]
        promoted_a = promote(
            root,
            approve(root, prepare(root, entries[0]["fixture_id"])),
        )
        promoted_b = promote(
            root,
            approve(root, prepare(root, entries[1]["fixture_id"])),
        )
        check(
            promoted_a["status"] == "PROMOTED"
            and promoted_b["status"] == "PROMOTED",
            "two exact fixtures promote before mismatch test",
        )
        promotion_directory = (
            root
            / "memory"
            / "rmc_language_core_governance_v1"
            / "promotion_receipts"
        )
        receipts = {
            json.loads(path.read_text(encoding="utf-8"))["record_ref"]: path
            for path in promotion_directory.glob("*.json")
        }
        first_path = receipts[promoted_a["record_id"]]
        second_payload = receipts[promoted_b["record_id"]].read_text(
            encoding="utf-8"
        )
        first_path.write_text(second_payload, encoding="utf-8")
        mismatched = load_trusted_rmc_language_store(root)
        check(mismatched.load_status == "REJECTED", "mismatched promotion receipt rejected")
        check(mismatched.records == (), "one mismatched promotion rejects whole snapshot")


def main() -> int:
    test_three_stage_transaction()
    test_rejections_and_idempotency()
    test_concurrent_commit_is_single_record()
    test_promotion_receipt_tamper_and_mismatch()
    print(f"Governed RMC language promotion: {checks} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
