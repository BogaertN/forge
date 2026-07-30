"""Forge-owned provisional law registry for all ten RSOC glyphs.

The user's supplied glyph/name list controls the provisional Forge labels.
Google Drive and imported packets remain reference evidence only.  Conflicting
reference claims are recorded instead of silently resolved.
"""

from __future__ import annotations

from typing import Final

from ..schema import stable_record_id
from .schema import RSOC_LAW_LAB_SCHEMA_VERSION, RsocLawDefinition


_COMMON_INVARIANTS: Final[tuple[str, ...]] = (
    "exact_input_field_identity_validated",
    "source_lineage_never_deleted",
    "no_live_memory_or_action_authority",
    "successor_is_preview_only",
)

_REFERENCE_SOURCE_REFS: Final[tuple[str, ...]] = (
    "operator_supplied_glyph_name_list:2026-07-27",
    (
        "google_drive:1Ma6QGau6_6KXH-E9Q4Dj3SZZ6eJYsPfGFDJ2LnhfEgw:"
        "revision:AIroW34CBNiIz7EzodgTlQBNyx2ayNSubzTchS6PMy5eeMRVk0PVk_"
        "sgJD6c1_ALFhk8AQBV5uPlHqSGbNdrFA"
    ),
)


# key, glyph, Forge provisional name, arity, reference names, admitted preview,
# explicit conflicts that prevent an executable numeric law.
_LAW_ROWS: Final[tuple[tuple[object, ...], ...]] = (
    (
        "resonance_merge",
        "⟁",
        "Resonance Merge",
        2,
        ("Merge", "Resonance Merge"),
        "",
        (
            "reference_identity_preservation_vs_new_identity_conflict",
            "reference_entropy_monotonicity_vs_entropy_credit_conflict",
            "forge_numeric_merge_law_not_admitted",
        ),
    ),
    (
        "resonance_severance",
        "⧧",
        "Resonance Severance",
        1,
        ("Sever", "Resonance Severance"),
        "",
        ("forge_constituent_and_charge_split_law_not_admitted",),
    ),
    (
        "recursive_amplification",
        "⧒",
        "Recursive Amplification",
        1,
        ("Amplify", "Recursive Amplification"),
        "",
        ("forge_gain_and_drift_law_not_admitted",),
    ),
    (
        "symbolic_discharge",
        "⧀",
        "Symbolic Discharge / Collapse",
        1,
        ("Discharge", "Symbolic Discharge / Collapse"),
        "",
        (
            "reference_entropy_monotonicity_vs_entropy_reduction_conflict",
            "forge_charge_disposition_law_not_admitted",
        ),
    ),
    (
        "recursive_lock",
        "⧙",
        "Recursive Lock / Fusion",
        2,
        ("Lock", "Recursive Lock / Fusion"),
        "",
        (
            "reference_identity_preservation_vs_new_identity_conflict",
            "reference_entropy_monotonicity_vs_entropy_credit_conflict",
            "forge_unlock_and_discharge_law_not_admitted",
        ),
    ),
    (
        "recursive_memory_integral",
        "⧜",
        "Recursive Integration / Memory",
        1,
        ("Memory Integral", "Recursive Integration / Memory"),
        "",
        ("forge_time_interval_and_charge_law_not_admitted",),
    ),
    (
        "christ_function",
        "χ(t)",
        "Christ Function / Grace Override",
        1,
        ("Christ Function – Grace Override", "Christ Function / Grace Override"),
        "",
        (
            "automatic_invocation_conflicts_with_operator_authority_boundary",
            "forge_grace_threshold_and_transform_not_admitted",
        ),
    ),
    (
        "resurrection_reload",
        "R̂",
        "Resurrection Reload",
        1,
        ("Resurrection Reload", "Resonance Elevation"),
        "",
        (
            "canonical_name_and_semantic_effect_conflict",
            "forge_reload_source_and_phase_law_not_admitted",
        ),
    ),
    (
        "controlled_archival",
        "Ĉ",
        "Controlled Archival",
        1,
        ("Controlled Archival",),
        "archive_state_preview",
        (),
    ),
    (
        "echo_validation",
        "Ê",
        "Echo Validation",
        1,
        ("Echo Validation",),
        "exact_ancestry_echo_preview",
        (),
    ),
)


def _definition(row: tuple[object, ...]) -> RsocLawDefinition:
    key, glyph, name, arity, reference_names, operation, conflicts = row
    body = {
        "operator_key": key,
        "glyph": glyph,
        "forge_provisional_name": name,
        "declared_arity": arity,
        "reference_names": reference_names,
        "reference_source_refs": _REFERENCE_SOURCE_REFS,
        "typed_operand_kind": "symbolic_field_state",
        "admitted_preview_operation": operation,
        "reference_conflict_codes": conflicts,
        "invariant_codes": _COMMON_INVARIANTS,
        "forge_owned": True,
        "provisional": True,
        "external_reference_authority": False,
        "runtime_enabled": False,
        "schema_version": RSOC_LAW_LAB_SCHEMA_VERSION,
    }
    return RsocLawDefinition(
        law_id=stable_record_id("rsoc_lab_law", body),
        **body,
    )


RSOC_LAW_REGISTRY: Final[tuple[RsocLawDefinition, ...]] = tuple(
    _definition(row) for row in _LAW_ROWS
)


def rsoc_law_registry() -> tuple[RsocLawDefinition, ...]:
    return RSOC_LAW_REGISTRY


def law_for_glyph(glyph: str) -> RsocLawDefinition | None:
    return next((law for law in RSOC_LAW_REGISTRY if law.glyph == glyph), None)


__all__ = ("RSOC_LAW_REGISTRY", "law_for_glyph", "rsoc_law_registry")
