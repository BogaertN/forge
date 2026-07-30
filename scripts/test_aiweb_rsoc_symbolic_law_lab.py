#!/usr/bin/env python3
"""Behavior and authority-boundary checks for the isolated RSOC law lab."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiweb_language_core_bootstrap.rsoc_symbolic_law_lab import (
    RsocLawStatus,
    build_symbolic_field_state,
    preview_rsoc_law,
    rsoc_law_registry,
)


checks = 0


def check(value: object, label: str) -> None:
    global checks
    if value is not True:
        raise AssertionError(label)
    checks += 1


registry = rsoc_law_registry()
check(len(registry) == 10, "ten exact laws registered")
check(len({law.law_id for law in registry}) == 10, "law identities unique")
check(len({law.glyph for law in registry}) == 10, "glyphs unique")
check(all(law.law_id == law.expected_id() for law in registry), "law IDs canonical")
check(all(law.external_reference_authority is False for law in registry), "references have no authority")
check(all(law.runtime_enabled is False for law in registry), "runtime disabled")

field = build_symbolic_field_state(
    identity_refs=("identity:alpha",),
    phase_index=4,
    recursion_depth=2,
    drift_micro=200_000,
    resonance_micro=800_000,
    memory_charge_micro=500_000,
    entropy_micro=300_000,
    loop_ref="loop:alpha",
    echo_ancestry_refs=("ancestry:origin", "ancestry:step-2"),
    lineage_refs=("lineage:origin",),
)
check(field.field_id == field.expected_id(), "field ID canonical")

echo_pass = preview_rsoc_law("Ê", (field,), expected_ancestry_ref="ancestry:origin")
echo_fail = preview_rsoc_law("Ê", (field,), expected_ancestry_ref="ancestry:missing")
check(echo_pass.status is RsocLawStatus.PREVIEW_READY, "Echo preview admitted")
check(echo_pass.echo_valid is True, "exact Echo ancestry passes")
check(echo_fail.echo_valid is False, "missing Echo ancestry fails")
check(not echo_pass.output_fields, "Echo does not mutate field")
check(echo_pass.result_id == echo_pass.expected_id(), "Echo receipt canonical")

archive = preview_rsoc_law("Ĉ", (field,))
check(archive.status is RsocLawStatus.PREVIEW_READY, "archive preview admitted")
check(len(archive.output_fields) == 1, "archive creates one successor preview")
archived = archive.output_fields[0]
check(archived.archived is True, "successor marked archived")
check(archived.identity_refs == field.identity_refs, "archive identity preserved")
check(archived.memory_charge_micro == field.memory_charge_micro, "archive charge preserved")
check(archived.entropy_micro == field.entropy_micro, "archive entropy preserved")
check(field.archived is False, "input remains immutable")
check(preview_rsoc_law("Ĉ", (archived,)).status is RsocLawStatus.HELD_PRECONDITION, "repeat archive held")

for law in registry:
    if law.glyph in {"Ê", "Ĉ"}:
        continue
    operands = (field, field) if law.declared_arity == 2 else (field,)
    held = preview_rsoc_law(law.glyph, operands)
    check(held.status is RsocLawStatus.HELD_REFERENCE_CONFLICT, f"unresolved law held {law.glyph}")
    check(not held.output_fields, f"unresolved law has no successor {law.glyph}")
    check(bool(held.issue_codes), f"unresolved law exposes issues {law.glyph}")

check(preview_rsoc_law("R^", (field,)).status is RsocLawStatus.UNSUPPORTED, "lookalike glyph refused")
check(preview_rsoc_law("Ê", ()).status is RsocLawStatus.HELD_PRECONDITION, "arity enforced")
tampered = replace(field, entropy_micro=field.entropy_micro + 1)
check(preview_rsoc_law("Ê", (tampered,), expected_ancestry_ref="ancestry:origin").status is RsocLawStatus.HELD_INVALID, "tampered field held")

for name, value in echo_pass.boundary.to_dict().items():
    if name in {"isolated_lab", "preview_only", "forge_owned_provisional_law"}:
        check(value is True, f"boundary true {name}")
    else:
        check(value is False, f"boundary false {name}")
for name in ("runtime_authority", "memory_authority", "action_authority", "delivery_authority"):
    check(getattr(echo_pass, name) is False, f"receipt grants no {name}")

try:
    field.phase_index = 9
    raise AssertionError("field unexpectedly mutable")
except (FrozenInstanceError, AttributeError):
    check(True, "field immutable")

print(f"RSOC symbolic law lab: {checks} checks passed")
