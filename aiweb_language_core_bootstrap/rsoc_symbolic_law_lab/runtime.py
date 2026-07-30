"""Pure deterministic evaluation for the isolated RSOC law laboratory."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from ..schema import stable_record_id
from .laws import law_for_glyph
from .schema import (
    MICRO_SCALE,
    RSOC_LAW_LAB_SCHEMA_VERSION,
    RsocLawBoundary,
    RsocLawPreviewResult,
    RsocLawStatus,
    SymbolicFieldState,
)


def build_symbolic_field_state(
    *,
    identity_refs: object,
    phase_index: object,
    recursion_depth: object = 0,
    drift_micro: object = 0,
    resonance_micro: object = MICRO_SCALE,
    memory_charge_micro: object = 0,
    entropy_micro: object = 0,
    loop_ref: object = "",
    echo_ancestry_refs: object = (),
    lineage_refs: object = (),
    locked: object = False,
    archived: object = False,
    grace_used: object = False,
    revision: object = 0,
) -> SymbolicFieldState:
    """Build one immutable, content-addressed lab field or fail closed."""

    def refs(value: object, name: str, *, required: bool = False) -> tuple[str, ...]:
        if not isinstance(value, (tuple, list)):
            raise TypeError(f"{name} must be a tuple or list")
        result = tuple(value)
        if any(type(item) is not str or not item for item in result):
            raise ValueError(f"{name} contains an invalid reference")
        if len(result) != len(set(result)):
            raise ValueError(f"{name} contains duplicate references")
        if required and not result:
            raise ValueError(f"{name} must not be empty")
        return tuple(sorted(result))

    identities = refs(identity_refs, "identity_refs", required=True)
    ancestry = refs(echo_ancestry_refs, "echo_ancestry_refs")
    lineage = refs(lineage_refs, "lineage_refs", required=True)
    for name, value, lower, upper in (
        ("phase_index", phase_index, 1, 9),
        ("recursion_depth", recursion_depth, 0, 1_000_000),
        ("drift_micro", drift_micro, 0, MICRO_SCALE),
        ("resonance_micro", resonance_micro, 0, MICRO_SCALE),
        ("memory_charge_micro", memory_charge_micro, 0, 10**18),
        ("entropy_micro", entropy_micro, 0, MICRO_SCALE),
        ("revision", revision, 0, 10**12),
    ):
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f"{name} is outside the admitted fixed-point range")
    for name, value in (
        ("locked", locked),
        ("archived", archived),
        ("grace_used", grace_used),
    ):
        if type(value) is not bool:
            raise TypeError(f"{name} must be bool")
    if type(loop_ref) is not str:
        raise TypeError("loop_ref must be text")
    body = {
        "identity_refs": identities,
        "phase_index": phase_index,
        "recursion_depth": recursion_depth,
        "drift_micro": drift_micro,
        "resonance_micro": resonance_micro,
        "memory_charge_micro": memory_charge_micro,
        "entropy_micro": entropy_micro,
        "loop_ref": loop_ref,
        "echo_ancestry_refs": ancestry,
        "lineage_refs": lineage,
        "locked": locked,
        "archived": archived,
        "grace_used": grace_used,
        "revision": revision,
        "schema_version": RSOC_LAW_LAB_SCHEMA_VERSION,
    }
    return SymbolicFieldState(
        field_id=stable_record_id("rsoc_lab_field", body),
        **body,
    )


def _valid_field(value: object) -> bool:
    if type(value) is not SymbolicFieldState:
        return False
    try:
        rebuilt = build_symbolic_field_state(
            identity_refs=value.identity_refs,
            phase_index=value.phase_index,
            recursion_depth=value.recursion_depth,
            drift_micro=value.drift_micro,
            resonance_micro=value.resonance_micro,
            memory_charge_micro=value.memory_charge_micro,
            entropy_micro=value.entropy_micro,
            loop_ref=value.loop_ref,
            echo_ancestry_refs=value.echo_ancestry_refs,
            lineage_refs=value.lineage_refs,
            locked=value.locked,
            archived=value.archived,
            grace_used=value.grace_used,
            revision=value.revision,
        )
    except (TypeError, ValueError):
        return False
    return rebuilt == value


def _result(
    *,
    status: RsocLawStatus,
    reason_code: str,
    law=None,
    inputs: Iterable[SymbolicFieldState] = (),
    outputs: tuple[SymbolicFieldState, ...] = (),
    echo_valid: bool | None = None,
    issues: tuple[str, ...] = (),
    trace: tuple[str, ...] = (),
) -> RsocLawPreviewResult:
    boundary = RsocLawBoundary()
    input_refs = tuple(item.field_id for item in inputs)
    body = {
        "status": status,
        "reason_code": reason_code,
        "law": law,
        "input_field_refs": input_refs,
        "output_fields": outputs,
        "echo_valid": echo_valid,
        "issue_codes": issues,
        "trace": trace,
        "boundary": boundary,
        "deterministic": True,
        "runtime_authority": False,
        "memory_authority": False,
        "action_authority": False,
        "delivery_authority": False,
        "schema_version": RSOC_LAW_LAB_SCHEMA_VERSION,
    }
    return RsocLawPreviewResult(
        result_id=stable_record_id("rsoc_lab_result", body),
        **body,
    )


def preview_rsoc_law(
    glyph: object,
    operands: object,
    *,
    expected_ancestry_ref: object = "",
) -> RsocLawPreviewResult:
    """Evaluate one typed law in memory and grant no operational authority."""

    if type(glyph) is not str:
        return _result(
            status=RsocLawStatus.HELD_INVALID,
            reason_code="glyph_must_be_exact_text",
            issues=("invalid_glyph_type",),
        )
    law = law_for_glyph(glyph)
    if law is None:
        return _result(
            status=RsocLawStatus.UNSUPPORTED,
            reason_code="glyph_not_in_forge_provisional_law_registry",
            issues=("unknown_exact_glyph",),
        )
    if not isinstance(operands, (tuple, list)):
        return _result(
            status=RsocLawStatus.HELD_INVALID,
            reason_code="operands_must_be_a_bounded_sequence",
            law=law,
            issues=("invalid_operand_container",),
        )
    fields = tuple(operands)
    if len(fields) != law.declared_arity:
        return _result(
            status=RsocLawStatus.HELD_PRECONDITION,
            reason_code="operator_arity_not_satisfied",
            law=law,
            inputs=tuple(item for item in fields if type(item) is SymbolicFieldState),
            issues=("operator_arity_not_satisfied",),
        )
    if not all(_valid_field(item) for item in fields):
        return _result(
            status=RsocLawStatus.HELD_INVALID,
            reason_code="invalid_or_tampered_symbolic_field",
            law=law,
            inputs=tuple(item for item in fields if type(item) is SymbolicFieldState),
            issues=("invalid_or_tampered_symbolic_field",),
        )
    if law.reference_conflict_codes or not law.admitted_preview_operation:
        return _result(
            status=RsocLawStatus.HELD_REFERENCE_CONFLICT,
            reason_code="forge_executable_law_not_admitted",
            law=law,
            inputs=fields,
            issues=law.reference_conflict_codes or ("missing_forge_owned_law",),
            trace=("validate_exact_law_identity", "hold_before_numeric_or_state_transform"),
        )

    field = fields[0]
    if law.admitted_preview_operation == "archive_state_preview":
        if field.archived:
            return _result(
                status=RsocLawStatus.HELD_PRECONDITION,
                reason_code="field_already_archived",
                law=law,
                inputs=fields,
                issues=("field_already_archived",),
            )
        successor = build_symbolic_field_state(
            identity_refs=field.identity_refs,
            phase_index=field.phase_index,
            recursion_depth=field.recursion_depth,
            drift_micro=field.drift_micro,
            resonance_micro=field.resonance_micro,
            memory_charge_micro=field.memory_charge_micro,
            entropy_micro=field.entropy_micro,
            loop_ref=field.loop_ref,
            echo_ancestry_refs=field.echo_ancestry_refs,
            lineage_refs=tuple(sorted(set(field.lineage_refs + (field.field_id,)))),
            locked=field.locked,
            archived=True,
            grace_used=field.grace_used,
            revision=field.revision + 1,
        )
        return _result(
            status=RsocLawStatus.PREVIEW_READY,
            reason_code="controlled_archival_state_preview_ready",
            law=law,
            inputs=fields,
            outputs=(successor,),
            trace=(
                "validate_exact_field_identity",
                "preserve_identity_charge_entropy_and_lineage",
                "mark_successor_archived_in_isolated_preview",
            ),
        )

    if law.admitted_preview_operation == "exact_ancestry_echo_preview":
        if type(expected_ancestry_ref) is not str or not expected_ancestry_ref:
            return _result(
                status=RsocLawStatus.HELD_PRECONDITION,
                reason_code="expected_ancestry_ref_required",
                law=law,
                inputs=fields,
                issues=("expected_ancestry_ref_required",),
            )
        valid = expected_ancestry_ref in field.echo_ancestry_refs
        return _result(
            status=RsocLawStatus.PREVIEW_READY,
            reason_code=(
                "exact_echo_ancestry_present"
                if valid
                else "exact_echo_ancestry_absent"
            ),
            law=law,
            inputs=fields,
            echo_valid=valid,
            trace=(
                "validate_exact_field_identity",
                "compare_exact_ancestry_reference",
                "return_boolean_without_field_mutation",
            ),
        )

    return _result(
        status=RsocLawStatus.UNSUPPORTED,
        reason_code="unimplemented_admitted_preview_operation",
        law=law,
        inputs=fields,
    )


__all__ = ("build_symbolic_field_state", "preview_rsoc_law")
