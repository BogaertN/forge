#!/usr/bin/env python3
"""Patch 300 behavior tests - Contribution Economy no-write contract foundation."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from pathlib import Path
from typing import Any, Callable

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from contribution_economy_v1 import PATCH_ID, SCHEMA_KERNEL_VERSION, kernel_identity  # noqa: E402
from contribution_economy_v1.contracts import (  # noqa: E402
    BASIS_POINTS_DENOMINATOR,
    CT_REWARD_POLICY_VERSION,
    ConsentPermission,
    ConsentScopeReferenceContract,
    ContractObjectType,
    ContractValueError,
    ContributionEventContract,
    ContributionType,
    CTMintEventContract,
    DifficultyClass,
    FinalizedMemoryCapsuleContract,
    InfluenceLedgerEntryContract,
    InfluenceType,
    InvestmentLedgerEntryContract,
    LedgerType,
    MemoryCapsuleCandidateContract,
    NullificationCorrectionEventContract,
    Patch300ActivationState,
    REQUIRED_FUTURE_VALIDATION_GATES,
    SourceEvidenceReference,
    ValidatedMemoryCapsuleContract,
    ValidationRecordContract,
    calculate_reward_preview,
    canonical_json,
    evaluate_lifecycle_transition,
    format_milli_ct,
    hash_contract_payload,
    patch300_boundary_manifest,
    reward_policy_manifest,
)
from contribution_economy_v1.contracts.identity_reference_schema import (  # noqa: E402
    ContributorPrincipalReferenceContract,
    reject_raw_private_identity,
)

passed = 0
failed = 0


def check(name: str, condition: bool, detail: object | None = None) -> None:
    global passed, failed
    if condition:
        passed += 1
        suffix = f" - {detail}" if detail is not None else ""
        print(f"  [PASS] {name}{suffix}")
    else:
        failed += 1
        suffix = f" - observed={detail!r}" if detail is not None else ""
        print(f"  [FAIL] {name}{suffix}")


def expect_rejection(name: str, func: Callable[[], Any]) -> None:
    try:
        func()
    except ValueError:
        check(name, True)
    except Exception as exc:
        check(name, False, f"unexpected {type(exc).__name__}: {exc}")
    else:
        check(name, False, "did not reject")


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(child) for child in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_float(child) for child in value)
    return False


def synthetic_principal() -> ContributorPrincipalReferenceContract:
    consent = ConsentScopeReferenceContract(consent_record_id="consent_contract_only_001")
    return ContributorPrincipalReferenceContract(
        principal_id="principal_contract_only_001",
        pseudonymous_alias_id="alias_contract_only_001",
        identity_proof_reference="1" * 64,
        consent=consent,
    )


def synthetic_event(**overrides: Any) -> ContributionEventContract:
    args: dict[str, Any] = {
        "event_id": "event_contract_only_001",
        "contributor": synthetic_principal(),
        "timestamp_contributed": "2026-05-30T17:30:00Z",
        "proof_hash": "2" * 64,
        "contribution_type": ContributionType.BLD,
        "difficulty_class": DifficultyClass.STANDARD,
        "influence_type": InfluenceType.DIRECT,
        "source_evidence": (
            SourceEvidenceReference("code_patch_contract", "fixture:patch300", "3" * 64),
        ),
    }
    args.update(overrides)
    return ContributionEventContract(**args)


def main() -> int:
    print("PATCH 300 BEHAVIOR TESTS - CONTRIBUTION ECONOMY CONTRACT FOUNDATION / NO-WRITE")
    print(f"Forge root: {FORGE_ROOT}")

    identity = kernel_identity()
    check("patch_id_locked", PATCH_ID == "Patch 300 - Contribution Economy Contract Foundation / No-Write Schema and Policy Kernel", PATCH_ID)
    check("kernel_version_locked", SCHEMA_KERNEL_VERSION == "contribution_economy_contract_foundation_v1_patch300", SCHEMA_KERNEL_VERSION)
    check("policy_version_locked", CT_REWARD_POLICY_VERSION == "ct_reward_policy_v1_memory_economy_appendix_a", CT_REWARD_POLICY_VERSION)
    boundary = patch300_boundary_manifest()
    check("kernel_boundary_embedded", identity["boundary"] == boundary)
    for key in (
        "routes_exposed", "writes_files", "writes_runtime_state", "writes_memory", "writes_rmc_memory",
        "writes_jsonl_ledger", "writes_chroma", "writes_identity_vault", "creates_contribution_event",
        "creates_memory_capsule", "finalizes_memory_capsule", "mints_contribution_tokens",
        "writes_influence_ledger", "writes_investment_ledger", "creates_nullification_event",
        "applies_penalty_or_burn", "renders_public_output", "calls_llm", "executes_shell",
        "performs_network_io", "modifies_mea", "modifies_rmc", "modifies_main_py",
    ):
        check(f"boundary_{key}_false", boundary[key] is False, boundary[key])

    expect_rejection("enum_rejects_unknown_contribution_type", lambda: ContributionType("TOKEN"))
    expect_rejection("enum_rejects_unknown_difficulty", lambda: DifficultyClass("tiny"))
    expect_rejection("enum_rejects_unknown_influence", lambda: InfluenceType("owner"))
    expect_rejection("enum_rejects_unknown_ledger", lambda: LedgerType("mixed"))
    expect_rejection("enum_rejects_live_state", lambda: Patch300ActivationState("minted"))

    canonical_a = {"schema_version": "fixture_v1", "b": None, "a": 1, "nested": {"z": "yes", "a": False}}
    canonical_b = {"nested": {"a": False, "z": "yes"}, "a": 1, "b": None, "schema_version": "fixture_v1"}
    encoded_a = canonical_json(canonical_a)
    encoded_b = canonical_json(canonical_b)
    check("canonical_json_deterministic", encoded_a == encoded_b)
    check("canonical_json_preserves_explicit_null", '"b":null' in encoded_a, encoded_a)
    expect_rejection("canonical_json_requires_schema_version", lambda: canonical_json({"a": 1}))
    expect_rejection("canonical_json_rejects_float", lambda: canonical_json({"schema_version": "x", "amount": 1.5}))
    expect_rejection(
        "reward_hash_requires_policy_version",
        lambda: canonical_json({"schema_version": "x"}, require_policy_version=True),
    )
    hash_a = hash_contract_payload(canonical_a)
    hash_b = hash_contract_payload(canonical_b)
    hash_changed = hash_contract_payload({**canonical_a, "a": 2})
    check("hash_deterministic", hash_a.object_hash == hash_b.object_hash)
    check("hash_changes_on_governed_field_change", hash_a.object_hash != hash_changed.object_hash)
    check("hash_algorithm_sha256", hash_a.hash_algorithm == "sha256")
    check("hash_is_preview_only", hash_a.persisted is False and hash_a.economic_action_authorized is False)

    policy = reward_policy_manifest()
    check("reward_policy_manifest_version", policy["ct_reward_policy_version"] == CT_REWARD_POLICY_VERSION)
    check("reward_policy_integer_only_declaration", policy["floating_point_ct_arithmetic_permitted"] is False)
    expected_cases = {
        ("CRT", "light", "direct"): 1000,
        ("CRT", "standard", "collaborative"): 1650,
        ("CPT", "light", "collaborative"): 165,
        ("BLD", "monument", "direct"): 80000,
    }
    for args, expected in expected_cases.items():
        result = calculate_reward_preview(*args)
        check(f"known_reward_{'_'.join(args)}", result.calculated_milli_ct == expected, result.calculated_milli_ct)
        check(f"known_reward_policy_{'_'.join(args)}", result.ct_reward_policy_version == CT_REWARD_POLICY_VERSION)
        check(f"known_reward_not_minted_{'_'.join(args)}", result.mint_authorized is False and result.ledger_write_authorized is False)
    all_calcs = [
        calculate_reward_preview(kind, difficulty, influence).as_dict()
        for kind in ContributionType for difficulty in DifficultyClass for influence in InfluenceType
    ]
    check("reward_policy_all_36_combinations_present", len(all_calcs) == 36, len(all_calcs))
    check("reward_policy_all_values_integer_only", not any(contains_float(item) for item in all_calcs))
    check("reward_policy_exact_basis_denominator", BASIS_POINTS_DENOMINATOR == 10000)
    check("reward_display_integer_conversion", format_milli_ct(1650) == "1.650 CT")
    expect_rejection("reward_rejects_invalid_type", lambda: calculate_reward_preview("BAD", "standard", "direct"))

    principal = synthetic_principal()
    principal_payload = principal.as_dict()
    check("principal_is_reference_only", principal_payload["identity_vault_write_authorized"] is False)
    check("consent_all_disabled", all(value == ConsentPermission.NOT_AUTHORIZED.value for value in principal_payload["consent"]["consent_scope"].values()))
    expect_rejection(
        "raw_private_identity_rejected",
        lambda: reject_raw_private_identity({"public_capsule": {"email": "not-allowed@example.invalid"}}),
    )
    expect_rejection(
        "consent_authorization_rejected",
        lambda: ConsentScopeReferenceContract(
            consent_record_id="consent_invalid",
            attribution="granted",  # type: ignore[arg-type]
        ),
    )

    event = synthetic_event()
    event_payload = event.as_dict()
    check("contribution_event_contract_only", event_payload["event_status"] == "contract_only_not_persisted")
    check("contribution_event_no_persistence", event_payload["persistence_authorized"] is False)
    check("contribution_event_no_mint", event_payload["mint_authorized"] is False)
    check("contribution_event_no_public_output", event_payload["public_output_authorized"] is False)
    expect_rejection("event_rejects_finalization_claim", lambda: synthetic_event(finalized=True))
    expect_rejection("event_rejects_mint_claim", lambda: synthetic_event(mint_requested=True))
    expect_rejection("event_rejects_ledger_write_claim", lambda: synthetic_event(ledger_write_requested=True))
    expect_rejection("event_rejects_public_output_claim", lambda: synthetic_event(public_output_requested=True))
    expect_rejection("event_rejects_bad_proof_hash", lambda: synthetic_event(proof_hash="not-a-hash"))
    expect_rejection("event_rejects_non_utc_timestamp", lambda: synthetic_event(timestamp_contributed="2026-05-30T17:30:00-04:00"))

    validation = ValidationRecordContract("validation_contract_only_001", event.event_id)
    validation_payload = validation.as_dict()
    check("validation_gate_registry_complete", set(REQUIRED_FUTURE_VALIDATION_GATES) == set(validation_payload["required_future_gates"]))
    check("validation_not_executed", validation_payload["validation_executed"] is False)
    expect_rejection(
        "validation_activation_rejected",
        lambda: ValidationRecordContract("v", "e", status=Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED),
    )

    candidate = MemoryCapsuleCandidateContract(
        "capsule_contract_only_001", (event.event_id,), "artifact:synthetic-contract-only", {"difficulty_class": "standard"}
    )
    candidate_payload = candidate.as_dict()
    check("candidate_not_persisted", candidate_payload["persisted"] is False)
    check("candidate_not_finalized", candidate_payload["finalized"] is False and candidate_payload["top_level_hash"] is None)
    check("candidate_mint_blocked", candidate_payload["ct_minting_status"] == "blocked_not_authorized")
    expect_rejection(
        "candidate_rejects_duplicate_event_refs",
        lambda: MemoryCapsuleCandidateContract("c", ("event", "event"), "artifact:x", {}),
    )
    expect_rejection(
        "candidate_rejects_private_identity",
        lambda: MemoryCapsuleCandidateContract("c", ("event",), "artifact:x", {"email": "nope"}),
    )
    validated = ValidatedMemoryCapsuleContract(candidate.capsule_contract_id, validation)
    finalized = FinalizedMemoryCapsuleContract(candidate.capsule_contract_id)
    check("validated_capsule_is_inactive", validated.as_dict()["validated"] is False)
    check("finalized_capsule_is_inactive", finalized.as_dict()["finalized"] is False)
    expect_rejection(
        "finalization_activation_rejected",
        lambda: FinalizedMemoryCapsuleContract("c", status=Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED),
    )

    reward = calculate_reward_preview("BLD", "standard", "direct")
    mint = CTMintEventContract("mint_contract_only_001", candidate.capsule_contract_id, reward)
    influence = InfluenceLedgerEntryContract("influence_contract_only_001", mint.mint_contract_id)
    investment = InvestmentLedgerEntryContract("investment_contract_only_001", "investment:disabled-contract")
    check("mint_inactive_zero_ct", mint.as_dict()["ct_minted_milli_ct"] == 0 and mint.as_dict()["mint_executed"] is False)
    check("influence_ledger_inactive_zero_effect", influence.as_dict()["ct_delta_milli_ct"] == 0 and influence.as_dict()["entry_written"] is False)
    investment_payload = investment.as_dict()
    check("investment_ledger_separate", investment_payload["ledger_type"] == "investment_ledger")
    check("investment_never_creates_ct", investment_payload["creates_ct"] is False and investment_payload["creates_contribution_ownership"] is False)
    expect_rejection(
        "influence_rejects_investment_substitution",
        lambda: InfluenceLedgerEntryContract("i", "m", ledger_type=LedgerType.INVESTMENT),
    )
    expect_rejection(
        "investment_rejects_influence_substitution",
        lambda: InvestmentLedgerEntryContract("i", "ref", ledger_type=LedgerType.INFLUENCE),
    )
    expect_rejection(
        "mint_activation_rejected",
        lambda: CTMintEventContract("m", "c", reward, status=Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED),
    )

    correction = NullificationCorrectionEventContract("correction_contract_only_001", candidate.capsule_contract_id, "proof_hash_mismatch")
    check("nullification_is_append_only_future_rule", correction.as_dict()["append_only_required_if_activated_later"] is True)
    check("nullification_not_executed", correction.as_dict()["action_executed"] is False)
    expect_rejection(
        "nullification_activation_rejected",
        lambda: NullificationCorrectionEventContract("n", "c", "reason", status=Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED),
    )

    for object_type in ContractObjectType:
        decision = evaluate_lifecycle_transition(object_type, Patch300ActivationState.DEFINED_DISABLED, "persisted")
        check(f"lifecycle_blocks_persisted_{object_type.value}", decision.allowed is False)
        check(f"lifecycle_has_no_state_write_{object_type.value}", decision.as_dict()["writes_state"] is False)

    print(f"RESULT: PATCH_300_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
