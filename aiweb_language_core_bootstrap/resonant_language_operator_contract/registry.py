"""Closed RSOC operator contract registry for Slice 36B0.

The ten entries mirror the canonical RSOC glyph set as disabled contracts.
This module provides no operator implementation and performs no application.
"""

from __future__ import annotations

from .schema import (
    CONTRACT_SCHEMA_VERSION,
    CONTRACT_SPEC_ID,
    CONTRACT_SPEC_VERSION,
    EXPECTED_RSOC_OPERATOR_COUNT,
    FBSC_AUTHORITY_REF,
    FIELD_SCHEMA_ID,
    LineageIdentityHandling,
    OPERATOR_SCHEMA_ID,
    OperatorArity,
    OperatorRuntimeStatus,
    RMC_LANGUAGE_LAW_AUTHORITY_REF,
    RSOC_AUTHORITY_REF,
    RsocLanguageOperatorRegistry,
    RsocOperatorContract,
)
from ..schema import stable_record_id


_OPERATOR_ROWS = (
    (
        "resonance_merge",
        "⟁",
        "Resonance Merge",
        OperatorArity.BINARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no merge execution in Slice 36B0", "no source binding", "no meaning"),
    ),
    (
        "resonance_severance",
        "⧧",
        "Resonance Severance",
        OperatorArity.BINARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no severance execution in Slice 36B0", "trace deletion prohibited"),
    ),
    (
        "recursive_amplification",
        "⧒",
        "Recursive Amplification",
        OperatorArity.UNARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no amplification execution in Slice 36B0", "no candidate generation"),
    ),
    (
        "symbolic_discharge",
        "⧀",
        "Symbolic Discharge / Collapse",
        OperatorArity.UNARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no discharge execution in Slice 36B0", "no destructive deletion"),
    ),
    (
        "recursive_lock",
        "⧙",
        "Recursive Lock / Fusion",
        OperatorArity.BINARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no lock execution in Slice 36B0", "no sealing authority"),
    ),
    (
        "recursive_memory_integral",
        "⧜",
        "Recursive Integration / Memory",
        OperatorArity.UNARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no memory operation in Slice 36B0", "no persistence authority"),
    ),
    (
        "christ_function",
        "χ(t)",
        "Christ Function / Grace Override",
        OperatorArity.UNARY,
        LineageIdentityHandling.CONTROLLED_MASK_ONLY_UNDER_LATER_AUTHORITY,
        True,
        (
            "only RSOC operator permitted to decrease entropy",
            "no threshold or trigger installed in Slice 36B0",
            "no automatic invocation",
        ),
    ),
    (
        "resurrection_reload",
        "R̂",
        "Resurrection Reload",
        OperatorArity.UNARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no resurrection execution in Slice 36B0", "no memory reload"),
    ),
    (
        "controlled_archival",
        "Ĉ",
        "Controlled Archival",
        OperatorArity.UNARY,
        LineageIdentityHandling.CONTROLLED_MASK_ONLY_UNDER_LATER_AUTHORITY,
        False,
        ("no archival execution in Slice 36B0", "no storage access"),
    ),
    (
        "echo_validation",
        "Ê",
        "Echo Validation",
        OperatorArity.UNARY,
        LineageIdentityHandling.COPY_UNCHANGED,
        False,
        ("no validation execution in Slice 36B0", "no acceptance authority"),
    ),
)


def _build_operator(
    *,
    operator_key: str,
    glyph: str,
    canonical_name: str,
    arity: OperatorArity,
    identity_handling: LineageIdentityHandling,
    may_decrease_entropy: bool,
    hard_boundaries: tuple[str, ...],
) -> RsocOperatorContract:
    body = {
        "operator_key": operator_key,
        "glyph": glyph,
        "canonical_name": canonical_name,
        "arity": arity,
        "identity_handling": identity_handling,
        "domain_schema_id": FIELD_SCHEMA_ID,
        "range_schema_id": FIELD_SCHEMA_ID,
        "runtime_status": OperatorRuntimeStatus.CONTRACT_ONLY_DISABLED,
        "source_authority_refs": (
            RSOC_AUTHORITY_REF,
            FBSC_AUTHORITY_REF,
            RMC_LANGUAGE_LAW_AUTHORITY_REF,
        ),
        "hard_boundaries": hard_boundaries,
        "may_decrease_entropy": may_decrease_entropy,
        "entropy_thresholds_installed": False,
        "commutation_table_installed": False,
        "numeric_transform_installed": False,
        "runtime_enabled": False,
        "application_implemented": False,
        "automatic_trigger_authorized": False,
        "source_binding_authorized": False,
        "phase_assignment_authorized": False,
        "meaning_authorized": False,
        "memory_authorized": False,
        "route_authorized": False,
        "tool_authorized": False,
        "action_authorized": False,
        "delivery_authorized": False,
        "contract_spec_id": CONTRACT_SPEC_ID,
        "contract_spec_version": CONTRACT_SPEC_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "operator_schema_id": OPERATOR_SCHEMA_ID,
    }
    return RsocOperatorContract(
        contract_id=stable_record_id("rsoc_operator_contract", body),
        **body,
    )


def build_default_rsoc_operator_registry() -> RsocLanguageOperatorRegistry:
    operators = tuple(
        _build_operator(
            operator_key=row[0],
            glyph=row[1],
            canonical_name=row[2],
            arity=row[3],
            identity_handling=row[4],
            may_decrease_entropy=row[5],
            hard_boundaries=row[6],
        )
        for row in _OPERATOR_ROWS
    )
    body = {
        "operators": operators,
        "exact_operator_count": EXPECTED_RSOC_OPERATOR_COUNT,
        "default_runtime_enabled": False,
        "operator_application_available": False,
        "source_binding_available": False,
        "phase_assignment_available": False,
        "legacy_imports_allowed": False,
        "mea_substitution_allowed": False,
        "hidden_fallback_allowed": False,
        "contract_spec_id": CONTRACT_SPEC_ID,
        "contract_spec_version": CONTRACT_SPEC_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "registry_schema_id": "aiweb-rsoc-language-operator-registry-v1",
    }
    return RsocLanguageOperatorRegistry(
        registry_id=stable_record_id("rsoc_language_operator_registry", body),
        **body,
    )


def operator_contract_for_key(
    operator_key: object,
    registry: RsocLanguageOperatorRegistry | None = None,
) -> RsocOperatorContract | None:
    if type(operator_key) is not str:
        return None
    selected = registry or build_default_rsoc_operator_registry()
    return next(
        (item for item in selected.operators if item.operator_key == operator_key),
        None,
    )


def operator_contract_for_glyph(
    glyph: object,
    registry: RsocLanguageOperatorRegistry | None = None,
) -> RsocOperatorContract | None:
    if type(glyph) is not str:
        return None
    selected = registry or build_default_rsoc_operator_registry()
    return next((item for item in selected.operators if item.glyph == glyph), None)
