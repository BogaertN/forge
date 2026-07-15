#!/usr/bin/env python3
"""Behavior and adversarial tests for Slice 36C."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.input_event_custody import (
    capture_input_event,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    SourceFieldProjectionStatus,
    project_source_field,
)
from aiweb_language_core_bootstrap.symbolic_grammar_operator_registry import (
    EXPECTED_FBSC_CANONICAL_OPERATOR_COUNT,
    EXPECTED_GRAMMAR_OPERATOR_COUNT,
    EXPECTED_REQUIRED_FAMILY_COUNT,
    REQUIRED_LANGUAGE_CORE_FAMILIES,
    GrammarOperatorDefinition,
    GrammarOperatorFamily,
    GrammarOperatorOrigin,
    GrammarOperatorPhaseAffinityStatus,
    GrammarOperatorProposalDecision,
    GrammarOperatorRuntimeStatus,
    ProposalDecisionStatus,
    build_default_symbolic_grammar_operator_registry,
    evaluate_grammar_operator_proposal,
    grammar_operator_for_glyph,
    grammar_operator_for_key,
    grammar_operators_for_family,
    validate_grammar_operator_definition,
    validate_grammar_operator_proposal_decision,
    validate_symbolic_grammar_operator_registry,
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1


def projection_for(text: str, sequence: int):
    custody = capture_input_event(
        text,
        source_id="fixture.user",
        channel_id="fixture.chat",
        sequence_number=sequence,
    )
    check(custody.event is not None, "custody event created")
    result = project_source_field(custody.event)
    check(result.projection is not None, "source projection created")
    return result


registry_a = build_default_symbolic_grammar_operator_registry()
registry_b = build_default_symbolic_grammar_operator_registry()

check(registry_a == registry_b, "registry deterministic")
check(registry_a.registry_id == registry_a.expected_id(), "registry stable id")
check(
    validate_symbolic_grammar_operator_registry(registry_a).ok,
    "registry validates",
)
check(
    len(registry_a.operators) == EXPECTED_GRAMMAR_OPERATOR_COUNT == 25,
    "operator count exact",
)
check(
    registry_a.exact_fbsc_canonical_operator_count
    == EXPECTED_FBSC_CANONICAL_OPERATOR_COUNT
    == 8,
    "FBSC canonical count exact",
)
check(
    registry_a.exact_required_family_count
    == EXPECTED_REQUIRED_FAMILY_COUNT
    == 20,
    "required family count exact",
)
check(registry_a.proposal_rules == (), "no proposal rules installed")
check(registry_a.exact_proposal_rule_count == 0, "proposal rule count zero")
check(registry_a.closed_world, "registry closed world")

for field_name in (
    "default_runtime_enabled",
    "automatic_activation_available",
    "proposal_creation_available",
    "source_binding_available",
    "operator_application_available",
    "phase_assignment_available",
    "rsoc_mapping_available",
    "meaning_authority_available",
    "permission_authority_available",
    "route_authority_available",
    "action_authority_available",
    "hidden_fallback_allowed",
):
    check(
        getattr(registry_a, field_name) is False,
        f"registry authority false {field_name}",
    )

keys = tuple(item.operator_key for item in registry_a.operators)
ids = tuple(item.definition_id for item in registry_a.operators)
glyphs = tuple(
    item.glyph for item in registry_a.operators if item.glyph is not None
)
check(len(set(keys)) == len(keys), "operator keys unique")
check(len(set(ids)) == len(ids), "definition ids unique")
check(len(set(glyphs)) == len(glyphs), "glyphs unique")
check(
    set(REQUIRED_LANGUAGE_CORE_FAMILIES).issubset(
        {item.family for item in registry_a.operators}
    ),
    "all required families present",
)

canonical = {
    "fbsc_initiator": ("⊕", ("Φ1",)),
    "fbsc_desire_vector": ("⇋", ("Φ3",)),
    "fbsc_structural_binding": ("⚯", ("Φ4",)),
    "fbsc_decay_mark": ("↧", ("Φ5",)),
    "fbsc_grace_override": ("†", ("Φ6",)),
    "fbsc_name_declaration": ("✎", ("Φ7",)),
    "fbsc_projection": ("↠", ("Φ8",)),
    "fbsc_loop_seal": ("⟲", ("Φ9",)),
}

for definition in registry_a.operators:
    check(
        type(definition) is GrammarOperatorDefinition,
        f"definition exact type {definition.operator_key}",
    )
    check(
        definition.definition_id == definition.expected_id(),
        f"definition stable id {definition.operator_key}",
    )
    check(
        validate_grammar_operator_definition(definition).ok,
        f"definition validates {definition.operator_key}",
    )
    check(
        definition.runtime_status
        is GrammarOperatorRuntimeStatus.REGISTERED_INERT,
        f"definition inert {definition.operator_key}",
    )
    check(
        definition.operator_version == "1.0.0",
        f"definition version {definition.operator_key}",
    )
    check(
        definition.permitted_source_field_prerequisites,
        f"permitted prerequisites present {definition.operator_key}",
    )
    check(
        definition.prohibited_prerequisites,
        f"prohibited prerequisites present {definition.operator_key}",
    )
    check(
        definition.source_span_requirements,
        f"span requirements present {definition.operator_key}",
    )
    check(
        definition.ancestry_requirements,
        f"ancestry requirements present {definition.operator_key}",
    )
    check(
        definition.required_companion_operator_keys == (),
        f"companions unasserted {definition.operator_key}",
    )
    check(
        definition.compatible_operator_keys == (),
        f"compatibility unasserted {definition.operator_key}",
    )
    check(
        definition.incompatible_operator_keys == (),
        f"incompatibility unasserted {definition.operator_key}",
    )
    check(
        definition.proposal_rule_ids == (),
        f"proposal rules absent {definition.operator_key}",
    )
    check(
        definition.rsoc_operator_keys == (),
        f"RSOC mapping absent {definition.operator_key}",
    )
    check(
        definition.allowed_effects,
        f"responsibility effects present {definition.operator_key}",
    )
    for field_name in (
        "automatic_activation_authorized",
        "source_binding_authorized",
        "operator_application_authorized",
        "phase_assignment_authorized",
        "meaning_authorized",
        "permission_authorized",
        "memory_authorized",
        "route_authorized",
        "tool_authorized",
        "action_authorized",
        "delivery_authorized",
    ):
        check(
            getattr(definition, field_name) is False,
            f"definition authority false {definition.operator_key}:{field_name}",
        )

    if definition.operator_key in canonical:
        expected_glyph, expected_phases = canonical[definition.operator_key]
        check(
            definition.origin
            is GrammarOperatorOrigin.FBSC_VOLUME_II_CANONICAL,
            f"canonical origin {definition.operator_key}",
        )
        check(
            definition.glyph == expected_glyph,
            f"canonical glyph {definition.operator_key}",
        )
        check(
            definition.phase_affinity == expected_phases,
            f"canonical phase affinity {definition.operator_key}",
        )
        check(
            definition.phase_affinity_status
            is GrammarOperatorPhaseAffinityStatus.EXPLICIT_ADVISORY_ONLY,
            f"canonical phase advisory {definition.operator_key}",
        )
    else:
        check(
            definition.origin
            is GrammarOperatorOrigin.AIWEB_LANGUAGE_CORE_BOUNDED_EXTENSION,
            f"extension origin {definition.operator_key}",
        )
        check(
            definition.glyph is None,
            f"extension glyph absent {definition.operator_key}",
        )
        check(
            definition.phase_affinity == (),
            f"extension phase absent {definition.operator_key}",
        )
        check(
            definition.phase_affinity_status
            is GrammarOperatorPhaseAffinityStatus.UNDEFINED,
            f"extension phase undefined {definition.operator_key}",
        )

# Lookups are exact and deterministic.
for definition in registry_a.operators:
    check(
        grammar_operator_for_key(
            definition.operator_key,
            registry_a,
        )
        == definition,
        f"key lookup exact {definition.operator_key}",
    )
    family_items = grammar_operators_for_family(
        definition.family,
        registry_a,
    )
    check(
        definition in family_items,
        f"family lookup contains {definition.operator_key}",
    )
    if definition.glyph is not None:
        check(
            grammar_operator_for_glyph(
                definition.glyph,
                registry_a,
            )
            == definition,
            f"glyph lookup exact {definition.operator_key}",
        )

check(grammar_operator_for_key("unknown", registry_a) is None, "unknown key")
check(grammar_operator_for_key(None, registry_a) is None, "non-string key")
check(grammar_operator_for_glyph("?", registry_a) is None, "unknown glyph")
check(
    grammar_operators_for_family("negation", registry_a) == (),
    "non-enum family refused",
)

# Visible language remains source only. Even exact spans produce no operator.
supported = projection_for("Do not install it.", 1)
check(
    supported.status is SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED,
    "supported projection status",
)
projection = supported.projection
assert projection is not None

text = "Do not install it."
not_start = text.index("not")
not_spans = tuple(
    projection.code_points[index].source_span_id
    for index in range(not_start, not_start + 3)
)
install_start = text.index("install")
install_spans = tuple(
    projection.code_points[index].source_span_id
    for index in range(install_start, install_start + 7)
)

for operator_key, spans in (
    ("grammar_negation", not_spans),
    ("grammar_prohibition", not_spans),
    ("fbsc_decay_mark", not_spans),
    ("fbsc_projection", install_spans),
):
    decision = evaluate_grammar_operator_proposal(
        projection,
        operator_key=operator_key,
        source_span_ids=spans,
        registry=registry_a,
    )
    check(
        type(decision) is GrammarOperatorProposalDecision,
        f"decision exact type {operator_key}",
    )
    check(
        decision.status
        is ProposalDecisionStatus.REFUSED_NO_RULE_INSTALLED,
        f"no rule refusal {operator_key}",
    )
    check(decision.operator_found, f"operator found {operator_key}")
    check(not decision.rule_found, f"rule absent {operator_key}")
    check(not decision.proposal_created, f"proposal absent {operator_key}")
    check(
        decision.candidate_operator_key is None,
        f"candidate absent {operator_key}",
    )
    check(
        decision.supporting_condition_codes == (),
        f"support not fabricated {operator_key}",
    )
    check(
        "exact_versioned_operator_proposal_rule_not_installed"
        in decision.missing_condition_codes,
        f"missing rule explicit {operator_key}",
    )
    check(
        validate_grammar_operator_proposal_decision(decision).ok,
        f"decision validates {operator_key}",
    )
    check(
        decision.decision_id == decision.expected_id(),
        f"decision stable id {operator_key}",
    )
    for field_name in (
        "source_binding_performed",
        "operator_application_performed",
        "phase_assignment_performed",
        "meaning_created",
        "permission_inferred",
        "route_created",
        "tool_routing_performed",
        "action_performed",
        "memory_read_performed",
        "memory_write_performed",
        "delivery_performed",
    ):
        check(
            getattr(decision, field_name) is False,
            f"decision consequence false {operator_key}:{field_name}",
        )

# Every registered operator remains inert even with the complete root span.
for definition in registry_a.operators:
    decision = evaluate_grammar_operator_proposal(
        projection,
        operator_key=definition.operator_key,
        source_span_ids=(projection.root_source_span_id,),
        registry=registry_a,
    )
    check(
        decision.status
        is ProposalDecisionStatus.REFUSED_NO_RULE_INSTALLED,
        f"all operators inert {definition.operator_key}",
    )
    check(
        validate_grammar_operator_proposal_decision(decision).ok,
        f"all inert decisions valid {definition.operator_key}",
    )

unknown = evaluate_grammar_operator_proposal(
    projection,
    operator_key="not_registered",
    source_span_ids=(projection.root_source_span_id,),
    registry=registry_a,
)
check(
    unknown.status is ProposalDecisionStatus.REFUSED_UNKNOWN_OPERATOR,
    "unknown operator typed refusal",
)
check(not unknown.operator_found, "unknown operator not found")
check(validate_grammar_operator_proposal_decision(unknown).ok, "unknown valid")

missing_span = evaluate_grammar_operator_proposal(
    projection,
    operator_key="grammar_negation",
    source_span_ids=(),
    registry=registry_a,
)
check(
    missing_span.status
    is ProposalDecisionStatus.REFUSED_INVALID_SOURCE_SPAN,
    "missing span typed refusal",
)
check(validate_grammar_operator_proposal_decision(missing_span).ok, "missing span valid")

foreign_span = evaluate_grammar_operator_proposal(
    projection,
    operator_key="grammar_negation",
    source_span_ids=("foreign:span",),
    registry=registry_a,
)
check(
    foreign_span.status
    is ProposalDecisionStatus.REFUSED_INVALID_SOURCE_SPAN,
    "foreign span typed refusal",
)
check(foreign_span.conflicting_condition_codes, "foreign span conflict visible")
check(validate_grammar_operator_proposal_decision(foreign_span).ok, "foreign valid")

invalid_field = evaluate_grammar_operator_proposal(
    object(),
    operator_key="grammar_negation",
    source_span_ids=("x",),
    registry=registry_a,
)
check(
    invalid_field.status
    is ProposalDecisionStatus.REFUSED_INVALID_SOURCE_FIELD,
    "invalid field typed refusal",
)
check(validate_grammar_operator_proposal_decision(invalid_field).ok, "invalid field decision valid")

unsupported = projection_for("A\ue000B", 2)
check(
    unsupported.status
    is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED,
    "unsupported projection status",
)
unsupported_projection = unsupported.projection
assert unsupported_projection is not None
held = evaluate_grammar_operator_proposal(
    unsupported_projection,
    operator_key="grammar_reference",
    source_span_ids=(unsupported_projection.root_source_span_id,),
    registry=registry_a,
)
check(
    held.status
    is ProposalDecisionStatus.REFUSED_INVALID_SOURCE_FIELD,
    "unsupported field held",
)
check(not held.proposal_created, "unsupported no proposal")
check(validate_grammar_operator_proposal_decision(held).ok, "unsupported decision valid")

tampered_registry = replace(registry_a, default_runtime_enabled=True)
check(
    not validate_symbolic_grammar_operator_registry(tampered_registry).ok,
    "tampered registry invalid",
)
invalid_registry_decision = evaluate_grammar_operator_proposal(
    projection,
    operator_key="grammar_negation",
    source_span_ids=(projection.root_source_span_id,),
    registry=tampered_registry,
)
check(
    invalid_registry_decision.status
    is ProposalDecisionStatus.REFUSED_INVALID_REGISTRY,
    "invalid registry typed refusal",
)
check(
    validate_grammar_operator_proposal_decision(
        invalid_registry_decision
    ).ok,
    "invalid registry decision valid",
)

# Grace Override grammar glyph is not silently equated with RSOC chi(t).
grace = grammar_operator_for_key("fbsc_grace_override", registry_a)
assert grace is not None
check(grace.glyph == "†", "grace glyph exact")
check(grace.rsoc_operator_keys == (), "grace has no RSOC mapping")
check(
    "not_rsoc_christ_function" in grace.drift_effect_code,
    "grace/Christ separation explicit",
)

# Immutable records.
try:
    registry_a.default_runtime_enabled = True  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("registry mutable")

try:
    registry_a.operators[0].meaning_authorized = True  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("definition mutable")

print(f"SLICE 36C BEHAVIOR TEST: PASS ({checks} checks)")
