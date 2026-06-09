"""Patch 300 - Integer-only CT reward-policy arithmetic from Memory Economy Appendix A."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .enums import ContributionType, ContractValueError, DifficultyClass, InfluenceType, parse_enum

CT_REWARD_POLICY_VERSION = "ct_reward_policy_v1_memory_economy_appendix_a"
CT_UNIT_MILLI = 1000
BASIS_POINTS_DENOMINATOR = 10000
SCHEMA_VERSION = "ct_reward_calculation_preview_v1_patch300"

_BASE_REWARDS_MUTABLE = {
    ContributionType.CRT: {
        DifficultyClass.LIGHT: 1000,
        DifficultyClass.STANDARD: 5000,
        DifficultyClass.HEAVY: 20000,
        DifficultyClass.MONUMENT: 60000,
    },
    ContributionType.CPT: {
        DifficultyClass.LIGHT: 500,
        DifficultyClass.STANDARD: 2000,
        DifficultyClass.HEAVY: 8000,
        DifficultyClass.MONUMENT: 40000,
    },
    ContributionType.BLD: {
        DifficultyClass.LIGHT: 2000,
        DifficultyClass.STANDARD: 10000,
        DifficultyClass.HEAVY: 30000,
        DifficultyClass.MONUMENT: 80000,
    },
}
BASE_REWARDS_MILLI_CT = MappingProxyType(
    {kind: MappingProxyType(values) for kind, values in _BASE_REWARDS_MUTABLE.items()}
)
INFLUENCE_MULTIPLIER_BPS = MappingProxyType(
    {
        InfluenceType.DIRECT: 10000,
        InfluenceType.INDIRECT: 5000,
        InfluenceType.COLLABORATIVE: 3300,
    }
)


@dataclass(frozen=True)
class RewardCalculationPreview:
    contribution_type: ContributionType
    difficulty_class: DifficultyClass
    influence_type: InfluenceType
    base_reward_milli_ct: int
    influence_multiplier_bps: int
    calculated_milli_ct: int
    ct_reward_policy_version: str = CT_REWARD_POLICY_VERSION
    schema_version: str = SCHEMA_VERSION
    calculation_status: str = "CALCULATION_PREVIEW_NOT_MINTED"
    mint_authorized: bool = False
    ledger_write_authorized: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ct_reward_policy_version": self.ct_reward_policy_version,
            "calculation_status": self.calculation_status,
            "contribution_type": self.contribution_type.value,
            "difficulty_class": self.difficulty_class.value,
            "influence_type": self.influence_type.value,
            "base_reward_milli_ct": self.base_reward_milli_ct,
            "influence_multiplier_bps": self.influence_multiplier_bps,
            "basis_points_denominator": BASIS_POINTS_DENOMINATOR,
            "calculated_milli_ct": self.calculated_milli_ct,
            "mint_authorized": self.mint_authorized,
            "ledger_write_authorized": self.ledger_write_authorized,
        }

    @property
    def display_ct(self) -> str:
        return format_milli_ct(self.calculated_milli_ct)


def format_milli_ct(amount: int) -> str:
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
        raise ContractValueError("milli_ct amount must be a non-negative integer")
    whole, fraction = divmod(amount, CT_UNIT_MILLI)
    return f"{whole}.{fraction:03d} CT"


def calculate_reward_preview(
    contribution_type: ContributionType | str,
    difficulty_class: DifficultyClass | str,
    influence_type: InfluenceType | str,
) -> RewardCalculationPreview:
    """Compute a deterministic, non-minting integer milli-CT reward preview."""
    ctype = parse_enum(ContributionType, contribution_type, "contribution_type")
    difficulty = parse_enum(DifficultyClass, difficulty_class, "difficulty_class")
    influence = parse_enum(InfluenceType, influence_type, "influence_type")
    base = BASE_REWARDS_MILLI_CT[ctype][difficulty]
    multiplier = INFLUENCE_MULTIPLIER_BPS[influence]
    numerator = base * multiplier
    quotient, remainder = divmod(numerator, BASIS_POINTS_DENOMINATOR)
    if remainder != 0:
        raise ContractValueError("policy v1 calculation must resolve to an exact integer milli_ct value")
    return RewardCalculationPreview(ctype, difficulty, influence, base, multiplier, quotient)


def reward_policy_manifest() -> dict[str, Any]:
    return {
        "schema_version": "ct_reward_policy_manifest_v1_patch300",
        "ct_reward_policy_version": CT_REWARD_POLICY_VERSION,
        "ct_unit": {"unit_name": "milli_ct", "milli_ct_per_ct": CT_UNIT_MILLI},
        "base_rewards_milli_ct": {
            ctype.value: {difficulty.value: value for difficulty, value in values.items()}
            for ctype, values in BASE_REWARDS_MILLI_CT.items()
        },
        "influence_multiplier_bps": {
            influence.value: value for influence, value in INFLUENCE_MULTIPLIER_BPS.items()
        },
        "basis_points_denominator": BASIS_POINTS_DENOMINATOR,
        "floating_point_ct_arithmetic_permitted": False,
        "mint_authorized": False,
        "ledger_write_authorized": False,
    }
